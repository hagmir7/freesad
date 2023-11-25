from django.db import models
from freewsad.models import filename


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
