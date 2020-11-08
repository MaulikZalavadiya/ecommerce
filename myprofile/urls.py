from django.urls import path
from . import views

app_name = 'login'
urlpatterns = [
    path('loadMyprofile', views.loadMyprofile, name='loadMyprofile'),
    path('updatePassword', views.updatePassword, name='updatePassword'),
    path('editAddress', views.editAddress, name='editAddress'),
    path('loadAddress', views.loadAddress, name='loadAddress'),
    path('insertAddress', views.insertAddress, name='insertAddress'),
    path('deleteAddress', views.deleteAddress, name='deleteAddress'),
    path('insertDefault', views.insertDefault, name='insertDefault'),
    path('updateAddress', views.updateAddress, name='updateAddress'),

]
