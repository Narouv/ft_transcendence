from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
#from . import consumer

urlpatterns = [
	path("", views.single_page_app, name="app-base"),
	path("views/<str:view>/", views.SubViewManger.as_view(), name="viewMngr"),
]