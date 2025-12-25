"""
Menu models for managing categories and dishes
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from utils.supabase_storage import upload_file

class Category(models.Model):
    """
    Menu category (e.g., Appetizers, Main Course, Beverages)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MenuItem(models.Model):
    """
    Individual menu item/dish
    """
    AVAILABILITY_CHOICES = (
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('seasonal', 'Seasonal'),
    )
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # Store public URL returned by Supabase Storage
    image = models.URLField(max_length=500, blank=True, null=True, default='')

    def set_image_from_file(self, file_obj, file_name: str = None):
        """Upload a file to Supabase and set `image` to the returned public URL."""
        if file_name is None:
            file_name = getattr(file_obj, 'name', 'menu/unnamed')
        url = upload_file(file_obj, file_name)
        self.image = url
        self.save(update_fields=['image'])
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    # Purchase price (cost) for margin calculations
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cost/purchase price used to calculate margin"
    )
    
    # Availability
    availability = models.CharField(
        max_length=20, 
        choices=AVAILABILITY_CHOICES, 
        default='available'
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show in featured menu")
    
    # Inventory tracking
    stock_quantity = models.IntegerField(default=0, help_text="Available quantity")
    low_stock_threshold = models.IntegerField(default=10, help_text="Alert when stock is below this")
    
    # Additional info
    preparation_time = models.IntegerField(default=15, help_text="Time in minutes")
    calories = models.IntegerField(blank=True, null=True)
    is_vegetarian = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0, help_text="Display order within category")
    
    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ['category', 'order', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured']),
        ]
        # Custom permission so inventory management can be granted via admin
        permissions = (
            ("manage_inventory", "Can manage inventory"),
        )
    
    def __str__(self):
        return f"{self.name} - NPR {self.price}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_low_stock(self):
        """Check if item is low on stock"""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def is_in_stock(self):
        """Check if item is in stock"""
        return self.stock_quantity > 0 and self.availability == 'available'
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            if self.stock_quantity == 0:
                self.availability = 'out_of_stock'
            self.save()
            return True
        return False
    
    def increase_stock(self, quantity):
        """Increase stock quantity"""
        self.stock_quantity += quantity
        if self.availability == 'out_of_stock' and self.stock_quantity > 0:
            self.availability = 'available'
        self.save()


class FeaturedMenu(models.Model):
    """
    Featured menu items for homepage display
    """
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Featured Menu"
        verbose_name_plural = "Featured Menus"
        ordering = ['display_order']
    
    def __str__(self):
        return f"Featured: {self.menu_item.name}"