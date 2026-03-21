from django.db import models
from django.conf import settings


class Post(models.Model):
    """社区帖子"""
    POST_TYPES = (
        ('note', '养宠笔记'),
        ('qa', '问答咨询'),
        ('show', '宠物展示'),
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='作者')
    post_type = models.CharField('类型', max_length=10, choices=POST_TYPES)
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    image = models.ImageField('图片', upload_to='posts/', blank=True)
    likes_count = models.IntegerField('点赞数', default=0)
    comments_count = models.IntegerField('评论数', default=0)
    is_pinned = models.BooleanField('置顶', default=False)
    created_at = models.DateTimeField('发布时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '社区帖子'
        verbose_name_plural = '社区帖子'
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    """评论"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='帖子')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='comments', verbose_name='作者')
    content = models.TextField('内容')
    created_at = models.DateTimeField('评论时间', auto_now_add=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.content[:30]}'


class Like(models.Model):
    """点赞"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class LostPet(models.Model):
    """走失/寻回宠物"""
    STATUS_CHOICES = (
        ('lost', '走失中'),
        ('found', '已找到'),
        ('adopted', '已领养'),
        ('expired', '已失效'),
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='lost_pets', verbose_name='发布者')
    pet_name = models.CharField('宠物名', max_length=50)
    pet_breed = models.CharField('品种', max_length=50, blank=True)
    pet_description = models.TextField('特征描述')
    location = models.CharField('走失地点', max_length=200)
    contact = models.CharField('联系方式', max_length=100)
    image = models.ImageField('宠物照片', upload_to='lost/', blank=True)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='lost')
    created_at = models.DateTimeField('发布时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '走失宠物'
        verbose_name_plural = '走失宠物'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.pet_name} ({self.get_status_display()})'


class SavedPost(models.Model):
    """帖子收藏"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saves')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='saved_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = '帖子收藏'
        verbose_name_plural = '帖子收藏'


class SavedLost(models.Model):
    """走失信息收藏"""
    lost_pet = models.ForeignKey(LostPet, on_delete=models.CASCADE, related_name='saves')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='saved_lost')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lost_pet', 'user')
        verbose_name = '走失信息收藏'
        verbose_name_plural = '走失信息收藏'
