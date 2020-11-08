from django.urls import path
from . import views

app_name = 'login'
urlpatterns = [
    path('loadLogin', views.loadLogin, name='loadLogin'),
    path('insertRegister', views.insertRegister, name='insertRegister'),
    path('insertLogin', views.insertLogin, name='insertLogin'),
    path('valideOTP', views.valideOTP, name='valideOTP'),
    path("logout", views.logout, name="logout"),

]
