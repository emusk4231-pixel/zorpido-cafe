from django.contrib import admin
from .models import GalleryImage


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'is_active', 'is_glimpses', 'is_zorpido_glimpses', 'created_at')
	list_filter = ('category', 'is_active', 'is_glimpses', 'is_zorpido_glimpses')
	search_fields = ('title', 'caption')
