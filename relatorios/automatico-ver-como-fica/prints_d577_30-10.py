"""Prints offscreen do conserto da D-577 depois do teste do Samuel de 30/10/2026, com o livro de
teste dele (Na escola de Jesus, a capa = página 1, mexida à mão no filtro).

O projeto é COPIADO da pasta de dados de teste (dados-teste-rodada-de-consertos) para
_tmp/localapp_30 da cópia a cada rodada (nunca usado no lugar); o PDF do acervo só é lido.

  1-...  coisa 1: a capa mexida à mão, "Limpar a folha" em Preto e branco + "Só as letras" e
         depois Mágico pro. "antes do conserto" = o pedido da prévia pulando as mexidas (como o
         código de antes fazia: EstadoDoAutomatico.pedido() com pular_mexidas=True).
  2-...  coisa 2: o "tela cheia" de antes (TelaCheiaDoPDF, a folha crua) e o de agora
         (TelaCheiaDoAntesEDepois), com zoom e depois de folhear.
  3-...  coisa 3: o antes da capa ao trocar o filtro (não muda).
  Também lista as janelas soltas visíveis com o tela cheia aberto (o quadro laranja do a-08).

Rodar: .venv\\Scripts\\python.exe relatorios\\automatico-ver-como-fica\\prints_d577_30-10.py
"""
import hashlib
import os
import shutil
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP = os.path.join(RAIZ, "_tmp")
DADOS = os.path.join(TMP, "localapp_30")
ORIGEM = (r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
          r"\projetos\Na escola de Jesus - Catecismo explicado com imagens")
PDF = (r"D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
       r"Na escola de Jesus - Catecismo explicado com imagens..pdf")
destino = os.path.join(DADOS, "EditorImpressao", "projetos", os.path.basename(ORIGEM))
if os.path.isdir(destino):
    shutil.rmtree(destino)                     # só a cópia em _tmp, feita por este script
shutil.copytree(ORIGEM, destino)

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"
os.environ["LOCALAPPDATA"] = DADOS
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication([])
from core import automatico as A  # noqa: E402
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
import ui.automatico as UA  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402

SAIDA = os.path.join(RAIZ, "relatorios", "automatico-ver-como-fica")
QUAL = sys.argv[1] if len(sys.argv) > 1 else "depois"     # "antes" = como o código de antes


def assentar(n=5):
    for _ in range(n):
        app.processEvents()


def esperar(painel, limite=900):
    t0 = time.monotonic()
    while time.monotonic() - t0 < limite:
        app.processEvents()
        if not painel.calculando():
            assentar()
            if not painel.calculando():
                return
        time.sleep(0.02)
    raise SystemExit("nao terminou")


def resumo(img):
    return "nada" if img is None else hashlib.md5(img.tobytes()).hexdigest()[:8]


if QUAL == "antes":
    # o código de antes: a prévia saía com o pedido de fábrica do estado (pulando as mexidas)
    original = UA.EstadoDoAutomatico.pedido
    UA.EstadoDoAutomatico.pedido = lambda self, pular_mexidas=True, desligar=False: original(
        self, True, desligar)

janela = JanelaPrincipal()
janela.resize(1600, 900)
janela.abrir_livro(PDF)
assentar()
t0 = time.monotonic()
while getattr(janela, "medida_ao_abrir", None) is not None and time.monotonic() - t0 < 900:
    app.processEvents()
    time.sleep(0.05)
print("capa mexida a mao:", janela.projeto.paginas[0].mexida_a_mao)
janela.tela_conferir.ir_para_pagina(0)
assentar()
grande = janela.abrir_o_automatico()
grande.resize(1560, 860)
grande.show()
painel = grande.antes_e_depois
esperar(painel)
for etapa in A.ETAPAS:                      # só "Limpar a folha", como no teste dele
    item = grande.lista.item_da_etapa(etapa)
    q = Qt.Checked if etapa == A.LIMPAR else Qt.Unchecked
    if item.checkState() != q:
        item.setCheckState(q)
