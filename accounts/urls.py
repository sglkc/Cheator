from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index_view, name='index'),
    path('login/', login_view, name='login'),
    path('home/', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('open-class/<int:class_id>/', open_class_view, name='open_class'),
    path('close_class/', close_class_view, name='close_class'),
    path('join_class/', join_class_view, name='join_class'),
    path('class/room/<str:meeting_url>/', class_room_view, name='class_room'),
    path('process_frame/', process_frame, name='process_frame'),
    path('video-feed/', video_feed_view, name='video_feed'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
