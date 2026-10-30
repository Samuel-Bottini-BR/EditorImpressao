"""Prints offscreen da janela grande do Automático com o antes e depois (D-577).
Roda com LOCALAPPDATA apontando para _tmp (nunca a pasta de dados de verdade)."""
import os, sys, time
# o script mora em relatorios/automatico-ver-como-fica/; tudo o que ele grava (dados do
# programa, projeto, o livro copiado em _tmp/livro/escola.pdf) fica em _tmp/ da cópia
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AQUI = os.path.join(RAIZ, "_tmp")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"
os.environ["LOCALAPPDATA"] = os.path.join(AQUI, "localapp_prints")
os.makedirs(os.environ["LOCALAPPDATA"], exist_ok=True)
sys.path.insert(0, RAIZ)
from PySide6.QtWidgets import QApplication
app = QApplication([])
import projetos
from pathlib import Path
pasta = Path(AQUI) / "projetos_prints"
pasta.mkdir(exist_ok=True)
projetos.pasta_dos_projetos = lambda: pasta
from core import automatico as A
from core.filtros import PRETO_E_BRANCO, MAGICO_PRO
from ui.janela_principal import JanelaPrincipal
from PySide6.QtCore import Qt

SAIDA = Path(RAIZ) / "relatorios" / "automatico-ver-como-fica"
PDF = os.path.join(AQUI, "livro", "escola.pdf")

def assentar(n=5):
    for _ in range(n):
        app.processEvents()

def esperar(painel, limite=600):
    t0 = time.monotonic()
    while time.monotonic() - t0 < limite:
        app.processEvents()
        if not painel.calculando():
            assentar()
            if not painel.calculando():
                return time.monotonic() - t0
        time.sleep(0.02)
    raise SystemExit("nao terminou")

janela = JanelaPrincipal()
janela.resize(1600, 900)
janela.abrir_livro(PDF)
assentar()
t0 = time.monotonic()
while getattr(janela, "medida_ao_abrir", None) is not None and time.monotonic() - t0 < 900:
    app.processEvents(); time.sleep(0.05)
print("medida ao abrir: %.1fs" % (time.monotonic() - t0))
janela.tela_conferir.ir_para_pagina(12)
t = time.perf_counter(); c = A.copia_para_a_previa(janela.projeto); print("copia do projeto: %.3fs" % (time.perf_counter() - t), len(janela.projeto.paginas), "paginas")
grande = janela.abrir_o_automatico()
grande.resize(1560, 860)
grande.show()
painel = grande.antes_e_depois
print("abrir (antes e depois sem etapa): %.1fs" % esperar(painel))

def marcar(etapas, filtro=None):
    for etapa in A.ETAPAS:
        item = grande.lista.item_da_etapa(etapa)
        q = Qt.Checked if etapa in etapas else Qt.Unchecked
        if item.checkState() != q:
            item.setCheckState(q)
    if filtro is not None:
        grande.radios_de_filtro[filtro].click()

marcar({A.ENDIREITAR, A.CORTAR, A.LIMPAR, A.GRAVURAS}, PRETO_E_BRANCO)
grande.mostrar_etapa(A.LIMPAR)
assentar()
grande.grab().save(str(SAIDA / "2-bolinha-calculando.png"))
print("bolinha girando no print:", painel.bolinha.carregando)
print("receita de sempre, P&B (1a vez, pagina 13): %.1fs" % esperar(painel))
painel.visor.posicao = 0.5
painel.visor.update()
assentar()
grande.grab().save(str(SAIDA / "1-antes-e-depois-preto-e-branco.png"))
# trocar a opcao: Magico pro
grande.radios_de_filtro[MAGICO_PRO].click()
print("trocar para Magico pro: %.1fs" % esperar(painel))
grande.grab().save(str(SAIDA / "3-antes-e-depois-magico-pro.png"))
# folhear: proximas paginas
tempos = []
for _ in range(3):
    painel.virar(1)
    tempos.append(esperar(painel))
print("folhear (antes + depois, Magico pro):", ["%.1fs" % x for x in tempos])
grande.radios_de_filtro[PRETO_E_BRANCO].click()
print("voltar a P&B na pagina %d: %.1fs" % (painel._indice + 1, esperar(painel)))
painel.visor.posicao = 0.35
painel.visor.update(); assentar()
grande.grab().save(str(SAIDA / "4-outra-pagina-linha-arrastada.png"))
grande.botao_fechar.click()
assentar()
janela.close()
assentar()
from ui.automatico import _guardiao
for tarefa in list(_guardiao().tarefas):
    tarefa.wait(60000)
print("ok")
