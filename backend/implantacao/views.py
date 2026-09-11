from __future__ import annotations

from datetime import datetime

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone

from implantacao.models import (
    EtapaImplantacao,
    Implantacao,
    ImplantacaoModulo,
    StatusImplantacao,
    TarefaImplantacao,
    Treinamento,
)
from implantacao.services.implantacao_service import ImplantacaoService
from implantacao.services.modulo_service import ModuloService
from implantacao.services.workflow_service import WorkflowService
from implantacao.templates.etapas import ETAPAS
from implantacao.templates.implantacao import TEMPLATES

ETAPAS_PADRAO_NOMES = [e['nome'] for e in sorted(ETAPAS.values(), key=lambda x: x['ordem'])]

IMPLANTADORES_SUGESTAO = [
    'Analista Implantação 1',
    'Analista Implantação 2',
    'Consultor Sênior',
    'Tech Lead Implantação',
    'Gerente de Operações',
]


def _montar_pipeline_padrao(implantacao):
    pipeline = {}
    etapas_qs = list(
        EtapaImplantacao.objects.filter(implantacao=implantacao)
        .prefetch_related('tarefas')
        .order_by('ordem')
    )
    etapas_map = {e.nome: e for e in etapas_qs}

    for nome in ETAPAS_PADRAO_NOMES:
        etapa = etapas_map.get(nome)
        if etapa and etapa.status == 'concluida':
            concluida, andamento = True, False
        elif etapa and etapa.status == 'em_andamento':
            concluida, andamento = False, True
        elif etapa and etapa.status == 'bloqueada':
            concluida, andamento = False, False
        else:
            concluida, andamento = False, False

        total_tarefas = etapa.tarefas.count() if etapa else 0
        concluidas_tarefas = etapa.tarefas.filter(concluida=True).count() if etapa else 0
        if etapa and etapa.status in ('concluida', 'em_andamento'):
            texto = f'{concluidas_tarefas}/{total_tarefas} tarefas'
        else:
            texto = 'Aguardando etapas anteriores'
        pipeline[nome] = {
            'concluida': concluida,
            'andamento': andamento,
            'texto': texto,
        }
    return pipeline


def _calcular_progresso_dados(implantacao, etapas_qs_list):
    etapas = sorted(etapas_qs_list or [], key=lambda e: (e.ordem, e.pk))
    total_etapas = len(etapas)
    etapas_concluidas = sum(1 for e in etapas if e.status == 'concluida')

    total_tarefas = sum(e.tarefas.count() for e in etapas)
    tarefas_concluidas = sum(
        sum(1 for t in e.tarefas.all() if t.concluida) for e in etapas
    )

    etapa_atual = 'A definir'
    for e in etapas:
        if e.status != 'concluida':
            etapa_atual = e.nome
            break

    pct_etapas = (etapas_concluidas / total_etapas) * 60 if total_etapas else 0
    pct_tarefas = (tarefas_concluidas / total_tarefas) * 40 if total_tarefas else 0
    percentual = round(pct_etapas + pct_tarefas)

    if implantacao.status == StatusImplantacao.FINALIZADO:
        percentual = 100
        etapa_atual = 'Finalizada'
    elif implantacao.status == StatusImplantacao.NAO_INICIADO and total_etapas == 0:
        percentual = 0
        etapa_atual = 'Não iniciada'

    return {
        'implantacao': implantacao.pk,
        'percentual': percentual,
        'etapa_atual': etapa_atual,
        'etapas': {'total': total_etapas, 'concluidas': etapas_concluidas},
        'tarefas': {'total': total_tarefas, 'concluidas': tarefas_concluidas},
    }


