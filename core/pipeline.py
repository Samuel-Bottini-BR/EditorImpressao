"""Orquestra tudo, sempre uma página por vez.

Ordem obrigatoria do processamento:
    1. dividir folhas -> 2. cortar bordas -> 3. endireitar -> 4. filtro
    -> 5. montar cadernos

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

import logging
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
from core.endireitar import ANGULO_MINIMO, Inclinacao, detectar_angulo, girar_90, rotacionar
from core import dividir_scantailor, endireitar_scantailor, linhas_do_texto, misto, pontinhos_scantailor
from core.filtros import (ORIGINAL, PRETO_E_BRANCO, TIRAR_FUNDO, aplicar_filtro,
                          aplicar_filtro_com_selecao, aplicar_so_os_pedacos)
from core.folha import compor_na_folha
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
from core.recortar import Recorte, alargar_para_o_giro, aplicar_recorte, detectar_bordas, fatiar
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
        medir_as_duas = (projeto.endireitar and endireitar_scantailor.jeito_do_livro(projeto)
                         == endireitar_scantailor.JEITO_SCANTAILOR)

        for indice, info in enumerate(infos):
            _checar(cancelado)
            _avisar(progresso, indice, total, f"Analisando a folha {indice + 1} de {total}")

            img = pagina_para_array(doc, indice, dpi=DPI_ANALISE)

            # Item 2.1: dividir so com o livro marcado (G2 (a)), pelo jeito
            # escolhido; o corte da sobra so na folha que nao vai ser dividida
            # (G3 (b), desligado de fabrica).
            lombada = (achar_divisao(img, projeto.dividir_como, DPI_ANALISE)
                       if projeto.dividir_folhas else Lombada(0.5, 0.0, False))
            vai_dividir_esta = projeto.dividir_folhas and lombada.e_paisagem
            sobra = (achar_sobra(img, DPI_ANALISE)
                     if getattr(projeto, "cortar_sobra", False) and not vai_dividir_esta
                     else None)
            inclinacao = detectar_angulo(img) if projeto.endireitar else Inclinacao(0.0, 0.0)
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
                tamanho_fora_do_padrao=fora_do_padrao[indice],
            )
            folhas.append(folha)

            # A analise de cor e feita ja na metade certa: uma capa colorida na
            # direita nao deve pintar a pagina da esquerda de alerta.
            for metade, pedaco in _partes_da_folha(img, folha):
                pagina = ConfigPagina(
                    indice=len(paginas),
                    folha=indice,
                    metade=metade,
                    filtro=projeto.filtro_padrao,
                )
                alertas, tem_cor = analise.analisar_pagina(pedaco, projeto.filtro_padrao)
                pagina.alertas = alertas
                pagina.tem_cor = tem_cor
                paginas.append(pagina)
                if medir_as_duas:
                    medidas: dict = {}
                    _geometria(pedaco, pagina, projeto, dpi=DPI_ANALISE, dpi_do_scan=dpi_real,
                               medidas=medidas)
                    if medidas.get("discordam"):
                        discordam.append(pagina)

            del img

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

    Arriscado mudar: esta funcao alimenta a previa da tela, o PDF final e o
    avaliar.py; a ordem cortar -> endireitar e a do CLAUDE.md (e a de
    core/zonas_na_folha._matriz_folha_para_pagina: mudou uma, muda a outra).
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
    """
    from core.zonas_na_folha import geometria_do_desenho

    inteira = preparar_para_recorte(img_folha, folha, pagina, projeto)

    if geometria is None:
        geometria = _geometria_guardada(folha, pagina, projeto)
    if geometria is None:
        geometria = _geometria(inteira, pagina, projeto, dpi=dpi)
    recorte, angulo = geometria

    # 2. cortar bordas (o recorte ja vem com a folga do giro, se houver giro)
    img = inteira
    girar = projeto.endireitar and abs(angulo) >= ANGULO_MINIMO
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


