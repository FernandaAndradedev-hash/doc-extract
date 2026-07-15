"""
Cria PDFs fictícios para demonstração do DocExtract.
Requer: pip install reportlab
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pathlib import Path

def create_sample_nf():
    """Cria uma NF fictícia em PDF."""
    path = "samples/nf_exemplo_001.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "NOTA FISCAL ELETRÔNICA - NF-e")

    c.setFont("Helvetica", 10)
    dados = [
        ("Número:", "000.001"),
        ("Série:", "1"),
        ("Data de Emissão:", "15/03/2024"),
        ("Chave de Acesso:", "3524 0312 3456 7890 1234 5678 9012 3456 7890 1234 56"),
        ("", ""),
        ("EMITENTE", ""),
        ("Razão Social:", "VendaMais Comércio Eletrônico Ltda"),
        ("CNPJ:", "12.345.678/0001-90"),
        ("Endereço:", "Rua das Flores, 100 - São Paulo/SP"),
        ("", ""),
        ("DESTINATÁRIO", ""),
        ("Razão Social:", "Distribuidora Rápida Ltda"),
        ("CNPJ:", "98.765.432/0001-10"),
        ("Endereço:", "Av. Paulista, 500 - São Paulo/SP"),
        ("", ""),
        ("PRODUTOS", ""),
        ("001 - Smartphone XR Pro 128GB", "R$ 2.499,00 x 2 = R$ 4.998,00"),
        ("002 - Fone Bluetooth Premium", "R$ 399,00 x 5 = R$ 1.995,00"),
        ("", ""),
        ("TOTAIS", ""),
        ("Valor dos Produtos:", "R$ 6.993,00"),
        ("ICMS (12%):", "R$ 839,16"),
        ("PIS (0,65%):", "R$ 45,45"),
        ("COFINS (3%):", "R$ 209,79"),
        ("VALOR TOTAL DA NOTA:", "R$ 6.993,00"),
    ]

    y = height - 100
    for label, value in dados:
        if label == "EMITENTE" or label == "DESTINATÁRIO" or label == "PRODUTOS" or label == "TOTAIS":
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, label)
        else:
            c.setFont("Helvetica", 10)
            c.drawString(50, y, label)
            c.drawString(200, y, value)
        y -= 18

    c.save()
    print(f"✅ Criado: {path}")


def create_sample_contract():
    """Cria um contrato fictício em PDF."""
    path = "samples/contrato_exemplo_001.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS")

    c.setFont("Helvetica", 10)
    conteudo = [
        "",
        "PARTES:",
        "CONTRATANTE: VendaMais Comércio Eletrônico Ltda",
        "CNPJ: 12.345.678/0001-90",
        "Representada por: João Silva, Diretor Comercial",
        "",
        "CONTRATADA: Nexus Consultoria Empresarial Ltda",
        "CNPJ: 11.222.333/0001-44",
        "Representada por: Maria Santos, Sócia-Diretora",
        "",
        "OBJETO: Prestação de serviços de consultoria em gestão de",
        "processos logísticos e reestruturação do departamento de compras.",
        "",
        "VALOR: R$ 45.000,00 (quarenta e cinco mil reais)",
        "Pagamento: 3 parcelas mensais de R$ 15.000,00",
        "",
        "PRAZO: 90 (noventa) dias corridos a partir da assinatura",
        "",
        "DATA DE ASSINATURA: 01/03/2024",
        "",
        "CLÁUSULAS PRINCIPAIS:",
        "1. A CONTRATADA manterá sigilo sobre todas as informações",
        "   confidenciais da CONTRATANTE.",
        "2. Os relatórios serão entregues quinzenalmente.",
        "3. Rescisão com aviso prévio de 30 dias.",
        "",
        "FORO: Comarca de São Paulo/SP",
    ]

    y = height - 90
    for linha in conteudo:
        c.drawString(50, y, linha)
        y -= 16

    c.save()
    print(f"✅ Criado: {path}")


if __name__ == "__main__":
    Path("samples").mkdir(exist_ok=True)
    create_sample_nf()
    create_sample_contract()
    print("\nPDFs de exemplo criados em samples/")