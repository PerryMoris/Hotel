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

def hotelname ():
    hotelnamee = Info.objects.all().first()
    return f"{hotelnamee.name}"

def check_and_charge():
    today = timezone.now().date()
    bookings = Booked.objects.filter(Check_out__lt=today, out=False, room__occupied=True)

    try:
        # Check if there is already an UpdateClient entry for today
        updd = UpdateClient.objects.get(date=today)
        if updd:
            print("Already updated for today.")
            return
    except UpdateClient.DoesNotExist:
        # Proceed with checking overdue bookings
        for booking in bookings:
            days_overdue = (today - booking.Check_out.date()).days
            if days_overdue > 0:
                room_price = booking.room.amount
                extra_charge = room_price * days_overdue
                payment = Payments.objects.get(booked=booking)
                payment.amount_due += extra_charge
                payment.save()

        # Create an UpdateClient entry after processing all bookings
        upd = UpdateClient(date=today, updated=True)
        upd.save()
        print("Updated and charged overdue bookings for today.")

    if not bookings.exists():
        print("No booking for update today.")
 

def time_check_warning(request):
    return render(request, 'time_check_warning.html')

def check_user_exists(request):
    mobile = request.GET.get('mobile', None)
    exists = Client.objects.filter(mobile=mobile).exists()
    return JsonResponse({'exists': exists})


def login_view(request):
    today = timezone.now().date()
    if not UpdateClient.objects.filter(date=today).exists():
        check_and_charge()
    
    try:
        last_update = UpdateClient.objects.last()
        now = timezone.now()

        if last_update:
            if last_update.created_on > now:
                return redirect('time_check_warning')
    except UpdateClient.DoesNotExist:
        pass
 
  
        
    if request.user.is_authenticated:
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
            messages.error(request, "Invalid login credentials. Please try again.")
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
        'hotelname': hotelname(),
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
    clients_today = Booked.objects.filter(Check_out__date__lt=today, out=False)
    today = timezone.now().date()  # Get today's date
    reservations = Reservation.objects.filter(
        Check_in__date=today, 
        room__reserved=True,
        comply=False
    )

    reserved_rooms = Reservation.objects.filter(room__occupied=False,comply=False).count()

    context = {
        'number_of_clients': number_of_clients,
        'number_of_rooms': number_of_rooms,
        'available_rooms': available_rooms,
        'total_arrears': total_arrears,
        'arrears_clients': arrears_clients,
        'total_adults': total_adults,
        'total_children': total_children,
        'clients_today': clients_today,
        'reserved_rooms': reserved_rooms,  
        'reservation': reservations,
        'hotelname': hotelname(),
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
    reserved = allrooms.filter(reserved=True)
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
        'reserved': reserved,
        'categories': categories,
        'form': form,
        'hotelname': hotelname(),
    }
    return render(request, "room-list.html", context)

@login_required(login_url="login/")
def clientdetail(request):
    clients = Client.objects.all()
    booked_entries = Booked.objects.filter(room__occupied=True, out=False).order_by('-id')

    unique_bookings = {}
    for booking in booked_entries:
        if booking.client.id not in unique_bookings:
            unique_bookings[booking.client.id] = booking

    unique_booked_entries = list(unique_bookings.values())
    bookedc = len(unique_booked_entries)  # Count of distinct booked clients
    distinct_client_ids = list(set(Booked.objects.filter(room__occupied=False).values_list('client', flat=True)))
    cbooked = Client.objects.filter(id__in=distinct_client_ids).order_by('id')
    cbookedc = cbooked.count()  # Count of distinct clients not occupying rooms

    context = {
        'clients': clients,
        'booked': unique_booked_entries,
        'bookedc': bookedc,
        'cbooked': cbooked,
        'cbookedc': cbookedc,
        'hotelname': hotelname(),
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
        for_reservation = request.POST.get("for_reservation") == "on" 
        print(request.POST)
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
            room_id = request.POST.get("room")
            check_in = parse_date(request.POST.get("checkin"))
            check_out = parse_date(request.POST.get("checkout"))
            amount_paid = request.POST.get("amount_paid")
            amount_paid = float(amount_paid) if amount_paid else 0.0

            # Fetch the room
            room = Rooms.objects.get(id=room_id)
            days = (check_out - check_in).days if check_out else 1

            if for_reservation:
                # Handle Reservation Logic
                reservation = Reservation.objects.create(
                    client=client,
                    room=room,
                    Check_in=check_in,
                    Check_out=check_out,
                    comply=False,
                    
                )
                room.reserved = True
                room.save()
                ReservationPayments.objects.create(
                    mode=request.POST.get("payment_mode"),
                    reservation=reservation,
                    amount_due=days * room.amount,
                    amount_paid=amount_paid,
                    created_by=request.user
                )
            else:
                # Handle Booking Logic
                amount_due = days * room.amount
                booked = Booked.objects.create(
                    client=client,
                    room=room,
                    Check_in=check_in,
                    Check_out=check_out,
                    adult=adult,
                    children=children,
                    created_by=request.user,
                )
                room.occupied = True
                room.save()

                Payments.objects.create(
                    mode=request.POST.get("payment_mode"),
                    booked=booked,
                    amount_due=amount_due,
                    amount_paid=amount_paid,
                    created_by=request.user,
                    created_amount=amount_paid,
                )

            # Redirect to a success page or render the same template with a success message
            return render(request, "bookclient.html", {"success": True})

    else:
        rooms = Rooms.objects.filter(occupied=False, reserved=False)
        return render(request, "bookclient.html", {"rooms": rooms,'hotelname': hotelname(),})


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
        'hotelname': hotelname(),
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
   
    messages.error(request, "No bookings found or something went wrong.")
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
        'hotelname': hotelname(),
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
    total_updated_payments = payments_update.aggregate(total=Sum('updated_amount'))['total'] or 0

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
        'hotelname': hotelname(),
    }

    return render(request, 'mysales.html', context)


