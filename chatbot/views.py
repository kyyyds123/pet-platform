import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import ChatMessage, ManualRequest
from .llm import ask_llm




def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def chatbot_page(request):
    session_key = _get_session_key(request)

    # 检查是否有人工咨询中，有的话统一用咨询的session_key查询
    active_manual = None
    if request.user.is_authenticated:
        active_manual = ManualRequest.objects.filter(
            user=request.user, status='active'
        ).first()

    if active_manual:
        # 人工模式：用咨询的session_key查询所有消息
        messages_qs = ChatMessage.objects.filter(session_key=active_manual.session_key)
    elif request.user.is_authenticated:
        messages_qs = ChatMessage.objects.filter(
            models.Q(session_key=session_key) | models.Q(user=request.user)
        )
    else:
        messages_qs = ChatMessage.objects.filter(session_key=session_key)

    return render(request, 'chatbot/chat.html', {
        'chat_messages': messages_qs.order_by('created_at')[:100],
        'active_manual': active_manual,
    })


def chatbot_reply(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    user_msg = request.POST.get('message', '').strip()
    if not user_msg:
        return JsonResponse({'reply': '请输入您的问题'})

    session_key = _get_session_key(request)

    # 检查是否有人工咨询请求正在进行
    active_request = None
    if request.user.is_authenticated:
        active_request = ManualRequest.objects.filter(
            user=request.user, status='active'
        ).first()
        if active_request:
            # 人工模式：用咨询的session_key保存，确保管理员能看到
            session_key = active_request.session_key

    # 保存用户消息
    user_message = ChatMessage.objects.create(
        session_key=session_key,
        user=request.user if request.user.is_authenticated else None,
        role='user',
        content=user_msg,
    )

    # 人工模式直接返回
    if active_request:
        return JsonResponse({'reply': '消息已发送', 'manual': True, 'user_msg_id': user_message.id})

    # 构建对话历史
    history_msgs = ChatMessage.objects.filter(
        session_key=session_key, role__in=['user', 'bot']
    ).order_by('created_at')
    history = [
        {'role': 'user' if m.role == 'user' else 'assistant', 'content': m.content}
        for m in history_msgs
    ]

    try:
        answer = ask_llm(user_msg, history)
    except Exception:
        answer = '抱歉，我暂时无法回复您的问题，请稍后再试或转人工客服。'

    bot_message = ChatMessage.objects.create(
        session_key=session_key,
        user=request.user if request.user.is_authenticated else None,
        role='bot', content=answer,
    )
    return JsonResponse({'reply': answer, 'user_msg_id': user_message.id, 'bot_msg_id': bot_message.id})


@login_required
def chatbot_poll(request):
    """AJAX轮询：获取新消息"""
    session_key = _get_session_key(request)
    # 人工模式下用咨询的session_key
    active_request = ManualRequest.objects.filter(
        user=request.user, status='active'
    ).first()
    if active_request:
        session_key = active_request.session_key

    last_id = int(request.GET.get('last_id', 0))
    msgs = ChatMessage.objects.filter(
        session_key=session_key,
        id__gt=last_id
    ).order_by('created_at')
    data = [{
        'id': m.id,
        'role': m.role,
        'content': m.content,
        'time': m.created_at.strftime('%H:%M'),
    } for m in msgs]
    return JsonResponse({'messages': data})


@login_required
def admin_chat_poll(request, session_key):
    """管理员AJAX轮询：获取指定会话新消息"""
    if not request.user.is_admin_role:
        return JsonResponse({'error': '无权访问'}, status=403)
    last_id = int(request.GET.get('last_id', 0))
    msgs = ChatMessage.objects.filter(
        session_key=session_key,
        id__gt=last_id
    ).order_by('created_at')
    data = [{
        'id': m.id,
        'role': m.role,
        'content': m.content,
        'time': m.created_at.strftime('%H:%M:%S'),
    } for m in msgs]
    return JsonResponse({'messages': data})


@login_required
def request_manual(request):
    """请求人工咨询"""
    if request.method == 'POST':
        existing = ManualRequest.objects.filter(
            user=request.user,
            status__in=['pending', 'active']
        ).first()
        if existing:
            messages.info(request, '您已有人工咨询请求')
        else:
            session_key = _get_session_key(request)
            ManualRequest.objects.create(user=request.user, session_key=session_key)
            messages.success(request, '已提交人工咨询请求，请等待客服接入')
    return redirect('chatbot:chat')


@login_required
def close_manual(request):
    """用户结束人工咨询"""
    if request.method == 'POST':
        from django.utils import timezone
        manual_req = ManualRequest.objects.filter(
            user=request.user, status__in=['pending', 'active']
        ).first()
        if manual_req:
            manual_req.status = 'closed'
            manual_req.closed_at = timezone.now()
            manual_req.save()
            messages.success(request, '已结束人工咨询')
    return redirect('chatbot:chat')


# ========== 管理员功能 ==========

@login_required
def admin_chat_list(request):
    """管理员：查看所有对话记录"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    sessions = ChatMessage.objects.values('session_key').distinct()
    session_data = []
    for s in sessions:
        sk = s['session_key']
        first_msg = ChatMessage.objects.filter(session_key=sk).order_by('created_at').first()
        last_msg = ChatMessage.objects.filter(session_key=sk).order_by('-created_at').first()
        count = ChatMessage.objects.filter(session_key=sk).count()
        session_data.append({
            'session_key': sk,
            'first_msg': first_msg,
            'last_msg': last_msg,
            'count': count,
            'user': first_msg.user if first_msg and first_msg.user else None,
        })

    return render(request, 'chatbot/admin_chat_list.html', {'sessions': session_data})


@login_required
def admin_chat_detail(request, session_key):
    """管理员：查看指定对话"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    msgs = ChatMessage.objects.filter(session_key=session_key).order_by('created_at')
    manual_req = ManualRequest.objects.filter(session_key=session_key).first()
    return render(request, 'chatbot/admin_chat_detail.html', {
        'messages': msgs,
        'session_key': session_key,
        'manual_req': manual_req,
    })


@login_required
def admin_manual_list(request):
    """管理员：人工咨询请求列表"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    requests_qs = ManualRequest.objects.all().select_related('user')
    return render(request, 'chatbot/admin_manual_list.html', {'requests': requests_qs})


@login_required
def admin_manual_respond(request, pk):
    """管理员：接入人工咨询"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    manual_req = get_object_or_404(ManualRequest, pk=pk)
    if request.method == 'POST':
        manual_req.status = 'active'
        manual_req.save()
        messages.success(request, f'已接入 {manual_req.user.username} 的咨询')
    return redirect('chatbot:admin_manual')


@login_required
def admin_manual_close(request, pk):
    """管理员：结束人工咨询"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    manual_req = get_object_or_404(ManualRequest, pk=pk)
    if request.method == 'POST':
        from django.utils import timezone
        manual_req.status = 'closed'
        manual_req.closed_at = timezone.now()
        manual_req.save()
        messages.success(request, '咨询已结束')
    return redirect('chatbot:admin_manual')


@login_required
def admin_send_message(request, pk):
    """管理员：在人工咨询中发送消息给用户"""
    if not request.user.is_admin_role:
        return JsonResponse({'error': '无权操作'}, status=403)

    manual_req = get_object_or_404(ManualRequest, pk=pk, status='active')
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            ChatMessage.objects.create(
                session_key=manual_req.session_key,
                user=manual_req.user,
                role='agent',
                content=content,
            )
            return JsonResponse({'ok': True})
    return JsonResponse({'error': '无效请求'}, status=400)
