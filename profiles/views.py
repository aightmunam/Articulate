from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import LoginForm, SignupForm, UserChangeForm
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


@login_required
def profile_logout(request):
    if not request.user.is_authenticated:
        redirect("profiles:profile_login")
    logout(request)
    return redirect("articles:article_list")


def profile_detail(request, username):
    profile = get_object_or_404(Profile, username=username)
    articles = profile.get_authored_articles()
    return render(request, 'profiles/detail.html', context={"profile": profile,
                                                            "articles": articles,
                                                            "favorite": False})


def profile_favorites(request, username):
    profile = get_object_or_404(Profile, username=username)
    articles = profile.get_favorite_articles()
    return render(request, 'profiles/detail.html', context={"profile": profile,
                                                            "articles": articles,
                                                            "favorite": True})


@login_required
def profile_follow(request, username, follow=True):
    current_user = request.user
    if follow:
        current_user.follow_profile(username=username)
    else:
        current_user.unfollow_profile(username=username)
    return redirect("profiles:profile_detail", username=username)


@login_required
def profile_edit(request, username):
    current_user = request.user

    form = UserChangeForm(data=request.POST or None, files=request.FILES or None, instance=current_user)
    if request.method == 'POST':
        if form.is_valid():
            cleaned_data = form.cleaned_data
            current_user.first_name = cleaned_data["first_name"]
            current_user.last_name = cleaned_data["last_name"]
            current_user.bio = cleaned_data["bio"]
            current_user.display.file = cleaned_data["display"]
            current_user.set_password(cleaned_data["password"])
            current_user.save()
            authenticate(request, username=current_user.username, password=current_user.password)
            login(request, current_user)
            redirect("profiles:profile_detail", username=username)

    else:
        form = UserChangeForm(initial={'first_name': current_user.first_name,
                                       'last_name': current_user.last_name,
                                       'bio': current_user.bio,
                                       'display': current_user.display})
    return render(request, "profiles/edit_profile.html", context={"profile_form": form})
