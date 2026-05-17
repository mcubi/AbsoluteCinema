"""
URL configuration for absolute_cinema project.
DJANGO URL DOCUMETATION:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # administrator url pattern
    path('', include('movies.urls')), # including urlpatterns from movies - app
    path('users/', include('users.urls')), # including urlpatterns from users - app
]

# serving multimedia files in development mode (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)