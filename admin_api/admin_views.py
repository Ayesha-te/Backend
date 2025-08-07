from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.conf import settings
import os

class AdminPanelView(View):
    """Serve the admin panel login page"""
    
    def get(self, request):
        # Redirect to admin login
        return redirect('/static/admin/login.html')

class AdminDashboardView(View):
    """Serve the admin dashboard"""
    
    def get(self, request):
        # Redirect to admin dashboard
        return redirect('/static/admin/index.html')