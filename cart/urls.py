from django.urls import path
from . import views

urlpatterns = [
    path("insertOrder", views.insertOrder, name="insertOrder"),
    path("viewCart", views.viewCart, name="viewCart"),
    path("checkout", views.checkout, name="checkout"),
    path("selectAddress", views.selectAddress, name="selectAddress"),
    path("totalAmount", views.totalAmount, name="totalAmount"),
    path("deleteOrder", views.deleteOrder, name="deleteOrder"),
    path("viewOrder", views.viewOrder, name="viewOrder"),
    path("cancleOrder", views.cancleOrder, name="cancleOrder"),
    path("showsize", views.showsize, name="showsize"),
    path("showcolor", views.showcolor, name="showcolor"),
    path("changecolor", views.changecolor, name="changecolor"),
    path("changesize", views.changesize, name="changesize"),
    path("insertCoupon", views.insertCoupon, name="insertCoupon"),

    # --------------------- coupon-----------------

    path("admin/loadCoupon", views.adminLoadCoupon, name="adminLoadCoupon"),
    path("admin/insertCoupon", views.adminInsertCoupon, name="adminInsertCoupon"),
    path("admin/viewCoupon", views.adminViewCoupon, name="adminViewCoupon"),
    path("admin/editCoupon", views.adminEditCoupon, name="adminEditCoupon"),
    path("admin/updateCoupon", views.adminUpdateCoupon, name="adminUpdateCoupon"),
    path("admin/deleteCoupon", views.adminDeleteCoupon, name="adminDeleteCoupon"),

]
