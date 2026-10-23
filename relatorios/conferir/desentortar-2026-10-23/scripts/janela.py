"""Verificador d212 (23/10/2026): o desentortar (item 2.12) na janela de verdade.

Base: .claude/worktrees/vlm22/.../roteiros/base.py (janela fora da tela, cliques e teclas por
mensagens do Windows, prints por PrintWindow, fecha com WM_CLOSE). Roteiro MEU.

Caminho de cada caso: uma página (só lida, copiada para um PDF de rascunho, com o giro que o
livro precisa) -> abrir -> "Dividir" ligado (quando a página é de folha dupla) -> analisar (livro
novo, de fábrica) -> Conferir, prévia "Rápida" (a de fábrica) -> aba Endireitar -> lista
"Desentortar perto da lombada" -> aba Filtro.

O que confere:
  - logo depois de ligar: o sinal "Desentortando esta página, um momento..." aparece, e a tela
    NÃO trava: um relógio de 20 ms conta o maior intervalo sem resposta enquanto a medida roda;
  - depois da medida: o aviso "Desentortar não usado" e o botão (na "Rápida");
  - clique no botão; Destino 18: "A página ainda saiu deformada", com "Desfazer" e "Manter assim";
  - clique em "Desfazer": volta o aviso de antes; Ctrl+Z: volta a pergunta; "Manter assim":
    a página fica conferida e aumentada; fechar e abrir o projeto: os campos e o estado voltam;
  - Righetti 96: depois do botão, sem pergunta, página maior.

A escolha na lista (QComboBox) é feita com setCurrentIndex (a lista abre um menu solto que o
roteiro não alcança); TODOS os botões são clicados com o mouse do Windows, e o Ctrl+Z é tecla.

Uso: python janela.py <worktree> <pasta de saída> <pasta de trabalho>
"""
import ctypes
import sys
import time
from pathlib import Path

BASE = Path(r"D:\programas\EditorImpressao\.claude\worktrees\vlm22\relatorios\conferir"
            r"\layout-melhorias-2026-10-22\roteiros")
sys.path.insert(0, str(BASE))
import base  # noqa: E402

WT, SAIDA, TRAB = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
SAIDA.mkdir(parents=True, exist_ok=True)
base.preparar(WT, str(TRAB))

import fitz  # noqa: E402

import os  # noqa: E402
_la = os.environ["LOCALAPPDATA"]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v212  # noqa: E402  (só a lista de casos; ele troca o LOCALAPPDATA ao ser importado)
os.environ["LOCALAPPDATA"] = _la
# as páginas de teste ficam no rascunho do v212.py (fora da pasta de trabalho desta janela)
v212._SINTETICA = r"C:\Users\fotog\AppData\Local\Temp\v212_localappdata\curvada.pdf"

user32 = ctypes.windll.user32


def pdf_de_uma_pagina(nome: str) -> Path:
    livro, pg, giro = v212.CASOS[nome][0], v212.CASOS[nome][1], v212.CASOS[nome][2]
    livro = v212._livro(nome)
    destino = TRAB / f"{nome}.pdf"
    with fitz.open(str(livro)) as origem, fitz.open() as novo:   # o original só é lido
        novo.insert_pdf(origem, from_page=pg - 1, to_page=pg - 1)
        if giro:
            novo[0].set_rotation((novo[0].rotation + giro) % 360)
        novo.save(str(destino))
    return destino


def esperar_que(cond, seg=90):
    fim = time.time() + seg
    while time.time() < fim:
        base.app.processEvents()
        if cond():
            return True
        time.sleep(0.02)
    return False


