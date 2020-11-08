from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Product, Contact, Wishlist, Category, Subategory, Type, Benner
from math import ceil
from django.http import JsonResponse
from login.models import Loginmaster
from cart.models import Order, Coupon
import os
from django.conf import settings
from datetime import date, timedelta
from django.core.files.storage import default_storage, FileSystemStorage
from django.db.models import Sum


# Create your views here.

def index(request):
    allProds = []
    catprods = Product.objects.filter(status='active').values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat, status='active')
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    """------------------for header category------------------"""
    allCategory = Type.objects.all().order_by('id')
    categoryData = {}

    for i in allCategory:
        if i.categoryId.status == 'active':
            if i.categoryId.category in categoryData:
                if i.subcategoryId.status == 'active':
                    if i.subcategoryId.subcategory in categoryData[i.categoryId.category]:
                        if i.status == 'active':
                            if i.type in categoryData[i.categoryId.category][i.subcategoryId.subcategory]:
                                categoryData[i.categoryId.category][i.subcategoryId.subcategory][i.type] = i.id
                            else:
                                if i.type not in categoryData[i.categoryId.category][i.subcategoryId.subcategory]:
                                    if i.status == 'active':
                                        categoryData[i.categoryId.category][i.subcategoryId.subcategory][i.type] = i.id
                    else:
                        if i.subcategoryId.subcategory not in categoryData[i.categoryId.category]:
                            categoryData[i.categoryId.category][i.subcategoryId.subcategory] = {}
                            if i.subcategoryId.status == 'active':
                                categoryData[i.categoryId.category][i.subcategoryId.subcategory][i.type] = i.id
            else:
                if i.categoryId.category not in categoryData:
                    categoryData[i.categoryId.category] = {}
                    if i.subcategoryId.status == 'active':
                        categoryData[i.categoryId.category][i.subcategoryId.subcategory] = {}
                        if i.status == 'active':
                            categoryData[i.categoryId.category][i.subcategoryId.subcategory][i.type] = i.id

    request.session['categoryData'] = categoryData
    # print(">>>>>>>>>>>>", categoryData)

    """--------for benner-----------"""

    bennerList = Benner.objects.all().order_by('rank')

    return render(request, 'user/index.html', {'bennerList': bennerList, 'allProds': allProds})


def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query) < 4:
        params = {'msg': "can't find products !!!"}
    return render(request, 'user/search.html', params)


def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")
        desc = request.POST.get("desc", "")
        print(name, email, phone, desc)
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'user/contact.html', {'thank': thank})


def loadWishlist(request):
    if request.session.get('login_Role') == 'user':

        wishList = Wishlist.objects.filter(userId=request.session['login_Id'])
        return render(request, 'user/wishlist.html', {'wishList': wishList})
    else:
        return redirect('/loadLogin')


def inserWishlist(request):
    if request.session.get('login_Role') == 'user':
        product_Id = request.GET['id']
        userId = request.session['login_Id']

        varify = Wishlist.objects.filter(userId=userId, wishProductId_id=product_Id)
        if len(varify) == 0:
            addOrder = Wishlist(wishProductId_id=product_Id, userId=userId)
            addOrder.save()

    else:
        return JsonResponse({'loginRequire': "loginRequire"})


def deleteWishlist(request):
    if request.session.get('login_Role') == 'user':
        wishlistId = request.GET['id']

        deleteItem = Wishlist.objects.get(pk=wishlistId)
        deleteItem.delete()
        return JsonResponse({"deleteItemId": wishlistId})
    else:
        return redirect('/loadLogin')


def viewProductDetaile(request):
    productId = request.GET['productId']
    getProduct = Product.objects.get(pk=productId)

    return render(request, 'user/viewProductDetail.html', {'getProduct': getProduct})


