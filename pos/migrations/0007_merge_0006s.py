from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0006_add_expense_category_and_expense_category_fk'),
        ('pos', '0006_alter_attendance_unique_together_and_more'),
    ]

    operations = [
        # Merge migration: no operations, just unify branches
    ]