grande.radios_de_filtro[PRETO_E_BRANCO].click()
janela.estado_do_automatico.definir_opcao("misto_so_as_letras", True)
grande.mostrar_etapa(A.LIMPAR)
esperar(painel)
painel.visor.posicao = 0.5
painel.visor.update()
assentar()
antes0 = painel._antes[1]
grande.grab().save(os.path.join(SAIDA, f"1-{QUAL}-do-conserto-capa-preto-e-branco.png"))
print("P&B:", "antes", resumo(painel._antes[1]), "depois", resumo(painel._depois[1]))
grande.radios_de_filtro[MAGICO_PRO].click()
esperar(painel)
grande.grab().save(os.path.join(SAIDA, f"1-{QUAL}-do-conserto-capa-magico-pro.png"))
print("Magico pro:", "antes", resumo(painel._antes[1]), "depois", resumo(painel._depois[1]))
for filtro in (MELHORAR, ORIGINAL, PRETO_E_BRANCO):
    grande.radios_de_filtro[filtro].click()
    esperar(painel)
    print(filtro, "antes", resumo(painel._antes[1]), "igual ao primeiro:",
          painel._antes[1] is antes0 or bool((painel._antes[1] == antes0).all()),
          "depois", resumo(painel._depois[1]))
if QUAL == "depois":
    grande.radios_de_filtro[MAGICO_PRO].click()
    esperar(painel)
    painel.visor.posicao = 0.35
    grande.grab().save(os.path.join(SAIDA, "3-depois-do-conserto-o-antes-fica-o-mesmo-magico-pro.png"))


def soltas(rotulo):
    """As janelas de cima visíveis (procura o quadro solto do a-08)."""
    vis = [w for w in app.topLevelWidgets() if w.isVisible()]
    print(rotulo, [(type(w).__name__, w.objectName(), w.windowTitle(), w.geometry().getRect()) for w in vis])


soltas("janelas visiveis com a janela grande:")
if QUAL == "antes":
    from core.pdf_io import abrir_pdf
    from ui.widgets.folhear_pdf import TelaCheiaDoPDF

    doc = abrir_pdf(janela.projeto.caminho_entrada)
    tela = TelaCheiaDoPDF(doc, 0, painel)          # o que o "tela cheia" abria (exec bloquearia)
    tela.setWindowState(Qt.WindowNoState)
    tela.resize(1600, 900)
    assentar()
    soltas("janelas visiveis com o tela cheia de antes:")
    tela.grab().save(os.path.join(SAIDA, "2-antes-do-conserto-tela-cheia-folha-crua.png"))
    tela.accept()
    doc.close()
else:
    painel.botao_tela_cheia.click()
    tela = painel.tela_cheia
    tela.setWindowState(Qt.WindowNoState)
    tela.resize(1600, 900)
    assentar()
    soltas("janelas visiveis com o tela cheia novo:")
    tela.grab().save(os.path.join(SAIDA, "2-depois-do-conserto-tela-cheia-antes-e-depois.png"))
    tela.botao_mais.click()
    tela.botao_mais.click()
    tela.botao_mais.click()
    assentar()
    barra = tela.rolagem.horizontalScrollBar()
    barra.setValue(int(barra.maximum() * 0.45))
    tela.rolagem.verticalScrollBar().setValue(int(tela.rolagem.verticalScrollBar().maximum() * 0.3))
    assentar()
    tela.grab().save(os.path.join(SAIDA, "2-depois-do-conserto-tela-cheia-com-zoom.png"))
    tela.botao_caber.click()
    tela.botao_proxima.click()
    esperar(painel)
    assentar()
    tela.grab().save(os.path.join(SAIDA, "2-depois-do-conserto-tela-cheia-folheou-pagina-2.png"))
    print("tela cheia:", tela.contador.text())
    tela.accept()
    assentar()
grande.botao_fechar.click()
assentar()
janela.close()
assentar()
for tarefa in list(UA._guardiao().tarefas):
    tarefa.wait(60000)
print("ok")