"""-------------------user side----------------------------------------------------------------------------------


def adminLoadDeshbord(request):
    if request.session.get('login_Role') == 'admin':
        return render(request, 'admin/index.html')
    else:
        return redirect("/")


def adminViewUser(request):
    if request.session.get('login_Role') == 'admin':
        allUser = Loginmaster.objects.filter(loginRole='user').all()
        return render(request, 'admin/viewUser.html', {'allUser': allUser})
    else:
        return redirect("/")


def adminViewDataset(request):
    if request.session.get('login_Role') == 'admin':
        lastDataset = Product.objects.values('pub_date').distinct('pub_date')
        if len(lastDataset) != 0:
            pub_date = lastDataset[0]['pub_date']
            viewProduct = Product.objects.filter(pub_date=pub_date).all().order_by('-id')

            return render(request, 'admin/viewDataset.html', {'viewProduct': viewProduct})
        return render(request, 'admin/viewDataset.html')

    else:
        return redirect("/")


def adminViewCategory(request):
    if request.session.get('login_Role') == 'admin':
        viewCategory = Category.objects.all().order_by('-id')
        return render(request, 'admin/viewCatrgory.html', {'viewCategory': viewCategory})
    else:
        return redirect("/")


def adminViewProduct(request):
    if request.session.get('login_Role') == 'admin':
        allProduct = Product.objects.all().order_by('-id')
        return render(request, 'admin/viewProduct.html', {'allProduct': allProduct})
    else:
        return redirect("/")


def adminViewOrder(request):
    if request.session.get('login_Role') == 'admin':
        allOrder = Order.objects.filter(status="orderd").all().order_by('-id')
        return render(request, 'admin/viewOrder.html', {'allOrder': allOrder})
    else:
        return redirect("/")


def adminAddDataset(request):
    if request.session.get('login_Role') == 'admin':
        return render(request, 'admin/addDataset.html')
    else:
        return redirect("/")


def adminInsertDataset(request):
    if request.session.get('login_Role') == 'admin':
        dataset = request.FILES.getlist('dataset')
        for i in dataset:
            fileName = str(i).rsplit(".")[0]
            data = fileName.split("-")

            product_name = data[0]
            category = data[1]
            subcategory = data[2]
            type = data[3]
            desc = data[4]
            price = data[5]
            size = data[6][1:len(data[6]) - 1]
            image = i

            varifyCategory = Category.objects.filter(category=category, subcategory=subcategory, type=type)
            if len(varifyCategory) != 0:
                varifyProduct = Product.objects.filter(product_name=product_name, category=category,
                                                       subcategory=subcategory, type=type)
                if len(varifyProduct) == 0:
                    addProduct = Product(product_name=product_name, category=category, subcategory=subcategory,
                                         type=type,
                                         desc=desc, price=price, size=size, image=i, categoryId_id=varifyCategory[0].id)
                    addProduct.save()
            else:
                addCategory = Category(category=category, subcategory=subcategory, type=type)
                addCategory.save()
                varifyProduct = Product.objects.filter(product_name=product_name, category=category,
                                                       subcategory=subcategory, type=type)
                if len(varifyProduct) == 0:
                    addProduct = Product(product_name=product_name, category=category, subcategory=subcategory,
                                         type=type,
                                         desc=desc, price=price, size=size, image=i, categoryId_id=addCategory.id)
                    addProduct.save()

        return redirect('/admin/viewDataset')
    else:
        return redirect("/")


def adminAddCategory(request):
    if request.session.get('login_Role') == 'admin':
        return render(request, 'admin/addCategory.html')
    else:
        return redirect("/")


def adminInsertCategory(request):
    category = request.POST['category']
    subcategory = request.POST['subcategory']
    type = request.POST['type']

    varify = Category.objects.filter(category=category, subcategory=subcategory, type=type)
    if len(varify) == 0:
        addCategory = Category(category=category, subcategory=subcategory, type=type)
        addCategory.save()
        return redirect('/admin/viewCategory')
    else:
        return render(request, "admin/addCategory.html", {'categoryExist': "Category all ready Exist."})


def adminDeleteCategory(request):
    print(">>>>>>>>>>>>>>>")
    id = request.GET['id']
    print(">>>>>>>>>>>>>>")
    deleteCategory = Category.objects.get(pk=id)
    deleteCategory.delete()
    return redirect('/admin/viewCategory')


def adminEditCategory(request):
    id = request.GET['id']
    category = Category.objects.filter(pk=id)
    print(">>>>>>>", category, ">>>>>>>", type(category))
    return render(request, 'admin/editCategory.html', {'category': category})


def adminUpdateCategory(request):
    id = request.POST['id']
    category = request.POST['category']
    subcategory = request.POST['subcategory']
    type = request.POST['type']

    varify = Category.objects.filter(category=category, subcategory=subcategory, type=type)
    if len(varify) == 0:
        updateCategory = Category.objects.get(pk=id)
        updateCategory.category = category
        updateCategory.subcategory = subcategory
        updateCategory.type = type
        updateCategory.save()
        return redirect('/admin/viewCategory')
    else:
        return render(request, 'admin/editCategory.html', {'categoryExist': 'category all ready Exist'})


def adminEditDataset(request):
    id = request.GET['id']
    editProduct = Product.objects.filter(pk=id)
    return render(request, 'admin/editProduct.html', {'editProduct': editProduct})


def adminUpdateDataset(request):
    id = request.POST['id']
    product_name = request.POST['product_name']
    category = request.POST['category']
    subcategory = request.POST['subcategory']
    type = request.POST['type']
    desc = request.POST['desc']
    price = request.POST['price']
    size = request.POST['size']

    varify = Product.objects.filter(product_name=product_name, category=category, subcategory=subcategory, type=type,
                                    desc=desc, price=price, size=size)
    if len(varify) == 0:
        path = settings.MEDIA_URL
        updateProduct = Product.objects.get(pk=id)

        fileName = product_name + '-' + category + '-' + subcategory + '-' + type + '-' + desc + '-' + str(
            price) + '-' + size
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.", updateProduct.image)
        updateProduct.product_name = product_name
        updateProduct.category = category
        updateProduct.subcategory = subcategory
        updateProduct.type = type
        updateProduct.desc = desc
        updateProduct.price = price
        updateProduct.size = size
        updateProduct.image = fileName
        updateProduct.save()

        return redirect('/admin/viewDataset')
    else:
        return render(request, 'admin/editProduct.html', {'productExist': 'product all ready Exist'})
    
--------------------------------------------------------------------------------------------"""


