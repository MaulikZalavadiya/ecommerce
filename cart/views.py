from django.shortcuts import render, redirect
from django.http import JsonResponse, request
import json
from django.contrib import messages
from django.contrib.sessions.models import Session
from math import ceil
from .models import Order, Coupon
from shop.models import Product
from login.models import Loginmaster
from myprofile.models import Address
from datetime import date, timedelta
from django.db.models import Sum
import ast
import requests
from PayTm import Checksum, PaytmChecksum
from shop.models import Category, Subategory, Type

MERCHANT_KEY = '!c362cynoSpV4ER@'


# Create your views here.


def insertOrder(request):
    if request.session.get('login_Role') == 'user':
        if request.method == "POST":
            product_Id = request.POST['id']
            userId = request.session['login_Id']
            color = request.POST['color']
            size = request.POST['size']
            # print("00000000000000000000000000000000000000000000000000000000000000000000000", size, color)
        else:
            product_Id = request.GET['id']
            userId = request.session['login_Id']

        temp = {}
        defaultAddress = Address.objects.filter(login_Id=userId, action="default")

        getProduct = Product.objects.get(pk=product_Id)
        if request.method == 'POST':
            temp["color"] = color
            temp["size"] = size

        temp["code"] = getProduct.code
        temp["name"] = getProduct.name
        temp["image"] = getProduct.image
        temp["category"] = getProduct.category
        temp["subcategory"] = getProduct.subcategory
        temp["type"] = getProduct.type
        temp["desc"] = getProduct.desc
        temp["price"] = getProduct.price
        temp["quantity"] = 1
        totalPrice = getProduct.price * 1
        temp["totalprice"] = totalPrice
        if getProduct.coupon != None:
            temp["couponAvailable"] = 'yes'
        else:
            temp["couponAvailable"] = 'no'



        varify = Order.objects.filter(userId_id=userId, orderstatus='addtocart')
        if len(varify) == 0:
            orderItems = {}
            orderItems[product_Id] = temp

            addOrder = Order(product=orderItems, totalPrice=getProduct.price,
                             orderstatus='addtocart', userId_id=userId)

            if len(defaultAddress) != 0:
                addOrder.address_id = defaultAddress[0].id
            addOrder.save()
        else:
            getOrder = Order.objects.get(pk=varify[0].id)
            orderItems = eval(getOrder.product)
            if product_Id not in orderItems:
                orderItems[product_Id] = temp

                getOrder.totalPrice = getOrder.totalPrice + getProduct.price

            getOrder.product = orderItems

            getOrder.save()

        return redirect('/')

    else:
        return JsonResponse({'loginRequire': "loginRequire"})


def viewCart(request):
    if request.session.get('login_Role') == 'user':
        # orderList = Order.objects.filter(userId=request.session['login_Id'], status="addtocart").all()
        # selectedAddress = orderList.aggregate()
        # totalOrderAmount = orderList.aggregate(Sum('totalPrice'))
        # return render(request, 'user/cart.html',
        #               {'orderList': orderList, "totalOrderAmount": totalOrderAmount["totalPrice__sum"]})

        productList = Product.objects.all()
        orderList = Order.objects.filter(userId_id=request.session['login_Id'], orderstatus='addtocart')
        if len(orderList) != 0:
            orderListDict = eval(orderList[0].product)  # remenber eval use for string to dict

            return render(request, 'user/cart.html',
                          {'orderListDict': orderListDict, "productList": productList, 'orderList': orderList[0]})
        else:
            messages.success(request, "your cart is empty.")
            return render(request, 'user/cart.html')
    else:
        return redirect('/loadLogin')


