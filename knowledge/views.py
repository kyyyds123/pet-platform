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
