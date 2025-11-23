# -*- coding: utf-8 -*-
"""
Home page view for the application
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    """
    Home page - redirects to production dashboard if authenticated,
    otherwise shows welcome page
    """
    if request.user.is_authenticated:
        return redirect('production:dashboard')
    
    context = {
        'title': 'Floor Management System',
        'subtitle': 'Production Department',
    }
    return render(request, 'production/home.html', context)
