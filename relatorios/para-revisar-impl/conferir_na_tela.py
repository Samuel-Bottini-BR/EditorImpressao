"""Confere, com a tela de conferir de verdade (sem aparecer no monitor) e com
os fios de verdade, que a medida do "Para revisar" chega por tras e que os
botoes do aviso funcionam, em paginas reais do estudo.

Uso: python conferir_na_tela.py        (uns 2 minutos; pasta de dados isolada)

O que faz, em tres paginas:
  - Antiphonal 1547 p. 46 (a letra T vermelha que some): o aviso "Desenho
    apagado" chega sozinho, com o lugar marcado; "Trazer de volta nesta
    página" troca a pagina para "Guardar tudo" e o aviso some.
  - Camoes p. 27 (texto falhado): a forca do preto vai sozinha para 85, o aviso
    "Força do preto escurecida" aparece; "Desfazer" devolve a forca.
  - Egenloff p. 12 (verso em branco): o aviso "Página sem conteúdo" com os dois
    botoes; "Deixar em branco" deixa a pagina no livro, branca.

As paginas sao preparadas como num LIVRO NOVO de hoje (endireitar antes de
cortar, conta do ScanTailor): desde o reacerto dos limites de 13/10/2026 a
letra T do Antiphonal 46 vai para a lista tambem nesse preparo. Nada aqui muda
o programa nem o acervo. Nao substitui o olho do verificador na janela.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(AQUI))

from pasta_de_dados_dos_scripts import isolar_pasta_de_dados  # noqa: E402

isolar_pasta_de_dados("conferir-na-tela")

from PySide6.QtWidgets import QApplication  # noqa: E402

import conferir_89  # noqa: E402
from core import analise, misto  # noqa: E402
from core import pipeline as P  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from historico_acoes import HistoricoAcoes  # noqa: E402
from modelos import Projeto  # noqa: E402

FALHAS: list[str] = []


def cobrar(certo: bool, frase: str) -> None:
    print(("  ok    " if certo else "  FALHOU ") + frase, flush=True)
    if not certo:
        FALHAS.append(frase)


def esperar(app, condicao, segundos: float = 90.0) -> bool:
    """Roda os eventos do Qt ate `condicao()` ser verdade (ou o tempo acabar)."""
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        app.processEvents()
        if condicao():
            return True
        time.sleep(0.05)
    return False


def abrir(app, pid: str):
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    projeto = Projeto(caminho_entrada=str(conferir_89._pdf_da_pagina(pid)), nome=pid)
    projeto.filtro_padrao = PRETO_E_BRANCO
    projeto.misto_so_as_letras = True
    projeto = P.analisar_projeto(projeto)
    for pagina in projeto.paginas:
        pagina.filtro = PRETO_E_BRANCO
    tela = TelaConferir()
    tela.resize(1300, 850)
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    tela.ir_para_pagina(0)
    return tela, previas, projeto.paginas[0]


def medida_pronta(previas) -> bool:
    return previas.chave_da_medida(0) in previas._cache


def main() -> int:
    app = QApplication.instance() or QApplication([])

    print("Antiphonal 1547 p. 46 (a letra T que some)", flush=True)
    tela, previas, pagina = abrir(app, "antiphonal1547_p046")
    cobrar(esperar(app, lambda: analise.DESENHO_APAGADO in pagina.alertas),
           "o aviso 'Desenho apagado' chegou sozinho (medida por tras)")
    primeiro = tela.botoes_de_sugestao["filtro"]
    cobrar(primeiro.text() == "Trazer de volta nesta página" and not primeiro.isHidden(),
           f"o botao do aviso e 'Trazer de volta nesta página' (esta: {primeiro.text()!r})")
    marcas = P.marcas_do_aviso(pagina, analise.DESENHO_APAGADO)
    cobrar(bool(marcas), f"o lugar onde sumiu veio marcado: {[tuple(round(v, 2) for v in m) for m in marcas]}")
    cobrar(tela.cartoes[PRETO_E_BRANCO].amostra._marcas == [tuple(m) for m in marcas],
           "o cartao do Preto e branco mostra a marca")
    primeiro.click()
    cobrar(pagina.misto_fora_do_texto == misto.FORA_TUDO, "a pagina passou para 'Guardar tudo'")
    cobrar(analise.DESENHO_APAGADO not in pagina.alertas, "o aviso sumiu sozinho")
    previas.parar()

    print("Camoes p. 27 (texto falhado: a forca do preto sozinha)", flush=True)
    tela, previas, pagina = abrir(app, "camoes_p027")
    cobrar(tela.projeto.reforcar_texto_falhado is True, "livro novo: a forca sozinha vem ligada")
    cobrar(esperar(app, lambda: analise.FORCA_REFORCADA in pagina.alertas),
           "o aviso 'Força do preto escurecida' chegou sozinho")
    cobrar(pagina.forca_preto == P.FORCA_DO_REFORCO and pagina.forca_antes_do_reforco == 50,
           f"a forca foi de 50 para {pagina.forca_preto}, so nesta pagina")
    esperar(app, lambda: tela.medidor.valor == P.FORCA_DO_REFORCO, 20)
    cobrar(tela.medidor.valor == P.FORCA_DO_REFORCO, f"o medidor mostra a forca nova ({tela.medidor.valor})")
    cobrar(analise.TEXTO_FALHADO not in pagina.alertas,
           f"com a forca mais escura o texto nao sai mais falhado (avisos: {pagina.alertas})")
    primeiro = tela.botoes_de_sugestao["filtro"]
    cobrar(primeiro.text() == "Desfazer", f"o botao do aviso e 'Desfazer' (esta: {primeiro.text()!r})")
    primeiro.click()
    cobrar(pagina.forca_preto == 50 and pagina.reforco_desfeito, "o 'Desfazer' devolveu a forca 50")
    cobrar(esperar(app, lambda: analise.TEXTO_FALHADO in pagina.alertas),
           "sem o reforco, o aviso 'Texto falhado' aparece (e a forca nao volta a escurecer)")
    cobrar(pagina.forca_preto == 50, "a forca continua 50 depois de medir de novo")
    previas.parar()

    print("Egenloff p. 12 (verso em branco: pagina sem conteudo)", flush=True)
    tela, previas, pagina = abrir(app, "egenloff_p012")
    cobrar(esperar(app, lambda: analise.PAGINA_SEM_CONTEUDO in pagina.alertas),
           "o aviso 'Página sem conteúdo' chegou sozinho")
    esperar(app, lambda: bool(pagina.alertas_pendentes)
            and pagina.alertas_pendentes[0] == analise.PAGINA_SEM_CONTEUDO, 5)
    print("    avisos da pagina:", pagina.alertas_pendentes, flush=True)
    if pagina.alertas_pendentes and pagina.alertas_pendentes[0] == analise.PAGINA_SEM_CONTEUDO:
        primeiro, segundo = tela.botoes_de_sugestao["filtro"], tela.botoes_de_sugestao_2["filtro"]
        cobrar((primeiro.text(), segundo.text()) == ("Deixar em branco", "Tirar do livro"),
               f"os dois botoes: {primeiro.text()!r} e {segundo.text()!r}")
        primeiro.click()
        cobrar(pagina.em_branco and not pagina.apagada and pagina in tela.projeto.paginas_ativas,
               "'Deixar em branco': a pagina fica no livro")
        chave = previas.chave(0, tela._dpi_atual)
        esperar(app, lambda: chave in previas._cache, 60)
        img = previas._cache.get(chave)
        cobrar(img is not None and int(img.min()) == 255, "a previa da pagina ficou toda branca")
    else:
        cobrar(False, "o aviso 'Página sem conteúdo' nao e o primeiro da pagina")
    previas.parar()

    print()
    print("TUDO CERTO" if not FALHAS else f"FALHAS: {FALHAS}")
    return 1 if FALHAS else 0


if __name__ == "__main__":
    sys.exit(main())
