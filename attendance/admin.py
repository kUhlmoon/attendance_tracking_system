from django.contrib import admin
from .models import Attendance

# Register your models here.


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'recorded_by')
    list_filter = ('status', 'date')


admin.site.register(Attendance, AttendanceAdmin)

# i can manage attendance records in that URL