def _calcular_progresso(implantacao):
    etapas = list(
        EtapaImplantacao.objects.filter(implantacao=implantacao)
        .prefetch_related('tarefas')
        .order_by('ordem')
    )
    return _calcular_progresso_dados(implantacao, etapas)


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    template_name = 'pages/dashboard.html'

    def get(self, request):
        stats = {
            'total': Implantacao.objects.count(),
            'nao_iniciado': Implantacao.objects.filter(status=StatusImplantacao.NAO_INICIADO).count(),
            'em_andamento': Implantacao.objects.filter(status=StatusImplantacao.EM_ANDAMENTO).count(),
            'finalizado': Implantacao.objects.filter(status=StatusImplantacao.FINALIZADO).count(),
            'cancelado': Implantacao.objects.filter(status=StatusImplantacao.CANCELADO).count(),
        }

        ultimas = list(
            Implantacao.objects.select_related('movidesk').order_by('-criado_em')[:8]
        )

        if ultimas:
            etapas_pipeline = _montar_pipeline_padrao(ultimas[0])
        else:
            etapas_pipeline = {
                nome: {
                    'concluida': False,
                    'andamento': False,
                    'texto': 'Aguardando primeira implantação',
                }
                for nome in ETAPAS_PADRAO_NOMES
            }

        ultimas_com_progresso = []
        if ultimas:
            etapa_map = {}
            implantacao_pks = [i.pk for i in ultimas]
            for etapa in (
                EtapaImplantacao.objects.filter(implantacao_id__in=implantacao_pks)
                .prefetch_related('tarefas')
                .order_by('ordem')
            ):
                etapa_map.setdefault(etapa.implantacao_id, []).append(etapa)

            for imp in ultimas:
                progresso = _calcular_progresso_dados(imp, etapa_map.get(imp.pk, []))
                ultimas_com_progresso.append((imp, progresso))

        ctx = {
            'stats': stats,
            'ultimas': ultimas_com_progresso,
            'etapas_pipeline': etapas_pipeline,
        }
        return render(request, self.template_name, ctx)


@method_decorator(login_required, name='dispatch')
class ImplantacaoListView(ListView):
    template_name = 'pages/implantacao_list.html'
    context_object_name = 'object_list'
    paginate_by = 25

    def get_queryset(self):
        qs = Implantacao.objects.select_related('movidesk').order_by('-criado_em')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(cliente__icontains=q)
                | Q(codigo_cliente__icontains=q)
                | Q(documento_cliente__icontains=q)
                | Q(implantador__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '').strip()
        return ctx


@method_decorator(login_required, name='dispatch')
class ImplantacaoDetailView(DetailView):
    template_name = 'pages/implantacao_detail.html'
    context_object_name = 'object'
    queryset = Implantacao.objects.all()

    def get_queryset(self):
        return super().get_queryset().select_related('movidesk')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        imp = self.object
        ctx['progresso'] = _calcular_progresso(imp)
        ctx['movidesk'] = getattr(imp, 'movidesk', None)
        ctx['etapas'] = list(
            EtapaImplantacao.objects.filter(implantacao=imp)
            .prefetch_related('tarefas')
            .order_by('ordem')
        )
        ctx['modulos'] = list(
            ImplantacaoModulo.objects.filter(implantacao=imp)
            .select_related('modulo')
            .prefetch_related('telas', 'telas__tela')
            .order_by('modulo__nome')
        )
        ctx['treinamentos'] = list(
            Treinamento.objects.filter(implantacao=imp)
            .select_related('modulo')
            .order_by('data_agendada')
        )

        historico = list(
            Implantacao.objects.filter(implantador__isnull=False)
            .exclude(implantador='')
            .values_list('implantador', flat=True)
            .distinct()[:8]
        )
        sugestao = sorted({*IMPLANTADORES_SUGESTAO, *historico})
        if imp.implantador and imp.implantador not in sugestao:
            sugestao.insert(0, imp.implantador)
        ctx['implantadores_sugestao'] = [n for n in sugestao if n]
        return ctx


