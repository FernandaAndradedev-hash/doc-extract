import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _require(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        print(f"\nERRO: Variável '{key}' não encontrada no .env\n", file=sys.stderr)
        sys.exit(1)
    return value


ANTHROPIC_API_KEY: str = _require("ANTHROPIC_API_KEY")
LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-haiku-4-5")

# Limites de segurança
MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
MAX_PAGES: int = int(os.getenv("MAX_PAGES", "50"))
MAX_TEXT_LENGTH: int = 50_000   # máximo de chars enviados ao LLM

# Extensões permitidas
ALLOWED_EXTENSIONS: frozenset = frozenset({".pdf"})

# Tipos de documento suportados
SUPPORTED_DOC_TYPES = {"nota_fiscal", "contrato", "desconhecido"}

# Campos esperados por tipo de documento
EXPECTED_FIELDS = {
    "nota_fiscal": [
        "numero", "serie", "data_emissao", "chave_acesso",
        "emitente_nome", "emitente_cnpj",
        "destinatario_nome", "destinatario_cnpj",
        "valor_total", "valor_icms", "valor_pis", "valor_cofins",
        "itens",
    ],
    "contrato": [
        "partes", "objeto", "valor", "prazo",
        "data_assinatura", "clausulas_principais", "foro",
    ],
}