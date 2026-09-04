from django.db import transaction

from implantacao.models.modulo import (
    Modulo,
    ImplantacaoModulo,
    StatusModulo,
)

from implantacao.models.tela import (
    Tela,
    ImplantacaoTela,
    StatusTela,
)

from implantacao.templates.modulos import MODULOS


class ModuloService:

    @staticmethod
    @transaction.atomic
    def associar_modulos(implantacao, modulos):
        """
        Associa os módulos informados à implantação.

        Os módulos precisam existir no catálogo de templates.
        Para cada módulo associado, suas telas também são criadas.
        """

        resultado = []

        for codigo in modulos:

            config = MODULOS.get(codigo)

            if config is None:
                raise ValueError(
                    f"Módulo não encontrado no catálogo: {codigo}"
                )

            modulo = Modulo.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nome": config["nome"],
                    "ativo": True,
                },
            )[0]

            implantacao_modulo, _ = (
                ImplantacaoModulo.objects.get_or_create(
                    implantacao=implantacao,
                    modulo=modulo,
                    defaults={
                        "status": StatusModulo.PENDENTE,
                    },
                )
            )

            ModuloService._criar_telas(
                implantacao_modulo=implantacao_modulo,
                modulo=modulo,
                telas=config.get("telas", []),
            )

            resultado.append(implantacao_modulo)

        return resultado

    @staticmethod
    @transaction.atomic
    def associar_nomes(implantacao, nomes: list[str]):
        """Associa módulos por correspondência de nome (case-insensitive)
        com os códigos do catálogo MODULOS. Ignora nomes desconhecidos."""
        nomes_normalizados = [(n or '').strip().lower() for n in (nomes or []) if (n or '').strip()]
        if not nomes_normalizados:
            return []
        codigos = []
        for codigo, cfg in MODULOS.items():
            if codigo.lower() in nomes_normalizados or cfg['nome'].lower() in nomes_normalizados:
                codigos.append(codigo)
            else:
                for n in nomes_normalizados:
                    if n and (n in codigo.lower() or n in cfg['nome'].lower()):
                        codigos.append(codigo)
                        break
        if not codigos:
            return []
        return ModuloService.associar_modulos(implantacao, codigos)

    @staticmethod
    def _criar_telas(
        implantacao_modulo,
        modulo,
        telas,
    ):
        """
        Cria as telas pertencentes ao módulo.

        A criação é idempotente: se a tela já existir,
        ela não será duplicada.
        """

        for nome in telas:

            codigo = ModuloService._gerar_codigo_tela(
                modulo.codigo,
                nome,
            )

            tela, _ = Tela.objects.get_or_create(
                modulo=modulo,
                codigo=codigo,
                defaults={
                    "nome": nome,
                    "ativo": True,
                },
            )

            ImplantacaoTela.objects.get_or_create(
                implantacao_modulo=implantacao_modulo,
                tela=tela,
                defaults={
                    "status": StatusTela.PENDENTE,
                },
            )

    @staticmethod
    def _gerar_codigo_tela(
        modulo_codigo,
        nome,
    ):
        """
        Gera um código estável para a tela.
        """

        import re

        nome_normalizado = (
            nome.strip()
            .lower()
        )

        nome_normalizado = re.sub(
            r"[^a-z0-9]+",
            "_",
            nome_normalizado,
        )

        nome_normalizado = (
            nome_normalizado
            .strip("_")
        )

        return f"{modulo_codigo}_{nome_normalizado}"