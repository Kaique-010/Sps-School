from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configurações do aplicativo"""
    # Caminhos dos arquivos (absolutos, relativos ao pacote Assistente_Khronos)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    CAMINHO_FAISS: str = str(BASE_DIR / "faiss" / "faiss_full_rag.index")
    EMBED_DIM: int = 1536  # text-embedding-3-small
    # Configurações da API
    API_KEY: str = os.getenv("OPENAI_API_KEY")
    # Adicione outras configurações conforme necessário

settings = Settings()
