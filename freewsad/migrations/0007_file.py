# Generated by Django 4.1.5 on 2023-01-11 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freewsad', '0006_alter_post_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Name')),
                ('file', models.FileField(upload_to='Files')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('created', models.DateField(auto_now_add=True, verbose_name='Date')),
            ],
            options={
                'verbose_name': 'File',
                'verbose_name_plural': 'Files',
            },
        ),
    ]
