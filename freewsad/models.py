from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.utils import timezone
import uuid
import os
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os



def is_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False
    

# Generate file name
def filename(instance, filename):
    ext = filename.split('.')[-1]  # Get the file extension
    new_filename = f'{uuid.uuid4().hex}.{ext}'
    base_path = f"{str(instance._meta.model_name).lower()}s/{ext.upper()}" # Change this to your desired directory
    current_date = timezone.now().strftime('%Y-%m-%d')
    file = os.path.join(base_path, current_date, new_filename)
    
    return file

class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country_flag = models.CharField(max_length=300, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    browser = models.CharField(max_length=100, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.ip


class IpModel(models.Model):
    ip = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.ip


class Language(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=3)

    def __str__(self):
        return self.name





class PostCategory(models.Model):
    name = models.CharField(max_length=200)
    language = models.ForeignKey(Language, on_delete=models.CASCADE ,blank=True, null=True)
    slug = models.SlugField(unique=True, auto_created=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        random = get_random_string(length=5)
        if not self.slug:
            self.slug = slugify(str(self.name)[0:10] +"-"+ str(random))
        super(PostCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name




class PostList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, verbose_name='Name ')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    cover = models.ImageField(upload_to=filename, default='default-post.png')
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True,auto_created=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        random = get_random_string(length=5)
        if self.id:
            self.slug = self.slug
        elif self.name == None:
            self.slug = slugify(get_random_string(length=40).upper())
        else:
            self.slug = slugify(str(self.name) +"-"+ str(random))
        super(PostList, self).save(*args, **kwargs)
       

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='posts')
    list = models.ForeignKey(PostList, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to=filename, blank=True, null=True)
    imageURL = models.CharField(max_length=700, null=True, blank=True)
    body = models.TextField(verbose_name='Body ',blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    save_post = models.ManyToManyField(User, related_name='save_post')
    like_post = models.ManyToManyField(User, related_name='like_post')
    is_block = models.BooleanField(default=False, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(PostCategory, on_delete=models.PROTECT, blank=True, null=True)
    tags = models.CharField(max_length=150, null=True, blank=True)
    views = models.ManyToManyField(IpModel, related_name='post_views', blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE ,blank=True, null=True)
    valid = models.BooleanField(default=False, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, max_length=200)
    is_public = models.BooleanField(default=True)
    ip_like = models.ManyToManyField(IpModel, related_name='ip_like', blank=True)
        
        
    class Meta:
        ordering = ['-created']


    def get_absolute_url(self):
        return f'/{self.language.code}/p/{self.slug}'


    def save(self, *args, **kwargs):
        random = get_random_string(length=5)
        if self.id:
            self.slug = self.slug
        elif self.title == None:
            self.slug = slugify(get_random_string(length=40).upper())
        else:
            self.slug = slugify(str(self.title)[0:10] +"-"+ str(random))
        super(Post, self).save(*args, **kwargs)
    

    def next(self):
        return self.get_next_by_created()


    def pre(self):
        return self.get_previous_by_created()
    

    def __str__(self):
        return str(self.title)




class PostComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comment')
    body = models.TextField(max_length=400)
    likes = models.ManyToManyField(User, related_name='like_comment',blank=True)
    created = models.DateTimeField(auto_now=True,)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.user} Comment at {self.post.user.username}'s Post"



class Subscribe(models.Model):
    email = models.EmailField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=100, null=True, blank=True)
    catgory = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.email

    


class BookList(models.Model):
    name = models.CharField(max_length=300, verbose_name='Name ')
    description = models.TextField(blank=True, null=True)
    cover = models.ImageField(upload_to=filename, default='default-post.png')
    language = models.ForeignKey(Language, on_delete=models.CASCADE ,blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.CASCADE ,blank=True, null=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs ):
        random = get_random_string(length=5).upper()
        if not self.id:
            self.slug = slugify(self.name +"-"+ str(random))
        elif not self.slug:
            self.slug = slugify(self.name +"-"+ str(random))
        super(BookCategory, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    image = models.ImageField(_("Image"), upload_to=filename, null=True, blank=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    slug = models.SlugField(blank=True, null=True, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.slug == None:
            self.slug = get_random_string(length=40)
        super(Author, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name
    

class Type(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def save(self, *args, **kwargs):
        if self.name == None:
            self.slug = get_random_string(length=40)
        super(Type, self).save(*args, **kwargs)

    def __str__(self):
        return self.name



class Book(models.Model):
    name = models.CharField(max_length=80, verbose_name='BOOK ')
    title = models.CharField(max_length=150, null=True, blank=True)
    list = models.ForeignKey(BookList, models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")
    author = models.CharField(max_length=50, verbose_name='Author name', null=True, blank=True)
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE ,blank=True, null=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, null=True, blank=True)
    pages = models.IntegerField(verbose_name='Page Number ',  null=True, blank=True)
    size = models.CharField(verbose_name="Size", null=True, blank=True, max_length=100)
    book_type = models.CharField(max_length=30, verbose_name='Book Type ', null=True, blank=True)
    image = models.ImageField(upload_to=filename, verbose_name='Image ')
    description = models.TextField(null=True, blank=True, verbose_name='Description ')
    body = models.TextField(verbose_name='Body', null=True, blank=True)
    save_book = models.ManyToManyField(User, related_name='book_save')
    likes = models.ManyToManyField(User, related_name='book_like')
    tags = models.CharField(max_length=500, null=True, blank=True)
    views = models.ManyToManyField('Location', through='BookView')
    file = models.FileField(upload_to=filename, blank=True, verbose_name='File')
    is_public = models.BooleanField(default=True)
    status = models.BooleanField(default=None, null=True, blank=True)
    slug = models.SlugField(blank=True, null=True, editable=False, unique=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Rest of your model fields and methods

    # def delete(self):
    #     self.is_deleted = True
    #     self.save()

    def get_absolute_url(self, *args, **kwargs):
        return f'/{self.language.code}/book/{self.slug}'

    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return self.name

    
    def addView(self, *args, **kwargs):
        self.views = self.views + 1
        super(Book, self).save(*args, **kwargs)



            
    def save(self, *args, **kwargs):

        random = get_random_string(length=5).upper()

        
        if not self.id:
            self.slug = slugify(self.name[0:20] +"-"+ str(random))
        elif not self.slug:
            self.slug = slugify(self.name[0:20] +"-"+ str(random))
       

        if self.file:
            self.book_type = self.file.url.split('.')[-1].upper()

        super(Book, self).save(*args, **kwargs)


    def next(self):
        return self.get_next_by_created_at()

    def pre(self):
        return self.get_previous_by_created_at()


class BookView(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    view = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class CommentBook(models.Model):
    book = models.ForeignKey(Book, related_name='comments_book', on_delete=models.CASCADE)  
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    body = models.TextField()
    date = models.DateTimeField(auto_now=True)
    

    
    def __str__(self):
        name = self.name
        post = self.post
        return f'{name} Comment at {post}'
    

    class Meta:
        ordering = ('-date',)




# Contact
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name




class Page(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        random = get_random_string(length=5)
        if self.id:
            self.slug = self.slug
        else:
            self.slug = slugify(self.title +"-"+ str(random))

        super(Page, self).save(*args, **kwargs)


class VideoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_lists')
    name = models.CharField(max_length=300, verbose_name='Name ')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Tags "))
    image = models.ImageField(upload_to=filename, default='default-post.png')
    slug = models.SlugField(unique=True, auto_created=True, null=True, blank=True)
    category = models.ManyToManyField(PostCategory, related_name='video_list_category', blank=True, verbose_name=_("Category"))
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        random = get_random_string(length=5)
        if self.id:
            self.slug = self.slug
        elif self.name == None:
            self.slug = slugify(get_random_string(length=40).upper())
        else:
            self.slug = slugify(str(self.name) + "-" + str(random))
        super(VideoList, self).save(*args, **kwargs)
    
class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    image = models.ImageField(upload_to=filename, null=True, blank=True, verbose_name=_("Image"))
    list = models.ForeignKey(VideoList, on_delete=models.CASCADE, related_name="videos", null=True, blank=True, verbose_name=(_("Play list")))
    description = models.TextField(verbose_name=_("Description"))
    tags = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Tags "))
    views = models.ManyToManyField('Location', through='VideoView')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL ,blank=True, null=True, verbose_name=_("Language"))
    category = models.ManyToManyField(PostCategory, related_name='video_category', blank=True, verbose_name=_("Category"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    save = models.ManyToManyField(User, related_name='video_save', blank=True)
    slug = models.SlugField(null=True, blank=True)


    def __str__(self):
        return self.title
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex
        return super(Video, self).save(*args, **kwargs)  
    
    def get_absolute_url(self, *args, **kwargs):
        if self.language:
            return f'/{self.language.code}/video/{self.slug}'
        else:
            return f'/video/{self.slug}'
    

    

class VideoView(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    view = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Quality(models.Model):
    quality = models.CharField(max_length=100, verbose_name=(_("Quality")), null=True, blank=True)
    file = models.FileField(upload_to=filename, verbose_name="Video", null=True, blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="video_qualities")
    size = models.CharField(max_length=50, blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    duration = models.CharField(max_length=20, null=True, blank=True)
    url = models.CharField(max_length=600, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=True, blank=True)


    def __str__(self):
        return self.video.title

    class Meta:
            # Define the default ordering for querysets
        ordering = ['height']
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex
        return super(Quality, self).save(*args, **kwargs)
    


class VideoComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="video_comment")
    like = models.ManyToManyField(User, related_name='comment_like', blank=True)
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
