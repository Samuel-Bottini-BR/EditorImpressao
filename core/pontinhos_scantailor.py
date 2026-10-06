"""Limpar pontinhos do ScanTailor Advanced, com o código original (item M4 da Fase 2, 06/10/2026).

O PEDIDO
    Samuel, 05/10/2026 (P7): trazer o limpar pontinhos do ScanTailor COMO OPÇÃO,
    com controle "pouco / normal / muito"; ele quis ver os dois lado a lado
    antes de decidir (rodada_pontinhos_scantailor.py).

    A DECISÃO (Samuel, 06/10/2026, P7): de fábrica, o do ScanTailor "pouco";
    as outras continuam como opção - desligado, o nosso, pouco, normal, muito.
    "Eu vou poder ligar e desligar esse apagador de pingos? e selecionar o
    pouco, normal ou muito, ou selecionar o nosso" - "o nosso muitas vezes
    acaba comendo muito as letras". A escolha mora no livro
    (Projeto.limpar_pontinhos) e na página (ConfigPagina.limpar_pontinhos,
    None = segue o livro) - ver "A ESCOLHA NO PROGRAMA", no fim deste arquivo.

O QUE FAZ
    limpar_pontinhos(binaria, dpi, forca): o Despeckle do ScanTailor
    (src/core/Despeckle.cpp, sem mudança, dentro de core/nativo/
    st_ferramentas.dll) sobre uma imagem em preto e branco do programa
    (0 = preto, 255 = branco). Diferente do nosso (core.filtros._despeckle,
    que só olha o TAMANHO da mancha), o do ScanTailor olha também a DISTÂNCIA
    até a letra: pontinho pequeno PERTO de uma letra fica (pingo do "i",
    acento, vírgula), pontinho solto no papel sai. Só tira preto, nunca põe.

    preto_e_branco_com_pontinhos_do_scantailor(img, dpi, ...): o Preto e branco
    de hoje (core.filtros.filtro_preto_e_branco, com TODAS as regras aprovadas)
    sem o nosso limpar pontinhos, e o do ScanTailor no lugar. É "o preto e
    branco das letras" do Preto e branco e do Misto. Sem a DLL, cai no nosso
    (o de fábrica) e diz por quê.

AS FORÇAS (FORCAS)
    "pouco" = 1,0 = "cauteloso" do ScanTailor (é o padrão DELE);
    "normal" = 2,0 = "normal"; "muito" = 3,0 = "agressivo".
    A v1.2.1 do ScanTailor trocou os três botões por um controle de 0,5 a 3,5;
    nos valores 1, 2 e 3 a conta dá exatamente os números dos três botões
    antigos (conferido em Despeckle.cpp, Settings::get). Também aceita um
    número de 0,5 a 3,5.

O DPI
    O ScanTailor mede o pontinho e a distância em pontos a 300 DPI e acompanha
    o DPI da imagem (a 600 DPI, o mesmo pontinho tem o dobro de lado). Passe o
    DPI em que a imagem foi desenhada (no programa, o projeto.qualidade_dpi
    reduzido por pdf_io.dpi_seguro). ATENÇÃO: nos PDFs que dizem 72 DPI sem
    ser (Horas, Graduale, Marial), o programa desenha a página maior do que o
    papel de verdade; aí o ScanTailor vê o pontinho maior e limpa menos. No
    programa, quem acerta isso é dpi_para_os_pontinhos (06/10/2026), do mesmo
    jeito que o detector de gravura do item 1.2.

O QUE É SEGURO MUDAR
    Os textos da tela (NOMES_NA_TELA, EXPLICACAO_NA_TELA).

O QUE É ARRISCADO
    - FORCAS: mudar o número muda o que o Samuel vai ver lado a lado.
    - O fallback de preto_e_branco_com_pontinhos_do_scantailor: sem a DLL ele
      devolve o Preto e branco de hoje, igual ponto a ponto (o teste confere).
"""

from __future__ import annotations

