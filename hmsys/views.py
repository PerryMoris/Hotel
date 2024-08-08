from django.shortcuts import redirect, render
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from . models import *
from datetime import datetime, timedelta, date
from django.db.models import Sum, F, Q
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from .forms import *
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone




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
    available_rooms = Rooms.objects.filter(occupied=False).count()
    arrears_clients = Payments.objects.filter(fully_paid=False)
    total_arrears = Payments.objects.aggregate(
        total_arrears=Sum(F('amount_due') - F('amount_paid'))
    )['total_arrears']
    total_arrears = total_arrears if total_arrears else 0

    
    total_adults = Booked.objects.aggregate(total_adults=Sum('adult'))['total_adults']
    total_children = Booked.objects.aggregate(total_children=Sum('children'))['total_children']
    total_adults = total_adults if total_adults else 0
    total_children = total_children if total_children else 0

    today = timezone.now().date()
    clients_today = Booked.objects.filter(Check_out__date=today)

    context = {
        'number_of_clients': number_of_clients,
        'number_of_rooms': number_of_rooms,
        'available_rooms': available_rooms,
        'total_arrears': total_arrears,
        'arrears_clients': arrears_clients,
        'total_adults': total_adults,
        'total_children': total_children,
        'clients_today' : clients_today,
    }
    return render(request, 'dash2.html', context)



@login_required(login_url="login/")
def roomlist(request):
    category_id = request.GET.get('category')
    if category_id:
        allrooms = Rooms.objects.filter(category_id=category_id)
    else:
        allrooms = Rooms.objects.all()
    
    booked = allrooms.filter(occupied=True)
    available = allrooms.filter(occupied=False)
    categories = Category.objects.all()

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('room-list')
    else:
        form = RoomForm()

    context = {
        'allrooms': allrooms,
        'booked': booked,
        'available': available,
        'categories': categories,
        'form': form,
    }
    return render(request, "room-list.html", context)

@login_required(login_url="login/")
def clientdetail (request):
        clients = Client.objects.all()
        booked = Booked.objects.filter(room__occupied=True, out=False).order_by('-id')
        bookedc = booked.count()
        

        cdistinct_clients_ids = Booked.objects.filter(room__occupied=False).values_list('client', flat=True).distinct()
    
        # Get actual client objects
        cbooked = Client.objects.filter(id__in=cdistinct_clients_ids).order_by('id')
        cbookedc = cbooked.count()
        

        context ={
             'clients': clients,
             'booked' : booked,
             'bookedc' : bookedc,
             'cbooked' : cbooked,
             'cbookedc' : cbookedc,
        }
        return render(request, "client-detail.html", context)


def kitchen (request):
        return render(request, "underconstruct.html")

def cleaners (request):
        return render(request, "underconstruct.html")

def security (request):
        return render(request, "underconstruct.html")


@login_required(login_url="login/")
def bookclient(request):
    if request.method == "POST":
        surname = request.POST.get("surname")
        othernames = request.POST.get("othernames")
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        adult = int(request.POST.get("adult"))
        children = int(request.POST.get("children"))

        try:
            client = Client.objects.get(mobile=mobile)
        except Client.DoesNotExist:
            client = Client.objects.create(
                surname=surname,
                othernames=othernames,
                address=address,
                mobile=mobile
            )

        # Check if the client is already booked in any occupied room
        booked_rooms = Booked.objects.filter(client=client, room__occupied=True)
        if booked_rooms.exists():
            return render(request, "bookclient.html", {
                "error": True
            })
        else:
            # Get booking data from request.POST
            room_id = request.POST.get("room")
            check_in = parse_date(request.POST.get("checkin"))
            check_out = parse_date(request.POST.get("checkout"))
            amount_paid = float(request.POST.get("amount_paid"))

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
                Check_out=check_out,
                adult = adult,
                children = children,
                created_by = request.user,
            )
            room.occupied = True
            room.save()

            # Create and save Payment
            payment = Payments.objects.create(
                mode=request.POST.get("payment_mode"),  
                booked=booked,
                amount_due=amount_due,
                amount_paid=amount_paid,
                created_by = request.user
            )

            # Redirect to a success page or render the same template with a success message
            return render(request, "bookclient.html", {"success": True})

    else:
        # Fetch available rooms
        rooms = Rooms.objects.filter(occupied=False)
        return render(request, "bookclient.html", {"rooms": rooms})





