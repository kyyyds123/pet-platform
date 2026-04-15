from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'owner')
        phone = request.POST.get('phone', '')

        if password != password2:
            messages.error(request, '两次密码不一致')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=username, password=password,
            role=role, phone=phone
        )
        login(request, user)
        messages.success(request, '注册成功！')
        return redirect('index')

    return render(request, 'accounts/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        messages.error(request, '用户名或密码错误')

    return render(request, 'accounts/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('index')


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, '用户名不存在')
            return render(request, 'accounts/forgot_password.html')

        if new_password != new_password2:
            messages.error(request, '两次密码不一致')
            return render(request, 'accounts/forgot_password.html')

        user.set_password(new_password)
        user.save()
        messages.success(request, '密码重置成功，请使用新密码登录')
        return redirect('accounts:login')

    return render(request, 'accounts/forgot_password.html')


@login_required
def profile(request):
    if request.method == 'POST':
        request.user.phone = request.POST.get('phone', '')
        request.user.address = request.POST.get('address', '')
        request.user.bio = request.POST.get('bio', '')
        if request.FILES.get('avatar'):
            request.user.avatar = request.FILES['avatar']
        request.user.save()
        messages.success(request, '资料更新成功')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html')
