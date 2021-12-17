from django.urls import path
from . import views

urlpatterns = [
    path('', views.post, name='post'),
    path('show', views.show, name='show'),
]
