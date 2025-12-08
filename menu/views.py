<<<<<<< HEAD
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, MenuItem


def menu_list(request):
    """List all active menu items by category, excluding age-restricted categories.

    Cigarettes and Drinks categories are shown via separate pages and an age
    confirmation flow handled on the frontend.
    """
    # Exclude age-restricted categories by slug. These were updated to new slugs
    exclude_slugs = ['ciarettees', 'alcoholic-drinks', 'bottled-and-ice-cream']
    categories = Category.objects.filter(is_active=True).exclude(slug__in=exclude_slugs).prefetch_related('items')
    context = {'categories': categories}
    return render(request, 'menu/menu_list.html', context)


def special_list(request, kind):
    """Show cigarette or drinks list.

    The frontend opens this URL with ?age_confirm=1 when the user confirms
    they are 18+. If the query parameter is present we set a session flag so
    subsequent visits in the same browser session will be allowed.
    """
    kind = kind.lower()
    # Map incoming "kind" (used by frontend routes/buttons) to actual category slug
    # We keep the frontend kinds (cigarettes/drinks) for compatibility, but map to
    # the new category slugs created by the data migration.
    slug_map = {
        'cigarettes': 'ciarettees',
        'drinks': 'alcoholic-drinks'
    }
    if kind not in slug_map:
        return redirect('menu:list')

    # If frontend passes age_confirm=1, remember in session
    if request.GET.get('age_confirm') == '1':
        request.session[f'age_verified_{kind}'] = True

    # If session not verified, redirect back to menu list (frontend should
    # normally open this page after confirming age via modal)
    if not request.session.get(f'age_verified_{kind}'):
        # Redirecting to menu list is a safe fallback.
        return redirect('menu:list')

    slug = slug_map[kind]
    category = get_object_or_404(Category, slug=slug, is_active=True)
    items = category.items.filter(is_active=True)
    context = {'category': category, 'items': items, 'kind': kind}
    return render(request, 'menu/special_list.html', context)


def category_detail(request, slug):
    """Show all active items in a specific category."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    items = category.items.filter(is_active=True)
    context = {'category': category, 'items': items}
    return render(request, 'menu/menu_list.html', context)


def item_detail(request, slug):
    """Show details of a specific menu item."""
    item = get_object_or_404(MenuItem, slug=slug, is_active=True)
    context = {'item': item}
=======
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, MenuItem


def menu_list(request):
    """List all active menu items by category, excluding age-restricted categories.

    Cigarettes and Drinks categories are shown via separate pages and an age
    confirmation flow handled on the frontend.
    """
    exclude_slugs = ['cigarette', 'cigarettes', 'drinks', 'drink']
    categories = Category.objects.filter(is_active=True).exclude(slug__in=exclude_slugs).prefetch_related('items')
    context = {'categories': categories}
    return render(request, 'menu/menu_list.html', context)


def special_list(request, kind):
    """Show cigarette or drinks list.

    The frontend opens this URL with ?age_confirm=1 when the user confirms
    they are 18+. If the query parameter is present we set a session flag so
    subsequent visits in the same browser session will be allowed.
    """
    kind = kind.lower()
    slug_map = {
        'cigarettes': 'cigarette',
        'drinks': 'drinks'
    }
    if kind not in slug_map:
        return redirect('menu:list')

    # If frontend passes age_confirm=1, remember in session
    if request.GET.get('age_confirm') == '1':
        request.session[f'age_verified_{kind}'] = True

    # If session not verified, redirect back to menu list (frontend should
    # normally open this page after confirming age via modal)
    if not request.session.get(f'age_verified_{kind}'):
        # Redirecting to menu list is a safe fallback.
        return redirect('menu:list')

    slug = slug_map[kind]
    category = get_object_or_404(Category, slug=slug, is_active=True)
    items = category.items.filter(is_active=True)
    context = {'category': category, 'items': items, 'kind': kind}
    return render(request, 'menu/special_list.html', context)


def category_detail(request, slug):
    """Show all active items in a specific category."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    items = category.items.filter(is_active=True)
    context = {'category': category, 'items': items}
    return render(request, 'menu/menu_list.html', context)


def item_detail(request, slug):
    """Show details of a specific menu item."""
    item = get_object_or_404(MenuItem, slug=slug, is_active=True)
    context = {'item': item}
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
    return render(request, 'menu/menu_list.html', context)