def _geometria(base: np.ndarray, pagina: ConfigPagina, projeto: Projeto,
               dpi: float | None = None, dpi_do_scan: float | None = None,
               medidas: dict | None = None):
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
    """
    recorte = None
    automatico = None
    if projeto.cortar_bordas:
        if pagina.recorte is None:
            # o recorte automatico e calculado na metade ja separada: cada
            # pagina tem sua propria sombra de lombada de um lado so
            automatico = detectar_bordas(base, dpi=dpi)
            recorte = automatico.tupla
        else:
            recorte = tuple(pagina.recorte)

    angulo = 0.0
    if projeto.endireitar:
        angulo = pagina.angulo_manual
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


def _chave_da_geometria(folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto):
    """Tudo de que o corte e o angulo dependem. None se o arquivo do projeto
    nao existe (projeto de teste, arquivo movido) - ai nada e guardado."""
    try:
        # normcase: o mesmo PDF escrito com `\` ou `/`, ou com maiusculas
        # diferentes, da a mesma chave (bug de 29/09, projetos.mesmo_arquivo).
        caminho = os.path.normcase(os.path.abspath(projeto.caminho_entrada))
        info = os.stat(caminho)
    except (OSError, TypeError, ValueError):
        return None
    recorte = None if pagina.recorte is None else tuple(round(float(v), 6) for v in pagina.recorte)
    dividir = bool(folha.dividir) and pagina.metade != METADE_INTEIRA
    return (
        caminho, info.st_mtime_ns, info.st_size, int(projeto.qualidade_dpi),
        folha.indice, int(folha.rotacao) % 360,
        dividir, round(float(folha.posicao_corte), 6) if dividir else None,
        pagina.metade if dividir else None, bool(projeto.cortar_bordas),
        bool(projeto.endireitar), recorte, pagina.angulo_manual,
        faixa_da_sobra(folha, pagina, projeto),        # item 2.1
        endireitar_scantailor.jeito_da_pagina(projeto, pagina),   # item 2.2
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
                   if doc is not None and _usa_o_endireitar_do_scantailor(projeto, pagina) else None)
    medidas: dict = {}
    geometria = _geometria(preparar_para_recorte(img_folha_do_pdf, folha, pagina, projeto), pagina, projeto,
                           dpi=projeto.qualidade_dpi, dpi_do_scan=dpi_do_scan, medidas=medidas)
    with _TRANCA_GEOMETRIAS:
        _GEOMETRIAS[chave] = geometria
        while len(_GEOMETRIAS) > MAX_GEOMETRIAS:
            _GEOMETRIAS.popitem(last=False)
        if medidas:
            _ANGULOS_MEDIDOS[chave] = dict(medidas)
            while len(_ANGULOS_MEDIDOS) > MAX_GEOMETRIAS:
                _ANGULOS_MEDIDOS.popitem(last=False)
    _anotar_contas_discordam(pagina, bool(medidas.get("discordam")))


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


def _usa_o_endireitar_do_scantailor(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A conta do ScanTailor entra nesta pagina (a dela ou a do livro, para o
    C1)? So com o endireitar ligado e o angulo automatico."""
    es = endireitar_scantailor
    return (bool(projeto.endireitar) and pagina.angulo_manual is None
            and es.JEITO_SCANTAILOR in (es.jeito_da_pagina(projeto, pagina), es.jeito_do_livro(projeto)))


