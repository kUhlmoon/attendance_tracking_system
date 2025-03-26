from django.db import models
from users.models import CustomUser

# i created my models here


class Unit(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(
        CustomUser, related_name="registered_units")

    def __str__(self):
        return f"{self.code} - {self.name}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    date = models.DateField(auto_now_add=True)
    time = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.student.username} - {self.status} ({self.date})"


class AttendanceFile(models.Model):
    file = models.FileField(upload_to="attendance_uploads/")
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} uploaded by {self.uploaded_by.username}"
