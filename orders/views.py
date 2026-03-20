import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, Review
from services.models import Service
from pets.models import Pet


@login_required
def order_create(request, service_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    pets = Pet.objects.filter(owner=request.user)

    if request.method == 'POST':
        pet_id = request.POST.get('pet_id')
        pet_name = request.POST.get('pet_name', '')

        if pet_id:
            pet = get_object_or_404(Pet, pk=pet_id, owner=request.user)
            pet_name = pet.name

        order = Order.objects.create(
            order_no=uuid.uuid4().hex[:16].upper(),
            user=request.user,
            service=service,
            pet_name=pet_name,
            appointment_date=request.POST['appointment_date'],
            appointment_time=request.POST['appointment_time'],
            total_price=service.price,
            remark=request.POST.get('remark', ''),
            status='pending',
        )
        messages.success(request, f'预约成功！订单号：{order.order_no}')
        return redirect('orders:order_detail', pk=order.pk)

    return render(request, 'orders/order_form.html', {
        'service': service,
        'pets': pets,
    })


@login_required
def order_list(request):
    if request.user.is_provider:
        orders = Order.objects.filter(service__provider=request.user).select_related('service', 'user')
    else:
        orders = Order.objects.filter(user=request.user).select_related('service')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.user != request.user and order.service.provider != request.user:
        messages.error(request, '无权查看此订单')
        return redirect('orders:order_list')
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    action = request.POST.get('action')

    if action == 'pay' and order.user == request.user and order.status == 'pending':
        order.status = 'paid'
        order.save()
        messages.success(request, '支付成功')
    elif action == 'complete' and order.service.provider == request.user and order.status == 'paid':
        order.status = 'completed'
        order.save()
        messages.success(request, '订单已完成')
    elif action == 'cancel' and order.user == request.user and order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, '订单已取消')

    return redirect('orders:order_detail', pk=pk)


@login_required
def review_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user, status='completed')

    if hasattr(order, 'review'):
        messages.info(request, '已评价过')
        return redirect('orders:order_detail', pk=order_id)

    if request.method == 'POST':
        rating = int(request.POST['rating'])
        Review.objects.create(
            order=order,
            user=request.user,
            service=order.service,
            rating=rating,
            content=request.POST['content'],
        )
        service = order.service
        reviews = service.reviews.all()
        service.avg_rating = round(sum(r.rating for r in reviews) / reviews.count(), 1)
        service.rating_count = reviews.count()
        service.save()
        messages.success(request, '评价成功')
        return redirect('orders:order_detail', pk=order_id)

    return render(request, 'orders/review_form.html', {'order': order})
