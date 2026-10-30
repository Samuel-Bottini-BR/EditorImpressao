"""Prints offscreen da D-577 depois do 3º teste do Samuel (30/10/2026): a linha mostra o lado
para onde vai (à esquerda dela o depois, à direita o antes; os rótulos parados). Linha toda à
esquerda, toda à direita e no meio, na janela grande do Automático e no "antes / depois" da área
de trabalho. Livro de teste dele (Na escola de Jesus), capa = página 1.

O projeto é COPIADO da pasta de dados de teste para _tmp/localapp_30 a cada rodada (nunca usado
no lugar); o PDF do acervo só é lido.

Rodar: .venv\\Scripts\\python.exe relatorios\\automatico-ver-como-fica\\prints_d577_30-10c.py
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
from core.filtros import PRETO_E_BRANCO  # noqa: E402
import ui.automatico as UA  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402

SAIDA = os.path.join(RAIZ, "relatorios", "automatico-ver-como-fica")
LADOS = (("linha-toda-a-esquerda", 0.0), ("linha-no-meio", 0.5), ("linha-toda-a-direita", 1.0))


def assentar(n=5):
    for _ in range(n):
        app.processEvents()


def esperar(condicao, limite=900):
    t0 = time.monotonic()
    while time.monotonic() - t0 < limite:
        app.processEvents()
        if condicao():
            assentar()
            return
        time.sleep(0.02)
    raise SystemExit("nao terminou")


janela = JanelaPrincipal()
janela.resize(1600, 900)
janela.show()
janela.abrir_livro(PDF)
assentar()
esperar(lambda: getattr(janela, "medida_ao_abrir", None) is None)
tela = janela.tela_conferir
tela.ir_para_pagina(0)
assentar()

# --- a área de trabalho: o "antes / depois" da barra de baixo
tela.botao_antes_depois.click()
vista = tela.vista_antes_depois
esperar(lambda: vista.antes is not None and vista.depois is not None)
for nome, posicao in LADOS:
    vista.posicao = posicao
    vista.update()
    assentar()
    janela.grab().save(os.path.join(SAIDA, f"6-area-de-trabalho-{nome}.png"))
tela.botao_antes_depois.click()
assentar()

# --- a janela grande do Automático: só "Limpar a folha", Preto e branco + "Só as letras"
grande = janela.abrir_o_automatico()
grande.resize(1560, 860)
grande.show()
painel = grande.antes_e_depois
esperar(lambda: not painel.calculando())
for etapa in A.ETAPAS:
    item = grande.lista.item_da_etapa(etapa)
    q = Qt.Checked if etapa == A.LIMPAR else Qt.Unchecked
    if item.checkState() != q:
        item.setCheckState(q)
grande.radios_de_filtro[PRETO_E_BRANCO].click()
janela.estado_do_automatico.definir_opcao("misto_so_as_letras", True)
grande.mostrar_etapa(A.LIMPAR)
esperar(lambda: not painel.calculando())
for nome, posicao in LADOS:
    painel.visor.posicao = posicao
    painel.visor.update()
    assentar()
    grande.grab().save(os.path.join(SAIDA, f"7-automatico-{nome}.png"))
grande.botao_fechar.click()
assentar()
janela.close()
assentar()
for tarefa in list(UA._guardiao().tarefas):
    tarefa.wait(60000)
print("ok")
