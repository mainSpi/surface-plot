from django.urls import path
from . import views

urlpatterns = [
    path('', views.cu, name='cu'),
    path('show', views.bunda, name='show'),
]
