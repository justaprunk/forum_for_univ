from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login
from .models import *


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

    return render(request, 'forum_app/article.html',
                  context={'article': article,
                           'is_mine': article.author == request.user})


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
