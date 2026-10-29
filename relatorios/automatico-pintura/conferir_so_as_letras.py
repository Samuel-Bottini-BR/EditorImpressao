"""Pedido 1 (29/10/2026): "Só as letras" ligado na janela do Automático funciona?

Roda o programa de verdade, sem janela na tela (offscreen), numa CÓPIA do projeto
"Na escola de Jesus" (<worktree>/_tmp/dados; nada é escrito na pasta de dados de teste
nem no %LOCALAPPDATA%). Passos, como o Kaique faria:
  1. abre o livro; abre a janela grande do Automático;
  2. escolhe "Preto e branco" em "Jeito de limpar" e marca "Só as letras";
  3. deixa marcada só a etapa "Limpar a folha" (endireitar, cortar e gravuras o livro já
     tem ligados) e roda no livro todo;
  4. confere: o livro gravou "Só as letras"? (projeto aberto e projeto.json); o painel
     "Filtro da página" mostra ligado (herdado do livro)? a tela ("Uma página" e
     "antes / depois") e o PDF saem com as letras em preto e branco e a gravura com cor?
  5. Ctrl+Z (desfazer): o "Só as letras" do livro volta como estava? Ctrl+Y refaz.
Grava os prints (1280 x 657) nesta pasta e as medidas em medida-so-as-letras.txt.
Uso: python relatorios/automatico-pintura/conferir_so_as_letras.py [indice_da_pagina]
Antes: copiar o projeto para _tmp/dados/EditorImpressao/projetos/ e apontar a "pasta" do
resumo.json para a cópia.
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
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(RAIZ / "_tmp" / "temp")

import fitz  # noqa: E402
import numpy as np  # noqa: E402
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox  # noqa: E402

PDF = ("D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
       "Na escola de Jesus - Catecismo explicado com imagens..pdf")
PASTA = RAIZ / "_tmp/dados/EditorImpressao/projetos/Na escola de Jesus - Catecismo explicado com imagens"
IDX = int(sys.argv[1]) if len(sys.argv) > 1 else 8
SAIDA = Path(__file__).resolve().parent
LINHAS: list[str] = []

app = QApplication.instance() or QApplication([])
QDialog.exec = lambda self, *a, **k: 0
QMessageBox.exec = lambda self, *a, **k: 0
from core import automatico as A  # noqa: E402
from core import misto  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import processar, renderizar_com_filtro  # noqa: E402
from core.selecao import GRAVURA, LETRA  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402
from ui.tela_conferir import PAINEL_FILTRO  # noqa: E402


def dizer(*partes):
    texto = " ".join(str(p) for p in partes)
    print(texto, flush=True)
    LINHAS.append(texto)


def assentar(segundos=1.0):
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


def gravado():
    d = json.loads((PASTA / "projeto.json").read_text(encoding="utf-8"))
    return {"livro.misto_so_as_letras": d.get("misto_so_as_letras"), "livro.filtro_padrao": d.get("filtro_padrao"),
            f"pagina{IDX + 1}.misto_so_as_letras": d["paginas"][IDX].get("misto_so_as_letras")}


def painel():
    tela = janela.tela_conferir
    parte = tela.paineis.filtro_da_pagina.partes.get("letras")
    resumo = parte.cabeca.resumo.text() if parte is not None else "?"
    return {"caixinha 'Só as letras' marcada": tela.escolhas_misto.caixa.isChecked(),
            "resumo da parte": resumo}


def cor3(a):
    a = np.asarray(a)
    return np.repeat(a[..., None], 3, 2) if a.ndim == 2 else a


def medir(img, pagina, rotulo):
    """Na letra marcada: quanto tem cor e quanto é cinza do meio (deve ser ~0: preto e
    branco). Na gravura marcada: quanto tem cor (deve ser alto: fica como no original)."""
    img = cor3(img).astype(int)
    h, w = img.shape[:2]
    sel = pagina.obter_selecao()
    letra = sel.peso(h, w, LETRA) > 0.5
    gravura = sel.peso(h, w, GRAVURA) > 0.5
    croma = np.abs(img[..., 0] - img[..., 2]) + np.abs(img[..., 1] - img[..., 2])
    colorido = croma > 30
    cinza = img.mean(axis=2)
    meio = (cinza > 40) & (cinza < 215)
    dizer(f"  {rotulo}: na LETRA {colorido[letra].mean():.1%} com cor e {meio[letra].mean():.1%} cinza do meio; "
          f"na GRAVURA {colorido[gravura].mean():.1%} com cor")
    return float(colorido[letra].mean()), float(colorido[gravura].mean())


def pix_np(pix):
    q = pix.toImage().convertToFormat(pix.toImage().Format.Format_RGB888)
    w, h = q.width(), q.height()
    return np.frombuffer(q.constBits(), np.uint8).reshape(h, q.bytesPerLine())[:, :w * 3].reshape(h, w, 3)[..., ::-1].copy()   # copia: o QImage some ao sair


def esperar_a_previa(antes_depois=False, limite=180):
    tela = janela.tela_conferir
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        app.processEvents()
        pronta = tela.previas.ja_pronta(IDX, tela._dpi_atual)
        if antes_depois:
            if pronta is not None and tela.vista_antes_depois.depois is not None:
                break
        elif pronta is not None and tela.editor_selecao._img is pronta:
            break
        time.sleep(0.03)
    assentar(3)


def foto(nome):
    janela.resize(1280, 657)
    assentar(0.5)
    janela.grab().save(str(SAIDA / nome), "JPG", 85)
    dizer(f"  print: {nome} ({janela.width()} x {janela.height()})")


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
dizer(f"Na escola de Jesus, página {IDX + 1} (cópia do projeto dele; o livro já tem Endireitar, Cortar, "
      "Limpar a folha e Gravuras e fotos ligados)")
dizer("ANTES:", gravado(), "| painel:", painel())

jan = janela.abrir_o_automatico()
assentar(1)
jan.radios_de_filtro["preto_e_branco"].setChecked(True)
jan.escolhas_misto.caixa.setChecked(True)
assentar(0.5)
dizer("janela do Automático: Preto e branco + 'Só as letras' marcados -> escolha =",
      janela.estado_do_automatico.opcoes.get("misto_so_as_letras"),
      "| caixinha das molduras apagada (D-168)?", not jan.cx_decoracao_pb.isEnabled())
janela.estado_do_automatico.marcadas = {A.LIMPAR}
janela.estado_do_automatico.alcance = "livro"
ok = janela.rodar_o_automatico(esperar=True, perguntar=False)
assentar(2)
pag = janela.projeto.paginas[IDX]
dizer("rodou:", ok, "| projeto aberto: livro.misto_so_as_letras =", janela.projeto.misto_so_as_letras,
      "| página.filtro =", pag.filtro, "| página.misto_so_as_letras =", pag.misto_so_as_letras,
      "| vale na página:", misto.escolhas_da_pagina(janela.projeto, pag)[0])
dizer("gravado no projeto.json:", gravado())
dizer("painel 'Filtro da página' logo depois de rodar:", painel())

# a tela: "Uma página"
esperar_a_previa()
medir(tela.editor_selecao._img, pag, "tela, 'Uma página' (a prévia que a vista recebe)")
foto("1-so-as-letras-herdado-uma-pagina.jpg")
# a tela: "antes / depois"
tela.botao_antes_depois.click()
esperar_a_previa(antes_depois=True)
medir(pix_np(tela.vista_antes_depois.depois), pag, "tela, 'antes / depois' (lado depois)")
foto("2-so-as-letras-herdado-antes-depois.jpg")
tela.botao_antes_depois.click()
assentar(1)

# o desenho do tamanho do PDF e o PDF (só esta página: as outras apagadas numa cópia)
doc = abrir_pdf(PDF)
grande, _m = renderizar_com_filtro(doc, copy.deepcopy(janela.projeto), copy.deepcopy(pag), pag.filtro,
                                   dpi=janela.projeto.qualidade_dpi)
doc.close()
medir(grande, pag, f"desenho do tamanho do PDF ({janela.projeto.qualidade_dpi} dpi)")
copia = copy.deepcopy(janela.projeto)
for p in copia.paginas:
    if p.indice != IDX:
        p.apagada = True
copia.margens_iguais = False
copia.montar_cadernos = False
copia.caminho_saida = str(RAIZ / "_tmp" / "so_as_letras.pdf")
caminho = processar(copia)
with fitz.open(caminho) as d:
    pix = d[0].get_pixmap(dpi=110, colorspace=fitz.csRGB)
    no_pdf = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3][..., ::-1]
medir(no_pdf, pag, "PDF gerado (Confirmar e processar, só esta página)")

# desfazer / refazer
tela.desfazer()
assentar(2)
dizer("DESFEITO (Ctrl+Z):", "livro.misto_so_as_letras =", janela.projeto.misto_so_as_letras,
      "| filtro_padrao =", janela.projeto.filtro_padrao, "| página.filtro =", janela.projeto.paginas[IDX].filtro,
      "| gravado =", gravado())
tela.refazer()
assentar(2)
dizer("REFEITO (Ctrl+Y):", "livro.misto_so_as_letras =", janela.projeto.misto_so_as_letras, "| gravado =", gravado())
(SAIDA / "medida-so-as-letras.txt").write_text(
    "# python relatorios/automatico-pintura/conferir_so_as_letras.py " + str(IDX) + "\n" + "\n".join(LINHAS) + "\n",
    encoding="utf-8")
janela._fechar_a_janela_do_automatico()
if janela.previas is not None:
    janela.previas.parar()
janela.close()
