from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import Pet, VaccineRecord


@login_required
def pet_list(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'pets/pet_list.html', {'pets': pets})


@login_required
def pet_create(request):
    if request.method == 'POST':
        pet = Pet.objects.create(
            owner=request.user,
            name=request.POST['name'],
            breed=request.POST['breed'],
            age=request.POST.get('age', ''),
            gender=request.POST.get('gender', ''),
            birthday=request.POST.get('birthday') or None,
            description=request.POST.get('description', ''),
            photo=request.FILES.get('photo'),
        )
        messages.success(request, '宠物档案创建成功')
        return redirect('pets:pet_detail', pk=pet.pk)
    return render(request, 'pets/pet_form.html')


@login_required
def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    records = pet.records.all()
    return render(request, 'pets/pet_detail.html', {'pet': pet, 'records': records})


@login_required
def pet_edit(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        pet.name = request.POST['name']
        pet.breed = request.POST['breed']
        pet.age = request.POST.get('age', '')
        pet.gender = request.POST.get('gender', '')
        pet.birthday = request.POST.get('birthday') or None
        pet.description = request.POST.get('description', '')
        if request.FILES.get('photo'):
            pet.photo = request.FILES['photo']
        pet.save()
        messages.success(request, '更新成功')
        return redirect('pets:pet_detail', pk=pet.pk)
    return render(request, 'pets/pet_form.html', {'pet': pet})


@login_required
def record_create(request, pet_id):
    pet = get_object_or_404(Pet, pk=pet_id, owner=request.user)
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
        messages.success(request, '记录添加成功')
        return redirect('pets:pet_detail', pk=pet.pk)
    return render(request, 'pets/record_form.html', {'pet': pet})


@login_required
def reminders(request):
    """疫苗/体检提醒"""
    today = date.today()
    upcoming = today + timedelta(days=30)
    pets = Pet.objects.filter(owner=request.user)
    reminders = VaccineRecord.objects.filter(
        pet__in=pets,
        next_date__isnull=False,
        next_date__lte=upcoming,
        is_reminded=False,
    ).select_related('pet')

    return render(request, 'pets/reminders.html', {
        'reminders': reminders,
        'today': today,
    })


@login_required
def mark_reminded(request, pk):
    record = get_object_or_404(VaccineRecord, pk=pk, pet__owner=request.user)
    record.is_reminded = True
    record.save()
    messages.success(request, '已标记完成')
    return redirect('pets:reminders')
