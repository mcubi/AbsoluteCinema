from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_devolution) # on-click execute the homepage function
]