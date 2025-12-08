<<<<<<< HEAD
"""
Views for public website
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from menu.models import MenuItem, FeaturedMenu
from blogs.models import BlogPost
from gallery.models import GalleryImage
from users.forms import CustomerMessageForm
from .models import Testimonial
from .models import FeaturedImage

def home(request):
    """
    Homepage with featured sections
    """
    # Get featured menu items
    featured_items = FeaturedMenu.objects.filter(
        is_active=True,
        menu_item__is_active=True
    ).select_related('menu_item')
    
    # Get featured blog posts
    featured_blogs = BlogPost.objects.filter(
        is_published=True,
        is_featured=True
    )[:3]
    
    # Get gallery images marked as "Zorpido's Glimpses"
    gallery_images = GalleryImage.objects.filter(is_active=True, is_zorpido_glimpses=True)
    
    # If no FeaturedMenu records are configured, fall back to MenuItem.is_featured
    fallback_items = None
    if not featured_items:
        fallback_items = MenuItem.objects.filter(is_active=True, is_featured=True)[:6]

    context = {
        'featured_items': featured_items,
        'fallback_items': fallback_items,
        'featured_blogs': featured_blogs,
        'gallery_images': gallery_images,
        'testimonials': Testimonial.objects.filter(is_active=True)[:6],
        'featured_images': FeaturedImage.objects.filter(is_active=True).order_by('order')[:10],
    }
    
    return render(request, 'website/home.html', context)


def about(request):
    """
    About page
    """
    return render(request, 'website/about.html')


def contact(request):
    """
    Contact page with message form
    """
    if request.method == 'POST':
        form = CustomerMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('website:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerMessageForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'website/contact.html', context)


def blog_list(request):
    """
    List all published blog posts
    """
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    
    context = {
        'posts': posts,
    }
    
    return render(request, 'website/blog_list.html', context)


def blog_detail(request, slug):
    """
    Blog post detail page
    """
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.increment_views()
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'website/blog_detail.html', context)


def gallery_view(request):
    """
    Gallery page
    """
    category = request.GET.get('category', 'all')
    
    if category and category != 'all':
        images = GalleryImage.objects.filter(is_active=True, category=category)
    else:
        images = GalleryImage.objects.filter(is_active=True)
    
    # Get all categories for filter
    categories = GalleryImage.CATEGORY_CHOICES
    
    context = {
        'images': images,
        'categories': categories,
        'current_category': category,
    }
    
    return render(request, 'website/gallery.html', context)


def terms(request):
    """Render Terms & Conditions page"""
    return render(request, 'terms.html')


def workflow(request):
    """Render the café customer journey / workflow visualization page"""
=======
"""
Views for public website
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from menu.models import MenuItem, FeaturedMenu
from blogs.models import BlogPost
from gallery.models import GalleryImage
from users.forms import CustomerMessageForm
from .models import Testimonial
from .models import FeaturedImage

def home(request):
    """
    Homepage with featured sections
    """
    # Get featured menu items
    featured_items = FeaturedMenu.objects.filter(
        is_active=True,
        menu_item__is_active=True
    ).select_related('menu_item')
    
    # Get featured blog posts
    featured_blogs = BlogPost.objects.filter(
        is_published=True,
        is_featured=True
    )[:3]
    
    # Get gallery images marked as "Zorpido's Glimpses"
    gallery_images = GalleryImage.objects.filter(is_active=True, is_zorpido_glimpses=True)
    
    # If no FeaturedMenu records are configured, fall back to MenuItem.is_featured
    fallback_items = None
    if not featured_items:
        fallback_items = MenuItem.objects.filter(is_active=True, is_featured=True)[:6]

    context = {
        'featured_items': featured_items,
        'fallback_items': fallback_items,
        'featured_blogs': featured_blogs,
        'gallery_images': gallery_images,
        'testimonials': Testimonial.objects.filter(is_active=True)[:6],
        'featured_images': FeaturedImage.objects.filter(is_active=True).order_by('order')[:10],
    }
    
    return render(request, 'website/home.html', context)


def about(request):
    """
    About page
    """
    return render(request, 'website/about.html')


def contact(request):
    """
    Contact page with message form
    """
    if request.method == 'POST':
        form = CustomerMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('website:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerMessageForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'website/contact.html', context)


def blog_list(request):
    """
    List all published blog posts
    """
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    
    context = {
        'posts': posts,
    }
    
    return render(request, 'website/blog_list.html', context)


def blog_detail(request, slug):
    """
    Blog post detail page
    """
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.increment_views()
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'website/blog_detail.html', context)


def gallery_view(request):
    """
    Gallery page
    """
    category = request.GET.get('category', 'all')
    
    if category and category != 'all':
        images = GalleryImage.objects.filter(is_active=True, category=category)
    else:
        images = GalleryImage.objects.filter(is_active=True)
    
    # Get all categories for filter
    categories = GalleryImage.CATEGORY_CHOICES
    
    context = {
        'images': images,
        'categories': categories,
        'current_category': category,
    }
    
    return render(request, 'website/gallery.html', context)


def terms(request):
    """Render Terms & Conditions page"""
    return render(request, 'terms.html')


def workflow(request):
    """Render the café customer journey / workflow visualization page"""
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
    return render(request, 'website/workflow.html')