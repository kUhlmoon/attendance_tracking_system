from django import forms
from .models import AttendanceFile, Unit, Student
from users.models import CustomUser

class AttendanceUploadForm(forms.ModelForm):
    class Meta:
        model = AttendanceFile
        fields = ["file"]

class StudentUploadForm(forms.Form):
    file = forms.FileField(label="Student CSV File")

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)
        # Filter students to only those who are active and have a Student profile
        valid_student_users = CustomUser.objects.filter(
            role='student',
            is_active=True,
            id__in=Student.objects.values_list('user_id', flat=True)
        )
        self.fields['students'].queryset = valid_student_users

class AttendanceCSVUploadForm(forms.Form):
    file = forms.FileField()

class StudentCSVUploadForm(forms.Form):
    file = forms.FileField()