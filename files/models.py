from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.crypto import get_random_string






class Folder(models.Model):
    name = models.CharField(max_length=100, default="New Folder")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.IntegerField(default=0, null=True, blank=True )
    created = models.DateTimeField(auto_now_add=True)




    def save(self, *args, **kwargs):
        if not self.slug:
            random = get_random_string(length=5)
            self.slug = slugify(self.name +"-"+ str(random))
        super(Folder, self).save(*args, **kwargs)


    def __str__(self):
        return self.name



class File(models.Model):
    name = models.CharField("Name", max_length=150, null=True, blank=True)
    file = models.FileField(upload_to="Files")
    slug = models.SlugField("Slug", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField("Date",auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=20, null=True, blank=True)
    size = models.CharField(max_length=20, null=True, blank=True)






    def get_size(self, *args, **kwargs):
        if round(self.file.size * 1e-6, 3) >= 1:
            return str(round(self.file.size * 1e-6, 2)) + ' MB'
        else:
            return str(round(self.file.size * 0.001, 2)) + ' KB'

    # Check if file is image
    def is_image(self):
        files = ["JPEG", "PNG", "SVG", "JPG", "GIF", "TIFF", "WEBP", "PDF", "TXT", "JSON", "HTML", "CSS" ]
        if self.type() in files:
            return True
        else:
            return False



    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"

    def get_type(self):
        self.type = self.file.url.split('.')[-1].upper()

    def __str__(self):
        return self.name

    def get_name(self):
        if not self.name:
            self.name = self.file.url.split('.')[0].split('/')[-1].replace("%20", ' ').replace("%40", ' ')

    def get_slug(self):
        if not self.slug:
            random = get_random_string(length=5).upper()
            self.slug = slugify(self.name +"-"+ str(random))


    def save(self, *args, **kwargs):
        # Get file tpype
        self.get_type()
        # Get file size
        self.size = self.get_size()
        # Get name
        self.get_name()
        # Get slug
        self.get_slug()
        super(File, self).save(*args, **kwargs)


 









