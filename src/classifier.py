"""
Classifica o tipo do documento PDF.

Por que classificar antes de extrair?
Cada tipo de documento tem campos diferentes.
Saber o tipo permite usar o prompt correto para extração,
melhorando a precisão dos dados extraídos.

A classificação é feita com base nas primeiras 1.000 chars do texto,
que geralmente contêm o cabeçalho do documento.
"""
import logging
import re

import config

logger = logging.getLogger(__name__)

# Padrões que identificam cada tipo de documento
_PATTERNS = {
    "nota_fiscal": [
        r"nota\s+fiscal\s+eletr[oô]nica",
        r"NF-?e",
        r"DANFE",
        r"chave\s+de\s+acesso",
        r"n[uú]mero\s+da\s+nota",
        r"valor\s+total\s+da\s+nota",
        r"CFOP",
        r"NCM",
        r"ICMS",
    ],
    "contrato": [
        r"contrato\s+de\s+(presta[çc][aã]o|servi[çc]o|fornecimento|locação)",
        r"CONTRATANTE",
        r"CONTRATADA",
        r"cl[aá]usula",
        r"objeto\s+do\s+contrato",
        r"foro\s+(da\s+comarca|competente)",
        r"partes\s+contratantes",
        r"instrumento\s+particular",
    ],
}


def classify_document(text: str) -> str:
    """
    Classifica o tipo do documento com base no texto extraído.

    Usa as primeiras 2.000 chars onde geralmente está o cabeçalho.
    Conta quantos padrões de cada tipo são encontrados e retorna
    o tipo com maior score.

    Args:
        text: Texto extraído do PDF (sanitizado).

    Returns:
        Tipo do documento: "nota_fiscal", "contrato" ou "desconhecido".
    """
    # Analisa apenas o início do documento (mais eficiente)
    sample = text[:2000]

    scores = {}

    for doc_type, patterns in _PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, sample, re.IGNORECASE):
                score += 1
        scores[doc_type] = score

    logger.debug("Scores de classificação: %s", scores)

    # Retorna o tipo com maior score, se suficiente
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    if best_score == 0:
        logger.info("Tipo de documento não identificado.")
        return "desconhecido"

    # Requer pelo menos 2 padrões para classificar com confiança
    if best_score < 2:
        logger.info(
            "Score baixo (%d) para '%s'. Retornando 'desconhecido'.",
            best_score,
            best_type,
        )
        return "desconhecido"

    logger.info(
        "Documento classificado como '%s' (score: %d/%d padrões)",
        best_type,
        best_score,
        len(_PATTERNS[best_type]),
    )

    return best_type