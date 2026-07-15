"""
Extrai texto de arquivos PDF usando pypdf.

pypdf é a biblioteca padrão para extração de texto de PDFs em Python.
Funciona para PDFs com texto selecionável (não escaneados).

Para PDFs escaneados (imagens), seria necessário OCR (Tesseract ou similar).
Este projeto foca em PDFs de texto, que é o caso da maioria das NFs eletrônicas.
"""
import logging
from pathlib import Path

from pypdf import PdfReader

import config
from validators import sanitize_text_for_llm

logger = logging.getLogger(__name__)


def extract_text(pdf_path: Path) -> dict:
    """
    Extrai texto de um PDF página por página.

    Args:
        pdf_path: Caminho do PDF (já validado).

    Returns:
        Dict com:
        {
            "full_text": str,         # texto completo concatenado
            "pages": list[str],       # texto por página
            "num_pages": int,
            "is_encrypted": bool,
        }

    Raises:
        ValueError: Se PDF estiver criptografado ou não tiver texto.
        RuntimeError: Para erros de leitura.
    """
    try:
        reader = PdfReader(str(pdf_path))

        if reader.is_encrypted:
            raise ValueError(
                f"PDF '{pdf_path.name}' está criptografado. "
                "Forneça a senha ou use um PDF sem senha."
            )

        num_pages = len(reader.pages)

        if num_pages > config.MAX_PAGES:
            raise ValueError(
                f"PDF com {num_pages} páginas excede o limite de {config.MAX_PAGES} páginas."
            )

        logger.info("Extraindo texto de '%s' (%d páginas)...", pdf_path.name, num_pages)

        pages_text = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                pages_text.append(page_text)
            except Exception as exc:
                logger.warning("Erro ao extrair página %d: %s", i + 1, exc)
                pages_text.append("")

        full_text = "\n\n".join(
            f"--- Página {i+1} ---\n{text}"
            for i, text in enumerate(pages_text)
            if text.strip()
        )

        if not full_text.strip():
            raise ValueError(
                f"Nenhum texto extraído de '{pdf_path.name}'. "
                "O PDF pode ser baseado em imagens (escaneado). "
                "Este sistema processa apenas PDFs com texto selecionável."
            )

        # Sanitiza antes de retornar
        clean_text = sanitize_text_for_llm(full_text)

        logger.info(
            "Texto extraído: %d chars de %d páginas",
            len(clean_text),
            num_pages,
        )

        return {
            "full_text": clean_text,
            "pages": pages_text,
            "num_pages": num_pages,
            "is_encrypted": False,
        }

    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        raise RuntimeError(f"Erro ao ler '{pdf_path.name}': {str(exc)}")