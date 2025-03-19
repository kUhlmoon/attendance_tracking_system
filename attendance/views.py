import csv
import io
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from users.models import CustomUser

# i created my views here


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attendance_csv(request):
    """ API to upload attendance data fro CSV"""
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=400)

    file = request.FILES['file']

    # read CSV file
    try:
        decode_file = file.read().decode('utf-8')
        reader = csv.reader(io.StringIO(decode_file))
        next(reader)  # skip header row

        for row in header:
            student_id, date, statues, recorded_by_id = row

            # validate user exists
            try:
                student = CustomUser.objects.get(id=student_id, role="student")
                recorded_by = CustomUser.objects.get(id=recorded_by_id)
            except CustomUser.DoesNotExist:
                continue  # skips invalid records

            Attendance.objects.create(
                student=student,
                date=date,
                status=status.lower(),
                recorded_by=recorded_by
            )

        return Response({"message": "Attendance data uploaded successfully!"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

    # this API process a CSV files and file and stores attendance data