def checkout(request):
    orderList = Order.objects.get(userId=request.session['login_Id'], orderstatus="addtocart")
    viewAddress = Address.objects.filter(login_Id=request.session['login_Id']).order_by("id")
    return render(request, 'user/checkout.html',
                  {'productList': eval(orderList.product), 'viewAddress': viewAddress,
                   "selectedAddress": orderList.address, 'orderList': orderList})


    # if request.session.get('login_Role') == 'user':
    #     orderList = Order.objects.filter(userId=request.session['login_Id'], status="addtocart")
    #     viewAddress = Address.objects.filter(login_Id=request.session['login_Id']).order_by("id")
    #     totalOrderAmount = orderList.aggregate(Sum('totalPrice'))
    #     if len(orderList) != 0:
    #         return render(request, 'user/checkout.html',
    #                       {'orderList': orderList, 'viewAddress': viewAddress,
    #                        'totalOrderAmount': totalOrderAmount['totalPrice__sum'],
    #                        "selectedAddress": orderList[0].address})
    #     else:
    #         return redirect('/viewCart')
    #
    # else:
    #     return redirect('/loadLogin')


def selectAddress(request):
    addressId = request.GET['addressId']

    orderList = Order.objects.get(userId=request.session['login_Id'], orderstatus="addtocart")
    orderList.address_id = addressId
    orderList.save()

    return JsonResponse({'addressId': addressId})






    # obj = Order.objects.filter(status="addtocart", userId=request.session['login_Id']).order_by("id")
    # beforeDefault = obj[0].address
    # obj.update(address=addressId)
    # return JsonResponse({"addressId": addressId})


def deleteOrder(request):
    productId = request.GET['productId']
    print(">>>>>>>>>>>>>>>>>>", productId)

    orderList = Order.objects.get(userId_id=request.session['login_Id'], orderstatus='addtocart')
    productList = eval(orderList.product)
    deleteItem = productList.pop(productId)

    totalprice = 0
    for key, value in productList.items():
        totalprice = totalprice + int(value['totalprice'])

    orderList.product = productList
    orderList.totalPrice = totalprice
    orderList.save()

    # quantityCounter = Product.objects.get(pk=int(productId))
    # quantityCounter.quantity = quantityCounter.quantity + int(deleteItem['quantity'])
    # quantityCounter.save()

    return JsonResponse({"deleteItemId": productId, 'totalOrderAmount': totalprice})


    # orderId = request.GET['orderId']
    # delterOreder = Order.objects.get(pk=orderId)
    # delterOreder.delete()
    # total = Order.objects.filter(userId=request.session['login_Id'], status="addtocart").all()
    # totalOrderAmount = total.aggregate(Sum('totalPrice'))
    # return JsonResponse({"deleteItemId": orderId, 'totalOrderAmount': totalOrderAmount["totalPrice__sum"]})


def cancleOrder(request):
    orderId = request.GET['orderId']
    productId = request.GET['productId']

    getOrder = Order.objects.get(pk=orderId)
    product = eval(getOrder.product)
    cancel = product.pop(productId)
    refundAmount = int(cancel['totalprice'])
    txnId = getOrder.txnId

    paytmParams = dict()

    paytmParams["body"] = {
        "mid": "nHXgex32367017368258",
        "txnType": "REFUND",
        "orderId": str(orderId),
        "txnId": str(txnId),
        "refId": str(orderId) + "-" + str(productId),
        "refundAmount": str(refundAmount),
    }

    checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), MERCHANT_KEY)

    paytmParams["head"] = {
        "signature": checksum
    }

    post_data = json.dumps(paytmParams)
    url = "https://securegw-stage.paytm.in/refund/apply"

    response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
    print(response)

    if product == {}:
        getOrder.totalPrice = getOrder.totalPrice - int(cancel['totalprice'])
        getOrder.delete()
    else:
        getOrder.totalPrice = getOrder.totalPrice - int(cancel['totalprice'])
        getOrder.product = product
        getOrder.save()

    # quantityCounter = Product.objects.get(pk=int(productId))
    # quantityCounter.quantity = quantityCounter.quantity + int(cancel['quantity'])
    # quantityCounter.save()

    quantityCounter = Product.objects.get(pk=int(productId))
    size = list(str(quantityCounter.size[1:len(quantityCounter.size) - 1]).split(","))
    quantity = list(str(quantityCounter.quantity[1:len(quantityCounter.quantity) - 1]).split(","))

    getIndexSize = size.index(getOrder.product[productId]['size'])
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", getIndexSize)
    getQuantity = int(quantity[getIndexSize]) + int(getOrder.product[productId]['quantity'])
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..", getQuantity)
    quantity.pop(getIndexSize)
    quantity.insert(getIndexSize, getQuantity)
    strquantity = ""
    for i in quantity:
        strquantity = strquantity + str(i) + ","
    quantityCounter.quantity = "[" + strquantity[0:len(strquantity) - 1] + "]"
    quantityCounter.save()

    return JsonResponse({"orderId": orderId, 'productId': productId, 'msg': 'you will get refund next 48 hour.'})


