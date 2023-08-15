from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

# Post
admin.site.register(PostComment)


@admin.register(PostCategory)
class PostCategoryIMportExport(ImportExportModelAdmin):
    pass


@admin.register(PostList)
class PostListIMportExport(ImportExportModelAdmin):
    pass



@admin.register(Post)
class PostIMportExport(ImportExportModelAdmin):
    pass

@admin.register(Book)
class BookIMportExport(ImportExportModelAdmin):
    pass


@admin.register(Subscribe)
class SubscribeIMportExport(ImportExportModelAdmin):
    pass





# Book

@admin.register(BookCategory)
class BookCategoryIMportExport(ImportExportModelAdmin):
    pass


admin.site.register(BookList)
admin.site.register(CommentBook)

# other Tols
admin.site.register(Contact)
admin.site.register(IpModel)



# Page
@admin.register(Page)
class PageIMportExport(ImportExportModelAdmin):
    pass


# Language
@admin.register(Language)
class LanguageIMportExport(ImportExportModelAdmin):
    pass


@admin.register(Author)
class AuthorImportExport(ImportExportModelAdmin):
    pass


@admin.register(Type)
class BookTypeImportExport(ImportExportModelAdmin):
    pass


# Video
@admin.register(Video)
class VideoImportExport(ImportExportModelAdmin):
    pass


@admin.register(Quality)
class QualityImportExport(ImportExportModelAdmin):
    pass


@admin.register(VideoComment)
class VideoCommentImportExport(ImportExportModelAdmin):
    pass




