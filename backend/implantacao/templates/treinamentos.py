"""
CATÁLOGO DE TREINAMENTOS
========================

Define os treinamentos disponíveis para utilização
nos templates de implantação.

A criação dos treinamentos da implantação é responsabilidade
do TemplateService.
"""

TREINAMENTOS = {

    "inicial": {
        "titulo": "Treinamento Inicial",
        "descricao": "Apresentação geral do sistema e principais funcionalidades.",
        "modulo": None,
    },

    "financeiro": {
        "titulo": "Treinamento Financeiro",
        "descricao": "Treinamento dos processos financeiros do sistema.",
        "modulo": "financeiro_robusto",
    },

    "vendas": {
        "titulo": "Treinamento de Vendas",
        "descricao": "Treinamento dos processos de vendas.",
        "modulo": "vendas",
    },

    "caixa": {
        "titulo": "Treinamento de Caixa / Frente de Caixa",
        "descricao": "Treinamento dos processos de caixa e frente de caixa.",
        "modulo": "caixa",
    },

    "agricola": {
        "titulo": "Treinamento Agrícola",
        "descricao": "Treinamento dos processos do módulo agrícola.",
        "modulo": "agricola",
    },

    "contabilidade": {
        "titulo": "Treinamento de Contabilidade",
        "descricao": "Treinamento dos processos contábeis.",
        "modulo": "contabilidade",
    },
}