def totalAmount(request):
    productId = request.GET["productId"]
    quantity = request.GET["quantity"]
    orderList = Order.objects.get(userId_id=request.session['login_Id'], orderstatus='addtocart')

    updateOrder = eval(orderList.product)
    price = updateOrder[productId]['price']
    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", price)
    # print(">>>>>>>>>>>>>>>>>", quantity)
    updateOrder[productId]['totalprice'] = price * int(quantity)
    # print("<<<<<<<<<<<<<<<<<<<<", updateOrder[productId]['totalprice'])
    updateOrder[productId]['quantity'] = quantity

    orderList.product = updateOrder

    totalprice = 0
    for key, value in updateOrder.items():
        totalprice = totalprice + int(value['totalprice'])

    orderList.totalPrice = totalprice
    orderList.save()

    dect = {"totalAmount": updateOrder[productId]['totalprice'], 'totalOrderAmount': orderList.totalPrice}
    return JsonResponse(dect)


# quantity = request.GET["quantity"]
# orderId = request.GET["orderId"]
# print(">>>>>>>>>>>>>>>", quantity, ">>>>>>>>>>>>>>>", orderId)
#
# modifyOrder = Order.objects.get(pk=orderId)
# modifyOrder.totalPrice = int(quantity) * int(modifyOrder.orderproductId.price)
# modifyOrder.Quantity = quantity
# print("++++++++++++++++++", modifyOrder.totalPrice)
# modifyOrder.save()
#
# total = Order.objects.filter(userId=request.session['login_Id'], status="addtocart").all()
# totalOrderAmount = total.aggregate(Sum('totalPrice'))
#
# dect = {"totalAmount": modifyOrder.totalPrice, 'totalOrderAmount': totalOrderAmount["totalPrice__sum"]}
#
# return JsonResponse(dect)


def viewOrder(request):
    if request.session.get('login_Role') == 'user':
        orderList = []

        getOrder = Order.objects.filter(userId=request.session['login_Id']).exclude(orderstatus='addtocart')
        for data in getOrder:
            product = eval(data.product)
            orderList.append(product)

        return render(request, 'user/viewOrder.html', {'orderList': orderList, 'getOrder': getOrder})

        # orderedList = Order.objects.filter(userId=request.session['login_Id'], status='orderd') | Order.objects.filter(
        #     userId=request.session['login_Id'], status='delivered')
        #
        # return render(request, 'user/viewOrder.html',
        #               {'orderList': orderedList})

    else:
        return redirect('/loadLogin')


def showsize(request):
    productId = request.GET['productId']
    getProduct = Product.objects.get(pk=productId)
    getsize = list(str(getProduct.size[1:len(getProduct.size) - 1]).split(","))
    getquantity = list(str(getProduct.quantity[1:len(getProduct.quantity) - 1]).split(","))
    size = {}
    for i in range(len(getsize)):
        if int(getquantity[i]) > 0:
            size[getsize[i]] = getquantity[i]
    # print(">>>>>>>>>>>>>", size)

    return JsonResponse({'size': size})


def showcolor(request):
    productId = request.GET['productId']
    getProduct = Product.objects.get(pk=productId)
    getcolor = list(str(getProduct.color[1:len(getProduct.color) - 1]).split(","))
    color = {}
    for i in range(len(getcolor)):
        color[getcolor[i]] = getcolor[i]
    # print(">>>>>>>>>>>>>", color)

    return JsonResponse({'color': color})


def changecolor(request):
    productId = request.GET['productId']
    color = request.GET['color']

    orderList = Order.objects.get(userId_id=request.session['login_Id'], orderstatus='addtocart')
    productDict = eval(orderList.product)
    productDict[productId]['color'] = color
    orderList.product = productDict
    orderList.save()


