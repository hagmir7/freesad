# Generated by Django 4.1.9 on 2024-08-11 20:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('freewsad', '0044_book_istm'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='istm',
            new_name='istn',
        ),
    ]