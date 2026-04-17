from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def index_view(request):
    return render(request, 'core/index.html')

def about_view(request):
    return render(request, 'core/about.html')

def contacts_view(request):
    return render(request, 'core/contacts.html')

def explore_view(request):
    return render(request , "core/explore.html")

def registration_view(request):
    if request.method == 'POST':
        print(request.POST)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You successfully registered!')
            return redirect('login')
        else:
            print("Form registration errors:", form.errors)
    else:
        form = RegistrationForm()

    context = {
        'form' : form
    }
    return render(request, 'core/registration.html', context)

def login_view(request):
    if request.method == 'POST':
        print(request.POST)
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.info(request, f'{user.username} you successfully logged in!')
            return redirect('home')
        else:
            print("Form login errors:", form.errors)
    else:
        form = LoginForm()

    context = {
        'form' : form
    }
    return render(request, 'core/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

def profile_view(request):
    return render(request, 'core/profile.html')