from django import forms
from .models import UserFile

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UserFile
        fields = ['file']  # We only need the file input