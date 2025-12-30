from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/buy/', views.buy_ticket, name='buy_ticket'),
    path('event/<int:event_id>/create_discount/', views.create_discount, name='create_discount'),
    path('signup/', views.signup, name='signup'),
]
