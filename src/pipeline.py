"""
Orquestrador do pipeline de extração de documentos.

Fluxo:
  arquivo → validação → extração de texto → classificação → parsing → JSON salvo
"""
import json
import logging
from datetime import datetime
from pathlib import Path

from classifier import classify_document
from extractor import extract_text
from parser import parse_document
from validators import compute_file_hash, validate_file

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")


def process_document(file_path: str) -> dict:
    """
    Processa um documento PDF e retorna os dados extraídos.

    Args:
        file_path: Caminho para o arquivo PDF.

    Returns:
        Dict com resultado completo:
        {
            "file": str,
            "doc_type": str,
            "hash": str,
            "num_pages": int,
            "data": dict,       # campos extraídos
            "error": str,       # vazio se sucesso
        }
    """
    result = {
        "file": str(file_path),
        "doc_type": "",
        "hash": "",
        "num_pages": 0,
        "data": {},
        "error": "",
    }

    try:
        # Etapa 1: Validação do arquivo
        path = validate_file(file_path)
        result["file"] = path.name
        result["hash"] = compute_file_hash(path)

        logger.info("Processando: '%s'", path.name)

        # Etapa 2: Extração de texto
        extracted = extract_text(path)
        result["num_pages"] = extracted["num_pages"]

        # Etapa 3: Classificação
        doc_type = classify_document(extracted["full_text"])
        result["doc_type"] = doc_type

        if doc_type == "desconhecido":
            result["error"] = (
                "Tipo de documento não identificado. "
                "Suportamos: Nota Fiscal e Contrato."
            )
            return result

        # Etapa 4: Extração de campos
        data = parse_document(extracted["full_text"], doc_type)
        result["data"] = data

        logger.info(
            "✅ '%s' processado com sucesso | tipo: %s | campos: %d",
            path.name,
            doc_type,
            len(data),
        )

    except (FileNotFoundError, ValueError) as exc:
        result["error"] = str(exc)
        logger.error("Erro de validação em '%s': %s", file_path, exc)

    except RuntimeError as exc:
        result["error"] = str(exc)
        logger.error("Erro de processamento em '%s': %s", file_path, exc)

    except Exception as exc:
        result["error"] = f"Erro inesperado: {str(exc)}"
        logger.error("Erro inesperado em '%s': %s", file_path, exc, exc_info=True)

    return result


def save_result(result: dict) -> str:
    """
    Salva o resultado da extração em JSON.

    Args:
        result: Resultado do process_document.

    Returns:
        Caminho do arquivo salvo.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{result['file'].replace('.pdf', '')}.json"
    filepath = OUTPUT_DIR / filename

    output = {
        "extracted_at": datetime.now().isoformat(),
        "source_file": result["file"],
        "doc_type": result["doc_type"],
        "file_hash": result["hash"],
        "num_pages": result["num_pages"],
        "error": result["error"],
        "data": result["data"],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info("Resultado salvo: %s", filepath)
    return str(filepath)


def process_batch(file_paths: list[str]) -> list[dict]:
    """
    Processa múltiplos documentos em sequência.

    Args:
        file_paths: Lista de caminhos de arquivos PDF.

    Returns:
        Lista de resultados.
    """
    results = []

    for i, file_path in enumerate(file_paths, 1):
        logger.info("Processando %d/%d: %s", i, len(file_paths), file_path)
        result = process_document(file_path)
        if not result["error"]:
            save_result(result)
        results.append(result)

    success = sum(1 for r in results if not r["error"])
    logger.info(
        "Batch concluído: %d/%d com sucesso",
        success,
        len(results),
    )

    return results