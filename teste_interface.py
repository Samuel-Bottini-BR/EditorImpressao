"""Dirige a interface de verdade e salva capturas de cada tela.

Uso:
    python teste_interface.py "livro.pdf"

Abre a janela, carrega o livro, roda a analise, passa pela tela de conferir
mexendo nos controles (filtro, corte, desfazer, refazer, apagar) e grava PNG de
cada passo em saida_teste/interface/. Serve para conferir a interface sem
precisar clicar em nada.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

SAIDA = Path("saida_teste/interface")
_passo = 0


def capturar(janela, nome: str) -> None:
    global _passo
    _passo += 1
    QApplication.processEvents()
    caminho = SAIDA / f"{_passo:02d}_{nome}.png"
    janela.grab().save(str(caminho))
    print(f"  captura: {caminho.name}")


def esperar(segundos: float, condicao=None) -> bool:
    """Deixa a interface respirar enquanto uma thread trabalha."""
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        QApplication.processEvents()
        if condicao is not None and condicao():
            return True
        time.sleep(0.02)
    return condicao() if condicao else True


def tecla(janela, chave, modificadores=Qt.NoModifier) -> None:
    janela.keyPressEvent(QKeyEvent(QEvent.KeyPress, chave, modificadores))
    QApplication.processEvents()


def main(caminho_pdf: str) -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)

    from ui.janela_principal import CONFERIR, FINAL, OPCOES, JanelaPrincipal

    janela = JanelaPrincipal()
    janela.show()
    esperar(0.4)
    capturar(janela, "tela1_inicio")

    print("Abrindo o livro...")
    janela.abrir_livro(caminho_pdf)
    esperar(0.3)
    assert janela.telas.currentIndex() == OPCOES, "nao chegou na tela de opcoes"
    capturar(janela, "tela2_opcoes")

    # marca tambem "montar cadernos", para a tela final mostrar as instrucoes
    janela.tela_opcoes.cx_cadernos.setChecked(True)
    esperar(0.2)
    capturar(janela, "tela2_com_cadernos")

    print("Analisando (isso leva alguns segundos)...")
    janela.analisar()
    esperar(1.0)
    capturar(janela, "progresso_analise")
    pronto = esperar(120, lambda: janela.telas.currentIndex() == CONFERIR)
    assert pronto, "a analise nao terminou"

    projeto = janela.projeto
    print(f"  {len(projeto.folhas)} folhas -> {len(projeto.paginas)} paginas")
    print(f"  pendentes de revisao: {projeto.pendentes_de_revisao()}")

    conferir = janela.tela_conferir
    esperar(3.0)   # deixa as primeiras previas chegarem
    capturar(janela, "tela3_onde_cortar")

    # --- aba Filtro -------------------------------------------------------
    abas = conferir._abas_ativas
    print(f"  abas: {abas}")
    conferir.abas.setCurrentIndex(abas.index("filtro"))
    esperar(4.0)
    capturar(janela, "tela3_filtro")

    # --- mexer nos controles ---------------------------------------------
    print("Trocando o filtro da pagina 2 para Magico pro...")
    conferir._ir_para(1)
    esperar(2.0)
    from core.filtros import MAGICO_PRO, PRETO_E_BRANCO

    antes = projeto.paginas[1].filtro
    conferir._escolher_filtro(MAGICO_PRO)
    esperar(3.0)
    assert projeto.paginas[1].filtro == MAGICO_PRO
    capturar(janela, "filtro_trocado")

    print("Desfazendo (Ctrl+Z)...")
    tecla(janela, Qt.Key_Z, Qt.ControlModifier)
    esperar(0.5)
    assert projeto.paginas[1].filtro == antes, "o desfazer nao voltou o filtro"

    print("Refazendo (Ctrl+Shift+Z)...")
    tecla(janela, Qt.Key_Z, Qt.ControlModifier | Qt.ShiftModifier)
    esperar(0.5)
    assert projeto.paginas[1].filtro == MAGICO_PRO, "o refazer nao reaplicou"
    print("  desfazer e refazer OK")

    print("Aplicando em todas e desfazendo o lote inteiro...")
    conferir._filtro_em_todas()
    esperar(0.6)
    assert all(p.filtro == MAGICO_PRO for p in projeto.paginas)
    tecla(janela, Qt.Key_Z, Qt.ControlModifier)
    esperar(0.6)
    diferentes = sum(1 for p in projeto.paginas if p.filtro != MAGICO_PRO)
    assert diferentes > 0, "um Ctrl+Z tinha que desfazer o lote inteiro"
    print(f"  o lote voltou com um unico Ctrl+Z ({diferentes} paginas restauradas)")

    print("Apagando uma pagina (Delete)...")
    tecla(janela, Qt.Key_Delete)
    esperar(0.4)
    assert projeto.total_apagadas == 1
    capturar(janela, "pagina_apagada")
    tecla(janela, Qt.Key_Z, Qt.ControlModifier)
    esperar(0.3)
    assert projeto.total_apagadas == 0

    print("Navegando com as setas e com Tab...")
    tecla(janela, Qt.Key_Right)
    tecla(janela, Qt.Key_Right)
    esperar(1.0)
    tecla(janela, Qt.Key_Tab)
    esperar(2.0)
    capturar(janela, "pulou_para_alerta")

    # --- aba Onde cortar: arrastar a linha --------------------------------
    if "corte" in abas:
        conferir.abas.setCurrentIndex(abas.index("corte"))
        esperar(2.5)
        folha = projeto.folhas[conferir.indice_folha]
        anterior = folha.posicao_corte
        conferir._mover_corte(0.47)
        esperar(1.5)
        assert abs(folha.posicao_corte - 0.47) < 1e-6
        print(f"  linha de corte movida de {anterior:.3f} para 0,470")
        capturar(janela, "corte_movido")

    # --- processar --------------------------------------------------------
    print("Processando o livro inteiro...")
    janela.processar()
    esperar(2.0)
    capturar(janela, "progresso_processar")
    pronto = esperar(600, lambda: janela.telas.currentIndex() == FINAL)
    assert pronto, "o processamento nao terminou"
    esperar(0.5)
    capturar(janela, "tela4_pronto")

    saida = Path(janela.tela_final.caminho)
    print(f"  gerado: {saida.name} ({saida.stat().st_size / 1024 / 1024:.1f} MB)")

    print("\nTudo passou.")
    janela.close()
    esperar(0.5)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
