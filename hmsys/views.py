from django.shortcuts import redirect, render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from . models import *
from datetime import datetime, timedelta, date
from django.db.models import Sum, F


def login_view(request):
    if request.user.is_authenticated:
        print("user logged in already")
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("login successful")
            return redirect('home') 
        else:
            error_message = "Invalid login credentials. Please try again."
            return render(request, 'login.html', { 'error_message': error_message})
    
    return render(request, 'login.html')

@login_required(login_url="login/")
def home(request):
    number_of_clients = Client.objects.all().count()
    number_of_rooms = Rooms.objects.all().count()
    available_rooms = Rooms.objects.filter(occupied = False)
    total_arrears = Payments.objects.aggregate(
        total_arrears=Sum(F('amount_due') - F('amount_paid'))
        )['total_arrears']
    total_arrears = total_arrears if total_arrears else 0

    context ={
        'number_of_clients': number_of_clients,
        'number_of_rooms': number_of_rooms,
        'available_rooms' : available_rooms,
        'total_arrears': total_arrears,
    }
    return render(request, 'dashboard.html', context)