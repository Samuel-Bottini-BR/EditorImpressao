"""Piloto da D-612 (04/11/2026) na janela de VERDADE (plataforma Windows), posta fora da tela:
cliques, arrastos, roda e teclas por mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/
base.py), prints por PrintWindow. Mesmo jeito do relatorios/mover-parou/piloto.py.

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF
aponta para a cópia do PDF.

O que confere (D-612: "1 - ele tem que funcionar com paginas lado a lado também"; D-605):
  1. Dividir em "Duas lado a lado": a folha inteira com a linha (D-601) e a linha se arrasta (D-609).
  2. Tecla F: o Mover, a vista continua "Duas lado a lado"; a página da vez nos pares tem os cantos.
  3. Arrastar a página da vez nos pares move; Ctrl+Z volta; Ctrl+Y refaz.
  4. Puxar o canto aumenta; o número "Tamanho do conteúdo" acompanha; digitar 80 diminui.
  5. Ctrl+roda em cima da página da vez dá zoom nos pares.
  6. Clicar na outra página do par: ela vira a da vez e o Mover passa a mexer nela.
  7. "Uma página": o Mover de sempre, o arrasto move; tecla F continua.
  8. A tira embaixo em pares com "Duas lado a lado" (D-611).

Rodar (na cópia mover-lado):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\mover-lado\\piloto.py
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

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f"
               r"\scratchpad\mover-lado-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
LOG = None          # aberto no main (os pilotos curtos importam este arquivo e põem o deles)
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    if LOG is not None:
        LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"p{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas que abrem por cima: anota o texto e clica no botão preferido."""

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
        if not arq.exists():
            continue
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


def vis_mover(j):
    return j.tela_conferir.visualizadores["mover"]


def esperar_previa(j, limite=60):
    vis = vis_mover(j)
    t = time.time()
    base.esperar(0.4)
    while time.time() - t < limite and (vis._pixmap is None or vis.carregando):
        base.esperar(0.2)
    base.esperar(0.8)


def estado(j) -> dict:
    t, pr = j.tela_conferir, j.projeto
    vis = vis_mover(j)
    pg = pr.paginas[t.indice_pagina]
    atual = t.vista_da_pagina.currentWidget()
    return {
        "aba": t.aba_atual, "pagina": t.indice_pagina + 1, "mostrar": t.mostrar,
        "vista": ("ferramenta" if atual is t.area_imagem else
                  "pares" if atual is t.lado_a_lado else "antes_depois"),
        "mover_nos_pares": t.lado_a_lado.isAncestorOf(vis), "mover_a_vista": vis.isVisible(),
        "escala": round(pg.conteudo_escala, 4), "desloc": [round(v, 4) for v in pg.conteudo_deslocamento],
        "campo_%": t.campo_tamanho_do_conteudo.value(), "zoom_pares": round(t.lado_a_lado.zoom, 3),
        "zoom_mover": round(vis.zoom, 3), "tira_em_pares": getattr(t.tira, "pares_pela_vista", None),
        "feitas": len(t.acoes.feitas) if t.acoes else None,
    }


def ctrl(j, tecla_vk):
    h = int(j.winId())
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[0x11] = est[0xA2] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, 0x11, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, tecla_vk, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, tecla_vk, 0xC0000001); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, 0x11, 0xC0000001); base.esperar(0.3)
    est[0x11] = est[0xA2] = 0
    base.user32.SetKeyboardState(est); base.esperar(1.5)


def roda_ctrl(j, widget, ponto, cliques=1):
    """Ctrl + roda por mensagem do Windows (WM_MOUSEWHEEL leva a posição na TELA)."""
    h = int(j.winId())
    alvo = widget.mapToGlobal(ponto)
    e = j.devicePixelRatioF()
    x, y = round(alvo.x() * e), round(alvo.y() * e)
    lp = ((y & 0xFFFF) << 16) | (x & 0xFFFF)
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[0x11] = 0x80
    base.user32.SetKeyboardState(est)
    for _ in range(cliques):
        wp = ((120 & 0xFFFF) << 16) | 0x0008
        base.user32.PostMessageW(h, 0x020A, wp, lp); base.esperar(0.15)
    est[0x11] = 0
    base.user32.SetKeyboardState(est)
    base.esperar(1.0)


def mostrar(j, qual):
    from ui.tela_conferir import DUAS, UMA
    base.clique(j, j.tela_conferir.botoes_mostrar[UMA if qual == "uma" else DUAS]); base.esperar(1.5)


def ferramenta(j, letra):
    base.tecla(j, ord(letra)); base.esperar(1.5)


def na_trilha(j, ferr):
    """Clica o botão da ferramenta `ferr` na trilha da esquerda."""
    from ui.widgets.trilha_agrupada import GRUPOS
    tr = j.tela_conferir.trilha
    i = next(k for k, g in enumerate(GRUPOS) if g != "-" and ferr in g)
    base.clique(j, tr, tr.retangulos()[i].center()); base.esperar(1.5)


