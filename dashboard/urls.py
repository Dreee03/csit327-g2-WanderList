from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path("add-destination/", views.add_destination, name="add_destination"),
    path('my-lists/', views.my_lists_view, name='my_lists'),
]
