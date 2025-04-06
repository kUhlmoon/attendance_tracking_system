from django.db import models
from users.models import CustomUser

# Unit model represents courses or subjects students register for
class Unit(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    lecturer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'role': 'tutor'})
    students = models.ManyToManyField(CustomUser, related_name="registered_units", limit_choices_to={'role': 'student'})

    def __str__(self):
        return f"{self.code} - {self.name}"

# Attendance model for tracking student attendance
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)  # Added unit to track attendance per subject
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.student.username} - {self.status} ({self.date})"

# Model to handle attendance file uploads
class AttendanceFile(models.Model):
    file = models.FileField(upload_to="attendance_uploads/")
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} uploaded by {self.uploaded_by.username}"
