"""Pedido 1 (29/10/2026): "Só as letras" ligado na janela do Automático funciona?

Roda o programa de verdade, sem janela na tela (offscreen), numa CÓPIA do projeto
"Na escola de Jesus" (<worktree>/_tmp/dados; nada é escrito na pasta de dados de teste
nem no %LOCALAPPDATA%). Passos, como o Kaique faria:
  1. abre o livro; abre a janela grande do Automático;
  2. escolhe "Preto e branco" em "Jeito de limpar" e marca "Só as letras";
  3. deixa marcada só a etapa "Limpar a folha" (as outras o livro já tem) e roda no livro todo;
  4. confere: o livro gravou "Só as letras"? (projeto e projeto.json); o painel "Filtro da
     página" mostra ligado? a página desenhada (prévia e PDF) sai com as letras em preto e
     branco e a gravura com cor?
  5. Ctrl+Z (desfazer): o "Só as letras" do livro volta como estava?
Uso: python relatorios/automatico-pintura/conferir_so_as_letras.py [indice_da_pagina]
"""
import copy
import json
import os
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(RAIZ / "_tmp" / "temp")

import numpy as np  # noqa: E402
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox  # noqa: E402

PDF = ("D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
       "Na escola de Jesus - Catecismo explicado com imagens..pdf")
PASTA = RAIZ / "_tmp/dados/EditorImpressao/projetos/Na escola de Jesus - Catecismo explicado com imagens"
IDX = int(sys.argv[1]) if len(sys.argv) > 1 else 8
SAIDA = Path(__file__).resolve().parent

app = QApplication.instance() or QApplication([])
QDialog.exec = lambda self, *a, **k: 0
QMessageBox.exec = lambda self, *a, **k: 0
from core import automatico as A  # noqa: E402
from core import misto  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import renderizar_com_filtro  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402
from ui.tela_conferir import PAINEL_FILTRO  # noqa: E402


def assentar(segundos=1.0):
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


def gravado():
    d = json.loads((PASTA / "projeto.json").read_text(encoding="utf-8"))
    return d.get("misto_so_as_letras"), d.get("filtro_padrao"), d["paginas"][IDX].get("misto_so_as_letras")


def painel():
    tela = janela.tela_conferir
    caixa = tela.escolhas_misto.caixa
    return {"visivel": tela.escolhas_misto.isVisible(), "marcada": caixa.isChecked()}


def desenho(filtro=None):
    doc = abrir_pdf(PDF)
    try:
        pag = janela.projeto.paginas[IDX]
        img, _ = renderizar_com_filtro(doc, copy.deepcopy(janela.projeto), copy.deepcopy(pag),
                                       filtro or pag.filtro, dpi=110)
    finally:
        doc.close()
    return img


def medir(img, rotulo):
    """Quanto da página tem cor (|R-B| > 25) e quanto é cinza do meio (não preto, não branco)."""
    if img.ndim == 2:
        print(f"  {rotulo}: 1 canal (só preto/branco/cinza); cinza do meio {((img > 30) & (img < 225)).mean():.1%}")
        return 0.0
    cor = (np.abs(img[..., 0].astype(int) - img[..., 2].astype(int)) > 25).mean()
    print(f"  {rotulo}: pontos com cor {cor:.1%}")
    return float(cor)


janela = JanelaPrincipal()
janela.resize(1280, 657)
janela.show()
janela.abrir_livro(PDF)
assentar(3)
tela = janela.tela_conferir
tela.escolher_ferramenta("zoom")
tela.ir_para_pagina(IDX)
tela.paineis.abrir(PAINEL_FILTRO)
assentar(2)
print("ANTES: projeto.misto_so_as_letras =", janela.projeto.misto_so_as_letras,
      "| gravado (livro, filtro, pagina) =", gravado(), "| painel:", painel())

jan = janela.abrir_o_automatico()
assentar(1)
jan.radios_de_filtro["preto_e_branco"].setChecked(True)
jan.escolhas_misto.caixa.setChecked(True)
assentar(0.5)
print("janela do Automático: estado.opcoes['misto_so_as_letras'] =",
      janela.estado_do_automatico.opcoes.get("misto_so_as_letras"),
      "| caixa das molduras acesa?", jan.cx_decoracao_pb.isEnabled())
janela.estado_do_automatico.marcadas = {A.LIMPAR}
janela.estado_do_automatico.alcance = "livro"
ok = janela.rodar_o_automatico(esperar=True, perguntar=False)
assentar(3)
print("rodou:", ok)
pag = janela.projeto.paginas[IDX]
print("DEPOIS: projeto.misto_so_as_letras =", janela.projeto.misto_so_as_letras,
      "| pagina.filtro =", pag.filtro, "| pagina.misto_so_as_letras =", pag.misto_so_as_letras,
      "| vale na pagina:", misto.escolhas_da_pagina(janela.projeto, pag)[0])
print("  gravado (livro, filtro_padrao, pagina) =", gravado())
print("  painel 'Filtro da página' (sem trocar de página):", painel())
tela.ir_para_pagina(IDX + 1)
assentar(1)
tela.ir_para_pagina(IDX)
assentar(2)
print("  painel depois de ir e voltar de página:", painel())
img = desenho()
medir(img, f"pagina {IDX + 1} desenhada (Preto e branco + Só as letras do livro)")
from PIL import Image  # noqa: E402
Image.fromarray(img if img.ndim == 2 else img[..., ::-1]).save(RAIZ / "_tmp" / f"so_letras_p{IDX + 1}.png")

tela.desfazer()
assentar(2)
print("DESFEITO: projeto.misto_so_as_letras =", janela.projeto.misto_so_as_letras,
      "| filtro_padrao =", janela.projeto.filtro_padrao, "| pagina.filtro =", janela.projeto.paginas[IDX].filtro,
      "| gravado =", gravado(), "| painel:", painel())
tela.refazer()
assentar(2)
print("REFEITO: projeto.misto_so_as_letras =", janela.projeto.misto_so_as_letras, "| gravado =", gravado())
janela._fechar_a_janela_do_automatico()
if janela.previas is not None:
    janela.previas.parar()
janela.close()
