"""Desentortar a página curva perto da lombada (item 2.12 da Fase 2, 21/10/2026).

O PEDIDO
    Item 2.12 do plano: "Desentortar página curva perto da lombada". Regra da
    Fase 2 (Samuel, 13/10/2026): "implementar igual ao ScanTailor, sem
    perguntar antes" - com os ajustes de fábrica dele e, como muda a imagem,
    DESLIGADO de fábrica (livro novo e livro já começado saem iguais ao de
    hoje).

COMO O SCANTAILOR FAZ (src/dewarping e OutputGenerator.cpp, v1.2.1)
    O livro aberto no scanner faz a folha subir perto da lombada: as linhas
    do texto saem curvas e as letras ficam espremidas ali. O ScanTailor segue
    as linhas do texto (ou as beiradas brancas de cima e de baixo), monta
    duas curvas - a de cima e a de baixo do bloco de texto -, imagina a folha
    como um pedaço de cilindro entre elas e redesenha a página reta. É
    redesenho de pontos (como girar), não inventa detalhe. A cola em C está em
    terceiros/scantailor-advanced/ligacao-ferramentas/desentortar.cpp (a
    ordem e o que foi trocado estão no topo dela).

    Modos do ScanTailor e o que veio:
      "desligado"      OFF, o de fábrica dele e o nosso;
      "automatico"     AUTO: as curvas pelas linhas do texto;
      "pelas_margens"  MARGINAL: as curvas pelas beiradas brancas de cima e
                       de baixo, e um endireitar depois (o "post deskew",
                       ligado de fábrica no ScanTailor);
      (MANUAL, a malha mexida à mão, NÃO veio: precisa de uma tela de malha
       que o programa não tem.)
    Profundidade ("Depth perception"): 2,0 de fábrica (de 1,0 a 3,0); não
    há controle para ela na tela (o ScanTailor tem um, escondido no painel).

ONDE ENTRA NO PROGRAMA
    core.pipeline._preparar_metade_e_geometria, no fim do preparo da página
    (girar 90 -> dividir -> endireitar -> cortar -> DESENTORTAR), antes do
    filtro: é onde o ScanTailor faz (na saída, depois do corte). Assim a
    prévia, os cartões e o PDF veem a mesma página, e a marcação automática
    de gravura é feita na página já desentortada (por isso a assinatura dela
    ganha SUFIXO_DA_GRAVURA quando o desentortar está ligado).

O QUE É SEGURO MUDAR
    Os textos da tela (ROTULOS_NA_TELA, EXPLICACAO_NA_TELA, FRASE_DO_DESFAZER).

O QUE É ARRISCADO
    - FABRICA: tem de ser DESLIGADO. Com outro valor, todo livro (inclusive os
      já começados) muda de imagem.
    - aplicar() com o modo "desligado" tem de devolver a MESMA imagem, sem
      conta nenhuma (é a prova de que nada muda de fábrica).
    - Os códigos (DESLIGADO, AUTOMATICO, PELAS_MARGENS) ficam gravados no
      projeto.json: nunca trocar o texto deles; o texto da tela é outra coisa.
    - _CODIGO_DO_MODO: os números são os de output::DewarpingMode do
      ScanTailor (OFF 0, AUTO 1, MANUAL 2, MARGINAL 3).
"""

from __future__ import annotations

import ctypes
import logging
import threading
import time
from dataclasses import dataclass

import numpy as np

from core import st_ferramentas as st

_log = logging.getLogger(__name__)

# Códigos gravados no projeto (ConfigPagina.desentortar); nunca o texto da tela.
DESLIGADO = "desligado"
AUTOMATICO = "automatico"
PELAS_MARGENS = "pelas_margens"
MODOS = (DESLIGADO, AUTOMATICO, PELAS_MARGENS)

# O de fábrica do ScanTailor (DewarpingOptions(mode = OFF)) e o nosso.
FABRICA = DESLIGADO

# output::DewarpingMode do ScanTailor.
_CODIGO_DO_MODO = {AUTOMATICO: 1, PELAS_MARGENS: 3}

# A "Depth perception" do ScanTailor (DepthPerception.h: defaultValue 2,0,
# minValue 1,0, maxValue 3,0) e o "post deskew" (DewarpingOptions: ligado).
PROFUNDIDADE_DE_FABRICA = 2.0
PROFUNDIDADE_MINIMA = 1.0
PROFUNDIDADE_MAXIMA = 3.0
ENDIREITAR_DEPOIS_DE_FABRICA = True

