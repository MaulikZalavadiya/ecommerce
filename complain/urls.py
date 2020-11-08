from django.urls import path
from . import views

urlpatterns = [
    path("admin/viewComplain", views.adminViewComplain, name="adminViewComplain"),
    path("admin/complainreply", views.adminComplainreply, name="adminComplainreply"),
    path("admin/insertReply", views.adminInsertreply, name="adminInsertreply"),

    path("loadComplain", views.loadComplain, name="loadComplain"),
    path("insertComplain", views.insertComplain, name="insertComplain"),
    path("viewComplain", views.viewComplain, name="viewComplain"),
    path("deleteComplain", views.deleteComplain, name="deleteComplain"),

    path("loadfeedback", views.loadfeedback, name="loadfeedback"),
    path("insertFeedback", views.insertFeedback, name="insertFeedback"),
    path("viewFeedback", views.viewFeedback, name="viewFeedback"),

    path("admin/viewFeedback", views.adminViewFeedback, name="adminViewFeedback"),

]