def adminLoadDashbord(request):
    revenue = Order.objects.filter(orderstatus='delivered')
    totalRevenue = revenue.aggregate(Sum('totalPrice'))

    users = Loginmaster.objects.filter(loginRole='user').all()
    admin = Loginmaster.objects.filter(loginRole='admin').all()

    product = Product.objects.all()

    orders = Order.objects.filter(orderstatus='delivered')

    return render(request, 'admin/index.html',
                  {'totalPrice__sum': totalRevenue['totalPrice__sum'], 'users': len(users), 'admin': len(admin),
                   'product': len(product), 'orders': len(orders)})


def adminLoadDatabase(request):
    return render(request, 'admin/datatable.html')


def adminLoadValidation(request):
    return render(request, 'admin/validation.html')


def adminViewUser(request):
    userList = Loginmaster.objects.filter(loginRole='user').all()
    return render(request, 'admin/viewUser.html', {'userList': userList})


"""
def adminEditUser(request):
    loginId = request.GET['loginId']
    userInfo = Loginmaster.objects.get(pk=loginId)
    return render(request, 'admin/editUser.html', {'userInfo': userInfo})


def adminUpdateUser(request):
    loginId = request.POST['loginId']
    loginUserName = request.POST['loginUserName']
    loginEmail = request.POST['loginEmail']
    loginMobileNo = request.POST['loginMobileNo']
    loginRole = request.POST['loginRole']
    loginStatus = request.POST['loginStatus']

    userInfo = Loginmaster.objects.get(pk=loginId)
    userInfo.loginUserName = loginUserName
    userInfo.loginEmail = loginEmail
    userInfo.loginMobileNo = loginMobileNo
    userInfo.loginRole = loginRole
    userInfo.loginStatus = loginStatus
    userInfo.save()
    return redirect('/admin/viewUser')
"""


def changeStatus(request, foo):
    if foo == 'login':
        loginId = request.GET['loginId']
        loginStatus = request.GET['loginStatus']
        print(">>>>>>>>>>>>>>>>>>>>>>>", loginStatus)
        changestatus = Loginmaster.objects.get(pk=loginId)
        if loginStatus == 'active':
            changestatus.loginStatus = 'inactive'
        if loginStatus == 'inactive':
            changestatus.loginStatus = 'active'
        changestatus.save()
        if changestatus.loginRole == 'admin':
            return redirect('/admin/viewAdmin')
        if changestatus.loginRole == 'user':
            return redirect('/admin/viewUser')

    if foo == 'category':
        id = request.GET['id']
        status = request.GET['status']
        changeStatus = Category.objects.get(pk=id)
        if status == 'active':
            changeStatus.status = 'inactive'
        if status == 'inactive':
            changeStatus.status = 'active'
        changeStatus.save()
        return redirect('/admin/viewCategory')

    if foo == 'subcategory':
        id = request.GET['id']
        status = request.GET['status']
        changeStatus = Subategory.objects.get(pk=id)
        if status == 'active':
            changeStatus.status = 'inactive'
        if status == 'inactive':
            changeStatus.status = 'active'
        changeStatus.save()
        return redirect('/admin/viewSubcategory')

    if foo == 'type':
        id = request.GET['id']
        status = request.GET['status']
        changeStatus = Type.objects.get(pk=id)
        if status == 'active':
            changeStatus.status = 'inactive'
        if status == 'inactive':
            changeStatus.status = 'active'
        changeStatus.save()
        return redirect('/admin/viewType')

    if foo == 'benner':
        id = request.GET['id']
        status = request.GET['status']
        changeStatus = Benner.objects.get(pk=id)
        if status == 'active':
            changeStatus.status = 'inactive'
        if status == 'inactive':
            changeStatus.status = 'active'
        changeStatus.save()
        return redirect('/admin/viewBenner')

    if foo == 'product':
        id = request.GET['id']
        status = request.GET['status']
        changeStatus = Product.objects.get(pk=id)
        if status == 'active':
            changeStatus.status = 'inactive'
        if status == 'inactive':
            changeStatus.status = 'active'
        changeStatus.save()
        return redirect('/admin/viewProduct')

    if foo == 'dataset':
        id = request.GET['id']
        status = request.GET['status']
        changeStatus = Product.objects.get(pk=id)
        if status == 'active':
            changeStatus.status = 'inactive'
        if status == 'inactive':
            changeStatus.status = 'active'
        changeStatus.save()
        return redirect('/admin/loadDataset')

    if foo == 'coupon':
        id = request.GET['id']
        status = request.GET['status']
        changeStatus = Coupon.objects.get(pk=id)
        if status == 'active':
            changeStatus.status = 'inactive'
        if status == 'inactive':
            changeStatus.status = 'active'
        changeStatus.save()
        return redirect('/admin/viewCoupon')


