from django.urls import re_path
from .consumers import OCPPWebSocketConsumer

websocket_urlpatterns = [
    re_path(r'ws/ocpp/(?P<charger_id>\w+)/$', OCPPWebSocketConsumer.as_asgi()),
]
