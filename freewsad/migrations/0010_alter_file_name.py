# Generated by Django 4.1.5 on 2023-01-11 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freewsad', '0009_file_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Name'),
        ),
    ]