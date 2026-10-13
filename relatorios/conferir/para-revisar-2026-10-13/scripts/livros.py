"""Onde esta cada livro da conferencia (so leitura) e quantas folhas tem."""
import glob
import sys
from pathlib import Path

HD = Path(r"D:\Livros para editar")
ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")


def _um(pasta, padrao):
    achados = sorted(glob.glob(str(pasta / "**" / padrao), recursive=True))
    return achados[0] if achados else None


LIVROS = {
    "antiphonal": str(HD / "Antiphonal 1547.pdf"),
    "egenloff": str(HD / "Egenloff15271880ModelbuchWHZ_231103_053749.pdf"),
    "camoes": str(HD / "HISTÓRIA" / "Luiz de Camões levantando o seu monumento ou A Historia de Portugal justificada pelos Lusiadas.pdf"),
    "rariora": str(HD / "Rariora musei besleriani quae olim basilius et michael rupertus besleri.pdf"),
    "gladstone": str(HD / "Gladstone_Chaves_de_Melo_Novo_Manual_de_Análise_Sintática_1954.pdf"),
    "graduale": _um(ACERVO, "Graduale*.pdf"),
    "cursus": _um(ACERVO, "Cursus philosophicus*.pdf"),
    "opusmajus": _um(ACERVO, "*pus*ajus*.pdf") or _um(ACERVO, "*Opus*.pdf"),
    "palatino": _um(ACERVO, "Giovambattista Palatino*.pdf"),
    "antiphon": _um(ACERVO, "Antiphon_25.pdf"),
}

if __name__ == "__main__":
    import fitz
    sys.stdout.reconfigure(encoding="utf-8")
    for nome, caminho in LIVROS.items():
        if not caminho or not Path(caminho).exists():
            print(nome, "NAO ACHEI", caminho)
            continue
        d = fitz.open(caminho)
        print(f"{nome:11s} {len(d):4d} folhas  {Path(caminho).stat().st_size / 1e6:7.1f} MB  {caminho}")
        d.close()
