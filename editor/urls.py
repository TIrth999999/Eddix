from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<str:room_code>/', views.room, name='room'),
    path('upload/<str:room_code>/', views.upload_files, name='upload_files'),
    path('download/<str:room_code>/', views.download_room, name='download_room'),
    path('api/file/<int:file_id>/', views.get_file_content, name='get_file_content'),
]