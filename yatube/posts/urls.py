from django.urls import path
from . import views
app_name = 'posts'
urlpatterns = [
    path('', views.index, name='last_upds'),
    path('group_list/', views.group_list),
    path('group/<slug:slug>/', views.group_posts),
]