import ctypes
import logging
import threading
import time
from dataclasses import dataclass

import numpy as np

from core import st_ferramentas as st

FORCAS = {"pouco": 1.0, "normal": 2.0, "muito": 3.0}
FORCA_MINIMA, FORCA_MAXIMA = 0.5, 3.5   # o controle do ScanTailor v1.2.1


def forca_em_numero(forca: str | float) -> float:
    """"pouco" / "normal" / "muito", ou um número de 0,5 a 3,5. ValueError se não for."""
    if isinstance(forca, str):
        if forca not in FORCAS:
            raise ValueError(f"força desconhecida: {forca!r} (use {', '.join(FORCAS)})")
        return FORCAS[forca]
    valor = float(forca)
    if not FORCA_MINIMA <= valor <= FORCA_MAXIMA:
        raise ValueError(f"força fora de {FORCA_MINIMA} a {FORCA_MAXIMA}: {forca!r}")
    return valor


def limpar_pontinhos(binaria: np.ndarray, dpi, forca: str | float = "normal", *,
                     biblioteca: st.BibliotecaScanTailor | None = None) -> st.Resultado:
    """O limpar pontinhos do ScanTailor numa imagem em preto e branco.

    binaria: uint8, 2 dimensões; menor que 128 = preto (tinta), o resto = branco.
    dpi: o DPI da imagem (um número, ou horizontal e vertical).
    forca: "pouco", "normal", "muito", ou um número de 0,5 a 3,5.
    Devolve st.Resultado: .imagem uint8 só com 0 e 255 (None se indisponível,
    com .motivo em português). Nunca levanta exceção; não muda `binaria`.
    """
    biblioteca = biblioteca or st.padrao()
    try:
        if not isinstance(binaria, np.ndarray) or binaria.dtype != np.uint8 or binaria.ndim != 2:
            raise ValueError("a imagem tem de ser preto e branco (uint8, um canal só)")
        numero = forca_em_numero(forca)
        dpi_x, dpi_y = st.dpi_inteiro(dpi)
    except (TypeError, ValueError) as erro:
        return st.indisponivel("A página não pôde ser passada ao limpar pontinhos do ScanTailor.",
                               str(erro))
    altura, largura = binaria.shape
    recusa = st.motivo_de_recusa(largura, altura, dpi_x, dpi_y, "o limpar pontinhos do ScanTailor")
    if recusa is not None:
        return st.indisponivel(recusa, f"página {largura}x{altura}, DPI {dpi_x}x{dpi_y}")

    funcao = biblioteca.funcao("st_ferramentas_pontinhos")
    if funcao is None:
        return st.Resultado(None, biblioteca.motivo_indisponivel, biblioteca.detalhe_indisponivel)

    entrada = np.ascontiguousarray(binaria)
    saida = np.empty((altura, largura), np.uint8)
    erro = ctypes.create_string_buffer(512)
    inicio = time.perf_counter()
    try:
        codigo = funcao(entrada.ctypes.data_as(ctypes.c_void_p), largura, altura, entrada.strides[0],
                        dpi_x, dpi_y, ctypes.c_double(numero),
                        saida.ctypes.data_as(ctypes.c_void_p), saida.strides[0], erro, len(erro))
    except Exception as falha:  # noqa: BLE001
        return st.indisponivel("O limpar pontinhos do ScanTailor falhou nesta página.",
                               f"{type(falha).__name__}: {falha}")
    segundos = time.perf_counter() - inicio
    if codigo != st.OK:
        detalhe = f"código {codigo}: {erro.value.decode('utf-8', 'replace')}"
        if codigo == st.ERRO_MEMORIA:
            return st.indisponivel("Faltou memória para limpar os pontinhos desta página.", detalhe)
        return st.indisponivel("O limpar pontinhos do ScanTailor falhou nesta página.", detalhe)
    return st.Resultado(saida, None, None, segundos)


