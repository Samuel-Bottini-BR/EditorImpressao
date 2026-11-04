"""Reproduzir o "mover e dimensionar para de funcionar" (Samuel, 04/11/2026, Gradus Primus) na
janela de VERDADE (plataforma Windows), posta fora da tela, como o verificador clicando de 03/11
(relatorios/verif-03-11/piloto.py): cliques, arrastos e teclas por mensagens do Windows ao hwnd
(relatorios/obra-etapa3/roteiro/base.py), prints por PrintWindow.

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF
aponta para a cópia do PDF.

Rodar (na cópia mover-parou):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\mover-parou\\piloto.py <fase>
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

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\mover-parou-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
FASE = sys.argv[1] if len(sys.argv) > 1 else "t1"
LOG = open(AQUI / f"anotacoes-{FASE}.txt", "w", encoding="utf-8")
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{FASE}-{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas que abrem por cima: anota o texto e clica no primeiro botão preferido."""

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
    """Espera a prévia da ferramenta Mover chegar (o visualizador para de 'carregar')."""
    from ui.tela_conferir import ABA_MOVER
    vis = j.tela_conferir.visualizadores[ABA_MOVER]
    t = time.time()
    base.esperar(0.4)
    while time.time() - t < limite and (vis._pixmap is None or vis.carregando):
        base.esperar(0.2)
    base.esperar(0.6)


def estado(j) -> dict:
    from PySide6.QtWidgets import QApplication
    from ui.tela_conferir import ABA_MOVER
    t, pr = j.tela_conferir, j.projeto
    vis = t.visualizadores[ABA_MOVER]
    pg = pr.paginas[t.indice_pagina]
    foco = QApplication.focusWidget()
    atual = t.vista_da_pagina.currentWidget()
    return {
        "aba": t.aba_atual, "pagina": t.indice_pagina + 1, "folha": t.indice_folha + 1,
        "mostrar": t.mostrar, "comparando": t.comparando,
        "vista": ("ferramenta" if atual is t.area_imagem else
                  "lado_a_lado" if atual is t.lado_a_lado else "antes_depois"),
        "ferramenta_na_vista": type(t.area_imagem.currentWidget()).__name__,
        "vis_do_mover_e_o_da_vista": t.area_imagem.currentWidget() is vis,
        "pixmap": vis._pixmap is not None, "carregando": vis.carregando, "modo": vis.modo,
        "folha_do_mover": vis._folha_do_mover, "arrastando": vis._arrastando,
        "mundo_fixo": vis._mundo_fixo, "zoom": round(vis.zoom, 3),
        "retangulo": [round(v, 4) for v in vis._retangulo_conteudo],
        "escala": pg.conteudo_escala, "desloc": list(pg.conteudo_deslocamento),
        "campo_%": t.campo_tamanho_do_conteudo.value(), "pronta": t._pronta(),
        "foco": type(foco).__name__ if foco else None,
        "feitas": len(t.acoes.feitas) if t.acoes else None,
    }


def vis_mover(j):
    from ui.tela_conferir import ABA_MOVER
    return j.tela_conferir.visualizadores[ABA_MOVER]


def arrastar_conteudo(j, dx=60, dy=0, nome="arrasto"):
    """Arrasta do meio do conteúdo (como a mão) dx, dy pontos. Devolve se o lugar mudou."""
    t = j.tela_conferir
    vis = vis_mover(j)
    pg = j.projeto.paginas[t.indice_pagina]
    antes = (pg.conteudo_escala, tuple(pg.conteudo_deslocamento))
    if not vis.isVisible():
        anotar(f"{nome}-o-visualizador-do-mover-NAO-esta-a-vista", estado(j))
        alvo = t.vista_da_pagina.currentWidget()
        centro = alvo.rect().center()
        base.arrastar(j, alvo, centro, centro + __import__("PySide6.QtCore", fromlist=["QPoint"]).QPoint(dx, dy))
    else:
        from PySide6.QtCore import QPoint
        c = vis._area_do_conteudo().center() if vis._pixmap is not None else vis.rect().center()
        base.arrastar(j, vis, c, c + QPoint(dx, dy))
    base.esperar(1.0)
    depois = (pg.conteudo_escala, tuple(pg.conteudo_deslocamento))
    mudou = antes != depois
    anotar(f"{nome}", {"mudou": mudou, "antes": antes, "depois": depois, "estado": estado(j)})
    return mudou


