from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from .models import User
from .forms import CustomUserCreationForm

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('reviews:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/form.html', context)

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('reviews:index')
    else:
        form = AuthenticationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/form.html', context)

@login_required
def logout(request):
    auth_logout(request)
    return redirect('reviews:index')

@login_required
def profile(request, username):
    person = get_object_or_404(User, username=username)
    context = {
        'person' : person,
    }
    return render(request, 'accounts/profile.html', context)

def follow(request, username):
    person = get_object_or_404(User, username=username)
    user = request.user
    if user != person:
        if user in person.followers.all():
            person.followers.remove(user)
        else:
            person.followers.add(user)
    return redirect('accounts:profile', person.username)