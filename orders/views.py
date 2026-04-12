import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, Review, OrderMessage
from services.models import Service
from pets.models import Pet, VaccineRecord


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
    order = get_object_or_404(Order.objects.select_related('service__category', 'user', 'service__provider'), pk=pk)
    if order.user != request.user and order.service.provider != request.user:
        messages.error(request, '无权查看此订单')
        return redirect('orders:order_list')

    # 检查是否是宠物医疗类商家，且订单已完成
    is_medical_provider = (
        request.user.is_provider
        and order.service.provider == request.user
        and order.service.category.name == '宠物医疗'
        and order.status == 'completed'
    )

    # 查找客户的宠物（用于添加健康记录）
    customer_pets = []
    if is_medical_provider:
        customer_pets = Pet.objects.filter(owner=order.user, name=order.pet_name)

    # 订单沟通消息
    order_messages = order.messages.select_related('sender').all()
    can_chat = (
        order.user == request.user or order.service.provider == request.user
    ) and order.status not in ('cancelled',)

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'is_medical_provider': is_medical_provider,
        'customer_pets': customer_pets,
        'order_messages': order_messages,
        'can_chat': can_chat,
    })


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


@login_required
def order_add_record(request, order_id):
    """宠物医疗商家为客户的宠物添加健康记录"""
    order = get_object_or_404(
        Order.objects.select_related('service__category'),
        pk=order_id,
        service__provider=request.user,
        service__category__name='宠物医疗',
        status='completed',
    )

    # 找到客户的对应宠物
    pet = get_object_or_404(Pet, owner=order.user, name=order.pet_name)

    if request.method == 'POST':
        VaccineRecord.objects.create(
            pet=pet,
            record_type=request.POST['record_type'],
            name=request.POST['name'],
            date=request.POST['date'],
            next_date=request.POST.get('next_date') or None,
            hospital=request.POST.get('hospital', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, f'已为 {pet.name} 添加健康记录')
        return redirect('orders:order_detail', pk=order.pk)

    return render(request, 'orders/add_record.html', {'order': order, 'pet': pet})


# ========== 管理员评价管理 ==========

@login_required
def order_send_message(request, pk):
    """发送订单沟通消息"""
    order = get_object_or_404(Order.objects.select_related('service__provider'), pk=pk)

    # 只有订单的宠物主人和服务商可以发消息
    if order.user != request.user and order.service.provider != request.user:
        messages.error(request, '无权操作')
        return redirect('orders:order_list')

    if order.status == 'cancelled':
        messages.error(request, '订单已取消，无法发送消息')
        return redirect('orders:order_detail', pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            OrderMessage.objects.create(
                order=order,
                sender=request.user,
                content=content,
            )
            messages.success(request, '消息已发送')
    return redirect('orders:order_detail', pk=pk)


@login_required
def admin_review_list(request):
    """管理员：评价列表"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    reviews = Review.objects.all().select_related('user', 'service', 'order')
    return render(request, 'orders/admin_review_list.html', {'reviews': reviews})


@login_required
def admin_review_approve(request, pk):
    """管理员：审核通过评价"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.is_approved = True
        review.save()
        messages.success(request, '评价已审核通过')
    return redirect('orders:admin_reviews')


@login_required
def admin_review_reject(request, pk):
    """管理员：屏蔽评价"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.is_approved = False
        review.save()
        messages.success(request, '评价已屏蔽')
    return redirect('orders:admin_reviews')
