import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import ChatMessage, ManualRequest


FAQ_RULES = [
    {
        'keywords': ['预约', '预约服务', '怎么预约', '如何预约'],
        'answer': '预约流程：1. 浏览服务列表选择服务 2. 点击"立即预约" 3. 填写宠物信息和预约时间 4. 确认提交。您也可以在"我的订单"中查看预约状态。'
    },
    {
        'keywords': ['支付', '付款', '怎么付款', '费用'],
        'answer': '目前支持在线支付。创建预约后，在订单详情页面点击"立即支付"即可完成付款。'
    },
    {
        'keywords': ['退款', '取消', '取消订单'],
        'answer': '待支付状态的订单可以取消。已完成的服务如需退款，请联系商家协商处理。'
    },
    {
        'keywords': ['注册', '怎么注册', '注册账号'],
        'answer': '点击页面右上角"注册"按钮，填写用户名、密码，选择身份（宠物主人/服务商家），即可完成注册。'
    },
    {
        'keywords': ['评价', '怎么评价', '评分'],
        'answer': '订单完成后，进入订单详情页，点击"去评价"按钮，选择评分并填写评价内容即可。'
    },
    {
        'keywords': ['宠物档案', '添加宠物', '宠物信息'],
        'answer': '登录后进入"我的宠物"，点击"添加宠物"即可创建宠物档案，支持录入品种、年龄、照片等信息。'
    },
    {
        'keywords': ['走失', '寻回', '丢失宠物', '找宠物'],
        'answer': '在社区板块中可以发布走失/寻回信息，填写宠物特征、走失地点和联系方式，帮助找回爱宠。'
    },
    {
        'keywords': ['疫苗', '体检', '提醒'],
        'answer': '在宠物档案中添加疫苗或体检记录，设置下次日期后，系统会在到期前自动提醒您。'
    },
    {
        'keywords': ['服务', '有什么服务', '服务类型'],
        'answer': '平台提供宠物医疗、美容、寄养、训练等多种服务。您可以在服务列表页按类别筛选，也可以通过搜索功能快速找到所需服务。'
    },
    {
        'keywords': ['你好', '在吗', 'hello', 'hi'],
        'answer': '您好！我是宠物平台智能客服，很高兴为您服务。请问有什么可以帮助您的？'
    },
    {
        'keywords': ['谢谢', '感谢', 'thanks'],
        'answer': '不客气！如果还有其他问题，随时可以问我哦~'
    },
]


def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def chatbot_page(request):
    session_key = _get_session_key(request)
    messages_qs = ChatMessage.objects.filter(session_key=session_key)
    if request.user.is_authenticated:
        messages_qs = ChatMessage.objects.filter(
            models.Q(session_key=session_key) | models.Q(user=request.user)
        )
    # 检查是否有人工咨询中
    active_manual = None
    if request.user.is_authenticated:
        active_manual = ManualRequest.objects.filter(
            user=request.user, status='active'
        ).first()
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

    # 保存用户消息
    ChatMessage.objects.create(
        session_key=session_key,
        user=request.user if request.user.is_authenticated else None,
        role='user',
        content=user_msg,
    )

    # 检查是否有人工咨询请求正在进行
    if request.user.is_authenticated:
        active_request = ManualRequest.objects.filter(
            user=request.user, status='active'
        ).first()
        if active_request:
            reply = '您正在人工咨询中，消息已发送给客服，请等待回复。'
            return JsonResponse({'reply': reply, 'manual': True})

    # FAQ 匹配
    for rule in FAQ_RULES:
        for kw in rule['keywords']:
            if kw in user_msg:
                ChatMessage.objects.create(
                    session_key=session_key,
                    user=request.user if request.user.is_authenticated else None,
                    role='bot', content=rule['answer'],
                )
                return JsonResponse({'reply': rule['answer']})

    reply = '抱歉，我暂时无法理解您的问题。您可以点击下方"转人工客服"获取帮助，或尝试换个问法。'
    ChatMessage.objects.create(
        session_key=session_key,
        user=request.user if request.user.is_authenticated else None,
        role='bot', content=reply,
    )
    return JsonResponse({'reply': reply})


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
            'user': first_msg.user if first_msg else None,
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
        messages.error(request, '仅管理员可操作')
        return redirect('index')

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
            messages.success(request, '消息已发送')
    return redirect('chatbot:admin_chat_detail', session_key=manual_req.session_key)
