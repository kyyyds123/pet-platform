from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import KnowledgeArticle, KnowledgeCategory, KnowledgeLike, KnowledgeFavorite


def article_list(request):
    articles = KnowledgeArticle.objects.all().select_related('category')
    categories = KnowledgeCategory.objects.all()

    category_id = request.GET.get('category')
    keyword = request.GET.get('keyword', '')

    if category_id:
        articles = articles.filter(category_id=category_id)
    if keyword:
        articles = articles.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        )

    hot_articles = KnowledgeArticle.objects.filter(is_hot=True)[:5]

    return render(request, 'knowledge/article_list.html', {
        'articles': articles,
        'categories': categories,
        'hot_articles': hot_articles,
        'current_category': category_id,
        'keyword': keyword,
    })


def article_detail(request, pk):
    article = get_object_or_404(KnowledgeArticle.objects.select_related('category'), pk=pk)
    article.view_count += 1
    article.save(update_fields=['view_count'])

    related = KnowledgeArticle.objects.filter(
        category=article.category
    ).exclude(pk=pk)[:5]

    user_liked = False
    user_favorited = False
    if request.user.is_authenticated:
        user_liked = KnowledgeLike.objects.filter(article=article, user=request.user).exists()
        user_favorited = KnowledgeFavorite.objects.filter(article=article, user=request.user).exists()

    return render(request, 'knowledge/article_detail.html', {
        'article': article,
        'related': related,
        'user_liked': user_liked,
        'user_favorited': user_favorited,
    })


@login_required
def article_like(request, pk):
    article = get_object_or_404(KnowledgeArticle, pk=pk)
    like, created = KnowledgeLike.objects.get_or_create(article=article, user=request.user)
    if not created:
        like.delete()
    count = KnowledgeLike.objects.filter(article=article).count()
    return JsonResponse({'liked': created, 'count': count})


@login_required
def article_favorite(request, pk):
    article = get_object_or_404(KnowledgeArticle, pk=pk)
    fav, created = KnowledgeFavorite.objects.get_or_create(article=article, user=request.user)
    if not created:
        fav.delete()
        messages.success(request, '已取消收藏')
    else:
        messages.success(request, '已收藏')
    return redirect('knowledge:article_detail', pk=pk)


# ========== 管理员文章管理 ==========

@login_required
def admin_article_list(request):
    """管理员：文章管理列表"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    articles = KnowledgeArticle.objects.all().select_related('category', 'created_by')
    category_id = request.GET.get('category')
    keyword = request.GET.get('keyword', '')

    if category_id:
        articles = articles.filter(category_id=category_id)
    if keyword:
        articles = articles.filter(Q(title__icontains=keyword))

    categories = KnowledgeCategory.objects.all()
    return render(request, 'knowledge/admin_article_list.html', {
        'articles': articles,
        'categories': categories,
        'current_category': category_id,
        'keyword': keyword,
    })


@login_required
def admin_article_create(request):
    """管理员：创建文章"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    if request.method == 'POST':
        article = KnowledgeArticle.objects.create(
            category_id=request.POST['category'],
            title=request.POST['title'],
            content=request.POST['content'],
            summary=request.POST.get('summary', ''),
            is_hot=request.POST.get('is_hot') == 'on',
            image=request.FILES.get('image'),
            created_by=request.user,
        )
        messages.success(request, f'文章「{article.title}」创建成功')
        return redirect('knowledge:admin_articles')

    categories = KnowledgeCategory.objects.all()
    return render(request, 'knowledge/admin_article_form.html', {
        'categories': categories,
    })


@login_required
def admin_article_edit(request, pk):
    """管理员：编辑文章"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    article = get_object_or_404(KnowledgeArticle, pk=pk)

    if request.method == 'POST':
        article.category_id = request.POST['category']
        article.title = request.POST['title']
        article.content = request.POST['content']
        article.summary = request.POST.get('summary', '')
        article.is_hot = request.POST.get('is_hot') == 'on'
        if request.FILES.get('image'):
            article.image = request.FILES['image']
        article.save()
        messages.success(request, f'文章「{article.title}」已更新')
        return redirect('knowledge:admin_articles')

    categories = KnowledgeCategory.objects.all()
    return render(request, 'knowledge/admin_article_form.html', {
        'article': article,
        'categories': categories,
    })


@login_required
def admin_article_delete(request, pk):
    """管理员：删除文章"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    article = get_object_or_404(KnowledgeArticle, pk=pk)
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'文章「{title}」已删除')
    return redirect('knowledge:admin_articles')
