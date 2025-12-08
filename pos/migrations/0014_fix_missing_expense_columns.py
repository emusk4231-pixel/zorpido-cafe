"""Add missing columns to pos_expense table if they were created out-of-sync.

Duplicate of earlier fix but with new migration number to avoid conflicts.
"""
from django.db import migrations


def add_missing_columns(apps, schema_editor):
    conn = schema_editor.connection
    table_name = 'pos_expense'
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s", (table_name,))
        if not cursor.fetchone():
            return
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        existing = {row[1] for row in cursor.fetchall()}
        to_add = {
            'updated_at': "ALTER TABLE pos_expense ADD COLUMN updated_at datetime",
            'created_by_id': "ALTER TABLE pos_expense ADD COLUMN created_by_id integer",
            'description': "ALTER TABLE pos_expense ADD COLUMN description text",
            'date': "ALTER TABLE pos_expense ADD COLUMN date date",
            'category_id': "ALTER TABLE pos_expense ADD COLUMN category_id integer",
            'created_at': "ALTER TABLE pos_expense ADD COLUMN created_at datetime",
            'amount': "ALTER TABLE pos_expense ADD COLUMN amount numeric",
        }
        for col, sql in to_add.items():
            if col not in existing:
                try:
                    cursor.execute(sql)
                except Exception:
                    pass
    finally:
        try:
            cursor.close()
        except Exception:
            pass


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0013_fix_missing_expense_columns'),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, reverse_code=noop),
    ]
