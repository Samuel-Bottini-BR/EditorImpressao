"""Endireitar a página com o código do ScanTailor Advanced (item 2.2 da Fase 2).

O QUE FAZ
    Chama a função st_ferramentas_endireitar da DLL comum (core/st_ferramentas.py):
    o que o deskew::Task do ScanTailor Advanced v1.2.1 faz numa página nova -
    preto e branco Otsu, detecção "claro no escuro", LIMPEZA DAS SOMBRAS
    HORIZONTAIS COMPRIDAS (copiada sem mudança de src/core/filters/deskew/
    Task.cpp) e o SkewFinder (src/imageproc/SkewFinder.cpp, sem mudança), que
    só aceita o ângulo com confiança 2,0 ou mais. A cola está em
    terceiros/scantailor-advanced/ligacao-ferramentas/endireitar.cpp. Nada
    aqui reescreve a conta do ScanTailor: só leva a página até a DLL e põe o
    ângulo no sentido do programa.

    Decisões do Samuel (Registro de mudanças do plano, conferência 9 e 14):
      G4 (b), 05/10/2026: "endireitar do ScanTailor de fábrica; quando as duas
        contas discordarem mais de 0,3°, a página fica 'conferir' (C1 Sim),
        com a escolha da conta disponível." -> JEITO_SCANTAILOR é o de fábrica
        (modelos.Projeto.endireitar_como), a conta do programa continua
        (core/endireitar.py, JEITO_PROGRAMA), cada página pode trocar só nela
        (modelos.ConfigPagina.endireitar_como) e discordam() decide o
        "conferir" (LIMITE_DA_DISCORDANCIA).
      G6 (a), 05/10/2026: endireitar ANTES de cortar, como o ScanTailor.
        LIGADO em 09/10/2026 ("Pode começar", pergunta g6-endireitar-antes)
        só para o livro novo (core/ordem_do_preparo.py,
        Projeto.ordem_do_preparo); o projeto de antes continua cortar ->
        endireitar. Nas duas ordens a medida do ScanTailor é feita na página
        ANTES do corte (core/pipeline._angulo_automatico), como ele faz.

O SENTIDO DO ÂNGULO
    O ScanTailor devolve o ângulo que ele aplica (QTransform.rotate: positivo
    gira no sentido do relógio na tela). O programa usa o do OpenCV
    (core/endireitar.rotacionar: positivo gira no sentido contrário ao do
    relógio). Por isso medir() troca o sinal (SINAL_DO_SCANTAILOR = -1).
    Conferido por teste numa folha de mentira girada 2° para cada lado
    (tests/test_endireitar_scantailor.py), como no D3 de 05/10.

O DPI
    O DPI só muda a limpeza das sombras (tijolo de 200 x 14 pontos a 150 DPI).
    Nos PDFs que dizem 72 DPI (Livro de Horas, Graduale, Marial) usa-se a
    MESMA conta do limpar pontinhos e do detector de gravura
    (pontinhos_scantailor.dpi_para_os_pontinhos): os três do ScanTailor veem
    a página do mesmo tamanho. Quem chama passa o DPI do desenho e o do scan
    (core/pipeline.py).

SE A DLL FALTAR OU FALHAR
    Nada levanta exceção: o resultado volta com `disponivel` False e o motivo
    em português; quem chama decide (o programa cai na conta dele e escreve o
    motivo no erros.log uma vez).

O QUE É SEGURO MUDAR
    Os textos (NOMES_DOS_JEITOS). LIMITE_DA_DISCORDANCIA é decisão do Samuel
    (0,3°): mudar só com ele.

O QUE É ARRISCADO
    - SINAL_DO_SCANTAILOR: errado, a página sai duas vezes mais torta.
    - Os códigos JEITO_*: estão gravados nos projetos (nunca gravar o texto da
      tela).
"""

from __future__ import annotations

import ctypes
import logging
import threading
import time
from dataclasses import dataclass

import numpy as np

from core import st_ferramentas

_log = logging.getLogger(__name__)

# As contas que a pessoa escolhe (códigos internos, gravados no projeto; o
# texto da tela mora em NOMES_DOS_JEITOS). Nunca gravar o texto da tela.
JEITO_SCANTAILOR = "scantailor"
JEITO_PROGRAMA = "programa"
JEITOS = (JEITO_SCANTAILOR, JEITO_PROGRAMA)
# De fábrica (decisão G4 (b) do Samuel): a do ScanTailor.
PADRAO = JEITO_SCANTAILOR
# Projeto salvo antes do item 2.2 endireitava pela conta do programa: continua
# com ela, para sair idêntico ("o programa [...] vai ter que ser capaz de abrir
# arquivos de versões anteriores", Samuel, 05/10/2026).
JEITO_DO_PROJETO_ANTIGO = JEITO_PROGRAMA

