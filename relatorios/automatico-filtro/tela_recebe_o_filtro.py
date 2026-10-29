"""D-582 (b): a imagem que a tela RECEBE a cada filtro escolhido (pelo painel "Filtro da
pagina", o mesmo sinal do clique no cartao) e igual ao desenho de verdade desse filtro?
Quanto tempo leva? Copia do projeto em _tmp/dados; offscreen."""
import copy
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parents[2] / "_tmp"   # a copia do projeto mora em <worktree>/_tmp/dados
sys.path.insert(0, str(AQUI.parent))
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["LOCALAPPDATA"] = str(AQUI / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(AQUI / "temp")

import numpy as np  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

PDF = ("D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
       "Na escola de Jesus - Catecismo explicado com imagens..pdf")
IDX = int(os.environ.get("PAG", "0"))
app = QApplication.instance() or QApplication([])
from ui.janela_principal import JanelaPrincipal  # noqa: E402
from ui.tela_conferir import PAINEL_FILTRO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import renderizar_com_filtro  # noqa: E402


def assentar(n=4):
    for _ in range(n):
        app.processEvents()


def pix_np(pix):
    q = pix.toImage().convertToFormat(pix.toImage().Format.Format_RGB888)
    w, h = q.width(), q.height()
    return np.frombuffer(q.constBits(), np.uint8).reshape(h, q.bytesPerLine())[:, :w * 3].reshape(h, w, 3)[..., ::-1].astype(int)


def cor3(a):
    return np.repeat(a[..., None], 3, 2).astype(int) if a.ndim == 2 else a.astype(int)


janela = JanelaPrincipal()
janela.resize(1280, 657)
janela.show()
janela.abrir_livro(PDF)
tela = janela.tela_conferir
assentar(10)
tela.ir_para_pagina(IDX)
tela.escolher_ferramenta("retangulo")
tela.paineis.abrir(PAINEL_FILTRO)
assentar(10)
if os.environ.get("MODO") == "ad":
    tela.botao_antes_depois.click()
pag = janela.projeto.paginas[IDX]
print("filtro de partida:", pag.filtro)
painel = tela.paineis.filtro_da_pagina
for f in (sys.argv[1:] or ["preto_e_branco", "melhorar", "magico_pro"]):
    t0 = time.monotonic()
    painel.filtro_escolhido.emit(f)
    esperado_chave = tela.previas.chave(IDX, tela._dpi_atual)
    while time.monotonic() - t0 < 90:
        assentar(2)
        if os.environ.get("MODO") == "ad":
            ok = tela.vista_antes_depois.depois is not None and tela.previas.ja_pronta(IDX, tela._dpi_atual) is not None
        else:
            ok = tela.editor_selecao._img is not None and tela.previas.ja_pronta(IDX, tela._dpi_atual) is tela.editor_selecao._img
        if ok:
            break
        time.sleep(0.01)
    dt = time.monotonic() - t0
    assentar(6)
    doc = abrir_pdf(PDF)
    verdade, _ = renderizar_com_filtro(doc, copy.deepcopy(janela.projeto), copy.deepcopy(pag), f,
                                       dpi=tela._dpi_atual)
    doc.close()
    if os.environ.get("MODO") == "ad":
        recebida = pix_np(tela.vista_antes_depois.depois)
        quem = "antes/depois (lado depois)"
    else:
        recebida = cor3(tela.editor_selecao._img)
        quem = "Uma pagina (editor)"
    v = cor3(verdade)
    dif = np.abs(recebida - v).mean() if recebida.shape == v.shape else f"formas {recebida.shape} {v.shape}"
    print(f"{f:15s} pagina.filtro={pag.filtro:15s} chegou em {dt:5.2f}s  {quem}: |recebida - desenho de {f}| = {dif}")
janela.previas.parar()
janela.close()
