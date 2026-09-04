from implantacao.services.template_service import TemplateService


class TemplateResolver:
    TEMPLATE_FALLBACK = "padrao"

    @staticmethod
    def resolver(*, template_codigo=None, contexto=None):
        """
        Resolve o template que será utilizado na implantação.

        Prioridade:
        1. Template informado explicitamente.
        2. Template identificado pelo contexto.
        3. Template padrão como fallback.
        """

        if template_codigo:
            TemplateService.obter(template_codigo)
            return template_codigo

        template_detectado = TemplateResolver._resolver_por_contexto(
            contexto
        )

        if template_detectado:
            TemplateService.obter(template_detectado)
            return template_detectado

        return TemplateResolver.TEMPLATE_FALLBACK

    @staticmethod
    def _resolver_por_contexto(contexto):
        """
        Futuramente será responsável por identificar
        o template através de dados externos, como Movidesk.

        Por enquanto, não existe regra automática.
        """
        return None