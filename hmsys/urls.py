from django.urls import path
from . import views

urlpatterns = [
  path("", views.home, name="home" ),
  path("login/", views.login_view, name="login" ),
  path('logout/', views.logout_view, name='logout'),
  path("roomlist", views.roomlist, name="roomlist" ),
  path("clientdetail", views.clientdetail, name="client-detail" ),
  path("kitchen", views.kitchen, name="kitchen" ),
  path("cleaners", views.cleaners, name="cleaners" ),
  path("security", views.security, name="security" ),
]
