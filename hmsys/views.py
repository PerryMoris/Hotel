from django.shortcuts import redirect, render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from . models import *
from datetime import datetime, timedelta, date
from django.db.models import Sum, F
from django.utils.dateparse import parse_date
from django.http import JsonResponse

def check_user_exists(request):
    mobile = request.GET.get('mobile', None)
    exists = Client.objects.filter(mobile=mobile).exists()
    return JsonResponse({'exists': exists})


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

def logout_view(request):
    logout(request)
    return redirect('login') 

@login_required(login_url="login/")
def home(request):
    number_of_clients = Client.objects.all().count()
    number_of_rooms = Rooms.objects.all().count()
    available_rooms = Rooms.objects.filter(occupied = False).count()
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
    return render(request, 'home.html', context)

@login_required(login_url="login/")
def dashboard(request):
    number_of_clients = Client.objects.all().count()
    number_of_rooms = Rooms.objects.all().count()
    available_rooms = Rooms.objects.filter(occupied = False).count()
    arrears_clients = Payments.objects.filter(fully_paid = False)
    total_arrears = Payments.objects.aggregate(
        total_arrears=Sum(F('amount_due') - F('amount_paid'))
        )['total_arrears']
    total_arrears = total_arrears if total_arrears else 0

    context ={
        'number_of_clients': number_of_clients,
        'number_of_rooms': number_of_rooms,
        'available_rooms' : available_rooms,
        'total_arrears': total_arrears,
        'arrears_clients': arrears_clients,
    }
    return render(request, 'dash2.html', context)


def roomlist (request):
        allrooms = Rooms.objects.all()
        booked = Rooms.objects.filter(occupied=True)
        unavailable = Rooms.objects.filter(occupied=False)

        context ={
             'allrooms': allrooms,
             'booked':booked,
             'unavailable':unavailable,
        }
        return render(request, "room-list.html", context)

def clientdetail (request):
        return render(request, "underconstruct.html")


def kitchen (request):
        return render(request, "underconstruct.html")

def cleaners (request):
        return render(request, "underconstruct.html")

def security (request):
        return render(request, "underconstruct.html")



def bookclient(request):
    if request.method == "POST":
        surname = request.POST.get("surname")
        othernames = request.POST.get("othernames")
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        
        try:
            client = Client.objects.get(mobile=mobile)
        except Client.DoesNotExist:
            client = Client.objects.create(
                surname=surname,
                othernames=othernames,
                address=address,
                mobile=mobile
            )

        # Get booking data from request.POST
        room_id = request.POST.get("room")
        check_in = parse_date(request.POST.get("checkin"))
        check_out = parse_date(request.POST.get("checkout"))
        amount_paid = int(request.POST.get("amount_paid"))

        # Fetch the room
        room = Rooms.objects.get(id=room_id)

        # Calculate the number of days
        days = (check_out - check_in).days if check_out else 1

        # Calculate the amount due
        amount_due = days * room.amount

        # Create and save Booked
        booked = Booked.objects.create(
            client=client,
            room=room,
            Check_in=check_in,
            Check_out=check_out
        )
        room.occupied = True
        room.save()
        # Create and save Payment
        payment = Payments.objects.create(
            mode=request.POST.get("payment_mode"),  
            booked=booked,
            amount_due=amount_due,
            amount_paid=amount_paid
        )

        # Redirect to a success page or render the same template with a success message
        return render(request, "bookclient.html", {"success": True})

    else:
        # Fetch available rooms
        rooms = Rooms.objects.filter(occupied=False)
        return render(request, "bookclient.html", {"rooms": rooms})
