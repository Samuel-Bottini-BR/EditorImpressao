"""Os dois prints da pergunta 1 (02/11/2026, pedido da gerente): a MESMA folha (Gradus Primus,
folha 1) na janela do Automático com a etapa 7 aberta, de dois jeitos:

  O livro é dividido antes (o "Dividir folhas ao meio" rodado no livro todo), como o dele no
  print a-44 (71 páginas).

  (A) escolha-A-folha-A4.png: a folha A4 como sairia do "Montar para imprimir" com o de fábrica
      ("Livreto A4, 20 por caderno"): core/impressao.previa_da_folha num PDF de teste feito das
      mesmas páginas prontas (as 4 páginas da folha 1 desenhadas como o "depois"; as outras em
      branco, só para a conta da dobra dar a mesma folha). É um print de teste: o lado direito
      recebe essa folha à mão; a janela não monta assim.
  (B) escolha-B-tamanho-do-scan.png: a folha como a etapa 7 monta (core/cadernos.impor_pdf, no
      tamanho do scan, sem A4, sem margem), que é o que o ramo constrói.

Cópia do Gradus em _tmp/livros-prints/ e pasta de dados própria (_tmp/dados-escolha).
Rodar: .venv\\Scripts\\python.exe relatorios\\caderno-tela-grande\\escolha.py
"""

from __future__ import annotations

import os
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
DADOS = RAIZ / "_tmp" / "dados-escolha"
shutil.rmtree(DADOS, ignore_errors=True)
DADOS.mkdir(parents=True)
os.environ["LOCALAPPDATA"] = str(DADOS)
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402
from PySide6.QtGui import QFontDatabase  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication.instance() or QApplication(sys.argv)
for arquivo in ("segoeui.ttf", "segoeuib.ttf", "seguisb.ttf"):
    if Path("C:/Windows/Fonts", arquivo).is_file():
        QFontDatabase.addApplicationFont(str(Path("C:/Windows/Fonts", arquivo)))

from core import automatico as A  # noqa: E402
from core import impressao as imp  # noqa: E402
from core import perfis  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402
from ui.widgets.folhas_do_caderno import DPI_DA_FOLHA  # noqa: E402
from ui.widgets.visualizador import numpy_para_qimage  # noqa: E402


def rodar(seg):
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.005)


def esperar(painel, seg=900):
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        if not painel.calculando():
            rodar(0.05)
            if not painel.calculando():
                return
        time.sleep(0.01)


pasta = RAIZ / "_tmp" / "livros-prints"
pasta.mkdir(parents=True, exist_ok=True)
gradus = pasta / "pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf"
if not gradus.exists():
    shutil.copy2(RAIZ / "_tmp" / "livros" / "gradus.pdf", gradus)

janela = JanelaPrincipal()
janela.resize(1280, 657)
janela.show()
janela.abrir_livro(str(gradus))
rodar(1.0)
while getattr(janela, "medida_ao_abrir", None) is not None:
    rodar(0.2)
estado = janela.estado_do_automatico
# o livro DIVIDIDO, como o dele no print a-44 (71 páginas): roda o "Dividir folhas ao meio" antes
estado.marcadas = {A.DIVIDIR}
estado.alcance = "livro"
janela.rodar_o_automatico(esperar=True)
rodar(0.5)
print("páginas depois de dividir:", len(janela.projeto.paginas_ativas))
estado.por_receita(perfis.NOME_DE_FABRICA)
estado.marcadas.add(A.CADERNOS)
grande = janela.abrir_o_automatico(A.CADERNOS)
folhas = grande.folhas_do_caderno
esperar(folhas)
rodar(0.3)
grande.grab().save(str(AQUI / "escolha-B-tamanho-do-scan.png"))
print("B:", folhas.rotulos["frente"].text())

# (A) as mesmas 4 páginas prontas, num PDF de teste do tamanho do livro (as outras em branco)
ativas = [p.indice for p in janela.projeto.paginas_ativas]
folha = folhas.folhas()[0]
copia = A.copia_para_a_previa(janela.projeto)
pedido = estado.pedido(pular_mexidas=False)
doc = abrir_pdf(copia.caminho_entrada)
prontas = {}
for lado in folha:
    for pos in (lado.esquerda, lado.direita):
        if pos is not None and pos < len(ativas):
            import copy as _copy

            depois = A.depois_da_pagina(doc, _copy.deepcopy(copia), pedido, ativas[pos], DPI_DA_FOLHA)
            prontas[pos] = depois[0]
doc.close()
altura, largura = next(iter(prontas.values())).shape[:2]
pt = (largura / DPI_DA_FOLHA * 72, altura / DPI_DA_FOLHA * 72)
teste = DADOS / "gradus-pronto-teste.pdf"
pdf = fitz.open()
for pos in range(len(ativas)):
    pagina = pdf.new_page(width=pt[0], height=pt[1])
    if pos in prontas:
        ok, png = cv2.imencode(".png", prontas[pos])
        pagina.insert_image(pagina.rect, stream=png.tobytes())
pdf.save(str(teste))
pdf.close()
os.environ["EDITOR_PAGINAS_AQUI"] = "1"        # desenha aqui (só o print de teste)
a4 = imp.previa_da_folha(str(teste), imp.OpcoesDeImpressao(), 0, folhas.imagens["frente"].width() * 3)
faces = []
for face in a4.faces:
    img = np.frombuffer(face.amostras, np.uint8).reshape(face.altura, face.largura, face.canais)
    faces.append(np.ascontiguousarray(img[:, :, ::-1]) if face.canais == 3 else img)
folhas._folha = tuple(faces)
folhas._pix = None
folhas._qimagens = {"inteiras": tuple(numpy_para_qimage(f) for f in faces), "pequenas": None,
                    "tamanho_pequeno": None}
for lado in folhas.imagens.values():
    lado._feito_de = None
folhas._mostrar()
rodar(0.3)
grande.grab().save(str(AQUI / "escolha-A-folha-A4.png"))
print("A:", folhas.rotulos["frente"].text(), "folha", a4.numero, "de", a4.total)

# as duas lado a lado, num arquivo só (para a Central)
a = cv2.imread(str(AQUI / "escolha-A-folha-A4.png"))
b = cv2.imread(str(AQUI / "escolha-B-tamanho-do-scan.png"))
h = max(a.shape[0], b.shape[0])
vao = np.full((h, 24, 3), 255, np.uint8)
cv2.imwrite(str(AQUI / "escolha-A-e-B-lado-a-lado.png"), np.concatenate([a, vao, b], axis=1))
grande.reject()
rodar(0.3)
janela.close()
