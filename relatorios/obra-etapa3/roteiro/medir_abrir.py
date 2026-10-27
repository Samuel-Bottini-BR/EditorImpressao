"""Mede quanto o livro leva para chegar na área de trabalho (etapa 3 da obra de 26/10/2026).

Pergunta: abrir direto na área de trabalho (D-002) deixou o abrir mais rápido? Mede, na janela
de verdade (sem tela: offscreen), num livro grande do acervo (Marial, só lido):

- livro novo: do `abrir_livro` até a área de trabalho pronta. No código ANTIGO isso é abrir +
  clicar "Conferir" na tela "O que fazer" (a análise do livro inteiro) com as caixinhas de
  fábrica; no NOVO o livro abre direto (e a medida por trás, D-284, roda depois - o tempo dela
  vai numa coluna à parte, porque a pessoa já está trabalhando enquanto ela roda).
- livro salvo: "continuar" um livro com trabalho salvo. No antigo, a análise rodava de novo; no
  novo, o trabalho salvo volta como está.

Uso: python medir_abrir.py <rotulo> <raiz do codigo>   (raiz = a worktree a medir)
Grava em relatorios/obra-etapa3/velocidade-<rotulo>.txt (desta worktree). Dados e TEMP em
saida_teste/obra-etapa3/medir-<rotulo> (fora do git), nunca na pasta de dados do Samuel.
"""
from __future__ import annotations

import os
import shutil
import statistics
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parents[3]
ROTULO = sys.argv[1] if len(sys.argv) > 1 else "agora"
CODIGO = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else AQUI
TRAB = AQUI / "saida_teste" / "obra-etapa3" / f"medir-{ROTULO}"
TRAB.mkdir(parents=True, exist_ok=True)
os.environ["TEMP"] = os.environ["TMP"] = str(TRAB)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(CODIGO))
os.chdir(CODIGO)

LIVRO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE"
             r"\Marial de sermoens - Frei Balthasar Paez. (1).pdf")
VEZES = 3


def _esperar(app, segundos, condicao) -> bool:
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        app.processEvents()
        if condicao():
            return True
        time.sleep(0.01)
    return condicao()


def main() -> None:
    linhas = [f"codigo: {CODIGO}", f"livro: {LIVRO.name}; {VEZES} vezes; mediana em segundos"]
    novo, salvo, por_tras = [], [], []
    for vez in range(VEZES):
        dados = TRAB / f"dados-{vez}"
        shutil.rmtree(dados, ignore_errors=True)
        dados.mkdir(parents=True)
        os.environ["LOCALAPPDATA"] = str(dados)
        t_novo, t_tras, t_salvo = _uma_vez()
        novo.append(t_novo)
        salvo.append(t_salvo)
        if t_tras is not None:
            por_tras.append(t_tras)
        print(f"vez {vez + 1}: livro novo {t_novo:.2f} s; medida por tras "
              f"{'-' if t_tras is None else f'{t_tras:.2f} s'}; livro salvo {t_salvo:.2f} s", flush=True)

    def _l(nome, ts):
        return f"{nome:34s} mediana {statistics.median(ts):7.2f} s  (todas: {', '.join(f'{t:.2f}' for t in ts)})"

    linhas.append(_l("livro novo ate a area de trabalho", novo))
    if por_tras:
        linhas.append(_l("medida por tras (depois de abrir)", por_tras))
    linhas.append(_l("livro salvo (continuar)", salvo))
    texto = "\n".join(linhas) + "\n"
    print(texto)
    destino = AQUI / "relatorios" / "obra-etapa3" / f"velocidade-{ROTULO}.txt"
    destino.write_text(texto, encoding="utf-8")
    print("gravado em", destino)


def _uma_vez():
    import projetos
    from PySide6.QtWidgets import QApplication

    from ui.janela_principal import CONFERIR, JanelaPrincipal

    app = QApplication.instance() or QApplication([])
    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    janela.show()
    app.processEvents()

    inicio = time.perf_counter()
    janela.abrir_livro(str(LIVRO))
    antigo = hasattr(janela, "tela_opcoes") and janela.telas.currentIndex() != CONFERIR
    if antigo:
        janela.analisar()                      # o "Conferir" com as caixinhas de fabrica
    assert _esperar(app, 900, lambda: janela.telas.currentIndex() == CONFERIR
                    and getattr(janela, "tarefa", None) is None or (
                        janela.telas.currentIndex() == CONFERIR
                        and not janela.tarefa.isRunning())), "nao chegou a area de trabalho"
    t_novo = time.perf_counter() - inicio
    t_tras = None
    if not antigo:
        _esperar(app, 900, lambda: getattr(janela, "medida_ao_abrir", None) is None
                 or not janela.medida_ao_abrir.isRunning())
        t_tras = time.perf_counter() - inicio - t_novo
    _esperar(app, 0.5, lambda: False)

    resumo = janela.resumo
    janela._salvar_agora()
    projetos.esperar_gravacoes(30)
    janela.close()
    app.processEvents()

    outra = JanelaPrincipal()
    outra.resize(1280, 657)
    outra.show()
    app.processEvents()
    inicio = time.perf_counter()
    outra._continuar_projeto(resumo)
    assert _esperar(app, 900, lambda: outra.telas.currentIndex() == CONFERIR and (
        getattr(outra, "tarefa", None) is None or not outra.tarefa.isRunning())), "nao voltou"
    t_salvo = time.perf_counter() - inicio
    outra._relogio_de_salvar.stop() if hasattr(outra, "_relogio_de_salvar") else None
    outra.close()
    app.processEvents()
    return t_novo, t_tras, t_salvo


if __name__ == "__main__":
    main()
