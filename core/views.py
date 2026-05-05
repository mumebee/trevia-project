from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Activity, Restaurant, Hotel, SavedPlace, Itinerary, ItineraryItem
from .filters import ActivityFilterEngine, RestaurantFilterEngine, HotelFilterEngine
from .forms import RegistrationForm, LoginForm


# pages
def index_view(request):
    form = RegistrationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("/")

    return render(request, "core/index.html", {"form": form})





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
    engine = ActivityFilterEngine()
    qs = Activity.objects.all()
    params = request.GET
    activities = engine.filter_queryset(qs, params)

    # Get dynamic filter options
    countries = Activity.objects.values_list('country', flat=True).distinct().order_by('country')

    selected_countries = params.getlist('country')
    selected_cities = params.getlist('city')

    if selected_countries:
        cities = Activity.objects.filter(country__in=selected_countries).values_list('city', flat=True).distinct().order_by('city')
    else:
        cities = Activity.objects.values_list('city', flat=True).distinct().order_by('city')

    # Dynamically extract unique categories for the filter sidebar
    raw_categories = Activity.objects.values_list('category', flat=True)
    unique_categories = set()
    for cat_list in raw_categories:
        # Ensure we only process lists and ignore None/bad data
        if isinstance(cat_list, list):
            # Normalize to lowercase and strip whitespace to prevent "Shopping" vs "shopping" duplicates
            unique_categories.update(str(c).strip().lower() for c in cat_list if c)


    # Group current results by country
    activities_by_country = {}
    for a in activities:
        if a.country not in activities_by_country:
            activities_by_country[a.country] = []
        activities_by_country[a.country].append(a)

    return render(request, "core/activities.html", {
        "activities_by_country": activities_by_country.items(),
        "categories": sorted(list(unique_categories)),
        "countries": countries,
        "cities": cities,
        "params": params,
        "selected_tags": params.getlist("tags"),
        "selected_countries": selected_countries,
        "selected_cities": selected_cities,
    })

def restaurants_view(request):
    engine = RestaurantFilterEngine()

    qs = Restaurant.objects.all()
    restaurants = engine.filter_queryset(qs, request.GET)

    return render(request, "core/restaurants.html", {"restaurants": restaurants})
    


# def hotels_view(request):
#     engine = HotelFilterEngine()

#     qs = Hotel.objects.all()
#     hotels = engine.filter_queryset(qs, request.GET)

#     return render(request, "core/hotels.html", {"hotels": hotels})
def hotels_view(request):
    engine = HotelFilterEngine()
    qs = Hotel.objects.all()
    params = request.GET
    hotels = engine.filter_queryset(qs, params)

    countries = Hotel.objects.values_list('country', flat=True).distinct().order_by('country')
    selected_countries = params.getlist('country')
    selected_cities = params.getlist('city')

    if selected_countries:
        cities = Hotel.objects.filter(country__in=selected_countries).values_list('city', flat=True).distinct().order_by('city')
    else:
        cities = Hotel.objects.values_list('city', flat=True).distinct().order_by('city')

    hotels_by_country = {}
    for h in hotels:
        if h.country not in hotels_by_country:
            hotels_by_country[h.country] = []
        hotels_by_country[h.country].append(h)

    return render(request, "core/hotels.html", {
        "hotels_by_country": hotels_by_country.items(),
        "countries": countries,
        "cities": cities,
        "params": params,
        "selected_countries": selected_countries,
        "selected_cities": selected_cities,
    })


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


# AJAX endpoint for cascading filters
def get_cities_ajax(request):
    countries = request.GET.getlist('countries[]')
    if countries:
        cities = Activity.objects.filter(country__in=countries).values_list('city', flat=True).distinct().order_by('city')
    else:
        cities = Activity.objects.values_list('city', flat=True).distinct().order_by('city')
    return JsonResponse({'cities': list(cities)})

# hotels end point
def get_hotel_cities_ajax(request):
    countries = request.GET.getlist('countries[]')
    if countries:
        cities = Hotel.objects.filter(country__in=countries).values_list('city', flat=True).distinct().order_by('city')
    else:
        cities = Hotel.objects.values_list('city', flat=True).distinct().order_by('city')
    return JsonResponse({'cities': list(cities)})

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