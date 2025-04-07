import csv
from django.contrib import admin
from django.utils.timezone import datetime
from django.core.exceptions import ValidationError

from .models import Attendance, Unit, AttendanceFile, Student
from .forms import UnitForm

# CSV Processing Function
def process_attendance_csv(file_path):
    import csv
    from django.utils.timezone import datetime
    from .models import Attendance, Unit, Student
    from django.core.exceptions import ValidationError

    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            student_id = row.get('student_id')
            unit_code = row.get('unit_code')
            date = row.get('date')
            status = row.get('status').strip().lower()

            if status not in ['present', 'absent']:
                print(f"Invalid status '{status}' for student {student_id} on {date}. Skipping.")
                continue
            
            print(f"Processing: student={student_id}, unit={unit_code}, date={date}, status={status}")

            try:
                student = Student.objects.get(user__username=student_id)
                unit = Unit.objects.get(code=unit_code)
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()

                attendance, created = Attendance.objects.get_or_create(
                    student=student.user,
                    unit=unit,
                    date=date_obj,
                    defaults={'status': status}
                )
                if not created:
                    attendance.status = status
                    attendance.save()

            except Student.DoesNotExist:
                print(f"Student with ID '{student_id}' not found.")
            except Unit.DoesNotExist:
                print(f"Unit with code '{unit_code}' not found.")
            except Exception as e:
                print(f"Error: {e}")

# Register Student model
admin.site.register(Student)

# Customize Attendance admin
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit', 'date', 'status')
    list_filter = ('status', 'date', 'unit')
    search_fields = ('student__username', 'unit__code')

# Customize Unit admin
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'lecturer')  # Assumes lecturer is a field in Unit
    search_fields = ('code', 'name', 'lecturer__username')
    filter_horizontal = ('students',)
    form = UnitForm

# Customize AttendanceFile admin with CSV processing
@admin.register(AttendanceFile)
class AttendanceFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('uploaded_by__username',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        process_attendance_csv(obj.file.path)

# i can manage attendance records in that URL
