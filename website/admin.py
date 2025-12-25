from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Testimonial, FeaturedImage
from utils.supabase_storage import upload_file


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	class TestimonialAdminForm(forms.ModelForm):
		profile_upload = forms.FileField(required=False, label='Upload Profile Picture')

		class Meta:
			model = Testimonial
			exclude = ('profile_picture',)

	form = TestimonialAdminForm
	list_display = ('customer_name', 'rating', 'is_active', 'created_at')
	list_filter = ('is_active', 'rating')
	search_fields = ('customer_name', 'message')
	readonly_fields = ('created_at', 'profile_preview')
	fieldsets = (
		(None, {
			'fields': ('customer_name', 'profile_upload', 'profile_preview', 'rating', 'message', 'is_active')
		}),
		('Timestamps', {
			'fields': ('created_at',),
		}),
	)

	def profile_preview(self, obj):
		if obj and getattr(obj, 'profile_picture'):
			return format_html('<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;" />', obj.profile_picture)
		return '-'

	profile_preview.short_description = 'Profile Preview'


@admin.register(FeaturedImage)
class FeaturedImageAdmin(admin.ModelAdmin):
	class FeaturedImageAdminForm(forms.ModelForm):
		image_upload = forms.FileField(required=False, label='Upload Image')

		class Meta:
			model = FeaturedImage
			exclude = ('image',)

	form = FeaturedImageAdminForm
	list_display = ('title', 'order', 'is_active', 'created_at')
	list_filter = ('is_active',)
	ordering = ('order', 'created_at')
	search_fields = ('title',)
	readonly_fields = ('created_at', 'image_preview')

	def image_preview(self, obj):
		if obj and getattr(obj, 'image'):
			return format_html('<img src="{}" style="max-width:200px;max-height:200px;object-fit:cover;" />', obj.image)
		return '-'

	image_preview.short_description = 'Image Preview'

	def save_model(self, request, obj, form, change):
		file = form.cleaned_data.get('image_upload') if form.is_valid() else None
		if not change and not obj.pk:
			super().save_model(request, obj, form, change)
			if file:
				file_name = f"featured/{obj.pk}_{file.name}"
				url = upload_file(file, file_name)
				obj.image = url
				obj.save(update_fields=['image'])
			return
		if file:
			file_name = f"featured/{obj.pk or 'unknown'}_{file.name}"
			url = upload_file(file, file_name)
			obj.image = url
		super().save_model(request, obj, form, change)
