from django.db import models
from django.contrib.auth.models import User
import os

# Function to define where files will be uploaded
def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/<username>/<filename>
    return '{0}/{1}'.format(instance.user.username, filename)

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)  # Save in user-specific folder
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.file.name}'


class Folder(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_folder = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders'
    )

    def __str__(self):
        return f'{self.name} - {self.owner.username}'


class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    file = models.FileField(upload_to=user_directory_path)  # Save in user-specific folder
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField(default=0)  # Store file size

    def __str__(self):
        return f'{self.file.name} - {self.owner.username}'
    
    def save(self, *args, **kwargs):
        # Automatically update the size field when saving the file
        self.size = self.file.size
        super().save(*args, **kwargs)

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_files')
    file = models.FileField(upload_to=user_directory_path)  # Save in user-specific folder
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.file_name}'

    @property
    def file_name(self):
        return os.path.basename(self.file.name)

    @property
    def file_size(self):
        return self.file.size