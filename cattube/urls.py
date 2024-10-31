from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

import cattube.core.api
from cattube.core import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Website
    path('', views.VideoListView.as_view(), name='home'),
    path('search', views.VideoSearchView.as_view(), name='search'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('upload', views.VideoCreateView.as_view(), name='upload'),

    path('videos/result', views.VideoResultView.as_view(), name='result'),
    path('videos/<str:video_id>', views.VideoDetailView.as_view(), name='watch'),
    path('videos/delete/<str:video_id>', views.VideoDeleteView.as_view(), name='delete'),

    # REST API
    path('api/videos/delete', cattube.core.api.delete_videos),
    path('api/videos/index', cattube.core.api.index_videos),
    path('api/videos/status', cattube.core.api.get_status),
    path('api/videos/', cattube.core.api.receive_notification_from_transcoder, name='notification'),
    path('api/videos/<str:video_id>', cattube.core.api.video_detail, name='video_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
