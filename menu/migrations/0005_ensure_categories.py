from django.db import migrations


DESIRED = [
    'Sips',
    'Snacks',
    'Ciarettees',
    'alcoholic drinks',
    'bottled',
    'bottled and ice-cream',
]


def create_categories(apps, schema_editor):
    Category = apps.get_model('menu', 'Category')
    from django.utils.text import slugify
    for name in DESIRED:
        slug = slugify(name)
        Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': ''})


def remove_categories(apps, schema_editor):
    Category = apps.get_model('menu', 'Category')
    from django.utils.text import slugify
    for name in DESIRED:
        slug = slugify(name)
        try:
            c = Category.objects.get(slug=slug)
            # Only delete if name matches desired exactly to avoid removing unrelated categories
            if c.name == name:
                c.delete()
        except Exception:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_add_purchase_price'),
    ]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]
