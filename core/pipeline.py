"""Orquestra tudo, sempre uma página por vez.

Ordem obrigatoria do processamento (depende do livro desde 09/10/2026, item
2.2, G6 - core/ordem_do_preparo.py, Projeto.ordem_do_preparo):
    livro novo ("endireitar_antes", como o ScanTailor):
        1. dividir folhas -> 2. endireitar a pagina inteira -> 3. achar o
        corte na pagina reta e cortar -> 4. filtro -> 5. montar cadernos
    projeto gravado antes do G6 ("cortar_antes", identico ao de antes):
        1. dividir folhas -> 2. cortar bordas -> 3. endireitar -> 4. filtro
        -> 5. montar cadernos
O giro de 90 em 90 vem antes de tudo, nas duas.

As páginas apagadas somem logo depois da etapa 1.

Item 1.1 (tirar o fundo de PDF com camadas, core/camadas.py): é o filtro
"Tirar o fundo" (core.filtros.TIRAR_FUNDO), que só aparece em PDF com
camadas. Ele trabalha na PÁGINA DO PDF (as camadas são da folha inteira),
então roda ANTES da etapa 1, no lugar do desenho da folha, e as etapas 1 a 3
seguem por cima do resultado, com o corte e o ângulo medidos na folha como
ela veio (os mesmos de sempre, guardados para a prévia = PDF). A etapa 4 é
pulada: nenhum outro filtro vai por cima. Página que core/camadas.py deixa
intacta sai como veio (igual ao Original). Ver usa_tirar_fundo e
_sem_fundo_da_folha.

Sobre memória: nenhuma funcao daqui monta uma lista de páginas processadas. Ler
-> processar -> escrever -> soltar. Foi o que travou a versão anterior com
livros de 500 páginas a 400 DPI.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import math
import os
import shutil
import tempfile
import threading
from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path

import cv2
import numpy as np

from core import analise
from core.cadernos import impor_pdf
from core.dividir import Lombada, detectar_lombada, dividir_imagem
from core.endireitar import (ANGULO_MINIMO, Inclinacao, detectar_angulo, girar_90, rotacionar,
                             rotacionar_e_cortar)
from core import dividir_scantailor, endireitar_scantailor, linhas_do_texto, misto, pontinhos_scantailor
from core import revisar
from core import claro_no_escuro, cores_scantailor, desentortar_scantailor
from core import corte_pelo_conteudo   # item 2.5 (so com Projeto.cortar_pelo_conteudo)
from core import borda_preta           # item 2.13 (so com Projeto.borda_preta)
from core import recortar              # etapa 10a: _caixa_sem_comer usa as contas do corte comum
from core import etapas                # obra 26/10 etapa 1: "esta etapa vale nesta pagina?" (D-009)
from core.ordem_do_preparo import endireita_antes, ordem_do_livro
from core.filtros import (ORIGINAL, PRETO_E_BRANCO, TIRAR_FUNDO, aplicar_filtro,
                          aplicar_filtro_com_selecao, aplicar_so_os_pedacos)
from core.folha import compor_na_folha
from core import editar_zonas, luz_scantailor, margens_scantailor, nucleos
from core.pdf_io import (
    DPI_PREVIA,
    dpi_real_da_pagina,
    EscritorPDF,
    ErroPDF,
    abrir_pdf,
    info_paginas,
    pagina_para_array,
    tamanho_da_pagina_pt,
)
from core.recortar import (Recorte, alargar_para_o_giro, aplicar_recorte, caixa_em_pontos,
                           detectar_bordas, fatiar)
from modelos import (
    METADE_DIREITA,
    METADE_ESQUERDA,
    METADE_INTEIRA,
    ConfigFolha,
    ConfigPagina,
    Projeto,
)

# DPI usado na fase de analise. Nao precisa de mais: lombada, angulo e cor
# aparecem de sobra a 150 DPI, e assim a analise de um livro inteiro leva
# segundos em vez de minutos.
DPI_ANALISE = 150

_log = logging.getLogger(__name__)

Progresso = Callable[[int, int, str], None] | None
Cancelado = Callable[[], bool] | None


class Cancelou(Exception):
    """O usuario apertou cancelar. Não é erro."""


def _checar(cancelado: Cancelado) -> None:
    if cancelado is not None and cancelado():
        raise Cancelou()


def _avisar(progresso: Progresso, feito: int, total: int, texto: str) -> None:
    if progresso is not None:
        progresso(feito, total, texto)


# ---------------------------------------------------------------------------
# Fase 1: analisar o livro e propor tudo
# ---------------------------------------------------------------------------

def analisar_projeto(
    projeto: Projeto, progresso: Progresso = None, cancelado: Cancelado = None
) -> Projeto:
    """Le o livro inteiro em baixa resolução e preenche folhas e páginas.

    E o que a tela 2 dispara antes de abrir a tela de conferir.
    """
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        infos = info_paginas(doc)
        total = len(infos)

        # Item 1.1: o PDF vem com camadas? Só a estrutura (lista de imagens e
        # conteúdo de até 12 páginas), sem desenhar nada: milissegundos. Feito
        # aqui também (além de ui/janela_principal.abrir_livro) para quem
        # chega sem passar pela tela - a conferencia.py e o teste de velocidade.
        # É o que faz o filtro "Tirar o fundo" aparecer na tela.
        from core.camadas import pdf_tem_camadas

        projeto.tem_camadas = pdf_tem_camadas(doc)
        tamanhos = [(i.largura_pt, i.altura_pt) for i in infos]
        fora_do_padrao = analise.tamanhos_fora_do_padrao(tamanhos)

        folhas: list[ConfigFolha] = []
        paginas: list[ConfigPagina] = []
        # Item 2.2, C1: as paginas em que as duas contas do endireitar
        # discordam (so no livro pela conta do ScanTailor). O aviso entra
        # DEPOIS das observacoes: e por pagina, nunca vira caracteristica do
        # livro (a previa o poria de volta em cada pagina).
        discordam: list[ConfigPagina] = []
        # Item 2.15: o angulo automatico de cada pagina, para destacar as
        # que se afastam das outras (core/paginas_diferentes.py).
        angulos_das_paginas: list[float | None] = []
        medir_as_duas = (projeto.endireitar and endireitar_scantailor.jeito_do_livro(projeto)
                         == endireitar_scantailor.JEITO_SCANTAILOR)

        # Item 2.16: as folhas sao analisadas por varios trabalhadores ao mesmo
        # tempo (core/nucleos.py; uma folha por trabalhador) e juntadas aqui
        # NA ORDEM. Com 1 trabalhador, e o laco de sempre.
        def analisar(indice: int):
            return _analisar_a_folha(projeto, doc, indice, fora_do_padrao[indice], medir_as_duas)

        trabalhadores = nucleos.quantos_trabalhadores()
        _avisar(progresso, 0, total, f"Analisando a folha 1 de {total}")
        for indice, (folha, partes) in nucleos.em_ordem(range(total), analisar, trabalhadores,
                                                        cancelado):
            _checar(cancelado)
            folhas.append(folha)
            for pagina, discorda, angulo_da_analise in partes:
                pagina.indice = len(paginas)
                paginas.append(pagina)
                if discorda:
                    discordam.append(pagina)
                # item 2.15: o angulo que valeu nesta pagina (juncao de
                # 23/10/2026: medido por _analisar_a_folha, no trabalhador)
                angulos_das_paginas.append(angulo_da_analise)
            if indice + 1 < total:
                _avisar(progresso, indice + 1, total, f"Analisando a folha {indice + 2} de {total}")
        _checar(cancelado)

        # Um alerta que vale para quase todas as páginas não e exceção, e sim
        # caracteristica do livro: sai das páginas e vira observação.
        #
        # Folhas e páginas sao contadas SEPARADAS. Juntar as duas listas fazia
        # cada código chegar no máximo a 50% - um alerta de folha nunca aparece
        # numa página - e nada passava do limiar: a separação nunca acontecia.
        observacoes: list[str] = []
        for itens in (folhas, paginas):
            achadas, remover = analise.separar_observacoes([i.alertas for i in itens])
            observacoes.extend(achadas)
            if remover:
                for item in itens:
                    item.alertas = [a for a in item.alertas if a not in remover]

        for pagina in discordam:
            _anotar_contas_discordam(pagina, True)
        marcar_paginas_diferentes(paginas, angulos_das_paginas)

        projeto.observacoes = observacoes
        projeto.folhas = folhas
        projeto.paginas = paginas
        # Modo Misto (bug Misto 1, 05/10/2026): com "So as letras" ligada no
        # livro, o "Tem cor" nao vale (a ilustracao sai em cor). Depois das
        # observacoes de proposito: o "livro inteiro e colorido" continua
        # sendo contado como antes.
        acertar_alertas_de_cor(projeto)
        _avisar(progresso, total, total, "Pronto")
        return projeto
    finally:
        doc.close()


def _analisar_a_folha(projeto: Projeto, doc, indice: int, fora_do_padrao: bool,
                      medir_as_duas: bool
                      ) -> tuple[ConfigFolha, list[tuple[ConfigPagina, bool, float | None]]]:
    """Uma folha da analise: a ConfigFolha e as paginas dela (com a pagina,
    se as duas contas do endireitar discordam e, item 2.15, o angulo
    automatico que valeu - juncao de 23/10/2026). O indice da pagina no livro e
    posto por quem junta (analisar_projeto), na ordem. E o corpo do laco de
    sempre, separado em 22/10/2026 (item 2.16) para varias folhas serem
    analisadas ao mesmo tempo; a conta e a mesma, linha por linha."""
    img = pagina_para_array(doc, indice, dpi=DPI_ANALISE)

    # Item 2.1: dividir so com o livro marcado (G2 (a)), pelo jeito
    # escolhido; o corte da sobra so na folha que nao vai ser dividida
    # (G3 (b), desligado de fabrica).
    lombada = (achar_divisao(img, projeto.dividir_como, DPI_ANALISE)
               if projeto.dividir_folhas else Lombada(0.5, 0.0, False))
    vai_dividir_esta = projeto.dividir_folhas and lombada.e_paisagem
    inclinacao = detectar_angulo(img) if projeto.endireitar else Inclinacao(0.0, 0.0)
    sobra = (achar_sobra(img, DPI_ANALISE)
             if getattr(projeto, "cortar_sobra", False) and not vai_dividir_esta
             else None)
    # obra 26/10, etapa 10a: o corte da sobra deixa a folga que o endireitar
    # vai precisar (Cursus 3: as primeiras letras das linhas de baixo sumiam)
    sobra = folga_do_giro_na_sobra(sobra, img.shape, inclinacao.angulo, DPI_ANALISE)
    recorte = (detectar_bordas(img, dpi=DPI_ANALISE) if projeto.cortar_bordas
               else Recorte.inteiro())

    # DPI de verdade, tirado da imagem embutida no PDF. Medir na imagem
    # que acabamos de rasterizar devolveria sempre DPI_ANALISE.
    dpi_real = dpi_real_da_pagina(doc, indice)

    folha = ConfigFolha(
        indice=indice,
        dividir=vai_dividir_esta,
        posicao_corte=lombada.posicao,
        confianca_corte=lombada.confianca,
        angulo_detectado=inclinacao.angulo,
        confianca_angulo=inclinacao.confianca,
        e_paisagem=lombada.e_paisagem,
        sobra=sobra,
    )
    folha.alertas = analise.analisar_folha(
        img, lombada, inclinacao, recorte,
        vai_dividir=projeto.dividir_folhas,
        vai_endireitar=projeto.endireitar,
        vai_cortar=projeto.cortar_bordas,
        dpi_real=dpi_real,
        tamanho_fora_do_padrao=fora_do_padrao,
    )

    # A analise de cor e feita ja na metade certa: uma capa colorida na
    # direita nao deve pintar a pagina da esquerda de alerta.
    partes: list[tuple[ConfigPagina, bool, float | None]] = []
    for metade, pedaco in _partes_da_folha(img, folha):
        pagina = ConfigPagina(
            indice=-1,                 # quem junta poe o lugar dela no livro
            folha=indice,
            metade=metade,
            filtro=projeto.filtro_padrao,
        )
        alertas, tem_cor = analise.analisar_pagina(pedaco, projeto.filtro_padrao)
        pagina.alertas = alertas
        pagina.tem_cor = tem_cor
        discorda = False
        angulo_da_analise = folha.angulo_detectado if projeto.endireitar else None
        if medir_as_duas:
            medidas: dict = {}
            _geometria(pedaco, pagina, projeto, dpi=DPI_ANALISE, dpi_do_scan=dpi_real,
                       medidas=medidas, com_o_corte=False)
            discorda = bool(medidas.get("discordam"))
            angulo_da_analise = _angulo_que_valeu(medidas, angulo_da_analise)
        partes.append((pagina, discorda, angulo_da_analise))
    del img
    return folha, partes


# ---------------------------------------------------------------------------
# Item 2.1: dividir pelo jeito escolhido, e o corte da sobra do ScanTailor
# ---------------------------------------------------------------------------

def jeito_de_dividir(projeto: Projeto, folha: ConfigFolha) -> str:
    """O jeito que vale nesta folha: o dela (ConfigFolha.dividir_como) ou o
    do livro (Projeto.dividir_como). Codigos de core/dividir_scantailor."""
    return dividir_scantailor.jeito_valido(
        folha.dividir_como or getattr(projeto, "dividir_como", None))


def achar_divisao(img: np.ndarray, jeito: str, dpi: float,
                  forcar: bool = False) -> Lombada:
    """Onde dividir a folha `img` (ja girada como vai ser usada), pelo jeito
    pedido. Devolve uma core.dividir.Lombada: `e_paisagem` diz se a folha
    deve ser dividida, `posicao` onde.

    "programa": core.dividir.detectar_lombada (como sempre: folha deitada,
        mais larga que 1,2 x a altura, dividida na lombada).
    "scantailor": o automatico do ScanTailor (core/dividir_scantailor.py):
        folha mais larga que alta = duas paginas, no lugar que ele acha. A
        confianca fica 1,0 (o ScanTailor nao da uma); o alerta "conferir"
        sai quando a divisao fica longe do meio (analise.LOMBADA_INCERTA,
        core.dividir.FAIXA_CONFIAVEL). Sem a DLL, cai no jeito do programa
        (o motivo vai para o log).
    forcar=True (a pessoa mandou dividir ESTA folha): o ScanTailor divide
        mesmo a folha em pe (modo "duas paginas"); o do programa procura a
        lombada perto do meio como se a folha fosse deitada.

    Arriscado: o dpi tem de ser o da imagem (o ScanTailor mede em pontos a
    300 e a 150 DPI)."""
    if dividir_scantailor.jeito_valido(jeito) == dividir_scantailor.JEITO_SCANTAILOR:
        modo = (dividir_scantailor.MODO_DUAS_PAGINAS if forcar
                else dividir_scantailor.MODO_AUTOMATICO)
        resultado = dividir_scantailor.achar(img, dpi, modo)
        if resultado.disponivel:
            posicao = dividir_scantailor.posicao_da_divisao(resultado)
            if posicao is None:
                return Lombada(0.5, 0.0, False)
            return Lombada(float(posicao), 1.0, True)
        _log.warning("dividir do ScanTailor indisponivel, usando o do programa: %s (%s)",
                     resultado.motivo, resultado.detalhe_tecnico)
    lombada = detectar_lombada(img)
    if forcar and not lombada.e_paisagem:
        # folha em pe que a pessoa mandou dividir: a mesma busca, numa copia
        # esticada para parecer deitada (so a posicao, em fracao, interessa)
        altura, largura = img.shape[:2]
        esticada = cv2.resize(img, (max(largura, int(altura * 1.5)), altura),
                              interpolation=cv2.INTER_AREA)
        achada = detectar_lombada(esticada)
        lombada = Lombada(achada.posicao, achada.confianca, True)
    return lombada


def achar_sobra(img: np.ndarray, dpi: float) -> tuple[float, float] | None:
    """O corte da sobra do ScanTailor na folha `img`: (esquerda, direita) em
    fracao da largura, ou None (nada a cortar, ou a DLL indisponivel - ai a
    folha sai sem esse corte, como antes).

    Pelo AUTOMATICO do ScanTailor (o que ele faz sozinho num projeto novo, e o
    que o Samuel viu no D3 antes de decidir G3 (b)): so ha sobra quando ele
    acha que a folha e UMA pagina com a beirada da vizinha ("uma pagina +
    sobra"). Escolhido em vez do modo "uma pagina + sobra" FORCADO porque, no
    teste de 06/10 (relatorios/conferir/dividir-2026-10-06), o forcado, numa
    folha de livro aberto, tomou a dobra do meio por beirada e cortou fora
    uma pagina inteira, e na tabela do Opus Majus 256 cortou colunas. Custo:
    folha deitada de uma pagina so (Siebmacher) nao ganha corte da sobra (o
    automatico a toma por duas paginas). Arriscado: trocar o modo sem refazer
    esse teste."""
    resultado = dividir_scantailor.achar(img, dpi, dividir_scantailor.MODO_AUTOMATICO)
    if not resultado.disponivel:
        _log.warning("corte da sobra do ScanTailor indisponivel: %s (%s)",
                     resultado.motivo, resultado.detalhe_tecnico)
        return None
    return dividir_scantailor.sobra_da_folha(resultado)


# Obra de 26/10/2026, etapa 10a ("os lugares que podem comer a pagina", D-104;
# lista unica 4.2, Cursus 3: "o corte da esquerda comeu a primeira letra ou duas
# das linhas do bloco de baixo"). O corte da sobra e feito na folha COMO VEIO,
# antes do endireitar; no livro novo a pagina cortada e depois girada inteira,
# no mesmo tamanho (core/endireitar.rotacionar), e o que o giro empurra para
# fora da imagem some. A linha do ScanTailor fica colada no texto (no Cursus 3,
# 2 mm), e o giro de 0,75 grau levava os cantos do bloco de baixo para fora; a
# letra encostada na beirada ainda fazia a caixa do conteudo do ScanTailor
# (borda preta "ate a moldura") jogar fora um quarto da pagina.
# O conserto: cada lado do corte da sobra anda para FORA o que o giro pode
# empurrar (meia altura x seno do angulo, com GIRO_A_MAIS de sobra, porque o
# angulo que vale no fim pode ser outro: o do ScanTailor, ou um a mao) mais 1
# mm. O pedaco da beirada da vizinha que entra de volta e tirado depois, pelo
# corte de sempre, na pagina ja reta.
# Arriscado: tirar o GIRO_A_MAIS (o angulo final nao e o da analise); andar
# para DENTRO (comeria mais). Seguro: o milimetro.
GIRO_A_MAIS = 0.5


def folga_do_giro_na_sobra(sobra: tuple[float, float] | None, forma, angulo: float | None,
                           dpi: float) -> tuple[float, float] | None:
    """O corte da sobra (esquerda, direita, em fracao da largura da folha
    `forma` = img.shape) com a folga do giro de cada lado (ver o comentario
    acima). None continua None. Nunca passa da folha (0 a 1)."""
    if sobra is None:
        return None
    altura, largura = forma[0], forma[1]
    graus = abs(float(angulo or 0.0)) + GIRO_A_MAIS
    folga = (altura / 2.0) * math.sin(math.radians(graus)) + float(dpi) / 25.4
    em_fracao = folga / max(1, largura)
    a, b = sobra
    a = 0.0 if a <= 0.0 else max(0.0, a - em_fracao)
    b = 1.0 if b >= 1.0 else min(1.0, b + em_fracao)
    return (round(a, 6), round(b, 6))


def faixa_da_sobra(folha: ConfigFolha, pagina: ConfigPagina,
                   projeto: Projeto | None) -> tuple[float, float] | None:
    """A parte da folha (esquerda, direita, em fracao da largura) que fica
    depois do corte da sobra NESTA pagina, ou None quando nao corta.

    So corta com o livro marcado (Projeto.cortar_sobra), em pagina que nao
    vem de folha dividida, com a sobra achada na analise e a folha sem giro
    de 90 graus (a sobra foi medida na folha como veio; girada, ela ja nao
    vale - o giro desliga o corte da sobra nessa folha). Arriscado: mudar
    esta regra sem mudar as chaves das previas (ela entra em
    _chave_da_geometria, _entradas_do_preparo, _chave_das_linhas e
    ui/tarefas.py)."""
    if projeto is None or not getattr(projeto, "cortar_sobra", False):
        return None
    if getattr(folha, "sobra", None) is None:
        return None
    if folha.dividir and pagina.metade != METADE_INTEIRA:
        return None
    if int(folha.rotacao) % 360 != 0:
        return None
    try:
        a, b = (float(v) for v in folha.sobra)
    except (TypeError, ValueError):
        return None
    if not 0.0 <= a < b <= 1.0 or b - a < 0.2:
        return None
    return (a, b)


def _cortar_a_sobra(img: np.ndarray, faixa: tuple[float, float] | None) -> np.ndarray:
    """Fica so a faixa de colunas (fatia, sem copiar). Sem faixa, a imagem
    como veio. A conta das colunas e a de core/zonas_na_folha (fracao vezes
    largura); arredondar muda menos de um ponto."""
    if faixa is None:
        return img
    largura = img.shape[1]
    x0 = max(0, min(largura - 1, int(round(faixa[0] * largura))))
    x1 = max(x0 + 1, min(largura, int(round(faixa[1] * largura))))
    return img[:, x0:x1]


def recalcular_divisao(projeto: Projeto, indice_folha: int, jeito: str,
                       forcar: bool = False) -> Lombada:
    """A divisao da folha `indice_folha` por outro jeito, na hora (a aba
    "Onde cortar", quando a pessoa troca o jeito so desta folha). Abre o PDF,
    desenha a folha a DPI_ANALISE (como a analise), gira como a folha esta
    girada e acha a divisao. Leva uns decimos de segundo. Levanta ErroPDF se
    o livro nao abre."""
    folha = projeto.folhas[indice_folha]
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img = pagina_para_array(doc, indice_folha, dpi=DPI_ANALISE)
    finally:
        doc.close()
    if folha.rotacao:
        img = girar_90(img, folha.rotacao)
    return achar_divisao(img, jeito, DPI_ANALISE, forcar=forcar)


def trazer_divisao_da_analise(salvo: Projeto, fresco: Projeto) -> int:
    """O trabalho salvo volta por cima da analise nova (ui/janela_principal.
    _analise_pronta). Se a pessoa mudou, na tela "O que fazer", o JEITO de
    dividir do livro ou o corte da sobra, o salvo traria as posicoes velhas.
    Aqui vem da analise nova:
      - o corte da sobra do livro e a sobra de cada folha (nao ha sobra feita
        a mao);
      - com o jeito do livro trocado: a posicao da divisao das folhas que
        seguem o livro (ConfigFolha.dividir_como None) e que continuam
        divididas do mesmo jeito (uma folha com "nao dividir esta" fica como
        a pessoa deixou).
    Devolve quantas folhas tiveram a divisao trocada. So chamar quando o
    salvo combina com o fresco (projetos.combina_com: as mesmas folhas e as
    mesmas paginas em cada folha)."""
    salvo.cortar_sobra = bool(getattr(fresco, "cortar_sobra", False))
    for f_salva, f_nova in zip(salvo.folhas, fresco.folhas):
        f_salva.sobra = f_nova.sobra
    jeito_antes = dividir_scantailor.jeito_valido(getattr(salvo, "dividir_como", None))
    jeito_agora = dividir_scantailor.jeito_valido(getattr(fresco, "dividir_como", None))
    salvo.dividir_como = jeito_agora
    if jeito_antes == jeito_agora:
        return 0
    trocadas = 0
    for f_salva, f_nova in zip(salvo.folhas, fresco.folhas):
        if f_salva.dividir_como is not None or f_salva.dividir != f_nova.dividir:
            continue
        f_salva.posicao_corte = f_nova.posicao_corte
        f_salva.confianca_corte = f_nova.confianca_corte
        f_salva.e_paisagem = f_nova.e_paisagem
        trocadas += 1
    return trocadas


def _partes_da_folha(img: np.ndarray, folha: ConfigFolha) -> list[tuple[str, np.ndarray]]:
    """Divide a folha se for o caso. Não aplica filtro nem recorte."""
    if not folha.dividir:
        return [(METADE_INTEIRA, img)]
    esq, dir_ = dividir_imagem(img, folha.posicao_corte)
    return [(METADE_ESQUERDA, esq), (METADE_DIREITA, dir_)]


# ---------------------------------------------------------------------------
# Fase 2: gerar a imagem final de uma pagina
# ---------------------------------------------------------------------------

def preparar_para_recorte(
    img_folha: np.ndarray, folha: ConfigFolha, pagina: ConfigPagina,
    projeto: Projeto | None = None,
) -> np.ndarray:
    """Gira e divide a folha, mas NUNCA corta bordas nem endireita.

    É a base estável que a aba Bordas mostra enquanto o recorte está sendo
    ajustado - bug real achado ao vivo (23/09/2026, Samuel): a aba usava a
    MESMA prévia das outras abas, já cortada por `aplicar_recorte` (a que
    `renderizar_pagina` gera) - o retângulo do recorte era então desenhado
    como fração de uma imagem que JÁ era um recorte, e cada atualização
    (ao soltar o mouse) reaplicava a fração em cima do resultado anterior,
    encolhendo o corte sozinho a cada vez ("corto até a metade da coroa, mas
    o corte vai pra frente"). Com a aba mostrando sempre esta versão
    (girada/dividida, nunca cortada), o recorte sempre mapeia 1:1 para a
    imagem original, sem compor com o recorte de antes.
    """
    img = img_folha
    if folha.rotacao:
        img = girar_90(img, folha.rotacao)
    if folha.dividir and pagina.metade != METADE_INTEIRA:
        esq, dir_ = dividir_imagem(img, folha.posicao_corte)
        img = esq if pagina.metade == METADE_ESQUERDA else dir_
    # Item 2.1 (G3 (b)): o corte da sobra do ScanTailor, ainda na etapa
    # "dividir" (onde o ScanTailor o faz), antes de cortar as bordas. Sem o
    # projeto (quem chama de fora), nada muda.
    return _cortar_a_sobra(img, faixa_da_sobra(folha, pagina, projeto))


def preparar_metade(
    img_folha: np.ndarray, folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto,
    geometria: tuple | None = None, dpi: float | None = None,
) -> np.ndarray:
    """Aplica giro, divisão, recorte e endireitamento - nesta ordem.

    O filtro fica de fora de proposito: ele e por página e a interface precisa
    trocar só ele sem refazer o resto.

    Corte automatico + endireitar (conserto de 28/09/2026, Lista de bugs): o
    angulo continua sendo medido na pagina ja cortada, como sempre; se ela vai
    ser girada, o corte automatico e refeito um pouco maior
    (alargar_para_o_giro), para o giro nao levar os cantos do conteudo - era
    o comeco das linhas sumindo na Escola 35. O recorte que a pessoa escolheu
    a mao (pagina.recorte) NAO e alargado: sai como ela escolheu.

    Previa = PDF (conserto de 28/09/2026, noite): usa o corte e o angulo ja
    GUARDADOS para esta pagina (ver _GEOMETRIAS), calculados na folha na
    resolucao do PDF - por processar ou por renderizar_pagina. So quando nao
    ha nada guardado calcula em `img_folha`, como antes. Nunca abre o PDF: os
    cartoes e a tela ampliada chamam esta funcao no fio da tela.

    geometria: (recorte, angulo) ja pronto, que vale no lugar do guardado.
    Item 1.1: a folha sem o fundo (core/camadas.py) e cortada e endireitada
    com a geometria medida na folha COMO VEIO (_geometria_da_folha_como_veio),
    nunca medida nela mesma. None (o padrao) = como sempre.

    dpi: a resolucao de `img_folha`, so para quando o corte ainda nao esta
    guardado e e calculado aqui: a folga do corte sai em milimetros
    (recortar.FOLGA_MM). None (a tela, que nao sabe) = folga em fracao do lado.

    Item 2.2, G6 (09/10/2026): no livro novo (Projeto.ordem_do_preparo
    "endireitar_antes") a ordem e girar 90 -> dividir -> endireitar a pagina
    inteira -> cortar, com o corte medido na pagina reta e SEM a folga do
    giro (o paragrafo "Corte automatico + endireitar" acima vale so para o
    projeto "cortar_antes"). Ver _preparar_metade_e_geometria.

    Arriscado mudar: esta funcao alimenta a previa da tela, o PDF final e o
    avaliar.py; as duas ordens tem de ser as de core/zonas_na_folha.
    _matriz_folha_para_pagina (mudou uma, muda a outra).
    """
    return _preparar_metade_e_geometria(img_folha, folha, pagina, projeto,
                                        geometria=geometria, dpi=dpi)[0]


def preparar_metade_e_geometria(
    img_folha: np.ndarray, folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto,
    dpi: float | None = None,
) -> tuple[np.ndarray, dict]:
    """preparar_metade, devolvendo tambem a geometria do desenho (o giro de
    90, a divisao, o corte e o angulo aplicados; core/zonas_na_folha).

    Para a tela saber se as zonas da pagina valem nesta imagem
    (zonas_na_folha.zonas_valem_no_desenho) sem leva-las: e o que o
    "Ajustar o pedaco a figura" usa (junção do girar ao fase-1, 06/10/2026).
    `img_folha` e a folha COMO VEIO no PDF (sem o giro: quem gira e esta
    funcao). Nao mexe na pagina."""
    return _preparar_metade_e_geometria(img_folha, folha, pagina, projeto, dpi=dpi)


def _preparar_metade_e_geometria(
    img_folha: np.ndarray, folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto,
    geometria: tuple | None = None, dpi: float | None = None,
    so_a_geometria: bool = False,
) -> tuple[np.ndarray | None, dict]:
    """preparar_metade, devolvendo tambem a geometria do desenho (decisao D2,
    core/zonas_na_folha.geometria_do_desenho): o giro de 90, a divisao, o
    corte e o angulo que foram MESMO aplicados, e a proporcao da folha. E o
    que renderizar_pagina e processar passam a zonas_na_folha.acompanhar,
    para as zonas da aba Marcar ficarem sobre o mesmo pedaco da folha.

    so_a_geometria=True (converter_zonas_do_livro, decisao Z1): devolve
    (None, geometria) sem copiar o corte nem girar a imagem - a MESMA conta
    de sempre (inclusive o "recorte absurdo nao corta"), sem o custo do
    desenho. Arriscado: separar as duas contas em funcoes diferentes (a
    geometria anotada ao abrir deixaria de ser a da previa e a do PDF).

    Item 2.12 (21/10/2026; refeito em 22/10/2026): no fim, nas duas ordens,
    o desentortar do ScanTailor, se a pagina o tiver ligado. O corte continua
    MEDIDO como sempre (mesma conta, mesma caixa), mas e so uma medida: o
    desentortar recebe a pagina endireitada SEM o corte, com o papel do scan
    em volta, e a imagem e recortada uma vez, pela medida, dentro dele (a
    escolha do Samuel na Central, 22/10: "A - Como o ScanTailor: cortar uma
    vez so, no fim"; _desentortar_com_o_papel_em_volta). Desligado (o de
    fabrica) o codigo e o de sempre, sem passo nenhum: nada muda. O desenho
    (geometria das zonas) NAO inclui o desentortar: as zonas da aba Marcar
    ficam onde estavam na pagina reta (ressalva do item).
    Arriscado: (1) passar ao desentortar a pagina ja cortada (era o defeito
    de 21/10: o cabecalho e o comeco das linhas sumiam no Righetti 96 e no
    Cursus 151); (2) medir o corte na pagina desentortada (mudaria a ordem
    aprovada em 09/10: endireitar -> cortar -> desentortar -> filtro); (3)
    mexer no caminho do desligado (o livro tem de sair identico).

    As duas ordens (item 2.2, G6, core/ordem_do_preparo):
      "cortar_antes" (projeto de antes de 09/10/2026): o codigo de sempre,
        sem mudanca nenhuma (_preparar_cortando_antes);
      "endireitar_antes" (livro novo): a pagina inteira e endireitada e o
        recorte (em fracao da pagina RETA) e cortado dela.
    """
    from core.zonas_na_folha import geometria_do_desenho

    inteira = preparar_para_recorte(img_folha, folha, pagina, projeto)

    if geometria is None:
        geometria = _geometria_guardada(folha, pagina, projeto)
    if geometria is None:
        geometria = _geometria(inteira, pagina, projeto, dpi=dpi)
    recorte, angulo = geometria
    # item 2.5: com o livro em "cortar seguindo o conteudo", o corte do livro
    # (do tamanho das outras paginas); fora disso, volta como esta
    recorte = _corte_do_livro(folha, pagina, projeto, recorte, angulo, inteira)
    # item 2.14: o que fica fora da pagina achada vira branco (so com a borda
    # preta ligada e "pintar de branco"); None = nada a pintar
    area = None if so_a_geometria else _area_que_fica(folha, pagina, projeto)

    # item 2.12: so com o desentortar ligado o preparo vai pelo caminho do
    # "papel em volta"; desligado (o de fabrica) e o codigo de sempre.
    desentortar = desentortar_scantailor.ligado(pagina) and not so_a_geometria
    if not desentortar and not so_a_geometria:
        # os avisos da protecao (item 2.12) so valem com o desentortar ligado;
        # desligado, so tira o aviso que tiver ficado (nao muda a imagem)
        _anotar_desentortar_saiu_sem(pagina, False)
        _anotar_desentortar_ainda_deformada(pagina, False)

    if endireita_antes(projeto):
        if desentortar:
            img, cortou, girar = _desentortar_com_o_papel_em_volta(
                inteira, recorte, angulo, projeto, pagina, dpi, endireita_antes=True, folha=folha)
        else:
            img, cortou, girar = _preparar_endireitando_antes(inteira, recorte, angulo, projeto,
                                                              so_a_geometria, pagina)
        # juncao de 23/10/2026 (2.14 com o 2.12, os dois desligados de
        # fabrica): com o desentortar, a pagina sai do tamanho do corte, e o
        # pintar de branco vale do mesmo jeito; com o "desentortar aumentando
        # a pagina" ela sai maior que o corte e a conta da area nao vale: nao
        # pinta (ressalva da juncao).
        pode_pintar = not (desentortar and getattr(pagina, "desentortar_aumentar", False))
        if area is not None and img is not None and pode_pintar:
            # a area foi medida na pagina RETA, e o recorte e fracao dela
            img = _pintar_na_cortada(img, area, tuple(recorte) if cortou else None)
        dividida = bool(folha.dividir) and pagina.metade != METADE_INTEIRA
        desenho = geometria_do_desenho(
            img_folha.shape[1] / max(1, img_folha.shape[0]), folha.rotacao,
            folha.posicao_corte if dividida else None,
            pagina.metade if dividida else METADE_INTEIRA,
            tuple(recorte) if cortou else None, float(angulo) if girar else 0.0,
            sobra=faixa_da_sobra(folha, pagina, projeto), ordem=ordem_do_livro(projeto))
        return img, desenho

    if desentortar:
        if area is not None:
            # juncao de 23/10/2026: item 2.14 na ordem antiga, como abaixo (a
            # area foi medida na `inteira`), antes do desentortar
            inteira = borda_preta.pintar_fora(inteira, area)
        img, cortou, girar = _desentortar_com_o_papel_em_volta(
            inteira, recorte, angulo, projeto, pagina, dpi, endireita_antes=False, folha=folha)
        dividida = bool(folha.dividir) and pagina.metade != METADE_INTEIRA
        desenho = geometria_do_desenho(
            img_folha.shape[1] / max(1, img_folha.shape[0]), folha.rotacao,
            folha.posicao_corte if dividida else None,
            pagina.metade if dividida else METADE_INTEIRA,
            tuple(recorte) if cortou else None, float(angulo) if girar else 0.0,
            sobra=faixa_da_sobra(folha, pagina, projeto))
        return img, desenho

    # 2. cortar bordas (o recorte ja vem com a folga do giro, se houver giro)
    if area is not None:
        # item 2.14, ordem antiga: a area foi medida na pagina antes do corte
        # (a `inteira`): pinta nela, e o corte e o giro levam junto
        inteira = borda_preta.pintar_fora(inteira, area)
    img = inteira
    girar = etapas.endireita(projeto, pagina) and abs(angulo) >= ANGULO_MINIMO
    if recorte is not None:
        # fatiar (sem copiar) quando vai girar: o rotacionar ja devolve uma
        # imagem nova. Sem giro, copia, como sempre.
        img = (fatiar(inteira, recorte) if girar or so_a_geometria
               else aplicar_recorte(inteira, recorte))
    # recorte absurdo (menos de 8 pontos) volta a pagina inteira: nao cortou
    cortou = recorte is not None and (img is not inteira)

    # 3. endireitar
    if girar and not so_a_geometria:
        img = rotacionar(img, angulo)
    if so_a_geometria:
        img = None

    dividida = bool(folha.dividir) and pagina.metade != METADE_INTEIRA
    desenho = geometria_do_desenho(
        img_folha.shape[1] / max(1, img_folha.shape[0]), folha.rotacao,
        folha.posicao_corte if dividida else None,
        pagina.metade if dividida else METADE_INTEIRA,
        tuple(recorte) if cortou else None, float(angulo) if girar else 0.0,
        sobra=faixa_da_sobra(folha, pagina, projeto))
    return img, desenho


def _desentortar_com_o_papel_em_volta(inteira: np.ndarray, recorte, angulo: float,
                                      projeto: Projeto, pagina: ConfigPagina, dpi,
                                      endireita_antes: bool, folha: ConfigFolha | None = None):
    """O preparo da pagina com o desentortar LIGADO (item 2.12, 22/10/2026).
    Devolve (imagem, cortou, girou), como _preparar_endireitando_antes.

    A escolha do Samuel na Central (22/10/2026): "A - Como o ScanTailor:
    cortar uma vez so, no fim". O corte e medido como sempre (o mesmo
    `recorte`, a mesma caixa_em_pontos); a pagina e endireitada INTEIRA e
    entregue ao desentortar com o papel do proprio scan em volta, junto com a
    caixa do corte; o desentortar recorta uma vez, pela caixa
    (core/desentortar_scantailor.aplicar_no_corte). Nao inventa papel branco
    e nao corta duas vezes.

    As duas ordens dao a MESMA caixa e o MESMO giro do caminho desligado:
      livro novo ("endireitar_antes"): a pagina inteira girada em volta do
        centro DELA (rotacionar), como _preparar_endireitando_antes; a caixa
        e a do corte na pagina reta;
      livro de antes de 09/10 ("cortar_antes"): la o giro e feito no pedaco
        ja cortado, em volta do centro do CORTE. Aqui a pagina inteira e
        girada em volta desse mesmo centro: dentro da caixa os pontos sao os
        do caminho de sempre, e o que estava fora do corte (o papel de
        verdade) fica no lugar do branco que o giro punha nos cantos.

    Custo: o giro da pagina inteira (em vez de so a caixa) e a DLL lendo a
    pagina inteira; so com o desentortar ligado (desligado nao passa aqui).
    Arriscado: cortar antes de chamar o desentortar (o defeito de 21/10) ou
    trocar a caixa/o centro do giro (a pagina deixaria de bater com a do
    desentortar desligado nos pontos que nao mudam).

    A MEDIDA NA RESOLUCAO DO LIVRO (resposta P6 do Samuel, 23/10/2026, opcao
    (b), "Como o ScanTailor"): o desentortar so e feito de verdade na
    resolucao do livro (projeto.qualidade_dpi); o resultado fica guardado
    (_DESENTORTADAS) e qualquer desenho menor (previa rapida, cartoes,
    miniaturas, tela ampliada) usa ESSA pagina, so reduzida - com os avisos
    dela. Enquanto a medida nao existe, o desenho menor sai SEM desentortar
    (a tela pede a medida numa tarefa por tras: medir_o_desentortar) e nao
    mexe nos avisos. `folha` None (quem chama de fora) ou sem chave (arquivo
    que nao existe no disco, filtro "Tirar o fundo"): o caminho de antes
    (desentorta na resolucao que vier). Ver _desentortada_guardada.
    """
    girar = etapas.endireita(projeto, pagina) and abs(angulo) >= ANGULO_MINIMO
    caixa = None if recorte is None else caixa_em_pontos(inteira.shape, recorte)
    cortou = caixa is not None
    if not girar:
        reta = inteira
    elif endireita_antes or caixa is None:
        reta = rotacionar(inteira, angulo)  # em volta do centro da pagina
    else:
        reta = _rotacionar_em_volta_de(inteira, angulo, caixa)
    na_resolucao_do_livro = _julga_os_avisos_do_desentortar(projeto, dpi)
    chave = None if folha is None else _chave_do_desentortar(folha, pagina, projeto)
    if chave is not None:
        guardada = _desentortada_guardada(chave)
        if guardada is not None:
            # a medida ja feita na resolucao do livro: a mesma pagina, so
            # reduzida (ou a mesma, se este desenho e o da resolucao do livro)
            _anotar_desentortar_saiu_sem(pagina, guardada.saiu_sem)
            _anotar_desentortar_ainda_deformada(pagina, guardada.ainda_deformada)
            return _desentortada_no_tamanho(guardada, reta.shape, caixa, pagina), cortou, girar
        if not na_resolucao_do_livro:
            # ainda nao medida: a pagina sem desentortar (o corte de sempre),
            # sem mexer nos avisos; a medida vem por tras (medir_o_desentortar)
            x0, y0, x1, y1 = (0, 0, reta.shape[1], reta.shape[0]) if caixa is None else caixa
            return reta[y0:y1, x0:x1].copy(), cortou, girar
    preparo = desentortar_scantailor.preparar_no_corte(reta, caixa, pagina, dpi)
    if na_resolucao_do_livro:
        _anotar_desentortar_saiu_sem(pagina, preparo.saiu_sem)
        _anotar_desentortar_ainda_deformada(pagina, preparo.ainda_deformada)
        if chave is not None:
            _guardar_desentortada(chave, preparo, reta.shape)
    return preparo.imagem, cortou, girar


# ---------------------------------------------------------------------------
# A medida do desentortar (item 2.12, resposta P6 do Samuel, 23/10/2026, opcao
# (b): "Como o ScanTailor: o desentortar sempre é medido na resolução do livro
# (300 DPI), numa tarefa por trás (uns 3 a 8 s por página, só nas páginas com
# ele ligado), e a prévia rápida e os cartões (Preto e branco, Melhorar,
# Mágico pro, Original) usam essa medida, só reduzida. A página na tela fica
# igual à do PDF, e os avisos [...] aparecem na hora.").
#
# Por que: o desentortar do ScanTailor nao acha as linhas curvas em resolucao
# baixa (medido no Destino 18 e no Righetti 96: a 100, 150 e 200 DPI nao
# mexe; a 300 mexe), entao a previa rapida (110 DPI) e os cartoes mostravam a
# pagina como se ele nao existisse. No ScanTailor o modelo da curva e medido
# uma vez, na imagem inteira, e guardado; a saida em qualquer tamanho usa ele.
#
# Aqui a "medida" guardada e a pagina ja desentortada na resolucao do livro
# (a mesma que vai para o PDF), com o que a protecao decidiu (saiu_sem,
# ainda_deformada). O desenho menor reduz essa pagina (INTER_AREA). Guardada
# so na memoria, nesta sessao, com limite de tamanho (MAX_BYTES_DESENTORTADAS:
# o pico nao cresce com o livro). A chave e a do corte (_chave_da_geometria:
# arquivo, giro, divisao, corte, angulo, ordem...) mais o modo do desentortar
# e o "aumentando a pagina": mudou qualquer um, mede de novo; o filtro e os
# ajustes do filtro NAO entram (o desentortar vem antes do filtro).
#
# Desligado (o de fabrica) nada disto roda: o preparo nem chama
# _desentortar_com_o_papel_em_volta.
#
# Seguro mudar: MAX_BYTES_DESENTORTADAS. Arriscado: guardar medida feita em
# outra resolucao que nao projeto.qualidade_dpi (a tela deixaria de bater com
# o PDF); tirar da chave algo de que a pagina depende (a tela mostraria a
# pagina de antes da mudanca).
# ---------------------------------------------------------------------------

class _Desentortada:
    """A medida guardada: a pagina desentortada na resolucao do livro e o
    que a protecao decidiu. altura_reta/largura_reta: o tamanho da pagina
    reta (sem corte) em que foi medida, para a conta da reducao."""

    __slots__ = ("imagem", "saiu_sem", "ainda_deformada", "altura_reta", "largura_reta")

    def __init__(self, imagem: np.ndarray, saiu_sem: bool, ainda_deformada: bool,
                 forma_reta: tuple) -> None:
        self.imagem = imagem
        self.saiu_sem = bool(saiu_sem)
        self.ainda_deformada = bool(ainda_deformada)
        self.altura_reta, self.largura_reta = int(forma_reta[0]), int(forma_reta[1])


_DESENTORTADAS: "OrderedDict[tuple, _Desentortada]" = OrderedDict()
_TRANCA_DESENTORTADAS = threading.Lock()
MAX_BYTES_DESENTORTADAS = 400 * 1024 * 1024   # ~15 a 30 paginas a 300 DPI


def _chave_do_desentortar(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto):
    """A chave da medida do desentortar desta pagina, ou None (sem medida
    guardada: arquivo que nao existe no disco, desentortar desligado, ou o
    filtro "Tirar o fundo", em que a pagina desentortada e a folha sem o
    fundo - essa fica no caminho de antes, ressalva do item)."""
    if not desentortar_scantailor.ligado(pagina) or usa_tirar_fundo(projeto, pagina):
        return None
    base = _chave_da_geometria(folha, pagina, projeto)
    if base is None:
        return None
    return base + (desentortar_scantailor.modo_da_pagina(pagina),
                   bool(getattr(pagina, "desentortar_aumentar", False)))


def _desentortada_guardada(chave) -> "_Desentortada | None":
    """A medida guardada sob `chave`, ou None."""
    with _TRANCA_DESENTORTADAS:
        guardada = _DESENTORTADAS.get(chave)
        if guardada is not None:
            _DESENTORTADAS.move_to_end(chave)
        return guardada


def _guardar_desentortada(chave, preparo, forma_reta: tuple) -> None:
    """Guarda a medida (uma copia da imagem: quem recebeu a de `preparo` pode
    mexer nela). Joga fora as mais antigas acima de MAX_BYTES_DESENTORTADAS."""
    guardada = _Desentortada(preparo.imagem.copy(), preparo.saiu_sem,
                             preparo.ainda_deformada, forma_reta)
    with _TRANCA_DESENTORTADAS:
        _DESENTORTADAS[chave] = guardada
        _DESENTORTADAS.move_to_end(chave)
        total = sum(g.imagem.nbytes for g in _DESENTORTADAS.values())
        while total > MAX_BYTES_DESENTORTADAS and len(_DESENTORTADAS) > 1:
            _, velha = _DESENTORTADAS.popitem(last=False)
            total -= velha.imagem.nbytes


def _desentortada_no_tamanho(guardada: "_Desentortada", forma_reta: tuple, caixa,
                             pagina: ConfigPagina) -> np.ndarray:
    """A pagina guardada no tamanho deste desenho. Na resolucao do livro
    (mesma pagina reta): uma copia, ponto por ponto. Menor: reduzida; sem o
    "aumentando a pagina", exatamente do tamanho do corte deste desenho (o
    mesmo tamanho do desenho com o desentortar desligado, e o que a geometria
    das zonas supoe); com ele, pela proporcao das duas paginas retas."""
    img = guardada.imagem
    altura, largura = int(forma_reta[0]), int(forma_reta[1])
    if (altura, largura) == (guardada.altura_reta, guardada.largura_reta):
        return img.copy()
    aumentar = bool(getattr(pagina, "desentortar_aumentar", False))
    if not aumentar and caixa is not None:
        x0, y0, x1, y1 = caixa
        alvo = (max(1, x1 - x0), max(1, y1 - y0))
    elif not aumentar:
        alvo = (largura, altura)
    else:
        alvo = (max(1, int(round(img.shape[1] * largura / max(1, guardada.largura_reta)))),
                max(1, int(round(img.shape[0] * altura / max(1, guardada.altura_reta)))))
    if (img.shape[1], img.shape[0]) == alvo:
        return img.copy()
    reduz = alvo[0] <= img.shape[1] and alvo[1] <= img.shape[0]
    return cv2.resize(img, alvo, interpolation=cv2.INTER_AREA if reduz else cv2.INTER_LINEAR)


def desentortar_por_medir(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A pagina tem o desentortar ligado e a medida dele (na resolucao do
    livro) ainda nao foi feita? E o que a tela olha para pedir a medida por
    tras (medir_o_desentortar) e mostrar o sinal "Desentortando esta
    pagina". Desligado, sem chave (ver _chave_do_desentortar) ou ja medida:
    False. Barato (sem desenho): pode ser chamado no fio da tela."""
    try:
        folha = projeto.folhas[pagina.folha]
    except (IndexError, AttributeError, TypeError):
        return False
    chave = _chave_do_desentortar(folha, pagina, projeto)
    return chave is not None and _desentortada_guardada(chave) is None


def estado_do_desentortar(projeto: Projeto, pagina: ConfigPagina) -> str:
    """Para a chave das previas da tela (ui/tarefas.GerenciadorPrevias.chave):
    "" desligado; "medido" ou "por_medir". Quando a medida chega, a chave
    muda e a tela desenha de novo (a previa e os cartoes) com ela."""
    if not desentortar_scantailor.ligado(pagina):
        return ""
    return "por_medir" if desentortar_por_medir(projeto, pagina) else "medido"


def medir_o_desentortar(doc, projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A medida do desentortar desta pagina, na resolucao do livro (resposta
    P6, opcao (b)). Desenha a folha em projeto.qualidade_dpi e prepara a
    pagina (o mesmo caminho do PDF): a pagina desentortada fica guardada e os
    avisos da protecao sao postos ou tirados. Uns 3 a 8 s por pagina:
    chamar SEMPRE fora do fio da tela (ui/tarefas.TarefaMedirDesentortar).
    Devolve True se mediu agora; False se nao havia o que medir (desligado,
    ja medida ou sem chave). Arriscado: medir em outra resolucao."""
    if not desentortar_por_medir(projeto, pagina):
        return False
    folha = projeto.folhas[pagina.folha]
    grande = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
    if _precisa_de_geometria(pagina, projeto):
        _guardar_geometria(folha, pagina, projeto, grande, doc)
    _preparar_metade_e_geometria(grande, folha, pagina, projeto, dpi=projeto.qualidade_dpi)
    return True


def _julga_os_avisos_do_desentortar(projeto: Projeto, dpi) -> bool:
    """Item 2.12, conserto de 23/10/2026 (achado ao fazer os prints da janela
    para a resposta P5): so o desenho da pagina na resolucao do livro
    (projeto.qualidade_dpi, a do PDF final) poe ou tira os avisos do
    desentortar. O desentortar do ScanTailor nao acha as curvas na resolucao
    baixa (medido no Destino do socialismo 18 e no Righetti 96: a 100, 150 e
    200 DPI nao mexe; a 300 mexe), entao a prévia rapida (110 DPI), as
    miniaturas e os cartoes TIRAVAM o aviso que o desenho a 300 DPI tinha
    posto: o "Desentortar não usado" e o "A página ainda saiu deformada"
    sumiam da faixa antes do clique. dpi None (quem chama nao sabe) tambem
    nao julga. Arriscado: julgar em qualquer resolucao (volta o aviso que
    pisca e some)."""
    try:
        return dpi is not None and float(dpi) >= float(projeto.qualidade_dpi) - 0.5
    except (TypeError, ValueError, AttributeError):
        return False


def _anotar_desentortar_saiu_sem(pagina: ConfigPagina, saiu_sem: bool) -> None:
    """Poe ou tira o aviso analise.DESENTORTAR_SAIU_SEM (item 2.12, respostas
    P1 e P2 do Samuel, 22/10/2026: a protecao recusou o desentortar e a pagina
    saiu sem ele). Do mesmo jeito que _anotar_conferir: ao POR, a pagina volta
    a "nao conferida" e o aviso vai para a frente; o "esta bom assim" depois
    disso continua valendo. Tirado quando a pagina sai desentortada (o botao
    "Desentortar aumentando a página") ou com o desentortar desligado.
    Arriscado: por o aviso sem voltar `revisada` (nasceria escondido)."""
    _anotar_aviso_da_pagina(pagina, analise.DESENTORTAR_SAIU_SEM, saiu_sem)


def _anotar_desentortar_ainda_deformada(pagina: ConfigPagina, deformada: bool) -> None:
    """Poe ou tira o aviso analise.DESENTORTAR_AINDA_DEFORMADA (item 2.12,
    resposta P5 do Samuel, 23/10/2026: depois do botao "Desentortar aumentando
    a página" o programa confere de novo e, se a pagina ainda saiu deformada,
    o aviso PERGUNTA - "Desfazer" ou "Manter assim" -, sem voltar sozinho).
    Mesmo jeito de _anotar_desentortar_saiu_sem: ao por, a pagina volta a "nao
    conferida"; o "Manter assim" (que marca a pagina como conferida) continua
    valendo nas proximas vezes que a pagina for desenhada. Tirado quando a
    pagina aumentada sai boa, quando o aumento e desfeito ou com o desentortar
    desligado."""
    _anotar_aviso_da_pagina(pagina, analise.DESENTORTAR_AINDA_DEFORMADA, deformada)


def _anotar_aviso_da_pagina(pagina: ConfigPagina, codigo: str, vale: bool) -> None:
    """O jeito comum dos dois avisos do desentortar (item 2.12): ao POR, na
    frente e a pagina volta a "nao conferida"; ja posto, nada muda (o "esta
    bom assim" continua); ao TIRAR, so sai da lista. Arriscado: por sem voltar
    `revisada` (o aviso nasceria escondido)."""
    if not hasattr(pagina, "alertas"):
        return
    tem = codigo in pagina.alertas
    if vale and not tem:
        pagina.alertas.insert(0, codigo)
        pagina.revisada = False
    elif not vale and tem:
        pagina.alertas = [a for a in pagina.alertas if a != codigo]


def _rotacionar_em_volta_de(img: np.ndarray, angulo: float, caixa) -> np.ndarray:
    """A pagina inteira girada como core.endireitar.rotacionar gira o pedaco
    img[y0:y1, x0:x1] (em volta do centro DO PEDACO, mesma interpolacao), mas
    com o papel de verdade em volta no lugar do branco. So para o desentortar
    no livro "cortar_antes" (_desentortar_com_o_papel_em_volta)."""
    x0, y0, x1, y1 = caixa
    altura, largura = img.shape[:2]
    centro = (x0 + (x1 - x0) / 2.0, y0 + (y1 - y0) / 2.0)
    matriz = cv2.getRotationMatrix2D(centro, angulo, 1.0)
    borda = 255 if img.ndim == 2 else (255, 255, 255)
    return cv2.warpAffine(img, matriz, (largura, altura), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=borda)


def _preparar_endireitando_antes(inteira: np.ndarray, recorte, angulo: float,
                                 projeto: Projeto, so_a_geometria: bool,
                                 pagina: ConfigPagina | None = None):
    """A ordem nova (item 2.2, G6, 09/10/2026): endireitar a pagina inteira
    (`inteira`: girada de 90 e dividida, sem corte), depois cortar a pagina
    reta pelo `recorte` (fracao da pagina RETA). Devolve (imagem, cortou,
    girou). Com so_a_geometria: imagem None e nada e girado nem copiado
    (o endireitar nao muda o tamanho, entao o "recorte absurdo nao corta" e
    decidido na mesma conta).

    Velocidade (regra 6): com corte, so a parte cortada da pagina reta e
    desenhada (core/endireitar.rotacionar_e_cortar), nunca a pagina inteira.

    Arriscado: cortar antes de girar aqui (seria a ordem antiga com o
    recorte da nova); girar em volta de outro centro ou com outro tamanho
    (core/zonas_na_folha._matriz_folha_para_pagina supoe o rotacionar).

    pagina (obra 26/10, etapa 1, D-009): para o angulo a mao valer com
    "Endireitar" desligado (core/etapas.endireita). None (quem chama de
    fora, sem a pagina): so a caixinha, como antes.

    Ordem obrigatoria (D-016): endireita a pagina inteira, depois corta uma
    vez so - com o corte e o angulo a mao ou automaticos, igual.
    """
    girar = ((etapas.endireita(projeto, pagina) if pagina is not None
              else etapas.endireita_sozinho(projeto)) and abs(angulo) >= ANGULO_MINIMO)
    # o endireitar nao muda o tamanho: a caixa do corte e a mesma na pagina
    # inteira e na reta (None = sem corte, ou recorte absurdo: nao corta)
    caixa = None if recorte is None else caixa_em_pontos(inteira.shape, recorte)
    cortou = caixa is not None
    if so_a_geometria:
        return None, cortou, girar
    if caixa is not None:
        # etapa 10a: a cunha do giro com a cor da beirada (D-095, cunhas brancas)
        img = rotacionar_e_cortar(inteira, angulo if girar else 0.0, caixa, cunha_com_o_papel=True)
    else:
        img = rotacionar(inteira, angulo) if girar else inteira
    return img, cortou, girar


def _geometria(base: np.ndarray, pagina: ConfigPagina, projeto: Projeto,
               dpi: float | None = None, dpi_do_scan: float | None = None,
               medidas: dict | None = None, com_o_corte: bool = True,
               extras: dict | None = None):
    """(recorte, angulo) da pagina, medidos em `base` (a pagina ja girada de
    90 em 90 e dividida, antes de cortar).

    dpi: a resolucao em que `base` foi desenhada, para a folga do corte sair
    em milimetros (core/recortar.FOLGA_MM, conferencia 5, P2, 01/10/2026).
    None quando quem chama nao sabe (a tela, sem o corte do PDF guardado): ai
    a folga e uma fracao do lado (recortar.FOLGA).
    dpi_do_scan: o que o PDF diz do escaneamento (_dpi_do_scan), so para o
    DPI dito ao endireitar do ScanTailor (item 2.2); None = nao se sabe.
    medidas: dicionario que, se vier, recebe as duas contas do angulo
    automatico (_angulo_automatico) - e o que _guardar_geometria guarda para
    a aba Endireitar e para o aviso C1.

    recorte: (x, y, largura, altura) em fracao, ou None quando nao corta. O
    manual (pagina.recorte) vale como esta; o automatico vem de
    detectar_bordas e ganha a folga do giro (alargar_para_o_giro).
    angulo: em graus; 0.0 quando nao endireita. O manual (pagina.angulo_manual)
    vale como esta; o automatico vem da conta da pagina (_angulo_automatico).

    Item 2.2, G6: no livro "endireitar_antes" a conta e a de
    _geometria_endireitando_antes (o recorte sai em fracao da pagina RETA).
    com_o_corte=False (so a analise, que quer as duas contas do angulo para
    o aviso C1): nessa ordem nao mede o corte (recorte None). Na ordem
    antiga e ignorado - a conta de sempre, sem mudanca nenhuma.
    extras (obra 26/10, etapa 10a): se vier, recebe "encostou" (o corte comum
    encostou no texto, medido na pagina reta) - so no livro novo.
    """
    if endireita_antes(projeto):
        return _geometria_endireitando_antes(base, pagina, projeto, dpi, dpi_do_scan,
                                             medidas, com_o_corte, extras)
    recorte = None
    automatico = None
    # obra 26/10, etapa 1 (D-009): o corte a mao vale com "Cortar as bordas"
    # desligado tambem (core/etapas.recorte_a_mao); o AUTOMATICO so mede com a
    # caixinha ligada, como sempre
    recorte_a_mao = etapas.recorte_a_mao(projeto, pagina)
    if recorte_a_mao is not None:
        recorte = recorte_a_mao
    elif etapas.corta_sozinho(projeto):
        # o recorte automatico e calculado na metade ja separada: cada
        # pagina tem sua propria sombra de lombada de um lado so
        automatico = detectar_bordas(base, dpi=dpi)
        recorte = automatico.tupla
        if _corte_sugerido(projeto, pagina):
            # itens 2.5 e 2.13: o corte do ScanTailor (ou "so o preto"),
            # medido na pagina ainda torta (nesta ordem o giro vem depois
            # do corte); a folga do giro entra abaixo, como no corte comum
            medido = _medir_o_conteudo(base, dpi, dpi_do_scan, automatico.pecas, projeto,
                                       base if _corta_pela_borda(projeto, pagina) else None,
                                       comum=automatico,
                                       em_branco=analise.EM_BRANCO in pagina.alertas)
            if medidas is not None:
                medidas["conteudo"] = medido
            proprio = medido.recorte_proprio() if _troca_o_corte(projeto, pagina) else None
            if proprio is not None:
                automatico = Recorte(*proprio, pecas=automatico.pecas)
                recorte = automatico.tupla

    angulo = 0.0
    # obra 26/10, etapa 1 (D-009): o angulo a mao vale com "Endireitar"
    # desligado tambem; o automatico so com a caixinha ligada
    angulo_a_mao = etapas.angulo_a_mao(projeto, pagina)
    if angulo_a_mao is not None or etapas.endireita_sozinho(projeto):
        angulo = angulo_a_mao
        if angulo is None:
            cortada = base if recorte is None else fatiar(base, recorte)
            angulo = _angulo_automatico(base, cortada, pagina, projeto, dpi, dpi_do_scan, medidas)
        angulo = float(angulo or 0.0)
        if automatico is not None and abs(angulo) >= ANGULO_MINIMO:
            # mesma regra do rotacionar: abaixo de ANGULO_MINIMO nao gira
            recorte = alargar_para_o_giro(automatico, angulo, base).tupla
    return recorte, angulo


def _angulo_automatico(base: np.ndarray, cortada: np.ndarray, pagina: ConfigPagina,
                       projeto: Projeto, dpi: float | None, dpi_do_scan: float | None,
                       medidas: dict | None = None) -> float:
    """O angulo automatico da pagina, pela conta que vale nela (item 2.2,
    decisao G4 (b) do Samuel, 05/10/2026: "O do ScanTailor de fabrica [...]
    mas eu vou ter a opcao de escolher").

    "programa": core.endireitar.detectar_angulo na pagina ja cortada
        (`cortada`), como sempre - o livro antigo sai identico.
    "scantailor": o SkewFinder do ScanTailor na pagina ANTES do corte
        (`base`), como o ScanTailor faz (core/endireitar_scantailor.py). Sem
        a DLL, cai na conta do programa (o motivo vai uma vez para o log).

    As duas contas so sao feitas juntas quando a do ScanTailor entra (a do
    livro ou a da pagina): o livro antigo nao fica mais lento. `medidas`
    recebe "programa", "scantailor" (None se indisponivel ou nao medido),
    "jeito" (a conta que valeu) e "discordam" (C1: so em livro cuja conta e a
    do ScanTailor; endireitar_scantailor.discordam). Arriscado: medir a do
    programa em `base` (sem o corte) - mudaria o angulo do livro antigo."""
    es = endireitar_scantailor
    jeito = es.jeito_da_pagina(projeto, pagina)
    do_livro = es.jeito_do_livro(projeto)
    nosso = detectar_angulo(cortada).angulo
    do_scantailor = None
    if es.JEITO_SCANTAILOR in (jeito, do_livro):
        medida = es.medir_na_pagina(base, dpi, dpi_do_scan)
        if medida.disponivel:
            do_scantailor = float(medida.angulo)
        else:
            es.avisar_uma_vez(medida)
    valeu = es.JEITO_SCANTAILOR if (jeito == es.JEITO_SCANTAILOR and do_scantailor is not None) \
        else es.JEITO_PROGRAMA
    if medidas is not None:
        medidas.update(
            programa=float(nosso), scantailor=do_scantailor, jeito=valeu,
            discordam=bool(do_livro == es.JEITO_SCANTAILOR and es.discordam(nosso, do_scantailor)))
    return do_scantailor if valeu == es.JEITO_SCANTAILOR else nosso


def _geometria_endireitando_antes(base: np.ndarray, pagina: ConfigPagina, projeto: Projeto,
                                  dpi: float | None, dpi_do_scan: float | None,
                                  medidas: dict | None, com_o_corte: bool = True,
                                  extras: dict | None = None):
    """(recorte, angulo) na ordem nova (item 2.2, G6, decisao do Samuel de
    09/10/2026: "Endireitar antes de cortar (como o ScanTailor)" -> "Pode
    comecar"). `base`: a pagina girada de 90 e dividida, sem corte.

    1. O angulo: o manual (pagina.angulo_manual) como esta; o automatico pela
       MESMA conta de sempre (_angulo_automatico): a do ScanTailor em `base`,
       a do programa na pagina cortada pelo corte automatico de `base`
       (detectar_bordas, como antes) - o angulo de um livro novo e o mesmo
       que seria na ordem antiga, so o corte muda (foi o que a simulacao
       mostrou ao Samuel). O corte a mao NAO entra na medida do angulo: ele
       esta em fracao da pagina reta, que so existe depois do angulo.
    2. O corte: o manual (pagina.recorte) como esta, em fracao da pagina
       RETA; o automatico e detectar_bordas na pagina ja endireitada (a
       inteira, girada em volta do centro, mesmo tamanho), sem a folga do
       giro (alargar_para_o_giro): o giro ja aconteceu.

    Custo: o corte automatico e medido duas vezes (uma para a conta do
    programa, outra na pagina reta) - so na hora de guardar a geometria
    (_guardar_geometria, uma vez por pagina). Para pesar menos, as duas
    medidas sao feitas na pagina em CINZA (detectar_bordas so olha o cinza;
    a primeira da exatamente o mesmo corte que na pagina colorida) e e o
    cinza que e girado para a segunda (girar o cinza custa 1/4 de girar a
    cor; a diferenca para "girar a cor e passar para cinza" e de 1 nivel de
    cinza no arredondamento).

    g6-retangulo (Samuel, 09/10/2026, "Fica no mesmo lugar da pagina (como
    no ScanTailor)"): quando o angulo muda DEPOIS, os numeros do corte a mao
    nao mudam - ele fica no mesmo lugar da pagina reta. A outra opcao
    ("acompanha o texto") esta pronta, sem tela: recorte_depois_de_mudar_o_angulo.

    Arriscado: medir a conta do programa em outro lugar (o C1 mudaria);
    alargar o corte para o giro aqui (a pagina ja esta reta: so cresceria).
    """
    angulo = 0.0
    # obra 26/10, etapa 1 (D-009): o angulo e o corte a mao valem com as
    # caixinhas desligadas tambem (core/etapas); o automatico so mede com elas
    angulo_a_mao = etapas.angulo_a_mao(projeto, pagina)
    recorte_a_mao = etapas.recorte_a_mao(projeto, pagina)
    cinza = None

    def em_cinza():
        nonlocal cinza
        if cinza is None:
            cinza = base if base.ndim == 2 else cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
        return cinza

    if angulo_a_mao is not None or etapas.endireita_sozinho(projeto):
        angulo = angulo_a_mao
        if angulo is None:
            provisorio = (detectar_bordas(em_cinza(), dpi=dpi).tupla
                          if etapas.corta_sozinho(projeto) else None)
            cortada = base if provisorio is None else fatiar(base, provisorio)
            angulo = _angulo_automatico(base, cortada, pagina, projeto, dpi, dpi_do_scan, medidas)
        angulo = float(angulo or 0.0)

    recorte = None
    if recorte_a_mao is not None:
        recorte = recorte_a_mao
    elif etapas.corta_sozinho(projeto):
        if com_o_corte:
            girar = etapas.endireita(projeto, pagina) and abs(angulo) >= ANGULO_MINIMO
            reta = rotacionar(em_cinza(), angulo) if girar else em_cinza()
            # `girada` (conserto de 13/10/2026): diz ao corte de quanto a
            # pagina foi girada, para a cunha branca do giro nao esconder a
            # borda preta do scanner (core/recortar, "A cunha do giro").
            # Arriscado: tirar (volta a faixa preta do Cursus 3).
            # `como_veio` (conserto de 20/10/2026): a pergunta "ha o que
            # recortar?" e feita na pagina antes do giro, como na ordem
            # antiga. Arriscado: tirar (o Pesel 21 volta a sair cortado rente).
            comum = detectar_bordas(reta, dpi=dpi, girada=angulo if girar else None,
                                    como_veio=em_cinza() if girar else None, livro_novo=True)
            recorte = comum.tupla
            if extras is not None:
                # etapa 10a (D-104): o "Corte encostou no texto" medido no
                # corte de verdade (a pagina reta), nao na folha da analise
                extras["encostou"] = bool(comum.encostou_no_conteudo)
            if _corte_sugerido(projeto, pagina):
                # itens 2.5 e 2.13: o corte do ScanTailor (ou "so o preto"), na
                # pagina ja reta (a ordem dele); sem caixa (pagina em branco,
                # sem a DLL) fica o comum
                # a borda preta ve a pagina COLORIDA (a cor separa o fundo do
                # scanner, neutro, de cartao ou capa escura) com a cunha preta
                cunha_preta = (((rotacionar(base, angulo, fundo=0) if girar else base))
                               if _corta_pela_borda(projeto, pagina) else None)
                medido = _medir_o_conteudo(reta, dpi, dpi_do_scan, comum.pecas, projeto, cunha_preta,
                                           comum=comum,
                                           em_branco=analise.EM_BRANCO in pagina.alertas)
                if medidas is not None:
                    medidas["conteudo"] = medido
                if _troca_o_corte(projeto, pagina):
                    recorte = medido.recorte_proprio() or recorte
    return recorte, angulo


# Decisao do Samuel, g6-retangulo (09/10/2026): o que acontece com o corte a
# mao (pagina.recorte) quando o angulo muda DEPOIS, no livro novo. Codigos
# internos (nunca texto de tela).
RETANGULO_FICA = "fica"            # de fabrica: fica no mesmo lugar da pagina reta
RETANGULO_ACOMPANHA = "acompanha"  # a outra opcao: cresce para o texto continuar dentro
RETANGULO_PADRAO = RETANGULO_FICA


def recorte_depois_de_mudar_o_angulo(projeto: Projeto, pagina: ConfigPagina,
                                     angulo_antes: float | None, angulo_depois: float | None,
                                     jeito: str = RETANGULO_PADRAO,
                                     proporcao: float | None = None):
    """O corte a mao da pagina depois de o angulo mudar de `angulo_antes`
    para `angulo_depois` (graus, sentido do OpenCV). Nunca muda a pagina:
    devolve o recorte (x, y, largura, altura) ou None.

    Decisao do Samuel, pergunta g6-retangulo, 09/10/2026: "Fica no mesmo
    lugar da pagina (como no ScanTailor)" e o de FABRICA (RETANGULO_FICA): o
    retangulo nao se mexe, os numeros do corte ficam como estao - por isso
    ninguem precisa chamar esta funcao no caminho de fabrica. Ele pediu
    tambem a outra opcao, "Acompanha o texto" (RETANGULO_ACOMPANHA), mas ONDE
    a pessoa troca ainda vai ser perguntado: NAO ha controle na tela nem
    campo no projeto; quando houver, quem muda o angulo (aba Endireitar,
    ui/tela_conferir) chama esta funcao com o jeito escolhido e grava o
    recorte devolvido na mesma acao do desfazer.

    "Acompanha": o retangulo (em fracao da pagina reta com angulo_antes) e
    levado de volta a pagina sem endireitar, girado pelo angulo novo, e o
    corte vira a caixa em volta dos quatro cantos (cresce um pouco; nunca
    passa da pagina). Precisa de `proporcao` (largura / altura da pagina
    girada de 90 e dividida, antes do corte; o endireitar nao muda o
    tamanho); sem ela, ou na ordem antiga ("cortar_antes", em que o giro
    acontece dentro do corte e o texto ja acompanha), devolve como esta.

    Arriscado: trocar RETANGULO_PADRAO (decisao do Samuel); girar em volta
    de outro centro que nao o da pagina inteira (rotacionar).
    """
    if pagina.recorte is None:
        return None
    recorte = tuple(float(v) for v in pagina.recorte)
    if (jeito != RETANGULO_ACOMPANHA or not endireita_antes(projeto) or not proporcao
            or angulo_antes is None or angulo_depois is None):
        return recorte
    giro = angulo_aplicado(angulo_depois) - angulo_aplicado(angulo_antes)
    if abs(giro) < 1e-9:
        return recorte
    from core.zonas_na_folha import _giro_em_fracao

    x, y, w, h = recorte
    cantos = np.array([[x, y, 1.0], [x + w, y, 1.0], [x + w, y + h, 1.0], [x, y + h, 1.0]]).T
    # da pagina reta antiga para a nova: desfaz o giro antigo e faz o novo,
    # em volta do centro da pagina inteira (o mesmo do rotacionar)
    m = (_giro_em_fracao(angulo_aplicado(angulo_depois), proporcao)
         @ np.linalg.inv(_giro_em_fracao(angulo_aplicado(angulo_antes), proporcao)))
    q = m @ cantos
    x0, y0 = max(0.0, float(q[0].min())), max(0.0, float(q[1].min()))
    x1, y1 = min(1.0, float(q[0].max())), min(1.0, float(q[1].max()))
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------------------
# Previa = PDF: o corte e o angulo automaticos sao calculados UMA vez por
# pagina, na folha desenhada na resolucao do PDF (projeto.qualidade_dpi), e
# guardados. Antes, a previa (110 DPI na "rapida", 180 na "media") e o PDF
# (300 DPI) calculavam cada um na sua imagem, e a conta do corte tem limiares
# (80% de coluna escura, 0,2% de tinta descartada, fechamento de 5 x 5
# pontos) que caem de um lado numa imagem e do outro na outra: ate 8% de
# diferenca no Palatino 5 - o Kaique via um corte na tela e recebia outro no
# PDF (Lista de bugs, 28/09/2026).
#
# Por que a resolucao do PDF, e nao uma imagem menor e mais rapida: qualquer
# outra imagem muda o corte de algumas paginas, e para pior (medido em 28/09
# com 1600, 2000, 2400 e 3200 pontos de altura: a barra da moldura do
# Palatino 66 saia cortada, a pauta do Graduale 222 tambem). O corte do PDF
# e o que foi conferido; a previa passa a mostrar ele.
#
# Guardado so na memoria, nesta sessao do programa (nada muda no arquivo do
# projeto). A chave leva o arquivo (caminho, data, tamanho) e tudo de que o
# corte depende. Quem enche: processar (de graca, a imagem ja esta na
# resolucao do PDF) e renderizar_pagina (a previa, num fio de fundo). Quem so
# le: preparar_metade.
# ---------------------------------------------------------------------------

_GEOMETRIAS: "OrderedDict[tuple, tuple]" = OrderedDict()
_TRANCA_GEOMETRIAS = threading.Lock()
MAX_GEOMETRIAS = 4096


def _arquivo_do_projeto(projeto: Projeto):
    """(caminho normalizado, os.stat) do PDF do projeto, ou None se ele nao
    existe. Separado de _chave_da_geometria so para quem faz a chave de
    muitas paginas de uma vez (item 2.5, tamanho_do_livro) consultar o disco
    uma vez so."""
    try:
        # normcase: o mesmo PDF escrito com `\` ou `/`, ou com maiusculas
        # diferentes, da a mesma chave (bug de 29/09, projetos.mesmo_arquivo).
        caminho = os.path.normcase(os.path.abspath(projeto.caminho_entrada))
        return caminho, os.stat(caminho)
    except (OSError, TypeError, ValueError):
        return None


def _chave_da_geometria(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto,
                        arquivo=False):
    """Tudo de que o corte e o angulo dependem. None se o arquivo do projeto
    nao existe (projeto de teste, arquivo movido) - ai nada e guardado.
    arquivo: o _arquivo_do_projeto ja consultado (False = consulta aqui)."""
    if arquivo is False:
        arquivo = _arquivo_do_projeto(projeto)
    if arquivo is None:
        return None
    caminho, info = arquivo
    # obra 26/10, etapa 1: o corte e o angulo a mao que VALEM nesta pagina
    # (core/etapas; com a caixinha ligada, os gravados, como sempre)
    recorte_a_mao = etapas.recorte_a_mao(projeto, pagina)
    recorte = None if recorte_a_mao is None else tuple(round(float(v), 6) for v in recorte_a_mao)
    dividir = bool(folha.dividir) and pagina.metade != METADE_INTEIRA
    return (
        caminho, info.st_mtime_ns, info.st_size, int(projeto.qualidade_dpi),
        folha.indice, int(folha.rotacao) % 360,
        dividir, round(float(folha.posicao_corte), 6) if dividir else None,
        pagina.metade if dividir else None, bool(projeto.cortar_bordas),
        bool(projeto.endireitar), recorte, etapas.angulo_a_mao(projeto, pagina),
        faixa_da_sobra(folha, pagina, projeto),        # item 2.1
        endireitar_scantailor.jeito_da_pagina(projeto, pagina),   # item 2.2
        ordem_do_livro(projeto),                       # item 2.2, G6
        bool(getattr(projeto, "cortar_pelo_conteudo", False)),   # item 2.5
        (borda_preta.jeito_valido(getattr(projeto, "borda_preta_ate", None))   # item 2.13
         if getattr(projeto, "borda_preta", False) else None),
        (borda_preta.fazer_valido(getattr(projeto, "borda_preta_fazer", None))   # item 2.14
         if getattr(projeto, "borda_preta", False) else None),
    )


def _geometria_guardada(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto):
    """O (recorte, angulo) ja guardado para esta pagina, ou None."""
    chave = _chave_da_geometria(folha, pagina, projeto)
    if chave is None:
        return None
    with _TRANCA_GEOMETRIAS:
        geometria = _GEOMETRIAS.get(chave)
        if geometria is not None:
            _GEOMETRIAS.move_to_end(chave)
        return geometria


def _guardar_geometria(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto,
                       img_folha_do_pdf: np.ndarray, doc=None) -> None:
    """Calcula e guarda o (recorte, angulo) da pagina, a partir da folha JA
    desenhada na resolucao do PDF (projeto.qualidade_dpi). Arriscado: passar
    aqui uma imagem de outra resolucao guardaria um corte diferente do PDF.

    Item 2.2: guarda tambem as duas contas do angulo automatico
    (_ANGULOS_MEDIDOS, para a aba Endireitar) e poe ou tira o aviso C1
    (_anotar_contas_discordam): e a medida que vale, na resolucao do PDF.
    doc: o PDF aberto, so para o DPI do escaneamento dito ao ScanTailor
    (_dpi_do_scan); None = nao se sabe (a conta do limpar pontinhos supoe)."""
    chave = _chave_da_geometria(folha, pagina, projeto)
    if chave is None:
        return
    with _TRANCA_GEOMETRIAS:
        if chave in _GEOMETRIAS:
            return
    dpi_do_scan = (_dpi_do_scan(doc, folha)
                   if doc is not None and (_usa_o_endireitar_do_scantailor(projeto, pagina)
                                           or _corte_sugerido(projeto, pagina)) else None)
    medidas: dict = {}
    extras: dict = {}                                     # etapa 10a
    geometria = _geometria(preparar_para_recorte(img_folha_do_pdf, folha, pagina, projeto), pagina, projeto,
                           dpi=projeto.qualidade_dpi, dpi_do_scan=dpi_do_scan, medidas=medidas,
                           extras=extras)
    conteudo = medidas.pop("conteudo", None)              # item 2.5
    encostou = extras.get("encostou")
    with _TRANCA_GEOMETRIAS:
        _GEOMETRIAS[chave] = geometria
        while len(_GEOMETRIAS) > MAX_GEOMETRIAS:
            _GEOMETRIAS.popitem(last=False)
        if conteudo is not None:
            _guardar_o_conteudo(chave, conteudo)
        if medidas:
            _ANGULOS_MEDIDOS[chave] = dict(medidas)
            while len(_ANGULOS_MEDIDOS) > MAX_GEOMETRIAS:
                _ANGULOS_MEDIDOS.popitem(last=False)
    _anotar_contas_discordam(pagina, bool(medidas.get("discordam")))
    if encostou is not None:
        _anotar_corte_encostou(folha, encostou)


def _anotar_corte_encostou(folha: ConfigFolha, encostou: bool) -> None:
    """Obra 26/10, etapa 10a (D-104, Lista de bugs 22/10: o aviso "Corte
    encostou no texto quase nunca toca: e medido uma vez, na folha inteira,
    antes de dividir e endireitar, nao no corte de verdade"). No livro novo a
    medida do corte na pagina reta poe o aviso na folha; tira so da folha nao
    dividida (na dividida, a outra metade pode ter encostado). Arriscado:
    tirar o aviso da folha dividida por uma metade so."""
    alertas = getattr(folha, "alertas", None)
    if alertas is None:
        return
    tem = analise.CORTE_PEGOU_CONTEUDO in alertas
    if encostou and not tem:
        alertas.append(analise.CORTE_PEGOU_CONTEUDO)
        folha.revisada = False
    elif not encostou and tem and not folha.dividir:
        folha.alertas = [a for a in alertas if a != analise.CORTE_PEGOU_CONTEUDO]


# Item 2.2: as duas contas do angulo automatico de cada pagina (ver
# _angulo_automatico), na mesma chave de _GEOMETRIAS - e o que a aba
# Endireitar mostra (angulos_medidos). Seguro esvaziar a qualquer hora (a
# proxima previa mede de novo).
_ANGULOS_MEDIDOS: "OrderedDict[tuple, dict]" = OrderedDict()


def angulos_medidos(projeto: Projeto, pagina: ConfigPagina) -> dict | None:
    """As duas contas do angulo automatico desta pagina, como medidas na
    resolucao do PDF: {"programa": graus, "scantailor": graus ou None,
    "jeito": a conta que valeu, "discordam": bool}. None quando ainda nao foi
    medida nesta sessao (a previa mede) ou quando o angulo e a mao."""
    if not 0 <= pagina.folha < len(projeto.folhas):
        return None
    chave = _chave_da_geometria(projeto.folhas[pagina.folha], pagina, projeto)
    if chave is None:
        return None
    with _TRANCA_GEOMETRIAS:
        medidas = _ANGULOS_MEDIDOS.get(chave)
        return None if medidas is None else dict(medidas)


def angulo_da_pagina(projeto: Projeto, pagina: ConfigPagina) -> float | None:
    """O angulo que vale nesta pagina agora, em graus (sentido do OpenCV):
    0 com o endireitar desligado, o a mao (ConfigPagina.angulo_manual), ou o
    automatico ja medido nesta sessao (_GEOMETRIAS). None quando o automatico
    ainda nao foi medido (a previa mede). Item 2.2 (G5): e o numero da aba
    Endireitar e a base dos ajustes a mao (setas, alca, linha-guia). Abaixo
    de ANGULO_MINIMO a pagina nao gira (angulo_aplicado).

    Obra 26/10, etapa 1 (D-009): o angulo a mao vale com o endireitar
    desligado tambem (core/etapas.angulo_a_mao); sem ele e com a caixinha
    desligada, 0."""
    angulo_a_mao = etapas.angulo_a_mao(projeto, pagina)
    if angulo_a_mao is not None:
        return float(angulo_a_mao)
    if not etapas.endireita_sozinho(projeto):
        return 0.0
    if not 0 <= pagina.folha < len(projeto.folhas):
        return None
    geometria = _geometria_guardada(projeto.folhas[pagina.folha], pagina, projeto)
    return None if geometria is None else float(geometria[1])


def angulo_aplicado(angulo: float | None) -> float:
    """O giro que a pagina desenhada MESMO tem com este angulo: a regra de
    _preparar_metade_e_geometria (abaixo de ANGULO_MINIMO nao gira)."""
    if angulo is None or abs(float(angulo)) < ANGULO_MINIMO:
        return 0.0
    return float(angulo)


def _usa_o_endireitar_do_scantailor(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A conta do ScanTailor entra nesta pagina (a dela ou a do livro, para o
    C1)? So com o endireitar ligado e o angulo automatico."""
    es = endireitar_scantailor
    return (etapas.endireita_sozinho(projeto) and etapas.angulo_a_mao(projeto, pagina) is None
            and es.JEITO_SCANTAILOR in (es.jeito_da_pagina(projeto, pagina), es.jeito_do_livro(projeto)))


def _angulo_que_valeu(medidas: dict, reserva: float | None) -> float | None:
    """Item 2.15: o angulo automatico que valeu na pagina (a conta de
    _angulo_automatico), ou `reserva` quando nada foi medido."""
    angulo = medidas.get("scantailor") if medidas.get("jeito") == endireitar_scantailor.JEITO_SCANTAILOR         else medidas.get("programa")
    return reserva if angulo is None else float(angulo)


def marcar_paginas_diferentes(paginas: list[ConfigPagina], angulos: list[float | None]) -> None:
    """Item 2.15 (igual ao ScanTailor, core/paginas_diferentes.py): poe o aviso
    analise.ANGULO_DIFERENTE_DAS_OUTRAS nas paginas cujo angulo se afasta das
    outras (coeficiente e limite de fabrica do ScanTailor) E a pelo menos
    AFASTAMENTO_MINIMO_DO_ANGULO da media (decisao da gerente, 20-21/10). `angulos` na
    ordem de `paginas`; None = sem numero (endireitar desligado: nenhuma
    pagina e marcada). So poe: quem chama e a analise, com as paginas novas."""
    from core import paginas_diferentes

    if not paginas_diferentes.DESTACAR_DE_FABRICA or len(angulos) != len(paginas):
        return
    for pagina, diferente in zip(paginas, paginas_diferentes.diferentes_e_longe(
            angulos, paginas_diferentes.ENDIREITAR,
            paginas_diferentes.AFASTAMENTO_MINIMO_DO_ANGULO)):
        if diferente and analise.ANGULO_DIFERENTE_DAS_OUTRAS not in pagina.alertas:
            pagina.alertas.append(analise.ANGULO_DIFERENTE_DAS_OUTRAS)


def _anotar_contas_discordam(pagina: ConfigPagina, discordam: bool) -> None:
    """Poe ou tira o aviso C1 (analise.CONTAS_DO_ENDIREITAR_DISCORDAM), do
    mesmo jeito que _por_avisos_do_so_as_letras: ao POR, a pagina volta a "nao
    conferida"; o "esta bom assim" depois disso continua valendo."""
    codigo = analise.CONTAS_DO_ENDIREITAR_DISCORDAM
    tem = codigo in pagina.alertas
    if discordam and not tem:
        pagina.alertas.insert(0, codigo)
        pagina.revisada = False
    elif not discordam and tem:
        pagina.alertas = [a for a in pagina.alertas if a != codigo]


def acertar_alerta_do_endireitar(projeto: Projeto, pagina: ConfigPagina) -> None:
    """Tira o aviso C1 da pagina onde ele nao vale mais (angulo a mao,
    endireitar desligado, livro na conta do programa), sem desenhar nada.
    Onde ainda pode valer, fica como esta (a previa acerta)."""
    es = endireitar_scantailor
    if analise.CONTAS_DO_ENDIREITAR_DISCORDAM not in pagina.alertas:
        return
    if (not projeto.endireitar or pagina.angulo_manual is not None
            or es.jeito_do_livro(projeto) != es.JEITO_SCANTAILOR):
        _anotar_contas_discordam(pagina, False)


# ---------------------------------------------------------------------------
# Item 2.5: o corte que segue o conteudo, como o ScanTailor (decisoes G8 e G9
# de 05/10/2026, g8-moldura-tinta-fora e g9-pagina-muito-maior de 13/10; as
# contas estao em core/corte_pelo_conteudo.py). SO com o livro em
# Projeto.cortar_pelo_conteudo (desligado de fabrica): desligado, nada aqui e
# chamado e o livro sai identico (tests/test_corte_pelo_conteudo_no_programa.py).
#
# Como funciona:
#   1. _geometria mede a caixa do conteudo da pagina (na pagina reta, no
#      livro novo; na pagina torta, no projeto antigo, onde o giro vem depois)
#      e o corte guardado em _GEOMETRIAS passa a ser o "proprio" (a caixa + 1
#      mm). _guardar_geometria guarda a medida em _CONTEUDOS e o tamanho do
#      conteudo em _TAMANHOS (os dois na mesma chave de _GEOMETRIAS).
#   2. tamanho_do_livro: a conta do ScanTailor (o maior conteudo do livro),
#      com as paginas ja medidas nesta sessao; a muito maior fica de fora.
#   3. _corte_do_livro (chamado por _preparar_metade_e_geometria, isto e, na
#      previa e no PDF): alarga o corte proprio ate o tamanho do livro e poe ou
#      tira os dois avisos (CORTE_DEIXOU_TINTA_FORA, PAGINA_MUITO_MAIOR).
#   4. processar mede antes, numa passada, as paginas ainda nao medidas
#      (medir_conteudo_do_livro), para o tamanho do livro ser o mesmo da
#      primeira a ultima pagina do PDF. A tela pode chamar a mesma passada por
#      tras, ao abrir o livro.
# Guardado so na memoria, nesta sessao (como _GEOMETRIAS): nada muda no
# arquivo do projeto alem dos dois campos novos (Projeto.cortar_pelo_conteudo
# e ConfigPagina.alinhar_com_as_outras). Seguro esvaziar a qualquer hora (a
# proxima previa e a passada medem de novo).
# ---------------------------------------------------------------------------

_CONTEUDOS: "OrderedDict[tuple, ConteudoMedido]" = OrderedDict()
_TAMANHOS: "OrderedDict[tuple, tuple | None]" = OrderedDict()
# Ate 21/10/2026 a passada media numa imagem de 150 DPI (metade do tempo);
# agora mede na mesma resolucao da geracao (projeto.qualidade_dpi): a conta
# do ScanTailor da caixas diferentes em resolucoes diferentes, e o tamanho do
# livro mudava (verificador, Egenloff 1-14). Fica o nome, sem uso no codigo.
DPI_DA_PASSADA = 150


@dataclass(frozen=True)
class ConteudoMedido:
    """O que _geometria mediu do conteudo de uma pagina (item 2.5): a medida
    do ScanTailor, as pecas de tinta do corte comum (em fracao da pagina
    medida; para a folga do giro na ordem antiga) e as candidatas ao "ficou
    de fora" (corte_pelo_conteudo.candidatas, medidas no corte proprio)."""

    medida: "corte_pelo_conteudo.MedidaDoConteudo"
    pecas: np.ndarray | None
    candidatas: tuple
    # item 2.13, "so o preto" sem o 2.5: o corte e a propria pagina achada
    # (medida.limite), sem apertar no conteudo
    so_o_limite: bool = False

    def recorte_proprio(self) -> tuple[float, float, float, float] | None:
        """O corte da pagina sozinha, em fracao; None = fica o corte comum.
        Segue o conteudo (caixa + 1 mm, sem passar da pagina): o 2.5 e o
        "ate a moldura". "So o preto" sozinho: a pagina sem a faixa preta
        (sem faixa preta nenhuma, None: o corte comum, como hoje). Sem caixa
        (pagina em branco) mas com a pagina achada: a pagina."""
        m = self.medida
        inteira = (0.0, 0.0, float(m.largura), float(m.altura))
        if self.so_o_limite:
            if m.limite is None or tuple(m.limite) == inteira:
                return None
            return corte_pelo_conteudo.em_fracao(m.limite, m.largura, m.altura)
        caixa = corte_pelo_conteudo.caixa_do_corte(m)
        if caixa is None:
            if m.limite is not None and tuple(m.limite) != inteira:
                return corte_pelo_conteudo.em_fracao(m.limite, m.largura, m.altura)
            return None
        return corte_pelo_conteudo.em_fracao(caixa, m.largura, m.altura)


def _corta_pelo_conteudo(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """Esta pagina usa o corte do conteudo? So com o livro ligado, o cortar
    ligado e o corte automatico (o corte a mao vale como esta)."""
    return bool(getattr(projeto, "cortar_pelo_conteudo", False) and projeto.cortar_bordas
                and pagina.recorte is None)


def _corta_pela_borda(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """Item 2.13: esta pagina usa o corte sugerido pela borda preta? So com o
    livro ligado (Projeto.borda_preta, desligado de fabrica), o cortar ligado
    e o corte automatico (o corte a mao e a excecao por pagina)."""
    return bool(getattr(projeto, "borda_preta", False) and projeto.cortar_bordas
                and pagina.recorte is None)


def _jeito_da_borda(projeto: Projeto) -> str | None:
    """"ate_a_moldura", "so_o_preto" ou None (borda preta desligada)."""
    if not getattr(projeto, "borda_preta", False):
        return None
    return borda_preta.jeito_valido(getattr(projeto, "borda_preta_ate", None))


def _so_pinta(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """Item 2.14: a borda desta pagina e PINTADA de branco em vez de cortada,
    e o corte fica o de sempre (o 2.5, se ligado junto, continua mandando no
    corte)."""
    return bool(_corta_pela_borda(projeto, pagina)
                and borda_preta.fazer_valido(getattr(projeto, "borda_preta_fazer", None))
                == borda_preta.PINTAR)


def _troca_o_corte(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """O corte automatico desta pagina e trocado pelo medido (2.5, ou 2.13
    cortando fora)? Pintando (2.14) sem o 2.5, o corte fica o comum."""
    return _corta_pelo_conteudo(projeto, pagina) or (
        _corta_pela_borda(projeto, pagina) and not _so_pinta(projeto, pagina))


def _corte_sugerido(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """O corte automatico desta pagina e um dos novos (2.5 ou 2.13)?"""
    return _corta_pelo_conteudo(projeto, pagina) or _corta_pela_borda(projeto, pagina)


def _segue_o_conteudo(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """O corte desta pagina segue o impresso (2.5, ou 2.13 "ate a moldura")?
    So ai vale o aviso do que ficou de fora (g8)."""
    return _corta_pelo_conteudo(projeto, pagina) or (
        _corta_pela_borda(projeto, pagina) and _jeito_da_borda(projeto) == borda_preta.ATE_A_MOLDURA)


def _medida_da_pagina(img: np.ndarray, dpi: float | None, dpi_do_scan: float | None,
                      projeto: Projeto, com_a_cunha_preta: np.ndarray | None = None):
    """(medida, so_o_limite) de `img` conforme as opcoes do livro:
    - 2.13 "so o preto": a pagina sem a faixa preta (borda_preta.so_o_preto)
      vira o limite; com o 2.5 junto, o conteudo e procurado dentro dele;
      sozinho, o corte e o proprio limite (so_o_limite);
    - 2.13 "ate a moldura": a mesma pagina do "so o preto" vira o limite e o
      conteudo e procurado dentro dela (ContentBoxFinder do ScanTailor). Era a
      busca da pagina do ScanTailor (PageFinder) ate 20/10/2026; trocada
      porque no Pesel 21 (cartao marrom escuro em volta da gravura) ela
      cortava o cartao, o titulo e a legenda, e nas cinco paginas que o
      Samuel escolheu como alvo da borda preta (Antiphon 260 e 88, Camoes
      104, Cursus 3, Matematica 32) a caixa do conteudo dava o mesmo com e
      sem ela (relatorios/caixa-conteudo-impl/parte2-*.md);
    - so o 2.5: o conteudo na imagem inteira (a busca da pagina desligada).
    com_a_cunha_preta: a mesma pagina COLORIDA (a cor e o que separa o fundo
    do scanner, cinza neutro, de um cartao ou capa escura; core/borda_preta)
    e, no livro novo com a pagina girada, com a cunha das beiradas PRETA em
    vez de branca: so para as contas da borda preta. Achado olhando o Righetti 55 (20/10/2026): com a cunha branca, o
    "so o preto" parava na primeira linha (a cunha e clara) e nao tirava
    nada. A cunha fica fora da folha escaneada, entao trata-la como fundo do
    scanner e o certo. O 2.5 sozinho continua na pagina de sempre."""
    jeito = _jeito_da_borda(projeto)
    if jeito is not None and com_a_cunha_preta is not None:
        img = com_a_cunha_preta
    com_o_conteudo = bool(getattr(projeto, "cortar_pelo_conteudo", False))
    if jeito is not None:
        limite = borda_preta.so_o_preto(img)
        if jeito == borda_preta.ATE_A_MOLDURA or com_o_conteudo:
            return corte_pelo_conteudo.medir(img, dpi, dpi_do_scan, limite=limite), False
        altura, largura = img.shape[:2]
        return corte_pelo_conteudo.MedidaDoConteudo(largura, altura, None, None, None,
                                                    "so o preto", limite), True
    return corte_pelo_conteudo.medir(img, dpi, dpi_do_scan), False


# Obra de 26/10/2026, etapa 10a: a caixa do conteudo do ScanTailor (corte que
# segue o impresso: borda preta "ate a moldura", item 2.13, e o 2.5) nao pode
# comer a pagina (D-077, 28/09: "nao comer conteudo"; D-104, 22/10: os lugares
# que comem a pagina sem a gente querer). Achado nas paginas do teste dos 14
# livros (23/10), pelo projeto salvo de cada livro:
#   - folha quase em branco: a caixa abraca o pouco que ha e a pagina vira uma
#     tira. ljs47 2 (guarda com a etiqueta da biblioteca): 21 x 11 cm, "so com
#     a etiqueta"; Siebmacher 74 (folha so com o decalque claro): 2,6 x 8,6 cm.
#     Conserto: quando o corte comum ja achou que nao ha o que cortar (capa,
#     guarda, pagina em branco: pecas None) ou a caixa cobre menos que
#     CAIXA_QUASE_VAZIA da pagina achada, a pagina fica a pagina achada (o
#     "so o preto"), sem apertar no impresso. So no "ate a moldura" sem o 2.5
#     (com o 2.5 a pagina vazia ganha o tamanho do livro, aprovado em 21/10).
#   - a borda da caixa passando no meio de uma peca de tinta (letra, numero,
#     barra de moldura): a borda anda ate o fim da peca, com o mesmo limite do
#     corte comum (recortar.ESTICAR_NO_MAXIMO, 2% do lado) e as mesmas regras
#     de quem empurra (risco comprido e fino so empurra a borda paralela). A
#     peca INTEIRA de fora continua fora, com o aviso "Corte deixou algo de
#     fora" (D-098, 13/10: "Só avisa").
# Arriscado: subir CAIXA_QUASE_VAZIA (pagina de rosto com pouco texto deixa de
# seguir o impresso); tirar o limite de esticar (o risco tracejado da beirada
# arrasta o corte, como no corte comum).
CAIXA_QUASE_VAZIA = 0.20


def _caixa_sem_comer(medida: "corte_pelo_conteudo.MedidaDoConteudo", pecas,
                     projeto: Projeto, comum: Recorte | None = None,
                     img: np.ndarray | None = None, em_branco: bool = False
                     ) -> "corte_pelo_conteudo.MedidaDoConteudo":
    """A medida do ScanTailor com as duas protecoes acima. `pecas`: as do corte
    comum na MESMA imagem (recortar.Recorte.pecas, em fracao; None quando o
    corte comum nao achou o que cortar). `comum`: o proprio corte comum (o
    limite da pagina quase em branco; None = so a pagina achada). `img`: a
    imagem medida (para tirar a faixa escura da beirada da pagina quase em
    branco; None = nao tira). `em_branco`: a analise achou a pagina quase sem
    tinta forte no miolo (aviso analise.EM_BRANCO; Antiphon 2, guarda manchada:
    a caixa do ScanTailor abracava as manchas e cortava o numero "19" e o
    carimbo). Sem caixa, devolve como esta."""
    from dataclasses import replace

    if not medida.tem_conteudo or not medida.largura or not medida.altura:
        return medida
    larg, alt = float(medida.largura), float(medida.altura)
    lx0, ly0, lx1, ly1 = medida.limite or (0.0, 0.0, larg, alt)
    x0, y0, x1, y1 = medida.caixa
    so_a_moldura = (_jeito_da_borda(projeto) == borda_preta.ATE_A_MOLDURA
                    and not getattr(projeto, "cortar_pelo_conteudo", False))
    if so_a_moldura:
        area_pagina = max(1.0, (lx1 - lx0) * (ly1 - ly0))
        if (pecas is None or em_branco
                or (x1 - x0) * (y1 - y0) / area_pagina < CAIXA_QUASE_VAZIA):
            # a pagina achada, dentro do corte comum (que, na folha sem o que
            # recortar, ja tira a faixa escura da beirada: recortar.beiradas_escuras)
            if comum is not None:
                cx, cy, cw, ch = comum.tupla
                c0, c1 = max(lx0, cx * larg), min(lx1, (cx + cw) * larg)
                d0, d1 = max(ly0, cy * alt), min(ly1, (cy + ch) * alt)
                # so se o corte comum nao for ele mesmo a tira (folha limpa so
                # com uma etiqueta: o comum aperta nela)
                if c1 - c0 >= 8 and d1 - d0 >= 8 and (c1 - c0) * (d1 - d0) >= 0.5 * area_pagina:
                    lx0, lx1, ly0, ly1 = c0, c1, d0, d1
            # e sem a faixa escura colada na beirada da pagina achada (a
            # lombada do Siebmacher 74, que a conta do "so o preto" deixa)
            if img is not None:
                pedaco = img[int(ly0):int(ly1), int(lx0):int(lx1)]
                sem_faixa = recortar.beiradas_escuras(pedaco) if pedaco.size else None
                if sem_faixa is not None:
                    fx, fy, fw, fh = sem_faixa.tupla
                    w, h = lx1 - lx0, ly1 - ly0
                    lx0, ly0, lx1, ly1 = (lx0 + fx * w, ly0 + fy * h,
                                          lx0 + (fx + fw) * w, ly0 + (fy + fh) * h)
            return replace(medida, caixa=None, tamanho_mm=None, limite=(lx0, ly0, lx1, ly1),
                           motivo="quase em branco: fica a pagina achada")
    if pecas is None or len(pecas) == 0:
        return medida
    p = np.asarray(pecas, dtype=np.float64)
    em_pontos = np.hstack([p[:, :4] * np.array([larg, alt, larg, alt]), p[:, 4:5]])
    # as pecas vem da mascara reduzida (recortar.ALTURA_ANALISE pontos de
    # altura): cada beirada delas erra ate 1,5 ponto de la. Encolhidas disso,
    # a caixa do ScanTailor rente a peca nao conta como "partindo" a peca.
    tol = 1.5 * alt / recortar.ALTURA_ANALISE
    em_pontos[:, 0:2] += tol
    em_pontos[:, 2:4] -= tol
    respeitar, pode_x, pode_y = recortar._quem_empurra(em_pontos, larg, alt)
    n0, m0, n1, m1 = recortar._nao_partir_pecas(
        respeitar, x0, y0, x1, y1, larg * recortar.ESTICAR_NO_MAXIMO,
        alt * recortar.ESTICAR_NO_MAXIMO, pode_x, pode_y)
    n0, m0 = max(lx0, float(n0)), max(ly0, float(m0))
    n1, m1 = min(lx1, float(n1)), min(ly1, float(m1))
    if (n0, m0, n1, m1) == (x0, y0, x1, y1):
        return medida
    mx, my = medida.mm_por_ponto
    return replace(medida, caixa=(n0, m0, n1, m1), tamanho_mm=((n1 - n0) * mx, (m1 - m0) * my))


def _medir_o_conteudo(img: np.ndarray, dpi: float | None, dpi_do_scan: float | None,
                      pecas, projeto: Projeto | None = None,
                      com_a_cunha_preta: np.ndarray | None = None,
                      comum: Recorte | None = None, em_branco: bool = False) -> ConteudoMedido:
    """A medida do conteudo de `img` (a pagina onde o corte vai ser feito) e as
    candidatas ao "ficou de fora". Nunca levanta excecao (sem a DLL: sem
    caixa, e quem chama fica com o corte comum). Sem `projeto`: so o 2.5."""
    if projeto is None:
        medida, so_o_limite = corte_pelo_conteudo.medir(img, dpi, dpi_do_scan), False
    else:
        medida, so_o_limite = _medida_da_pagina(img, dpi, dpi_do_scan, projeto, com_a_cunha_preta)
        if not so_o_limite:
            medida = _caixa_sem_comer(medida, pecas, projeto, comum, img, em_branco)
    candidatas: tuple = ()
    caixa = None if so_o_limite else corte_pelo_conteudo.caixa_do_corte(medida)
    if caixa is not None and pecas is not None and len(pecas):
        cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        candidatas = tuple(corte_pelo_conteudo.candidatas(caixa, pecas, cinza, medida.mm_por_ponto))
    return ConteudoMedido(medida, None if pecas is None else np.asarray(pecas), candidatas,
                          so_o_limite)


def _guardar_o_conteudo(chave: tuple, conteudo: ConteudoMedido) -> None:
    """Guarda a medida e o tamanho (chamar com _TRANCA_GEOMETRIAS presa)."""
    _CONTEUDOS[chave] = conteudo
    # O tamanho de uma pagina ja medido (pela passada, medir_conteudo_do_livro)
    # NAO e trocado: conserto de 21/10/2026 (Egenloff 1-14 a 300 DPI, achado do
    # verificador). A passada mede a DPI_DA_PASSADA e a geometria a 300; a
    # conta do ScanTailor decide a beirada um pouco diferente em cada uma
    # (Egenloff 5: 380 x 358 mm), e a medida nova mudava o tamanho do livro no
    # meio da geracao (paginas 3 e 4 com 382 mm, as outras 360). Arriscado:
    # voltar a sobrescrever.
    _TAMANHOS.setdefault(chave, conteudo.medida.tamanho_mm
                         if conteudo.medida.tem_conteudo and not conteudo.so_o_limite else None)
    for guardados in (_CONTEUDOS, _TAMANHOS):
        while len(guardados) > MAX_GEOMETRIAS:
            guardados.popitem(last=False)


def _paginas_do_corte_do_livro(projeto: Projeto) -> list[ConfigPagina]:
    """As paginas que entram na conta do tamanho do livro: as que vao para o
    PDF, com o corte automatico."""
    return [p for p in projeto.paginas_ativas
            if p.recorte is None and 0 <= p.folha < len(projeto.folhas)]


def tamanho_do_livro(projeto: Projeto) -> "corte_pelo_conteudo.TamanhoDoLivro | None":
    """O tamanho do livro (G9, a conta do ScanTailor) com as paginas ja
    medidas nesta sessao; None com a opcao desligada ou sem medida. A pagina
    muito maior fica de fora sozinha (g9), menos a que o Kaique pos de volta
    (ConfigPagina.alinhar_com_as_outras True); a que ele tirou (False) nunca
    entra."""
    if not getattr(projeto, "cortar_pelo_conteudo", False) or not projeto.cortar_bordas:
        return None
    tamanhos, dentro, fora = {}, [], []
    arquivo = _arquivo_do_projeto(projeto)
    for pagina in _paginas_do_corte_do_livro(projeto):
        chave = _chave_da_geometria(projeto.folhas[pagina.folha], pagina, projeto, arquivo)
        if chave is None:
            continue
        with _TRANCA_GEOMETRIAS:
            if chave not in _TAMANHOS:
                continue
            tamanhos[pagina.indice] = _TAMANHOS[chave]
        alinhar = getattr(pagina, "alinhar_com_as_outras", None)
        if alinhar is True:
            dentro.append(pagina.indice)
        elif alinhar is False:
            fora.append(pagina.indice)
    return corte_pelo_conteudo.tamanho_do_livro(tamanhos, sempre_dentro=dentro, sempre_fora=fora)


def _anotar(pagina: ConfigPagina, codigo: str, tem: bool) -> None:
    """Poe ou tira um aviso, do jeito de _anotar_contas_discordam: ao POR, a
    pagina volta a "nao conferida"."""
    esta = codigo in pagina.alertas
    if tem and not esta:
        pagina.alertas.insert(0, codigo)
        pagina.revisada = False
    elif not tem and esta:
        pagina.alertas = [a for a in pagina.alertas if a != codigo]


def _caixa_do_livro(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto):
    """(ConteudoMedido, caixa do corte do livro em pontos, livro) desta pagina,
    ou None quando ela nao usa o corte que segue o conteudo (2.5, ou 2.13
    "ate a moldura") ou ainda nao foi medida. Sem o 2.5, livro e None (sem
    tamanho do livro: so a pagina)."""
    if not _segue_o_conteudo(projeto, pagina):
        return None
    chave = _chave_da_geometria(folha, pagina, projeto)
    if chave is None:
        return None
    with _TRANCA_GEOMETRIAS:
        medido = _CONTEUDOS.get(chave)
    if medido is None or medido.so_o_limite or not medido.medida.disponivel:
        return None
    livro = tamanho_do_livro(projeto) if _corta_pelo_conteudo(projeto, pagina) else None
    alinhar = getattr(pagina, "alinhar_com_as_outras", None)
    if not medido.medida.tem_conteudo:
        # Pagina sem conteudo (verso em branco, so um carimbo claro): do
        # tamanho do livro, no meio da pagina, como o ScanTailor
        # (page_layout/Utils.cpp, adaptContentRect: conteudo vazio vira um
        # ponto no centro). Sem o livro (2.5 desligado): o corte comum.
        # Conserto de 21/10/2026 (Egenloff 1-14: os versos em branco saiam
        # maiores que as outras paginas).
        if livro is None or alinhar is False:
            return None
        caixa = corte_pelo_conteudo.caixa_vazia(medido.medida, livro)
        return (medido, caixa, livro) if caixa is not None else None
    # A pagina "muito maior" (g9) fica fora da CONTA do tamanho, mas nunca sai
    # MENOR que o livro: caixa_do_corte so alarga, entao ela cresce ate o livro
    # no lado em que e menor e fica do tamanho dela no lado em que e maior.
    # Conserto de 21/10/2026 (verificador, Egenloff pagina 6: o bloco de texto
    # era mais largo que os enfeites das outras, ela ficava fora da conta e
    # saia uma tira de 253 x 139 mm). So a que o Kaique tirou da conta
    # (alinhar_com_as_outras False) sai do tamanho dela, como no ScanTailor.
    sozinha = livro is None or alinhar is False
    caixa = corte_pelo_conteudo.caixa_do_corte(medido.medida, None if sozinha else livro)
    if caixa is not None and not sozinha:
        # o corte do tamanho do livro nao parte uma peca impressa ao meio
        # (conserto de 21/10/2026, Egenloff 3 com as duas opcoes)
        caixa = corte_pelo_conteudo.sem_partir(
            caixa, medido.candidatas, corte_pelo_conteudo.caixa_do_corte(medido.medida), medido.medida)
    return medido, caixa, livro


def _corte_do_livro(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto,
                    recorte, angulo: float, inteira: np.ndarray):
    """O corte que vale nesta pagina (chamado por _preparar_metade_e_geometria
    com o corte da geometria). Fora do item 2.5, devolve `recorte` como esta
    e so tira os avisos dele, se sobraram (opcao desligada, corte a mao).
    Com o item 2.5 e a pagina medida: o corte do tamanho do livro, com a folga
    do giro na ordem antiga (como o corte comum), e poe ou tira os avisos."""
    achado = _caixa_do_livro(folha, pagina, projeto)
    if achado is None:
        if pagina.alertas and not _segue_o_conteudo(projeto, pagina):
            _anotar(pagina, analise.CORTE_DEIXOU_TINTA_FORA, False)
            _anotar(pagina, analise.PAGINA_MUITO_MAIOR, False)
        return recorte
    medido, caixa, livro = achado
    _anotar(pagina, analise.CORTE_DEIXOU_TINTA_FORA,
            bool(corte_pelo_conteudo.tiradas_do_corte(caixa, medido.candidatas)))
    _anotar(pagina, analise.PAGINA_MUITO_MAIOR,
            bool(livro is not None and pagina.indice in livro.muito_maiores
                 and getattr(pagina, "alinhar_com_as_outras", None) is not True))
    if not _troca_o_corte(projeto, pagina):
        return recorte                      # item 2.14: pinta, nao corta
    final = corte_pelo_conteudo.em_fracao(caixa, medido.medida.largura, medido.medida.altura)
    if not endireita_antes(projeto) and etapas.endireita(projeto, pagina) and abs(angulo) >= ANGULO_MINIMO:
        final = alargar_para_o_giro(Recorte(*final, pecas=medido.pecas), angulo, inteira).tupla
    return final


def _area_que_fica(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto):
    """Item 2.14: o que NAO e pintado de branco, (x0, y0, x1, y1) em fracao
    da pagina medida (a reta, no livro novo; a inteira antes do corte, no
    projeto antigo): "so o preto" = a pagina achada; "ate a moldura" = o
    impresso + 1 mm, dentro dela. None quando nao pinta (opcao desligada,
    cortar fora, corte a mao, pagina ainda nao medida, nada a pintar)."""
    if not _so_pinta(projeto, pagina):
        return None
    chave = _chave_da_geometria(folha, pagina, projeto)
    if chave is None:
        return None
    with _TRANCA_GEOMETRIAS:
        medido = _CONTEUDOS.get(chave)
    if medido is None:
        return None
    m = medido.medida
    area = None
    if not medido.so_o_limite:
        area = corte_pelo_conteudo.caixa_do_corte(m)
    if area is None:
        area = m.limite
    if area is None or not m.largura or not m.altura:
        return None
    fr = (area[0] / m.largura, area[1] / m.altura, area[2] / m.largura, area[3] / m.altura)
    if fr[0] <= 0 and fr[1] <= 0 and fr[2] >= 1 and fr[3] >= 1:
        return None
    return fr


def _pintar_na_cortada(img: np.ndarray, area, recorte) -> np.ndarray:
    """Pinta de branco, na pagina ja cortada `img`, o que fica fora de `area`
    (fracao da pagina antes do corte); `recorte` (x, y, largura, altura em
    fracao) e o corte que foi aplicado, None = nenhum."""
    x, y, w, h = recorte if recorte is not None else (0.0, 0.0, 1.0, 1.0)
    if w <= 0 or h <= 0:
        return img
    na_cortada = ((area[0] - x) / w, (area[1] - y) / h, (area[2] - x) / w, (area[3] - y) / h)
    return borda_preta.pintar_fora(img, na_cortada)


def corte_alargado(projeto: Projeto, pagina: ConfigPagina) -> tuple[float, float, float, float] | None:
    """O corte alargado desta pagina (g8: "mostrar ele alargado com o que foi
    tirado"), em fracao, para a tela mostrar e o botao do aviso gravar como
    corte a mao. None quando nao ha o que alargar (nada ficou de fora, a
    pagina nao usa o corte do conteudo ou ainda nao foi medida). Na ordem
    antiga, sem a folga do giro (o corte a mao vale como esta)."""
    if not 0 <= pagina.folha < len(projeto.folhas):
        return None
    achado = _caixa_do_livro(projeto.folhas[pagina.folha], pagina, projeto)
    if achado is None:
        return None
    medido, caixa, _livro = achado
    tiradas = corte_pelo_conteudo.tiradas_do_corte(caixa, medido.candidatas)
    if not tiradas:
        return None
    m = medido.medida
    alargada = corte_pelo_conteudo.alargar(caixa, tiradas, m.mm_por_ponto, m.largura, m.altura)
    # Obra 26/10, etapa 10a (lista unica 1.4, Antiphon 2: "usar o corte
    # alargado" deixou a pagina MENOR, "do meio para a direita"): o alargado
    # nunca fica menor que o corte que a pagina tem agora (o guardado da
    # geometria, que a tela mostra): contem os dois. Arriscado: tirar (o botao
    # volta a poder encolher a pagina).
    guardada = _geometria_guardada(projeto.folhas[pagina.folha], pagina, projeto)
    if guardada is not None and guardada[0] is not None:
        gx0, gy0, gx1, gy1 = corte_pelo_conteudo.de_fracao(guardada[0], m.largura, m.altura)
        alargada = (min(alargada[0], gx0), min(alargada[1], gy0),
                    max(alargada[2], gx1), max(alargada[3], gy1))
    return corte_pelo_conteudo.em_fracao(alargada, m.largura, m.altura)


def paginas_sem_medida_do_conteudo(projeto: Projeto) -> list[ConfigPagina]:
    """As paginas que a passada ainda precisa medir (vazio com a opcao
    desligada)."""
    if not getattr(projeto, "cortar_pelo_conteudo", False) or not projeto.cortar_bordas:
        return []
    faltam = []
    arquivo = _arquivo_do_projeto(projeto)
    for pagina in _paginas_do_corte_do_livro(projeto):
        chave = _chave_da_geometria(projeto.folhas[pagina.folha], pagina, projeto, arquivo)
        if chave is None:
            continue
        with _TRANCA_GEOMETRIAS:
            if chave in _TAMANHOS:
                continue
        faltam.append(pagina)
    return faltam


def medir_conteudo_do_livro(projeto: Projeto, doc=None, progresso: Progresso = None,
                            cancelado: Cancelado = None) -> int:
    """A passada do item 2.5: mede o tamanho do conteudo das paginas ainda
    nao medidas, para o tamanho do livro valer em todas. Devolve quantas mediu.

    Uma folha por vez na memoria, desenhada na resolucao do PDF
    (projeto.qualidade_dpi, a mesma da geometria). O angulo e o
    que ja vale na pagina (angulo_da_pagina); se ainda nao foi medido, e
    medido aqui pela mesma conta (_geometria sem o corte). progresso(feitas,
    total, texto) depois de cada pagina; cancelado() e olhado entre uma e
    outra (levanta Cancelou). No fim poe ou tira o aviso PAGINA_MUITO_MAIOR em
    todas. Sem a opcao do livro, nao faz nada. Custo: de 0,3 a 1 s por pagina
    comum (a folha grande do Antiphon, uns 2 s).
    Arriscado: medir aqui em outra pagina que nao a do corte (a girada de 90,
    dividida e, no livro novo, endireitada), ou guardar em outra chave."""
    faltam = paginas_sem_medida_do_conteudo(projeto)
    if not faltam:
        _avisos_da_folha_muito_maior(projeto)
        return 0
    abriu = doc is None
    if abriu:
        doc = abrir_pdf(projeto.caminho_entrada)
    try:
        medidas = 0
        folha_atual, img_folha = None, None
        for feitas, pagina in enumerate(faltam):
            _checar(cancelado)
            _avisar(progresso, feitas, len(faltam),
                    f"Medindo o tamanho do livro: página {feitas + 1} de {len(faltam)}")
            folha = projeto.folhas[pagina.folha]
            if folha_atual != folha.indice:
                img_folha = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
                folha_atual = folha.indice
            # VELOCIDADE (22/10/2026): a passada guarda a geometria INTEIRA da
            # pagina (angulo, corte comum e a medida do conteudo), pela mesma
            # funcao que a geracao do PDF e a previa usam (_guardar_geometria,
            # mesma imagem, mesmo DPI). Antes ela fazia a sua propria medida e
            # jogava o resto fora, e a geracao calculava tudo de novo na mesma
            # pagina: o angulo e a caixa do ScanTailor eram feitos duas vezes.
            # O tamanho guardado e o da propria medida que corta (antes eram
            # duas contas que tinham de dar o mesmo). Arriscado: voltar a
            # medir aqui por outra conta.
            _guardar_geometria(folha, pagina, projeto, img_folha, doc)
            chave = _chave_da_geometria(folha, pagina, projeto)
            with _TRANCA_GEOMETRIAS:
                ja_tem = chave is None or chave in _TAMANHOS
            if ja_tem:
                medidas += 1
                continue
            # Reserva (nao deveria acontecer: a geometria ja estava guardada
            # de antes sem a medida do conteudo): a medida so do tamanho.
            # o MESMO desenho e o MESMO DPI da geometria (_guardar_geometria):
            # a conta do ScanTailor da caixas diferentes em resolucoes
            # diferentes (contracapa do Egenloff: 276 mm a 300 DPI, <= 252 a
            # 150), e o tamanho do livro tem de ser o das caixas que cortam
            dpi = float(projeto.qualidade_dpi)
            dpi_do_scan = _dpi_do_scan(doc, folha)
            base = preparar_para_recorte(img_folha, folha, pagina, projeto)
            cinza = base if base.ndim == 2 else cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
            cunha_preta = base if _corta_pela_borda(projeto, pagina) else None
            if endireita_antes(projeto) and etapas.endireita(projeto, pagina):
                angulo = angulo_da_pagina(projeto, pagina)
                if angulo is None:
                    angulo = _geometria(base, pagina, projeto, dpi=dpi, dpi_do_scan=dpi_do_scan,
                                        com_o_corte=False)[1]
                if abs(float(angulo or 0.0)) >= ANGULO_MINIMO:
                    if _corta_pela_borda(projeto, pagina):
                        cunha_preta = rotacionar(base, float(angulo), fundo=0)
                    cinza = rotacionar(cinza, float(angulo))
            medida, _so = _medida_da_pagina(cinza, dpi, dpi_do_scan, projeto, cunha_preta)
            chave = _chave_da_geometria(folha, pagina, projeto)
            if chave is not None:
                with _TRANCA_GEOMETRIAS:
                    if chave not in _TAMANHOS:
                        _TAMANHOS[chave] = medida.tamanho_mm if medida.tem_conteudo else None
                        while len(_TAMANHOS) > MAX_GEOMETRIAS:
                            _TAMANHOS.popitem(last=False)
                medidas += 1
        _avisar(progresso, len(faltam), len(faltam), "Tamanho do livro medido")
        _avisos_da_folha_muito_maior(projeto)
        return medidas
    finally:
        if abriu:
            doc.close()


def _avisos_da_folha_muito_maior(projeto: Projeto) -> None:
    """Poe o aviso PAGINA_MUITO_MAIOR nas paginas que ficaram de fora da conta
    do tamanho do livro, e tira das outras (as que a passada mediu e que a
    previa ainda nao desenhou tambem ficam sabendo)."""
    livro = tamanho_do_livro(projeto)
    fora = livro.muito_maiores if livro is not None else frozenset()
    for pagina in projeto.paginas:
        _anotar(pagina, analise.PAGINA_MUITO_MAIOR,
                pagina.indice in fora and getattr(pagina, "alinhar_com_as_outras", None) is not True
                and _corta_pelo_conteudo(projeto, pagina))


def acertar_avisos_do_corte(projeto: Projeto) -> None:
    """Tira os dois avisos do item 2.5 de onde nao valem mais (a opcao foi
    desligada, a pagina ganhou corte a mao), sem desenhar nada. Onde ainda
    podem valer, a previa acerta. Para a tela chamar ao mudar a opcao."""
    for pagina in projeto.paginas:
        if not _segue_o_conteudo(projeto, pagina):
            _anotar(pagina, analise.CORTE_DEIXOU_TINTA_FORA, False)
        if not _corta_pelo_conteudo(projeto, pagina):
            _anotar(pagina, analise.PAGINA_MUITO_MAIOR, False)


def _precisa_de_geometria(pagina: ConfigPagina, projeto: Projeto) -> bool:
    """Ha corte ou angulo automatico a calcular nesta pagina?"""
    # obra 26/10, etapa 1: o automatico de cada etapa, onde nao ha valor a
    # mao que valha (core/etapas; com a caixinha ligada, a conta de sempre)
    return ((etapas.corta_sozinho(projeto) and etapas.recorte_a_mao(projeto, pagina) is None)
            or (etapas.endireita_sozinho(projeto) and etapas.angulo_a_mao(projeto, pagina) is None))


def escolha_da_gravura(projeto: Projeto,
                       pagina: ConfigPagina | None = None):
    """(detector, OpcoesDaGravura) que valem para esta pagina (item 1.2).

    As opcoes vem do livro (Projeto.gravura_forma, gravura_sensibilidade,
    gravura_mais_sensivel, gravura_normalizar - a tela "O que fazer", grupo
    "Gravuras e fotos"). A forma pode ser trocada so numa pagina
    (ConfigPagina.gravura_forma, "Esta pagina tem foto" na aba Marcar), menos
    quando o livro esta em "nao procurar" (forma "desligada"): ai nenhuma
    pagina procura. Valor invalido vindo do arquivo vale o padrao
    (OpcoesDaGravura.corrigida). O detector e sempre o do ScanTailor
    (core.detectar_regioes.DETECTOR_DE_GRAVURA_PADRAO); o antigo so entra
    sozinho, quando a DLL falha - o "desligar" da regra 8 e a forma
    "desligada". Seguro mudar: os padroes, em modelos.Projeto.
    """
    from core import detectar_regioes as dr

    forma = getattr(projeto, "gravura_forma", None) or dr.FORMA_DA_GRAVURA_PADRAO
    da_pagina = getattr(pagina, "gravura_forma", None) if pagina is not None else None
    if (da_pagina in ("livre", "retangular") and forma in dr.FORMAS_DA_GRAVURA
            and forma != dr.FORMA_DESLIGADA):
        forma = da_pagina
    opcoes = dr.OpcoesDaGravura(
        forma=forma,
        sensibilidade=getattr(projeto, "gravura_sensibilidade", 100),
        mais_sensivel=getattr(projeto, "gravura_mais_sensivel", False),
        normalizar=getattr(projeto, "gravura_normalizar", True),
    ).corrigida()
    return dr.DETECTOR_DE_GRAVURA_PADRAO, opcoes


def _gravura_a_refazer(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A marcacao desta pagina foi feita com outras opcoes de gravura?

    Compara a assinatura guardada na pagina (gravura_feita_com) com a das
    opcoes de agora (escolha_da_gravura). Pagina sem marcacao, ou com
    assinatura vazia (marcacao de antes do campo existir), nao conta aqui.
    """
    from core.detectar_regioes import assinatura_da_gravura

    if not pagina.selecao or not getattr(pagina, "gravura_feita_com", ""):
        return False
    return pagina.gravura_feita_com != _assinatura_da_gravura_da_pagina(projeto, pagina)


def _assinatura_da_gravura_da_pagina(projeto: Projeto, pagina: ConfigPagina) -> str:
    """A assinatura das opcoes com que a gravura desta pagina e achada
    (core.detectar_regioes.assinatura_da_gravura) e, desde o item 2.9, a
    caixinha "Letra clara em fundo escuro": com ela ligada, o detector ve a
    pagina invertida (como no ScanTailor), e a assinatura ganha
    claro_no_escuro.SUFIXO_DA_GRAVURA. Desligada, a assinatura e a de sempre
    (nenhum livro ja comecado refaz a marcacao). Arriscado: por o sufixo
    sempre (todas as paginas refariam a gravura)."""
    from core.detectar_regioes import assinatura_da_gravura

    assinatura = assinatura_da_gravura(*escolha_da_gravura(projeto, pagina))
    if claro_no_escuro.ligado(pagina):
        assinatura += claro_no_escuro.SUFIXO_DA_GRAVURA
    # item 2.12: a pagina desentortada e outra imagem para o detector; so com
    # o desentortar ligado (desligado, a assinatura de sempre)
    if desentortar_scantailor.ligado(pagina):
        assinatura += (desentortar_scantailor.SUFIXO_DA_GRAVURA
                       + desentortar_scantailor.modo_da_pagina(pagina))
    return assinatura


# As opcoes de gravura do LIVRO (modelos.Projeto), na tela "O que fazer".
CAMPOS_DA_GRAVURA = ("gravura_forma", "gravura_sensibilidade",
                     "gravura_mais_sensivel", "gravura_normalizar")

# Assinatura posta na pagina marcada antes do campo gravura_feita_com existir,
# quando a pessoa muda as opcoes do livro: nao bate com nenhuma assinatura de
# verdade, e garantir_selecao refaz a parte automatica dela.
REFAZER_A_GRAVURA = "refazer"


def trocar_opcoes_da_gravura(projeto: Projeto, novas: Projeto) -> int:
    """Poe em `projeto` as opcoes de gravura do livro que estao em `novas`.

    E o que acontece ao clicar "Conferir" depois de mudar o grupo "Gravuras e
    fotos" da tela "O que fazer" num livro com trabalho
    (ui/janela_principal._analise_pronta: o trabalho salvo volta por cima da
    analise, e estas opcoes vem da tela). Devolve quantas paginas vao ter a
    gravura achada sozinha refeita (na proxima vez que forem desenhadas; a
    marcacao a mao fica - ver garantir_selecao). 0 = nada muda.

    Pagina marcada antes do campo gravura_feita_com existir (assinatura
    vazia) e que tem alguma regiao automatica ganha REFAZER_A_GRAVURA:
    quem mudou as opcoes do livro quer ver o efeito tambem nela. Pagina so
    com marcacao a mao nao e tocada. Nunca desenha nada nem apaga regiao
    aqui. Arriscado: refazer sem guardar copia do trabalho antes (quem chama
    guarda) - um ajuste feito numa regiao automatica se perde.
    """
    from core.selecao import MAO

    antes = [getattr(projeto, campo) for campo in CAMPOS_DA_GRAVURA]
    for campo in CAMPOS_DA_GRAVURA:
        setattr(projeto, campo, getattr(novas, campo))
    if antes == [getattr(projeto, campo) for campo in CAMPOS_DA_GRAVURA]:
        return 0
    refeitas = 0
    for pagina in projeto.paginas:
        if not pagina.selecao:
            continue
        if not pagina.gravura_feita_com:
            if not any(isinstance(r, dict) and r.get("origem") != MAO for r in pagina.selecao):
                continue
            pagina.gravura_feita_com = REFAZER_A_GRAVURA
        if _gravura_a_refazer(projeto, pagina):
            refeitas += 1
    return refeitas


TITULO_DO_AVISO_DA_GRAVURA = "Gravuras e fotos"


def aviso_das_opcoes_da_gravura(projeto: Projeto, quantas: int, copia) -> tuple[str, str]:
    """(titulo, frase) do aviso de quando as opcoes de "Gravuras e fotos"
    mudaram num livro ja conferido (trocar_opcoes_da_gravura devolveu
    `quantas` > 0). `copia` = o caminho da copia do trabalho, ou None.

    Parecer do verificador (30/09, r09): o aviso dizia "serao procuradas de
    novo" tambem no "nao procurar", em que elas deixam de ser procuradas, e a
    caixa tinha o titulo generico "Um momento". Agora a frase diz o que vai
    acontecer em cada caso, e o titulo diz do que se trata. Quem mostra e
    ui/janela_principal._analise_pronta. Seguro mudar: os textos.
    """
    paginas = f"{quantas} {'página' if quantas == 1 else 'páginas'} já {'marcada' if quantas == 1 else 'marcadas'}"
    if getattr(projeto, "gravura_forma", "livre") == "desligada":
        frase = ("Este livro não vai mais procurar gravuras e fotos: o que o programa "
                 f"tinha achado sozinho sai de {paginas}. O que você marcou à mão fica.")
    else:
        frase = ("As gravuras e fotos vão ser procuradas de novo, com as opções novas, "
                 f"em {paginas}. O que você marcou à mão fica.")
    if copia is not None:
        caminho = str(copia)
        if len(caminho) > 2 and caminho[1] == ":":
            # WORD JOINER: o Qt nao quebra a linha depois de "D:" (ver
            # ui/janela_principal._frase_do_recomeco)
            caminho = caminho[:2] + "⁠" + caminho[2:]
        frase += f"\n\nGuardei uma cópia do trabalho de antes:\n{caminho}"
    else:
        frase += "\n\nNão consegui guardar uma cópia do trabalho de antes."
    return TITULO_DO_AVISO_DA_GRAVURA, frase


def garantir_selecao(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
                     dpi: float | None = None, dpi_do_scan: float | None = None,
                     no_tamanho_do_pdf: bool = True, _de_novo: bool = False):
    """Descobre onde estao gravura, letra e papel - uma vez por pagina.

    PROVISORIA E DEFINITIVA (13/10/2026). O defeito (verificador): a marcacao
    era procurada no primeiro desenho da pagina e guardada; na janela esse
    desenho e a previa (110 DPI), e o detector acha areas diferentes das de
    300 DPI (Graduale 221: 9 areas contra 18). A mesma pagina saia no PDF - e
    era medida pela regra do "Para revisar" - diferente conforme tinha sido
    vista na tela antes ou nao (nas 89 paginas do estudo: 24 iam e 73 certas
    na ordem da janela, 22 e 75 direto). Agora:
      - no_tamanho_do_pdf=False (a previa): a marcacao achada fica guardada
        como PROVISORIA (ConfigPagina.marcacao_provisoria = True). A previa
        aparece no tempo de sempre.
      - no_tamanho_do_pdf=True (o PDF e os desenhos que a tela pede por tras):
        a marcacao provisoria e procurada DE NOVO nesta imagem e trocada - o
        que a MAQUINA marcou sai, o que a pessoa marcou a mao volta por cima,
        como quando as opcoes de gravura mudam - e passa a ser a definitiva.
        A regra do "Para revisar" so mede com a definitiva.
    Pagina de projeto antigo, com marcacao e sem o campo, e definitiva (fica
    como esta). Arriscado: medir a regra com a provisoria; trocar a
    definitiva pela achada numa imagem pequena.

    Item 1.2: a gravura vem do detector escolhido em escolha_da_gravura (de
    fabrica, o ScanTailor). dpi = o DPI em que `img` foi desenhada; sem ele
    o ScanTailor nao roda e vale o detector antigo (ver detectar).
    dpi_do_scan = o DPI do escaneamento, que limita o DPI da gravura.

    Roda SOB DEMANDA, e nao na analise do livro. Detectar leva quase um segundo
    por pagina, e na analise isso daria sete minutos para quinhentas folhas,
    contra a meta de tres. Aqui a conta so acontece quando a pagina vai ser
    mostrada ou exportada, e o resultado fica guardado no projeto: a segunda vez
    e de graca, e o que a pessoa corrigir a mao sobrevive.

    A imagem tem de ser a JA PREPARADA - depois de dividir, cortar e endireitar
    - porque a selecao guarda fracoes daquele recorte. Detectar antes deixaria a
    marcacao deslocada na hora de aplicar.

    Corrida com a tela (achada na juncao do girar ao fase-1, 06/10/2026):
    isto roda no fio da previa e a deteccao leva quase um segundo. Se a
    pessoa marca alguma coisa na aba Marcar nesse meio-tempo, a marcacao
    dela vale: o resultado da deteccao e jogado fora em vez de gravado por
    cima (antes a marcacao a mao sumia; tests/test_ajustar_pedaco_na_aba_
    marcar.py falhava de vez em quando por isso). Quem grava a marcacao
    sempre poe uma lista NOVA em pagina.selecao (guardar_selecao), entao
    basta ver se a lista ainda e a mesma que foi lida. Arriscado: comparar
    por igualdade em vez de identidade (uma marcacao igual de outra origem
    passaria) ou gravar sem conferir.
    """
    from core.selecao import MAO

    if not etapas.marca_sozinho(projeto):
        # obra 26/10, etapa 1 (D-009): sem o AUTOMATICO da marcacao ("Limpar a
        # folha" + "Procurar gravura e letra"), nada e procurado, mas a
        # marcacao feita A MAO vale (core/etapas.marcacao_a_mao; vazia no
        # projeto antigo sem a marca - como antes, que devolvia vazia)
        return etapas.marcacao_a_mao(projeto, pagina)

    lida = pagina.selecao          # a lista de agora (ver a corrida, acima)
    antiga = pagina.obter_selecao()
    # a provisoria (achada na previa) e trocada no desenho do tamanho do PDF
    trocar_a_provisoria = bool(no_tamanho_do_pdf and getattr(pagina, "marcacao_provisoria", False))
    refazer = _gravura_a_refazer(projeto, pagina) or (trocar_a_provisoria and not antiga.vazia)
    if not antiga.vazia and not refazer:
        return antiga

    try:
        from core.detectar_regioes import assinatura_da_gravura, detectar

        detector, opcoes = escolha_da_gravura(projeto, pagina)
        selecao = detectar(img, detector_de_gravura=detector, opcoes_da_gravura=opcoes,
                           dpi=dpi, dpi_do_scan=dpi_do_scan)
    except Exception:  # noqa: BLE001 - sem deteccao o filtro trata a folha toda
        _log.exception("a deteccao de gravura e letra falhou")
        return antiga      # vazia, ou a marcacao de antes intacta

    # Item 1.2: as opcoes de gravura mudaram (no livro ou so nesta pagina):
    # sai o que a MAQUINA tinha marcado, entra o novo, e o que a pessoa
    # marcou a mao volta POR CIMA, na ordem em que estava (a ordem importa:
    # um "tirar" a mao so apaga o que veio antes dele). O filtro por pedaco
    # mora na regiao a mao e vem junto. Arriscado: por a marcacao a mao antes
    # da nova (o "tirar" deixaria de valer), ou refazer sem assinatura.
    if refazer:
        for regiao in antiga.regioes:
            if regiao.origem == MAO:
                selecao.acrescentar(regiao)
    if pagina.selecao is not lida:
        # a marcacao mudou durante a deteccao (a pessoa marcou a mao, ou a
        # previa guardou a provisoria dela): vale a que esta la. No desenho
        # do tamanho do PDF tenta mais UMA vez, por cima da de agora, para a
        # definitiva nao se perder (a marcacao a mao volta por cima).
        if no_tamanho_do_pdf and not _de_novo and getattr(pagina, "marcacao_provisoria", False):
            return garantir_selecao(projeto, pagina, img, dpi, dpi_do_scan,
                                    no_tamanho_do_pdf=True, _de_novo=True)
        return pagina.obter_selecao()
    pagina.gravura_feita_com = _assinatura_da_gravura_da_pagina(projeto, pagina)   # item 2.9

    # A deteccao pode acabar sem certeza se a folha e desenho ou escrita.
    # Quando isso acontece a pagina fica laranja, para a pessoa conferir na
    # aba Marcar - ver DESENHO_OU_ESCRITA. Ficar calado seria pior: a
    # partitura do Graduale passou dois dias marcada como desenho sem
    # ninguem ver.
    if getattr(selecao, "em_duvida", False):
        if analise.DESENHO_OU_ESCRITA not in pagina.alertas:
            pagina.alertas.append(analise.DESENHO_OU_ESCRITA)

    # o campo "provisoria" vai junto com a lista (ConfigPagina.guardar_selecao
    # grava o campo antes dela): o outro fio nunca ve a lista nova com o
    # campo de antes
    pagina.guardar_selecao(selecao, provisoria=not no_tamanho_do_pdf)
    return selecao


# ---------------------------------------------------------------------------
# Item 1.1: tirar o fundo de PDF com camadas (core/camadas.py)
#
# Decisao do Samuel (29/09/2026, depois de ver a primeira ligacao, commit
# bb54b7d): "Pagina sempre abre em 'Original', sem mexer. Em PDF com camadas,
# 'Tirar o fundo' vira mais uma opcao na lista de filtros (ao lado de
# Original, Preto e branco, Melhorar e Magico pro), com botao para aplicar no
# livro inteiro. Assim eu decido se tiro ou nao, e o Kaique escolhe um filtro
# so, sem mudanca escondida." E: "eu quero poder escolher tirar o fundo sem
# colocar nenhum filtro." A pagina duvidosa continua saindo "conferir".
#
# Entao: so a pagina com o filtro "Tirar o fundo" (TIRAR_FUNDO) usa o
# core/camadas.py. Se ele diz "fundo tirado" ou "conferir", sai o resultado
# dele; se diz "intacta" (ou o PDF nao tem camadas, ou deu erro), a pagina
# sai COMO VEIO, igual ao Original - nunca com outro filtro por cima.
#
# Onde entra na ordem dividir -> cortar -> endireitar -> filtro: as camadas
# sao da PAGINA DO PDF (a folha inteira, antes de dividir), entao o "tirar o
# fundo" roda primeiro, na folha, no lugar do desenho dela; dividir, cortar e
# endireitar seguem por cima do resultado; o filtro e pulado. O corte e o
# angulo sao os da folha COMO VEIO (medidos no desenho normal, na resolucao
# do PDF, e guardados em _GEOMETRIAS): os mesmos de qualquer outro filtro, e
# os mesmos na previa e no PDF.
#
# Os caminhos que desenham pagina final passam por aqui: processar (o PDF),
# renderizar_pagina (a previa da tela de conferir, e por ela a
# conferencia.py e o teste de velocidade) e renderizar_com_filtro (o cartao
# "Tirar o fundo" da aba Filtro e o "comparar" da tela ampliada).
# ---------------------------------------------------------------------------


def usa_tirar_fundo(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """Esta pagina tenta o "tirar o fundo" (item 1.1)?

    Sim quando a pagina tem o filtro "Tirar o fundo", "Limpar a folha" esta
    marcada (sem ela nenhum filtro vale) e o PDF tem camadas. Se a pagina vai
    mesmo sair sem o fundo, quem diz e core/camadas.py (pode deixa-la
    intacta). Com o filtro salvo num PDF sem camadas: False, e a pagina sai
    como veio (_filtrar).

    Pagina marcada "Deixar em branco" (ConfigPagina.em_branco, 12/10/2026):
    False - ela sai toda branca (_filtrar), e tirar o fundo dela seria
    trabalho jogado fora.
    """
    # obra 26/10, etapa 1: o filtro que VALE (core/etapas.filtro_que_vale: o
    # da pagina com "Limpar a folha" ligado, ou escolhido a mao)
    return bool(projeto.tem_camadas and etapas.filtro_que_vale(projeto, pagina) == TIRAR_FUNDO
                and not getattr(pagina, "em_branco", False))


def _sem_fundo_da_folha(doc, folha: ConfigFolha, dpi: int):
    """core.camadas.tirar_fundo da folha inteira, no DPI pedido.

    Devolve o PaginaSemFundo (imagem None = a pagina sai como veio). Um erro
    aqui nunca derruba a previa nem o PDF: a folha sai como veio, como se o
    PDF nao tivesse camadas, e o erro vai para o log. A decisao (tirar,
    deixar intacta, conferir) e tomada sempre na mesma resolucao
    (camadas.DPI_DA_ANALISE), qualquer que seja `dpi`: a previa e o PDF
    decidem igual. A decisao fica guardada por folha nesta sessao
    (_DECISOES_DO_FUNDO), para o alerta "conferir" poder ser acertado sem
    desenhar a pagina de novo (acertar_alertas_do_fundo).
    """
    from core import camadas

    chave = _chave_da_folha(doc, folha)
    if chave is not None:
        with _TRANCA_GEOMETRIAS:
            if _DECISOES_DO_FUNDO.get(chave) == _INTACTA:
                return camadas.PaginaSemFundo(
                    None, camadas.DEIXADA_INTACTA,
                    "Esta página fica como está (decidido antes, nesta sessão).")
    try:
        resultado = camadas.tirar_fundo(doc, folha.indice, dpi=dpi)
    except Exception as erro:  # noqa: BLE001 - na duvida, a pagina sai como veio
        _log.exception("tirar o fundo falhou na folha %s", folha.indice + 1)
        return camadas.PaginaSemFundo(
            None, camadas.DEIXADA_INTACTA,
            "Não consegui tirar o fundo desta página; ela sai como veio.",
            medidas={"erro": f"{type(erro).__name__}: {erro}"})
    if chave is not None:
        if resultado.imagem is None:
            decisao = _INTACTA
        else:
            decisao = _CONFERIR if resultado.conferir else _TIRADO
        with _TRANCA_GEOMETRIAS:
            _DECISOES_DO_FUNDO[chave] = decisao
    return resultado


# O que core/camadas.py decidiu para cada folha, nesta sessao do programa:
# _TIRADO (fundo tirado, sem duvida), _CONFERIR (tirado, mas pede
# conferencia) ou _INTACTA (fica como veio: intacta ou sem camadas). A
# decisao nao depende do DPI (e tomada sempre em camadas.DPI_DA_ANALISE).
# Serve para duas coisas:
#   - a folha _INTACTA nao paga de novo o ~1,8 s de tirar o fundo para depois
#     jogar fora (medido em 29/09: Palatino 5, previa de 2,6-3,2 s para
#     4,6-4,8 s sem isto) - a segunda previa, a ampliada, o cartao e o PDF;
#   - o alerta "conferir" pode ser posto na hora em que a pessoa escolhe o
#     filtro, sem esperar a previa (acertar_alertas_do_fundo), quando o
#     cartao ou uma previa anterior ja descobriu a decisao.
# Um erro no core/camadas.py nao e guardado (a proxima vez tenta de novo).
# So guarda a decisao; a imagem sem o fundo nunca fica guardada (uma pagina
# por vez na memoria). A chave leva o arquivo (caminho, data, tamanho), como
# _GEOMETRIAS. Seguro mudar: pode ser esvaziado a qualquer hora (so custa
# tempo; o alerta volta quando a pagina for desenhada).
_TIRADO, _CONFERIR, _INTACTA = "tirado", "conferir", "intacta"
_DECISOES_DO_FUNDO: dict[tuple, str] = {}


def _chave_da_folha(doc, folha: ConfigFolha) -> tuple | None:
    """(arquivo, data, tamanho, folha) do PDF aberto em `doc`; None se o
    documento nao vem de um arquivo no disco."""
    return _chave_do_arquivo(getattr(doc, "name", None), folha)


def _chave_do_arquivo(caminho, folha: ConfigFolha) -> tuple | None:
    """A mesma chave de _chave_da_folha, a partir do caminho do PDF (o
    projeto.caminho_entrada, que e o que o programa abre).

    O caminho entra na forma comum (absoluto, normcase): o mesmo PDF escrito
    com `\\` ou `/`, ou com maiusculas diferentes, da a mesma chave - senao
    a decisao do "tirar o fundo" e as geometrias guardadas nao seriam achadas
    (bug de 29/09, projetos.mesmo_arquivo). So muda o texto da chave."""
    try:
        caminho = os.path.normcase(os.path.abspath(caminho))
        info = os.stat(caminho)
    except (OSError, TypeError, ValueError):
        return None
    return (caminho, info.st_mtime_ns, info.st_size, folha.indice)


def _anotar_conferir(pagina: ConfigPagina, conferir: bool) -> None:
    """Poe ou tira o alerta analise.CONFERIR_FUNDO_TIRADO da pagina.

    Posto quando o fundo saiu mas core/camadas.py ficou em duvida (escrita
    fraca, traco trazido do fundo); tirado quando a pagina sai do filtro
    "Tirar o fundo" ou saiu sem duvida.

    Ao POR o alerta, a pagina volta a "nao conferida" (revisada = False) e o
    alerta vai para a frente da lista (e o primeiro que a faixa mostra).
    Conserto do defeito 2 do verificador (29/09): escolher o filtro marca a
    pagina como conferida (tela_conferir._escolher_filtro), e o alerta, que
    so e conhecido depois, nascia escondido. O "esta bom assim" continua
    valendo: ele marca a pagina conferida com o alerta ja posto, e o alerta
    ja posto nao mexe mais em `revisada`. Arriscado: por o alerta sem voltar
    `revisada` traz o defeito de volta.
    """
    tem = analise.CONFERIR_FUNDO_TIRADO in pagina.alertas
    if conferir and not tem:
        pagina.alertas.insert(0, analise.CONFERIR_FUNDO_TIRADO)
        pagina.revisada = False
    elif not conferir and tem:
        pagina.alertas = [a for a in pagina.alertas if a != analise.CONFERIR_FUNDO_TIRADO]


def acertar_alertas_do_fundo(projeto: Projeto,
                             paginas: list[ConfigPagina] | None = None) -> None:
    """Acerta o alerta "conferir o fundo tirado" sem desenhar nada.

    Pagina fora do filtro "Tirar o fundo" (ou livro sem camadas, ou sem
    "Limpar a folha"): o alerta sai. Pagina no filtro: o alerta entra ou sai
    conforme a decisao ja conhecida nesta sessao (_DECISOES_DO_FUNDO); se
    ainda nao se sabe, fica como esta, e a previa acerta quando chegar
    (renderizar_pagina). Barato: nenhuma pagina e lida.

    Chamado pela tela ao abrir a conferencia (todas as paginas) e a cada
    atualizacao da tela de conferir (a pagina da vez) - e assim que o alerta
    aparece na hora em que se escolhe o filtro, e some quando se sai dele.
    """
    for pagina in projeto.paginas if paginas is None else paginas:
        # Modo Misto (05/10/2026): o "Tinta forte fora do texto" sai na hora
        # em que a pagina deixa o Misto A ou C (mesmo jeito, mesmo momento)
        _acertar_alerta_do_misto(projeto, pagina)
        # e o "Tem cor" segue o "So as letras" (bug Misto 1, 05/10/2026)
        acertar_alertas_de_cor(projeto, [pagina])
        # e o C1 do endireitar sai onde nao vale mais (item 2.2)
        acertar_alerta_do_endireitar(projeto, pagina)
        # e o aviso da "forca do preto sozinha" segue o reforco (12/10/2026)
        acertar_aviso_do_reforco(projeto, pagina)
        # e os dois avisos do corte pelo conteudo (item 2.5), idem
        if not _segue_o_conteudo(projeto, pagina):
            _anotar(pagina, analise.CORTE_DEIXOU_TINTA_FORA, False)
        if not _corta_pelo_conteudo(projeto, pagina):
            _anotar(pagina, analise.PAGINA_MUITO_MAIOR, False)
        if not usa_tirar_fundo(projeto, pagina):
            _anotar_conferir(pagina, False)
            continue
        if not 0 <= pagina.folha < len(projeto.folhas):
            continue
        chave = _chave_do_arquivo(projeto.caminho_entrada, projeto.folhas[pagina.folha])
        if chave is None:
            continue
        with _TRANCA_GEOMETRIAS:
            decisao = _DECISOES_DO_FUNDO.get(chave)
        if decisao is not None:
            _anotar_conferir(pagina, decisao == _CONFERIR)


def _geometria_da_folha_como_veio(doc, folha: ConfigFolha, pagina: ConfigPagina,
                                  projeto: Projeto, img_folha_do_pdf: np.ndarray | None):
    """O (recorte, angulo) da pagina medido na folha COMO VEIO (sem tirar o
    fundo), na resolucao do PDF - o mesmo que o caminho sem o 1.1 usa.

    Usa o guardado; se falta, desenha a folha na resolucao do PDF (ou usa
    img_folha_do_pdf, se quem chamou ja a tem), calcula e guarda. Arriscado:
    medir o corte na folha SEM o fundo mudaria o corte das paginas (o papel
    branco e a borda do scanner sumida confundem detectar_bordas) e faria a
    previa e o PDF dependerem do botao.
    """
    if not _precisa_de_geometria(pagina, projeto):
        return None          # preparar_metade calcula sozinho (manual ou desligado)
    geometria = _geometria_guardada(folha, pagina, projeto)
    if geometria is not None:
        return geometria
    grande = img_folha_do_pdf
    if grande is None:
        grande = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
    _guardar_geometria(folha, pagina, projeto, grande, doc)
    geometria = _geometria_guardada(folha, pagina, projeto)
    if geometria is None:     # arquivo sem chave (nao existe no disco): so calcula
        geometria = _geometria(preparar_para_recorte(grande, folha, pagina, projeto), pagina, projeto,
                               dpi=projeto.qualidade_dpi)
    return geometria


def renderizar_pagina(
    doc, projeto: Projeto, pagina: ConfigPagina, dpi: int = DPI_PREVIA
) -> tuple[np.ndarray, bool]:
    """Imagem final de uma página de saida, do jeito que ela vai sair.

    A marcacao de gravura, letra e papel (13/10/2026): no desenho menor que o
    do PDF (a previa), a pagina sem marcacao ganha a que o detector acha
    nessa imagem pequena, PROVISORIA (ConfigPagina.marcacao_provisoria), para
    a previa aparecer no tempo de sempre. No desenho do tamanho do PDF (o
    PDF, e o que a tela pede por tras: marcar_na_resolucao_do_pdf e a medida
    do "Para revisar"), a provisoria e trocada pela achada nessa imagem
    grande, que e a que vale. Ver garantir_selecao.

    Devolve (imagem, monocromatica). E o que a prévia da tela 3 mostra.

    Item 1.1: se a pagina esta no filtro "Tirar o fundo" (usa_tirar_fundo)
    e core/camadas.py tira o fundo, a previa e a folha sem o fundo, dividida,
    cortada e endireitada como o PDF final (processar faz a mesma coisa), sem
    filtro. Se ele deixa a pagina intacta, ela sai como veio (_filtrar). O
    alerta "conferir" da pagina e acertado aqui (_anotar_conferir).
    """
    folha = projeto.folhas[pagina.folha]
    if usa_tirar_fundo(projeto, pagina):
        resultado = _sem_fundo_da_folha(doc, folha, dpi)
        _anotar_conferir(pagina, bool(resultado.imagem is not None and resultado.conferir))
        if resultado.imagem is not None:
            geometria = _geometria_da_folha_como_veio(doc, folha, pagina, projeto, None)
            img, desenho = _preparar_metade_e_geometria(resultado.imagem, folha, pagina, projeto,
                                                        geometria=geometria)
            # as zonas sao levadas para o preparo de agora ANTES de os
            # pedacos de "so neste pedaco" serem lidos (decisao D2)
            _acompanhar_as_zonas(pagina, desenho)
            return _pedacos_na_pagina_sem_fundo(
                doc, projeto, folha, pagina, img, resultado.imagem.shape, geometria,
                dpi, None), False
    else:
        _anotar_conferir(pagina, False)

    if (dpi != projeto.qualidade_dpi and _precisa_de_geometria(pagina, projeto)
            and _geometria_guardada(folha, pagina, projeto) is None):
        # Primeira vez desta pagina: desenha a folha UMA vez, na resolucao do
        # PDF, calcula e guarda o corte (o mesmo que o PDF vai usar) e reduz
        # essa mesma imagem para a previa, em vez de desenhar de novo. Da
        # segunda vez em diante, desenha so na resolucao da previa.
        grande = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
        _guardar_geometria(folha, pagina, projeto, grande, doc)
        img_folha = _reduzir_para_o_dpi(doc, folha.indice, grande, dpi)
        del grande
    else:
        img_folha = pagina_para_array(doc, folha.indice, dpi=dpi)
        if dpi == projeto.qualidade_dpi and _precisa_de_geometria(pagina, projeto):
            _guardar_geometria(folha, pagina, projeto, img_folha, doc)
    # item 1.2: o DPI de verdade desta imagem e o do scan, para o detector de
    # gravura (so custam alguma coisa quando a pagina ainda nao tem marcacao)
    # e para o limpar pontinhos do ScanTailor (06/10/2026; milissegundos: a
    # conta do desenho e pela area, o do scan fica guardado por folha)
    dpi_desenho = dpi_scan = None
    if _vai_detectar(projeto, pagina, dpi) or _vai_limpar_pelo_scantailor(projeto, pagina):
        dpi_desenho = _dpi_do_desenho(doc, folha.indice, img_folha)
        dpi_scan = _dpi_do_scan(doc, folha)
    _tirar_o_em_branco_falso(projeto, folha, pagina, img_folha, dpi)   # etapa 9c
    img, desenho = _preparar_metade_e_geometria(img_folha, folha, pagina, projeto, dpi=dpi)
    _acompanhar_as_zonas(pagina, desenho)
    return _filtrar(projeto, pagina, img, dpi_desenho, dpi_scan, dpi_pedido=dpi)


def _tirar_o_em_branco_falso(projeto: Projeto, folha: ConfigFolha, pagina: ConfigPagina,
                             img_folha: np.ndarray, dpi: float) -> None:
    """Tira o aviso "Parece em branco" da pagina que, como esta dividida
    AGORA, tem conteudo (etapa 9c da obra, 26/10/2026; D-271, D-288; teste do
    Kaique, "La vida eterna" pagina 7, lista unica 5.7).

    O aviso e decidido uma vez, na analise (_analisar_a_folha), na metade da
    folha que a analise dividiu. Quando a divisao muda depois (a pessoa
    arrasta a linha; o ScanTailor tinha dividido a folha 4 do "La vida
    eterna" a 10%, na linha escura da beirada, e a pagina 7 era uma tira de
    margem), a pagina passa a ter o texto e o aviso ficava - falso.

    Aqui a pagina e medida de novo pela MESMA conta da analise
    (analise.parece_em_branco), na MESMA etapa (girada e dividida, sem corte
    nem giro do endireitar: preparar_para_recorte) e na MESMA escala
    (DPI_ANALISE: o desenho maior e reduzido antes). Pagina branca de verdade
    mede igual a analise e fica com o aviso. So TIRA, nunca poe: o aviso
    tirado pela pessoa ("esta bom assim", "tirar da lista") nao pode voltar.
    Desenho menor que o da analise (o do arrasto, 55 DPI): nao mede (a letra
    miuda some e a conta nao vale). Barato: so roda na pagina com o aviso.
    Arriscado: medir na pagina cortada ou endireitada (os cantos do giro e a
    borda mudam a conta) ou em outra escala (o limite foi medido a 150 DPI).
    Nunca derruba a previa: um erro aqui deixa o aviso como estava."""
    if analise.EM_BRANCO not in pagina.alertas or dpi < DPI_ANALISE * 0.95:
        return
    try:
        metade = preparar_para_recorte(img_folha, folha, pagina, projeto)
        if dpi > DPI_ANALISE * 1.05:
            fator = DPI_ANALISE / float(dpi)
            metade = cv2.resize(metade, (max(1, round(metade.shape[1] * fator)),
                                         max(1, round(metade.shape[0] * fator))),
                                interpolation=cv2.INTER_AREA)
        if not analise.parece_em_branco(metade):
            pagina.alertas = [a for a in pagina.alertas if a != analise.EM_BRANCO]
    except Exception:  # noqa: BLE001 - o aviso fica como estava; a previa segue
        _log.exception("nao consegui medir de novo o 'parece em branco' da pagina %s",
                       pagina.indice + 1)


def precisa_do_desenho_do_pdf(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A tela precisa pedir, por tras, um desenho desta pagina no tamanho do
    PDF? Sim quando a marcacao dela ainda e a provisoria (a achada na previa)
    ou quando a regra do "Para revisar" vale nela (precisa_medir_para_revisar).
    Para ui/tarefas.GerenciadorPrevias.pedir_medida. Barato: so le campos."""
    if pagina.apagada or getattr(pagina, "em_branco", False):
        return False
    provisoria = bool(getattr(pagina, "marcacao_provisoria", False) and etapas.marca_sozinho(projeto)
                      and pagina.filtro != TIRAR_FUNDO)
    return provisoria or precisa_medir_para_revisar(projeto, pagina)


def acertar_no_tamanho_do_pdf(doc, projeto: Projeto, pagina: ConfigPagina) -> bool:
    """O que a tela pede POR TRAS para a pagina da vez (ui/tarefas, numa
    QThread; decisao da gerente, 13/10/2026): troca a marcacao provisoria (a
    da previa) pela achada na pagina do tamanho do PDF e, se a regra do "Para
    revisar" vale na pagina, mede a regra. Devolve True se a marcacao da
    pagina mudou (a tela desenha a previa de novo).

    Por tras, e nao na frente: procurar na pagina grande antes de mostrar a
    previa custava 0,8 s a mais na primeira previa de cada pagina (medido em
    8 paginas do gabarito: de 1,14 para 1,92 s), e trocar de pagina e o que o
    Kaique mais faz (regra 6 do plano).

    Pagina em que a regra vale: o desenho inteiro no tamanho do PDF
    (renderizar_pagina), que troca a marcacao, acha as linhas do leitor de
    texto nessa imagem e mede. Nas outras: so desenhar a folha, preparar e
    procurar a marcacao (sem passar o filtro, que seria tempo jogado fora).
    Nunca levanta excecao para fora de quem chama por causa da marcacao: se a
    procura falhar, a pagina continua com a provisoria (e a regra nao mede).
    Arriscado: chamar isto no fio da tela (leva segundos)."""
    lida = pagina.selecao
    if precisa_medir_para_revisar(projeto, pagina):
        renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
    elif getattr(pagina, "marcacao_provisoria", False):
        folha = projeto.folhas[pagina.folha]
        grande = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
        if _precisa_de_geometria(pagina, projeto):
            _guardar_geometria(folha, pagina, projeto, grande, doc)
        dpi_desenho = _dpi_do_desenho(doc, folha.indice, grande)
        dpi_scan = _dpi_do_scan(doc, folha)
        img, desenho = _preparar_metade_e_geometria(grande, folha, pagina, projeto,
                                                    dpi=projeto.qualidade_dpi)
        _acompanhar_as_zonas(pagina, desenho)
        garantir_selecao(projeto, pagina, img, dpi_desenho, dpi_scan, no_tamanho_do_pdf=True)
    return pagina.selecao is not lida


def _acompanhar_as_zonas(pagina: ConfigPagina, desenho: dict) -> None:
    """Decisao D2 (02/10/2026): as zonas da aba Marcar ficam sobre o mesmo
    pedaco da folha quando o preparo da pagina muda (core/zonas_na_folha.
    acompanhar). Chamado logo depois de preparar a pagina, ANTES de a selecao
    ser usada (_filtrar) ou mostrada (a aba Marcar recebe esta mesma previa).
    Um erro aqui nunca derruba a previa nem o PDF: as zonas ficam como
    estavam (o comportamento de antes) e o erro vai para o log."""
    from core import zonas_na_folha

    try:
        zonas_na_folha.acompanhar(pagina, desenho)
    except Exception:  # noqa: BLE001 - zona que nao deu para levar fica como estava
        _log.exception("nao consegui levar as zonas para o preparo novo da pagina %s",
                       pagina.indice + 1)


# ---------------------------------------------------------------------------
# Converter as zonas do livro inteiro, por tras, ao abrir (decisao Z1 (b) do
# Samuel, conferencia 9, 05/10/2026: "O livro inteiro, por tras, ao abrir -
# ele poderia fazer isso quando abre o livro e fica carregando dai né?").
#
# Converter uma pagina de projeto antigo = anotar nela o preparo de HOJE
# (ConfigPagina.geometria_das_zonas), sem mexer nas zonas - o mesmo que
# _acompanhar_as_zonas faz da primeira vez que ela e desenhada. Feito isso, a
# gravacao seguinte poe as zonas na folha original no projeto.json (com a
# copia de seguranca do arquivo antigo antes, projetos.salvar_estado), e
# mudar o corte ou o angulo depois leva as zonas junto, mesmo numa pagina que
# nunca foi aberta.
#
# Quem chama: ui/tarefas.TarefaConverterZonas (QThread), quando o trabalho
# salvo volta (ui/janela_principal._analise_pronta). A pessoa trabalha
# enquanto isso: pagina que a previa desenhar antes e convertida por ela, e a
# tarefa so pula.
# ---------------------------------------------------------------------------

def _entradas_do_preparo(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto) -> tuple:
    """Tudo de que a geometria das zonas de uma pagina depende (o giro, a
    divisao, o corte e o angulo, a mao ou automaticos). Se mudar enquanto a
    tarefa calcula, a geometria calculada ja nao vale (converter_zonas_do_livro).
    Seguro: acrescentar campos. Arriscado: tirar algum."""
    recorte_a_mao = etapas.recorte_a_mao(projeto, pagina)     # obra 26/10, etapa 1
    recorte = None if recorte_a_mao is None else tuple(float(v) for v in recorte_a_mao)
    return (int(folha.rotacao) % 360, bool(folha.dividir), float(folha.posicao_corte),
            pagina.metade, int(pagina.folha), recorte, etapas.angulo_a_mao(projeto, pagina),
            bool(projeto.cortar_bordas), bool(projeto.endireitar), int(projeto.qualidade_dpi),
            faixa_da_sobra(folha, pagina, projeto),       # item 2.1
            endireitar_scantailor.jeito_da_pagina(projeto, pagina))   # item 2.2


def converter_zonas_do_livro(
    projeto: Projeto,
    progresso: Callable[[int, int], None] | None = None,
    cancelado: Callable[[], bool] | None = None,
) -> int:
    """Converte para o formato novo as zonas de todas as paginas que ainda
    estao no antigo (core/zonas_na_folha.paginas_por_converter). Devolve
    quantas paginas ESTA chamada converteu.

    Uma folha por vez na memoria (regra 3 do CLAUDE.md): a folha e desenhada
    na resolucao do PDF (projeto.qualidade_dpi) - o mesmo desenho em que o
    corte e o angulo automaticos sao sempre medidos (_guardar_geometria) -, e
    a folha dividida e desenhada uma vez so para as duas metades. De quebra,
    o corte e o angulo ficam guardados (_GEOMETRIAS): a primeira previa de
    cada pagina sai mais rapida depois.

    progresso(feitas, total): depois de cada pagina (inclusive as que a
    previa ja tinha convertido, que so sao puladas). cancelado(): olhado
    antes de cada pagina; parar no meio nao estraga nada - o que foi feito
    fica na memoria e vai para o disco na proxima gravacao; o resto continua
    no formato antigo e e convertido da proxima vez que o livro abrir.

    Nunca levanta: PDF que sumiu ou folha que nao desenha so ficam para
    depois (o erro vai para o log), e a pagina continua sendo convertida
    quando for desenhada, como antes.

    Arriscado: anotar sem anotar_se_ainda_antiga (por cima do que a previa
    anotou, ou com o corte de antes de a pessoa mexer); medir o corte em
    outra resolucao que nao projeto.qualidade_dpi (a geometria anotada nao
    seria a da previa nem a do PDF, e as zonas andariam ao desenhar).
    """
    from core import zonas_na_folha

    pendentes = zonas_na_folha.paginas_por_converter(projeto)
    total = len(pendentes)
    if not total:
        return 0
    # Na ordem do livro, agrupadas por folha: as duas metades de uma folha
    # dividida usam o mesmo desenho.
    grupos: "OrderedDict[int, list[ConfigPagina]]" = OrderedDict()
    for pagina in pendentes:
        grupos.setdefault(int(pagina.folha), []).append(pagina)

    try:
        doc = abrir_pdf(projeto.caminho_entrada)
    except Exception:  # noqa: BLE001 - sem o PDF, cada pagina converte ao ser desenhada
        _log.exception("nao consegui abrir o PDF para converter as zonas do livro")
        return 0

    feitas = convertidas = 0
    try:
        for indice_folha, paginas in grupos.items():
            folha = projeto.folhas[indice_folha]
            img_folha = None
            for pagina in paginas:
                if cancelado is not None and cancelado():
                    return convertidas
                if not zonas_na_folha.geometria_valida(pagina.geometria_das_zonas):
                    antes = _entradas_do_preparo(folha, pagina, projeto)
                    try:
                        if img_folha is None:
                            img_folha = pagina_para_array(doc, folha.indice,
                                                          dpi=projeto.qualidade_dpi)
                        if _precisa_de_geometria(pagina, projeto):
                            _guardar_geometria(folha, pagina, projeto, img_folha, doc)
                        _, desenho = _preparar_metade_e_geometria(
                            img_folha, folha, pagina, projeto, dpi=projeto.qualidade_dpi,
                            so_a_geometria=True)
                        if zonas_na_folha.anotar_se_ainda_antiga(
                                pagina, desenho,
                                ainda_vale=lambda f=folha, p=pagina, a=antes:
                                    _entradas_do_preparo(f, p, projeto) == a):
                            convertidas += 1
                    except Exception:  # noqa: BLE001 - fica para quando for desenhada
                        _log.exception("nao consegui converter as zonas da pagina %s",
                                       pagina.indice + 1)
                feitas += 1
                if progresso is not None:
                    progresso(feitas, total)
            del img_folha                 # uma folha por vez na memoria
    finally:
        doc.close()
    return convertidas


def _vai_detectar(projeto: Projeto, pagina: ConfigPagina, dpi_pedido: float | None = None) -> bool:
    """_filtrar vai chamar a deteccao de gravura e letra nesta pagina? (a
    mesma conta de _filtrar + garantir_selecao; so serve para nao medir DPI a
    toa). Errar para "sim" so custa milissegundos. Atencao: no filtro
    Original a deteccao roda do mesmo jeito (_filtrar chama garantir_selecao
    antes de saber o filtro), e a marcacao fica guardada para quando a pessoa
    trocar de filtro - por isso o Original NAO fica de fora aqui.
    dpi_pedido: a resolucao do desenho; no do tamanho do PDF a marcacao
    provisoria (a da previa) tambem e procurada de novo (13/10/2026)."""
    if not (etapas.marca_sozinho(projeto) and pagina.filtro != TIRAR_FUNDO):
        return False
    if not pagina.selecao or _gravura_a_refazer(projeto, pagina):
        return True
    return bool(getattr(pagina, "marcacao_provisoria", False)
                and _e_o_desenho_do_pdf(projeto, dpi_pedido))


def _e_o_desenho_do_pdf(projeto: Projeto, dpi_pedido: float | None) -> bool:
    """Este desenho e do tamanho do PDF (ou maior)? Sem a resolucao (testes e
    scripts que chamam _filtrar direto), conta como sendo: e o jeito de quem
    gera o resultado de verdade. A previa da tela (110 DPI) e o arrasto (55)
    dizem a resolucao e nao sao."""
    return dpi_pedido is None or dpi_pedido >= projeto.qualidade_dpi


def _vai_limpar_pelo_scantailor(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """_filtrar vai usar o limpar pontinhos do ScanTailor nesta pagina (o
    Preto e branco com "pouco", "normal" ou "muito")? So serve para medir o
    DPI de verdade so quando precisa. Errar para "sim" so custa milissegundos."""
    return bool(etapas.filtro_que_vale(projeto, pagina) == PRETO_E_BRANCO
                and (pontinhos_scantailor.escolha_da_pagina(projeto, pagina)
                     in pontinhos_scantailor.DO_SCANTAILOR
                     or _jeito_do_scantailor(pagina)))


def _jeito_do_scantailor(pagina: ConfigPagina) -> bool:
    """A pagina usa um dos dez jeitos de preto e branco do ScanTailor (item
    2.8)? Eles tambem precisam do DPI de verdade (a suavizacao Savitzky-Golay
    escolhe a janela pelo DPI); ver pontinhos_da_pagina."""
    from core.preto_e_branco_scantailor import e_do_scantailor

    return e_do_scantailor(getattr(pagina, "algoritmo_preto_branco", None))


def pontinhos_da_pagina(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
                        dpi: float | None = None,
                        dpi_do_scan: float | None = None) -> "pontinhos_scantailor.Pontinhos":
    """O "Limpar pontinhos" desta pagina pronto para o filtro (decisao do
    Samuel, 06/10/2026, P7): a escolha que vale nela (dela ou do livro;
    pontinhos_scantailor.escolha_da_pagina) e o DPI de verdade de `img` (a
    pagina ja preparada) - dpi e o do desenho (_dpi_do_desenho) e dpi_do_scan
    o que o PDF diz (_dpi_do_scan); nos PDFs de "72 DPI" o DPI e acertado
    como no detector de gravura (pontinhos_scantailor.dpi_para_os_pontinhos).
    Sem dpi, o filtro estima pela altura. Publica: a tela ampliada e o
    montar_misto.py tambem usam."""
    escolha = pontinhos_scantailor.escolha_da_pagina(projeto, pagina)
    dpi_certo = None
    # item 2.8: os dez jeitos do ScanTailor leem o DPI daqui (Pontinhos.dpi)
    if (escolha in pontinhos_scantailor.DO_SCANTAILOR or _jeito_do_scantailor(pagina)) and dpi:
        dpi_certo = pontinhos_scantailor.dpi_para_os_pontinhos(
            img.shape[1], img.shape[0], dpi, dpi_do_scan)
    return pontinhos_scantailor.Pontinhos(escolha, dpi_certo)


def _dpi_do_desenho(doc, indice: int, img_folha: np.ndarray) -> float | None:
    """O DPI em que a folha `indice` foi desenhada em img_folha (a folha
    inteira, antes de girar, dividir e cortar).

    Nao e o DPI pedido: pdf_io.dpi_seguro (e _reduzir_para_o_dpi) baixam o
    DPI de pagina gigante. Medido pela area (pontos x pixels), para nao
    depender de a folha estar em pe ou deitada. None se nao der para medir.
    Usado pelo detector de gravura do ScanTailor (item 1.2), que precisa do
    DPI de verdade da imagem.
    """
    try:
        largura_pt, altura_pt = tamanho_da_pagina_pt(doc, indice)
        area_pol = (largura_pt / 72.0) * (altura_pt / 72.0)
        if area_pol <= 0:
            return None
        return float((img_folha.shape[0] * img_folha.shape[1] / area_pol) ** 0.5)
    except Exception:  # noqa: BLE001 - sem o DPI, o detector antigo resolve
        return None


def _dpi_do_scan(doc, folha: ConfigFolha) -> float | None:
    """O DPI do escaneamento da folha: a largura da maior imagem
    embutida dividida pela largura da pagina em polegadas - a mesma conta de
    pdf_io.dpi_real_da_pagina, mas lendo a largura na lista de imagens
    (get_images), sem tirar a imagem de dentro do PDF (milissegundos, contra
    ate um segundo num JPEG 2000 grande). None se nao ha imagem (PDF de
    texto) ou se der erro. Guardado por folha nesta sessao (_DPIS_DO_SCAN).
    """
    chave = _chave_da_folha(doc, folha)
    if chave is not None:
        with _TRANCA_GEOMETRIAS:
            if chave in _DPIS_DO_SCAN:
                return _DPIS_DO_SCAN[chave]
    dpi = None
    try:
        from core.pdf_io import _TRANCA

        with _TRANCA:
            pagina = doc[folha.indice]
            largura_pt = float(pagina.rect.width)
            maior = max((int(i[2]) for i in pagina.get_images()), default=0)
        if largura_pt > 0 and maior > 0:
            dpi = maior / (largura_pt / 72.0)
    except Exception:  # noqa: BLE001 - sem o DPI do scan, vale o do desenho
        dpi = None
    if chave is not None:
        with _TRANCA_GEOMETRIAS:
            _DPIS_DO_SCAN[chave] = dpi
    return dpi


# O DPI do escaneamento de cada folha, nesta sessao (ver _dpi_do_scan). Seguro
# esvaziar a qualquer hora.
_DPIS_DO_SCAN: dict[tuple, float | None] = {}


def _filtrar(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
             dpi: float | None = None, dpi_do_scan: float | None = None,
             dpi_pedido: float | None = None) -> tuple[np.ndarray, bool]:
    """Etapa 4, a porta de entrada: o filtro da pagina (_filtrar_a_pagina), ou
    a folha toda branca se a pessoa escolheu "Deixar em branco"
    (ConfigPagina.em_branco; Samuel, rodada 5 do "Para revisar",
    `rv5-erro-5-sem-conteudo`). O MESMO para a previa e o PDF.

    dpi_pedido: a resolucao em que o desenho foi pedido (a da previa, a do
    arrasto, a do PDF); so serve para a regra do "Para revisar" nao ser medida
    no desenho pequeno do arrasto (_da_para_medir). None = nao se sabe: mede.

    Em branco: a pagina sai do tamanho que teria (ja dividida, cortada e
    endireitada), em 1 bit, sem passar por filtro nem por detector. Os avisos
    do "So as letras" ficam como estavam (nada foi medido; a pagina ja esta
    dada como conferida, e se a pessoa voltar atras o aviso ainda esta la). No
    fim, o aviso da "forca do preto sozinha" e acertado
    (acertar_aviso_do_reforco). Arriscado: devolver aqui uma folha de outro
    tamanho (a encadernacao e a folha escolhida contam com o tamanho da
    pagina)."""
    if getattr(pagina, "em_branco", False):
        acertar_aviso_do_reforco(projeto, pagina)
        return np.full(img.shape[:2], 255, np.uint8), True
    saida = _filtrar_a_pagina(projeto, pagina, img, dpi, dpi_do_scan, dpi_pedido)
    acertar_aviso_do_reforco(projeto, pagina)
    return saida


def _filtrar_a_pagina(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
                      dpi: float | None = None, dpi_do_scan: float | None = None,
                      dpi_pedido: float | None = None) -> tuple[np.ndarray, bool]:
    """Etapa 4: o filtro da pagina, com a marcacao de gravura/letra/papel.

    Item 2.9 (20/10/2026, Samuel P9 (a)): pagina com a caixinha "Letra clara
    em fundo escuro" (core.claro_no_escuro) passa invertida por todo o
    caminho abaixo - marcacao de gravura inclusive - e o resultado e invertido
    de novo, como o ScanTailor faz (initFilterData e o fim da saida). Original
    e "Tirar o fundo" nao mudam (inverter duas vezes daria a mesma pagina).
    Caixinha desmarcada (o de fabrica): nenhuma conta a mais.

    dpi e dpi_do_scan vao para garantir_selecao (o detector de gravura do
    ScanTailor precisa deles; item 1.2) e para o "Limpar pontinhos" do
    Preto e branco e do "So as letras" (pontinhos_da_pagina; decisao do
    Samuel de 06/10/2026, P7; de fabrica core/pontinhos_scantailor.PADRAO,
    que desde 07/10 nunca e o do ScanTailor).

    O MESMO para a previa (renderizar_pagina) e o PDF (processar): antes era
    escrito duas vezes, igual. Devolve (imagem, monocromatica); sem "Limpar a
    folha", a imagem como veio.

    Filtro "Tirar o fundo" (item 1.1) que chega aqui: core/camadas.py deixou
    a pagina intacta, o PDF nao tem camadas ou deu erro - a pagina sai como
    veio, sem outro filtro por cima e sem procurar gravura e letra (a
    marcacao nao serviria para nada, e custa ~1 s). So o "so neste pedaco"
    marcado a mao vale por cima, como no Original (conferencia 14, "FUNDO";
    ver _so_os_pedacos_no_tirar_o_fundo).

    A opcao do livro Projeto.pb_decoracao_em_preto_e_branco (moldura e
    iluminura tambem em preto e branco; emenda N2 do Samuel, 30/09/2026) vai
    para o filtro aqui; so vale no Preto e branco.

    Modo Misto (05/10/2026): pagina em Preto e branco com "So as letras"
    ligada (core.misto.opcoes_da_pagina) vai para _filtrar_no_misto; ali a
    caixinha das molduras nao vale (decisao P5 do Samuel: fica apagada na
    tela enquanto "So as letras" estiver marcada). Sem "So as letras", o
    caminho de sempre, sem nenhuma conta a mais (provado: as 32 paginas do
    gabarito nos 4 filtros saem identicas ao ace15b2).

    "Limpar a folha" desligado e o "so neste pedaco" (achado do verificador,
    05/10/2026): o pedaco marcado na aba Marcar NAO vale aqui, e de proposito -
    nao e a mesma causa da pagina em Original (consertada em
    core.filtros.aplicar_filtro_com_selecao). Desligar "Limpar a folha" e a
    escolha do LIVRO de nao passar filtro em pagina nenhuma, e com ela a tela
    de conferir nem monta as abas Marcar e Filtro (ui/tela_conferir.py,
    TelaConferir.carregar): o pedaco ficaria invisivel, sem como ver nem tirar, e mesmo
    assim mudaria o PDF. Se o Samuel quiser o contrario, a mudanca e aqui (e
    na tela, para o pedaco aparecer). Coberto por
    tests/test_so_neste_pedaco_no_original.py.

    MUDOU na obra de 26/10/2026, etapa 1 (decisao D-009 do Samuel: "eu deveria
    conseguir abrir o livro sem escolher nenhuma opção para fazer tudo
    manualmente."): o paragrafo acima vale so para o PROJETO ANTIGO
    (Projeto.feito_a_mao_sempre_vale False) sem a marca "mexida a mao". No
    livro novo, com "Limpar a folha" desligado:
      - pagina sem nada a mao: sai como veio (como sempre);
      - filtro escolhido a mao na pagina (core/etapas.filtro_a_mao): o
        caminho inteiro abaixo, com esse filtro e so a marcacao a mao (o
        automatico da marcacao fica desligado: garantir_selecao);
      - so marcacao a mao ("so neste pedaco", "pintar por cima"...): a pagina
        fica no Original e so o marcado muda (_so_a_marcacao_a_mao).
    Arriscado: deixar o filtro do livro (escondido na tela de opcoes) valer
    numa pagina que ninguem mexeu - por isso filtro_que_vale.
    """
    if not etapas.filtra(projeto, pagina):
        _tirar_avisos_do_so_as_letras(projeto, pagina)
        return img, False
    if not projeto.limpar and not etapas.filtro_a_mao(projeto, pagina):
        return _so_a_marcacao_a_mao(projeto, pagina, img)
    invertida = claro_no_escuro.ligado(pagina) and pagina.filtro not in (ORIGINAL, TIRAR_FUNDO)
    entrada = claro_no_escuro.inverter(img) if invertida else img
    saida, monocromatica = _filtrar_preto_no_branco(projeto, pagina, entrada, dpi, dpi_do_scan,
                                                       dpi_pedido)
    # Item 2.11: "Letras com a cor delas" e "Reduzir cores" (core.cores_scantailor),
    # o ultimo passo, antes de desinverter (como no ScanTailor). Desmarcadas (o de
    # fabrica): nenhuma conta a mais.
    if cores_scantailor.letras_ligadas(pagina) or cores_scantailor.reduzir_ligado(pagina):
        dpi_certo = (pontinhos_scantailor.dpi_para_os_pontinhos(
            entrada.shape[1], entrada.shape[0], dpi, dpi_do_scan) if dpi else None)
        com_cor = cores_scantailor.aplicar(
            entrada, saida, pagina.filtro, cores_scantailor.letras_ligadas(pagina),
            cores_scantailor.reduzir_ligado(pagina), dpi_certo)
        if com_cor is not None:
            saida, monocromatica = com_cor
    return (claro_no_escuro.inverter(saida) if invertida else saida), monocromatica


def _so_a_marcacao_a_mao(projeto: Projeto, pagina: ConfigPagina,
                         img: np.ndarray) -> tuple[np.ndarray, bool]:
    """A pagina no Original com so o que foi marcado A MAO por cima (obra de
    26/10/2026, etapa 1, D-009): "Limpar a folha" desligado, o filtro da
    pagina nao foi escolhido a mao, mas ha marcacao a mao que vale (um pedaco
    com filtro proprio, "pintar por cima", "tinta preta, fundo original"...).
    E o mesmo caminho da pagina em Original com marcacao (aplicar_filtro_com_
    selecao no ORIGINAL, que so mexe nos pedacos com filtro, e
    editar_zonas.aplicar_por_cima). Sem pedaco nem zona, a pagina sai como
    veio. Arriscado: passar aqui pelo filtro da pagina (o do livro, que
    ninguem escolheu nesta pagina)."""
    selecao = etapas.marcacao_a_mao(projeto, pagina)
    _tirar_avisos_do_so_as_letras(projeto, pagina)
    saida, monocromatica = aplicar_filtro_com_selecao(
        img, ORIGINAL, selecao, pagina.forca_preto, pagina.clareza_melhorar,
        pagina.intensidade_magico, algoritmo_pb=pagina.algoritmo_preto_branco)
    return editar_zonas.aplicar_por_cima(img, saida, monocromatica, selecao,
                                         pagina.forca_preto, pagina.algoritmo_preto_branco,
                                         preto_e_branco=False)


def filtro_com_as_caixinhas(img: np.ndarray, pagina: ConfigPagina, filtro: str, dpi: float,
                            forca_preto: int, clareza: int, intensidade: int,
                            algoritmo_pb: str = "auto", despeckle=True) -> np.ndarray:
    """O filtro `filtro` numa imagem solta (o cartao do filtro, a tela
    ampliada), com as caixinhas desta pagina, na ordem de _filtrar: "Letra
    clara em fundo escuro" (item 2.9) inverte na entrada e na saida (nunca no
    Original nem no Tirar o fundo); "Letras com a cor delas" e "Reduzir
    cores" (item 2.11) sao o ultimo passo antes de desinverter. Sem caixinha
    marcada sai exatamente o aplicar_filtro de sempre.

    Bug do verificador do 2.9 (21/10/2026): o cartao chamava aplicar_filtro
    direto e mostrava a pagina sem inverter (tests/
    test_cartoes_seguem_as_caixinhas.py). Arriscado: tirar daqui uma das
    caixinhas (o cartao volta a mostrar outra coisa que a pagina)."""
    invertida = claro_no_escuro.ligado(pagina) and filtro not in (ORIGINAL, TIRAR_FUNDO)
    entrada = claro_no_escuro.inverter(img) if invertida else img
    saida, _ = aplicar_filtro(entrada, filtro, forca_preto, clareza, intensidade,
                              algoritmo_pb=algoritmo_pb, despeckle=despeckle)
    if cores_scantailor.letras_ligadas(pagina) or cores_scantailor.reduzir_ligado(pagina):
        com_cor = cores_scantailor.aplicar(
            entrada, saida, filtro, cores_scantailor.letras_ligadas(pagina),
            cores_scantailor.reduzir_ligado(pagina), dpi)
        if com_cor is not None:
            saida = com_cor[0]
    return claro_no_escuro.inverter(saida) if invertida else saida


def _filtrar_preto_no_branco(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
                             dpi: float | None = None,
                             dpi_do_scan: float | None = None,
                             dpi_pedido: float | None = None) -> tuple[np.ndarray, bool]:
    """O corpo de _filtrar (ver a explicacao la): a pagina tratada como letra
    escura em papel claro. Chamado direto, ou com a pagina ja invertida
    (item 2.9). dpi_pedido: o do "Para revisar" (ver _filtrar), repassado
    pela juncao de 23/10/2026 (os dois ramos mexeram no mesmo corpo). Arriscado: chamar daqui fora sem passar por _filtrar (a
    caixinha "Letra clara em fundo escuro" deixaria de valer)."""
    if pagina.filtro == TIRAR_FUNDO:
        # Conferencia 14 (Samuel, "FUNDO: Sim, do mesmo jeito (só muda se
        # alguém marcar um pedaço)"): o pedaco vale aqui como no Original. A
        # marcacao usada e a GUARDADA (pagina.obter_selecao), sem chamar o
        # detector: o pedaco e desenhado a mao, e a pagina sem pedaco nao
        # paga o ~1 s da deteccao (e sai o mesmo objeto, como antes).
        _tirar_avisos_do_so_as_letras(projeto, pagina)
        return _so_os_pedacos_no_tirar_o_fundo(projeto, pagina, img, img), False
    # Item 2.17 (desligado de fabrica): igualar a luz e tirar o chuvisco,
    # ANTES do filtro e da marcacao, como o ScanTailor (transformToWorkingCs e
    # o Wiener vem antes de tudo na saida dele). Tudo desligado: `img` e o
    # mesmo objeto, nenhuma conta a mais.
    if pagina.filtro != ORIGINAL:          # o Original nao muda nada (nem a luz)
        img = luz_scantailor.antes_do_filtro(img, pagina)
    # O "suavizar as letras" vale dentro do Preto e branco desta pagina, neste
    # fio (core.luz_scantailor.suavizar_nesta_pagina; item 2.16: varias
    # paginas ao mesmo tempo, cada uma no seu fio).
    with luz_scantailor.suavizar_nesta_pagina(
            pagina, dpi or pontinhos_scantailor.dpi_pela_altura(img.shape[0])):
        return _filtrar_com_a_marcacao(projeto, pagina, img, dpi, dpi_do_scan, dpi_pedido)


def _filtrar_com_a_marcacao(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
                            dpi: float | None, dpi_do_scan: float | None,
                            dpi_pedido: float | None = None) -> tuple[np.ndarray, bool]:
    """O fim de _filtrar (a marcacao e o filtro), separado em 22/10/2026 so
    para caber dentro do "suavizar nesta pagina" do item 2.17. A conta e a
    mesma de antes, linha por linha. dpi_pedido: o do "Para revisar" (ver
    _filtrar; juncao de 23/10/2026)."""
    # a marcacao provisoria (da previa) e trocada no desenho do tamanho do PDF
    no_pdf = _e_o_desenho_do_pdf(projeto, dpi_pedido)
    selecao = garantir_selecao(projeto, pagina, img, dpi, dpi_do_scan, no_tamanho_do_pdf=no_pdf)
    saida, monocromatica = _filtro_da_pagina(projeto, pagina, img, selecao, dpi, dpi_do_scan,
                                             dpi_pedido, no_pdf)
    # Item 2.18 (P11 (a) e TINTA3, 05/10/2026): "Pintar por cima", "Tinta com
    # a cor original, papel branco" e "Tinta preta, fundo original" valem POR
    # CIMA do filtro, so dentro da area (core.editar_zonas). Sem nenhuma
    # dessas areas: o mesmo resultado, o mesmo objeto.
    # O filtro da pagina vai junto: no Preto e branco o "papel como o resto
    # da pagina" sai igual ao "papel branco" (pergunta 10, 23/10/2026).
    return editar_zonas.aplicar_por_cima(img, saida, monocromatica, selecao,
                                         pagina.forca_preto, pagina.algoritmo_preto_branco,
                                         preto_e_branco=(pagina.filtro == PRETO_E_BRANCO))


def _filtro_da_pagina(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray, selecao,
                      dpi: float | None, dpi_do_scan: float | None,
                      dpi_pedido: float | None = None,
                      no_pdf: bool = True) -> tuple[np.ndarray, bool]:
    """O filtro da pagina com a marcacao (o corpo de sempre do _filtrar).
    dpi_pedido e no_pdf: os do "Para revisar" (a regra so mede no desenho do
    tamanho do PDF; juncao de 23/10/2026)."""
    # "Limpar pontinhos" (06/10/2026): a escolha da pagina e o DPI de verdade
    pontinhos = pontinhos_da_pagina(projeto, pagina, img, dpi, dpi_do_scan)
    if pagina.filtro == PRETO_E_BRANCO:
        opcoes = misto.opcoes_da_pagina(projeto, pagina)
        if opcoes is not None:
            # a regra so mede com a marcacao definitiva (a do tamanho do PDF)
            medir = (_da_para_medir(img, dpi_pedido, projeto)
                     and not getattr(pagina, "marcacao_provisoria", False))
            return _filtrar_no_misto(projeto, pagina, img, selecao, opcoes, pontinhos,
                                     medir=medir, linhas_definitivas=no_pdf)
    _tirar_avisos_do_so_as_letras(projeto, pagina)
    return aplicar_filtro_com_selecao(
        img, pagina.filtro, selecao,
        pagina.forca_preto, pagina.clareza_melhorar, pagina.intensidade_magico,
        algoritmo_pb=pagina.algoritmo_preto_branco, despeckle=pontinhos,
        decoracao_em_preto_e_branco=bool(
            getattr(projeto, "pb_decoracao_em_preto_e_branco", False)),
    )


# ---------------------------------------------------------------------------
# Modo Misto ("So as letras" no Preto e branco), ligado em 05/10/2026
#
# Pedidos do Samuel: a caixinha "So as letras" por livro e por pagina
# (conferencia 10, P1 (a)); A "Guardar a tinta forte" de fabrica, achando as
# linhas so com o docTR (conferencia 14); "Para revisar" sozinho quando sobra
# muita tinta forte fora das linhas (conferencia 8, REVISAR: "Sim").
# ---------------------------------------------------------------------------

# QUEM VAI PARA "PARA REVISAR" NO "SO AS LETRAS" (regra ajustada, 12/10/2026)
#
# Ate 12/10/2026 a pagina ia quando a tinta forte fora das linhas passava de
# 10% de toda a tinta (o aviso "Tinta forte fora do texto", conferencia 8).
# Nas 89 paginas do estudo isso mandava 55 e acertava 52. O Samuel aprovou a
# regra ajustada (rodada 4, `rv4-resumo`: "Fica assim"), que manda 21 e acerta
# 78: as contas e os limites moram em core/revisar.py, e quem poe e tira os
# avisos e _acertar_avisos_do_misto, abaixo. O limite antigo continua valendo
# so no "Guardar só o texto" (revisar.LIMITE_SO_O_TEXTO).
#
# A REGRA SO E MEDIDA NO DESENHO FEITO NA RESOLUCAO DO PDF (Projeto.
# qualidade_dpi), nunca no da previa da tela. Medido em 12/10/2026 nas 89
# paginas do estudo (relatorios/para-revisar-impl/conferir_89.py --programa):
# a 300 DPI, a resolucao em que a regra foi acertada e aprovada, o programa
# decide como o estudo; a 110 DPI (a previa) 13 paginas decidem diferente (24
# vao, 67 certas): o texto falhado da falso em varias paginas (o preto e
# branco pequeno quebra o traco fino) e a letra T do Antiphonal 46 nao e
# vista (a pagina tem 396 pontos de altura na previa). Com a "forca do preto
# sozinha", um falso "texto falhado" escureceria a pagina sem motivo.
# Entao: o PDF (processar) mede; a tela pede, por tras, um desenho na
# resolucao do PDF so para medir a pagina da vez (ui/tarefas.
# GerenciadorPrevias.pedir_medida); a previa e o arrasto (55 DPI) nao medem
# e deixam os avisos como estavam. Quem diz a resolucao e quem pede o
# desenho (renderizar_pagina, processar); sem ela (testes, scripts que chamam
# _filtrar direto), mede. E nunca em imagem minuscula.
# Arriscado: medir na previa (os numeros 21 e 78 nao valem la).
# MEDIR_SO_NA_RESOLUCAO_DO_PDF = False e so para o script que mediu isto.
MEDIR_SO_NA_RESOLUCAO_DO_PDF = True
DPI_MINIMO_PARA_REVISAR = 100
LADO_MINIMO_PARA_REVISAR = 400


def _da_para_medir(img: np.ndarray, dpi_pedido: float | None, projeto: Projeto | None = None) -> bool:
    """A regra do "Para revisar" pode ser medida neste desenho? (ver acima)"""
    if max(img.shape[:2]) < LADO_MINIMO_PARA_REVISAR:
        return False
    if dpi_pedido is None:
        return True
    if MEDIR_SO_NA_RESOLUCAO_DO_PDF and projeto is not None:
        return dpi_pedido >= projeto.qualidade_dpi
    return dpi_pedido >= DPI_MINIMO_PARA_REVISAR


def precisa_medir_para_revisar(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A regra do "Para revisar" vale nesta pagina? (ela esta em Preto e
    branco com "So as letras" num jeito que usa o leitor de texto, e nao foi
    deixada em branco nem apagada). Para a tela saber se pede a medida por
    tras (ui/tarefas.GerenciadorPrevias.pedir_medida). Barato: so le campos."""
    if (etapas.filtro_que_vale(projeto, pagina) != PRETO_E_BRANCO or pagina.apagada
            or getattr(pagina, "em_branco", False)):
        return False
    opcoes = misto.opcoes_da_pagina(projeto, pagina)
    return opcoes is not None and opcoes.precisa_das_linhas


def _chave_das_linhas(projeto: Projeto, pagina: ConfigPagina):
    """O que identifica a pagina PREPARADA (para guardar as linhas de texto
    achadas nela; core.linhas_do_texto): o arquivo, a folha, a metade e tudo
    que muda o corte e o giro. O filtro e os ajustes nao entram (nao mudam
    onde esta o texto). None (nao guarda) se o arquivo nao esta no disco.
    Arriscado: tirar daqui algo que muda a imagem preparada (as linhas
    guardadas ficariam deslocadas)."""
    if not 0 <= pagina.folha < len(projeto.folhas):
        return None
    folha = projeto.folhas[pagina.folha]
    arquivo = _chave_do_arquivo(projeto.caminho_entrada, folha)
    if arquivo is None:
        return None
    recorte_a_mao = etapas.recorte_a_mao(projeto, pagina)     # obra 26/10, etapa 1
    recorte = tuple(round(float(v), 4) for v in recorte_a_mao) if recorte_a_mao else None
    return (arquivo, pagina.metade, folha.rotacao, folha.dividir,
            round(float(folha.posicao_corte), 4), recorte, etapas.angulo_a_mao(projeto, pagina),
            projeto.dividir_folhas, projeto.cortar_bordas, projeto.endireitar,
            faixa_da_sobra(folha, pagina, projeto))       # item 2.1


def _filtrar_no_misto(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray, selecao,
                      opcoes, pontinhos=True, medir: bool = True,
                      linhas_definitivas: bool = True) -> tuple[np.ndarray, bool]:
    """O Preto e branco so nas letras (core.misto.aplicar_misto) com as
    escolhas da pagina (`opcoes`, core.misto.OpcoesDoMisto) e o "Limpar
    pontinhos" dela (`pontinhos`, de pontinhos_da_pagina).

    A e C precisam das linhas de texto: core.linhas_do_texto (o docTR, uma
    vez por pagina; guardadas por _chave_das_linhas, a previa e o PDF usam as
    mesmas). Quem chama esta numa QThread (previa e PDF): o leitor bloqueia
    1 a 2,5 s na primeira vez da pagina, nunca a tela. Se o leitor nao estiver
    disponivel, sai o Misto B (o motivo vai para o erros.log).

    Os avisos do "Para revisar" (regra ajustada, core/revisar.py) sao
    acertados aqui (A e C, com o leitor de texto); na B eles saem (sem as
    linhas, nao ha o que medir). Ver _acertar_avisos_do_misto.

    "Forca do preto sozinha" (Samuel, rodada 4, `rv4-erro-4-texto-falhado`):
    se a regra achou o texto falhado e o livro tem o reforco ligado, a forca
    do preto desta pagina e escurecida (_reforcar_se_o_texto_falhou) e a
    pagina e filtrada e medida DE NOVO, ja com a forca nova - e essa que
    sai. Custa um filtro a mais, so nessas paginas e so na primeira vez."""
    linhas, altura_linha, resultados = None, 0.0, []
    if opcoes.precisa_das_linhas:
        # linhas_definitivas: no desenho do tamanho do PDF as linhas do leitor
        # sao as achadas NESSA imagem (as da previa, achadas na pagina
        # pequena, sao provisorias como a marcacao: core.linhas_do_texto)
        resultados = linhas_do_texto.linhas_da_pagina(img, _chave_das_linhas(projeto, pagina),
                                                      definitivas=linhas_definitivas)
        if resultados:
            linhas, altura_linha = misto.mascara_das_linhas(resultados, img.shape)

    def uma_vez():
        """(saida, sinais): o Misto com a forca de agora e os avisos acertados."""
        medidas: dict = {}
        # as pecas do meio da conta, para a regra do "Para revisar" nao
        # refazer o filtro; so quando ha o que medir (o leitor deu certo e a
        # pagina e grande)
        pecas: dict | None = None
        if linhas is not None and medir:
            pecas = {}
        saida = misto.aplicar_misto(
            img, selecao, pagina.forca_preto, pagina.algoritmo_preto_branco, pontinhos,
            pagina.clareza_melhorar, pagina.intensidade_magico,
            papel_da_gravura_branco=opcoes.papel_da_gravura == misto.PAPEL_BRANCO,
            letras_na_moldura=opcoes.letras_na_moldura,
            fora_do_texto=opcoes.fora_do_texto, linhas=linhas, altura_linha=altura_linha,
            medidas=medidas, pecas=pecas)
        sinais = None
        if not opcoes.precisa_das_linhas:
            _tirar_avisos_do_so_as_letras(projeto, pagina)
        elif pecas:
            sinais = _acertar_avisos_do_misto(projeto, pagina, opcoes, saida[0], medidas, pecas,
                                              linhas, resultados, altura_linha)
        return saida, sinais

    saida, sinais = uma_vez()
    if _reforcar_se_o_texto_falhou(projeto, pagina, sinais):
        saida, depois = uma_vez()
        if not _o_reforco_resolveu(sinais, depois):
            # escureceu e as linhas falhadas nao cairam (o texto vermelho do
            # Egenloff 3, o Antiphonal 252): a forca volta a de antes, o
            # programa nao tenta de novo nesta pagina, e ela fica so com o
            # aviso "Texto falhado" e o botao "usar mais escuro"
            pagina.forca_preto = int(pagina.forca_antes_do_reforco)
            pagina.forca_antes_do_reforco = None
            pagina.reforco_desfeito = True
            saida, _sinais = uma_vez()
    return saida


# --- a forca do preto sozinha ---------------------------------------------------
#
# Samuel, rodada 4 do "Para revisar" (08/10/2026, `rv4-erro-4-texto-falhado`):
# "Força sozinha" + "mas temos que melhorar o reconhecimento de tintas, para
# não sair falhado assim, não precisar usar sempre o reforço." (o certo de
# verdade e o item 1.4 do plano; rodada 5: "Fica no plano; até lá, a força
# sozinha"). Quando a regra do "Para revisar" acha o texto falhado, o
# programa escurece a forca do preto SO nessa pagina, avisa
# (analise.FORCA_REFORCADA) e oferece "Desfazer".
#
# A forca do reforco: medido na rodada 4 (LEIA-ME, "Forca do preto"), 85 em
# vez de 50 fecha as letras do Camoes 27 e 104; nao resolve o vermelho do
# Egenloff 3. E o mesmo valor do botao "usar mais escuro". Seguro mudar: o
# numero (so muda o quanto escurece).
FORCA_DO_REFORCO = 85

# QUANDO a forca age sozinha (decisao da gerente, 13/10/2026, a "P3"): o aviso
# "Texto falhado" continua valendo com 2 linhas falhadas, mas a forca so e
# escurecida sozinha com LINHAS_PARA_REFORCAR ou mais linhas falhadas, ou com
# todas as linhas contadas falhadas; e, depois de escurecer, a pagina e medida
# de novo e o reforco so fica se as linhas falhadas CAIREM
# (_o_reforco_resolveu). Um aviso a mais custa pouco; uma pagina boa
# escurecida sozinha custa caro.
# O defeito que isto conserta (verificador, 13/10): no Palatino 66, pagina de
# caligrafia de traco fino, a regra achava 3 linhas falhadas, a forca era
# escurecida e sujava a moldura. Medido nas 89 paginas, livro novo, 300 DPI
# (relatorios/para-revisar-impl/ONDE-PAREI.md, "Investigacao 8"): com 2
# linhas a forca agia em 7 paginas - Camoes 27 (5 linhas falhadas de 28) e
# 104 (1 de 1), onde precisa e resolve; Camoes 11, ljs47 103 e Palatino 66 (3
# linhas cada: nenhum numero separa o Palatino, que nao precisava, dos outros
# dois); Antiphonal 252 (2, e a 85 continuam 2) e Egenloff 3 (2, e a 85 viram
# 5). Com 4 linhas ou todas, age so no Camoes 27 e no 104; as outras ficam
# com o aviso e o botao "usar mais escuro" (um clique).
# Seguro mudar: o numero, olhando essa tabela. Arriscado: baixar para 3 (o
# Palatino 66 volta a ser escurecido sozinho).
LINHAS_PARA_REFORCAR = 4


def _o_reforco_resolveu(antes, depois) -> bool:
    """Depois de escurecer a forca, as linhas falhadas cairam? `antes` e
    `depois` sao os sinais (core.revisar.Sinais) da pagina com a forca dela e
    com a do reforco; sem a medida de depois (None), nao da para dizer que
    resolveu: nao."""
    return depois is not None and depois.falhadas < antes.falhadas


def _reforcar_se_o_texto_falhou(projeto: Projeto, pagina: ConfigPagina, sinais) -> bool:
    """Escurece a forca do preto desta pagina se a regra achou o texto
    falhado (`sinais`, de core.revisar; None = nao foi medida). Devolve True
    se escureceu (quem chama filtra a pagina de novo).

    So quando: a pagina tem LINHAS_PARA_REFORCAR ou mais linhas falhadas, ou
    todas as linhas contadas falhadas (com menos, fica so o aviso; ver
    LINHAS_PARA_REFORCAR); o livro tem o reforco ligado
    (Projeto.reforcar_texto_falhado,
    o botao de desligar da regra 8 do plano); o programa ainda nao reforcou
    esta pagina; a pessoa nao desfez o reforco nem mexeu na forca depois dele
    (ConfigPagina.reforco_desfeito); e a forca dela esta abaixo da do
    reforco. Guarda a forca de antes (forca_antes_do_reforco) para o
    "Desfazer". Vale tambem na copia da pagina que os cartoes desenham: so
    a copia muda. Arriscado: reforcar sem guardar a forca de antes (o
    "Desfazer" nao teria para onde voltar)."""
    if sinais is None or not sinais.texto_falhado:
        return False
    todas = sinais.linhas_contadas > 0 and sinais.falhadas == sinais.linhas_contadas
    if sinais.falhadas < LINHAS_PARA_REFORCAR and not todas:
        return False
    if not getattr(projeto, "reforcar_texto_falhado", False):
        return False
    if pagina.forca_antes_do_reforco is not None or pagina.reforco_desfeito:
        return False
    if int(pagina.forca_preto) >= FORCA_DO_REFORCO:
        return False
    pagina.forca_antes_do_reforco = int(pagina.forca_preto)
    pagina.forca_preto = FORCA_DO_REFORCO
    return True


def acertar_aviso_do_reforco(projeto: Projeto, pagina: ConfigPagina) -> None:
    """Poe ou tira o aviso "Força do preto escurecida"
    (analise.FORCA_REFORCADA), sem desenhar nada: ele vale enquanto o reforco
    que o programa fez estiver valendo na pagina (forca_antes_do_reforco
    guardada, a forca ainda na do reforco, a pagina em Preto e branco e nao
    em branco).

    Se a pessoa mexeu na forca depois do reforco, a forca passa a ser dela: o
    "Desfazer" some e o programa nao reforca de novo (reforco_desfeito).
    Ao POR o aviso, a pagina volta a "nao conferida", como os outros avisos.
    Chamado por _filtrar (previa e PDF) e por acertar_alertas_do_fundo (a
    tela, a cada atualizacao). Barato: so le campos."""
    if not hasattr(pagina, "forca_antes_do_reforco"):
        return                    # objeto de pagina de antes do campo: nada a acertar
    if pagina.forca_antes_do_reforco is not None and int(pagina.forca_preto) != FORCA_DO_REFORCO:
        pagina.forca_antes_do_reforco = None
        pagina.reforco_desfeito = True
    vale = bool(pagina.forca_antes_do_reforco is not None
                and etapas.filtro_que_vale(projeto, pagina) == PRETO_E_BRANCO
                and not getattr(pagina, "em_branco", False))
    tem = analise.FORCA_REFORCADA in pagina.alertas
    if vale and not tem:
        pagina.alertas = [analise.FORCA_REFORCADA] + pagina.alertas
        pagina.revisada = False
    elif not vale and tem:
        pagina.alertas = [a for a in pagina.alertas if a != analise.FORCA_REFORCADA]
        _esquecer_aceitos(pagina, [analise.FORCA_REFORCADA])


def _esquecer_aceitos(pagina: ConfigPagina, codigos) -> None:
    """Os avisos `codigos` sairam da pagina: saem tambem dos "está bom" dados
    motivo a motivo (ConfigPagina.alertas_aceitos), para o aviso pedir um
    olhar de novo se o problema voltar."""
    aceitos = getattr(pagina, "alertas_aceitos", None)
    if aceitos and any(c in aceitos for c in codigos):
        pagina.alertas_aceitos = [a for a in aceitos if a not in codigos]


def medir_para_revisar(opcoes, img_saida: np.ndarray, medidas: dict, pecas: dict,
                       linhas: np.ndarray, resultados, altura_linha: float) -> "revisar.Sinais":
    """Os sinais do "Para revisar" (core.revisar.Sinais) de uma pagina que
    acabou de sair do "So as letras": junta o que core.misto.aplicar_misto
    entregou (`pecas`, `medidas`) com a imagem que saiu (`img_saida`) e as
    linhas do leitor de texto. Nao muda a pagina. Publica para o script que
    confere a regra nas 89 paginas do estudo
    (relatorios/para-revisar-impl/conferir_89.py).

    No jeito de fabrica ("Guardar a tinta forte") mede o desenho apagado; no
    "Guardar só o texto", que apaga de proposito o que nao e linha, mede so
    onde sumiu a tinta forte (para a marca do aviso)."""
    cinza_saida = img_saida if img_saida.ndim == 2 else cv2.cvtColor(img_saida, cv2.COLOR_BGR2GRAY)
    fabrica = opcoes.fora_do_texto == misto.FORA_REDE
    forte = pecas.get("forte")
    return revisar.medir(
        pecas["cinza"], pecas["base_tinta"], linhas, pecas["imagem"], cinza_saida < 128,
        revisar.poligonos_das_linhas(resultados, img_saida.shape), altura_linha,
        tinta_forte_apagada=None if fabrica else forte, com_o_desenho_apagado=fabrica)


def _acertar_avisos_do_misto(projeto: Projeto, pagina: ConfigPagina, opcoes, img_saida: np.ndarray,
                             medidas: dict, pecas: dict, linhas: np.ndarray, resultados,
                             altura_linha: float):
    """Poe e tira os avisos da regra ajustada do "Para revisar"
    (analise.AVISOS_DO_SO_AS_LETRAS) na pagina que acabou de ser desenhada no
    "So as letras" A ou C, e guarda onde o desenho sumiu (marcas_do_aviso).
    Devolve os sinais medidos (core.revisar.Sinais), ou None se nao deu.

    O aviso some sozinho quando o motivo some (a pessoa trocou o jeito, a
    forca do preto, marcou a area): a conta e refeita a cada desenho. Nunca
    levanta excecao: se a conta falhar, os avisos ficam como estavam e o
    motivo vai para o erros.log (a pagina sai do mesmo jeito).
    Arriscado: chamar com a imagem de um filtro que nao seja o da pagina."""
    try:
        sinais = medir_para_revisar(opcoes, img_saida, medidas, pecas, linhas, resultados,
                                    altura_linha)
    except Exception:  # noqa: BLE001 - a regra nunca derruba o desenho da pagina
        _log.exception("nao consegui medir a pagina %s para o Para revisar", pagina.indice + 1)
        return None
    fabrica = opcoes.fora_do_texto == misto.FORA_REDE
    pagina.faixa_na_beirada = bool(sinais.faixa_na_beirada)
    codigos = revisar.motivos(sinais, desenho_apagado_vale=fabrica,
                              tinta_forte_apagada=float(medidas.get("forte_fora", 0.0)),
                              faixa_do_livro=_faixa_e_do_livro(projeto))
    _por_avisos_do_so_as_letras(pagina, codigos)
    _guardar_marcas(projeto, pagina, {
        analise.DESENHO_APAGADO: sinais.onde_sumiu,
        analise.SO_O_TEXTO_APAGOU: sinais.onde_sumiu_a_tinta_forte,
        analise.TEXTO_FALHADO: sinais.linhas_falhadas,
    }, codigos)
    return sinais


# os avisos em que a regra mexe: os dela e o antigo, que so sai
_AVISOS_QUE_SAEM = frozenset(analise.AVISOS_DO_SO_AS_LETRAS) | {analise.TINTA_FORTE_FORA_DO_TEXTO}


def _por_avisos_do_so_as_letras(pagina: ConfigPagina, codigos: list[str]) -> None:
    """Deixa na pagina, dos avisos da regra ajustada, exatamente `codigos`
    (os outros alertas dela nao mudam). Do mesmo jeito que _anotar_conferir:
    ao POR um aviso que nao estava, a pagina volta a "nao conferida" e o
    aviso vai para a frente; o "esta bom assim" depois disso continua valendo
    (o aviso ja posto nao mexe mais em `revisada`). O aviso antigo ("Tinta
    forte fora do texto") sai sempre. Barato: so olha a lista."""
    novos = [c for c in codigos if c not in pagina.alertas]
    saem = [a for a in pagina.alertas if a in _AVISOS_QUE_SAEM and a not in codigos]
    if not novos and not saem:
        return
    pagina.alertas = novos + [a for a in pagina.alertas if a not in saem]
    if saem:
        _esquecer_aceitos(pagina, saem)
    if novos:
        pagina.revisada = False


def _tirar_avisos_do_so_as_letras(projeto: Projeto, pagina: ConfigPagina) -> None:
    """A pagina nao esta (mais) no "So as letras" A ou C: os avisos da regra
    ajustada saem, a faixa volta a "nao medida" e as marcas somem. Barato."""
    _por_avisos_do_so_as_letras(pagina, [])
    if pagina.faixa_na_beirada is not None:
        pagina.faixa_na_beirada = None
    _guardar_marcas(projeto, pagina, {}, [])


def _acertar_alerta_do_misto(projeto: Projeto, pagina: ConfigPagina) -> None:
    """Tira os avisos do "So as letras" da pagina que nao esta mais no Misto
    A ou C (mudou de filtro, desligou "So as letras", escolheu B), sem
    desenhar nada. Se ainda esta, ficam como estao (a previa acerta) - menos o
    aviso antigo ("Tinta forte fora do texto"), que sai de qualquer pagina:
    desde 12/10/2026 ninguem mais o poe, e o projeto salvo antes ainda o tem."""
    opcoes = (misto.opcoes_da_pagina(projeto, pagina)
              if etapas.filtro_que_vale(projeto, pagina) == PRETO_E_BRANCO else None)
    if opcoes is None or not opcoes.precisa_das_linhas:
        if (pagina.faixa_na_beirada is not None
                or any(a in _AVISOS_QUE_SAEM for a in pagina.alertas)):
            _tirar_avisos_do_so_as_letras(projeto, pagina)
    elif analise.TINTA_FORTE_FORA_DO_TEXTO in pagina.alertas:
        pagina.alertas = [a for a in pagina.alertas if a != analise.TINTA_FORTE_FORA_DO_TEXTO]


# --- a faixa na beirada do livro inteiro --------------------------------------

# Com menos paginas medidas que isto, nao se conclui nada sobre o livro (o
# mesmo minimo de analise.separar_observacoes).
MINIMO_DE_PAGINAS_PARA_A_FAIXA_DO_LIVRO = 4


def _faixa_e_do_livro(projeto: Projeto) -> bool:
    """A faixa na beirada ja e aviso do livro? (a frase esta nas observacoes)"""
    return analise.OBSERVACOES[analise.FAIXA_NA_BEIRADA] in (
        getattr(projeto, "observacoes", None) or [])


def acertar_faixa_do_livro(projeto: Projeto) -> bool:
    """A faixa escura na beirada em 70% ou mais das paginas medidas vira UM
    aviso do livro (Projeto.observacoes) e sai das paginas; se deixar de ser,
    a frase sai e o aviso volta para as paginas em que a faixa foi medida.
    Devolve True se mudou alguma coisa (para a tela se redesenhar).

    "Medida" = desenhada no "So as letras" (ConfigPagina.faixa_na_beirada nao
    e None); a faixa so e conhecida quando a pagina e desenhada, por isso a
    conta e sobre as paginas ja vistas, e precisa de pelo menos
    MINIMO_DE_PAGINAS_PARA_A_FAIXA_DO_LIVRO delas. Sem desenhar nada: so le
    campos. Chamado pela tela de conferir a cada atualizacao e no fim do PDF.
    Quando o aviso VOLTA para uma pagina, ela nao volta a "nao conferida" (a
    pessoa nao mexeu nela). Arriscado: tirar o minimo de paginas (a primeira
    pagina com faixa viraria "o livro inteiro")."""
    frase = analise.OBSERVACOES[analise.FAIXA_NA_BEIRADA]
    medidas = [p for p in projeto.paginas
               if not p.apagada and p.faixa_na_beirada is not None]
    do_livro = (len(medidas) >= MINIMO_DE_PAGINAS_PARA_A_FAIXA_DO_LIVRO
                and revisar.faixa_no_livro([bool(p.faixa_na_beirada) for p in medidas]))
    mudou = False
    observacoes = list(getattr(projeto, "observacoes", None) or [])
    if do_livro and frase not in observacoes:
        projeto.observacoes = observacoes + [frase]
        mudou = True
    elif not do_livro and frase in observacoes:
        projeto.observacoes = [o for o in observacoes if o != frase]
        mudou = True
    for pagina in projeto.paginas:
        tem = analise.FAIXA_NA_BEIRADA in pagina.alertas
        if do_livro and tem:
            pagina.alertas = [a for a in pagina.alertas if a != analise.FAIXA_NA_BEIRADA]
            mudou = True
        elif not do_livro and not tem and pagina.faixa_na_beirada and not pagina.apagada:
            pagina.alertas = pagina.alertas + [analise.FAIXA_NA_BEIRADA]
            mudou = True
    return mudou


# --- onde sumiu: as marcas do aviso -------------------------------------------
#
# Samuel, rodada 5 (09/10/2026, `rv5-erro-1-desenho`): "onde sumiu, tem que
# aparecer selecionado automaticamente"; `rv5-erro-6-so-texto`: "aparece
# marcado". As caixas (fracao da pagina) saem da mesma conta do aviso
# (core.revisar.medir) e ficam penduradas na propria pagina, num atributo
# SOLTO, fora dos campos dela (_ATRIBUTO_DAS_MARCAS): nao vao para o
# projeto.json (dataclasses.asdict so leva os campos), valem so nesta sessao
# e sao refeitas a cada desenho. A copia da pagina que os cartoes de filtro
# desenham (renderizar_com_filtro, dataclasses.replace) nao leva o atributo
# nem mexe no da pagina de verdade - por isso nao e um dicionario por
# pagina aqui no modulo. Seguro apagar o atributo a qualquer hora (a marca
# volta quando a pagina e desenhada de novo).
_ATRIBUTO_DAS_MARCAS = "_marcas_do_aviso"


def _guardar_marcas(projeto: Projeto, pagina: ConfigPagina, marcas: dict[str, list],
                    codigos: list[str]) -> None:
    """Guarda na pagina as marcas dos avisos que ela tem (`codigos`); as dos
    avisos que ela nao tem somem. Uma atribuicao so (a tela le de outro fio)."""
    validas = {codigo: list(caixas) for codigo, caixas in marcas.items()
               if codigo in codigos and caixas}
    if validas or getattr(pagina, _ATRIBUTO_DAS_MARCAS, None):
        setattr(pagina, _ATRIBUTO_DAS_MARCAS, validas)


def marcas_do_aviso(pagina: ConfigPagina, codigo: str | None = None) -> list:
    """As caixas (x0, y0, x1, y1, em fracao da pagina) que mostram ONDE esta o
    problema do aviso `codigo` nesta pagina (None = as de todos os avisos que
    ela tem agora). Vazia se a pagina ainda nao foi desenhada nesta sessao ou
    se o aviso nao tem lugar (pagina sem conteudo, faixa). So le."""
    guardadas = dict(getattr(pagina, _ATRIBUTO_DAS_MARCAS, None) or {})
    if codigo is not None:
        return list(guardadas.get(codigo, [])) if codigo in pagina.alertas else []
    return [caixa for c, caixas in guardadas.items() if c in pagina.alertas for caixa in caixas]


def _misto_vale(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A pagina vai sair pelo Misto ("So as letras")? A MESMA conta de
    _filtrar: "Limpar a folha" ligado, filtro Preto e branco e "So as letras"
    valendo nela (dela ou do livro). Barato (so le campos)."""
    return bool(etapas.filtro_que_vale(projeto, pagina) == PRETO_E_BRANCO
                and misto.opcoes_da_pagina(projeto, pagina) is not None)


def _cor_valeria_sem_o_misto(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A analise (analise.analisar_pagina + separar_observacoes) teria posto o
    alerta "Tem cor" nesta pagina? Sim quando ela tem cor, o filtro dela e o
    do livro sao o Preto e branco, ela nao e pagina em branco, e o "Tem cor"
    nao virou observacao do livro ("o livro inteiro e colorido") - nem o "em
    branco" (que tira o alerta das paginas em branco). Le so campos."""
    observacoes = getattr(projeto, "observacoes", None) or []
    return bool(pagina.tem_cor and pagina.filtro == PRETO_E_BRANCO
                and projeto.filtro_padrao == PRETO_E_BRANCO
                and analise.EM_BRANCO not in pagina.alertas
                and analise.OBSERVACOES[analise.COR] not in observacoes
                and analise.OBSERVACOES[analise.EM_BRANCO] not in observacoes)


def acertar_alertas_de_cor(projeto: Projeto,
                           paginas: list[ConfigPagina] | None = None) -> None:
    """O alerta "Tem cor" ("o preto e branco vai perder a ilustracao", com o
    botao "usar Mágico pro nesta") segue o "So as letras". Sem desenhar nada.

    Bug Misto 1 do verificador (05/10/2026, print 14): com "So as letras"
    ligada, a ilustracao sai EM COR (core.misto), e o alerta era falso - ele
    e decidido uma vez, na analise (analise.analisar_pagina), sem olhar o
    Misto, e mandava paginas certas para o "Para revisar". Agora:
      - pagina que vai sair pelo Misto (_misto_vale): o alerta sai;
      - pagina que deixou o Misto ("So as letras" desligada, no livro ou so
        nela): o alerta volta, se a analise o teria posto
        (_cor_valeria_sem_o_misto). `revisada` nao muda: o alerta volta como
        estava (se a pessoa ja tinha conferido a pagina, continua conferida).
    Pagina que nunca passou pelo Misto nao muda: o alerta so volta onde a
    analise o poria, e nessa pagina ele ja esta.

    Chamado pela analise (no fim), por acertar_alertas_do_fundo (ao abrir a
    conferencia) e pela tela de conferir a cada atualizacao, em TODAS as
    paginas (o "So as letras" do livro e o "todas" mudam muitas de uma vez,
    e o "Para revisar" conta todas). Barato: pagina sem cor e sem o alerta
    e pulada sem conta nenhuma.

    Arriscado: tirar o alerta sem a mesma conta de _filtrar (_misto_vale) - a
    pagina que sai em preto e branco de verdade ficaria sem o aviso.
    """
    for pagina in projeto.paginas if paginas is None else paginas:
        tem = analise.COR in pagina.alertas
        if not tem and not pagina.tem_cor:
            continue
        if _misto_vale(projeto, pagina):
            if tem:
                pagina.alertas = [a for a in pagina.alertas if a != analise.COR]
        elif not tem and _cor_valeria_sem_o_misto(projeto, pagina):
            pagina.alertas.append(analise.COR)


def _tem_pedaco_com_filtro(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A pagina tem algum pedaco com "so neste pedaco" (um filtro proprio)?
    Barato: le so a marcacao guardada, sem detector e sem imagem.

    Sem "Procurar gravura e letra" (projeto.detectar_regioes) a resposta e
    nao, como no Original (garantir_selecao devolve a marcacao vazia): sem
    ele a aba Marcar nem aparece, e um pedaco que ficou guardado mudaria o
    PDF sem poder ser visto. Arriscado: tirar esta condicao."""
    if not pagina.selecao:
        return False
    if not projeto.detectar_regioes:
        # obra 26/10, etapa 1 (D-009): o pedaco e feito a mao - vale no livro
        # novo (no projeto antigo, so com a marca: core/etapas)
        return etapas.tem_pedaco_a_mao(projeto, pagina)
    return bool(pagina.obter_selecao().filtros_pedidos())


def _so_os_pedacos_no_tirar_o_fundo(projeto: Projeto, pagina: ConfigPagina,
                                    base: np.ndarray, como_veio: np.ndarray) -> np.ndarray:
    """Os pedacos de "so neste pedaco" de uma pagina no filtro "Tirar o
    fundo", por cima de `base` (a pagina sem o fundo, ou como veio quando
    core/camadas.py a deixou intacta), calculados em `como_veio` (a pagina
    como veio, ja dividida, cortada e endireitada igual a `base`).

    Conferencia 14 (Samuel): "FUNDO: Sim, do mesmo jeito (só muda se alguém
    marcar um pedaço)" - o mesmo jeito do Original (conferencia 13, S4,
    core.filtros.aplicar_so_os_pedacos). Sem pedaco devolve `base`, o MESMO
    objeto: a pagina sai exatamente como antes. Usa a marcacao guardada, sem
    detector (o pedaco e desenhado a mao). Os ajustes do pedaco (forca do
    preto etc.) sao os da pagina, como no Original."""
    if not _tem_pedaco_com_filtro(projeto, pagina):
        return base
    return aplicar_so_os_pedacos(
        como_veio, base, pagina.obter_selecao(), TIRAR_FUNDO, pagina.forca_preto,
        pagina.clareza_melhorar, pagina.intensidade_magico)


def _pedacos_na_pagina_sem_fundo(doc, projeto: Projeto, folha: ConfigFolha,
                                 pagina: ConfigPagina, img: np.ndarray,
                                 forma_da_folha: tuple, geometria, dpi: float,
                                 img_folha: np.ndarray | None) -> np.ndarray:
    """A pagina de que o fundo FOI tirado (`img`, ja dividida, cortada e
    endireitada) com os pedacos de "so neste pedaco" por cima (conferencia
    14, "FUNDO"). O mesmo para a previa (renderizar_pagina) e o PDF
    (processar): previa = PDF.

    Para o pedaco sair do filtro dele a partir da pagina COMO VEIO (um pedaco
    em "Original" mostra o papel de verdade, e nao o branco do fundo tirado),
    a folha e desenhada normalmente - `img_folha`, se quem chamou ja a tem,
    ou desenhada aqui em `dpi` - e passa pelo MESMO giro, divisao, corte e
    endireitamento (`geometria`, a medida na folha como veio). Se o tamanho
    dela nao bater com o da folha sem o fundo (`forma_da_folha`; o MuPDF e o
    core/camadas.py arredondam diferente, 1 ponto), ela e reduzida a ele
    antes, para as duas coincidirem ponto a ponto.

    Sem pedaco (o normal), devolve `img`, o MESMO objeto, sem desenhar nada
    a mais: a pagina sai exatamente como antes e o tempo nao muda. Com
    pedaco, custa um desenho a mais da folha (so nessa pagina). Sem "Limpar
    a folha" o fundo nem e tirado (usa_tirar_fundo), entao nao chega aqui.
    """
    if not _tem_pedaco_com_filtro(projeto, pagina):
        return img
    if img_folha is None:
        img_folha = pagina_para_array(doc, folha.indice, dpi=dpi)
    altura, largura = forma_da_folha[:2]
    if img_folha.shape[:2] != (altura, largura):
        img_folha = cv2.resize(img_folha, (largura, altura), interpolation=cv2.INTER_AREA)
    como_veio = preparar_metade(img_folha, folha, pagina, projeto, geometria=geometria)
    if como_veio.shape[:2] != img.shape[:2]:     # nunca visto; so por seguranca
        como_veio = cv2.resize(como_veio, (img.shape[1], img.shape[0]),
                               interpolation=cv2.INTER_AREA)
    if como_veio.ndim != img.ndim:
        como_veio = (cv2.cvtColor(como_veio, cv2.COLOR_GRAY2BGR) if como_veio.ndim == 2
                     else cv2.cvtColor(como_veio, cv2.COLOR_BGR2GRAY))
    return _so_os_pedacos_no_tirar_o_fundo(projeto, pagina, img, como_veio)


def renderizar_com_filtro(
    doc, projeto: Projeto, pagina: ConfigPagina, filtro: str, dpi: int = DPI_PREVIA
) -> tuple[np.ndarray, bool]:
    """A pagina como sairia com `filtro`, SEM mudar a pagina.

    E o que o cartao "Tirar o fundo" da aba Filtro e o "comparar" da tela
    ampliada mostram (item 1.1, 29/09/2026: o resultado de verdade, e nao o
    filtro comum): o mesmo renderizar_pagina, numa copia da pagina com o
    outro filtro. Os alertas que o desenho acertar (o "conferir") ficam na
    copia; a decisao do core/camadas.py fica guardada por folha
    (_DECISOES_DO_FUNDO), e a pagina de verdade ganha o alerta quando passar
    para esse filtro (acertar_alertas_do_fundo). Arriscado: desenhar a pagina
    de verdade aqui mudaria os alertas dela sem ela ter mudado de filtro.
    """
    from dataclasses import replace

    copia = replace(pagina, filtro=filtro, alertas=list(pagina.alertas))
    return renderizar_pagina(doc, projeto, copia, dpi=dpi)


def _reduzir_para_o_dpi(doc, indice: int, img: np.ndarray, dpi: int) -> np.ndarray:
    """A folha desenhada em alta resolucao, reduzida ao tamanho que o MuPDF
    daria em `dpi` (pontos da pagina x dpi / 72, arredondado para cima, com o
    mesmo teto de pixels de pdf_io.dpi_seguro). Media de area (INTER_AREA)."""
    from core.pdf_io import MAX_PIXELS

    largura_pt, altura_pt = tamanho_da_pagina_pt(doc, indice)
    area_pol = (largura_pt / 72.0) * (altura_pt / 72.0)
    if area_pol > 0:
        dpi = max(50, min(dpi, int((MAX_PIXELS / area_pol) ** 0.5)))
    largura = max(1, int(np.ceil(largura_pt * dpi / 72.0 - 0.001)))
    altura = max(1, int(np.ceil(altura_pt * dpi / 72.0 - 0.001)))
    if (largura, altura) == (img.shape[1], img.shape[0]):
        return img
    return cv2.resize(img, (largura, altura), interpolation=cv2.INTER_AREA)


def renderizar_pagina_para_recorte(
    doc, projeto: Projeto, pagina: ConfigPagina, dpi: int = DPI_PREVIA
) -> np.ndarray:
    """A imagem que a aba Bordas mostra enquanto o recorte está sendo
    ajustado - girada e dividida, nunca cortada. Ver `preparar_para_recorte`.

    Item 2.2, G6 (09/10/2026): no livro "endireitar_antes" o corte a mao e
    marcado sobre a pagina RETA (o recorte esta em fracao dela), entao a
    imagem desta aba e tambem endireitada, com o angulo que vale na pagina
    (o a mao, ou o automatico guardado; se ainda nao foi medido, mede e
    guarda na resolucao do PDF, como a previa). Nunca cortada. No projeto
    "cortar_antes", como sempre (sem endireitar).
    Arriscado: mostrar aqui a pagina com outro angulo que nao o do PDF (o
    retangulo marcado cairia em outro lugar).
    """
    folha = projeto.folhas[pagina.folha]
    img_folha = pagina_para_array(doc, folha.indice, dpi=dpi)
    base = preparar_para_recorte(img_folha, folha, pagina, projeto)
    if not endireita_antes(projeto) or not etapas.endireita(projeto, pagina):
        return base
    grande = img_folha if dpi == projeto.qualidade_dpi else None
    geometria = _geometria_da_folha_como_veio(doc, folha, pagina, projeto, grande)
    angulo = etapas.angulo_a_mao(projeto, pagina) if geometria is None else geometria[1]
    return rotacionar(base, angulo_aplicado(angulo))


# ---------------------------------------------------------------------------
# Fase 3: processar o livro inteiro
# ---------------------------------------------------------------------------

# Quantas vezes a troca do arquivo a parte pelo PDF final e tentada, e quanto
# se espera entre uma e outra, antes de concluir que o PDF antigo esta aberto
# em outro programa (ver _trocar_pelo_final). O antivirus e o indexador do
# Windows seguram um arquivo recem-fechado por uma fracao de segundo; o leitor
# de PDF o segura enquanto estiver aberto. Seguro mudar: os dois numeros (mais
# tentativas so atrasam o aviso). Os testes poem a espera em zero.
TENTATIVAS_DA_TROCA = 5
ESPERA_DA_TROCA_S = 0.25


class ErroPDFSalvoComOutroNome(ErroPDF):
    """O PDF novo ficou pronto, mas o antigo nao pode ser substituido (aberto
    em outro programa); o novo foi gravado com outro nome, em `caminho`.

    `antigo` e o arquivo que ficou preso (o destino pedido).

    E um ErroPDF (quem chama processar sem tratar este caso ve o aviso em
    portugues, como antes), mas NAO e falha: o PDF ficou pronto. A
    TarefaProcessar (ui/tarefas.py) o entrega como `concluida`, com o caminho
    do "(2)", e a tela "Ficou pronto!" mostra o nome novo e uma frase dizendo
    que o antigo estava aberto noutro programa (conserto de 05/10/2026,
    achado do verificador: antes a tela voltava para Conferir, o cartao nao
    virava "PDF gerado" e o caso ia para o erros.log). Arriscado: deixar de
    preencher `caminho` (a tela mostraria o nome errado).
    """

    def __init__(self, mensagem: str, caminho: Path, antigo: Path | None = None) -> None:
        super().__init__(mensagem)
        self.caminho = caminho
        self.antigo = antigo


def _caminho_parcial(saida_final: Path) -> Path:
    """O arquivo a parte em que o PDF novo e gravado ate ficar pronto.

    Fica na MESMA pasta do destino: so assim a troca pelo antigo (os.replace)
    e uma operacao so, sem copiar nada, e nunca deixa o destino pela metade.
    O nome comeca com "~" e termina em ".parcial" (nao em .pdf) para o Kaique
    nao o confundir com o livro nem tentar abri-lo. Ex.: pronto.pdf ->
    ~pronto.pdf.parcial.

    Arriscado mudar: o nome e o que permite apagar a sobra de uma queda do
    programa (ver processar), e so ele - mudar para algo que possa coincidir
    com um arquivo do Kaique faria o programa apagar o que nao e dele.
    """
    return saida_final.with_name(f"~{saida_final.name}.parcial")


def _nome_livre(caminho: Path) -> Path:
    """`nome (2).pdf`, `nome (3).pdf`... o primeiro que ainda nao existe.
    O mesmo jeito de configuracoes.caminho_sem_repetir (o "salvar como (2)"
    da tela), repetido aqui porque core/ nao depende do que a tela usa."""
    contador = 2
    while True:
        tentativa = caminho.with_name(f"{caminho.stem} ({contador}){caminho.suffix or '.pdf'}")
        if not tentativa.exists():
            return tentativa
        contador += 1


def _trocar_pelo_final(parcial: Path, saida_final: Path) -> Path:
    """Poe o PDF novo (pronto, em `parcial`) no lugar do destino. Devolve onde
    ele ficou.

    os.replace troca de uma vez: ou o destino continua o antigo, inteiro, ou
    ja e o novo, inteiro. No Windows ele falha (PermissionError) quando o
    antigo esta aberto em outro programa; tenta-se de novo algumas vezes (ver
    TENTATIVAS_DA_TROCA) e, se continuar preso, o novo vai para
    `nome (2).pdf` e sobe ErroPDFSalvoComOutroNome, com o nome no aviso: o
    antigo fica como estava e o trabalho de processar nao se perde.

    Arriscado mudar: apagar o antigo antes de trocar (abre de novo o buraco
    em que o antigo some e o novo nao chega), ou copiar em vez de trocar (um
    disco cheio no meio da copia deixaria o destino pela metade).
    """
    for tentativa in range(TENTATIVAS_DA_TROCA):
        try:
            os.replace(parcial, saida_final)
            return saida_final
        except PermissionError:
            if tentativa + 1 < TENTATIVAS_DA_TROCA and ESPERA_DA_TROCA_S > 0:
                import time

                time.sleep(ESPERA_DA_TROCA_S)
        except OSError:
            break       # outro motivo (destino virou pasta...): nao adianta esperar

    alternativo = _nome_livre(saida_final)
    try:
        os.replace(parcial, alternativo)
    except OSError as exc:
        raise ErroPDF(
            f"O livro ficou pronto, mas não consegui gravá-lo como "
            f"\"{saida_final.name}\": o arquivo antigo pode estar aberto em outro "
            f"programa. O arquivo antigo ficou como estava. Feche o PDF antigo "
            f"e processe de novo."
        ) from exc
    _log.warning("PDF antigo preso (aberto em outro programa?): %s; o novo foi para %s",
                 saida_final, alternativo)
    raise ErroPDFSalvoComOutroNome(
        f"Não consegui substituir o arquivo antigo \"{saida_final.name}\": ele "
        f"parece estar aberto em outro programa (o leitor de PDF, por exemplo). "
        f"O arquivo antigo ficou como estava, e o PDF novo foi gravado ao lado "
        f"dele, na mesma pasta, com o nome \"{alternativo.name}\".",
        alternativo,
        saida_final,
    )


def processar(
    projeto: Projeto, progresso: Progresso = None, cancelado: Cancelado = None
) -> str:
    """Gera o PDF final. Devolve o caminho gravado.

    Levanta Cancelou se o usuario cancelar - e a única excecao esperada.

    O PDF ANTIGO NUNCA E TOCADO ANTES DO FIM (conserto de 05/10/2026, bug
    grave da Lista de bugs; o Samuel mandou consertar na conferencia 11). Ate
    ali, sem "Montar cadernos", o PDF era gravado direto no arquivo final:
    com "substituir o antigo" + "cancelar", o antigo era sobrescrito pelas
    paginas feitas ate ali e depois apagado - sumia, sem aviso. Agora:

    - o PDF novo e gravado num arquivo a parte, na mesma pasta
      (_caminho_parcial: `~nome.pdf.parcial`), e so troca de lugar com o
      antigo quando terminou (_trocar_pelo_final, os.replace);
    - cancelou ou deu erro (inclusive disco cheio ao gravar): apaga so o
      arquivo a parte (e o temporario dos cadernos); o antigo fica intacto;
    - o mesmo vale com "Montar cadernos" e no caminho rapido "so cadernos"
      (a imposicao tambem gravava direto no final);
    - a sobra do arquivo a parte de uma vez que o programa caiu e apagada no
      comeco (so a deste destino, pelo nome exato);
    - o antigo aberto em outro programa: o novo vai para `nome (2).pdf` e
      sobe ErroPDFSalvoComOutroNome, com aviso em portugues.

    Arriscado mudar: voltar a abrir o EscritorPDF no arquivo final, ou apagar
    o final em qualquer caminho de erro/cancelamento. Testes:
    tests/test_substituir_e_cancelar.py.
    """
    saida_final = Path(projeto.caminho_saida)
    # Pendrive arrancado, unidade de rede caida, pasta apagada entre escolher e
    # gravar: tudo isso cai aqui, e nao pode virar erro tecnico na tela.
    try:
        saida_final.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ErroPDF(
            "Não consegui gravar nessa pasta. Ela pode ter sido removida, "
            "estar cheia ou ser um pendrive que foi tirado. "
            "Escolha outra pasta e tente de novo."
        ) from exc

    # O PDF novo nasce num arquivo a parte, ao lado do destino (ver o
    # docstring). Uma sobra dele - o programa caiu ou faltou luz no meio de
    # uma gravacao anterior deste mesmo destino - sai antes de comecar.
    parcial = _caminho_parcial(saida_final)
    try:
        parcial.unlink(missing_ok=True)
    except OSError:
        pass            # presa por outro programa: a gravacao abaixo avisa

    # Caminho rapido: so reordenar, sem tocar em imagem nenhuma.
    if projeto.so_cadernos:
        _avisar(progresso, 0, 1, "Montando os cadernos")
        try:
            impor_pdf(
                projeto.caminho_entrada, parcial, projeto.paginas_por_caderno,
                progresso=lambda f, t: _avisar(progresso, f, t, f"Montando a folha {f} de {t}"),
            )
            return str(_trocar_pelo_final(parcial, saida_final))
        finally:
            parcial.unlink(missing_ok=True)     # ja trocado, nao existe mais

    # Quando vamos montar cadernos, primeiro gravamos as paginas em ordem
    # normal num arquivo temporario e so depois reordenamos. Assim a imposicao
    # trabalha com um PDF em disco e nao precisa de nada na memoria. A
    # imposicao grava no arquivo a parte, como sem cadernos.
    temporario: Path | None = None
    if projeto.montar_cadernos:
        temporario = Path(tempfile.gettempdir()) / f"_editor_impressao_{saida_final.stem}.pdf"
        destino = temporario
    else:
        destino = parcial

    ativas = projeto.paginas_ativas
    total = len(ativas)
    if total == 0:
        raise ErroPDF("Não sobrou nenhuma página para gerar. Restaure alguma página apagada.")

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        # Item 2.5: com "cortar seguindo o conteudo", o tamanho do livro tem de
        # estar medido antes da primeira pagina (senao a primeira e a ultima
        # sairiam de tamanhos diferentes). Desligado: nao faz nada.
        if getattr(projeto, "cortar_pelo_conteudo", False):
            medir_conteudo_do_livro(projeto, doc, progresso, cancelado)
        # Item 2.4: com as margens iguais ligadas (desligadas de fabrica), uma
        # passada antes mede o tamanho de cada pagina pronta - so dois numeros
        # por pagina - para saber o tamanho do livro (o da maior). Desligadas,
        # conta e None e nada muda.
        conta = None
        if getattr(projeto, "margens_iguais", False):
            conta = medir_o_livro_para_as_margens(projeto, doc, ativas, progresso, cancelado)
        with EscritorPDF(destino) as escritor:
            try:
                _escrever_as_paginas(projeto, doc, ativas, escritor, progresso, cancelado,
                                     conta_das_margens=conta)
            except BaseException:
                # cancelou ou deu erro: nada vai para o disco (antes o
                # __exit__ gravava as paginas feitas ate ali - no PDF antigo,
                # quando era ele o destino)
                escritor.descartar()
                raise

        if projeto.montar_cadernos and temporario is not None:
            _avisar(progresso, total, total, "Montando os cadernos")
            impor_pdf(temporario, parcial, projeto.paginas_por_caderno)

        # O livro de entrada e solto antes da troca: se o Kaique escolheu
        # gravar por cima do proprio PDF de entrada, o Windows nao deixa
        # trocar um arquivo aberto.
        doc.close()
        final = _trocar_pelo_final(parcial, saida_final)
        _avisar(progresso, total, total, "Pronto")
        return str(final)

    finally:
        # Cancelou, deu erro ou terminou: o temporario dos cadernos e o
        # arquivo a parte saem (depois da troca, o arquivo a parte ja nao
        # existe). O PDF final nunca e apagado aqui.
        if temporario is not None:
            temporario.unlink(missing_ok=True)
        parcial.unlink(missing_ok=True)
        if not doc.is_closed:
            doc.close()


class _FolhaDaVez:
    """A folha da vez de quem faz as paginas (uma so na memoria; as duas
    metades vem dela): o desenho normal e, se alguma metade usa o item 1.1, a
    folha sem o fundo. Os dois sao feitos so quando alguem precisa. Cada
    trabalhador do item 2.16 tem a sua (core/nucleos.py)."""

    __slots__ = ("indice", "img", "sem_fundo")

    def __init__(self) -> None:
        self.indice: int | None = None
        self.img: np.ndarray | None = None
        self.sem_fundo = None          # core.camadas.PaginaSemFundo da folha da vez


def _pagina_pronta(projeto: Projeto, doc, folha: ConfigFolha, pagina: ConfigPagina,
                   da_vez: _FolhaDaVez, posicao: int, conta_das_margens=None
                   ) -> tuple[np.ndarray, bool]:
    """Uma pagina do PDF final, pronta para o escritor: (imagem, monocromatica).

    E o corpo do laco do processar de sempre, separado em 22/10/2026 (item
    2.16) para varios trabalhadores poderem fazer paginas ao mesmo tempo; a
    conta e a mesma, linha por linha. `posicao` e o lugar da pagina na lista
    de paginas ativas (as margens iguais do item 2.4 usam)."""
    if da_vez.indice != folha.indice:
        da_vez.img, da_vez.sem_fundo = None, None
        da_vez.indice = folha.indice

    # Item 1.1: esta pagina sai sem o fundo? (ver usa_tirar_fundo)
    imagem_sem_fundo = None
    if usa_tirar_fundo(projeto, pagina):
        if da_vez.sem_fundo is None:
            da_vez.sem_fundo = _sem_fundo_da_folha(doc, folha, projeto.qualidade_dpi)
        imagem_sem_fundo = da_vez.sem_fundo.imagem
        _anotar_conferir(pagina, bool(imagem_sem_fundo is not None
                                      and da_vez.sem_fundo.conferir))
    else:
        _anotar_conferir(pagina, False)

    # O desenho normal da folha: para o filtro e para medir o corte
    # (que e sempre medido nele, mesmo quando sai sem o fundo).
    precisa_do_desenho = imagem_sem_fundo is None or (
        _precisa_de_geometria(pagina, projeto)
        and _geometria_guardada(folha, pagina, projeto) is None)
    if precisa_do_desenho and da_vez.img is None:
        da_vez.img = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
    img_folha = da_vez.img

    if imagem_sem_fundo is not None:
        # dividir, cortar e endireitar a folha sem o fundo, com o
        # corte da folha como veio; o filtro fica de fora
        geometria = _geometria_da_folha_como_veio(doc, folha, pagina, projeto, img_folha)
        img, desenho = _preparar_metade_e_geometria(
            imagem_sem_fundo, folha, pagina, projeto, geometria=geometria)
        # as zonas sao levadas para o preparo de agora ANTES de os
        # pedacos de "so neste pedaco" serem lidos (decisao D2)
        _acompanhar_as_zonas(pagina, desenho)
        # conferencia 14 ("FUNDO"): o "so neste pedaco" vale aqui tambem.
        # Sem pedaco, `img` volta como esta e nada mais e desenhado.
        if _tem_pedaco_com_filtro(projeto, pagina) and img_folha is None:
            da_vez.img = img_folha = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
        img = _pedacos_na_pagina_sem_fundo(
            doc, projeto, folha, pagina, img, imagem_sem_fundo.shape, geometria,
            projeto.qualidade_dpi, img_folha)
        mono = False
    else:
        # o corte e calculado nesta mesma imagem (a do PDF) e
        # guardado: a previa, se vier depois, mostra este (ver
        # _GEOMETRIAS)
        if _precisa_de_geometria(pagina, projeto):
            _guardar_geometria(folha, pagina, projeto, img_folha, doc)
        dpi_desenho = dpi_scan = None
        if (_vai_detectar(projeto, pagina, projeto.qualidade_dpi)     # item 1.2
                or _vai_limpar_pelo_scantailor(projeto, pagina)):
            dpi_desenho = _dpi_do_desenho(doc, folha.indice, img_folha)
            dpi_scan = _dpi_do_scan(doc, folha)
        img, desenho = _preparar_metade_e_geometria(
            img_folha, folha, pagina, projeto, dpi=projeto.qualidade_dpi)
        _acompanhar_as_zonas(pagina, desenho)
        img, mono = _filtrar(projeto, pagina, img, dpi_desenho, dpi_scan,
                             dpi_pedido=projeto.qualidade_dpi)

    # Item 2.4: as margens iguais do ScanTailor (so com a conta feita, isto
    # e, ligadas). Antes do tamanho de folha escolhido a mao, que continua
    # valendo por cima (e nao corta nada se nao couber).
    if conta_das_margens is not None:
        img = _por_as_margens(img, conta_das_margens, posicao, projeto)

    # Item 2/4 do teste do Boecio (secao 3a do plano): cola o conteudo (ja
    # filtrado) dentro do tamanho de folha escolhido, com a margem branca ao
    # redor - nunca antes daqui, porque `preparar_metade` tambem alimenta
    # `avaliar.py` (a regua de qualidade dos filtros) e padding ali
    # contaminaria as metricas. Sem `tamanho_folha_cm` (None, o padrao)
    # devolve `img` sem nenhuma alteracao - comportamento de sempre.
    #
    # Obra 26/10, etapa 1 (D-008/D-009): o conteudo movido ou redimensionado A
    # MAO chega ao PDF tambem sem tamanho de folha, e nunca e jogado fora por
    # 1 ponto de arredondamento (core/etapas.conteudo_mexido; projeto antigo
    # sem a marca: a conta de sempre). Vem depois do filtro e das margens: a
    # pagina pronta e que anda (a montagem continua endireitar -> cortar ->
    # filtro, D-016).
    img = compor_na_folha(
        img, pagina.tamanho_folha_cm, projeto.qualidade_dpi,
        escala=pagina.conteudo_escala,
        deslocamento=pagina.conteudo_deslocamento,
        mexido_a_mao=etapas.conteudo_mexido(projeto, pagina),
    )
    return img, mono


def _escrever(escritor: EscritorPDF, img: np.ndarray, mono: bool, projeto: Projeto) -> None:
    """Uma pagina pronta ate o PDF. Itens 2.10 e 1.6 (opcao do livro,
    desmarcada de fabrica): com Projeto.pdf_em_duas_camadas, a pagina que nao
    e 1 bit vai em duas camadas (core/duas_camadas.py); a de 1 bit e toda
    pagina com a caixinha desmarcada saem como sempre."""
    if getattr(projeto, "pdf_em_duas_camadas", False) and not mono:
        escritor.escrever_em_duas_camadas(img, dpi=projeto.qualidade_dpi)
    else:
        escritor.escrever_imagem(img, dpi=projeto.qualidade_dpi, monocromatico=mono)


def _grupos_por_folha(projeto: Projeto, ativas: list[ConfigPagina]) -> list[list[tuple[int, ConfigPagina]]]:
    """As paginas ativas juntadas por folha (as duas metades seguidas de uma
    folha dividida vao para o mesmo trabalhador, que desenha a folha uma vez
    so). Cada item: (posicao na lista de ativas, pagina). So referencias:
    nenhuma imagem."""
    grupos: list[list[tuple[int, ConfigPagina]]] = []
    for posicao, pagina in enumerate(ativas):
        if grupos and grupos[-1][-1][1].folha == pagina.folha:
            grupos[-1].append((posicao, pagina))
        else:
            grupos.append([(posicao, pagina)])
    return grupos


def _escrever_as_paginas(projeto: Projeto, doc, ativas: list[ConfigPagina],
                         escritor: EscritorPDF, progresso: Progresso,
                         cancelado: Cancelado, conta_das_margens=None,
                         trabalhadores: int | None = None) -> None:
    """O laco do processar: cada pagina ativa ate o escritor, NA ORDEM.

    Separado do processar em 05/10/2026 so para o tratamento de cancelar e
    erro caber em volta dele (ver processar); o conteudo e o mesmo de antes.
    Levanta Cancelou entre uma pagina e outra, e depois da ultima.

    Item 2.16 (22/10/2026): com mais de um trabalhador (core/nucleos.py: de
    fabrica todos os nucleos, como o ScanTailor), varias folhas sao feitas ao
    mesmo tempo, cada uma por um trabalhador com a sua folha da vez, e as
    paginas vao para o escritor na ordem do livro. Com 1 (Configuracoes,
    "Uma pagina por vez"), e o laco de sempre, sem linha nenhuma.

    Arriscado: guardar aqui qualquer lista de paginas processadas (regra
    "uma pagina por vez na memoria", por trabalhador): cada imagem vai para o
    escritor e sai; a fila de core/nucleos.em_ordem tem o tamanho do numero
    de trabalhadores, nunca o do livro.
    """
    total = len(ativas)
    if trabalhadores is None:
        trabalhadores = nucleos.quantos_trabalhadores()

    if trabalhadores <= 1:
        da_vez = _FolhaDaVez()
        for feito, pagina in enumerate(ativas):
            _checar(cancelado)
            _avisar(progresso, feito, total, f"Página {feito + 1} de {total}")
            folha = projeto.folhas[pagina.folha]
            if folha.apagada:
                continue
            img, mono = _pagina_pronta(projeto, doc, folha, pagina, da_vez, feito,
                                       conta_das_margens)
            _escrever(escritor, img, mono, projeto)
            del img
        # Regra ajustada do "Para revisar" (12/10/2026): todas as paginas foram
        # medidas agora; a faixa na beirada em quase todas vira aviso do livro
        acertar_faixa_do_livro(projeto)
        _checar(cancelado)
        return

    def fazer(grupo):
        da_vez = _FolhaDaVez()
        prontas = []
        for posicao, pagina in grupo:
            folha = projeto.folhas[pagina.folha]
            if folha.apagada:
                prontas.append(None)
                continue
            prontas.append(_pagina_pronta(projeto, doc, folha, pagina, da_vez, posicao,
                                          conta_das_margens))
        return prontas

    _avisar(progresso, 0, total, f"Página 1 de {total}")
    for grupo, prontas in nucleos.em_ordem(_grupos_por_folha(projeto, ativas), fazer,
                                           trabalhadores, cancelado):
        _checar(cancelado)
        for (posicao, _pagina), pronta in zip(grupo, prontas):
            if pronta is None:
                continue
            img, mono = pronta
            _escrever(escritor, img, mono, projeto)
            del img
        del prontas
        feito = grupo[-1][0] + 1
        _avisar(progresso, feito, total, f"Página {min(feito + 1, total)} de {total}")
    # o mesmo do "Para revisar" acima (juncao de 23/10/2026)
    acertar_faixa_do_livro(projeto)
    _checar(cancelado)


def tamanho_da_pagina_pronta(img_folha: np.ndarray, folha: ConfigFolha,
                             pagina: ConfigPagina, projeto: Projeto,
                             doc=None) -> tuple[tuple[int, int], tuple[float, float]]:
    """Item 2.4: o tamanho em pontos (largura, altura) que a pagina vai ter
    depois do preparo (girar, dividir, cortar, endireitar), e o centro do
    conteudo em fracao da pagina antes do corte - sem girar nem copiar a
    imagem (as mesmas contas de _preparar_metade_e_geometria: o endireitar
    nao muda o tamanho, e o corte e o caixa_em_pontos da pagina inteira).

    Guarda o corte e o angulo (_guardar_geometria, com o mesmo doc do
    processar): a segunda passada usa os mesmos, sem medir de novo.
    Arriscado: medir de outro jeito que o preparo (o tamanho medido deixaria
    de ser o da pagina gravada)."""
    inteira = preparar_para_recorte(img_folha, folha, pagina, projeto)
    if _precisa_de_geometria(pagina, projeto):
        _guardar_geometria(folha, pagina, projeto, img_folha, doc)
    chave = _chave_da_geometria(folha, pagina, projeto)
    if chave is not None:
        with _TRANCA_GEOMETRIAS:
            pronto = _TAMANHOS_PRONTOS.get(chave)
        if pronto is not None:
            return pronto
    geometria = _geometria_guardada(folha, pagina, projeto)
    if geometria is None:
        geometria = _geometria(inteira, pagina, projeto, dpi=projeto.qualidade_dpi)
    recorte = geometria[0]
    altura, largura = inteira.shape[:2]
    caixa = None if recorte is None else caixa_em_pontos(inteira.shape, recorte)
    if caixa is None:
        pronto = ((largura, altura), (0.5, 0.5))
    else:
        x0, y0, x1, y1 = caixa
        pronto = ((x1 - x0, y1 - y0),
                  ((x0 + x1) / 2 / max(1, largura), (y0 + y1) / 2 / max(1, altura)))
    if chave is not None:
        with _TRANCA_GEOMETRIAS:
            _TAMANHOS_PRONTOS[chave] = pronto
            while len(_TAMANHOS_PRONTOS) > MAX_GEOMETRIAS:
                _TAMANHOS_PRONTOS.popitem(last=False)
    return pronto


# Item 2.4: o tamanho da pagina pronta (e o centro do conteudo) de cada
# pagina ja medida, na mesma chave do corte (_GEOMETRIAS): a tela de conferir
# monta a conta das margens iguais com eles, sem desenhar nada (decisao do
# Samuel, 22/10/2026: "Sim, a tela mostra igual ao que sai"). Seguro esvaziar
# a qualquer hora (mede de novo).
_TAMANHOS_PRONTOS: "OrderedDict[tuple, tuple]" = OrderedDict()


def tamanhos_ja_medidos(projeto: Projeto) -> list | None:
    """Os (tamanho, centro) de todas as paginas ativas, se todas ja foram
    medidas no estado de agora (corte, angulo, giro); None se falta alguma."""
    medidos = []
    for pagina in projeto.paginas_ativas:
        chave = _chave_da_geometria(projeto.folhas[pagina.folha], pagina, projeto)
        if chave is None:
            return None
        with _TRANCA_GEOMETRIAS:
            pronto = _TAMANHOS_PRONTOS.get(chave)
        if pronto is None:
            return None
        medidos.append(pronto)
    return medidos


def conta_das_margens_para_a_tela(projeto: Projeto):
    """Item 2.4: a conta das margens iguais, se todas as paginas ja foram
    medidas (senao None: a tela pede a medida por tras e mostra sem
    margem ate la). Mesma conta do processar."""
    if not getattr(projeto, "margens_iguais", False):
        return None
    medidos = tamanhos_ja_medidos(projeto)
    if medidos is None:
        return None
    ms = margens_scantailor
    conta = ms.montar_a_conta([t for t, _c in medidos], projeto.qualidade_dpi,
                              ms.Margens.de(getattr(projeto, "margens_mm", None)),
                              ms.alinhamento_valido(getattr(projeto, "margens_alinhamento", None)))
    conta.centros = [c for _t, c in medidos]
    return conta


def margens_na_tela(img: np.ndarray, projeto: Projeto, pagina: ConfigPagina, conta) -> np.ndarray:
    """Item 2.4: a pagina da tela (em qualquer resolucao) com as margens iguais,
    como sai no PDF: a resolucao da imagem sai do tamanho medido da pagina.
    Sem conta, ou pagina fora da lista, devolve `img`."""
    if conta is None or img is None:
        return img
    ativas = projeto.paginas_ativas
    try:
        posicao = next(i for i, p in enumerate(ativas) if p is pagina)
    except StopIteration:
        return img
    medidos = tamanhos_ja_medidos(projeto)
    if medidos is None or posicao >= len(medidos):
        return img
    altura_px = medidos[posicao][0][1]
    dpi = projeto.qualidade_dpi * img.shape[0] / max(1, altura_px)
    altura, largura = img.shape[:2]
    suaves, livro = conta.margens_da_pagina(
        posicao, (round(largura * projeto.qualidade_dpi / dpi), altura_px),
        projeto.qualidade_dpi, conta.centros[posicao] if posicao < len(conta.centros) else None)
    return margens_scantailor.compor_com_margens(img, dpi, conta.margens, suaves, livro)


def medir_o_livro_para_as_margens(projeto: Projeto, doc, ativas: list[ConfigPagina],
                                  progresso: Progresso = None, cancelado: Cancelado = None):
    """Item 2.4: a primeira passada das margens iguais. Desenha cada folha
    (uma por vez, solta logo), mede o tamanho da pagina pronta e monta a
    conta do livro (core/margens_scantailor.montar_a_conta): o tamanho do
    livro e as paginas muito maiores, que ficam fora da conta e ganham o
    aviso (g9-pagina-muito-maior, Samuel 14/10/2026: "O programa deixa essa
    folha de fora sozinho, e avisa").

    Regra "uma pagina por vez": guarda so dois numeros e um centro por
    pagina, nunca imagem. Custa um desenho a mais por folha (a segunda
    passada nao mede o corte de novo: ele fica guardado)."""
    ms = margens_scantailor
    total = len(ativas)
    tamanhos: list[tuple[int, int]] = []
    centros: list[tuple[float, float]] = []
    folha_atual, img_folha = None, None
    for feito, pagina in enumerate(ativas):
        _checar(cancelado)
        _avisar(progresso, feito, total,
                f"Medindo as páginas para as margens iguais: {feito + 1} de {total}")
        folha = projeto.folhas[pagina.folha]
        # ja medida neste estado (pela tela ou por um processar de antes):
        # nao desenha a folha de novo
        chave = _chave_da_geometria(folha, pagina, projeto)
        with _TRANCA_GEOMETRIAS:
            pronto = _TAMANHOS_PRONTOS.get(chave) if chave is not None else None
        if pronto is not None:
            tamanhos.append(pronto[0])
            centros.append(pronto[1])
            continue
        if folha_atual != folha.indice:
            img_folha = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
            folha_atual = folha.indice
        tamanho, centro = tamanho_da_pagina_pronta(img_folha, folha, pagina, projeto, doc)
        tamanhos.append(tamanho)
        centros.append(centro)
    del img_folha
    conta = ms.montar_a_conta(tamanhos, projeto.qualidade_dpi,
                              ms.Margens.de(getattr(projeto, "margens_mm", None)),
                              ms.alinhamento_valido(getattr(projeto, "margens_alinhamento", None)))
    conta.centros = centros
    for posicao, pagina in enumerate(ativas):
        _anotar_folha_maior(pagina, posicao in conta.fora_da_conta)
    return conta


def _anotar_folha_maior(pagina: ConfigPagina, fora: bool) -> None:
    """Poe (ou tira) o aviso da pagina muito maior na lista de avisos da
    pagina (core/analise.FOLHA_MAIOR_FORA_DAS_MARGENS)."""
    codigo = analise.FOLHA_MAIOR_FORA_DAS_MARGENS
    alertas = list(getattr(pagina, "alertas", []) or [])
    tem = codigo in alertas
    if fora and not tem:
        alertas.append(codigo)
    elif not fora and tem:
        alertas.remove(codigo)
    else:
        return
    pagina.alertas = alertas


def _por_as_margens(img: np.ndarray, conta, posicao: int, projeto: Projeto) -> np.ndarray:
    """Item 2.4: cola a pagina pronta na folha branca com as margens fixas e
    as suaves (core/margens_scantailor.compor_com_margens)."""
    ms = margens_scantailor
    centros = getattr(conta, "centros", None) or []
    centro = centros[posicao] if posicao < len(centros) else None
    altura, largura = img.shape[:2]
    suaves, livro = conta.margens_da_pagina(posicao, (largura, altura),
                                            projeto.qualidade_dpi, centro)
    return ms.compor_com_margens(img, projeto.qualidade_dpi, conta.margens, suaves, livro)


def _so_as_letras_no_livro(projeto: Projeto) -> bool:
    """"So as letras" vale no livro: "Limpar a folha", o Preto e branco como
    filtro do livro e a caixinha marcada (Projeto.misto_so_as_letras)."""
    return bool(projeto.limpar and projeto.filtro_padrao == PRETO_E_BRANCO
                and getattr(projeto, "misto_so_as_letras", False) is True)


def _frase_do_so_as_letras(projeto: Projeto) -> str:
    """O que o Preto e branco com "So as letras" vai fazer de verdade, em
    portugues simples, para o resumo da tela "O que fazer" (ressalva 4 do
    verificador do Misto, 05/10/2026: a frase dizia "deixar tudo em preto e
    branco" com a caixinha marcada). Muda com o botao escolhido (A, B ou C,
    core.misto.FORAS_DO_TEXTO) e com "Achar as gravuras" desligado (ai so
    fica como no original o que a pessoa marcar a mao). Seguro mudar: os
    textos (sem jargao: nada de "OCR", "mascara", "Misto")."""
    _ligado, escolhas = misto.escolhas_da_pagina(projeto, None)
    if getattr(projeto, "gravura_forma", "livre") == "desligada":
        imagens = "as gravuras que você marcar à mão"
    else:
        imagens = "gravuras, fotos, molduras e iluminuras"
    if escolhas.fora_do_texto == misto.FORA_TUDO:
        return (f"deixar tudo em preto e branco menos {imagens} "
                f"(essas ficam como no original)")
    if escolhas.fora_do_texto == misto.FORA_APAGAR:
        return (f"deixar só o texto que eu achar, em preto e branco ({imagens} "
                f"ficam como no original; o resto vai a branco)")
    return (f"deixar só as letras em preto e branco ({imagens} ficam como no "
            f"original; fora do texto, só fica a tinta escura)")


def resumo_em_portugues(projeto: Projeto, total_folhas: int) -> str:
    """A caixa (i) da tela 2, atualizada ao vivo. Sem jargao nenhum.

    Item 1.1: com o filtro do livro em "Tirar o fundo" (so aparece em PDF
    com camadas), diz que tira o fundo de todas as paginas e que, onde nao
    der, a pagina fica como veio (ver usa_tirar_fundo e _filtrar). Num PDF
    sem camadas esse filtro nao faz nada, e o resumo nao fala dele.

    Modo Misto (05/10/2026): com "So as letras" marcada no Preto e branco, a
    frase do filtro diz o que vai acontecer de verdade
    (_frase_do_so_as_letras), e nao "deixar tudo em preto e branco".
    """
    from core.filtros import NOMES_AMIGAVEIS

    partes: list[str] = []

    if projeto.dividir_folhas:
        # item 2.1: diz o jeito (o texto mora em core/dividir_scantailor)
        jeito = dividir_scantailor.NOMES_DOS_JEITOS[
            dividir_scantailor.jeito_valido(getattr(projeto, "dividir_como", None))]
        partes.append(f"dividir as {total_folhas} folhas em {total_folhas * 2} páginas "
                      f"(jeito: {jeito})")
    if getattr(projeto, "cortar_sobra", False):
        partes.append("cortar a beirada da folha vizinha (o corte da sobra do ScanTailor)")
    if projeto.endireitar:
        partes.append("endireitar as tortas")
    if projeto.cortar_bordas:
        # itens 2.5, 2.13 e 2.14 (achado do verificador, 21/10/2026: a frase
        # nao dizia nada das opcoes novas)
        corte = "cortar as bordas"
        if getattr(projeto, "borda_preta", False):
            jeito = borda_preta.jeito_valido(getattr(projeto, "borda_preta_ate", None))
            fazer = borda_preta.fazer_valido(getattr(projeto, "borda_preta_fazer", None))
            ate = "até o que está impresso" if jeito == borda_preta.ATE_A_MOLDURA else "só o preto"
            corte += (f", tirando a borda preta do scanner ({ate})" if fazer == borda_preta.CORTAR_FORA
                      else f", pintando de branco a borda preta do scanner ({ate})")
        if getattr(projeto, "cortar_pelo_conteudo", False):
            corte += (", seguindo o que está impresso, com todas as páginas do tamanho "
                      "da maior")
        partes.append(corte)
    comum = projeto.limpar and projeto.filtro_padrao not in (ORIGINAL, TIRAR_FUNDO)
    if projeto.limpar and projeto.filtro_padrao == TIRAR_FUNDO:
        if projeto.tem_camadas:
            partes.append("tirar o fundo de todas as páginas, que este PDF já traz "
                          "separado do que está impresso (onde não der, a página "
                          "fica como veio)")
    elif projeto.limpar and projeto.filtro_padrao != ORIGINAL:
        nome = NOMES_AMIGAVEIS.get(projeto.filtro_padrao, projeto.filtro_padrao).lower()
        if _so_as_letras_no_livro(projeto):
            partes.append(_frase_do_so_as_letras(projeto))
        else:
            partes.append(f"deixar tudo em {nome}")
    if comum:
        # item 1.2: o grupo "Gravuras e fotos" (ui/tela_opcoes.py)
        forma = getattr(projeto, "gravura_forma", "livre")
        if forma == "desligada":
            partes.append("não procurar gravuras e fotos")
        elif forma == "retangular":
            partes.append("achar as fotos em retângulo")
        elif not _so_as_letras_no_livro(projeto):
            # com "So as letras", separar a gravura do texto ja esta dito
            # na frase dela (_frase_do_so_as_letras)
            partes.append("separar as gravuras do texto")
    if getattr(projeto, "margens_iguais", False):
        # item 2.4 (as margens do ScanTailor)
        partes.append("deixar todas as páginas do tamanho da maior, com margens iguais")
    # obra 26/10, etapa 1 (D-009): o que foi feito a mao numa etapa desligada
    # tambem vai para o PDF - o resumo diz (so aparece quando ha)
    a_mao = len(etapas.paginas_a_mao_fora_do_automatico(projeto))
    if a_mao:
        partes.append("manter o que você fez à mão em "
                      + ("1 página" if a_mao == 1 else f"{a_mao} páginas"))
    if projeto.montar_cadernos:
        partes.append(f"montar cadernos de {projeto.paginas_por_caderno} páginas")

    if not partes:
        return "Marque pelo menos uma coisa para eu fazer."
    if len(partes) == 1:
        return f"Vou {partes[0]}."
    return f"Vou {', '.join(partes[:-1])} e {partes[-1]}."
