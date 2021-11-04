from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError


class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=64)
    profile_photo = models.ImageField(upload_to = 'profiles/', default=None, null=True,
        blank=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-username']


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    deploy_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    title_image = models.ImageField(default=None, upload_to = 'articles/', null=True,
        blank=True)
    text = models.CharField(max_length=500)

    class Meta:
        ordering = ['author', '-deploy_time']

    def __str__(self):
        return f"{self.title} Author: {self.author.username if self.author else None}, " \
               f"ID: {self.id}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article_parent = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    comment_parent = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True,
        blank=True)
    text = models.CharField(max_length=500)
    deploy_time = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(default=None, upload_to = 'attachments/', null=True,
        blank=True)

    def __str__(self):
        return f"{self.author.username if self.author else None} comments " \
               f"{self.article_parent.__str__() if self.article_parent else self.comment_parent.__str__() if self.comment_parent else None}"


    def clean(self):
        if (self.comment_parent and self.article_parent) or (not self.comment_parent and not self.article_parent):
            raise ValidationError("Comment xor article is required.")

    class Meta:
        ordering = ['article_parent', 'comment_parent', '-deploy_time']


class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('V', 'View'),
        ('L', 'Like'),
        ('D', 'Dislike'),
    )
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article_parent = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    comment_parent = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)

    def __str__(self):
        return f"{self.author.username if self.author else None} {self.activity_type} " \
               f"{self.article_parent.__str__() if self.article_parent else self.comment_parent.__str__() if self.comment_parent else None}"

    def clean(self):
        if (self.comment_parent and self.article_parent) or (not self.comment_parent and not self.article_parent):
            raise ValidationError("Comment xor article is required.")

    class Meta:
        ordering = ['author', '-activity_type']
        unique_together = (('author', 'article_parent', 'comment_parent', 'activity_type'),)
