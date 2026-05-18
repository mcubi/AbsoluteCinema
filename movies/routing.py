# WEBSOCKET URL CONFIG

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/reviews/(?P<movie_id>\d+)/$', consumers.ReviewConsumer.as_asgi()),
]