# Textos da tela (provisórios até o layout; ver ui/tela_opcoes.py e
# ui/tela_conferir.py). Seguro mudar.
NOMES_DOS_JEITOS = {
    JEITO_SCANTAILOR: "a do ScanTailor",
    JEITO_PROGRAMA: "a do programa",
}

# Decisão do Samuel (G4 (b), C1): discordância MAIOR que isto manda a página
# para "Para revisar". Em graus.
LIMITE_DA_DISCORDANCIA = 0.3

# O ScanTailor gira no sentido do relógio para ângulo positivo; o programa
# (OpenCV), no sentido contrário. Ver "O SENTIDO DO ÂNGULO" no topo.
SINAL_DO_SCANTAILOR = -1.0

# Confiança mínima do ScanTailor (Skew::GOOD_CONFIDENCE, SkewFinder.cpp). Só
# para mostrar; quem decide é a DLL (devolve 0 abaixo disso).
CONFIANCA_BOA = 2.0


def jeito_valido(jeito) -> str:
    """O jeito gravado, ou o de fábrica se vier vazio ou estranho."""
    return jeito if jeito in JEITOS else PADRAO


def jeito_do_livro(projeto) -> str:
    """A conta do livro (Projeto.endireitar_como)."""
    return jeito_valido(getattr(projeto, "endireitar_como", PADRAO))


def jeito_da_pagina(projeto, pagina) -> str:
    """A conta que vale nesta página: a dela (ConfigPagina.endireitar_como),
    ou a do livro quando ela segue o livro (None)."""
    propria = getattr(pagina, "endireitar_como", None)
    if propria in JEITOS:
        return propria
    return jeito_do_livro(projeto)


def discordam(nosso: float | None, do_scantailor: float | None) -> bool:
    """As duas contas discordam mais que LIMITE_DA_DISCORDANCIA? (C1). Sem uma
    das duas (DLL indisponível), não há discordância a mostrar."""
    if nosso is None or do_scantailor is None:
        return False
    # 1e-6: 0,3° exatos (0,4 - 0,1 em ponto flutuante) não contam como "mais".
    return abs(float(nosso) - float(do_scantailor)) > LIMITE_DA_DISCORDANCIA + 1e-6


def dpi_para_o_endireitar(largura: int, altura: int, dpi: float | None,
                          dpi_do_scan: float | None = None) -> float | None:
    """O DPI que se diz ao ScanTailor para uma página de largura x altura
    pontos desenhada a `dpi`: a MESMA conta do limpar pontinhos (ver o topo,
    "O DPI"). None se `dpi` não é um número positivo (aí medir() supõe 10
    polegadas de altura, como o limpar pontinhos)."""
    from core.pontinhos_scantailor import dpi_para_os_pontinhos

    return dpi_para_os_pontinhos(largura, altura, dpi, dpi_do_scan)


@dataclass(frozen=True)
class Medida:
    """O que o ScanTailor achou numa página.

    angulo: o ângulo a aplicar, em graus, no sentido do PROGRAMA (OpenCV:
        positivo gira no sentido contrário ao do relógio); 0 quando a
        confiança ficou baixa. None se indisponível.
    angulo_bruto: o achado, mesmo com confiança baixa (no mesmo sentido).
    confianca: a do SkewFinder (2,0 ou mais = boa).
    preto_no_branco: False quando o ScanTailor viu a página "claro no
        escuro" e mediu invertida.
    dpi: o DPI que foi dito à DLL.
    """

    angulo: float | None
    angulo_bruto: float = 0.0
    confianca: float = 0.0
    preto_no_branco: bool = True
    dpi: float | None = None
    motivo: str | None = None
    detalhe_tecnico: str | None = None
    segundos: float = 0.0

    @property
    def disponivel(self) -> bool:
        return self.angulo is not None


def _indisponivel(motivo: str, detalhe: str | None = None) -> Medida:
    return Medida(None, motivo=motivo, detalhe_tecnico=detalhe)


