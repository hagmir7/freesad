# Generated by Django 4.1.9 on 2023-11-25 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0003_link_urls_alter_link_link'),
    ]

    operations = [
        migrations.RenameField(
            model_name='link',
            old_name='urls',
            new_name='url',
        ),
    ]