from django.urls import path
from .views import (
    UnitListCreateView,
    AttendanceFileUploadView,
    upload_students_csv,
    upload_attendance_csv,
    attendance_list,
    upload_attendance,
    upload_students,
    attendance_dashboard,
    predict_absenteeism,
)

urlpatterns = [
    # API endpoints (JWT-protected)
    path('api/units/', UnitListCreateView.as_view(), name='unit-list-create'),
    path('api/students/upload_csv/', upload_students_csv, name='upload_students_csv'),
    path('api/upload_csv/', upload_attendance_csv, name='upload_attendance_csv'),
    path('api/upload_file/', AttendanceFileUploadView.as_view(), name='attendance_file_upload'),
    path('api/list/', attendance_list, name='attendance_list'),

    # Web views (HTML-based forms)
    path('upload/', upload_attendance, name='upload_attendance'),
    path('upload_students/', upload_students, name='upload_students'),
    path('dashboard/', attendance_dashboard, name='attendance_dashboard'),
    path('predict/', predict_absenteeism, name='predict_absenteeism'),
]
