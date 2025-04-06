from django.contrib import admin
from .models import Attendance, Unit, AttendanceFile

# Register your models here.

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields=('student_username',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    filter_horizontal = ('students',)  # Easier many-to-many management


@admin.register(AttendanceFile)
class AttendanceFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('uploaded_by__username',)


# i can manage attendance records in that URL