def roda(j, widget, cliques=1, ponto=None, ctrl=False):
    """Roda do mouse por mensagem do Windows (WM_MOUSEWHEEL leva a posição na TELA)."""
    from PySide6.QtCore import QPoint
    h = int(j.winId())
    alvo = widget.mapToGlobal(ponto if ponto is not None else widget.rect().center())
    e = j.devicePixelRatioF()
    x, y = round(alvo.x() * e), round(alvo.y() * e)
    lp = ((y & 0xFFFF) << 16) | (x & 0xFFFF)
    delta = 120 if cliques > 0 else -120
    for _ in range(abs(cliques)):
        wp = ((delta & 0xFFFF) << 16) | (0x0008 if ctrl else 0)
        base.user32.PostMessageW(h, 0x020A, wp, lp); base.esperar(0.12)
    base.esperar(0.8)


def ctrl(j, tecla_vk):
    h = int(j.winId())
    VK_CONTROL, VK_LCONTROL = 0x11, 0xA2
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, VK_CONTROL, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, tecla_vk, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, tecla_vk, 0xC0000001); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, VK_CONTROL, 0xC0000001); base.esperar(0.3)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0
    base.user32.SetKeyboardState(est); base.esperar(1.5)


def mostrar(j, qual):
    from ui.tela_conferir import DUAS, UMA
    t = j.tela_conferir
    base.clique(j, t.botoes_mostrar[UMA if qual == "uma" else DUAS]); base.esperar(1.5)


def ferramenta(j, letra):
    base.tecla(j, ord(letra)); base.esperar(1.5)


def abrir():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import projetos
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    porteiro = Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    return j, porteiro


def main():
    j, _porteiro = abrir()
    t = j.tela_conferir
    anotar("inicio", estado(j))
    p(j, "abriu")
    fases = {"t1": fase_t1, "t2": fase_t2, "t3": fase_t3, "t4": fase_t4}
    fases[FASE](j)
    base.fechar(j)


def ir_pagina(j, numero):
    """Vai à página `numero` (1...) clicando a miniatura da tira."""
    t = j.tela_conferir
    i = numero - 1
    mapa = getattr(t.tira, "_miniaturas", [])
    if 0 <= i < len(mapa):
        mini = mapa[i]
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(1.0)
    esperar_previa(j)


def fase_t1(j):
    """O caminho do registro: Mover na página 2, arrastar, diminuir pela roda no número, 100."""
    t = j.tela_conferir
    ferramenta(j, "F"); esperar_previa(j)
    anotar("mover-aberto", estado(j)); p(j, "mover")
    ir_pagina(j, 2)
    anotar("pagina-2", estado(j)); p(j, "pagina2")
    arrastar_conteudo(j, 40, 0, "arrasto-1")
    roda(j, t.campo_tamanho_do_conteudo, -12)
    anotar("depois-da-roda", estado(j)); p(j, "depois-roda")
    arrastar_conteudo(j, -40, 0, "arrasto-2-depois-da-roda")
    base.clique(j, t.campo_tamanho_do_conteudo)
    base.tecla(j, 0x23)  # End
    for _ in range(4):
        base.tecla(j, 0x08)  # Backspace
    base.digitar(j, "100", enter=True)
    anotar("depois-de-digitar-100", estado(j)); p(j, "depois-100")
    arrastar_conteudo(j, 50, 0, "arrasto-3-depois-de-digitar")
    p(j, "depois-arrasto-3")


def tentar(j, nome, dx=30):
    """Depois de um preparo: o arrasto ainda move? Print quando não move."""
    ok = arrastar_conteudo(j, dx, 0, f"[{nome}]")
    if not ok:
        p(j, f"PAROU-{nome}")
    anotar(f"RESULTADO {nome}", "move" if ok else "NAO MOVE")
    return ok


