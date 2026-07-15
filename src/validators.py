"""
Validação de arquivos PDF e saídas do sistema.

Riscos específicos de sistemas de extração de documentos:
1. Path traversal via nome de arquivo
2. PDFs maliciosos (muito grandes, com scripts embutidos)
3. Prompt injection via conteúdo do documento
4. Vazamento de dados sensíveis na saída
"""
import hashlib
import logging
import re
from pathlib import Path

import config

logger = logging.getLogger(__name__)


# Prompt Injection via conteúdo do documento ────────────────────────────────

# Documentos podem conter instruções escondidas para o LLM
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions?",
    r"you\s+are\s+now\s+(a|an)",
    r"new\s+instructions?\s*:",
    r"system\s+prompt\s*:",
    r"jailbreak",
    r"\[INST\]",
    r"\[SYSTEM\]",
]

_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)


def validate_file(file_path: str | Path) -> Path:
    """
    Valida um arquivo PDF antes do processamento.

    Verificações:
    1. Path traversal — arquivo deve estar em diretório autorizado
    2. Extensão — apenas PDF
    3. Existência e leiturabilidade
    4. Tamanho máximo
    5. Não vazio

    Args:
        file_path: Caminho para o arquivo.

    Returns:
        Path absoluto validado.

    Raises:
        ValueError: Para arquivos inválidos.
        FileNotFoundError: Se não existir.
    """
    path = Path(file_path).resolve()

    # Proteção contra path traversal
    # Permite apenas arquivos dentro do diretório de trabalho
    cwd = Path.cwd().resolve()
    try:
        path.relative_to(cwd)
    except ValueError:
        raise ValueError(
            f"Acesso negado: '{file_path}' está fora do diretório de trabalho."
        )

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: '{path}'")

    if not path.is_file():
        raise ValueError(f"'{path}' não é um arquivo.")

    if path.suffix.lower() not in config.ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Extensão '{path.suffix}' não permitida. "
            f"Apenas PDF é aceito."
        )

    size = path.stat().st_size

    if size == 0:
        raise ValueError(f"Arquivo '{path.name}' está vazio.")

    if size > config.MAX_FILE_SIZE_BYTES:
        size_mb = size / 1024 / 1024
        limit_mb = config.MAX_FILE_SIZE_BYTES / 1024 / 1024
        raise ValueError(
            f"Arquivo muito grande: {size_mb:.1f} MB. "
            f"Limite: {limit_mb:.0f} MB."
        )

    return path


def compute_file_hash(path: Path) -> str:
    """SHA-256 do arquivo para identificação única."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def sanitize_text_for_llm(text: str) -> str:
    """
    Sanitiza texto extraído do PDF antes de enviar ao LLM.

    Remove caracteres de controle e detecta tentativas de injection
    embutidas no documento.

    Args:
        text: Texto bruto extraído do PDF.

    Returns:
        Texto sanitizado. Marca trechos suspeitos em vez de remover,
        para não perder informação legítima.
    """
    if not text:
        return ""

    # Remove caracteres de controle (exceto \n e \t)
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normaliza múltiplas quebras de linha
    clean = re.sub(r"\n{4,}", "\n\n\n", clean)

    # Detecta e marca injection embutida
    if _INJECTION_RE.search(clean):
        logger.warning("Possível prompt injection embutida no documento.")
        # Substitui os trechos suspeitos por marcador
        clean = _INJECTION_RE.sub("[CONTEÚDO REMOVIDO]", clean)

    # Trunca se muito longo para evitar custo excessivo de tokens
    if len(clean) > config.MAX_TEXT_LENGTH:
        logger.warning(
            "Texto truncado: %d → %d chars", len(clean), config.MAX_TEXT_LENGTH
        )
        clean = clean[:config.MAX_TEXT_LENGTH] + "\n\n[DOCUMENTO TRUNCADO]"

    return clean.strip()


def validate_extracted_json(data: dict, doc_type: str) -> tuple[dict, list[str]]:
    """
    Valida o JSON extraído pelo LLM.

    Verifica se os campos esperados estão presentes e
    se os valores não contêm dados suspeitos.

    Args:
        data: Dict extraído pelo LLM.
        doc_type: Tipo do documento.

    Returns:
        Tupla (data_validado, lista_de_avisos).
    """
    warnings = []
    expected = config.EXPECTED_FIELDS.get(doc_type, [])

    for field in expected:
        if field not in data:
            warnings.append(f"Campo esperado ausente: '{field}'")
        elif data[field] is None or data[field] == "":
            warnings.append(f"Campo vazio: '{field}'")

    # Verifica se algum valor parece ser vazamento de system prompt
    leak_patterns = [r"system\s+prompt", r"sk-ant-", r"ANTHROPIC_API_KEY"]
    for key, value in data.items():
        if isinstance(value, str):
            for pattern in leak_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    logger.warning("Possível vazamento em campo '%s'.", key)
                    data[key] = "[VALOR REMOVIDO POR SEGURANÇA]"

    return data, warnings