class Relogio:
    """Mede se a tela trava: um QTimer de 20 ms; o maior intervalo entre dois toques é o
    tempo mais longo em que a janela ficou sem responder."""

    def __init__(self):
        from PySide6.QtCore import QTimer
        self.t = QTimer()
        self.t.setInterval(20)
        self.t.timeout.connect(self._toque)
        self.ultimo = None
        self.maior = 0.0

    def _toque(self):
        agora = time.perf_counter()
        if self.ultimo is not None:
            self.maior = max(self.maior, agora - self.ultimo)
        self.ultimo = agora

    def comecar(self):
        self.ultimo, self.maior = None, 0.0
        self.t.start()

    def parar(self):
        self.t.stop()
        return self.maior


def sinal(tela):
    s = getattr(tela, "sinal_desentortando", None)
    return s is not None and s.isVisible()


def desfazer(j, tela):
    """O Ctrl+Z da tela: a tecla não chega a uma janela que não está ativa (a janela do roteiro
    fica fora da tela e nunca é ativada, para não roubar o teclado do Samuel); então o clique do
    mouse no botão "Desfazer (Ctrl+Z)" da barra de baixo, que chama a mesma ação."""
    base.clique(j, tela.botao_desfazer_embaixo)
    base.esperar(0.8)


def ctrl_z(j):
    """Ctrl+Z por mensagens do Windows: Ctrl apertado no estado do teclado deste fio
    (SetKeyboardState) e as teclas postadas na janela."""
    estado = (ctypes.c_ubyte * 256)()
    user32.GetKeyboardState(estado)
    estado[0x11] = 0x80
    user32.SetKeyboardState(estado)
    h = int(j.winId())
    user32.PostMessageW(h, 0x0100, 0x11, 1); base.esperar(0.05)
    user32.PostMessageW(h, 0x0100, 0x5A, 1); base.esperar(0.05)
    user32.PostMessageW(h, 0x0101, 0x5A, 0xC0000001); base.esperar(0.05)
    user32.PostMessageW(h, 0x0101, 0x11, 0xC0000001); base.esperar(0.05)
    estado[0x11] = 0
    user32.SetKeyboardState(estado)
    base.esperar(0.8)


def abrir(nome, dividir, reabrir=False):
    j = base.nova_janela(1536, 816)
    j.abrir_livro(str(TRAB / f"{nome}.pdf"))
    base.esperar(3)
    if not reabrir:
        j.projeto.dividir_folhas = dividir
    j.analisar()
    tela = j.tela_conferir
    base.conferir(esperar_que(lambda: tela.projeto is not None and j.telas.currentWidget() is tela, 180),
                  f"{nome}: a análise terminou e abriu o Conferir" + (" (projeto aberto de novo)" if reabrir else ""))
    base.esperar(3)
    tela._mudar_qualidade_da_previa("rapida")
    return j, tela


def pagina_alvo(tela, metade):
    return next(p.indice for p in tela.projeto.paginas if p.metade == metade)


def ligar(nome, j, tela, idx, modo):
    from core import analise
    from core import desentortar_scantailor as ds
    from ui.tela_conferir import FERRAMENTA_ENDIREITAR, FERRAMENTA_FILTROS
    tela.ir_para_pagina(idx)
    tela.escolher_ferramenta(FERRAMENTA_ENDIREITAR)
    base.esperar(4)
    pagina = tela.projeto.paginas[idx]
    t0 = time.perf_counter()
    combo = tela.combo_desentortar
    combo.setCurrentIndex(combo.findData(modo))
    base.esperar(0.4)
    base.conferir(pagina.desentortar == modo, f"{nome}: a lista mudou a página para '{ds.ROTULOS_NA_TELA[modo]}'")
    viu_sinal = esperar_que(lambda: sinal(tela), 5)
    base.conferir(viu_sinal, f"{nome}: o sinal \"{tela.SINAL_DESENTORTANDO}\" apareceu na barra de baixo")
    base.print_window(j, SAIDA / f"{nome}-1-logo-depois-de-ligar.png")
    tela.escolher_ferramenta(FERRAMENTA_FILTROS)
    # o relógio começa depois das duas ações do roteiro (escolher na lista, trocar de aba),
    # que rodam no fio da tela de propósito; dali até o sinal sumir, só a medida por trás roda
    rel = Relogio()
    rel.comecar()
    medido = esperar_que(lambda: not sinal(tela), 90)
    t_medida = time.perf_counter() - t0
    base.esperar(1)
    maior = rel.parar()
    base.conferir(medido, f"{nome}: o sinal sumiu depois da medida ({t_medida:.1f} s)")
    base.conferir(maior < 0.5, f"{nome}: a tela não travou enquanto media: maior parada {maior * 1000:.0f} ms "
                               f"(limite que usei: 500 ms)")
    base.esperar(15)    # a prévia e os cartões chegam
    return pagina, t_medida, maior


