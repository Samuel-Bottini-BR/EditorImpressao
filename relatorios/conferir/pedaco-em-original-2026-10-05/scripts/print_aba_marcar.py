r"""Prints da aba Marcar com o aviso e o botão "Ajustar o pedaço à figura"
(conferência 13, S3), na Escola de Jesus 7 do gabarito: página em Preto e
branco, a pintura marcada com "só neste pedaço: Original" num retângulo com
folga larga. Três prints: com o aviso; depois de clicar no botão; depois do
Desfazer. A tela de conferir de verdade (TelaConferir, GerenciadorPrevias
real), sem janela na tela (offscreen), 1280 x 760. Pasta de dados descartável.

Uso: .venv\Scripts\python.exe relatorios\conferir\pedaco-em-original-2026-10-05\scripts\print_aba_marcar.py
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")     # o offscreen nao acha as fontes sozinho
TRABALHO = Path(tempfile.mkdtemp(prefix="print_marcar_"))
os.environ["LOCALAPPDATA"] = str(TRABALHO)
AQUI = Path(__file__).resolve().parents[1]
RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

from PySide6.QtWidgets import QApplication  # noqa: E402

from core import pipeline  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao  # noqa: E402
from historico_acoes import HistoricoAcoes  # noqa: E402
from modelos import Projeto  # noqa: E402
from ui.estilo import FOLHA_DE_ESTILO  # noqa: E402

FOLGADO = (0.33, 0.36, 1.0, 0.975)


def esperar(segundos: float, ate=lambda: False) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim and not ate():
        QApplication.processEvents()
        time.sleep(0.05)


def main() -> None:
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import ABA_MARCAR, TelaConferir

    app = QApplication.instance() or QApplication([])
    app.setStyleSheet(FOLHA_DE_ESTILO)
    pdf = RAIZ / "gabarito" / "paginas" / "escola_p007.pdf"
    projeto = Projeto(caminho_entrada=str(pdf), nome="escola_p007")
    projeto.filtro_padrao = PRETO_E_BRANCO
    projeto = pipeline.analisar_projeto(projeto)
    pagina = projeto.paginas[0]
    pagina.filtro = PRETO_E_BRANCO
    selecao = pagina.obter_selecao()
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[FOLGADO[:2], FOLGADO[2:]],
                               origem=MAO, filtro=ORIGINAL))
    pagina.guardar_selecao(selecao)

    tela = TelaConferir()
    tela.resize(1280, 760)
    previas = GerenciadorPrevias(str(pdf), projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index(ABA_MARCAR))
    tela.show()
    esperar(60, lambda: tela.editor_selecao._img is not None and not tela.linha_pedaco.isHidden())
    esperar(1.5)
    tela.grab().save(str(AQUI / "marcar-1-aviso.png"))
    print("aviso:", tela.aviso_pedaco.text())

    tela.botao_ajustar_pedaco.click()
    esperar(60, lambda: tela.editor_selecao._img is not None)
    esperar(1.5)
    tela.grab().save(str(AQUI / "marcar-2-ajustado.png"))
    print("depois:", pagina.obter_selecao().regioes[-1].pontos, "|", tela.aviso_pedaco.text())

    tela.desfazer()
    esperar(60, lambda: tela.editor_selecao._img is not None)
    esperar(1.5)
    tela.grab().save(str(AQUI / "marcar-3-desfeito.png"))
    print("desfeito:", pagina.obter_selecao().regioes[-1].pontos)
    previas.parar()
    tela.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        shutil.rmtree(TRABALHO, ignore_errors=True)
