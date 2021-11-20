from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import *
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, AbstractUser


class UserManager(BaseUserManager):
    def create_superuser(self, username, password):
        u = self.create_user(username, password)
        u.is_superuser = True
        u.save()
        return u

    def create_user(self, username, password):
        u = User(username=username)
        u.set_password(password)
        u.save()
        return u


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True)
    profile_photo = models.ImageField(upload_to='profiles/', default=None,
                                      null=True, blank=True)
    is_staff = True
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-username']

    objects = UserManager()


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    deploy_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    title_image = models.ImageField(default=None, upload_to='articles/',
                                    null=True, blank=True)
    text = models.CharField(max_length=500)

    class Meta:
        ordering = ['author', '-deploy_time']

    def __str__(self):
        return f"{self.title}"

    def rating(self):
        rating = 0
        for activity in Activity.objects.filter(article_parent=self):
            if activity.activity_type == 'L':
                rating += 1
            elif activity.activity_type == 'D':
                rating -= 1
        return rating


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article_parent = models.ForeignKey(Article, on_delete=models.CASCADE,
                                       null=True, blank=True)
    comment_parent = models.ForeignKey('Comment', on_delete=models.CASCADE,
                                       null=True, blank=True)
    text = models.CharField(max_length=500)
    deploy_time = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(default=None, upload_to='attachments/',
                                  null=True, blank=True)

    def __str__(self):
        return f"comment for " \
               f"{self.article_parent if self.article_parent else 'another comment'}"

    def rating(self):
        rating = 0
        for activity in Activity.objects.filter(comment_parent=self):
            if activity.activity_type == 'L':
                rating += 1
            elif activity.activity_type == 'D':
                rating -= 1
        return rating

    def clean(self):
        if (self.comment_parent and self.article_parent) or \
                (not self.comment_parent and not self.article_parent):
            raise ValidationError("Comment xor article is required.")
        super().clean()

    class Meta:
        ordering = ['-deploy_time']


class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('V', 'View'),
        ('L', 'Like'),
        ('D', 'Dislike'),
    )
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article_parent = models.ForeignKey(Article, on_delete=models.CASCADE,
                                       null=True, blank=True)
    comment_parent = models.ForeignKey(Comment, on_delete=models.CASCADE,
                                       null=True, blank=True)
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)

    def __str__(self):
        return f"{self.activity_type}"

    def clean(self):
        if (self.comment_parent and self.article_parent) or \
                (not self.comment_parent and not self.article_parent):
            raise ValidationError("Comment xor article is required.")
        super().clean()

    class Meta:
        ordering = ['author', '-activity_type']
        unique_together = (('author', 'article_parent',
                            'comment_parent', 'activity_type'),)
