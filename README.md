# DocExtract — Extração Estruturada de Documentos
 
> Sistema que lê PDFs de Notas Fiscais e contratos e extrai os dados
> automaticamente em JSON usando IA. Desenvolvido para a VendaMais E-commerce.

---
 
## Funcionalidades
 
- Extrai texto de PDFs com texto selecionável
- Classifica automaticamente: Nota Fiscal ou Contrato
- Extrai campos estruturados via Claude (JSON)
- Proteção contra path traversal e prompt injection via PDF
- Processamento individual ou em lote
- Testes unitários com cobertura completa
 
---
 
## Stack
 
| Camada | Tecnologia |
|--------|-----------|
| Extração de PDF | pypdf |
| Classificação | Regex + heurística |
| Extração de campos | Anthropic Claude Haiku |
| Interface | Rich (CLI) |
 
---
 
## Como rodar
 
```bash
git clone https://github.com/FernandaAndradedev-hash/doc-extract
cd doc-extract
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Preencha ANTHROPIC_API_KEY no .env!
 
# Criar PDFs de exemplo:
pip install reportlab
python create_samples.py
 
# Processar um arquivo:
python src/cli.py samples/nf_exemplo_001.pdf
 
# Processar pasta inteira:
python src/cli.py samples/
```
 
---
 
## Testes
 
```bash
pytest tests/ -v
```
 
---
 
## Estrutura
 
````
doc-extract/
├── src/
│   ├── config.py        # Configurações
│   ├── validators.py    # Segurança e validação
│   ├── extractor.py     # Extração de texto do PDF
│   ├── classifier.py    # Identificação do tipo
│   ├── parser.py        # Extração de campos com Claude
│   ├── pipeline.py      # Orquestrador
│   └── cli.py           # Interface CLI
├── samples/             # PDFs de exemplo
├── output/              # JSONs extraídos
└── tests/
````
## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.