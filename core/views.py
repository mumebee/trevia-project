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
    print("TOTAL:", qs.count())
    params = request.GET
    
    # 1. Apply filtering via the Engine
    # This uses the 'tags' field as identified in your model schema
    restaurants = engine.filter_queryset(qs, params)
    print(f"Filtered Count: {restaurants.count()}")
    for r in restaurants:
        print(f"Match: {r.name} - {r.country}")

    # 2. Get distinct countries for the filter sidebar
    countries = Restaurant.objects.values_list('country', flat=True).distinct().order_by('country')
    
    # 3. Handle dynamic City filtering based on selected countries
    selected_countries = [c.strip() for c in params.getlist('country') if c.strip()]
    selected_cities = [c.strip() for c in params.getlist('city') if c.strip()]
    
    if selected_countries:
        cities = Restaurant.objects.filter(country__in=selected_countries).values_list('city', flat=True).distinct().order_by('city')
    else:
        cities = Restaurant.objects.values_list('city', flat=True).distinct().order_by('city')

    # 4. Dynamically extract unique cuisine tags for the sidebar
    # We check for both list types and string types to prevent empty sidebars
    raw_tags = Restaurant.objects.values_list('tags', flat=True)
    unique_cuisines = set()
    
    for entry in raw_tags:
        if not entry:
            continue
        
        # If stored as a true list (JSONField)
        if isinstance(entry, list):
            unique_cuisines.update(str(t).strip().lower() for t in entry if t)
        # If stored as a string (common in SQLite stringified arrays)
        elif isinstance(entry, str):
            clean_entry = entry.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
            tags = clean_entry.split(',')
            unique_cuisines.update(t.strip().lower() for t in tags if t)

    # 5. Group results by country for the template carousel
    restaurants_by_country = {}
    for r in restaurants:
        if r.country not in restaurants_by_country:
            restaurants_by_country[r.country] = []
        restaurants_by_country[r.country].append(r)

    return render(request, "core/restaurants.html", {
        "restaurants_by_country": restaurants_by_country.items(),
        "cuisines": sorted(list(unique_cuisines)), 
        "countries": countries,
        "cities": cities,
        "params": params,
        "selected_countries": selected_countries,
        "selected_cities": selected_cities, 
        "selected_tags": params.getlist("tags"),
    })


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
        return JsonResponse({"error": "login_required"}, status=401)

    p_type = request.POST.get("type")
    p_id = request.POST.get("id")

    # Toggle Logic: If exists, delete (unlike); else, create (like)
    existing = SavedPlace.objects.filter(user=request.user, place_type=p_type, place_id=p_id)
    if existing.exists():
        existing.delete()
        return JsonResponse({"status": "unliked"})
    else:
        SavedPlace.objects.create(user=request.user, place_type=p_type, place_id=p_id)
        return JsonResponse({"status": "liked"})

def get_user_itineraries(request):
    if not request.user.is_authenticated:
        return JsonResponse({"itineraries": []})
    itins = list(Itinerary.objects.filter(user=request.user).values('id', 'name'))
    return JsonResponse({"itineraries": itins})

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
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    data = json.loads(request.body)
    itin_id = data.get("itinerary_id")
    new_name = data.get("new_itinerary_name")

    itinerary = None
    if new_name and new_name.strip(): # Create new itinerary
        itinerary = Itinerary.objects.create(user=request.user, name=new_name)
    elif itin_id: # Use existing itinerary
        itinerary = Itinerary.objects.get(id=itin_id, user=request.user)
    
    if not itinerary: # If no itinerary was found or created
        return JsonResponse({"status": "error", "message": "No itinerary selected or new name provided."}, status=400)
    
    ItineraryItem.objects.create(
        itinerary=itinerary,
        place_type=data["type"],
        place_id=data["id"],
        order=itinerary.itineraryitem_set.count()
    )
    return JsonResponse({"status": "success", "itinerary_name": itinerary.name})

@login_required
def itinerary_view(request):
    itineraries = Itinerary.objects.filter(user=request.user).prefetch_related('itineraryitem_set')
    
    structured_data = []
    for itin in itineraries:
        items = []
        for item in itin.itineraryitem_set.all():
            obj = None
            if item.place_type == 'activity':
                obj = Activity.objects.filter(id=item.place_id).first()
            elif item.place_type == 'restaurant':
                obj = Restaurant.objects.filter(id=item.place_id).first()
            
            if obj:
                items.append({
                    "id": item.id,
                    "name": obj.name,
                    "lat": obj.lat,
                    "lng": obj.lng,
                    "city": getattr(obj, 'city', 'N/A'), # Use getattr for safety
                    "description": getattr(obj, 'description', ''),
                    "country": getattr(obj, 'country', ''),
                    "image": getattr(obj, 'image', ''), # Include image for potential future use
                    "type": item.place_type
                })
        structured_data.append({
            "id": itin.id,
            "name": itin.name,
            "items": items
        })

    return render(request, "core/itinerary.html", {"itineraries": structured_data})


def remove_itinerary_item(request, item_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)
    item = ItineraryItem.objects.filter(id=item_id, itinerary__user=request.user).first()
    if item:
        item.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Item not found"}, status=404)

def delete_itinerary(request, itin_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)
    itin = Itinerary.objects.filter(id=itin_id, user=request.user).first()
    if itin:
        itin.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Itinerary not found"}, status=404)

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
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
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