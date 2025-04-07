from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin'),
    ]

    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_tutor(self):
        return self.role == 'tutor'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
