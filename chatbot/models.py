from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    """客服对话记录"""
    ROLE_CHOICES = (
        ('user', '用户'),
        ('bot', '机器人'),
        ('agent', '人工客服'),
    )
    session_key = models.CharField('会话标识', max_length=64, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             null=True, blank=True, related_name='chat_messages', verbose_name='用户')
    role = models.CharField('角色', max_length=10, choices=ROLE_CHOICES)
    content = models.TextField('内容')
    created_at = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        verbose_name = '对话记录'
        verbose_name_plural = '对话记录'
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.role}] {self.content[:30]}'


class ManualRequest(models.Model):
    """人工咨询请求"""
    STATUS_CHOICES = (
        ('pending', '等待接入'),
        ('active', '咨询中'),
        ('closed', '已结束'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='manual_requests', verbose_name='用户')
    session_key = models.CharField('会话标识', max_length=64)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('发起时间', auto_now_add=True)
    closed_at = models.DateTimeField('结束时间', null=True, blank=True)

    class Meta:
        verbose_name = '人工咨询'
        verbose_name_plural = '人工咨询'
        ordering = ['-created_at']
