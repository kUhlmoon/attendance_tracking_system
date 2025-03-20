import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import CustomUser
from .models import Attendance
from .forms import AttendanceUploadForm
from .utils import process_csv

# API for uploading attendance via CSV (Supports multiple lecturers)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attendance_csv(request):
    """Allows lecturers to upload attendance CSV files through the API"""
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=400)

    file = request.FILES['file']

    try:
        decoded_file = file.read().decode('utf-8')
        # Use DictReader for better parsing
        reader = csv.DictReader(io.StringIO(decoded_file))

        errors = []
        records_saved = 0

        for row in reader:
            try:
                student = CustomUser.objects.get(student_id=row["student_id"])
                date = datetime.strptime(row["date"], "%Y-%m-%d").date()
                status = row["status"].lower()

                # Prevent duplicate records
                attendance, created = Attendance.objects.get_or_create(
                    student=student, date=date, status=status
                )
                if created:
                    records_saved += 1
                else:
                    errors.append(
                        f"Duplicate entry for {student.student_id} on {date}"
                    )

            except CustomUser.DoesNotExist:
                errors.append(f"Student ID {row['student_id']} not found")
            except Exception as e:
                errors.append(f"Error processing row {row}: {e}")

        response_message = {
            "message": f"Successfully saved {records_saved} records!"
        }
        if errors:
            response_message["errors"] = errors  # Include errors in response

        return Response(response_message, status=201 if records_saved else 400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# API to fetch all attendance records
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def attendance_list(request):
    """Lists attendance records for all students"""
    attendance_records = Attendance.objects.select_related(
        "student"
    ).all().order_by("-date")

    # Formatting response
    data = [
        {
            "student": record.student.username,
            "student_id": record.student.student_id,
            "date": record.date.strftime("%Y-%m-%d"),
            "status": record.status
        }
        for record in attendance_records
    ]

    return Response({"attendance_records": data})


# Protected route - requires authentication
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_attendance_view(request):
    """Returns a message if the user is authenticated."""
    return Response({"message": "Only authenticated users can access this!"})


# Web-based upload attendance form
def upload_attendance(request):
    """Handles attendance upload via a form and processes CSV"""
    if request.method == "POST":
        form = AttendanceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save()
            process_csv(file_instance.file.path)  # Process the uploaded CSV
            messages.success(request, "Attendance file uploaded successfully!")
            return redirect("attendance_dashboard")  # Redirect to dashboard
        else:
            messages.error(request, "Invalid file. Please try again.")

    else:
        form = AttendanceUploadForm()

    return render(request, "attendance/upload_attendance.html", {"form": form})


# Web-based attendance dashboard
def attendance_dashboard(request):
    """Displays attendance records in a dashboard"""
    records = Attendance.objects.select_related(
        "student"
    ).all().order_by("-date")

    return render(request, "attendance/attendance_dashboard.html", {"records": records})
