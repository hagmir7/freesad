from users.models import Profile
from rest_framework import serializers
from freewsad.models import *
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# post language view
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields =  'name', 'code', 'id'
    def save(self):
        lang = Language(
            name = self.validated_data['name'],
            code = self.validated_data['code']
        )
        if Language.objects.filter(name=lang.name).exists():
            raise serializers.ValidationError({'message': _("The language already exists.")})

        if Language.objects.filter(code=lang.code).exists():
            raise serializers.ValidationError({'message': _("The language already exists.")})
        
        return lang.save()


class BookCategorySerializer(serializers.ModelSerializer):
    language = LanguageSerializer()
    class Meta:
        model = Book
        fields =  'name', 'title', 'language', 'id', 'slug'



class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model= Book
        fields = ("id", 'title', 'slug', 'name', 'image')

class BookSerializer(serializers.ModelSerializer):
    category = BookCategorySerializer()
    language = LanguageSerializer()
    class Meta:
        model = Book
        fields = ('id', 'name', 'pages','title', 'image', 'description', 'tags', 'created_at', 'pages',
                  'file', 'language', 'book_type', 'list', 'author', 'category', 'slug',
                  'views', "size" )


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('name', 'image', 'description', 'tags', 'file', 'language', 'list', 'author_id', 'category')

class PostCategorySerializer(serializers.ModelSerializer):
    language = LanguageSerializer()
    class Meta:
        model = Post
        fields =  'name', 'title', 'language', 'id', 'slug'

# Post Serializer
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = 'title','image', 'imageURL', 'tags', 'slug', 'description', 'body','created'



# Create post
class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'image', 'tags', 'language', 'category', 'description', 'body', 'list')


 
# cotact create serializer
class ContactSerializers(serializers.ModelSerializer):
    class Meta:
        model= Contact
        fields = 'name','email','body'



# Save Emails
class SaveEmailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = "email",



# Get profile
class ProfileSerialize(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

# Update profile
class UpdatedProfileSerialize(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = 'phone', 'bio', 'gander', 'country', 'city', 'avatar'

# Update avatar
class AvatarSerialize(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = 'avatar',


# Get user 
class UserSerialize(serializers.ModelSerializer):
    profile = UpdatedProfileSerialize()
    class Meta:
        model = User
        fields = 'id', 'username', 'first_name', 'email','last_name', 'is_superuser', 'profile'


    
# Update User
class UpdateUserSerialize(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  'username', 'first_name','last_name','email'


# Craete User
class UserCreationSerialize(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only':True},
            'passwor2': {'write_only':True}

        }

    def save(self):
        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],

        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if User.objects.filter(email=account.username).exists():
            raise serializers.ValidationError([{'username': _('Username already exists.')}])


        if User.objects.filter(email=account.email).exists():
            raise serializers.ValidationError([{'email': _('Email already exists.')}])

        if password != password2:
            raise serializers.ValidationError({'password': _("Password must match.")})



        account.set_password(password)
        account.save()
        return account








# post play list
class PostListSerialiszer(serializers.ModelSerializer):
    language = LanguageSerializer()
    class Meta:
        model = PostList
        fields = 'name', 'description', 'cover', 'id', 'language', 'slug', 'date'

# book play list
class BookListSerialiszer(serializers.ModelSerializer):
    class Meta:
        model = BookList
        fields = 'name', 'description', 'cover', 'id'


class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerialize()
    class Meta:
        model = Author
        fields = 'full_name', 'image', 'description', 'id', 'user'


class CreateAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = 'full_name', 'image', 'description'


class VideoSerializer(serializers.ModelSerializer):
    user = UserSerialize()
    language = LanguageSerializer()
    class Meta:
        model = Video
        fields = ['user', 'title', 'image', 'description', 'tags', 'language', 'category', 'created_at', 'slug']
class VideoCommentSerializer(serializers.ModelSerializer):
    user = UserSerialize()
    class Meta:
        model = VideoComment
        fields = 'user',  'body', 'id', 'created_at'
