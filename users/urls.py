from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import test_view, register_user

urlpatterns = [
    # Example route (adjust later based on actual views)
    path('test/', test_view, name='test_view'),
    path('register/', register_user, name='register'),
    path('login/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),  # Login
    path('refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),  # Refresh token
]
