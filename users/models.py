from django.db import models
from django.contrib.auth.models import User
# from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _




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
        return f'/user/{self.slug}'

