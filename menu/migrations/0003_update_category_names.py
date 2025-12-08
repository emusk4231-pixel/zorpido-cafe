from django.db import migrations
from django.utils.text import slugify


OLD_TO_NEW = {
    # old name (case-insensitive) : new display name
    'sips': 'Sips',
    'snacks': 'Snacks',
    'ce-creams': 'bottled and ice-cream',
    'cigarettes': 'Ciarettees',
    'drinks': 'alcoholic drinks',
}


def forwards(apps, schema_editor):
    Category = apps.get_model('menu', 'Category')
    for old_slug, new_name in OLD_TO_NEW.items():
        # try match by slug or by name (case-insensitive)
        qs = Category.objects.filter(slug=old_slug) | Category.objects.filter(name__iexact=old_slug)
        for cat in qs.distinct():
            cat.name = new_name
            cat.slug = slugify(new_name)
            cat.save()


def backwards(apps, schema_editor):
    # Revert names back to their original form where possible
    Category = apps.get_model('menu', 'Category')
    for old_slug, new_name in OLD_TO_NEW.items():
        reverted_name = old_slug if old_slug.isalpha() else old_slug
        # match by new slug/name
        qs = Category.objects.filter(slug=slugify(new_name)) | Category.objects.filter(name__iexact=new_name)
        for cat in qs.distinct():
            cat.name = reverted_name
            cat.slug = old_slug
            cat.save()


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_alter_menuitem_options'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
