"""Limpar pontinhos do ScanTailor Advanced, com o código original (item M4 da Fase 2, 06/10/2026).

O PEDIDO
    Samuel, 05/10/2026 (P7): trazer o limpar pontinhos do ScanTailor COMO OPÇÃO,
    com controle "pouco / normal / muito"; o nosso continua de fábrica, e ele
    quer ver os dois lado a lado antes de decidir. Por isso este módulo NÃO
    está ligado a nada do programa (nem filtro, nem projeto, nem tela).

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
    papel de verdade; aí o ScanTailor vê o pontinho maior e limpa menos.

O QUE É SEGURO MUDAR
    Os nomes das forças (são da tela, que ainda não existe).

O QUE É ARRISCADO
    - FORCAS: mudar o número muda o que o Samuel vai ver lado a lado.
    - O fallback de preto_e_branco_com_pontinhos_do_scantailor: sem a DLL ele
      devolve o Preto e branco de hoje, igual ponto a ponto (o teste confere).
"""

from __future__ import annotations

import ctypes
import time

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
    # o de fábrica: a mesma conta de filtro_preto_e_branco(despeckle=True)
    return F._despeckle(sem_limpar, sem_limpar.shape[0]), resultado
