"""Captura, SEM JANELA NA TELA (QT_QPA_PLATFORM=offscreen), as imagens dos prints dos defeitos
D-649 (miniatura x PDF) e D-648 (cartões da tela cheia), numa versão do programa.

    python capturar.py <raiz do código> <pasta de saída> <cópia do Palatino (12 páginas)>

Roda a mesma coisa no código antigo (obra 58806f81) e no novo (graves-2026-11-10); o
montar.py junta as duas no modelo do girar. Usa um LOCALAPPDATA e uma pasta de projetos à
parte (nada do Samuel é tocado) e só uma CÓPIA do livro.

O caminho: Palatino (cópia, páginas 1 a 12), aberto como livro novo, "Não" na pergunta do
fundo, filtro Original de fábrica. Página 9: ferramenta Mover, conteúdo 17% para cima (o
deslocamento do Lusíadas de 07/11). Depois: PDF; fechar e reabrir o livro na página 1;
miniaturas (tira e "Todas as páginas"); "Filtros em tela cheia" com a ferramenta Cortar.
"""
from __future__ import annotations

import copy
import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ, SAIDA, LIVRO = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
SAIDA.mkdir(parents=True, exist_ok=True)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")   # as letras da tela, sem janela
dados = Path(tempfile.mkdtemp(prefix="graves-prints-"))
os.environ["LOCALAPPDATA"] = str(dados / "dados")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

import fitz  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402

(dados / "projetos").mkdir()
projetos.pasta_dos_projetos = lambda: dados / "projetos"
app = QApplication.instance() or QApplication([])

from ui.janela_principal import JanelaPrincipal  # noqa: E402

MOVIDA = 8          # a página 9


def assentar(segundos: float) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


def esperar(condicao, segundos: float = 60) -> bool:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        if condicao():
            return True
        time.sleep(0.05)
    return False


def sem_a_pergunta_do_fundo(janela) -> None:
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)            # "Não": fica em Original
        assentar(0.3)


janela = JanelaPrincipal()
janela.resize(1600, 900)
janela.abrir_livro(LIVRO)
sem_a_pergunta_do_fundo(janela)
tela = janela.tela_conferir
tela.ir_para_pagina(MOVIDA)
tela.escolher_ferramenta("mover")
esperar(lambda: tela.previas.ja_pronta(MOVIDA, tela._dpi_atual) is not None)
tela._gravar_o_conteudo(1.0, (0.0, -0.17), "conteúdo 17% para cima")
assentar(0.5)

# o PDF (o "Confirmar e processar")
from core.pipeline import processar  # noqa: E402

projeto = copy.copy(janela.projeto)
projeto.caminho_saida = str(SAIDA / "saida.pdf")
with fitz.open(processar(projeto)) as doc:
    doc[MOVIDA].get_pixmap(dpi=60).save(str(SAIDA / "pdf-pagina-9.png"))

# fechar e reabrir, na página 1 (nenhuma prévia guardada)
tela.ir_para_pagina(0)
janela._salvar_agora()
janela.abrir_livro(LIVRO)
sem_a_pergunta_do_fundo(janela)
tela = janela.tela_conferir
tela.ir_para_pagina(0)
tela.escolher_ferramenta("filtros")
assentar(25)                                     # tempo de sobra para as prévias por trás
for i in range(6, 11):
    tela.tira._miniaturas[i].grab().save(str(SAIDA / f"tira-{i + 1}.png"))
tela.abrir_todas_as_paginas()
assentar(10)
for quadro in tela.todas.quadros:
    if quadro.itens[0].indice in range(6, 11):
        quadro.grab().save(str(SAIDA / f"grade-{quadro.itens[0].indice + 1}.png"))
tela._voltar_das_todas(None)

# "Filtros em tela cheia" com a ferramenta Cortar (o painel do Filtro fechado), página 9
from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia  # noqa: E402

tela.escolher_ferramenta("cortar")
tela.ir_para_pagina(MOVIDA)
assentar(1)
cheia = FiltrosEmTelaCheia(tela, parent=janela)
cheia.resize(1600, 900)
cheia.show()
assentar(30)
cheia.atualizar()
assentar(1)
cheia.grab().save(str(SAIDA / "tela-cheia.png"))
cheia.done(0)
if janela.previas is not None:
    janela.previas.parar()
janela.close()
print("pronto", SAIDA)
