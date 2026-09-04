# Integração Movidesk

Esta camada é responsável exclusivamente pela comunicação com a API do Movidesk e pela transformação do payload externo em dados do domínio.

## Componentes

- `client.py`: HTTP e tratamento de erros.
- `mapper.py`: transformação do payload.
- `service.py`: orquestração da importação.

O mapeamento definitivo dos campos será implementado após analisarmos um payload real do ticket principal de implantação.
