<<<<<<< HEAD
from django.contrib import admin
from .models import Category, MenuItem, FeaturedMenu


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'is_active', 'order')
	prepopulated_fields = {'slug': ('name',)}
	search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'price', 'availability', 'is_active', 'stock_quantity')
	list_filter = ('category', 'availability', 'is_active', 'is_featured')
	search_fields = ('name', 'description')
	prepopulated_fields = {'slug': ('name',)}


@admin.register(FeaturedMenu)
class FeaturedMenuAdmin(admin.ModelAdmin):
	list_display = ('menu_item', 'title', 'is_active', 'display_order')
	list_filter = ('is_active',)
=======
from django.contrib import admin
from .models import Category, MenuItem, FeaturedMenu


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'is_active', 'order')
	prepopulated_fields = {'slug': ('name',)}
	search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'price', 'availability', 'is_active', 'stock_quantity')
	list_filter = ('category', 'availability', 'is_active', 'is_featured')
	search_fields = ('name', 'description')
	prepopulated_fields = {'slug': ('name',)}


@admin.register(FeaturedMenu)
class FeaturedMenuAdmin(admin.ModelAdmin):
	list_display = ('menu_item', 'title', 'is_active', 'display_order')
	list_filter = ('is_active',)
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
