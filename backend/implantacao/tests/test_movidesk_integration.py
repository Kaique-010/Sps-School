from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone

from implantacao.integrations.movidesk.client import MovideskError
from implantacao.integrations.movidesk.mapper import MovideskMapper
from implantacao.integrations.movidesk.service import MovideskImportService
from implantacao.models import Implantacao, OrigemMovidesk, EtapaImplantacao, TarefaImplantacao


TICKET_FIXTURE = {
    'id': 88,
    'number': 'MOV-88',
    'subject': 'Implantação Completa - Vendas + Financeiro',
    'description': 'Emissão de NF, Pedidos, Contas a pagar e receber.',
    'createdDate': '2026-03-01T10:00:00',
    'slaSolutionDate': '2026-03-25T18:00:00',
    'customer': {
        'id': 'C999',
        'businessName': 'Cliente Beta SA',
        'cnpj': '98.765.432/0001-00',
    },
    'owner': {'businessName': 'Bruno Consultor'},
    'clients': [{'name': 'Maria Beta', 'email': 'maria@beta.com'}],
    'customFields': [{'value': 'Sistema de Vendas e Financeiro'}],
}


class FakeMovideskClient:
    def __init__(self, ticket=None, error=None):
        self._ticket = ticket or TICKET_FIXTURE
        self._error = error
        self.calls = []

    def obter_ticket(self, ticket_id: int):
        self.calls.append(ticket_id)
        if self._error:
            raise self._error
        return self._ticket


class MovideskImportServiceTest(TestCase):

    def setUp(self):
        self.client_mock = FakeMovideskClient()

    # ---- 1. FLUXO PRINCIPAL: importar ticket NOVO ----
    def test_importar_ticket_novo_cria_tudo(self):
        service = MovideskImportService(client=self.client_mock)

        implantacao = service.importar_ticket(88, auto_iniciar_se_implantador=False)

        self.assertIsNotNone(implantacao.pk)
        self.assertEqual(implantacao.codigo_cliente, 'C999')
        self.assertEqual(implantacao.cliente, 'Cliente Beta SA')
        self.assertEqual(implantacao.documento_cliente, '98.765.432/0001-00')
        self.assertEqual(implantacao.implantador, 'Bruno Consultor')
        self.assertEqual(implantacao.empresa, 1)
        self.assertEqual(implantacao.filial, 1)
        self.assertEqual(implantacao.status, 'nao_iniciado')

        origem = OrigemMovidesk.objects.filter(implantacao=implantacao).first()
        self.assertIsNotNone(origem)
        self.assertEqual(origem.ticket_id, 88)
        self.assertIsNotNone(origem.sincronizado_em)
        self.assertEqual(origem.dados_origem['id'], 88)

        etapas = list(EtapaImplantacao.objects.filter(implantacao=implantacao).order_by('ordem'))
        self.assertGreaterEqual(len(etapas), 5)
        self.assertTrue(all(e.nome for e in etapas))

        tarefas = TarefaImplantacao.objects.filter(etapa__implantacao=implantacao).count()
        self.assertGreater(tarefas, 0)

        self.assertTrue(implantacao.modulos_implantacao.count() > 0)
        self.assertTrue(implantacao.treinamentos.count() > 0)

        self.assertEqual(self.client_mock.calls, [88])

    # ---- 2. FLUXO REIMPORTAR (ATUALIZAR) ----
    def test_importar_ticket_existente_atualiza_sem_duplicar(self):
        service = MovideskImportService(client=self.client_mock)
        imp1 = service.importar_ticket(88, auto_iniciar_se_implantador=False)
        imp2 = service.importar_ticket(88, auto_iniciar_se_implantador=False)

        self.assertEqual(imp1.pk, imp2.pk)
        self.assertEqual(Implantacao.objects.count(), 1)
        self.assertEqual(OrigemMovidesk.objects.count(), 1)
        self.assertEqual(EtapaImplantacao.objects.filter(implantacao=imp1).count(),
                         EtapaImplantacao.objects.count())

    # ---- 3. AUTO-INICIAR SE IMPLANTADOR ----
    def test_importar_ticket_auto_iniciar(self):
        service = MovideskImportService(client=self.client_mock)

        implantacao = service.importar_ticket(88, auto_iniciar_se_implantador=True)

        self.assertEqual(implantacao.status, 'em_andamento')
        primeira = EtapaImplantacao.objects.filter(implantacao=implantacao).order_by('ordem').first()
        self.assertEqual(primeira.status, 'em_andamento')
        self.assertIsNotNone(primeira.iniciada_em)

    # ---- 4. ERRO NA API ----
    def test_importar_ticket_erro_api_propaga(self):
        erro_client = FakeMovideskClient(error=MovideskError('Credenciais inválidas.'))
        service = MovideskImportService(client=erro_client)

        with self.assertRaises(MovideskError) as ctx:
            service.importar_ticket(1)
        self.assertIn('Credenciais inválidas', str(ctx.exception))
        self.assertEqual(Implantacao.objects.count(), 0)
        self.assertEqual(OrigemMovidesk.objects.count(), 0)

    # ---- 5. SEM IMPLANTADOR NÃO AUTO-INICIA ----
    def test_sem_implantador_nao_inicia_automaticamente(self):
        ticket = dict(TICKET_FIXTURE)
        ticket['owner'] = {}
        client_sem_owner = FakeMovideskClient(ticket=ticket)
        service = MovideskImportService(client=client_sem_owner)

        imp = service.importar_ticket(88, auto_iniciar_se_implantador=True)
        self.assertEqual(imp.status, 'nao_iniciado')

    # ---- 6. DETECÇÃO DE MÓDULOS NA IMPORTAÇÃO ----
    def test_modulos_sugeridos_sao_associados(self):
        ticket = dict(TICKET_FIXTURE)
        ticket['subject'] = 'Implantação Agrícola + Contabilidade'
        ticket['customFields'] = [{'value': 'Fazenda e Escrituração Contábil'}]
        cli = FakeMovideskClient(ticket=ticket)
        service = MovideskImportService(client=cli)

        imp = service.importar_ticket(88, auto_iniciar_se_implantador=False)
        codigos = [im.modulo.codigo for im in imp.modulos_implantacao.select_related('modulo').all()]
        self.assertTrue(
            any(m in codigos for m in ('agricola', 'contabilidade')),
            f"Esperava agricola/contabilidade nos módulos: {codigos}",
        )


class MovideskClientConfigTest(TestCase):
    def test_client_sem_config_erro_ao_buscar(self):
        with self.settings(MOVIDESK_BASE_URL='', MOVIDESK_TOKEN=''):
            from implantacao.integrations.movidesk.client import MovideskClient
            client = MovideskClient()
            with self.assertRaises(MovideskError) as ctx:
                client.obter_ticket(1)
            self.assertIn('MOVIDESK_BASE_URL', str(ctx.exception))
