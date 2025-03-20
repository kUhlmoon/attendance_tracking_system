from django import forms
from .models import AttendanceFile


class AttendanceUploadForm(forms.ModelForm):
    class Meta:
        model = AttendanceFile
        fields = ["file"]
