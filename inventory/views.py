from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core import serializers

import json
import re
from .models import *
from .forms import *
from .decorators import *
from .models import Order

crv = None

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

@unauthenticated
def home(request):
    return render(request, 'inventory/home2.html')

@login_required(login_url='loginCash')
def stonk(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM inventory_stock")
    data = dictfetchall(cursor)
    return render(request, 'inventory/stock.html', {'data': data})

@login_required(login_url='loginCash')
def createStock(request):
    form = StockForm()
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/stock')
    context = {'form': form}

    return render(request, 'inventory/stock_form.html', context)

@login_required(login_url='loginCash')
def updateStock(request, pk):
    stockObj = stock.objects.get(sku=pk)
    form = StockForm(instance=stockObj)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stockObj)
        if form.is_valid():
            form.save()
            return redirect('/stock')
    context = {'form': form}
    return render(request, 'inventory/stock_form.html', context)

@unauthenticated
def registerCust(request):
    # if User().is_authenticated:
    #     return redirect('cashier')
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(
                user = user,
                )
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created successfully for ' + username)
            return redirect('loginCust')
    context = {'form': form}
    return render(request, 'inventory/registerCust.html', context)

@unauthenticated
def registerCash(request):
    # if User().is_authenticated:
    #     return redirect('cashier')
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='cashier')
            user.groups.add(group)
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created successfully for ' + username)
            return redirect('loginCash')
    context = {'form': form}
    return render(request, 'inventory/registercash.html', context)

@unauthenticated
def loginCust(request):
    # if User().is_authenticated:
    #     return redirect('cashier')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('customer', pk=user.id)
        else:
            messages.info(request, 'Username OR password is incorrect')
        
    return render(request, 'inventory/logincust.html')

@unauthenticated
def loginCash(request):
    # if User().is_authenticated:
    #     return redirect('cashier')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return cashier(request)
        else:
            messages.info(request, 'Username OR password is incorrect')
        
    return render(request, 'inventory/logincash.html')

def logoutCust(request):
    logout(request)
    return redirect('home')

def logoutCash(request):
    logout(request)
    return redirect('home')

def logoutAny(request):
    logout(request)
    return redirect('home')

def customer(request, pk):
    customer = Customer.objects.get(user_id=pk)
    cursor = connection.cursor()
    query = 'SELECT * FROM auth_user WHERE id = ' + pk
    cursor.execute(query)
    data = dictfetchall(cursor)
    try:
        order = Order.objects.filter(customer=customer.id)
        for ouda in order:
            items = ouda.orderitem_set.all()
        items = []
    except:
        items = []

    cotext = {'data': data, 'items': items, 'order': order}
    return render(request, 'inventory/customer.html', cotext)

# @login_required(login_url='loginCash')
@allowed_users(allowed_roles=['cashier'])
def cashier(request, external_context=None):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM auth_user WHERE is_superuser = 0")
    product_cursor = connection.cursor()
    product_cursor.execute("SELECT * FROM inventory_stock")
    data = dictfetchall(cursor)    
    data_ = dictfetchall(product_cursor)
    context = {'customers': data, 'products': data_}
    if external_context:
        # get chosen customer's order history
        customer = crv[0]['id']
        customer = Customer.objects.get(user_id=customer)
        print(customer.user.first_name)
        orders = Order.objects.filter(customer=customer, complete=1)
        context.update(external_context)
        context.update({'orders': orders})
    else:
        context.update({'chosen': crv})
    return render(request, 'inventory/cashier.html', context)

def chooseCust(request, pk):
    # flushCart()
    cursor_0 = connection.cursor()
    query = 'SELECT * FROM auth_user WHERE id = ' + pk
    cursor_0.execute(query)
    data_0 = dictfetchall(cursor_0)
    external_context = {'chosen': data_0}
    global crv
    crv = data_0
    return cashier(request, external_context)

