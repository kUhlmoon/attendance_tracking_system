from django.urls import path
from .views import (
    UnitListCreateView,
    upload_students_csv,
    attendance_list,
    upload_attendance_csv,
    upload_attendance,
    attendance_dashboard,
    AttendanceFileUploadView,
    predict_absenteeism
)

urlpatterns = [
    #  API endpoints (JSON-based)
    path('api/units/', UnitListCreateView.as_view(), name='unit-list-create'),
    path('api/students/upload_csv/', upload_students_csv, name='upload_students_csv'),
    path('api/upload_csv/', upload_attendance_csv, name='upload_attendance_csv'),
    path('api/upload_file/', AttendanceFileUploadView.as_view(), name='attendance_file_upload'),
    path('api/list/', attendance_list, name='attendance_list'),

    # Web views (HTML form uploads, dashboards)
    path('upload/', upload_attendance, name='upload_attendance'),
    path('dashboard/', attendance_dashboard, name='attendance_dashboard'),
    path('predict/', predict_absenteeism, name='predict_absenteeism'),
]
