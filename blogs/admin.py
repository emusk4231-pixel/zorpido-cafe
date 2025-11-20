from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'is_published', 'is_featured', 'published_at')
	list_filter = ('is_published', 'is_featured', 'author')
	search_fields = ('title', 'excerpt', 'content')
	prepopulated_fields = {'slug': ('title',)}
