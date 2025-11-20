from django.contrib import admin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	list_display = ('customer_name', 'rating', 'is_active', 'created_at')
	list_filter = ('is_active', 'rating')
	search_fields = ('customer_name', 'message')
	readonly_fields = ('created_at',)
	fieldsets = (
		(None, {
			'fields': ('customer_name', 'profile_picture', 'rating', 'message', 'is_active')
		}),
		('Timestamps', {
			'fields': ('created_at',),
		}),
	)


from .models import FeaturedImage


@admin.register(FeaturedImage)
class FeaturedImageAdmin(admin.ModelAdmin):
	list_display = ('title', 'order', 'is_active', 'created_at')
	list_filter = ('is_active',)
	ordering = ('order', 'created_at')
	search_fields = ('title',)
	readonly_fields = ('created_at',)