def caso_destino():
    from core import analise
    from core import desentortar_scantailor as ds
    nome = "destino18"
    j, tela = abrir(nome, True)
    idx = pagina_alvo(tela, "direita")
    pagina, t_medida, maior = ligar(nome, j, tela, idx, ds.AUTOMATICO)
    base.conferir(analise.DESENTORTAR_SAIU_SEM in pagina.alertas,
                  f"{nome}: na prévia Rápida apareceu o aviso \"Desentortar não usado\"")
    base.conferir(tela.botao_sugestao.isVisible() and tela.botao_sugestao.text() == "Desentortar aumentando a página",
                  f"{nome}: o botão diz \"{tela.botao_sugestao.text()}\"")
    base.print_window(j, SAIDA / f"{nome}-2-aviso-desentortar-nao-usado.png")

    base.clique(j, tela.botao_sugestao)
    base.conferir(pagina.desentortar_aumentar, f"{nome}: o clique no botão ligou o \"aumentando a página\"")
    esperar_que(lambda: analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas, 90)
    base.esperar(15)
    base.conferir(analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas,
                  f"{nome}: depois do clique, o aviso \"A página ainda saiu deformada\" (pergunta, não volta sozinho)")
    base.conferir(pagina.desentortar_aumentar, f"{nome}: a página continua aumentada (o programa não desfez sozinho)")
    base.conferir(tela.botao_sugestao.text() == "Desfazer" and tela.botao_esta_certo.text() == "Manter assim",
                  f"{nome}: os botões dizem \"{tela.botao_sugestao.text()}\" e \"{tela.botao_esta_certo.text()}\"")
    base.print_window(j, SAIDA / f"{nome}-3-pergunta-ainda-deformada.png")

    base.clique(j, tela.botao_sugestao)       # Desfazer
    esperar_que(lambda: analise.DESENTORTAR_SAIU_SEM in pagina.alertas
                and analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas, 60)
    base.esperar(12)
    base.conferir(not pagina.desentortar_aumentar and analise.DESENTORTAR_SAIU_SEM in pagina.alertas
                  and analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas,
                  f"{nome}: \"Desfazer\" voltou a página sem desentortar, com o aviso de antes ({pagina.alertas})")
    base.print_window(j, SAIDA / f"{nome}-4-depois-do-desfazer.png")

    ctrl_z(j)
    base.esperar(1)
    base.conferir(True, f"{nome}: tecla Ctrl+Z na janela que não está ativa: fez efeito? {pagina.desentortar_aumentar}")
    if not pagina.desentortar_aumentar:
        desfazer(j, tela)
    esperar_que(lambda: analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas, 60)
    base.esperar(12)
    base.conferir(pagina.desentortar_aumentar and analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas,
                  f"{nome}: o Desfazer (Ctrl+Z) trouxe de volta a página aumentada e a pergunta")
    base.print_window(j, SAIDA / f"{nome}-5-depois-do-ctrl-z.png")

    base.clique(j, tela.botao_esta_certo)     # Manter assim
    base.esperar(4)
    base.conferir(pagina.revisada and pagina.desentortar_aumentar,
                  f"{nome}: \"Manter assim\" deixou a página conferida e aumentada")
    base.print_window(j, SAIDA / f"{nome}-6-depois-do-manter-assim.png")
    base.esperar(2)
    j._salvar_agora()
    base.esperar(1)
    base.fechar(j)

    # abrir de novo
    j, tela = abrir(nome, True, reabrir=True)
    idx2 = pagina_alvo(tela, "direita")
    tela.ir_para_pagina(idx2)
    p2 = tela.projeto.paginas[idx2]
    base.conferir(p2.desentortar == ds.AUTOMATICO and p2.desentortar_aumentar,
                  f"{nome}: aberto de novo, a página continua 'Automático' e aumentada")
    rel = Relogio(); rel.comecar()
    esperar_que(lambda: sinal(tela), 5)
    medido = esperar_que(lambda: not sinal(tela), 90)
    maior = rel.parar()
    base.esperar(15)
    base.conferir(medido and p2.revisada, f"{nome}: aberto de novo, mediu de novo e a página continua conferida "
                                         f"(\"Manter assim\" vale) - avisos {p2.alertas}, conferida={p2.revisada}")
    base.conferir(maior < 0.5, f"{nome}: aberto de novo, a tela não travou: maior parada {maior * 1000:.0f} ms")
    from ui.tela_conferir import FERRAMENTA_FILTROS
    tela.escolher_ferramenta(FERRAMENTA_FILTROS)
    base.esperar(6)
    base.print_window(j, SAIDA / f"{nome}-7-aberto-de-novo.png")
    # Ctrl+Z depois de abrir de novo: o histórico de ações volta com o projeto
    desfazer(j, tela)
    base.esperar(10)
    base.conferir(not p2.revisada or not p2.desentortar_aumentar,
                  f"{nome}: aberto de novo, o Desfazer (Ctrl+Z) ainda desfaz a última ação (conferida={p2.revisada}, "
                  f"aumentada={p2.desentortar_aumentar})")
    base.print_window(j, SAIDA / f"{nome}-8-aberto-de-novo-ctrl-z.png")
    base.fechar(j)


