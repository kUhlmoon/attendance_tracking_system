from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password  # Fixed typo
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status  # Fixed typo

# Create your views here.


@api_view(['GET'])
def test_view(request):
    return Response({"message": "Test route is working!"})


@api_view(['POST'])
def register_user(request):
    # Get data from request
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    # Validate input
    if not username or not email or not password:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

    # Create and save user
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password)  # Hash password for security
    )

    return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