@method_decorator(login_required, name='dispatch')
class ImplantacaoIniciarView(View):
    def post(self, request, pk):
        imp = get_object_or_404(Implantacao, pk=pk)
        implantador = (request.POST.get('implantador') or '').strip()
        if not implantador:
            messages.error(request, 'Selecione ou informe o implantador antes de iniciar.')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)
        try:
            ImplantacaoService.iniciar(imp, implantador=implantador)
            messages.success(request, f'Implantação iniciada com {imp.implantador}.')
        except Exception as exc:
            messages.error(request, f'Não foi possível iniciar a implantação: {exc}')
        return redirect('implantacao:implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class ImplantacaoCancelarView(View):
    def post(self, request, pk):
        imp = get_object_or_404(Implantacao, pk=pk)
        motivo = (request.POST.get('motivo') or '').strip() or 'Cancelado manualmente'
        try:
            ImplantacaoService.cancelar(imp, motivo=motivo)
            messages.success(request, 'Implantação cancelada.')
        except Exception as exc:
            messages.error(request, f'Não foi possível cancelar: {exc}')
        return redirect('implantacao:implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class ImplantacaoEtapaConcluirView(View):
    def post(self, request, pk, etapa_id):
        imp = get_object_or_404(Implantacao, pk=pk)
        etapa = get_object_or_404(EtapaImplantacao, pk=etapa_id, implantacao=imp)

        tarefas_pendentes = etapa.tarefas.filter(obrigatoria=True, concluida=False)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if tarefas_pendentes.exists():
            msg = (
                f'Existem {tarefas_pendentes.count()} tarefas obrigatórias pendentes. '
                'Conclua todas antes de prosseguir.'
            )
            if is_ajax:
                return JsonResponse({'ok': False, 'erro': msg}, status=400)
            messages.error(request, msg)
            return redirect('implantacao:implantacao_detail', pk=imp.pk)

        try:
            WorkflowService.concluir_etapa(etapa)
            if is_ajax:
                return JsonResponse({
                    'ok': True,
                    'etapa_id': etapa.id,
                    'mensagem': f'Etapa "{etapa.nome}" concluída com sucesso.',
                })
            messages.success(request, f'Etapa "{etapa.nome}" concluída.')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)
        except Exception as exc:
            if is_ajax:
                return JsonResponse({'ok': False, 'erro': str(exc)}, status=400)
            messages.error(request, f'Não foi possível concluir a etapa: {exc}')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class ImplantacaoTarefaConcluirView(View):
    def post(self, request, pk, etapa_id, tarefa_id):
        imp = get_object_or_404(Implantacao, pk=pk)
        etapa = get_object_or_404(EtapaImplantacao, pk=etapa_id, implantacao=imp)
        tarefa = get_object_or_404(TarefaImplantacao, pk=tarefa_id, etapa=etapa)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        try:
            if not tarefa.concluida:
                tarefa.concluida = True
                tarefa.concluida_em = timezone.now()
                tarefa.save()

            if is_ajax:
                return JsonResponse({
                    'ok': True,
                    'tarefa_id': tarefa.id,
                    'concluida': tarefa.concluida,
                    'concluida_em': tarefa.concluida_em.strftime('%d/%m/%Y %H:%M') if tarefa.concluida_em else None,
                })
            messages.success(request, f'Tarefa "{tarefa.titulo}" concluída.')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)
        except Exception as exc:
            if is_ajax:
                return JsonResponse({'ok': False, 'erro': str(exc)}, status=400)
            messages.error(request, f'Não foi possível concluir a tarefa: {exc}')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class ImplantacaoTelaConcluirView(View):
    def post(self, request, pk, modulo_id, tela_id):
        imp = get_object_or_404(Implantacao, pk=pk)
        modulo = get_object_or_404(ImplantacaoModulo, pk=modulo_id, implantacao=imp)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        try:
            if tela_rel.status != 'concluida':
                tela_rel.status = 'concluida'
                tela_rel.concluida_em = timezone.now()
                tela_rel.save()

            if is_ajax:
                return JsonResponse({
                    'ok': True,
                    'tela_id': tela_rel.id,
                    'status': tela_rel.status,
                    'concluida_em': tela_rel.concluida_em.strftime('%d/%m/%Y %H:%M') if tela_rel.concluida_em else None,
                })
            messages.success(request, f'Tela "{tela_rel.tela.nome}" concluída.')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)
        except Exception as exc:
            if is_ajax:
                return JsonResponse({'ok': False, 'erro': str(exc)}, status=400)
            messages.error(request, f'Não foi possível concluir a tela: {exc}')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class ImplantacaoModuloConcluirView(View):
    def post(self, request, pk, modulo_id):
        imp = get_object_or_404(Implantacao, pk=pk)
        modulo = get_object_or_404(ImplantacaoModulo, pk=modulo_id, implantacao=imp)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        telas_pendentes = modulo.telas.filter(status__in=['pendente', 'em_andamento'])
        if telas_pendentes.exists():
            msg = f'Existem {telas_pendentes.count()} telas pendentes. Conclua todas antes de prosseguir.'
            if is_ajax:
                return JsonResponse({'ok': False, 'erro': msg}, status=400)
            messages.error(request, msg)
            return redirect('implantacao:implantacao_detail', pk=imp.pk)

        try:
            modulo.status = 'concluido'
            modulo.concluido_em = timezone.now()
            modulo.save()

            if is_ajax:
                return JsonResponse({
                    'ok': True,
                    'modulo_id': modulo.id,
                    'mensagem': f'Módulo "{modulo.modulo.nome}" concluído com sucesso.',
                })
            messages.success(request, f'Módulo "{modulo.modulo.nome}" concluído.')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)
        except Exception as exc:
            if is_ajax:
                return JsonResponse({'ok': False, 'erro': str(exc)}, status=400)
            messages.error(request, f'Não foi possível concluir o módulo: {exc}')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class MovideskImportView(View):
    template_name = 'pages/movidesk_import.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        ticket_id = request.POST.get('ticket_id')
        try:
            ticket_id_int = int(ticket_id) if ticket_id else None
        except (TypeError, ValueError):
            messages.error(request, 'Informe um ID de ticket válido.')
            return render(request, self.template_name, {'ticket_id': ticket_id})

        if not ticket_id_int or ticket_id_int <= 0:
            messages.error(request, 'Informe um ID de ticket maior que zero.')
            return render(request, self.template_name, {'ticket_id': ticket_id})

        try:
            from implantacao.integrations.movidesk.service import MovideskImportService
            service = MovideskImportService()
            implantacao = service.importar_ticket(ticket_id_int)
            messages.success(
                request,
                f'Ticket #{ticket_id_int} importado com sucesso — Implantação #{implantacao.pk} criada/atualizada.',
            )
            return redirect('implantacao:implantacao_detail', pk=implantacao.pk)
        except Exception as exc:
            messages.error(request, f'Falha ao importar ticket #{ticket_id_int}: {exc}')
            return render(request, self.template_name, {'ticket_id': ticket_id})


