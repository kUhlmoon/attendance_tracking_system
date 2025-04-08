import csv
import io
from datetime import datetime
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator 
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, authentication_classes, permission_classes
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
from .forms import AttendanceUploadForm, StudentUploadForm
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
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file provided"}, status=400)

    # Save file for record-keeping
    attendance_file = AttendanceFile.objects.create(
        file=file,
        uploaded_by=request.user
    )

    reader, error = decode_csv(attendance_file.file)
    if error:
        return Response({"error": f"Error reading CSV: {error}"}, status=500)

    records_saved = 0
    errors = []

    for idx, row in enumerate(reader, start=1):
        student_id = row.get("student_id")
        unit_code = row.get("unit_code")
        date_str = row.get("date")
        status_str = row.get("status", "").strip().lower()

        # Basic validation
        if not all([student_id, unit_code, date_str, status_str]):
            errors.append(f"Row {idx}: Missing required fields.")
            continue

        if status_str not in ["present", "absent"]:
            errors.append(f"Row {idx}: Invalid status '{status_str}'. Expected 'present' or 'absent'.")
            continue

        try:
            student = CustomUser.objects.get(student_id=student_id)
        except CustomUser.DoesNotExist:
            errors.append(f"Row {idx}: Student '{student_id}' not found.")
            continue

        try:
            unit = Unit.objects.get(code=unit_code)
        except Unit.DoesNotExist:
            errors.append(f"Row {idx}: Unit '{unit_code}' not found.")
            continue

        if unit.lecturer != request.user:
            errors.append(f"Row {idx}: Unauthorized to upload attendance for unit '{unit_code}'.")
            continue

        if student not in unit.students.all():
            errors.append(f"Row {idx}: Student '{student_id}' not registered in unit '{unit_code}'.")
            continue

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"Row {idx}: Invalid date format '{date_str}'. Expected YYYY-MM-DD.")
            continue

        try:
            obj, created = Attendance.objects.get_or_create(
                student=student,
                unit=unit,
                date=date,
                defaults={"status": status_str}
            )
            if not created:
                errors.append(f"Row {idx}: Attendance already recorded for student '{student_id}' on {date}.")
            else:
                records_saved += 1
        except Exception as e:
            errors.append(f"Row {idx}: Unexpected error: {str(e)}")

    return Response({
        "file_id": attendance_file.id,
        "message": f"{records_saved} attendance records successfully uploaded.",
        "errors": errors
    }, status=status.HTTP_201_CREATED if records_saved else status.HTTP_400_BAD_REQUEST)


def home_redirect(request):
    return redirect('attendance:login')

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_page = request.GET.get('next')  # Retrieve the 'next' parameter from the request
            return redirect(next_page or reverse_lazy('attendance:attendance_dashboard'))  # If no 'next', redirect to dashboard
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'attendance/login.html', {'form': form})
# Logout view
def logout_view(request):
    logout(request)
    return redirect('attendance:login')  # Redirect to login page after logout

@login_required(login_url='/login/')  # Redirect to login if not authenticated
def attendance_dashboard(request):
    if request.user.role != 'LECTURER':  # Assuming 'LECTURER' is the role for lecturers
        messages.error(request, "Only lecturers can access this dashboard.")
        return redirect("attendance:attendance_dashboard")  # Stay within the dashboard for other roles

    # Personalized welcome message
    welcome_message = f"Welcome to your Attendance Tracker Dashboard, {request.user.first_name}!"

    units = request.user.units.all()
    records = Attendance.objects.filter(unit__in=units).select_related("student", "unit").order_by("-date")

    # Pagination setup
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "attendance/attendance_dashboard.html", {"page_obj": page_obj, "welcome_message": welcome_message})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsLecturer])
def attendance_list(request):
    unit_code = request.GET.get('unit_code')
    date_str = request.GET.get('date')

    # Get all units for the logged-in lecturer
    lecturer_units = Unit.objects.filter(lecturer=request.user)

    # Filter attendance records by the lecturer's units
    records = Attendance.objects.filter(unit__in=lecturer_units).select_related("student", "unit")

    # Optional filters
    if unit_code:
        records = records.filter(unit__code=unit_code)
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            records = records.filter(date=date_obj)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

    # Format results
    results = []
    for record in records:
        results.append({
            "student_id": record.student.student_id,
            "student_name": f"{record.student.first_name} {record.student.last_name}",
            "unit": record.unit.code,
            "date": record.date.strftime("%Y-%m-%d"),
            "status": record.status,
        })

    return Response({
        "count": len(results),
        "records": results
    }, status=200)


    return render(request, "attendance/attendance_dashboard.html", {"page_obj": page_obj})

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
    # Check if the user is a lecturer
    if not request.user.is_lecturer:  # or use request.user.role == 'LECTURER'
        raise PermissionDenied("You do not have permission to access this data.")
    
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

    results = df[['student_id', 'unit1', 'unit2', 'unit3', 'prediction']]

    return Response({
        "accuracy": accuracy,
        "predictions": results.to_dict(orient="records")
    })