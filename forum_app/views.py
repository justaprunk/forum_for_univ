from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import login
from .models import User


def profile(request, name=None):
    if request.method == "GET":
        if name is None or name == request.user.username:
            subj_user = request.user
            it_is_i = True
        else:
            try:
                subj_user = User.objects.get(username=name)
                it_is_i = False
            except:
                return redirect('/auth/login/')

    else:  # POST
        if request.user.is_anonymous:
            subj_user = User.objects.create_user(request.POST['username'], request.POST['password'])
            login(request, subj_user, 'django.contrib.auth.backends.ModelBackend')
        else:
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

    return render(
        request,
        'forum_app/profile.html',
        context={'user': {'username': subj_user.username,
                          'photo': photo,
                          'it_is_i': it_is_i}})
