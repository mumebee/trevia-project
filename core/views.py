from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.http import JsonResponse
from .models import SavedPlace
from .models import Activity, Restaurant, Hotel
from .filters import FilterEngine

def index_view(request):
    return render(request, 'core/index.html')

def about_view(request):
    return render(request, 'core/about.html')

def contacts_view(request):
    return render(request, 'core/contacts.html')

def explore_view(request):
    return render(request, "core/explore.html")

def add_to_itinerary_activity(request):
    return render(request, "core/itinerary.html")

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


def like_place(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"})

    place_type = request.POST.get("type")
    place_id = request.POST.get("id")

    SavedPlace.objects.create(
        user=request.user,
        place_type=place_type,
        place_id=place_id
    )

    return JsonResponse({"status": "saved"})


def saved_places_view(request):
    saved = SavedPlace.objects.filter(user=request.user)
    return render(request, "core/saved.html", {"saved": saved})


def activities_view(request):
    engine = FilterEngine()

    params = {
        "country": request.GET.get("country"),
        "city": request.GET.get("city"),
        "min_price": request.GET.get("min_price"),
        "max_price": request.GET.get("max_price"),
        "tags": request.GET.getlist("tags"),
    }

    activities = engine.filter_activities(params)

    return render(request, "core/activities.html", {
        "activities": activities
    })


def restaurants_view(request):
    qs = Restaurant.objects.all()

    if request.GET.get("country"):
        qs = qs.filter(country=request.GET["country"])

    if request.GET.get("min_price"):
        qs = qs.filter(price__gte=request.GET["min_price"])

    if request.GET.get("max_price"):
        qs = qs.filter(price__lte=request.GET["max_price"])

    return render(request, "core/restaurants.html", {
        "restaurants": qs
    })


def hotels_view(request):
    qs = Hotel.objects.all()

    if request.GET.get("country"):
        qs = qs.filter(country=request.GET["country"])

    if request.GET.get("min_price"):
        qs = qs.filter(price__gte=request.GET["min_price"])

    if request.GET.get("max_price"):
        qs = qs.filter(price__lte=request.GET["max_price"])

    return render(request, "core/hotels.html", {
        "hotels": qs
    })