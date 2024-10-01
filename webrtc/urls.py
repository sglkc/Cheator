from django.urls import path
from . import views

urlpatterns = [
    path('class/', views.classroom, name='rtc_classroom'),
    path('supervisor/', views.supervisor, name='rtc_supervisor'),
]
