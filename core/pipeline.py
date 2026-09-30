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
from core.filtros import ORIGINAL, TIRAR_FUNDO, aplicar_filtro, aplicar_filtro_com_selecao
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
    img_folha: np.ndarray, folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto,
    geometria: tuple | None = None,
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

    Arriscado mudar: esta funcao alimenta a previa da tela, o PDF final e o
    avaliar.py; a ordem cortar -> endireitar e a do CLAUDE.md.
    """
    inteira = preparar_para_recorte(img_folha, folha, pagina)

    if geometria is None:
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
    """
    from core.selecao import MAO, Selecao

    if not projeto.detectar_regioes:
        return Selecao()

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
    _guardar_geometria(folha, pagina, projeto, grande)
    geometria = _geometria_guardada(folha, pagina, projeto)
    if geometria is None:     # arquivo sem chave (nao existe no disco): so calcula
        geometria = _geometria(preparar_para_recorte(grande, folha, pagina), pagina, projeto)
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
            img = preparar_metade(resultado.imagem, folha, pagina, projeto, geometria=geometria)
            return img, False
    else:
        _anotar_conferir(pagina, False)

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
    # item 1.2: o DPI de verdade desta imagem e o do scan, para o detector de
    # gravura (so custam alguma coisa quando a pagina ainda nao tem marcacao)
    dpi_desenho = dpi_scan = None
    if _vai_detectar(projeto, pagina):
        dpi_desenho = _dpi_do_desenho(doc, folha.indice, img_folha)
        dpi_scan = _dpi_do_scan(doc, folha)
    img = preparar_metade(img_folha, folha, pagina, projeto)
    return _filtrar(projeto, pagina, img, dpi_desenho, dpi_scan)


def _vai_detectar(projeto: Projeto, pagina: ConfigPagina) -> bool:
    """_filtrar vai chamar a deteccao de gravura e letra nesta pagina? (a
    mesma conta de _filtrar + garantir_selecao; so serve para nao medir DPI a
    toa). Errar para "sim" so custa milissegundos. Atencao: no filtro
    Original a deteccao roda do mesmo jeito (_filtrar chama garantir_selecao
    antes de saber o filtro), e a marcacao fica guardada para quando a pessoa
    trocar de filtro - por isso o Original NAO fica de fora aqui."""
    return bool(projeto.limpar and pagina.filtro != TIRAR_FUNDO and projeto.detectar_regioes
                and (not pagina.selecao or _gravura_a_refazer(projeto, pagina)))


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
    ScanTailor precisa deles; item 1.2).

    O MESMO para a previa (renderizar_pagina) e o PDF (processar): antes era
    escrito duas vezes, igual. Devolve (imagem, monocromatica); sem "Limpar a
    folha", a imagem como veio.

    Filtro "Tirar o fundo" (item 1.1) que chega aqui: core/camadas.py deixou
    a pagina intacta, o PDF nao tem camadas ou deu erro - a pagina sai como
    veio, sem outro filtro por cima e sem procurar gravura e letra (a
    marcacao nao serviria para nada, e custa ~1 s).
    """
    if not projeto.limpar or pagina.filtro == TIRAR_FUNDO:
        return img, False
    return aplicar_filtro_com_selecao(
        img, pagina.filtro, garantir_selecao(projeto, pagina, img, dpi, dpi_do_scan),
        pagina.forca_preto, pagina.clareza_melhorar, pagina.intensidade_magico,
        algoritmo_pb=pagina.algoritmo_preto_branco, despeckle=pagina.despeckle,
    )


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
                    img = preparar_metade(imagem_sem_fundo, folha, pagina, projeto,
                                          geometria=geometria)
                    mono = False
                else:
                    # o corte e calculado nesta mesma imagem (a do PDF) e
                    # guardado: a previa, se vier depois, mostra este (ver
                    # _GEOMETRIAS)
                    if _precisa_de_geometria(pagina, projeto):
                        _guardar_geometria(folha, pagina, projeto, img_folha)
                    dpi_desenho = dpi_scan = None
                    if _vai_detectar(projeto, pagina):     # item 1.2 (ver renderizar_pagina)
                        dpi_desenho = _dpi_do_desenho(doc, folha.indice, img_folha)
                        dpi_scan = _dpi_do_scan(doc, folha)
                    img = preparar_metade(img_folha, folha, pagina, projeto)
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
    """A caixa (i) da tela 2, atualizada ao vivo. Sem jargao nenhum.

    Item 1.1: com o filtro do livro em "Tirar o fundo" (so aparece em PDF
    com camadas), diz que tira o fundo de todas as paginas e que, onde nao
    der, a pagina fica como veio (ver usa_tirar_fundo e _filtrar). Num PDF
    sem camadas esse filtro nao faz nada, e o resumo nao fala dele.
    """
    from core.filtros import NOMES_AMIGAVEIS

    partes: list[str] = []

    if projeto.dividir_folhas:
        partes.append(f"dividir as {total_folhas} folhas em {total_folhas * 2} páginas")
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
        partes.append(f"deixar tudo em {nome}")
    if comum:
        # item 1.2: o grupo "Gravuras e fotos" (ui/tela_opcoes.py)
        forma = getattr(projeto, "gravura_forma", "livre")
        if forma == "desligada":
            partes.append("não procurar gravuras e fotos")
        elif forma == "retangular":
            partes.append("achar as fotos em retângulo")
        else:
            partes.append("separar as gravuras do texto")
    if projeto.montar_cadernos:
        partes.append(f"montar cadernos de {projeto.paginas_por_caderno} páginas")

    if not partes:
        return "Marque pelo menos uma coisa para eu fazer."
    if len(partes) == 1:
        return f"Vou {partes[0]}."
    return f"Vou {', '.join(partes[:-1])} e {partes[-1]}."
