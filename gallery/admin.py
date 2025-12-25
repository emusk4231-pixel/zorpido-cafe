from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import GalleryImage
from utils.supabase_storage import upload_file


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
	# Provide a file upload for the URL-backed `image` field
	class GalleryImageAdminForm(forms.ModelForm):
		image_upload = forms.FileField(required=False, label='Upload Image')

		class Meta:
			model = GalleryImage
			exclude = ('image',)

	form = GalleryImageAdminForm
	list_display = ('title', 'category', 'is_active', 'is_glimpses', 'is_zorpido_glimpses', 'created_at')
	list_filter = ('category', 'is_active', 'is_glimpses', 'is_zorpido_glimpses')
	search_fields = ('title', 'caption')

	readonly_fields = ('image_preview',)

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
				file_name = f"gallery/{obj.pk}_{file.name}"
				url = upload_file(file, file_name)
				obj.image = url
				obj.save(update_fields=['image'])
			return

		if file:
			file_name = f"gallery/{obj.pk or 'unknown'}_{file.name}"
			url = upload_file(file, file_name)
			obj.image = url
		super().save_model(request, obj, form, change)
