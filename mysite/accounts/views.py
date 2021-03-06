from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout
from .models import User

# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect('articles:index')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('articles:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form' : form
    }
    return render(request, 'accounts/form.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect('articles:index')
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        # AuthenticationForm은 ModelForm이 아닌 Form 상속
        # 별도로 정의된 모델이 없다는 뜻
        # 그래서 넘겨주는 인자가 달라진다
        if form.is_valid():
            # 로그인은 DB에 뭔가 작성하는 것은 동일하지만, 연결된 모델이 있는건 아니다
            # 세션과 유저 정보를 확인해야한다
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or 'articles:index')
    else:
        form = AuthenticationForm()
    context = {
        'form' : form
    }
    return render(request, 'accounts/form.html', context)

def logout(request):
    auth_logout(request)
    return redirect('accounts:signup')

@require_POST
def delete(request):
    request.user.delete()
    return redirect('articles:index')

@login_required
def update(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('articles:index')
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'form' : form
    }
    return render(request, 'accounts/form.html', context)

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('articles:index')
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'form' : form
    }
    return render(request, 'accounts/form.html', context)

def profile(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    context = {
        'person' : person
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def follow(request, user_pk):
    person = get_object_or_404(get_user_model(), pk=user_pk) #person은 profile주인
    if request.user in person.followers.all(): #request.user는 요청하는 나
        person.followers.remove(request.user)
    else:
        person.followers.add(request.user)
    return redirect('accounts:profile', person.username)