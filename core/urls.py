from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),
        path('about/', views.about_view, name='about'),
    path('profile/', views.profile_view, name='profile'),
    path('contacts/', views.contacts_view, name='contacts'),

    path('explore/', views.explore_view, name='explore'),
    path('explore/activities/', views.activities_view, name='activities'),
    path('explore/restaurants/', views.restaurants_view, name='restaurants'),
    path('explore/hotels/', views.hotels_view, name='hotels'),
    path('ajax/get-cities/', views.get_cities_ajax, name='get_cities_ajax'),
    path("add-to-itinerary/", views.add_to_itinerary),
    path("itinerary/", views.itinerary_view, name="itinerary"),
    path('like/', views.like_place),
    path('saved/', views.saved_places_view),

    path('itinerary/', views.itinerary_view),
    path('itinerary/create/', views.create_itinerary),
    path('itinerary/add/', views.add_to_itinerary),

    path('registration/', views.registration_view),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    # urls.py — add this line
    path('ajax/get-hotel-cities/', views.get_hotel_cities_ajax, name='get_hotel_cities_ajax')
]