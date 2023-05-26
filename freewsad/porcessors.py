from .models import PostCategory, Post

def context(request):
    categories = PostCategory.objects.filter(language__code=request.LANGUAGE_CODE)
    new_posts = Post.objects.filter(language__code=request.LANGUAGE_CODE).order_by('-created')[0:3]
    if request.user.is_authenticated:
        return {
            'categories' : categories,
            'new_posts' : new_posts
        }