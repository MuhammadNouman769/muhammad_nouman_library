from django.urls import path
from . import views

app_name = 'audio'

urlpatterns = [
    path('', views.audiobook_list, name='list'),
    path('<slug:slug>/player-data/', views.player_data, name='player_data'),
]
