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

import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

import numpy as np

from core import analise
from core.cadernos import impor_pdf
from core.dividir import Lombada, detectar_lombada, dividir_imagem
from core.endireitar import Inclinacao, detectar_angulo, girar_90, rotacionar
from core.filtros import ORIGINAL, aplicar_filtro, aplicar_filtro_com_selecao
from core.pdf_io import (
    DPI_PREVIA,
    dpi_real_da_pagina,
    EscritorPDF,
    ErroPDF,
    abrir_pdf,
    info_paginas,
    pagina_para_array,
)
from core.recortar import Recorte, aplicar_recorte, detectar_bordas
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

def preparar_metade(
    img_folha: np.ndarray, folha: ConfigFolha, pagina: ConfigPagina, projeto: Projeto
) -> np.ndarray:
    """Aplica giro, divisão, recorte e endireitamento - nesta ordem.

    O filtro fica de fora de proposito: ele e por página e a interface precisa
    trocar só ele sem refazer o resto.
    """
    img = img_folha
    if folha.rotacao:
        img = girar_90(img, folha.rotacao)

    # 1. dividir
    if folha.dividir and pagina.metade != METADE_INTEIRA:
        esq, dir_ = dividir_imagem(img, folha.posicao_corte)
        img = esq if pagina.metade == METADE_ESQUERDA else dir_

    # 2. cortar bordas
    if projeto.cortar_bordas:
        recorte = pagina.recorte
        if recorte is None:
            # o recorte automatico e recalculado na metade ja separada: cada
            # pagina tem sua propria sombra de lombada de um lado so
            recorte = detectar_bordas(img).tupla
        img = aplicar_recorte(img, recorte)

    # 3. endireitar
    if projeto.endireitar:
        angulo = pagina.angulo_manual
        if angulo is None:
            angulo = detectar_angulo(img).angulo
        if angulo:
            img = rotacionar(img, angulo)

    return img


def renderizar_pagina(
    doc, projeto: Projeto, pagina: ConfigPagina, dpi: int = DPI_PREVIA
) -> tuple[np.ndarray, bool]:
    """Imagem final de uma página de saida, do jeito que ela vai sair.

    Devolve (imagem, monocromatica). E o que a prévia da tela 3 mostra.
    """
    folha = projeto.folhas[pagina.folha]
    img_folha = pagina_para_array(doc, folha.indice, dpi=dpi)
    img = preparar_metade(img_folha, folha, pagina, projeto)

    if not projeto.limpar:
        return img, False
    return aplicar_filtro_com_selecao(
        img, pagina.filtro, pagina.obter_selecao(), pagina.forca_preto,
        pagina.clareza_melhorar, pagina.intensidade_magico,
    )


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

                img = preparar_metade(img_folha, folha, pagina, projeto)

                if projeto.limpar:
                    img, mono = aplicar_filtro_com_selecao(
                        img, pagina.filtro, pagina.obter_selecao(),
                        pagina.forca_preto, pagina.clareza_melhorar,
                        pagina.intensidade_magico,
                    )
                else:
                    mono = False

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
