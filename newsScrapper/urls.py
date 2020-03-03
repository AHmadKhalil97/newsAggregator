from django.urls import path
from newsScrapper import views

urlpatterns = [
    # path('', views.scrap_the_onion, name='scrapTheOnion'),
    path('', views.scrap_all_latest, name='scrap_all_latest'),
    path('politics', views.scrap_all_politics, name='scrap_all_politics'),
    path('business', views.scrap_all_business, name='scrap_all_business'),
    path('health', views.scrap_all_health, name='scrap_all_health'),
]
