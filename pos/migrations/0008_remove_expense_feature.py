# Migration to remove Expense feature from POS system
# Removes Expense and ExpenseCategory models completely
# Removes related_expense FK from Payable model
# Removes expenses_total field from Register model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0007_merge_0006s'),
    ]

    operations = [
        # Remove expenses_total field from Register
        migrations.RemoveField(
            model_name='register',
            name='expenses_total',
        ),
        # Remove related_expense FK from Payable (now empty, kept for historical payables)
        migrations.RemoveField(
            model_name='payable',
            name='related_expense',
        ),
        # Delete Expense model completely
        migrations.DeleteModel(
            name='Expense',
        ),
        # Delete ExpenseCategory model completely
        migrations.DeleteModel(
            name='ExpenseCategory',
        ),
    ]
