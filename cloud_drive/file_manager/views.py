from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
import os
from django.conf import settings
from .forms import FileUploadForm
from .models import UserFile
from django.http import HttpResponse
from .models import UserFile  
from django.contrib.auth.decorators import login_required
import shutil
from django.shortcuts import get_object_or_404




def home(request):
    return HttpResponse("Welcome to the Cloud Drive")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create a folder for the new user
            user_folder = os.path.join(settings.MEDIA_ROOT, user.username)
            os.makedirs(user_folder, exist_ok=True)  # Create user folder if not exists
            
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.user = request.user  # Assign the file to the logged-in user
            user_file.save()
            return redirect('home')  # Redirect after successful upload
    else:
        form = FileUploadForm()
    return render(request, 'file_manager/upload.html', {'form': form})

@login_required
def list_files(request):
    files = UserFile.objects.filter(user=request.user)  # Get files for the logged-in user
    return render(request, 'file_manager/list_files.html', {'files': files})

@login_required
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        if folder_name:
            # Construct the folder path in the user's directory
            user_folder_path = os.path.join(settings.MEDIA_ROOT, request.user.username, folder_name)
            os.makedirs(user_folder_path, exist_ok=True)  # Create folder if it doesn't exist
            return redirect('list_files')  # Redirect to file list after creating folder
    return render(request, 'file_manager/create_folder.html')



@login_required
def move_file(request, file_id):
    file = get_object_or_404(UserFile, id=file_id, user=request.user)
    if request.method == 'POST':
        new_folder = request.POST.get('new_folder')
        if new_folder:
            # Define the source and destination paths
            old_path = file.file.path
            new_path = os.path.join(settings.MEDIA_ROOT, request.user.username, new_folder, os.path.basename(file.file.name))
            shutil.move(old_path, new_path)  # Move the file
            file.file.name = os.path.join(new_folder, os.path.basename(file.file.name))  # Update file path in DB
            file.save()
            return redirect('list_files')
    return render(request, 'file_manager/move_file.html', {'file': file})


@login_required
def copy_file(request, file_id):
    file = get_object_or_404(UserFile, id=file_id, user=request.user)
    if request.method == 'POST':
        destination_folder = request.POST.get('destination_folder')
        if destination_folder:
            # Define the source and destination paths
            source_path = file.file.path
            destination_path = os.path.join(settings.MEDIA_ROOT, request.user.username, destination_folder, os.path.basename(file.file.name))
            shutil.copy(source_path, destination_path)  # Copy the file
            return redirect('list_files')
    return render(request, 'file_manager/copy_file.html', {'file': file})