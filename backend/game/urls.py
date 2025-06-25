from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'game'

urlpatterns = [
    path('lobby/', views.lobby_view, name='lobby'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='game/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('game/<uuid:room_id>/', views.game_room, name='game_room'),
    path('delete_game/<uuid:room_id>/', views.delete_game, name='delete_game'),
    path('start_from_scenario/<int:scenario_id>/', views.start_from_scenario, name='start_from_scenario'),
]