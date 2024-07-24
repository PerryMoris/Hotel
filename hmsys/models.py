from django.db import models


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
    number = models.CharField(max_length=255, null=False, blank=True)
    amount = models.PositiveIntegerField(null=True, blank=False)
    occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category} - {self.number}"
    
class Booked (models.Model):
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, verbose_name="client", null=True, blank=False)
    room = models.ForeignKey(Rooms, on_delete=models.DO_NOTHING, verbose_name="rooms", null=True, blank=False)
    Check_in = models.DateTimeField(null=True, blank=False)
    Check_out = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.get_full_name()} - {self.room}"

class Payments (models.Model):
    pass

    