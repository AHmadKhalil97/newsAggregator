from django.urls import path
from newsScrapper import views

urlpatterns = [
    # path('', views.scrap_the_onion, name='scrapTheOnion'),
    path('', views.scrap_all, name='scrapAll'),
]