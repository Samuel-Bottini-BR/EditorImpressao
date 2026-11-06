"""Girar a página numa folha dividida (D-618) na janela de VERDADE (plataforma Windows), posta
fora da tela: cliques e teclas por mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/
base.py), prints por PrintWindow. Mesmo jeito do piloto do mover-parou (04/11/2026).

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF
aponta para a cópia do PDF.

Fases:
    antes   o caminho do Samuel (prints a-70 a a-73): Cortar as bordas, página 14 (folha 7
            dividida), "¼ à esquerda" do Propriedades três vezes; mede a página 13 e a 14.
    depois  o mesmo, e mais: canto, Ctrl+Seta, meia volta, Ctrl+Z, a página 13 igual,
            o que funcionava ao redor (folha inteira, aplicar em, Endireitar, Dividir).
    folha   a folha inteira (não dividida): mede a proporção antes e depois de girar.

Rodar (na cópia girar-pagina):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\girar-pagina\\piloto.py <fase>
"""
from __future__ import annotations

import ctypes
import json
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

# a pasta de trabalho (apagada e refeita a cada fase): só a deste piloto, no scratchpad da sessão
SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd\e4fd3df2-ffc2-4ff8-9d6b-c5c2f4b2d0ca\scratchpad\girar-pagina-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
FASE = sys.argv[1] if len(sys.argv) > 1 else "antes"
(AQUI / "prints").mkdir(exist_ok=True)
LOG = open(AQUI / f"anotacoes-{FASE}.txt", "w", encoding="utf-8")
N = [0]
VK_LEFT, VK_RIGHT = 0x25, 0x27


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{FASE}-{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas que abrem por cima: anota o texto e clica no botão padrão."""

    def __init__(self):
        from PySide6.QtCore import QTimer
        self.ocupado = False
        self.t = QTimer(); self.t.setInterval(250); self.t.timeout.connect(self.olhar); self.t.start()

    def olhar(self):
        if self.ocupado:
            return
        from PySide6.QtWidgets import QApplication, QMessageBox
        for w in QApplication.topLevelWidgets():
            try:
                if not w.isVisible() or w.property("_visto") or not isinstance(w, QMessageBox):
                    continue
            except RuntimeError:
                continue
            w.setProperty("_visto", True)
            self.ocupado = True
            try:
                base.esperar(0.5)
                anotar("caixa", {"titulo": w.windowTitle(), "texto": w.text(),
                                 "botoes": [b.text() for b in w.buttons()]})
                b = w.defaultButton() or w.buttons()[0]
                base.clique(w, b)
            finally:
                self.ocupado = False
            return


def preparar_copia() -> Path:
    """Copia o projeto e o PDF para a pasta de trabalho; o caminho do PDF vai para a cópia."""
    livros = base.TRAB / "livros"
    livros.mkdir(parents=True, exist_ok=True)
    pdf = livros / GRADUS.name
    if not pdf.exists():
        shutil.copy2(GRADUS, pdf)
    destino = base.TRAB / "projetos" / PROJ_ORIGEM.name
    if destino.exists():
        shutil.rmtree(destino)               # só a cópia, na pasta de trabalho deste script
    shutil.copytree(PROJ_ORIGEM, destino)
    for nome in ("projeto.json", "resumo.json"):
        arq = destino / nome
        dados = json.loads(arq.read_text(encoding="utf-8"))
        dados["caminho_entrada"] = str(pdf).replace("\\", "/")
        if "pasta" in dados:
            dados["pasta"] = str(destino)
        if "miniatura" in dados:
            dados["miniatura"] = str(destino / "capa.png")
        arq.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    return destino


def esperar_tela(j, limite=300):
    from ui.janela_principal import CONFERIR
    t = time.time()
    while time.time() - t < limite:
        base.esperar(0.3)
        if j.telas.currentIndex() == CONFERIR and j.tela_conferir._pronta():
            break
    base.esperar(2.0)
    return round(time.time() - t, 1)


def esperar_previa(j, limite=60):
    """Espera a prévia da ferramenta da vez chegar."""
    t0 = time.time()
    base.esperar(0.5)
    while time.time() - t0 < limite:
        t = j.tela_conferir
        vis = getattr(t, "visualizadores", {}).get(t.aba_atual) or t.area_imagem.currentWidget()
        if getattr(vis, "_pixmap", 1) is not None and not getattr(vis, "carregando", False):
            break
        base.esperar(0.2)
    base.esperar(1.0)


_DOC = {}


def medir_paginas(j, indices=(12, 13)) -> dict:
    """Mede, pela MESMA conta do programa (core/pipeline.preparar_para_recorte, 60 DPI), a
    página como a ferramenta Cortar a mostra: tamanho, proporção, quanto dela é branco, e um
    resumo da imagem (para saber se a outra página mudou)."""
    import hashlib

    import numpy as np

    from core import pipeline
    from core.pdf_io import abrir_pdf, pagina_para_array
    pr = j.projeto
    if "doc" not in _DOC:
        _DOC["doc"] = abrir_pdf(pr.caminho_entrada)
    doc = _DOC["doc"]
    saida = {}
    for i in indices:
        pg = pr.paginas[i]
        f = pr.folhas[pg.folha]
        img = pagina_para_array(doc, f.indice, 60)
        base_ = pipeline.preparar_para_recorte(img, f, pg, pr)
        cinza = base_.mean(axis=2) if base_.ndim == 3 else base_
        saida[f"pagina {i + 1}"] = {
            "folha": f.indice + 1, "metade": pg.metade, "rotacao_da_folha": f.rotacao,
            "giro_da_pagina": getattr(pg, "giro_da_pagina", "(nao existe)"),
            "linha": f.posicao_corte, "recorte": pg.recorte,
            "altura x largura": list(base_.shape[:2]),
            "proporcao (larg/alt)": round(base_.shape[1] / base_.shape[0], 3),
            "tinta (% escuro)": round(float((cinza < 128).mean() * 100), 2),
            "resumo": hashlib.md5(np.ascontiguousarray(base_).tobytes()).hexdigest()[:10],
        }
    return saida


def estado(j) -> dict:
    t = j.tela_conferir
    return {"aba": t.aba_atual, "pagina": t.indice_pagina + 1, "folha": t.indice_folha + 1,
            "mostrar": t.mostrar, "feitas": len(t.acoes.feitas) if t.acoes else None,
            "desfazer": t.acoes.descricao_desfazer() if t.acoes else None}


def ctrl(j, tecla_vk):
    h = int(j.winId())
    VK_CONTROL, VK_LCONTROL = 0x11, 0xA2
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, 0x0100, VK_CONTROL, 1); base.esperar(0.05)
    # as setas sao teclas "estendidas" (bit 24 do lParam): sem ele o Windows as
    # entrega como as do teclado numerico e o atalho Ctrl+Seta nao casa
    ext = 0x01000000 if tecla_vk in (VK_LEFT, VK_RIGHT) else 0
    base.user32.PostMessageW(h, 0x0100, tecla_vk, 1 | ext); base.esperar(0.05)
    base.user32.PostMessageW(h, 0x0101, tecla_vk, 0xC0000001 | ext); base.esperar(0.05)
    base.user32.PostMessageW(h, 0x0101, VK_CONTROL, 0xC0000001); base.esperar(0.3)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0
    base.user32.SetKeyboardState(est); base.esperar(1.5)


def mostrar(j, qual):
    from ui.tela_conferir import DUAS, UMA
    t = j.tela_conferir
    base.clique(j, t.botoes_mostrar[UMA if qual == "uma" else DUAS]); base.esperar(1.5)


def ferramenta(j, letra):
    base.tecla(j, ord(letra)); base.esperar(1.5)


def ir_pagina(j, numero):
    """Vai à página `numero` (1...) clicando a miniatura da tira."""
    t = j.tela_conferir
    i = numero - 1
    mapa = getattr(t.tira, "_miniaturas", [])
    if 0 <= i < len(mapa):
        mini = mapa[i]
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(1.0)
    if t.indice_pagina != i:
        anotar("tira-nao-levou; vou pelo programa", {"queria": numero, "estou": t.indice_pagina + 1})
        t.ir_para_pagina(i); base.esperar(1.0)
    esperar_previa(j)


def girar_painel(j, giro):
    from core import girar
    b = j.tela_conferir.barra_girar.botoes_de_giro[giro]
    base.clique(j, b); esperar_previa(j)


def girar_canto(j, giro):
    b = j.tela_conferir.girar_do_canto.botoes_de_giro[giro]
    base.clique(j, b); esperar_previa(j)


def abrir():
    # limpar=True: a pasta de trabalho deste piloto (no scratchpad) comeca vazia a cada fase;
    # com limpar=False o historico.json de uma fase anterior fazia o livro abrir outro trabalho
    base.preparar(str(RAIZ), str(SCRATCH), limpar=True)
    import projetos
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    porteiro = Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    return j, porteiro


def passo(j, nome):
    anotar(nome, {"estado": estado(j), "medidas": medir_paginas(j)})
    p(j, nome)


def fase_antes(j):
    """O caminho do Samuel: Cortar as bordas, página 14, ¼ à esquerda três vezes."""
    from core import girar
    ferramenta(j, "X"); esperar_previa(j)
    ir_pagina(j, 14)
    passo(j, "cortar-pagina14")
    for n in range(1, 4):
        girar_painel(j, girar.GIRO_ESQUERDA)
        passo(j, f"esquerda-{n}")
    ctrl(j, ord("Z")); esperar_previa(j)
    passo(j, "ctrl-z")


def fase_depois(j):
    """O mesmo caminho e o que funcionava ao redor."""
    from core import girar
    ferramenta(j, "X"); esperar_previa(j)
    ir_pagina(j, 14)
    passo(j, "cortar-pagina14")
    girar_painel(j, girar.GIRO_ESQUERDA); passo(j, "painel-esquerda")
    girar_painel(j, girar.GIRO_ESQUERDA); passo(j, "painel-esquerda-2")
    girar_canto(j, girar.GIRO_DIREITA); passo(j, "canto-direita")
    # Ctrl+Seta: o atalho do menu Pagina so dispara com a janela ATIVA, e a janela do piloto
    # fica fora da tela, sem foco (a mensagem do Windows cai na navegacao: o mesmo no codigo de
    # antes, fase "tecla"). Vai pela acao do menu, que e o que o atalho chama.
    j.menu.acoes["girar"].trigger(); esperar_previa(j); passo(j, "menu-girar-direita-ctrl-seta")
    girar_painel(j, girar.GIRO_MEIA_VOLTA); passo(j, "meia-volta")
    for n in range(1, 6):
        ctrl(j, ord("Z")); esperar_previa(j)
    passo(j, "ctrl-z-tudo")
    girar_painel(j, girar.GIRO_ESQUERDA); passo(j, "esquerda-de-novo")
    ir_pagina(j, 13); passo(j, "pagina13")
    ir_pagina(j, 14); passo(j, "volta-pagina14")
    ferramenta(j, "E"); esperar_previa(j); passo(j, "endireitar-pagina14")
    ferramenta(j, "D"); esperar_previa(j); mostrar(j, "uma"); passo(j, "dividir-uma-pagina")
    mostrar(j, "duas"); passo(j, "dividir-duas-lado-a-lado"); mostrar(j, "uma")
    ferramenta(j, "X"); esperar_previa(j)
    # folha inteira: a capa (folha 1) do Gradus é dividida? procura a primeira não dividida
    inteiras = [pg.indice for pg in j.projeto.paginas
                if not j.projeto.folhas[pg.folha].dividir]
    anotar("paginas-de-folha-inteira", inteiras[:10])
    if inteiras:
        ir_pagina(j, inteiras[0] + 1)
        passo(j, "folha-inteira")
        girar_painel(j, girar.GIRO_ESQUERDA); passo(j, "folha-inteira-esquerda")
        ctrl(j, ord("Z")); esperar_previa(j)


def medir_na_tela(j) -> dict:
    """O que a tela mostra: o tamanho da imagem posta no visualizador da vez e o retângulo em
    que ela é desenhada (proporção na tela = largura/altura do desenho)."""
    vis = j.tela_conferir.area_imagem.currentWidget()
    saida = {"visualizador": type(vis).__name__}
    pix = getattr(vis, "_pixmap", None)
    if pix is not None:
        saida["imagem (larg x alt)"] = [pix.width(), pix.height()]
        saida["proporcao da imagem"] = round(pix.width() / max(1, pix.height()), 3)
    for nome in ("_area_da_imagem", "_area_do_conteudo", "_retangulo_da_imagem"):
        f = getattr(vis, nome, None)
        if callable(f):
            try:
                r = f()
                saida[nome] = [r.x(), r.y(), r.width(), r.height(),
                               round(r.width() / max(1, r.height()), 3)]
            except Exception as erro:  # noqa: BLE001 - só anotação
                saida[nome] = str(erro)
    return saida


def fase_folha(j):
    """A folha inteira (não dividida): a proporção antes e depois de girar ¼. O Gradus tem todas
    as folhas divididas: a folha 1 é juntada no Dividir ("não dividir esta"), como o Kaique."""
    from core import girar
    t = j.tela_conferir
    ferramenta(j, "D"); mostrar(j, "duas"); esperar_previa(j)
    ir_pagina(j, 1)
    if j.projeto.folhas[t.indice_folha].dividir:
        base.clique(j, t.botao_nao_dividir); base.esperar(2.0)
    anotar("juntou", {"folha": t.indice_folha + 1, "dividida": j.projeto.folhas[t.indice_folha].dividir,
                      "estado": estado(j)})
    mostrar(j, "uma")
    i = next(pg.indice for pg in j.projeto.paginas if pg.folha == t.indice_folha)
    for letra, nome in (("X", "cortar"), ("F", "mover"), ("E", "endireitar")):
        ferramenta(j, letra); esperar_previa(j); ir_pagina(j, i + 1)
        anotar(f"{nome}-antes", {"estado": estado(j), "medidas": medir_paginas(j, (i,)),
                                 "tela": medir_na_tela(j)})
        p(j, f"{nome}-folha-inteira")
        girar_painel(j, girar.GIRO_ESQUERDA)
        anotar(f"{nome}-depois-de-girar", {"estado": estado(j), "medidas": medir_paginas(j, (i,)),
                                           "tela": medir_na_tela(j)})
        p(j, f"{nome}-folha-inteira-girada")
        ctrl(j, ord("Z")); esperar_previa(j)
    mostrar(j, "duas"); esperar_previa(j)
    p(j, "duas-lado-a-lado-antes")
    girar_painel(j, girar.GIRO_ESQUERDA)
    anotar("duas-depois-de-girar", {"estado": estado(j), "medidas": medir_paginas(j, (i,))})
    p(j, "duas-lado-a-lado-girada")


def fase_tecla(j):
    """So a tecla Ctrl+Seta na pagina 14 do Cortar: gira ou troca de pagina? (para comparar
    com o codigo de antes)."""
    ferramenta(j, "X"); esperar_previa(j)
    ir_pagina(j, 14)
    from PySide6.QtWidgets import QApplication
    foco = QApplication.focusWidget()
    anotar("foco-antes", type(foco).__name__ if foco else None)
    ctrl(j, VK_RIGHT); esperar_previa(j)
    passo(j, "ctrl-seta-direita")


def fase_foto(j):
    """"girar - sim" (04/11): a folha inteira gira como uma foto, com o corte a mao e o tamanho
    escolhido. O Gradus abre aqui como livro novo (folhas inteiras). Na folha 1 (capa e
    contracapa), um corte a mao so na contracapa (posto pelo programa, como o arrasto o
    gravaria: _mover_recorte) e o "¼ à esquerda" do Propriedades (clique)."""
    from core import girar
    t = j.tela_conferir
    ferramenta(j, "D"); mostrar(j, "duas"); esperar_previa(j)
    ir_pagina(j, 1)
    if j.projeto.folhas[t.indice_folha].dividir:
        base.clique(j, t.botao_nao_dividir); base.esperar(2.0)      # "não dividir esta"
    anotar("folha-1", {"dividida": j.projeto.folhas[0].dividir, "estado": estado(j)})
    mostrar(j, "uma")
    ferramenta(j, "X"); esperar_previa(j)
    ir_pagina(j, 1)
    t._mover_recorte((0.02, 0.03, 0.45, 0.94)); esperar_previa(j)
    anotar("corte-a-mao", {"estado": estado(j), "medidas": medir_paginas(j, (0,))}); p(j, "corte-a-mao")
    girar_painel(j, girar.GIRO_ESQUERDA)
    anotar("corte-girado", {"estado": estado(j), "medidas": medir_paginas(j, (0,))}); p(j, "corte-girado")
    ferramenta(j, "F"); esperar_previa(j); p(j, "mover-depois-de-girar")
    ctrl(j, ord("Z")); esperar_previa(j)
    ferramenta(j, "X"); esperar_previa(j)
    anotar("ctrl-z", {"estado": estado(j), "medidas": medir_paginas(j, (0,))}); p(j, "ctrl-z")


def textos_do_girar(j) -> dict:
    """O que o quadro do girar, a lista, o menu e o canto dizem agora (D-636)."""
    t = j.tela_conferir
    combo = t.barra_girar.combo_alcance
    return {"quadro": t.barra_girar.rotulo.text(),
            "lista": [combo.itemText(i) for i in range(combo.count())],
            "escolhida": combo.currentText(),
            "menu": [j.menu.acoes[f"giro_em_{a}"].text() for a in
                     ("esta", "todas", "daqui_em_diante", "pares", "impares")],
            "canto": [b.toolTip() for b in t.girar_do_canto.botoes_de_giro.values()][:1]}


def gerar_pdf(j, indices, nome) -> list:
    """O PDF que sai, só com as páginas `indices` (as outras tiradas numa CÓPIA do projeto),
    pela conta do programa (core/pipeline.processar); cada página vira um PNG para olhar."""
    import copy as _copy

    import fitz

    from core import pipeline
    copia = _copy.deepcopy(j.projeto)
    for pg in copia.paginas:
        if pg.indice not in indices:
            pg.apagada = True
    destino = base.TRAB / f"{nome}.pdf"
    copia.caminho_saida = str(destino)
    caminho = pipeline.processar(copia)
    saida = []
    with fitz.open(caminho) as doc:
        for n, pagina in enumerate(doc):
            png = AQUI / "prints" / f"{FASE}-pdf-{nome}-{n + 1}.png"
            pagina.get_pixmap(dpi=40).save(str(png))
            saida.append({"png": png.name, "larg x alt (pt)": [round(pagina.rect.width), round(pagina.rect.height)]})
    return saida


def fase_aplicar(j):
    """D-636 (05/11/2026): numa folha dividida o "aplicar em" gira PÁGINAS, cada uma sozinha;
    na grade "ver todas" também. O Gradus abre com as folhas inteiras: o livro é dividido pelo
    "dividir todas" da ferramenta Dividir (como o Kaique) e a folha 1 é juntada ("não dividir
    esta") para ter uma folha inteira no livro, como uma capa aberta."""
    from core import girar
    t = j.tela_conferir
    ferramenta(j, "D"); mostrar(j, "duas"); esperar_previa(j)
    base.clique(j, t.botao_dividir_todas)
    t0 = time.time()
    while time.time() - t0 < 600 and not all(f.dividir for f in j.projeto.folhas[1:]):
        base.esperar(1.0)
    base.esperar(3.0)
    anotar("dividiu-todas", {"s": round(time.time() - t0, 1), "paginas": len(j.projeto.paginas),
                             "divididas": sum(f.dividir for f in j.projeto.folhas)})
    ir_pagina(j, 1)
    if j.projeto.folhas[t.indice_folha].dividir:
        base.clique(j, t.botao_nao_dividir); base.esperar(2.0)      # "não dividir esta"
    anotar("juntou-a-folha-1", {"folha 1 dividida": j.projeto.folhas[0].dividir,
                                "paginas": len(j.projeto.paginas)})
    mostrar(j, "uma")
    ferramenta(j, "X"); esperar_previa(j)
    ir_pagina(j, 1)
    anotar("folha-inteira-textos", textos_do_girar(j)); p(j, "folha-inteira-quadro")
    ir_pagina(j, 14)
    numero = t.indice_pagina + 1
    anotar("pagina-dividida-textos", {"pagina": numero, **textos_do_girar(j)})
    vizinhas = tuple(i for i in (0, t.indice_pagina - 1, t.indice_pagina, t.indice_pagina + 1,
                                 t.indice_pagina + 2) if 0 <= i < len(j.projeto.paginas))
    anotar("antes", {"estado": estado(j), "medidas": medir_paginas(j, vizinhas)})
    p(j, "pagina-dividida-quadro")
    anotar("pdf-antes", gerar_pdf(j, vizinhas, "antes"))
    # a lista "aplicar em": pelo menu Página (o mesmo da lista; abrir a lista por mensagens do
    # Windows não é confiável com a janela fora da tela)
    j.menu.acoes["giro_em_todas"].trigger(); base.esperar(0.5)
    anotar("escolheu-todas", textos_do_girar(j))
    girar_painel(j, girar.GIRO_ESQUERDA)
    anotar("todas-esquerda", {"estado": estado(j), "medidas": medir_paginas(j, vizinhas),
                              "giros": [pg.giro_da_pagina for pg in j.projeto.paginas][:20],
                              "rotacoes": sorted({f.rotacao for f in j.projeto.folhas})})
    p(j, "todas-esquerda")
    anotar("pdf-depois", gerar_pdf(j, vizinhas, "depois"))
    ir_pagina(j, numero - 1); p(j, "todas-esquerda-pagina-anterior")
    ir_pagina(j, 1); anotar("capa-depois", {"estado": estado(j), **textos_do_girar(j)})
    p(j, "todas-esquerda-capa-inteira")
    ir_pagina(j, numero)
    ctrl(j, ord("Z")); esperar_previa(j)
    anotar("ctrl-z", {"estado": estado(j), "medidas": medir_paginas(j, vizinhas),
                      "giros": sorted({pg.giro_da_pagina for pg in j.projeto.paginas})})
    p(j, "ctrl-z")
    # pares: na página par gira as pares; na ímpar avisa
    j.menu.acoes["giro_em_pares"].trigger(); base.esperar(0.5)
    ir_pagina(j, numero if numero % 2 == 0 else numero + 1)
    girar_painel(j, girar.GIRO_MEIA_VOLTA)
    anotar("pares-meia-volta", {"estado": estado(j),
                                "giros": [pg.giro_da_pagina for pg in j.projeto.paginas][:12]})
    p(j, "pares-meia-volta")
    ir_pagina(j, 3)
    girar_painel(j, girar.GIRO_MEIA_VOLTA)
    anotar("pares-na-impar", {"estado": estado(j), "avisos": getattr(j, "avisos_anotados", None)})
    p(j, "pares-na-impar-aviso")
    ctrl(j, ord("Z")); esperar_previa(j)
    j.menu.acoes["giro_em_esta"].trigger(); base.esperar(0.5)
    # a grade "ver todas": escolher a página do Samuel e a capa inteira, "girar ¼ →"
    t.abrir_todas_as_paginas(); base.esperar(2.0)
    grade = t.todas
    grade.marcar(numero - 1); grade.marcar(0); base.esperar(0.5)
    p(j, "ver-todas-escolhidas")
    base.clique(j, grade.botoes_da_escolha["girar_direita"]); base.esperar(2.5)
    anotar("ver-todas-girar", {"giros": [pg.giro_da_pagina for pg in j.projeto.paginas][:16],
                               "rotacoes": [f.rotacao for f in j.projeto.folhas][:8],
                               "desfazer": t.acoes.descricao_desfazer()})
    p(j, "ver-todas-girada")
    ctrl(j, ord("Z")); base.esperar(2.0)
    anotar("ver-todas-ctrl-z", {"giros": sorted({pg.giro_da_pagina for pg in j.projeto.paginas}),
                                "rotacoes": sorted({f.rotacao for f in j.projeto.folhas})})


def main():
    j, _porteiro = abrir()
    anotar("inicio", estado(j))
    {"antes": fase_antes, "depois": fase_depois, "folha": fase_folha, "tecla": fase_tecla, "foto": fase_foto,
     "aplicar": fase_aplicar}[FASE](j)
    base.fechar(j)


if __name__ == "__main__":
    main()
