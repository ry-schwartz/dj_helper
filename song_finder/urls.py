from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('song_search/', views.song_search, name='song_search'),
    path('results/', views.results, name = 'results')
]