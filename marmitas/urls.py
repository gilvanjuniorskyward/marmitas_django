from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from entregas import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', v.login_view, name='login'),
    path('logout/', v.logout_view, name='logout'),
    path('', v.dashboard, name='dashboard'),
    path('scanner/', v.scanner, name='scanner'),
    path('registrar/', v.registrar_retirada, name='registrar_retirada'),
    path('funcionarios/', include('entregas.urls')),
    path('relatorios/dia', v.relatorio_dia, name='relatorio_dia'),
    path('relatorios/mes', v.relatorio_mes, name='relatorio_mes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)