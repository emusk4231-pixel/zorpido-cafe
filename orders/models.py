"""
Models for order management
"""

from django.db import models
from django.conf import settings
from menu.models import MenuItem
import uuid
from decimal import Decimal

class Order(models.Model):
    """
    Order model for tracking customer orders
    """
    ORDER_TYPE_CHOICES = (
        ('dine_in', 'Dine In'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('qr', 'QR Code'),
        ('credit', 'Customer Credit'),
        ('mixed', 'Mixed Payment'),
    )
    
    # Order identification
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    
    # Customer & staff info
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='processed_orders',
        null=True,
        blank=True,
        limit_choices_to={'user_type__in': ['staff', 'admin']}
    )
    
    # Order details
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='dine_in')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financial information
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Payment
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )
    payment_status = models.CharField(
        max_length=20,
        choices=(('pending', 'Pending'), ('completed', 'Completed')),
        default='pending'
    )
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Loyalty points used/earned
    loyalty_points_used = models.IntegerField(default=0)
    loyalty_points_earned = models.IntegerField(default=0)

    # Delivery information (if applicable)
    delivery_address = models.TextField(blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Notes
    customer_notes = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer}"
    
    def save(self, *args, **kwargs):
        # Generate unique order number
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number"""
        import datetime
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        random_str = str(uuid.uuid4().hex[:6]).upper()
        return f"ZRP{date_str}{random_str}"
    
    def calculate_totals(self):
        """Calculate order totals from order items"""
        items = self.items.all()
        # Sum subtotals (ensure Decimal)
        self.subtotal = sum((item.subtotal for item in items), Decimal('0.00'))

        # Tax removed — keep the field but it's always zero
        self.tax = Decimal('0.00')

        # Add delivery fee if applicable
        if self.order_type == 'delivery':
            self.delivery_fee = Decimal('50.00')  # Fixed delivery fee

        # Calculate total (tax excluded)
        self.total = (self.subtotal + self.delivery_fee - self.discount).quantize(Decimal('0.01'))

        # Calculate loyalty points earned (1 point per NPR 1 spent)
        if self.customer:
            self.loyalty_points_earned = int(self.total)

        self.save()
    
    def mark_as_completed(self):
        """Mark order as completed and update customer data"""
        from django.utils import timezone

        self.status = 'completed'
        self.payment_status = 'completed'
        self.completed_at = timezone.now()
        self.save()

        # Update customer loyalty points and spending
        if self.customer:
            # Always update total spent
            self.customer.update_total_spent(self.total)

            # Add loyalty points and log a LoyaltyTransaction for cash/qr payments
            if self.payment_method in ['cash', 'qr']:
                try:
                    points = int(self.total // 10)
                except Exception:
                    points = 0
                if points > 0:
                    self.customer.add_loyalty_points(points)
                    try:
                        from loyalty.models import LoyaltyTransaction
                        LoyaltyTransaction.objects.create(
                            customer=self.customer,
                            transaction_type='earned',
                            points=points,
                            description=f'Order #{self.order_number} paid via {self.payment_method}',
                            order=self
                        )
                    except Exception:
                        pass

            # If paid on customer credit, add to customer's credit balance and log transaction
            if self.payment_method == 'credit':
                self.customer.add_credit(self.total)

                # Log transaction in pos.CreditTransaction if available
                try:
                    from pos.models import CreditTransaction as PosCreditTransaction
                    PosCreditTransaction.objects.create(
                        user=self.customer,
                        amount=self.total,
                        action='add',
                        balance_after=self.customer.credit_balance,
                        note=f'Order #{self.order_number} completed on credit',
                        staff=self.staff
                    )
                except Exception:
                    # Fallback: log in loyalty CreditTransaction
                    try:
                        from loyalty.models import CreditTransaction as LoyaltyCreditTransaction
                        LoyaltyCreditTransaction.objects.create(
                            customer=self.customer,
                            transaction_type='credit_added',
                            amount=self.total,
                            description=f'Order #{self.order_number} completed on credit'
                        )
                    except Exception:
                        pass


class OrderItem(models.Model):
    """
    Individual items in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    
    # Item details (stored to preserve historical data)
    item_name = models.CharField(max_length=200)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Quantity and totals
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Special instructions
    special_instructions = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.item_name}"
    
    def save(self, *args, **kwargs):
        # Store item details
        if not self.item_name:
            self.item_name = self.menu_item.name
        if not self.item_price:
            self.item_price = self.menu_item.price
        
        # Calculate subtotal
        self.subtotal = self.item_price * self.quantity
        
        super().save(*args, **kwargs)
        
        # Recalculate order totals
        self.order.calculate_totals()