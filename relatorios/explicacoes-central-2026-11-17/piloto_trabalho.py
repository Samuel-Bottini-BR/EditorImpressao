"""Piloto de quatro perguntas na área de trabalho, no "La vida eterna" (CÓPIA das 12 primeiras folhas,
dividido pelo Automático só com "Dividir"), na janela de verdade fora da tela:

M. ferramenta Mover (au-d-541), página 3 (texto "7" do livro): arrastar, puxar o canto, digitar 80 no
   "Tamanho do conteúdo (%)", arrastar até passar da beirada; o PDF de cada um (Ctrl+Z entre eles).
P. "Jeito do preto e branco" (nm-jeito-pb): página 3 em Preto e branco (clique no cartão), "Mais
   ajustes" aberto, a lista aberta; SIMULAÇÃO dos nomes novos (texto trocado só nesta janela).
A. "Antes de processar" (nm-antes-de-processar): clique em "Confirmar e processar" com avisos; a
   janela de hoje e as SIMULAÇÕES dos nomes (texto trocado só nesta janela; nada é processado).
F. folha e página (nm-folha-pagina): o "Para revisar" (cartões por página), a SIMULAÇÃO com
   "(folha N)", o botão "tamanho da folha..." do Mover e a etapa "Endireitar folhas tortas".
"""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comum as c  # noqa: E402
from comum import anotar, base  # noqa: E402


def ctrl(j, tecla_vk):
    """Ctrl + tecla por mensagens do Windows (como relatorios/mover-lado/piloto.py)."""
    c.normal(j)
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


def trocar_textos(raiz, trocas: dict):
    """SIMULAÇÃO: troca o texto de rótulos e botões desta janela (só na memória, para o print)."""
    from PySide6.QtWidgets import QAbstractButton, QLabel
    voltar = []
    for w in raiz.findChildren(QLabel) + raiz.findChildren(QAbstractButton):
        for de, para in trocas.items():
            if de in w.text():
                voltar.append((w, w.text()))
                w.setText(w.text().replace(de, para))
                break
    return voltar


def desfazer_trocas(voltar):
    for w, t in voltar:
        w.setText(t)