def adminViewAdmin(request):
    adminList = Loginmaster.objects.filter(loginRole='admin').all()
    return render(request, 'admin/viewAdmin.html', {'adminList': adminList})


def adminEditAdmin(request):
    loginId = request.GET['loginId']
    adminInfo = Loginmaster.objects.get(pk=loginId)
    return render(request, 'admin/editAdmin.html', {'adminInfo': adminInfo})


def adminUpdateAdmin(request):
    loginId = request.POST['loginId']
    loginUserName = request.POST['loginUserName']
    loginEmail = request.POST['loginEmail']
    loginMobileNo = request.POST['loginMobileNo']
    loginPassword = request.POST['loginPassword']
    loginRole = request.POST['loginRole']

    adminInfo = Loginmaster.objects.get(pk=loginId)
    adminInfo.loginUserName = loginUserName
    adminInfo.loginPassword = loginPassword
    adminInfo.loginRole = loginRole

    varify = Loginmaster.objects.filter(loginEmail=loginEmail, loginRole='admin') | Loginmaster.objects.filter(
        loginMobileNo=loginMobileNo, loginRole='admin')
    if len(varify) == 0:
        adminInfo.loginEmail = loginEmail
        adminInfo.loginMobileNo = loginMobileNo
        adminInfo.save()
        return redirect('/admin/viewAdmin')
    else:
        adminInfo.save()
        return render(request, 'admin/editAdmin.html',
                      {'adminInfo': adminInfo, 'msg': 'this email or mobile NO. alredy exist. Othre data is change.'})


def adminLoadAdmin(request):
    return render(request, 'admin/addAdmin.html')


def adminInsertAdmin(request):
    loginUserName = request.POST['loginUserName']
    loginEmail = request.POST['loginEmail']
    loginPassword = request.POST['loginPassword']
    loginMobileNo = request.POST['loginMobileNo']
    loginStatus = request.POST['loginStatus']

    varify = Loginmaster.objects.filter(loginEmail=loginEmail, loginRole='admin') | Loginmaster.objects.filter(
        loginMobileNo=loginMobileNo, loginRole='admin')
    if len(varify) == 0:
        addAdmin = Loginmaster(loginUserName=loginUserName, loginEmail=loginEmail, loginPassword=loginPassword,
                               loginMobileNo=loginMobileNo, loginStatus=loginStatus, loginRole='admin')
        addAdmin.save()
        return redirect('/admin/viewAdmin')
    else:
        dic = {'loginUserName': loginUserName, 'loginEmail': loginEmail, 'loginPassword': loginPassword,
               'loginMobileNo': loginMobileNo, 'loginStatus': loginStatus}
        return render(request, 'admin/addAdmin.html', {'msg': 'this email or mobile NO. alredy exist.', 'dic': dic})


def adminDeleteAdmin(request):
    id = request.GET['id']
    deleteAdmin = Loginmaster.objects.get(pk=id)
    deleteAdmin.delete()
    return redirect('/admin/viewAdmin')


def adminLoadProduct(request):
    return render(request, 'admin/addProduct.html')


def adminInsertProduct(request):
    code = request.POST['code']
    name = request.POST['name']
    image = request.FILES.getlist('image')
    category = request.POST['category']
    subcategory = request.POST['subcategory']
    type = request.POST['type']
    color = request.POST.getlist('color')
    desc = request.POST['desc']
    size = request.POST.getlist('size')  # remember
    price = request.POST['price']
    quantity = request.POST['quantity']
    promocode = request.POST['promocode']
    print(">>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<", color)

    imgStr = ""
    for i in image:
        fs = FileSystemStorage()  # defaults to   MEDIA_ROOT
        fs.save(i.name, i)
        if len(imgStr) == 0:
            imgStr = i.name.rsplit(".")[0]
        else:
            imgStr = imgStr + "," + i.name.rsplit(".")[0]
    sizeStr = ""
    for i in size:
        if len(sizeStr) == 0:
            sizeStr = i
        else:
            sizeStr = sizeStr + "," + i
    colorStr = ""
    for i in color:
        if len(colorStr) == 0:
            colorStr = i
        else:
            colorStr = colorStr + "," + i
    print(">>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<", colorStr)

    varify = Product.objects.filter(code=code)
    if len(varify) == 0:
        addProduct = Product(code=code, name=name, image="[" + imgStr + "]", category=category, subcategory=subcategory,
                             type=type, color="[" + colorStr + "]", desc=desc, size="[" + sizeStr + "]", price=price,
                             quantity=quantity, promocode=promocode, status='active')
        addProduct.save()

        varifyCategory = Category.objects.filter(category=category)
        if len(varifyCategory) == 0:
            addCategory = Category(category=category, status='active')
            addCategory.save()

        getCategory = Category.objects.get(category=category)
        varifySubcategory = Subategory.objects.filter(subcategory=subcategory, categoryId_id=getCategory.id)
        if len(varifySubcategory) == 0:
            addSubcategory = Subategory(subcategory=subcategory, categoryId_id=getCategory.id, status='active')
            addSubcategory.save()

        getCategory = Category.objects.get(category=category)
        getSubcategory = Subategory.objects.get(subcategory=subcategory, categoryId_id=getCategory.id)
        varifyType = Type.objects.filter(type=type, categoryId_id=getCategory.id, subcategoryId_id=getCategory.id)
        if len(varifyType) == 0:
            addType = Type(type=type, categoryId_id=getCategory.id, subcategoryId_id=getSubcategory.id,
                           status='active')
            addType.save()

    return render(request, 'admin/addProduct.html')


