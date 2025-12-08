"""
Loyalty program models
"""

from django.db import models
from django.conf import settings

class LoyaltyTransaction(models.Model):
    """
    Track loyalty points transactions
    """
    TRANSACTION_TYPE_CHOICES = (
        ('earned', 'Points Earned'),
        ('redeemed', 'Points Redeemed'),
        ('expired', 'Points Expired'),
        ('adjusted', 'Admin Adjustment'),
    )
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loyalty_transactions'
    )
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    
    # Related order (if applicable)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_transactions'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Loyalty Transaction"
        verbose_name_plural = "Loyalty Transactions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.transaction_type} - {self.points} points"


class LoyaltyProgram(models.Model):
    """
    Loyalty program configuration
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    points_per_rupee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Points earned per NPR 1 spent"
    )
    redemption_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Value of 1 point in NPR"
    )
    minimum_redemption_points = models.IntegerField(
        default=100,
        help_text="Minimum points required for redemption"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Loyalty Program"
        verbose_name_plural = "Loyalty Programs"
    
    def __str__(self):
        return self.name


class CreditTransaction(models.Model):
    """Track credit additions and deductions for customers"""
    TRANSACTION_TYPE_CHOICES = (
        ('credit_added', 'Credit Added'),
        ('credit_deducted', 'Credit Deducted'),
        ('adjustment', 'Adjustment'),
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loyalty_credit_transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Credit Transaction'
        verbose_name_plural = 'Credit Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.full_name or self.customer.email} - {self.transaction_type} - {self.amount}"