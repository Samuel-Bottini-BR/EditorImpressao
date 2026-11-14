"""Perguntas A2, A3 e A4 (Tirar o fundo), SEM JANELA NA TELA (offscreen, com as fontes do Windows).

    python fundo_a.py <cópia do Siebmacher, 10 folhas> <pasta de saída>

O caminho, como o Kaique faria: abrir o livro → "Sim, tirar o fundo" (todas as páginas ficam sem o
fundo) → ...

A3 (a frase da faixa): página 4. Print da janela com a página em "Tirar o fundo" (a faixa diz a
frase do fundo). Clicar na figurinha "Original" (o mesmo caminho da figurinha, da tecla 1 e do
menu): a página continua sem o fundo, igual; a faixa passa a dizer "Esta página vai sair em
Original.".

A4 (o menu Filtro): print do menu Filtro aberto na página 4 (como é hoje).

A2 (o "só neste pedaço"): página 5. Painel "Filtro da página" > "Só neste pedaço" > "Original" e
um retângulo marcado na página (gravado na página como o desenho do Retângulo grava: área à mão,
com o filtro do pedaço). Desenhada pela conta do PDF (core.pipeline.renderizar_pagina):
  - página em "Tirar o fundo", sem pedaço;
  - página em "Tirar o fundo", com o pedaço em Original;
  - a mesma página depois da figurinha "Original" (Original com o fundo tirado), com o pedaço;
  - a mesma página depois da figurinha "Preto e branco", com o pedaço.
Grava também a caixa do pedaço (em fração da página) para o desenho.

Nada do programa muda. LOCALAPPDATA e projetos numa pasta à parte; só a CÓPIA do livro.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parents[1]
RAIZ = AQUI.parents[1]
LIVRO, SAIDA = sys.argv[1], Path(sys.argv[2])
SAIDA.mkdir(parents=True, exist_ok=True)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
(AQUI / "_dados").mkdir(exist_ok=True)
dados = Path(tempfile.mkdtemp(prefix="fundo-", dir=AQUI / "_dados"))  # nova a cada rodada: livro sempre novo
os.environ["LOCALAPPDATA"] = str(dados)
os.environ["TEMP"] = os.environ["TMP"] = tempfile.mkdtemp(prefix="t-", dir=dados)
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
try:                                    # prioridade baixa: o PC do Samuel está em uso
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:  # noqa: BLE001
    pass

import cv2  # noqa: E402
from PySide6.QtWidgets import QAbstractButton, QApplication  # noqa: E402

import projetos  # noqa: E402

(dados / "projetos").mkdir(exist_ok=True)
projetos.pasta_dos_projetos = lambda: dados / "projetos"
app = QApplication.instance() or QApplication([])

from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import renderizar_pagina  # noqa: E402
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402
from ui.widgets.paineis import PAINEL_FILTRO  # noqa: E402

PEDACO = (0.30, 0.30, 0.72, 0.62)      # o retângulo marcado (fração da página), no meio do texto
info: dict = {"pedaco": PEDACO}


def assentar(segundos: float) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


def textos_da_faixa(conferir) -> list[str]:
    from PySide6.QtWidgets import QLabel
    return [r.text() for r in conferir.faixa.findChildren(QLabel) if r.isVisible() and r.text()]


def desenhar(janela, indice: int, nome: str) -> None:
    doc = abrir_pdf(LIVRO)
    try:
        pagina = janela.projeto.paginas[indice]
        img, _ = renderizar_pagina(doc, janela.projeto, pagina, dpi=80)
        cv2.imwrite(str(SAIDA / f"{nome}.png"), img)
        info[nome] = {"filtro": pagina.filtro, "fundo_tirado": getattr(pagina, "fundo_tirado", None),
                      "pedacos": len([r for r in (pagina.obter_selecao().regioes
                                                  if pagina.obter_selecao() else [])
                                      if r.origem == MAO])}
        print(nome, info[nome], flush=True)
    finally:
        doc.close()


janela = JanelaPrincipal()
janela.resize(1600, 1000)
janela.show()
janela.abrir_livro(LIVRO)
assentar(1)
next(b for b in janela.aviso_do_fundo.findChildren(QAbstractButton)
     if b.text() == "Sim, tirar o fundo").click()
assentar(1)
conferir = janela.tela_conferir

if "so_a2" not in sys.argv:
    # ---- A3: a frase da faixa (página 4)
    conferir.ir_para_pagina(3)
    conferir.paineis.abrir(PAINEL_FILTRO)
    assentar(10)
    janela.grab().save(str(SAIDA / "a3-janela-tirar-o-fundo.png"))
    info["a3_faixa_antes"] = textos_da_faixa(conferir)
    desenhar(janela, 3, "a3-pagina-tirar-o-fundo")
    conferir._escolher_filtro(ORIGINAL)          # a figurinha "Original" (tecla 1, menu: o mesmo caminho)
    assentar(10)
    janela.grab().save(str(SAIDA / "a3-janela-original.png"))
    info["a3_faixa_depois"] = textos_da_faixa(conferir)
    desenhar(janela, 3, "a3-pagina-original")

    # ---- A4: o menu Filtro (página 4)
    janela._marcar_o_filtro_no_menu()
    menu = janela.menu.menus["Filtro"]
    menu.popup(janela.mapToGlobal(janela.rect().topLeft()))
    assentar(0.5)
    menu.grab().save(str(SAIDA / "a4-menu-filtro.png"))
    info["a4_menu"] = [a.text() for a in menu.actions()]
    menu.hide()


# ---- A2: o pedaço em Original (página 5)
conferir.ir_para_pagina(4)
assentar(6)
desenhar(janela, 4, "a2-0-tirar-o-fundo-sem-pedaco")
painel = conferir.paineis.filtro_da_pagina
parte = painel.partes.get("pedaco")
if parte is not None and not parte.aberta:
    parte.alternar()
painel._escolher_pedaco(ORIGINAL)            # "Só neste pedaço" > "Original"
assentar(1)
painel.grab().save(str(SAIDA / "a2-painel-so-neste-pedaco.png"))
pagina = janela.projeto.paginas[4]
s = pagina.obter_selecao() or Selecao()
s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[PEDACO[:2], PEDACO[2:]],
                     origem=MAO, filtro=ORIGINAL))
pagina.guardar_selecao(s)
# (o pedaço é gravado direto na página, como tests/test_so_neste_pedaco_no_tirar_o_fundo.py faz;
# a tela, se avisada, regravaria a marcação do editor por cima. O desenho é o do PDF.)
desenhar(janela, 4, "a2-1-tirar-o-fundo-com-pedaco")
conferir._escolher_filtro(ORIGINAL)
assentar(4)
pagina.guardar_selecao(s)
desenhar(janela, 4, "a2-2-original-com-pedaco")
conferir._escolher_filtro(PRETO_E_BRANCO)
assentar(4)
pagina.guardar_selecao(s)
desenhar(janela, 4, "a2-3-preto-e-branco-com-pedaco")

(SAIDA / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
if janela.previas is not None:
    janela.previas.parar()
janela.close()
print("pronto", SAIDA, flush=True)
