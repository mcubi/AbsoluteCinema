"""
URL configuration for absolute_cinema project.
DJANGO URL DOCUMETATION:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""


from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # administrator url pattern
    path('', include('movies.urls')) # including the urlpatterns from movies - app
]
