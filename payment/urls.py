from django.urls import path
from . import views

urlpatterns = [
    path("loadPayment", views.loadPayment, name="loadPayment"),
    path("handlerequest/", views.handlerequest, name="HandleRequest"),
    path("admin/refund", views.adminRefund, name="adminRefund"),

    path('getpdfPage', views.getpdfPage, name='getpdfPage'),
]
