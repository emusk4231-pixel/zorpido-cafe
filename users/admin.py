from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django import forms
from .models import User, CustomerMessage
from django.utils.html import format_html
from utils.supabase_storage import upload_file


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	"""Use Django's built-in UserAdmin to expose permissions and groups."""
	model = User
	# Use a custom admin form that accepts a file upload (profile_upload).
	# The uploaded file will be sent to Supabase and the returned public URL
	# stored in the model's `profile_picture` URLField.

	class UserAdminForm(forms.ModelForm):
		profile_upload = forms.FileField(required=False, label='Upload Profile Picture')

		class Meta:
			model = User
			exclude = ('profile_picture',)

	form = UserAdminForm
	list_display = ('username', 'profile_thumbnail', 'full_name', 'email', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'created_at')
	list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups')
	search_fields = ('username', 'full_name', 'email')
	readonly_fields = ('created_at', 'updated_at', 'profile_thumbnail')

	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Personal info', {'fields': ('full_name', 'email', 'phone', 'date_of_birth', 'location', 'profile_upload', 'profile_thumbnail')}),
		('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type', 'groups', 'user_permissions')}),
		('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'profile_upload')
		}),
	)

	ordering = ('email',)
	filter_horizontal = ('groups', 'user_permissions')

	def profile_thumbnail(self, obj):
		"""Return a small avatar image for list display and detail preview."""
		if obj and getattr(obj, 'profile_picture'):
			# `profile_picture` is now a URL string. Accept either string URL
			# or a storage-backed file-like object for backward compatibility.
			url = None
			if isinstance(obj.profile_picture, str):
				url = obj.profile_picture
			else:
				try:
					url = obj.profile_picture.url
				except Exception:
					url = None
			if url:
				return format_html('<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />', url)
			return '-'
		return '-'

	profile_thumbnail.short_description = 'Avatar'
	profile_thumbnail.allow_tags = True


	def save_model(self, request, obj, form, change):
		"""Handle profile file upload from the admin form and store on Supabase.

		If the user is being created (no `pk` yet) we save once to obtain an ID,
		then upload the file and update the `profile_picture` URL.
		"""
		file = form.cleaned_data.get('profile_upload') if form.is_valid() else None
		# If creating a new object, first save to get a primary key
		if not change and not obj.pk:
			super().save_model(request, obj, form, change)
			# obj now has a pk
			if file:
				file_name = f"profile_pictures/{obj.pk}_{file.name}"
				url = upload_file(file, file_name)
				obj.profile_picture = url
				obj.save(update_fields=['profile_picture'])
			return

		# For updates or if pk exists, upload then save
		if file:
			file_name = f"profile_pictures/{obj.pk or 'unknown'}_{file.name}"
			url = upload_file(file, file_name)
			obj.profile_picture = url
		super().save_model(request, obj, form, change)


@admin.register(CustomerMessage)
class CustomerMessageAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'subject', 'created_at', 'is_read', 'replied')
	list_filter = ('is_read', 'replied', 'created_at')
	search_fields = ('name', 'email', 'subject')
