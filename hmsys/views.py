from django.shortcuts import redirect, render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from . models import *
from datetime import datetime, timedelta, date



def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            error_message = "Invalid login credentials. Please try again."
            return render(request, 'login.html', { 'error_message': error_message})
    
    return render(request, 'login.html')

def home(request):
    return render(request, 'dashboard.html')