def fase_t2(j):
    """Uma situação por vez, cada uma seguida de um arrasto."""
    from PySide6.QtCore import QPoint
    t = j.tela_conferir
    ferramenta(j, "F"); esperar_previa(j)
    ir_pagina(j, 2)
    tentar(j, "inicio")
    # 1. Ctrl+Z e Ctrl+Y
    ctrl(j, ord("Z")); esperar_previa(j); tentar(j, "depois-ctrl-z")
    ctrl(j, ord("Z")); ctrl(j, ord("Y")); esperar_previa(j); tentar(j, "depois-ctrl-z-ctrl-y")
    # 2. trocar de página e voltar (setas)
    base.tecla(j, 0x27); esperar_previa(j); tentar(j, "pagina-3")
    base.tecla(j, 0x25); esperar_previa(j); tentar(j, "volta-pagina-2")
    # 3. trocar de ferramenta e voltar
    ferramenta(j, "X"); ferramenta(j, "F"); esperar_previa(j); tentar(j, "cortar-e-volta")
    ferramenta(j, "D"); ferramenta(j, "F"); esperar_previa(j); tentar(j, "dividir-e-volta")
    # 4. antes / depois liga e desliga
    base.clique(j, t.botao_antes_depois); base.esperar(1.5)
    base.clique(j, t.botao_antes_depois); esperar_previa(j); tentar(j, "antes-depois-e-volta")
    # 5. zoom (Ctrl + roda) e volta
    roda(j, vis_mover(j), 3, ctrl=True); tentar(j, "com-zoom")
    base.clique(j, t.botao_ajustar_a_tela); esperar_previa(j); tentar(j, "zoom-ajustar-a-tela")
    # 6. pequeno (5%), canto, voltar como veio, centralizar
    base.clique(j, t.campo_tamanho_do_conteudo); base.tecla(j, 0x23); base.tecla(j, 0x08, vezes=4)
    base.digitar(j, "5"); esperar_previa(j); tentar(j, "tamanho-5")
    base.clique(j, t.botao_centralizar); esperar_previa(j); tentar(j, "centralizar")
    vis = vis_mover(j)
    canto = vis._area_do_conteudo().bottomRight()
    base.arrastar(j, vis, canto - QPoint(1, 1), canto + QPoint(80, 80)); base.esperar(1)
    anotar("canto", estado(j)); tentar(j, "depois-do-canto")
    # 7. levar longe (o meio na beirada) e de novo
    tentar(j, "longe-1", dx=900); tentar(j, "longe-2", dx=-60)
    # 8. Duas lado a lado e volta
    mostrar(j, "duas"); anotar("duas", estado(j)); p(j, "duas-lado-a-lado")
    tentar(j, "em-duas-lado-a-lado")
    mostrar(j, "uma"); esperar_previa(j); tentar(j, "duas-e-volta-uma")
    # 9. Dividir em Duas lado a lado, depois F
    ferramenta(j, "D"); mostrar(j, "duas"); ferramenta(j, "F"); esperar_previa(j)
    anotar("dividir-duas-depois-F", estado(j)); p(j, "dividir-duas-depois-F")
    tentar(j, "dividir-em-duas-depois-F")
    mostrar(j, "uma"); esperar_previa(j)
    # 10. voltar como veio
    for b in t.findChildren(type(t.botao_centralizar)):
        if b.text() == "voltar como veio" and b.isVisible():
            base.clique(j, b); break
    esperar_previa(j); tentar(j, "voltar-como-veio")


