"""Orquestra tudo, sempre uma página por vez.

Ordem obrigatoria do processamento:
    1. dividir folhas -> 2. cortar bordas -> 3. endireitar -> 4. filtro
    -> 5. montar cadernos

As páginas apagadas somem logo depois da etapa 1.

Sobre memória: nenhuma funcao daqui monta uma lista de páginas processadas. Ler
-> processar -> escrever -> soltar. Foi o que travou a versão anterior com
livros de 500 páginas a 400 DPI.
"""

from __future__ import annotations

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
from core.filtros import ORIGINAL, aplicar_filtro, aplicar_filtro_com_selecao
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
        tamanhos = [(i.largura_pt, i.altura_pt) for i in infos]
        fora_do_padrao = analise.tamanhos_fora_do_padrao(tamanhos)

        folhas: list[ConfigFolha] = []
        paginas: list[ConfigPagina] = []

        for indice, info in enumerate(infos):
            _checar(cancelado)
            _avisar(progresso, indice, total, f"Analisando a folha {indice + 1} de {total}")

            img = pagina_para_array(doc, indice, dpi=DPI_ANALISE)

            lombada = detectar_lombada(img) if projeto.dividir_folhas else Lombada(0.5, 0.0, False)
            inclinacao = detectar_angulo(img) if projeto.endireitar else Inclinacao(0.0, 0.0)
            recorte = detectar_bordas(img) if projeto.cortar_bordas else Recorte.inteiro()

            # DPI de verdade, tirado da imagem embutida no PDF. Medir na imagem
            # que acabamos de rasterizar devolveria sempre DPI_ANALISE.
            dpi_real = dpi_real_da_pagina(doc, indice)

            folha = ConfigFolha(
                indice=indice,
                dividir=projeto.dividir_folhas and lombada.e_paisagem,
                posicao_corte=lombada.posicao,
                confianca_corte=lombada.confianca,
                angulo_detectado=inclinacao.angulo,
                confianca_angulo=inclinacao.confianca,
                e_paisagem=lombada.e_paisagem,
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

        projeto.observacoes = observacoes
        projeto.folhas = folhas
        projeto.paginas = paginas
        _avisar(progresso, total, total, "Pronto")
        return projeto
    finally:
        doc.close()


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
    img_folha: np.ndarray, folha: ConfigFolha, pagina: ConfigPagina
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
    return img


def preparar_metade(
    img_folha: np.ndarray, folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto
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

    Arriscado mudar: esta funcao alimenta a previa da tela, o PDF final e o
    avaliar.py; a ordem cortar -> endireitar e a do CLAUDE.md.
    """
    inteira = preparar_para_recorte(img_folha, folha, pagina)

    geometria = _geometria_guardada(folha, pagina, projeto)
    if geometria is None:
        geometria = _geometria(inteira, pagina, projeto)
    recorte, angulo = geometria

    # 2. cortar bordas (o recorte ja vem com a folga do giro, se houver giro)
    img = inteira
    girar = projeto.endireitar and abs(angulo) >= ANGULO_MINIMO
    if recorte is not None:
        # fatiar (sem copiar) quando vai girar: o rotacionar ja devolve uma
        # imagem nova. Sem giro, copia, como sempre.
        img = fatiar(inteira, recorte) if girar else aplicar_recorte(inteira, recorte)

    # 3. endireitar
    if girar:
        img = rotacionar(img, angulo)

    return img


def _geometria(base: np.ndarray, pagina: ConfigPagina, projeto: Projeto):
    """(recorte, angulo) da pagina, medidos em `base` (a pagina ja girada de
    90 em 90 e dividida, antes de cortar).

    recorte: (x, y, largura, altura) em fracao, ou None quando nao corta. O
    manual (pagina.recorte) vale como esta; o automatico vem de
    detectar_bordas e ganha a folga do giro (alargar_para_o_giro).
    angulo: em graus; 0.0 quando nao endireita. O manual (pagina.angulo_manual)
    vale como esta; o automatico e medido na pagina ja cortada.
    """
    recorte = None
    automatico = None
    if projeto.cortar_bordas:
        if pagina.recorte is None:
            # o recorte automatico e calculado na metade ja separada: cada
            # pagina tem sua propria sombra de lombada de um lado so
            automatico = detectar_bordas(base)
            recorte = automatico.tupla
        else:
            recorte = tuple(pagina.recorte)

    angulo = 0.0
    if projeto.endireitar:
        angulo = pagina.angulo_manual
        if angulo is None:
            cortada = base if recorte is None else fatiar(base, recorte)
            angulo = detectar_angulo(cortada).angulo
        angulo = float(angulo or 0.0)
        if automatico is not None and abs(angulo) >= ANGULO_MINIMO:
            # mesma regra do rotacionar: abaixo de ANGULO_MINIMO nao gira
            recorte = alargar_para_o_giro(automatico, angulo, base).tupla
    return recorte, angulo


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
        caminho = os.path.abspath(projeto.caminho_entrada)
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
                       img_folha_do_pdf: np.ndarray) -> None:
    """Calcula e guarda o (recorte, angulo) da pagina, a partir da folha JA
    desenhada na resolucao do PDF (projeto.qualidade_dpi). Arriscado: passar
    aqui uma imagem de outra resolucao guardaria um corte diferente do PDF."""
    chave = _chave_da_geometria(folha, pagina, projeto)
    if chave is None:
        return
    with _TRANCA_GEOMETRIAS:
        if chave in _GEOMETRIAS:
            return
    geometria = _geometria(preparar_para_recorte(img_folha_do_pdf, folha, pagina), pagina, projeto)
    with _TRANCA_GEOMETRIAS:
        _GEOMETRIAS[chave] = geometria
        while len(_GEOMETRIAS) > MAX_GEOMETRIAS:
            _GEOMETRIAS.popitem(last=False)


def _precisa_de_geometria(pagina: ConfigPagina, projeto: Projeto) -> bool:
    """Ha corte ou angulo automatico a calcular nesta pagina?"""
    return ((projeto.cortar_bordas and pagina.recorte is None)
            or (projeto.endireitar and pagina.angulo_manual is None))


def garantir_selecao(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray):
    """Descobre onde estao gravura, letra e papel - uma vez por pagina.

    Roda SOB DEMANDA, e nao na analise do livro. Detectar leva quase um segundo
    por pagina, e na analise isso daria sete minutos para quinhentas folhas,
    contra a meta de tres. Aqui a conta so acontece quando a pagina vai ser
    mostrada ou exportada, e o resultado fica guardado no projeto: a segunda vez
    e de graca, e o que a pessoa corrigir a mao sobrevive.

    A imagem tem de ser a JA PREPARADA - depois de dividir, cortar e endireitar
    - porque a selecao guarda fracoes daquele recorte. Detectar antes deixaria a
    marcacao deslocada na hora de aplicar.
    """
    from core.selecao import Selecao

    if not projeto.detectar_regioes:
        return Selecao()

    selecao = pagina.obter_selecao()
    if not selecao.vazia:
        return selecao

    try:
        from core.detectar_regioes import detectar

        selecao = detectar(img)
    except Exception:  # noqa: BLE001 - sem deteccao o filtro trata a folha toda
        return Selecao()

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


def renderizar_pagina(
    doc, projeto: Projeto, pagina: ConfigPagina, dpi: int = DPI_PREVIA
) -> tuple[np.ndarray, bool]:
    """Imagem final de uma página de saida, do jeito que ela vai sair.

    Devolve (imagem, monocromatica). E o que a prévia da tela 3 mostra.
    """
    folha = projeto.folhas[pagina.folha]
    if (dpi != projeto.qualidade_dpi and _precisa_de_geometria(pagina, projeto)
            and _geometria_guardada(folha, pagina, projeto) is None):
        # Primeira vez desta pagina: desenha a folha UMA vez, na resolucao do
        # PDF, calcula e guarda o corte (o mesmo que o PDF vai usar) e reduz
        # essa mesma imagem para a previa, em vez de desenhar de novo. Da
        # segunda vez em diante, desenha so na resolucao da previa.
        grande = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
        _guardar_geometria(folha, pagina, projeto, grande)
        img_folha = _reduzir_para_o_dpi(doc, folha.indice, grande, dpi)
        del grande
    else:
        img_folha = pagina_para_array(doc, folha.indice, dpi=dpi)
        if dpi == projeto.qualidade_dpi and _precisa_de_geometria(pagina, projeto):
            _guardar_geometria(folha, pagina, projeto, img_folha)
    img = preparar_metade(img_folha, folha, pagina, projeto)

    if not projeto.limpar:
        return img, False
    return aplicar_filtro_com_selecao(
        img, pagina.filtro, garantir_selecao(projeto, pagina, img),
        pagina.forca_preto, pagina.clareza_melhorar, pagina.intensidade_magico,
        algoritmo_pb=pagina.algoritmo_preto_branco, despeckle=pagina.despeckle,
    )


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
    return preparar_para_recorte(img_folha, folha, pagina)


# ---------------------------------------------------------------------------
# Fase 3: processar o livro inteiro
# ---------------------------------------------------------------------------

def processar(
    projeto: Projeto, progresso: Progresso = None, cancelado: Cancelado = None
) -> str:
    """Gera o PDF final. Devolve o caminho gravado.

    Levanta Cancelou se o usuario cancelar - e a única excecao esperada.
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

    # Caminho rapido: so reordenar, sem tocar em imagem nenhuma.
    if projeto.so_cadernos:
        _avisar(progresso, 0, 1, "Montando os cadernos")
        impor_pdf(
            projeto.caminho_entrada, saida_final, projeto.paginas_por_caderno,
            progresso=lambda f, t: _avisar(progresso, f, t, f"Montando a folha {f} de {t}"),
        )
        return str(saida_final)

    # Quando vamos montar cadernos, primeiro gravamos as paginas em ordem
    # normal num arquivo temporario e so depois reordenamos. Assim a imposicao
    # trabalha com um PDF em disco e nao precisa de nada na memoria.
    temporario: Path | None = None
    if projeto.montar_cadernos:
        temporario = Path(tempfile.gettempdir()) / f"_editor_impressao_{saida_final.stem}.pdf"
        destino = temporario
    else:
        destino = saida_final

    ativas = projeto.paginas_ativas
    total = len(ativas)
    if total == 0:
        raise ErroPDF("Não sobrou nenhuma página para gerar. Restaure alguma página apagada.")

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        with EscritorPDF(destino) as escritor:
            folha_atual: int | None = None
            img_folha: np.ndarray | None = None

            for feito, pagina in enumerate(ativas):
                _checar(cancelado)
                _avisar(progresso, feito, total, f"Página {feito + 1} de {total}")

                folha = projeto.folhas[pagina.folha]
                if folha.apagada:
                    continue

                # As duas metades vem da mesma folha: rasterizamos so uma vez.
                if folha_atual != folha.indice:
                    img_folha = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
                    folha_atual = folha.indice

                # o corte e calculado nesta mesma imagem (a do PDF) e guardado:
                # a previa, se vier depois, mostra este (ver _GEOMETRIAS)
                if _precisa_de_geometria(pagina, projeto):
                    _guardar_geometria(folha, pagina, projeto, img_folha)
                img = preparar_metade(img_folha, folha, pagina, projeto)

                if projeto.limpar:
                    img, mono = aplicar_filtro_com_selecao(
                        img, pagina.filtro,
                        garantir_selecao(projeto, pagina, img),
                        pagina.forca_preto, pagina.clareza_melhorar,
                        pagina.intensidade_magico,
                        algoritmo_pb=pagina.algoritmo_preto_branco,
                        despeckle=pagina.despeckle,
                    )
                else:
                    mono = False

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

        if projeto.montar_cadernos and temporario is not None:
            _avisar(progresso, total, total, "Montando os cadernos")
            impor_pdf(temporario, saida_final, projeto.paginas_por_caderno)
            temporario.unlink(missing_ok=True)

        _avisar(progresso, total, total, "Pronto")
        return str(saida_final)

    except Cancelou:
        # deixa o disco limpo: nada de PDF pela metade
        if temporario is not None:
            temporario.unlink(missing_ok=True)
        Path(destino).unlink(missing_ok=True)
        raise
    finally:
        doc.close()


def resumo_em_portugues(projeto: Projeto, total_folhas: int) -> str:
    """A caixa (i) da tela 2, atualizada ao vivo. Sem jargao nenhum."""
    from core.filtros import NOMES_AMIGAVEIS

    partes: list[str] = []

    if projeto.dividir_folhas:
        partes.append(f"dividir as {total_folhas} folhas em {total_folhas * 2} páginas")
    if projeto.endireitar:
        partes.append("endireitar as tortas")
    if projeto.cortar_bordas:
        partes.append("cortar as bordas")
    if projeto.limpar and projeto.filtro_padrao != ORIGINAL:
        nome = NOMES_AMIGAVEIS.get(projeto.filtro_padrao, projeto.filtro_padrao).lower()
        partes.append(f"deixar tudo em {nome}")
    if projeto.montar_cadernos:
        partes.append(f"montar cadernos de {projeto.paginas_por_caderno} páginas")

    if not partes:
        return "Marque pelo menos uma coisa para eu fazer."
    if len(partes) == 1:
        return f"Vou {partes[0]}."
    return f"Vou {', '.join(partes[:-1])} e {partes[-1]}."