def lugar_da_vez(j):
    """O retângulo (no widget dos pares) da página da vez."""
    pares = j.tela_conferir.lado_a_lado
    ret = next(r for i, r in pares.retangulos() if i == pares.atual)
    return ret.translated(pares.folhas.mapTo(pares, ret.topLeft()) - ret.topLeft())


def main():
    global LOG
    from PySide6.QtCore import QPoint

    LOG = open(AQUI / "anotacoes-piloto.txt", "w", encoding="utf-8")
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import projetos
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    _porteiro = Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    t = j.tela_conferir
    pr = j.projeto
    anotar("divididas", sum(1 for f in pr.folhas if f.dividir))
    p(j, "abriu")

    # 1. Dividir em "Duas lado a lado": a folha inteira com a linha (D-601) e a linha anda (D-609)
    ferramenta(j, "D"); mostrar(j, "duas")
    vis_d = t.visualizadores["corte"]
    base.esperar(2)
    limite = time.time() + 20                 # a linha do motor chega por trás (D-602)
    while time.time() < limite and not vis_d.corte_visivel:
        base.esperar(0.3)
    vis_d.repaint()
    folha = pr.folhas[t.indice_folha]
    anotar("dividir-duas", {"vista": "ferramenta" if t.vista_da_pagina.currentWidget() is t.area_imagem
                            else "outra", "folha": t.indice_folha + 1, "dividir": folha.dividir,
                            "linha": folha.posicao_corte})
    p(j, "dividir-duas-lado-a-lado-folha-inteira")
    if vis_d._area.width() > 0 and vis_d.corte_visivel and vis_d.corte_arrastavel:
        x = vis_d._area.left() + round(folha.posicao_corte * vis_d._area.width())
        de = QPoint(x, vis_d._area.center().y())
        antes = folha.posicao_corte
        base.arrastar(j, vis_d, de, de + QPoint(-25, 0))
        base.conferir(abs(pr.folhas[t.indice_folha].posicao_corte - antes) > 0.01,
                      f"Dividir em Duas lado a lado: a linha anda com o mouse ({antes:.3f} -> "
                      f"{pr.folhas[t.indice_folha].posicao_corte:.3f})")
        ctrl(j, ord("Z"))
        base.conferir(abs(pr.folhas[t.indice_folha].posicao_corte - antes) < 1e-6,
                      "Ctrl+Z devolve a linha")
    else:
        anotar("linha-nao-arrastavel-nesta-folha", {"visivel": vis_d.corte_visivel,
                                                     "arrastavel": vis_d.corte_arrastavel})

    # 2. Tecla F: o Mover; a vista continua "Duas lado a lado"
    ferramenta(j, "F"); esperar_previa(j)
    base.esperar(1.5)
    e = estado(j); anotar("F-em-duas", e)
    base.conferir(e["aba"] == "mover" and e["mostrar"] == "duas" and e["vista"] == "pares",
                  "tecla F no Duas lado a lado: ferramenta Mover, a vista continua nos pares")
    base.conferir(e["mover_nos_pares"] and e["mover_a_vista"],
                  "a página da vez nos pares é o Mover (com os cantos)")
    base.conferir(e["tira_em_pares"] is not False, "a tira embaixo continua em pares (D-611)")
    p(j, "F-mover-nos-pares")

    # vai para a página 2 (a da esquerda do par 2-3), pela seta
    base.tecla(j, 0x27); esperar_previa(j); base.esperar(1)
    anotar("pagina-da-vez", estado(j))
    vis = vis_mover(j)
    pg = pr.paginas[t.indice_pagina]

    # 3. arrastar nos pares; Ctrl+Z; Ctrl+Y
    antes = tuple(pg.conteudo_deslocamento)
    c = vis._area.center()
    base.arrastar(j, vis, c, c + QPoint(-int(vis._area.width() * 0.12), 0))
    esperar_previa(j)
    depois = tuple(pg.conteudo_deslocamento)
    anotar("arrasto-nos-pares", {"antes": antes, "depois": depois, "estado": estado(j)})
    base.conferir(depois[0] < antes[0] - 0.05, f"arrastar nos pares move ({antes} -> {depois})")
    base.conferir(estado(j)["vista"] == "pares", "depois do arrasto a vista continua nos pares")
    p(j, "arrastou-nos-pares")
    ctrl(j, ord("Z")); esperar_previa(j)
    base.conferir(tuple(pg.conteudo_deslocamento) == antes, "Ctrl+Z desfaz o arrasto nos pares")
    ctrl(j, ord("Y")); esperar_previa(j)
    base.conferir(tuple(pg.conteudo_deslocamento) == depois, "Ctrl+Y refaz o arrasto nos pares")
    p(j, "ctrl-z-ctrl-y")

    # 4. puxar o canto; o número acompanha; digitar 80
    vis.repaint()
    canto = vis._alcas(vis._area_do_conteudo())["se"]
    escala_antes = pg.conteudo_escala
    base.arrastar(j, vis, canto, canto + QPoint(-30, -30))
    esperar_previa(j)
    e = estado(j); anotar("canto-nos-pares", e)
    base.conferir(pg.conteudo_escala < escala_antes - 0.03,
                  f"puxar o canto nos pares muda o tamanho ({escala_antes:.2f} -> {pg.conteudo_escala:.2f})")
    base.conferir(e["campo_%"] == round(pg.conteudo_escala * 100), "o número do tamanho acompanha")
    p(j, "canto-nos-pares")
    base.clique(j, t.campo_tamanho_do_conteudo)
    base.tecla(j, 0x23); base.tecla(j, 0x08, vezes=4)
    base.digitar(j, "80"); esperar_previa(j)
    base.conferir(abs(pg.conteudo_escala - 0.8) < 1e-6, "digitar 80 no número diminui a página nos pares")
    p(j, "numero-80-nos-pares")

    # 5. Ctrl+roda em cima da página da vez: zoom nos pares
    vis.repaint()
    roda_ctrl(j, vis, vis._area.center(), 2)
    e = estado(j); anotar("ctrl-roda", e)
    base.conferir(e["zoom_pares"] > 1.2 and e["zoom_mover"] == 1.0,
                  "Ctrl+roda na página da vez dá zoom nos pares")
    p(j, "ctrl-roda-zoom-nos-pares")
    base.clique(j, t.botao_ajustar_a_tela); base.esperar(1)

    # 6. clicar na outra página do par
    pares = t.lado_a_lado
    # a outra página do MESMO par (a da vez pode ser a da esquerda ou a da direita)
    outra = next((r for i, r in pares.retangulos()
                  if i != pares.atual and pares._linha_de(i) == pares._linha_de(pares.atual)), None)
    if outra is not None:
        ponto = pares.folhas.mapTo(pares, outra.center())
        era = t.indice_pagina
        base.clique(j, pares, ponto); esperar_previa(j); base.esperar(1)
        e = estado(j); anotar("clicou-na-outra", e)
        base.conferir(t.indice_pagina != era and e["mover_nos_pares"],
                      "clicar na outra página do par: ela vira a da vez, com o Mover")
        pg2 = pr.paginas[t.indice_pagina]
        a2 = tuple(pg2.conteudo_deslocamento)
        vis.repaint()
        c = vis._area.center()
        base.arrastar(j, vis, c, c + QPoint(int(vis._area.width() * 0.1), 0)); esperar_previa(j)
        base.conferir(pg2.conteudo_deslocamento[0] > a2[0] + 0.04, "e o arrasto move a outra")
        p(j, "outra-pagina-do-par")
        ctrl(j, ord("Z")); esperar_previa(j)

    # 7. "Uma página": o Mover de sempre
    mostrar(j, "uma"); esperar_previa(j)
    e = estado(j); anotar("uma-pagina", e)
    base.conferir(e["vista"] == "ferramenta" and not e["mover_nos_pares"] and e["mover_a_vista"],
                  "Uma página: o Mover de sempre, no lugar dele")
    pg = pr.paginas[t.indice_pagina]
    a = tuple(pg.conteudo_deslocamento)
    vis.repaint()
    c = vis._area.center()
    base.arrastar(j, vis, c, c + QPoint(-40, 0)); esperar_previa(j)
    base.conferir(pg.conteudo_deslocamento[0] < a[0] - 0.02, "Uma página: arrastar move")
    p(j, "uma-pagina-mover")
    # (o foco do teclado ficou no número "Tamanho do conteúdo", onde X e F são texto: o
    # Cortar vem pela trilha, como sempre foi)
    na_trilha(j, "cortar")
    base.conferir(t.aba_atual == "bordas", "trilha: Cortar")
    # o foco DENTRO da janela (com a janela fora da tela e inativa, o QApplication diz None)
    foco = j.focusWidget()
    anotar("foco-antes-do-F", type(foco).__name__ if foco else None)
    if foco is t.campo_tamanho_do_conteudo:
        foco.clearFocus()                 # como clicar fora do número (o foco ficou nele)
    ferramenta(j, "F"); esperar_previa(j)
    base.conferir(t.aba_atual == "mover" and t.mostrar == "uma", "tecla F de novo na Uma página")
    # 8. de volta aos pares com outra ferramenta: os pares de sempre
    na_trilha(j, "cortar"); mostrar(j, "duas")
    e = estado(j); anotar("cortar-em-duas", e)
    base.conferir(e["vista"] == "pares" and not e["mover_nos_pares"],
                  "Cortar em Duas lado a lado: os pares de sempre (sem o Mover)")
    p(j, "cortar-nos-pares")

    base.gravar_resultados(AQUI)
    base.fechar(j)


if __name__ == "__main__":
    main()
