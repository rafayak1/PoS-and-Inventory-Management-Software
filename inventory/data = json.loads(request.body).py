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