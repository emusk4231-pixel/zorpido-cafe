"""
Custom User Model for Zorpido
Extends Django's AbstractUser to include customer-specific fields
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom User model with additional fields for customer management
    Supports both customers and staff users
    """
    
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    
    # Phone number validator (Nepal format)
    phone_regex = RegexValidator(
        regex=r'^[9][6-9]\d{8}$',
        message="Phone number must be in format: '98XXXXXXXX' (Nepal mobile)"
    )
    
    # Required fields for all users
    email = models.EmailField(unique=True, verbose_name="Email Address")
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    
    # Customer-specific fields
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(validators=[phone_regex], max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    location = models.CharField(max_length=255, blank=True)
    
    # Financial fields
    credit_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Customer's credit balance in NPR"
    )
    total_spent = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Total amount spent by customer"
    )
    
    # Loyalty points
    loyalty_points = models.IntegerField(default=0, help_text="Current loyalty points")
    total_points_earned = models.IntegerField(default=0, help_text="Total points earned lifetime")
    total_points_redeemed = models.IntegerField(default=0, help_text="Total points redeemed")
    
    # (email verification removed)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    # Profile picture
    # Store only file path / name as default; template will resolve static/media locations
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, default='images/default_profile.png')
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name or self.username} ({self.user_type})"
    
    def add_loyalty_points(self, points):
        """Add loyalty points to user account"""
        self.loyalty_points += points
        self.total_points_earned += points
        self.save()
    
    def redeem_loyalty_points(self, points):
        """Redeem loyalty points (returns True if successful)"""
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            self.total_points_redeemed += points
            self.save()
            return True
        return False
    
    def add_credit(self, amount):
        """Add credit to user's account"""
        # Ensure Decimal arithmetic
        if amount is None:
            return
        amt = Decimal(str(amount))
        if amt <= Decimal('0'):
            return
        current = self.credit_balance or Decimal('0.00')
        self.credit_balance = (current + amt).quantize(Decimal('0.01'))
        self.save()
    
    def deduct_credit(self, amount):
        """Deduct credit from user's account (returns True if successful)"""
        if amount is None:
            return False
        amt = Decimal(str(amount))
        if amt <= Decimal('0'):
            return False
        current = self.credit_balance or Decimal('0.00')
        if current >= amt:
            self.credit_balance = (current - amt).quantize(Decimal('0.01'))
            self.save()
            return True
        return False
    
    def update_total_spent(self, amount):
        """Update total amount spent by customer"""
        if amount is None:
            return
        amt = Decimal(str(amount))
        if amt <= Decimal('0'):
            return
        current = self.total_spent or Decimal('0.00')
        self.total_spent = (current + amt).quantize(Decimal('0.01'))
        self.save()
    
    @property
    def points_lost(self):
        """Calculate points lost (redeemed)"""
        return self.total_points_redeemed
    
    @property
    def is_customer(self):
        """Check if user is a customer"""
        return self.user_type == 'customer'
    
    @property
    def is_staff_user(self):
        """Check if user is staff (not admin)"""
        return self.user_type == 'staff'


class CustomerMessage(models.Model):
    """
    Model for customer messages/inquiries from website
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Customer Message"
        verbose_name_plural = "Customer Messages"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"