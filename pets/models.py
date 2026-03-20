from django.db import models
from django.conf import settings


class Pet(models.Model):
    """宠物档案"""
    GENDER_CHOICES = (
        ('male', '公'),
        ('female', '母'),
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='pets', verbose_name='主人')
    name = models.CharField('宠物名', max_length=50)
    breed = models.CharField('品种', max_length=50)
    age = models.CharField('年龄', max_length=20, blank=True)
    gender = models.CharField('性别', max_length=6, choices=GENDER_CHOICES, blank=True)
    photo = models.ImageField('照片', upload_to='pets/', blank=True)
    description = models.TextField('描述', blank=True)
    birthday = models.DateField('生日', null=True, blank=True)
    created_at = models.DateTimeField('建档时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '宠物档案'
        verbose_name_plural = '宠物档案'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.breed})'


class VaccineRecord(models.Model):
    """疫苗/体检记录"""
    RECORD_TYPES = (
        ('vaccine', '疫苗'),
        ('checkup', '体检'),
    )
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE,
                            related_name='records', verbose_name='宠物')
    record_type = models.CharField('类型', max_length=10, choices=RECORD_TYPES)
    name = models.CharField('名称', max_length=100)
    date = models.DateField('日期')
    next_date = models.DateField('下次日期', null=True, blank=True)
    hospital = models.CharField('医院', max_length=200, blank=True)
    notes = models.TextField('备注', blank=True)
    is_reminded = models.BooleanField('已提醒', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '健康记录'
        verbose_name_plural = '健康记录'
        ordering = ['-date']

    def __str__(self):
        return f'{self.pet.name} - {self.name}'
