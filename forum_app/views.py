from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login
from .models import *

__all__ = ["profile", "remove_profile", "article_view", "article_editor",
           "article_remove", "article_comment", "article_activity", "comment_activity",
           "comment_remove", "comment_comment", "all_users", "all_articles"]


def render_error(request, msg):
    return render(request, 'forum_app/error.html',
                  context={'msg': msg})


def profile(request, name=None):
    if not name:
        name = request.user.username
    if request.method == "GET":
        if request.user.is_anonymous:
            return redirect('/auth/login/')
        elif name == request.user.username:
            subj_user = request.user
            it_is_i = True
        else:
            try:
                subj_user = User.objects.get(username=name)
                it_is_i = False
            except:
                return render_error(request, f"Пользователя '{name}' не существует")
    else:  # POST
        if request.user.is_anonymous:
            subj_user = User.objects.create_user(request.POST['username'], request.POST['password'])
            login(request, subj_user, 'django.contrib.auth.backends.ModelBackend')
        else:
            if name != request.user.username:
                return render_error(request, 'No Access')
            subj_user = request.user
            subj_user.username = request.POST['username']
            if request.POST['password']:
                subj_user.set_password(request.POST['password'])
            if request.FILES.get('photo'):
                subj_user.profile_photo = request.FILES['photo']
            subj_user.save()
        it_is_i = True

    try:
        photo = subj_user.profile_photo.url
    except:
        photo = ''

    articles = Article.objects.filter(author=subj_user)

    return render(
        request,
        'forum_app/profile.html',
        context={'user': {'username': subj_user.username,
                          'photo': photo,
                          'it_is_i': it_is_i},
                 'articles': articles})


def remove_profile(request, name):
    if name != request.user.username:
        return render_error(request, 'No Access')
    try:
        subj_user = User.objects.get(username=name)
    except:
        return render_error(request, f"Пользователя '{name}' не существует")
    subj_user.delete()
    return redirect('/auth/login/')


def article_view(request, id):
    try:
        article = Article.objects.get(id=id)
    except:
        return render_error(request, "Статья не существует")

    try:
        activity = Activity.objects.get(author=request.user,
                                        article_parent=article).activity_type
    except:
        activity = None

    return render(request, 'forum_app/article.html',
                  context={'article': article,
                           'is_mine': article.author == request.user,
                           'activity': activity,
                           #'comments': Comment.objects.filter(article_parent=article),
                           'user': request.user})


def article_editor(request, id=None):
    article = None
    if id:
        try:
            article = Article.objects.get(id=id)
        except:
            return render_error(request, "Статья не существует")
    if request.method == 'GET':
        return render(request, 'forum_app/edit_article.html', context={'article': article})
    else:
        if not article:
            article = Article(author=request.user)
        if article.author != request.user:
            return render_error(request, 'Это не ваша статья')
        else:
            article.title = request.POST.get('title', article.title)
            article.text = request.POST.get('text', article.title)
            article.title_image = request.FILES.get('image', article.title_image)
            article.save()
            return redirect(f'/forum/article/{article.id}')


def article_remove(request, id):
    try:
        article = Article.objects.get(id=id)
    except:
        return render_error(request, "Статья не существует")
    if article.author != request.user:
        return render_error(request, 'Это не ваша статья')
    else:
        article.delete()
        return redirect('/forum/profile')


def article_activity(request, id, activity):
    try:
        article = Article.objects.get(id=id)
    except:
        return render_error(request, "Статья не существует")
    if activity not in ('L', 'D'):
        return render_error(request, 'Неизвестный тип активности')
    try:
        activity_obj = Activity.objects.get(author=request.user,
                                            article_parent=article)
    except:
        activity_obj = Activity(author=request.user, article_parent=article)

    if activity_obj.activity_type == activity:
        activity_obj.delete()
    else:
        activity_obj.activity_type = activity
        activity_obj.save()

    return redirect(f'/forum/article/{id}')


def article_comment(request, id):
    try:
        article = Article.objects.get(id=id)
    except:
        return render_error(request, "Статья не существует")
    if request.user.is_anonymous:
        return redirect('/auth/login/')
    else:
        Comment.objects.create(article_parent=article, author=request.user,
                               text=request.POST['comment'])
        return redirect(f'/forum/article/{id}')


def comment_activity(request, id, activity):
    try:
        comment = Comment.objects.get(id=id)
    except:
        return render_error(request, "Комментарий не существует")
    if activity not in ('L', 'D'):
        return render_error(request, 'Неизвестный тип активности')
    try:
        activity_obj = Activity.objects.get(author=request.user,
                                            comment_parent=comment)
    except:
        activity_obj = Activity(author=request.user, comment_parent=comment)

    if activity_obj.activity_type == activity:
        activity_obj.delete()
    else:
        activity_obj.activity_type = activity
        activity_obj.save()

    while not comment.article_parent:
        comment = comment.comment_parent

    return redirect(f'/forum/article/{comment.article_parent.id}')


def comment_remove(request, id):
    try:
        comment = Comment.objects.get(id=id)
    except:
        return render_error(request, "Комментарий не существует")
    if comment.author != request.user:
        return render_error(request, 'Это не ваш комментарий')
    else:

        comment.delete()

        while not comment.article_parent:
            comment = comment.comment_parent

        return redirect(f'/forum/article/{comment.article_parent.id}')


def comment_comment(request, id):
    try:
        comment = Comment.objects.get(id=id)
    except:
        return render_error(request, "Комментарий не существует")
    if request.user.is_anonymous:
        return redirect('/auth/login/')
    else:
        Comment.objects.create(comment_parent=comment, author=request.user,
                               text=request.POST['comment'])
        while not comment.article_parent:
            comment = comment.comment_parent

        return redirect(f'/forum/article/{comment.article_parent.id}')


def all_users(request):
    page_size = int(request.GET.get("pagesize", 10))
    page = int(request.GET.get("page", 0))
    users = User.objects.all()

    def users_sort(u_set):
        return sorted(u_set, key=lambda x: x.comments.count(), reverse=True)

    sort_users = users_sort(users)[page*page_size:(page + 1) * page_size]
    return render(request, "alls/users.html",
                  context={"users": sort_users,
                           "count": users.count(),
                           "page": page,
                           "pagesize": page_size, })


def all_articles(request):
    page_size = int(request.GET.get("pagesize", 10))
    page = int(request.GET.get("page", 0))
    articles = Article.objects.all()

    def article_sort(u_set):
        return sorted(u_set, key=lambda x: x.rating, reverse=True)

    sort_articles = article_sort(articles)[page*page_size:(page + 1) * page_size]
    return render(request, "alls/articles.html",
        context={"articles": sort_articles,
                 "count": articles.count(),
                 "page": page,
                 "pagesize": page_size, })