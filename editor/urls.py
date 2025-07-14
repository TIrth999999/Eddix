from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<str:room_code>/', views.room, name='room'),
    path('upload/<str:room_code>/', views.upload_files, name='upload_files'),
    path('download/<str:room_code>/', views.download_room, name='download_room'),
    path('api/file/<int:file_id>/', views.get_file_content, name='get_file_content'),
    path('api/filelist/<str:room_code>/', views.api_file_list, name='api_file_list'),
    path('delete_room/<str:room_code>/', views.delete_room, name='delete_room'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
]