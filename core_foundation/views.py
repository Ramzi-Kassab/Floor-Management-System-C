from django.shortcuts import render
import django

def home(request):
    """Simple home page view with no dependencies."""
    context = {
        'django_version': django.get_version(),
    }
    return render(request, 'home.html', context)
