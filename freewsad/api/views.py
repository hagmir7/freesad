
from django.core.paginator import Paginator
from rest_framework import status
from django.views.generic import View
from rest_framework.parsers import MultiPartParser, FormParser
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from freewsad.models import Post, Book, PostCategory, Subscribe, PostList, BookCategory, BookList
from rest_framework.views import APIView
from .serializers import *
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from users.models import Profile
from django.utils.translation import gettext_lazy as _
from django.forms.models import model_to_dict


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def home(request):
    list = Post.objects.filter(language__code=request.LANGUAGE_CODE, is_public=True).order_by('-created')
    paginator = Paginator(list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    serializer = PostSerializer(posts, many=True)
    return Response({'data': serializer.data, 'has_next': posts.has_next()})



@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def postCreate(request):
    serializer = PostSerializer(data=request.data)
    # serializer.is_valid(raise_exception=True)
    #     # process file
    # file = serializer.validated_data['image']
    if request.method == 'POST':
        if serializer.is_valid():
            serializer.save()
            respons = 'Item successfully added!'
        else:
            respons = 'Data not valid!'
    return Response(respons)


# ViewSets define the view behavior.
class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostUploadImage(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        print(request.data)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)








@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def postDetail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    serializer = PostSerializer(post)
    return Response(serializer.data)

# Contact page


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def contact_api(request):
    serializer = ContactSerializers(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Message has ben send Successfully", })
    else:
        raise serializers.ValidationError({'error': "error messsage"})
        # return Response({"message": "Error! Data is not valid."})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def createPost(request):
    if request.method == 'POST':
        files = request.FILES.getlist('image')
        post = PostSerializer(data=request.data, )
        if post.is_valid():
            post.save(imageA=files[0])
            return Response({'message': "Post Created Successfully..."})
        else:
            print("data note valide")
    return Response({'message': "Create New Post"})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def saveEmails(request):
    if request.method == 'POST':
        serializer = SaveEmailsSerializer(data=request.data)
        if serializer.is_valid():
            # print(serializer.data.get('email'))
            if not Subscribe.objects.filter(email=serializer.validated_data.get('email')).exists():
                print("not exists")
                serializer.save()
                return Response({'message': "Email Created Successfully...", 'created': True})
            else:
                return Response({'message': "Email alredy Exists ...", 'created': False})
    return Response({'message': "Create New Email"})


# JWT Views
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['id'] = user.id
        token['avatar'] = user.profile.avatar.url
        token['is_superuser'] = user.is_superuser
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPoas(request):
    user = request.user
    profile = user.profile_set.all()
    serializer = PostSerializer(profile, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def user(request, username):
    profile = get_object_or_404(Profile, slug=username)
    user = User.objects.get(username=username)
    serializer1 = UserSerialize(user, many=False)
    serializer2 = ProfileSerialize(profile, many=False)
    serializer = []

    serializer.append(serializer1.data)
    serializer.append(serializer2.data)

    return Response(serializer)


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def userId(request, id):
    profile = get_object_or_404(Profile, id=id)
    user = User.objects.get(id=id)
    serializer1 = UserSerialize(user, many=False)
    serializer2 = ProfileSerialize(profile, many=False)
    serializer = []

    serializer.append(serializer1.data)
    serializer.append(serializer2.data)

    return Response(serializer)


@api_view(['PUT'],)
@permission_classes((permissions.AllowAny,))
def updateProfile(request, id):
    profile = get_object_or_404(Profile, id=id)
    if request.method == "PUT":
        serializer = UpdatedProfileSerialize(profile, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['message'] = "Profile updated successfully."
            return Response(data=data)
    return Response(serializer.errors)


# Update user API
@api_view(['PUT', ])
@permission_classes((permissions.AllowAny,))
def updateUserInfo(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'PUT':
        serializer = UpdateUserSerialize(user, data=request.data,)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['message'] = "Your info updated successfully..."
            return Response(data=data)
    return Response(serializer.errors)

# Delete user


@api_view(['DELETE', ])
@permission_classes([IsAuthenticated])
def deleteUser(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'DELETE':
        operation = user.delete()
        data = {}
        if(operation):
            data['message'] = "The user deleted successfully..."
        else:
            data['message'] = "The user delete failed..."
    return Response(data=data)


# Create user API
@api_view(['POST', ])
@permission_classes((permissions.AllowAny,))
def register(request):
    if request.method == 'POST':
        serializer = UserCreationSerialize(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(email=serializer.data.get('email')):
                return Response({'email': "Email is alredy exists."}, status=(status.HTTP_406_NOT_ACCEPTABLE))
            serializer.save()
            return Response({'message': 'User created successfully...'})
        else:
            return Response({'username': 'Username is alredy exists.'}, status=(status.HTTP_406_NOT_ACCEPTABLE))


@api_view(['PUT', ])
@permission_classes((permissions.AllowAny,))
def avatarUpdate(request, id):
    profile = get_object_or_404(Profile, id=id)
    profile_serializer = AvatarSerialize(profile, data=request.data)
    if profile_serializer.is_valid():
        profile_serializer.save()
        return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create Post
@api_view(['POST', 'GET'])
@permission_classes((permissions.AllowAny,))
def createPost(request):
    if request.method == 'POST':
        user = User.objects.get(id=1)
        serializer = CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Message has ben send Successfully"), })
        else:
            # return Response({"message": "Error! data Not valide"})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Create new Post"})


@api_view(['PUT'],)
@permission_classes((permissions.AllowAny,))
def updatePost(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == "PUT":
        serializer = PostSerializer(post, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['message'] = _("Post updated successfully.")
            return Response(data=data)
    return Response(serializer.errors)


# Post Languages
@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def postLanguage(request):
    language = Language.objects.all()
    serializer = LanguageSerializer(language, many=True)
    return Response(serializer.data)


# Post Category
@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def postCategoryFilter(request, id):
    language = PostCategory.objects.filter(language=id)
    serializer = PostCategorySerializer(language, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes((permissions.AllowAny, ))
def postDelete(request, id):
    if request.method == 'DELETE':
        post = get_object_or_404(Post, id=id)
        post.delete()
        return Response({'message': _('Post deleted successfully.')})
    else:
        return Response({'message': _('Post deleted Fail.')})


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def getPostForUpdate(request, id):
    post = get_object_or_404(Post, id=id)
    serializer = PostSerializer(post, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPosts(request):
    user = request.user
    posts = user.post_set.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def dashboardTools(request):
    return Response({
        'books': Book.objects.all().count(),
        'posts': Post.objects.all().count(),
        'products': 0
    })


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def createBook(request):
    user = User.objects.get(id=1)
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response({'message': _("Book created successfully...")})
    else:
        print("Not valid.")
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'GET'],)
@permission_classes((permissions.AllowAny,))
def updateBook(request, id):
    book = get_object_or_404(Book, id=id)
    serializer = BookSerializer(book, many=False)
    if request.method == "PUT":
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': _("Book updated successfully.")})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data)


@api_view(['GET', 'POST', 'PUT', 'DELETE'],)
@permission_classes((permissions.AllowAny,))
def postListCrud(request, id):

    # For create
    if request.method == 'POST':
        user = User.objects.get(id=1)
        serializer = PostListSerialiszer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({'message': _("List Created successfully.")})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # For update
    elif request.method == "PUT":
        list = get_object_or_404(PostList, id=id)
        serializer = PostListSerialiszer(list, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': _("List updated successfully.")})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # For Delete
    elif request.method == "DELETE":
        list = get_object_or_404(PostList, id=id)
        list.delete()
        return Response({'messaeg': _("List Deleted successfully.")})
    # For singl list
    else:
        list = get_object_or_404(PostList, id=id)
        serializer = PostListSerialiszer(list, many=False)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def postList(request):
    list = PostList.objects.filter(language__code=request.LANGUAGE_CODE)[0:10]
    serializer = PostListSerialiszer(list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def allPostList(request):
    play_list = PostList.objects.filter(
        language__code=request.LANGUAGE_CODE).order_by('-date')
    paginator = Paginator(play_list, 20)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    list = paginator.get_page(page_number)
    serializer = PostListSerialiszer(list, many=True)

    return Response({'data': serializer.data, 'has_next': list.has_next()})


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def playListPosts(request, id):
    list = Post.objects.filter(list__id=id)
    serializer = PostSerializer(list, many=True)
    return Response(serializer.data)










@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def bookListCategory(request, category):
    books = Book.objects.filter(category__name=category.capitalize())
    paginator = Paginator(books, 24)
    page_number = request.GET.get('page')
    book = paginator.get_page(page_number)
    serializer = BookSerializer(book, many=True)
    return Response({'data': serializer.data, 'has_next': book.has_next()})


#----------------------------- Books -----------


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def booklist(request):
    book_list = Book.objects.filter(language__code=request.LANGUAGE_CODE).order_by('-views')
    paginator = Paginator(book_list, 24)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    serializer = BooksSerializer(books, many=True)
    return Response({'data': serializer.data, 'has_next': books.has_next()})

# Books By Category
@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def bookByCategory(request, slug):
    books = Book.objects.filter(category__slug=slug)
    serializer = BooksSerializer(books, many=True)
    return Response({'data': serializer.data})

# Book Category
@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def bookCategory(request, id):
    language = BookCategory.objects.filter(language=id)
    serializer = BookCategorySerializer(language, many=True)
    return Response(serializer.data)


class BookView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]
        
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        book = get_object_or_404(Book, id=id)
        book.delete()
        return Response({'message': _("Book deleted successfully.")})

    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        book.addView()
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, id):
        book = get_object_or_404(Book, id=id)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)








        
    

    

@api_view(['GET', 'POST', 'PUT', 'DELETE'],)
@permission_classes((permissions.AllowAny,))
def bookListCrud(request, id):

    # For create
    if request.method == 'POST':
        user = User.objects.get(id=1)
        serializer = BookListSerialiszer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({'message': _("List Created successfully.")})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # For update
    elif request.method == "PUT":
        list = get_object_or_404(BookList, id=id)
        serializer = BookListSerialiszer(list, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': _("List updated successfully.")})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # For Delete
    elif request.method == "DELETE":
        list = get_object_or_404(BookList, id=id)
        list.delete()
        return Response({'messaeg': _("List Deleted successfully.")})
    # For singl list
    else:
        list = get_object_or_404(BookList, id=id)
        serializer = BookListSerialiszer(list, many=False)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def bookPlayList(request):
    list = BookList.objects.all()
    serializer = BookListSerialiszer(list, many=True)
    return Response(serializer.data)


# Langauge create / update / delete / get single
@api_view(['GET', 'POST', 'PUT', 'DELETE'],)
@permission_classes((permissions.AllowAny,))
def languageCrud(request, id):

    # For create
    if request.method == 'POST':
        serializer = LanguageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': _("Language Created successfully.")})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # For update
    elif request.method == "PUT":
        lang = get_object_or_404(Language, id=id)
        serializer = LanguageSerializer(lang, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': _("Language updated successfully.")})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # For Delete
    elif request.method == "DELETE":
        lang = get_object_or_404(Language, id=id)
        lang.delete()
        return Response({'messaeg': _("Language Deleted successfully.")})
    # For singl lang
    else:
        lang = get_object_or_404(Language, id=id)
        serializer = LanguageSerializer(lang, many=False)
        return Response(serializer.data)

# Language get list


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def language(request):
    lang = Language.objects.all()
    serializer = LanguageSerializer(lang, many=True)
    return Response(serializer.data)


# Post category CREATE / DELETE / UDPATE / GET Single
@api_view(['GET', 'POST', 'PUT', 'DELETE'],)
@permission_classes((permissions.AllowAny,))
def postCategory(request, id):
    # For create
    if request.method == 'POST':
        serializer = PostCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': _("Post category created successfully.")})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # For update
    elif request.method == "PUT":
        category = get_object_or_404(PostCategory, id=id)
        serializer = PostCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': _("Post Category updated successfully.")})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # For Delete
    elif request.method == "DELETE":
        category = get_object_or_404(PostCategory, id=id)
        category.delete()
        return Response({'messaeg': _("Post Category Deleted successfully.")})
    # For singl category
    else:
        category = get_object_or_404(PostCategory, id=id)
        serializer = PostCategorySerializer(category, many=False)
        return Response(serializer.data)

# Post category get list


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def postCategoryList(request):
    category = PostCategory.objects.all()
    data = []
    for item in category:
        data.append({
            'name': item.name,
            'language': item.language.name,
            'id': item.id
        })
    return Response({'data': data})


@api_view(['POST', 'GET'])
@permission_classes((permissions.AllowAny, ))
def search(request):
    query = request.POST.get('q')
    if query:
        title = Post.objects.filter(title__icontains=query)
        desc = Post.objects.filter(description__icontains=query)
        serializer = PostSerializer(title | desc, many=True)
        return Response(serializer.data)
    else:
        serializer = PostSerializer(Post.objects.all()[0:50], many=True)
        return Response(serializer.data)


@api_view(['POST', 'GET'])
@permission_classes((permissions.AllowAny, ))
def searchBook(request):
    query = request.GET.get('q')
    book = Book.objects.filter(name__icontains=query).order_by('-views')[0:10]
    serializer = BookSerializer(book, many=True)
    return Response(serializer.data)


@api_view(['POST', 'GET'])
@permission_classes((permissions.AllowAny, ))
def trafiq(request):
    ref = request.GET.get('ref')
    profile = get_object_or_404(Profile, slug=ref)
    profile.trafiq = profile.trafiq + 1
    profile.save()
    return Response({'message': profile.slug})