def adminViewProduct(request):
    productList = Product.objects.all().order_by('-id')
    return render(request, 'admin/viewProduct.html', {'productList': productList})


def adminDeleteProduct(request, foo):
    id = request.GET['id']

    deleteProduct = Product.objects.get(pk=id)
    for i in list(str(deleteProduct.image[1:len(deleteProduct.image) - 1]).split(",")):
        os.remove("../eshopper/media/" + i + ".jpeg")
    deleteProduct.delete()

    if foo == 'dataset':
        return redirect('/admin/loadDataset')
    else:
        return redirect('/admin/viewProduct')


def adminEditProduct(request, foo):
    navigate = foo
    id = request.GET['id']
    editProduct = Product.objects.get(pk=id)

    return render(request, 'admin/editProduct.html', {'editProduct': editProduct, 'navigate': navigate})


def adminDeleteImage(request):
    imageName = request.GET['imageName']
    productId = request.GET['productId']
    print(">>>>>>>>>>>>>>>>>", imageName, "<<<<<<<<<<<<<<<<", productId)
    deleteImage = Product.objects.get(pk=productId)
    images = list(str(deleteImage.image[1:len(deleteImage.image) - 1]).split(","))
    images.remove(imageName)
    os.remove('../eshopper/media/' + imageName + '.jpeg')

    imgStr = ""
    for i in images:
        if len(imgStr) == 0:
            imgStr = i
        else:
            imgStr = imgStr + "," + i

    deleteImage.image = "[" + imgStr + "]"
    deleteImage.save()
    return JsonResponse({'imageName': imageName})


def adminUpdateProduct(request):
    id = request.POST['id']
    navigate = request.POST['navigate']
    code = request.POST['code']
    name = request.POST['name']
    image = request.FILES.getlist('image')
    category = request.POST['category']
    subcategory = request.POST['subcategory']
    type = request.POST['type']
    color = request.POST.getlist('color')
    desc = request.POST['desc']
    size = request.POST.getlist('size')
    price = request.POST['price']
    quantity = request.POST['quantity']
    promocode = request.POST['promocode']

    imgStr = ""
    for i in image:
        fs = FileSystemStorage()  # defaults to   MEDIA_ROOT
        fs.save(i.name, i)
        if len(imgStr) == 0:
            imgStr = i.name.rsplit(".")[0]
        else:
            imgStr = imgStr + "," + i.name.rsplit(".")[0]
    sizeStr = ""
    for i in size:
        if len(sizeStr) == 0:
            sizeStr = i
        else:
            sizeStr = sizeStr + "," + i
    colorStr = ""
    for i in color:
        if len(colorStr) == 0:
            colorStr = i
        else:
            colorStr = colorStr + "," + i

    updateProduct = Product.objects.get(pk=id)
    if len(imgStr) > 0 and updateProduct.image != "[]":
        image = str(updateProduct.image)[1:len(str(updateProduct.image)) - 1] + "," + imgStr
    elif updateProduct.image == "[]":
        image = imgStr
    else:
        image = str(updateProduct.image)[1:len(str(updateProduct.image)) - 1]

    updateProduct.code = code
    updateProduct.name = name
    updateProduct.image = "[" + image + "]"
    updateProduct.category = category
    updateProduct.subcategory = subcategory
    updateProduct.type = type
    updateProduct.color = "[" + colorStr + "]"
    updateProduct.desc = desc
    updateProduct.size = "[" + sizeStr + "]"
    updateProduct.price = price
    updateProduct.quantity = quantity
    updateProduct.promocode = promocode
    updateProduct.save()

    varifyCategory = Category.objects.filter(category=category)
    if len(varifyCategory) == 0:
        addCategory = Category(category=category, status='active')
        addCategory.save()

    getCategory = Category.objects.get(category=category)
    varifySubcategory = Subategory.objects.filter(subcategory=subcategory, categoryId_id=getCategory.id)
    if len(varifySubcategory) == 0:
        addSubcategory = Subategory(subcategory=subcategory, categoryId_id=getCategory.id, status='active')
        addSubcategory.save()

    getCategory = Category.objects.get(category=category)
    getSubcategory = Subategory.objects.get(subcategory=subcategory, categoryId_id=getCategory.id)
    varifyType = Type.objects.filter(type=type, categoryId_id=getCategory.id, subcategoryId_id=getCategory.id)
    if len(varifyType) == 0:
        addType = Type(type=type, categoryId_id=getCategory.id, subcategoryId_id=getSubcategory.id,
                       status='active')
        addType.save()

    if navigate == 'dataset':
        return redirect('/admin/loadDataset')
    else:
        return redirect('/admin/viewProduct')


