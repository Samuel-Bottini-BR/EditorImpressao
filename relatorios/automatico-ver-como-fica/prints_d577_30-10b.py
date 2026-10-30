"""Prints offscreen da D-577 depois do 2º teste do Samuel (30/10/2026): o antes é a folha crua
(sem filtro, sem nada) e a tela cheia tem o "comparar". Livro de teste dele (Na escola de Jesus),
capa = página 1 (no livro, em Preto e branco do teste da D-588).

O projeto é COPIADO da pasta de dados de teste para _tmp/localapp_30 a cada rodada (nunca usado
no lugar); o PDF do acervo só é lido.

  4-...  a capa na janela grande: o antes cru e o depois em Preto e branco + "Só as letras";
  5-...  a tela cheia com a linha, e com o "comparar" (Preto e branco e Mágico pro escolhidos),
         também com zoom.

Rodar: .venv\\Scripts\\python.exe relatorios\\automatico-ver-como-fica\\prints_d577_30-10b.py
"""
import os
import shutil
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DADOS = os.path.join(RAIZ, "_tmp", "localapp_30")
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
from core.filtros import MAGICO_PRO, PRETO_E_BRANCO  # noqa: E402
import ui.automatico as UA  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402

SAIDA = os.path.join(RAIZ, "relatorios", "automatico-ver-como-fica")


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


janela = JanelaPrincipal()
janela.resize(1600, 900)
janela.abrir_livro(PDF)
assentar()
t0 = time.monotonic()
while getattr(janela, "medida_ao_abrir", None) is not None and time.monotonic() - t0 < 900:
    app.processEvents()
    time.sleep(0.05)
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
print("antes", painel._antes[1].shape, "depois", painel._depois[1].shape)
grande.grab().save(os.path.join(SAIDA, "4-antes-cru-depois-preto-e-branco.png"))

painel.botao_tela_cheia.click()
tela = painel.tela_cheia
tela.setWindowState(Qt.WindowNoState)
tela.resize(1600, 900)
assentar()
tela.grab().save(os.path.join(SAIDA, "5-tela-cheia-antes-cru-depois-preto-e-branco.png"))
tela.botao_comparar.click()
esperar(painel)
assentar()
print("comparar:", tela.rotulo_a.text(), "|", tela.rotulo_b.text())
tela.grab().save(os.path.join(SAIDA, "5-tela-cheia-comparar-preto-e-branco.png"))
grande.radios_de_filtro[MAGICO_PRO].click()
esperar(painel)
assentar()
print("comparar:", tela.rotulo_a.text(), "|", tela.rotulo_b.text())
tela.grab().save(os.path.join(SAIDA, "5-tela-cheia-comparar-magico-pro.png"))
for _ in range(4):
    tela.botao_mais.click()
assentar()
tela.grab().save(os.path.join(SAIDA, "5-tela-cheia-comparar-magico-pro-com-zoom.png"))
tela.botao_comparar.click()
tela.accept()
assentar()
grande.botao_fechar.click()
assentar()
janela.close()
assentar()
for tarefa in list(UA._guardiao().tarefas):
    tarefa.wait(60000)
print("ok")
