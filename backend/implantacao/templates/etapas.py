"""
ETAPAS PADRÃO DA IMPLANTAÇÃO
=============================

Edite este arquivo para personalizar:
- Ordem e quantidade de etapas
- Nome de cada etapa
- Se é obrigatória
- Tarefas que cada etapa deve conter (título e se é obrigatória)

Sintaxe:
{
    'nome': str,                     # Nome da etapa (aparece no detalhe, dashboard)
    'ordem': int,                    # Ordem de execução
    'obrigatoria': bool,             # Não pode ser pulada
    'tarefas': list[tuple[str,bool]] # [(nome_tarefa, obrigatoria?), ...]
}
"""

ETAPAS = {

    "diagnostico": {
        "nome": "Diagnóstico",
        "ordem": 10,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Realizar reunião de diagnóstico",
                "obrigatoria": True,
            },
            {
                "titulo": "Levantar necessidades do cliente",
                "obrigatoria": True,
            },
        ],
    },

    "kickoff": {
        "nome": "Kickoff",
        "ordem": 20,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Realizar reunião de kickoff com apresentação do guia de onboarding",
                "obrigatoria": True,
            },
            {
                "titulo": "Aplicar Questionário de Levantamento da Operação (Anexo I)",
                "obrigatoria": True,
            },
            {
                "titulo": "Definir escopo final da implantação conforme contrato",
                "obrigatoria": True,
            },
            {
                "titulo": "Definir empresas e filiais no sistema",
                "obrigatoria": True,
            },
            {
                "titulo": "Definir prazo da implantação e cronograma",
                "obrigatoria": True,
            },
            {
                "titulo": "Validar módulos da implantação contratados",
                "obrigatoria": True,
            },
            {
                "titulo": "Confirmar envolvimento do contador para configurações fiscais",
                "obrigatoria": True,
            },
            {
                "titulo": "Indicar responsáveis por cada área/módulo",
                "obrigatoria": True,
            },
            {
                "titulo": "Definir datas e horários para treinamentos",
                "obrigatoria": True,
            },
            {
                "titulo": "Verificar necessidade de importação de dados de sistema anterior",
                "obrigatoria": True,
            },
            {
                "titulo": "Definir canais de comunicação e suporte",
                "obrigatoria": True,
            },
            {
                "titulo": "Alinhar expectativas sobre período de adaptação (1-3 meses)",
                "obrigatoria": True,
            },
            {
                "titulo": "Obter assinatura do termo de compromisso de colaboração",
                "obrigatoria": True,
            },
        ],
    },

    "pre_setup": {
        "nome": "Pré-Setup (Configuração Inicial)",
        "ordem": 30,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Configurar ambiente do sistema conforme contrato",
                "obrigatoria": True,
            },
            {
                "titulo": "Realizar configuração fiscal inicial (CFOP, regras tributárias, parâmetros)",
                "obrigatoria": True,
            },
            {
                "titulo": "Validar configurações fiscais com contador do cliente",
                "obrigatoria": True,
            },
            {
                "titulo": "Importar cadastro de produtos/serviços de sistema anterior (se aplicável)",
                "obrigatoria": False,
            },
            {
                "titulo": "Criar usuários e perfis de acesso conforme acordado/contratado",
                "obrigatoria": True,
            },
            {
                "titulo": "Parametrizar configurações básicas da empresa",
                "obrigatoria": True,
            },
            {
                "titulo": "Configurar parâmetros de NF-e conforme orientações do contador",
                "obrigatoria": True,
            },
            {
                "titulo": "Verificar ambiente técnico para suportar operação (servidor, backup, etc)",
                "obrigatoria": True,
            },
        ],
    },

    "configuracao": {
        "nome": "Configuração de Cadastros",
        "ordem": 40,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Treinar responsável pelos cadastros básicos",
                "obrigatoria": True,
            },
            {
                "titulo": "Configurar cadastro de entidades (clientes, fornecedores, transportadoras)",
                "obrigatoria": True,
            },
            {
                "titulo": "Configurar cadastro de produtos e serviços (ou revisão após importação)",
                "obrigatoria": True,
            },
            {
                "titulo": "Configurar cadastro de centro de custo",
                "obrigatoria": True,
            },
            {
                "titulo": "Verificar configurações fiscais dos produtos (NCM, CFOP, impostos)",
                "obrigatoria": True,
            },
            {
                "titulo": "Configurar cadastro de tabelas de preço",
                "obrigatoria": True,
            },
            {
                "titulo": "Configurar condições de pagamento",
                "obrigatoria": True,
            },
        ],
    },

    "treinamento_estoque": {
        "nome": "Treinamento - Estoque",
        "ordem": 50,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Agendar treinamento com responsável do estoque",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar movimentações de estoque",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar processo de inventário",
                "obrigatoria": True,
            },
            {
                "titulo": "Configurar alertas de estoque mínimo",
                "obrigatoria": True,
            },
        ],
    },

    "treinamento_compras": {
        "nome": "Treinamento - Compras",
        "ordem": 60,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Agendar treinamento com responsável de compras",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar importação de NF de entrada",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar processo de notas destinadas",
                "obrigatoria": True,
            },
        ],
    },

    "treinamento_vendas": {
        "nome": "Treinamento - Vendas",
        "ordem": 70,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Agendar treinamento com responsável de vendas",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar processo de orçamento",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar pedido de venda",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar emissão de NF-e, NFSe e O.S",
                "obrigatoria": True,
            },
        ],
    },

    "treinamento_financeiro": {
        "nome": "Treinamento - Financeiro",
        "ordem": 80,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Agendar treinamento com responsável financeiro",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar gestão de contas a pagar",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar gestão de contas a receber",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar bancos e caixas",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar balancete por centro de custo",
                "obrigatoria": True,
            },
            {
                "titulo": "Treinar relatórios financeiros diversos",
                "obrigatoria": True,
            },
        ],
    },

    "homologacao": {
        "nome": "Homologação",
        "ordem": 90,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Validar processos com cliente em ambiente de teste",
                "obrigatoria": True,
            },
            {
                "titulo": "Realizar testes integrados entre módulos",
                "obrigatoria": True,
            },
            {
                "titulo": "Validar emissão de notas fiscais de teste",
                "obrigatoria": True,
            },
            {
                "titulo": "Confirmar configurações finais com cliente",
                "obrigatoria": True,
            },
        ],
    },

    "go_live": {
        "nome": "Go Live (Entrada em Produção)",
        "ordem": 100,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Preparar ambiente de produção",
                "obrigatoria": True,
            },
            {
                "titulo": "Realizar backup final do sistema anterior",
                "obrigatoria": True,
            },
            {
                "titulo": "Acompanhar entrada em produção no dia da virada",
                "obrigatoria": True,
            },
            {
                "titulo": "Verificar funcionamento de todos os módulos em produção",
                "obrigatoria": True,
            },
            {
                "titulo": "Acompanhar primeiras operações reais do cliente",
                "obrigatoria": True,
            },
        ],
    },

    "checkpoint_30_dias": {
        "nome": "Checkpoint - 30 Dias",
        "ordem": 110,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Verificação de uso do sistema",
                "obrigatoria": True,
            },
            {
                "titulo": "Resolver dúvidas iniciais",
                "obrigatoria": True,
            },
            {
                "titulo": "Ajustes de configuração identificados",
                "obrigatoria": True,
            },
            {
                "titulo": "Avaliar adaptação da equipe",
                "obrigatoria": True,
            },
        ],
    },

    "checkpoint_60_dias": {
        "nome": "Checkpoint - 60 Dias",
        "ordem": 120,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Avaliar principais módulos em operação",
                "obrigatoria": True,
            },
            {
                "titulo": "Verificar relatórios em uso",
                "obrigatoria": True,
            },
            {
                "titulo": "Identificar dificuldades remanescentes",
                "obrigatoria": True,
            },
            {
                "titulo": "Ajustar processos conforme necessário",
                "obrigatoria": True,
            },
        ],
    },

    "checkpoint_90_dias": {
        "nome": "Checkpoint - 90 Dias",
        "ordem": 130,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Revisão completa do sistema",
                "obrigatoria": True,
            },
            {
                "titulo": "Encerramento do período de adaptação",
                "obrigatoria": True,
            },
            {
                "titulo": "Avaliar independência da equipe",
                "obrigatoria": True,
            },
            {
                "titulo": "Passagem de bastão para suporte regular",
                "obrigatoria": True,
            },
            {
                "titulo": "Documentar ajustes finais realizados",
                "obrigatoria": True,
            },
        ],
    },

    "acompanhamento": {
        "nome": "Acompanhamento Contínuo",
        "ordem": 140,
        "obrigatoria": False,
        "tarefas": [
            {
                "titulo": "Suporte durante horários comerciais",
                "obrigatoria": True,
            },
            {
                "titulo": "Retorno sobre dúvidas dentro do prazo SLA",
                "obrigatoria": True,
            },
            {
                "titulo": "Documentação e materiais de apoio disponíveis",
                "obrigatoria": True,
            },
        ],
    },
}