@method_decorator(login_required, name='dispatch')
class ImplantacaoEnviarAcaoView(View):

    TIPO_INTERNO = 'interna'
    TIPO_PUBLICA = 'publica'

    def _voltar(self, request, imp):
        next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect('implantacao:implantacao_detail', pk=imp.pk)

    def _tem_origem(self, imp):
        return bool(getattr(imp, 'movidesk', None))

    def get(self, request, pk):
        imp = get_object_or_404(Implantacao, pk=pk)
        next_url = (request.GET.get('next') or '').strip()
        sem_origem = not self._tem_origem(imp)
        data = {
            'implantacao': imp,
            'next': next_url,
            'sem_origem': sem_origem,
            'origem': imp.movidesk if not sem_origem else None,
        }
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('partial') == '1':
            return render(request, 'partials/movidesk_acao_modal.html', data)
        return render(request, 'pages/movidesk_acao.html', data)

    def post(self, request, pk):
        imp = get_object_or_404(Implantacao, pk=pk)
        tipo = (request.POST.get('tipo_acao') or '').strip().lower()
        descricao = (request.POST.get('descricao_acao') or '').strip()
        arquivos = request.FILES.getlist('anexos')

        if tipo not in (self.TIPO_INTERNO, self.TIPO_PUBLICA):
            messages.error(request, 'Selecione o tipo da ação: Interna ou Pública.')
            return self._voltar(request, imp)

        if not descricao:
            messages.error(request, 'Informe a descrição da ação antes de enviar.')
            return self._voltar(request, imp)

        try:
            from implantacao.integrations.movidesk.services.movidesk_sync_service import (
                MovideskSyncService,
            )
            sync = MovideskSyncService()
            tipo_enum = sync.TIPO_ACAO_INTERNA if tipo == self.TIPO_INTERNO else sync.TIPO_ACAO_PUBLICA

            if arquivos:
                sync.adicionar_acao_com_anexo(
                    implantacao=imp,
                    descricao=descricao,
                    arquivos=arquivos,
                    tipo=tipo_enum,
                )
            elif tipo == self.TIPO_INTERNO:
                sync.adicionar_acao_interna(imp, descricao)
            else:
                sync.adicionar_acao_publica(imp, descricao)

            tipo_nome = 'interna' if tipo == self.TIPO_INTERNO else 'pública'
            msg_sucesso = f'Ação {tipo_nome} enviada para o ticket Movidesk com sucesso.'
            if arquivos:
                msg_sucesso += f' ({len(arquivos)} anexo(s) enviado(s)).'

            messages.success(request, msg_sucesso)

        except ValueError as ve:
            messages.error(request, f'{ve}')
        except Exception as exc:
            messages.error(request, f'Erro ao enviar ação para o Movidesk: {exc}')

        return self._voltar(request, imp)


