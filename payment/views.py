from django.db.models import Sum
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
# from payment.models import Payment
from datetime import date, timedelta
from PayTm import Checksum, PaytmChecksum
from cart.models import Order
from login.models import Loginmaster
from shop.models import Product
from django.contrib import messages
import requests
import json
from io import BytesIO
from django.template.loader import get_template
# from xhtml2pdf import pisa

MERCHANT_KEY = '!c362cynoSpV4ER@'


# Create your views here.

def loadPayment(request):
    # orderList = Order.objects.filter(userId=request.session['login_Id'], status="addtocart").order_by('id')
    # totalOrderAmount = orderList.aggregate(Sum('totalPrice'))
    # allOrder = []
    # for i in orderList:
    #     allOrder.append(i.id)
    # print(">>>>>>>>>>>>>>", allOrder)
    # addPayment = Payment.objects.filter(payment=totalOrderAmount['totalPrice__sum'], paymentstatus='pending',
    #                                     orders=str(allOrder)[1:len(str(allOrder)) - 1],
    #                                     userId_id=request.session['login_Id'])
    # if len(addPayment) == 0:
    #     addPayment = Payment(payment=totalOrderAmount['totalPrice__sum'], paymentstatus="pending",
    #                          userId_id=request.session['login_Id'], orders=str(allOrder)[1:len(str(allOrder)) - 1])
    #     addPayment.save()
    #     orderid = addPayment.id
    # else:
    #     orderid = addPayment[0].id

    orderList = Order.objects.get(userId=request.session['login_Id'], orderstatus="addtocart")

    param_dict = {

        'MID': 'nHXgex32367017368258',
        'ORDER_ID': str(orderList.id),
        'TXN_AMOUNT': str(orderList.totalPrice),
        'CUST_ID': request.session['login_Email'],
        'INDUSTRY_TYPE_ID': 'Retail',
        'WEBSITE': 'WEBSTAGING',
        'CHANNEL_ID': 'WEB',
        'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',

    }

    param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", param_dict)
    return render(request, 'user/paytm.html', {'param_dict': param_dict})


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    print("++++++++++++++++++++++++++++++++++=", response_dict)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')

            orderList = Order.objects.get(pk=int(response_dict['ORDERID']))
            orderList.orderstatus = 'ordered'
            orderList.paymentstatus = 'success'
            today = date.today()
            delhiveryDate = today + timedelta(days=3)
            orderList.delhiveryDate = delhiveryDate
            orderList.orderDate = today

            product = eval(orderList.product)
            for key, value in product.items():
                value['orderId'] = orderList.id
                value['orderDate'] = str(orderList.orderDate)
                value['delhiveryDate'] = str(orderList.delhiveryDate)
                value['orderstatus'] = orderList.orderstatus
                value['paymentstatus'] = orderList.paymentstatus
                value['userId'] = orderList.userId_id

                quantityCounter = Product.objects.get(pk=int(key))
                size = list(str(quantityCounter.size[1:len(quantityCounter.size) - 1]).split(","))
                quantity = list(str(quantityCounter.quantity[1:len(quantityCounter.quantity) - 1]).split(","))

                getIndexSize = size.index(value['size'])
                getQuantity = int(quantity[getIndexSize]) - int(value['quantity'])
                quantity.pop(getIndexSize)
                quantity.insert(getIndexSize, getQuantity)
                strquantity=""
                for i in quantity:
                    strquantity = strquantity + str(i)+","
                quantityCounter.quantity = "["+strquantity[0:len(strquantity)-1]+"]"
                quantityCounter.save()

            orderList.product = product
            orderList.txnId = response_dict['TXNID']

            orderList.save()

            user = Loginmaster.objects.get(pk=orderList.userId_id)
            request.session['login_Id'] = user.id
            request.session['login_UserName'] = user.loginUserName
            request.session['login_Email'] = user.loginEmail
            request.session['login_Role'] = user.loginRole
            request.session['login_MobileNO'] = user.loginMobileNo
            messages.success(request, "your order success fully received")
            return redirect('/viewOrder')



            # getPayment = Payment.objects.get(pk=int(str(response_dict['ORDERID']).replace("ORD","")))
            # getPayment.paymentstatus = "success"
            # getPayment.save()
            # userId = getPayment.userId_id
            # orders = getPayment.orders.split(',')
            # for i in orders:
            #     updateOrder = Order.objects.get(pk=int(i))
            #     updateOrder.paymentId_id = int(str(response_dict['ORDERID']).replace("ORD",""))
            #     updateOrder.save()
            # updateOrder = Order.objects.filter(userId_id=request.session['login_Id'], status="addtocart")
            # updateOrder.update(status='orderd')
        else:
            # print('order was not successful because' + response_dict['RESPMSG'])

            orderList = Order.objects.get(pk=int(response_dict['ORDERID']))
            orderList.orderstatus = 'addtocart'
            orderList.paymentstatus = 'fail'
            orderList.save()

            user = Loginmaster.objects.get(pk=orderList.userId_id)
            request.session['login_Id'] = user.id
            request.session['login_UserName'] = user.loginUserName
            request.session['login_Email'] = user.loginEmail
            request.session['login_Role'] = user.loginRole
            request.session['login_MobileNO'] = user.loginMobileNo

            messages.success(request, "some issues")
            return redirect('/checkout')

            # getPayment = Payment.objects.get(pk=int(str(response_dict['ORDERID'])))
            # userId = getPayment.userId_id
            # getPayment.paymentstatus = 'fail'
            # getPayment.save()

            # return render(request, 'user/paymentstatus.html', {'response': response_dict})


