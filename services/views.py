from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Service, ServiceCategory


def service_list(request):
    services = Service.objects.filter(is_active=True).select_related('category', 'provider')
    categories = ServiceCategory.objects.all()

    # Filtering
    category_id = request.GET.get('category')
    keyword = request.GET.get('keyword', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_id:
        services = services.filter(category_id=category_id)
    if keyword:
        services = services.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
    if min_price:
        services = services.filter(price__gte=min_price)
    if max_price:
        services = services.filter(price__lte=max_price)

    context = {
        'services': services,
        'categories': categories,
        'current_category': category_id,
        'keyword': keyword,
    }
    return render(request, 'services/service_list.html', context)


def service_detail(request, pk):
    service = get_object_or_404(Service.objects.select_related('provider', 'category'), pk=pk)
    reviews = service.reviews.filter(is_approved=True).select_related('user')[:10]
    return render(request, 'services/service_detail.html', {
        'service': service,
        'reviews': reviews,
    })


@login_required
def service_create(request):
    if not request.user.is_provider:
        messages.error(request, '仅商家可以发布服务')
        return redirect('services:service_list')

    if request.method == 'POST':
        service = Service.objects.create(
            provider=request.user,
            category_id=request.POST['category'],
            name=request.POST['name'],
            description=request.POST['description'],
            price=request.POST['price'],
            duration=request.POST.get('duration', 60),
            address=request.POST.get('address', ''),
            image=request.FILES.get('image'),
        )
        messages.success(request, '服务发布成功')
        return redirect('services:service_detail', pk=service.pk)

    categories = ServiceCategory.objects.all()
    return render(request, 'services/service_form.html', {'categories': categories})


@login_required
def my_services(request):
    services = Service.objects.filter(provider=request.user)
    return render(request, 'services/my_services.html', {'services': services})
