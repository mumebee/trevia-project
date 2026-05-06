from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),

    # path('about/', views.about_view, name='about'),
    # path('profile/', views.profile_view, name='profile'),
    # path('contacts/', views.contacts_view, name='contacts'),

    path('explore/', views.explore_view, name='explore'),
    path('explore/activities/', views.activities_view, name='activities'),
    path('explore/restaurants/', views.restaurants_view, name='restaurants'),
    path('explore/hotels/', views.hotels_view, name='hotels'),
    path('ajax/get-cities/', views.get_cities_ajax, name='get_cities_ajax'),
    path('ajax/get-itineraries/', views.get_user_itineraries, name='get_user_itineraries'),
    path("add-to-itinerary/", views.add_to_itinerary, name="add_to_itinerary"),
    path("itinerary/", views.itinerary_view, name="itinerary"),
    path("itinerary/remove-item/<int:item_id>/", views.remove_itinerary_item, name="remove_item"),
    path("itinerary/delete/<int:itin_id>/", views.delete_itinerary, name="delete_itinerary"),
    path('liked/', views.liked_view, name='liked_places'),
    path('ajax/toggle-like/', views.toggle_like, name='toggle_like'),
    path('saved/', views.saved_places_view, name='saved_places'),

    path('registration/', views.registration_view, name='registration'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # urls.py — add this line
    path('ajax/get-hotel-cities/', views.get_hotel_cities_ajax, name='get_hotel_cities_ajax')
]