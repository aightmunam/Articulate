from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from .forms import LoginForm, SignupForm
from .models import Profile

# Create your views here.
def profile_login(request):
    if request.user.is_authenticated:
        return redirect("articles:article_list")

    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect("articles:article_list")
    return render(request, 'profiles/login.html', context={'login_form': form})


def profile_register(request):
    if request.user.is_authenticated:
        return redirect("articles:article_list")

    form = SignupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("profiles:profile_detail", username=user.username)

    return render(request, 'profiles/register.html', context={"register_form": form})


def profile_logout(request):
    if not request.user.is_authenticated:
        redirect("profiles:profile_login")
    logout(request)
    return redirect("articles:article_list")


def profile_detail(request, username):
    profile = get_object_or_404(Profile, username=username)
    articles = profile.articles.all()
    return render(request, 'profiles/detail.html', context={"profile": profile,
                                                            "articles": articles,
                                                            "favorite": False})


def profile_favorites(request, username):
    profile = get_object_or_404(Profile, username=username)
    articles = profile.starred_articles.all()
    return render(request, 'profiles/detail.html', context={"profile": profile,
                                                            "articles": articles,
                                                            "favorite": True})


def profile_follow(request, username):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    current_user = request.user
    if current_user.followed_profiles.filter(username=username).exists():
        current_user.followed_profiles.remove(current_user.followed_profiles.get(username=username))
    else:
        current_user.followed_profiles.add(Profile.objects.get(username=username))
    return redirect("profiles:profile_detail", username=username)