def fase_t3(j):
    """O caminho do registro desde antes de 02:27: desfazer tudo, Dividir em Duas lado a lado,
    "dividir todas", F, mover e diminuir a página 2, 100%, e de novo."""
    t = j.tela_conferir
    ferramenta(j, "D"); mostrar(j, "duas")
    for _ in range(17):
        ctrl(j, ord("Z"))
    base.esperar(3)
    anotar("desfeito", {"divididas": sum(f.dividir for f in j.projeto.folhas), "estado": estado(j)})
    p(j, "dividir-duas-desfeito")
    base.clique(j, t.botao_dividir_todas); base.esperar(2)
    t0 = time.time()
    while time.time() - t0 < 600:
        caixa = getattr(t, "_caixa_de_dividir_todas", None)
        try:
            aberta = caixa is not None and caixa.isVisible()
        except RuntimeError:
            aberta = False
        if not aberta and sum(f.dividir for f in j.projeto.folhas) > 0:
            break
        base.esperar(0.5)
    base.esperar(3)
    anotar("dividiu-todas", {"divididas": sum(f.dividir for f in j.projeto.folhas), "estado": estado(j)})
    p(j, "dividir-todas")
    ferramenta(j, "F"); esperar_previa(j)
    anotar("F-depois-de-dividir-todas", estado(j)); p(j, "F-depois-de-dividir-todas")
    tentar(j, "F-direto-depois-de-dividir-todas")
    mostrar(j, "uma"); esperar_previa(j)
    ir_pagina(j, 2)
    tentar(j, "uma-pagina-pagina-2")
    roda(j, t.campo_tamanho_do_conteudo, -12)
    tentar(j, "depois-da-roda-88")
    base.clique(j, t.campo_tamanho_do_conteudo); base.tecla(j, 0x23); base.tecla(j, 0x08, vezes=4)
    base.digitar(j, "100"); esperar_previa(j)
    tentar(j, "depois-de-100", dx=-30)
    base.clique(j, t.botao_antes_depois); base.esperar(2)
    anotar("antes-depois-ligado", estado(j)); p(j, "antes-depois-ligado")
    tentar(j, "com-antes-depois-ligado", dx=-30)
    base.clique(j, t.botao_antes_depois); esperar_previa(j)
    vis = vis_mover(j)
    c = vis._area_do_conteudo().center()
    fora = vis.mapFrom(j, t.campo_tamanho_do_conteudo.mapTo(j, t.campo_tamanho_do_conteudo.rect().center()))
    pg = j.projeto.paginas[t.indice_pagina]
    antes = tuple(pg.conteudo_deslocamento)
    base.arrastar(j, vis, c, fora); base.esperar(1)
    anotar("soltou-no-painel", {"antes": antes, "depois": tuple(pg.conteudo_deslocamento), "estado": estado(j)})
    tentar(j, "depois-de-soltar-no-painel", dx=-30)
    for b in t.findChildren(type(t.botao_centralizar)):
        if b.text() == "ver no Mover" and b.isVisible():
            base.clique(j, b); base.esperar(1.5); anotar("cliquei ver no Mover", estado(j)); break
    tentar(j, "depois-de-ver-no-mover", dx=-30)
    for b in t.findChildren(type(t.botao_centralizar)):
        if b.text() == "está bom assim" and b.isVisible():
            base.clique(j, b); base.esperar(1.5); anotar("cliquei está bom assim", estado(j)); break
    tentar(j, "depois-de-esta-bom-assim", dx=-30)


def com_tecla(vk, fazer):
    """Faz `fazer()` com a tecla `vk` (Ctrl 0x11, Shift 0x10) "apertada" no estado do teclado
    deste fio (só este programa)."""
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[vk] = 0x80
    base.user32.SetKeyboardState(est)
    try:
        fazer()
    finally:
        est[vk] = 0
        base.user32.SetKeyboardState(est)
        base.esperar(0.5)


def fase_t4(j):
    """Zoom e vista: o "+" da barra, Ctrl+roda, Shift+roda, o "Duas lado a lado" e o
    "antes / depois" ligados, a roda sem Ctrl (troca de página) e o foco no número."""
    t = j.tela_conferir
    ferramenta(j, "F"); esperar_previa(j)
    ir_pagina(j, 2)
    tentar(j, "inicio", dx=-30)
    base.clique(j, t.botao_mais_zoom); base.clique(j, t.botao_mais_zoom); base.esperar(1)
    anotar("zoom-mais", estado(j)); p(j, "zoom-mais")
    tentar(j, "zoom-mais", dx=-30)
    com_tecla(0x10, lambda: roda(j, vis_mover(j), -3))
    anotar("shift-roda", estado(j)); tentar(j, "depois-shift-roda", dx=-30)
    base.clique(j, t.botao_ajustar_a_tela); base.esperar(1)
    com_tecla(0x11, lambda: roda(j, vis_mover(j), 3))
    anotar("ctrl-roda", estado(j)); p(j, "ctrl-roda")
    tentar(j, "depois-ctrl-roda", dx=-30)
    base.clique(j, t.botao_ajustar_a_tela); esperar_previa(j)
    tentar(j, "ajustar-a-tela", dx=30)
    base.clique(j, t.botao_antes_depois); base.esperar(2)
    anotar("antes-depois", estado(j)); p(j, "antes-depois-no-mover")
    tentar(j, "antes-depois-ligado", dx=30)
    base.clique(j, t.botao_antes_depois); esperar_previa(j)
    mostrar(j, "duas"); anotar("duas", estado(j)); p(j, "duas-no-mover")
    tentar(j, "duas-lado-a-lado", dx=30)
    mostrar(j, "uma"); esperar_previa(j)
    tentar(j, "volta-uma", dx=-30)


if __name__ == "__main__":
    main()
