from django.urls import path
from .views import login_view, home_view, dashboard_view, index_view, logout_view

urlpatterns = [
    path('', index_view, name='index'),
    path('login/', login_view, name='login'),
    path('home/', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
]
