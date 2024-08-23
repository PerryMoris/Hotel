from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Info, Booked, Client, Category, Rooms, Payments, Service_Request, Cleaning, ClientChallenges, Kitchen_Items, Reservation, ReservationPayments

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'permissions','mobile', 'location', 'profile_pic')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

    # The following fields are needed for managing users
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('mobile', 'location','permissions', 'profile_pic')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'permissions', 'mobile', 'location', 'profile_pic')}
        ),
    )
    # Define the form fields for add and change user forms
    form = UserAdmin.form
    add_form = UserAdmin.add_form


# Register other models
admin.site.register(Info)
admin.site.register(Booked)
admin.site.register(Client)
admin.site.register(Category)
admin.site.register(Rooms)
admin.site.register(Payments)
admin.site.register(Service_Request)
admin.site.register(Cleaning)
admin.site.register(ClientChallenges)
admin.site.register(Kitchen_Items)
admin.site.register(Reservation)
admin.site.register(ReservationPayments)
