from django.urls import path
from . import views
from .views import (
    UnitListCreateView,
    AttendanceFileUploadView,
    upload_students_csv,
    upload_attendance_csv,
    attendance_dashboard,
    predict_absenteeism,
    login_view,
    logout_view,
)

app_name = 'attendance'

urlpatterns = [
    # Web views
    path('login/', login_view, name='login'),  # Add login path
    path('logout/', logout_view, name='logout'),  # Add logout path
    path('dashboard/', attendance_dashboard, name='attendance_dashboard'),
    path('upload-attendance/', views.upload_attendance_csv, name='upload_attendance_csv'),
    path('upload-students/', views.upload_students_csv, name='upload_students_csv'),
    path('predict/', predict_absenteeism, name='predict_absenteeism'),
]
