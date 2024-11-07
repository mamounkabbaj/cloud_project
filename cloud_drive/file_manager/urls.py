from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),  # Use Django's built-in LoginView
    path('user/home/', views.user_home, name='user_home'),
    path('files/', views.list_files, name='list_files'),  # Main files list (root level)
    path('files/<int:folder_id>/', views.list_files, name='list_files_in_folder'),  # List files in specific folder
    path('upload/', views.upload_file, name='upload_file'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('delete-folder/<int:folder_id>/', views.delete_folder, name='delete_folder'),
    path('move-files/', views.move_files_to_folder, name='move_files_to_folder'),
    path('statistics/', views.statistics, name='statistics'), 
]
