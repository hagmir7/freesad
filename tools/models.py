from django.db import models
from freewsad.models import filename
from freewsad.models import Language


class Link(models.Model):
    name = models.CharField(max_length=100)
    custom = models.CharField(max_length=100, null=True, blank=True)
    link = models.URLField(max_length=1000)
    image = models.ImageField(upload_to=filename)
    start = models.IntegerField()
    end = models.IntegerField()
    description = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class FacebookGroup(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=filename)
    url = models.URLField(max_length=1000)
    members = models.IntegerField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    status = models.BooleanField()
    description = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    full_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=filename)
    identity = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    status = models.BooleanField()
    gender = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.full_name