@login_required(login_url="login/")
def summarypayment (request):
    payments = Payments.objects.all().order_by('-id')
    total_payments = payments.aggregate(total=Sum('amount_paid'))['total'] or 0

    context ={
        'total': total_payments,
        'payments' : payments,
        'hotelname': hotelname(),
    }

    return render (request, 'sumpayments.html', context)

from django.db.models import Sum

def records(request):
    booked = Booked.objects.all().order_by('-id')
    reservation = Reservation.objects.all().order_by('-id')
    
    # Prefetch related payments and calculate total_amount_paid
    reservations = Reservation.objects.prefetch_related('reservationpayments_set').all()
    for res in reservations:
        total_amount_paid = res.reservationpayments_set.aggregate(Sum('amount_paid'))['amount_paid__sum']
        res.total_amount_paid = total_amount_paid or 0
    
    service = Service_Request.objects.all().order_by('-id')
    context = {
        'booked': booked,
        'services': service,
        'reservation': reservations,
        'hotelname': hotelname(),
    }

    return render(request, 'records.html', context)



@login_required(login_url="login/")
def request_service(request):
    requests = Service_Request.objects.all().order_by('-created_on')
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.created_by = request.user
            service_request.save()
            return redirect('request_service') 
    else:
        form = RequestForm()

    context = {
        'form': form,
        'requests': requests,
        'hotelname': hotelname(),
    }
    return render(request, 'request_service.html', context)


@login_required(login_url="login/")
def service(request):
    services = Services.objects.all()
    if request.method == 'POST':
        form = ServicesForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.save()
            return redirect('services') 
    else:
        form = ServicesForm()

    context = {
        'form': form,
        'services': services,
        'hotelname': hotelname(),
    }
    return render(request, 'services.html', context)


@login_required(login_url="login/")
def delivered(request, idd):
    request = Service_Request.objects.get(id=idd)
    request.delivered = True
    request.save()
    return redirect('request_service')


@login_required(login_url="login/")
def mark_client_in(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if not reservation.comply:
       
        reservation.comply = True
        reservation.save()
        
       
        reservation_payments = ReservationPayments.objects.filter(reservation=reservation)
        for payment in reservation_payments:
            Payments.objects.create(
                mode=payment.mode,
                booked=Booked.objects.create(
                    client=reservation.client,
                    room=reservation.room,
                    Check_in=reservation.Check_in,
                    Check_out=reservation.Check_out,
                    adult=1,  
                    children=0,  
                    created_by=request.user,
                ),
                
                amount_due=payment.amount_due,
                amount_paid=payment.amount_paid,

                created_by=request.user,
                created_amount=payment.amount_paid,
            )
        
      
        room = reservation.room
        room.occupied = True
        room.reserved = False
        room.save()

        messages.success(request, 'Client marked as in, and reservation updated.')
    else:
        messages.warning(request, 'Reservation is already marked as compliant.')
    
    return redirect('dashboard')  

@login_required(login_url="login/")
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
   
    reservation.delete()
    
    
    room = reservation.room
    room.reserved = False
    room.save()

    messages.success(request, 'Reservation has been canceled.')
    
    return redirect('dashboard')  
