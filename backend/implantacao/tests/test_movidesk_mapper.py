from datetime import datetime
from django.test import SimpleTestCase

from implantacao.integrations.movidesk.mapper import MovideskMapper, MovideskFormatter


class MovideskFormatterTest(SimpleTestCase):
    def test_format_cnpj(self):
        self.assertEqual(MovideskFormatter.format_document('12345678000199'),
                         '12.345.678/0001-99')

    def test_format_cpf(self):
        self.assertEqual(MovideskFormatter.format_document('12345678909'),
                         '123.456.789-09')

    def test_format_with_simbols(self):
        self.assertEqual(MovideskFormatter.format_document('12.345.678/0001-99'),
                         '12.345.678/0001-99')


TICKET_FIXTURE = {
    'id': 42,
    'number': 'MOV-42',
    'subject': 'Implantação Vendas e Financeiro',
    'description': 'Cliente precisa de emissão de notas e contas a receber. Contato: 123.456.789-09',
    'category': 'Implantação',
    'createdDate': '2026-01-10T09:00:00',
    'slaSolutionDate': '2026-02-05T18:00:00',
    'customer': {
        'id': 'C123',
        'businessName': 'Empresa Alfa Ltda',
        'cnpj': '12.345.678/0001-99',
    },
    'owner': {
        'businessName': 'Ana Implantadora',
    },
    'clients': [
        {'name': 'Contato Alfa', 'email': 'alfa@example.com'},
    ],
    'customFieldValues': [
        {'value': 'Vendas, Financeiro e Cadastros'},
    ],
}


class MovideskMapperTest(SimpleTestCase):

    def test_ticket_to_implantacao_data_campos_obrigatorios(self):
        result = MovideskMapper.ticket_to_implantacao_data(TICKET_FIXTURE)

        self.assertEqual(result['ticket_id'], 42)
        self.assertEqual(result['codigo_cliente'], 'C123')
        self.assertEqual(result['cliente'], 'Empresa Alfa Ltda')
        self.assertEqual(result['documento_cliente'], '12.345.678/0001-99')
        self.assertEqual(result['implantador'], 'Ana Implantadora')
        self.assertEqual(result['empresa'], 1)
        self.assertEqual(result['filial'], 1)
        self.assertEqual(result['data_implantacao'], datetime(2026, 1, 10).date())
        self.assertEqual(result['prazo_implementacao'], datetime(2026, 2, 5).date())
        self.assertIn('Assunto Movidesk:', result['observacoes'])
        self.assertIn('Protocolo Movidesk:', result['observacoes'])
        self.assertIs(result['raw'], TICKET_FIXTURE)

    def test_ticket_detecta_modulos_vendas(self):
        ticket = dict(TICKET_FIXTURE)
        ticket['subject'] = 'Implantação de Vendas Pedidos e Orçamentos'
        result = MovideskMapper.ticket_to_implantacao_data(ticket)
        self.assertIn('vendas', result['modulos_sugeridos'])

    def test_ticket_sem_detectar_cai_no_fallback(self):
        ticket = {
            'id': 1, 'subject': 'Ticket genérico', 'description': 'sem palavras chave',
        }
        result = MovideskMapper.ticket_to_implantacao_data(ticket)
        self.assertEqual(result['modulos_sugeridos'], ['cadastros', 'vendas', 'financeiro_basico'])

    def test_ticket_minimo_sem_campos(self):
        result = MovideskMapper.ticket_to_implantacao_data({})
        self.assertIsNone(result['ticket_id'])
        self.assertTrue(result['cliente'].startswith('Ticket '))

    def test_extract_ticket_id_multiple_keys(self):
        for key, val in [('id', 10), ('ticketId', 20), ('number', '30')]:
            data = {key: val}
            result = MovideskMapper.ticket_to_implantacao_data(data)
            self.assertEqual(result['ticket_id'], int(val))
