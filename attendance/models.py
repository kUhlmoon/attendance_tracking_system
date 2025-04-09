# attendance/models.py
from django.db import models
from django.conf import settings
from users.models import CustomUser

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    reg_number = models.CharField(max_length=100, default='TEMP123', unique=True)

    def __str__(self):
        return f"{self.name} ({self.reg_number})"
    
class Unit(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    # Remove limit_choices_to from the lecturer field
    lecturer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    students = models.ManyToManyField(
        CustomUser,
        related_name="registered_units",
        limit_choices_to={'role': 'student', 'is_active': True}
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student', 'is_active': True}
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.student.username} - {self.unit.code} - {self.status} ({self.date})"

class AttendanceFile(models.Model):
    file = models.FileField(upload_to="attendance_uploads/")
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} uploaded by {self.uploaded_by.username}"
