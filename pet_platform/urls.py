from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


def index(request):
    from services.models import ServiceCategory, Service
    from knowledge.models import KnowledgeArticle
    from community.models import LostPet
    from pets.models import VaccineRecord, Pet
    from datetime import date, timedelta

    categories = ServiceCategory.objects.all()
    hot_services = Service.objects.filter(is_active=True).order_by('-avg_rating')[:6]
    hot_articles = KnowledgeArticle.objects.filter(is_hot=True)[:4]
    lost_recent = LostPet.objects.filter(status='lost')[:3]

    reminders = []
    if request.user.is_authenticated:
        today = date.today()
        pets = Pet.objects.filter(owner=request.user)
        reminders = VaccineRecord.objects.filter(
            pet__in=pets,
            next_date__isnull=False,
            next_date__lte=today + timedelta(days=30),
            is_reminded=False,
        ).select_related('pet')[:5]

    return render(request, 'index.html', {
        'categories': categories,
        'hot_services': hot_services,
        'hot_articles': hot_articles,
        'lost_recent': lost_recent,
        'reminders': reminders,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include('accounts.urls')),
    path('services/', include('services.urls')),
    path('orders/', include('orders.urls')),
    path('community/', include('community.urls')),
    path('pets/', include('pets.urls')),
    path('knowledge/', include('knowledge.urls')),
    path('chatbot/', include('chatbot.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
