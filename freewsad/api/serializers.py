from users.models import Profile
from rest_framework import serializers
from freewsad.models import Book, BookList, Contact, Language, Post, PostCategory, PostList, Subscribe
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id',
                  'name',
                  'pages',
                  'image',
                  'description',
                  'tags',
                  'date',
                  'pages',
                  'file',
                  'language',
                  'book_type',
                  'list',
                  'author',
                  'category',
                  'slug',
                  'views',
                  "size" )


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
        fields = 'phone', 'bio', 'gander', 'country', 'city'

# Update avatar
class AvatarSerialize(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = 'avatar',


# Get user 
class UserSerialize(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'username', 'first_name', 'email','last_name', 'is_superuser'


    
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

# post category view
class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields =  'name', 'language', 'id'


# post category view
class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields =  'name', 'language', 'id'


# post play list
class PostListSerialiszer(serializers.ModelSerializer):
    class Meta:
        model = PostList
        fields = 'name', 'description', 'cover', 'id', 'language', 'slug', 'date'

# book play list
class BookListSerialiszer(serializers.ModelSerializer):
    class Meta:
        model = BookList
        fields = 'name', 'description', 'cover', 'id'
