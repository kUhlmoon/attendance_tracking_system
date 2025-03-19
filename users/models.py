from django.contrib.auth.models import AbstractUser
from django.db import models

# i created my models here


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin')
    ]
    student_id = models.CharField(
        max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='student')

    def _str_(self):
        return f"{self.username} ({self.role})"
# this extends Django's default user model with a role field.