def adminLoadDataset(request):
    lastDataset = Product.objects.values('pub_date').distinct('pub_date')
    if len(lastDataset) != 0:
        pub_date = lastDataset[0]['pub_date']
        productList = Product.objects.filter(pub_date=pub_date).all().order_by('-id')

        return render(request, 'admin/addDataset.html', {'productList': productList})
    return render(request, 'admin/addDataset.html')


def adminInsertDataset(request):
    dataset = request.FILES.getlist('dataset')

    available = ""
    for i in dataset:
        fileName = str(i).rsplit(".")[0]
        data = fileName.split("-")

        if len(data) > 1:
            code = data[0]
            name = data[1]
            category = data[2]
            subcategory = data[3]
            type = data[4]
            color = data[5]
            desc = data[6]
            price = data[7]
            size = data[8]
            images = data[9]
            quantity = data[10]

            varifyCategory = Category.objects.filter(category=category)
            if len(varifyCategory) == 0:
                addCategory = Category(category=category, status='active')
                addCategory.save()

            getCategory = Category.objects.get(category=category)
            varifySubcategory = Subategory.objects.filter(subcategory=subcategory, categoryId_id=getCategory.id)
            if len(varifySubcategory) == 0:
                addSubcategory = Subategory(subcategory=subcategory, categoryId_id=getCategory.id, status='active')
                addSubcategory.save()

            getCategory = Category.objects.get(category=category)
            getSubcategory = Subategory.objects.get(subcategory=subcategory, categoryId_id=getCategory.id)
            varifyType = Type.objects.filter(type=type, categoryId_id=getCategory.id, subcategoryId_id=getCategory.id)
            if len(varifyType) == 0:
                addType = Type(type=type, categoryId_id=getCategory.id, subcategoryId_id=getSubcategory.id,
                               status='active')
                addType.save()

            varifyProduct = Product.objects.filter(code=code)

            if len(varifyProduct) == 0:

                addProduct = Product(code=code, name=name, image=images,
                                     category=category, subcategory=subcategory,
                                     type=type, color=color,
                                     desc=desc, price=price, size=size, quantity=quantity, status='active')
                addProduct.save()

                fs = FileSystemStorage()  # defaults to   MEDIA_ROOT
                fs.save(i.name, i)

                os.rename('../eshopper/media/' + i.name, '../eshopper/media/' + code + 'img1.' + str(i).rsplit(".")[1])

            else:
                available = available + " " + code

        else:
            fs = FileSystemStorage()  # defaults to   MEDIA_ROOT
            fs.save(i.name, i)

        if len(available) != 0:
            messages.success(request, "this product already available : " + available)

    return redirect('/admin/loadDataset')


def adminViewCategory(request):
    couponList = Coupon.objects.all()
    categoryList = Category.objects.all().order_by('-id')
    return render(request, 'admin/viewCategory.html', {'categoryList': categoryList, 'couponList': couponList})


def adminInsertCategory(request):
    category = request.POST['category']
    # couponId = request.POST['coupon']
    varify = Category.objects.filter(category=category)
    if len(varify) == 0:
        addCategory = Category(category=category, status='active')
        addCategory.save()
        # subcategory = Subategory.objects.filter(categoryId_id=addCategory.id)
        # for i in subcategory:
        #     i.coupon_id=couponId
        #     i.save()
        messages.success(request, 'category successfully saved.')
        return redirect('/admin/viewCategory')
    else:
        messages.success(request, 'Category already exist.')
        return redirect('/admin/viewCategory')


def adminDeleteCategory(request):
    id = request.GET['id']
    deleteCategory = Category.objects.get(pk=id)
    deleteCategory.delete()
    messages.success(request, 'category successfully deleted.')
    return redirect('/admin/viewCategory')


def adminEditCategory(request):
    couponList = Coupon.objects.all()
    id = request.GET['id']
    editCategory = Category.objects.get(pk=id)
    categoryList = Category.objects.all().order_by('-id')
    return render(request, 'admin/viewCategory.html',
                  {'editCategory': editCategory, 'categoryList': categoryList, 'couponList': couponList})


