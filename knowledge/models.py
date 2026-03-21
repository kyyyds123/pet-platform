from django.db import models
from django.conf import settings


class KnowledgeCategory(models.Model):
    """知识分类"""
    name = models.CharField('分类名', max_length=50)
    icon = models.CharField('图标', max_length=50, default='bi-book')
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '知识分类'
        verbose_name_plural = '知识分类'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class KnowledgeArticle(models.Model):
    """知识文章"""
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.CASCADE,
                                 related_name='articles', verbose_name='分类')
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    summary = models.TextField('摘要', max_length=500, blank=True)
    image = models.ImageField('封面', upload_to='knowledge/', blank=True)
    view_count = models.IntegerField('浏览数', default=0)
    is_hot = models.BooleanField('热门', default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='knowledge_articles', verbose_name='作者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '知识文章'
        verbose_name_plural = '知识文章'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class KnowledgeLike(models.Model):
    """知识文章点赞"""
    article = models.ForeignKey(KnowledgeArticle, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')
        verbose_name = '文章点赞'
        verbose_name_plural = '文章点赞'


class KnowledgeFavorite(models.Model):
    """知识文章收藏"""
    article = models.ForeignKey(KnowledgeArticle, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')
        verbose_name = '文章收藏'
        verbose_name_plural = '文章收藏'
