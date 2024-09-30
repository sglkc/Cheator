from django.urls import path
from . import consumers, views

urlpatterns = [
    path('ws/', consumers.WebRtcConsumer.as_asgi()),
    path('', views.index, name='rtc_index')
]
