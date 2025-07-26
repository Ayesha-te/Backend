from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import Booking, Vehicle, Document
from .serializers import UserSerializer, BookingSerializer, VehicleSerializer, DocumentSerializer

User = get_user_model()

# Register user API
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Save user with hashed password
        user = serializer.save()
        user.set_password(self.request.data['password'])
        user.save()

# Login with HTML form + session authentication
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')  # your login form template

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')  # change 'profile' to your success page url name
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html')

# JWT token login API view for JSON API clients
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Inherits from SimpleJWT's TokenObtainPairView
    Accepts POST with 'username' and 'password',
    returns JSON with 'access' and 'refresh' tokens.
    """
    permission_classes = [permissions.AllowAny]

# User detail for logged-in user (session or token auth)
class UserDetail(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# List bookings for logged in user
class BookingList(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

# List vehicles for logged in user
class VehicleList(generics.ListAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

# List documents for logged in user
class DocumentList(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)
