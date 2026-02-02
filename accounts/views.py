from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Ensure the Student group exists and add the new user to it
            student_group, _ = Group.objects.get_or_create(name='Student')
            user.groups.add(student_group)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to NovaExam.')
            return redirect('student:dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """Log the user out and redirect to the public landing page.

    Uses a simple GET/POST handler so the navbar "Logout" link always works
    and shows a clear confirmation message.
    """
    logout(request)
    messages.success(request, 'You have been logged out of NovaExam.')
    return redirect('landing')
