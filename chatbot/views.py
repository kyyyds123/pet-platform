from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST


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


def chatbot_page(request):
    return render(request, 'chatbot/chat.html')


@require_POST
def chatbot_reply(request):
    user_msg = request.POST.get('message', '').strip()
    if not user_msg:
        return JsonResponse({'reply': '请输入您的问题'})

    for rule in FAQ_RULES:
        for kw in rule['keywords']:
            if kw in user_msg:
                return JsonResponse({'reply': rule['answer']})

    return JsonResponse({
        'reply': '抱歉，我暂时无法理解您的问题。您可以尝试换个问法，或联系人工客服获取帮助。常见问题包括：预约、支付、退款、注册、评价、宠物档案、走失寻回、疫苗提醒等。'
    })
