"""Mede quanto a tela de trabalho leva para ABRIR um livro grande (etapa 2 da obra de 26/10/2026).

Pergunta: montar todas as ferramentas sempre (D-001) deixa o abrir mais lento? Mede só
`TelaConferir.carregar` (a montagem das ferramentas, da tira e do primeiro desenho da tela), num
livro de verdade do acervo (Marial, 214 MB, só lido), com quatro combinações de caixinhas: nenhuma,
só "Limpar", tudo e "Dividir + Endireitar". Cada combinação 5 vezes; vale a mediana. A análise do
livro não entra (não muda nesta etapa): o projeto é montado com uma página por folha.

Uso (na worktree):  .venv\\Scripts\\python.exe relatorios\\obra-etapa2\\roteiro\\medir_abrir.py <rotulo>
Grava o resultado em relatorios/obra-etapa2/velocidade-<rotulo>.txt. Dados e TEMP numa pasta de
saida_teste/ (fora do git), nunca na pasta de dados do Samuel.
"""
from __future__ import annotations

import os
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
TRAB = RAIZ / "saida_teste" / "obra-etapa2" / "medir"
(TRAB / "dados").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(TRAB / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(TRAB)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

LIVRO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE"
             r"\Marial de sermoens - Frei Balthasar Paez. (1).pdf")

COMBINACOES = {
    "nenhuma": dict(dividir_folhas=False, cortar_bordas=False, endireitar=False, limpar=False,
                    detectar_regioes=False),
    "so_limpar": dict(dividir_folhas=False, cortar_bordas=False, endireitar=False, limpar=True,
                      detectar_regioes=False),
    "tudo": dict(dividir_folhas=True, cortar_bordas=True, endireitar=True, limpar=True,
                 detectar_regioes=True),
    "dividir_endireitar": dict(dividir_folhas=True, cortar_bordas=False, endireitar=True,
                               limpar=False, detectar_regioes=False),
}
VEZES = 5


def main() -> None:
    import fitz
    from PySide6.QtWidgets import QApplication

    from historico_acoes import HistoricoAcoes
    from modelos import ConfigFolha, ConfigPagina, Projeto
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    rotulo = sys.argv[1] if len(sys.argv) > 1 else "agora"
    app = QApplication.instance() or QApplication([])
    with fitz.open(str(LIVRO)) as doc:
        total = doc.page_count
    tela = TelaConferir()
    tela.resize(1280, 657)
    tela.show()
    linhas = [f"livro: {LIVRO.name} ({total} folhas); {VEZES} vezes cada; mediana em segundos"]
    for nome, opcoes in COMBINACOES.items():
        tempos = []
        for _vez in range(VEZES):
            projeto = Projeto(caminho_entrada=str(LIVRO), nome=LIVRO.stem)
            for campo, valor in opcoes.items():
                setattr(projeto, campo, valor)
            projeto.folhas = [ConfigFolha(indice=i) for i in range(total)]
            projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(total)]
            previas = GerenciadorPrevias(str(LIVRO), projeto, tela)
            acoes = HistoricoAcoes(None)
            app.processEvents()
            inicio = time.perf_counter()
            tela.carregar(projeto, acoes, previas)
            app.processEvents()
            tempos.append(time.perf_counter() - inicio)
            tela.tira.parar()
            previas.parar()
            app.processEvents()
        linha = (f"{nome:20s} mediana {statistics.median(tempos):.3f} s  "
                 f"(todas: {', '.join(f'{t:.3f}' for t in tempos)})")
        print(linha, flush=True)
        linhas.append(linha)
    destino = RAIZ / "relatorios" / "obra-etapa2" / f"velocidade-{rotulo}.txt"
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("gravado em", destino)


if __name__ == "__main__":
    main()
