from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Activity, Restaurant, Hotel, SavedPlace, Itinerary, ItineraryItem
from .filters import FilterEngine
from .forms import RegistrationForm, LoginForm


# pages
def index_view(request):
    return render(request, "core/index.html")


def explore_view(request):
    activities = list(Activity.objects.values())
    restaurants = list(Restaurant.objects.values())
    hotels = list(Hotel.objects.values())

    return render(request, "core/explore.html", {
        "activities": activities,
        "restaurants": restaurants,
        "hotels": hotels,
    })


# =========================
# FILTERED LISTS
# =========================
def activities_view(request):
    engine = FilterEngine()

    qs = Activity.objects.all()
    params = request.GET

    activities = engine.filter_queryset(qs, params)

    return render(request, "core/activities.html", {"activities": activities})


def restaurants_view(request):
    engine = FilterEngine()

    qs = Restaurant.objects.all()
    restaurants = engine.filter_queryset(qs, request.GET)

    return render(request, "core/restaurants.html", {"restaurants": restaurants})


def hotels_view(request):
    engine = FilterEngine()

    qs = Hotel.objects.all()
    hotels = engine.filter_queryset(qs, request.GET)

    return render(request, "core/hotels.html", {"hotels": hotels})


# =========================
# LIKE SYSTEM
# =========================
def like_place(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"})

    SavedPlace.objects.create(
        user=request.user,
        place_type=request.POST.get("type"),
        place_id=request.POST.get("id")
    )

    return JsonResponse({"status": "saved"})


def saved_places_view(request):
    saved = SavedPlace.objects.filter(user=request.user)

    return render(request, "core/saved.html", {"saved": saved})


# =========================
# ITINERARY
# =========================
def create_itinerary(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"})

    itinerary = Itinerary.objects.create(
        user=request.user,
        name=request.POST.get("name", "My Trip")
    )

    return JsonResponse({"id": itinerary.id})


import json

def add_to_itinerary(request):
    if request.method == "POST":
        data = json.loads(request.body)

        item = {
            "type": data["type"],
            "id": data["id"],
            "name": data["name"],
            "lat": data["lat"],
            "lng": data["lng"]
        }

        itinerary = request.session.get("itinerary", [])
        itinerary.append(item)
        request.session["itinerary"] = itinerary

        return JsonResponse({"status": "ok"})


def itinerary_view(request):
    itinerary = request.session.get("itinerary", [])
    return render(request, "core/itinerary.html", {
        "itinerary": itinerary
    })



def registration_view(request):
    form = RegistrationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("login")

    return render(request, "core/registration.html", {"form": form})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if form.is_valid():
        login(request, form.get_user())
        return redirect("home")

    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")



@login_required
def profile_view(request):
    return render(request, "core/profile.html")

def about_view(request):
    return render(request, "core/about.html")

def contacts_view(request):
    return render(request, "core/contacts.html")