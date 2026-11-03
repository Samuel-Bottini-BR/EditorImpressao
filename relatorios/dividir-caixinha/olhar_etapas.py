"""D-590 (03/11/2026): o print da janela grande reaberta com o "Dividir" desmarcado, e o OLHAR (sem
conserto) das etapas 2 Endireitar, 3 Cortar as bordas e 4 Limpar a folha.

O que faz (na janela de verdade do programa, offscreen, com a pasta de dados ISOLADA: LOCALAPPDATA
aponta para _tmp/dividir-caixinha-dados, nunca a pasta de dados do Samuel):
  1. Dividir: livro sintético de 3 folhas abertas (duas páginas lado a lado) → Rodar "Dividir" e
     "Limpar" → na janela grande desmarcar "1 Dividir" e Rodar → print do painel e da janela grande
     aberta de novo; diz as páginas, a caixinha e a situação.
  2. Para cada etapa 2, 3 e 4: livro sintético (uma página torta, com margem preta de scanner) →
     Rodar a etapa junto com outra (para o "Rodar" valer) → desmarcar a etapa na janela grande e
     Rodar → a caixinha volta marcada? a etapa continua valendo no livro (o campo do livro que o
     PDF lê)? print da janela aberta de novo.
  3. Liga sozinha? Livro novo → Rodar UMA etapa por vez (a janela começa sem nada marcado de
     propósito) → que etapas a janela mostra marcadas depois?
Uso (na pasta da cópia):

    $env:QT_QPA_PLATFORM="offscreen"; ...python.exe relatorios/dividir-caixinha/olhar_etapas.py
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = Path(__file__).resolve().parent
DADOS = RAIZ / "_tmp" / "dividir-caixinha-dados"
shutil.rmtree(DADOS, ignore_errors=True)
(DADOS / "projetos").mkdir(parents=True)
os.environ["LOCALAPPDATA"] = str(DADOS)                  # pasta de dados isolada
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"        # sem isso o offscreen desenha quadradinhos
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402
from core import automatico as A  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402

projetos.pasta_dos_projetos = lambda: DADOS / "projetos"
APP = QApplication.instance() or QApplication([])
AMARELADO = (170, 215, 235)


def assentar(vezes: int = 40) -> None:
    for _ in range(vezes):
        APP.processEvents()


def _pagina(giro: float = 0.0, borda: bool = False) -> np.ndarray:
    img = np.full((840, 600, 3), AMARELADO, np.uint8)
    for y in range(140, 680, 40):
        img[y:y + 12, 110:490] = 25
    if giro:
        m = cv2.getRotationMatrix2D((300, 420), giro, 1.0)
        img = cv2.warpAffine(img, m, (600, 840), borderValue=AMARELADO)
    if borda:
        img[:, :30] = 10
        img[:30, :] = 10
    return img


def _pdf(nome: str, imagens) -> str:
    caminho = DADOS / nome
    doc = fitz.open()
    for img in imagens:
        ok, buffer = cv2.imencode(".png", img)
        largura, altura = img.shape[1] / 150 * 72, img.shape[0] / 150 * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _janela(caminho: str):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 720)
    janela.show()
    janela.abrir_livro(caminho)
    assentar()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    return janela


def _fechar(janela) -> None:
    janela._fechar_a_janela_do_automatico()
    janela.close()


def _marcada(lista, etapa: str) -> bool:
    return lista.item_da_etapa(etapa).checkState() == Qt.Checked


def _rodar_pela_janela(janela, etapa: str, marcar: bool) -> None:
    jan = janela.abrir_o_automatico()
    assentar()
    jan.lista.item_da_etapa(etapa).setCheckState(Qt.Checked if marcar else Qt.Unchecked)
    assentar()
    jan.botao_rodar.click()
    if janela.tarefa is not None:
        janela.tarefa.wait(120000)
    assentar(60)


def _print_reaberta(janela, etapa: str, nome: str) -> bool:
    jan = janela.abrir_o_automatico(etapa)
    jan.resize(1280, 720)
    jan.lista.scrollToTop()
    assentar(60)
    jan.grab().save(str(SAIDA / nome))
    marcada = _marcada(jan.lista, etapa)
    frase = jan.frase.text()
    janela._fechar_a_janela_do_automatico()
    return marcada, frase


def dividir() -> None:
    caminho = _pdf("aberto.pdf", [np.concatenate([_pagina(), _pagina()], axis=1)] * 3)
    janela = _janela(caminho)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR, A.LIMPAR}
    janela.rodar_o_automatico(esperar=True, perguntar=False)
    assentar()
    _rodar_pela_janela(janela, A.DIVIDIR, marcar=False)
    janela.tela_conferir.paineis.mostrar_painel("automatico", True)
    assentar(40)
    janela.grab().save(str(SAIDA / "1-painel-depois-de-rodar-dividir-desmarcado.png"))
    marcada, frase = _print_reaberta(janela, A.DIVIDIR, "2-janela-reaberta-dividir-desmarcado.png")
    p = janela.projeto
    print(f"DIVIDIR: paginas={len(p.paginas)} folhas_divididas={sum(f.dividir for f in p.folhas)} "
          f"dividir_folhas={p.dividir_folhas} situacao='{estado.situacoes[A.DIVIDIR]}' "
          f"caixinha_reaberta_marcada={marcada} frase='{frase}'")
    janela._salvar_agora()
    _fechar(janela)
    janela = _janela(caminho)                            # fechar e reabrir o trabalho
    marcada, frase = _print_reaberta(janela, A.DIVIDIR, "3-trabalho-reaberto-janela-dividir.png")
    print(f"DIVIDIR (trabalho reaberto): paginas={len(janela.projeto.paginas)} "
          f"caixinha_marcada={marcada} frase='{frase}'")
    _fechar(janela)


CAMPO = {A.ENDIREITAR: "endireitar", A.CORTAR: "cortar_bordas", A.LIMPAR: "limpar"}


def olhar(etapa: str, n: int) -> None:
    caminho = _pdf(f"olhar-{etapa}.pdf", [_pagina(giro=3.0, borda=True)] * 2)
    janela = _janela(caminho)
    estado = janela.estado_do_automatico
    outra = A.MARGENS if etapa != A.MARGENS else A.LIMPAR
    estado.marcadas = {etapa, outra}
    estado.opcoes["filtro_padrao"] = PRETO_E_BRANCO
    janela.rodar_o_automatico(esperar=True, perguntar=False)
    assentar()
    antes = getattr(janela.projeto, CAMPO[etapa])
    _rodar_pela_janela(janela, etapa, marcar=False)
    p = janela.projeto
    marcada, frase = _print_reaberta(janela, etapa, f"{n}-olhar-{etapa}-desmarcada-reaberta.png")
    print(f"{etapa.upper()}: ligada_antes={antes} campo_do_livro_depois={getattr(p, CAMPO[etapa])} "
          f"situacao='{estado.situacoes[etapa]}' marcada_no_estado={etapa in estado.marcadas} "
          f"caixinha_reaberta_marcada={marcada} frase='{frase}'")
    _fechar(janela)


def liga_sozinha() -> None:
    for etapa in (A.DIVIDIR, A.ENDIREITAR, A.CORTAR, A.LIMPAR, A.GRAVURAS, A.MARGENS, A.CADERNOS):
        caminho = _pdf(f"sozinha-{etapa}.pdf", [_pagina(giro=3.0, borda=True)] * 2)
        janela = _janela(caminho)
        estado = janela.estado_do_automatico
        estado.marcadas = {etapa}
        janela.rodar_o_automatico(esperar=True, perguntar=False)
        assentar()
        mais = sorted(set(estado.marcadas) - {etapa})
        print(f"SO {etapa.upper()} marcada e Rodar -> marcadas depois: {sorted(estado.marcadas)}"
              f"{'  (LIGOU SOZINHA: ' + ', '.join(mais) + ')' if mais else ''}")
        _fechar(janela)


if __name__ == "__main__":
    dividir()
    for n, etapa in ((4, A.ENDIREITAR), (5, A.CORTAR), (6, A.LIMPAR)):
        olhar(etapa, n)
    liga_sozinha()