@login_required(login_url="login/")
def extend_booking(request, booking_id):
    booking = get_object_or_404(Booked, id=booking_id)
    payment = get_object_or_404(Payments, booked=booking)
    rate = booking.room.amount

    if request.method == 'POST':
        days_to_add = int(request.POST.get('days_to_add'))

        # Update the checked_out date
        booking.Check_out = booking.Check_out + timedelta(days=days_to_add)
        booking.save()

        # Update the amount_due
        additional_amount = Decimal(days_to_add) * rate
        payment.amount_due += additional_amount
        payment.save()

        return redirect('dashboard')  # Redirect to your desired page after processing

    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'extend_booking.html', context)


@login_required(login_url="login/")
def checkout(request, idd):
    client = Client.objects.get(id=idd)
    bookings = Booked.objects.filter(client=client, room__occupied=True)
 
    for booking in bookings:
        payments = Payments.objects.filter(booked=booking)
        for payment in payments:
            if not payment.fully_paid:
                messages.error(request, "Payment not fully completed. Cannot check out.")
                return redirect("client-detail")
        else:
            r = Rooms.objects.get(id=booking.room.id)
            r.occupied= False
            r.save()
            rr = booking
            rr.out = True
            rr.save()
            messages.success(request, "Checked out successfully.")
            return redirect("client-detail")
   

@login_required(login_url="login/")
def manage_payments(request):
    arrears_clients = Payments.objects.filter(fully_paid = False)
    clients_with_arrears = Client.objects.annotate(
        total_arrears=Sum(
            F('booked__payments__amount_due') - F('booked__payments__amount_paid'),
            filter=Q(booked__payments__fully_paid=False)
        )
    ).filter(total_arrears__gt=0).distinct()

    selected_client = None
    selected_client_arrears = 0

    if 'client_id' in request.GET:
        client_id = request.GET['client_id']
        selected_client = Client.objects.filter(id=client_id).first()
        if selected_client:
            selected_client_arrears = Payments.objects.filter(
                booked__client=selected_client,
                fully_paid=False
            ).aggregate(total_arrears=Sum(F('amount_due') - F('amount_paid')))['total_arrears'] or 0

    context = {
        'clients': clients_with_arrears,
        'selected_client': selected_client,
        'selected_client_arrears': selected_client_arrears,
        'arrears_clients': arrears_clients,
    }
    return render(request, 'manage_payments.html', context)


@login_required(login_url="login/")
def clear_arrears(request):
    if request.method == "POST":
        client_id = request.POST.get('client_id')
        if client_id:
            client = Client.objects.filter(id=client_id).first()
            if client:
                Payments.objects.filter(booked__client=client, fully_paid=False).update(updated_amount=(F('amount_due') - F('amount_paid')),amount_paid=F('amount_due'),fully_paid=True,updated_by=request.user)
    return redirect('managepayment')



@login_required(login_url="login/")
def mysales(request):
    today = timezone.now().date()

    # Filter payments by the user who created them
    payments = Payments.objects.filter(created_by=request.user).order_by("-id")
    payments_update = Payments.objects.filter(updated_by=request.user).order_by("-id")

    # Filter payments created today by the user
    today_payments = Payments.objects.filter(created_on__date=today, created_by=request.user).order_by("-id")
    today_payments_update = Payments.objects.filter(updated_on__date=today, updated_by=request.user).order_by("-id")

    # Calculate the totals for created payments and updated payments
    total_created_payments = payments.aggregate(total=Sum('created_amount'))['total'] or 0
    total_updated_payments = payments_update.aggregate(total=Sum('upadated_amount'))['total'] or 0

    # Calculate the totals for today's created and updated payments
    total_today_created_payments = today_payments.aggregate(total=Sum('created_amount'))['total'] or 0
    total_today_updated_payments = today_payments_update.aggregate(total=Sum('updated_amount'))['total'] or 0

    context = {
        'payments': payments,
        'payments_update': payments_update,
        'today_payments': today_payments,
        'today_payments_update': today_payments_update,
        'total_created_payments': total_created_payments,
        'total_updated_payments': total_updated_payments,
        'total_today_created_payments': total_today_created_payments,
        'total_today_updated_payments': total_today_updated_payments,
    }

    return render(request, 'mysales.html', context)