def main():
    pasta = c.preparar("trabalho")
    from PySide6.QtCore import QPoint

    from ui.janela_dos_avisos import JanelaDosAvisos
    from core.filtros import PRETO_E_BRANCO

    pdf = c.copia_da_vida(12)
    j = base.nova_janela(1280, 657)
    t = c.abrir(j, pdf)
    painel = c.rodar_automatico(j, {"dividir"})
    c.clicar_rodar(j, painel)
    t = j.tela_conferir
    pr = j.projeto
    anotar("dividido", [len(pr.folhas), len(pr.paginas)])

    # F. o Para revisar (cartões por página) e a etapa do Automático
    t.paineis.abrir("revisar")
    base.esperar(1.5)
    c.p(j, pasta, "F0-para-revisar")
    voltar = trocar_textos(t.paineis.para_revisar, {"Página 7": "Página 7 (folha 4)",
                                                     "Página 8": "Página 8 (folha 4)",
                                                     "Página 9": "Página 9 (folha 5)",
                                                     "Página 2": "Página 2 (folha 1)"})
    base.esperar(0.8)
    c.p(j, pasta, "F1-para-revisar-SIMULACAO")
    desfazer_trocas(voltar)

    # M. ferramenta Mover, página 3
    t.ir_para_pagina(2)
    c.esperar_previa(t)
    c.letra(j, "f")
    vis = t.visualizadores["mover"]
    c.esperar_previa(t)
    base.esperar(1.5)
    pg = pr.paginas[2]
    anotar("M0", {"aba": t.aba_atual, "escala": pg.conteudo_escala, "desloc": pg.conteudo_deslocamento,
                  "campo": t.campo_tamanho_do_conteudo.value()})
    c.p(j, pasta, "M0-mover-antes")
    c.pdf_das_paginas(pr, [2], pasta, "M0")

    vis.repaint()
    meio = vis._area.center()
    base.arrastar(j, vis, meio, meio + QPoint(-int(vis._area.width() * 0.15), 0))
    c.esperar_previa(t)
    anotar("M1-arrastou", {"desloc": pg.conteudo_deslocamento, "escala": pg.conteudo_escala})
    c.p(j, pasta, "M1-mover-arrastou")
    c.pdf_das_paginas(pr, [2], pasta, "M1")
    ctrl(j, ord("Z"))
    c.esperar_previa(t)

    vis.repaint()
    canto = vis._alcas(vis._area_do_conteudo())["se"]
    base.arrastar(j, vis, canto, canto + QPoint(40, 40))
    c.esperar_previa(t)
    anotar("M2-canto", {"desloc": pg.conteudo_deslocamento, "escala": pg.conteudo_escala,
                        "campo": t.campo_tamanho_do_conteudo.value()})
    c.p(j, pasta, "M2-mover-canto")
    c.pdf_das_paginas(pr, [2], pasta, "M2")
    ctrl(j, ord("Z"))
    c.esperar_previa(t)

    base.clique(j, t.campo_tamanho_do_conteudo)
    base.tecla(j, 0x23); base.tecla(j, 0x08, vezes=4)
    base.digitar(j, "80")
    c.esperar_previa(t)
    anotar("M3-numero-80", {"escala": pg.conteudo_escala, "campo": t.campo_tamanho_do_conteudo.value()})
    c.p(j, pasta, "M3-mover-numero-80")
    c.pdf_das_paginas(pr, [2], pasta, "M3")
    t.campo_tamanho_do_conteudo.clearFocus()
    ctrl(j, ord("Z"))
    c.esperar_previa(t)

    vis.repaint()
    meio = vis._area.center()
    base.arrastar(j, vis, meio, meio + QPoint(int(vis._area.width() * 0.9), 0), passos=20)
    c.esperar_previa(t)
    anotar("M4-arrastou-muito", {"desloc": pg.conteudo_deslocamento})
    c.p(j, pasta, "M4-mover-passou-da-beirada")
    c.pdf_das_paginas(pr, [2], pasta, "M4")
    ctrl(j, ord("Z"))
    c.esperar_previa(t)
    anotar("M-depois-dos-ctrl-z", {"desloc": pg.conteudo_deslocamento, "escala": pg.conteudo_escala})

    # P. Jeito do preto e branco (página 3)
    t.paineis.abrir("filtro")
    base.esperar(8.0)
    cartoes = t.paineis.filtro_da_pagina.cartoes
    base.clique(j, cartoes[PRETO_E_BRANCO])
    c.esperar_previa(t)
    anotar("P-filtro-pagina-3", pr.paginas[2].filtro)
    from ui.widgets.paineis import ParteQueAbre
    sel = t.seletor_algoritmo_pb
    w = sel.parentWidget()
    while w is not None and not isinstance(w, ParteQueAbre):
        w = w.parentWidget()
    for parte in t.paineis.filtro_da_pagina.findChildren(ParteQueAbre):
        parte.abrir(parte is w)
    base.esperar(1.0)
    from PySide6.QtWidgets import QScrollArea
    for area in t.paineis.filtro_da_pagina.findChildren(QScrollArea):
        if area.isAncestorOf(sel):
            area.ensureWidgetVisible(sel, 10, 120)
    base.esperar(1.0)
    c.p(j, pasta, "P0-painel-filtro-jeito")
    itens = [sel.itemText(i) for i in range(sel.count())]
    anotar("P-itens", itens)
    sel.showPopup()
    base.esperar(1.0)
    sel.view().window().grab().save(str(pasta / "P1-lista-hoje.png"))
    sel.hidePopup()
    novos = {"pelo-uso": ["o programa escolhe", "letra fina", "letra grossa ou gótica", "scan apagado"],
             "so-padrao": ["Automático", "Sauvola", "Otsu (letra grossa/gótica)", "Wolf (scan de baixo contraste)"]}
    for nome, lista in novos.items():
        for i, texto in enumerate(lista):
            sel.setItemText(i, texto)
        sel.showPopup()
        base.esperar(1.0)
        sel.view().window().grab().save(str(pasta / f"P2-lista-SIMULACAO-{nome}.png"))
        sel.hidePopup()
    for i, texto in enumerate(itens[:4]):
        sel.setItemText(i, texto)

    # A. Antes de processar (nada é processado: a janela é fechada no fim)
    def simular(jan):
        trocas = {
            "segunda": {"ver": "ir para a página", "continuar assim mesmo": "processar com os avisos"},
            "nova-1": {"ver": "ver a página", "continuar assim mesmo": "processar mesmo assim"},
            "nova-2": {"ver": "abrir esta página", "continuar assim mesmo": "processar sem olhar"},
            "nova-3": {"ver": "conferir a página", "continuar assim mesmo": "processar agora"},
        }
        anotar("A-botoes", [b.text() for b in (jan.botao_todas, jan.botao_nenhuma, jan.botao_aceitar,
                                                jan.botao_ver, jan.botao_continuar)])
        for nome, tr in trocas.items():
            antes = (jan.botao_ver.text(), jan.botao_continuar.text())
            jan.botao_ver.setText(tr["ver"])
            jan.botao_continuar.setText(tr["continuar assim mesmo"])
            base.esperar(0.8)
            c.p(jan, pasta, f"A1-SIMULACAO-{nome}")
            jan.botao_ver.setText(antes[0])
            jan.botao_continuar.setText(antes[1])
    base.quando_abrir_janela(JanelaDosAvisos, "A0-antes-de-processar-hoje", pasta, pasta / "textos.txt",
                             depois=simular, fechar=True)
    base.clique(j, t.botao_processar)
    base.esperar(12.0)
    anotar("A-depois", {"tela": j.telas.currentIndex()})

    # F. o botão "tamanho da folha..." do Mover (Propriedades)
    t.paineis.abrir("props")
    c.letra(j, "f")
    base.esperar(1.5)
    c.p(j, pasta, "F2-mover-tamanho-da-folha")
    t.paineis.abrir("automatico")
    base.esperar(1.0)
    c.p(j, pasta, "F3-automatico-endireitar-folhas")
    base.fechar(j)
    base.gravar_resultados(pasta)


if __name__ == "__main__":
    main()
