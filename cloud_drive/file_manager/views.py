from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from .forms import FileUploadForm
from .models import UserFile, Folder
from django.utils.timezone import now, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from collections import Counter
from django.core.serializers.json import DjangoJSONEncoder
import json

import os
import shutil

# Main Home Page (General Landing Page)
def home(request):
    return render(request, 'general/home.html')

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_folder = os.path.join(settings.MEDIA_ROOT, user.username)
            os.makedirs(user_folder, exist_ok=True)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# User Home / Dashboard View
@login_required
def user_home(request):
    files = UserFile.objects.filter(user=request.user)
    folders = Folder.objects.filter(owner=request.user)
    context = {
        'files': files,
        'folders': folders,
    }
    return render(request, 'file_manager/user_home.html', context)

# List Files and Folders View
@login_required
def list_files(request, folder_id=None):
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
        folders = Folder.objects.filter(owner=request.user, parent_folder=current_folder)
        files = UserFile.objects.filter(user=request.user, folder=current_folder)
    else:
        current_folder = None
        folders = Folder.objects.filter(owner=request.user, parent_folder__isnull=True)
        files = UserFile.objects.filter(user=request.user, folder__isnull=True)

    context = {
        'folders': folders,
        'files': files,
        'current_folder': current_folder,
    }
    return render(request, 'file_manager/list_files.html', context)

# Upload File View
@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.user = request.user
            user_file.save()
            return redirect('user_home')
    else:
        form = FileUploadForm()
    return render(request, 'file_manager/upload.html', {'form': form})

# Create Folder View
@login_required
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        parent_folder_id = request.POST.get('parent_folder_id')
        parent_folder = get_object_or_404(Folder, id=parent_folder_id, owner=request.user) if parent_folder_id else None
        Folder.objects.create(owner=request.user, name=folder_name, parent_folder=parent_folder)
        return redirect('list_files')
    return render(request, 'file_manager/create_folder.html')

# Delete File View
@login_required
def delete_file(request, file_id):
    file = get_object_or_404(UserFile, id=file_id, user=request.user)
    if request.method == 'POST':
        file_path = file.file.path
        file.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
        return redirect('list_files')
    else:
        # Redirect if a GET request is made to this endpoint
        return redirect('list_files')
# Delete Folder View
@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    if request.method == 'POST':
        folder.delete()
        return redirect('list_files')
    return render(request, 'file_manager/delete_folder.html', {'folder': folder})


# Download File View
@login_required
def download_file(request, file_id):
    try:
        user_file = UserFile.objects.get(id=file_id, user=request.user)
        file_path = user_file.file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        else:
            raise Http404("File does not exist.")
    except UserFile.DoesNotExist:
        raise Http404("File not found")

@login_required
def move_files_to_folder(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('file_ids')
        target_folder_id = request.POST.get('target_folder_id')

        if file_ids and target_folder_id:
            target_folder = get_object_or_404(Folder, id=target_folder_id, owner=request.user)
            UserFile.objects.filter(id__in=file_ids, user=request.user).update(folder=target_folder)
            return redirect('list_files')
        else:
            return JsonResponse({"error": "No files selected or no target folder chosen."}, status=400)
    return redirect('list_files')



def file_type_breakdown(request):
    # Define file type mappings based on extensions
    file_type_map = {
        'Documents': ['.pdf', '.doc', '.docx', '.txt'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif'],
        'Videos': ['.mp4', '.mov', '.avi', '.mkv'],
        'Others': []
    }

    # Get user's files and categorize by type
    files = UserFile.objects.filter(user=request.user)
    file_type_counts = Counter()

    # Calculate file types and total storage usage
    total_size_gb = 0
    for file in files:
        ext = os.path.splitext(file.file.name)[1].lower()
        file_type = next((type_name for type_name, extensions in file_type_map.items() if ext in extensions), 'Others')
        file_type_counts[file_type] += 1

        # Calculate total storage in GB
        if file.file:
            total_size_gb += file.file.size / (1024 * 1024 * 1024)  # Convert bytes to GB

    # Format file type data for the chart
    file_type_data = [{'file_type': key, 'count': value} for key, value in file_type_counts.items()]

    # Storage usage over time (last 30 days)
    usage_data = []
    date_files_map = files.filter(uploaded_at__gte=now() - timedelta(days=30)).annotate(date=TruncDay('uploaded_at')).values('date')

    for entry in date_files_map:
        date = entry['date']
        date_files = files.filter(uploaded_at__date=date)
        date_total_size = sum(file.file.size for file in date_files if file.file) / (1024 * 1024 * 1024)  # Size in GB
        usage_data.append({'date': date, 'total_size': date_total_size})

    context = {
        'file_type_data': file_type_data,
        'usage_data': usage_data,
        'total_size_gb': total_size_gb,
    }
    return render(request, 'file_manager/dashboard.html', context)



@login_required
def dashboard(request):
    # Define file type mappings based on extensions
    file_type_map = {
        'Documents': ['.pdf', '.doc', '.docx', '.txt'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif'],
        'Videos': ['.mp4', '.mov', '.avi', '.mkv'],
        'Others': []
    }

    # Initialize counters for file types
    file_type_counts = Counter()
    total_size_gb = 0
    user_files = UserFile.objects.filter(user=request.user)

    # Categorize files and calculate total size
    for user_file in user_files:
        ext = os.path.splitext(user_file.file.name)[1].lower()
        file_type = next((type_name for type_name, extensions in file_type_map.items() if ext in extensions), 'Others')
        file_type_counts[file_type] += 1
        if user_file.file:
            total_size_gb += user_file.file.size / (1024 * 1024 * 1024)  # Convert bytes to GB

    # Prepare data for file type distribution chart
    file_type_data = [{'file_type': key, 'count': value} for key, value in file_type_counts.items()]

    # Prepare data for storage usage over time (last 30 days)
    usage_data = (
        user_files
        .filter(uploaded_at__gte=now() - timedelta(days=30))
        .annotate(date=TruncDay('uploaded_at'))
        .values('date')
        .annotate(total_size=Sum('file__size') / (1024 * 1024 * 1024))  # Size in GB
        .order_by('date')
    )
    usage_data = [{'date': item['date'].strftime('%Y-%m-%d'), 'total_size': item['total_size']} for item in usage_data]

    context = {
        'file_type_data': json.dumps(file_type_data, cls=DjangoJSONEncoder),
        'usage_data': json.dumps(usage_data, cls=DjangoJSONEncoder),
        'total_size_gb': total_size_gb,
    }
    return render(request, 'file_manager/dashboard.html', context)