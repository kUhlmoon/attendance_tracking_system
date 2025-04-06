from django.test import TestCase
from .models import Unit, Attendance
from users.models import CustomUser

class AttendanceTests(TestCase):
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.unit = Unit.objects.create(code='CS101', name='Computer Science 101')
        self.attendance = Attendance.objects.create(student=self.user, unit=self.unit, status='present')

    def test_attendance_creation(self):
        attendance = Attendance.objects.get(id=self.attendance.id)
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.student.username, 'testuser')
        self.assertEqual(attendance.unit.name, 'Computer Science 101')

    def test_unit_creation(self):
        unit = Unit.objects.get(code='CS101')
        self.assertEqual(unit.name, 'Computer Science 101')