def _anotar_contas_discordam(pagina: ConfigPagina, discordam: bool) -> None:
    """Poe ou tira o aviso C1 (analise.CONTAS_DO_ENDIREITAR_DISCORDAM), do
    mesmo jeito que _anotar_tinta_forte_fora: ao POR, a pagina volta a "nao
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


def _precisa_de_geometria(pagina: ConfigPagina, projeto: Projeto) -> bool:
    """Ha corte ou angulo automatico a calcular nesta pagina?"""
    return ((projeto.cortar_bordas and pagina.recorte is None)
            or (projeto.endireitar and pagina.angulo_manual is None))


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
    return pagina.gravura_feita_com != assinatura_da_gravura(*escolha_da_gravura(projeto, pagina))


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
                     dpi: float | None = None, dpi_do_scan: float | None = None):
    """Descobre onde estao gravura, letra e papel - uma vez por pagina.

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
    from core.selecao import MAO, Selecao

    if not projeto.detectar_regioes:
        return Selecao()

    lida = pagina.selecao          # a lista de agora (ver a corrida, acima)
    antiga = pagina.obter_selecao()
    refazer = _gravura_a_refazer(projeto, pagina)
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
        # a pessoa marcou durante a deteccao: vale a marcacao dela
        return pagina.obter_selecao()
    pagina.gravura_feita_com = assinatura_da_gravura(detector, opcoes)

    # A deteccao pode acabar sem certeza se a folha e desenho ou escrita.
    # Quando isso acontece a pagina fica laranja, para a pessoa conferir na
    # aba Marcar - ver DESENHO_OU_ESCRITA. Ficar calado seria pior: a
    # partitura do Graduale passou dois dias marcada como desenho sem
    # ninguem ver.
    if getattr(selecao, "em_duvida", False):
        if analise.DESENHO_OU_ESCRITA not in pagina.alertas:
            pagina.alertas.append(analise.DESENHO_OU_ESCRITA)

    pagina.guardar_selecao(selecao)
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
    """
    return bool(projeto.limpar and projeto.tem_camadas and pagina.filtro == TIRAR_FUNDO)


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
    if _vai_detectar(projeto, pagina) or _vai_limpar_pelo_scantailor(projeto, pagina):
        dpi_desenho = _dpi_do_desenho(doc, folha.indice, img_folha)
        dpi_scan = _dpi_do_scan(doc, folha)
    img, desenho = _preparar_metade_e_geometria(img_folha, folha, pagina, projeto, dpi=dpi)
    _acompanhar_as_zonas(pagina, desenho)
    return _filtrar(projeto, pagina, img, dpi_desenho, dpi_scan)


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
    recorte = None if pagina.recorte is None else tuple(float(v) for v in pagina.recorte)
    return (int(folha.rotacao) % 360, bool(folha.dividir), float(folha.posicao_corte),
            pagina.metade, int(pagina.folha), recorte, pagina.angulo_manual,
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


def _vai_detectar(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """_filtrar vai chamar a deteccao de gravura e letra nesta pagina? (a
    mesma conta de _filtrar + garantir_selecao; so serve para nao medir DPI a
    toa). Errar para "sim" so custa milissegundos. Atencao: no filtro
    Original a deteccao roda do mesmo jeito (_filtrar chama garantir_selecao
    antes de saber o filtro), e a marcacao fica guardada para quando a pessoa
    trocar de filtro - por isso o Original NAO fica de fora aqui."""
    return bool(projeto.limpar and pagina.filtro != TIRAR_FUNDO and projeto.detectar_regioes
                and (not pagina.selecao or _gravura_a_refazer(projeto, pagina)))


def _vai_limpar_pelo_scantailor(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """_filtrar vai usar o limpar pontinhos do ScanTailor nesta pagina (o
    Preto e branco com "pouco", "normal" ou "muito")? So serve para medir o
    DPI de verdade so quando precisa. Errar para "sim" so custa milissegundos."""
    return bool(projeto.limpar and pagina.filtro == PRETO_E_BRANCO
                and pontinhos_scantailor.escolha_da_pagina(projeto, pagina)
                in pontinhos_scantailor.DO_SCANTAILOR)


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
    if escolha in pontinhos_scantailor.DO_SCANTAILOR and dpi:
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
             dpi: float | None = None, dpi_do_scan: float | None = None) -> tuple[np.ndarray, bool]:
    """Etapa 4: o filtro da pagina, com a marcacao de gravura/letra/papel.

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
    """
    if not projeto.limpar:
        _anotar_tinta_forte_fora(pagina, False)
        return img, False
    if pagina.filtro == TIRAR_FUNDO:
        # Conferencia 14 (Samuel, "FUNDO: Sim, do mesmo jeito (só muda se
        # alguém marcar um pedaço)"): o pedaco vale aqui como no Original. A
        # marcacao usada e a GUARDADA (pagina.obter_selecao), sem chamar o
        # detector: o pedaco e desenhado a mao, e a pagina sem pedaco nao
        # paga o ~1 s da deteccao (e sai o mesmo objeto, como antes).
        _anotar_tinta_forte_fora(pagina, False)
        return _so_os_pedacos_no_tirar_o_fundo(projeto, pagina, img, img), False
    selecao = garantir_selecao(projeto, pagina, img, dpi, dpi_do_scan)
    # "Limpar pontinhos" (06/10/2026): a escolha da pagina e o DPI de verdade
    pontinhos = pontinhos_da_pagina(projeto, pagina, img, dpi, dpi_do_scan)
    if pagina.filtro == PRETO_E_BRANCO:
        opcoes = misto.opcoes_da_pagina(projeto, pagina)
        if opcoes is not None:
            return _filtrar_no_misto(projeto, pagina, img, selecao, opcoes, pontinhos)
    _anotar_tinta_forte_fora(pagina, False)
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

# A pagina vai para "Para revisar" (analise.TINTA_FORTE_FORA_DO_TEXTO) quando
# a tinta forte fora das linhas de texto e fora das gravuras passa desta
# fracao de toda a tinta da pagina. Medido na rodada da conferencia 8 (docTR +
# Kraken; o formulario sugeria "uns 10%"): Graduale 222 76% (a musica),
# Palatino 9 47% (a capitular e as molduras), Opus 165 6%, Marial 7 5%, Horas
# 13 4%, Boecio 22 2%, Horas 11 menos de 1%. Com 10%, vao para revisar as
# paginas em que o leitor deixou de fora uma parte grande do que esta impresso
# - nao as que tem so umas letrinhas de diagrama ou pontos.
# Medido de novo em 05/10, SO com o docTR (como no programa), nas 34 paginas
# das 32 folhas do gabarito (relatorios/conferir/misto-no-programa-2026-10-05/
# dados/medidas-misto.json, imagens em tinta-forte/): 19 passam de 10%, e
# quase todas tem MUITO impresso fora do texto que o detector de gravura nao
# marcou - moldura de filetes e floreios (Palatino 9, 10, 57, 66, 67;
# Siebmacher 7 e 9; Rhetorica 18), tabela com regua (Horas 14, Opus 256),
# chaves de diagrama (Rhetorica 73), musica (Graduale 221-223), gravura e
# carimbo nao marcados (Boecio 3), pagina so de desenho (Siebmacher, lado
# direito). Texto corrido fica abaixo de 4% (Boecio 7, 8, 22; Escola 7 e 35;
# Palatino 5 e 7; Opus 11; Horas 11, 13, 26, 27, 47), e as de diagrama
# pequeno entre 5% e 9% (Opus 20, 165; Marial 7). Nao ha um vao claro entre
# as duas turmas acima de 10%: subir para 30% tiraria do aviso so 3 das 19.
# No A, essa tinta e guardada (a moldura e a tabela saem); no C ela vai a
# branco - e ai que o aviso mais importa. Seguro mudar: o numero (so muda
# quem vai para revisar). Arriscado: baixar muito (quase toda pagina com
# gravura ou sujeira na beirada iria para revisar, e o aviso deixaria de ser
# lido).
LIMITE_DA_TINTA_FORTE_FORA = 0.10


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
    recorte = tuple(round(float(v), 4) for v in pagina.recorte) if pagina.recorte else None
    return (arquivo, pagina.metade, folha.rotacao, folha.dividir,
            round(float(folha.posicao_corte), 4), recorte, pagina.angulo_manual,
            projeto.dividir_folhas, projeto.cortar_bordas, projeto.endireitar,
            faixa_da_sobra(folha, pagina, projeto))       # item 2.1


def _filtrar_no_misto(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray, selecao,
                      opcoes, pontinhos=True) -> tuple[np.ndarray, bool]:
    """O Preto e branco so nas letras (core.misto.aplicar_misto) com as
    escolhas da pagina (`opcoes`, core.misto.OpcoesDoMisto) e o "Limpar
    pontinhos" dela (`pontinhos`, de pontinhos_da_pagina).

    A e C precisam das linhas de texto: core.linhas_do_texto (o docTR, uma
    vez por pagina; guardadas por _chave_das_linhas, a previa e o PDF usam as
    mesmas). Quem chama esta numa QThread (previa e PDF): o leitor bloqueia
    1 a 2,5 s na primeira vez da pagina, nunca a tela. Se o leitor nao estiver
    disponivel, sai o Misto B (o motivo vai para o erros.log).

    O aviso "Tinta forte fora do texto" e acertado aqui (A e C, com linhas);
    na B ele sai (sem as linhas, nao ha o que medir)."""
    linhas, altura_linha = None, 0.0
    if opcoes.precisa_das_linhas:
        resultados = linhas_do_texto.linhas_da_pagina(img, _chave_das_linhas(projeto, pagina))
        if resultados:
            linhas, altura_linha = misto.mascara_das_linhas(resultados, img.shape)
    medidas: dict = {}
    saida = misto.aplicar_misto(
        img, selecao, pagina.forca_preto, pagina.algoritmo_preto_branco, pontinhos,
        pagina.clareza_melhorar, pagina.intensidade_magico,
        papel_da_gravura_branco=opcoes.papel_da_gravura == misto.PAPEL_BRANCO,
        letras_na_moldura=opcoes.letras_na_moldura,
        fora_do_texto=opcoes.fora_do_texto, linhas=linhas, altura_linha=altura_linha,
        medidas=medidas)
    if "forte_fora" in medidas:
        _anotar_tinta_forte_fora(pagina, medidas["forte_fora"] > LIMITE_DA_TINTA_FORTE_FORA)
    elif not opcoes.precisa_das_linhas:
        _anotar_tinta_forte_fora(pagina, False)
    return saida


def _anotar_tinta_forte_fora(pagina: ConfigPagina, sobrou: bool) -> None:
    """Poe ou tira o alerta analise.TINTA_FORTE_FORA_DO_TEXTO, do mesmo jeito
    que _anotar_conferir: ao POR, a pagina volta a "nao conferida" e o alerta
    vai para a frente; o "esta bom assim" depois disso continua valendo (o
    alerta ja posto nao mexe mais em `revisada`). Barato: so olha a lista."""
    tem = analise.TINTA_FORTE_FORA_DO_TEXTO in pagina.alertas
    if sobrou and not tem:
        pagina.alertas.insert(0, analise.TINTA_FORTE_FORA_DO_TEXTO)
        pagina.revisada = False
    elif not sobrou and tem:
        pagina.alertas = [a for a in pagina.alertas if a != analise.TINTA_FORTE_FORA_DO_TEXTO]


def _acertar_alerta_do_misto(projeto: Projeto, pagina: ConfigPagina) -> None:
    """Tira o "Tinta forte fora do texto" da pagina que nao esta mais no
    Misto A ou C (mudou de filtro, desligou "So as letras", escolheu B), sem
    desenhar nada. Se ainda esta, fica como esta (a previa acerta)."""
    if analise.TINTA_FORTE_FORA_DO_TEXTO not in pagina.alertas:
        return
    opcoes = (misto.opcoes_da_pagina(projeto, pagina)
              if projeto.limpar and pagina.filtro == PRETO_E_BRANCO else None)
    if opcoes is None or not opcoes.precisa_das_linhas:
        _anotar_tinta_forte_fora(pagina, False)


def _misto_vale(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """A pagina vai sair pelo Misto ("So as letras")? A MESMA conta de
    _filtrar: "Limpar a folha" ligado, filtro Preto e branco e "So as letras"
    valendo nela (dela ou do livro). Barato (so le campos)."""
    return bool(getattr(projeto, "limpar", True) and pagina.filtro == PRETO_E_BRANCO
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
    if not projeto.detectar_regioes or not pagina.selecao:
        return False
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
    ajustado - girada e dividida, nunca cortada. Ver `preparar_para_recorte`."""
    folha = projeto.folhas[pagina.folha]
    img_folha = pagina_para_array(doc, folha.indice, dpi=dpi)
    return preparar_para_recorte(img_folha, folha, pagina, projeto)


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
        with EscritorPDF(destino) as escritor:
            try:
                _escrever_as_paginas(projeto, doc, ativas, escritor, progresso, cancelado)
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


