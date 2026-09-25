"""Testa os medidores deslizantes e captura a aba Filtro reorganizada.

Uso:
    python teste_medidor.py "livro.pdf"

Confere que arrastar o medidor muda a imagem de verdade, que o desfazer volta
o valor num Ctrl+Z só, e que cada filtro mostra o seu próprio medidor.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication

SAIDA = Path("saida_teste/medidor")


def esperar(segundos: float, condicao=None) -> bool:
    """Bombeia o loop de eventos do Qt ate `segundos` passarem ou `condicao`
    ficar verdadeira (o que vier primeiro). Devolve se a condicao foi atendida."""
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        QApplication.processEvents()
        if condicao is not None and condicao():
            return True
        time.sleep(0.02)
    return condicao() if condicao else True


def capturar(janela, nome: str) -> None:
    """Tira um print da janela e grava em SAIDA/<nome>.png."""
    QApplication.processEvents()
    caminho = SAIDA / f"{nome}.png"
    janela.grab().save(str(caminho))
    print(f"  captura: {caminho.name}")


def main(caminho_pdf: str) -> int:
    """Abre o programa de verdade (janela real, cliques simulados) e confere:
    cada filtro mostra o medidor certo, arrastar o medidor muda a imagem de
    fato, um arrasto inteiro vira UMA acao no desfazer, e "aplicar a todas"
    leva o ajuste do medidor junto. Grava um print a cada checagem."""
    SAIDA.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)

    from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO
    from ui.janela_principal import CONFERIR, JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1300, 850)
    janela.show()
    janela.abrir_livro(caminho_pdf)
    esperar(0.3)

    print("Analisando...")
    janela.analisar()
    if not esperar(180, lambda: janela.telas.currentIndex() == CONFERIR):
        print("a análise não terminou")
        return 1

    conferir = janela.tela_conferir
    projeto = janela.projeto
    conferir.barra_abas.setCurrentIndex(conferir._abas_ativas.index("filtro"))
    conferir._ir_para(2)
    esperar(4.0)

    falhas = 0

    # --- cada filtro mostra o seu medidor ---------------------------------
    esperados = {
        PRETO_E_BRANCO: ("Força do preto", "forca_preto"),
        MELHORAR: ("Clareza do fundo", "clareza_melhorar"),
        MAGICO_PRO: ("Intensidade", "intensidade_magico"),
    }
    print("\n--- o medidor acompanha o filtro escolhido ---")
    for filtro, (rotulo, campo) in esperados.items():
        conferir._escolher_filtro(filtro)
        esperar(1.5)
        visivel = conferir.bloco_ajuste.isVisible()
        atual = conferir.medidor.rotulo.text()
        ok = visivel and atual == rotulo
        falhas += 0 if ok else 1
        print(f"  {'ok   ' if ok else 'FALHA'} {filtro:<15} -> '{atual}'")
        capturar(janela, f"medidor_{filtro}")

    conferir._escolher_filtro(ORIGINAL)
    esperar(1.0)
    sem_ajuste = not conferir.bloco_ajuste.isVisible()
    falhas += 0 if sem_ajuste else 1
    print(f"  {'ok   ' if sem_ajuste else 'FALHA'} original        -> sem bloco de ajuste")

    # --- arrastar muda a imagem -------------------------------------------
    print("\n--- arrastar o medidor muda a página ---")
    conferir._escolher_filtro(PRETO_E_BRANCO)
    esperar(2.5)
    pagina = projeto.paginas[conferir.indice_pagina]

    from core.filtros import aplicar_filtro
    from core.pipeline import preparar_metade

    base = conferir._imagem_sem_filtro()
    pretos = []
    for valor in (10, 50, 90):
        saida, _ = aplicar_filtro(base, PRETO_E_BRANCO, forca_preto=valor)
        pretos.append(float((saida == 0).mean()))
    ordenado = pretos == sorted(pretos)
    falhas += 0 if ordenado else 1
    print(f"  {'ok   ' if ordenado else 'FALHA'} tinta por valor do medidor: "
          f"{['%.3f' % p for p in pretos]}")

    # --- o arrasto vira UMA ação no desfazer ------------------------------
    print("\n--- um arrasto inteiro = uma ação no desfazer ---")
    antes_valor = pagina.forca_preto
    antes_pilha = len(conferir.acoes.feitas)

    conferir._medidor_pegou()
    for valor in range(antes_valor, 91, 10):     # simula o arrasto passo a passo
        conferir._medidor_arrastando(valor)
        esperar(0.05)
    conferir._medidor_soltou(90)
    esperar(1.0)

    acoes_criadas = len(conferir.acoes.feitas) - antes_pilha
    uma_acao = acoes_criadas == 1 and pagina.forca_preto == 90
    falhas += 0 if uma_acao else 1
    print(f"  {'ok   ' if uma_acao else 'FALHA'} {acoes_criadas} ação(ões) para "
          f"{antes_valor} -> {pagina.forca_preto}")
    capturar(janela, "medidor_arrastado")

    conferir.desfazer()
    esperar(0.5)
    voltou = pagina.forca_preto == antes_valor
    falhas += 0 if voltou else 1
    print(f"  {'ok   ' if voltou else 'FALHA'} Ctrl+Z devolveu para {pagina.forca_preto}")

    # --- 'todas' leva o ajuste junto --------------------------------------
    print("\n--- 'todas' leva o ajuste junto ---")
    conferir._medidor_pegou()
    conferir._medidor_arrastando(75)
    conferir._medidor_soltou(75)
    esperar(0.6)
    conferir._filtro_em_todas()
    esperar(0.6)
    todas = all(p.forca_preto == 75 for p in projeto.paginas)
    falhas += 0 if todas else 1
    print(f"  {'ok   ' if todas else 'FALHA'} todas as {len(projeto.paginas)} "
          f"páginas com o ajuste 75")

    print(f"\n{falhas} problemas")
    janela.close()
    esperar(0.4)
    return 1 if falhas else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
