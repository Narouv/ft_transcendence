from django.urls import path

from . import views

urlpatterns = [
    path("", views.game_site, name="index"),
    path("embed", views.game_window, name="index"),
]