from django.contrib import admin
from .models import User, Article, Activity, Comment

admin.site.register(User)
admin.site.register(Article)
admin.site.register(Activity)
admin.site.register(Comment)
