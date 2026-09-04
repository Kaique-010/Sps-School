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
                "titulo": "Realizar reunião de kickoff",
                "obrigatoria": True,
            },
            {
                "titulo": "Definir escopo final da implantação",
                "obrigatoria": True,
            },
            {
                "titulo": "Definir empresas e filiais",
                "obrigatoria": True,
            },
            {
                "titulo": "Definir prazo da implantação",
                "obrigatoria": True,
            },
            {
                "titulo": "Validar módulos da implantação",
                "obrigatoria": True,
            },
        ],
    },

    "configuracao": {
        "nome": "Configuração",
        "ordem": 30,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Configurar ambiente",
                "obrigatoria": True,
            },
        ],
    },

    "migracao": {
        "nome": "Migração de Dados",
        "ordem": 40,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Validar dados para migração",
                "obrigatoria": True,
            },
            {
                "titulo": "Executar migração",
                "obrigatoria": True,
            },
        ],
    },

    "homologacao": {
        "nome": "Homologação",
        "ordem": 50,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Validar processos com cliente",
                "obrigatoria": True,
            },
        ],
    },

    "treinamento": {
        "nome": "Treinamento",
        "ordem": 60,
        "obrigatoria": True,
        "tarefas": [],
    },

    "go_live": {
        "nome": "Go Live",
        "ordem": 70,
        "obrigatoria": True,
        "tarefas": [
            {
                "titulo": "Acompanhar entrada em produção",
                "obrigatoria": True,
            },
        ],
    },

    "acompanhamento": {
        "nome": "Acompanhamento",
        "ordem": 80,
        "obrigatoria": False,
        "tarefas": [],
    },
}