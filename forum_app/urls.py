from .views import *
from django.urls import path

urlpatterns = [
    path('profile/', profile, name='forum_profile'),
    path('profile/<name>', profile),
    path('profile/<name>/remove', remove_profile, name='remove_profile'),
    path('article/add', article_editor, name='add_article'),
    path('article/<id>', article_view, name='article'),
    path('article/<id>/edit', article_editor, name='edit_article'),
    path('article/<id>/remove', article_remove, name='remove_article'),
    path('article/<id>/<activity>', article_activity, name='activity_article')

]
