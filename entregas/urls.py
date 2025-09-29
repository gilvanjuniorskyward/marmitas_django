from django.urls import path
from . import views

urlpatterns = [
    path('', views.funcionario_list, name='funcionario_list'),
    path('novo/', views.funcionario_create, name='funcionario_create'),
    path('<int:pk>/', views.funcionario_detail, name='funcionario_detail'),
    path('<int:pk>/editar/', views.funcionario_update, name='funcionario_update'),
    path('<int:pk>/excluir/', views.funcionario_delete, name='funcionario_delete'),
    path('<int:pk>/qrcode/', views.funcionario_qrcode, name='funcionario_qrcode'),
]