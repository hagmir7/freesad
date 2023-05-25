from import_export import resources
from .models import Post

class PostResource(resources.ModelResource):
    class Meta:
        model = Post
        fields = ('title', 'image', 'category', 'language', 'tags','list', 'description', 'body', 'is_public',)