@login_required
def implantacao_nova(request):
    template_name = 'pages/implantacao_nova.html'
    if request.method == 'POST':
        codigo_cliente = (request.POST.get('codigo_cliente') or '').strip()
        cliente = (request.POST.get('cliente') or '').strip()
        documento_cliente = (request.POST.get('documento_cliente') or '').strip()
        empresa = request.POST.get('empresa') or 0
        filial = request.POST.get('filial') or 0
        implantador = (request.POST.get('implantador') or '').strip()
        data_implantacao = (request.POST.get('data_implantacao') or None) or None
        prazo = (request.POST.get('prazo_implementacao') or None) or None
        observacoes = (request.POST.get('observacoes') or '').strip()
        template = (request.POST.get('template') or 'padrao').strip()
        movidesk_ticket_id = (request.POST.get('movidesk_ticket_id') or '').strip() or None
        modulos_codigos_raw = (request.POST.get('modulos_codigos') or '').strip() or None

        if not codigo_cliente or not cliente or not documento_cliente:
            messages.error(request, 'Preencha os campos obrigatórios: Código, Cliente e Documento.')
            return render(request, template_name, {'form_data': request.POST, 'templates': TEMPLATES})

        try:
            imp = ImplantacaoService.criar(
                codigo_cliente=codigo_cliente,
                cliente=cliente,
                documento_cliente=documento_cliente,
                empresa=int(empresa),
                filial=int(filial),
                implantador=implantador,
                data_implantacao=data_implantacao,
                prazo_implementacao=prazo,
                observacoes=observacoes,
                template=template,
            )
            if modulos_codigos_raw:
                codigos = [c.strip() for c in modulos_codigos_raw.split(',') if c.strip()]
                if codigos:
                    ModuloService.associar_nomes(imp, codigos)
            if movidesk_ticket_id and str(movidesk_ticket_id).isdigit():
                try:
                    from implantacao.integrations.movidesk.client import MovideskClient
                    client = MovideskClient()
                    raw = client.obter_ticket(int(movidesk_ticket_id))
                    ImplantacaoService.registrar_origem(imp, int(movidesk_ticket_id), raw)
                except Exception as e:
                    messages.warning(
                        request,
                        f'Implantação #{imp.pk} criada, porém não foi possível registrar a origem Movidesk: {e}',
                    )
            messages.success(request, f'Implantação #{imp.pk} criada com sucesso.')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)
        except Exception as exc:
            messages.error(request, f'Erro ao criar implantação: {exc}')
            return render(request, template_name, {'form_data': request.POST, 'templates': TEMPLATES})

    templates_meta = {
        k: {
            'nome': v['nome'],
            'modulos': list(v.get('modulos', [])),
            'etapas': list(v.get('etapas', [])),
            'treinamentos': list(v.get('treinamentos', [])),
        }
        for k, v in TEMPLATES.items()
    }
    return render(request, template_name, {'templates': TEMPLATES, 'templates_meta': templates_meta})


@login_required
def movidesk_preview_ticket(request):
    """Endpoint JSON: busca ticket por ID e retorna dados mapeados (sem salvar).
    Usado pelo formulário de Nova Implantação para pré-preencher."""
    ticket_id_raw = request.GET.get('ticket_id') or ''
    if not ticket_id_raw:
        return JsonResponse({'ok': False, 'erro': 'Informe ticket_id na query string.'}, status=400)
    try:
        ticket_id = int(ticket_id_raw)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'erro': 'ticket_id deve ser um número inteiro.'}, status=400)

    try:
        from implantacao.integrations.movidesk.client import MovideskClient
        from implantacao.integrations.movidesk.mapper import MovideskMapper
        client = MovideskClient()
        ticket = client.obter_ticket(ticket_id)
        data = MovideskMapper.ticket_to_implantacao_data(ticket)
        data.pop('raw', None)
        if data.get('data_implantacao') is not None:
            data['data_implantacao'] = data['data_implantacao'].isoformat()
        if data.get('prazo_implementacao') is not None:
            data['prazo_implementacao'] = data['prazo_implementacao'].isoformat()
        data['modulos_sugeridos'] = list(data.get('modulos_sugeridos') or [])
    except Exception as exc:
        return JsonResponse({'ok': False, 'erro': str(exc)}, status=502)

    return JsonResponse({'ok': True, 'dados': data})


