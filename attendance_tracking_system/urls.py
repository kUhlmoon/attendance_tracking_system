"""
URL configuration for attendance_tracking_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Redirect '/' based on user authentication
def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        return redirect('attendance_dashboard')  # redirect to dashboard if logged in
    else:
        return redirect('/admin/')  # redirect to admin login if not logged in

urlpatterns = [
    path('', redirect_to_dashboard),  # Redirect logic update
    path('admin/', admin.site.urls),

    # JWT auth endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App-specific APIs
    path('api/auth/', include('users.urls')),            # Auth endpoints (register/login)
    path('api/attendance/', include('attendance.urls')), # Attendance API

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('attendance/', include('attendance.urls')),
]
