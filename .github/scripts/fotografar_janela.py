"""Abre o programa de verdade NA TELA do Windows do GitHub e fotografa a janela.

Usado pelo job "janela" do .github/workflows/testes-windows.yml. Nao e parte do
programa: nada aqui e importado por core/, ui/ ou tests/.

    python .github/scripts/fotografar_janela.py --saida prints

Adaptado do roteiro abrir_e_fotografar.py que a gerente usou em 08/10/2026 na
pasta principal (saida_teste/abrir-programa, fora do git), com duas diferencas:
  - aqui o Qt desenha NA TELA de verdade (plataforma normal "windows", nunca
    "offscreen"): a maquina do GitHub e descartavel, nao ha tela do Samuel para
    atrapalhar; e o que se quer ver e justamente a janela real;
  - cada momento sai em DOIS prints: a janela (janela.grab(), o que o Qt
    desenhou) e a tela inteira (QScreen.grabWindow(0), o que o Windows mostra,
    com borda e barra de titulo).

O que fotografa:
  01..03  a tela inicial nos tres temas (escuro, cinza, claro), trocados pelo
          menu Ver > Tema, como o Kaique trocaria;
  04      a tela "O que fazer" com um livro sintetico de folhas duplas (cinza);
  05      a tela de conferir depois da analise (cinza);
  06..07  a tela de conferir com a ferramenta Cortar (antiga aba Bordas) e com
          Endireitar escolhidas, com a janela maximizada;
  08..09  as mesmas duas com a janela em 1280x657 (pedido da gerente em
          09/10/2026), para ver se as filas de botoes cabem.
  O livro sintetico tem folhas duplas e "Dividir folhas ao meio" e marcado
  antes de analisar (desde 09/10/2026), como o Kaique faria com esse livro.
  Funciona com as abas (fase-1) e sem elas (layout etapa 2, trilha de
  ferramentas): ver escolher_ferramenta_da_pagina.
Caixas de aviso que aparecerem sao fotografadas (aviso-N.png) e respondidas no
primeiro botao, para o roteiro nao parar esperando clique.

A pasta de dados (LOCALAPPDATA) e uma pasta propria, dentro de --saida, apagada
a cada rodada. Grava tambem roteiro.txt com o tamanho da tela, o tema medido em
cada passo e os avisos; e o erros.log da rodada, se existir.

Seguro mudar: os passos fotografados, os tempos de espera, o tamanho da janela.
Arriscado: tirar a pasta de dados propria (a maquina do GitHub nao tem dado
real, mas o roteiro tambem roda num PC e la gravaria na pasta de verdade);
trocar o vigia das caixas por esperas fixas (uma caixa modal trava o roteiro
ate o limite do job).
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
import traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def main() -> int:
    """Abre a janela, percorre os passos e grava os prints. Devolve 1 se algum
    passo deu erro (o erro vai para roteiro.txt e o roteiro segue)."""
    p = argparse.ArgumentParser()
    p.add_argument("--saida", default="prints")
    a = p.parse_args()
    saida = Path(a.saida).resolve()
    if saida.exists():
        shutil.rmtree(saida)
    saida.mkdir(parents=True)
    dados = saida / "_dados"
    dados.mkdir()
    os.environ["LOCALAPPDATA"] = str(dados)
    os.environ.pop("QT_QPA_PLATFORM", None)          # tela de verdade
    sys.path.insert(0, str(RAIZ))
    os.chdir(RAIZ)

    import fitz
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QMessageBox

    linhas: list[str] = []
    erros = 0

    def anotar(texto: str) -> None:
        print(texto, flush=True)
        linhas.append(texto)

    app = QApplication(sys.argv)
    from ui import estilo
    from ui.janela_principal import JanelaPrincipal

    tela = app.primaryScreen()
    geo = tela.geometry()
    anotar(f"programa testado: {os.environ.get('TESTADO_RAMO', '?')} {os.environ.get('TESTADO_SHA', '?')}")
    anotar(f"plataforma do Qt: {app.platformName()}")
    anotar(f"tela: {geo.width()}x{geo.height()} (escala {tela.devicePixelRatio()}, "
           f"{tela.logicalDotsPerInch():.0f} dpi logicos)")

    def esperar(segundos: float) -> None:
        fim = time.time() + segundos
        while time.time() < fim:
            app.processEvents()
            time.sleep(0.02)

    janela = JanelaPrincipal()
    avisos = {"n": 0}

    def vigiar() -> None:
        caixa = app.activeModalWidget()
        if isinstance(caixa, QMessageBox):
            avisos["n"] += 1
            anotar(f"aviso {avisos['n']}: [{caixa.windowTitle()}] {caixa.text()}")
            caixa.grab().save(str(saida / f"aviso-{avisos['n']}.png"))
            botoes = caixa.buttons()
            (botoes[0].click() if botoes else caixa.accept())

    vigia = QTimer()
    vigia.timeout.connect(vigiar)
    vigia.start(300)

    def fotografar(nome: str) -> None:
        esperar(0.8)
        janela.grab().save(str(saida / f"{nome}-janela.png"))
        tela.grabWindow(0).save(str(saida / f"{nome}-tela-inteira.png"))
        anotar(f"{nome}: tema {estilo.tema_atual()}, janela {janela.width()}x{janela.height()}")

    janela.showMaximized()
    esperar(2.0)
    anotar(f"tema ao abrir: {estilo.tema_atual()}")

    for i, nome in enumerate(("escuro", "cinza", "claro"), 1):
        try:
            janela.menu.acoes[f"tema_{nome}"].trigger()
            esperar(0.8)
            fotografar(f"0{i}-inicio-tema-{nome}")
        except Exception:
            erros += 1
            anotar(f"ERRO no tema {nome}:\n{traceback.format_exc()}")

    try:
        janela.menu.acoes["tema_cinza"].trigger()
        livro = saida / "_livro" / "Folhas Duplas.pdf"
        livro.parent.mkdir()
        doc = fitz.open()
        for i in range(6):
            pagina = doc.new_page(width=800, height=560)
            for y in range(80, 520, 18):
                pagina.insert_text((40, y), f"esquerda {i} linha de texto", fontsize=11)
                pagina.insert_text((440, y), f"direita {i} linha de texto", fontsize=11)
        doc.save(str(livro))
        doc.close()
        janela.abrir_livro(str(livro))
        esperar(2.0)
        opcoes = janela.tela_opcoes
        if hasattr(opcoes, "cx_dividir"):
            opcoes.cx_dividir.setChecked(True)
            esperar(0.5)
        fotografar("04-o-que-fazer-tema-cinza")

        from ui.janela_principal import CONFERIR
        janela.analisar()
        fim = time.time() + 180
        while time.time() < fim and janela.telas.currentIndex() != CONFERIR:
            esperar(0.5)
        esperar(4.0)                        # previas e miniaturas chegam por tras
        anotar(f"chegou na tela de conferir: {janela.telas.currentIndex() == CONFERIR}")
        fotografar("05-conferir-tema-cinza")
    except Exception:
        erros += 1
        anotar(f"ERRO no livro/conferir:\n{traceback.format_exc()}")

    def escolher_ferramenta_da_pagina(aba: str, ferramenta: str) -> None:
        """Leva a tela de conferir para Cortar ("bordas") ou Endireitar
        ("angulo"). Sem abas (layout etapa 2) vai pela trilha, como o clique
        do Kaique; com abas, pela barra de abas. Espera a previa chegar."""
        import ui.tela_conferir as tc
        conferir = janela.tela_conferir
        if hasattr(tc, "ABA_DA_FERRAMENTA"):
            conferir.escolher_ferramenta(ferramenta)
        else:
            conferir.barra_abas.setCurrentIndex(conferir._abas_ativas.index(aba))
        vis = getattr(conferir, "visualizadores", {}).get(aba)
        fim = time.time() + 30
        while time.time() < fim and vis is not None and (
                getattr(vis, "_pixmap", None) is None or getattr(vis, "carregando", False)):
            esperar(0.3)
        esperar(1.0)
        anotar(f"ferramenta {ferramenta}: aba atual {getattr(conferir, 'aba_atual', '?')}")

    for numero, (aba, ferramenta) in ((6, ("bordas", "cortar")), (7, ("angulo", "endireitar"))):
        try:
            escolher_ferramenta_da_pagina(aba, ferramenta)
            fotografar(f"0{numero}-conferir-{ferramenta}-maximizada")
        except Exception:
            erros += 1
            anotar(f"ERRO na ferramenta {ferramenta}:\n{traceback.format_exc()}")
    # 10..12 (verificador, 09/10/2026, conferencia da etapa 2 do layout): as
    # outras ferramentas de pagina, Dividir, Filtro e Marcar (retangulo), com a
    # janela maximizada. Livro sem a aba (ex.: Marcar no fase-1 com este livro)
    # vira ERRO anotado e o roteiro segue.
    for numero, (aba, ferramenta) in ((10, ("corte", "dividir")), (11, ("filtro", "filtros")),
                                      (12, ("marcar", "retangulo"))):
        try:
            escolher_ferramenta_da_pagina(aba, ferramenta)
            fotografar(f"{numero}-conferir-{ferramenta}-maximizada")
        except Exception:
            erros += 1
            anotar(f"ERRO na ferramenta {ferramenta}:\n{traceback.format_exc()}")
    # 13: o grupo "Contornar" da trilha aberto (so existe sem abas, layout
    # etapa 2); a lista aparece na tela inteira, nao no print so da janela.
    try:
        trilha = getattr(janela.tela_conferir, "trilha", None)
        if trilha is not None and hasattr(trilha, "abrir_o_grupo"):
            from ui.widgets.trilha_agrupada import GRUPOS
            indice = next(i for i, g in enumerate(GRUPOS) if "laco" in g)
            trilha.abrir_o_grupo(indice)
            fotografar("13-grupo-contornar-aberto-maximizada")
            menu = getattr(trilha, "menu_do_grupo", None)
            if menu is not None:
                menu.close()
        else:
            anotar("13: sem trilha agrupada neste programa (com abas)")
    except Exception:
        erros += 1
        anotar(f"ERRO no grupo aberto:\n{traceback.format_exc()}")
    try:
        janela.showNormal()
        esperar(0.5)
        janela.resize(1280, 657)
        esperar(1.0)
        for numero, (aba, ferramenta) in ((8, ("bordas", "cortar")), (9, ("angulo", "endireitar"))):
            escolher_ferramenta_da_pagina(aba, ferramenta)
            fotografar(f"0{numero}-conferir-{ferramenta}-1280x657")
    except Exception:
        erros += 1
        anotar(f"ERRO em 1280x657:\n{traceback.format_exc()}")

    if getattr(janela, "previas", None) is not None:
        janela.previas.parar()
    janela.close()
    esperar(1.5)
    vigia.stop()
    log = dados / "EditorImpressao" / "erros.log"
    if log.exists():
        shutil.copy(log, saida / "erros.log")
        anotar(f"erros.log da rodada: {log.stat().st_size} bytes (copiado)")
    else:
        anotar("erros.log da rodada: (nenhum)")
    (saida / "roteiro.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    shutil.rmtree(dados, ignore_errors=True)
    shutil.rmtree(saida / "_livro", ignore_errors=True)
    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