def preto_e_branco_com_pontinhos_do_scantailor(
        img: np.ndarray, dpi, forca: str | float = "normal", forca_preto: int | None = None,
        algoritmo: str = "auto", *, biblioteca: st.BibliotecaScanTailor | None = None,
) -> tuple[np.ndarray, st.Resultado]:
    """O Preto e branco de hoje, com o limpar pontinhos do ScanTailor no lugar do nosso.

    img, forca_preto, algoritmo: os de core.filtros.filtro_preto_e_branco
    (forca_preto None = o meio, AJUSTE_PADRAO). dpi e forca: os de
    limpar_pontinhos. Devolve (binaria, resultado): a imagem de 1 canal, só 0 e
    255; `resultado` diz se o do ScanTailor rodou. Se não rodou (sem a DLL,
    página recusada), a imagem é o Preto e branco de hoje com o NOSSO limpar
    pontinhos (o de fábrica), igual ponto a ponto, e resultado.motivo diz por quê.
    """
    from core import filtros as F

    if forca_preto is None:
        forca_preto = F.AJUSTE_PADRAO
    sem_limpar = F.filtro_preto_e_branco(img, forca=forca_preto, despeckle=False, algoritmo=algoritmo)
    resultado = limpar_pontinhos(sem_limpar, dpi, forca, biblioteca=biblioteca)
    if resultado.disponivel:
        return resultado.imagem, resultado
    # o nosso: a mesma conta de filtro_preto_e_branco(despeckle=True)
    return F._despeckle(sem_limpar, sem_limpar.shape[0]), resultado


# =============================================================================
# A ESCOLHA NO PROGRAMA: "Limpar pontinhos" (decisão do Samuel, 06/10/2026, P7)
#
# Cinco valores, por livro (Projeto.limpar_pontinhos) e por página
# (ConfigPagina.limpar_pontinhos; None = segue o livro), valendo no Preto e
# branco e no "Só as letras" (core.pipeline._filtrar):
#   DESLIGADO  nenhum limpar pontinhos;
#   NOSSO      o de antes (core.filtros._despeckle: tira toda mancha pequena,
#              pelo tamanho; "muitas vezes acaba comendo muito as letras");
#   POUCO, NORMAL, MUITO  o do ScanTailor (limpar_pontinhos, acima), nas
#              três forças dele. POUCO é o de fábrica (livro novo).
# Projeto salvo antes desta escolha abre como estava: a caixinha antiga
# "limpar poeirinha" (ConfigPagina.despeckle) ligada vira NOSSO, desligada
# vira DESLIGADO (modelos.Projeto.de_dicionario). Assim um livro já
# conferido não muda sem o Samuel saber.
#
# Seguro mudar: ROTULO_NA_TELA, NOMES_NA_TELA e EXPLICACAO_NA_TELA (textos).
# Arriscado: os valores das constantes (vão para o projeto.json; mudar um
# quebra os livros salvos com ele - escolha_valida faria o livro cair no de
# fábrica) e PADRAO (é a decisão do Samuel).
# =============================================================================

DESLIGADO = "desligado"
NOSSO = "nosso"
POUCO, NORMAL, MUITO = "pouco", "normal", "muito"
ESCOLHAS = (DESLIGADO, NOSSO, POUCO, NORMAL, MUITO)   # a ordem da tela
DO_SCANTAILOR = (POUCO, NORMAL, MUITO)
PADRAO = POUCO                    # livro novo (decisão do Samuel, 06/10)
DO_PROJETO_ANTIGO = NOSSO         # livro salvo antes da escolha existir

# Os textos da tela (provisórios até o layout; regra do Samuel de 06/10: o
# controle entra com aparência provisória e vai para a lista do agente de
# layout).
ROTULO_NA_TELA = "Limpar pontinhos:"
NOMES_NA_TELA = {DESLIGADO: "desligado", NOSSO: "o nosso", POUCO: "pouco",
                 NORMAL: "normal", MUITO: "muito"}
