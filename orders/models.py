from django.db import models
from django.conf import settings


class Order(models.Model):
    """预约订单"""
    STATUS_CHOICES = (
        ('pending', '待支付'),
        ('paid', '待执行'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    order_no = models.CharField('订单编号', max_length=32, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='orders', verbose_name='用户')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE,
                                related_name='orders', verbose_name='服务')
    pet_name = models.CharField('宠物名', max_length=50)
    appointment_date = models.DateField('预约日期')
    appointment_time = models.TimeField('预约时间')
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField('总价', max_digits=10, decimal_places=2)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '预约订单'
        verbose_name_plural = '预约订单'
        ordering = ['-created_at']

    def __str__(self):
        return f'订单 {self.order_no}'


class Review(models.Model):
    """服务评价"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE,
                                 related_name='review', verbose_name='订单')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='reviews', verbose_name='用户')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE,
                                related_name='reviews', verbose_name='服务')
    rating = models.IntegerField('评分', choices=[(i, f'{i}星') for i in range(1, 6)])
    content = models.TextField('评价内容')
    is_approved = models.BooleanField('已审核', default=False)
    created_at = models.DateTimeField('评价时间', auto_now_add=True)

    class Meta:
        verbose_name = '服务评价'
        verbose_name_plural = '服务评价'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.rating}星'


class OrderMessage(models.Model):
    """订单沟通消息（宠物主人 ↔ 服务商）"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='messages', verbose_name='订单')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='order_messages', verbose_name='发送者')
    content = models.TextField('消息内容')
    created_at = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        verbose_name = '订单消息'
        verbose_name_plural = '订单消息'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.content[:30]}'
