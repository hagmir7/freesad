from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils.crypto import get_random_string




user_type = (
    (_('Male'),_('Male')),
    (_('Female'), _('Female')),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    avatar = models.ImageField(upload_to='avatar/', default='user_default.webp', blank=True)
    cover = models.ImageField(upload_to='cover/',  default='cover_default.png', blank=True)
    bio = models.TextField(max_length=300, blank=True)
    phone = models.IntegerField(blank=True, default=False)
    gander = models.CharField(max_length=40, blank=True)
    follow = models.ManyToManyField(User, related_name='follow', blank=True)
    friends = models.ManyToManyField(User, related_name='friend', blank=True)
    country = models.CharField(max_length=40, blank=True)
    is_admin = models.BooleanField(default=False, blank=True)
    is_publesher = models.BooleanField(default=False, blank=True)
    is_blocked = models.BooleanField(default=False, blank=True)
    block = models.ManyToManyField(User, related_name='user_block', blank=True)
    viewrs = models.ManyToManyField(User, related_name='user_viewrs', blank=True)
    birth = models.CharField(max_length=300, blank=True)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(auto_now=True)
    verificated = models.BooleanField(default=False)
    trafiq = models.IntegerField(null=True, blank=True, default=0)
    
    location = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=200, blank=True)
    flag = models.CharField(max_length=2000, blank=True)
    device = models.CharField(max_length=100, blank=True)
    continent = models.CharField(max_length=100, blank=True)
    capital = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=100, blank=True)
    ipAddress = models.GenericIPAddressField(null=True, blank=True)
    earning = models.FloatField(default=0.00)

    slug = models.SlugField(blank=True, null=True)




    def get_friend(self):
        return self.friends.all()
    
    def get_friend_no(self):
        return self.friends.all().count
    

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.created.strftime('%d-%m-%Y')}"

    
    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.user.username))
        return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/{self.slug}'



class Media(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,)
    facebook = models.CharField(max_length=300, null=True, blank=True)
    instagram = models.CharField(max_length=300, null=True, blank=True)
    twitter = models.CharField(max_length=300, null=True, blank=True)
    github = models.CharField(max_length=300, null=True, blank=True)
    web = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.user)



STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)





class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) 


    def __str__(self):
        return f'{self.sender} - {self.receiver} - {self.status}'


class Public(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    email = models.BooleanField(default=True, blank=True)
    phone = models.BooleanField(default=True, blank=True)
    web = models.BooleanField(default=True, blank=True)
    bio = models.BooleanField(default=True, blank=True)
    gander = models.BooleanField(default=True, blank=True)
    friends = models.BooleanField(default=True, blank=True)
    country = models.BooleanField(default=True, blank=True)
    birth = models.BooleanField(default=True, blank=True)
    created = models.BooleanField(default=True, blank=True)



class PusblisherCategoryEnglish(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class PusblisherCategoryArabic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PusblisherCategoryfranch(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Pusblisher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # photo = models.ImageField(upload_to='photo_publisher')
    # cin_1 = models.ImageField(upload_to='CIN', blank=True, null=True)
    # cin_2 = models.ImageField(upload_to='CIN', blank=True, null=True)
    category = models.CharField(max_length=600,null=True, blank=True)
    send = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
