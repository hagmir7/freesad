# Generated by Django 4.1.9 on 2023-06-04 11:58

from django.db import migrations, models
import freewsad.models


class Migration(migrations.Migration):

    dependencies = [
        ('freewsad', '0019_postcategory_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='template',
            name='add_to_cart',
        ),
        migrations.RemoveField(
            model_name='template',
            name='category',
        ),
        migrations.RemoveField(
            model_name='template',
            name='image',
        ),
        migrations.RemoveField(
            model_name='template',
            name='tols',
        ),
        migrations.RemoveField(
            model_name='template',
            name='user',
        ),
        migrations.DeleteModel(
            name='TemplateLanguage',
        ),
        migrations.RemoveField(
            model_name='templateorder',
            name='template',
        ),
        migrations.RemoveField(
            model_name='templateorder',
            name='user',
        ),
        migrations.DeleteModel(
            name='TemplateType',
        ),
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['-date']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created']},
        ),
        migrations.AlterField(
            model_name='book',
            name='file',
            field=models.FileField(blank=True, upload_to=freewsad.models.filename, verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='book',
            name='image',
            field=models.ImageField(upload_to=freewsad.models.filename, verbose_name='Image '),
        ),
        migrations.AlterField(
            model_name='booklist',
            name='cover',
            field=models.ImageField(default='default-post.png', upload_to=freewsad.models.filename),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=freewsad.models.filename),
        ),
        migrations.AlterField(
            model_name='postlist',
            name='cover',
            field=models.ImageField(default='default-post.png', upload_to=freewsad.models.filename),
        ),
        migrations.DeleteModel(
            name='Template',
        ),
        migrations.DeleteModel(
            name='TemplateImages',
        ),
        migrations.DeleteModel(
            name='TemplateOrder',
        ),
        migrations.DeleteModel(
            name='TemplatesCategory',
        ),
        migrations.DeleteModel(
            name='TemplateTols',
        ),
    ]
