from django.test import TestCase

from implantacao.models import (
    Implantacao,
    OrigemMovidesk,
    ImplantacaoModulo,
    Treinamento,
    StatusImplantacao,
)
from implantacao.services.implantacao_service import ImplantacaoService
from implantacao.services.modulo_service import ModuloService
from implantacao.services.treinamento_service import TreinamentoService


class RegistrarOrigemTest(TestCase):
    def setUp(self):
        self.impl = Implantacao.objects.create(
            codigo_cliente='X1',
            cliente='Cliente X',
            documento_cliente='',
            status=StatusImplantacao.NAO_INICIADO,
        )

    def test_registrar_origem_cria(self):
        origem = ImplantacaoService.registrar_origem(self.impl, 123, {'foo': 'bar'})
        self.assertEqual(origem.ticket_id, 123)
        self.assertEqual(origem.dados_origem, {'foo': 'bar'})
        self.assertIsNotNone(origem.sincronizado_em)
        self.assertEqual(OrigemMovidesk.objects.count(), 1)

    def test_registrar_origem_atualiza(self):
        ImplantacaoService.registrar_origem(self.impl, 123, {'v1': 1})
        ImplantacaoService.registrar_origem(self.impl, 456, {'v2': 2})

        self.assertEqual(OrigemMovidesk.objects.count(), 1)
        origem = OrigemMovidesk.objects.get(implantacao=self.impl)
        self.assertEqual(origem.ticket_id, 456)
        self.assertEqual(origem.dados_origem, {'v2': 2})


class ImplantacaoServiceCriarTest(TestCase):
    def test_criar_usa_empresa_e_filial(self):
        imp = ImplantacaoService.criar(
            codigo_cliente='C1',
            cliente='Cli',
            documento_cliente='123',
            empresa=3,
            filial=7,
            template='padrao',
        )
        self.assertEqual(imp.empresa, 3)
        self.assertEqual(imp.filial, 7)
        self.assertEqual(imp.status, 'nao_iniciado')
        self.assertGreater(imp.etapas.count(), 0)

    def test_criar_com_data_implantacao(self):
        imp = ImplantacaoService.criar(
            codigo_cliente='C2',
            cliente='Cli2',
            documento_cliente='321',
            data_implantacao=__import__('datetime').date(2026, 5, 1),
            template='padrao',
        )
        self.assertEqual(imp.data_implantacao.isoformat(), '2026-05-01')


class ModuloServiceAssociarNomesTest(TestCase):
    def setUp(self):
        self.impl = Implantacao.objects.create(
            codigo_cliente='M1', cliente='ModTest', documento_cliente='',
        )

    def test_associar_por_codigo_exato(self):
        ModuloService.associar_nomes(self.impl, ['vendas', 'cadastros'])
        codigos = sorted(
            ImplantacaoModulo.objects.filter(implantacao=self.impl)
            .values_list('modulo__codigo', flat=True)
        )
        self.assertEqual(codigos, ['cadastros', 'vendas'])

    def test_associar_por_nome_aproximado(self):
        ModuloService.associar_nomes(self.impl, ['Financeiro'])
        codigos = list(
            ImplantacaoModulo.objects.filter(implantacao=self.impl)
            .values_list('modulo__codigo', flat=True)
        )
        self.assertTrue(len(codigos) >= 1, f'Esperava pelo menos 1 módulo, obtive {codigos}')
        self.assertTrue(any('financeiro' in c for c in codigos))

    def test_associar_nomes_lista_vazia(self):
        result = ModuloService.associar_nomes(self.impl, [])
        self.assertEqual(result, [])
        self.assertEqual(ImplantacaoModulo.objects.filter(implantacao=self.impl).count(), 0)


class TreinamentoServiceAgendaPadraoTest(TestCase):
    def setUp(self):
        self.impl = ImplantacaoService.criar(
            codigo_cliente='T1',
            cliente='TreinTest',
            documento_cliente='111',
            template='padrao',
        )

    def test_criar_agenda_padrao_nao_duplica(self):
        antes = Treinamento.objects.filter(implantacao=self.impl).count()
        result1 = TreinamentoService.criar_agenda_padrao(self.impl)
        result2 = TreinamentoService.criar_agenda_padrao(self.impl)
        depois = Treinamento.objects.filter(implantacao=self.impl).count()
        self.assertEqual(len(result2), 0, "Segunda chamada não deve criar novos")
        self.assertGreaterEqual(depois, antes)
