from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_update_category_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='purchase_price',
            field=models.DecimalField(default=0, help_text='Cost/purchase price used to calculate margin', max_digits=10, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
