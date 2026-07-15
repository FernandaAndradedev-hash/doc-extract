"""
Interface CLI do DocExtract com Rich.
"""
import json
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich import box

from pipeline import process_batch, process_document, save_result

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
console = Console()

DOC_TYPE_LABELS = {
    "nota_fiscal": "📄 Nota Fiscal",
    "contrato": "📋 Contrato",
    "desconhecido": "❓ Desconhecido",
}


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]DocExtract[/bold cyan]\n"
        "[dim]Extração estruturada de documentos PDF — VendaMais[/dim]",
        border_style="cyan",
    ))


def print_result(result: dict):
    """Exibe o resultado da extração de forma visual."""
    label = DOC_TYPE_LABELS.get(result["doc_type"], result["doc_type"])

    if result["error"]:
        console.print(Panel(
            f"[red]{result['error']}[/red]",
            title=f"❌ Erro — {result['file']}",
            border_style="red",
        ))
        return

    # Exibe JSON extraído com syntax highlighting
    json_str = json.dumps(result["data"], ensure_ascii=False, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)

    console.print(Panel(
        syntax,
        title=f"[bold green]{label} — {result['file']}[/bold green]",
        subtitle=f"{result['num_pages']} página(s) | {len(result['data'])} campos",
        border_style="green",
    ))


def print_batch_summary(results: list[dict]):
    """Exibe tabela resumo do processamento em lote."""
    table = Table(title="Resumo do Processamento", box=box.ROUNDED)
    table.add_column("Arquivo", style="bold")
    table.add_column("Tipo", justify="center")
    table.add_column("Páginas", justify="center")
    table.add_column("Campos", justify="center")
    table.add_column("Status", justify="center")

    for r in results:
        label = DOC_TYPE_LABELS.get(r["doc_type"], r["doc_type"])
        status = "[green]✅ OK[/green]" if not r["error"] else "[red]❌ Erro[/red]"
        fields = str(len(r["data"])) if r["data"] else "—"

        table.add_row(
            r["file"],
            label,
            str(r["num_pages"]),
            fields,
            status,
        )

    console.print(table)


def main():
    print_banner()

    args = sys.argv[1:]

    if not args:
        console.print(
            "\n[bold]Uso:[/bold]\n"
            "  python cli.py arquivo.pdf\n"
            "  python cli.py arquivo1.pdf arquivo2.pdf\n"
            "  python cli.py samples/\n"
        )
        return

    # Resolve arquivos
    file_paths = []
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            # Processa todos os PDFs do diretório
            file_paths.extend(str(f) for f in sorted(path.glob("*.pdf")))
        elif path.suffix.lower() == ".pdf":
            file_paths.append(str(path))
        else:
            console.print(f"[yellow]Ignorando '{arg}' — não é um PDF.[/yellow]")

    if not file_paths:
        console.print("[red]Nenhum arquivo PDF encontrado.[/red]")
        return

    console.print(f"\n[dim]Processando {len(file_paths)} arquivo(s)...[/dim]\n")

    if len(file_paths) == 1:
        # Processamento único — exibe resultado detalhado
        result = process_document(file_paths[0])
        if not result["error"]:
            saved = save_result(result)
            print_result(result)
            console.print(f"\n[dim]JSON salvo em: {saved}[/dim]")
        else:
            print_result(result)
    else:
        # Processamento em lote — exibe tabela resumo
        results = process_batch(file_paths)
        print_batch_summary(results)

        success = sum(1 for r in results if not r["error"])
        console.print(
            f"\n[green]{success}[/green] de [bold]{len(results)}[/bold] "
            f"arquivos processados com sucesso."
        )


if __name__ == "__main__":
    main()