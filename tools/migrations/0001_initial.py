# Generated by Django 4.1.9 on 2023-11-25 13:52

from django.db import migrations, models
import freewsad.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Linke',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('link', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to=freewsad.models.filename)),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
                ('description', models.CharField(max_length=100)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
