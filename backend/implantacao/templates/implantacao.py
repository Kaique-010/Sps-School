"""
Implantações, padrão de templates para tipos distintos de implantação
================
"""


TEMPLATES = {

    "padrao": {
        "nome": "Implantação Padrão",
        "descricao": "Implantação básica do sistema com processo completo de onboarding.",
        "base": None,

        "etapas": [
            "diagnostico",
            "kickoff",
            "pre_setup",
            "configuracao",
            "treinamento_estoque",
            "treinamento_compras",
            "treinamento_vendas",
            "treinamento_financeiro",
            "homologacao",
            "go_live",
            "checkpoint_30_dias",
            "checkpoint_60_dias",
            "checkpoint_90_dias",
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
        "descricao": "Implantação intermediária com módulos adicionais.",
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