# PageId::SubPage do ScanTailor: a metade da folha (modelos.METADE_*).
_LADO_DA_METADE = {"inteira": 0, "esquerda": 1, "direita": 2}

ROTULO_NA_TELA = "Desentortar perto da lombada"
ROTULOS_NA_TELA = {
    DESLIGADO: "Desligado",
    AUTOMATICO: "Automático (pelas linhas do texto)",
    PELAS_MARGENS: "Pelas margens de cima e de baixo",
}
EXPLICACAO_NA_TELA = (
    "Quando a folha sobe perto da lombada, as linhas saem curvas e as letras "
    "ficam espremidas ali. O programa segue as linhas do texto (ou as margens "
    "brancas de cima e de baixo) e redesenha a página reta, como o ScanTailor. "
    "Vem desligado; ligue só nas páginas curvas.")
FRASE_DO_DESFAZER = "Desentortar na página {pagina}: {estado}"

# Acrescentado à assinatura da marcação automática de gravura quando o
# desentortar está ligado (a página que o detector vê muda). Desligado: nada.
SUFIXO_DA_GRAVURA = "|desentortar="


@dataclass(frozen=True)
class Resultado(st.Resultado):
    """st.Resultado com o que o desentortar achou.

    achou_curvas: as curvas achadas não são as do modelo "sem curva" (False =
        o ScanTailor não achou linhas que bastem e só redesenhou a página).
    angulo_depois: o endireitar depois do desentortar, em graus (só no
        "pelas margens"; 0 se não endireitou).
    """

    achou_curvas: bool = False
    angulo_depois: float = 0.0


def modo_valido(modo) -> str:
    """O modo gravado, ou DESLIGADO se vier vazio ou estranho (nunca ligar por engano)."""
    return modo if modo in MODOS else DESLIGADO


def modo_da_pagina(pagina) -> str:
    """O modo desta página (ConfigPagina.desentortar). Objeto sem o campo
    (projeto de antes do item 2.12): desligado."""
    return modo_valido(getattr(pagina, "desentortar", DESLIGADO))


def ligado(pagina) -> bool:
    return modo_da_pagina(pagina) != DESLIGADO


def lado_da_pagina(pagina) -> int:
    """0 = página única, 1 = esquerda, 2 = direita (a metade da folha)."""
    return _LADO_DA_METADE.get(getattr(pagina, "metade", "inteira"), 0)


