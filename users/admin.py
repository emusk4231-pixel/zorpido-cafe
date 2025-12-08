from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, CustomerMessage


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	"""Use Django's built-in UserAdmin to expose permissions and groups."""
	model = User
	list_display = ('username', 'full_name', 'email', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'created_at')
	list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups')
	search_fields = ('username', 'full_name', 'email')
	readonly_fields = ('created_at', 'updated_at')

	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Personal info', {'fields': ('full_name', 'email', 'phone', 'date_of_birth', 'location')}),
		('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type', 'groups', 'user_permissions')}),
		('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff')
		}),
	)

	ordering = ('email',)
	filter_horizontal = ('groups', 'user_permissions')


@admin.register(CustomerMessage)
class CustomerMessageAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'subject', 'created_at', 'is_read', 'replied')
	list_filter = ('is_read', 'replied', 'created_at')
	search_fields = ('name', 'email', 'subject')
