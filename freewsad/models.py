from django.db import models
from django.contrib.auth.models import User

from django.utils.text import slugify
from django.utils.crypto import get_random_string



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

    def __str__(self):
        return self.name




class PostList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, verbose_name='Name ')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    cover = models.ImageField(upload_to='play_list_cover', default='default-post.png')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    list = models.ForeignKey(PostList, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to='AdminImage/', blank=True, null=True)
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

# BOOk MODEL
        

type_book = {
    'PDF':'PDF',
    'DOCS':'DOCS',
    'TXT':'TXT',
    'PDF':'PDF',
}


class BookList(models.Model):
    name = models.CharField(max_length=300, verbose_name='Name ')
    description = models.TextField(blank=True, null=True)
    cover = models.ImageField(upload_to='play_list_cover', default='default-post.png')
    language = models.ForeignKey(Language, on_delete=models.CASCADE ,blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.CASCADE ,blank=True, null=True)

    def __str__(self):
        return self.name







class Book(models.Model):
    name = models.CharField(max_length=80, verbose_name='BOOK ')
    list = models.ForeignKey(BookList, models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.CharField(max_length=50, verbose_name='Author ', null=True, blank=True)
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE ,blank=True, null=True)
    pages = models.IntegerField(verbose_name='Page Number ',  null=True, blank=True)
    size = models.CharField(verbose_name="Size", null=True, blank=True, max_length=100)

    book_type = models.CharField(max_length=30, verbose_name='Book Type ', null=True, blank=True)
    image = models.ImageField(upload_to='books_Image/', verbose_name='Image ')
    description = models.TextField(null=True, blank=True, verbose_name='Description ' , max_length=300)
    body = models.TextField(verbose_name='Body', null=True, blank=True)
    save_book = models.ManyToManyField(User, related_name='book_save')
    like = models.ManyToManyField(User, related_name='book_like')
    tags = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0, null=True, blank=True)
    file = models.FileField(upload_to='books/', blank=True, verbose_name='File')
    is_public = models.BooleanField(default=True)
    slug = models.SlugField(blank=True, null=True)

    def get_absolute_url(self, *args, **kwargs):
        return f'/{self.language.code}/book/{self.id}'


    def __str__(self):
        return self.name

    
    def addView(self, *args, **kwargs):
        self.views = self.views + 1
        super(Book, self).save(*args, **kwargs)



    def getSize(self, *args, **kwargs):
        if round(self.file.size * 1e-6, 3) >= 1:
            return str(round(self.file.size * 1e-6, 2)) + ' MB'
        else:
            return str(round(self.file.size * 0.001, 2)) + ' KB'

    
    def getType(self, *args, **kwargs):
        return self.file.url.split('.')[-1].split('?')[0].upper()


            
    def save(self, *args, **kwargs):
        random = get_random_string(length=5).upper()
        if not self.id:
            self.slug = slugify(self.name +"-"+ str(random))[0:30]
        self.size = self.getSize()
        self.book_type = self.getType()

        super(Book, self).save(*args, **kwargs)



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



# Template

class TemplatesCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')

    def __str__(self):
        return self.name

class TemplateType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')
    logo = models.ImageField(upload_to='TemplatesCategoryImages', verbose_name='Logo')

    def __str__(self):
        return self.name


class TemplateImages(models.Model):
    images = models.ImageField(upload_to='TempletsImages')

class TemplateLanguage(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name 


class TemplateTols(models.Model):
    name = models.CharField(max_length=300)
    image = models.ImageField(upload_to='TemplateImageTools', blank=True)

    def __str__(self):
        return self.name

class Template(models.Model):
    title = models.CharField(max_length=300, verbose_name='Template Name')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='User Template')
    price = models.FloatField(verbose_name='Price')
    olde_price = models.FloatField(verbose_name='Olde Price', blank=True, null=True)
    demo = models.CharField(max_length=1000, verbose_name='Demo Link')
    file = models.FileField(upload_to='Templates', verbose_name='Template File')
    # language = models.ManyToManyField(TemplateLanguage, related_name='template_language', verbose_name='Template Language', blank=True)
    # template_type = models.ForeignKey(TemplateType, on_delete=models.CASCADE, verbose_name='Template Type')
    category = models.ForeignKey(TemplatesCategory, on_delete=models.CASCADE, verbose_name='Template Category')
    image = models.ManyToManyField(TemplateImages, related_name='templateImage', verbose_name='Templates Images')
    add_to_cart = models.ManyToManyField(User, verbose_name='Cart', related_name='template_add_to_catd')
    tags = models.CharField(max_length=166, verbose_name='Tags', blank=True)
    body = models.TextField(verbose_name='Description', default=' ')
    tols = models.ManyToManyField(TemplateTols, related_name='template_tols', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        random = get_random_string(length=5)
        if self.id:
            self.slug = self.slug
        else:
            self.slug = slugify(self.title +"-"+ str(random))

        super(Template, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/templates/{self.id}'


class TemplateOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, )
    email = models.EmailField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    date = models.DateTimeField(auto_now_add=True)



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






 
