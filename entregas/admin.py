from django.contrib import admin
from .models import Funcionario, Retirada

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'matricula', 'token')
    search_fields = ('nome', 'matricula', 'token')

@admin.register(Retirada)
class RetiradaAdmin(admin.ModelAdmin):
    list_display = ('id', 'funcionario', 'data', 'criado_em')
    list_filter = ('data',)
    search_fields = ('funcionario__nome', 'funcionario__matricula')