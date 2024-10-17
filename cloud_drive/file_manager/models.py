from django.db import models
from django.contrib.auth.models import User
import os


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/<username>/<filename>
    return 'media/{0}/{1}'.format(instance.user.username, filename)

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)  # Save in user-specific folder
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.file.name}'