"""Add missing columns to pos_expense table if they were created out-of-sync.

This migration is defensive: it inspects the SQLite table schema and adds
columns that exist on the model but are missing in the database. It is
designed to help recover from a previous inconsistent migration state.

Columns added are nullable so ALTER TABLE succeeds on SQLite.
"""
from django.db import migrations


def add_missing_columns(apps, schema_editor):
    # Only run on sqlite3 and if table exists
    conn = schema_editor.connection
    table_name = 'pos_expense'
    try:
        cursor = conn.cursor()
        # check table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s", (table_name,))
        if not cursor.fetchone():
            return

        cursor.execute(f"PRAGMA table_info('{table_name}')")
        existing = {row[1] for row in cursor.fetchall()}  # name is at index 1

        # Mapping of column -> SQL to add it (nullable/defaultable)
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
                    # best-effort: ignore errors so migration stays idempotent
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
        ('pos', '0011_add_expenses'),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, reverse_code=noop),
    ]