def adminUpdateCategory(request):
    id = request.POST['id']
    category = request.POST['category']
    # couponId = request.POST['coupon']
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", couponId)
    varify = Category.objects.filter(category=category)
    if len(varify) == 0:
        updateCategory = Category.objects.get(pk=id)
        updateCategory.category = category
        # updateCategory.coupon_id = couponId
        updateCategory.save()
        # subcategory = Subategory.objects.filter(categoryId=updateCategory.id)
        # for i in subcategory:
        #     i.coupon_id=couponId
        #     i.save()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>updateCategory.coupon_id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", updateCategory.coupon_id)
        messages.success(request, 'category successfully updated.')
        return redirect('/admin/viewCategory')
    else:
        messages.success(request, 'Category already exist.')
        # updateCategory = Category.objects.get(pk=id)
        # updateCategory.coupon_id = couponId
        # updateCategory.save()
        # subcategory = Subategory.objects.filter(categoryId=updateCategory.id)
        # for i in subcategory:
        #     i.coupon_id = couponId
        #     i.save()
        return redirect('/admin/viewCategory')


def adminViewSubcategory(request):
    couponList = Coupon.objects.all()
    subcategoryList = Subategory.objects.all().order_by('-id')
    categoryList = Category.objects.all().order_by('-id')
    return render(request, 'admin/viewSubcategory.html',
                  {'subcategoryList': subcategoryList, 'categoryList': categoryList, 'couponList': couponList})


def adminInsertSubCategory(request):
    categoryId = request.POST['categoryId']
    subcategory = request.POST['subcategory']
    varify = Subategory.objects.filter(subcategory=subcategory, categoryId_id=categoryId)
    if len(varify) == 0:
        addCategory = Subategory(subcategory=subcategory, categoryId_id=categoryId, status='active')
        addCategory.save()
        messages.success(request, 'Subcategory successfully saved.')
        return redirect('/admin/viewSubcategory')
    else:
        messages.success(request, 'Subcategory alredy exist.')
        return redirect('/admin/viewSubcategory')


def adminDeleteSubcategory(request):
    id = request.GET['id']
    deleteSubcategory = Subategory.objects.get(pk=id)
    deleteSubcategory.delete()
    messages.success(request, 'Subcategory successfully deleted.')
    return redirect('/admin/viewSubcategory')


def adminEditSubcategory(request):
    id = request.GET['id']
    couponList = Coupon.objects.all()
    editSubcategory = Subategory.objects.get(pk=id)
    subcategoryList = Subategory.objects.all().order_by('-id')
    categoryList = Category.objects.all().order_by('-id')
    return render(request, 'admin/viewSubcategory.html',
                  {'editSubcategory': editSubcategory, 'subcategoryList': subcategoryList,
                   'categoryList': categoryList,'couponList':couponList})


def adminUpdateSubcategory(request):
    id = request.POST['id']
    categoryId = request.POST['categoryId']
    subcategory = request.POST['subcategory']
    # coupon = request.POST['coupon']
    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",coupon)
    varify = Subategory.objects.filter(categoryId_id=categoryId, subcategory=subcategory)
    if len(varify) == 0:
        updateSubcategory = Subategory.objects.get(pk=id)
        updateSubcategory.categoryId_id = categoryId
        updateSubcategory.subcategory = subcategory
        # updateSubcategory.coupon_id=int(coupon)
        updateSubcategory.save()
        messages.success(request, 'Subcategory successfully updated.')
        return redirect('/admin/viewSubcategory')
    else:
        messages.success(request, 'Subcategory already exist.')
        return redirect('/admin/viewSubcategory')


def adminViewType(request):
    typeList = Type.objects.all().order_by('-id')
    categoryList = Category.objects.all().order_by('-id')
    return render(request, 'admin/viewType.html', {'categoryList': categoryList, 'typeList': typeList})


def adminAjaxSubcategory(request):
    categoryId = request.GET['categoryId']
    subcategoryList = Subategory.objects.filter(categoryId=categoryId)
    ajaxSubcategoryJson = [i.as_dict() for i in subcategoryList]
    return JsonResponse(ajaxSubcategoryJson, safe=False)


def adminInsertType(request):
    categoryId = request.POST['categoryId']
    subcategoryId = request.POST['subcategoryId']
    type = request.POST['type']

    varify = Type.objects.filter(type=type, categoryId_id=categoryId, subcategoryId_id=subcategoryId)
    if len(varify) == 0:
        addType = Type(type=type, subcategoryId_id=subcategoryId, categoryId_id=categoryId, status='active')
        addType.save()
        messages.success(request, 'Type successfuly saved.')
        return redirect('/admin/viewType')
    else:
        messages.success(request, 'Type alredy exist.')
        return redirect('/admin/viewType')


def adminDeleteType(request):
    id = request.GET['id']
    deleteType = Type.objects.get(pk=id)
    deleteType.delete()
    messages.success(request, 'Type successfully deleted.')
    return redirect('/admin/viewType')


