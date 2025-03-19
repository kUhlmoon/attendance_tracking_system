from django.db import models
from users.models import CustomUser

# i created my models here


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
    recorded_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="recorded_attendance")

    def __str__(self):
        return f"{self.student.user.username} - {self.status} ({self.date})"
