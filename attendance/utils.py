import csv
import logging
from datetime import datetime
from attendance.models import Attendance
from users.models import CustomUser

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Optional: configure logging output to file or console if not already handled in settings
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_csv(file_path, lecturer_user=None):
    """
    Processes an uploaded CSV file and saves attendance records per unit.

    Expects CSV with columns: student_id, unit_code, date, status
    Returns a dictionary with number of saved records and any errors encountered.
    """
    from attendance.models import Unit

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        errors = []
        records_saved = 0

        for row in reader:
            try:
                required_fields = ["student_id", "unit_code", "date", "status"]
                if not all(field in row for field in required_fields):
                    errors.append(f"Missing fields in row: {row}")
                    continue

                student_id = row["student_id"].strip()
                unit_code = row["unit_code"].replace(" ", "").upper()
                status = row["status"].strip().lower()

                # Validate status
                if status not in ["present", "absent", "late"]:
                    errors.append(f"Invalid status '{status}' in row: {row}")
                    continue

                # Validate student
                student = CustomUser.objects.filter(student_id=student_id).first()
                if not student:
                    errors.append(f"Student {student_id} not found.")
                    continue

                # Validate unit
                unit = Unit.objects.filter(code=unit_code).first()
                if not unit:
                    errors.append(f"Unit {unit_code} not found.")
                    continue

                # Assign lecturer if not already assigned
                if lecturer_user and not unit.lecturer:
                    unit.lecturer = lecturer_user
                    unit.save()
                    logger.info(f"Assigned lecturer {lecturer_user.username} to unit {unit_code}")

                # Check if student is registered for this unit
                if student not in unit.students.all():
                    errors.append(f"Student {student_id} not registered for unit {unit_code}.")
                    continue

                # Parse date
                date_str = row["date"].strip()
                date = None
                for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                    try:
                        date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                if not date:
                    errors.append(f"Invalid date format in row: {row}")
                    continue

                # Create or skip duplicate
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    unit=unit,
                    date=date,
                    defaults={"status": status},
                )

                if created:
                    records_saved += 1
                else:
                    errors.append(f"Duplicate record for {student_id} on {date} in {unit_code}")

            except Exception as e:
                errors.append(f"Unexpected error processing row {row}: {e}")

        # Log errors to file
        if errors:
            log_filename = f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(log_filename, "w", encoding="utf-8") as error_file:
                error_file.write("\n".join(errors))
            logger.error("Errors occurred during CSV processing. See log file: " + log_filename)
        else:
            logger.info("CSV processed successfully without errors.")

        logger.info(f"Successfully saved {records_saved} records.")
        return {
            "records_saved": records_saved,
            "errors": errors,
        }


def register_students_for_unit(unit_code, student_ids):
    """
    Registers a list of students (by student_id) to a specific unit.
    Creates the unit if it doesn't exist.
    """
    from attendance.models import Unit
    from users.models import CustomUser

    unit_code = unit_code.replace(" ", "").upper()
    unit, created = Unit.objects.get_or_create(code=unit_code)

    for student_id in student_ids:
        try:
            student = CustomUser.objects.get(student_id=student_id)
            unit.students.add(student)
            logger.info(f"Registered {student.username} ({student_id}) to {unit.name}")
        except CustomUser.DoesNotExist:
            logger.warning(f"Student ID {student_id} not found.")

    logger.info("Registration process completed.")
