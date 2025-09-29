from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from .models import Funcionario, Retirada
from .forms import FuncionarioForm
import io, json
import qrcode

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    msg = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        msg = 'Usuário ou senha inválidos.'
    return render(request, 'login.html', {'msg': msg})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    hoje = timezone.localdate()
    funcionarios = Funcionario.objects.all().order_by('nome')
    retiradas_hoje = set(Retirada.objects.filter(data=hoje).values_list('funcionario_id', flat=True))
    contexto = {
        'funcionarios': [{'obj': f, 'retirou': f.id in retiradas_hoje} for f in funcionarios],
        'hoje': hoje,
        'total': funcionarios.count(),
        'total_retiradas': len(retiradas_hoje),
    }
    return render(request, 'dashboard.html', contexto)

@login_required
def scanner(request):
    return render(request, 'scanner.html')

@login_required
def registrar_retirada(request):
    token = request.GET.get('code') or request.POST.get('code')
    if not token:
        return HttpResponseBadRequest('Código não informado.')
    try:
        func = Funcionario.objects.get(token=token)
    except Funcionario.DoesNotExist:
        return JsonResponse({'ok': False, 'mensagem': 'Funcionário não encontrado para este código.'}, status=404)

    hoje = timezone.localdate()
    try:
        ret, created = Retirada.objects.get_or_create(funcionario=func, data=hoje, defaults={})
        if not created:
            return JsonResponse({'ok': False, 'mensagem': 'Este funcionário já retirou a marmita hoje.'}, status=409)
    except IntegrityError:
        return JsonResponse({'ok': False, 'mensagem': 'Este funcionário já retirou a marmita hoje.'}, status=409)

    return JsonResponse({
        'ok': True,
        'mensagem': f'Retirada registrada para {func.nome} às {timezone.now().strftime("%H:%M:%S")}',
        'funcionario': {'id': func.id, 'nome': func.nome, 'matricula': func.matricula},
        'data': str(hoje),
    })

@login_required
def funcionario_list(request):
    funcionarios = Funcionario.objects.all().order_by('nome')
    return render(request, 'funcionarios/list.html', {'funcionarios': funcionarios})

@login_required
def funcionario_detail(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    return render(request, 'funcionarios/detail.html', {'func': func})

@login_required
def funcionario_create(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            func = form.save()
            return redirect('funcionario_detail', pk=func.pk)
    else:
        form = FuncionarioForm()
    return render(request, 'funcionarios/form.html', {'form': form, 'acao': 'Novo'})

@login_required
def funcionario_update(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=func)
        if form.is_valid():
            form.save()
            return redirect('funcionario_detail', pk=func.pk)
    else:
        form = FuncionarioForm(instance=func)
    return render(request, 'funcionarios/form.html', {'form': form, 'acao': 'Editar'})

@login_required
def funcionario_delete(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        func.delete()
        return redirect('funcionario_list')
    return render(request, 'funcionarios/confirm_delete.html', {'func': func})

@login_required
def funcionario_qrcode(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    # Gera QR Code on-the-fly com o token do funcionário
    img = qrcode.make(func.token)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')

@login_required
def relatorio_dia(request):
    data_str = request.GET.get('data')
    data = timezone.localdate()
    if data_str:
        try:
            data = timezone.datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            pass
    funcionarios = list(Funcionario.objects.all().order_by('nome'))
    retiradas = Retirada.objects.filter(data=data).select_related('funcionario')
    retiradas_ids = set(retiradas.values_list('funcionario_id', flat=True))

    if request.GET.get('export') == 'json':
        payload = {
            'data': str(data),
            'registros': [
                {
                    'funcionario_id': r.funcionario.id,
                    'nome': r.funcionario.nome,
                    'matricula': r.funcionario.matricula,
                    'hora': r.criado_em.astimezone(timezone.get_current_timezone()).strftime('%H:%M:%S')
                } for r in retiradas
            ]
        }
        return JsonResponse(payload, json_dumps_params={'ensure_ascii': False, 'indent': 2})

    contexto = {
        'data': data,
        'retiradas': retiradas,
        'faltantes': [f for f in funcionarios if f.id not in retiradas_ids],
    }
    return render(request, 'relatorios/dia.html', contexto)

@login_required
def relatorio_mes(request):
    try:
        ano = int(request.GET.get('ano', timezone.now().year))
        mes = int(request.GET.get('mes', timezone.now().month))
    except ValueError:
        ano, mes = timezone.now().year, timezone.now().month

    from calendar import monthrange
    inicio = timezone.datetime(ano, mes, 1, tzinfo=timezone.get_current_timezone())
    ultimo_dia = monthrange(ano, mes)[1]
    fim = timezone.datetime(ano, mes, ultimo_dia, 23, 59, 59, tzinfo=timezone.get_current_timezone())

    retiradas = Retirada.objects.filter(criado_em__range=(inicio, fim)).select_related('funcionario')

    if request.GET.get('export') == 'json':
        payload = {
            'ano': ano,
            'mes': mes,
            'registros': [
                {
                    'data': r.data.isoformat(),
                    'hora': r.criado_em.astimezone(timezone.get_current_timezone()).strftime('%H:%M:%S'),
                    'funcionario_id': r.funcionario.id,
                    'nome': r.funcionario.nome,
                    'matricula': r.funcionario.matricula,
                } for r in retiradas
            ]
        }
        return JsonResponse(payload, json_dumps_params={'ensure_ascii': False, 'indent': 2})

    # Resumo por funcionário (qtd de dias que retirou)
    from collections import Counter
    contagem = Counter([r.funcionario_id for r in retiradas])
    funcionarios = Funcionario.objects.all().order_by('nome')
    resumo = [ {'func': f, 'qtd': contagem.get(f.id, 0)} for f in funcionarios ]

    contexto = {'ano': ano, 'mes': mes, 'retiradas': retiradas, 'resumo': resumo}
    return render(request, 'relatorios/mes.html', contexto)