def desentortar(img: np.ndarray, dpi, modo: str, *, lado: int = 0,
                profundidade: float = PROFUNDIDADE_DE_FABRICA,
                endireitar_depois: bool = ENDIREITAR_DEPOIS_DE_FABRICA,
                conteudo: tuple[int, int, int, int] | None = None,
                biblioteca: st.BibliotecaScanTailor | None = None) -> Resultado:
    """O desentortar do ScanTailor numa página.

    img: uint8, cinza ou azul/verde/vermelho (a página já preparada).
    dpi: o DPI da imagem (número ou par). modo: AUTOMATICO ou PELAS_MARGENS.
    lado: 0 única, 1 esquerda, 2 direita. conteudo: (x, y, largura, altura) em
    pontos, ou None = a página inteira (o que o programa usa hoje).
    Devolve Resultado: .imagem do mesmo tamanho e canais, ou None com .motivo.
    Nunca levanta exceção; não muda a entrada.
    """
    biblioteca = biblioteca or st.padrao()
    try:
        if modo not in _CODIGO_DO_MODO:
            raise ValueError(f"modo do desentortar inválido: {modo!r}")
        if not isinstance(img, np.ndarray) or img.dtype != np.uint8 or img.ndim not in (2, 3):
            raise ValueError("a página tem de ser uint8, cinza ou com 3 canais")
        if img.ndim == 3 and img.shape[2] != 3:
            raise ValueError("a página colorida tem de ter 3 canais")
        if lado not in (0, 1, 2):
            raise ValueError(f"lado inválido: {lado!r}")
        profundidade = float(profundidade)
        if not PROFUNDIDADE_MINIMA <= profundidade <= PROFUNDIDADE_MAXIMA:
            raise ValueError(f"profundidade fora de 1 a 3: {profundidade}")
        cx, cy, cl, ca = (0, 0, 0, 0) if conteudo is None else (int(v) for v in conteudo)
        if cl < 0 or ca < 0:
            raise ValueError("caixa do conteúdo com tamanho negativo")
        dpi_x, dpi_y = st.dpi_inteiro(dpi)
    except (TypeError, ValueError) as erro:
        return Resultado(*_motivo("A página não pôde ser passada ao desentortar do ScanTailor.", str(erro)))
    altura, largura = img.shape[:2]
    recusa = st.motivo_de_recusa(largura, altura, dpi_x, dpi_y, "o desentortar do ScanTailor")
    if recusa is not None:
        return Resultado(*_motivo(recusa, f"página {largura}x{altura}, DPI {dpi_x}x{dpi_y}"))
    funcao = biblioteca.funcao("st_ferramentas_desentortar")
    if funcao is None:
        return Resultado(None, biblioteca.motivo_indisponivel, biblioteca.detalhe_indisponivel)

    entrada = np.ascontiguousarray(img)
    saida = np.empty_like(entrada)
    achou = ctypes.c_int(0)
    angulo = ctypes.c_double(0.0)
    erro = ctypes.create_string_buffer(512)
    canais = 1 if entrada.ndim == 2 else 3
    inicio = time.perf_counter()
    try:
        codigo = funcao(entrada.ctypes.data_as(ctypes.c_void_p), largura, altura,
                        int(entrada.strides[0]), canais, dpi_x, dpi_y,
                        _CODIGO_DO_MODO[modo], int(lado), profundidade, int(bool(endireitar_depois)),
                        cx, cy, cl, ca,
                        saida.ctypes.data_as(ctypes.c_void_p), int(saida.strides[0]),
                        ctypes.byref(achou), ctypes.byref(angulo), erro, len(erro))
    except Exception as falha:  # noqa: BLE001
        return Resultado(*_motivo("O desentortar do ScanTailor falhou nesta página.",
                                  f"{type(falha).__name__}: {falha}"))
    segundos = time.perf_counter() - inicio
    if codigo != st.OK:
        detalhe = f"código {codigo}: {erro.value.decode('utf-8', 'replace')}"
        if codigo == st.ERRO_MEMORIA:
            return Resultado(*_motivo("Faltou memória para desentortar esta página.", detalhe))
        return Resultado(*_motivo("O desentortar do ScanTailor falhou nesta página.", detalhe))
    return Resultado(saida, None, None, segundos, bool(achou.value), float(angulo.value))


def _motivo(motivo: str, detalhe: str | None) -> tuple:
    r = st.indisponivel(motivo, detalhe)
    return (r.imagem, r.motivo, r.detalhe_tecnico)


_AVISADOS: set[str] = set()
_TRANCA = threading.Lock()


def _avisar_uma_vez(motivo, detalhe) -> None:
    chave = f"{motivo}|{detalhe}"
    with _TRANCA:
        if chave in _AVISADOS:
            return
        _AVISADOS.add(chave)
    _log.warning("desentortar do ScanTailor indisponível, a página saiu sem ele: %s (%s)", motivo, detalhe)
    st.anotar_no_erros_log("desentortar do ScanTailor (item 2.12): a página saiu sem ele", motivo, detalhe)


def aplicar(img: np.ndarray, pagina, dpi=None, *,
            biblioteca: st.BibliotecaScanTailor | None = None) -> np.ndarray:
    """O passo do preparo (ver o topo). Com o desentortar desligado (o de
    fábrica) devolve a MESMA imagem, sem conta nenhuma. Ligado: a página
    desentortada, ou a mesma imagem se a DLL não rodou (anotado uma vez no
    erros.log). dpi None (a tela não sabe): o DPI pela altura da página, como
    nas cores (core.pontinhos_scantailor.dpi_pela_altura)."""
    modo = modo_da_pagina(pagina)
    if modo == DESLIGADO or img is None:
        return img
    try:
        dpi_ok = float(dpi) > 0
    except (TypeError, ValueError):
        dpi_ok = False
    if not dpi_ok:
        from core import pontinhos_scantailor

        dpi = pontinhos_scantailor.dpi_pela_altura(img.shape[0])
    resultado = desentortar(img, dpi, modo, lado=lado_da_pagina(pagina), biblioteca=biblioteca)
    if not resultado.disponivel:
        _avisar_uma_vez(resultado.motivo, resultado.detalhe_tecnico)
        return img
    return resultado.imagem
