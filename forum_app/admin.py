from django.contrib import admin
from .models import User, Article, Activity, Comment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', "profile_photo"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "rating", "title_image"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["author", "activity_type", "comment_parent",
                    'article_parent']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "rating", "comment_parent", 'article_parent']

