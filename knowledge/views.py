from django.shortcuts import render, get_object_or_404
from .models import KnowledgeArticle, KnowledgeCategory


def article_list(request):
    articles = KnowledgeArticle.objects.all().select_related('category')
    categories = KnowledgeCategory.objects.all()

    category_id = request.GET.get('category')
    if category_id:
        articles = articles.filter(category_id=category_id)

    hot_articles = KnowledgeArticle.objects.filter(is_hot=True)[:5]

    return render(request, 'knowledge/article_list.html', {
        'articles': articles,
        'categories': categories,
        'hot_articles': hot_articles,
        'current_category': category_id,
    })


def article_detail(request, pk):
    article = get_object_or_404(KnowledgeArticle.objects.select_related('category'), pk=pk)
    article.view_count += 1
    article.save(update_fields=['view_count'])

    related = KnowledgeArticle.objects.filter(
        category=article.category
    ).exclude(pk=pk)[:5]

    return render(request, 'knowledge/article_detail.html', {
        'article': article,
        'related': related,
    })