def adminEditType(request):
    id = request.GET['id']
    editType = Type.objects.get(pk=id)
    typeList = Type.objects.all().order_by('-id')
    categoryList = Category.objects.all().order_by('-id')
    return render(request, 'admin/viewType.html',
                  {'typeList': typeList,
                   'categoryList': categoryList, 'editType': editType})


def adminUpdateType(request):
    id = request.POST['id']
    categoryId = request.POST['categoryId']
    subcategoryId = request.POST['subcategoryId']
    type = request.POST['type']

    varify = Type.objects.filter(type=type, categoryId_id=categoryId, subcategoryId_id=subcategoryId)
    if len(varify) == 0:
        updateType = Type.objects.get(pk=id)
        updateType.type = type
        updateType.categoryId_id = categoryId
        updateType.subcategoryId_id = subcategoryId
        updateType.save()
        messages.success(request, 'Type successfuly Updated.')
        return redirect('/admin/viewType')

    else:
        messages.success(request, 'Type alredy Exist.')
        return redirect('/admin/viewType')


def adminLoadBenner(request):
    return render(request, 'admin/addBenner.html')


def adminInsertBenner(request):
    image = request.FILES.get('image')
    link = request.POST['link']
    contact = request.POST['contact']
    rank = request.POST['rank']

    addBenner = Benner(image=image, link=link, contact=contact, rank=rank, status='active')
    addBenner.save()
    messages.success(request, 'Benner successfuly saved.')
    return redirect('/admin/viewBenner')


def adminViewBenner(request):
    bennerList = Benner.objects.all().order_by('rank')
    return render(request, 'admin/viewBenner.html', {'bennerList': bennerList})


def adminDeleteBenner(request):
    id = request.GET['id']
    deleteBenner = Benner.objects.get(pk=id)
    os.remove('../eshopper/media/' + str(deleteBenner.image))
    deleteBenner.delete()
    messages.success(request, 'Benner successfuly deleted')
    return redirect('/admin/viewBenner')


def adminEditBenner(request):
    id = request.GET['id']
    editBenner = Benner.objects.get(pk=id)
    return render(request, 'admin/addBenner.html', {'editBenner': editBenner})


def adminUpdateBenner(request):
    id = request.POST['id']
    image = request.FILES.get('image')
    print(">>>>>>>>>>>>>.", image)
    link = request.POST['link']
    contact = request.POST['contact']
    rank = request.POST['rank']

    updateBenner = Benner.objects.get(pk=id)
    if image != None:
        os.remove('../eshopper/media/' + str(updateBenner.image))
        updateBenner.image = image
    updateBenner.link = link
    updateBenner.contact = contact
    updateBenner.rank = rank
    updateBenner.save()
    messages.success(request, 'Benner successfuly updated.')
    return redirect('/admin/viewBenner')


def adminViewOrder(request):
    allOrder = Order.objects.exclude(orderstatus='addtocart').all().order_by('-id')
    return render(request, 'admin/viewOrder.html', {'allOrder': allOrder})


def adminOrderStatus(request, foo):
    if foo == 'ordered':
        orderId = request.GET['orderId']
        changestatus = Order.objects.get(pk=orderId)
        changestatus.orderstatus = 'ordered'
        product = eval(changestatus.product)
        for key, value in product.items():
            value['orderstatus'] = 'ordered'
        changestatus.product = product
        changestatus.save()
        return redirect('/admin/viewOrder')

    if foo == 'packed':
        orderId = request.GET['orderId']
        changestatus = Order.objects.get(pk=orderId)
        changestatus.orderstatus = 'packed'
        product = eval(changestatus.product)
        for key, value in product.items():
            value['orderstatus'] = 'packed'
        changestatus.product = product
        changestatus.save()
        return redirect('/admin/viewOrder')

    if foo == 'dispatched':
        orderId = request.GET['orderId']
        changestatus = Order.objects.get(pk=orderId)
        changestatus.orderstatus = 'dispatched'
        product = eval(changestatus.product)
        for key, value in product.items():
            value['orderstatus'] = 'dispatched'
        changestatus.product = product
        changestatus.save()
        return redirect('/admin/viewOrder')

    if foo == 'delivered':
        orderId = request.GET['orderId']
        changestatus = Order.objects.get(pk=orderId)
        changestatus.orderstatus = 'delivered'
        product = eval(changestatus.product)
        for key, value in product.items():
            value['orderstatus'] = 'delivered'
        changestatus.product = product
        changestatus.save()
        return redirect('/admin/viewOrder')

    if foo == 'return':
        orderId = request.GET['orderId']
        productId = request.GET['productId']
        changestatus = Order.objects.get(pk=orderId)
        changestatus.anyReturn = 'yes'
        product = eval(changestatus.product)
        product[productId]['orderstatus'] = 'return'
        today = date.today()
        product[productId]['returnDate'] = str(today)
        changestatus.product = product
        changestatus.save()
        if request.session.get('login_Role') == 'admin':
            return redirect('/admin/viewOrder')
        elif request.session.get('login_Role') == 'user':
            return redirect('/viewOrder')
