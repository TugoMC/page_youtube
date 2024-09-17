from django.urls import path
from . import views

urlpatterns = [
    path('videos/', views.youtube_videos_view, name='youtube_videos'),
    path('video/<str:video_id>/', views.video_detail_view, name='video_detail'),
    
]
