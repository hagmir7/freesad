# Generated by Django 4.1.9 on 2023-08-31 12:05

from django.db import migrations, models
import django.db.models.deletion
import freewsad.models


class Migration(migrations.Migration):

    dependencies = [
        ('freewsad', '0037_book_title_alter_book_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='freewsad.bookcategory', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='book',
            name='image',
            field=models.ImageField(upload_to=freewsad.models.filename, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='book',
            name='name',
            field=models.CharField(max_length=80, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='book',
            name='tags',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='book',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='freewsad.type', verbose_name='Type'),
        ),
    ]
