from typing import Any
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from multiselectfield import MultiSelectField


class CustomUser (AbstractUser):
    perm = (
        ('Administrator', 'Administrator'),
        ('Account', 'Account'),
        ('Receptionist', 'Receptionist'),
        ('Auditor', 'Auditor'),
    )
    mobile = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=225, null=True, blank=True)
    permissions = MultiSelectField(choices=perm, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile/', null=True, blank=True)

    def __str__(self):
        return self.username 

class Info (models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=150, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to='imgs/', null=True, blank=True)
    display1 = models.ImageField(upload_to='imgs/', null=True, blank=True)
    display2 = models.ImageField(upload_to='imgs/', null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class UpdateClient(models.Model):
    updated = models.BooleanField(default=True)
    date = models.DateField(auto_now_add=True)
    created_on = models.DateTimeField(auto_now_add=True)
    
class Client (models.Model):
    surname = models.CharField(max_length=100, null=False, blank=True)
    othernames = models.CharField(max_length=100, null=False, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=100, null=False, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.surname}, {self.othernames} - {self.mobile}"
    
    def get_full_name(self):
        return f"{self.surname}, {self.othernames}"
    
class Category (models.Model):
    name = models.CharField(max_length=255, null=False, blank=True)

    def __str__(self):
        return self.name

class Rooms (models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=False)
    number = models.CharField(max_length=255, null=True, blank=False)
    lan_line = models.CharField(max_length=255, null=True, blank=True)
    properties = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=False)
    occupied = models.BooleanField(default=False)
    reserved = models.BooleanField(default=False)
    image = models.ImageField(upload_to='room_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.category} - {self.number}"
    
class Booked (models.Model):
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, verbose_name="client", null=True, blank=False)
    room = models.ForeignKey(Rooms, on_delete=models.DO_NOTHING, verbose_name="rooms", null=True, blank=False)
    Check_in = models.DateTimeField(null=True, blank=False)
    Check_out = models.DateTimeField(null=True, blank=True)
    adult = models.IntegerField(null=True, blank=True)
    children = models.IntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    out = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f"{self.client.get_full_name()} - {self.room}"

class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, verbose_name="client", null=True, blank=False)
    room = models.ForeignKey(Rooms, on_delete=models.DO_NOTHING, verbose_name="rooms", null=True, blank=False)
    Check_in = models.DateTimeField(null=True, blank=False)
    Check_out = models.DateTimeField(null=True, blank=True)
    comply = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.room}"

class ReservationPayments(models.Model):
    mode = models.CharField(max_length=150, null=True, blank=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, null=True, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fully_paid = models.BooleanField(default=False)
    created_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True)
    
    def __str__(self):
        return f"{self.booked} - {self.amount_paid}"
    

class Payments(models.Model):
    mode = models.CharField(max_length=150, null=True, blank=True)
    booked = models.ForeignKey(Booked, on_delete=models.CASCADE, null=True, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fully_paid = models.BooleanField(default=False)
    created_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)  # Automatically updates to current timestamp on save
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payments_updated_by', on_delete=models.SET_NULL, null=True, blank=True)
    updated_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Track the updated amount
        if self.pk:
            original = Payments.objects.get(pk=self.pk)
            self.updated_amount = self.amount_due - original.amount_paid
        else:
            self.updated_amount = float(self.amount_due) - float(self.amount_paid if self.amount_paid else 0)

        # Determine if the payment is fully paid
        if self.amount_due == self.amount_paid:
            self.fully_paid = True
        else:
            self.fully_paid = False

        super().save(*args, **kwargs)

    def arrears(self):
        arrea = self.amount_due - self.amount_paid
        return arrea if arrea > 0 else 0

    def __str__(self):
        return f"{self.booked} - {self.amount_paid}"


class Kitchen_Items(models.Model):
    image = models.ImageField(upload_to='room_images/', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.amount}'

class Services(models.Model):
    name = models.CharField(max_length=255, null=True, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.amount}'
    
class Service_Request(models.Model):
    booked = models.ForeignKey(Booked, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, related_name='services', on_delete=models.SET_NULL, null=True, blank=True)
    requested = models.TextField('Request Details',null=True, blank=True)
    delivered = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_by', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.booked.client} - {self.requested:[70]}"
    
class Cleaning(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name='user')
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE, null=True, blank=True)
    challenges = models.TextField(null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Room cleaned ({self.room})"
    
class ClientChallenges (models.Model):
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, verbose_name="client", null=True, blank=False)
    challenges = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From - {self.client.get_full_name()}"