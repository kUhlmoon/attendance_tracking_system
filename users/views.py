from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

User = get_user_model()


# Test route for checking if the API is working
@api_view(['GET'])
def test_view(request):
    return Response({"message": "Test route is working!"})


# Register a new user (role: student or lecturer)
@api_view(['POST'])
def register_user(request):
    # Get data from request
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', ROLE_STUDENT)  # Default to student role

    # Validate input
    if not username or not email or not password:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    if role not in [ROLE_STUDENT, ROLE_LECTURER]:
        return Response({"error": "Invalid role provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

    # Create and save user
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password),  # Hash password for security
        role=role
    )

    return Response({"message": f"{role.capitalize()} registered successfully!"}, status=status.HTTP_201_CREATED)
