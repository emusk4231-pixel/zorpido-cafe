from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Category, MenuItem, FeaturedMenu
from utils.supabase_storage import upload_file


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'is_active', 'order')
	prepopulated_fields = {'slug': ('name',)}
	search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
	# Provide a file upload in the admin even though `image` is a URLField.
	class MenuItemAdminForm(forms.ModelForm):
		image_upload = forms.FileField(required=False, label='Upload Image')

		class Meta:
			model = MenuItem
			exclude = ('image',)

	form = MenuItemAdminForm
	list_display = ('name', 'category', 'price', 'availability', 'is_active', 'stock_quantity')
	list_filter = ('category', 'availability', 'is_active', 'is_featured')
	search_fields = ('name', 'description')
	prepopulated_fields = {'slug': ('name',)}

	readonly_fields = ('image_preview',)

	def image_preview(self, obj):
		if obj and getattr(obj, 'image'):
			return format_html('<img src="{}" style="max-width:200px;max-height:200px;object-fit:cover;" />', obj.image)
		return '-'

	image_preview.short_description = 'Image Preview'

	def save_model(self, request, obj, form, change):
		"""Handle file uploaded via `image_upload`, upload to Supabase, store public URL."""
		file = form.cleaned_data.get('image_upload') if form.is_valid() else None
		# If creating, save first to get PK
		if not change and not obj.pk:
			super().save_model(request, obj, form, change)
			if file:
				file_name = f"menu/{obj.pk}_{file.name}"
				url = upload_file(file, file_name)
				obj.image = url
				obj.save(update_fields=['image'])
			return

		if file:
			file_name = f"menu/{obj.pk or 'unknown'}_{file.name}"
			url = upload_file(file, file_name)
			obj.image = url
		super().save_model(request, obj, form, change)


@admin.register(FeaturedMenu)
class FeaturedMenuAdmin(admin.ModelAdmin):
	list_display = ('menu_item', 'title', 'is_active', 'display_order')
	list_filter = ('is_active',)