def changesize(request):
    productId = request.GET['productId']
    size = request.GET['size']

    orderList = Order.objects.get(userId_id=request.session['login_Id'], orderstatus='addtocart')
    productDict = eval(orderList.product)
    productDict[productId]['size'] = size
    orderList.product = productDict
    orderList.save()


def adminLoadCoupon(request):
    categoryList = Category.objects.all()
    subcategory = Subategory.objects.all()
    type = Type.objects.all()
    return render(request, 'admin/addCoupon.html',
                  {'categoryList': categoryList, 'subcategory': subcategory, 'type': type})


def adminInsertCoupon(request):
    code = request.POST['code']
    validfrom = request.POST['validfrom']
    validto = request.POST['validto']
    discount = request.POST['discount']
    perameter = request.POST['perameter']

    varify = Coupon.objects.filter(code=code)
    if len(varify) == 0:
        addCoupon = Coupon(code=code, valid_from=validfrom, valid_to=validto, discount=discount, perameter=perameter,
                           status='active')
        if request.POST['category'] != "":
            print(">>>>...", request.POST['category'])
            category = request.POST['category']
            getProduct = Product.objects.filter(category=category)
            addCoupon.category = category

        if request.POST['subcategory'] != "":
            print(">>>>...", request.POST['subcategory'])
            subcategory = request.POST['subcategory']
            getProduct = getProduct.filter(subcategory=subcategory)
            addCoupon.subcategory = subcategory

        if request.POST['type'] != "":
            print(">>>>...", request.POST['type'])
            type = request.POST['type']
            getProduct = getProduct.filter(type=type)
            addCoupon.type = type

        addCoupon.save()

        for i in getProduct:
            i.coupon = code
            i.save()

        return redirect('/admin/viewCoupon')
    else:
        return redirect('/admin/loadCoupon')


def adminViewCoupon(request):
    couponList = Coupon.objects.all()
    return render(request, 'admin/viewCoupon.html', {'couponList': couponList})


def adminEditCoupon(request):
    id = request.GET['id']
    getCoupon = Coupon.objects.get(pk=id)
    return render(request, 'admin/addCoupon.html', {'getCoupon': getCoupon})


def adminUpdateCoupon(request):
    id = request.POST['id']
    code = request.POST['code']
    validfrom = request.POST['validfrom']
    validto = request.POST['validto']
    discount = request.POST['discount']
    perameter = request.POST['perameter']

    updateCoupon = Coupon.objects.get(pk=id)
    updateCoupon.code = code
    updateCoupon.valid_from = validfrom
    updateCoupon.valid_to = validto
    updateCoupon.discount = discount
    updateCoupon.perameter = perameter
    updateCoupon.save()

    return redirect('/admin/viewCoupon')


def adminDeleteCoupon(request):
    id = request.GET['id']
    deleteCoupon = Coupon.objects.get(pk=id)
    deleteCoupon.delete()
    return redirect('/admin/viewCoupon')


def insertCoupon(request):
    productId = request.GET['productId']
    # orderId = request.GET['orderId']
    coupon = request.GET['coupon']

    varify = Product.objects.get(pk=productId)
    if varify.coupon == coupon:
        getOrder = Order.objects.get(userId_id=request.session['login_Id'],orderstatus='addtocart')
        getcoupon = Coupon.objects.get(code=coupon)
        product = eval(getOrder.product)
        print("OOOOOOOOOOO>>>>>..",product)
        product[productId]['coupon'] = coupon
        product[productId]['discount'] = str(getcoupon.discount) + " " + getcoupon.perameter

        if getcoupon.perameter == '%':
            product[productId]['totalprice'] = product[productId]['totalprice'] - (product[productId]['totalprice'] * (getcoupon.discount / 100))
        if getcoupon.perameter == 'Rs':
            product[productId]['totalprice'] = product[productId]['totalprice'] - getcoupon.discount

        totalprice = 0
        for key, value in product.items():
            totalprice = totalprice + float(value['totalprice'])

        getOrder.totalPrice = totalprice
        print(">>>>>..", product,">>>>",totalprice)
        getOrder.product=product
        getOrder.save()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        return JsonResponse({'totalprice':totalprice})
