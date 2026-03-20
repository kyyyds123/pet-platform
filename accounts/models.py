from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """多角色用户模型"""
    ROLE_CHOICES = (
        ('owner', '宠物主人'),
        ('provider', '服务商家'),
        ('admin', '系统管理员'),
    )
    role = models.CharField('角色', max_length=10, choices=ROLE_CHOICES, default='owner')
    phone = models.CharField('手机号', max_length=11, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True)
    address = models.CharField('地址', max_length=200, blank=True)
    bio = models.TextField('个人简介', max_length=500, blank=True)
    created_at = models.DateTimeField('注册时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_owner(self):
        return self.role == 'owner'

    @property
    def is_provider(self):
        return self.role == 'provider'

    @property
    def is_admin_role(self):
        return self.role == 'admin'
