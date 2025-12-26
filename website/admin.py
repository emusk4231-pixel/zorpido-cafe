from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Testimonial, FeaturedImage


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
			url = None
			try:
				url = obj.profile_picture.url
			except Exception:
				url = obj.profile_picture if isinstance(obj.profile_picture, str) else None
			if url:
				return format_html('<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;" />', url)
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
			url = None
			try:
				url = obj.image.url
			except Exception:
				url = obj.image if isinstance(obj.image, str) else None
			if url:
				return format_html('<img src="{}" style="max-width:200px;max-height:200px;object-fit:cover;" />', url)
		return '-'

	image_preview.short_description = 'Image Preview'

	def save_model(self, request, obj, form, change):
		file = form.cleaned_data.get('image_upload') if form.is_valid() else None
		if file:
			obj.image = file
		super().save_model(request, obj, form, change)