"""-------------------------------------refund process--------------------------------------------------------"""


def adminRefund(request):
    orderId = request.GET['orderId']
    productId = request.GET['productId']

    getOrder = Order.objects.get(pk=orderId)
    getproduct = eval(getOrder.product)
    refundAmount = int(getproduct[productId]['totalprice']) * 0.7
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

    # Generate checksum by parameters we have in body
    # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
    checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), MERCHANT_KEY)

    paytmParams["head"] = {
        "signature": checksum
    }

    post_data = json.dumps(paytmParams)

    # for Staging
    url = "https://securegw-stage.paytm.in/refund/apply"

    # for Production
    # url = "https://securegw.paytm.in/refund/apply"

    response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
    print(response)
    if response['body']['resultInfo']['resultStatus'] == 'TXN_FAILURE':
        fail = 'refund status :' + response['body']['resultInfo']['resultMsg']
        messages.success(request, fail)

    elif response['body']['resultInfo']['resultStatus'] == 'PENDING':
        getproduct[productId]['paymentstatus'] = 'refund'
        today = date.today()
        getproduct[productId]['refundDate'] = str(today)
        getproduct[productId]['refundId'] = response['body']['refundId']
        getproduct[productId]['refundAmount'] = response['body']['refundAmount']
        getOrder.product = getproduct
        refAmo = float(str(response['body']['refundAmount']))
        getOrder.totalPrice = getOrder.totalPrice - refAmo
        getOrder.save()

        # quantityCounter = Product.objects.get(pk=int(productId))
        # quantityCounter.quantity = quantityCounter.quantity + int(getproduct[productId]['quantity'])
        # quantityCounter.save()

        quantityCounter = Product.objects.get(pk=int(productId))
        size = list(str(quantityCounter.size[1:len(quantityCounter.size) - 1]).split(","))
        quantity = list(str(quantityCounter.quantity[1:len(quantityCounter.quantity) - 1]).split(","))

        getIndexSize = size.index(getproduct[productId]['size'])
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",getIndexSize)
        getQuantity = int(quantity[getIndexSize]) + int(getproduct[productId]['quantity'])
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..",getQuantity)
        quantity.pop(getIndexSize)
        quantity.insert(getIndexSize, getQuantity)
        strquantity = ""
        for i in quantity:
            strquantity = strquantity + str(i) + ","
        quantityCounter.quantity = "[" + strquantity[0:len(strquantity) - 1] + "]"
        quantityCounter.save()

    return redirect('/admin/viewOrder')


##################################################################################
def getpdfPage(request):
    orderId = request.GET['orderId']
    orderList = Order.objects.get(pk=orderId)
    today = date.today()
    data = {'orderList': orderList, 'today': today}
    template = get_template("user/pdf_page.html")
    data_p = template.render(data)
    response = BytesIO()

    pdfPage = pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")), response)
    if not pdfPage.err:
        print(">>>>>>>>>>>>>>>>>>>>>>", orderList)
        return HttpResponse(response.getvalue(), content_type="application/pdf")
    else:
        return HttpResponse("Error Generating PDF")
