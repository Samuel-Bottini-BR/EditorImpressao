"""Prints novos da Parte 2 (aba nomes-28-10), sem janela na tela.

A. nm-desligar-marcadas (Gradus, cópia): o que o botão "desligar as marcadas" faz.
   1. Automático só com "Dividir folhas ao meio", no livro todo: as folhas ficam divididas.
      Foto com o painel Automático aberto (a etapa Dividir marcada, "Rodar: no livro todo").
   2. "desligar as marcadas" (o mesmo que o botão chama: rodar_o_automatico(desligar=True)):
      as folhas voltam inteiras. Foto igual.
B. nm-jeito-pb (Palatino, cópia, página 9): a mesma página em Preto e branco com cada um dos quatro
   primeiros da lista "Jeito do preto e branco" (Automático, Sauvola, Otsu, Wolf), desenhada pela
   mesma conta do PDF (core.pipeline.renderizar_pagina), livro novo de fábrica, sem dividir.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum  # noqa: E402

CRU = comum.CRU / "p4"
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", json.dumps(valor, ensure_ascii=False, default=str), flush=True)
    (CRU / "notas.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")


def mostrar_automatico(tela):
    from ui.widgets.paineis import PAINEL_AUTOMATICO
    try:
        tela.paineis.mostrar_painel(PAINEL_AUTOMATICO, True)
    except Exception as erro:  # noqa: BLE001
        nota("erro ao abrir o painel", str(erro))


def parte_a():
    from core import automatico as A

    j = comum.nova_janela()
    j.abrir_livro(str(comum.LIVROS / "gradus.pdf"))
    nota("A abrir (s)", comum.esperar_tela(j))
    projeto, tela = j.projeto, j.tela_conferir
    estado = j.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    nota("A rodou o dividir", j.rodar_o_automatico(esperar=True, perguntar=False))
    comum.esperar(2.0)
    try:
        j._fechar_a_janela_do_automatico()
    except Exception:
        pass
    nota("A paginas depois de dividir", len(projeto.paginas_ativas))
    tela.ir_para_pagina(20)
    mostrar_automatico(tela)
    comum.esperar(2.0)
    comum.esperar_previas(tela, [20])
    nota("A marcadas antes", sorted(estado.marcadas))
    comum.foto(j, CRU / "a1-depois-do-dividir.png")

    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    nota("A desligou", j.rodar_o_automatico(desligar=True, esperar=True, perguntar=False))
    comum.esperar(3.0)
    nota("A paginas depois de desligar", len(projeto.paginas_ativas))
    nota("A historico", j.acoes.feitas[-1].descricao if j.acoes.feitas else None)
    tela.ir_para_pagina(10)
    mostrar_automatico(tela)
    comum.esperar(2.0)
    comum.esperar_previas(tela, [10])
    comum.foto(j, CRU / "a2-depois-de-desligar.png")
    comum.fechar(j)


def parte_b():
    import cv2

    from core import pipeline
    from core.filtros import PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf

    j = comum.nova_janela()
    j.abrir_livro(str(comum.LIVROS / "palatino.pdf"))
    nota("B abrir (s)", comum.esperar_tela(j))
    projeto = j.projeto
    pagina = projeto.paginas[8]                       # página 9
    projeto.limpar = True        # "Limpar a folha" ligado: o filtro da página vale (core/etapas.filtro_que_vale)
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for valor in ("auto", "sauvola", "otsu", "wolf"):
            pagina.filtro = PRETO_E_BRANCO
            pagina.algoritmo_preto_branco = valor
            img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=150)
            cv2.imwrite(str(CRU / f"b-pagina-9-{valor}.png"), img)
            nota(f"B {valor}", list(img.shape))
        from core.filtros import escolher_algoritmo_automatico
        projeto.limpar = False
        pagina.filtro = "original"
        img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=150)
        cv2.imwrite(str(CRU / "b-pagina-9-original.png"), img)
        cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
        nota("B o automatico escolheria", escolher_algoritmo_automatico(cinza))
    finally:
        doc.close()
    comum.fechar(j)


def main():
    import faulthandler
    faulthandler.dump_traceback_later(2400, exit=True)
    comum.preparar("p4")
    pedidos = sys.argv[1:] or ["a", "b"]
    if "a" in pedidos:
        parte_a()
    if "b" in pedidos:
        parte_b()


if __name__ == "__main__":
    main()