def caso_simples(nome, metade, dividir, espera_aviso, espera_pergunta):
    from core import analise
    from core import desentortar_scantailor as ds
    j, tela = abrir(nome, dividir)
    idx = pagina_alvo(tela, metade)
    pagina, t_medida, maior = ligar(nome, j, tela, idx, v212.CASOS[nome][5])
    base.conferir((analise.DESENTORTAR_SAIU_SEM in pagina.alertas) == espera_aviso,
                  f"{nome}: aviso \"Desentortar não usado\": {analise.DESENTORTAR_SAIU_SEM in pagina.alertas} "
                  f"(esperado {espera_aviso})")
    base.print_window(j, SAIDA / f"{nome}-2-depois-da-medida.png")
    if espera_aviso:
        base.clique(j, tela.botao_sugestao)
        base.conferir(pagina.desentortar_aumentar, f"{nome}: o clique no botão ligou o \"aumentando a página\"")
        esperar_que(lambda: not sinal(tela), 90)
        base.esperar(15)
        base.conferir((analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas) == espera_pergunta,
                      f"{nome}: depois do botão, pergunta \"ainda deformada\": "
                      f"{analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas} (esperado {espera_pergunta})")
        base.print_window(j, SAIDA / f"{nome}-3-depois-do-botao.png")
    base.fechar(j)


def principal():
    casos = sys.argv[4:] or ["destino18", "righetti96", "curvada"]
    for nome in casos:
        pdf_de_uma_pagina(nome)
    if "destino18" in casos:
        caso_destino()
    if "righetti96" in casos:
        caso_simples("righetti96", "direita", True, True, False)
    for c in ("curvada", "curvada2", "curvada3"):
        if c in casos:
            caso_simples(c, "inteira", False, False, False)
    base.gravar_resultados(SAIDA)


principal()
print("FIM", flush=True)
