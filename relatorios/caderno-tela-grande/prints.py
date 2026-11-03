"""Prints da D-574 na etapa 7 "Montar cadernos" do Automático (02/11/2026), fora da tela (offscreen).

Usa CÓPIAS dos livros (o Gradus Primus da Área de Trabalho do Samuel e o Palatino do verificador,
copiados para _tmp/livros/; os originais só foram lidos) e uma pasta de dados própria
(_tmp/dados-prints-caderno: nada vai para o configuracoes.json dele). A janela principal tem
1280 x 657 (o tamanho do print a-44); a janela grande do Automático abre do tamanho de sempre.

Rodar: .venv\\Scripts\\python.exe relatorios\\caderno-tela-grande\\prints.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
DADOS = RAIZ / "_tmp" / "dados-prints-caderno"
if DADOS.exists():
    shutil.rmtree(DADOS)
DADOS.mkdir(parents=True)
os.environ["LOCALAPPDATA"] = str(DADOS)
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

from PySide6.QtGui import QFontDatabase  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication.instance() or QApplication(sys.argv)
for arquivo in ("segoeui.ttf", "segoeuib.ttf", "seguisb.ttf"):
    if Path("C:/Windows/Fonts", arquivo).is_file():
        QFontDatabase.addApplicationFont(str(Path("C:/Windows/Fonts", arquivo)))

from core import automatico as A  # noqa: E402
from core import perfis  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402

MED: dict = {}


def rodar(seg: float) -> None:
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.005)


def esperar(painel, seg: float = 600.0) -> float:
    t = time.monotonic()
    while time.monotonic() - t < seg:
        app.processEvents()
        if not painel.calculando():
            rodar(0.05)
            if not painel.calculando():
                break
        time.sleep(0.01)
    return round(time.monotonic() - t, 2)


def foto(widget, nome: str) -> str:
    rodar(0.15)
    widget.grab().save(str(AQUI / nome))
    return nome


def copia(origem: Path, nome: str) -> Path:
    pasta = RAIZ / "_tmp" / "livros-prints"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / nome
    if not destino.exists():
        try:
            os.link(origem, destino)        # mesmo disco: sem copiar de novo
        except OSError:
            shutil.copy2(origem, destino)
    return destino


def abrir(janela, livro: Path, etapa: str, dividir: bool = False):
    janela.abrir_livro(str(livro))
    rodar(1.0)
    fim = time.monotonic() + 600
    while time.monotonic() < fim and getattr(janela, "medida_ao_abrir", None) is not None:
        rodar(0.2)
    estado = janela.estado_do_automatico
    if dividir:
        # o livro dividido, como o dele (o "Dividir folhas ao meio" rodado no livro todo)
        estado.marcadas = {A.DIVIDIR}
        estado.alcance = "livro"
        janela.rodar_o_automatico(esperar=True)
        rodar(0.5)
    estado.por_receita(perfis.NOME_DE_FABRICA)       # as etapas de fábrica, como no print a-44
    estado.marcadas.add(A.CADERNOS)
    grande = janela.abrir_o_automatico(etapa)
    rodar(0.3)
    return grande


janela = JanelaPrincipal()
janela.resize(1280, 657)
janela.show()
rodar(0.5)

gradus = copia(RAIZ / "_tmp" / "livros" / "gradus.pdf", "pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
grande = abrir(janela, gradus, A.LIMPAR, dividir=True)
esperar(grande.folhear)
foto(grande, "00-antes-outra-etapa-antes-e-depois.png")
lista = grande.painel_de_opcoes.lista
lista.setCurrentItem(lista.item_da_etapa(A.CADERNOS))
rodar(0.3)
folhas = grande.folhas_do_caderno
MED["01_montando_bolinha"] = folhas.calculando()
foto(grande, "01-etapa-7-aberta-montando.png")
MED["02_primeira_folha_s"] = esperar(folhas)
foto(grande, "02-folha-1-frente-e-verso.png")
MED["02_textos"] = [folhas.rotulos["frente"].text(), folhas.rotulos["verso"].text(), folhas.rotulo_da_folha.text()]
folhas.passar_folha(1)
MED["03_seta_s"] = esperar(folhas)
foto(grande, "03-seta-folha-2.png")
combo = grande.controles["paginas_por_caderno"]
combo.setCurrentIndex(combo.findData(12))
MED["04_trocar_para_12_s"] = esperar(folhas)
MED["04_textos"] = folhas.rotulos["frente"].text()
foto(grande, "04-trocou-para-12-por-caderno.png")
combo.setCurrentIndex(combo.findData(20))
esperar(folhas)
folhas.abrir_em_tela_cheia()
tela = folhas.tela_grande
tela.setWindowState(tela.windowState() & ~tela.windowState())
tela.resize(1280, 657)
rodar(0.5)
tela._desenhar()
foto(tela, "05-tela-grande-de-caderno.png")
tela.botao_mais.click()
tela.botao_mais.click()
rodar(0.3)
foto(tela, "06-tela-grande-com-zoom.png")
tela.accept()
rodar(0.2)
lista.setCurrentItem(lista.item_da_etapa(A.LIMPAR))
esperar(grande.folhear)
foto(grande, "07-outra-etapa-volta-o-antes-e-depois.png")

# pergunta 2: a caixinha da etapa 7 desmarcada, a etapa clicada
lista.setCurrentItem(lista.item_da_etapa(A.CADERNOS))
item = lista.item_da_etapa(A.CADERNOS)
from PySide6.QtCore import Qt  # noqa: E402

item.setCheckState(Qt.Unchecked)
rodar(0.3)
esperar(folhas)
foto(grande, "08-caixinha-desmarcada-etapa-7-aberta.png")
grande.reject()
rodar(0.3)

# pergunta 3: o painel Automático da área de trabalho, com a etapa 7 escolhida
from ui.automatico import PainelAutomatico  # noqa: E402

painel = janela.findChildren(PainelAutomatico)[0]
janela.tela_conferir.paineis.abrir("automatico")
painel.lista.setCurrentItem(painel.lista.item_da_etapa(A.CADERNOS))
rodar(0.3)
foto(janela, "09-painel-automatico-etapa-7-escolhida.png")

# Palatino: a folha 1
palatino = copia(RAIZ / "_tmp" / "livros" / "palatino.pdf", "palatino.pdf")
grande = abrir(janela, palatino, A.CADERNOS)
folhas = grande.folhas_do_caderno
MED["10_palatino_primeira_folha_s"] = esperar(folhas)
MED["10_palatino_textos"] = folhas.rotulos["frente"].text()
foto(grande, "10-palatino-folha-1.png")
grande.reject()
rodar(0.3)

(AQUI / "prints.json").write_text(json.dumps(MED, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(MED, ensure_ascii=False, indent=1))
janela._fechar_a_janela_do_automatico()
janela.close()
