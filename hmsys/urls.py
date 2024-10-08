from django.urls import path
from . import views

urlpatterns = [
  path("", views.home, name="home" ),
  path("login/", views.login_view, name="login" ),
  path("info/", views.info, name="info" ),
  path("wrngtime/", views.time_check_warning, name="time_check_warning" ),
  path('logout/', views.logout_view, name='logout'),
  path('check-user-exists/', views.check_user_exists, name='check_user_exists'),
  path("roomlist", views.roomlist, name="room-list" ),
  path("clientdetail", views.clientdetail, name="client-detail" ),
  path("kitchen", views.kitchen, name="kitchen" ),
  path("cleaners", views.cleaners, name="cleaners" ),
  path("security", views.security, name="security" ),
  path("bookclient", views.bookclient, name="Book_A_Client" ),
  path("security", views.security, name="security" ),
  path("dashboard", views.dashboard, name="dashboard" ),
  path("managepayment", views.manage_payments, name="managepayment" ),
  path('clear-arrears/', views.clear_arrears, name='clear_arrears'),
  path('mysales/', views.mysales, name='mysales'),
  path('records/', views.records, name='record'),
  path('allpayments/', views.summarypayment, name='payments'),
  path('request-service/', views.request_service, name='request_service'),
  path('services/', views.service, name='services'),
  path('checkout/<int:idd>/', views.checkout, name='checkout'),
  path('delivered/<int:idd>/', views.delivered, name='deliver'),
  path('extend-booking/<int:booking_id>/', views.extend_booking, name='extend_booking'),
  path('mark-client-in/<int:reservation_id>/', views.mark_client_in, name='mark_client_in'),
  path('cancel-reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
]

