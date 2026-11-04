"""D-614 na janela de VERDADE (plataforma Windows, posta fora da tela): o Automático do Gradus Primus,
página 68, com o "Dividir" marcado. Cliques, arrastos e teclas por mensagens do Windows ao hwnd
(relatorios/obra-etapa3/roteiro/base.py); prints por PrintWindow. Mesmo jeito do
relatorios/mover-parou/piloto.py (ramo mover-parou-2026-11-04).

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF
aponta para a cópia do PDF.

O que faz e fotografa (prints/ e anotacoes.txt):
  1. abre o Automático na página 68, nenhuma etapa marcada; clica a caixinha "1 Dividir";
  2. o depois com a linha no meio e com a linha toda para a direita (arrastada);
  3. ">" (a outra metade), ">" (a folha 69), "<" "<" (volta à metade da esquerda da 68);
  4. "tela cheia", o "comparar" nela, ">" na tela cheia; fecha;
  5. ao redor: desmarcar Dividir (folha inteira de novo); Limpar em Preto e branco; Margens iguais;
     a etapa 7 aberta com o Dividir ("Folha 1 de 35");
  6. "Rodar" só com o Dividir: o livro passa a 140 páginas.

Rodar (na cópia previa-dividida):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\previa-dividida\\piloto.py
"""
from __future__ import annotations

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
               r"\scratchpad\previa-dividida-piloto")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
