import csv
from datetime import datetime
import logging
from attendance.models import Attendance
from users.models import CustomUser

# Set up logging
logger = logging.getLogger(__name__)


def process_csv(file_path):
    """Processes an uploaded CSV file and saves attendance records."""
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        errors = []
        records_saved = 0

        for row in reader:
            try:
                # Ensure all required fields are present
                required_fields = ["student_id", "date", "time", "status"]
                if not all(field in row for field in required_fields):
                    errors.append(f"Missing required fields in row: {row}")
                    continue

                # Fetch the student
                student = CustomUser.objects.filter(
                    student_id=row["student_id"]).first()
                if not student:
                    errors.append(f"Student ID {row['student_id']} not found.")
                    continue

                # Parse date
                try:
                    date = datetime.strptime(row["date"], "%Y-%m-%d").date()
                except ValueError:
                    errors.append(f"Invalid date format in row: {row}")
                    continue

                # Parse time (ensuring it's stored as `TimeField`)
                try:
                    time = datetime.strptime(row["time"], "%H:%M").time()
                except ValueError:
                    errors.append(f"Invalid time format in row: {row}")
                    continue

                status = row["status"].strip().lower()
                if status not in ["present", "absent", "late"]:
                    errors.append(f"Invalid status '{status}' in row: {row}")
                    continue

                # Prevent duplicate attendance records
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=date,
                    time=time,
                    status=status
                )

                if created:
                    records_saved += 1
                else:
                    errors.append(
                        f"Duplicate record for {student.student_id} on {date}")

            except Exception as e:
                errors.append(f"Unexpected error processing row {row}: {e}")

        # Log errors if any
        if errors:
            logger.error(
                "Errors occurred during CSV processing:\n" + "\n".join(errors))
            with open("error_log.txt", "w", encoding="utf-8") as error_file:
                error_file.write("\n".join(errors))

        print(f"Successfully saved {records_saved} records.")
