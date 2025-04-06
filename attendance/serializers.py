from rest_framework import serializers
from .models import Unit, Attendance, AttendanceFile
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'student_id']
        read_only_fields = ['id', 'username', 'email', 'role', 'student_id']


class UnitSerializer(serializers.ModelSerializer):
    students = CustomUserSerializer(many=True, read_only=True)

    class Meta:
        model = Unit
        fields = ['id', 'code', 'name', 'students']
        read_only_fields = ['id']


class AttendanceSerializer(serializers.ModelSerializer):
    student = CustomUserSerializer(read_only=True)
    unit = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'unit', 'date', 'time', 'status']
        read_only_fields = ['id', 'student', 'unit', 'date', 'time']


class AttendanceFileSerializer(serializers.ModelSerializer):
    uploaded_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = AttendanceFile
        fields = ['id', 'file', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']
