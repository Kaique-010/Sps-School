from copy import deepcopy
from implantacao.templates.implantacao import TEMPLATES


class TemplateService:
    
    @staticmethod
    def obter(template_codigo: str):
        if template_codigo not in TEMPLATES:
            raise ValueError(f"Template não encontrado: código {template_codigo}")
        return TemplateService._resolver(template_codigo)
    
    @staticmethod
    def _resolver(template_codigo):
        template = deepcopy(TEMPLATES[template_codigo])

        base = template.get("base")

        if not base:
            return template

        template_base = TemplateService._resolver(base)

        return {
            **template_base,
            "nome": template["nome"],
            "descricao": template["descricao"],
            "base": base,
            "etapas": [
                *template_base.get("etapas", []),
                *template.get("etapas", []),
            ],
            "modulos": [
                *template_base.get("modulos", []),
                *template.get("modulos", []),
            ],
            "treinamentos": [
                *template_base.get("treinamentos", []),
                *template.get("treinamentos", []),
            ],
        }

    @staticmethod
    def _adicionar_unicos(base, adicionais):
        resultado = list(base)

        for item in adicionais:
            if item not in resultado:
                resultado.append(item)

        return resultado

