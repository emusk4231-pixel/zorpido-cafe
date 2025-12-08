from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
import math


class Command(BaseCommand):
    help = 'Apply 5% inactivity deduction to loyalty points for customers inactive for 24 hours.'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24, help='Inactivity window in hours (default 24)')
        parser.add_argument('--dry-run', action='store_true', help='Show which customers would be affected without applying changes')

    def handle(self, *args, **options):
        hours = options.get('hours') or 24
        dry_run = options.get('dry_run')
        cutoff = timezone.now() - timezone.timedelta(hours=hours)

        # Import here to avoid app-loading issues when management command runs
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            from loyalty.models import LoyaltyTransaction
        except Exception:
            self.stderr.write('loyalty.models.LoyaltyTransaction not available. Exiting.')
            return

        try:
            from orders.models import Order
        except Exception:
            Order = None

        qs = User.objects.filter(user_type='customer')
        total_affected = 0
        for u in qs.iterator():
            try:
                # Skip users with no points
                current_points = int(getattr(u, 'loyalty_points', 0) or 0)
                if current_points <= 0:
                    continue

                # Has the user earned points within the window?
                recent_earned = LoyaltyTransaction.objects.filter(customer=u, transaction_type='earned', created_at__gte=cutoff).exists()

                # Has the user made a completed order within the window?
                recent_order = False
                if Order is not None:
                    recent_order = Order.objects.filter(status='completed', customer=u, completed_at__gte=cutoff).exists()

                # If either event happened, user is active; skip
                if recent_earned or recent_order:
                    continue

                # Avoid duplicate deductions within same window: check for recent 'expired' transaction
                recent_expired = LoyaltyTransaction.objects.filter(customer=u, transaction_type='expired', created_at__gte=cutoff).exists()
                if recent_expired:
                    continue

                # Compute deduction: floor of 5% of current points
                deduction = math.floor(current_points * 0.05)
                if deduction <= 0:
                    # Nothing to deduct
                    continue

                total_affected += 1
                msg = f'User {u.pk} ({u.get_full_name() or u.email}): points={current_points} -> deduct={deduction}'
                if dry_run:
                    self.stdout.write('[DRY RUN] ' + msg)
                    continue

                with transaction.atomic():
                    # Create an 'expired' loyalty transaction with negative points to reflect deduction
                    LoyaltyTransaction.objects.create(
                        customer=u,
                        transaction_type='expired',
                        points=-deduction,
                        description=f'Inactivity deduction: {deduction} points (5% of {current_points})'
                    )

                    # Apply deduction to user record (ensure not negative)
                    new_points = max(0, current_points - deduction)
                    # Update user's loyalty fields
                    u.loyalty_points = new_points
                    # Track total redeemed/lost points for reporting
                    try:
                        u.total_points_redeemed = int(getattr(u, 'total_points_redeemed', 0) or 0) + deduction
                    except Exception:
                        pass
                    u.save()

                self.stdout.write('Applied: ' + msg)
            except Exception as e:
                self.stderr.write(f'Failed for user {u.pk}: {e}')

        self.stdout.write(f'Done. Total affected customers: {total_affected}')
