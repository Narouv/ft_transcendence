from django.urls import path

from . import views

urlpatterns = [
    path("score/", views.Web3Score.as_view(), name="index"),
]