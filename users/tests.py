from django.test import TestCase
from users.models import CustomUser
from django.urls import reverse

class UserTests(TestCase):
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_user_creation(self):
        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpassword'))

    def test_user_register(self):
        response = self.client.post(reverse('register'), {'username': 'newuser', 'password': 'newpassword'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())