def medir(img: np.ndarray, dpi=None,
          biblioteca: st_ferramentas.BibliotecaScanTailor | None = None) -> Medida:
    """O ângulo que o ScanTailor acharia nesta página.

    img: a página (cinza 2D, ou colorida BGR como o OpenCV/pdf_io devolve),
        ja girada de 90 em 90 e dividida, ANTES de cortar (como o ScanTailor:
        o endireitar vem antes da caixa do conteúdo).
    dpi: o DPI a dizer à DLL (número ou par; ver dpi_para_o_endireitar).
        None: supõe 10 polegadas de altura.
    Nunca levanta exceção (ver o topo)."""
    if img is None or img.ndim not in (2, 3) or (img.ndim == 3 and img.shape[2] not in (1, 3, 4)):
        return _indisponivel("A página não veio no formato esperado.",
                             None if img is None else f"forma {img.shape}")
    altura, largura = img.shape[:2]
    if dpi is None:
        from core.pontinhos_scantailor import dpi_pela_altura

        dpi = dpi_pela_altura(altura)
    try:
        dpi_x, dpi_y = st_ferramentas.dpi_inteiro(dpi)
    except (TypeError, ValueError) as erro:
        return _indisponivel("O DPI da página é inválido.", str(erro))
    recusa = st_ferramentas.motivo_de_recusa(largura, altura, dpi_x, dpi_y,
                                             "o endireitar do ScanTailor")
    if recusa:
        return _indisponivel(recusa)

    biblioteca = biblioteca or st_ferramentas.padrao()
    funcao = biblioteca.funcao("st_ferramentas_endireitar")
    if funcao is None:
        return _indisponivel(biblioteca.motivo_indisponivel or "O endireitar do ScanTailor não abriu.",
                             biblioteca.detalhe_indisponivel)

    if img.ndim == 3 and img.shape[2] == 1:
        img = img[:, :, 0]
    elif img.ndim == 3 and img.shape[2] == 4:
        img = img[:, :, :3]
    canais = 1 if img.ndim == 2 else 3
    pontos = np.ascontiguousarray(img, dtype=np.uint8)
    angulo = ctypes.c_double(0.0)
    bruto = ctypes.c_double(0.0)
    confianca = ctypes.c_double(0.0)
    preto_no_branco = ctypes.c_int(1)
    erro = ctypes.create_string_buffer(512)
    inicio = time.perf_counter()
    codigo = funcao(pontos.ctypes.data, largura, altura, int(pontos.strides[0]), canais,
                    dpi_x, dpi_y, ctypes.byref(angulo), ctypes.byref(bruto),
                    ctypes.byref(confianca), ctypes.byref(preto_no_branco), erro, len(erro))
    segundos = time.perf_counter() - inicio
    if codigo != st_ferramentas.OK:
        return _indisponivel("O endireitar do ScanTailor falhou nesta página.",
                             f"codigo {codigo}: {erro.value.decode('utf-8', 'replace')}")
    # + 0.0: o -0,0 vira 0,0 (o texto da tela não mostra "-0,0")
    return Medida(SINAL_DO_SCANTAILOR * float(angulo.value) + 0.0,
                  SINAL_DO_SCANTAILOR * float(bruto.value) + 0.0,
                  float(confianca.value), bool(preto_no_branco.value),
                  float(dpi_x), segundos=segundos)


def medir_na_pagina(base: np.ndarray, dpi_do_desenho=None, dpi_do_scan=None,
                    biblioteca: st_ferramentas.BibliotecaScanTailor | None = None) -> Medida:
    """O ângulo do ScanTailor numa página do programa (core/pipeline.
    _geometria): `base` é a página já girada de 90 em 90 e dividida, ANTES de
    cortar, desenhada a `dpi_do_desenho` (o DPI do desenho; None = não se
    sabe); dpi_do_scan é o que o PDF diz do escaneamento (None = não se sabe).

    O DPI dito à DLL é o da conta do limpar pontinhos (dpi_para_o_endireitar,
    ver "O DPI" no topo). Nunca levanta exceção (como medir).
    Arriscado: mudar a imagem que vai à DLL (o ângulo do ScanTailor muda com
    o tamanho da imagem; ver o relatório relatorios/conferir/
    endireitar-2026-10-07)."""
    if base is None or base.ndim < 2:
        return medir(base, None, biblioteca=biblioteca)
    altura, largura = base.shape[:2]
    dpi = dpi_para_o_endireitar(largura, altura, dpi_do_desenho, dpi_do_scan)
    return medir(base, dpi, biblioteca=biblioteca)


_AVISADOS: set[str] = set()
_TRANCA_DOS_AVISOS = threading.Lock()


def avisar_uma_vez(medida: Medida) -> None:
    """O motivo de ter caído na conta do programa vai para o erros.log uma vez
    por sessão (senão seria uma linha por página)."""
    chave = f"{medida.motivo}|{medida.detalhe_tecnico}"
    with _TRANCA_DOS_AVISOS:
        if chave in _AVISADOS:
            return
        _AVISADOS.add(chave)
    _log.warning("endireitar do ScanTailor indisponível, usei o do programa: %s (%s)",
                 medida.motivo, medida.detalhe_tecnico)
