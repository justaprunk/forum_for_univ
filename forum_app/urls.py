from .views import *
from django.urls import path

urlpatterns = [
    path('profile/', profile, name='forum_profile'),
    path('profile/<name>', profile, name='forum_profile')
]
