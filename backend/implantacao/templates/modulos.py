"""
CATÁLOGO DE MÓDULOS E TELAS
============================

Define os módulos disponíveis no sistema e as telas
pertencentes a cada módulo.

A seleção dos módulos de uma implantação é determinada
pelo template escolhido e posteriormente validada/ajustada
durante o kickoff.
"""

MODULOS = {

    "cadastros": {
        "nome": "Cadastros Gerais",
        "telas": [
            "Entidades Gerais",
            "Produtos",
            "Transportadoras",
        ],
    },

    "vendas": {
        "nome": "Vendas",
        "telas": [
            "Pedidos de Venda",
            "Orçamentos",
            "Entidades",
            "Emissões de Notas Fiscais",
            "Relatórios de Vendas",
        ],
    },

    "financeiro_basico": {
        "nome": "Financeiro Básico",
        "telas": [
            "Contas a Pagar",
            "Contas a Receber",
        ],
    },

    "financeiro_robusto": {
        "nome": "Financeiro",
        "telas": [
            "Contas a Pagar",
            "Contas a Receber",
            "Fluxo de Caixa",
            "Caixa / Frente de Caixa",
        ],
    },

    "transportes": {
        "nome": "Transportes",
        "telas": [
            "Transportadoras",
            "CTEs",
            "MDFE",
            "Relatórios de Transportes",
        ],
    },

    "agricola": {
        "nome": "Agrícola",
        "telas": [],
    },

    "contabilidade": {
        "nome": "Contabilidade",
        "telas": [],
    },
}