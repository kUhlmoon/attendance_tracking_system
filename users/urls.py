from django.urls import path
from .views import test_view, register_user

urlpatterns = [
    # Example route (adjust later based on actual views)
    path('test/', test_view, name='test_view'),
    path('register/', register_user, name='register'),
]
