import os
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-fake")

import json
from unittest.mock import MagicMock, patch
import pytest


class TestParser:

    @patch("parser._client")
    def test_extrai_nota_fiscal(self, mock_client):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps({
            "numero": "001",
            "serie": "1",
            "data_emissao": "15/03/2024",
            "chave_acesso": "1234567890",
            "emitente_nome": "VendaMais Ltda",
            "emitente_cnpj": "12.345.678/0001-90",
            "destinatario_nome": "Cliente S.A.",
            "destinatario_cnpj": "98.765.432/0001-10",
            "itens": [{"descricao": "Produto A", "quantidade": "2", "valor_unitario": "R$ 100,00", "valor_total": "R$ 200,00"}],
            "valor_produtos": "R$ 200,00",
            "valor_icms": "R$ 24,00",
            "valor_pis": None,
            "valor_cofins": None,
            "valor_total": "R$ 200,00",
        }))]
        mock_client.messages.create.return_value = mock_response

        from parser import parse_document
        result = parse_document("texto da NF aqui", "nota_fiscal")

        assert result["numero"] == "001"
        assert result["emitente_nome"] == "VendaMais Ltda"
        assert result["_doc_type"] == "nota_fiscal"

    @patch("parser._client")
    def test_json_invalido_lanca_erro(self, mock_client):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="isso não é json")]
        mock_client.messages.create.return_value = mock_response

        from parser import parse_document
        with pytest.raises(RuntimeError, match="Falha ao parsear"):
            parse_document("texto qualquer", "nota_fiscal")

    def test_tipo_nao_suportado_lanca_erro(self):
        from parser import parse_document
        with pytest.raises(ValueError, match="não suportado"):
            parse_document("texto", "boleto")