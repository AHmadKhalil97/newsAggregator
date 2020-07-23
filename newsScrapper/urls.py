from django.urls import path
from newsScrapper import views

urlpatterns = [
    # path('', views.scrap_the_onion, name='scrapTheOnion'),
    path('', views.get_all, name='home'),
    path('category/<str:category>', views.get_all, name='get_all'),
    path('search', views.search, name='search'),
    path('sync_now', views.sync_now, name='sync_now'),
    path('api', views.NewsAggregatorApi.as_view(), name='api'),
    # path('<str:category>', views.get_all, name='get_all_politics'),
    # path('<str:category>', views.get_all, name='get_all_business'),
    # path('<str:category>', views.get_all, name='get_all_health'),
]
