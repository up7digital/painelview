from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/painel/(?P<painel_id>\d+)/$", consumers.PainelConsumer.as_asgi()),
]
