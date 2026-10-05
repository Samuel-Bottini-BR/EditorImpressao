"""O modo Misto: o Preto e branco so nas letras (Fase 2, comecada em 05/10/2026).

O PEDIDO
    Samuel, conferencia 5 (01/10/2026, X3): "eu quero ter a opcao de colocar
    [o filtro] onde eu escolher, se quero so nos textos ou nas gravuras, como
    tem no ScanTailor Advanced". Proposta aceita (D1, 02/10): "Modo Misto: o
    Preto e branco so nas letras; gravuras e fotos ficam como estao; e voce
    corrige a mao, marcando zonas, onde o automatico errar." E a caixinha "So
    as letras" do item 1.5 (Samuel, 30/09): "marcada, so as letras viram preto
    e branco, e gravuras, fotos, molduras, iluminuras e outros detalhes
    coloridos ficam como no original. Vale para o livro inteiro ou para uma
    pagina so."

O QUE FAZ (aplicar_misto), como o Misto do ScanTailor (OutputGenerator.cpp,
processWithoutDewarping; ver docs/pesquisa/fase2-mapa-scantailor.md, secao 5)
    1. a pagina INTEIRA vai a preto e branco pelo filtro de sempre
       (core.filtros.filtro_preto_e_branco: escolha Sauvola/Otsu, o vermelho
       e a letra colorida saem pretos, limpeza de pontinhos);
    2. a MASCARA DA IMAGEM diz, ponto a ponto, onde fica o original: a gravura
       achada sozinha (o detector do ScanTailor do item 1.2, ja guardada na
       marcacao da pagina) corrigida pelas zonas feitas a mao (ver
       _peso_da_imagem);
    3. dentro da mascara, cada zona (pedaco ligado) e tratada pelo que ela e
       (core.filtros._tipos_das_zonas, a mesma pergunta do Preto e branco):
         - FOTO ou PINTURA de tom continuo: os pontos do original, sem mudar
           nada (foto_em_cinza=True: em tons de cinza, como no Preto e branco
           desde 30/09 - variante para o Samuel escolher);
         - DECORACAO COLORIDA (moldura dourada, iluminura): a cor original,
           so o papel vai a branco, e a letra solta no papel dela sai preta -
           e EXATAMENTE o que o Preto e branco de hoje ja faz (emenda N2 e
           decisao P4 do Samuel);
         - GRAVURA DE TRACO (xilogravura, retrato, diagrama): os pontos do
           original, so o papel DELA vai a branco
           (_gravura_de_traco_com_o_papel_branco; onde essa conta desiste, a
           da decoracao, sem a letra preta - a hachura viraria preto chapado);
       papel_da_gravura_branco=False: nada vai a branco dentro das zonas (o
       Misto puro do ScanTailor, em que o papel da gravura fica creme);
    4. o "so neste pedaco" com outro filtro (Regiao.filtro, aba Marcar) vale
       por cima, como nos outros filtros (core.filtros._filtro_so_no_pedaco);
    5. o papel marcado vai a branco por ultimo.

    Pagina sem nenhuma zona de imagem (e sem "so neste pedaco"): sai
    IDENTICA ao Preto e branco de hoje, em 1 bit.

LIGADO AO PROGRAMA (05/10/2026)
    A caixinha "So as letras" e as escolhas moram no projeto (modelos.Projeto
    e ConfigPagina, CAMPOS_DO_MISTO; o que vale numa pagina: opcoes_da_pagina).
    core.pipeline._filtrar chama aplicar_misto na pagina em Preto e branco com
    "So as letras" ligada - a previa e o PDF pelo mesmo caminho -, com as
    linhas do leitor de texto (core/linhas_do_texto.py) quando a opcao e A ou
    C. Sem "So as letras", o caminho de sempre
    (core.filtros.aplicar_filtro_com_selecao) nao foi tocado. Tambem roda por
    linha de comando (montar_misto.py, so a opcao B).

O QUE E SEGURO MUDAR
    Os padroes de papel_da_gravura_branco e foto_em_cinza (sao a pergunta ao
    Samuel); a ordem dos passos 4 e 5.

O QUE E ARRISCADO MUDAR
    - _peso_da_imagem: e ela que diz que a marcacao A MAO ganha da maquina.
      Deixar a letra AUTOMATICA furar a gravura poria tracos da foto em preto
      e branco (o detector marca letra em volta da gravura).
    - Usar outro preto e branco no passo 1: as regras aprovadas do Preto e
      branco (vermelho preto, letra colorida, medidor) moram em
      filtro_preto_e_branco.
    - A sequencia da decoracao (pintar o papel, _com_a_decoracao, misturar o
      papel): e a mesma de _preto_e_branco_com_gravura, e o teste
      test_so_moldura_da_o_mesmo_que_o_preto_e_branco_de_hoje confere.
    - Rodar o Melhorar dentro da gravura: e o que escurecia o dourado e lavava
      a iluminura (ver o comentario de DECORACAO_CROMA em core/filtros.py).

Nao importa ui/. Uma pagina por vez. Nunca levanta excecao de OpenCV para
fora: vira core.filtros.ErroFiltro, como os outros filtros.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from core import filtros as F
from core.selecao import GRAVURA, LETRA, MAO, PAPEL, SOMAR, SUBTRAIR, _desenhar


# --- A, B e C: a tinta fora das linhas do leitor (05/10/2026) --------------
#
# Pedido do Samuel (05/10): "Quero ver o lado a lado antes de decidir: A, B e
# C, com o detector de gravura ligado [...] A opcao D fica de fora, porque o
# papel tem que sair branco." Pesquisa: docs/pesquisa/fase2-misto-letras-fora-
# do-ocr.md (secoes 4 e 9). Valem SO fora das gravuras (a imagem continua como
# no original em qualquer uma) e SO quando ha linhas; sem linha nenhuma, as tres
# dao o Misto de sempre (o leitor nao achou texto: nao ha como saber o escuro
# da letra, e apagar tudo seria perder a pagina).
#   B, FORA_TUDO   - tudo o que nao e gravura vira preto e branco (o Misto do
#                    ScanTailor). O padrao da FUNCAO aplicar_misto (sem linhas).
#   A, FORA_REDE   - "rede de seguranca" (DE FABRICA no programa, conferencia
#                    14): dentro das linhas, o preto e branco de sempre;
#                    fora delas, cada pedaco de tinta (pedaco ligado do
#                    preto e branco) fica se tem pelo menos um ponto tao
#                    escuro quanto as letras desta pagina (a mediana do cinza
#                    da tinta DENTRO das linhas) e area de pelo menos
#                    (altura da linha / 6)^2; o resto (a mancha clara) vai a
#                    branco. Guarda nota de musica, capitular, letrinha de
#                    diagrama; tira a escrita clara do verso.
#   C, FORA_APAGAR - so o que esta dentro das linhas fica; o resto vai a branco.
#                    Apaga a musica do Graduale: nunca de fabrica.
# Arriscado: usar a rede para decidir gravura (a moldura dourada clara iria a
# branco - pesquisa, 4.3, Horas 13); baixar a area minima (a poeira volta).
FORA_TUDO = "tudo"
FORA_REDE = "rede"
FORA_APAGAR = "apagar"
FORAS_DO_TEXTO = (FORA_TUDO, FORA_REDE, FORA_APAGAR)
# as linhas do leitor sao alargadas esta fracao da altura delas (como no 1.3:
# o docTR nao cobre a perna das letras que o Kraken cobre)
FOLGA_DAS_LINHAS = 0.15
# a area minima de um pedaco guardado pela rede, em (altura da linha / isto)^2
PEDACO_MINIMO_DA_REDE = 6.0


# --- as escolhas do Misto no projeto (ligar ao programa, 05/10/2026) ----------
#
# Pedido do Samuel (conferencia 10, P1 (a)): a caixinha "So as letras" dentro
# do Preto e branco, "para o livro (tela 'O que fazer') e para a pagina (aba
# Filtro)". Regra geral (conferencia 12): "esse programa deve presar por dar
# opcoes" - a escolha dele e o padrao de fabrica e as outras ficam disponiveis.
#
# fora_do_texto (conferencia 8: "Escolher dentro do programa: sim, e tem que
#   ser algo bem visivel"; conferencia 14, PADRAO (1): A de fabrica, linhas
#   achadas so com o leitor rapido):
#     FORA_REDE   A "Guardar a tinta forte"     (de fabrica)
#     FORA_TUDO   B "Tudo em preto e branco"
#     FORA_APAGAR C "So o texto achado"
# papel_da_gravura (conferencia 12, P2 (a)): o papel de dentro da gravura de
#   traco vai a branco (de fabrica) ou fica como foi escaneado ("eu deixar
#   todas as gravuras originais e nao mexer nelas").
# letras_na_moldura (conferencia 12, P4 (a), com (b) e (c) disponiveis): as
#   letras dentro da moldura dourada ou da iluminura (o oval da Horas 11,
#   "NOVEMBRE."):
#     LETRAS_COR_PAPEL_BRANCO    com a cor delas e o papel branco atras (de fabrica)
#     LETRAS_COR_FUNDO_ORIGINAL  com a cor delas e o fundo como foi escaneado
#                                (a moldura/iluminura inteira como no original)
#     LETRAS_PRETAS              pretas, com o papel branco atras (o Preto e
#                                branco de hoje, decisao P4 de 01/10)
# Foto e pintura no Misto: sempre com a cor original (conferencia 11, P3 (a);
#   em preto e branco so sem "So as letras", ou com "so neste pedaco").
#
# Os valores sao os gravados no projeto.json: mudar o TEXTO de um deles faz o
# projeto salvo voltar ao padrao (opcoes_da_pagina corrige o desconhecido).
# Seguro mudar: os padroes (sao decisao do Samuel). Arriscado: renomear.
PAPEL_BRANCO = "branco"
PAPEL_COMO_ESCANEADO = "como_escaneado"
PAPEIS_DA_GRAVURA = (PAPEL_BRANCO, PAPEL_COMO_ESCANEADO)
LETRAS_COR_PAPEL_BRANCO = "cor_papel_branco"
LETRAS_COR_FUNDO_ORIGINAL = "cor_fundo_original"
LETRAS_PRETAS = "pretas"
LETRAS_NA_MOLDURA = (LETRAS_COR_PAPEL_BRANCO, LETRAS_COR_FUNDO_ORIGINAL, LETRAS_PRETAS)

FORA_DO_TEXTO_PADRAO = FORA_REDE
PAPEL_DA_GRAVURA_PADRAO = PAPEL_BRANCO
LETRAS_NA_MOLDURA_PADRAO = LETRAS_COR_PAPEL_BRANCO

# Os campos do Misto, com o MESMO nome no livro (modelos.Projeto, com o valor
# de fabrica) e na pagina (modelos.ConfigPagina, None = segue o livro). Quem
# copia as opcoes do livro de um projeto para outro (ui/janela_principal) e
# quem os testa le esta lista.
CAMPOS_DO_MISTO = ("misto_so_as_letras", "misto_fora_do_texto",
                   "misto_papel_da_gravura", "misto_letras_na_moldura")


@dataclass(frozen=True)
class OpcoesDoMisto:
    """As escolhas do Misto que valem numa pagina (ver opcoes_da_pagina)."""

    fora_do_texto: str = FORA_DO_TEXTO_PADRAO
    papel_da_gravura: str = PAPEL_DA_GRAVURA_PADRAO
    letras_na_moldura: str = LETRAS_NA_MOLDURA_PADRAO

    @property
    def precisa_das_linhas(self) -> bool:
        """A e C precisam saber onde esta o texto (o leitor de texto); B nao."""
        return self.fora_do_texto != FORA_TUDO


def _da_pagina_ou_do_livro(projeto, pagina, campo: str):
    """O valor do campo na pagina; None (ou sem o campo) = o do livro."""
    valor = getattr(pagina, campo, None)
    return getattr(projeto, campo, None) if valor is None else valor


def escolhas_da_pagina(projeto, pagina) -> tuple[bool, OpcoesDoMisto]:
    """(so_as_letras, escolhas) que valem nesta pagina, com "So as letras"
    ligada ou nao (a tela mostra os tres botoes com a escolha de agora, para
    quando a caixinha for marcada).

    A pagina herda cada campo do livro (modelos.Projeto) e pode trocar so nela
    (modelos.ConfigPagina, None = segue o livro). Projeto de versao anterior,
    sem os campos: desligado, com os padroes. Valor desconhecido (arquivo
    mexido, versao futura): o padrao de fabrica. Barato (so le campos)."""
    ligado = _da_pagina_ou_do_livro(projeto, pagina, "misto_so_as_letras") is True
    fora = _da_pagina_ou_do_livro(projeto, pagina, "misto_fora_do_texto")
    papel = _da_pagina_ou_do_livro(projeto, pagina, "misto_papel_da_gravura")
    letras = _da_pagina_ou_do_livro(projeto, pagina, "misto_letras_na_moldura")
    return ligado, OpcoesDoMisto(
        fora_do_texto=fora if fora in FORAS_DO_TEXTO else FORA_DO_TEXTO_PADRAO,
        papel_da_gravura=papel if papel in PAPEIS_DA_GRAVURA else PAPEL_DA_GRAVURA_PADRAO,
        letras_na_moldura=letras if letras in LETRAS_NA_MOLDURA else LETRAS_NA_MOLDURA_PADRAO)


def alguma_precisa_das_linhas(projeto) -> bool:
    """Alguma pagina em Preto e branco esta no Misto A ou C (precisa do leitor
    de texto)? Para a tela aquecer o leitor antes da primeira previa
    (core.linhas_do_texto.aquecer_em_segundo_plano). Sem "Limpar a folha",
    nenhum filtro vale: False. Barato (so le campos)."""
    if not getattr(projeto, "limpar", True):
        return False
    for pagina in getattr(projeto, "paginas", []):
        if getattr(pagina, "filtro", None) != F.PRETO_E_BRANCO or getattr(pagina, "apagada", False):
            continue
        opcoes = opcoes_da_pagina(projeto, pagina)
        if opcoes is not None and opcoes.precisa_das_linhas:
            return True
    return False


def opcoes_da_pagina(projeto, pagina) -> OpcoesDoMisto | None:
    """As escolhas do Misto desta pagina, ou None se o Misto nao vale nela
    (ver escolhas_da_pagina). Nao olha o filtro: quem chama so pergunta para
    pagina em Preto e branco (core.pipeline._filtrar)."""
    ligado, opcoes = escolhas_da_pagina(projeto, pagina)
    return opcoes if ligado else None


def mascara_das_linhas(resultados, forma: tuple[int, int]) -> tuple[np.ndarray, float]:
    """(mascara, altura_linha): a uniao das linhas dos leitores de texto
    (core.ocr_comum.ResultadoOCR, um por leitor; o indisponivel nao conta),
    alargada FOLGA_DAS_LINHAS da altura mediana delas, no tamanho `forma`
    (altura, largura) da pagina. Sem linha nenhuma: mascara vazia e 0,0."""
    altura, largura = forma[:2]
    tela = np.zeros((altura, largura), np.uint8)
    alturas: list[float] = []
    for r in resultados:
        if r is None or not r.disponivel:
            continue
        fx = largura / r.largura if r.largura else 1.0
        fy = altura / r.altura if r.altura else 1.0
        for linha in r.linhas:
            pontos = np.asarray(linha.poligono, np.float64) * (fx, fy)
            if len(pontos) < 3 or not np.isfinite(pontos).all():
                continue
            alturas.append(float(pontos[:, 1].max() - pontos[:, 1].min()))
            cv2.fillPoly(tela, [np.round(pontos).astype(np.int32)], 255)
    if not alturas:
        return tela > 0, 0.0
    altura_linha = float(np.median(alturas))
    raio = int(round(FOLGA_DAS_LINHAS * altura_linha))
    if raio >= 1:
        tela = cv2.dilate(tela, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                          (2 * raio + 1, 2 * raio + 1)))
    return tela > 0, altura_linha


def _fora_do_texto(binaria: np.ndarray, cinza: np.ndarray, linhas: np.ndarray,
                   altura_linha: float, modo: str, fora_da_imagem: np.ndarray,
                   medidas: dict | None = None) -> np.ndarray:
    """O preto e branco da pagina com a opcao `modo` aplicada a tinta fora das
    linhas e fora da imagem (ver o comentario de FORA_TUDO). binaria: 0 =
    tinta. Nunca muda a tinta de dentro das linhas. medidas recebe:
    tinta_fora (fracao da tinta da pagina fora das linhas e da imagem),
    forte_fora (fracao dela que e "tinta forte": os pedacos que a rede
    guarda, medidos tambem no C, onde vao a branco - e o que manda a pagina
    para "Para revisar", core.pipeline), guardada_fora (fracao que ficou la
    fora: = forte_fora no A, 0 no C) e escuro_da_letra."""
    tinta = binaria == 0
    total = int(np.count_nonzero(tinta)) or 1
    fora = tinta & ~linhas & fora_da_imagem
    saida = binaria.copy()
    forte = np.zeros_like(fora)
    escuro = None
    dentro = tinta & linhas
    if modo in (FORA_REDE, FORA_APAGAR) and dentro.any() and fora.any():
        escuro = float(np.median(cinza[dentro]))
        quantos, rotulos, stats, _c = cv2.connectedComponentsWithStats(
            fora.view(np.uint8), connectivity=8)
        if quantos > 1:
            fica = np.zeros(quantos, bool)
            fica[np.unique(rotulos[fora & (cinza <= escuro)])] = True
            minimo = (max(altura_linha, 1.0) / PEDACO_MINIMO_DA_REDE) ** 2
            fica &= stats[:, cv2.CC_STAT_AREA] >= minimo
            fica[0] = False
            forte = fica[rotulos]
    elif dentro.any():
        escuro = float(np.median(cinza[dentro]))
    guardar = forte if modo == FORA_REDE else np.zeros_like(fora)
    saida[fora & ~guardar] = 255
    if medidas is not None:
        medidas.update({"tinta_fora": float(np.count_nonzero(fora)) / total,
                        "forte_fora": float(np.count_nonzero(forte)) / total,
                        "guardada_fora": float(np.count_nonzero(guardar)) / total,
                        "escuro_da_letra": escuro})
    return saida


def _tira_a_imagem(regiao) -> bool:
    """Esta regiao manda o ponto para o preto e branco, mesmo dentro de uma
    gravura? A LETRA marcada A MAO (o ZONEERASER1 do ScanTailor, "subtrair da
    camada automatica") e qualquer regiao com "so neste pedaco" em Preto e
    branco. A letra que a maquina achou nao conta (ver o topo)."""
    if regiao.operacao != SOMAR:
        return False
    return (regiao.tipo == LETRA and regiao.origem == MAO) or regiao.filtro == F.PRETO_E_BRANCO


def _peso_da_imagem(selecao, altura: int, largura: int) -> np.ndarray:
    """Onde a pagina fica como imagem (0 a 1, borda suave como a da gravura).

    Sem regiao que tire a imagem (_tira_a_imagem), e exatamente o peso da
    gravura (Selecao.peso), o mesmo que o Preto e branco de hoje usa. Com
    ela, as regioes sao percorridas NA ORDEM em que foram feitas: gravura de
    somar acende, gravura de tirar apaga, e a regiao que tira a imagem apaga
    - uma gravura marcada depois dela volta a valer. A suavidade e a da
    gravura (a mesma conta de Selecao.peso)."""
    if not any(_tira_a_imagem(r) for r in selecao.regioes if r.valida()):
        return selecao.peso(altura, largura, GRAVURA)
    tela = np.zeros((altura, largura), np.uint8)
    for regiao in selecao.regioes:
        if not regiao.valida():
            continue
        tira = _tira_a_imagem(regiao)
        if regiao.tipo != GRAVURA and not tira:
            continue
        camada = np.zeros_like(tela)
        _desenhar(camada, regiao)
        if tira or regiao.operacao == SUBTRAIR:
            tela[camada > 0] = 0
        else:
            tela = np.maximum(tela, camada)
    dura = (tela > 0).astype(np.float32)
    suavidades = [r.suavidade for r in selecao.regioes if r.tipo == GRAVURA and r.suavidade > 0]
    if not suavidades or not dura.any():
        return dura
    sigma = max(0.6, max(suavidades) * min(altura, largura) / 2.0)
    return np.clip(cv2.GaussianBlur(dura, (0, 0), sigmaX=sigma, sigmaY=sigma), 0, 1)


def _onde_tira_a_imagem(selecao, altura: int, largura: int) -> np.ndarray | None:
    """Mascara booleana das regioes que tiram a imagem (_tira_a_imagem), sem
    olhar a ordem; None se nao ha nenhuma."""
    regioes = [r for r in selecao.regioes if r.valida() and _tira_a_imagem(r)]
    if not regioes:
        return None
    tela = np.zeros((altura, largura), np.uint8)
    for regiao in regioes:
        _desenhar(tela, regiao)
    return tela > 0


def _gravura_de_traco_com_o_papel_branco(img3: np.ndarray, rotulos: np.ndarray,
                                         desenho: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(tratada, sobra): a pagina com cada zona de gravura de traco (desenho:
    booleano por rotulo) nos pontos do original e so o papel DELA a branco
    (core.filtros._so_o_papel_da_gravura, a conta feita para o retrato do
    Palatino 5: o papel e medido entre os tracos da propria gravura, que e
    mais escuro e mais amarelo que a margem da folha). sobra: os rotulos em
    que a conta desistiu (pouco traco para medir o papel; ela devolve o
    pedaco como estava) - quem chama usa outra conta neles.

    Testado em 05/10 (relatorios/fase2-misto-2026-10-05/teste-papel/): a
    conta da decoracao (papel pela cor do papel da PAGINA) deixava o fundo do
    retrato do Palatino 5 amarelo e trazia a mancha de fora do oval; esta o
    deixa branco, com o traco marrom do original. Arriscado: trocar o
    `original` por uma versao filtrada (o tom do traco deixaria de ser o do
    original)."""
    tratada = img3.copy()
    sobra = np.zeros_like(desenho)
    for i in np.flatnonzero(desenho):
        x, y, w, h = cv2.boundingRect((rotulos == i).astype(np.uint8))
        pedaco = np.ascontiguousarray(img3[y:y + h, x:x + w])
        feito = F._so_o_papel_da_gravura(pedaco, pedaco)
        if feito is pedaco:
            sobra[i] = True
        else:
            tratada[y:y + h, x:x + w] = feito
    return tratada, sobra


def _so_das(rotulos: np.ndarray, zonas: np.ndarray, peso: np.ndarray) -> np.ndarray:
    """O peso so das zonas pedidas (zonas: booleano por rotulo); se sao
    todas, o peso inteiro (sem a conta ponto a ponto)."""
    if zonas[1:].all():
        return peso
    return np.where(zonas[rotulos], peso, 0.0).astype(np.float32)


def aplicar_misto(
    img: np.ndarray,
    selecao,
    forca_preto: int = F.AJUSTE_PADRAO,
    algoritmo_pb: str = "auto",
    despeckle: bool = True,
    clareza: int = F.AJUSTE_PADRAO,
    intensidade: int = F.AJUSTE_PADRAO,
    *,
    papel_da_gravura_branco: bool = True,
    foto_em_cinza: bool = False,
    letras_na_moldura: str = LETRAS_NA_MOLDURA_PADRAO,
    fora_do_texto: str = "tudo",
    linhas: np.ndarray | None = None,
    altura_linha: float = 0.0,
    medidas: dict | None = None,
) -> tuple[np.ndarray, bool]:
    """O Preto e branco so nas letras; o resto como no original (ver o topo).

    EXPERIMENTAL (parte C, 05/10/2026; ver _fora_do_texto): fora_do_texto diz
    o que acontece com a tinta FORA das linhas do leitor de texto e fora das
    gravuras - FORA_TUDO (de fabrica, o Misto de sempre), FORA_REDE (a rede de
    seguranca) ou FORA_APAGAR (so as linhas). linhas: mascara booleana das
    linhas (mascara_das_linhas), altura_linha: a altura mediana delas, em
    pontos. Sem linhas, as tres opcoes dao o mesmo. medidas (dict, opcional):
    recebe o que a opcao fez (ver _fora_do_texto).

    img: a pagina ja preparada (dividida, cortada, endireitada), BGR ou cinza.
    selecao: a marcacao da pagina (core.selecao.Selecao; None = nenhuma).
    forca_preto, algoritmo_pb, despeckle: os do Preto e branco da pagina
    (ConfigPagina.forca_preto, algoritmo_preto_branco, despeckle).
    clareza, intensidade: so para o "so neste pedaco" em Melhorar ou Magico
    pro. Devolve (imagem, monocromatica), como aplicar_filtro_com_selecao:
    monocromatica=True quando tudo saiu em preto e branco (1 canal, 0 e 255).

    papel_da_gravura_branco: o papel de dentro da GRAVURA DE TRACO vai a
    branco (P2 (a), de fabrica) ou fica como foi escaneado (False).
    letras_na_moldura: o que acontece na DECORACAO COLORIDA (moldura dourada,
    iluminura) e nas letras dentro dela (P4; ver LETRAS_NA_MOLDURA no topo):
    a cor delas com o papel branco (de fabrica), a decoracao inteira como foi
    escaneada, ou letras pretas com o papel branco. As duas escolhas sao
    independentes (ate 05/10 o papel_da_gravura_branco=False tambem deixava a
    decoracao como escaneada; agora isso e letras_na_moldura =
    LETRAS_COR_FUNDO_ORIGINAL). foto_em_cinza: so para o script de comparacao
    (no programa a foto fica sempre com a cor, P3 (a)).
    """
    usa_linhas = fora_do_texto != FORA_TUDO and linhas is not None and bool(np.any(linhas))
    if (selecao is None or getattr(selecao, "vazia", True)) and not usa_linhas:
        return F.aplicar_filtro(img, F.PRETO_E_BRANCO, forca_preto, clareza, intensidade,
                                algoritmo_pb=algoritmo_pb, despeckle=despeckle)
    if selecao is None:
        from core.selecao import Selecao

        selecao = Selecao()
    try:
        return _misto(img, selecao, forca_preto, algoritmo_pb, despeckle, clareza, intensidade,
                      papel_da_gravura_branco, foto_em_cinza,
                      fora_do_texto if usa_linhas else FORA_TUDO, linhas, altura_linha, medidas,
                      letras_na_moldura)
    except cv2.error as exc:
        raise F.ErroFiltro("Não consegui limpar esta página.") from exc


def _misto(img, selecao, forca_preto, algoritmo_pb, despeckle, clareza, intensidade,
           papel_da_gravura_branco, foto_em_cinza, fora_do_texto=None, linhas=None,
           altura_linha=0.0, medidas=None,
           letras_na_moldura=LETRAS_NA_MOLDURA_PADRAO) -> tuple[np.ndarray, bool]:
    altura, largura = img.shape[:2]
    peso_imagem = _peso_da_imagem(selecao, altura, largura)
    peso_papel = selecao.peso(altura, largura, PAPEL)
    # a borda suave do papel nao passa por cima da letra (a mesma protecao do
    # Preto e branco: ver core.filtros._peso_do_papel_sem_tocar_a_tinta), menos
    # quando a folha inteira foi marcada como papel ("quero esta folha em branco")
    if peso_papel.any() and float((peso_papel > 0.5).mean()) < F.FOLHA_INTEIRA_EM_BRANCO:
        peso_papel = F._peso_do_papel_sem_tocar_a_tinta(img, peso_papel)

    binaria = F.filtro_preto_e_branco(img, forca=forca_preto, algoritmo=algoritmo_pb,
                                      despeckle=despeckle)
    if fora_do_texto not in (None, FORA_TUDO):
        binaria = _fora_do_texto(binaria, F._cinza_para_binarizar(img), linhas, altura_linha,
                                 fora_do_texto, ~(peso_imagem > 0), medidas)
    pedidos = [f for f in selecao.filtros_pedidos()
               if f in F.FILTROS_COMUNS and f != F.PRETO_E_BRANCO]

    if not peso_imagem.any() and not pedidos:
        # so letra e papel: o Preto e branco de hoje, ponto por ponto (o mesmo
        # ramo de aplicar_filtro_com_selecao sem gravura)
        saida = binaria
        if peso_papel.any():
            saida = F._misturar(saida, np.full_like(saida, 255), peso_papel)
        return saida, True

    img3 = F._tres_canais(img)
    saida = binaria.copy()
    if peso_papel.any():
        F._pintar_de_branco(saida, peso_papel >= 0.5)

    if peso_imagem.any():
        rotulos, foto, decoracao, referencia = F._tipos_das_zonas(img3, peso_imagem)
        desenho = ~(foto | decoracao)
        desenho[0] = False

        if foto.any():
            peso_foto = _so_das(rotulos, foto, peso_imagem)
            # a foto que quase enche o fecho convexo dela vale o fecho inteiro
            # (o rosto da estatua do Opus 20 que o contorno livre deixa de
            # fora; conferencia 5, F1): a mesma conta do Preto e branco
            fechos = F._fechos_de_foto(rotulos, foto, peso_imagem)
            if fechos is not None:
                dentro = (fechos > 0) & (peso_foto < 1.0)
                # ...menos onde a pessoa tirou a imagem a mao (o fecho nao
                # pode desfazer a letra marcada a mao num canto da foto)
                tirado = _onde_tira_a_imagem(selecao, altura, largura)
                if tirado is not None:
                    dentro &= ~tirado
                peso_foto = np.where(dentro, 1.0, peso_foto).astype(np.float32)
                peso_papel = np.where(dentro, 0.0, peso_papel).astype(np.float32)
            if foto_em_cinza and saida.ndim == 2:
                tons = saida.copy()
                bx, by, bw, bh = cv2.boundingRect((peso_foto > 0).astype(np.uint8))
                y0, y1 = max(0, by - 4), min(altura, by + bh + 4)
                x0, x1 = max(0, bx - 4), min(largura, bx + bw + 4)
                tons[y0:y1, x0:x1] = F._foto_em_tons_de_cinza(
                    img3[y0:y1, x0:x1], F._niveis_da_foto(img3, peso_imagem > 0))
                saida = F._misturar(saida, tons, peso_foto)
            else:
                saida = F._misturar(F._tres_canais(saida).copy(), img3, peso_foto)

        if desenho.any():
            peso_desenho = _so_das(rotulos, desenho, peso_imagem)
            base = F._tres_canais(saida).copy()
            if papel_da_gravura_branco:
                tratada, sobra = _gravura_de_traco_com_o_papel_branco(img3, rotulos, desenho)
                saida = F._misturar(base, tratada, peso_desenho)
                if sobra.any():
                    # a zona em que a conta da gravura desistiu (pouco traco
                    # para medir o papel dela): a conta da decoracao, pelo
                    # papel da pagina
                    saida = F._com_a_decoracao(
                        F._tres_canais(saida).copy(), img3, _so_das(rotulos, sobra, peso_imagem),
                        referencia or F._referencia_do_papel(img3, peso_imagem > 0),
                        letras_pretas=False)
            else:
                saida = F._misturar(base, img3, peso_desenho)

        if decoracao.any():
            peso_decoracao = _so_das(rotulos, decoracao, peso_imagem)
            base = F._tres_canais(saida).copy()
            if letras_na_moldura == LETRAS_COR_FUNDO_ORIGINAL:
                # P4 (b): a moldura/iluminura inteira como foi escaneada
                saida = F._misturar(base, img3, peso_decoracao)
            else:
                # P4 (a) a cor das letras com o papel branco atras; (c) as
                # letras soltas pretas - a mesma conta do Preto e branco
                saida = F._com_a_decoracao(base, img3, peso_decoracao, referencia,
                                           letras_pretas=letras_na_moldura == LETRAS_PRETAS)

    if pedidos:
        # "so neste pedaco" com outro filtro: por cima, so no conteudo do
        # pedaco (o papel dele segue a pagina) - core.filtros._filtro_so_no_pedaco
        saida = F._filtro_so_no_pedaco(img, saida, selecao, F.PRETO_E_BRANCO,
                                       forca_preto, clareza, intensidade)

    if peso_papel.any():
        saida = F._misturar(saida, np.full_like(saida, 255), peso_papel)
    return saida, False
