from django.db import models
from django.db.models import Sum
from django.conf import settings
from decimal import Decimal


class CreditTransaction(models.Model):
    ACTION_CHOICES = (
        ('add', 'Add'),
        ('deduct', 'Deduct'),
        ('payment', 'Payment (order)')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='performed_credit_transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} {self.amount} for {self.user} at {self.created_at}"


class Register(models.Model):
    """Daily cash register for POS terminals."""
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='opened_registers')
    opened_at = models.DateTimeField(auto_now_add=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='closed_registers')
    closed_at = models.DateTimeField(null=True, blank=True)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    cash_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    credit_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    qr_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    # expenses_total removed: Expense feature has been removed from the system

    is_open = models.BooleanField(default=True)

    class Meta:
        ordering = ['-opened_at']

    def __str__(self):
        return f"Register #{self.id} opened at {self.opened_at} by {self.opened_by}"

    def recalculate_totals(self):
        """Recalculate totals from related orders (Expense feature removed)."""
        from orders.models import Order
        orders = Order.objects.filter(status='completed', completed_at__gte=self.opened_at)
        cash = orders.filter(payment_method='cash').aggregate(s=Sum('paid_amount'))['s'] or Decimal('0.00')
        credit = orders.filter(payment_method='credit').aggregate(s=Sum('paid_amount'))['s'] or Decimal('0.00')
        qr = orders.filter(payment_method='qr').aggregate(s=Sum('paid_amount'))['s'] or Decimal('0.00')

        self.cash_total = cash
        self.credit_total = credit
        self.qr_total = qr
        # closing balance: opening + sales (Expense feature removed)
        self.closing_balance = (self.opening_balance + cash + credit + qr)
        self.save()


# REMOVED: Expense model (tracked daily expenses with categories and payment status)
# REMOVED: ExpenseCategory model (classified expenses by type)
# Both models removed entirely from the system
# Database: migration will drop pos_expense and pos_expensecategory tables


class Payable(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('settled', 'Settled'),
    ]

    seller = models.ForeignKey('Seller', on_delete=models.SET_NULL, null=True, blank=True, related_name='payables')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # related_expense removed: Expense feature has been removed
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payable {self.amount} to {self.seller or 'Unknown'} ({self.status})"


class PayablePaymentHistory(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('qr', 'QR')
    ]

    seller = models.ForeignKey('Seller', on_delete=models.CASCADE, related_name='payable_payments')
    payable = models.ForeignKey(Payable, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES, default='cash')
    remark = models.CharField(max_length=255, blank=True)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.amount} to {self.seller} on {self.created_at}"


class Seller(models.Model):
    """Suppliers / Sellers from whom purchases are made."""
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'
        ordering = ['name']

    def __str__(self):
        return self.name

    def total_purchases(self):
        # total_purchases: now returns 0 (Expense feature removed)
        # Historical purchases tracked via Payable model if needed
        return Decimal('0.00')

    def total_payable(self):
        from django.db.models import Sum
        # Sum remaining_amount on pending payables
        s = self.payables.filter(status='pending').aggregate(total=Sum('remaining_amount'))['total'] or Decimal('0.00')
        return s

    def total_paid(self):
        # Total paid can be computed as total_purchases - total_payable
        try:
            return (self.total_purchases() or Decimal('0.00')) - (self.total_payable() or Decimal('0.00'))
        except Exception:
            return Decimal('0.00')


class ExpenseCategory(models.Model):
    """Category for expenses (Food, Gas, Salary, etc.)."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Expense Category'
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Record of a single expense."""
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(db_index=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.category.name}: {self.amount} on {self.date}"


# Attendance feature removed
