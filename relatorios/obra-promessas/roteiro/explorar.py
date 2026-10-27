"""Exploração (verificador, 26/10/2026): lista todos os botões de cada tela, sem janela visível."""
import os, sys, uuid
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
os.environ["QT_QPA_PLATFORM"] = "offscreen"
dados = RAIZ / "saida_teste" / "explorar" / uuid.uuid4().hex[:6]
dados.mkdir(parents=True)
os.environ["LOCALAPPDATA"] = str(dados)
import fitz
from PySide6.QtWidgets import QApplication, QAbstractButton
app = QApplication([])
from core import pipeline
from ui.janela_principal import JanelaPrincipal

def pdf(folhas=3):
    c = dados / "Livro de Teste.pdf"
    d = fitz.open()
    for i in range(folhas):
        p = d.new_page(width=400, height=560); p.insert_text((40, 60), f"folha {i}", fontsize=14)
    d.save(str(c)); d.close(); return c

def dump(raiz, rotulo, so_visiveis=False):
    print(f"\n===== {rotulo} =====")
    for b in raiz.findChildren(QAbstractButton):
        if so_visiveis and not b.isVisibleTo(raiz):
            continue
        cadeia = []
        w = b.parentWidget()
        while w is not None and w is not raiz and len(cadeia) < 4:
            cadeia.append(type(w).__name__); w = w.parentWidget()
        print(f"{type(b).__name__:14} vis={int(b.isVisibleTo(raiz))} en={int(b.isEnabled())} "
              f"txt={b.text()!r} tip={b.toolTip()[:60]!r} obj={b.objectName()!r} <- {'/'.join(cadeia)}")

j = JanelaPrincipal(); j.resize(1280, 800); j.show(); app.processEvents()
dump(j.tela_inicio, "tela_inicio (vazia)")
caminho = pdf()
j.abrir_livro(str(caminho)); app.processEvents()
dump(j.tela_opcoes, "tela_opcoes")
for nome in ("cx_dividir", "cx_cortar", "cx_endireitar", "cx_limpar"):
    getattr(j.tela_opcoes, nome).setChecked(False)
j.projeto.detectar_regioes = False
j._analise_pronta(pipeline.analisar_projeto(j.projeto)); 
for _ in range(10): app.processEvents()
dump(j.tela_conferir, "tela_conferir", so_visiveis=False)
dump(j.tela_final, "tela_final")
dump(j.tela_progresso, "tela_progresso")
j._voltar_das_opcoes() if False else None
