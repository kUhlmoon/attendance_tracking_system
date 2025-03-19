import csv
import io
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.storage import default_storage
from users.models import CustomUser
from .models import Attendance  # Ensure Attendance model is correctly imported

# API to upload attendance data from CSV


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attendance_csv(request):
    """API to upload attendance data from CSV"""
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=400)

    file = request.FILES['file']

    # Read CSV file
    try:
        decoded_file = file.read().decode('utf-8')
        reader = csv.reader(io.StringIO(decoded_file))
        next(reader)  # Skip header row

        for row in reader:
            if len(row) != 3:
                return Response({"error": "CSV format incorrect. Expected 3 values per row."}, status=400)

            student_id, date, status = row

            # Validate student exists using student_id
            try:
                student = CustomUser.objects.get(
                    student_id=student_id, role="student")
            except CustomUser.DoesNotExist:
                continue  # Skip invalid records

            # Create attendance record
            Attendance.objects.create(
                student=student,
                date=date,
                status=status.lower()
            )
            print(f"Saved attendance: {student.username} - {date}- {status}")

        return Response({"message": "Attendance data uploaded successfully!"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# Protected route - requires authentication
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_attendance_view(request):
    """Returns a message if the user is authenticated."""
    return Response({"message": "Only authenticated users can access this!"})


# Simple endpoint to confirm attendance API is working
@api_view(['GET'])
def attendance_list(request):
    """Returns a success message to confirm the API is working."""
    return Response({"message": "Attendance API is working!"})
