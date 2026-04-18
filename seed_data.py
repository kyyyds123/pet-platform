import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_platform.settings')
django.setup()

from accounts.models import User
from services.models import ServiceCategory, Service
from knowledge.models import KnowledgeCategory, KnowledgeArticle
from community.models import Post
from pets.models import Pet

print("Seeding database...")

# Create superuser
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')
    print("  ✓ Superuser: admin / admin123")

# Create demo users
owner, _ = User.objects.get_or_create(username='petlover', defaults={
    'role': 'owner', 'phone': '13800001111'
})
owner.set_password('123456')
owner.save()

provider, _ = User.objects.get_or_create(username='petshop', defaults={
    'role': 'provider', 'phone': '13800002222'
})
provider.set_password('123456')
provider.save()
print("  ✓ Demo users: petlover/123456 (主人), petshop/123456 (商家)")

# Service categories
categories_data = [
    ('宠物医疗', 'bi-hospital'),
    ('宠物美容', 'bi-scissors'),
    ('宠物寄养', 'bi-house-heart'),
    ('宠物训练', 'bi-lightning'),
    ('宠物用品', 'bi-bag'),
    ('宠物食品', 'bi-cup-straw'),
]
cats = []
for name, icon in categories_data:
    cat, _ = ServiceCategory.objects.get_or_create(name=name, defaults={'icon': icon})
    cats.append(cat)
print("  ✓ 6 个服务类别")

# Demo services
services_data = [
    (cats[0], '宠物体检套餐', '全面健康检查，包含血液检查、X光、B超等', 299, 120),
    (cats[0], '疫苗接种', '猫狗核心疫苗接种服务', 150, 30),
    (cats[1], '宠物洗澡美容', '专业洗护+造型修剪+指甲护理', 128, 90),
    (cats[1], '猫咪SPA护理', '深层清洁+护毛+按摩放松', 198, 60),
    (cats[2], '日托寄养', '白天看护，含遛狗和喂食', 80, 480),
    (cats[2], '长期寄养', '节假日安心出行，专业照料', 150, 1440),
    (cats[3], '幼犬基础训练', '社会化训练+基础服从训练', 500, 60),
    (cats[4], '宠物用品礼包', '精选宠物日常用品组合', 199, 0),
]
for cat, name, desc, price, duration in services_data:
    Service.objects.get_or_create(name=name, defaults={
        'provider': provider, 'category': cat, 'description': desc,
        'price': price, 'duration': duration,
    })
print("  ✓ 8 个示例服务")

# Knowledge categories & articles
k_cats_data = [
    ('疫苗防疫', 'bi-shield-check'),
    ('喂养常识', 'bi-cup-hot'),
    ('健康护理', 'bi-heart-pulse'),
    ('行为训练', 'bi-emoji-smile'),
    ('品种百科', 'bi-book'),
]
k_cats = []
for name, icon in k_cats_data:
    cat, _ = KnowledgeCategory.objects.get_or_create(name=name, defaults={'icon': icon})
    k_cats.append(cat)

articles_data = [
    (k_cats[0], '幼犬疫苗接种时间表', '幼犬在6-8周龄开始接种第一针疫苗...', True),
    (k_cats[0], '猫咪年度疫苗指南', '猫咪每年需要接种核心疫苗和加强针...', True),
    (k_cats[1], '狗狗每日喂食量参考', '根据狗狗体重和年龄，合理调整每日食量...', True),
    (k_cats[1], '猫咪不能吃的食物清单', '巧克力、葡萄、洋葱等食物对猫咪有毒...', True),
    (k_cats[2], '如何判断宠物是否生病', '观察食欲、精神、排便等日常表现...', False),
    (k_cats[3], '纠正狗狗乱叫的方法', '通过正向强化训练减少吠叫行为...', False),
    (k_cats[4], '热门犬种性格特点', '金毛温顺、边牧聪明、柴犬倔强...', False),
]
for cat, title, content, hot in articles_data:
    KnowledgeArticle.objects.get_or_create(title=title, defaults={
        'category': cat, 'content': content + '\n\n这是一篇关于' + title + '的详细知识文章。包含实用的养宠建议和专业知识。',
        'summary': content[:100], 'is_hot': hot, 'created_by': admin,
    })
print("  ✓ 7 篇知识文章")

# Demo posts
posts_data = [
    ('note', '我家金毛的成长日记', '从3个月养到现在1岁半，记录了满满的回忆...'),
    ('qa', '猫咪突然不吃东西怎么办？', '最近猫咪食欲下降，大家有什么建议吗？'),
    ('show', '晒晒我家的布偶猫', '颜值超高，给大家看看我家的小公主！'),
]
for ptype, title, content in posts_data:
    Post.objects.get_or_create(title=title, defaults={
        'author': owner, 'post_type': ptype, 'content': content, 'is_approved': True,
    })
print("  ✓ 3 条社区帖子")

# Demo pet
Pet.objects.get_or_create(name='旺财', defaults={
    'owner': owner, 'breed': '金毛', 'age': '2岁', 'gender': 'male',
    'description': '活泼好动的大金毛',
})
print("  ✓ 示例宠物档案")

print("\n✅ 种子数据完成！")
print("   管理员: admin / admin123")
print("   宠物主人: petlover / 123456")
print("   服务商家: petshop / 123456")