EXPLICACAO_NA_TELA = (
    "Tira os pontinhos pretos soltos no papel (poeira, sujeira do scanner).\n"
    "pouco, normal e muito: tiram o pontinho solto e deixam o que está perto "
    "da letra (pingo do i, acento, vírgula); \"muito\" tira mais.\n"
    "o nosso: o jeito de antes, que tira toda mancha pequena e às vezes come "
    "pedaço de letra.\n"
    "desligado: não tira nada.")


def escolha_valida(valor, padrao: str = PADRAO) -> str:
    """`valor` se for uma das ESCOLHAS; senão `padrao` (valor estranho vindo
    do arquivo, ou de uma versão futura, não derruba nada)."""
    return valor if valor in ESCOLHAS else padrao


def escolha_da_pagina(projeto, pagina) -> str:
    """O que vale nesta página: a escolha dela (ConfigPagina.limpar_pontinhos)
    ou, se ela segue o livro (None ou valor estranho), a do livro
    (Projeto.limpar_pontinhos). Objeto sem os campos (projeto em memória de
    antes desta escolha): o de fábrica."""
    propria = getattr(pagina, "limpar_pontinhos", None)
    if propria in ESCOLHAS:
        return propria
    return escolha_valida(getattr(projeto, "limpar_pontinhos", PADRAO))


# --- o DPI de verdade (passo 1 da ligação, 06/10/2026) ------------------------
#
# Nos PDFs que dizem 72 DPI (Livro de Horas, Graduale, Marial) o tamanho da
# página no PDF não é o do papel: a folha vira 24 x 33 cm a 36 x 51 cm, e a
# página desenhada "a 300 DPI" tem, na verdade, uns 380 a 520 pontos por polegada
# de papel. Com o DPI do PDF, o ScanTailor acha que o pontinho é maior do que
# é e limpa menos. O detector de gravura do item 1.2 já resolve isso
# (core.detectar_regioes._dpi_declarado_a_dll): se a página, levada a 300
# DPI, passaria de PONTOS_MAXIMOS_DA_GRAVURA (7 milhões de pontos, uma página
# de uns 19 x 26 cm), diz-se o DPI que a faz caber - o mesmo que supor que o
# papel tem no máximo esse tamanho. Usamos a MESMA conta, para os dois do
# ScanTailor verem a página do mesmo tamanho.
#
# Diferença de propósito: não vale quando o PDF diz DPI_CONFIAVEL ou mais.
# Num PDF que diz 300 ou 400 DPI, o número é o do scanner, e uma página
# grande de verdade (um fólio bem escaneado) não pode ganhar DPI a mais - o
# ScanTailor passaria a tirar manchas maiores. Abaixo disso o número é do
# programa que montou o PDF: o Horas e o Marial dizem 72; o Graduale diz 112
# na largura e 93 na altura (a imagem esticada na página), e o detector de
# gravura também o trata como "72 DPI". No acervo de hoje o resultado é o
# mesmo da conta da gravura sem esta trava (só esses três livros passam do
# teto). Por que 140: o Boécio diz 150 (149,9 a 150,3) e a Escola 200 (199,9
# a 200,1) e são de verdade; um número redondo como 150 ou 200 cairia em
# cima deles. Seguro mudar: o número, sabendo que a página grande de um PDF
# que diga menos que ele passa a ser tratada como menor.
DPI_CONFIAVEL = 140
# Sem DPI nenhum (quem chama não sabe): a mesma suposição do nosso limpar
# pontinhos (core.filtros._despeckle: 3000 pontos de altura = 300 DPI, uma
# página de 10 polegadas).
POLEGADAS_DA_ALTURA_SUPOSTA = 10.0


