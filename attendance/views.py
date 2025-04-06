import csv
import io
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import CustomUser
from .models import Attendance, Unit, AttendanceFile
from .forms import AttendanceUploadForm
from .utils import process_csv
from .serializers import UnitSerializer, AttendanceFileSerializer

ROLE_LECTURER = "lecturer"
ROLE_STUDENT = "student"

# --- Permissions ---
class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == ROLE_LECTURER

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == ROLE_STUDENT

# --- Helpers ---
def decode_csv(file):
    try:
        decoded = file.read().decode("utf-8")
        return csv.DictReader(io.StringIO(decoded)), None
    except Exception as e:
        return None, str(e)

# --- DRF API Views ---

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsLecturer])
def upload_students_csv(request):
    if "file" not in request.FILES:
        return Response({"error": "No CSV file uploaded"}, status=400)

    reader, error = decode_csv(request.FILES["file"])
    if error:
        return Response({"error": f"Error reading CSV: {error}"}, status=500)

    units = Unit.objects.all()
    if not units.exists():
        return Response({"error": "No units available to enroll students."}, status=400)

    registered, errors = [], []

    for row in reader:
        admission_number = row.get("admission_number")
        first_name = row.get("first_name")
        last_name = row.get("last_name")
        email = row.get("email")

        if not all([admission_number, first_name, last_name, email]):
            errors.append(f"Incomplete data: {row}")
            continue

        student, created = CustomUser.objects.get_or_create(
            student_id=admission_number,
            defaults={
                "username": admission_number,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "role": ROLE_STUDENT,
            }
        )

        if not created:
            errors.append(f"Student {admission_number} already exists.")
        else:
            registered.append(admission_number)

        student.registered_units.set(units)
        student.save()

    return Response({
        "message": f"{len(registered)} students registered.",
        "students": registered,
        "errors": errors
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsLecturer])
def upload_attendance_csv(request):
    if "file" not in request.FILES:
        return Response({"error": "No file provided"}, status=400)

    reader, error = decode_csv(request.FILES["file"])
    if error:
        return Response({"error": f"Error reading CSV: {error}"}, status=500)

    errors, records_saved = [], 0

    for row in reader:
        student_id = row.get("student_id")
        unit_code = row.get("unit_code")
        date_str = row.get("date")
        status_str = row.get("status", "").strip().lower()

        if not all([student_id, unit_code, date_str, status_str]):
            errors.append(f"Missing data: {row}")
            continue

        if status_str not in ["present", "absent"]:
            errors.append(f"Invalid status '{status_str}' for row: {row}")
            continue

        try:
            student = CustomUser.objects.get(student_id=student_id)
            unit = Unit.objects.get(code=unit_code)

            if unit.lecturer != request.user:
                errors.append(f"Unauthorized to upload for {unit_code}")
                continue

            if student not in unit.students.all():
                errors.append(f"Student {student_id} not enrolled in {unit_code}")
                continue

            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            _, created = Attendance.objects.get_or_create(
                student=student,
                unit=unit,
                date=date,
                defaults={"status": status_str}
            )

            if not created:
                errors.append(f"Duplicate entry for {student_id} on {date}")
            else:
                records_saved += 1

        except CustomUser.DoesNotExist:
            errors.append(f"Student {student_id} not found")
        except Unit.DoesNotExist:
            errors.append(f"Unit {unit_code} not found")
        except Exception as e:
            errors.append(f"Error processing row {row}: {str(e)}")

    return Response({
        "message": f"{records_saved} attendance records uploaded.",
        "errors": errors
    }, status=status.HTTP_201_CREATED if records_saved else status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsStudent])
def attendance_list(request):
    records = Attendance.objects.filter(student=request.user).select_related("student", "unit").order_by("-date")

    data = [{
        "student": rec.student.username,
        "student_id": rec.student.student_id,
        "unit": rec.unit.code,
        "date": rec.date.strftime("%Y-%m-%d"),
        "status": rec.status
    } for rec in records]

    return Response({"attendance_records": data})


# --- Optional: Leave legacy web views for admin/staff use only ---

@login_required
def upload_attendance(request):
    if request.method == "POST":
        form = AttendanceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save()
            process_csv(file_instance.file.path)
            messages.success(request, "Attendance uploaded successfully!")
            return redirect("attendance_dashboard")
        messages.error(request, "Invalid file. Try again.")
    else:
        form = AttendanceUploadForm()
    return render(request, "attendance/upload_attendance.html", {"form": form})


@login_required
def attendance_dashboard(request):
    if request.user.role != ROLE_LECTURER:
        messages.error(request, "Only lecturers can access this dashboard.")
        return redirect("home")

    records = Attendance.objects.filter(unit__lecturer=request.user).select_related("student", "unit").order_by("-date")
    return render(request, "attendance/attendance_dashboard.html", {"records": records})


# --- DRF Generic Views ---
class UnitListCreateView(generics.ListCreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]


class AttendanceFileUploadView(generics.ListCreateAPIView):
    queryset = AttendanceFile.objects.all()
    serializer_class = AttendanceFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


@api_view(['GET'])
def predict_absenteeism(request):
    # Mock dataset — replace with real DB queries later
    data = {
        'student_id': [1, 2, 3, 4, 5],
        'unit1': [1, 1, 0, 1, 0],
        'unit2': [1, 0, 0, 1, 0],
        'unit3': [1, 1, 0, 1, 0],
        'absent_next_week': [0, 0, 1, 0, 1]  # Target variable
    }

    df = pd.DataFrame(data)
    X = df[['unit1', 'unit2', 'unit3']]
    y = df['absent_next_week']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    # Predict on all students for demo
    full_predictions = model.predict(X)
    df['prediction'] = full_predictions

    results = df[['student_id', 'prediction']].to_dict(orient='records')

    return Response({
        'accuracy': accuracy,
        'predictions': results
    })