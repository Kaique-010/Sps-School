"""
Implantações, padrão de templates para tipos distintos de implantação
================
"""


TEMPLATES = {

    "padrao": {
        "nome": "Implantação Padrão",
        "descricao": "Implantação básica do sistema.",
        "base": None,

        "etapas": [
            "diagnostico",
            "kickoff",
            "configuracao",
            "migracao",
            "homologacao",
            "treinamento",
            "go_live",
            "acompanhamento",
        ],

        "modulos": [
            "cadastros",
            "vendas",
            "financeiro_basico",
        ],

        "treinamentos": [
            "inicial",
            "vendas",
        ],
    },

    "medio": {
        "nome": "Implantação Média",
        "descricao": "Implantação intermediária.",
        "base": "padrao",

        "modulos": [
            "financeiro_robusto",
        ],

        "treinamentos": [
            "financeiro",
            "caixa",
        ],
    },

    "robusto": {
        "nome": "Implantação Robusta",
        "descricao": "Implantação completa com módulos especializados.",
        "base": "medio",

        "modulos": [
            "agricola",
            "contabilidade",
        ],

        "treinamentos": [
            "agricola",
            "contabilidade",
        ],
    },
}