@login_required
def editar_treinamentos(request, pk):
    imp = get_object_or_404(Implantacao, pk=pk)
    treinamentos = Treinamento.objects.filter(implantacao=imp)

    if request.method == 'POST':
        for t in treinamentos:
            data_agendada = request.POST.get(f'treinamento_{t.id}')
            responsavel = request.POST.get(f'responsavel_{t.id}', '').strip()
            realizado = request.POST.get(f'realizado_{t.id}') == 'on'

            if data_agendada:
                try:
                    t.data_agendada = datetime.fromisoformat(data_agendada)
                except ValueError:
                    pass

            if responsavel:
                t.responsavel = responsavel

            t.realizado = realizado
            t.save()

        messages.success(request, 'Datas de treinamentos atualizadas com sucesso.')
        return redirect('implantacao:implantacao_detail', pk=imp.pk)

    return redirect('implantacao:implantacao_detail', pk=imp.pk)


@login_required
def editar_modulos(request, pk):
    imp = get_object_or_404(Implantacao, pk=pk)
    modulos = ImplantacaoModulo.objects.filter(implantacao=imp)

    if request.method == 'POST':
        for im in modulos:
            inicio_previsto = request.POST.get(f'modulo_inicio_{im.id}')
            fim_previsto = request.POST.get(f'modulo_fim_{im.id}')
            concluido = request.POST.get(f'modulo_concluido_{im.id}') == 'on'

            if inicio_previsto:
                try:
                    im.inicio_previsto = datetime.strptime(inicio_previsto, '%Y-%m-%d').date()
                except ValueError:
                    pass

            if fim_previsto:
                try:
                    im.fim_previsto = datetime.strptime(fim_previsto, '%Y-%m-%d').date()
                except ValueError:
                    pass

            if concluido:
                im.status = 'concluido'
                im.concluido_em = timezone.now()

            im.save()

        messages.success(request, 'Datas de módulos atualizadas com sucesso.')
        return redirect('implantacao:implantacao_detail', pk=imp.pk)

    return redirect('implantacao:implantacao_detail', pk=imp.pk)


@login_required
def kickoff_form(request, pk):
    imp = get_object_or_404(Implantacao, pk=pk)

    if request.method == 'POST':
        data_kickoff = request.POST.get('data_kickoff')
        participantes = request.POST.get('participantes', '').strip()
        escopo = request.POST.get('escopo', '').strip()
        responsaveis = request.POST.get('responsaveis', '').strip()
        contador = request.POST.get('contador', '').strip()
        importacao_dados = request.POST.get('importacao_dados', '').strip()
        observacoes = request.POST.get('observacoes', '').strip()

        kickoff_info = (
            '\n=== FORMULÁRIO KICKOFF ===\n'
            f'Data: {data_kickoff or "Não informada"}\n'
            f'Participantes: {participantes or "Não informados"}\n'
            f'Escopo: {escopo or "Não definido"}\n'
            f'Responsáveis: {responsaveis or "Não definidos"}\n'
            f'Contador: {contador or "Não informado"}\n'
            f'Importação de Dados: {importacao_dados or "Não informado"}\n'
            f'Observações: {observacoes or "Nenhuma"}\n'
            '============================\n'
        )

        imp.observacoes = f'{imp.observacoes}\n\n{kickoff_info}' if imp.observacoes else kickoff_info
        imp.save()

        messages.success(request, 'Formulário de kickoff salvo com sucesso.')
        return redirect('implantacao:implantacao_detail', pk=imp.pk)

    return redirect('implantacao:implantacao_detail', pk=imp.pk)


@login_required
def gerar_pdf(request, pk):
    imp = get_object_or_404(Implantacao, pk=pk)
    etapas = EtapaImplantacao.objects.filter(implantacao=imp).prefetch_related('tarefas').order_by('ordem')

    html_string = render_to_string('pages/implantacao_pdf.html', {
        'imp': imp,
        'etapas': etapas,
    })

    try:
        import weasyprint
        pdf_file = weasyprint.HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="implantacao_{imp.id}_{imp.cliente}.pdf"'
        return response
    except ImportError:
        # weasyprint não instalado: devolve o HTML para download/impressão
        response = HttpResponse(html_string, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="implantacao_{imp.id}_{imp.cliente}.html"'
        return response
    except Exception as exc:
        return JsonResponse({'ok': False, 'erro': f'Falha ao gerar PDF: {exc}'}, status=500)