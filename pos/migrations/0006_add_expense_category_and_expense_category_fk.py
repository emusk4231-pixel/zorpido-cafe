from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


def create_default_categories(apps, schema_editor):
    ExpenseCategory = apps.get_model('pos', 'ExpenseCategory')
    defaults = ['Supplies', 'Utilities', 'Rent', 'Salaries', 'Misc']
    for name in defaults:
        base_slug = slugify(name)[:150]
        slug = base_slug or 'cat'
        # Ensure unique slug
        i = 1
        while ExpenseCategory.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"[:150]
            i += 1
        ExpenseCategory.objects.get_or_create(name=name, defaults={'slug': slug})


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0005_attendance_shift_attendanceaudit_attendance_shift_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=150, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Expense Category',
                'verbose_name_plural': 'Expense Categories',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='expense',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='pos.expensecategory'),
        ),
        migrations.RunPython(create_default_categories, lambda apps, schema_editor: None),
    ]
