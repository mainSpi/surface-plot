from django.urls import path
from . import views

urlpatterns = [
    path('', views.cu, name='post'),
    path('show', views.bunda, name='show'),
]
