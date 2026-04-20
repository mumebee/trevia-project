from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('registration/', views.registration_view, name='registration'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('explore/', views.explore_view, name='explore'),

    path("like/", views.like_place),
    path("itinerary/", views.add_to_itinerary_activity),

    path("explore/", views.explore_view, name="explore"),

    path("explore/activities/", views.activities_view, name="activities"),
    path("explore/restaurants/", views.restaurants_view, name="restaurants"),
    path("explore/hotels/", views.hotels_view, name="hotels"),
]