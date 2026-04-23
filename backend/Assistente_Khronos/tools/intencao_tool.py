from langchain_core.tools import tool
import re
import logging
from .rag_tool import rag_url_resposta_vetorial
from .web_tool import procura_web
from .file_tool import ler_documentos
from .tool_mapa_semantico import plotar_mapa_semantico
from .fiscal import fiscal_router

logger = logging.getLogger(__name__)

@tool
def executar_intencao(
    mensagem: str,
    banco: str = "default",
    slug: str = None,
    empresa_id: str = "1",
    filial_id: str = "1"
) -> str:
    """
    Executa a intenção detectada roteando para a tool adequada.

    MODIFICAÇÃO CRÍTICA: NÃO chama mais faiss_context_qa ou faiss_condicional_qa.
    O contexto FAISS já foi fornecido pela view ANTES do agente!

    Regras principais:
    - Cadastro: "produto <nome> ncm <codigo>" -> cadastrar_produtos
    - Saldo: contém "saldo|estoque|quantidade" e "codigo|produto <número>" -> consultar_saldo
    - Pergunta de negócio (vendas, pedidos, clientes, etc.) -> consulta_inteligente_prime
    - Fiscal: "nota fiscal|emissão|devolução|CFOP|CST|impostos|rejeições SEFAZ|erro fiscal" -> fiscal_router
    
    - Histórico de pedidos do cliente: "meu histórico de pedidos" -> historico_de_pedidos_cliente
    - Pergunta sobre URL específica -> rag_url_resposta_vetorial
    - Pesquisa na web (google, web, internet) -> procura_web
    - Leitura de arquivo local (caminho/arquivo) -> ler_documentos
    - Visualização do cérebro semântico (mapa semântico, pca/tsne) -> plotar_mapa_semantico
    - Perguntas gerais/documentação -> CONTEXTO JÁ FORNECIDO, retorna orientação
    """
    msg_lower = mensagem.lower()
    


    def normalizar_data_token(dia:str, mes_nome:str, ano:str=None):
        try:
            d = int(dia)
            m = mes_pt_para_num(mes_nome) if mes_nome else None
            y = int(ano) if ano else __import__('datetime').datetime.now().year
            if not m:
                m = __import__('datetime').datetime.now().month
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            return None

    # ========== INSTRUÇÕES DE USO ==========
    if re.search(r"(?i)como(\s+posso|\s+fa[cç]o)?\s+cadastrar", msg_lower):
        return (
            "Para cadastrar produto, envie: 'produto <nome> ncm <codigo>'.\n"
            "Exemplo: produto Mesa de Jantar ncm 94036000"
        )
    
    # ========== VISUALIZAÇÃO — MAPA SEMÂNTICO ==========
    if re.search(r"(?i)(mapa\s+sem[aâ]ntico|c[ée]rebro|pca|tsne)", msg_lower):
        metodo = "tsne" if "tsne" in msg_lower else "pca"
        return plotar_mapa_semantico.func(pergunta=mensagem, metodo=metodo)

    # ========== LEITURA DE ARQUIVO LOCAL ==========
    if re.search(r"(?i)(ler|abrir)\s+(arquivo|documento)", msg_lower):
        m_path = re.search(r"(?i)arquivo\s+([\w:\\\/\.\-]+)|['\"]([^'\"]+)['\"]", mensagem)
        file_path = None
        if m_path:
            file_path = m_path.group(1) or m_path.group(2)
        if file_path:
            return ler_documentos.func(file_path=file_path)
        else:
            return "Informe o caminho do arquivo (ex.: C:\\path\\arquivo.txt)"

    # ========== RAG — URL ESPECÍFICA ==========
    # Se menciona URL/link específico, usa RAG vetorial
    if re.search(r"(?i)(http|www\.|\.com|\.br|link\s+)", msg_lower):
        return rag_url_resposta_vetorial.func(pergunta=mensagem)

    # ========== PESQUISA WEB ==========
    if re.search(r"(?i)(pesquisar|buscar|google|web|internet)", msg_lower):
        # Evita uso indevido para dados internos
        termos_internos = [
            "estoque", "saldo", "pedido", "pedidos", "venda", "vendas",
            "produto", "produtos", "nota fiscal", "nf", "cliente", "fornecedor"
        ]
        if any(t in msg_lower for t in termos_internos):
            pass  # Cai para consulta de negócio
        else:
            return procura_web.func(query=mensagem)

    # ========== CONSULTAS DE NEGÓCIO / BANCO ==========
    termos_negocio = [
        "pedido", "pedidos", "venda", "vendas", "cliente", "clientes",
        "nota fiscal", "nf", "faturamento", "receita",
        "despesa", "comiss[õo]es"
    ]
    # Evita "como..." para DB
    if not re.search(r"(?i)\bcomo\b", msg_lower):
        if any(re.search(t, msg_lower) for t in termos_negocio):
            if re.search(r"(?i)hist[óo]rico|relat[óo]rio\s+de\s+pedidos|pedidos\s+por\s+cliente", msg_lower):
                pass
            else:
                return consulta_inteligente_prime.func(pergunta=mensagem, slug=real_banco)

    # ========== PERGUNTAS GERAIS/DOCUMENTAÇÃO ==========
    # ❌ REMOVIDO: Chamadas para faiss_context_qa e faiss_condicional_qa
    # ✅ NOVO: Informa que o contexto já foi fornecido
    if "?" in msg_lower or re.search(r"(?i)(como|o\s+que|qual|quais|quando|onde|instru[cç][aã]o|tutorial)", msg_lower):
        return (
            "📎 O contexto relevante já foi fornecido no início da conversa. "
            "Responda com base nesse contexto ou peça esclarecimentos específicos."
        )

    # ========== NENHUMA INTENÇÃO CLARA ==========
    logger.warning(f"[KHRONOS_CHAT] Nenhuma intenção identificada {log_ctx}")
    return (
        "Não identifiquei a intenção. Exemplos:\n"
        "- Pesquisa: 'buscar na web ...'"
    )