PAGINA = 67
LOG = open(AQUI / "anotacoes.txt", "w", encoding="utf-8")
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas que abrem por cima: anota o texto e clica no botão de fábrica (na pergunta das
    páginas mexidas, "Rodar nelas também")."""

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
                # a pergunta da D-004/D-607 ao "Rodar" (o livro de teste teve "juntar todas"):
                # "Rodar nelas também", para o Dividir dividir de verdade
                nelas = [b for b in w.buttons() if b.text() == "Rodar nelas também"]
                b = nelas[0] if nelas else (w.defaultButton() or w.buttons()[0])
                base.clique(w, b)
            finally:
                self.ocupado = False
            return


def preparar_copia() -> Path:
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


def esperar_previa(painel, limite=300):
    """Até a conta do antes e depois acabar (a bolinha parar). Devolve os segundos."""
    t = time.time()
    base.esperar(0.3)
    while time.time() - t < limite and painel.calculando():
        base.esperar(0.1)
    base.esperar(0.8)
    return round(time.time() - t, 2)


def caixinha(grande, etapa):
    """Clica a caixinha da etapa na lista (mensagens do Windows)."""
    from PySide6.QtCore import QPoint
    lista = grande.lista
    item = lista.item_da_etapa(etapa)
    r = lista.visualItemRect(item)
    antes = item.checkState()
    base.clique(grande, lista.viewport(), QPoint(r.left() + 18, r.center().y()))
    base.esperar(0.6)
    item = lista.item_da_etapa(etapa)
    anotar(f"caixinha-{etapa}", {"mudou": item.checkState() != antes,
                                 "marcadas": sorted(grande.estado.marcadas)})


def abrir_etapa(grande, etapa):
    """Clica no texto da etapa (abre as opções dela; não muda a caixinha)."""
    from PySide6.QtCore import QPoint
    lista = grande.lista
    r = lista.visualItemRect(lista.item_da_etapa(etapa))
    base.clique(grande, lista.viewport(), QPoint(r.center().x() + 40, r.center().y()))
    base.esperar(1.0)


def estado_da_previa(painel):
    import numpy as np  # noqa: F401
    d = painel._depois[1] if painel._depois else None
    a = painel._antes[1] if painel._antes else None
    return {"contador": painel.contador.text(), "indice": painel._indice, "metade": painel._metade,
            "antes": None if a is None else list(a.shape[:2]),
            "depois": None if d is None else list(d.shape[:2]),
            "linha": round(painel.visor.posicao, 2),
            "<": painel.botao_anterior.isEnabled(), ">": painel.botao_proxima.isEnabled()}


def main():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import projetos
    from core import automatico as A
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    _porteiro = Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    j.tela_conferir.ir_para_pagina(PAGINA)
    base.esperar(1.5)
    anotar("livro", {"paginas": len(j.projeto.paginas), "folhas": len(j.projeto.folhas),
                     "divididas": sum(1 for f in j.projeto.folhas if f.dividir)})

    # 1. a janela grande, nenhuma etapa marcada; depois a caixinha do Dividir
    grande = j.abrir_o_automatico()
    grande.resize(1460, 760)
    base.esperar(1.0)
    painel = grande.antes_e_depois
    for etapa in A.ETAPAS:
        if etapa in grande.estado.marcadas:
            caixinha(grande, etapa)
    abrir_etapa(grande, A.DIVIDIR)
    anotar("sem-etapa-s", esperar_previa(painel))
    anotar("sem-etapa", estado_da_previa(painel))
    p(grande, "sem-etapa-folha-inteira")
    t = time.time()
    caixinha(grande, A.DIVIDIR)
    anotar("marcar-dividir-ate-o-depois-s", round(esperar_previa(painel), 2))
    anotar("dividir-metade-esquerda", estado_da_previa(painel))
    p(grande, "dividir-pagina-68-linha-no-meio")

    # 2. a linha toda para a direita (arrastada pela mensagem do Windows)
    from PySide6.QtCore import QPoint
    vista = painel.visor
    area = vista._area(vista.depois)
    y = int(area.center().y())
    de = QPoint(int(area.left() + area.width() * vista.posicao), y)
    para = QPoint(int(area.right() + 30), y)
    base.arrastar(grande, vista, de, para)
    base.esperar(0.8)
    anotar("linha-a-direita", estado_da_previa(painel))
    p(grande, "dividir-pagina-68-linha-toda-a-direita")

    # 3. as setas
    t = time.time()
    base.clique(grande, painel.botao_proxima)
    anotar("seta-outra-metade-s", esperar_previa(painel))
    anotar("metade-direita", estado_da_previa(painel))
    p(grande, "seta-metade-direita-da-68")
    base.clique(grande, painel.botao_proxima)
    anotar("seta-folha-69-s", esperar_previa(painel))
    anotar("folha-69", estado_da_previa(painel))
    p(grande, "seta-folha-69")
    base.clique(grande, painel.botao_anterior)
    esperar_previa(painel)
    anotar("volta-1", estado_da_previa(painel))
    base.clique(grande, painel.botao_anterior)
    esperar_previa(painel)
    anotar("volta-2", estado_da_previa(painel))
    # a linha volta ao meio (arrastada)
    area = vista._area(vista.depois)
    y = int(area.center().y())
    base.arrastar(grande, vista, QPoint(int(area.left() + area.width() * vista.posicao) - 2, y),
                  QPoint(int(area.left() + area.width() * 0.5), y))
    base.esperar(0.8)
    anotar("linha-de-volta-ao-meio", estado_da_previa(painel))

    # 4. tela cheia e comparar
    base.clique(grande, painel.botao_tela_cheia)
    base.esperar(2.0)
    tela = painel.tela_cheia
    anotar("tela-cheia", {"aberta": tela is not None and tela.isVisible(), "contador": tela.contador.text(),
                          "depois": list(tela.visor._crus[1].shape[:2]) if tela.visor._crus[1] is not None else None})
    p(tela, "tela-cheia-metade-esquerda")
    base.clique(tela, tela.botao_comparar)
    esperar_previa(painel)
    base.esperar(1.5)
    anotar("comparar", {"ligado": tela.comparando, "a": tela.rotulo_a.text(), "b": tela.rotulo_b.text(),
                        "pix_b": [tela.vista_b._pixmap.height(), tela.vista_b._pixmap.width()]
                        if tela.vista_b._pixmap is not None else None})
    p(tela, "comparar-metade-esquerda")
    base.clique(tela, tela.botao_proxima)
    esperar_previa(painel)
    base.esperar(1.0)
    anotar("comparar-seta", {"painel": estado_da_previa(painel),
                             "pix_b": [tela.vista_b._pixmap.height(), tela.vista_b._pixmap.width()]
                             if tela.vista_b._pixmap is not None else None})
    p(tela, "comparar-metade-direita")
    base.clique(tela, tela.botao_comparar)
    base.esperar(1.0)
    base.clique(tela, tela.botao_anterior)
    esperar_previa(painel)
    base.tecla(tela, 0x1B)               # Esc fecha
    base.esperar(1.0)
    anotar("tela-cheia-fechou", painel.tela_cheia is None)

    # 5. ao redor: desmarcar o Dividir volta a folha inteira
    caixinha(grande, A.DIVIDIR)
    anotar("desmarcar-dividir-s", esperar_previa(painel))
    anotar("sem-dividir", estado_da_previa(painel))
    p(grande, "desmarcado-folha-inteira")
    # Limpar em Preto e branco (só ele)
    from core.filtros import PRETO_E_BRANCO
    caixinha(grande, A.LIMPAR)
    abrir_etapa(grande, A.LIMPAR)
    base.clique(grande, grande.radios_de_filtro[PRETO_E_BRANCO])
    anotar("limpar-pb-s", esperar_previa(painel))
    anotar("limpar-pb", estado_da_previa(painel))
    p(grande, "limpar-preto-e-branco")
    # com o Dividir junto: a metade, em Preto e branco
    caixinha(grande, A.DIVIDIR)
    anotar("dividir-e-limpar-s", esperar_previa(painel))
    anotar("dividir-e-limpar", estado_da_previa(painel))
    p(grande, "dividir-e-limpar-metade")
    caixinha(grande, A.LIMPAR)
    esperar_previa(painel)
    # Margens iguais com o Dividir
    caixinha(grande, A.MARGENS)
    abrir_etapa(grande, A.MARGENS)
    anotar("margens-s", esperar_previa(painel, limite=600))
    anotar("dividir-e-margens", estado_da_previa(painel))
    p(grande, "dividir-e-margens-iguais")
    caixinha(grande, A.MARGENS)
    esperar_previa(painel)
    # a etapa 7 aberta (sem marcar), com o Dividir marcado
    abrir_etapa(grande, A.CADERNOS)
    folhas = grande.folhas_do_caderno
    t = time.time()
    while time.time() - t < 300 and folhas.calculando():
        base.esperar(0.3)
    base.esperar(1.5)
    textos = [w.text() for w in grande.findChildren(__import__("PySide6.QtWidgets", fromlist=["QLabel"]).QLabel)
              if w.isVisible() and "olha" in w.text()]
    anotar("etapa-7", {"total": folhas.total(), "textos": textos, "s": round(time.time() - t, 1)})
    p(grande, "etapa-7-caderno-com-dividir")
    abrir_etapa(grande, A.DIVIDIR)
    esperar_previa(painel)

    # 6. Rodar só com o Dividir
    anotar("antes-de-rodar", {"marcadas": sorted(grande.estado.marcadas), "botao": grande.botao_rodar.text()})
    base.clique(grande, grande.botao_rodar)
    t = time.time()
    while time.time() - t < 600:
        base.esperar(1.0)
        if len(j.projeto.paginas) != 70 and not getattr(j, "_tarefa_do_automatico", None):
            break
    base.esperar(3.0)
    anotar("rodou", {"s": round(time.time() - t, 1), "paginas": len(j.projeto.paginas),
                     "divididas": sum(1 for f in j.projeto.folhas if f.dividir)})
    p(j, "depois-de-rodar-area-de-trabalho")
    base.fechar(j)
    LOG.close()


def so_a_tela_cheia():
    """Só o "tela cheia" (o print 06 da rodada inteira saiu branco: a janela maximizada fora da
    tela ainda não tinha desenhado a vista). Espera mais e fotografa também depois do comparar."""
    global LOG
    LOG = open(AQUI / "anotacoes-tela-cheia.txt", "w", encoding="utf-8")
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import projetos
    from core import automatico as A
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    _porteiro = Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    esperar_tela(j)
    j.tela_conferir.ir_para_pagina(PAGINA)
    base.esperar(1.5)
    grande = j.abrir_o_automatico()
    grande.resize(1460, 760)
    base.esperar(1.0)
    painel = grande.antes_e_depois
    for etapa in A.ETAPAS:
        if (etapa in grande.estado.marcadas) != (etapa == A.DIVIDIR):
            caixinha(grande, etapa)
    esperar_previa(painel)
    base.clique(grande, painel.botao_tela_cheia)
    tela = painel.tela_cheia
    base.esperar(5.0)
    tela.visor.update()
    base.esperar(1.0)
    anotar("tela-cheia", {"contador": tela.contador.text(), "visor": [tela.visor.width(), tela.visor.height()],
                          "rolagem_visivel": tela.rolagem.isVisible(),
                          "depois": list(tela.visor._crus[1].shape[:2]), "linha": tela.visor.posicao})
    # o PrintWindow desta janela maximizada fora da tela sai branco (o Windows não pede o
    # desenho dela); o print vem do próprio Qt (QWidget.grab: o mesmo desenho da janela)
    tela.grab().save(str(AQUI / "prints" / "15-tela-cheia-metade-esquerda.png"))
    base.clique(tela, tela.botao_proxima)
    esperar_previa(painel)
    base.esperar(2.0)
    anotar("tela-cheia-seta", estado_da_previa(painel))
    tela.grab().save(str(AQUI / "prints" / "16-tela-cheia-metade-direita.png"))
    base.tecla(tela, 0x1B)
    base.esperar(1.0)
    base.fechar(j)
    LOG.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "tela":
        so_a_tela_cheia()
    else:
        main()