def dpi_para_os_pontinhos(largura: int, altura: int, dpi: float | None,
                          dpi_do_scan: float | None = None) -> float | None:
    """O DPI de verdade de uma página de largura x altura pontos desenhada a
    `dpi` (o do desenho: core.pipeline._dpi_do_desenho), para o limpar
    pontinhos do ScanTailor. dpi_do_scan: o DPI que o PDF diz do
    escaneamento (core.pipeline._dpi_do_scan), ou None se não se sabe.
    None se `dpi` não é um número positivo (aí limpar_conforme_a_escolha
    estima pela altura). Ver o comentário acima. Arriscado: trocar a conta da
    gravura por outra (os dois do ScanTailor deixariam de ver a mesma
    página)."""
    try:
        dpi = float(dpi)
    except (TypeError, ValueError):
        return None
    if not dpi > 0:
        return None
    if dpi_do_scan is not None and float(dpi_do_scan) >= DPI_CONFIAVEL:
        return dpi
    from core.detectar_regioes import _dpi_declarado_a_dll

    return float(_dpi_declarado_a_dll(int(largura), int(altura), dpi))


def dpi_pela_altura(altura: int) -> float:
    """O DPI suposto quando ninguém sabe (POLEGADAS_DA_ALTURA_SUPOSTA),
    dentro da faixa que a DLL aceita."""
    return max(float(st.DPI_MINIMO), min(float(st.DPI_MAXIMO),
                                         altura / POLEGADAS_DA_ALTURA_SUPOSTA))


@dataclass(frozen=True)
class Pontinhos:
    """A escolha de uma página já pronta para o filtro: o que fazer
    (`escolha`, uma das ESCOLHAS) e o DPI de verdade da imagem (`dpi`, de
    dpi_para_os_pontinhos; None = estimar pela altura). É o que
    core.pipeline passa no argumento `despeckle` dos filtros
    (core.filtros.filtro_preto_e_branco), que continua aceitando True (o
    nosso) e False (nada), como antes, para os scripts e testes antigos."""

    escolha: str
    dpi: float | None = None


_AVISADOS: set[str] = set()
_TRANCA_DOS_AVISOS = threading.Lock()
_log = logging.getLogger(__name__)


def _avisar_uma_vez(motivo: str | None, detalhe: str | None) -> None:
    """O motivo de ter caído no nosso vai para o erros.log uma vez por sessão
    (senão seria uma linha por página)."""
    chave = f"{motivo}|{detalhe}"
    with _TRANCA_DOS_AVISOS:
        if chave in _AVISADOS:
            return
        _AVISADOS.add(chave)
    _log.warning("limpar pontinhos do ScanTailor indisponível, usei o nosso: %s (%s)",
                 motivo, detalhe)


def limpar_conforme_a_escolha(binaria: np.ndarray, escolha, *,
                              biblioteca: st.BibliotecaScanTailor | None = None) -> np.ndarray:
    """Aplica a escolha "Limpar pontinhos" numa imagem em preto e branco
    (0 = preto, 255 = branco). `escolha`: um Pontinhos, ou só o texto (uma
    das ESCOLHAS; o DPI sai pela altura). Valor estranho vale o de fábrica.

    Se o do ScanTailor não puder rodar (DLL ausente, página recusada), usa o
    NOSSO (o de antes) e anota o motivo uma vez no log: a página nunca sai
    sem limpar só porque a DLL faltou. Nunca levanta exceção por causa da DLL.
    Arriscado: trocar esse recuo por "não limpar" (a página sairia com a
    poeira toda, sem aviso).
    """
    from core import filtros as F

    if isinstance(escolha, Pontinhos):
        nome, dpi = escolha_valida(escolha.escolha), escolha.dpi
    else:
        nome, dpi = escolha_valida(escolha), None
    if nome == DESLIGADO:
        return binaria
    if nome == NOSSO:
        return F._despeckle(binaria, binaria.shape[0])
    if not dpi or dpi <= 0:
        dpi = dpi_pela_altura(binaria.shape[0])
    resultado = limpar_pontinhos(binaria, dpi, nome, biblioteca=biblioteca)
    if resultado.disponivel:
        return resultado.imagem
    _avisar_uma_vez(resultado.motivo, resultado.detalhe_tecnico)
    return F._despeckle(binaria, binaria.shape[0])
