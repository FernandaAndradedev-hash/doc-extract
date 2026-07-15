import os
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-fake")

import pytest
from unittest.mock import MagicMock, patch


class TestExtractor:

    @patch("extractor.PdfReader")
    def test_extrai_texto_simples(self, mock_reader_class, tmp_path):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Nota Fiscal Eletrônica\nValor: R$ 1.000,00"

        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader

        pdf = tmp_path / "teste.pdf"
        pdf.write_bytes(b"%PDF conteudo")

        from extractor import extract_text
        result = extract_text(pdf)

        assert result["num_pages"] == 1
        assert "Nota Fiscal" in result["full_text"]
        assert result["is_encrypted"] is False

    @patch("extractor.PdfReader")
    def test_pdf_criptografado_lanca_erro(self, mock_reader_class, tmp_path):
        mock_reader = MagicMock()
        mock_reader.is_encrypted = True
        mock_reader_class.return_value = mock_reader

        pdf = tmp_path / "criptografado.pdf"
        pdf.write_bytes(b"%PDF conteudo")

        from extractor import extract_text
        with pytest.raises(ValueError, match="criptografado"):
            extract_text(pdf)

    @patch("extractor.PdfReader")
    def test_pdf_sem_texto_lanca_erro(self, mock_reader_class, tmp_path):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""

        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader

        pdf = tmp_path / "sem_texto.pdf"
        pdf.write_bytes(b"%PDF conteudo")

        from extractor import extract_text
        with pytest.raises(ValueError, match="texto"):
            extract_text(pdf)


class TestClassifier:

    def test_classifica_nota_fiscal(self):
        from classifier import classify_document
        text = """
        NOTA FISCAL ELETRÔNICA - NF-e
        Chave de Acesso: 1234 5678 9012
        ICMS: R$ 120,00
        Valor Total da Nota: R$ 1.000,00
        CFOP: 5102
        """
        result = classify_document(text)
        assert result == "nota_fiscal"

    def test_classifica_contrato(self):
        from classifier import classify_document
        text = """
        CONTRATO DE PRESTAÇÃO DE SERVIÇOS
        CONTRATANTE: Empresa A
        CONTRATADA: Empresa B
        Cláusula 1: Objeto do contrato
        Foro da Comarca de São Paulo
        Partes Contratantes
        """
        result = classify_document(text)
        assert result == "contrato"

    def test_documento_desconhecido(self):
        from classifier import classify_document
        text = "Este é um documento genérico sem identificação clara."
        result = classify_document(text)
        assert result == "desconhecido"