def _escrever_as_paginas(projeto: Projeto, doc, ativas: list[ConfigPagina],
                         escritor: EscritorPDF, progresso: Progresso,
                         cancelado: Cancelado) -> None:
    """O laco do processar: cada pagina ativa, uma por vez, ate o escritor.

    Separado do processar em 05/10/2026 so para o tratamento de cancelar e
    erro caber em volta dele (ver processar); o conteudo e o mesmo de antes.
    Levanta Cancelou entre uma pagina e outra, e depois da ultima.

    Arriscado: guardar aqui qualquer lista de paginas processadas (regra
    "uma pagina por vez na memoria"): cada imagem vai para o escritor e sai.
    """
    total = len(ativas)
    # A folha da vez, uma so na memoria (as duas metades vem dela):
    # o desenho normal e, se alguma metade usa o item 1.1, a folha sem
    # o fundo. Os dois sao feitos so quando alguem precisa.
    folha_atual: int | None = None
    img_folha: np.ndarray | None = None
    sem_fundo = None          # core.camadas.PaginaSemFundo da folha da vez

    for feito, pagina in enumerate(ativas):
        _checar(cancelado)
        _avisar(progresso, feito, total, f"Página {feito + 1} de {total}")

        folha = projeto.folhas[pagina.folha]
        if folha.apagada:
            continue

        if folha_atual != folha.indice:
            img_folha, sem_fundo = None, None
            folha_atual = folha.indice

        # Item 1.1: esta pagina sai sem o fundo? (ver usa_tirar_fundo)
        imagem_sem_fundo = None
        if usa_tirar_fundo(projeto, pagina):
            if sem_fundo is None:
                sem_fundo = _sem_fundo_da_folha(doc, folha, projeto.qualidade_dpi)
            imagem_sem_fundo = sem_fundo.imagem
            _anotar_conferir(pagina, bool(imagem_sem_fundo is not None
                                          and sem_fundo.conferir))
        else:
            _anotar_conferir(pagina, False)

        # O desenho normal da folha: para o filtro e para medir o corte
        # (que e sempre medido nele, mesmo quando sai sem o fundo).
        precisa_do_desenho = imagem_sem_fundo is None or (
            _precisa_de_geometria(pagina, projeto)
            and _geometria_guardada(folha, pagina, projeto) is None)
        if precisa_do_desenho and img_folha is None:
            img_folha = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)

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
                img_folha = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
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
            if (_vai_detectar(projeto, pagina)     # item 1.2 (ver renderizar_pagina)
                    or _vai_limpar_pelo_scantailor(projeto, pagina)):
                dpi_desenho = _dpi_do_desenho(doc, folha.indice, img_folha)
                dpi_scan = _dpi_do_scan(doc, folha)
            img, desenho = _preparar_metade_e_geometria(
                img_folha, folha, pagina, projeto, dpi=projeto.qualidade_dpi)
            _acompanhar_as_zonas(pagina, desenho)
            img, mono = _filtrar(projeto, pagina, img, dpi_desenho, dpi_scan)

        # Item 2/4 do teste do Boecio (secao 3a do plano): cola o
        # conteudo (ja filtrado) dentro do tamanho de folha escolhido,
        # com a margem branca ao redor - nunca antes daqui, porque
        # `preparar_metade` tambem alimenta `avaliar.py` (a regua de
        # qualidade dos filtros) e padding ali contaminaria as
        # metricas. Sem `tamanho_folha_cm` (None, o padrao) devolve
        # `img` sem nenhuma alteracao - comportamento de sempre.
        img = compor_na_folha(
            img, pagina.tamanho_folha_cm, projeto.qualidade_dpi,
            escala=pagina.conteudo_escala,
            deslocamento=pagina.conteudo_deslocamento,
        )

        escritor.escrever_imagem(img, dpi=projeto.qualidade_dpi, monocromatico=mono)
        del img

    _checar(cancelado)


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
        partes.append("cortar as bordas")
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
    if projeto.montar_cadernos:
        partes.append(f"montar cadernos de {projeto.paginas_por_caderno} páginas")

    if not partes:
        return "Marque pelo menos uma coisa para eu fazer."
    if len(partes) == 1:
        return f"Vou {partes[0]}."
    return f"Vou {', '.join(partes[:-1])} e {partes[-1]}."
