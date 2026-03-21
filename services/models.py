from django.db import models
from django.conf import settings


class ServiceCategory(models.Model):
    """服务类别"""
    name = models.CharField('类别名称', max_length=50)
    icon = models.CharField('图标', max_length=50, default='bi-heart')
    description = models.TextField('描述', blank=True)
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '服务类别'
        verbose_name_plural = '服务类别'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class Service(models.Model):
    """服务项目"""
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='services', verbose_name='商家')
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE,
                                 related_name='services', verbose_name='类别')
    name = models.CharField('服务名称', max_length=100)
    description = models.TextField('服务描述')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    duration = models.IntegerField('服务时长(分钟)', default=60)
    image = models.ImageField('封面图片', upload_to='services/', blank=True)
    address = models.CharField('服务地址', max_length=200, blank=True)
    longitude = models.FloatField('经度', null=True, blank=True)
    latitude = models.FloatField('纬度', null=True, blank=True)
    is_active = models.BooleanField('是否上架', default=True)
    avg_rating = models.FloatField('平均评分', default=0)
    rating_count = models.IntegerField('评价数量', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '服务项目'
        verbose_name_plural = '服务项目'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