# remove carts with incomplete status before choosing a new customer
def flushCart():
    incompleteOrders = Order.objects.filter(complete=0)
    for incompleteOrder in incompleteOrders:
        orderItem_ = orderItem.objects.filter(orderid=incompleteOrder)
        for oudaIteam in orderItem_:
            stock_inventory = stock.objects.get(sku=oudaIteam.stock.sku)
            stock_inventory.quantity += oudaIteam.quantity
            stock_inventory.save()
            oudaIteam.delete()
        incompleteOrder.delete()

def cart(request):
    payment = PaymentMethodForm()
    if request.method == 'POST':
        payment = PaymentMethodForm(request.POST)
        if payment.is_valid():
            payment.save()
            return checkout(request)
    global crv
    if crv:
        customer = crv[0]['id']
        customer = Customer.objects.get(user_id=customer)
        order, created = Order.objects.get_or_create(customer=customer, complete=0)
        items = order.orderitem_set.all()
    else:
        items = []
        order = []
    context = {'items': items, 'customer': crv, 'order': order, 'payment': payment}
    return render(request, 'inventory/cart.html', context)

def updateItem(request):
    data = json.loads(request.body)
    global crv
    productId = data['productId']
    action = data['action']
    customer = crv[0]['id']
    customer = Customer.objects.get(user_id=customer)
    product = stock.objects.get(sku=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem_, created = orderItem.objects.get_or_create(orderid=order, stock=product)
    if action == 'add':
        if stock.objects.get(sku=productId).quantity >= 1:
            stock_inventory = stock.objects.get(sku=productId)
            stock_inventory.quantity -= 1
            orderItem_.quantity = (orderItem_.quantity + 1)
    elif action == 'remove':
        stock_inventory = stock.objects.get(sku=productId)
        stock_inventory.quantity += 1
        stock_inventory.save()
        orderItem_.quantity = (orderItem_.quantity - 1)
    orderItem_.save()
    stock_inventory.save()
    if orderItem_.quantity <= 0:
        orderItem_.delete()
    return JsonResponse('Item was added', safe=False)

def checkout(request):
    global crv
    customer = crv[0]['id']
    customer = Customer.objects.get(user_id=customer)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    order.complete = True
    order.save()
    return cashier(request)
    
def refund(request, pk):
    order_ = Order.objects.get(id=pk)
    status = order_.refundOrder
    return cashier(request)

def change_password(request):
    if request.method == 'POST':
        form = Password_Change_Form(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            password = user.password
            messages.success(request, 'Your password was successfully updated!')
            if request.user.groups.filter(name='customer').exists():
                return redirect('customer', request.user.id)
            elif request.user.groups.filter(name='cashier').exists():
                return redirect('cashier')
            elif request.user.groups.filter(name='owner').exists():
                return redirect('owner')
            else:
                return redirect('home')
        else:
            messages.info(request, 'Please correct the error below.')
            
    else:
        form = Password_Change_Form(request.user)
    return render(request, 'inventory/change_password.html', {
        'form': form
    })
    
#add search functionality in cashier page to search for a customer
def search_cust(request):
    if request.GET.get('search_cust'):
        searched = request.GET.get('search_cust')
        try:
            customers = Customer.objects.filter(user__first_name__contains=searched)
            pk = customers.values_list('user_id', flat=True)
            return redirect('chooseCust', pk=pk[0])
        except:
            pass
        
    return render(request, 'inventory/cashier.html')

# def products(request):
#     products = stock.objects.all()
#     context = {'products': products}
#     return context

#add search functionality in cashier page to search for a product
# def search_prod(request):
#     if request.GET.get('search_prod'):
#         searched = request.GET.get('search_prod')
#         try:
#             products = stock.objects.filter(name__contains=searched)
#             pk = products.values_list('sku', flat=True)
#             return redirect('products', pk=pk[0])
#         except:
#             pass
        
#     return render(request, 'inventory/cashier.html')
    

    
