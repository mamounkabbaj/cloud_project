from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage URL
    path('register/', views.register, name='register'),  # Registration page
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.list_files, name='list_files'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('move-file/<int:file_id>/', views.move_file, name='move_file'),
    path('copy-file/<int:file_id>/', views.copy_file, name='copy_file'),
]


