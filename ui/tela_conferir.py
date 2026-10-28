"""TELA 3 - Conferir: a prévia e todos os ajustes manuais.

Empilhamento da tela, de cima para baixo, sem nenhuma sobreposicao:

    1. cabecalho (titulo, contador de alertas, desfazer/refazer)
    2. barra de abas
    3. área da imagem            <- fica com todo o espaço que sobrar
    4. faixa de explicação
    5. linha de botões
    6. tira de miniaturas
    7. onde salvar
    8. rodape (voltar / confirmar e processar)

Tudo isso num único QVBoxLayout. A faixa e os botões NAO moram dentro das
páginas das abas: elas guardam só a imagem. Foi por isso que a versão anterior
sobrepunha - a página da aba não tinha altura para caber imagem + faixa +
botões, e o Qt acabava empilhando um por cima do outro.

Por isso tambem usamos QTabBar (só a barra) com QStackedWidget, e não
QTabWidget: assim a faixa e os botões ficam de fora, como irmaos.

As abas (por dentro; na tela são as ferramentas da trilha) existem TODAS em
todo livro, com qualquer caixinha da tela 2 marcada ou nenhuma - D-001, etapa
2 da obra de 26/10/2026 (antes só existiam as das caixinhas marcadas: a
regra de julho do `carregar`). Cada uma edita uma unidade diferente:

    Onde cortar -> FOLHA do PDF de entrada (a linha da lombada)
    Bordas      -> PAGINA de saida (o retangulo do recorte)
    Endireitar  -> PAGINA de saida (o ângulo)
    Filtro      -> PAGINA de saida (o filtro e a força do preto)

O alerta chama atenção, nunca restringe: todo controle continua disponível em
qualquer página, com ou sem alerta.

Item 1.1 (29/09/2026): em PDF com camadas a aba Filtro ganha o quinto cartão,
"Tirar o fundo" (core.filtros.filtros_do_livro). Ele mostra o resultado de
verdade do core/camadas.py (core.pipeline.renderizar_com_filtro, pedido ao
GerenciadorPrevias como qualquer prévia), e não um filtro comum. O alerta
"Conferir o fundo tirado" é acertado a cada atualização da tela
(core.pipeline.acertar_alertas_do_fundo) e quando a prévia chega.

Modo Misto (05/10/2026; provisório até o layout, exceção da gerente para o
implementador mexer aqui): no bloco AJUSTE da aba Filtro, só com o Preto e
branco escolhido, a caixinha "Só as letras" desta página, os três botões
("Guardar a tinta forte" / "Guardar tudo" / "Guardar só o texto") e o
"Mais opções" (ui/widgets/escolhas_do_misto.py). A página herda do livro e
troca só nela (ConfigPagina.misto_*); cada mudança é uma ação do desfazer,
como o algoritmo e o "Limpar pontinhos". "todas" e "só nas próximas" levam
junto as escolhas do Misto desta página. O aviso "Tinta forte fora do texto"
é acertado como o do fundo tirado. O alerta "Tem cor" some das páginas que
saem pelo "Só as letras" (a ilustração fica em cor) e volta quando ela é
desligada, a cada atualização, em todas as páginas
(core.pipeline.acertar_alertas_de_cor; bug Misto 1 do verificador, 05/10).
Com "Só as letras" valendo na página, o cartão "Preto e branco" mostra a
página como vai sair, com o Misto, desenhada numa tarefa de prévia
(_cartao_do_misto; bug Misto 2).

Limpar pontinhos (decisão do Samuel de 06/10/2026, P7; provisório até o
layout, exceção da gerente para o implementador mexer aqui): no bloco AJUSTE,
só com o Preto e branco, a lista "Limpar a sujeira:" (Sem limpeza · Limpeza
bruta · Limpeza cuidadosa leve, média e forte; nomes escolhidos pelo Samuel
em 07/10/2026, Rodada 10 do layout, pergunta 501; antes "Limpar pontinhos:"
desligado · o nosso · pouco · normal · muito; os textos moram em
core/pontinhos_scantailor.py) no lugar da caixinha "limpar poeirinha". Mostra o que
vale na página (dela ou do livro: core.pontinhos_scantailor.escolha_da_pagina);
trocar é uma ação do desfazer só desta página (ConfigPagina.limpar_pontinhos);
"todas" e "só nas próximas" levam a escolha junto.

Girar a folha (item 2.3, 06/10/2026; provisório até o layout, exceção da
gerente para o implementador mexer aqui): a barrinha de girar
(ui/widgets/barra_girar.py) fica na linha das abas, à direita, em todas as
abas: 1/4 à esquerda, 1/4 à direita, meia volta e "aplicar em" (só esta /
todas / daqui em diante / só as pares / só as ímpares). Cada clique é UMA
ação do desfazer, com a rotação nova de cada folha (_girar_folhas; contas em
core/girar.py). O menu Página tem os mesmos giros (Ctrl+Esquerda,
Ctrl+Direita) e o mesmo "aplicar em". A tecla R deixou de girar (era fixa
aqui e nunca alcançada: a R do Retângulo ganhava).

Dividir (item 2.1, 06/10/2026, decisão G2 (a) do Samuel: "trocando numa
folha se um ficar ruim"; provisório até o layout, pedido da gerente): na
linha de botões da aba Onde cortar, a lista "jeito:" (o do programa · o do
ScanTailor) troca o jeito SÓ desta folha e recalcula a linha azul
(_trocar_jeito_da_folha; ConfigFolha.dividir_como), numa ação do desfazer;
só habilitada em folha dividida. Conserto junto: "não dividir esta" apaga na
mesma ação a metade da direita (antes o PDF saía com a folha repetida); a
folha que entrou como uma página só não oferece "dividir esta"
(_alternar_dividir).
Obra de 26/10/2026, etapa 4 (dividir à mão folha por folha): "dividir esta"
fica SEMPRE aceso e divide também a folha que entrou como uma página só (a
lista de páginas muda só no pedaço desta folha: core/dividir_a_mao); "não
dividir esta" junta as duas páginas numa só e as guarda; a tampa do scanner
achada ao dividir à mão sai branca (D-495). D-007: o livro abre e volta do
Automático mostrando uma página por vez; a folha inteira com a linha só
aparece dentro da ferramenta Dividir (_aba_de_partida, mostrar_paginas).

Endireitar (item 2.2, 07/10/2026, decisão G4 (b) do Samuel: "O do ScanTailor
de fábrica [...] mas eu vou ter a opção de escolher"; provisório até o
layout): na linha de botões da aba Endireitar, a lista "conta:" (a do
ScanTailor · a do programa) troca a conta do endireitar automático SÓ desta
página (_trocar_conta_do_endireitar; ConfigPagina.endireitar_como), numa
ação do desfazer; ao lado, os dois ângulos que as contas acharam
(core.pipeline.angulos_medidos), para escolher olhando. A página em que
elas discordam mais de 0,3° chega em "Para revisar" (aviso C1).

Tela do endireitar (item 2.2, decisão G5 (c) do Samuel, conferência 14: "Os
dois juntos"; provisório até o layout): grade azul reta, alça e linha-guia
no visualizador (ui/widgets/visualizador.py, "A ABA ENDIREITAR"); na linha
de botões, o ângulo em número com as setas de 0,1 grau (_ajustar_angulo; a
imagem gira ao vivo e o ângulo vai para o projeto numa ação só, um instante
depois do último clique) e o "aplicar em" (só esta / todas / daqui em diante
/ só as pares / só as ímpares; core/girar.paginas_do_alcance), que vale para
o ângulo a mão, "não endireitar" e "voltar ao automático".

Layout, etapa 3 (12/10/2026; decisões do Samuel nas rodadas 7 a 12 do
"Plano de layout"): o empilhamento descrito no alto deste texto é o de antes;
o de hoje está em TelaConferir._montar. À direita há a coluna de ícones e o
painel que ela abre ao lado da página (ui/widgets/paineis.py; de fábrica,
tudo fechado). Os botões de Dividir, Cortar e Endireitar moram no painel
Propriedades, em duas partes ("Só nesta página" e "Para o livro todo"); a
sugestão laranja do aviso, "está certo" e "próxima dúvida" moram na faixa do
conferir, iguais em todas as ferramentas. Nomes novos na tela (rodada 12, 710
B; as ações e o que vai para o projeto não mudaram): "deixar como veio" (era
"não endireitar esta"), "usar o ângulo do programa" e "usar o corte do
programa" (eram "voltar ao automático"). As listas "aplicar em" dizem folha
(a do girar) ou página (a do endireitar) nas palavras de dentro (709 B).
"""

from __future__ import annotations

import functools
import dataclasses
import traceback
from pathlib import Path

import numpy as np

import atalhos
from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtCore import QLocale, QSize
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from core import analise, dividir_scantailor, girar, linhas_do_texto, misto
from core import endireitar_scantailor
from core import pontinhos_scantailor as pontinhos
from core import avisos as avisos_do_livro
from core import preto_e_branco_scantailor
from core import claro_no_escuro, cores_scantailor, desentortar_scantailor
from core import luz_scantailor
from core import etapas as etapas_core       # obra 26/10, etapa 3: a marca "mexida a mao"
from core import dividir_a_mao              # obra 26/10, etapa 4: dividir a mao folha por folha
from core.pipeline import (FORCA_DO_REFORCO, acertar_alertas_de_cor, acertar_alertas_do_fundo,
                           acertar_faixa_do_livro, angulo_aplicado,
                           angulo_da_pagina, angulos_medidos, corte_alargado, jeito_de_dividir,
                           marcas_do_aviso, recalcular_divisao)
from core.filtros import (
    ALGORITMOS_PB,
    MAGICO_PRO,
    MELHORAR,
    NOMES_AMIGAVEIS,
    NOMES_DOS_ALGORITMOS_PB,
    ORIGINAL,
    PRETO_E_BRANCO,
    TIRAR_FUNDO,
    filtros_do_livro,
    palavra_do_ajuste,
)
from historico_acoes import HistoricoAcoes, aplicar, campo_de_pagina, montar_acao
from modelos import METADE_DIREITA, Projeto
from registro import registrar_erro
from ui import estilo
from ui.estilo import estilo_da_caixinha_com_quadrado
from ui.tarefas import MARCA_DA_MEDIDA, GerenciadorPrevias
from ui.widgets.barra_girar import BarraGirar, GirarDoCanto, nomes_dos_alcances
from ui.widgets.barra_opcoes import BarraOpcoes
from ui.widgets.cartao_filtro import CartaoFiltro
from ui.widgets.escolhas_do_misto import BOTOES_DO_TEXTO, EscolhasDoMisto
from ui.widgets.menu_com_amostra import ListaComAmostra, desenho_da_limpeza
from ui.widgets.editor_selecao import (
    FERRAMENTA_RETANGULO,
    FERRAMENTAS_DE_NAVEGACAO,
    ferramenta_da_tecla,
)
from ui.widgets.paineis import (
    _nome_da_borda,
    PAINEL_FILTRO,
    PAINEL_HISTORICO,
    PAINEL_PROPRIEDADES,
    Bloco,
    NaoEspreme,
    ColunaDePaineis,
    frase_do_painel,
    lista_estreita,
    nome_da_conta,
    nome_do_jeito_de_dividir,
    risco_do_painel,
    titulo_de_parte,
    titulo_de_secao,
)
from ui.widgets.trilha_agrupada import (
    FERRAMENTA_CORTAR,
    FERRAMENTA_DIVIDIR,
    FERRAMENTA_ENDIREITAR,
    FERRAMENTA_FILTROS,
    FERRAMENTA_MOVER,
    FERRAMENTAS_DA_PAGINA,
    NOMES as NOMES_DA_TRILHA,
    TrilhaAgrupada,
)

from ui.widgets.medidor import Medidor
from ui.widgets.miniaturas import EMBAIXO, ESQUERDA, DIREITA, PainelDeMiniaturas
from ui.widgets.todas_as_paginas import ItemDaGrade, TodasAsPaginas
# obra 26/10, etapa 6 (D-015, D-006): o "Duas lado a lado" e o "antes / depois"
from ui.widgets.paginas_lado_a_lado import PaginasLadoALado
from ui.widgets.paginas_rolando import DUAS, UMA
from ui.widgets.trilha_agrupada import ferramenta_da_pagina_da_tecla, tecla_de
from ui.widgets.visualizador import (
    MODO_ANGULO,
    MODO_CONTEUDO,
    MODO_CORTE,
    MODO_RECORTE,
    Visualizador,
)

DPI_PREVIA = 110          # baixo de proposito: a tela precisa abrir em segundos

# Etapa 5 da obra (ferramenta Mover): o maior tamanho do conteúdo, em vezes o
# de como veio (o mesmo teto do arrasto, ui/widgets/visualizador.MAIOR_CONTEUDO,
# que é em vezes a área branca), e a cor da frase do aviso da parte de fora
# (D-017). Seguro mudar.
MAIOR_TAMANHO_DO_CONTEUDO = 4.0
COR_DO_AVISO_DE_FORA = "#d63031"

# O lado maior da pagina, em pontos, na conta do aviso e do botao "Ajustar o
# pedaco a figura" (conferencia 13, S3). A conta e em fracoes, entao o tamanho
# nao muda o resultado (medido na Escola 7: o mesmo a 150 DPI e na metade), so
# o tempo: ~0,05 s aqui contra ~0,2 s a 150 DPI, no fio da tela. Seguro mudar.
LADO_DO_AJUSTE = 1000

# A dica do mouse do botao "Ajustar o pedaco a figura" (conserto de
# 05/10/2026: o botao ajusta UM pedaco, o da vez, e nunca o de texto).
DICA_DO_AJUSTE = (
    "Encolhe até a figura o último pedaço que você desenhou em volta de uma "
    "figura (gravura, foto, pintura), para não sobrar papel em volta dela. Um "
    "pedaço por clique; pedaço de texto fica como está. Dá para desfazer.")

# O porque do botao apagado num pedaco de texto (regra: nunca botao apagado
# sem explicacao). A frase curta vai ao lado do botao; esta, na dica.
DICA_DO_TEXTO = (
    "Este pedaço parece texto, e não uma figura. O ajuste só serve para pedaço "
    "em volta de gravura, foto, pintura ou iluminura: no texto ele cortaria "
    "linhas e letras. O pedaço fica como você desenhou.")

# Qualidade da prévia, ajustável pelo Samuel (estilo After Effects) nas telas
# de trabalho - troca a resolução usada para renderizar a página nas abas
# Bordas/Endireitar/Marcar. "Rápida" é o valor de sempre (DPI_PREVIA); as
# outras duas custam mais memória/tempo por página, nunca acumulam páginas
# (continua sendo uma só por vez), só deixam ESSA página mais pesada.
QUALIDADES_DA_PREVIA = {"rapida": DPI_PREVIA, "media": 180, "alta": 300}
NOMES_DA_QUALIDADE = {"rapida": "Rápida", "media": "Média", "alta": "Alta"}

ABA_CORTE, ABA_BORDAS, ABA_ANGULO, ABA_FILTRO = "corte", "bordas", "angulo", "filtro"
ABA_MARCAR = "marcar"
# Etapa 5 da obra (D-008): a ferramenta "Mover e redimensionar", própria,
# separada do Cortar (_montar_aba_mover).
ABA_MOVER = "mover"
# As "abas" de dentro, uma por ferramenta, na ordem em que nascem em TODO livro
# (D-001; etapa 2 da obra, 26/10/2026). A ordem é a de sempre: quem procura uma
# aba usa _abas_ativas.index(...), nunca a posição. Seguro mudar: a ordem.
ORDEM_DAS_FERRAMENTAS = ("corte", "bordas", "angulo", "mover", "marcar", "filtro")

TITULOS = {
    ABA_CORTE: "Onde cortar",
    ABA_BORDAS: "Bordas",
    ABA_ANGULO: "Endireitar",
    ABA_MOVER: "Mover",
    ABA_MARCAR: "Marcar",
    ABA_FILTRO: "Filtro",
}

# Atalhos que não passam pelo menu (BarraDeMenu já registra os dela sozinha) -
# registrados aqui para a tela de Configurações também poder listá-los e
# remapeá-los. Ver `atalhos.py`.
CHAVE_RECORTE_ESPELHADO = "recorte_espelhado"
CHAVE_RECORTE_PROPORCAO = "recorte_proporcao_travada"
atalhos.registrar(CHAVE_RECORTE_ESPELHADO, "Recorte: espelhado", "M")
atalhos.registrar(CHAVE_RECORTE_PROPORCAO, "Recorte: proporção travada", "T")

CHAVE_NAVEGAR_ANTERIOR = "navegar_anterior"
CHAVE_NAVEGAR_PROXIMA = "navegar_proxima"
CHAVE_MARCAR_CERTO = "marcar_certo"
CHAVE_PROXIMO_ALERTA = "proximo_alerta"
atalhos.registrar(CHAVE_NAVEGAR_ANTERIOR, "Página anterior", "Left")
atalhos.registrar(CHAVE_NAVEGAR_PROXIMA, "Próxima página", "Right")
atalhos.registrar(CHAVE_MARCAR_CERTO, "Marcar como certo e avançar", "Space")
atalhos.registrar(CHAVE_PROXIMO_ALERTA, "Ir para a próxima dúvida", "Tab")

# Nomes de tecla que o QKeySequenceEdit da tela de Configurações devolve para
# essas quatro - não são letras simples, então precisam de uma tradução de
# volta para o Qt.Key que o `tratar_tecla` compara.
_QT_KEY_DAS_TECLAS_DE_NAVEGACAO = {
    "Left": Qt.Key_Left, "Right": Qt.Key_Right,
    "Space": Qt.Key_Space, "Tab": Qt.Key_Tab,
}

# Enquanto o medidor esta sendo arrastado a prévia sai menor: a 110 DPI o
# filtro nao acompanha o dedo. Ao soltar, volta para DPI_PREVIA.
DPI_ARRASTO = 55
ESPERA_ARRASTO_MS = 150   # espera antes de redesenhar, para nao refazer a cada pixel
ESPERA_COMMIT_MS = 450    # fecha a ação quando o medidor foi mexido pelo teclado

# Qual campo da página cada filtro ajusta, e como o medidor se apresenta.
CAMPO_DO_AJUSTE = {
    PRETO_E_BRANCO: "forca_preto",
    MELHORAR: "clareza_melhorar",
    MAGICO_PRO: "intensidade_magico",
}

ROTULOS_DO_AJUSTE = {
    PRETO_E_BRANCO: ("Força do preto", "mais fraco", "mais escuro"),
    MELHORAR: ("Clareza do fundo", "suave", "bem clara"),
    MAGICO_PRO: ("Intensidade", "suave", "bem forte"),
}

CARTOES = [
    (ORIGINAL, "Original", "sem mexer"),
    (PRETO_E_BRANCO, "Preto e branco", "tira o amarelado"),
    (MELHORAR, "Melhorar", "mantem a cor"),
    (MAGICO_PRO, "Mágico pro", "cor viva"),
    # Item 1.1: so em livro com camadas (ver _montar_aba_filtro).
    (TIRAR_FUNDO, "Tirar o fundo", "só o que está impresso"),
]

# A tecla de cada filtro (as mesmas do menu Filtro), escrita na fila do
# painel "Filtro da página". O "Tirar o fundo" nao tem tecla.
TECLAS_DOS_FILTROS = {ORIGINAL: "1", PRETO_E_BRANCO: "2", MELHORAR: "3", MAGICO_PRO: "4"}

# A frase de cada jeito do "Limpar a sujeira" na lista com amostra (etapa 4 do
# layout; as mesmas palavras da EXPLICACAO_NA_TELA de core/pontinhos_scantailor,
# decididas na rodada 10). Seguro mudar: os textos.
FRASES_DA_LIMPEZA = {
    pontinhos.DESLIGADO: "a sujeira fica como está",
    pontinhos.NOSSO: ("apaga todo ponto pequeno, sem olhar onde ele está: a borda da letra "
                      "fica lisa, mas some pingo do i, vírgula e tracinho de desenho"),
    pontinhos.POUCO: ("só apaga o que está longe das letras: pingo do i e pontuação ficam; "
                      "a força mais fraca"),
    pontinhos.NORMAL: "só apaga o que está longe das letras, com força média",
    pontinhos.MUITO: "só apaga o que está longe das letras, com a força mais forte",
}

# Resolucao da amostra dos cartoes de filtro (_imagem_sem_filtro): a folha
# como veio no PDF, desenhada pequena, e preparada na tela. Era o 70 escrito
# direto no codigo; virou nome em 06/10/2026 (D1) porque entra tambem na
# chave dos cartoes (_chave_dos_cartoes). Seguro mudar (so tempo e nitidez).
DPI_AMOSTRA_DOS_CARTOES = 70

# Item 1.1: resolucao do cartao "Tirar o fundo". A mesma da amostra dos outros
# cartoes (_imagem_sem_filtro). Ele e desenhado pelo caminho do programa
# (core/camadas.py, na folha inteira), numa tarefa de previa; a decisao do
# core/camadas.py nao depende da resolucao, entao o cartao mostra o mesmo que
# a pagina vai ter. Seguro mudar (so tempo e nitidez do cartao).
DPI_CARTAO_SEM_FUNDO = 70

# Modo Misto (bug Misto 2 do verificador, 05/10/2026): com "Só as letras"
# valendo na página, o cartão "Preto e branco" é a página desenhada pelo
# caminho do programa (core.pipeline.renderizar_com_filtro, com o Misto), e
# não o filtro puro na amostra - senão ele mostra a gravura em preto e branco
# e a página sai com ela em cor. Na resolução da prévia "Rápida", e não na
# dos outros cartões: o leitor de texto (opções A e C) guarda as linhas por
# nitidez (core.linhas_do_texto._serve), e achadas aqui servem para a prévia
# e o PDF (a 70 DPI a prévia acharia de novo, mais 1 a 2,5 s). Seguro mudar
# (só tempo e nitidez do cartão).
DPI_CARTAO_DO_MISTO = DPI_PREVIA


def protegido(metodo):
    """Nenhuma acao de botão pode fechar a janela (regra 3.3).

    Qualquer excecao vira aviso em portugues e vai para o arquivo de log. Sem
    isto, um erro dentro de um slot do Qt derruba o programa inteiro e o
    usuario perde o trabalho da tela de conferir.
    """

    @functools.wraps(metodo)
    def envolvido(self, *args, **kwargs):
        try:
            return metodo(self, *args, **kwargs)
        except Exception:  # noqa: BLE001 - e exatamente o ponto
            registrar_erro(f"tela_conferir.{metodo.__name__}", traceback.format_exc())
            self._avisar_problema()
            return None

    return envolvido


class _LugaresDeEncaixe(QWidget):
    """Os três lugares onde as miniaturas podem ser soltas, desenhados por cima
    da tela enquanto a alça é arrastada (rodada 8: contorno azul tracejado; o
    lugar sob o mouse fica azul cheio). Não pega o mouse (os cliques vão para
    a tela de baixo)."""

    def __init__(self, tela) -> None:
        super().__init__(tela)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.retangulos: dict = {}
        self.aceso = None
        self.setVisible(False)

    def mostrar(self, retangulos: dict, aceso) -> None:
        self.retangulos = retangulos
        self.aceso = aceso
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.setVisible(True)
        self.update()

    def esconder(self) -> None:
        self.setVisible(False)

    def paintEvent(self, _evento) -> None:  # noqa: N802 - nome do Qt
        from PySide6.QtGui import QPen

        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        azul = QColor(estilo.cor("azul"))
        for lugar, ret in self.retangulos.items():
            if lugar == self.aceso:
                cheio = QColor(azul)
                cheio.setAlpha(90)
                pintor.setBrush(cheio)
            else:
                pintor.setBrush(Qt.NoBrush)
            caneta = QPen(azul, 2, Qt.DashLine)
            pintor.setPen(caneta)
            pintor.drawRoundedRect(ret.adjusted(4, 4, -4, -4), 8, 8)
        pintor.end()


# Os vãos da barra de baixo (etapa 9b-1; eram 6 e 8). Seguro mudar: aumentar
# volta a cortar a conta a 1280 com um painel aberto (prova em
# tests/test_decisoes_9b1.py).
ESPACO_DA_BARRA_DE_BAIXO = 4
RESPIRO_DA_BARRA_DE_BAIXO = 4


class _RotuloDoLivro(QLabel):
    """O "nome · N de M conferidas · K com dúvida" da barra de baixo.

    Etapa 7 da obra (lista única 1.1: "o rodapé continua '0 de 360
    conferidas'"; D-010: "contador sobe"): com a barra de baixo cheia (os
    botões do ver, etapa 6) a 1280 de largura, o rótulo era cortado pela
    direita e sobrava só "La vida ete" - o contador sumia. Agora quem encolhe
    é o NOME do livro (com reticências); a conta fica à vista. O texto
    inteiro continua no balão. Seguro mudar: o separador."""

    def __init__(self) -> None:
        super().__init__("")
        self._nome = ""
        self._conta = ""

    def definir(self, nome: str, conta: str) -> None:
        self._nome, self._conta = nome, conta
        inteiro = f"{nome} · {conta}" if nome else conta
        self.setToolTip(inteiro)
        self._encaixar()

    def texto_inteiro(self) -> str:
        return f"{self._nome} · {self._conta}" if self._nome else self._conta

    # Etapa 9b-1 (ressalva 1 da etapa 7: "o contador do rodapé ainda sai
    # cortado com um painel aberto a 1280"): quando nem a conta cabe numa
    # linha, ela vai em DUAS ("N de M conferidas" em cima, "K com dúvida"
    # embaixo), em letra um ponto menor, para caber nos 30 pontos da barra.
    # Nada sai da barra; o nome do livro (que já encolhia primeiro) fica no
    # balão, com o texto inteiro. Seguro mudar: o tamanho da letra das duas
    # linhas (LETRA_EM_DUAS_LINHAS). Arriscado: voltar a cortar a conta.
    LETRA_EM_DUAS_LINHAS = 11

    def _medida_normal(self):
        """As medidas da letra de sempre (a da folha de estilo do programa),
        mesmo com a letra menor posta (guardada antes de pôr)."""
        from PySide6.QtGui import QFont, QFontMetrics

        if not self.styleSheet():
            self._fonte_normal = QFont(self.font())
        return QFontMetrics(getattr(self, "_fonte_normal", self.font()))

    def _encaixar(self) -> None:
        medida = self._medida_normal()
        cabe = max(0, self.width() - 4)
        inteiro = self.texto_inteiro()
        if not self.isVisible() or cabe <= 0:     # sem tela ainda: não há largura para medir
            self._por(inteiro)
            return
        if medida.horizontalAdvance(inteiro) <= cabe:
            self._por(inteiro)
            return
        if self._nome:
            resto = f" · {self._conta}"
            sobra = cabe - medida.horizontalAdvance(resto)
            if sobra >= medida.horizontalAdvance("M…"):
                self._por(medida.elidedText(self._nome, Qt.ElideRight, sobra) + resto)
                return
        if medida.horizontalAdvance(self._conta) <= cabe:
            self._por(self._conta)
            return
        if not self._em_duas_linhas(cabe):
            self._por(medida.elidedText(self._conta, Qt.ElideRight, cabe))

    def _por(self, texto: str, pequena: bool = False) -> None:
        """Escreve o texto, na letra de sempre ou na menor (duas linhas)."""
        folha = f"font-size: {self.LETRA_EM_DUAS_LINHAS}px;" if pequena else ""
        if self.styleSheet() != folha:
            self.setStyleSheet(folha)
        if self.text() != texto:
            super().setText(texto)

    def em_duas_linhas(self) -> bool:
        """A conta está em duas linhas agora? (testes e prints)"""
        return "\n" in self.text()

    def _em_duas_linhas(self, cabe: int) -> bool:
        """Põe a conta em duas linhas, na letra menor, se cada linha couber
        inteira; True se pôs. Se não couber nem assim, False (quem chama
        encurta com "…", como antes)."""
        from PySide6.QtGui import QFont, QFontMetrics

        partes = self._conta.split(" · ")
        if len(partes) < 2:
            return False
        fonte = QFont(getattr(self, "_fonte_normal", self.font()))
        fonte.setPixelSize(self.LETRA_EM_DUAS_LINHAS)
        medida = QFontMetrics(fonte)
        if max(medida.horizontalAdvance(parte) for parte in partes) > cabe:
            return False
        self._por("\n".join(partes), pequena=True)
        return True

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        self._encaixar()

    def showEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().showEvent(evento)
        self._encaixar()


class TelaConferir(QWidget):
    voltar = Signal()
    processar = Signal()

    # Alguma coisa do trabalho mudou e precisa ir para o disco. Sai de UM lugar
    # so - o metodo `atualizar`, por onde toda alteracao passa - porque um sinal
    # espalhado por vinte metodos e um sinal que alguem esquece de emitir no
    # vigesimo primeiro, e o trabalho da pessoa some sem ninguem notar.
    trabalho_mudou = Signal()

    # Item 2.3: o giro pegou folhas com zonas ainda no formato antigo; a
    # janela comeca a conversao por tras se ela nao estiver andando.
    marcacoes_por_converter = Signal()

    # Etapa 2 do layout: o botao do Historico da barra de baixo foi apertado
    # (a janela marca o "Painel: Historico" do menu Ver).
    historico_pedido = Signal()

    # etapa 5 do layout: as miniaturas abriram (True) ou fecharam; a janela
    # acompanha no menu Ver > "Miniaturas"
    miniaturas_mudaram = Signal(bool)

    # Obra de 26/10/2026, etapa 3 (o Automatico; quem atende e a janela
    # principal, ui/janela_principal.py):
    #   automatico_pedido: abrir a janela grande do Automatico nesta etapa
    #       (codigo de core/automatico; "" = a primeira marcada). E o que o
    #       "mudar no Automático..." do Propriedades pede.
    #   rodar_do_aviso_pedido: o "Rodar o automático..." do aviso do livro novo
    #       (D-005, R13 804 B; D-018: abre a janela com a receita de sempre).
    #   escolhidas_para_o_automatico: a grade "Todas as páginas" devolveu as
    #       paginas escolhidas para o Automatico rodar (D-334, rodada 2: "Escolher
    #       folhas abrindo a tela de todas as páginas (marcar/desmarcar)").
    automatico_pedido = Signal(str)
    rodar_do_aviso_pedido = Signal()
    escolhidas_para_o_automatico = Signal(list)

    # Obra 26/10, etapa 6 (D-015): o jeito de mostrar mudou ("uma" ou
    # "duas"); a janela marca o "Ver lado a lado" do menu Ver
    mostrar_mudou = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.projeto: Projeto | None = None
        self.acoes: HistoricoAcoes | None = None
        self.previas: GerenciadorPrevias | None = None

        self.indice_folha = 0
        self.indice_pagina = 0

        self._abas_ativas: list[str] = []
        self._carregando = False
        # Decisao Z1 (b), 05/10/2026: "Preparando as marcações do livro…
        # 12 de 50" enquanto a janela converte as zonas do livro por tras
        # (mostrar_andamento_das_marcacoes); "" quando nao ha.
        self._andamento_das_marcacoes = ""

        # estado do medidor de ajuste
        self._valor_ao_pegar: int | None = None
        import configuracoes
        self._qualidade_da_previa = configuracoes.ler("qualidade_previa") or "rapida"
        if self._qualidade_da_previa not in QUALIDADES_DA_PREVIA:
            self._qualidade_da_previa = "rapida"
        self._dpi_normal = QUALIDADES_DA_PREVIA[self._qualidade_da_previa]
        self._dpi_atual = self._dpi_normal

        self._agendar = QTimer(self)
        self._agendar.setSingleShot(True)
        self._agendar.timeout.connect(self._redesenhar_previa)

        self._commit = QTimer(self)
        self._commit.setSingleShot(True)
        self._commit.timeout.connect(lambda: self._medidor_soltou(None))

        # Item 2.2 (G5): as setas de 0,1 grau giram a imagem na hora e gravam
        # o angulo um instante depois do ultimo clique (uma acao so do
        # desfazer para varios cliques). (indice da pagina, angulo) ainda nao
        # gravado.
        self._angulo_pendente: tuple[int, float] | None = None
        self._gravar_angulo_timer = QTimer(self)
        self._gravar_angulo_timer.setSingleShot(True)
        self._gravar_angulo_timer.setInterval(ESPERA_PARA_GRAVAR_O_ANGULO_MS)
        self._gravar_angulo_timer.timeout.connect(self._gravar_angulo_pendente)

        # Referencias diretas em Python, uma por aba. A versao anterior
        # guardava o widget dentro de setProperty() e o buscava de volta a cada
        # clique; isso devolve um ponteiro que o Python nao mantem vivo e e uma
        # fonte classica de fechamento sem aviso no PySide6.
        self.visualizadores: dict[str, Visualizador] = {}
        self.paginas_de_imagem: dict[str, QWidget] = {}
        self.linhas_de_botoes: dict[str, QWidget] = {}
        # Etapa 3 do layout: o conteudo do painel Propriedades de cada
        # ferramenta que ja mora la (Dividir, Cortar, Endireitar), pela "aba".
        self.propriedades_das_abas: dict[str, QWidget] = {}
        # O botao laranja da sugestao e um so, na faixa do conferir; este
        # dicionario (uma entrada por aba, todas para o mesmo botao) fica para
        # quem ainda o procura pela aba.
        self.botoes_de_sugestao: dict[str, QPushButton] = {}
        # o SEGUNDO botão do aviso (12/10/2026: "Deixar em branco" / "Tirar do
        # livro"; "Trazer de volta nesta página" / "está bom assim"), ao lado
        # do primeiro, em cada aba (ver _atualizar_faixa, _aplicar_sugestao)
        self.botoes_de_sugestao_2: dict[str, QPushButton] = {}
        # e o TERCEIRO (13/10/2026): o "está bom assim" dos avisos que ja tem
        # dois botoes de conserto ("Parece em branco", "Página sem conteúdo")
        self.botoes_de_sugestao_3: dict[str, QPushButton] = {}
        self.cartoes: dict[str, CartaoFiltro] = {}
        self.botoes_forca: dict[str, QPushButton] = {}
        self._cartoes_cache: dict[str, np.ndarray] = {}
        self._cartoes_cache_chave: tuple | None = None
        self._tira_assinatura: tuple | None = None

        self._montar()

    # ------------------------------------------------------------------
    # montagem
    # ------------------------------------------------------------------

    def _montar(self) -> None:
        """Etapa 2 do layout (08/10/2026): a tela de trabalho sem abas, como
        o Samuel decidiu (estilo Photoshop, 25/09; rodadas 7 a 9):

            linha dos menus  (a janela põe ali a barra de opções da
                              ferramenta e a barrinha de girar: R8 303 B)
            trilha | página                         | painel  | ícones
                   | faixa fina do conferir         | aberto  |
                   | botões dos filtros (provisório; os de Marcar
                   |   foram para o painel Propriedades na etapa 4)
                   | miniaturas + Confirmar e processar
                   | barra de baixo: página N de M, desfazer, refazer,
                   |   histórico, o livro e quantas faltam

        As abas continuam por dentro (barra_abas, escondida): cada ferramenta
        de página da trilha escolhe a "aba" dela, e tudo o que já dependia da
        aba da vez (a tira em folhas ou páginas, a prévia, os botões) segue
        igual. Assim nenhum botão sumiu: só mudaram de lugar.

        Etapa 3 do layout (12/10/2026): à direita, a coluna de ícones e o
        painel que ela abre empurrando a página (ui/widgets/paineis.py; de
        fábrica, tudo fechado). A faixa do conferir ganhou os três botões do
        desenho (a sugestão laranja, "está certo" e "próxima dúvida"), e os
        botões de Dividir, Cortar e Endireitar saíram da fila embaixo da
        página para o painel Propriedades (rodada 9, 402 C; rodada 12, 701 A:
        "Fazer logo o painel Propriedades do Cortar").
        """
        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(0)

        # O cabecalho e criado mas NAO entra na tela: ver _montar_cabecalho.
        self._cabecalho_escondido = self._montar_cabecalho()

        self.barra_abas = QTabBar()
        self.barra_abas.setExpanding(False)
        self.barra_abas.currentChanged.connect(self._trocou_de_aba)
        # Etapa 2 do layout: sem abas na tela. A barra fica por dentro, só
        # para guardar qual é a "aba" da vez (quem troca é a trilha).
        self.barra_abas.setVisible(False)

        # Girar a folha (item 2.3). Rodada 12 do layout, 703 B e D, e rodada
        # 13, 803 B: o bloco "Girar a folha", com o "aplicar em", mora no alto
        # do painel Propriedades (posto la mais abaixo, quando os paineis
        # existem), e tres botoes pequenos, que giram so esta folha, ficam por
        # cima do canto da area da pagina (_por_o_girar_no_canto). Na etapa 2
        # a barrinha ficava na ponta da linha dos menus (lugar provisorio).
        self.barra_girar = BarraGirar()
        self.barra_girar.girar_pedido.connect(self._girar_folhas)
        # As abas, que a tela nao mostra mais, continuam dentro desta caixa
        # escondida (o nome ficou de quando a linha das abas aparecia).
        self.linha_das_abas = QWidget(self)
        linha_das_abas = QHBoxLayout(self.linha_das_abas)
        linha_das_abas.setContentsMargins(0, 0, 0, 0)
        linha_das_abas.addWidget(self.barra_abas)
        self.linha_das_abas.setVisible(False)

        # A barra de opcoes: faixa fina que muda conforme a ferramenta na mao.
        # E o que deixa a tela ter nove ferramentas sem entulhar - so os
        # controles da ferramenta ativa aparecem.
        self.barra_opcoes = BarraOpcoes(self)
        self.barra_opcoes.setVisible(False)

        # 3 - a trilha, o meio (pagina, faixa, botoes, tira, barra de baixo)
        # e os paineis. O meio e o unico que cresce.
        corpo = QHBoxLayout()
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(0)

        self.trilha = TrilhaAgrupada()
        self.trilha.escolhida.connect(self._ferramenta_da_trilha)
        corpo.addWidget(self.trilha)

        # Etapa 5 do layout: os dois lugares de lado das miniaturas (rodada
        # 7, 204 A: à direita JUNTO DA PÁGINA, antes do painel e dos ícones).
        self.lugar_esquerda = QWidget()
        self.lugar_direita = QWidget()
        for lugar in (self.lugar_esquerda, self.lugar_direita):
            caixa = QVBoxLayout(lugar)
            caixa.setContentsMargins(0, 0, 0, 0)
            caixa.setSpacing(0)
            lugar.setVisible(False)
        corpo.addWidget(self.lugar_esquerda)

        centro = QVBoxLayout()
        centro.setContentsMargins(0, 0, 0, 0)
        centro.setSpacing(0)

        self.area_imagem = QStackedWidget()
        self.area_imagem.setObjectName("areaDaPagina")
        self.area_imagem.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Minimo pequeno para que a soma de todas as linhas caiba na janela
        # minima de 1000x680. Abaixo disso o Qt sobreporia as faixas.
        self.area_imagem.setMinimumHeight(112)
        # Obra 26/10/2026, etapa 6: o lugar da pagina mostra a ferramenta da
        # vez (uma pagina, como sempre), o "Duas lado a lado" (D-015, D-006:
        # os pares rolando, as paginas como vao sair) ou o "antes / depois"
        # (o desenho decidido da barra de baixo, rodada 13). Quem escolhe e a
        # barra de baixo (e o menu Ver): _acertar_a_vista_da_pagina.
        self.vista_da_pagina = QStackedWidget()
        self.vista_da_pagina.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vista_da_pagina.addWidget(self.area_imagem)
        self.lado_a_lado = PaginasLadoALado()
        self.lado_a_lado.definir_fonte(self._previa_do_lado_a_lado)
        self.lado_a_lado.pagina_da_vez_mudou.connect(self._pagina_do_lado_a_lado)
        self.vista_da_pagina.addWidget(self.lado_a_lado)
        from ui.widgets.filtros_tela_cheia import VistaAntesDepois
        self.vista_antes_depois = VistaAntesDepois()
        # o minimo e o da area da pagina (112, para a janela minima caber)
        self.vista_antes_depois.setMinimumSize(QSize(0, 0))
        self.lado_a_lado.setMinimumSize(QSize(0, 0))
        self.vista_da_pagina.addWidget(self.vista_antes_depois)
        self.mostrar = UMA            # "Uma página" de fabrica (D-007)
        self.comparando = False       # "antes / depois" desligado de fabrica
        self._roda_acumulada = 0      # a roda do mouse que ainda nao virou pagina
        self._tamanhos_das_folhas: tuple[str, list] = ("", [])
        centro.addWidget(self.vista_da_pagina, 1)
        # os botoes de girar do canto: filhos da area da pagina, por cima dela
        self.girar_do_canto = GirarDoCanto(self.area_imagem)
        self.girar_do_canto.girar_pedido.connect(
            lambda giro: self._girar_folhas(giro, so_esta=True))
        self.girar_do_canto.setVisible(False)
        self.area_imagem.installEventFilter(self)
        self.area_imagem.currentChanged.connect(lambda _i: self._por_o_girar_no_canto())

        # Etapa 3 do layout: a coluna de icones na borda direita e o painel
        # que ela abre ao lado da pagina (de fabrica, tudo fechado). Os
        # paineis recebem o que eram linhas de botoes atravessando a tela.
        self.paineis = ColunaDePaineis()
        # o bloco "Girar a folha" no alto do Propriedades, em todas as
        # ferramentas, e embaixo dele os dois botões de "Esta página" (etapa 2
        # da obra, _montar_os_botoes_da_pagina)
        alto = NaoEspreme()          # sem fundo proprio: o do painel aparece
        coluna_do_alto = QVBoxLayout(alto)
        coluna_do_alto.setContentsMargins(0, 0, 0, 0)
        coluna_do_alto.setSpacing(7)
        coluna_do_alto.addWidget(self.barra_girar)
        coluna_do_alto.addWidget(risco_do_painel())
        coluna_do_alto.addWidget(self._montar_os_botoes_da_pagina())
        self.paineis.propriedades.por_no_alto(alto)

        self._ligar_paineis()

        # 4 - a faixa fina do conferir, colada embaixo da pagina (decidido em
        # 05/10: "faixa fina embaixo da página"), com os tres botoes do
        # desenho dentro dela (opcao 1 do Conferir, aprovada na rodada 2): a
        # sugestao laranja do aviso (so quando o aviso tem uma), "está certo"
        # e "próxima dúvida". Antes cada ferramenta tinha o seu "está certo" e
        # a sua sugestao na fila de botoes embaixo; agora e um lugar so, igual
        # em todas. Seguro mudar: os textos. Arriscado: tirar um dos tres.
        self.faixa = QFrame()
        self.faixa.setObjectName("faixaInfo")
        self.faixa.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        faixa_camadas = QHBoxLayout(self.faixa)
        faixa_camadas.setContentsMargins(14, 5, 10, 5)
        faixa_camadas.setSpacing(8)
        self.texto_faixa = QLabel("")
        self.texto_faixa.setWordWrap(True)
        faixa_camadas.addWidget(self.texto_faixa, 1)
        self.botao_sugestao = QPushButton("")
        self.botao_sugestao.setObjectName("sugestao")
        self.botao_sugestao.setToolTip("Faz o que o aviso sugere, nesta página.")
        _ligar(self.botao_sugestao, self._aplicar_sugestao)
        # O segundo e o terceiro botão do aviso (Para revisar, 12 e 13/10/2026:
        # "Deixar em branco" / "Tirar do livro" / "está bom assim", "Trazer de
        # volta nesta página" / "está bom assim"), ao lado do primeiro, na
        # mesma faixa (junção com o layout de 14/10: os botões do aviso moram
        # aqui, iguais em todas as ferramentas). Escondidos quando o aviso não
        # os tem. Seguro mudar: a ordem entre os três. Arriscado: tirá-los da
        # faixa (_mostrar_sugestao os acha por botoes_de_sugestao_2 e _3).
        self.botao_sugestao_2 = QPushButton("")
        self.botao_sugestao_2.setObjectName("sugestao")
        _ligar(self.botao_sugestao_2, functools.partial(self._aplicar_sugestao, 1))
        self.botao_sugestao_3 = QPushButton("")
        self.botao_sugestao_3.setObjectName("sugestao")
        _ligar(self.botao_sugestao_3, functools.partial(self._aplicar_sugestao, 2))
        self.botao_esta_certo = QPushButton("está certo")
        self.botao_esta_certo.setObjectName("acaoPrimaria")
        self.botao_esta_certo.setToolTip(
            "Marca como conferida (a barra de espaço marca e já vai para a próxima).")
        # etapa 7 da obra (lista única 1.1, D-010): conferida, tique, contador
        # e a próxima dúvida (esta_certo); antes só gravava, e nada mudava
        _ligar(self.botao_esta_certo, self.esta_certo)
        self.botao_proxima_duvida = QPushButton("próxima dúvida")
        self.botao_proxima_duvida.setToolTip("Vai para a próxima com dúvida (tecla Tab).")
        _ligar(self.botao_proxima_duvida, self._ir_para_proximo_alerta)
        for botao in (self.botao_sugestao, self.botao_sugestao_2, self.botao_sugestao_3,
                      self.botao_esta_certo, self.botao_proxima_duvida):
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)        # o teclado continua da página
            faixa_camadas.addWidget(botao)
        for botao in (self.botao_sugestao, self.botao_sugestao_2, self.botao_sugestao_3):
            botao.setVisible(False)
        centro.addWidget(self._montar_aviso_do_livro_novo())
        centro.addWidget(self.faixa)

        # A fila de botoes de cada aba. O QStackedWidget reserva, por padrao, a
        # altura da MAIOR pagina dele - entao a aba de Marcar, que agora tem uma
        # linha so, ficava com o buraco da aba de Filtro embaixo. Eram uns
        # 150 px de vazio no meio da tela, tirados justamente da pagina.
        #
        # A conta e feita a mao em _encolher_a_barra_de_botoes: as paginas que
        # nao estao na frente passam a ser ignoradas no calculo, e a pilha
        # ganha a altura da atual. A troca de aba reavalia.
        # Etapa 2 do layout: PROVISORIO ate a etapa 4, quando estes botoes
        # vao para o painel Propriedades (R9 402 C: muda conforme a ferramenta).
        # Etapa 3: os de Dividir, Cortar e Endireitar ja foram (a pagina
        # deles nesta pilha e vazia, com altura zero); ficam aqui os de
        # Marcar e os dos quatro filtros.
        self.barra_botoes = QStackedWidget()                 # 5
        self.barra_botoes.setObjectName("barraDeBotoes")
        # largura "ignorada": com um painel aberto a fila tem menos lugar, e
        # nunca pode empurrar a janela para mais largo que a tela
        self.barra_botoes.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)
        self.caixa_dos_botoes = QVBoxLayout()
        self.caixa_dos_botoes.setContentsMargins(*MARGENS_DA_FILA_DE_BOTOES)
        self.caixa_dos_botoes.addWidget(self.barra_botoes)
        centro.addLayout(self.caixa_dos_botoes)

        # A tira e o botao de processar dividem UMA faixa, como no desenho: a
        # tira a esquerda, "Confirmar e processar" no canto direito. Eram duas
        # faixas empilhadas, e a de baixo custava uns 70 px so para segurar um
        # botao.
        # Etapa 5 do layout (rodadas 7, 8 e 13): as miniaturas com o
        # cabeçalho "PÁGINAS" (seta, três pontinhos, alça, "ver todas"),
        # embaixo, à esquerda ou à direita da página. Embaixo e abertas, o
        # "Confirmar e processar" fica ao lado delas (704 A); fechadas ou de
        # lado, ele desce para a barra de baixo (801 A).
        self.miniaturas = PainelDeMiniaturas()               # 6
        self.tira = self.miniaturas.tira
        self.tira.selecionada.connect(self._escolher_da_tira)
        self.tira.ampliar_pedido.connect(self._ampliar_miniatura)
        self.miniaturas.lugar_pedido.connect(self._por_as_miniaturas)
        self.miniaturas.aberta_mudou.connect(lambda _a: self._por_as_miniaturas(self.miniaturas.lugar))
        self.miniaturas.ver_todas.connect(self.abrir_todas_as_paginas)
        self.miniaturas.alca.arrastando.connect(self._arrastando_as_miniaturas)
        self.miniaturas.alca.soltou.connect(self._soltou_as_miniaturas)

        self.lugar_embaixo = QFrame()
        self.lugar_embaixo.setObjectName("lugarDasMiniaturas")
        # o mesmo fundo do cabeçalho "PÁGINAS", até o canto do "Confirmar e processar"
        estilo.estilizar(self.lugar_embaixo, lambda: (
            f"QFrame#lugarDasMiniaturas {{ background: {estilo.cor('bar')}; "
            f"border-top: 1px solid {estilo.cor('linha')}; }}"))
        self.faixa_da_tira = QHBoxLayout(self.lugar_embaixo)
        self.faixa_da_tira.setContentsMargins(0, 0, 10, 0)
        self.faixa_da_tira.setSpacing(10)
        self._montar_rodape()
        self.caixa_do_processar = QVBoxLayout()
        self.caixa_do_processar.setContentsMargins(0, 26, 0, 6)
        self.faixa_da_tira.addLayout(self.caixa_do_processar)
        centro.addWidget(self.lugar_embaixo)

        # 7 - a barra de baixo (etapa 2 do layout, R9 405 C: desfazer e refazer
        # sempre a mao, mais o painel Historico).
        centro.addWidget(self._montar_barra_de_baixo())

        corpo.addLayout(centro, 1)
        corpo.addWidget(self.lugar_direita)
        corpo.addWidget(self.paineis)
        # Etapa 5 do layout: a tela de trabalho e "Todas as páginas" (808 A)
        # dividem o lugar; a barra de menus fica.
        self.trabalho = QWidget()
        self.trabalho.setLayout(corpo)
        self.todas = TodasAsPaginas(com_escolha=True)
        self.todas.ir_para.connect(self._voltar_das_todas)
        self.todas.voltar.connect(lambda: self._voltar_das_todas(None))
        # D-334 (etapa 3 da obra): as acoes nas paginas escolhidas e o
        # "escolher páginas..." do Automatico
        self.todas.acao_nas_escolhidas.connect(self._acao_nas_escolhidas)
        self.todas.escolha_pronta.connect(self._escolha_pronta)
        self.pilha_da_tela = QStackedWidget()
        self.pilha_da_tela.addWidget(self.trabalho)
        self.pilha_da_tela.addWidget(self.todas)
        camadas.addWidget(self.pilha_da_tela, 1)
        # os lugares de encaixe que aparecem ao arrastar as miniaturas
        self.lugares_de_encaixe = _LugaresDeEncaixe(self)
        # as miniaturas voltam como a pessoa deixou no último livro (Samuel,
        # 21/10/2026: "Sim, lembrar para todos os livros"); de fábrica, embaixo,
        # abertas, uma a uma
        guardadas = miniaturas_guardadas()
        self.miniaturas.definir_aberta(guardadas["aberta"])
        self.miniaturas.definir_em_pares(guardadas["em_pares"])
        self._por_as_miniaturas(guardadas["lugar"])
        self.miniaturas.em_pares_mudou.connect(lambda _p: self._guardar_as_miniaturas())
        # a barra de opções e o editor de marcar: ligados uma vez só (etapa 2
        # da obra; antes era a cada livro, ver _ligar_ferramentas)
        self._ligar_ferramentas()

    def _montar_barra_de_baixo(self) -> QWidget:
        """A barra fina de baixo, como no prototipo das rodadas 9 a 11:
        "< pagina N de M >", desfazer, refazer e o Historico, o nome do livro
        e quantas foram conferidas e quantas tem duvida. As setas "<" e ">"
        que ficavam dos lados da pagina moraram aqui (as dos lados ficam
        escondidas: a roda do mouse e as setas do teclado continuam)."""
        barra = QFrame()
        barra.setObjectName("barraDeBaixo")
        barra.setFixedHeight(30)
        linha = QHBoxLayout(barra)
        linha.setContentsMargins(10, 0, 10, 0)
        # etapa 9b-1 (ressalva 1 da etapa 7, o contador cortado a 1280 com um
        # painel aberto): os vãos da barra ficaram menores (6 -> 4 entre as
        # peças, 8 -> 4 nos respiros) para sobrar lugar à conta; nada saiu
        linha.setSpacing(ESPACO_DA_BARRA_DE_BAIXO)

        def botao_pequeno(texto: str, dica: str, acao) -> QPushButton:
            botao = QPushButton(texto)
            botao.setObjectName("botaoDaBarraDeBaixo")
            botao.setToolTip(dica)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)
            _ligar(botao, acao)
            linha.addWidget(botao)
            return botao

        self.botao_anterior = botao_pequeno("‹", "página anterior (seta para a esquerda)",
                                            lambda: self._navegar(-1))
        self.rotulo_da_pagina = QLabel("")
        self.rotulo_da_pagina.setObjectName("rotuloDaBarraDeBaixo")
        linha.addWidget(self.rotulo_da_pagina)
        self.botao_proxima = botao_pequeno("›", "próxima página (seta para a direita)",
                                           lambda: self._navegar(1))
        # Item 2.12 (resposta P6 do Samuel, 23/10/2026): o sinal discreto
        # enquanto o desentortar desta pagina e medido por tras (3 a 8 s). A
        # pagina na tela fica sem desentortar ate a medida chegar. So aparece
        # em pagina com o desentortar ligado. Seguro mudar: os textos
        # (SINAL_DESENTORTANDO e a dica).
        self.sinal_desentortando = QLabel(self.SINAL_DESENTORTANDO)
        self.sinal_desentortando.setObjectName("rotuloDaBarraDeBaixo")
        self.sinal_desentortando.setToolTip(
            "A página na tela ainda está sem desentortar. Em alguns segundos ela "
            "aparece desentortada, igual vai sair no PDF.")
        self.sinal_desentortando.setVisible(False)
        linha.addSpacing(RESPIRO_DA_BARRA_DE_BAIXO)
        linha.addWidget(self.sinal_desentortando)
        linha.addSpacing(RESPIRO_DA_BARRA_DE_BAIXO)
        self.botao_desfazer_embaixo = botao_pequeno(
            "", "Desfazer (Ctrl+Z)", self.desfazer)
        self.botao_desfazer_embaixo.setIcon(_icone_da_barra("desfazer"))
        self.botao_refazer_embaixo = botao_pequeno(
            "", "Refazer (Ctrl+Shift+Z)", self.refazer)
        self.botao_refazer_embaixo.setIcon(_icone_da_barra("refazer"))
        self.botao_historico_embaixo = botao_pequeno(
            "", "Abrir ou fechar o painel Histórico (a lista do que foi feito)",
            self._mostrar_o_historico)
        self.botao_historico_embaixo.setIcon(_icone_da_barra("historico"))
        linha.addSpacing(RESPIRO_DA_BARRA_DE_BAIXO)
        self.rotulo_do_livro = _RotuloDoLivro()
        self.rotulo_do_livro.setObjectName("rotuloDaBarraDeBaixo")
        # cede lugar (etapa 3): com um painel aberto numa janela estreita, o
        # nome comprido do livro e cortado em vez de empurrar a coluna de
        # icones para fora da janela (o nome inteiro fica no balao)
        self.rotulo_do_livro.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        linha.addWidget(self.rotulo_do_livro, 1)
        self._montar_o_ver_da_barra_de_baixo(linha)
        # rodada 13, 801 A: o "Confirmar e processar" pequeno, no canto direito,
        # com as miniaturas fechadas ou de lado (_por_as_miniaturas)
        self.caixa_do_processar_na_barra = QHBoxLayout()
        self.caixa_do_processar_na_barra.setContentsMargins(0, 0, 0, 0)
        linha.addLayout(self.caixa_do_processar_na_barra)
        # os icones desenhados a mao acompanham a troca de tema
        estilo.estilizar(barra, self._icones_da_barra_de_baixo)
        return barra

    # Obra 26/10, etapa 6: os botoes do "ver" na barra de baixo, (jeito,
    # texto, balao). Os nomes "Uma página" e "Duas lado a lado" sao os do
    # livro aberto aprovado (D-015, lyupdf "Aprovado"); os baloes tambem.
    JEITOS_DE_MOSTRAR = (
        (UMA, "Uma página", "Uma página de cada vez"),
        (DUAS, "Duas lado a lado",
         "As páginas em pares, como no livro aberto (a 1 sozinha, à direita)"),
    )

    def _montar_o_ver_da_barra_de_baixo(self, linha: QHBoxLayout) -> None:
        """Obra 26/10, etapa 6. Na barra de baixo, à direita (antes do
        "Confirmar e processar" quando ele desce para ela):

          "Uma página" / "Duas lado a lado"  (D-015: como na barra de baixo
              do livro aberto aprovado; D-006: o lado a lado e opcao, nao
              padrao; D-007: de fabrica, uma pagina por vez)
          "antes / depois", "–  N%  +", "ajustar à tela"  (o desenho decidido
              da barra de baixo, rodada 13: `21-rodada13-base.html`)

        O "antes / depois" mostra a pagina da vez com o Original a esquerda
        da linha e como vai sair a direita (o mesmo "Comparar com o Original"
        da tela cheia dos filtros, R11 601 A, com a linha que se arrasta). O
        zoom e o mesmo do menu Ver (Aproximar, Afastar, Ajustar à tela), e o
        numero e o que a pagina da vez tem (100% = a pagina inteira cabendo,
        como o "Zoom: N%" que a ferramenta de marcar ja mostrava).
        Seguro mudar: textos e baloes. Arriscado: ligar o zoom ao lado a lado
        (ele nao tem zoom: as paginas cabem na tela)."""
        from PySide6.QtWidgets import QButtonGroup

        def botao(texto: str, dica: str, acao, marcavel: bool = False,
                  objeto: str = "jeitoDaBarraDeBaixo") -> QPushButton:
            b = QPushButton(texto)
            b.setObjectName(objeto)      # ui/estilo.py: o tamanho e o aceso
            b.setToolTip(dica)
            b.setCursor(Qt.PointingHandCursor)
            b.setFocusPolicy(Qt.NoFocus)
            b.setCheckable(marcavel)
            _ligar(b, acao)
            linha.addWidget(b)
            return b

        self.botoes_mostrar: dict[str, QPushButton] = {}
        self._grupo_mostrar = QButtonGroup(self)
        self._grupo_mostrar.setExclusive(True)
        for jeito, texto, dica in self.JEITOS_DE_MOSTRAR:
            b = botao(texto, dica, functools.partial(self.definir_mostrar, jeito), marcavel=True)
            self._grupo_mostrar.addButton(b)
            self.botoes_mostrar[jeito] = b
        self.botoes_mostrar[UMA].setChecked(True)
        linha.addSpacing(RESPIRO_DA_BARRA_DE_BAIXO)
        self.botao_antes_depois = botao(
            "antes / depois",
            "Mostra a página da vez com o Original à esquerda e como vai sair à direita. "
            "Arraste a linha do meio para comparar.", self._alternar_antes_depois, marcavel=True)
        linha.addSpacing(RESPIRO_DA_BARRA_DE_BAIXO)
        self.botao_menos_zoom = botao("–", "Afastar (Ctrl+-)",
                                      lambda: self.mudar_o_zoom(1 / self.PASSO_DO_ZOOM),
                                      objeto="botaoDaBarraDeBaixo")
        self.rotulo_do_zoom = QLabel("100%")
        self.rotulo_do_zoom.setObjectName("rotuloDaBarraDeBaixo")
        self.rotulo_do_zoom.setAlignment(Qt.AlignCenter)
        self.rotulo_do_zoom.setMinimumWidth(40)
        linha.addWidget(self.rotulo_do_zoom)
        self.botao_mais_zoom = botao("+", "Aproximar (Ctrl++)",
                                     lambda: self.mudar_o_zoom(self.PASSO_DO_ZOOM),
                                     objeto="botaoDaBarraDeBaixo")
        self.botao_ajustar_a_tela = botao("ajustar à tela", "A página inteira cabe na tela (Ctrl+0)",
                                          lambda: self.mudar_o_zoom(None))

    def _icones_das_setas_do_angulo(self) -> str:
        """(Re)desenha as setinhas dos botoes de 0,1 grau da ferramenta
        Endireitar na cor do tema da vez. Devolve a folha (vazia) para
        estilo.estilizar, que chama isto de novo a cada troca de tema."""
        from ui.widgets.barra_girar import icone_de_giro

        self.botao_angulo_anti_horario.setIcon(icone_de_giro(girar.GIRO_ESQUERDA))
        self.botao_angulo_horario.setIcon(icone_de_giro(girar.GIRO_DIREITA))
        return ""

    def _icones_da_barra_de_baixo(self) -> str:
        """(Re)desenha os icones da barra de baixo na cor do tema da vez; a
        folha dela mora em ui/estilo.py (QFrame#barraDeBaixo)."""
        self.botao_desfazer_embaixo.setIcon(_icone_da_barra("desfazer"))
        self.botao_refazer_embaixo.setIcon(_icone_da_barra("refazer"))
        self.botao_historico_embaixo.setIcon(_icone_da_barra("historico"))
        # os dois botoes do painel Historico levam os mesmos desenhos
        self.paineis.historico.definir_icones(
            _icone_da_barra("desfazer"), _icone_da_barra("refazer"))
        return ""

    def _mostrar_o_historico(self) -> None:
        """Botao do Historico na barra de baixo: abre o painel Historico, ou
        fecha se ja era ele o aberto (o mesmo que o icone do relogio na
        coluna da direita; rodada 9, 405 C: os botoes sempre a mao e a lista
        no painel)."""
        self.paineis.alternar(PAINEL_HISTORICO)
        self.historico_pedido.emit()

    # O sinal da barra de baixo enquanto o desentortar e medido (item 2.12,
    # resposta P6). Portugues simples, sem jargao (quem le e o Kaique).
    SINAL_DESENTORTANDO = "Desentortando esta página, um momento..."

    def _acertar_o_desentortar(self) -> None:
        """Item 2.12 (resposta P6 do Samuel, 23/10/2026, opcao (b)): se a
        pagina da vez tem o desentortar ligado e a medida dele (na resolucao
        do livro) ainda nao existe, pede a medida por tras e mostra o sinal
        discreto; senao, esconde o sinal. Barato (sem desenho). A medida
        pronta chega por _desentortar_medido."""
        if not hasattr(self, "sinal_desentortando"):
            return
        pendente = False
        if (self.previas is not None and self.projeto is not None
                and not self.trabalha_com_folhas
                and 0 <= self.indice_pagina < len(self.projeto.paginas)):
            # na qualidade "Alta" (a resolucao do livro) a propria previa mede;
            # pedir por tras tambem seria medir duas vezes ao mesmo tempo
            if self._dpi_atual >= self.projeto.qualidade_dpi:
                pendente = self.previas.desentortar_pendente(self.indice_pagina)
            else:
                pendente = self.previas.pedir_desentortar(self.indice_pagina)
        self.sinal_desentortando.setVisible(pendente)

    def _desentortar_medido(self, indice: int) -> None:
        """A medida do desentortar de uma pagina chegou (tarefa por tras). Se
        e a pagina da vez, desenha de novo (a chave da previa e dos cartoes ja
        mudou sozinha: ui/tarefas.GerenciadorPrevias.chave) e acerta a faixa,
        a tira e os paineis (os avisos da protecao podem ter entrado)."""
        if not self._pronta() or self.projeto is None:
            return
        if indice == self.indice_pagina and not self.trabalha_com_folhas:
            self._atualizar_previa()
            self._alertas_da_previa()
        else:
            self._acertar_o_desentortar()

    def _atualizar_barra_de_baixo(self) -> None:
        """Pagina (ou folha, no Dividir), desfazer/refazer acesos so quando ha
        o que fazer, e o andamento do livro."""
        if self.projeto is None or not hasattr(self, "rotulo_da_pagina"):
            return
        if self.trabalha_com_folhas:
            texto = f"folha {self.indice_folha + 1} de {len(self.projeto.folhas)}"
        else:
            texto = f"página {self.indice_pagina + 1} de {len(self.projeto.paginas)}"
        self.rotulo_da_pagina.setText(texto)
        total = self._total()
        self.botao_anterior.setEnabled(self.indice_atual > 0)
        self.botao_proxima.setEnabled(self.indice_atual < total - 1)
        feitas = bool(self.acoes and self.acoes.feitas)
        desfeitas = bool(self.acoes and self.acoes.desfeitas)
        self.botao_desfazer_embaixo.setEnabled(feitas)
        self.botao_refazer_embaixo.setEnabled(desfeitas)
        if feitas:
            self.botao_desfazer_embaixo.setToolTip(
                f"Desfazer: {self.acoes.feitas[-1].descricao} (Ctrl+Z)")
        # etapa 7 da obra (lista única 1.1 e 5.4): no Dividir se confere a
        # FOLHA, e o contador conta folhas (antes contava páginas, e o "está
        # certo" do Dividir não mexia nele: "0 de 360 conferidas"); nas outras
        # ferramentas, páginas. As dúvidas: o número de todo lugar (5.5).
        itens = self.projeto.folhas if self.trabalha_com_folhas else self.projeto.paginas
        conferidas = sum(1 for item in itens if item.revisada)
        duvidas = avisos_do_livro.quantas_com_duvida(self.projeto)
        nome = Path(self.projeto.caminho_entrada).stem if self.projeto.caminho_entrada else ""
        # o nome encolhe primeiro, a conta fica à vista (_RotuloDoLivro); o
        # texto inteiro fica no balão
        self.rotulo_do_livro.definir(
            nome, f"{conferidas} de {len(itens)} conferidas · {duvidas} com dúvida")

    def _ligar_paineis(self) -> None:
        """Cada painel manda no mesmo lugar em que o botao antigo mandava.

        Etapa 3 do layout: o Historico ganhou os botoes de desfazer e refazer
        (os mesmos da barra de baixo), e o Automatico leva a tela "O que
        fazer" pelo mesmo caminho do menu Arquivo > "Voltar para as opções"
        (o sinal `voltar`), que grava o trabalho antes de sair."""
        painel = self.paineis
        # etapa 7 da obra: o clique no cartão deixa o aviso à vista (sai do
        # Dividir quando o aviso é da página; sessão 0, 0-8)
        painel.para_revisar.ir_para.connect(self._ir_do_para_revisar)
        # os botões do aviso no cartão da página da vez (lista única 1.8)
        painel.para_revisar.botao_do_aviso.connect(self._aplicar_sugestao)
        # "ver as N em tela cheia" (D-259)
        painel.para_revisar.ver_em_tela_cheia.connect(self.abrir_so_as_que_precisam)
        # "está bom" de uma vez e o seletor grande (12/10/2026)
        painel.para_revisar.aceitar_motivo.connect(self._aceitar_o_motivo_em_todas)
        painel.para_revisar.aceitar_tudo.connect(self._aceitar_tudo)
        painel.para_revisar.abrir_lista.connect(self._abrir_a_lista_dos_avisos)
        painel.marcar_como.escolheu.connect(self._escolher_tipo_de_marcacao)
        # (pelo _ao_editor: o editor nasce a cada livro; antes de o primeiro
        # livro abrir ele nem existe)
        painel.marcar_como.cor_escolhida.connect(              # item 2.18
            lambda cor: self._ao_editor("definir_cor_de_pintar", cor))
        painel.marcar_como.escurecer_escolhido.connect(        # item 2.18, A ou B
            lambda escura: self._ao_editor("definir_tinta_escurecida", escura))
        painel.marcar_como.papel_escolhido.connect(            # item 2.18, o papel
            lambda da_pagina: self._ao_editor("definir_papel_da_pagina", da_pagina))
        painel.filtro_da_pagina.filtro_do_pedaco.connect(
            self._escolher_filtro_da_regiao)
        # etapa 4 do layout: a fila de filtros do painel escolhe o filtro da
        # pagina (o mesmo caminho dos cartoes grandes e das teclas 1 a 4)
        painel.filtro_da_pagina.filtro_escolhido.connect(self._escolher_filtro)
        painel.filtro_da_pagina.tela_cheia_pedida.connect(self.abrir_filtros_em_tela_cheia)
        painel.abriu.connect(self._painel_abriu)
        painel.historico.voltar_para.connect(self._voltar_no_historico)
        painel.historico.desfazer_pedido.connect(self.desfazer)
        painel.historico.refazer_pedido.connect(self.refazer)
        # etapa 3 da obra: o painel Automatico de verdade. "abrir em janela
        # grande"/"ajustar" viram o pedido da janela grande; o resto (rodar,
        # desligar, escolher paginas, receita) a janela principal liga direto
        # nos sinais do painel (ui/janela_principal._ligar_o_automatico).
        painel.automatico.janela_pedida.connect(self.automatico_pedido.emit)

    def _painel_abriu(self, chave: str) -> None:
        """Abriu o painel Filtro: as páginas pequenas da fila (as amostras
        dos outros filtros) são pedidas agora, e daqui em diante a cada troca
        de página, só enquanto ele estiver aberto (_filtro_aberto). Com ele
        fechado nada é calculado a mais."""
        if chave == PAINEL_FILTRO and self._pronta() and self.previas is not None:
            self._atualizar_previa()

    def _filtro_aberto(self) -> bool:
        """O painel "Filtro da página" está aberto?"""
        return self.paineis.aberto == PAINEL_FILTRO

    def _cartoes_a_vista(self) -> bool:
        """As amostras dos filtros estão sendo mostradas (a tela provisória
        dos quatro filtros, ou a fila do painel Filtro)?"""
        return self.aba_atual == ABA_FILTRO or self._filtro_aberto()

    def _voltar_no_historico(self, posicao: int) -> None:
        """Volta o trabalho ate a acao clicada no painel Historico."""
        if self.acoes is None or self.projeto is None:
            return
        # pendencia da D2: nao muda o preparo de pagina com zonas antigas
        feitas = self.acoes.feitas
        if posicao < len(feitas):
            if self._acoes_esperam_pelas_marcacoes(feitas[posicao:], para_tras=True):
                return
        elif self._acoes_esperam_pelas_marcacoes(
                list(reversed(self.acoes.desfeitas))[:posicao - len(feitas)], para_tras=False):
            return
        self.acoes.voltar_para(self.projeto, posicao)
        if self.previas is not None:
            self.previas.invalidar()
        self.atualizar()

    def _ao_editor(self, metodo: str, *argumentos) -> None:
        """Chama `metodo` no editor de marcar do livro aberto, se houver um.
        O editor nasce de novo a cada livro (_montar_aba_marcar); quem liga
        uma vez só (a barra de opções, os painéis) passa por aqui, e assim
        nunca fala com o editor de um livro anterior, já destruído."""
        editor = getattr(self, "editor_selecao", None)
        if editor is not None:
            getattr(editor, metodo)(*argumentos)

    def _mudar_no_editor(self, campo: str, valor) -> None:
        """Muda um ajuste do editor de marcar do livro aberto (tolerância,
        espessura), se houver um."""
        editor = getattr(self, "editor_selecao", None)
        if editor is not None:
            setattr(editor, campo, valor)

    def _ligar_ferramentas(self) -> None:
        """A trilha manda na barra de opcoes e no editor, nesta ordem.

        Um lugar so decide qual ferramenta esta na mao. Antes havia uma fila de
        botoes que sabia disso e o editor que sabia de novo, e os dois saiam do
        ar quando alguem esquecia de avisar o outro.

        Etapa 2 da obra (26/10/2026): ligado UMA vez, no _montar. Antes era a
        cada livro aberto com a ferramenta de marcar, e cada livro somava mais
        uma ligacao da barra (as antigas apontavam para o editor do livro
        anterior, ja destruido). Agora a barra fala com o editor da vez por
        _ao_editor. Arriscado: voltar a ligar aqui direto no editor.
        """
        # Etapa 2 do layout: a trilha agrupada avisa a tela
        # (_ferramenta_da_trilha), e a tela avisa a barra e o editor.
        opcoes = self.barra_opcoes
        opcoes.operacao_mudou.connect(lambda operacao: self._ao_editor("definir_operacao", operacao))
        opcoes.tolerancia_mudou.connect(
            lambda valor: self._mudar_no_editor("tolerancia", int(valor)))
        opcoes.espessura_mudou.connect(
            lambda valor: self._mudar_no_editor("espessura", float(valor)))
        opcoes.zoom_mudou.connect(lambda zoom: self._ao_editor("definir_zoom", zoom))
        opcoes.ajustar_pedido.connect(lambda: self._ao_editor("ajustar_a_tela"))

        self.trilha.definir_ferramenta(FERRAMENTA_RETANGULO)
        self.barra_opcoes.definir_ferramenta(FERRAMENTA_RETANGULO)

    def escolher_ferramenta(self, ferramenta: str) -> None:
        """Ponto unico de troca - usado tambem pelos atalhos de letra.

        Etapa 2 do layout (sem abas): as ferramentas de marcar so trabalham
        na pagina de marcar, entao escolher uma delas (na trilha ou pela
        letra) leva a tela para la, como no Photoshop.

        As ferramentas de pagina (Dividir, Cortar, Endireitar, Os quatro
        filtros) nao sao do editor de marcar: vao pelo mesmo caminho do clique
        na trilha, que escolhe a "aba" delas. Sem isto, a trilha acendia a
        ferramenta e a tela continuava na de marcar (achado em 09/10/2026)."""
        if ferramenta in ABA_DA_FERRAMENTA:
            self._ferramenta_da_trilha(ferramenta)
            return
        self.trilha.definir_ferramenta(ferramenta)
        self.barra_opcoes.definir_ferramenta(ferramenta)
        self._ao_editor("definir_ferramenta", ferramenta)
        if ABA_MARCAR in self._abas_ativas and self.aba_atual != ABA_MARCAR:
            self.barra_abas.setCurrentIndex(self._abas_ativas.index(ABA_MARCAR))
        self._acertar_as_propriedades()     # o painel Propriedades segue a ferramenta

    def _ferramenta_da_trilha(self, ferramenta: str) -> None:
        """Clique na trilha (ou no menu Ferramentas). As de pagina (Dividir,
        Cortar, Endireitar) escolhem a "aba" delas; as de marcar e de navegar
        vao para a pagina de marcar. ("Os quatro filtros" saiu da trilha na
        etapa 2 da obra, R9 403 B; a "aba" dela continua por dentro, para os
        cartoes do painel Filtro.)"""
        aba = ABA_DA_FERRAMENTA.get(ferramenta)
        if aba is not None:
            if aba in self._abas_ativas:
                self.barra_abas.setCurrentIndex(self._abas_ativas.index(aba))
                # Rodada 13 do layout, 802 A ("Abre sozinho"): ao ESCOLHER
                # Dividir, Cortar ou Endireitar, o painel Propriedades abre,
                # porque e nele que estao os botoes delas. So ao escolher: se
                # a pessoa fechar o painel, ele fica fechado ate ela escolher
                # outra dessas tres. Abrir um livro nao abre painel nenhum
                # (rodada 7, 203 D: de fabrica, tudo fechado).
                if aba in self.propriedades_das_abas:
                    self.paineis.abrir(PAINEL_PROPRIEDADES)
            return
        if hasattr(self, "editor_selecao") and ABA_MARCAR in self._abas_ativas:
            self.escolher_ferramenta(ferramenta)

    def _acertar_a_trilha(self) -> None:
        """A trilha mostra TODAS as ferramentas e marca a da vez.

        Até a etapa 2 da obra (26/10/2026) ela mostrava só as do livro (as
        das caixinhas marcadas na tela "O que fazer"); com nenhuma marcada,
        só "Os quatro filtros". D-001: todas, sempre."""
        self.trilha.definir_disponiveis(None)
        aba = self.aba_atual
        if aba == ABA_MARCAR and hasattr(self, "editor_selecao"):
            ferramenta = self.barra_opcoes.ferramenta
        else:
            ferramenta = FERRAMENTA_DA_ABA.get(aba)
        self.trilha.definir_ferramenta(ferramenta)
        # a barra de opcoes, na linha dos menus, diz a ferramenta de pagina
        # (so o nome: rodada 12, 702 C; a frase do que fazer fica no balao da
        # ferramenta, na trilha)
        if aba != ABA_MARCAR and ferramenta in FERRAMENTAS_DA_PAGINA:
            self.barra_opcoes.definir_ferramenta_da_pagina(NOMES_DA_TRILHA[ferramenta])
        elif aba == ABA_MARCAR and hasattr(self, "editor_selecao"):
            self.barra_opcoes.definir_ferramenta(self.barra_opcoes.ferramenta)
        self._acertar_as_propriedades()
        self._por_o_girar_no_canto()

    def _acertar_as_propriedades(self) -> None:
        """O painel Propriedades mostra o que e da ferramenta da vez (rodada
        9, 402 C: "Muda conforme a ferramenta (como no Photoshop)"):

          Dividir, Cortar, Endireitar   os botoes delas (montados em
                                        _montar_aba_corte/_bordas/_angulo)
          ferramentas de marcar         o "Marcar como" e, embaixo, as
                                        partes "Marcação desta página",
                                        "Foto" e "Pedaço" (etapa 4)
          Zoom e Mao                    a frase de que nao tem propriedades
          Os quatro filtros             idem (provisorio ate o painel Filtro)

        Chamado a cada troca de ferramenta. Nunca levanta excecao por faltar
        uma peca: o painel mostra a frase de "sem propriedades"."""
        painel = self.paineis.propriedades
        aba = self.aba_atual
        if aba in self.propriedades_das_abas:
            painel.mostrar(aba, NOMES_DA_TRILHA[FERRAMENTA_DA_ABA[aba]])
            return
        if aba == ABA_MARCAR and hasattr(self, "editor_selecao"):
            ferramenta = self.barra_opcoes.ferramenta
            nome = NOMES_DA_TRILHA.get(ferramenta, "")
            if ferramenta in FERRAMENTAS_DE_NAVEGACAO:
                painel.mostrar(painel.SEM_PROPRIEDADES, nome,
                               f"{nome} só serve para olhar a página: não tem propriedades.")
            else:
                painel.mostrar(painel.CONTEUDO_DE_MARCAR, nome)
            return
        ferramenta = FERRAMENTA_DA_ABA.get(aba)
        painel.mostrar(painel.SEM_PROPRIEDADES, NOMES_DA_TRILHA.get(ferramenta, ""),
                       "Os ajustes do filtro estão no painel “Filtro da página”.")

    def _montar_cabecalho(self) -> QWidget:
        """Os controles do antigo cabecalho, que agora vivem em outros lugares.

        A FAIXA some da tela - custava 42 px para dizer o que a barra de menu e
        a propria tela ja dizem. Os controles nao somem:

          contador de alertas    virou o painel "Para revisar"
          Desfazer / Refazer     estao no menu Editar e no painel Historico
          observacoes do livro   vao para a faixa de estado

        Eles continuam sendo CRIADOS aqui, e escondidos. O resto da tela ainda
        escreve neles - o contador, por exemplo, e atualizado a cada pagina - e
        deixar de cria-los quebraria isso em silencio: o erro viraria uma caixa
        modal, e numa bateria de testes uma caixa modal trava tudo. Foi
        exatamente o que aconteceu quando eu simplesmente tirei a chamada.
        """
        caixa = QWidget(self)
        caixa.setVisible(False)
        topo = QHBoxLayout(caixa)
        titulo = QLabel("Confira antes de processar")
        titulo.setObjectName("secao")
        topo.addWidget(titulo)

        # Os fatos do livro inteiro ficam aqui, ditos uma vez, em vez de
        # marcarem todas as páginas e afogarem o contador de alertas.
        self.rotulo_observacoes = QLabel("")
        self.rotulo_observacoes.setObjectName("fraco")
        self.rotulo_observacoes.setVisible(False)
        topo.addWidget(self.rotulo_observacoes)

        topo.addStretch()

        self.botao_alertas = QPushButton("tudo certo")
        self.botao_alertas.setObjectName("contadorAlerta")
        _ligar(self.botao_alertas, self._ir_para_proximo_alerta)
        topo.addWidget(self.botao_alertas)

        self.botao_desfazer = QPushButton("Desfazer")
        _ligar(self.botao_desfazer, self.desfazer)
        topo.addWidget(self.botao_desfazer)

        self.botao_refazer = QPushButton("Refazer")
        _ligar(self.botao_refazer, self.refazer)
        topo.addWidget(self.botao_refazer)
        return caixa

    def _montar_rodape(self) -> QVBoxLayout:
        """O rodape encolheu a uma linha, e ela mora ao lado da tira.

        A linha de atalhos saiu: eram 25 px repetindo o que Ajuda ja lista, e a
        lista de Ajuda sai dos proprios menus, entao nao diverge. "voltar" saiu
        tambem - esta em Arquivo. Sobra "Confirmar e processar", que o desenho
        poe no canto direito da faixa da tira.
        """
        fora = QVBoxLayout()
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(0)

        self.botao_processar = QPushButton("Confirmar e processar")
        self.botao_processar.setObjectName("primario")
        _ligar(self.botao_processar, self._pedir_processamento)
        return fora

    # --- paginas de imagem e linhas de botoes -----------------------------

    def _area_de_visualizador(self, aba: str, modo: str) -> Visualizador:
        """Uma página da área de imagem: setas nas laterais e a prévia no meio."""
        pagina = QWidget()
        linha = QHBoxLayout(pagina)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(6)

        anterior = QPushButton("<")
        anterior.setFixedWidth(40)
        _ligar(anterior, lambda: self._navegar(-1))
        linha.addWidget(anterior)

        visualizador = Visualizador()
        visualizador.definir_modo(modo)
        visualizador.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        linha.addWidget(visualizador, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(40)
        _ligar(proxima, lambda: self._navegar(1))
        linha.addWidget(proxima)

        visualizador.ampliar_pedido.connect(self.ampliar)
        # etapa 6: a roda do mouse troca de pagina sem zoom (_roda_na_pagina)
        visualizador.installEventFilter(self)
        visualizador.vista_mudou.connect(lambda *_: self._acertar_o_zoom_da_barra())
        self.visualizadores[aba] = visualizador
        self.paginas_de_imagem[aba] = pagina
        return visualizador

    # --- o painel Propriedades de Dividir, Cortar e Endireitar ------------
    #
    # Etapa 3 do layout (12/10/2026; rodada 9, 402 C: "Muda conforme a
    # ferramenta (como no Photoshop)"; rodada 12, 701 A: "Fazer logo o painel
    # Propriedades do Cortar"; 706 B: duas partes, "Só nesta página" e "Para o
    # livro todo"). Os botoes destas tres ferramentas sairam da fila embaixo
    # da pagina (onde a do Cortar nao cabia em 1280 x 657) para o painel
    # Propriedades. SAO OS MESMOS BOTOES, ligados as mesmas acoes; so mudaram
    # de lugar e, alguns, de nome (rodada 12, 710 B). O "está certo" e a
    # sugestao laranja de cada fila viraram os da faixa do conferir.

    def _conteudo_de_propriedades(self, aba: str) -> QVBoxLayout:
        """Cria a caixa (vazia) do conteudo do painel Propriedades da
        ferramenta da "aba" e devolve a coluna para por as pecas. A caixa
        tambem fica em `linhas_de_botoes[aba]`: quem procurava os botoes da
        ferramenta ali continua achando."""
        caixa = Bloco()
        coluna = QVBoxLayout(caixa)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(7)
        self.propriedades_das_abas[aba] = caixa
        self.linhas_de_botoes[aba] = caixa
        return coluna

    def _par_de_botoes(self, coluna: QVBoxLayout) -> QHBoxLayout:
        """Uma linha para dois botoes lado a lado, da mesma largura."""
        linha = QHBoxLayout()
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(6)
        coluna.addLayout(linha)
        return linha

    def _caixinha_do_painel(self, texto: str, dica: str, acao, coluna: QVBoxLayout) -> QCheckBox:
        """Uma caixinha de ligar e desligar do painel Propriedades (com o
        quadrado a vista tambem desligada: ui/estilo.py). Tem os mesmos
        metodos do botao "apertado" que ela substitui (isChecked, setChecked,
        click, setEnabled)."""
        caixinha = QCheckBox(texto)
        estilo.estilizar(caixinha, lambda: estilo_da_caixinha_com_quadrado(13))
        caixinha.setCursor(Qt.PointingHandCursor)
        caixinha.setFocusPolicy(Qt.NoFocus)        # o teclado continua da pagina
        caixinha.setToolTip(dica)
        _ligar(caixinha, acao)
        coluna.addWidget(caixinha)
        return caixinha

    def _parte_do_livro(self, linhas: list[str], etapa: str = "") -> QFrame:
        """A parte "Para o livro todo" do Propriedades (rodada 12, 706 B).

        Mostra o que vale para o livro inteiro e, desde a etapa 3 da obra
        (26/10/2026), abre o Automatico na etapa (`etapa`, codigo de
        core/automatico), que e onde o livro todo se muda (a tela "O que
        fazer" saiu do caminho: D-002)."""
        caixa = QFrame()
        caixa.setObjectName("parteDoLivro")
        caixa.setAttribute(Qt.WA_StyledBackground, True)
        coluna = QVBoxLayout(caixa)
        coluna.setContentsMargins(10, 8, 10, 9)
        coluna.setSpacing(5)
        coluna.addWidget(titulo_de_parte("Para o livro todo"))
        for texto in linhas:
            rotulo = QLabel(texto)
            rotulo.setObjectName("rotuloDoPainel")
            rotulo.setWordWrap(True)
            coluna.addWidget(rotulo)
        botao = _botao("mudar no Automático...", coluna,
                       lambda: self.automatico_pedido.emit(etapa))
        botao.setToolTip(
            "Abre o Automático nesta etapa: lá ela muda para o livro inteiro (ou para as "
            "páginas escolhidas). O trabalho deste livro continua.")
        return caixa

    def _montar_aba_corte(self) -> None:
        """A ferramenta Dividir a folha: a pagina com a linha azul e, no
        painel Propriedades, os botoes dela."""
        vis = self._area_de_visualizador(ABA_CORTE, MODO_CORTE)
        vis.corte_movido.connect(self._mover_corte)
        assert self.projeto is not None

        coluna = self._conteudo_de_propriedades(ABA_CORTE)
        coluna.addWidget(titulo_de_parte("Só nesta folha"))
        coluna.addWidget(titulo_de_secao("Onde dividir"))
        # Item 2.1 (G2 (a), "trocando numa folha se um ficar ruim"): o jeito
        # de dividir SO desta folha. Trocar recalcula a linha azul pelo outro
        # jeito (core.pipeline.recalcular_divisao). So habilitada em folha
        # dividida (_atualizar_botoes).
        linha = self._par_de_botoes(coluna)
        self.rotulo_jeito_da_folha = QLabel("jeito:")
        self.rotulo_jeito_da_folha.setObjectName("rotuloDoPainel")
        linha.addWidget(self.rotulo_jeito_da_folha)
        self.combo_jeito_da_folha = QComboBox()
        for jeito in dividir_scantailor.JEITOS:
            self.combo_jeito_da_folha.addItem(nome_do_jeito_de_dividir(jeito), jeito)
        self.combo_jeito_da_folha.setToolTip(
            "Divide esta folha de outro jeito: o do Editor ou o do ScanTailor. "
            "A linha azul vai para onde o outro jeito acha a divisão.")
        self.combo_jeito_da_folha.currentIndexChanged.connect(
            lambda _i: self._trocar_jeito_da_folha())
        linha.addWidget(self.combo_jeito_da_folha, 1)
        lista_estreita(self.combo_jeito_da_folha)
        par = self._par_de_botoes(coluna)
        self.botao_nao_dividir = _botao("não dividir esta", par, self._alternar_dividir)
        _botao("usar em todas", par, self._corte_em_todas).setToolTip(
            "Põe a linha de divisão desta folha em todas as folhas.")
        par.setStretch(0, 1)
        par.setStretch(1, 1)
        # (O botao "girar" que ficava aqui saiu em 13/10/2026: fazia o mesmo que
        # o "¼ à direita" do bloco "Girar a folha", logo acima no painel - os
        # dois chamavam _girar_folhas(GIRO_DIREITA), com o mesmo "aplicar em".)
        coluna.addSpacing(6)
        jeito_do_livro = dividir_scantailor.jeito_valido(
            getattr(self.projeto, "dividir_como", None))
        coluna.addWidget(self._parte_do_livro(
            [f"Jeito de dividir: {nome_do_jeito_de_dividir(jeito_do_livro)}"], "dividir"))

    def _montar_aba_bordas(self) -> None:
        """A ferramenta Cortar as bordas: a pagina com o retangulo verde e,
        no painel Propriedades, os botoes dela (rodada 12, 701 A)."""
        vis = self._area_de_visualizador(ABA_BORDAS, MODO_RECORTE)
        vis.recorte_movido.connect(self._mover_recorte)
        # Etapa 5 da obra (D-008: "a ferramenta de mover não deveria estar
        # vinculada ao corte de bordas, deveriam ser duas coisas
        # independentes"): o "Mover conteúdo" e as linhas de apoio sairam
        # daqui para a ferramenta Mover (_montar_aba_mover).
        assert self.projeto is not None

        coluna = self._conteudo_de_propriedades(ABA_BORDAS)
        coluna.addWidget(titulo_de_parte("Só nesta página"))
        coluna.addWidget(titulo_de_secao("Corte desta página"))
        _botao("não cortar esta", coluna, self._sem_recorte).setToolTip(
            "Esta página sai inteira, sem cortar a borda.")
        # Rodada 12, 710 B: era "voltar ao automático" (a mesma acao: tira o
        # corte feito a mao e volta a valer o que o programa acha sozinho).
        _botao("usar o corte do programa", coluna, self._recorte_automatico).setToolTip(
            "Desfaz o corte que você arrastou nesta página: volta a valer o corte "
            "que o programa acha sozinho.")
        par = self._par_de_botoes(coluna)
        _botao("usar em todas", par, self._recorte_em_todas).setToolTip(
            "Põe o corte desta página em todas as páginas.")
        _botao("tamanho...", par, self._escolher_tamanho_da_folha).setToolTip(
            "Escolhe o tamanho da folha em que esta página vai sair.")
        par.setStretch(0, 1)
        par.setStretch(1, 1)

        coluna.addWidget(risco_do_painel())
        coluna.addWidget(titulo_de_secao("Ao arrastar"))
        tecla_m = atalhos.tecla_atual(CHAVE_RECORTE_ESPELHADO)
        tecla_t = atalhos.tecla_atual(CHAVE_RECORTE_PROPORCAO)
        self.botao_espelhado = self._caixinha_do_painel(
            f"Espelhado   (tecla {tecla_m})",
            "Arrastar um lado do retângulo mexe o lado oposto junto.",
            self._alternar_espelhado, coluna)
        self.botao_proporcao_travada = self._caixinha_do_painel(
            f"Proporção travada   (tecla {tecla_t})",
            "O retângulo muda de tamanho sem mudar de formato.",
            self._alternar_proporcao_travada, coluna)
        coluna.addWidget(frase_do_painel(
            "Para mover ou mudar o tamanho do conteúdo na folha, use a ferramenta Mover "
            f"(tecla {tecla_de(FERRAMENTA_MOVER)})."))

        coluna.addWidget(risco_do_painel())
        coluna.addWidget(titulo_de_secao("Qualidade da prévia"))
        seletor_qualidade = QComboBox()
        for chave, nome in NOMES_DA_QUALIDADE.items():
            seletor_qualidade.addItem(nome, chave)
        seletor_qualidade.setCurrentIndex(
            seletor_qualidade.findData(self._qualidade_da_previa))
        seletor_qualidade.setToolTip(
            "Rápida: abre logo. Alta: mais nítida no zoom, demora mais por página."
        )
        seletor_qualidade.currentIndexChanged.connect(
            lambda i: self._mudar_qualidade_da_previa(seletor_qualidade.itemData(i)))
        self.seletor_qualidade = seletor_qualidade
        coluna.addWidget(seletor_qualidade)
        lista_estreita(seletor_qualidade)
        coluna.addWidget(frase_do_painel(
            "Rápida: abre logo. Alta: mais nítida no zoom, demora mais por página."))
        coluna.addSpacing(6)
        coluna.addWidget(self._parte_do_livro(
            ["Cortar a beirada da folha vizinha: "
             + ("sim" if getattr(self.projeto, "cortar_sobra", False) else "não"),
             # item 2.5 (G8): o corte que segue o conteudo
             "Cortar seguindo o conteúdo (como o ScanTailor): "
             + ("sim" if getattr(self.projeto, "cortar_pelo_conteudo", False) else "não"),
             # item 2.13 (g7): a borda preta do scanner
             "Página dentro da borda preta: "
             + (_nome_da_borda(self.projeto) if getattr(self.projeto, "borda_preta", False)
                else "não")], "cortar"))

    def _escolher_tamanho_da_folha(self) -> None:
        """Problema 1, opção A: digitar o tamanho final em vez de arrastar.

        Item 2/4 do teste do Boécio (seção 3a do plano): este botão SÓ decide
        o tamanho da FOLHA (`ConfigPagina.tamanho_folha_cm`) - nunca mais toca
        em `recorte`. Antes ele chamava `recorte_para_tamanho_cm` e
        `_mover_recorte`, o que substituía e recentralizava o corte que o
        usuário já tinha feito à mão (o bug relatado). O recorte serve para
        DUAS coisas agora, sem se atropelar: recortar a imagem original, e
        (separadamente) posicionar-se dentro do tamanho de folha escolhido
        aqui - ver `core/folha.py::compor_na_folha`.

        Etapa 5 da obra: o mesmo botão mora também na ferramenta Mover ("tamanho
        da folha..."), onde a folha é a ÁREA BRANCA em que a página anda. Lá a
        imagem já é a página cortada: o tamanho de agora é o dela.
        """
        from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha
        from core.folha import medidas_do_recorte_em_cm

        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if self.aba_atual == ABA_MOVER:
            vis = self.visualizadores[ABA_MOVER]
            recorte = (0.0, 0.0, 1.0, 1.0)
        else:
            vis = self.visualizadores[ABA_BORDAS]
            recorte = pagina.recorte or (0.0, 0.0, 1.0, 1.0)
        largura_px, altura_px = vis.tamanho_da_pagina_px()
        if largura_px == 0:
            return
        dpi = vis.dpi_atual()

        atual = medidas_do_recorte_em_cm(recorte, largura_px, altura_px, dpi)

        dialogo = DialogoTamanhoDaFolha(
            atual["largura_final"], atual["altura_final"],
            tamanho_atual=pagina.tamanho_folha_cm, parent=self,
        )

        if dialogo.exec() != DialogoTamanhoDaFolha.Accepted:
            return

        self._mudar_tamanho_da_folha(dialogo.tamanho_escolhido())

    @protegido
    def _mudar_tamanho_da_folha(self, tamanho_cm: tuple[float, float]) -> None:
        """Registra `tamanho_folha_cm` no histórico - mesmo padrão de
        `_mover_corte`/`_mover_angulo` (`@protegido` + `_registrar`)."""
        arredondado = (round(tamanho_cm[0], 2), round(tamanho_cm[1], 2))
        self._registrar(
            "tamanho_folha", "pagina", [self.indice_pagina],
            {"tamanho_folha_cm": list(arredondado)},
            f"Tamanho da folha da página {self.indice_pagina + 1}: "
            f"{arredondado[0]:.1f} × {arredondado[1]:.1f} cm",
        )

    def _atualizar_previa_para_recorte(self, vis, pagina) -> None:
        """A aba Bordas, fora do modo "Mover conteúdo": mostra a folha girada
        e dividida, mas NUNCA cortada - o recorte é só um retângulo desenhado
        por cima, sempre em fração da MESMA imagem estável.

        Bug real achado ao vivo (23/09/2026, Samuel: "quando eu diminuo a
        linha verde ele corta a própria folha e o corte vai pra frente
        sozinho"): antes, esta aba mostrava a prévia JÁ cortada por
        `pagina.recorte` (a mesma das outras ferramentas) - o
        retângulo do recorte era desenhado como fração de uma imagem que já
        era um recorte, e cada atualização (ao soltar o mouse) reaplicava a
        fração em cima do resultado anterior, comprimindo o corte sozinho a
        cada vez. Ver `core.pipeline.preparar_para_recorte`.
        """
        img = self.previas.pegar_para_recorte(self.indice_pagina, self._dpi_atual)
        vis.definir_imagem(img, dono=("pagina", self.indice_pagina))   # D4
        if img is not None:
            vis.definir_composicao((0.0, 0.0, 1.0, 1.0), (img.shape[1], img.shape[0]))

    def _conferir_tamanho_da_folha(self, pagina, vis) -> None:
        """Decisão 2 do plano: se o recorte crescer depois de já haver uma
        folha escolhida e ela ficar pequena demais, avisa DE FORMA VISÍVEL
        E PERSISTENTE na tela (não só no instante do diálogo) - mesmo padrão
        de `_conferir_qualidade_do_preto_e_branco` (alerta computado ao vivo,
        comparando com o estado atual da página).
        """
        from core.analise import FOLHA_MENOR_QUE_O_RECORTE
        from core.folha import medidas_do_recorte_em_cm, tamanho_da_folha_cabe

        largura_px, altura_px = vis.tamanho_da_pagina_px()
        tinha = FOLHA_MENOR_QUE_O_RECORTE in pagina.alertas
        pagina.alertas = [a for a in pagina.alertas if a != FOLHA_MENOR_QUE_O_RECORTE]

        cabe = True
        if pagina.tamanho_folha_cm is not None and largura_px > 0 and altura_px > 0:
            medidas = medidas_do_recorte_em_cm(
                pagina.recorte or (0.0, 0.0, 1.0, 1.0), largura_px, altura_px, vis.dpi_atual())
            cabe = tamanho_da_folha_cabe(
                pagina.tamanho_folha_cm,
                (medidas["largura_final"], medidas["altura_final"]),
            )
            if not cabe:
                pagina.alertas.append(FOLHA_MENOR_QUE_O_RECORTE)

        if tinha != (not cabe):
            self._atualizar_faixa()
            self._atualizar_tira()
            self._atualizar_contador()

    def _mudar_qualidade_da_previa(self, nome_qualidade: str) -> None:
        """Troca a resolução da prévia (estilo After Effects: Rápida/Média/Alta).

        Fica salvo (configuracoes.py) e vale para a próxima vez que o
        programa abrir também.
        """
        import configuracoes

        if nome_qualidade not in QUALIDADES_DA_PREVIA:
            return
        self._qualidade_da_previa = nome_qualidade
        self._dpi_normal = QUALIDADES_DA_PREVIA[nome_qualidade]
        self._dpi_atual = self._dpi_normal
        configuracoes.escrever("qualidade_previa", nome_qualidade)
        self.atualizar()

    def _alternar_espelhado(self) -> None:
        if self.botao_espelhado.isChecked():
            self.botao_proporcao_travada.setChecked(False)
        self._atualizar_modo_arraste_recorte()

    def _alternar_proporcao_travada(self) -> None:
        if self.botao_proporcao_travada.isChecked():
            self.botao_espelhado.setChecked(False)
        self._atualizar_modo_arraste_recorte()

    def _atualizar_modo_arraste_recorte(self) -> None:
        from ui.widgets.visualizador import (
            RECORTE_ESPELHADO,
            RECORTE_LIVRE,
            RECORTE_PROPORCAO,
        )

        if self.botao_espelhado.isChecked():
            modo = RECORTE_ESPELHADO
        elif self.botao_proporcao_travada.isChecked():
            modo = RECORTE_PROPORCAO
        else:
            modo = RECORTE_LIVRE
        self.visualizadores[ABA_BORDAS].definir_modo_arraste_recorte(modo)

    # --- item 2.5, g8-guias: as linhas de apoio do "Mover conteudo" -------

    def _mostrar_as_linhas_de_apoio(self, vis, pagina, folha_cm=None) -> None:
        """Passa ao visualizador as linhas do livro (guardadas em mm a partir
        do meio da folha, core/guias) convertidas para a área branca desta
        página, e se as automaticas valem. Etapa 5 da obra: sem tamanho de
        folha a área branca é a própria página (`folha_cm`, o tamanho dela em
        cm); antes, sem folha escolhida, não havia linha nenhuma."""
        from core import guias

        folha_cm = pagina.tamanho_folha_cm or folha_cm
        linhas = []
        if folha_cm is not None:
            linhas = [(g.orientacao, guias.em_fracao(g, folha_cm))
                      for g in guias.do_projeto(getattr(self.projeto, "guias", []))]
        vis.definir_guias(linhas, bool(getattr(self.projeto, "guias_automaticas", True)))
        self.botao_linhas_automaticas.blockSignals(True)
        self.botao_linhas_automaticas.setChecked(
            bool(getattr(self.projeto, "guias_automaticas", True)))
        self.botao_linhas_automaticas.blockSignals(False)

    def _gravar_no_livro(self, campo: str, valor, descricao: str) -> None:
        """Uma mudanca que vale para o livro (campo "livro." da acao,
        historico_acoes.aplicar), numa acao do Historico que o Ctrl+Z desfaz."""
        assert self.projeto is not None and self.acoes is not None
        acao = montar_acao(self.projeto, campo, "pagina", [], {}, descricao)
        acao.antes[f"livro.{campo}"] = getattr(self.projeto, campo)
        acao.depois[f"livro.{campo}"] = valor
        aplicar(self.projeto, acao, acao.depois)
        self.acoes.registrar(acao)
        self.atualizar()

    @protegido
    def _mudar_as_linhas_de_apoio(self, linhas: list) -> None:
        """O menu do botao direito mudou as linhas (fracao da area branca desta
        pagina): grava no livro em mm a partir do meio da folha (como o
        ScanTailor). Sem tamanho de folha, a area branca e a propria pagina
        (etapa 5 da obra)."""
        from core import guias

        if self.projeto is None:
            return
        folha_cm = self._area_branca_em_cm()
        if folha_cm is None:
            return
        novas = guias.para_salvar(guias.de_fracao(o, p, folha_cm) for o, p in linhas)
        antes = len(getattr(self.projeto, "guias", []) or [])
        descricao = ("Linha de apoio posta" if len(novas) > antes
                     else "Linhas de apoio tiradas" if not novas else "Linha de apoio tirada")
        self._gravar_no_livro("guias", novas, descricao)

    @protegido
    def _alternar_linhas_automaticas(self) -> None:
        if self.projeto is None:
            return
        ligadas = self.botao_linhas_automaticas.isChecked()
        if ligadas == bool(getattr(self.projeto, "guias_automaticas", True)):
            return
        self._gravar_no_livro("guias_automaticas", ligadas,
                              "Linhas automáticas " + ("ligadas" if ligadas else "desligadas"))

    # --- etapa 5 da obra: a ferramenta "Mover e redimensionar" --------------
    #
    # Decisões do Samuel (docs/plano/DECISOES.md): D-008 ("a ferramenta de
    # mover não deveria estar vinculada ao corte de bordas, deveriam ser duas
    # coisas independentes"; "como é no photoshope, que você arrasta a hora que
    # quiser e aumenta a hora que quiser"), D-017 (aumentar além da beirada:
    # aviso, a parte de fora marcada, nada diminuído sozinho), D-303
    # ("precisamos centralizar"), D-056 (`g8-guias`: linhas à mão e
    # automáticas, que se desligam), D-473 (a tela mostra o que sai no PDF),
    # G10 + D-090 ("usar em todas" com as exceções desmarcadas).
    # A ÁREA BRANCA é a folha escolhida ou, sem folha, a própria página
    # (core.folha.area_branca_que_vale, a mesma conta de compor_na_folha).
    # Tudo o que muda aqui é uma ação do desfazer e grava a marca "mexida à
    # mão" (MOVER) pelo _registrar. Arriscado: gravar o retângulo em fração da
    # área MOSTRADA sem passar pelos pontos (_gravar_o_retangulo): na página
    # com a folha menor que o conteúdo (rede de segurança) o lugar mudaria.

    def _montar_aba_mover(self) -> None:
        """A ferramenta Mover e redimensionar: a página na área branca (o
        visualizador no modo do conteúdo, ver ui/widgets/visualizador.py, "A
        FERRAMENTA MOVER") e, no painel Propriedades, a área branca, o tamanho
        em %, "Centralizar", "voltar como veio", "usar em todas..." e as
        linhas de apoio."""
        vis = self._area_de_visualizador(ABA_MOVER, MODO_CONTEUDO)
        vis.conteudo_movido.connect(self._mover_conteudo)
        vis.guias_mudaram.connect(self._mudar_as_linhas_de_apoio)    # item 2.5, g8-guias
        assert self.projeto is not None

        coluna = self._conteudo_de_propriedades(ABA_MOVER)
        coluna.addWidget(titulo_de_parte("Só nesta página"))
        coluna.addWidget(frase_do_painel(
            "Arraste a página para mover. Puxe um canto para aumentar ou diminuir."))
        coluna.addWidget(titulo_de_secao("Área branca"))
        self.rotulo_area_branca = QLabel("")
        self.rotulo_area_branca.setObjectName("rotuloDoPainel")
        self.rotulo_area_branca.setWordWrap(True)
        coluna.addWidget(self.rotulo_area_branca)
        _botao("tamanho da folha...", coluna, self._escolher_tamanho_da_folha).setToolTip(
            "Escolhe o tamanho da folha em que esta página vai sair. Sem escolher, a área "
            "branca é a própria página.")

        coluna.addWidget(risco_do_painel())
        coluna.addWidget(titulo_de_secao("Tamanho do conteúdo"))
        self.campo_tamanho_do_conteudo = QSpinBox()
        self.campo_tamanho_do_conteudo.setRange(5, int(MAIOR_TAMANHO_DO_CONTEUDO * 100))
        self.campo_tamanho_do_conteudo.setSuffix(" %")
        self.campo_tamanho_do_conteudo.setKeyboardTracking(False)
        self.campo_tamanho_do_conteudo.setValue(100)
        self.campo_tamanho_do_conteudo.setToolTip(
            "O tamanho do conteúdo: 100% é como veio. Mais que 100% aumenta (o que passar "
            "da beirada fica de fora e aparece marcado em vermelho).")
        self.campo_tamanho_do_conteudo.valueChanged.connect(self._mudar_tamanho_do_conteudo)
        coluna.addWidget(self.campo_tamanho_do_conteudo)
        par = self._par_de_botoes(coluna)
        self.botao_centralizar = _botao("Centralizar", par, self._centralizar_conteudo)
        self.botao_centralizar.setToolTip(
            "Põe o que está impresso no meio da área branca, nas duas direções.")
        _botao("voltar como veio", par, self._conteudo_como_veio).setToolTip(
            "Desfaz o mover e o tamanho desta página: o conteúdo volta como veio.")
        par.setStretch(0, 1)
        par.setStretch(1, 1)
        _botao("usar em todas...", coluna, self._mover_em_todas).setToolTip(
            "Põe o tamanho e o lugar do conteúdo desta página nas páginas que você escolher.")
        # D-017: o aviso da parte de fora fica no painel (e na faixa de baixo,
        # como todo aviso), nunca por cima da página (D-019)
        self.aviso_de_fora = QLabel(
            "Parte do que está impresso vai ficar de fora (marcada em vermelho na página).")
        self.aviso_de_fora.setObjectName("rotuloDoPainel")
        self.aviso_de_fora.setWordWrap(True)
        self.aviso_de_fora.setStyleSheet(f"color: {COR_DO_AVISO_DE_FORA}; font-weight: 600;")
        self.aviso_de_fora.setVisible(False)
        coluna.addWidget(self.aviso_de_fora)

        coluna.addWidget(risco_do_painel())
        coluna.addWidget(titulo_de_secao("Linhas de apoio"))
        # Item 2.5, g8-guias (Samuel, 13/10/2026: "As duas" + "Mas ele vai
        # poder tirar a automatica a hora que ele quiser."): o ima do meio e
        # das beiradas, para o livro todo. As linhas do Kaique: botao direito
        # sobre a pagina. Desde a etapa 5 moram aqui (antes, no "Mover
        # conteudo" das Bordas).
        self.botao_linhas_automaticas = self._caixinha_do_painel(
            "Linhas automáticas (meio e beiradas)",
            "Ao mover, o que está impresso gruda no meio e nas beiradas da área branca. "
            "Vale para o livro todo.",
            self._alternar_linhas_automaticas, coluna)
        self.botao_linhas_automaticas.setChecked(
            bool(getattr(self.projeto, "guias_automaticas", True)))
        coluna.addWidget(frase_do_painel(
            "Para pôr uma linha sua, clique com o botão direito na página."))

    def _atualizar_o_mover(self, img, pagina) -> None:
        """Põe a página da vez na ferramenta Mover: a página como vai sair (com
        as margens iguais, se ligadas: D-329), a área branca de verdade, o
        lugar e o tamanho de agora, a caixa do impresso e as linhas de apoio;
        acerta o painel e o aviso do D-017 (mesma conta do PDF)."""
        from core.folha import (area_branca_que_vale, caixa_do_impresso,
                                parte_impressa_de_fora, retangulo_na_folha)
        from core.pipeline import anotar_o_impresso_de_fora

        vis = self.visualizadores[ABA_MOVER]
        vis.definir_dpi(self._dpi_atual)
        dono = ("pagina", self.indice_pagina)
        if img is None:
            vis.definir_mover(None, None, vis._retangulo_conteudo, vis._caixa_do_impresso,
                              dono=dono)
            return
        conteudo = self._com_as_margens(img)
        conteudo_px = (conteudo.shape[1], conteudo.shape[0])
        mexido = etapas_core.conteudo_mexido(self.projeto, pagina)
        area, vale = area_branca_que_vale(conteudo_px, pagina.tamanho_folha_cm,
                                          self._dpi_atual, pagina.conteudo_escala, mexido)
        if vale:
            retangulo = retangulo_na_folha(pagina.conteudo_escala,
                                           pagina.conteudo_deslocamento, area, conteudo_px)
        else:
            retangulo = (0.0, 0.0, 1.0, 1.0)      # compor_na_folha deixa como esta
        chave = (id(img), conteudo_px)
        if getattr(self, "_caixa_do_mover", (None, None))[0] != chave:
            self._caixa_do_mover = (chave, caixa_do_impresso(conteudo))
        caixa = self._caixa_do_mover[1]
        vis.definir_mover(conteudo, area, retangulo, caixa, dono=dono)
        # o que as acoes da ferramenta precisam (em pontos desta previa)
        self._mover_da_vez = {"area": area, "vale": vale, "conteudo": conteudo_px,
                              "caixa": caixa, "dpi": self._dpi_atual}
        self._mostrar_as_linhas_de_apoio(vis, pagina, self._area_branca_em_cm())

        tinha = analise.IMPRESSO_DE_FORA in pagina.alertas
        fora = anotar_o_impresso_de_fora(pagina, parte_impressa_de_fora(
            conteudo, pagina.tamanho_folha_cm, self._dpi_atual,
            escala=pagina.conteudo_escala, deslocamento=pagina.conteudo_deslocamento,
            mexido_a_mao=mexido))
        self._acertar_o_painel_do_mover(pagina, area, conteudo_px, vale, fora)
        if tinha != fora:
            self._atualizar_faixa()
            self._atualizar_tira()
            self._atualizar_contador()

    def _acertar_o_painel_do_mover(self, pagina, area, conteudo_px, vale, fora) -> None:
        """As palavras do painel da ferramenta Mover: o tamanho da área branca
        (a página, ou a folha escolhida), o tamanho do conteúdo em % e o aviso
        da parte de fora."""
        dpi = self._dpi_atual or 1
        largura_cm, altura_cm = area[0] / dpi * 2.54, area[1] / dpi * 2.54
        medida = f"{largura_cm:.1f} × {altura_cm:.1f} cm".replace(".", ",")
        if pagina.tamanho_folha_cm is None:
            texto = f"A própria página ({medida})."
        elif vale:
            texto = f"A folha escolhida ({medida})."
        else:
            folha = pagina.tamanho_folha_cm
            escolhida = f"{folha[0]:.1f} × {folha[1]:.1f} cm".replace(".", ",")
            texto = (f"A folha escolhida ({escolhida}) é menor que o conteúdo: a página sai "
                     f"do tamanho dele ({medida}) até você mover ou diminuir.")
        self.rotulo_area_branca.setText(texto)
        self.campo_tamanho_do_conteudo.blockSignals(True)
        self.campo_tamanho_do_conteudo.setValue(int(round(float(pagina.conteudo_escala) * 100)))
        self.campo_tamanho_do_conteudo.blockSignals(False)
        self.aviso_de_fora.setVisible(bool(fora))

    def _area_branca_em_cm(self) -> tuple[float, float] | None:
        """A área branca da página da vez, em cm (para as linhas de apoio, que
        o livro guarda em mm a partir do meio): a folha escolhida ou a própria
        página. None antes de a página chegar à ferramenta Mover."""
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        if pagina.tamanho_folha_cm is not None:
            return tuple(pagina.tamanho_folha_cm)
        da_vez = getattr(self, "_mover_da_vez", None)
        if not da_vez:
            return None
        dpi = da_vez["dpi"] or 1
        return (da_vez["area"][0] / dpi * 2.54, da_vez["area"][1] / dpi * 2.54)

    def _gravar_o_retangulo(self, retangulo, descricao: str) -> None:
        """O retângulo do conteúdo (fração da área branca MOSTRADA) vira o
        tamanho e o lugar gravados na página. A conta é em pontos: o centro e
        o tamanho na área mostrada, e o deslocamento em fração da área branca
        que o PDF vai usar - as duas têm o mesmo meio. É a mesma área, menos na
        página com a folha escolhida menor que o conteúdo, que ainda não foi
        mexida: lá a tela mostra a página inteira (o PDF não a corta) e o
        primeiro mover passa a valer na folha escolhida."""
        from core.folha import tamanho_da_folha_px

        da_vez = getattr(self, "_mover_da_vez", None)
        if not da_vez or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        mostrada, conteudo_px = da_vez["area"], da_vez["conteudo"]
        x, y, w, h = retangulo
        escala = (w * mostrada[0] / conteudo_px[0] + h * mostrada[1] / conteudo_px[1]) / 2
        de_verdade = tamanho_da_folha_px(pagina.tamanho_folha_cm, da_vez["dpi"], conteudo_px)
        deslocamento = ((x + w / 2 - 0.5) * mostrada[0] / de_verdade[0],
                        (y + h / 2 - 0.5) * mostrada[1] / de_verdade[1])
        self._gravar_o_conteudo(escala, deslocamento, descricao)

    def _gravar_o_conteudo(self, escala: float, deslocamento, descricao: str,
                           indices: list[int] | None = None) -> bool:
        """Grava tamanho e lugar do conteúdo (numa ação do desfazer; a marca
        "mexida à mão" vem do _registrar). Nada muda se já está assim.
        Devolve se gravou."""
        assert self.projeto is not None
        indices = [self.indice_pagina] if indices is None else list(indices)
        escala = round(max(0.05, min(MAIOR_TAMANHO_DO_CONTEUDO, float(escala))), 4)
        deslocamento = (round(float(deslocamento[0]), 4), round(float(deslocamento[1]), 4))
        if all(self.projeto.paginas[i].conteudo_escala == escala
               and tuple(self.projeto.paginas[i].conteudo_deslocamento) == deslocamento
               for i in indices):
            return False
        self._registrar(
            "mover_conteudo", "pagina", indices,
            {"conteudo_deslocamento": list(deslocamento), "conteudo_escala": escala},
            descricao)
        return True

    @protegido
    def _mudar_tamanho_do_conteudo(self, porcento: int) -> None:
        """O número "Tamanho do conteúdo" (em %): aumenta ou diminui em volta
        do meio de agora (o lugar não muda), como puxar um canto."""
        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        self._gravar_o_conteudo(int(porcento) / 100.0, pagina.conteudo_deslocamento,
                                f"Tamanho do conteúdo da página {self.indice_pagina + 1}: "
                                f"{int(porcento)}%")

    @protegido
    def _centralizar_conteudo(self) -> None:
        """D-303 ("precisamos centralizar"; teste do Kaique, 26/10: "mover ele
        para o meio da folha"): o que está IMPRESSO vai para o meio da área
        branca, nas duas direções, no tamanho de agora. Usa a caixa do
        impresso (core.folha.caixa_do_impresso), não a moldura da página -
        que tem margens diferentes dos dois lados (o 15 × 53 do Kaique)."""
        from core.folha import deslocamento_para_centralizar, tamanho_da_folha_px

        da_vez = getattr(self, "_mover_da_vez", None)
        if not self._pronta() or self.projeto is None or not da_vez:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        area = tamanho_da_folha_px(pagina.tamanho_folha_cm, da_vez["dpi"], da_vez["conteudo"])
        deslocamento = deslocamento_para_centralizar(
            da_vez["caixa"], pagina.conteudo_escala, area, da_vez["conteudo"])
        self._gravar_o_conteudo(pagina.conteudo_escala, deslocamento,
                                f"Conteúdo no meio da página {self.indice_pagina + 1}")

    @protegido
    def _conteudo_como_veio(self) -> None:
        """"voltar como veio": tamanho 100% e sem mover (o tamanho de folha,
        se escolhido, fica)."""
        if not self._pronta() or self.projeto is None:
            return
        self._gravar_o_conteudo(1.0, (0.0, 0.0),
                                f"Conteúdo como veio na página {self.indice_pagina + 1}")

    @protegido
    def _mover_em_todas(self) -> None:
        """"usar em todas..." (G10, 05/10: "ter uma opção para passar isso para
        todas as folhas"; D-090: as exceções vêm desmarcadas e nunca são
        apagadas; D-091: "Selecionar todas" e "Nenhuma"): o tamanho e o lugar
        do conteúdo desta página vão para as páginas escolhidas, numa ação do
        desfazer. Depois, por trás, o programa confere em cada uma se parte do
        impresso ficou de fora (D-017) e põe o aviso no "Para revisar"."""
        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = self._escolher_paginas_do_mover()
        if not indices:
            return
        if self._gravar_o_conteudo(pagina.conteudo_escala, pagina.conteudo_deslocamento,
                                   f"Tamanho e lugar do conteúdo em {len(indices)} páginas",
                                   indices=indices):
            self._conferir_o_impresso_por_tras([i for i in indices if i != self.indice_pagina])

    def _escolher_paginas_do_mover(self) -> list[int]:
        """A janela "Em quais páginas?" do "usar em todas..." da ferramenta
        Mover (as páginas com tamanho ou lugar próprio vêm desmarcadas).
        Separado para os testes trocarem a janela."""
        from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

        dialogo = DialogoEscolherPaginas(
            self.projeto, self.indice_pagina, self,
            tem_proprio=etapas_core.conteudo_fora_do_padrao,
            explicacao=("O tamanho e o lugar do conteúdo desta página vão para as páginas "
                        "marcadas. As páginas em que você já mexeu vêm desmarcadas, para não "
                        "perder o que fez nelas."),
            marca="já mexida")
        if dialogo.exec() != DialogoEscolherPaginas.Accepted:
            return []
        return dialogo.escolhidas()

    def _conferir_o_impresso_por_tras(self, indices: list[int]) -> None:
        """Confere por trás (QThread, a janela não para) se parte do impresso
        fica de fora nas páginas `indices` (D-017: "nada é cortado sem a
        pessoa ver"), e põe ou tira o aviso de cada uma quando a conta chega."""
        from ui.tarefas import TarefaConferirOImpressoDeFora

        if not indices or self.projeto is None:
            return
        anterior = getattr(self, "_tarefa_do_impresso", None)
        if anterior is not None and anterior.isRunning():
            anterior.cancelar()
            anterior.wait(2000)
        tarefa = TarefaConferirOImpressoDeFora(self.projeto, indices)
        tarefa.conferida.connect(self._impresso_conferido)
        tarefa.terminou.connect(self._impresso_conferido_em_todas)
        self._tarefa_do_impresso = tarefa
        tarefa.start()

    def _medir_o_em_branco_por_tras(self, paginas: list[int]) -> None:
        """D-497 (etapa 7 da obra): depois de dividir, juntar ou mover a linha
        de uma folha, mede por trás (QThread) se alguma página dela ficou
        branca e põe o "Parece em branco" (o aviso que a pessoa já tirou não
        volta). A conta é do núcleo, da etapa 9d (core.pipeline.
        medir_o_em_branco); ENQUANTO ELA NÃO ESTIVER NA OBRA, nada acontece
        aqui - a parte da tela fica pronta para ligar. Nunca levanta."""
        try:
            from core import pipeline

            medir = getattr(pipeline, "medir_o_em_branco", None)
            if medir is None or not paginas or self.projeto is None:
                return
            from ui.tarefas import TarefaMedirOEmBranco

            anterior = getattr(self, "_tarefa_do_em_branco", None)
            if anterior is not None and anterior.isRunning():
                anterior.cancelar()
                anterior.wait(2000)
            tarefa = TarefaMedirOEmBranco(self.projeto, paginas, medir)
            tarefa.terminou.connect(self._impresso_conferido_em_todas)
            self._tarefa_do_em_branco = tarefa
            tarefa.start()
        except Exception:  # noqa: BLE001 - o aviso é ajuda; nunca derruba a tela
            registrar_erro("medir o em branco por tras", traceback.format_exc())

    def _impresso_conferido(self, indice: int, fracao: float) -> None:
        """A conta de uma página chegou da conferência por trás: põe ou tira
        o aviso (a mesma função do PDF e da tela)."""
        from core.pipeline import anotar_o_impresso_de_fora

        if self.projeto is None or not 0 <= indice < len(self.projeto.paginas):
            return
        anotar_o_impresso_de_fora(self.projeto.paginas[indice], fracao)

    def _impresso_conferido_em_todas(self) -> None:
        """A conferência por trás terminou: a faixa, a tira, o contador e os
        painéis mostram os avisos novos."""
        if not self._pronta():
            return
        self._atualizar_faixa()
        self._atualizar_tira()
        self._atualizar_contador()
        self._atualizar_paineis()

    def _montar_aba_angulo(self) -> None:
        vis = self._area_de_visualizador(ABA_ANGULO, MODO_ANGULO)
        vis.angulo_movido.connect(self._mover_angulo)

        assert self.projeto is not None
        # Etapa 3 do layout: os botoes do Endireitar moram no painel
        # Propriedades (ver "o painel Propriedades de Dividir, Cortar e
        # Endireitar", acima). Item 2.2 (G5 (c)): o angulo em numero com as
        # setas de 0,1 grau (icones desenhados a mao, os da barra de girar) e
        # o "aplicar em".
        from ui.widgets.barra_girar import LADO_DO_ICONE, icone_de_giro

        coluna = self._conteudo_de_propriedades(ABA_ANGULO)
        coluna.addWidget(titulo_de_parte("Só nesta página"))
        coluna.addWidget(titulo_de_secao("Inclinação desta página"))
        linha2 = self._par_de_botoes(coluna)

        self.botao_angulo_anti_horario = _botao(
            "0,1°", linha2, lambda: self._ajustar_angulo(+PASSO_DO_ANGULO))
        self.botao_angulo_anti_horario.setIcon(icone_de_giro(girar.GIRO_ESQUERDA))
        self.botao_angulo_anti_horario.setToolTip(
            "Gira a página 0,1 grau no sentido anti-horário")
        self.campo_angulo = QDoubleSpinBox()
        self.campo_angulo.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))   # virgula
        self.campo_angulo.setRange(-45.0, 45.0)
        self.campo_angulo.setDecimals(2)
        self.campo_angulo.setSingleStep(PASSO_DO_ANGULO)
        self.campo_angulo.setSuffix(" graus")
        # Sem as setinhas proprias (as de 0,1 grau ficam ao lado): elas
        # existem com largura zero pela folha de estilo (ui/estilo.py,
        # "campo_angulo"). NoButtons deixava o numero invisivel no Qt 6.12.
        self.campo_angulo.setObjectName("campo_angulo")
        self.campo_angulo.setKeyboardTracking(False)
        self.campo_angulo.setAlignment(Qt.AlignRight)
        self.campo_angulo.setToolTip(
            "A inclinação desta página, em graus (positivo = sentido anti-horário). "
            "Digite um número e aperte Enter, ou use as setas ao lado.")
        self.campo_angulo.valueChanged.connect(self._angulo_digitado)
        self.campo_angulo.editingFinished.connect(self._angulo_digitado_acabou)
        linha2.addWidget(self.campo_angulo, 1)
        self.botao_angulo_horario = _botao(
            "0,1°", linha2, lambda: self._ajustar_angulo(-PASSO_DO_ANGULO))
        self.botao_angulo_horario.setIcon(icone_de_giro(girar.GIRO_DIREITA))
        self.botao_angulo_horario.setToolTip("Gira a página 0,1 grau no sentido horário")
        for botao in (self.botao_angulo_anti_horario, self.botao_angulo_horario):
            botao.setIconSize(QSize(LADO_DO_ICONE, LADO_DO_ICONE))
            botao.setFocusPolicy(Qt.NoFocus)       # nao rouba as setas do teclado
        # as setinhas desenhadas a mao acompanham a troca de tema (etapa 2 do
        # layout: no tema claro elas ficavam na cor clara do tema de antes)
        estilo.estilizar(self.propriedades_das_abas[ABA_ANGULO],
                         self._icones_das_setas_do_angulo)
        linha3 = self._par_de_botoes(coluna)
        self.rotulo_alcance_do_angulo = QLabel("aplicar em:")
        self.rotulo_alcance_do_angulo.setObjectName("rotuloDoPainel")
        linha3.addWidget(self.rotulo_alcance_do_angulo)
        self.combo_alcance_do_angulo = QComboBox()
        self.combo_alcance_do_angulo.setFocusPolicy(Qt.NoFocus)
        # Rodada 12, 709 B: as palavras da lista dizem PAGINA (a lista do
        # girar diz folha); os codigos (core/girar.ALCANCES) sao os mesmos.
        nomes = nomes_dos_alcances("página")
        for alcance in girar.ALCANCES:
            self.combo_alcance_do_angulo.addItem(nomes[alcance], alcance)
        self.combo_alcance_do_angulo.setToolTip(
            "Em quais páginas o ângulo vale: o que você fizer aqui (girar, "
            "deixar como veio, usar o ângulo do programa) vale para todas as escolhidas.")
        linha3.addWidget(self.combo_alcance_do_angulo, 1)
        lista_estreita(self.combo_alcance_do_angulo)
        # Rodada 12, 710 B: eram "não endireitar esta" e "voltar ao
        # automático" (as mesmas acoes, com outro nome).
        _botao("deixar como veio", coluna, self._angulo_zero).setToolTip(
            "Não endireita: a página sai com a inclinação com que veio no PDF.")
        _botao("usar o ângulo do programa", coluna, self._angulo_automatico).setToolTip(
            "Desfaz o seu ajuste: volta a valer o ângulo que o programa acha sozinho.")

        # Item 2.2 (G4 (b): "eu vou ter a opção de escolher"): a conta do
        # endireitar automatico SO desta pagina, e os dois angulos que as
        # contas acharam (_atualizar_botoes).
        coluna.addWidget(risco_do_painel())
        self.rotulo_conta_do_endireitar = titulo_de_secao("Conta")
        coluna.addWidget(self.rotulo_conta_do_endireitar)
        self.combo_conta_do_endireitar = QComboBox()
        for jeito in endireitar_scantailor.JEITOS:
            self.combo_conta_do_endireitar.addItem(nome_da_conta(jeito), jeito)
        self.combo_conta_do_endireitar.setToolTip(
            "Endireita esta página por outra conta: a do ScanTailor ou a do Editor. "
            "Os números embaixo são os ângulos que cada uma achou.")
        self.combo_conta_do_endireitar.currentIndexChanged.connect(
            lambda _i: self._trocar_conta_do_endireitar())
        coluna.addWidget(self.combo_conta_do_endireitar)
        lista_estreita(self.combo_conta_do_endireitar)
        self.rotulo_angulos_medidos = frase_do_painel("")
        coluna.addWidget(self.rotulo_angulos_medidos)

        # Item 2.12 (regra da Fase 2, 13/10/2026: igual ao ScanTailor,
        # desligado de fabrica; controle minimo, a aparencia e do agente de
        # layout): desentortar a pagina curva perto da lombada, SO desta
        # pagina. Os textos moram em core/desentortar_scantailor.py.
        ds = desentortar_scantailor
        coluna.addWidget(risco_do_painel())
        coluna.addWidget(titulo_de_secao(ds.ROTULO_NA_TELA))
        self.combo_desentortar = QComboBox()
        self.combo_desentortar.setFocusPolicy(Qt.NoFocus)
        for modo in ds.MODOS:
            self.combo_desentortar.addItem(ds.ROTULOS_NA_TELA[modo], modo)
        self.combo_desentortar.setToolTip(ds.EXPLICACAO_NA_TELA)
        self.combo_desentortar.currentIndexChanged.connect(
            lambda _i: self._mudar_desentortar())
        coluna.addWidget(self.combo_desentortar)
        lista_estreita(self.combo_desentortar)
        coluna.addSpacing(6)
        conta_do_livro = endireitar_scantailor.jeito_do_livro(self.projeto)
        # D-093/D-094 (g6-retangulo, 09/10/2026: "quero a b e c juntas."): o que
        # o corte a mao DESTA pagina faz quando o angulo muda depois (a mesma
        # escolha existe no Automatico, para o livro, e nas Configuracoes)
        coluna.addWidget(titulo_de_secao("Quando o ângulo muda, o corte desta página"))
        self.combo_retangulo_da_pagina = QComboBox()
        for valor, nome in ((None, "segue o livro"), ("fica", "fica no mesmo lugar"),
                            ("acompanha", "acompanha o texto")):
            self.combo_retangulo_da_pagina.addItem(nome, valor)
        self.combo_retangulo_da_pagina.setToolTip(
            "Só vale se esta página tem o corte feito à mão. \"Fica no mesmo lugar\" é como o "
            "ScanTailor; \"acompanha o texto\" faz o retângulo crescer para o texto continuar "
            "dentro. \"Segue o livro\" usa a escolha do Automático (ou das Configurações).")
        self.combo_retangulo_da_pagina.currentIndexChanged.connect(
            lambda _i: self._mudar_retangulo_da_pagina())
        coluna.addWidget(self.combo_retangulo_da_pagina)
        lista_estreita(self.combo_retangulo_da_pagina)
        coluna.addSpacing(6)
        coluna.addWidget(self._parte_do_livro(
            ["Conta do endireitar: " + nome_da_conta(conta_do_livro),
             "Corte quando o ângulo muda: " + _nome_do_retangulo(self.projeto)], "endireitar"))

    def _montar_aba_marcar(self) -> None:
        """A aba de marcar a mao onde estao gravura, letra e papel.

        O detector acerta a maioria das paginas. Esta aba existe para as que ele
        erra: sem ela, nao havia como consertar.
        """
        from core.selecao import GRAVURA, LETRA, PAPEL, SOMAR, SUBTRAIR
        from ui.widgets.editor_selecao import (
            FERRAMENTA_ELIPSE,
            FERRAMENTA_LACO,
            FERRAMENTA_PINCEL,
            FERRAMENTA_POLIGONO,
            FERRAMENTA_RETANGULO,
            FERRAMENTA_COR,
            FERRAMENTA_VARINHA,
            NOMES_DAS_FERRAMENTAS,
            EditorSelecao,
        )

        pagina = QWidget()
        linha = QHBoxLayout(pagina)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(6)

        anterior = QPushButton("<")
        anterior.setFixedWidth(40)
        _ligar(anterior, lambda: self._navegar(-1))
        linha.addWidget(anterior)

        self.editor_selecao = EditorSelecao()
        self.editor_selecao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor_selecao.selecao_mudou.connect(self._selecao_mudou)
        self.editor_selecao.aviso.connect(self._mostrar_aviso_da_marcacao)
        # etapa 6: a roda troca de pagina sem zoom, e o "N%" da barra de baixo
        # acompanha o zoom da ferramenta de marcar (ela avisa "Zoom: N%")
        self.editor_selecao.installEventFilter(self)
        self.editor_selecao.aviso.connect(lambda *_: self._acertar_o_zoom_da_barra())
        linha.addWidget(self.editor_selecao, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(40)
        _ligar(proxima, lambda: self._navegar(1))
        linha.addWidget(proxima)
        self.paginas_de_imagem[ABA_MARCAR] = pagina

        # --- os botoes: no painel Propriedades ---
        #
        # Etapa 4 do layout (20/10/2026; rodada 9, 402 C: "Muda conforme a
        # ferramenta (como no Photoshop)"; protótipo da rodada 13,
        # `propsMarcarA`): as filas "Marcação:", "Foto:" e "Pedaço:", que
        # atravessavam a tela embaixo da página, viraram partes do painel
        # Propriedades das ferramentas de marcar, embaixo do "Marcar como".
        # SAO OS MESMOS BOTOES, ligados as mesmas acoes; so mudaram de lugar.
        # Embaixo da pagina fica uma pagina vazia (altura zero), como a de
        # Dividir, Cortar e Endireitar desde a etapa 3. Antes, na etapa 3:
        #
        #   Marcar como               painel Propriedades
        #   Filtro so neste pedaco    painel "Filtro da pagina"
        #   desfazer, procurar de     menu Marcar e menu Editar, ja na etapa 1
        #   novo, limpar tudo,
        #   deixar a folha em branco
        extra = NaoEspreme()
        fora = QVBoxLayout(extra)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(7)

        # O resumo do que esta marcado ("Marcado: 4 de letra e traço..."):
        # uma frase, logo embaixo do "Marcar como".
        self.aviso_marcacao = frase_do_painel("")
        fora.addWidget(self.aviso_marcacao)
        self.aviso_marcacao.setVisible(False)

        # Problema 2 do plano (redesenho do fluxo): a detecção automática não
        # roda mais sozinha - o Samuel pede quando quiser, aqui ou pelo menu
        # Marcar -> "Procurar de novo" (mesma ação). Item 1.2 (verificador,
        # 30/09, r06): cada parte diz a que se refere (o titulo), e cada botao
        # diz na dica o que copia. Fase 3b do plano: "usar em todas" e "daqui
        # em diante" (rodada 13, 806 B), como no corte, nas bordas e no filtro.
        fora.addWidget(risco_do_painel())
        fora.addWidget(titulo_de_secao("Marcação desta página"))
        _botao("detectar automaticamente", fora, self._detectar_de_novo).setToolTip(
            "Procura de novo a gravura, a letra e o papel desta página. "
            "O que você marcou à mão continua.")
        par = self._par_de_botoes(fora)
        _botao("usar em todas", par, self._marcacao_em_todas).setToolTip(
            "Copia a marcação desta página (gravura, letra, papel) para todas as páginas.")
        _botao("daqui em diante", par, self._marcacao_nas_proximas).setToolTip(
            "Copia a marcação desta página para esta e as páginas seguintes.")
        par.setStretch(0, 1)
        par.setStretch(1, 1)

        # Item 1.2 (decisao do Samuel, 30/09/2026): "Quero poder trocar
        # tambem so numa pagina (ex.: so a pagina da estatua do Opus Majus),
        # sem mudar o livro inteiro." Marcada = a gravura desta pagina e
        # procurada em retangulo (pega a foto inteira); desmarcada = seguindo
        # o contorno do desenho. Por cima do "Este livro tem fotos" da tela
        # "O que fazer". Mesmo desfazer (ConfigPagina.gravura_forma).
        fora.addWidget(risco_do_painel())
        fora.addWidget(titulo_de_secao("Foto"))
        self.caixa_tem_foto = QCheckBox("Esta página tem foto")
        # com quadrado tambem desmarcada (na janela de verdade saia so o
        # texto: verificador, 30/09, r06); ver ui/estilo.py
        estilo.estilizar(self.caixa_tem_foto, lambda: estilo_da_caixinha_com_quadrado(13))
        self.caixa_tem_foto.setCursor(Qt.PointingHandCursor)
        self.caixa_tem_foto.setFocusPolicy(Qt.NoFocus)     # o teclado continua da pagina
        self.caixa_tem_foto.setToolTip(
            "Procura a gravura desta página em retângulo, que pega a foto inteira. "
            "Desmarcada, segue o contorno do desenho. O que você marcou à mão continua.")
        self.caixa_tem_foto.toggled.connect(self._mudar_forma_da_pagina)
        fora.addWidget(self.caixa_tem_foto)
        par = self._par_de_botoes(fora)
        _botao("usar em todas", par, self._forma_em_todas).setToolTip(
            "Leva o \"Esta página tem foto\" desta página (marcado ou não) para todas as páginas.")
        _botao("daqui em diante", par, self._forma_nas_proximas).setToolTip(
            "Leva o \"Esta página tem foto\" desta página para esta e as páginas seguintes.")
        par.setStretch(0, 1)
        par.setStretch(1, 1)

        # Conferencia 13, S3 (Samuel, 05/10/2026): "(b) e (c) juntas - Mas
        # caso ele nao queira mudar, fica do jeito que esta." O pedaco com
        # outro filtro obedece inteiro ao filtro dele, inclusive o papel pego
        # junto em volta da figura (a faixa creme da Escola 7). Esta parte so
        # aparece quando a pagina tem um pedaco assim: (c) o botao encolhe o
        # retangulo ate a figura (core/ajustar_pedaco.py), numa acao do
        # desfazer; (b) a frase avisa quando o papel em volta e muito
        # (core.ajustar_pedaco.PAPEL_DEMAIS). Os dois so sugerem: nada muda
        # sozinho. Ver _avaliar_os_pedacos e _ajustar_pedaco_a_figura. No
        # painel (com rolagem) a frase pode quebrar linha; embaixo da pagina
        # nao podia (o defeito 1 do verificador, 05/10/2026, era isso).
        self.linha_pedaco = QWidget()
        linha_pedaco = QVBoxLayout(self.linha_pedaco)
        linha_pedaco.setContentsMargins(0, 0, 0, 0)
        linha_pedaco.setSpacing(7)
        linha_pedaco.addWidget(risco_do_painel())
        linha_pedaco.addWidget(titulo_de_secao("Pedaço"))
        self.botao_ajustar_pedaco = _botao(
            "Ajustar o pedaço à figura", linha_pedaco, self._ajustar_pedaco_a_figura)
        self.botao_ajustar_pedaco.setIcon(_icone_de_ajustar_o_pedaco())
        self.botao_ajustar_pedaco.setToolTip(DICA_DO_AJUSTE)
        self.aviso_pedaco = frase_do_painel("")
        linha_pedaco.addWidget(self.aviso_pedaco)
        self.linha_pedaco.setVisible(False)
        fora.addWidget(self.linha_pedaco)

        # Item 2.18 (rodadas 4 e 5 do "Para revisar"; P11 (a) e P11b do
        # Samuel, 05/10/2026). CONTROLE MINIMO, provisorio ate o layout
        # (relatorios/fase2-novas/ONDE-PAREI.md): mostrar as areas achadas
        # delineadas (nas paginas do "Para revisar" ja vem ligado) e, para a
        # area escolhida com a ferramenta "Mover e mudar o tamanho da area"
        # (tecla A), apagar, pintar de branco, copiar e colar.
        # Juncao de 23/10/2026: no ramo das ferramentas era a linha "Área:"
        # embaixo da pagina, na aba Marcar; no layout (etapas 4 a 7) tudo da
        # Marcar mora no painel Propriedades e a fila embaixo da pagina fica
        # vazia (tests/test_ajustar_pedaco_na_aba_marcar.py). Entao a "Área"
        # virou uma parte do painel, com os mesmos controles e nomes. O lugar
        # final e do agente de layout.
        fora.addWidget(risco_do_painel())
        fora.addWidget(titulo_de_secao("Área"))
        self.caixa_mostrar_achadas = QCheckBox("Mostrar as áreas achadas")
        estilo.estilizar(self.caixa_mostrar_achadas, lambda: estilo_da_caixinha_com_quadrado(15))
        self.caixa_mostrar_achadas.setToolTip(
            "Desenha em laranja o contorno das áreas que o programa achou sozinho. "
            "Nas páginas do \"Para revisar\" elas já aparecem.")
        self.caixa_mostrar_achadas.toggled.connect(
            lambda marcada: self._mostrar_as_achadas(bool(marcada)))
        fora.addWidget(self.caixa_mostrar_achadas)
        par = self._par_de_botoes(fora)
        self.botao_apagar_area = _botao("apagar a área", par,
                                        lambda: self._mexer_na_area("apagar"))
        self.botao_branco_area = _botao("pintar de branco", par,
                                        lambda: self._mexer_na_area("branco"))
        par = self._par_de_botoes(fora)
        self.botao_copiar_area = _botao("copiar", par,
                                        lambda: self._mexer_na_area("copiar"))
        self.botao_colar_area = _botao("colar", par,
                                       lambda: self._mexer_na_area("colar"))
        for botao in (self.botao_apagar_area, self.botao_branco_area, self.botao_copiar_area):
            botao.setToolTip("Escolha a área antes, com a ferramenta \"Mover e mudar o "
                             "tamanho da área\" (tecla A).")

        self.paineis.propriedades.definir_extra_de_marcar(extra)
        # embaixo da pagina, uma pagina vazia: a pilha precisa de uma por aba
        self.linhas_de_botoes[ABA_MARCAR] = QWidget()

    # --- acoes da aba de marcar -------------------------------------------

    def _escolher_tipo_de_marcacao(self, tipo: str) -> None:
        """Quem mostra o estado agora e o painel "Marcar como"."""
        self._ao_editor("definir_tipo", tipo)
        self.paineis.marcar_como.tipo = tipo
        self.paineis.marcar_como._montar()

    def _mostrar_as_achadas(self, mostrar: bool) -> None:
        """Item 2.18: delinear as areas achadas pela maquina (a caixinha), ou
        sempre nas paginas do "Para revisar"."""
        pagina = self._pagina_marcada()
        self.editor_selecao.definir_mostrar_achadas(
            mostrar or bool(pagina is not None and pagina.precisa_revisao))

    @protegido
    def _mexer_na_area(self, acao: str) -> None:
        """Item 2.18: apagar, pintar de branco, copiar ou colar a area escolhida
        (a marcacao muda pelo mesmo caminho de sempre: _selecao_mudou)."""
        editor = self.editor_selecao
        feito = {"apagar": editor.apagar_area_escolhida,
                 "branco": editor.pintar_de_branco_area_escolhida,
                 "copiar": editor.copiar_area_escolhida,
                 "colar": editor.colar}[acao]()
        if not feito:
            self._mostrar_aviso_da_marcacao(
                "Nada copiado ainda." if acao == "colar" else
                "Escolha a área antes: ferramenta \"Mover e mudar o tamanho da área\" (tecla A), "
                "e clique nela.")

    def _escolher_operacao(self, operacao: str) -> None:
        """Somar ou tirar. Quem mostra o estado agora e a barra de opcoes."""
        self._ao_editor("definir_operacao", operacao)
        self.barra_opcoes._escolher_modo(operacao, avisar=False)

    def _escolher_ferramenta(self, ferramenta: str) -> None:
        """Mantido pelo nome antigo; passa pelo ponto unico de troca."""
        self.escolher_ferramenta(ferramenta)

    def _escolher_filtro_da_regiao(self, filtro: str) -> None:
        """Que filtro vale so no que for marcado daqui em diante.

        Quem mostra o estado agora e o painel "Filtro da pagina".
        """
        self._ao_editor("definir_filtro_da_regiao", filtro)

    def _mostrar_aviso_da_marcacao(self, texto: str) -> None:
        """Escreve o resumo do que está marcado (ou o aviso da última ação de
        marcar) no painel Propriedades, embaixo do "Marcar como". Sem texto, a
        frase some (não deixa um buraco no painel)."""
        if hasattr(self, "aviso_marcacao"):
            self.aviso_marcacao.setText(texto)
            self.aviso_marcacao.setVisible(bool(texto))

    def _pagina_marcada(self):
        """A pagina que a aba de marcar esta editando, ou None."""
        if self.projeto is None or not self.projeto.paginas:
            return None
        if not 0 <= self.indice_pagina < len(self.projeto.paginas):
            return None
        return self.projeto.paginas[self.indice_pagina]

    def _selecao_mudou(self) -> None:
        """Grava a marcacao na pagina e joga fora a previa, que ficou velha."""
        pagina = self._pagina_marcada()
        if pagina is None:
            return
        # 13/10/2026: o que a máquina marcou na cópia do editor é o que ele
        # carregou (_atualizar_marcacao). Se era a marcação provisória (a da
        # prévia) e, por trás, a página já tinha ganhado a do tamanho do PDF,
        # gravar a cópia do editor põe de volta as áreas provisórias: a
        # página volta a dizer "provisória", e a busca por trás (ou o PDF)
        # troca de novo - com tudo o que a pessoa marcou à mão por cima.
        pagina.guardar_selecao(self.editor_selecao.selecao,
                               provisoria=getattr(self, "_editor_com_a_provisoria", None))
        # etapa 3 da obra: a marcacao feita aqui e "mexida a mao" (core/etapas)
        if any(r.origem == "mao" for r in self.editor_selecao.selecao.regioes):
            etapas_core.marcar_mexida_a_mao(pagina, etapas_core.MARCAR)
        self._mostrar_aviso_da_marcacao(
            self.editor_selecao.selecao.resumo_em_portugues())
        self._avaliar_os_pedacos(pagina)        # conferencia 13, S3
        if self.previas is not None:
            self.previas.invalidar(self.indice_pagina)
        # A marcacao nao passa por `atualizar` - ela nao mexe na tira nem no
        # contador. Mas mexe no TRABALHO, e por isso avisa daqui.
        self.trabalho_mudou.emit()

    def _desfazer_marcacao(self) -> None:
        self.editor_selecao.desfazer()
        self._selecao_mudou()

    def _limpar_marcacao(self) -> None:
        from core.selecao import Selecao

        if self._pagina_marcada() is None:
            return
        self.editor_selecao.definir_selecao(Selecao())
        self._selecao_mudou()
        self._mostrar_aviso_da_marcacao(
            "Tirei tudo. O filtro volta a tratar a folha inteira igual.")

    def _folha_em_branco(self) -> None:
        """Manda a folha inteira sair branca, seja capa ou pagina escrita.

        E o mesmo caminho da marcacao a mao: marcar a folha inteira como PAPEL.
        O filtro entende folha inteira marcada como papel como "quero a folha em
        branco", e nao como "aqui e fundo" - ver FOLHA_INTEIRA_EM_BRANCO. Assim
        nao ha um segundo jeito de dizer a mesma coisa dentro do programa, e o
        desfazer funciona igual ao das outras marcacoes.
        """
        from core.selecao import MAO, PAPEL, RETANGULO, Regiao, Selecao

        if self._pagina_marcada() is None:
            return
        folha = Selecao()
        folha.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO,
                                 pontos=[(0.0, 0.0), (1.0, 1.0)], origem=MAO))
        self.editor_selecao.definir_selecao(folha)
        self._selecao_mudou()
        self._mostrar_aviso_da_marcacao(
            "Esta folha vai sair em branco. Para voltar atrás, desfazer.")

    def _detectar_de_novo(self) -> None:
        """Roda a deteccao outra vez, SEM apagar o que foi feito a mao.

        E o ponto de as tres formas de marcar viverem na mesma lista: da para
        pedir a maquina de novo sem perder a correcao da pessoa.

        Item 1.2 (30/09/2026): ate aqui este botao chamava o detector ANTIGO,
        na imagem da previa ja filtrada - o que o Kaique via aqui nao era o
        que ia para o PDF. Agora ele so tira o que a maquina marcou e pede a
        previa de novo: quem procura e core/pipeline.garantir_selecao, o
        MESMO caminho da previa e do PDF (o detector do ScanTailor, com as
        opcoes do livro e da pagina, na pagina sem filtro, com o DPI certo).
        A marcacao a mao volta por cima da nova (ver garantir_selecao). O
        resultado aparece quando a previa chega (_atualizar_marcacao).
        Arriscado: voltar a chamar detectar() daqui.
        """
        from core.pipeline import REFAZER_A_GRAVURA

        pagina = self._pagina_marcada()
        if pagina is None:
            return

        self.editor_selecao.limpar_o_que_a_maquina_marcou()
        pagina.guardar_selecao(self.editor_selecao.selecao)
        # com marcacao a mao sobrando, a assinatura que nao bate com nenhuma
        # faz garantir_selecao procurar de novo (sem ela, a selecao nao vazia
        # seria usada como esta)
        pagina.gravura_feita_com = REFAZER_A_GRAVURA
        self.editor_selecao.update()
        self._mostrar_aviso_da_marcacao(
            "Procurando de novo, com as opções deste livro. O que você marcou à mão continua.")
        self.trabalho_mudou.emit()
        if self.previas is not None:
            self.previas.invalidar(self.indice_pagina)
            self._atualizar_previa()

    # --- item 1.2: "Esta pagina tem foto" ---------------------------------

    def _forma_do_livro(self) -> str:
        """A forma do contorno da gravura do livro (Projeto.gravura_forma)."""
        return getattr(self.projeto, "gravura_forma", "livre") if self.projeto else "livre"

    def _preparar_para_trocar_forma(self, paginas, valor) -> None:
        """Pagina marcada antes do campo gravura_feita_com existir (assinatura
        vazia) nao seria refeita sozinha: a que vai MESMO mudar de forma, e tem
        alguma marcacao da maquina, ganha a assinatura "refazer". Fora do
        desfazer de proposito: depois de refeita, a assinatura e a de verdade,
        e o desfazer (que so devolve a forma) refaz com a forma de antes."""
        from core.pipeline import REFAZER_A_GRAVURA, escolha_da_gravura
        from core.selecao import MAO

        assert self.projeto is not None
        for pagina in paginas:
            if pagina.gravura_feita_com or not pagina.selecao:
                continue
            if not any(isinstance(r, dict) and r.get("origem") != MAO for r in pagina.selecao):
                continue
            antes = escolha_da_gravura(self.projeto, pagina)[1].forma
            guardado = pagina.gravura_forma
            pagina.gravura_forma = valor
            depois = escolha_da_gravura(self.projeto, pagina)[1].forma
            pagina.gravura_forma = guardado
            if antes != depois:
                pagina.gravura_feita_com = REFAZER_A_GRAVURA

    def _valor_da_forma(self, tem_foto: bool):
        """O que vai em ConfigPagina.gravura_forma: None quando a pagina fica
        igual ao livro (assim, mudar o livro depois muda ela tambem)."""
        forma = "retangular" if tem_foto else "livre"
        return None if forma == self._forma_do_livro() else forma

    @protegido
    def _mudar_forma_da_pagina(self, tem_foto: bool) -> None:
        """A caixinha "Esta pagina tem foto": troca a forma so desta pagina."""
        pagina = self._pagina_marcada()
        if pagina is None or not self._pronta():
            return
        valor = self._valor_da_forma(tem_foto)
        if valor == pagina.gravura_forma:
            return
        self._preparar_para_trocar_forma([pagina], valor)
        self._registrar(
            "mudar_forma_da_gravura", "pagina", [self.indice_pagina],
            {"gravura_forma": valor},
            f"Página {self.indice_pagina + 1}: "
            + ("tem foto (gravura em retângulo)" if tem_foto else "gravura seguindo o desenho"),
        )
        self._mostrar_aviso_da_marcacao(
            "Procurando a gravura de novo nesta página. O que você marcou à mão continua.")

    @protegido
    def _forma_em_todas(self) -> None:
        self._forma_nas(0, "em todas as páginas")

    @protegido
    def _forma_nas_proximas(self) -> None:
        self._forma_nas(self.indice_pagina, "desta página em diante")

    def _forma_nas(self, desde: int, onde: str) -> None:
        """Leva a escolha "Esta pagina tem foto" da pagina atual para as
        paginas a partir de `desde` (0 = todas), numa acao so (um desfazer)."""
        pagina = self._pagina_marcada()
        if pagina is None or self.projeto is None:
            return
        valor = pagina.gravura_forma
        alvo = [p for p in self.projeto.paginas if p.indice >= desde]
        self._preparar_para_trocar_forma(alvo, valor)
        tem_foto = self.caixa_tem_foto.isChecked()
        self._registrar(
            "aplicar_em_todas", "pagina", [p.indice for p in alvo],
            {"gravura_forma": valor},
            ("Tem foto" if tem_foto else "Gravura seguindo o desenho") + f" {onde}",
        )

    def _mostrar_forma_da_pagina(self, pagina) -> None:
        """Acerta a caixinha "Esta pagina tem foto" pela pagina, sem disparar
        a troca. Livro em "nao procurar": a caixinha fica apagada."""
        from core.pipeline import escolha_da_gravura

        if not hasattr(self, "caixa_tem_foto") or self.projeto is None:
            return
        desligado = self._forma_do_livro() == "desligada"
        self.caixa_tem_foto.blockSignals(True)
        self.caixa_tem_foto.setChecked(
            not desligado and escolha_da_gravura(self.projeto, pagina)[1].forma == "retangular")
        self.caixa_tem_foto.blockSignals(False)
        self.caixa_tem_foto.setEnabled(not desligado)
        self.caixa_tem_foto.setToolTip(
            "O livro está em \"não procurar\" gravuras e fotos (painel Automático, "
            "etapa Gravuras e fotos)."
            if desligado else
            "Procura a gravura desta página em retângulo, que pega a foto inteira. "
            "Desmarcada, segue o contorno do desenho. O que você marcou à mão continua.")

    # Fase 3b do plano "corrigir bugs do teste do Boécio": faltava aqui o
    # "usar em todas / só nesta" que já existia para corte
    # (`_corte_em_todas`), recorte/bordas (`_recorte_em_todas`) e filtro
    # (`_filtro_em_todas`/`_filtro_nas_proximas`). O "resultado da detecção
    # automática" copiado é a MARCAÇÃO já computada nesta página (detecção +
    # qualquer correção manual, `ConfigPagina.selecao`) - mesmo padrão dos
    # irmãos acima: copia um valor já decidido para as outras páginas, não
    # roda `detectar()` de novo em cada uma (isso exigiria rasterizar e
    # processar o livro inteiro de forma síncrona na interface - a regra do
    # projeto "nenhum processamento pesado trava a interface" não permite
    # isso sem uma tarefa em segundo plano própria, fora do escopo desta
    # entrega; rodar a detecção de verdade página por página continua sendo
    # o botão "detectar automaticamente" de cima).
    @protegido
    def _marcacao_em_todas(self) -> None:
        import copy

        pagina = self._pagina_marcada()
        if pagina is None or not pagina.selecao:
            # Uma marcacao VAZIA copiada para todas apagaria sem querer o
            # trabalho de outras paginas - mesmo cuidado de `_limpar_marcacao`
            # so valer na pagina atual, nunca em lote.
            self._mostrar_aviso_da_marcacao(
                "Marque ou detecte algo nesta página antes de usar em todas.")
            return
        assert self.projeto is not None
        indices = [p.indice for p in self.projeto.paginas]
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"selecao": copy.deepcopy(pagina.selecao)},
            f"Marcação da página {self.indice_pagina + 1} em todas as {len(indices)} páginas",
        )

    @protegido
    def _marcacao_nas_proximas(self) -> None:
        import copy

        pagina = self._pagina_marcada()
        if pagina is None or not pagina.selecao:
            self._mostrar_aviso_da_marcacao(
                "Marque ou detecte algo nesta página antes de aplicar nas próximas.")
            return
        assert self.projeto is not None
        indices = [p.indice for p in self.projeto.paginas if p.indice >= self.indice_pagina]
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"selecao": copy.deepcopy(pagina.selecao)},
            f"Marcação da página {self.indice_pagina + 1} em diante ({len(indices)} páginas)",
        )

    def _montar_aba_filtro(self) -> None:
        pagina = QWidget()
        camadas = QVBoxLayout(pagina)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(6)

        # Item 1.1: em livro com camadas, cinco cartoes (o quinto e o "Tirar
        # o fundo"); nos outros, os quatro de sempre.
        assert self.projeto is not None
        filtros = filtros_do_livro(self.projeto)
        quantos = {4: "quatro", 5: "cinco"}.get(len(filtros), str(len(filtros)))
        explicacao = QLabel(f"A mesma página nos {quantos} filtros - clique no que preferir")
        explicacao.setObjectName("fraco")
        camadas.addWidget(explicacao)

        linha = QHBoxLayout()
        linha.setSpacing(6)
        anterior = QPushButton("<")
        anterior.setFixedWidth(40)
        _ligar(anterior, lambda: self._navegar(-1))
        linha.addWidget(anterior)

        for chave, nome, explica in CARTOES:
            if chave not in filtros:
                continue
            cartao = CartaoFiltro(chave, nome, explica)
            cartao.escolhido.connect(self._escolher_filtro)
            cartao.ampliar_pedido.connect(self._ampliar_com_filtro)
            self.cartoes[chave] = cartao
            linha.addWidget(cartao, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(40)
        _ligar(proxima, lambda: self._navegar(1))
        linha.addWidget(proxima)
        camadas.addLayout(linha, 1)

        self.paginas_de_imagem[ABA_FILTRO] = pagina

        # Etapa 4 do layout (20/10/2026): os controles que eram a fila de
        # botoes embaixo da pagina (o bloco AJUSTE, o "Algoritmo", o "Limpar a
        # sujeira", o "Só as letras", o "Aplicar em" e o "apagar página")
        # vao para o painel "Filtro da página" decidido (rodada 9, 403 B: a
        # fila dos filtros e partes que abrem e fecham; rodada 10, 502 B: as
        # escolhas em menu com amostra). SAO AS MESMAS PECAS, com os mesmos
        # nomes e as mesmas acoes: so mudaram de lugar e de desenho. Quem as
        # arruma no painel e PainelFiltroDaPagina.montar (ui/widgets/paineis.py).
        # Embaixo da pagina fica uma pagina vazia (altura zero).

        # --- Ajuste: o deslizante do filtro da vez (o Original nao tem) ---
        corpo_ajuste = Bloco()
        coluna_ajuste = QVBoxLayout(corpo_ajuste)
        coluna_ajuste.setContentsMargins(0, 0, 0, 0)
        coluna_ajuste.setSpacing(4)
        self.bloco_ajuste = Bloco()
        dentro = QVBoxLayout(self.bloco_ajuste)
        dentro.setContentsMargins(0, 0, 0, 0)
        dentro.setSpacing(2)
        self.medidor = Medidor("Força do preto", "mais fraco", "mais escuro", em_duas_linhas=True)
        self.medidor.arrastando.connect(self._medidor_arrastando)
        self.medidor.soltou.connect(self._medidor_soltou)
        self.medidor.barra.sliderPressed.connect(self._medidor_pegou)
        dentro.addWidget(self.medidor)
        coluna_ajuste.addWidget(self.bloco_ajuste)
        self.frase_sem_ajuste = frase_do_painel("O Original não tem ajuste.")
        coluna_ajuste.addWidget(self.frase_sem_ajuste)

        # --- Mais ajustes: o jeito do preto e branco (Problema 5 do plano) ---
        # So aparece com o Preto e branco escolhido (ver _configurar_medidor).
        # "Automático" é o padrão - o programa decide pela espessura do traço
        # desta página. Na tela o nome e "Jeito do preto e branco" (rodada 9:
        # no lugar do "Algoritmo: Sauvola/Otsu/Wolf"); a lista e a mesma.
        corpo_mais = Bloco()
        coluna_mais = QVBoxLayout(corpo_mais)
        coluna_mais.setContentsMargins(0, 0, 0, 0)
        coluna_mais.setSpacing(4)
        self.rotulo_algoritmo_pb = QLabel("Jeito do preto e branco")
        self.rotulo_algoritmo_pb.setObjectName("rotuloDoPainel")
        coluna_mais.addWidget(self.rotulo_algoritmo_pb)
        linha_algoritmo = QHBoxLayout()
        coluna_mais.addLayout(linha_algoritmo)
        self.seletor_algoritmo_pb = QComboBox()
        self.seletor_algoritmo_pb.addItem("Automático", "auto")
        for chave in ALGORITMOS_PB:
            self.seletor_algoritmo_pb.addItem(NOMES_DOS_ALGORITMOS_PB[chave], chave)
        # Item 2.8 (Samuel P8, 05/10/2026: "Trazer os dez do ScanTailor como
        # opções a mais"): os dez do ScanTailor, depois dos três de sempre.
        # Controle mínimo; a aparência é do agente de layout (listado em
        # layout/Botoes e funcoes para o layout.md). Seguro mudar: os textos
        # (moram em core/preto_e_branco_scantailor.py).
        self.seletor_algoritmo_pb.insertSeparator(self.seletor_algoritmo_pb.count())
        for chave in preto_e_branco_scantailor.CODIGOS:
            self.seletor_algoritmo_pb.addItem(preto_e_branco_scantailor.NOMES_NA_TELA[chave], chave)
        self.seletor_algoritmo_pb.setToolTip(preto_e_branco_scantailor.EXPLICACAO_NA_TELA)
        self.seletor_algoritmo_pb.currentIndexChanged.connect(self._mudar_algoritmo_pb)
        linha_algoritmo.addWidget(self.seletor_algoritmo_pb, 1)
        lista_estreita(self.seletor_algoritmo_pb)

        # --- Limpar a sujeira (decisão do Samuel, 06/10/2026, P7) ---
        # Desligado, o nosso, e o do ScanTailor em pouco/normal/muito. Só
        # aparece com o Preto e branco (ver _configurar_medidor). Na lista com
        # amostra da rodada 10 (502 B). Seguro mudar: os textos (moram em
        # core/pontinhos_scantailor.py).
        corpo_limpar = Bloco()
        coluna_limpar = QVBoxLayout(corpo_limpar)
        coluna_limpar.setContentsMargins(0, 0, 0, 0)
        coluna_limpar.setSpacing(5)
        self.rotulo_pontinhos = frase_do_painel(pontinhos.EXPLICACAO_NA_TELA.split("\n")[0])
        coluna_limpar.addWidget(self.rotulo_pontinhos)
        self.seletor_pontinhos = ListaComAmostra(desenho_da_limpeza)
        for chave in pontinhos.ESCOLHAS:
            self.seletor_pontinhos.addItem(pontinhos.NOMES_NA_TELA[chave], chave)
            self.seletor_pontinhos.definir_detalhes(
                chave, FRASES_DA_LIMPEZA.get(chave, ""), de_fabrica=(chave == pontinhos.PADRAO))
        self.seletor_pontinhos.setToolTip(pontinhos.EXPLICACAO_NA_TELA)
        self.seletor_pontinhos.currentIndexChanged.connect(self._mudar_pontinhos)
        coluna_limpar.addWidget(self.seletor_pontinhos)

        # Na junção com o ramo da Fase 2 (22/10/2026), as caixinhas dos itens 2.9 e
        # 2.11 foram da aba Filtro antiga para a parte "Mais ajustes" do painel
        # Filtro da página (o lugar decidido para elas no desenho das rodadas 10 e 11).
        #
        # Item 2.9 (Samuel P9 (a), 05/10/2026): "Letra clara em fundo escuro",
        # caixinha SÓ desta página, marcada à mão (core/claro_no_escuro.py).
        # Vale nos filtros que mexem na imagem (o bloco AJUSTE só aparece neles).
        # Controle mínimo; a aparência é do agente de layout (listado em
        # layout/Botoes e funcoes para o layout.md). Seguro mudar: os textos
        # (moram em core/claro_no_escuro.py).
        self.caixa_claro_no_escuro = QCheckBox(claro_no_escuro.ROTULO_NA_TELA)
        estilo.estilizar(self.caixa_claro_no_escuro, lambda: estilo_da_caixinha_com_quadrado(15))
        self.caixa_claro_no_escuro.setToolTip(claro_no_escuro.EXPLICACAO_NA_TELA)
        self.caixa_claro_no_escuro.toggled.connect(self._mudar_claro_no_escuro)
        coluna_mais.addWidget(self.caixa_claro_no_escuro)

        # Item 2.11 (Samuel P10 (a), 05/10/2026): "Letras com a cor delas" (só no
        # Preto e branco) e "Reduzir cores", SÓ desta página (core/cores_scantailor.py).
        # Controle mínimo; aparência do agente de layout. Seguro mudar: os textos.
        linha_cores = QVBoxLayout()
        linha_cores.setSpacing(4)
        self.caixa_letras_com_a_cor = QCheckBox(cores_scantailor.ROTULO_LETRAS)
        self.caixa_reduzir_cores = QCheckBox(cores_scantailor.ROTULO_REDUZIR)
        for caixa, dica, campo in ((self.caixa_letras_com_a_cor, cores_scantailor.EXPLICACAO_LETRAS,
                                    "letras_com_a_cor"),
                                   (self.caixa_reduzir_cores, cores_scantailor.EXPLICACAO_REDUZIR,
                                    "reduzir_cores")):
            estilo.estilizar(caixa, lambda: estilo_da_caixinha_com_quadrado(15))
            caixa.setToolTip(dica)
            caixa.toggled.connect(lambda marcada, c=campo: self._mudar_cores(c, marcada))
            linha_cores.addWidget(caixa)
        coluna_mais.addLayout(linha_cores)

        # Item 2.17 (regra da Fase 2: igual ao ScanTailor, desligado de
        # fabrica): igualar a luz, suavizar as letras (so no Preto e branco) e
        # tirar o chuvisco, SO desta pagina. CONTROLE MINIMO, provisorio: a
        # aparencia e do agente de layout (relatorios/fase2-novas/ONDE-PAREI.md).
        # Juncao de 23/10/2026: no ramo era uma linha do bloco AJUSTE da aba
        # Filtro antiga; no layout ela vai para "Mais ajustes", como as
        # caixinhas dos itens 2.9 e 2.11 foram em 22/10.
        # Os textos moram em core/luz_scantailor.py.
        linha_luz = QHBoxLayout()
        self.caixa_luz_igualar = QCheckBox(luz_scantailor.ROTULO_IGUALAR)
        self.caixa_luz_igualar.setToolTip(luz_scantailor.EXPLICACAO_IGUALAR)
        self.caixa_luz_suavizar = QCheckBox(luz_scantailor.ROTULO_SUAVIZAR)
        self.caixa_luz_suavizar.setToolTip(luz_scantailor.EXPLICACAO_SUAVIZAR)
        for caixa, campo in ((self.caixa_luz_igualar, "luz_igualar"),
                             (self.caixa_luz_suavizar, "luz_suavizar")):
            estilo.estilizar(caixa, lambda: estilo_da_caixinha_com_quadrado(15))
            caixa.toggled.connect(lambda marcada, c=campo: self._mudar_luz(c, bool(marcada)))
            linha_luz.addWidget(caixa)
        self.rotulo_luz_chuvisco = QLabel(luz_scantailor.ROTULO_CHUVISCO + ":")
        self.rotulo_luz_chuvisco.setToolTip(luz_scantailor.EXPLICACAO_CHUVISCO)
        linha_luz.addWidget(self.rotulo_luz_chuvisco)
        self.seletor_luz_chuvisco = QSpinBox()
        self.seletor_luz_chuvisco.setRange(0, 100)
        self.seletor_luz_chuvisco.setSingleStep(10)
        self.seletor_luz_chuvisco.setToolTip(luz_scantailor.EXPLICACAO_CHUVISCO)
        self.seletor_luz_chuvisco.setKeyboardTracking(False)
        self.seletor_luz_chuvisco.valueChanged.connect(
            lambda valor: self._mudar_luz("luz_chuvisco", int(valor)))
        linha_luz.addWidget(self.seletor_luz_chuvisco)
        linha_luz.addStretch()
        coluna_mais.addLayout(linha_luz)
        # os avisos das opcoes de luz (Samuel, 22/10/2026)
        self.aviso_luz = QLabel("")
        self.aviso_luz.setObjectName("fraco")
        self.aviso_luz.setWordWrap(True)
        self.aviso_luz.setVisible(False)
        coluna_mais.addWidget(self.aviso_luz)

        # --- Só as letras (modo Misto, 05/10/2026), desta página ---
        # Só com o Preto e branco escolhido (ver _configurar_medidor). No
        # painel, com a lista com amostra (rodada 10, 502 B) no lugar dos três
        # botões, que continuam existindo, escondidos (EscolhasDoMisto).
        self.escolhas_misto = EscolhasDoMisto(com_amostra=True)
        self.escolhas_misto.so_as_letras_mudou.connect(self._mudar_so_as_letras)
        self.escolhas_misto.fora_do_texto_escolhido.connect(self._mudar_fora_do_texto)
        self.escolhas_misto.papel_escolhido.connect(self._mudar_papel_da_gravura)
        self.escolhas_misto.letras_escolhidas.connect(self._mudar_letras_na_moldura)

        # --- Aplicar em (o pé do painel, sempre à vista) ---
        # AJUSTE (o que muda a página) e APLICAR EM (onde a mudança vale) sao
        # coisas diferentes: misturar as duas na mesma linha confundia.
        aplicar = Bloco()
        coluna_aplicar = QVBoxLayout(aplicar)
        coluna_aplicar.setContentsMargins(0, 0, 0, 0)
        coluna_aplicar.setSpacing(5)
        coluna_aplicar.addWidget(titulo_de_secao("Aplicar em"))
        linha_botoes = QHBoxLayout()
        linha_botoes.setSpacing(6)
        _botao("só nesta", linha_botoes, self._marcar_revisada, "acaoPrimaria")
        _botao("todas", linha_botoes, self._filtro_em_todas)
        _botao("daqui em diante", linha_botoes, self._filtro_nas_proximas)
        coluna_aplicar.addLayout(linha_botoes)

        # Os dois botoes de "Esta pagina" (etapa 2 da obra, 26/10/2026; eram
        # so o "apagar página"): "deixar em branco" (a pagina fica, branca) e
        # "tirar do livro" (sai de vez). Destrutivos: ficam longe dos outros,
        # no fim do corpo do painel, depois de um risco (o painel arruma). Os
        # mesmos do alto do Propriedades (_montar_os_botoes_da_pagina).
        pagina_toda = Bloco()
        par_da_pagina = QHBoxLayout(pagina_toda)
        par_da_pagina.setContentsMargins(0, 0, 0, 0)
        par_da_pagina.setSpacing(6)
        self.botao_em_branco_do_filtro = _botao(
            "deixar em branco", par_da_pagina, self.deixar_em_branco_ou_voltar)
        self.botao_apagar = QPushButton("tirar do livro")
        self.botao_apagar.setObjectName("destrutivo")
        _ligar(self.botao_apagar, self.apagar_pagina)
        par_da_pagina.addWidget(self.botao_apagar)

        self.paineis.filtro_da_pagina.montar(
            [(chave, nome, TECLAS_DOS_FILTROS.get(chave, ""))
             for chave, nome, _explica in CARTOES if chave in filtros],
            {"ajuste": corpo_ajuste, "letras": self.escolhas_misto, "limpar": corpo_limpar,
             "mais": corpo_mais, "aplicar": aplicar, "apagar": pagina_toda})
        # a amostra de cada cartao grande vai tambem para a fila do painel
        for cartao in self.cartoes.values():
            cartao.amostra_mudou.connect(self.paineis.filtro_da_pagina.definir_amostra)

        # embaixo da pagina, uma pagina vazia: a pilha precisa de uma por aba
        self.linhas_de_botoes[ABA_FILTRO] = QWidget()

    # ------------------------------------------------------------------
    # carga
    # ------------------------------------------------------------------

    def carregar(self, projeto: Projeto, acoes: HistoricoAcoes,
                 previas: GerenciadorPrevias) -> None:
        self._carregando = True
        try:
            self.projeto = projeto
            self.acoes = acoes
            self.previas = previas
            self.previas.pronta.connect(self._previa_chegou)
            self.previas.cartoes_prontos.connect(self._cartoes_prontos)
            # item 2.12 (resposta P6): a medida do desentortar por tras
            self.previas.desentortar_medido.connect(self._desentortar_medido)
            self._cartoes_cache = {}
            self._cartoes_cache_chave = None
            self._tira_assinatura = None

            self.indice_folha = 0
            self.indice_pagina = 0
            # etapa 6: todo livro abre numa pagina por vez (D-007; o lado a
            # lado e opcao, nao padrao, D-006) e sem o "antes / depois"
            self.mostrar = UMA
            self.comparando = False
            self.lado_a_lado.limpar()
            self.mostrar_mudou.emit(UMA)

            self._limpar_abas()

            # D-001 (Samuel, 25/09/2026: "Estrutura: Photoshop puro, sem abas.
            # Uma única tela com todas as ferramentas."), construída de verdade
            # na etapa 2 da obra de 26/10/2026: TODAS as ferramentas nascem em
            # todo livro, com qualquer combinação de caixinhas, inclusive
            # nenhuma. Até aqui valia a regra de julho (commits d9fae8c,
            # f15e469, d83bb03, do tempo das "abas por etapa"): cada ferramenta
            # só existia se a caixinha dela estivesse marcada na tela "O que
            # fazer". A caixinha agora só diz o que o automático faz; a
            # ferramenta está sempre à mão. Arriscado: voltar a montar só
            # algumas (tests/test_decisoes_tela.py reprova).
            self._montar_aba_corte()
            self._montar_aba_bordas()
            self._montar_aba_angulo()
            self._montar_aba_mover()            # etapa 5 da obra (D-008)
            self._montar_aba_marcar()
            self._montar_aba_filtro()
            self._abas_ativas.extend(ORDEM_DAS_FERRAMENTAS)
            # a ferramenta de marcar que fica na mão ao abrir (ver
            # _ferramenta_de_partida); a trilha acende pela aba da vez
            ferramenta = self._ferramenta_de_partida(projeto)
            self.barra_opcoes.definir_ferramenta(ferramenta)
            self.editor_selecao.definir_ferramenta(ferramenta)

            for aba in self._abas_ativas:
                self.barra_abas.addTab(TITULOS[aba])
                self.area_imagem.addWidget(self.paginas_de_imagem[aba])
                if aba in self.propriedades_das_abas:
                    # etapa 3 do layout: os botoes desta ferramenta moram no
                    # painel Propriedades; embaixo da pagina fica uma pagina
                    # vazia (a pilha precisa de uma por aba, na mesma ordem)
                    self.barra_botoes.addWidget(QWidget())
                    self.paineis.propriedades.definir_conteudo(
                        aba, self.propriedades_das_abas[aba])
                else:
                    self.barra_botoes.addWidget(self.linhas_de_botoes[aba])
                # o botao laranja da sugestao e o da faixa, em todas
                self.botoes_de_sugestao[aba] = self.botao_sugestao
                self.botoes_de_sugestao_2[aba] = self.botao_sugestao_2
                self.botoes_de_sugestao_3[aba] = self.botao_sugestao_3
                self._botoes_do_aviso_sem_foco(aba)

            # A ferramenta da vez ao abrir (_aba_de_partida). As três pilhas
            # andam juntas: com _carregando, o _trocou_de_aba não as acerta.
            partida = self._abas_ativas.index(self._aba_de_partida(projeto))
            self.barra_abas.setCurrentIndex(partida)
            self.area_imagem.setCurrentIndex(partida)
            self.barra_botoes.setCurrentIndex(partida)
            self._encolher_a_barra_de_botoes()
            self._esconder_as_setas_dos_lados()
        finally:
            self._carregando = False
        self._acertar_a_trilha()

        self._montar_tira()
        self._aquecer_o_leitor_se_precisar()
        self.atualizar()

    @staticmethod
    def _aba_de_partida(projeto: Projeto) -> str:
        """Em qual ferramenta o livro abre (etapa 2 da obra, escolha do agente
        de layout anotada no ONDE-PAREI; não há decisão do Samuel sobre isto).

        A primeira etapa marcada, na ordem de sempre (Dividir, Cortar,
        Endireitar), como antes, quando só as marcadas existiam. Sem nenhuma
        delas, a página na ferramenta de marcar (a página como vai sair, com
        Zoom e Mão), e não mais a tela provisória dos quatro filtros: ela não
        tem mais botão na trilha (R9 403 B), e quem abrisse nela não teria
        como voltar. Seguro mudar: a ordem.

        D-007 (Samuel, 26/10/2026: "quando eu escolher para começar no
        automatico e dividir as folhas o livro tem que aparecer em uma pagina
        por vez para mim"), obra etapa 4: o livro NUNCA abre no Dividir (a
        folha inteira com a linha); o Dividir é só para consertar uma folha,
        quando a pessoa o escolhe. Arriscado: voltar a abrir no Dividir."""
        if projeto.cortar_bordas:
            return ABA_BORDAS
        if projeto.endireitar:
            return ABA_ANGULO
        return ABA_MARCAR

    def mostrar_paginas(self) -> None:
        """D-007 (obra etapa 4): se a tela está na ferramenta Dividir (a folha
        inteira com a linha), passa para a página como vai sair, uma por vez
        (a ferramenta de marcar, com a Mão ou o Retângulo de sempre). Chamada
        quando o Automático divide o livro. Fora do Dividir, nada muda."""
        if not self._pronta() or self.aba_atual != ABA_CORTE or ABA_MARCAR not in self._abas_ativas:
            return
        self.barra_abas.setCurrentIndex(self._abas_ativas.index(ABA_MARCAR))
        self._acertar_as_propriedades()

    @staticmethod
    def _ferramenta_de_partida(projeto: Projeto) -> str:
        """A ferramenta de marcar que fica na mão ao abrir: o Retângulo com
        "procurar gravuras" ligado (como sempre foi), a Mão sem ele - a Mão só
        olha a página, então um clique sem querer não marca nada. Escolha do
        agente de layout (etapa 2 da obra), anotada no ONDE-PAREI."""
        from ui.widgets.editor_selecao import FERRAMENTA_MAO

        if projeto.limpar and projeto.detectar_regioes:
            return FERRAMENTA_RETANGULO
        return FERRAMENTA_MAO

    def eventFilter(self, vigiado, evento) -> bool:  # noqa: N802 - nome do Qt
        """A area da pagina mudou de tamanho (a janela, ou um painel que abriu
        ou fechou): os botoes de girar voltam para o canto dela."""
        if vigiado is self.area_imagem and evento.type() == QEvent.Resize:
            self._por_o_girar_no_canto()
        # etapa 6: a roda do mouse na página (_roda_na_pagina)
        if evento.type() == QEvent.Wheel and hasattr(vigiado, "zoom") and (
                vigiado in self.visualizadores.values()
                or vigiado is getattr(self, "editor_selecao", None)):
            try:
                if self._roda_na_pagina(vigiado, evento):
                    evento.accept()
                    return True
            except Exception:  # noqa: BLE001 - a roda nunca fecha a janela
                registrar_erro("roda na pagina", traceback.format_exc())
        return super().eventFilter(vigiado, evento)

    def _por_o_girar_no_canto(self) -> None:
        """Poe os tres botoes pequenos de girar no canto direito de cima da
        area da pagina, por cima dela (rodada 12 do layout, 703 D; o Samuel
        escolheu sabendo que ficam por cima da pagina). So com um livro
        aberto; e nao na tela provisoria dos quatro filtros, onde cobririam o
        ultimo cartao (ali o girar continua no painel Propriedades e no menu
        Pagina). Seguro mudar: a folga do canto."""
        canto = self.girar_do_canto
        a_vista = self.projeto is not None and bool(self._abas_ativas) \
            and self.aba_atual != ABA_FILTRO
        canto.setVisible(a_vista)
        if not a_vista:
            return
        canto.adjustSize()
        canto.move(max(0, self.area_imagem.width() - canto.width() - FOLGA_DO_GIRAR_NO_CANTO[0]),
                   FOLGA_DO_GIRAR_NO_CANTO[1])
        canto.raise_()

    def _esconder_as_setas_dos_lados(self) -> None:
        """Etapa 2 do layout: as setas "<" e ">" dos lados da pagina viraram
        as da barra de baixo ("< pagina N de M >"), como no prototipo. As dos
        lados ficam escondidas (nao apagadas: cada aba ainda as cria)."""
        for pagina in self.paginas_de_imagem.values():
            for botao in pagina.findChildren(QPushButton):
                if botao.text() in ("<", ">"):
                    botao.setVisible(False)

    def _limpar_abas(self) -> None:
        """Descarta as abas de um projeto anterior antes de montar as novas."""
        while self.barra_abas.count():
            self.barra_abas.removeTab(0)
        for pilha in (self.area_imagem, self.barra_botoes):
            while pilha.count():
                widget = pilha.widget(0)
                pilha.removeWidget(widget)
                widget.deleteLater()

        # etapa 3 do layout: o conteudo do painel Propriedades das ferramentas
        # do livro anterior tambem sai (o painel destroi as pecas)
        self.paineis.propriedades.tirar_conteudos()
        self.propriedades_das_abas.clear()
        # etapa 4: as pecas do filtro do livro anterior saem do painel Filtro
        self.paineis.filtro_da_pagina.desmontar()

        self._abas_ativas.clear()
        # o editor de marcar do livro anterior foi destruido junto com a
        # pagina dele: o nome deixa de apontar para ele (quem o procura usa
        # hasattr/_ao_editor e nao acha nada ate o novo nascer)
        if hasattr(self, "editor_selecao"):
            del self.editor_selecao
        self.visualizadores.clear()
        self.paginas_de_imagem.clear()
        self.linhas_de_botoes.clear()
        self.botoes_de_sugestao.clear()
        self.botoes_de_sugestao_2.clear()
        self.botoes_de_sugestao_3.clear()
        self.cartoes.clear()
        self.botoes_forca.clear()

    def _montar_tira(self) -> None:
        """Recria a tira de miniaturas - mas só quando o conjunto de
        páginas/folhas muda de verdade.

        Remontar refaz a miniatura do livro inteiro do zero, reabrindo o PDF
        numa thread nova - achado ao vivo: se isso acontece enquanto outra
        tarefa de fundo já está lendo o mesmo arquivo, o MuPDF pode travar o
        programa inteiro (regra 3.2). Só trocar de aba, o caso comum, não
        muda nem a quantidade nem o mapeamento - remontar aí é caro à toa.
        """
        if self.projeto is None:
            return
        if self.aba_atual == ABA_CORTE:
            titulo = "Folhas - as laranjas eu não tive certeza"
            quantidade = len(self.projeto.folhas)
            folha_de = {i: i for i in range(len(self.projeto.folhas))}
            corte_de = None
        else:
            titulo = "Páginas - as laranjas eu não tive certeza"
            quantidade = len(self.projeto.paginas)
            folha_de = {p.indice: p.folha for p in self.projeto.paginas}
            corte_de = {
                p.indice: (p.metade, self.projeto.folhas[p.folha].posicao_corte)
                for p in self.projeto.paginas
            }

        self.tira.definir_titulo(titulo)
        self.miniaturas.definir_titulo("FOLHAS" if self.aba_atual == ABA_CORTE else "PÁGINAS")

        assinatura = (
            quantidade,
            tuple(sorted(folha_de.items())),
            tuple(sorted(corte_de.items())) if corte_de is not None else None,
        )
        if assinatura == self._tira_assinatura:
            return
        self._tira_assinatura = assinatura
        self.tira.montar(quantidade, self.projeto.caminho_entrada, folha_de, corte_de,
                         giros=self._giros_das_folhas())

    def _giros_das_folhas(self) -> dict[int, int]:
        """O giro de cada folha, para a tira de miniaturas (D2, 06/10/2026).
        O giro NAO entra na assinatura da tira: girar so redesenha os quadros
        das folhas giradas (TiraMiniaturas.definir_giros), sem ler o livro de
        novo. Arriscado: por o giro na assinatura (remontaria a tira inteira
        a cada giro)."""
        assert self.projeto is not None
        return {f.indice: int(f.rotacao) % 360 for f in self.projeto.folhas}

    # ------------------------------------------------------------------
    # estado
    # ------------------------------------------------------------------

    @property
    def aba_atual(self) -> str:
        indice = self.barra_abas.currentIndex()
        if 0 <= indice < len(self._abas_ativas):
            return self._abas_ativas[indice]
        return self._abas_ativas[0] if self._abas_ativas else ABA_FILTRO

    @property
    def trabalha_com_folhas(self) -> bool:
        return self.aba_atual == ABA_CORTE

    @property
    def item_atual(self):
        assert self.projeto is not None
        if self.trabalha_com_folhas:
            return self.projeto.folhas[self.indice_folha]
        return self.projeto.paginas[self.indice_pagina]

    @property
    def indice_atual(self) -> int:
        return self.indice_folha if self.trabalha_com_folhas else self.indice_pagina

    def _total(self) -> int:
        assert self.projeto is not None
        return (len(self.projeto.folhas) if self.trabalha_com_folhas
                else len(self.projeto.paginas))

    def _pronta(self) -> bool:
        return (self.projeto is not None and self.previas is not None
                and bool(self._abas_ativas) and not self._carregando)

    # ------------------------------------------------------------------
    # navegacao
    # ------------------------------------------------------------------

    @protegido
    def _navegar(self, passo: int) -> None:
        if not self._pronta():
            return
        self._ir_para(max(0, min(self._total() - 1, self.indice_atual + passo)))

    def _ir_para(self, indice: int) -> None:
        assert self.projeto is not None
        if self.trabalha_com_folhas:
            self.indice_folha = indice
            for pagina in self.projeto.paginas:
                if pagina.folha == indice:
                    self.indice_pagina = pagina.indice
                    break
        else:
            self.indice_pagina = indice
            self.indice_folha = self.projeto.paginas[indice].folha
        self.atualizar()

    @protegido
    def _escolher_da_tira(self, indice: int) -> None:
        if self._pronta():
            self._ir_para(indice)

    @protegido
    def _trocou_de_aba(self, _indice: int) -> None:
        if not self._pronta():
            return
        self.area_imagem.setCurrentIndex(self.barra_abas.currentIndex())
        self.barra_botoes.setCurrentIndex(self.barra_abas.currentIndex())
        # A pilha volta a caber na aba ATUAL. Sem isto ela guardaria a altura
        # da aba mais alta pelo resto da sessao, e o buraco voltaria.
        self._encolher_a_barra_de_botoes()
        self._montar_tira()
        self._acertar_a_trilha()
        self.atualizar()

    def _encolher_a_barra_de_botoes(self) -> None:
        """Deixa a fila de botoes com a altura da aba que esta na frente."""
        atual = self.barra_botoes.currentWidget()
        if atual is None:
            return
        for indice in range(self.barra_botoes.count()):
            pagina = self.barra_botoes.widget(indice)
            pagina.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred if pagina is atual else QSizePolicy.Ignored)
        altura = max(0, atual.sizeHint().height())
        self.barra_botoes.setFixedHeight(altura)
        # etapa 3 do layout: a ferramenta cujos botoes moram no painel
        # Propriedades tem aqui uma pagina vazia; sem as margens, a fila nao
        # gasta altura nenhuma e a pagina fica com ela
        self.caixa_dos_botoes.setContentsMargins(
            *(MARGENS_DA_FILA_DE_BOTOES if altura else (0, 0, 0, 0)))

    @protegido
    def ir_para_pagina(self, indice: int) -> None:
        """Poe a tela na pagina pedida. E como o projeto volta onde parou.

        Nao e o `_ir_para`: aquele trabalha no indice da ABA - que na aba de
        corte conta FOLHAS, e nao paginas. Aqui o numero e sempre de pagina,
        porque e isso que fica guardado no resumo do projeto.
        """
        if not self._pronta() or self.projeto is None:
            return
        indice = max(0, min(int(indice), len(self.projeto.paginas) - 1))
        self.indice_pagina = indice
        self.indice_folha = self.projeto.paginas[indice].folha
        self.atualizar()

    def _ir_para_proximo_alerta(self) -> bool:
        """"próxima dúvida" (e a tecla Tab): vai para a próxima folha (no
        Dividir) ou página com um aviso que ainda pede um olhar, dando a volta
        no fim do livro. Devolve True se andou. Etapa 7 da obra: "dúvida" é o
        mesmo que a faixa mostra (_avisos_do_item), com os avisos da folha
        nas páginas dela (antes ficavam de fora fora do Dividir)."""
        if not self._pronta():
            return False
        assert self.projeto is not None
        total = self._total()
        com_duvida = self._itens_com_duvida()
        for salto in range(1, total + 1):
            indice = (self.indice_atual + salto) % total
            if indice in com_duvida and indice != self.indice_atual:
                self._ir_para(indice)
                return True
        return False

    # --- "está certo" com resposta e um número só de dúvidas (etapa 7) ---------
    #
    # Plano de 26/10 (aprovado), etapa 7: "'está certo' com resposta [...]:
    # tique, contador certo, próxima dúvida (1.1); botões no cartão do aviso
    # (1.8); um número só de dúvidas (5.5)". D-010, o exemplo do Samuel: "a
    # folha fica conferida, tique na miniatura, contador sobe, vai para a
    # próxima dúvida". Sessão 1, 1-5: "eu clico no esta certo e não acontece
    # nada." O que conta como dúvida mora em core/avisos.py (avisos_da_pagina,
    # avisos_da_folha, quantas_com_duvida): a tela só pergunta.

    def _avisos_do_item(self, indice: int, de_folha: bool) -> list:
        """Os avisos (core.avisos.Aviso) que a folha `indice` (no Dividir) ou
        a página `indice` mostra na faixa: na página, os dela e depois os da
        folha dela (lista única 5.5: "os avisos de folha ficam escondidos")."""
        if self.projeto is None:
            return []
        if de_folha:
            return avisos_do_livro.avisos_da_folha(self.projeto, indice)
        return avisos_do_livro.avisos_da_pagina(self.projeto, indice)

    def _avisos_da_vez(self) -> list:
        """Os avisos da folha ou página que está na tela (o primeiro é o da faixa)."""
        if self.projeto is None:
            return []
        return self._avisos_do_item(self.indice_atual, self.trabalha_com_folhas)

    def _itens_com_duvida(self) -> set[int]:
        """As folhas (no Dividir) ou as páginas com dúvida, de uma vez (a tira
        e o "próxima dúvida" perguntam por todas)."""
        if self.projeto is None:
            return set()
        pendentes = avisos_do_livro.pendentes_do_livro(self.projeto)
        if self.trabalha_com_folhas:
            return {a.indice for a in pendentes if a.alvo == avisos_do_livro.FOLHA}
        return {indice for alvo, indice in avisos_do_livro._itens_com_aviso(pendentes, self.projeto)
                if alvo == avisos_do_livro.PAGINA}

    def _item_do_aviso(self, aviso):
        """A folha ou a página de um aviso (para os botões que dependem dela)."""
        assert self.projeto is not None
        if aviso.alvo == avisos_do_livro.FOLHA:
            return self.projeto.folhas[aviso.indice]
        return self.projeto.paginas[aviso.indice]

    @protegido
    def esta_certo(self) -> None:
        """O "está certo" da faixa: a folha (no Dividir) ou a página fica
        conferida (numa ação do desfazer), a miniatura ganha o tique, o
        contador de conferidas sobe, e a tela vai para a próxima dúvida. Sem
        outra dúvida no livro, fica onde está (o tique e o contador mostram
        que pegou). A barra de espaço continua "marca e vai para a próxima"."""
        if not self._pronta():
            return
        self._marcar_revisada()
        self._ir_para_proximo_alerta()

    def _ir_do_para_revisar(self, indice: int) -> None:
        """Clique num cartão do "Para revisar": vai até a página e deixa à
        vista o aviso dela, com os botões. Se o primeiro aviso da página é da
        divisão da folha ("Lombada incerta", "Não parece dupla"), vai ao
        Dividir nessa folha (D-501); senão, se a tela está no Dividir, sai dele
        para a página (D-007/D-501: no Dividir só se vê a folha inteira, e o
        aviso da página não aparecia - sessão 0, 0-8: "o clique levou à folha
        4 [...] sem os botões do aviso")."""
        if not self._pronta() or self.projeto is None:
            return
        if not 0 <= indice < len(self.projeto.paginas):
            return
        avisos = avisos_do_livro.avisos_da_pagina(self.projeto, indice)
        primeiro = avisos[0] if avisos else None
        if (primeiro is not None and primeiro.alvo == avisos_do_livro.FOLHA
                and primeiro.codigo in avisos_do_livro.DA_DIVISAO and ABA_CORTE in self._abas_ativas):
            if self.aba_atual != ABA_CORTE:
                self.barra_abas.setCurrentIndex(self._abas_ativas.index(ABA_CORTE))
            self.indice_folha = self.projeto.paginas[indice].folha
            self.indice_pagina = indice
            self.atualizar()
            return
        if self.trabalha_com_folhas:
            self.mostrar_paginas()
        self.ir_para_pagina(indice)

    @protegido
    def abrir_so_as_que_precisam(self) -> None:
        """"ver as N em tela cheia" do "Para revisar" (D-259, 05/10: "abrir
        todas as páginas em tela cheia (como no UPDF) mostrando as que precisam
        de atenção"; no desenho decidido, rodada 13, o botão largo no pé do
        painel): a grade "Todas as páginas" já em "só as que precisam de
        atenção" (D-343). O número do botão e o da grade são o mesmo
        (core.avisos.quantas_com_duvida)."""
        self.abrir_todas_as_paginas()
        if self.pilha_da_tela.currentWidget() is self.todas:
            self.todas.definir_so_atencao(True)

    # ------------------------------------------------------------------
    # desenho
    # ------------------------------------------------------------------

    @protegido
    def atualizar(self) -> None:
        """Redesenha a tela inteira a partir do projeto (depois de qualquer
        mudanca, navegacao ou desfazer).

        Item 1.1: antes de desenhar, acerta o alerta "conferir o fundo
        tirado" da pagina da vez (core.pipeline.acertar_alertas_do_fundo):
        some se ela saiu do filtro "Tirar o fundo", e aparece na hora se ela
        entrou nele e a decisao do core/camadas.py ja e conhecida (o cartao
        ja desenhou). Se nao e conhecida, a previa acerta quando chegar
        (_alertas_da_previa).
        """
        if not self._pronta():
            return
        if self.projeto is not None and 0 <= self.indice_pagina < len(self.projeto.paginas):
            acertar_alertas_do_fundo(self.projeto, [self.projeto.paginas[self.indice_pagina]])
        if self.projeto is not None:
            # Bug Misto 1 (05/10/2026): o "Tem cor" segue o "So as letras" em
            # TODAS as paginas (o "So as letras" do livro e o "todas" mudam
            # muitas de uma vez, e o "Para revisar" e o contador contam
            # todas). Barato: so le campos (core.pipeline.acertar_alertas_de_cor).
            acertar_alertas_de_cor(self.projeto)
            # Regra ajustada do "Para revisar" (12/10/2026): a faixa escura na
            # beirada em 70% ou mais das páginas já medidas vira um aviso só,
            # do livro. Barato: só lê campos.
            acertar_faixa_do_livro(self.projeto)
        self._atualizar_previa()
        self._atualizar_faixa()
        self._atualizar_botoes()
        self._atualizar_tira()
        self._atualizar_contador()
        self._atualizar_paineis()
        self._atualizar_barra_de_baixo()
        self._acertar_a_vista_da_pagina()       # etapa 6: lado a lado, antes / depois
        self.trabalho_mudou.emit()

    def _atualizar_paineis(self) -> None:
        """Os paineis da direita leem o mesmo estado que o resto da tela.
        Acertados a cada atualizacao, abertos ou nao (abrir um painel mostra
        o que ja esta em dia); cada um so se refaz quando o que ele mostra
        mudou."""
        if self.projeto is None:
            return
        self.paineis.para_revisar.atualizar(self.projeto)
        self.paineis.para_revisar.definir_pagina_atual(self.indice_pagina)
        # etapa 3 da obra: o "só nesta página" do Automatico e a da vez
        self.paineis.automatico.estado.pagina_atual = self.indice_pagina
        self.paineis.automatico.atualizar(self.projeto)
        self._mostrar_o_aviso_do_livro_novo()
        self.paineis.historico.atualizar(self.acoes)
        pagina = (self.projeto.paginas[self.indice_pagina]
                  if 0 <= self.indice_pagina < len(self.projeto.paginas) else None)
        self.paineis.filtro_da_pagina.atualizar(pagina)

    def _atualizar_previa(self) -> None:
        assert self.previas is not None and self.projeto is not None
        aba = self.aba_atual

        if aba == ABA_CORTE:
            img = self.previas.pegar_folha(self.indice_folha, DPI_PREVIA)
            vis = self.visualizadores[ABA_CORTE]
            vis.definir_imagem(img, dono=("folha", self.indice_folha))   # D4
            folha = self.projeto.folhas[self.indice_folha]
            # a linha so aparece em folha dividida (parecer do verificador, 06/10)
            vis.definir_corte(folha.posicao_corte, visivel=bool(folha.dividir))
            self.previas.pre_carregar_folhas(self.indice_folha, DPI_PREVIA)
            # na ferramenta Dividir a tela trabalha com a folha inteira: a
            # fila do painel Filtro fica sem as paginas pequenas (nao mostra
            # as de outra pagina)
            if self._filtro_aberto():
                for cartao in self.cartoes.values():
                    cartao.definir_amostra(None)
            self._acertar_o_desentortar()      # item 2.12: aqui so esconde o sinal
            return

        # item 2.12 (resposta P6): a medida do desentortar, por tras, antes de
        # pedir a previa (a previa sai sem desentortar ate ela chegar)
        self._acertar_o_desentortar()
        img = self.previas.pegar(self.indice_pagina, self._dpi_atual)
        self.previas.pre_carregar(self.indice_pagina, self._dpi_atual)
        pagina = self.projeto.paginas[self.indice_pagina]
        # A regra do "Para revisar" só vale na resolução do PDF (12/10/2026):
        # a prévia não mede; a medida da página da vez é pedida aqui, por
        # trás (GerenciadorPrevias.pedir_medida), e chega em _previa_chegou.
        # Não durante o arrasto do medidor (cada valor do meio seria um
        # desenho do tamanho do PDF): só com a prévia normal.
        # (13/10) e só DEPOIS de a prévia desta página existir: é ela que
        # guarda a marcação provisória, que o desenho de trás troca pela do
        # tamanho do PDF. Pedidos juntos, os dois procurariam a marcação ao
        # mesmo tempo, na página pequena e na grande.
        if self._dpi_atual == self._dpi_normal and img is not None:
            self.previas.pedir_medida(self.indice_pagina)

        if aba == ABA_BORDAS:
            vis = self.visualizadores[ABA_BORDAS]
            vis.definir_dpi(self._dpi_atual)
            # etapa 5 da obra: as Bordas so cortam (o mover e a ferramenta Mover)
            self._atualizar_previa_para_recorte(vis, pagina)
            vis.definir_recorte(pagina.recorte or (0.0, 0.0, 1.0, 1.0))
            self._conferir_tamanho_da_folha(pagina, vis)
        elif aba == ABA_MOVER:
            self._atualizar_o_mover(img, pagina)                     # etapa 5 (D-008)
        elif aba == ABA_ANGULO:
            vis = self.visualizadores[ABA_ANGULO]
            # item 2.2 (G5): o angulo de agora (o a mao ou o automatico ja
            # medido) e o giro que a imagem nova JA tem; a imagem velha que
            # fica na tela enquanto a nova nao chega gira ao vivo ate ele
            agora = angulo_da_pagina(self.projeto, pagina)
            pendente = self._angulo_pendente
            if pendente is not None and pendente[0] == self.indice_pagina:
                agora = pendente[1]               # setas ainda nao gravadas
            vis.definir_imagem(img, dono=("pagina", self.indice_pagina))   # D4
            vis.definir_angulo(agora, da_imagem=None if img is None
                               else angulo_aplicado(angulo_da_pagina(self.projeto, pagina)))
            self._mostrar_angulo(agora)
        elif aba == ABA_MARCAR:
            self._atualizar_marcacao(img, pagina)
        else:
            self._atualizar_cartoes(img)
        # etapa 4 do layout: com o painel "Filtro da página" aberto, a fila
        # dele mostra a pagina nos outros filtros (o mesmo pedido dos cartoes
        # grandes, com o mesmo cache): so enquanto ele estiver aberto
        if aba != ABA_FILTRO and self._filtro_aberto() and self.cartoes:
            self._atualizar_cartoes(img)

    def _atualizar_marcacao(self, img, pagina) -> None:
        """Poe a pagina e a marcacao dela no editor.

        Problema 2 do plano (redesenho do fluxo): a deteccao NAO roda mais
        sozinha aqui - antes disparava toda vez que a pagina nao tinha
        marcacao, sem avisar; agora so quando o Samuel pede (botao
        "detectar automaticamente" desta aba, ou menu Marcar -> "Procurar de
        novo" - mesma acao, `_detectar_de_novo`). O pipeline final continua
        detectando sozinho quando precisa (`core/pipeline.py::garantir_selecao`)
        - isso e so a tela deixar de adivinhar por baixo dos panos.
        """
        self.editor_selecao.definir_imagem(img)
        # De que marcação é a cópia que o editor passa a ter (ver
        # _selecao_mudou). Lido ANTES da lista: se a busca por trás trocar a
        # marcação entre as duas leituras, o pior que acontece é o editor
        # achar provisória uma cópia que já é a definitiva (e ela ser
        # procurada mais uma vez); o contrário gravaria a provisória como
        # definitiva.
        self._editor_com_a_provisoria = bool(getattr(pagina, "marcacao_provisoria", False))
        selecao = pagina.obter_selecao()

        self.editor_selecao.definir_selecao(selecao)
        self._mostrar_as_achadas(self.caixa_mostrar_achadas.isChecked())   # item 2.18
        self._mostrar_forma_da_pagina(pagina)      # item 1.2
        self._mostrar_aviso_da_marcacao(
            selecao.resumo_em_portugues() if not selecao.vazia
            else 'Nada marcado ainda. Clique em "detectar automaticamente" '
                 "ou marque à mão."
        )
        self._avaliar_os_pedacos(pagina)        # conferencia 13, S3

    # --- conferencia 13, S3: o pedaco que pegou papel em volta da figura ----

    def _pagina_sem_filtro_para_o_ajuste(self, pagina) -> np.ndarray | None:
        """A pagina como veio (sem filtro, ja girada, dividida, cortada e
        endireitada), reduzida a LADO_DO_AJUSTE, para o aviso e o botao do
        pedaco. Sem filtro de proposito: com o filtro, o papel de fora sai
        branco e o de dentro do pedaco creme, e a conta erra (ver
        core.ajustar_pedaco.caixa_justa). None enquanto a folha ainda nao
        chegou: ela e pedida aqui, e quando chega (_previa_chegou ->
        _atualizar_previa -> _atualizar_marcacao) a conta e refeita.

        Juncao do girar ao fase-1 (06/10/2026), dois cuidados:
        - a folha e pedida COMO VEIO no PDF (girada=False): quem gira e o
          preparar_metade. Com a folha ja girada, a pagina saia girada duas
          vezes numa folha girada (o mesmo defeito D1 dos cartoes);
        - None tambem enquanto as zonas da pagina ainda estao no preparo de
          ANTES (logo depois de girar, cortar ou mudar o angulo, ate a previa
          nova chegar e leva-las: zonas_na_folha.zonas_valem_no_desenho).
          Senao o retangulo velho era medido na pagina nova, e o botao o
          gravava no lugar errado do papel. Quando a previa chega, a conta e
          refeita (o caminho de cima)."""
        import cv2

        from core.pipeline import preparar_metade_e_geometria
        from core.zonas_na_folha import zonas_valem_no_desenho

        if self.previas is None or self.projeto is None:
            return None
        bruta = self.previas.pegar_folha(pagina.folha, DPI_PREVIA, girada=False)
        if bruta is None:
            return None
        img, desenho = preparar_metade_e_geometria(
            bruta, self.projeto.folhas[pagina.folha], pagina, self.projeto, dpi=DPI_PREVIA)
        if not zonas_valem_no_desenho(pagina, desenho):
            return None
        lado = max(img.shape[:2])
        if lado > LADO_DO_AJUSTE:
            escala = LADO_DO_AJUSTE / lado
            img = cv2.resize(img, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
        return img

    def _avaliar_os_pedacos(self, pagina) -> None:
        """Mostra ou esconde a parte "Pedaço" (painel Propriedades das
        ferramentas de marcar) e acerta o aviso.

        A linha aparece so quando a pagina tem um pedaco em retangulo com
        "so neste pedaco" num filtro diferente do da pagina, e com alguma
        tinta dentro. Ela fala do PEDACO DA VEZ (core.ajustar_pedaco.
        pedaco_da_vez): o ultimo desenhado em volta de uma figura que ainda
        tem o que ajustar. O botao fica aceso quando o ajuste muda alguma
        coisa nele; a frase avisa quando o papel em volta e muito
        (Folga.muito) ou diz por que o botao esta apagado (ja justo, ou so ha
        pedaco de TEXTO: conserto de 05/10/2026, o ajuste cortava o texto).
        Quando a linha aparece ou some, a barra de botoes e medida de novo
        (senao ela espreme as outras linhas: defeito 1 do verificador).
        Custa ~0,1 s no fio da tela, e so em pagina com um pedaco assim.
        Nunca levanta excecao: se a conta falhar, a linha some e o erro vai
        para o log."""
        if not hasattr(self, "linha_pedaco"):
            return
        folgas = {}
        da_vez = None
        try:
            from core.ajustar_pedaco import (
                avaliar_os_pedacos,
                pedaco_da_vez,
                pedacos_com_outro_filtro,
            )

            if pagina is not None:
                selecao = pagina.obter_selecao()
                if pedacos_com_outro_filtro(selecao, pagina.filtro):
                    img = self._pagina_sem_filtro_para_o_ajuste(pagina)
                    if img is not None:
                        # lida de novo DEPOIS da imagem: a previa pode ter
                        # levado as zonas para o preparo novo no meio
                        selecao = pagina.obter_selecao()
                        folgas = avaliar_os_pedacos(img, selecao, pagina.filtro)
                        da_vez = pedaco_da_vez(folgas)
        except Exception:  # noqa: BLE001 - o aviso nunca derruba a aba
            registrar_erro("avaliar o pedaco", traceback.format_exc())
            folgas, da_vez = {}, None
        folga = folgas.get(da_vez) if da_vez is not None else None
        estava_visivel = not self.linha_pedaco.isHidden()
        self.linha_pedaco.setVisible(bool(folgas))
        self.botao_ajustar_pedaco.setEnabled(bool(folga is not None and folga.muda))
        self.botao_ajustar_pedaco.setToolTip(DICA_DO_AJUSTE)
        # A frase cabe numa linha (a aba tem pouca altura); a explicacao
        # inteira fica na dica do mouse.
        if folgas and folga is None:
            # so pedaco de texto: o botao fica apagado, e a frase diz por que
            self.aviso_pedaco.setText("Pedaço de texto: o ajuste é só para figura.")
            self.aviso_pedaco.setToolTip(DICA_DO_TEXTO)
            self.botao_ajustar_pedaco.setToolTip(DICA_DO_TEXTO)
        elif folga is not None and folga.muito:
            porcento = max(1, int(round(100 * folga.fracao_de_papel)))
            self.aviso_pedaco.setText(
                f"Sobrou papel em volta da figura ({porcento}%): pode sair uma faixa.")
            self.aviso_pedaco.setToolTip(
                "O papel que ficou dentro do retângulo sai com o filtro do pedaço, "
                "e não com o da página, e pode aparecer como uma faixa em volta da "
                "figura. Se quiser, clique em \"Ajustar o pedaço à figura\". "
                "Se não quiser mudar, pode deixar como está.")
        elif folga is not None and not folga.muda:
            self.aviso_pedaco.setText("O pedaço já está justo na figura.")
            self.aviso_pedaco.setToolTip("")
        else:
            self.aviso_pedaco.setText("")
            self.aviso_pedaco.setToolTip("")
        # (desde a etapa 4 do layout a parte "Pedaço" mora no painel
        # Propriedades, com rolagem; a fila embaixo da pagina fica vazia, e
        # medir de novo nao custa nada)
        if estava_visivel != (not self.linha_pedaco.isHidden()):
            self._encolher_a_barra_de_botoes()
            self.paineis.propriedades.medir_de_novo()

    @protegido
    def _ajustar_pedaco_a_figura(self) -> None:
        """O botao "Ajustar o pedaco a figura": encolhe o PEDACO DA VEZ (o
        ultimo desenhado em volta de uma figura, core.ajustar_pedaco.
        pedaco_da_vez) ate a figura, numa acao do Historico - o Desfazer
        devolve o retangulo como estava. Um pedaco por clique; pedaco de
        texto nunca (conserto de 05/10/2026). So muda o tamanho do
        retangulo: o tipo, o filtro e o resto da marcacao ficam.
        Arriscado: mudar a marcacao sem passar por _registrar (o desfazer nao
        a veria)."""
        from core.ajustar_pedaco import ajustar_os_pedacos

        pagina = self._pagina_marcada()
        if pagina is None or not self._pronta():
            return
        img = self._pagina_sem_filtro_para_o_ajuste(pagina)
        if img is None:
            self.aviso_pedaco.setText("Ainda carregando a página. Tente de novo em um instante.")
            return
        nova, quantos = ajustar_os_pedacos(img, pagina.obter_selecao(), pagina.filtro)
        if not quantos:
            self.aviso_pedaco.setText("O pedaço já está justo na figura.")
            return
        self._registrar(
            "ajustar_pedaco", "pagina", [self.indice_pagina],
            {"selecao": nova.para_lista()},
            f"Página {self.indice_pagina + 1}: pedaço ajustado à figura",
        )
        self._mostrar_aviso_da_marcacao(
            "Pedaço ajustado à figura. Para voltar como estava, desfazer.")

    def _atualizar_cartoes(self, img: np.ndarray | None) -> None:
        """Os cartoes mostram a página de verdade, cada um com seu filtro.

        Só o cartão do filtro escolhido é imediato (a imagem já veio pronta).
        Os outros pedem o cálculo em segundo plano (regra 3.2): aplicar
        preto_e_branco/magico_pro de verdade - k_para_a_letra usa skeletonize -
        pode levar segundos numa página de traço fino, e isso não pode travar
        a tela.

        Item 1.1: o cartão "Tirar o fundo" (só em livro com camadas) não é um
        filtro aplicado na amostra: é a página desenhada pelo caminho do
        programa (core/camadas.py na folha inteira), pedida ao
        GerenciadorPrevias depois que a prévia principal chegou (para não
        disputar a máquina com ela) - ver _cartao_sem_fundo.

        Modo Misto (bug Misto 2, 05/10/2026): com "Só as letras" valendo na
        página, o cartão "Preto e branco" também é desenhado pelo caminho do
        programa, com o Misto (_cartao_do_misto), e não pelo filtro puro.
        Arriscado: pintar nele a amostra pura (o Kaique escolheria às cegas:
        o cartão mostrava a gravura em preto e branco e a página saía com ela
        em cor - prints 09 e 10 do verificador).
        """
        from core.pdf_io import limitar_altura

        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]

        for chave, cartao in self.cartoes.items():
            cartao.definir_selecionado(chave == pagina.filtro)

        if img is None:
            for cartao in self.cartoes.values():
                cartao.definir_amostra(None)
            return

        for chave, cartao in self.cartoes.items():
            if chave == pagina.filtro:
                cartao.definir_amostra(limitar_altura(self._com_as_margens(img), 260))

        outros = [chave for chave in self.cartoes if chave != pagina.filtro]
        if TIRAR_FUNDO in outros:
            outros.remove(TIRAR_FUNDO)
            self._cartao_sem_fundo()
        # Modo Misto (bug Misto 2): o cartao "Preto e branco" vem do caminho
        # do programa (_cartao_do_misto). O filtro puro continua sendo
        # calculado na amostra (para o aviso "ficou escura / texto quase
        # sumiu", _conferir_qualidade_do_preto_e_branco), so nao vai para o
        # cartao (_cartoes_a_pintar).
        if self._cartao_pb_pelo_misto(pagina):
            self._cartao_do_misto()
        base = self._imagem_sem_filtro()
        if base is None:
            for chave in self._cartoes_a_pintar(outros, pagina):
                self.cartoes[chave].definir_amostra(None)
            return

        chave_cache = self._chave_dos_cartoes()
        a_pintar = self._cartoes_a_pintar(outros, pagina)
        if (chave_cache == self._cartoes_cache_chave
                and all(c in self._cartoes_cache for c in a_pintar)):
            for chave in a_pintar:
                self.cartoes[chave].definir_amostra(
                    self._com_as_margens(self._cartoes_cache.get(chave)))
            return

        for chave in a_pintar:
            self.cartoes[chave].definir_amostra(None)
        assert self.previas is not None
        self.previas.pedir_cartoes(
            self.indice_pagina, base, outros,
            pagina.forca_preto, pagina.clareza_melhorar, pagina.intensidade_magico,
            chave=chave_cache, dpi=DPI_AMOSTRA_DOS_CARTOES,
        )

    def _com_as_margens(self, img):
        """Item 2.4 (Samuel, 22/10/2026: "Sim, a tela mostra igual ao que
        sai"): com as margens iguais ligadas, a pagina dos cartoes aparece com
        elas, como no PDF. Enquanto as paginas nao foram medidas, pede a
        medida por tras (TarefaMedirAsMargens) e mostra sem margem; quando
        termina, os cartoes sao pintados de novo. Desligadas: `img` mesmo."""
        from core.pipeline import conta_das_margens_para_a_tela, margens_na_tela

        if img is None or self.projeto is None or not getattr(self.projeto, "margens_iguais", False):
            return img
        conta = conta_das_margens_para_a_tela(self.projeto)
        if conta is None:
            self._medir_as_margens()
            return img
        return margens_na_tela(img, self.projeto, self.projeto.paginas[self.indice_pagina], conta)

    def _medir_as_margens(self) -> None:
        from ui.tarefas import TarefaMedirAsMargens

        tarefa = getattr(self, "_tarefa_das_margens", None)
        if tarefa is not None and tarefa.isRunning():
            return
        self._tarefa_das_margens = TarefaMedirAsMargens(self.projeto)
        self._tarefa_das_margens.pronta.connect(self._margens_medidas)
        self._tarefa_das_margens.start()

    def _margens_medidas(self) -> None:
        """A medida das margens chegou: pinta os cartoes de novo."""
        self._cartoes_cache_chave = None
        self.atualizar()

    def _chave_dos_cartoes(self) -> str:
        """Tudo de que os cartoes da pagina da vez dependem: o giro, a divisao,
        o corte, o angulo, as opcoes do livro e os tres ajustes - a mesma
        chave das previas (GerenciadorPrevias.chave), com um filtro fixo no
        lugar do da pagina (os cartoes sao os OUTROS filtros).

        D1 do verificador (06/10/2026): a chave de antes era so a pagina e os
        tres ajustes; girar a folha com a aba Filtro aberta reaproveitava os
        cartoes do giro de antes. Arriscado: tirar daqui o que muda a amostra
        (o cartao fica com a imagem de antes)."""
        assert self.previas is not None
        return self.previas.chave(self.indice_pagina, DPI_AMOSTRA_DOS_CARTOES, "cartoes")

    def _cartao_sem_fundo(self, img: np.ndarray | None = None) -> None:
        """Item 1.1: poe no cartão "Tirar o fundo" a página sem o fundo.

        `img` e a previa que acabou de chegar (de _previa_chegou); sem ela,
        pega do cache do GerenciadorPrevias ou pede (e mostra
        "preparando..." ate chegar). E o resultado de verdade: uma pagina que
        o core/camadas.py deixa intacta aparece como veio, igual ao Original.
        """
        from core.pdf_io import limitar_altura

        cartao = self.cartoes.get(TIRAR_FUNDO)
        if cartao is None or self.previas is None:
            return
        if img is None:
            img = self.previas.pegar_com_filtro(
                self.indice_pagina, DPI_CARTAO_SEM_FUNDO, TIRAR_FUNDO)
        cartao.definir_amostra(None if img is None else limitar_altura(img, 260))

    def _cartao_pb_pelo_misto(self, pagina) -> bool:
        """O cartão "Preto e branco" desta página tem de mostrar o Misto?
        Sim quando ela NÃO está no Preto e branco (no Preto e branco, o cartão
        dele é a própria prévia, que já passa pelo Misto) e, escolhendo-o, ela
        sairia pelo "Só as letras" (dela ou do livro, com "Limpar a folha"):
        a mesma conta de core.pipeline._filtrar. Barato (só lê campos)."""
        assert self.projeto is not None
        return bool(PRETO_E_BRANCO in self.cartoes
                    and pagina.filtro != PRETO_E_BRANCO
                    and self.projeto.limpar
                    and misto.opcoes_da_pagina(self.projeto, pagina) is not None)

    def _cartoes_a_pintar(self, chaves: list[str], pagina) -> list[str]:
        """Os cartões que recebem a amostra com o filtro puro: todos menos o
        "Preto e branco" quando ele vem do Misto (_cartao_pb_pelo_misto)."""
        if self._cartao_pb_pelo_misto(pagina):
            return [c for c in chaves if c != PRETO_E_BRANCO]
        return list(chaves)

    def _cartao_do_misto(self, img: np.ndarray | None = None) -> None:
        """Bug Misto 2 (05/10/2026): põe no cartão "Preto e branco" a página
        como ela vai sair escolhendo o Preto e branco, com o "Só as letras"
        (core.pipeline.renderizar_com_filtro numa cópia da página: o Misto,
        a gravura e o leitor de texto, numa tarefa de prévia - a tela não
        espera). `img` é a que acabou de chegar (_previa_chegou); sem ela,
        pega do cache do GerenciadorPrevias ou pede (e o cartão fica em
        "preparando..." até chegar). Mesmo jeito do _cartao_sem_fundo."""
        from core.pdf_io import limitar_altura

        cartao = self.cartoes.get(PRETO_E_BRANCO)
        if cartao is None or self.previas is None:
            return
        if img is None:
            img = self.previas.pegar_com_filtro(
                self.indice_pagina, DPI_CARTAO_DO_MISTO, PRETO_E_BRANCO)
        cartao.definir_amostra(None if img is None else limitar_altura(img, 260))

    @protegido
    def _cartoes_prontos(self, indice: int, resultados: dict, chave=None) -> None:
        """Os cartões calculados em segundo plano chegaram.

        Se o usuário já virou a página nesse meio tempo, descarta - senão
        pinta e guarda no cache, para não recalcular ao voltar para cá.

        chave: a de _chave_dos_cartoes no momento do pedido. Se a página
        mudou desde então (girou, mudou o corte ou um ajuste), o resultado é
        de um estado que já passou e é descartado: o pedido do estado novo
        já foi feito (D1, 06/10/2026). None (quem chama sem chave): vale
        para o estado de agora, como antes.
        """
        if self.projeto is None or indice != self.indice_pagina or self.previas is None:
            return
        atual = self._chave_dos_cartoes()
        if chave is not None and chave != atual:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        self._cartoes_cache_chave = atual
        self._cartoes_cache = resultados
        # o "Preto e branco" puro nao vai para o cartao quando ele vem do
        # Misto (_cartao_do_misto); continua no cache e no aviso abaixo
        a_pintar = self._cartoes_a_pintar(list(resultados), pagina)
        for chave, amostra in resultados.items():
            if chave in self.cartoes and chave in a_pintar:
                self.cartoes[chave].definir_amostra(self._com_as_margens(amostra))

        self._conferir_qualidade_do_preto_e_branco(pagina, resultados)

    def _conferir_qualidade_do_preto_e_branco(self, pagina, resultados: dict) -> None:
        """Problema 5.4 do plano: aponta sozinho páginas que podem ter saído
        erradas, comparando o resultado com o original - em vez do Samuel
        ter que abrir imagem por imagem procurando problema."""
        from core.analise import ESCURA_DEMAIS, APAGADA_DEMAIS, avaliar_preto_e_branco

        original = resultados.get(ORIGINAL)
        pb = resultados.get(PRETO_E_BRANCO)
        if original is None or pb is None:
            return

        achado = avaliar_preto_e_branco(original, pb)
        tinha_algum = pagina.alertas.count(ESCURA_DEMAIS) or pagina.alertas.count(APAGADA_DEMAIS)
        pagina.alertas = [a for a in pagina.alertas if a not in (ESCURA_DEMAIS, APAGADA_DEMAIS)]
        if achado is not None:
            pagina.alertas.append(achado)

        if achado is not None or tinha_algum:
            self._atualizar_faixa()
            self._atualizar_tira()
            self._atualizar_contador()

    def _imagem_sem_filtro(self) -> np.ndarray | None:
        """Versao pequena e sem filtro da página atual, para os outros cartoes.

        A folha vem COMO VEIO NO PDF (girada=False): o preparar_metade é que
        a gira, divide, corta e endireita. D1 do verificador (06/10/2026):
        vinha a folha já girada, e os cartões mostravam a folha girada duas
        vezes. Arriscado: pedir a folha girada aqui."""
        assert self.projeto is not None and self.previas is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        img_folha = self.previas.pegar_folha(pagina.folha, DPI_AMOSTRA_DOS_CARTOES,
                                             girada=False)
        if img_folha is None:
            return None

        from core.pipeline import preparar_metade

        folha = self.projeto.folhas[pagina.folha]
        try:
            return preparar_metade(img_folha, folha, pagina, self.projeto)
        except Exception:  # noqa: BLE001 - amostra que falha nao derruba a tela
            registrar_erro("amostra_de_filtro", traceback.format_exc())
            return None

    def _atualizar_faixa(self) -> None:
        """A faixa de aviso: o PRIMEIRO alerta que ainda pede um olhar nesta
        folha ou página (ConfigPagina.alertas_pendentes), com os botões dele
        (analise.Alerta.botoes: até dois, ao lado dos botões da aba). Dar
        "está bom assim" nele mostra o próximo motivo da mesma página (Samuel,
        rodada 4: "com um motivo individual de uma pagina"). Sem alerta, o
        texto tranquilo da aba. As marcas de "onde sumiu" seguem o alerta
        mostrado (_mostrar_marcas_do_aviso)."""
        item = self.item_atual
        aba = self.aba_atual
        # etapa 7 da obra: na página entram também os avisos da folha dela
        # (core.avisos.avisos_da_pagina; antes só apareciam no Dividir)
        pendentes = self._avisos_da_vez()
        alerta = analise.descrever(pendentes[0].codigo) if pendentes else None
        botoes_do_cartao: list[str] = []

        if alerta is not None:
            texto = alerta.mensagem
            if len(pendentes) > 1:
                texto += f"  (aviso 1 de {len(pendentes)} desta página)"
            self.texto_faixa.setText(self._com_andamento(texto))
            self._pintar_faixa(alerta=True)
            botoes = self._botoes_do_aviso(self._item_do_aviso(pendentes[0]), pendentes[0].codigo)
            for qual in range(3):
                self._mostrar_sugestao(aba, botoes[qual][0] if len(botoes) > qual else None, qual)
            botoes_do_cartao = [rotulo for rotulo, _c in botoes[:3]]
        elif getattr(item, "em_branco", False) and not self.trabalha_com_folhas:
            # "Deixar em branco": a página fica no livro, branca; o botão
            # devolve a página (o mesmo que o Desfazer faria)
            self.texto_faixa.setText(self._com_andamento(
                "Esta página vai sair em branco (uma folha branca no lugar dela)."))
            self._pintar_faixa(alerta=False)
            self._mostrar_sugestao(aba, "voltar a página")
            self._mostrar_sugestao(aba, None, qual=1)
            self._mostrar_sugestao(aba, None, qual=2)
        else:
            self.texto_faixa.setText(self._com_andamento(self._texto_tranquilo(aba)))
            self._pintar_faixa(alerta=False)
            for qual in range(3):
                self._mostrar_sugestao(aba, None, qual)
        self._mostrar_marcas_do_aviso()
        # etapa 7 da obra (lista única 1.8; D-268 "(a) Botão no aviso"; sessão
        # 0, 0-7: "tem os avisos mas não tem como apertar para fazer ele
        # sumir"): o cartão da página da vez no "Para revisar" ganha os mesmos
        # botões da faixa (o clique faz o mesmo: _aplicar_sugestao)
        if hasattr(self, "paineis"):
            self.paineis.para_revisar.definir_botoes_da_vez(
                self.indice_pagina, botoes_do_cartao)

    def _mostrar_marcas_do_aviso(self) -> None:
        """Mostra ONDE está o problema do aviso da página da vez: retângulos
        laranja nos cartões de filtro e na aba Marcar (Samuel, rodada 5:
        "onde sumiu, tem que aparecer selecionado automaticamente"). As
        caixas vêm da mesma conta do aviso (core.pipeline.marcas_do_aviso) e
        só existem depois que a página foi desenhada nesta sessão. Página já
        dada como boa: sem marcas. Nunca levanta exceção."""
        try:
            caixas: list = []
            if self.projeto is not None and 0 <= self.indice_pagina < len(self.projeto.paginas):
                pagina = self.projeto.paginas[self.indice_pagina]
                # as marcas seguem o aviso que a faixa mostra (se for da
                # página; o da folha não tem "onde sumiu")
                avisos = avisos_do_livro.avisos_da_pagina(self.projeto, self.indice_pagina)
                if avisos and avisos[0].alvo == avisos_do_livro.PAGINA:
                    caixas = marcas_do_aviso(pagina, avisos[0].codigo)
            for cartao in self.cartoes.values():
                cartao.definir_marcas(caixas)
            editor = getattr(self, "editor_selecao", None)
            if editor is not None:
                editor.definir_marcas_do_aviso(caixas)
        except Exception:  # noqa: BLE001 - a marca é só um desenho de ajuda
            registrar_erro("marcas do aviso", traceback.format_exc())

    def _com_andamento(self, texto: str) -> str:
        """O texto da faixa, com o andamento da conversao das marcacoes no
        fim enquanto ela roda (decisao Z1 (b)). Sem conversao, o texto como
        sempre."""
        if not self._andamento_das_marcacoes:
            return texto
        return f"{texto}  -  {self._andamento_das_marcacoes}"

    def mostrar_andamento_das_marcacoes(self, feitas: int, total: int) -> None:
        """Decisao Z1 (b) do Samuel (05/10/2026): enquanto a janela converte
        por tras as zonas do livro para o formato novo, a faixa azul (o aviso
        que ja existe nesta tela) diz "Preparando as marcações do livro…
        12 de 50". Sem tela nova e sem botao: o Kaique continua trabalhando.
        total 0, ou feitas >= total, tira o andamento. Seguro mudar: a frase.
        """
        texto = ""
        if total > 0 and feitas < total:
            texto = f"Preparando as marcações do livro… {feitas} de {total}"
        if texto == self._andamento_das_marcacoes:
            return
        self._andamento_das_marcacoes = texto
        if self.projeto is not None and self.projeto.paginas and not self._carregando:
            try:
                self._atualizar_faixa()
            except Exception:  # noqa: BLE001 - o andamento nunca derruba a tela
                registrar_erro("andamento_das_marcacoes", traceback.format_exc())

    def _texto_tranquilo(self, aba: str) -> str:
        assert self.projeto is not None
        if aba == ABA_CORTE:
            folha = self.projeto.folhas[self.indice_folha]
            if not folha.dividir:
                return "Esta folha não vai ser dividida."
            return ("Achei a lombada e vou cortar na linha azul. "
                    "Se estiver errado, arraste a linha.")
        if aba == ABA_BORDAS:
            pagina = self.projeto.paginas[self.indice_pagina]
            if pagina.recorte is None:
                return "Vou cortar a borda sozinho. Arraste o retângulo se quiser mudar."
            return "Você ajustou o corte desta página."
        if aba == ABA_ANGULO:
            pagina = self.projeto.paginas[self.indice_pagina]
            if pagina.angulo_manual is None:
                return ("Vou endireitar sozinho. Para acertar à mão: arraste a bolinha "
                        "azul, ou desenhe a linha laranja em cima de uma linha do texto.")
            return f"Você girou esta página em {_graus(pagina.angulo_manual)}."
        pagina = self.projeto.paginas[self.indice_pagina]
        if pagina.filtro == TIRAR_FUNDO:
            # item 1.1: "vai sair em Tirar o fundo" nao se le bem; e se o
            # core/camadas.py deixar a pagina intacta, ela sai como veio
            return ("Vou tirar o fundo desta página. Onde não der, "
                    "ela sai como veio.")
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        return f"Esta página vai sair em {nome}."

    def _pintar_faixa(self, alerta: bool) -> None:
        """Troca a cor da faixa.

        A folha de estilo e aplicada direto no widget, sem buscar ninguem por
        propriedade do Qt e sem repolir a arvore inteira.
        """
        # Etapa 1 do layout (temas): as cores saem do tema da vez, e a troca
        # de tema repinta a faixa sem esperar a próxima atualização.
        def montar() -> str:
            borda = estilo.cor("aviso_b") if alerta else estilo.cor("sep")
            fundo = estilo.cor("aviso_f") if alerta else estilo.cor("bar2")
            return (f"QFrame#faixaInfo {{ background: {fundo}; border: 1px solid {borda};"
                    f" border-radius: 8px; }} QLabel {{ background: transparent; border: none; }}")
        estilo.estilizar(self.faixa, montar)

    def _botoes_do_aviso_sem_foco(self, aba: str) -> None:
        """Os botões do aviso desta aba nunca ficam com o foco do teclado.

        O defeito (verificador, 13/10/2026): depois de clicar num botão do
        aviso o foco ficava nele; a seta para a direita pulava para outro
        botão em vez de trocar de página, e a barra de espaço apertava o botão
        em vez de "está certo e avança" - até um botão já escondido engolia a
        barra de espaço. Sem foco (como os botões da aba Endireitar), o clique
        do mouse funciona igual e o teclado continua sendo da página.
        Arriscado: tirar isto de um dos três."""
        for botoes in (self.botoes_de_sugestao, self.botoes_de_sugestao_2,
                       self.botoes_de_sugestao_3):
            botao = botoes.get(aba)
            if botao is not None:
                botao.setFocusPolicy(Qt.NoFocus)

    def _botoes_do_aviso(self, item, codigo: str) -> list[tuple[str, str]]:
        """Os botões do aviso `codigo` que valem para esta folha ou página
        AGORA: os do aviso (analise.Alerta.botoes) menos os que não fariam
        nada. Hoje só um caso: "usar mais escuro" / "usar mais fraco" com a
        força do preto já nesse valor (verificador, 13/10: no Egenloff 3 o
        aviso "Texto falhado" oferecia "usar mais escuro" com a força já em
        85). A faixa (_atualizar_faixa) e o clique (_aplicar_sugestao) usam
        esta mesma lista: o botão que aparece é o que age."""
        botoes = analise.descrever(codigo).botoes
        forca = getattr(item, "forca_preto", None)
        if forca is None:
            return botoes
        ja_esta = {"forca:mais_escuro": int(forca) >= FORCA_DO_REFORCO,
                   "forca:mais_fraco": int(forca) <= FORCA_MAIS_FRACA}
        return [(rotulo, correcao) for rotulo, correcao in botoes if not ja_esta.get(correcao, False)]

    def _mostrar_sugestao(self, aba: str, rotulo: str | None, qual: int = 0) -> None:
        """Mostra (com o rótulo) ou esconde (None) um botão do aviso na aba:
        qual=0 o primeiro, 1 o segundo (12/10/2026), 2 o terceiro (13/10)."""
        botao = (self.botoes_de_sugestao, self.botoes_de_sugestao_2,
                 self.botoes_de_sugestao_3)[qual].get(aba)
        if botao is None:
            return
        botao.setVisible(bool(rotulo))
        if rotulo:
            botao.setText(rotulo)

    def _atualizar_botoes(self) -> None:
        assert self.projeto is not None and self.acoes is not None

        self.botao_desfazer.setEnabled(self.acoes.pode_desfazer)
        self.botao_desfazer.setToolTip(self.acoes.descricao_desfazer())
        self.botao_refazer.setEnabled(self.acoes.pode_refazer)
        self.botao_refazer.setToolTip(self.acoes.descricao_refazer())

        if ABA_CORTE in self._abas_ativas:
            folha = self.projeto.folhas[self.indice_folha]
            self.botao_nao_dividir.setText(
                "dividir esta" if not folha.dividir else "não dividir esta"
            )
            # Obra 26/10, etapa 4 ("'dividir esta' sempre ativo"; promessa
            # P-059): aceso em toda folha, inclusive a que entrou como uma
            # pagina so (livro aberto sem "Dividir", folha girada depois).
            # Antes ficava cinza, com a dica "aqui nao da para dividi-la".
            self.botao_nao_dividir.setEnabled(True)
            self.botao_nao_dividir.setToolTip(
                "Junta as duas páginas desta folha numa só (as outras folhas não mudam)."
                if folha.dividir else
                "Divide esta folha em duas páginas, na lombada (as outras folhas não mudam).")
            # o jeito desta folha (sem sinal: so mostrar nao e trocar)
            self.combo_jeito_da_folha.blockSignals(True)
            self.combo_jeito_da_folha.setCurrentIndex(self.combo_jeito_da_folha.findData(
                jeito_de_dividir(self.projeto, folha)))
            self.combo_jeito_da_folha.blockSignals(False)
            self.combo_jeito_da_folha.setEnabled(bool(folha.dividir))
            self.rotulo_jeito_da_folha.setEnabled(bool(folha.dividir))

        if ABA_ANGULO in self._abas_ativas:
            self._atualizar_conta_do_endireitar()

        if ABA_FILTRO in self._abas_ativas:
            self._configurar_medidor()
        # "deixar em branco" / "tirar do livro" (os de "Esta página" e os do
        # painel Filtro), em toda ferramenta (etapa 2 da obra)
        self._atualizar_os_botoes_da_pagina()

    def _atualizar_tira(self) -> None:
        assert self.projeto is not None
        itens = (self.projeto.folhas if self.trabalha_com_folhas
                 else self.projeto.paginas)
        # etapa 7 da obra: o "!" é a mesma dúvida da faixa (com os avisos da
        # folha nas páginas dela) e o tique é o "está certo" (D-010: "a folha
        # fica conferida, tique na miniatura")
        com_duvida = self._itens_com_duvida()
        for i, item in enumerate(itens):
            self.tira.marcar(i, em_alerta=i in com_duvida,
                             apagada=getattr(item, "apagada", False),
                             conferida=bool(item.revisada))
        self.tira.definir_giros(self._giros_das_folhas())      # D2: so as que mudaram
        self.tira.selecionar(self.indice_atual)

    def _atualizar_contador(self) -> None:
        assert self.projeto is not None
        # etapa 7 da obra: o número de dúvidas de todo lugar (lista única 5.5)
        pendentes = avisos_do_livro.quantas_com_duvida(self.projeto)
        apagadas = self.projeto.total_apagadas

        if pendentes == 0:
            texto = "tudo certo"
        elif pendentes == 1:
            texto = "1 página para você olhar"
        else:
            texto = f"{pendentes} páginas para você olhar"
        if apagadas:
            texto += f"  -  {apagadas} apagadas"
        self.botao_alertas.setText(texto)
        self.botao_alertas.setEnabled(pendentes > 0)
        # o "próxima dúvida" da faixa (etapa 3 do layout) so acende quando ha
        # outra folha/pagina com duvida para onde ir (etapa 7: antes acendia
        # no Dividir com duvida so de pagina, e o clique nao fazia nada)
        outras = self._itens_com_duvida() - {self.indice_atual}
        self.botao_proxima_duvida.setEnabled(bool(outras))

        observacoes = getattr(self.projeto, "observacoes", [])
        self.rotulo_observacoes.setVisible(bool(observacoes))
        if observacoes:
            self.rotulo_observacoes.setText("   -   " + "; ".join(observacoes))
        # O rodapé ("N de M conferidas · K com dúvida") conta as mesmas
        # páginas: acerta junto. O defeito (verificador, 20/10/2026): quando
        # um aviso chegava com a medida por trás, o contador de cima mudava e
        # o rodapé só acertava na troca de página (um passo atrasado), porque
        # só atualizar() o refazia. Arriscado: tirar esta linha.
        self._atualizar_barra_de_baixo()

    @protegido
    def _previa_chegou(self, chave: str, _img: np.ndarray) -> None:
        """Uma prévia ficou pronta; se for a que estamos vendo, redesenha."""
        if not self._pronta():
            return
        assert self.previas is not None
        # etapa 6: o lado a lado e o "antes / depois" mostram prévias também
        visivel = self.vista_da_pagina.currentWidget()
        if visivel is self.lado_a_lado:
            self.lado_a_lado.atualizar_imagens()
        elif visivel is self.vista_antes_depois and chave.startswith(f"{self.indice_pagina}:"):
            self._mostrar_antes_depois()
        esperadas = (
            self.previas.chave(self.indice_pagina, self._dpi_atual),
            self.previas.chave_folha(self.indice_folha, DPI_PREVIA),
            self.previas.chave_para_recorte(self.indice_pagina, self._dpi_atual),
        )
        if chave in esperadas or chave.startswith("folha:"):
            self._atualizar_previa()
        elif (not self.trabalha_com_folhas
              and chave.startswith(f"{self.indice_pagina}:{self._dpi_atual}:")):
            # "Força do preto sozinha" (12/10/2026): a prévia que chegou é
            # desta página, mas de um estado que mudou DURANTE o desenho (o
            # programa escureceu a força, e a força entra na chave). Sem isto
            # a tela ficaria esperando uma prévia que ninguém pediu: pede a de
            # agora e acerta a faixa e o medidor. Não entra em laço: o reforço
            # só acontece uma vez por página.
            self._atualizar_previa()
            self._alertas_da_previa()
        elif (not self.trabalha_com_folhas
              and chave.startswith(f"{self.indice_pagina}{MARCA_DA_MEDIDA}")):
            # Chegou a medida do "Para revisar" da página da vez (feita por
            # trás, na resolução do PDF): os avisos, as marcas de "onde sumiu"
            # e a força do preto podem ter mudado. Se a força mudou (a "força
            # do preto sozinha"), a prévia de agora é outra: pede.
            self._atualizar_previa()
            self._alertas_da_previa()
        if chave == esperadas[0] and not self.trabalha_com_folhas:
            self._alertas_da_previa()
            # item 2.2: a previa mediu as duas contas do endireitar
            if ABA_ANGULO in self._abas_ativas:
                self._atualizar_conta_do_endireitar()
        # Item 1.1: chegou o cartao "Tirar o fundo" da pagina da vez.
        if (self._cartoes_a_vista() and TIRAR_FUNDO in self.cartoes
                and chave == self.previas.chave_com_filtro(
                    self.indice_pagina, DPI_CARTAO_SEM_FUNDO, TIRAR_FUNDO)):
            self._cartao_sem_fundo(_img)
        # Modo Misto (bug Misto 2): chegou o cartao "Preto e branco" com o
        # "So as letras" da pagina da vez (a chave inclui as escolhas do
        # Misto: uma que chegue atrasada, de antes de uma mudanca, nao serve)
        if (self._cartoes_a_vista() and self.projeto is not None
                and 0 <= self.indice_pagina < len(self.projeto.paginas)
                and self._cartao_pb_pelo_misto(self.projeto.paginas[self.indice_pagina])
                and chave == self.previas.chave_com_filtro(
                    self.indice_pagina, DPI_CARTAO_DO_MISTO, PRETO_E_BRANCO)):
            self._cartao_do_misto(_img)

    def _alertas_da_previa(self) -> None:
        """A prévia da página que está na tela pode ter mudado os alertas dela.

        Item 1.1 (29/09/2026): o alerta "conferir o fundo tirado" só é
        conhecido quando a página é desenhada (core.pipeline._anotar_conferir,
        numa tarefa de fundo), não na análise. Sem isto a faixa laranja, a
        miniatura e o contador só apareceriam ao virar a página. Só redesenha
        se os alertas mudaram desde a última vez (a tira tem uma miniatura por
        página).

        Os painéis da direita também (_atualizar_paineis): sem isso o "Para
        revisar" ficava "nada pendente" até virar a página, com a faixa e a
        miniatura já mostrando o alerta (bug do verificador, 29/09, print
        t03-cinco-cartoes-alerta-mas-para-revisar-vazio.jpg). Seguro: é o
        mesmo que atualizar() faz a cada mudança, e aqui só roda quando os
        alertas da página mudaram.
        """
        item = self.item_atual
        # 12/10/2026: entram também as marcas de "onde sumiu" (chegam com a
        # prévia) e a força do preto (a "força do preto sozinha" pode tê-la
        # escurecido durante o desenho: o medidor tem de mostrar a nova)
        marcas = tuple(marcas_do_aviso(item)) if hasattr(item, "filtro") else ()
        # etapa 7: os avisos da folha da página também (aparecem na faixa dela)
        folha = (self.projeto.folhas[self.indice_folha]
                 if self.projeto is not None and 0 <= self.indice_folha < len(self.projeto.folhas)
                 else None)
        da_folha = ((tuple(folha.alertas), folha.revisada, tuple(folha.alertas_aceitos))
                    if folha is not None else ())
        estado = (self.indice_pagina, tuple(item.alertas), item.revisada, marcas,
                  getattr(item, "forca_preto", None), da_folha)
        if estado == getattr(self, "_alertas_vistos", None):
            return
        self._alertas_vistos = estado
        if self.projeto is not None and acertar_faixa_do_livro(self.projeto):
            self._atualizar_tira()        # a faixa virou (ou deixou de ser) aviso do livro
        self._atualizar_faixa()
        self._atualizar_botoes()
        self._atualizar_tira()       # etapa 7: o aviso de folha muda duas miniaturas
        self._atualizar_contador()
        self._atualizar_paineis()

    # ------------------------------------------------------------------
    # alteracoes (todas passam pelo historico)
    # ------------------------------------------------------------------

    def _registrar(self, tipo: str, alvo: str, indices: list[int],
                   campos: dict, descricao: str) -> None:
        """Aplica a mudanca e guarda no histórico, numa acao só.

        Pendencia da D2 (06/10/2026): se a mudanca mexe no preparo (giro,
        divisao, linha de corte, borda, angulo) de alguma pagina com zonas
        ainda no formato antigo, nao aplica: espera a conversao e avisa
        (_espera_pelas_marcacoes)."""
        assert self.projeto is not None and self.acoes is not None
        if self._espera_pelas_marcacoes(alvo, indices, campos):
            return
        campos = self._com_a_marca_mexida_a_mao(alvo, indices, campos)
        acao = montar_acao(self.projeto, tipo, alvo, indices, campos, descricao)
        aplicar(self.projeto, acao, acao.depois)
        self.acoes.registrar(acao)

        if dividir_a_mao.muda_a_lista(campos):
            # obra 26/10, etapa 4: dividir/juntar uma folha a mao muda os
            # numeros das paginas dela em diante (as prévias guardam pelo
            # numero): limpa todas e remonta a tira, como o Automatico
            if self.previas is not None:
                self.previas.invalidar()
            self.lista_de_paginas_mudou()
            if alvo == "folha":            # D-497 (etapa 7): a página que ficou branca
                self._medir_o_em_branco_por_tras(self._paginas_das_folhas(indices))
            return
        if alvo == "folha" and "posicao_corte" in campos:
            # D-497 (etapa 7): mover a linha pode deixar uma metade só margem
            self._medir_o_em_branco_por_tras(self._paginas_das_folhas(indices))
        afetadas = indices if alvo == "pagina" else self._paginas_das_folhas(indices)
        if self.previas is not None and not set(campos) <= CAMPOS_SO_DO_MOVER:
            # etapa 5 da obra: mover/aumentar nao muda o desenho da pagina (a
            # tela a compoe ao vivo na area branca): nada a desenhar de novo
            for indice in afetadas:
                self.previas.invalidar(indice)
        self.atualizar()

    def _com_a_marca_mexida_a_mao(self, alvo: str, indices: list[int], campos: dict) -> dict:
        """Os campos da acao com a marca "mexida a mao" (core/etapas) de cada
        pagina ou folha, na MESMA acao (o desfazer devolve a marca junto).

        Obra de 26/10/2026, etapa 3 (pendencia da etapa 1; D-004: "Automático
        em livro já mexido à mão: o programa pergunta se quer pular as páginas
        mexidas."; D-009: o feito a mao vale no PDF com a etapa desligada).
        Mexer no corte, no angulo, no filtro da pagina (e nos ajustes dele), no
        mover/tamanho, na divisao/linha ou no giro grava a marca da etapa;
        "usar o corte/angulo do programa" (o valor volta a None) a tira.
        Arriscado: tirar isto (o filtro escolhido a mao com "Limpar" desligado
        nao chegaria ao PDF, e a pergunta do Automatico nao veria a pagina)."""
        assert self.projeto is not None
        itens = self.projeto.folhas if alvo == "folha" else self.projeto.paginas
        tabela = MARCAS_DA_FOLHA if alvo == "folha" else MARCAS_DA_PAGINA
        mexidas = {etapa for campo, etapa in tabela.items() if campo in campos}
        if not mexidas:
            return campos
        marcas = {}
        for indice in indices:
            if not 0 <= indice < len(itens):
                continue
            item = itens[indice]
            lista = list(getattr(item, "mexida_a_mao", []) or [])
            for campo, etapa in tabela.items():
                if campo not in campos:
                    continue
                valor = campos[campo]
                if isinstance(valor, dict):
                    valor = valor.get(str(indice), getattr(item, campo, None))
                if campo in DEVOLVEM_AO_AUTOMATICO and valor is None:
                    lista = [m for m in lista if m != etapa]
                elif etapa not in lista:
                    lista.append(etapa)
            marcas[str(indice)] = lista
        return {**campos, "mexida_a_mao": marcas}

    def _paginas_das_folhas(self, folhas: list[int]) -> list[int]:
        assert self.projeto is not None
        alvo = set(folhas)
        return [p.indice for p in self.projeto.paginas if p.folha in alvo]

    # --- corte ------------------------------------------------------------

    @protegido
    def _mover_corte(self, posicao: float) -> None:
        """A linha azul arrastada: só esta folha (e as páginas dela) mudam.
        Obra 26/10, etapa 4 (D-495): acertar a linha à mão também é dividir à
        mão; na primeira vez nesta rotação, procura a tampa do scanner da
        folha (uns décimos de segundo; depois não procura de novo)."""
        assert self.projeto is not None
        campos = {"posicao_corte": round(posicao, 4), "revisada": True}
        folha = self.projeto.folhas[self.indice_folha]
        if folha.dividir and not dividir_a_mao.tampa_ja_medida(folha):
            from PySide6.QtWidgets import QApplication

            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                campos["tampa_do_scanner"] = dividir_a_mao.medir_a_tampa(
                    self.projeto, self.indice_folha)
            finally:
                QApplication.restoreOverrideCursor()
        self._registrar(
            "mover_corte", "folha", [self.indice_folha], campos,
            f"Linha de corte da folha {self.indice_folha + 1}",
        )

    @protegido
    def _corte_em_todas(self) -> None:
        assert self.projeto is not None
        posicao = self.projeto.folhas[self.indice_folha].posicao_corte
        indices = [f.indice for f in self.projeto.folhas]
        self._registrar(
            "aplicar_em_todas", "folha", indices,
            {"posicao_corte": round(posicao, 4)},
            f"Linha de corte de todas as {len(indices)} folhas",
        )

    @protegido
    def _alternar_dividir(self) -> None:
        """O botão "não dividir esta" / "dividir esta" da ferramenta Dividir.

        Obra 26/10/2026, etapa 4 (plano: "'dividir esta' sempre ativo";
        Samuel, sessão 1: "eu posso entrar ali e mudar a marcação de folhas
        erradas"; promessa P-059). Dividida, junta (_nao_dividir); não
        dividida, divide (_dividir_esta) - inclusive a folha que entrou como
        uma página só (livro aberto sem "Dividir", folha girada depois: lista
        única 3.1), que antes deixava o botão cinza. Cada clique é UMA ação do
        desfazer e mexe só nas páginas desta folha (core/dividir_a_mao)."""
        assert self.projeto is not None
        if self.projeto.folhas[self.indice_folha].dividir:
            self._nao_dividir()
        else:
            self._dividir_esta()

    @protegido
    def _nao_dividir(self) -> None:
        """"não dividir esta" (botão da ferramenta e o do aviso "Não parece
        dupla"): as duas páginas da folha viram uma só, e as duas ficam
        guardadas para o "dividir esta" devolver (core/dividir_a_mao.
        campos_para_juntar). Folha já não dividida: só fica conferida - é o
        que o aviso "Esta folha parece ter uma página só" quer (antes da etapa
        4 era o mesmo; ele NUNCA divide).
        Até a etapa 4 a página da direita ficava na lista, "apagada", e a
        tira mostrava a folha duas vezes (a lista de páginas não podia
        mudar na conferência)."""
        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        if not folha.dividir and len(dividir_a_mao.paginas_da_folha(
                self.projeto, self.indice_folha)) < 2:
            self._marcar_revisada()
            return
        self._registrar(
            "nao_dividir", "folha", [self.indice_folha],
            dividir_a_mao.campos_para_juntar(self.projeto, self.indice_folha),
            f"Folha {self.indice_folha + 1}: não dividir")

    @protegido
    def _dividir_esta(self) -> None:
        """"dividir esta": a folha passa a sair como duas páginas.

        - Folha que a pessoa juntou antes ("não dividir esta"): as duas
          páginas voltam como estavam, na linha de antes (sem medir nada).
        - Folha com uma página só: acha a lombada na folha como ela está
          (girada, se foi girada: lista única 3.1), pelo jeito da folha ou do
          livro, e a tampa do scanner em volta do livro (D-495: sai branca);
          leva uns décimos de segundo (core/dividir_a_mao.medir_para_dividir).
        Uma ação do desfazer; grava a marca "mexida à mão" (_registrar)."""
        from PySide6.QtWidgets import QApplication

        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        pags = dividir_a_mao.paginas_da_folha(self.projeto, self.indice_folha)
        devolve = len(pags) >= 2 or bool(folha.metades_guardadas)
        if devolve and dividir_a_mao.tampa_ja_medida(folha):
            campos = dividir_a_mao.campos_para_dividir(self.projeto, self.indice_folha)
        else:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                lombada, tampa = dividir_a_mao.medir_para_dividir(
                    self.projeto, self.indice_folha, jeito_de_dividir(self.projeto, folha))
            finally:
                QApplication.restoreOverrideCursor()
            if devolve:        # as páginas de antes voltam, na linha de antes
                campos = dividir_a_mao.campos_para_dividir(self.projeto, self.indice_folha,
                                                           tampa=tampa)
            else:
                campos = dividir_a_mao.campos_para_dividir(
                    self.projeto, self.indice_folha, lombada.posicao, lombada.confianca, tampa)
        self._registrar("dividir_a_mao", "folha", [self.indice_folha], campos,
                        f"Folha {self.indice_folha + 1}: dividir")

    @protegido
    def _trocar_jeito_da_folha(self) -> None:
        """Item 2.1: a lista "jeito:" da aba Onde cortar. Recalcula a divisao
        DESTA folha pelo jeito escolhido (uns decimos de segundo: abre a folha
        a 150 DPI) e grava numa acao so (o desfazer devolve o jeito e a linha
        de antes). A folha continua dividida (o ScanTailor e chamado no modo
        "duas paginas"). Escolher o jeito do livro volta a "seguir o livro"
        (ConfigFolha.dividir_como None)."""
        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        jeito = dividir_scantailor.jeito_valido(self.combo_jeito_da_folha.currentData())
        if not folha.dividir or jeito == jeito_de_dividir(self.projeto, folha):
            return
        from PySide6.QtWidgets import QApplication

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            lombada = recalcular_divisao(self.projeto, self.indice_folha, jeito, forcar=True)
        finally:
            QApplication.restoreOverrideCursor()
        do_livro = dividir_scantailor.jeito_valido(getattr(self.projeto, "dividir_como", None))
        self._registrar(
            "jeito_de_dividir", "folha", [self.indice_folha],
            {"dividir_como": None if jeito == do_livro else jeito,
             "posicao_corte": round(float(lombada.posicao), 4),
             "confianca_corte": float(lombada.confianca), "revisada": True},
            f"Folha {self.indice_folha + 1}: dividir pelo jeito "
            f"“{nome_do_jeito_de_dividir(jeito)}”",
        )

    @protegido
    def _girar(self) -> None:
        """O botao "girar" da aba Onde cortar e o menu Pagina > "Girar 1/4 a
        direita": o mesmo giro de sempre (90 graus no sentido do relogio),
        agora obedecendo o "aplicar em" da barrinha de girar (item 2.3)."""
        self._girar_folhas(girar.GIRO_DIREITA)

    def _girar_esquerda(self) -> None:
        """Menu Pagina > "Girar 1/4 a esquerda"."""
        self._girar_folhas(girar.GIRO_ESQUERDA)

    def _girar_meia_volta(self) -> None:
        """Menu Pagina > "Girar meia volta"."""
        self._girar_folhas(girar.GIRO_MEIA_VOLTA)

    @protegido
    def _girar_folhas(self, giro: int, so_esta: bool = False) -> None:
        """Gira as folhas do "aplicar em" (item 2.3; core/girar.py).

        Uma acao so do desfazer para todas as folhas. Todas terminam viradas
        como a folha da vez (decisao do Samuel, 06/10/2026: a da vez gira a
        partir de onde esta e as outras copiam o giro final dela -
        core/girar.campos_do_giro); o Ctrl+Z devolve a cada uma o giro que
        ela tinha. O resto vem sozinho: a previa e refeita (a
        rotacao entra na chave), e o corte, a divisao e o endireitar sao
        recalculados na folha girada (core/pipeline); as zonas da aba Marcar
        sao levadas para o mesmo pedaco do papel quando a pagina e desenhada
        (core/zonas_na_folha.acompanhar).

        A folha da vez e a da pagina na tela (indice_folha acompanha a
        pagina em todas as abas).

        "So as pares" numa folha impar (ou "so as impares" numa par): avisa
        e nao gira nada, nem entra no historico (decisao do Samuel,
        06/10/2026: "O programa avisa: 'va a uma folha par'"; a frase vem de
        core/girar.aviso_fora_do_alcance). Vale para o botao, o menu Pagina
        e as teclas, que passam todos por aqui.
        """
        if not self._pronta():
            return
        assert self.projeto is not None
        # so_esta: os botoes do canto da pagina, que giram sempre so a folha
        # da vez, qualquer que seja o "aplicar em" do painel (rodada 13, 803 B)
        alcance = girar.ALCANCE_ESTA if so_esta else self.barra_girar.alcance()
        aviso = girar.aviso_fora_do_alcance(self.indice_folha, alcance)
        if aviso:
            janela = self.window()
            if janela is not self and hasattr(janela, "avisar"):
                janela.avisar(aviso)
            return
        indices = girar.folhas_do_alcance(len(self.projeto.folhas), self.indice_folha, alcance)
        if not indices or self._marcacoes_ainda_no_formato_antigo(indices):
            return
        self._registrar(
            "girar", "folha", indices,
            girar.campos_do_giro(self.projeto.folhas, indices, giro, self.indice_folha),
            girar.descricao_do_giro(giro, alcance, self.indice_folha, len(indices)),
        )

    def _marcacoes_ainda_no_formato_antigo(self, folhas: list[int]) -> bool:
        """Alguma pagina destas folhas tem zonas da aba Marcar que ainda nao
        foram convertidas para a folha original (projeto de antes de 05/10,
        com a conversao por tras ainda andando - a faixa azul "Preparando as
        marcações do livro")? Entao o giro espera: girar antes levaria as
        zonas dessas paginas para o lugar errado do papel (a conta precisa do
        preparo de ANTES do giro, que so a conversao anota).

        Avisa (janela.avisar) e pede a conversao, se ela nao estiver
        andando (sinal marcacoes_por_converter). Devolve True se o giro deve
        esperar. Seguro mudar: a frase. Arriscado: girar mesmo assim.
        """
        from core.zonas_na_folha import paginas_por_converter

        assert self.projeto is not None
        alvo = set(folhas)
        if not any(p.folha in alvo for p in paginas_por_converter(self.projeto)):
            return False
        self._avisar_que_as_marcacoes_estao_sendo_preparadas(
            "Ainda estou preparando as marcações destas folhas (a faixa azul "
            "mostra o andamento). Quando terminar, gire de novo: assim as "
            "marcações acompanham o giro.")
        return True

    # O que muda o preparo de uma pagina (girar 90 -> dividir -> cortar ->
    # endireitar), e portanto o lugar das zonas da aba Marcar na pagina
    # desenhada: os campos de core/pipeline._entradas_do_preparo que uma acao
    # da tela pode mudar. Seguro: acrescentar campo. Arriscado: tirar algum.
    CAMPOS_DO_PREPARO = frozenset({"rotacao", "dividir", "posicao_corte",
                                   "recorte", "angulo_manual",
                                   "endireitar_como"})        # item 2.2

    # O aviso "Um momento" do desfazer, do refazer e do Historico. Ressalva 3
    # do verificador-3 (06/10/2026): eles usavam a frase da mudanca feita na
    # tela ("desta pagina", "faca a mudanca de novo"), mas a pagina atingida
    # pode nao ser a da tela, e o que a pessoa refaz e o Ctrl+Z, nao a
    # mudanca. Seguro mudar: o texto.
    FRASE_DO_DESFAZER_ESPERA = (
        "Ainda estou preparando as marcações do livro (a faixa azul mostra o "
        "andamento). O que você pediu mexe numa página que ainda não está "
        "pronta, por isso nada mudou. Quando terminar, tente de novo.")

    def _espera_pelas_marcacoes(self, alvo: str, indices: list[int], campos: dict,
                                frase: str | None = None) -> bool:
        """A pendencia da D2 (anotada pelo implementador do girar, 06/10/2026):
        mudar o corte, a borda, a divisao ou o angulo de uma pagina cujas
        zonas ainda estao no formato antigo (projeto de antes de 05/10, com a
        conversao por tras ainda andando) deslocava as zonas - a conta que as
        leva para o preparo novo precisa do preparo de ANTES, que so a
        conversao anota. Recebe a mesma protecao do giro (9f8d4e5): a mudanca
        espera, a tela avisa e pede a conversao (se ela tiver parado).

        Escolhido em vez de converter a pagina na hora: converter precisa
        desenhar a folha na resolucao do PDF para medir o corte e o angulo
        automaticos (0,5 a 2 s), o que pararia a janela; e a conversao do
        livro inteiro ja esta andando (Boecio, 50 paginas: ~3 s).

        Vale para tudo que passa por _registrar e para desfazer, refazer e o
        Historico (o historico de acoes volta ao abrir o livro: um Ctrl+Z de
        outra sessao tambem mudaria o preparo). Devolve True se deve esperar.
        frase: o aviso, no lugar do da mudanca feita na tela (o desfazer usa
        FRASE_DO_DESFAZER_ESPERA). Seguro mudar: a frase. Arriscado:
        aplicar mesmo assim.
        """
        if self.projeto is None or not (self.CAMPOS_DO_PREPARO & set(campos)):
            return False
        from core.zonas_na_folha import paginas_por_converter

        pendentes = paginas_por_converter(self.projeto)
        if not pendentes:
            return False
        alvo_indices = set(indices)
        if alvo == "folha":
            atingidas = [p for p in pendentes if p.folha in alvo_indices]
        else:
            atingidas = [p for p in pendentes if p.indice in alvo_indices]
        if not atingidas:
            return False
        if frase is None and "rotacao" in campos:
            frase = ("Ainda estou preparando as marcações destas folhas (a faixa azul "
                     "mostra o andamento). Quando terminar, gire de novo: assim as "
                     "marcações acompanham o giro.")
        elif frase is None:
            frase = ("Ainda estou preparando as marcações desta página (a faixa azul "
                     "mostra o andamento). Quando terminar, faça a mudança de novo: "
                     "assim as marcações acompanham o corte e o ângulo.")
        self._avisar_que_as_marcacoes_estao_sendo_preparadas(frase)
        return True

    def _acoes_esperam_pelas_marcacoes(self, acoes, para_tras: bool) -> bool:
        """Desfazer/refazer/Historico: alguma destas acoes mudaria o preparo
        de uma pagina com zonas antigas (_espera_pelas_marcacoes)? para_tras:
        desfazendo (aplica o `antes` de cada uma) ou refazendo (o `depois`).
        O aviso e o do desfazer (FRASE_DO_DESFAZER_ESPERA): nao fala "desta
        pagina", que pode nao ser a da tela."""
        for acao in acoes:
            campos = acao.antes if para_tras else acao.depois
            if self._espera_pelas_marcacoes(acao.alvo, acao.indices, campos,
                                            frase=self.FRASE_DO_DESFAZER_ESPERA):
                return True
        return False

    def _avisar_que_as_marcacoes_estao_sendo_preparadas(self, frase: str) -> None:
        """Pede a conversao das zonas (sinal marcacoes_por_converter; a janela
        recomeca a tarefa se ela tiver parado) e mostra `frase`."""
        self.marcacoes_por_converter.emit()
        janela = self.window()
        if janela is not self and hasattr(janela, "avisar"):
            janela.avisar(frase, titulo="Um momento")

    # --- bordas -----------------------------------------------------------

    @protegido
    def _mover_recorte(self, recorte: tuple) -> None:
        arredondado = [round(float(v), 4) for v in recorte]
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": arredondado, "revisada": True},
            f"Corte de borda da página {self.indice_pagina + 1}",
        )

    @protegido
    def _sem_recorte(self) -> None:
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": [0.0, 0.0, 1.0, 1.0], "revisada": True},
            f"Não cortar a borda da página {self.indice_pagina + 1}",
        )

    @protegido
    def _usar_corte_alargado(self) -> None:
        """Item 2.5, g8-moldura-tinta-fora ("ele avisa e da opção e de mudar o
        corte e mostrar ele alargado com o que foi tirado"): troca o corte desta
        pagina pelo corte alargado (core.pipeline.corte_alargado), que passa a
        valer como corte a mao. Desfaz com Ctrl+Z; "usar o corte do programa"
        volta ao do conteudo. Sem corte alargado (ainda nao medido), so marca
        como conferida."""
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        alargado = corte_alargado(self.projeto, pagina)
        if alargado is None:
            self._marcar_revisada()
            return
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": [float(v) for v in alargado], "revisada": True},
            f"Corte alargado na página {self.indice_pagina + 1}",
        )

    @protegido
    def _alinhar_com_as_outras(self) -> None:
        """Item 2.5, g9-pagina-muito-maior: poe de volta na conta do tamanho do
        livro a pagina que o programa deixou de fora sozinho (o aviso deixa
        desfazer). Desfaz com Ctrl+Z."""
        self._registrar(
            "alinhar", "pagina", [self.indice_pagina],
            {"alinhar_com_as_outras": True, "revisada": True},
            f"Página {self.indice_pagina + 1} do tamanho das outras",
        )

    @protegido
    def _recorte_automatico(self) -> None:
        self._registrar(
            "recortar", "pagina", [self.indice_pagina], {"recorte": None},
            f"Voltar ao corte automático na página {self.indice_pagina + 1}",
        )

    @protegido
    def _recorte_em_todas(self) -> None:
        """O "usar em todas" do Cortar. Item 2.13 (pedido do Samuel, rodada 4,
        08/10/2026, e bug da Lista de bugs de 08/10: "usar em todas" apagava as
        excecoes por pagina): antes de aplicar, a janela "Em quais paginas?"
        (ui/dialogo_escolher_paginas) mostra as paginas, com as excecoes
        desmarcadas de fabrica e "Selecionar todas" / "Nenhuma". So as
        marcadas recebem o corte; cancelar nao muda nada."""
        assert self.projeto is not None
        recorte = self.projeto.paginas[self.indice_pagina].recorte
        campos = {"recorte": list(recorte) if recorte else None}
        # pendencia da D2: com marcacoes ainda no formato antigo, avisa e nao
        # abre a janela (o mesmo que _registrar faria depois)
        if self._espera_pelas_marcacoes("pagina", [p.indice for p in self.projeto.paginas], campos):
            return
        indices = self._escolher_paginas_do_corte()
        if not indices:
            return
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"recorte": list(recorte) if recorte else None},
            f"Corte de borda em {len(indices)} páginas",
        )

    def _escolher_paginas_do_corte(self) -> list[int]:
        """Abre a janela "Em quais paginas?" e devolve as marcadas (vazio se
        cancelou). Separado para os testes trocarem a janela."""
        from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

        dialogo = DialogoEscolherPaginas(self.projeto, self.indice_pagina, self)
        if dialogo.exec() != DialogoEscolherPaginas.Accepted:
            return []
        return dialogo.escolhidas()

    @protegido
    def _mover_conteudo(self, retangulo: tuple) -> None:
        """Fase 2+3 (aprovadas pelo Samuel em 22/09/2026): arrastar E
        redimensionar o CONTEÚDO dentro da folha - grava
        `conteudo_deslocamento` e `conteudo_escala` juntos, numa ação só.

        Etapa 5 da obra (D-008): é o soltar do mouse na ferramenta Mover, com
        ou sem tamanho de folha (sem folha, a área branca é a própria página).
        `retangulo` vem do widget em fração da área branca MOSTRADA; a conta
        para o formato salvo é feita em pontos (_gravar_o_retangulo), contra a
        área branca que o PDF vai usar. Antes só valia com uma folha escolhida
        (`if pagina.tamanho_folha_cm is None: return`) - era o "Mover
        conteúdo" preso às Bordas.
        """
        if not self._pronta() or self.projeto is None:
            return
        self._gravar_o_retangulo(retangulo, f"Posição/tamanho do conteúdo na página "
                                            f"{self.indice_pagina + 1}")

    # --- angulo -----------------------------------------------------------

    def _paginas_do_alcance_do_angulo(self, atual: int) -> list[int] | None:
        """As paginas do "aplicar em" da aba Endireitar (item 2.2, G5), ou
        None quando a pagina da vez fica fora dele ("so as pares" numa
        impar): ai avisa e nada muda, como no girar (core/girar)."""
        assert self.projeto is not None
        alcance = self.combo_alcance_do_angulo.currentData() if hasattr(
            self, "combo_alcance_do_angulo") else girar.ALCANCE_ESTA
        aviso = girar.aviso_fora_do_alcance(atual, alcance, "página")
        if aviso:
            janela = self.window()
            if janela is not self and hasattr(janela, "avisar"):
                janela.avisar(aviso)
            return None
        return girar.folhas_do_alcance(len(self.projeto.paginas), atual, alcance)

    def _mudar_o_angulo(self, atual: int, campos: dict, descricao_de_uma: str,
                        descricao_de_varias: str) -> None:
        """Grava o angulo (campos) na pagina `atual` e nas do "aplicar em",
        numa acao so. So a pagina da vez fica "conferida"."""
        indices = self._paginas_do_alcance_do_angulo(atual)
        if not indices:
            return
        campos = self._com_o_retangulo_do_corte(indices, campos)
        if indices == [atual]:
            self._registrar("ajustar_angulo", "pagina", indices,
                            {**campos, "revisada": True}, descricao_de_uma)
        else:
            self._registrar("ajustar_angulo", "pagina", indices, campos,
                            descricao_de_varias.format(n=len(indices)))

    def _jeito_do_retangulo(self, pagina) -> str:
        """D-094: "fica" ou "acompanha" para esta pagina - a dela, a do livro
        (Automatico) ou a das Configuracoes (de fabrica "fica", D-093)."""
        from core.pipeline import RETANGULO_ACOMPANHA, RETANGULO_PADRAO

        jeito = getattr(pagina, "retangulo_do_corte", None) or getattr(
            self.projeto, "retangulo_do_corte", None)
        if not jeito:
            import configuracoes

            jeito = configuracoes.ler("retangulo_do_corte") or RETANGULO_PADRAO
        return jeito if jeito == RETANGULO_ACOMPANHA else RETANGULO_PADRAO

    def _proporcao_da_pagina(self, pagina) -> float | None:
        """Largura / altura da pagina girada de 90 e dividida, antes do corte
        (o que recorte_depois_de_mudar_o_angulo precisa), pelo tamanho da
        folha no PDF (lido uma vez por livro). None se nao der para saber."""
        assert self.projeto is not None
        caminho = self.projeto.caminho_entrada
        if getattr(self, "_tamanhos_das_folhas", (None,))[0] != caminho:
            try:
                from core.pdf_io import abrir_pdf, info_paginas

                doc = abrir_pdf(caminho)
                try:
                    tamanhos = [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)]
                finally:
                    doc.close()
            except Exception:  # noqa: BLE001 - sem o tamanho, o corte fica como esta
                registrar_erro("proporcao da pagina", traceback.format_exc())
                return None
            self._tamanhos_das_folhas = (caminho, tamanhos)
        tamanhos = self._tamanhos_das_folhas[1]
        if not 0 <= pagina.folha < len(tamanhos):
            return None
        largura, altura = tamanhos[pagina.folha]
        folha = self.projeto.folhas[pagina.folha]
        if int(folha.rotacao) % 180 == 90:
            largura, altura = altura, largura
        if folha.dividir and pagina.metade in ("esquerda", "direita"):
            parte = folha.posicao_corte if pagina.metade == "esquerda" else 1 - folha.posicao_corte
            largura *= max(0.05, float(parte))
        return float(largura) / max(1.0, float(altura))

    def _com_o_retangulo_do_corte(self, indices: list[int], campos: dict) -> dict:
        """D-093/D-094: com o angulo mudando, o corte a mao de cada pagina vai
        junto na MESMA acao, se a escolha for "acompanha o texto" (core/
        pipeline.recorte_depois_de_mudar_o_angulo); "fica no mesmo lugar" (de
        fabrica) nao muda os numeros do corte."""
        from core.pipeline import RETANGULO_ACOMPANHA, angulo_da_pagina, recorte_depois_de_mudar_o_angulo

        if "angulo_manual" not in campos or self.projeto is None:
            return campos
        novos = {}
        for indice in indices:
            pagina = self.projeto.paginas[indice]
            if pagina.recorte is None or self._jeito_do_retangulo(pagina) != RETANGULO_ACOMPANHA:
                continue
            antes = pagina.angulo_manual if pagina.angulo_manual is not None else (
                angulo_da_pagina(self.projeto, pagina) or 0.0)
            depois = campos["angulo_manual"]
            if isinstance(depois, dict):
                depois = depois.get(str(indice))
            recorte = recorte_depois_de_mudar_o_angulo(
                self.projeto, pagina, antes, depois, RETANGULO_ACOMPANHA,
                self._proporcao_da_pagina(pagina))
            if recorte is not None and tuple(recorte) != tuple(pagina.recorte):
                novos[str(indice)] = [round(float(v), 6) for v in recorte]
        if not novos:
            return campos
        return {**campos, "recorte": novos}

    def _mudar_retangulo_da_pagina(self) -> None:
        """A lista "Quando o ângulo muda, o corte desta página" (D-094, a
        escolha "na página"). Uma acao do desfazer."""
        if self._carregando or not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        valor = self.combo_retangulo_da_pagina.currentData()
        if getattr(pagina, "retangulo_do_corte", None) == valor:
            return
        nomes = {None: "segue o livro", "fica": "fica no mesmo lugar",
                 "acompanha": "acompanha o texto"}
        self._registrar("retangulo_do_corte", "pagina", [self.indice_pagina],
                        {"retangulo_do_corte": valor},
                        f"Página {self.indice_pagina + 1}: o corte {nomes.get(valor, valor)} "
                        "quando o ângulo muda")

    # --- etapa 3 da obra: o aviso do livro novo (D-005) e a grade (D-334) ---

    def _montar_aviso_do_livro_novo(self) -> QWidget:
        """A faixa embaixo da pagina do livro que ainda nao passou pelo
        automatico. Decisao do Samuel (R13 804, 12/10/2026): "B — Um aviso
        embaixo da página", com "Rodar o automático…" e "agora não". O
        "Rodar..." abre a janela grande com a receita de sempre marcada (D-018,
        escolha da gerente); "agora não" some com o aviso deste livro."""
        faixa = QFrame()
        faixa.setObjectName("avisoDoLivroNovo")
        faixa.setAttribute(Qt.WA_StyledBackground, True)
        faixa.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        linha = QHBoxLayout(faixa)
        linha.setContentsMargins(14, 5, 10, 5)
        linha.setSpacing(8)
        self.texto_do_livro_novo = QLabel("Livro novo: ainda não passou pelo automático.")
        self.texto_do_livro_novo.setWordWrap(True)
        linha.addWidget(self.texto_do_livro_novo, 1)
        self.botao_rodar_do_aviso = QPushButton("Rodar o automático…")
        self.botao_rodar_do_aviso.setObjectName("acaoPrimaria")
        self.botao_rodar_do_aviso.setToolTip(
            "Abre o Automático com a receita de sempre marcada. Nada muda até você clicar em Rodar.")
        _ligar(self.botao_rodar_do_aviso, lambda: self.rodar_do_aviso_pedido.emit())
        self.botao_agora_nao = QPushButton("agora não")
        self.botao_agora_nao.setToolTip("Some com este aviso. O Automático continua no ícone da direita.")
        _ligar(self.botao_agora_nao, self._agora_nao)
        for botao in (self.botao_rodar_do_aviso, self.botao_agora_nao):
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)
            linha.addWidget(botao)
        estilo.estilizar(faixa, lambda: (
            f"QFrame#avisoDoLivroNovo {{ background: {estilo.cor('sel')};"
            f" border-top: 1px solid {estilo.cor('azul')}; }}"))
        faixa.setVisible(False)
        self.aviso_do_livro_novo = faixa
        return faixa

    def _mostrar_o_aviso_do_livro_novo(self) -> None:
        """O aviso aparece enquanto o livro nao passou pelo automatico."""
        mostrar = bool(self.projeto is not None
                       and not getattr(self.projeto, "passou_pelo_automatico", True))
        if self.aviso_do_livro_novo.isVisible() != mostrar:
            self.aviso_do_livro_novo.setVisible(mostrar)

    def _agora_nao(self) -> None:
        """"agora não": o aviso some deste livro (fica gravado; o Automatico
        continua no icone da direita). Escolha da gerente (D-014): nao volta a
        cada abertura, para nao incomodar."""
        if self.projeto is None:
            return
        self.projeto.passou_pelo_automatico = True
        self._mostrar_o_aviso_do_livro_novo()
        self.trabalho_mudou.emit()

    def abrir_para_escolher(self, escolhidas: list[int]) -> None:
        """O "escolher páginas..." do Automatico: a grade "Todas as páginas"
        no jeito de escolher (rodada 2: "Escolher folhas abrindo a tela de
        todas as páginas (marcar/desmarcar)"). A volta e escolha_pronta."""
        self.abrir_todas_as_paginas()
        if self.pilha_da_tela.currentWidget() is self.todas:
            self.todas.comecar_a_escolher(escolhidas, para_o_automatico=True)

    def _escolha_pronta(self, escolhidas: list) -> None:
        """A grade devolveu as paginas escolhidas para o Automatico."""
        self.pilha_da_tela.setCurrentWidget(self.trabalho)
        self.escolhidas_para_o_automatico.emit(list(escolhidas))

    def _acao_nas_escolhidas(self, acao: str, indices: list) -> None:
        """As acoes da grade nas paginas escolhidas (D-334, como o "Organizar
        páginas" do UPDF): girar, deixar em branco, tirar do livro, trazer de
        volta, extrair e rodar o automatico. Cada uma numa acao so do desfazer."""
        from core.girar import GIRO_DIREITA, GIRO_ESQUERDA

        if self.projeto is None or not indices:
            return
        indices = sorted(i for i in set(int(i) for i in indices)
                         if 0 <= i < len(self.projeto.paginas))
        n = len(indices)
        plural = "página" if n == 1 else "páginas"
        if acao in ("girar_esquerda", "girar_direita"):
            giro = GIRO_ESQUERDA if acao == "girar_esquerda" else GIRO_DIREITA
            folhas = sorted({self.projeto.paginas[i].folha for i in indices})
            novos = {str(f): (int(self.projeto.folhas[f].rotacao) + giro) % 360 for f in folhas}
            self._registrar("girar", "folha", folhas, {"rotacao": novos},
                            f"Girar {len(folhas)} folha" + ("" if len(folhas) == 1 else "s")
                            + " (escolhidas em Todas as páginas)")
        elif acao == "em_branco":
            self._registrar("em_branco", "pagina", indices, {"em_branco": True, "revisada": True},
                            f"Deixar em branco {n} {plural}")
        elif acao == "tirar":
            self._registrar("apagar", "pagina", indices, {"apagada": True, "revisada": True},
                            f"Tirar do livro {n} {plural}")
        elif acao == "trazer":
            self._registrar("restaurar", "pagina", indices, {"apagada": False, "em_branco": False},
                            f"Trazer de volta {n} {plural}")
        elif acao == "extrair":
            self._extrair(indices)
            return
        elif acao == "automatico":
            self.pilha_da_tela.setCurrentWidget(self.trabalho)
            self.escolhidas_para_o_automatico.emit(indices)
            return
        self.abrir_todas_as_paginas()
        self.todas.comecar_a_escolher(indices)

    def _extrair(self, indices: list[int]) -> None:
        """"Extrair": as folhas das paginas escolhidas, como estao no PDF de
        entrada (sem os ajustes), num PDF novo (o "Extrair" do UPDF)."""
        from ui.dialogos_de_arquivo import escolher_onde_salvar_pdf

        assert self.projeto is not None
        folhas = sorted({self.projeto.paginas[i].folha for i in indices})
        sugestao = str(Path(self.projeto.caminho_entrada).with_name(
            Path(self.projeto.caminho_entrada).stem + " - páginas escolhidas.pdf"))
        destino = escolher_onde_salvar_pdf(self, "Extrair as páginas escolhidas", sugestao)
        if not destino:
            return
        try:
            import fitz

            with fitz.open(self.projeto.caminho_entrada) as doc, fitz.open() as novo:
                for folha in folhas:
                    novo.insert_pdf(doc, from_page=folha, to_page=folha)
                novo.save(str(destino))
        except Exception:  # noqa: BLE001 - erro vira aviso, nunca fecha a janela
            registrar_erro("extrair paginas", traceback.format_exc())
            self._avisar("Não consegui gravar o PDF com as páginas escolhidas. "
                         "Confira se a pasta aceita gravação.")
            return
        self._avisar(f"Gravei {len(folhas)} folha" + ("" if len(folhas) == 1 else "s")
                     + f" do livro, como estão no PDF de entrada, em:\n{destino}")

    def _avisar(self, texto: str) -> None:
        janela = self.window()
        if janela is not self and hasattr(janela, "avisar"):
            janela.avisar(texto)

    @protegido
    def _mover_angulo(self, angulo: float) -> None:
        self._gravar_angulo(self.indice_pagina, angulo)

    def _gravar_angulo(self, indice: int, angulo: float) -> None:
        """O angulo a mao (alca, linha-guia, setas, numero) vai para o projeto."""
        self._gravar_angulo_timer.stop()
        self._angulo_pendente = None
        angulo = max(-45.0, min(45.0, round(float(angulo), 2)))
        texto = f"{angulo:+.2f}".replace(".", ",")
        self._mudar_o_angulo(
            indice, {"angulo_manual": angulo},
            f"Ângulo da página {indice + 1}: {texto} graus",
            f"Ângulo de {{n}} páginas: {texto} graus")

    def _ajustar_angulo(self, passo: float) -> None:
        """As setas de 0,1 grau: a imagem gira na hora; o angulo e gravado
        um instante depois do ultimo clique (ESPERA_PARA_GRAVAR_O_ANGULO_MS),
        numa acao so."""
        if not self._pronta() or ABA_ANGULO not in self.visualizadores:
            return
        vis = self.visualizadores[ABA_ANGULO]
        if not vis.angulo_conhecido:
            return
        self._angulo_ao_vivo(round(vis.angulo + passo, 2))

    def _angulo_ao_vivo(self, angulo: float) -> None:
        vis = self.visualizadores[ABA_ANGULO]
        vis.definir_angulo(max(-45.0, min(45.0, angulo)))
        self._angulo_pendente = (self.indice_pagina, vis.angulo)
        self._mostrar_angulo(vis.angulo)
        self._gravar_angulo_timer.start()

    @protegido
    def _gravar_angulo_pendente(self) -> None:
        """O instante depois do ultimo clique nas setas (ou no numero)."""
        pendente, self._angulo_pendente = self._angulo_pendente, None
        if pendente is not None and self.projeto is not None \
                and 0 <= pendente[0] < len(self.projeto.paginas):
            self._gravar_angulo(*pendente)

    def _mostrar_angulo(self, angulo: float | None) -> None:
        """O numero da aba Endireitar (sem sinal: mostrar nao e mudar)."""
        if not hasattr(self, "campo_angulo"):
            return
        conhecido = angulo is not None
        self.campo_angulo.blockSignals(True)
        if conhecido:
            self.campo_angulo.setValue(float(angulo))
        self.campo_angulo.blockSignals(False)
        for widget in (self.campo_angulo, self.botao_angulo_anti_horario,
                       self.botao_angulo_horario):
            widget.setEnabled(conhecido)
        self.campo_angulo.setToolTip(
            self.campo_angulo.toolTip() if conhecido
            else "Ainda estou medindo a inclinação desta página.")

    def _angulo_digitado(self, valor: float) -> None:
        """Seta do teclado ou Enter no numero: como as setas da tela."""
        if not self._pronta() or ABA_ANGULO not in self.visualizadores:
            return
        if self.visualizadores[ABA_ANGULO].angulo_conhecido:
            self._angulo_ao_vivo(round(float(valor), 2))

    def _angulo_digitado_acabou(self) -> None:
        """Enter ou sair do numero: grava ja e devolve o teclado a tela (as
        setas voltam a trocar de pagina)."""
        if self._angulo_pendente is not None:
            self._gravar_angulo_pendente()
        self.campo_angulo.clearFocus()

    @protegido
    def _angulo_zero(self) -> None:
        self._mudar_o_angulo(
            self.indice_pagina, {"angulo_manual": 0.0},
            f"Não endireitar a página {self.indice_pagina + 1}",
            "Não endireitar {n} páginas")

    def _atualizar_conta_do_endireitar(self) -> None:
        """Item 2.2: mostra a conta desta pagina e os dois angulos medidos
        (sem sinal: so mostrar nao e trocar). So vale com o angulo
        automatico: com o angulo a mao, a lista fica apagada."""
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        es = endireitar_scantailor
        # etapa 3 da obra: o automatico do livro OU so desta pagina (core/etapas)
        automatico = etapas_core.endireita_sozinho(self.projeto, pagina) and pagina.angulo_manual is None
        if hasattr(self, "combo_retangulo_da_pagina"):        # D-094, a escolha da pagina
            self.combo_retangulo_da_pagina.blockSignals(True)
            self.combo_retangulo_da_pagina.setCurrentIndex(max(0, self.combo_retangulo_da_pagina.findData(
                getattr(pagina, "retangulo_do_corte", None))))
            self.combo_retangulo_da_pagina.blockSignals(False)
        self.combo_conta_do_endireitar.blockSignals(True)
        self.combo_conta_do_endireitar.setCurrentIndex(self.combo_conta_do_endireitar.findData(
            es.jeito_da_pagina(self.projeto, pagina)))
        self.combo_conta_do_endireitar.blockSignals(False)
        self.combo_conta_do_endireitar.setEnabled(automatico)
        self.rotulo_conta_do_endireitar.setEnabled(automatico)
        # Rodada 14b do layout, 910 (Samuel, 20/10/2026: "A — Os dois ângulos
        # e, embaixo, o seu", com "os angulos continuam embaixo mas a
        # mensagem só aparece quando bota o mouse em cima"): com o ângulo à
        # mão a linha dos dois ângulos NÃO some (antes ficava vazia), e a
        # frase do giro à mão vai para o balão do mouse da linha e da lista.
        medidos = None
        if self.projeto.endireitar:
            # com o angulo a mao, as medidas guardadas sao as da pagina SEM
            # ele (a geometria automatica): procura com uma copia sem o a mao
            consulta = (pagina if pagina.angulo_manual is None
                        else dataclasses.replace(pagina, angulo_manual=None))
            medidos = angulos_medidos(self.projeto, consulta)
        if not self.projeto.endireitar:
            texto = ""
        elif medidos is None and pagina.angulo_manual is not None:
            texto = "(as contas não foram medidas nesta página)"
        else:
            texto = texto_dos_angulos_medidos(medidos)
        self.rotulo_angulos_medidos.setText(texto)
        frase = ""
        if pagina.angulo_manual is not None:
            frase = (f"Você girou à mão: {_graus(pagina.angulo_manual)}. As contas voltam com "
                     "“usar o ângulo do programa”.")
        for peca in (self.rotulo_angulos_medidos, self.combo_conta_do_endireitar):
            peca.setToolTip(frase or (
                "Endireita esta página por outra conta: a do ScanTailor ou a do Editor. "
                "Os números embaixo são os ângulos que cada uma achou."))
        # item 2.12: o desentortar desta pagina (sem sinal: mostrar nao e trocar)
        self.combo_desentortar.blockSignals(True)
        self.combo_desentortar.setCurrentIndex(self.combo_desentortar.findData(
            desentortar_scantailor.modo_da_pagina(pagina)))
        self.combo_desentortar.blockSignals(False)

    @protegido
    def _trocar_conta_do_endireitar(self) -> None:
        """Item 2.2: a lista "conta:" da aba Endireitar. Troca a conta do
        endireitar automatico SO desta pagina, numa acao do desfazer (a previa
        refaz o angulo). Escolher a conta do livro volta a "seguir o livro"
        (ConfigPagina.endireitar_como None)."""
        assert self.projeto is not None
        es = endireitar_scantailor
        pagina = self.projeto.paginas[self.indice_pagina]
        jeito = es.jeito_valido(self.combo_conta_do_endireitar.currentData())
        if pagina.angulo_manual is not None or jeito == es.jeito_da_pagina(self.projeto, pagina):
            return
        self._registrar(
            "conta_do_endireitar", "pagina", [self.indice_pagina],
            {"endireitar_como": None if jeito == es.jeito_do_livro(self.projeto) else jeito,
             "revisada": True},
            f"Página {self.indice_pagina + 1}: endireitar pela conta "
            f"“{nome_da_conta(jeito)}”",
        )

    @protegido
    def _mudar_desentortar(self) -> None:
        """Item 2.12: a lista "Desentortar perto da lombada" do Propriedades
        do Endireitar. Troca o desentortar SO desta pagina, numa acao do
        desfazer (a previa e refeita). Nada acontece se a pagina ja esta
        assim (mostrar o valor nunca grava)."""
        if not self._pronta() or self.projeto is None:
            return
        ds = desentortar_scantailor
        pagina = self.projeto.paginas[self.indice_pagina]
        modo = ds.modo_valido(self.combo_desentortar.currentData())
        if modo == ds.modo_da_pagina(pagina):
            return
        self._registrar(
            "mudar_desentortar", "pagina", [self.indice_pagina],
            {"desentortar": modo},
            ds.FRASE_DO_DESFAZER.format(pagina=self.indice_pagina + 1,
                                        estado=ds.ROTULOS_NA_TELA[modo]),
        )

    @protegido
    def _angulo_automatico(self) -> None:
        indices = self._paginas_do_alcance_do_angulo(self.indice_pagina)
        if not indices:
            return
        self._registrar(
            "ajustar_angulo", "pagina", indices, {"angulo_manual": None},
            f"Voltar ao endireitar automático na página {self.indice_pagina + 1}"
            if indices == [self.indice_pagina]
            else f"Voltar ao endireitar automático em {len(indices)} páginas",
        )

    # --- filtro -----------------------------------------------------------

    @protegido
    def _escolher_filtro(self, filtro: str) -> None:
        """Troca o filtro da página da vez (cartão, tecla 1 a 4, menu, botão do
        aviso), como ação do desfazer; a página fica dada como conferida.

        Escolher o filtro que JÁ está não faz nada (13/10/2026). O defeito
        (verificador): dois cliques no cartão do filtro - o jeito de abrir o
        "Ver de perto" - gravavam "Preto e branco para Preto e branco", a
        página ficava conferida e o aviso dela sumia sem ninguém ter decidido
        nada. Arriscado: voltar a gravar quando o filtro não muda."""
        assert self.projeto is not None
        atual = self.projeto.paginas[self.indice_pagina].filtro
        if filtro == atual:
            return
        nome_antes = NOMES_AMIGAVEIS.get(atual, atual)
        nome_depois = NOMES_AMIGAVEIS.get(filtro, filtro)
        self._registrar(
            "mudar_filtro", "pagina", [self.indice_pagina],
            {"filtro": filtro, "revisada": True},
            f"Filtro da página {self.indice_pagina + 1}: {nome_antes} para {nome_depois}",
        )
        self._aquecer_o_leitor_se_precisar()      # modo Misto (05/10/2026)

    @protegido
    def _mudar_algoritmo_pb(self, indice: int) -> None:
        """Problema 5 do plano (e item 2.8): qual algoritmo o Preto e branco usa
        nesta página. Chamado pelo seletor da aba Filtro."""
        if not self._pronta() or self.projeto is None:
            return
        novo = self.seletor_algoritmo_pb.itemData(indice)
        if novo is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if novo == pagina.algoritmo_preto_branco:
            return
        nome = (NOMES_DOS_ALGORITMOS_PB.get(novo)
                or preto_e_branco_scantailor.NOMES_NA_TELA.get(novo, novo)
                if novo != "auto" else "Automático")
        self._registrar(
            "mudar_algoritmo_pb", "pagina", [self.indice_pagina],
            {"algoritmo_preto_branco": novo},
            f"Algoritmo do Preto e branco na página {self.indice_pagina + 1}: {nome}",
        )

    @protegido
    def _mudar_cores(self, campo: str, marcada: bool) -> None:
        """As caixinhas "Letras com a cor delas" e "Reduzir cores" (item 2.11):
        SÓ desta página, como ação do desfazer. Mostrar o valor nunca grava."""
        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if bool(marcada) == bool(getattr(pagina, campo, False)):
            return
        rotulo = (cores_scantailor.ROTULO_LETRAS if campo == "letras_com_a_cor"
                  else cores_scantailor.ROTULO_REDUZIR)
        self._registrar(
            f"mudar_{campo}", "pagina", [self.indice_pagina], {campo: bool(marcada)},
            cores_scantailor.FRASE_DO_DESFAZER.format(
                rotulo=rotulo, pagina=self.indice_pagina + 1,
                estado="marcada" if marcada else "desmarcada"),
        )

    @protegido
    def _mudar_claro_no_escuro(self, marcada: bool) -> None:
        """A caixinha "Letra clara em fundo escuro" da aba Filtro (item 2.9):
        SÓ desta página, como ação do desfazer. Nada acontece se a página já
        está assim (mostrar o valor nunca grava)."""
        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if bool(marcada) == claro_no_escuro.ligado(pagina):
            return
        self._registrar(
            "mudar_claro_no_escuro", "pagina", [self.indice_pagina],
            {"claro_no_escuro": bool(marcada)},
            claro_no_escuro.FRASE_DO_DESFAZER.format(
                pagina=self.indice_pagina + 1, estado="marcada" if marcada else "desmarcada"),
        )

    @protegido
    def _mudar_pontinhos(self, indice: int) -> None:
        """A lista "Limpar pontinhos" da aba Filtro (decisão do Samuel,
        06/10/2026, P7): a escolha SÓ desta página, como ação do desfazer.
        Nada acontece se o que já vale nela (dela ou do livro) é esse valor -
        assim mostrar o valor do livro nunca grava na página."""
        if not self._pronta() or self.projeto is None:
            return
        novo = self.seletor_pontinhos.itemData(indice)
        if novo not in pontinhos.ESCOLHAS:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if novo == pontinhos.escolha_da_pagina(self.projeto, pagina):
            return
        self._registrar(
            "mudar_pontinhos", "pagina", [self.indice_pagina],
            {"limpar_pontinhos": novo},
            pontinhos.FRASE_DO_DESFAZER.format(pagina=self.indice_pagina + 1,
                                               nome=pontinhos.NOMES_NA_TELA[novo]),
        )

    @protegido
    def _mudar_luz(self, campo: str, valor) -> None:
        """Item 2.17: igualar a luz, suavizar as letras ou tirar o chuvisco SO
        desta página, como ação do desfazer. Nada acontece se a página já está
        assim (mostrar o valor nunca grava)."""
        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if getattr(pagina, campo, None) == valor:
            return
        rotulos = {"luz_igualar": luz_scantailor.ROTULO_IGUALAR,
                   "luz_suavizar": luz_scantailor.ROTULO_SUAVIZAR,
                   "luz_chuvisco": luz_scantailor.ROTULO_CHUVISCO}
        estado = (("ligado" if valor else "desligado") if isinstance(valor, bool)
                  else ("desligado" if not valor else f"{valor}"))
        self._registrar(
            "mudar_luz", "pagina", [self.indice_pagina], {campo: valor},
            luz_scantailor.FRASE_DO_DESFAZER.format(rotulo=rotulos[campo],
                                                    pagina=self.indice_pagina + 1, estado=estado),
        )

    # --- modo Misto ("Só as letras", 05/10/2026) ---------------------------

    def _mudar_misto(self, campo: str, valor, descricao: str) -> None:
        """Uma escolha do Misto SO desta página, como ação do desfazer. Nada
        acontece se o que vale nela (dela ou do livro) já é esse valor."""
        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        ligado, escolhas = misto.escolhas_da_pagina(self.projeto, pagina)
        agora = {"misto_so_as_letras": ligado,
                 "misto_fora_do_texto": escolhas.fora_do_texto,
                 "misto_papel_da_gravura": escolhas.papel_da_gravura,
                 "misto_letras_na_moldura": escolhas.letras_na_moldura}[campo]
        if agora == valor:
            return
        self._registrar("mudar_misto", "pagina", [self.indice_pagina], {campo: valor},
                        f"Só as letras na página {self.indice_pagina + 1}: {descricao}")
        self._aquecer_o_leitor_se_precisar()

    def _aquecer_o_leitor_se_precisar(self) -> None:
        """Se alguma página está no Misto A ou C, abre o leitor de texto numa
        thread à parte (core.linhas_do_texto.aquecer_em_segundo_plano): a
        primeira prévia não espera os ~7 a 20 s de abrir. Nunca levanta."""
        try:
            if self.projeto is not None and misto.alguma_precisa_das_linhas(self.projeto):
                linhas_do_texto.aquecer_em_segundo_plano()
        except Exception:  # noqa: BLE001 - aquecer e so uma otimizacao
            registrar_erro("aquecer o leitor de texto", traceback.format_exc())

    @protegido
    def _mudar_so_as_letras(self, ligado: bool) -> None:
        self._mudar_misto("misto_so_as_letras", bool(ligado),
                          "ligado" if ligado else "desligado")

    @protegido
    def _mudar_fora_do_texto(self, valor: str) -> None:
        nomes = {v: texto for v, texto, _frase in BOTOES_DO_TEXTO}
        self._mudar_misto("misto_fora_do_texto", valor, nomes.get(valor, valor))

    @protegido
    def _mudar_papel_da_gravura(self, valor: str) -> None:
        texto = "branco" if valor == misto.PAPEL_BRANCO else "como foi escaneado"
        self._mudar_misto("misto_papel_da_gravura", valor, f"papel das gravuras {texto}")

    @protegido
    def _mudar_letras_na_moldura(self, valor: str) -> None:
        textos = {misto.LETRAS_COR_PAPEL_BRANCO: "com a cor delas e papel branco",
                  misto.LETRAS_COR_FUNDO_ORIGINAL: "com a cor delas e o fundo original",
                  misto.LETRAS_PRETAS: "pretas"}
        self._mudar_misto("misto_letras_na_moldura", valor,
                          f"letras da moldura {textos.get(valor, valor)}")

    # --- medidor de ajuste ------------------------------------------------

    def _campo_do_ajuste(self, filtro: str | None = None) -> str | None:
        """Qual campo da página o medidor edita, conforme o filtro escolhido."""
        if filtro is None:
            if self.projeto is None:
                return None
            filtro = self.projeto.paginas[self.indice_pagina].filtro
        return CAMPO_DO_AJUSTE.get(filtro)

    def _configurar_medidor(self) -> None:
        """Mostra o medidor do filtro atual, com o valor daquela página."""
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        campo = self._campo_do_ajuste(pagina.filtro)

        # Original não tem o que ajustar: o bloco inteiro some (e a frase
        # "O Original não tem ajuste." aparece no lugar dele, no painel).
        self.bloco_ajuste.setVisible(campo is not None)
        self.frase_sem_ajuste.setVisible(campo is None)
        if campo is None:
            self._resumir_o_filtro(pagina, None)
            self._medir_de_novo_a_barra()
            return

        rotulo, esquerda, direita = ROTULOS_DO_AJUSTE[pagina.filtro]
        self.medidor.definir_rotulo(rotulo, esquerda, direita)
        self.medidor.definir(getattr(pagina, campo))
        # item 2.9: o que vale nesta pagina, sem virar acao
        self.caixa_claro_no_escuro.blockSignals(True)
        self.caixa_claro_no_escuro.setChecked(claro_no_escuro.ligado(pagina))
        self.caixa_claro_no_escuro.blockSignals(False)
        # item 2.11: idem; "Letras com a cor delas" so no Preto e branco
        for caixa, campo in ((self.caixa_letras_com_a_cor, "letras_com_a_cor"),
                             (self.caixa_reduzir_cores, "reduzir_cores")):
            caixa.blockSignals(True)
            caixa.setChecked(bool(getattr(pagina, campo, False)))
            caixa.blockSignals(False)
        self.caixa_letras_com_a_cor.setVisible(pagina.filtro == PRETO_E_BRANCO)

        # O algoritmo só faz sentido no Preto e branco - Melhorar/Mágico pro
        # não binarizam.
        eh_preto_e_branco = pagina.filtro == PRETO_E_BRANCO
        self.seletor_algoritmo_pb.setVisible(eh_preto_e_branco)
        self.rotulo_algoritmo_pb.setVisible(eh_preto_e_branco)
        self.rotulo_pontinhos.setVisible(eh_preto_e_branco)
        self.seletor_pontinhos.setVisible(eh_preto_e_branco)
        # modo Misto: so no Preto e branco; mostra o que vale nesta pagina
        # (dela ou do livro), sem virar acao no desfazer
        self.escolhas_misto.setVisible(eh_preto_e_branco)
        # item 2.17: o que vale nesta pagina, sem virar acao; suavizar so no
        # Preto e branco
        self.caixa_luz_suavizar.setVisible(eh_preto_e_branco)
        for controle, valor in ((self.caixa_luz_igualar, luz_scantailor.igualar_ligado(pagina)),
                                (self.caixa_luz_suavizar, luz_scantailor.suavizar_ligado(pagina))):
            controle.blockSignals(True)
            controle.setChecked(valor)
            controle.blockSignals(False)
        self.seletor_luz_chuvisco.blockSignals(True)
        self.seletor_luz_chuvisco.setValue(luz_scantailor.chuvisco(pagina))
        self.seletor_luz_chuvisco.blockSignals(False)
        avisos = luz_scantailor.avisos_da_pagina(pagina)
        self.aviso_luz.setText(" ".join(avisos))
        self.aviso_luz.setVisible(bool(avisos))
        if eh_preto_e_branco:
            ligado, escolhas = misto.escolhas_da_pagina(self.projeto, pagina)
            self.escolhas_misto.mostrar(ligado, escolhas.fora_do_texto,
                                        escolhas.papel_da_gravura, escolhas.letras_na_moldura)
        if eh_preto_e_branco:
            indice = self.seletor_algoritmo_pb.findData(pagina.algoritmo_preto_branco)
            self.seletor_algoritmo_pb.blockSignals(True)
            self.seletor_algoritmo_pb.setCurrentIndex(max(0, indice))
            self.seletor_algoritmo_pb.blockSignals(False)
            # o que vale nesta página (dela ou do livro), sem virar ação
            escolha = pontinhos.escolha_da_pagina(self.projeto, pagina)
            self.seletor_pontinhos.blockSignals(True)
            self.seletor_pontinhos.setCurrentIndex(
                max(0, self.seletor_pontinhos.findData(escolha)))
            self.seletor_pontinhos.blockSignals(False)
        self._resumir_o_filtro(pagina, campo)
        self._medir_de_novo_a_barra()

    def _resumir_o_filtro(self, pagina, campo: str | None) -> None:
        """Etapa 4 do layout: no painel "Filtro da página", as partes que só
        valem no Preto e branco ("Só as letras", "Limpar a sujeira", "Mais
        ajustes") aparecem só com ele, e cada parte fechada diz à direita o
        que está escolhido (desenho das rodadas 10 e 11: "Força do preto:
        normal", "Sem limpeza", "Guardar a tinta forte"). Só lê campos."""
        painel = self.paineis.filtro_da_pagina
        if campo is None:
            painel.definir_parte("ajuste", True, "não tem")
        else:
            painel.definir_parte("ajuste", True, f"{self.medidor.rotulo.text()}: "
                                                 f"{self.medidor.palavra.text()}")
        eh_pb = pagina.filtro == PRETO_E_BRANCO
        letras = "desligado"
        if eh_pb and self.escolhas_misto.caixa.isChecked():
            valor = self.escolhas_misto.fora_do_texto()
            letras = next((texto for v, texto, _f in BOTOES_DO_TEXTO if v == valor), "")
        painel.definir_parte("letras", eh_pb, letras)
        painel.definir_parte("limpar", eh_pb, self.seletor_pontinhos.currentText())
        # "Mais ajustes" (junção com a Fase 2, 22/10/2026): em todo filtro que tem
        # ajuste, porque "Letra clara em fundo escuro" (2.9) e "Reduzir cores" (2.11)
        # valem em todos; o jeito do preto e branco (com os dez do ScanTailor, 2.8) e
        # "Letras com a cor delas" só no Preto e branco.
        marcadas = [c.text() for c in (self.caixa_claro_no_escuro, self.caixa_letras_com_a_cor,
                                       self.caixa_reduzir_cores) if c.isChecked() and c.isVisibleTo(c.parentWidget())]
        resumo = ([self.seletor_algoritmo_pb.currentText()] if eh_pb else []) + [m.lower() for m in marcadas]
        painel.definir_parte("mais", campo is not None, " · ".join(resumo) or "nenhum")

    def _medir_de_novo_a_barra(self) -> None:
        """Mede de novo a barra de botões se a altura que a aba da frente
        pede mudou (o bloco AJUSTE apareceu ou sumiu, o "Só as letras" abriu
        ou fechou os três botões, o "Mais opções").

        Conserto de 05/10/2026 (ressalva 1 do verificador do Misto, prints
        10, 11 e 17; antigo, também no ace15b2): a barra tem a altura FIXA
        medida na troca de aba (_encolher_a_barra_de_botoes). Numa página
        Original, escolher o cartão "Preto e branco" fazia o bloco AJUSTE
        aparecer DEPOIS, espremido numa faixa vazia (com os botões do Misto
        escondidos e os "Aplicar em" sem texto) até trocar de aba. O mesmo
        conserto do 50b9319 na aba Marcar. Barato: só mede quando muda.
        Arriscado: medir sempre pelo maior (o buraco da aba alta volta)."""
        atual = self.barra_botoes.currentWidget()
        if atual is None:
            return
        if self.barra_botoes.maximumHeight() != max(0, atual.sizeHint().height()):
            self._encolher_a_barra_de_botoes()

    @protegido
    def _medidor_pegou(self) -> None:
        """Guarda o valor de antes, para o Ctrl+Z voltar ao ponto certo."""
        campo = self._campo_do_ajuste()
        if campo and self.projeto is not None:
            self._valor_ao_pegar = getattr(
                self.projeto.paginas[self.indice_pagina], campo
            )

    @protegido
    def _medidor_arrastando(self, valor: int) -> None:
        """Prévia ao vivo: aplica no objeto e agenda o redesenho.

        Nao registra no histórico a cada passo - seriam dezenas de ações por
        arrasto. O histórico só recebe uma ação, ao soltar.
        """
        if not self._pronta():
            return
        campo = self._campo_do_ajuste()
        if campo is None:
            return
        assert self.projeto is not None

        if self._valor_ao_pegar is None:
            self._valor_ao_pegar = getattr(
                self.projeto.paginas[self.indice_pagina], campo
            )

        setattr(self.projeto.paginas[self.indice_pagina], campo, int(valor))

        # Durante o arrasto a prévia sai em resolução baixa: a 110 DPI o filtro
        # não acompanha o dedo. Ao soltar volta para a resolução normal.
        self._dpi_atual = DPI_ARRASTO
        self._agendar.start(ESPERA_ARRASTO_MS)

        # Sem medidor preso (mexeu pelo teclado), o commit vem por tempo.
        if not self.medidor.barra.isSliderDown():
            self._commit.start(ESPERA_COMMIT_MS)

    @protegido
    def _medidor_soltou(self, valor: int | None = None) -> None:
        """Fecha o arrasto: uma ação só no histórico e prévia em resolução cheia."""
        self._commit.stop()
        if not self._pronta():
            return
        campo = self._campo_do_ajuste()
        if campo is None:
            return
        assert self.projeto is not None

        pagina = self.projeto.paginas[self.indice_pagina]
        novo = int(self.medidor.valor if valor is None else valor)
        antigo = self._valor_ao_pegar
        self._valor_ao_pegar = None
        self._dpi_atual = self._dpi_normal

        if antigo is None or antigo == novo:
            self.atualizar()
            return

        # Volta ao valor de antes para que o "antes" da ação fique correto;
        # o _registrar aplica o novo em seguida.
        setattr(pagina, campo, antigo)
        rotulo = ROTULOS_DO_AJUSTE[pagina.filtro][0]
        self._registrar(
            "ajuste_filtro", "pagina", [self.indice_pagina],
            {campo: novo, "revisada": True},
            f"{rotulo} da página {self.indice_pagina + 1}: {palavra_do_ajuste(novo)}",
        )

    # --- ver de perto -----------------------------------------------------

    @protegido
    def _ampliar_com_filtro(self, _filtro: str) -> None:
        """Veio de um clique num cartão: o filtro já foi escolhido antes."""
        self.ampliar()

    @protegido
    def _ampliar_miniatura(self, indice: int) -> None:
        """Duplo clique na tira: vai para aquela página e abre ampliada."""
        if not self._pronta():
            return
        self._ir_para(indice)
        self.ampliar()

    # --- os itens do menu Ver e Pagina que nao faziam nada ------------------
    #
    # Etapa 4 do layout (20/10/2026). Bug do inventario de 02/10 ("11 itens de
    # menu mortos"): Aproximar, Afastar, Ajustar à tela, Mostrar o histórico,
    # Restaurar página apagada, Modo comparar e Livros recentes estavam no
    # menu, com tecla, e nao faziam nada. Agora fazem o que o nome diz. Os
    # quatro "Painel: ..." do menu Ver viraram o menu Painéis (rodada 14, 903 B).

    def mostrar_miniaturas(self, a_vista: bool) -> None:
        """Menu Ver > "Miniaturas" (rodada 14 do layout, 904 A): abre ou fecha
        as miniaturas, como a seta do cabeçalho "PÁGINAS"."""
        self.miniaturas.definir_aberta(bool(a_vista))
        self._por_as_miniaturas(self.miniaturas.lugar)

    # --- etapa 5 do layout: as miniaturas e "Todas as páginas" -------------

    def _por_as_miniaturas(self, lugar: str) -> None:
        """Põe as miniaturas embaixo, à esquerda ou à direita da página, e o
        "Confirmar e processar" no lugar certo: ao lado delas quando estão
        embaixo e abertas (704 A); senão, pequeno, no canto direito da barra
        de baixo (801 A). Avisa a janela (o menu Ver acompanha a seta)."""
        m = self.miniaturas
        m.setParent(None)
        m.definir_lugar(lugar)
        if m.lugar == EMBAIXO:
            self.faixa_da_tira.insertWidget(0, m, 1)
        elif m.lugar == ESQUERDA:
            self.lugar_esquerda.layout().addWidget(m)
        else:
            self.lugar_direita.layout().addWidget(m)
        m.show()
        self.lugar_esquerda.setVisible(m.lugar == ESQUERDA)
        self.lugar_direita.setVisible(m.lugar == DIREITA)
        grande = m.lugar == EMBAIXO and m.aberta
        self.lugar_embaixo.setVisible(m.lugar == EMBAIXO)
        botao = self.botao_processar
        botao.setParent(None)
        if grande:
            botao.setObjectName("primario")
            self.caixa_do_processar.addWidget(botao)
        else:
            botao.setObjectName("primario")
            self.caixa_do_processar_na_barra.addWidget(botao)
        botao.setStyleSheet("" if grande else "padding: 2px 12px; font-size: 12px; min-height: 0px;")
        botao.style().unpolish(botao)
        botao.style().polish(botao)
        botao.show()
        self._guardar_as_miniaturas()
        self.miniaturas_mudaram.emit(m.aberta)

    def _guardar_as_miniaturas(self) -> None:
        """Grava o lugar, aberta/fechada e o "em pares" das miniaturas em
        configuracoes.json ("miniaturas"), para o próximo livro abrir igual.
        Só grava quando mudou (a tela é montada muitas vezes nos testes)."""
        import configuracoes

        m = self.miniaturas
        agora = {"lugar": m.lugar, "aberta": bool(m.aberta), "em_pares": bool(m.em_pares)}
        if agora != miniaturas_guardadas():
            configuracoes.escrever("miniaturas", agora)

    def _zona_de_encaixe(self, ponto_na_tela) -> str | None:
        """Qual lugar das miniaturas está sob o ponto (coordenadas da tela do
        computador), ou None."""
        ponto = self.mapFromGlobal(ponto_na_tela)
        for lugar, ret in self._retangulos_de_encaixe().items():
            if ret.contains(ponto):
                return lugar
        return None

    def _retangulos_de_encaixe(self) -> dict:
        """Os três lugares de encaixe (rodada 8: contorno azul tracejado), em
        coordenadas desta tela: embaixo da página, e uma faixa de cada lado."""
        from PySide6.QtCore import QRect

        area = QRect(self.area_imagem.mapTo(self, self.area_imagem.rect().topLeft()),
                     self.area_imagem.size())
        largura = min(160, max(60, area.width() // 4))
        return {
            ESQUERDA: QRect(area.left(), area.top(), largura, area.height()),
            DIREITA: QRect(area.right() - largura, area.top(), largura, area.height()),
            EMBAIXO: QRect(area.left() + largura, area.bottom() - 110, area.width() - 2 * largura, 110),
        }

    def _arrastando_as_miniaturas(self, ponto_na_tela) -> None:
        """A alça das miniaturas está sendo arrastada: mostra os três lugares
        e acende o que está sob o mouse."""
        self.lugares_de_encaixe.mostrar(self._retangulos_de_encaixe(),
                                        self._zona_de_encaixe(ponto_na_tela))

    def _soltou_as_miniaturas(self, ponto_na_tela) -> None:
        """Soltou a alça: num lugar de encaixe, as miniaturas vão para lá;
        fora deles, ficam onde estavam."""
        zona = self._zona_de_encaixe(ponto_na_tela)
        self.lugares_de_encaixe.esconder()
        if zona is not None and zona != self.miniaturas.lugar:
            self._por_as_miniaturas(zona)

    # --- etapa 6 do layout: a tela cheia dos filtros ------------------------

    def abrir_filtros_em_tela_cheia(self) -> None:
        """Ícone no título do painel Filtro (rodada 10, 503) e menu Ver >
        "Filtros em tela cheia" (rodada 14, 904 A): abre a tela cheia dos
        filtros (rodada 11, 601 A; ui/widgets/filtros_tela_cheia.py). Só em
        livro que passa pelos filtros."""
        if not self._pronta() or self.projeto is None or not self.cartoes:
            return
        from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

        # as páginas pequenas da fila (as mesmas dos cartões) são pedidas agora
        self._atualizar_previa()
        janela = FiltrosEmTelaCheia(self, parent=self.window())
        janela.fechou.connect(self.atualizar)
        janela.exec()

    @protegido
    def usar_da_tela_cheia(self, filtro: str, ajuste: int | None, alcance: str,
                           opcoes: dict | None = None) -> None:
        """O "Usar <filtro>" da tela cheia dos filtros: o filtro na página e,
        se foi mexido lá, o ajuste e as outras opções (`opcoes`: campo da
        página -> valor; 22/10/2026), cada um uma ação do desfazer, pelos
        MESMOS caminhos dos controles do painel Filtro da página; depois, com
        "todas" ou "daqui em diante", leva para as outras páginas como os
        botões do painel."""
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        if filtro != pagina.filtro:
            self._escolher_filtro(filtro)
        else:
            self._marcar_revisada()
        campo = self._campo_do_ajuste(filtro)
        if ajuste is not None and campo is not None and getattr(pagina, campo) != int(ajuste):
            rotulo = ROTULOS_DO_AJUSTE[filtro][0]
            self._registrar(
                "ajuste_filtro", "pagina", [self.indice_pagina],
                {campo: int(ajuste), "revisada": True},
                f"{rotulo} da página {self.indice_pagina + 1}: {palavra_do_ajuste(int(ajuste))}",
            )
        for campo, valor in (opcoes or {}).items():
            self._gravar_opcao_da_tela_cheia(campo, valor)
        if alcance == "todas":
            self._filtro_em_todas()
        elif alcance == "daqui":
            self._filtro_nas_proximas()

    def _gravar_opcao_da_tela_cheia(self, campo: str, valor) -> None:
        """Uma opção mexida na tela cheia, gravada pelo caminho do controle dela
        no painel (a mesma ação do desfazer e a mesma frase)."""
        if campo == "algoritmo_preto_branco":
            self._mudar_algoritmo_pb(self.seletor_algoritmo_pb.findData(valor))
        elif campo == "limpar_pontinhos":
            self._mudar_pontinhos(self.seletor_pontinhos.findData(valor))
        elif campo == "claro_no_escuro":
            self._mudar_claro_no_escuro(bool(valor))
        elif campo in ("letras_com_a_cor", "reduzir_cores"):
            self._mudar_cores(campo, bool(valor))
        elif campo == "misto_so_as_letras":
            self._mudar_so_as_letras(bool(valor))
        elif campo == "misto_fora_do_texto":
            self._mudar_fora_do_texto(valor)
        elif campo == "misto_papel_da_gravura":
            self._mudar_papel_da_gravura(valor)
        elif campo == "misto_letras_na_moldura":
            self._mudar_letras_na_moldura(valor)

    def abrir_todas_as_paginas(self) -> None:
        """Botão "ver todas" (808 A) e menu Ver > "Todas as páginas" (904 A):
        abre a grade do livro, sempre "uma a uma" (rodada 14, 901 A)."""
        if not self._pronta() or self.projeto is None:
            return
        itens = []
        for pagina in self.projeto.paginas:
            motivo = ""
            # etapa 7 da obra: a mesma dúvida do "Para revisar" (os avisos que
            # ainda pedem um olhar, com os da folha), para "só as que precisam
            # de atenção (N)" dar o número de todo lugar (lista única 5.5);
            # antes contava os avisos já dados por vistos
            avisos = avisos_do_livro.avisos_da_pagina(self.projeto, pagina.indice)
            if avisos:
                alerta = analise.descrever(avisos[0].codigo)
                motivo = alerta.titulo if alerta is not None else ""
            itens.append(ItemDaGrade(indice=pagina.indice, folha=pagina.folha, motivo=motivo,
                                     apagada=bool(pagina.apagada)))
        self.todas.mostrar(itens, self.indice_pagina, self.projeto.caminho_entrada,
                           self._pagina_dentro_da_folha)
        self.pilha_da_tela.setCurrentWidget(self.todas)

    def _pagina_dentro_da_folha(self, indice: int, img):
        """A página `indice` dentro da folha pequena `img` (como veio no PDF):
        gira a folha como ela está e pega a metade da página (a mesma conta da
        tira: core/pipeline.preparar_metade gira e depois divide)."""
        from core.endireitar import girar_90

        assert self.projeto is not None
        pagina = self.projeto.paginas[indice]
        giro = self._giros_das_folhas().get(pagina.folha, 0)
        if giro:
            img = girar_90(img, giro)
        folha = self.projeto.folhas[pagina.folha]
        if not folha.dividir or pagina.metade not in ("esquerda", "direita"):
            return img
        largura = img.shape[1]
        corte = max(1, min(largura - 1, int(folha.posicao_corte * largura)))
        return img[:, :corte] if pagina.metade == "esquerda" else img[:, corte:]

    def _voltar_das_todas(self, indice) -> None:
        """Volta da grade ao trabalho (na página clicada, se houver)."""
        self.pilha_da_tela.setCurrentWidget(self.trabalho)
        if indice is not None:
            self.ir_para_pagina(int(indice))
            # D-343 (05/10/2026: "Na opção 2 (pares), clicar abre as duas
            # páginas lado a lado, como vai ser impresso."), etapa 6: o clique
            # num par da grade abre o "Duas lado a lado" nele
            from ui.widgets.todas_as_paginas import EM_PARES
            if self.todas.vista == EM_PARES:
                if self.trabalha_com_folhas and ABA_MARCAR in self._abas_ativas:
                    self.mostrar_paginas()          # o lado a lado é de páginas
                self.definir_mostrar(DUAS)

    PASSO_DO_ZOOM = 1.25        # quanto o Aproximar/Afastar do menu muda o zoom
    PAGINAS_DO_PAGE_DOWN = 10   # etapa 6: Page Up/Down pulam 10 (PEDIDOS.md)

    def _vista_com_zoom(self):
        """A página com zoom que está à vista: a da ferramenta de marcar ou a
        da ferramenta de página (Dividir, Cortar, Endireitar, Mover). None no
        "Duas lado a lado" e no "antes / depois" (etapa 6: eles não têm zoom)."""
        if not self._pronta():
            return None
        if self.vista_da_pagina.currentWidget() is not self.area_imagem:
            return None
        aba = self.aba_atual
        if aba == ABA_MARCAR and hasattr(self, "editor_selecao"):
            return self.editor_selecao
        return self.visualizadores.get(aba)

    @protegido
    def mudar_o_zoom(self, fator: float | None) -> None:
        """Aproxima (fator > 1), afasta (fator < 1) ou ajusta à tela (None) a
        página que está à vista: a da ferramenta de marcar ou a da ferramenta
        de página (Dividir, Cortar, Endireitar). Sem livro, não faz nada.
        Etapa 6: o mesmo dos botões "–", "+" e "ajustar à tela" da barra de
        baixo, que mostra o zoom novo."""
        vista = self._vista_com_zoom()
        if vista is None:
            return
        if fator is None:
            vista.ajustar_a_tela()
        else:
            vista.definir_zoom(vista.zoom * fator)
        self._acertar_o_zoom_da_barra()

    def _acertar_o_zoom_da_barra(self) -> None:
        """O "N%" da barra de baixo e os botões do zoom: acesos só quando a
        página à vista tem zoom ("–" e "ajustar à tela" só com zoom: a página
        nunca fica menor que inteira, ZOOM_MIN)."""
        if not hasattr(self, "rotulo_do_zoom"):
            return
        vista = self._vista_com_zoom()
        com_zoom = vista is not None
        zoom = float(getattr(vista, "zoom", 1.0)) if com_zoom else 1.0
        self.rotulo_do_zoom.setText(f"{round(zoom * 100)}%")
        self.rotulo_do_zoom.setEnabled(com_zoom)
        self.botao_mais_zoom.setEnabled(com_zoom)
        self.botao_menos_zoom.setEnabled(com_zoom and zoom > 1.0 + 1e-3)
        self.botao_ajustar_a_tela.setEnabled(com_zoom and zoom > 1.0 + 1e-3)
        explicacao = ("" if com_zoom else
                      "\nNo “Duas lado a lado” e no “antes / depois” a página cabe na tela; "
                      "o zoom é na “Uma página”.")
        self.rotulo_do_zoom.setToolTip(
            "O zoom da página (100% = a página inteira cabendo na tela)" + explicacao)

    # --- etapa 6 da obra: ver o livro (lado a lado, antes / depois) -------------

    @protegido
    def definir_mostrar(self, jeito: str) -> None:
        """"Uma página" ou "Duas lado a lado" (barra de baixo e menu Ver > "Ver
        lado a lado"; D-015, D-006). Fica na mesma página. Escolher um dos dois
        desliga o "antes / depois" (ele mostra uma página só)."""
        if jeito not in (UMA, DUAS):
            return
        self.mostrar = jeito
        self.comparando = False
        self._acertar_a_vista_da_pagina()
        self.mostrar_mudou.emit(jeito)

    @protegido
    def _alternar_antes_depois(self) -> None:
        """O botão "antes / depois" da barra de baixo (liga e desliga)."""
        self.comparando = bool(self.botao_antes_depois.isChecked())
        self._acertar_a_vista_da_pagina()

    def _acertar_a_vista_da_pagina(self) -> None:
        """Põe no lugar da página o que a barra de baixo pede: a ferramenta da
        vez (uma página), os pares rolando ou o "antes / depois". No Dividir a
        tela trabalha com a folha inteira (D-007: a folha com a linha só
        dentro do Dividir): ali fica sempre a ferramenta, e os botões do ver
        dizem por quê. Barato quando nada mudou."""
        if not hasattr(self, "vista_da_pagina"):
            return
        pronta = self._pronta() and self.projeto is not None
        no_dividir = pronta and self.trabalha_com_folhas
        if pronta and not no_dividir and self.comparando:
            self._mostrar_antes_depois()
            self.vista_da_pagina.setCurrentWidget(self.vista_antes_depois)
        elif pronta and not no_dividir and self.mostrar == DUAS:
            self._acertar_o_lado_a_lado()
            self.vista_da_pagina.setCurrentWidget(self.lado_a_lado)
        else:
            self.vista_da_pagina.setCurrentWidget(self.area_imagem)
        # os botões mostram a escolha (mesmo no Dividir, onde ela espera)
        self.botoes_mostrar[self.mostrar].setChecked(True)
        self.botao_antes_depois.setChecked(self.comparando)
        motivo = ("\nNo Dividir a tela mostra a folha inteira, com a linha; "
                  "escolha outra ferramenta para ver as páginas.") if no_dividir else ""
        for jeito, _texto, dica in self.JEITOS_DE_MOSTRAR:
            self.botoes_mostrar[jeito].setEnabled(pronta and not no_dividir)
            self.botoes_mostrar[jeito].setToolTip(dica + motivo)
        self.botao_antes_depois.setEnabled(pronta and not no_dividir)
        self._acertar_o_zoom_da_barra()

    def _acertar_o_lado_a_lado(self) -> None:
        """Os pares rolando com as páginas que vão sair (Projeto.paginas_ativas,
        na ordem do PDF), na página da vez. A lista só é refeita quando muda
        (dividir ou juntar uma folha, tirar do livro, desfazer: a página da vez
        fica na mesma folha, lista_de_paginas_mudou)."""
        assert self.projeto is not None
        indices = [p.indice for p in self.projeto.paginas_ativas]
        if indices != self.lado_a_lado.indices:
            self.lado_a_lado.mostrar_paginas(indices, self._tamanhos_estimados(indices))
        self.lado_a_lado.ir_para_pagina(self.indice_pagina)
        self.lado_a_lado.atualizar_imagens()

    def _tamanhos_estimados(self, indices: list[int]) -> list[tuple[float, float]]:
        """O tamanho (pontos) de cada página antes de a prévia chegar: a folha
        do PDF, girada como está e partida na linha (a metade da página). A
        prévia acerta a proporção quando chega (PaginasLadoALado). As folhas
        do PDF são lidas uma vez por livro (só o tamanho)."""
        assert self.projeto is not None
        caminho = self.projeto.caminho_entrada
        if self._tamanhos_das_folhas[0] != caminho:
            folhas: list[tuple[float, float]] = []
            try:
                from core.pdf_io import abrir_pdf
                doc = abrir_pdf(caminho)
                try:
                    folhas = [(p.rect.width, p.rect.height) for p in doc]
                finally:
                    doc.close()
            except Exception:  # noqa: BLE001 - sem o PDF, todas do mesmo tamanho
                registrar_erro("lado a lado (tamanhos)", traceback.format_exc())
            self._tamanhos_das_folhas = (caminho, folhas)
        folhas = self._tamanhos_das_folhas[1]
        tamanhos = []
        for indice in indices:
            pagina = self.projeto.paginas[indice]
            folha = self.projeto.folhas[pagina.folha]
            w, h = folhas[pagina.folha] if 0 <= pagina.folha < len(folhas) else (420.0, 595.0)
            if folha.rotacao in (90, 270):
                w, h = h, w
            if folha.dividir and pagina.metade in ("esquerda", "direita"):
                parte = folha.posicao_corte if pagina.metade == "esquerda" else 1 - folha.posicao_corte
                w *= max(0.05, min(0.95, parte))
            if pagina.recorte:
                w *= max(0.05, pagina.recorte[2])
                h *= max(0.05, pagina.recorte[3])
            tamanhos.append((max(1.0, w), max(1.0, h)))
        return tamanhos

    def _previa_do_lado_a_lado(self, indice: int, da_vez: bool, so_olhar: bool = False):
        """A fonte do lado a lado: (a prévia da página `indice` como vai sair,
        ou None se ainda não está pronta, e a chave dela). A mesma prévia das
        ferramentas (mesmo cache, mesma qualidade). so_olhar: só a chave, sem
        pedir nada."""
        if self.previas is None or self.projeto is None:
            return None, ""
        chave = self.previas.chave(indice, self._dpi_atual)
        if so_olhar:
            return None, chave
        return self.previas.pegar(indice, self._dpi_atual), chave

    @protegido
    def _pagina_do_lado_a_lado(self, indice: int) -> None:
        """Rolando (ou clicando) no lado a lado, a página da vez mudou: a tela
        acompanha (a barra de baixo, as miniaturas, os painéis), sem mexer no
        rolar (o lado a lado já está nela)."""
        if not self._pronta() or self.projeto is None or indice == self.indice_pagina:
            return
        if not 0 <= indice < len(self.projeto.paginas):
            return
        self.ir_para_pagina(indice)

    def _mostrar_antes_depois(self) -> None:
        """O "antes / depois" da página da vez: o Original à esquerda da linha
        e como vai sair à direita (as prévias; o mesmo jeito da tela cheia dos
        filtros, R11 601 A, inclusive a frase quando a página já é Original)."""
        assert self.projeto is not None and self.previas is not None
        indice = self.indice_pagina
        pagina = self.projeto.paginas[indice]
        filtro = etapas_core.filtro_que_vale(self.projeto, pagina)
        nome = NOMES_AMIGAVEIS.get(filtro, filtro)
        depois = self.previas.pegar(indice, self._dpi_atual)
        rotulos = ("antes: Original", f"depois: {nome}")
        if filtro == ORIGINAL:
            self.vista_antes_depois.definir(
                None, depois, False, rotulos, "Escolha outro filtro para comparar com o Original.")
            return
        antes = self.previas.pegar_com_filtro(indice, self._dpi_atual, ORIGINAL)
        self.vista_antes_depois.definir(antes, depois, True, rotulos)

    def _roda_na_pagina(self, vista, evento) -> bool:
        """D-021 e o pedido da etapa 6 (27/10: "roda do mouse troca de página
        (quando não está com zoom)"). Na página da área de trabalho:
          - sem zoom (a página inteira cabendo), a roda troca de página (de
            folha, no Dividir): para baixo a próxima, para cima a anterior;
          - com zoom, a roda continua dando zoom, como antes (D-026);
          - Ctrl+roda dá zoom sempre (para o zoom pela roda não sumir);
          - na ferramenta de marcar com o Pincel ou a Varinha, a roda continua
            mudando a espessura ou a tolerância, como antes.
        Devolve True se a roda foi usada aqui."""
        passos = evento.angleDelta().y()
        if not passos or not self._pronta():
            return False
        if evento.modifiers() & Qt.ControlModifier:
            fator = self.PASSO_DO_ZOOM if passos > 0 else 1 / self.PASSO_DO_ZOOM
            vista.definir_zoom(vista.zoom * fator)
            self._acertar_o_zoom_da_barra()
            return True
        if vista is getattr(self, "editor_selecao", None) and (
                vista.ferramenta not in FERRAMENTAS_DE_NAVEGACAO):
            return False
        if vista.zoom > 1.0 + 1e-3:
            QTimer.singleShot(0, self._acertar_o_zoom_da_barra)    # a página dá o zoom
            return False
        self._roda_acumulada += passos
        if abs(self._roda_acumulada) >= 120:
            passo = -1 if self._roda_acumulada > 0 else 1
            self._roda_acumulada = 0
            self._navegar(passo)
        return True

    @protegido
    def restaurar_pagina(self) -> None:
        """Menu Página > "Restaurar página apagada": volta a página da vez,
        se ela estiver apagada (o mesmo caminho do botão "restaurar página",
        com desfazer). Página que não está apagada fica como está."""
        if not self._pronta() or self.projeto is None:
            return
        if self.projeto.paginas[self.indice_pagina].apagada:
            self.apagar_pagina()

    @protegido
    def ampliar(self, comparar: bool = False) -> None:
        """Abre a página em tamanho grande, no modo da aba atual. comparar=True
        (menu Ver > "Modo comparar") abre já com os dois filtros lado a lado."""
        if not self._pronta():
            return

        from ui.tela_ampliada import (
            MODO_BORDAS,
            MODO_CORTAR,
            MODO_FILTRO,
            TelaAmpliada,
        )

        modos = {ABA_CORTE: MODO_CORTAR, ABA_BORDAS: MODO_BORDAS}
        modo = modos.get(self.aba_atual, MODO_FILTRO)

        janela = TelaAmpliada(self, modo=modo, parent=self.window())
        # ao fechar, a tela normal se redesenha: o usuário pode ter trocado o
        # filtro ou movido a linha de corte lá dentro
        janela.fechou.connect(self.atualizar)
        if comparar and modo == MODO_FILTRO:
            janela.botao_comparar.setChecked(True)
            janela._alternar_comparar()
        janela.exec()

    def _redesenhar_previa(self) -> None:
        """Chamado pelo tempo de espera do arrasto."""
        if not self._pronta():
            return
        assert self.previas is not None
        self.previas.invalidar(self.indice_pagina)
        self._atualizar_previa()

    @protegido
    def _filtro_em_todas(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = [p.indice for p in self.projeto.paginas]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"filtro": pagina.filtro, "forca_preto": pagina.forca_preto,
             "clareza_melhorar": pagina.clareza_melhorar,
             "intensidade_magico": pagina.intensidade_magico,
             "algoritmo_preto_branco": pagina.algoritmo_preto_branco,
             # "Limpar pontinhos" DESTA pagina (None = segue o livro)
             "limpar_pontinhos": pagina.limpar_pontinhos,
             # item 2.11: as cores desta pagina
             "letras_com_a_cor": pagina.letras_com_a_cor,
             "reduzir_cores": pagina.reduzir_cores,
             # modo Misto: as escolhas DESTA pagina (None = segue o livro)
             **{campo: getattr(pagina, campo) for campo in misto.CAMPOS_DO_MISTO},
             # item 2.17: igualar a luz, suavizar e chuvisco DESTA pagina
             **{campo: getattr(pagina, campo) for campo in luz_scantailor.CAMPOS}},
            f"{nome} em todas as {len(indices)} páginas",
        )

    @protegido
    def _filtro_nas_proximas(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = [p.indice for p in self.projeto.paginas if p.indice >= self.indice_pagina]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"filtro": pagina.filtro, "forca_preto": pagina.forca_preto,
             "clareza_melhorar": pagina.clareza_melhorar,
             "intensidade_magico": pagina.intensidade_magico,
             "algoritmo_preto_branco": pagina.algoritmo_preto_branco,
             # "Limpar pontinhos" DESTA pagina (None = segue o livro)
             "limpar_pontinhos": pagina.limpar_pontinhos,
             # item 2.11: as cores desta pagina
             "letras_com_a_cor": pagina.letras_com_a_cor,
             "reduzir_cores": pagina.reduzir_cores,
             # modo Misto: as escolhas DESTA pagina (None = segue o livro)
             **{campo: getattr(pagina, campo) for campo in misto.CAMPOS_DO_MISTO},
             # item 2.17: igualar a luz, suavizar e chuvisco DESTA pagina
             **{campo: getattr(pagina, campo) for campo in luz_scantailor.CAMPOS}},
            f"{nome} da página {self.indice_pagina + 1} em diante ({len(indices)} páginas)",
        )

    # --- gerais -----------------------------------------------------------

    @protegido
    def apagar_pagina(self) -> None:
        """"Tirar do livro" (ou "trazer de volta", se ela já foi tirada): a
        página sai do PDF final de vez - é para o que não é página do livro
        (Samuel, 07/10/2026). Para pôr uma folha branca no lugar, e a
        encadernação não mudar, é o "Deixar em branco" (deixar_em_branco_ou_voltar).
        O nome do método ficou de quando era "apagar página"."""
        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        acao = "restaurar" if pagina.apagada else "apagar"
        self._registrar(
            acao, "pagina", [self.indice_pagina],
            {"apagada": not pagina.apagada, "revisada": True},
            (f"Trazer de volta a página {self.indice_pagina + 1}" if pagina.apagada
             else f"Tirar do livro a página {self.indice_pagina + 1}"),
        )

    @protegido
    def deixar_em_branco_ou_voltar(self) -> None:
        """A tecla Delete, o menu Página e o botão "deixar em branco" de
        "Esta página" (Samuel, 07/10/2026: "Deixar em branco" (tecla Delete;
        página branca no lugar, encadernação não muda); 09/10: "Essa opção de
        tirar do livro ou deixar folha em branco eu quero ter em outras
        paginas"). Página que já vai sair em branco volta a ser ela mesma (o
        mesmo que o "voltar a página" da faixa). No Dividir (que mostra a
        folha inteira) não faz nada: a página da vez não está à vista.
        Até a etapa 2 da obra (26/10/2026) a Delete apagava a página."""
        if not self._pronta() or self.projeto is None or self.trabalha_com_folhas:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        self._deixar_em_branco(not getattr(pagina, "em_branco", False))

    def _montar_os_botoes_da_pagina(self) -> QWidget:
        """O bloco "Esta página" do alto do painel Propriedades, em todas as
        ferramentas: "deixar em branco" e "tirar do livro" (etapa 2 da obra,
        26/10/2026; Samuel, 09/10: "Essa opção de tirar do livro ou deixar
        folha em branco eu quero ter em outras paginas"). Os mesmos dois botões
        do aviso "Página sem conteúdo", em qualquer página. Os textos trocam
        para "voltar a página" e "trazer de volta" quando a página já está
        assim (_atualizar_os_botoes_da_pagina). Seguro mudar: os textos."""
        bloco = NaoEspreme()
        coluna = QVBoxLayout(bloco)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(6)
        coluna.addWidget(titulo_de_secao("Esta página"))
        par = self._par_de_botoes(coluna)
        self.botao_em_branco = _botao("deixar em branco", par, self.deixar_em_branco_ou_voltar)
        self.botao_tirar_do_livro = _botao("tirar do livro", par, self.apagar_pagina)
        self.botao_tirar_do_livro.setObjectName("destrutivo")
        par.setStretch(0, 1)
        par.setStretch(1, 1)
        self._atualizar_os_botoes_da_pagina()
        return bloco

    # As dicas dos dois botoes de "Esta pagina" (e dos do painel Filtro).
    DICA_EM_BRANCO = ("A página fica no livro, no mesmo lugar, e sai toda branca: a "
                      "encadernação não muda. Tecla Delete. Dá para desfazer.")
    DICA_VOLTAR_DO_BRANCO = "A página volta a sair como era, com o que tem nela."
    DICA_TIRAR = ("A página sai do livro de vez (para o que não é página do livro). "
                  "As páginas depois dela andam uma casa. Dá para desfazer.")
    DICA_TRAZER_DE_VOLTA = "A página volta para o livro, no lugar dela."

    def _atualizar_os_botoes_da_pagina(self) -> None:
        """Acerta os textos e o aceso dos botões "deixar em branco" e "tirar
        do livro" (os de "Esta página" e os do painel Filtro) pela página da
        vez. Sem livro, ou no Dividir (folha inteira), ficam apagados com a
        explicação na dica. Nunca levanta exceção por faltar um botão."""
        pagina = None
        if (self.projeto is not None and not self.trabalha_com_folhas
                and 0 <= self.indice_pagina < len(self.projeto.paginas)):
            pagina = self.projeto.paginas[self.indice_pagina]
        em_branco = bool(getattr(pagina, "em_branco", False))
        tirada = bool(getattr(pagina, "apagada", False))
        pares = [(getattr(self, "botao_em_branco", None), getattr(self, "botao_tirar_do_livro", None)),
                 (getattr(self, "botao_em_branco_do_filtro", None), getattr(self, "botao_apagar", None))]
        for branco, tirar in pares:
            if branco is not None:
                branco.setText("voltar a página" if em_branco else "deixar em branco")
                branco.setToolTip(self.DICA_VOLTAR_DO_BRANCO if em_branco else self.DICA_EM_BRANCO)
                branco.setEnabled(pagina is not None and not tirada)
            if tirar is not None:
                tirar.setText("trazer de volta" if tirada else "tirar do livro")
                tirar.setToolTip(self.DICA_TRAZER_DE_VOLTA if tirada else self.DICA_TIRAR)
                tirar.setEnabled(pagina is not None)
        if pagina is None:
            for branco, tirar in pares:
                for botao in (branco, tirar):
                    if botao is not None:
                        botao.setToolTip("Escolha uma página: no Dividir a tela mostra a folha "
                                         "inteira. Os dois botões valem nas outras ferramentas.")

    @protegido
    def _marcar_revisada(self) -> None:
        alvo = "folha" if self.trabalha_com_folhas else "pagina"
        self._registrar(
            "revisar", alvo, [self.indice_atual], {"revisada": True},
            f"Conferir a {alvo} {self.indice_atual + 1}",
        )

    @protegido
    def marcar_certo_e_avancar(self) -> None:
        """Barra de espaço: aprova e já pula para a próxima."""
        self._marcar_revisada()
        self._navegar(1)

    @protegido
    def _aplicar_sugestao(self, qual: int = 0) -> None:
        """Um botão laranja do aviso (qual=0 o primeiro, 1 o segundo): faz o
        conserto que o aviso oferece (Samuel, rodada 4 do "Para revisar":
        "(a) Botão no aviso").

        E só um atalho. Todos os controles manuais continuam valendo. O aviso
        é o primeiro que ainda pede um olhar (o que a faixa mostra). Página
        "em branco" sem aviso: o botão é o "voltar a página".
        """
        item = self.item_atual
        pendentes = self._avisos_da_vez()
        if not pendentes:
            if getattr(item, "em_branco", False) and not self.trabalha_com_folhas and qual == 0:
                self._deixar_em_branco(False)
            return
        aviso = pendentes[0]
        botoes = self._botoes_do_aviso(self._item_do_aviso(aviso), aviso.codigo)
        if not 0 <= qual < len(botoes):
            if qual == 0:                       # aviso sem botão: "está bom" nele
                self._aceitar_avisos([aviso])
            return
        self._aplicar_correcao(aviso.codigo, botoes[qual][1], aviso)

    def _aplicar_correcao(self, codigo: str, correcao: str, aviso=None) -> None:
        """Faz o que um botão de aviso manda (os valores possíveis estão em
        core.analise.Alerta.botoes). "revisar" é o "está bom assim": aceita
        SÓ este motivo desta página; os outros motivos dela continuam na
        lista (o "está certo" da aba aceita a página inteira). `aviso`: o
        core.avisos.Aviso do botão (o da folha, na página, desde a etapa 7)."""
        if correcao == "revisar":
            if len(self._avisos_da_vez()) <= 1:
                # o único motivo que faltava: a página inteira fica conferida,
                # como este botão sempre fez
                self._marcar_revisada()
            else:
                self._aceitar_avisos([aviso if aviso is not None else self._aviso_da_vez(codigo)])
        elif correcao.startswith("filtro:"):
            self._escolher_filtro(correcao.split(":", 1)[1])
        elif correcao.startswith("forca:"):
            self._escolher_forca(correcao.split(":", 1)[1])
        elif correcao.startswith("misto_fora:"):
            # "Trazer de volta nesta página": troca o jeito do "Só as letras"
            # só nela (o aviso some sozinho quando a prévia nova chegar)
            self._mudar_fora_do_texto(correcao.split(":", 1)[1])
        elif correcao == "em_branco":
            self._deixar_em_branco(True)
        elif correcao == "desfazer_reforco":
            self._desfazer_o_reforco()
        elif correcao == "apagar":
            self.apagar_pagina()
        elif correcao == "nao_dividir":
            # nunca divide (etapa 4: o botão da ferramenta agora divide a
            # folha de uma página só; o do aviso so junta ou confere)
            self._nao_dividir()
        elif correcao == "angulo_zero":
            self._angulo_zero()
        elif correcao == "sem_recorte":
            self._sem_recorte()
        elif correcao == "corte_alargado":           # item 2.5, g8
            self._usar_corte_alargado()
        elif correcao == "alinhar_com_as_outras":    # item 2.5, g9
            self._alinhar_com_as_outras()
        elif correcao == "desentortar_aumentando":
            self._desentortar_aumentando()
        elif correcao == "desentortar_desfazer_aumento":
            self._desfazer_aumento_do_desentortar()
        elif correcao == "ver_no_mover":             # etapa 5 da obra (D-017)
            self.escolher_ferramenta(FERRAMENTA_MOVER)

    # --- os consertos dos avisos (12/10/2026) -----------------------------

    def _escolher_forca(self, palavra: str) -> None:
        """Os botões "usar mais fraco" / "usar mais escuro" dos avisos: põe a
        força do preto desta página no valor da palavra (os mesmos números
        dos projetos antigos, modelos._migrar). Até 12/10/2026 este método
        não existia, e os dois botões caíam em "Não consegui fazer isso
        agora" (bug achado ao fazer o botão do aviso "Texto falhado")."""
        assert self.projeto is not None
        valores = {"mais_fraco": FORCA_MAIS_FRACA, "normal": 50, "mais_escuro": FORCA_DO_REFORCO}
        novo = valores.get(palavra)
        if novo is None or self.trabalha_com_folhas:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if int(pagina.forca_preto) == novo:
            self._aceitar_avisos([self._aviso_da_vez(pagina.alertas_pendentes[0])]
                                 if pagina.alertas_pendentes else [])
            return
        self._registrar(
            "ajuste_filtro", "pagina", [self.indice_pagina], {"forca_preto": novo},
            f"Força do preto da página {self.indice_pagina + 1}: {palavra_do_ajuste(novo)}")

    def _deixar_em_branco(self, em_branco: bool) -> None:
        """"Deixar em branco" (e o "voltar a página"): a página fica no
        livro, no mesmo lugar, e sai toda branca - a encadernação não muda
        (Samuel, 07/10: "quando é apagada uma folha, tem que ser colocada uma
        no lugar dele né, pois se não a encadernação vai ficar errada").
        Ação do desfazer; a página fica dada como conferida."""
        assert self.projeto is not None
        if self.trabalha_com_folhas:
            return
        campos = {"em_branco": bool(em_branco)}
        if em_branco:
            campos["revisada"] = True
        self._registrar(
            "em_branco" if em_branco else "voltar_pagina", "pagina", [self.indice_pagina],
            campos,
            (f"Deixar em branco a página {self.indice_pagina + 1}" if em_branco
             else f"Voltar a página {self.indice_pagina + 1} (não fica mais em branco)"))

    def _desfazer_o_reforco(self) -> None:
        """O "Desfazer" do aviso "Força do preto escurecida": devolve a
        força que a página tinha antes de o programa escurecer, e o programa
        não reforça esta página de novo (ConfigPagina.reforco_desfeito).
        Ação do desfazer (o Ctrl+Z dela traz o reforço de volta)."""
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        if pagina.forca_antes_do_reforco is None:
            return
        self._registrar(
            "desfazer_reforco", "pagina", [self.indice_pagina],
            {"forca_preto": int(pagina.forca_antes_do_reforco),
             "forca_antes_do_reforco": None, "reforco_desfeito": True},
            f"Desfazer a força do preto escurecida na página {self.indice_pagina + 1}")

    # --- "está bom" em cada nível (12/10/2026) ----------------------------
    #
    # Samuel, rodada 4 do "Para revisar": "Eu tenho que conseguir fazer isso
    # com uma pagina individual, com um motivo individual de uma pagina e com
    # todas as paginas ou com todos os motivos de todas as paginas".
    #   a página inteira        "está certo" da aba (_marcar_revisada)
    #   um motivo de uma página "está bom assim" do aviso (_aplicar_correcao)
    #   um motivo em todas      "está bom: todas" do painel "Para revisar"
    #   tudo                    "está bom em tudo" do painel
    #   as que ele escolher     a lista grande (_abrir_a_lista_dos_avisos)
    # Tudo passa por _aceitar_avisos, que grava no histórico (o Ctrl+Z desfaz).

    def _aviso_da_vez(self, codigo: str):
        """O aviso `codigo` da folha ou página que está na tela (na página, o
        da folha dela também conta, desde a etapa 7)."""
        for aviso in self._avisos_da_vez():
            if aviso.codigo == codigo:
                return aviso
        alvo = avisos_do_livro.FOLHA if self.trabalha_com_folhas else avisos_do_livro.PAGINA
        return avisos_do_livro.Aviso(alvo, self.indice_atual, codigo)

    def _aceitar_avisos(self, avisos: list, descricao: str = "") -> int:
        """Dá "está bom" nos `avisos` (core.avisos.Aviso): cada um sai da
        lista "Para revisar"; a página não muda. UMA ação do desfazer, mesmo
        quando há avisos de folhas e de páginas juntos. Devolve quantos itens
        (folhas e páginas) mudaram.

        O defeito (verificador, 20/10/2026): o "está bom em tudo" gravava uma
        ação para as folhas e outra para as páginas, e o Ctrl+Z precisava de
        dois toques para desfazer um clique só. Agora, com os dois tipos, a
        ação é de folha e leva as páginas nos campos "pagina:N.alertas_aceitos"
        (historico_acoes.PREFIXO_PAGINA, o mesmo jeito do "não dividir esta").
        Arriscado: voltar a registrar uma ação por alvo."""
        assert self.projeto is not None and self.acoes is not None
        mudancas = avisos_do_livro.campos_para_aceitar(self.projeto, avisos)
        if not mudancas:
            return 0
        folhas = mudancas.get(avisos_do_livro.FOLHA)
        paginas = mudancas.get(avisos_do_livro.PAGINA)
        quantos = sum(len(indices) for indices, _c in mudancas.values())
        if folhas and paginas:
            alvo, (indices, campos) = avisos_do_livro.FOLHA, folhas
            campos = dict(campos)
            for chave, aceitos in paginas[1]["alertas_aceitos"].items():
                campos[campo_de_pagina(int(chave), "alertas_aceitos")] = aceitos
            nome = "folhas e páginas"
        else:
            alvo, (indices, campos) = next(iter(mudancas.items()))
            nome = "folha" if alvo == avisos_do_livro.FOLHA else "página"
        if descricao:
            texto = descricao
        elif quantos == 1:
            texto = f"Está bom: um aviso da {nome} {indices[0] + 1}"
        else:
            texto = f"Está bom: avisos de {quantos} " + (
                nome if folhas and paginas else nome + "s")
        # Sem passar por _registrar de propósito: ele joga fora a prévia
        # das páginas da ação, e aqui a imagem não muda (num "está bom em
        # tudo" de um livro grande, todas as prévias seriam refeitas).
        acao = montar_acao(self.projeto, "aceitar_avisos", alvo, indices, campos, texto)
        aplicar(self.projeto, acao, acao.depois)
        self.acoes.registrar(acao)
        self.atualizar()
        return quantos

    @protegido
    def _aceitar_o_motivo_em_todas(self, codigo: str) -> None:
        """"está bom: todas" do painel: o motivo `codigo` sai de todas as
        folhas e páginas em que ainda pede um olhar."""
        if not self._pronta() or self.projeto is None:
            return
        avisos = [a for a in avisos_do_livro.pendentes_do_livro(self.projeto)
                  if a.codigo == codigo]
        nome = analise.descrever(codigo).titulo
        self._aceitar_avisos(avisos, f"Está bom: \"{nome}\" em {len(avisos)} "
                             + ("página" if len(avisos) == 1 else "páginas"))

    @protegido
    def _aceitar_tudo(self) -> None:
        """"está bom em tudo" do painel: todos os avisos de todas as páginas."""
        if not self._pronta() or self.projeto is None:
            return
        avisos = avisos_do_livro.pendentes_do_livro(self.projeto)
        self._aceitar_avisos(avisos, f"Está bom em tudo ({len(avisos)} avisos)")

    def _ir_para_o_aviso(self, aviso) -> None:
        """Leva a tela à folha ou página de um aviso ("ver"). Aviso de folha:
        vai para a aba "Onde cortar", se ela existir neste livro."""
        assert self.projeto is not None
        if aviso.alvo == avisos_do_livro.FOLHA:
            # D-007 (obra etapa 4): a folha inteira só no Dividir, para
            # consertar a DIVISÃO; os outros avisos de folha (torta, resolução,
            # tamanho) levam à página dela, uma por vez
            if (ABA_CORTE in self._abas_ativas
                    and aviso.codigo in (analise.NAO_PARECE_DUPLA, analise.LOMBADA_INCERTA)):
                self.barra_abas.setCurrentIndex(self._abas_ativas.index(ABA_CORTE))
                self._ir_para(max(0, min(aviso.indice, len(self.projeto.folhas) - 1)))
                return
            for pagina in self.projeto.paginas:
                if pagina.folha == aviso.indice:
                    self.ir_para_pagina(pagina.indice)
                    return
            return
        if self.trabalha_com_folhas and ABA_FILTRO in self._abas_ativas:
            self.barra_abas.setCurrentIndex(self._abas_ativas.index(ABA_FILTRO))
        self.ir_para_pagina(aviso.indice)

    def _mostrar_a_lista_dos_avisos(self, antes_de_processar: bool) -> str:
        """Abre a lista grande (ui/janela_dos_avisos.py) e faz o que a pessoa
        escolher, até ela sair: "está bom nas marcadas" tira as marcadas e
        mostra o que sobrou; "ver" leva à página. Devolve a última escolha
        (as constantes de ui.janela_dos_avisos): VER, CONTINUAR ou FECHAR. Se
        os avisos acabarem depois de um "está bom", devolve CONTINUAR."""
        from ui.janela_dos_avisos import ACEITAR, CONTINUAR, FECHAR, VER, JanelaDosAvisos

        assert self.projeto is not None
        while True:
            avisos = avisos_do_livro.pendentes_do_livro(self.projeto)
            if not avisos:
                return CONTINUAR
            janela = JanelaDosAvisos(avisos, antes_de_processar=antes_de_processar, parent=self,
                                     projeto=self.projeto)
            janela.exec()
            if janela.escolha == ACEITAR:
                self._aceitar_avisos(janela.marcados)
                continue
            if janela.escolha == VER and janela.aviso_para_ver is not None:
                self._ir_para_o_aviso(janela.aviso_para_ver)
                return VER
            return CONTINUAR if janela.escolha == CONTINUAR else FECHAR

    @protegido
    def _abrir_a_lista_dos_avisos(self) -> None:
        """"ver a lista…" do painel "Para revisar": o seletor grande."""
        if self._pronta() and self.projeto is not None:
            self._mostrar_a_lista_dos_avisos(antes_de_processar=False)


    def _desentortar_aumentando(self) -> None:
        """Item 2.12 (22/10/2026): o botão "Desentortar aumentando a página"
        do aviso "Desentortar não usado" - a opção C do Samuel SÓ nesta página
        (pergunta P1: "Ainda vou poder selecionar a opção c para as paginas que
        entrarem para revisão?" - sim): a página cresce até caber o que o
        desentortar esticou. Ação do desfazer; o aviso some sozinho quando a
        prévia nova chega (core.pipeline._anotar_desentortar_saiu_sem)."""
        if self.projeto is None or self.trabalha_com_folhas:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if getattr(pagina, "desentortar_aumentar", False):
            return
        self._registrar(
            "mudar_desentortar", "pagina", [self.indice_pagina],
            {"desentortar_aumentar": True},
            f"Desentortar aumentando a página {self.indice_pagina + 1}",
        )

    def _desfazer_aumento_do_desentortar(self) -> None:
        """Item 2.12 (23/10/2026, resposta P5 do Samuel: "o aviso deve
        perguntar e não fazer automaticamente"): o botão "Desfazer" do aviso
        "A página ainda saiu deformada". Volta a página sem desentortar, como
        antes do clique em "Desentortar aumentando a página": tira o aumento
        só desta página e a proteção volta a valer (a página sai sem
        desentortar, com o aviso "Desentortar não usado" de antes). É uma
        ação do desfazer como as outras: o Ctrl+Z traz o aumento de volta. O
        aviso "ainda saiu deformada" some sozinho quando a prévia nova chega
        (core.pipeline._anotar_desentortar_ainda_deformada).
        Arriscado: mexer no modo do desentortar aqui (a pessoa só pediu para
        desfazer o aumento; o desentortar do livro fica como estava)."""
        if self.projeto is None or self.trabalha_com_folhas:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if not getattr(pagina, "desentortar_aumentar", False):
            return
        self._registrar(
            "mudar_desentortar", "pagina", [self.indice_pagina],
            {"desentortar_aumentar": False},
            f"Voltar a página {self.indice_pagina + 1} sem desentortar",
        )

    # --- desfazer / refazer -----------------------------------------------

    @protegido
    def lista_de_paginas_mudou(self) -> None:
        """A lista de paginas (ou de folhas) pode ter mudado por baixo da tela
        (o Automatico dividiu folhas que tinham uma pagina so, ou o desfazer
        disso): a pagina da vez fica dentro do livro, a tira e remontada (so
        se o conjunto mudou: _montar_tira) e a tela se redesenha. Etapa 3 da
        obra. Barato quando nada mudou."""
        if self.projeto is None:
            return
        total = len(self.projeto.paginas)
        if (total and 0 <= self.indice_folha < len(self.projeto.folhas)
                and not (0 <= self.indice_pagina < total
                         and self.projeto.paginas[self.indice_pagina].folha == self.indice_folha)):
            # Obra 26/10, etapa 4: a tela fica na MESMA folha (dividir/juntar
            # uma folha a mao, ou desfazer isso, muda os numeros das paginas
            # dela em diante; sem isto a tela pulava para a pagina de outra
            # folha). A pagina da vez passa a ser a primeira da folha.
            self.indice_pagina = next((p.indice for p in self.projeto.paginas
                                       if p.folha == self.indice_folha),
                                      min(self.indice_pagina, total - 1))
        elif total and not 0 <= self.indice_pagina < total:
            self.indice_pagina = total - 1
        if total:
            self.indice_folha = self.projeto.paginas[self.indice_pagina].folha
        self._montar_tira()
        self.atualizar()

    def desfazer(self) -> None:
        if self.acoes is None or self.projeto is None:
            return
        if self.acoes.feitas and self._acoes_esperam_pelas_marcacoes(
                [self.acoes.feitas[-1]], para_tras=True):
            return                       # pendencia da D2 (_espera_pelas_marcacoes)
        if self.acoes.desfazer(self.projeto) is not None:
            if self.previas is not None:
                self.previas.invalidar()
            self.lista_de_paginas_mudou()      # etapa 3: o Automatico muda a lista
            self._reacertar_as_opcoes()

    @protegido
    def refazer(self) -> None:
        if self.acoes is None or self.projeto is None:
            return
        if self.acoes.desfeitas and self._acoes_esperam_pelas_marcacoes(
                [self.acoes.desfeitas[-1]], para_tras=False):
            return                       # pendencia da D2 (_espera_pelas_marcacoes)
        if self.acoes.refazer(self.projeto) is not None:
            if self.previas is not None:
                self.previas.invalidar()
            self.lista_de_paginas_mudou()      # etapa 3: o Automatico muda a lista
            self._reacertar_as_opcoes()

    def _reacertar_as_opcoes(self) -> None:
        """Depois de desfazer ou refazer, a tela "O que fazer" deste mesmo
        projeto volta a mostrar o que ele tem agora (parecer do verificador,
        30/09, r15: desfeito o "Sim" da pergunta do fundo, ela continuava em
        "Tirar o fundo"). O menu Editar desfaz em qualquer tela, inclusive com
        "O que fazer" a vista; escondida, ela se reacerta sozinha ao aparecer
        (ui/tela_opcoes.showEvent). Nunca levanta excecao."""
        # Etapa 3 da obra: a tela "O que fazer" saiu do caminho; o que mostra
        # as escolhas do livro e o painel Automatico, que a atualizacao
        # (atualizar -> _atualizar_paineis) ja acerta. Fica so o aviso do
        # livro novo, que depende do projeto.
        try:
            self._mostrar_o_aviso_do_livro_novo()
            # o Automatico mostra o que o livro tem depois do desfazer (as
            # etapas ligadas, o filtro do livro...): como a tela "O que fazer"
            # acompanhava o desfazer (verificador, 30/09, r15)
            if self.projeto is not None:
                self.paineis.automatico.estado.do_projeto(self.projeto)
        except Exception:  # noqa: BLE001 - reacertar a tela nunca derruba o desfazer
            registrar_erro("reacertar as opcoes", traceback.format_exc())

    # --- teclado ----------------------------------------------------------

    def tratar_tecla(self, evento) -> bool:
        """Atalhos da secao 4.7. Devolve True se consumiu a tecla."""
        if not self._pronta():
            return False

        tecla = evento.key()
        ctrl = evento.modifiers() & Qt.ControlModifier
        shift = evento.modifiers() & Qt.ShiftModifier

        if ctrl and tecla == Qt.Key_Z:
            self.refazer() if shift else self.desfazer()
            return True
        if ctrl and tecla == Qt.Key_Y:
            self.refazer()
            return True
        if ctrl and tecla in (Qt.Key_Return, Qt.Key_Enter):
            self._pedir_processamento()
            return True

        # As letras das ferramentas (R O L P B V C Z E por padrão, mas
        # remapeáveis pela tela de Configurações). Nao conflitam com os
        # numeros 1 2 3 4, que continuam trocando o filtro. So valem sem Ctrl,
        # senao roubariam Ctrl+O e Ctrl+Z de quem espera abrir e desfazer.
        if not ctrl:
            letra = evento.text().upper()
            ferramenta = ferramenta_da_tecla(letra) or ferramenta_da_pagina_da_tecla(letra)
            if ferramenta is not None:
                self.escolher_ferramenta(ferramenta)
                return True
            if ABA_BORDAS in self._abas_ativas:
                if letra == atalhos.tecla_atual(CHAVE_RECORTE_ESPELHADO):
                    self.botao_espelhado.click()
                    return True
                if letra == atalhos.tecla_atual(CHAVE_RECORTE_PROPORCAO):
                    self.botao_proporcao_travada.click()
                    return True

        if tecla == _QT_KEY_DAS_TECLAS_DE_NAVEGACAO.get(
                atalhos.tecla_atual(CHAVE_NAVEGAR_ANTERIOR), Qt.Key_Left):
            self._navegar(-1)
            return True
        if tecla == _QT_KEY_DAS_TECLAS_DE_NAVEGACAO.get(
                atalhos.tecla_atual(CHAVE_NAVEGAR_PROXIMA), Qt.Key_Right):
            self._navegar(1)
            return True
        # Etapa 6 da obra (D-021: "Page Up/Down, Home/End"; PEDIDOS.md, "Page
        # Up / Page Down pula 10 páginas": "Pula 10 páginas de cada vez"):
        # Page Down/Up andam 10 páginas (10 folhas, no Dividir), Home vai à
        # primeira e End à última. Sem Ctrl (Ctrl+Home/End ficam livres).
        if not ctrl and tecla in (Qt.Key_PageDown, Qt.Key_PageUp, Qt.Key_Home, Qt.Key_End):
            total = self._total()
            destino = {Qt.Key_PageDown: self.indice_atual + self.PAGINAS_DO_PAGE_DOWN,
                       Qt.Key_PageUp: self.indice_atual - self.PAGINAS_DO_PAGE_DOWN,
                       Qt.Key_Home: 0, Qt.Key_End: total - 1}[tecla]
            if total:
                self._ir_para(max(0, min(total - 1, destino)))
            return True
        if tecla == _QT_KEY_DAS_TECLAS_DE_NAVEGACAO.get(
                atalhos.tecla_atual(CHAVE_MARCAR_CERTO), Qt.Key_Space):
            self.marcar_certo_e_avancar()
            return True
        if tecla == _QT_KEY_DAS_TECLAS_DE_NAVEGACAO.get(
                atalhos.tecla_atual(CHAVE_PROXIMO_ALERTA), Qt.Key_Tab):
            self._ir_para_proximo_alerta()
            return True
        if tecla == Qt.Key_Delete:
            # Samuel, 07/10/2026: "Deixar em branco" (tecla Delete). Ate a
            # etapa 2 da obra a Delete apagava (tirava do livro) a pagina.
            self.deixar_em_branco_ou_voltar()
            return True
        # A tecla R de "girar" (fixa aqui, fora das Configuracoes) nunca era
        # alcancada: a R do Retangulo ganha antes (Lista de bugs, 02/10).
        # Saiu no item 2.3: girar agora e Ctrl+Seta (menu Pagina) e a R fica
        # so para o Retangulo, como o desenho da conferencia 14 dizia.

        atalhos_de_filtro = {
            Qt.Key_1: ORIGINAL, Qt.Key_2: PRETO_E_BRANCO,
            Qt.Key_3: MELHORAR, Qt.Key_4: MAGICO_PRO,
        }
        if tecla in atalhos_de_filtro and not self.trabalha_com_folhas:
            self._escolher_filtro(atalhos_de_filtro[tecla])
            return True

        return False

    # --- saida ------------------------------------------------------------

    def _avisar_problema(self) -> None:
        """O que o usuario ve quando algo deu errado por baixo dos panos."""
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Um momento")
        caixa.setIcon(QMessageBox.Information)
        caixa.setText("Não consegui fazer isso agora.")
        caixa.setInformativeText(
            "O programa continua funcionando e o seu trabalho está salvo. "
            "Tente de novo, ou passe para a próxima página."
        )
        caixa.addButton("entendi", QMessageBox.AcceptRole)
        caixa.exec()

    @protegido
    def _pedir_processamento(self) -> None:
        """Avisa se ainda ha dúvidas, mas nunca bloqueia.

        A janela "Antes de processar" agora LISTA as páginas e os motivos
        (Samuel, rodada 5 do "Para revisar", 08/10/2026, `rv5-aviso-so-texto`:
        "Lista as páginas e os motivos"; rodada 4: "quando alguém tentar
        imprimir sem ver os alertas o programa para e mostra os alertas e a
        pessoa diz se quer ver ou continuar"). Antes só dizia quantas
        páginas eram. "ver" leva à página escolhida e não processa;
        "continuar assim mesmo" processa; fechar no X não processa. Sem
        aviso pendente, processa direto, como sempre."""
        if self.projeto is None:
            return
        if avisos_do_livro.pendentes_do_livro(self.projeto):
            from ui.janela_dos_avisos import CONTINUAR

            if self._mostrar_a_lista_dos_avisos(antes_de_processar=True) != CONTINUAR:
                return
        self.processar.emit()


MINIATURAS_DE_FABRICA = {"lugar": EMBAIXO, "aberta": True, "em_pares": False}


def miniaturas_guardadas() -> dict:
    """Como as miniaturas ficaram no último livro (configuracoes.json,
    "miniaturas"; layout, 22/10/2026, "Sim, lembrar para todos os livros").
    Cada valor estranho (arquivo mexido, versão antiga) volta ao de fábrica,
    sozinho, sem estragar os outros."""
    import configuracoes

    try:
        salvo = configuracoes.ler("miniaturas")
    except Exception:  # noqa: BLE001 - preferência nunca impede a tela de abrir
        salvo = None
    salvo = salvo if isinstance(salvo, dict) else {}
    lugar = salvo.get("lugar")
    return {
        "lugar": lugar if lugar in (EMBAIXO, ESQUERDA, DIREITA) else MINIATURAS_DE_FABRICA["lugar"],
        "aberta": salvo["aberta"] if isinstance(salvo.get("aberta"), bool) else MINIATURAS_DE_FABRICA["aberta"],
        "em_pares": (salvo["em_pares"] if isinstance(salvo.get("em_pares"), bool)
                     else MINIATURAS_DE_FABRICA["em_pares"]),
    }


def _icone_de_ajustar_o_pedaco():
    """A pista visual do botao "Ajustar o pedaco a figura": um retangulo
    tracejado (o pedaco como esta) com um cheio menor dentro (a figura) e
    quatro setinhas para dentro. Desenhado com QPainter - nunca emoji (regra
    3). Seguro mudar o desenho."""
    from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap

    lado = 32
    figura = QPixmap(lado, lado)
    figura.fill(Qt.transparent)
    pintor = QPainter(figura)
    pintor.setRenderHint(QPainter.Antialiasing)
    pintor.setPen(QPen(QColor(estilo.cor("fraco")), 2, Qt.DashLine))
    pintor.drawRect(2, 2, lado - 5, lado - 5)
    pintor.setPen(QPen(QColor(estilo.AZUL), 2))
    pintor.setBrush(QColor(estilo.AZUL_CLARO))
    pintor.drawRect(10, 10, lado - 21, lado - 21)
    meio = lado // 2
    for (x0, y0, x1, y1) in ((meio, 4, meio, 8), (meio, lado - 5, meio, lado - 9),
                             (4, meio, 8, meio), (lado - 5, meio, lado - 9, meio)):
        pintor.drawLine(x0, y0, x1, y1)
    pintor.end()
    return QIcon(figura)


def _ligar(botao: QPushButton, acao) -> None:
    """Liga o clique ignorando o argumento 'checked' que o Qt manda junto."""
    botao.clicked.connect(lambda *_: acao())


def _botao(texto: str, destino: QHBoxLayout, acao, objeto: str = "") -> QPushButton:
    botao = QPushButton(texto)
    if objeto:
        botao.setObjectName(objeto)
    _ligar(botao, acao)
    destino.addWidget(botao)
    return botao


# A força do preto que o botão "usar mais fraco" dos avisos põe (o "mais
# escuro" é core.pipeline.FORCA_DO_REFORCO). O mesmo número dos projetos
# antigos (modelos._migrar). Seguro mudar.
FORCA_MAIS_FRACA = 15


# --- etapa 2 do layout: a trilha no lugar das abas -------------------------
# Cada ferramenta de pagina da trilha escolhe a "aba" dela (as abas ficam por
# dentro, escondidas). "Os quatro filtros" e provisorio ate a etapa 4.
ABA_DA_FERRAMENTA = {
    FERRAMENTA_DIVIDIR: ABA_CORTE,
    FERRAMENTA_CORTAR: ABA_BORDAS,
    FERRAMENTA_ENDIREITAR: ABA_ANGULO,
    FERRAMENTA_MOVER: ABA_MOVER,          # etapa 5 da obra (D-008)
    FERRAMENTA_FILTROS: ABA_FILTRO,
}

# Etapa 5 da obra: os campos da pagina que so mudam ONDE a pagina pronta fica
# na area branca (ferramenta Mover). A previa da pagina nao depende deles (a
# chave do GerenciadorPrevias nao os tem; a tela compoe ao vivo): mexer neles
# nao precisa desenhar a pagina de novo. Arriscado: por aqui um campo que muda
# o desenho da pagina (a previa ficaria velha).
CAMPOS_SO_DO_MOVER = frozenset({"conteudo_escala", "conteudo_deslocamento",
                                "tamanho_folha_cm", "mexida_a_mao"})
FERRAMENTA_DA_ABA = {aba: ferramenta for ferramenta, aba in ABA_DA_FERRAMENTA.items()}

# As margens (esquerda, cima, direita, baixo) da fila de botoes embaixo da
# pagina, quando ela tem botoes (Marcar e os quatro filtros). Com a fila vazia
# (Dividir, Cortar e Endireitar, cujos botoes moram no painel Propriedades
# desde a etapa 3 do layout) as margens somem. Seguro mudar.
MARGENS_DA_FILA_DE_BOTOES = (10, 6, 10, 4)

# Quanto os botoes de girar do canto ficam afastados da beira direita e de
# cima da area da pagina (o desenho: 12 e 10). Seguro mudar.
FOLGA_DO_GIRAR_NO_CANTO = (12, 10)


def _icone_da_barra(qual: str):
    """Os icones da barra de baixo (desfazer, refazer, historico), desenhados a
    mao na cor do texto do tema (nada de emoji em rotulo)."""
    from PySide6.QtCore import QPointF, QRectF
    from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

    escala, lado = 3, 16
    imagem = QPixmap(lado * escala, lado * escala)
    imagem.fill(Qt.transparent)
    p = QPainter(imagem)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(escala, escala)
    p.setPen(QPen(QColor(estilo.cor("texto")), 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    caminho = QPainterPath()
    if qual in ("desfazer", "refazer"):
        caminho.moveTo(3, 6)
        caminho.lineTo(10, 6)
        caminho.arcTo(QRectF(6, 6, 8, 8), 90, -180)
        caminho.lineTo(7, 14)
        p.drawPath(caminho)
        p.drawLine(QPointF(3, 6), QPointF(6, 3))
        p.drawLine(QPointF(3, 6), QPointF(6, 9))
        if qual == "refazer":
            p.end()
            from PySide6.QtGui import QTransform
            # espelhado pela transformação (o QImage.mirrored saiu de uso no Qt 6)
            imagem = imagem.transformed(QTransform().scale(-1, 1))
            imagem.setDevicePixelRatio(escala)
            return QIcon(imagem)
    else:
        p.drawEllipse(QRectF(2.5, 2.5, 11, 11))
        p.drawLine(QPointF(8, 5), QPointF(8, 8))
        p.drawLine(QPointF(8, 8), QPointF(10.5, 9.5))
    p.end()
    imagem.setDevicePixelRatio(escala)
    return QIcon(imagem)


# Item 2.2 (G5): cada clique nas setas da aba Endireitar, em graus, e quanto
# se espera depois do ultimo clique para gravar (uma acao so do desfazer).
# Seguro mudar.
PASSO_DO_ANGULO = 0.1
ESPERA_PARA_GRAVAR_O_ANGULO_MS = 700


def _graus(angulo: float) -> str:
    """-1.5 -> "-1,5°" (virgula, como o Samuel le)."""
    return f"{angulo:+.1f}°".replace(".", ",")


def texto_dos_angulos_medidos(medidas: dict | None) -> str:
    """O texto ao lado da lista "conta:" da aba Endireitar (item 2.2). Seguro
    mudar: o texto."""
    if not medidas:
        return "(medindo...)"
    partes = []
    if medidas.get("scantailor") is not None:
        partes.append(f"ScanTailor {_graus(medidas['scantailor'])}")
    if medidas.get("programa") is not None:
        # Rodada 13 do layout, 805 C ("A conta vira 'Editor'"): so o texto
        # desta linha; o codigo gravado no projeto continua "programa", e a
        # lista "conta:" (core/endireitar_scantailor) nao foi mexida.
        partes.append(f"Editor {_graus(medidas['programa'])}")
    texto = " · ".join(partes)
    if medidas.get("discordam"):
        texto += "  (discordam)"
    return texto


# --- obra de 26/10/2026, etapa 3: a marca "mexida a mao" (core/etapas) --------
# Qual campo da pagina (ou da folha), mexido pela tela, marca qual etapa. Ver
# TelaConferir._com_a_marca_mexida_a_mao. Seguro mudar: acrescentar campo novo
# que a pessoa muda a mao. Arriscado: tirar um (a edicao deixaria de valer com
# a etapa desligada, D-009, e a pergunta do Automatico, D-004, nao a veria).
MARCAS_DA_PAGINA = {
    "recorte": etapas_core.CORTAR,
    "angulo_manual": etapas_core.ENDIREITAR,
    "filtro": etapas_core.FILTRO, "forca_preto": etapas_core.FILTRO,
    "clareza_melhorar": etapas_core.FILTRO, "intensidade_magico": etapas_core.FILTRO,
    "algoritmo_preto_branco": etapas_core.FILTRO, "limpar_pontinhos": etapas_core.FILTRO,
    "misto_so_as_letras": etapas_core.FILTRO, "misto_fora_do_texto": etapas_core.FILTRO,
    "misto_papel_da_gravura": etapas_core.FILTRO, "misto_letras_na_moldura": etapas_core.FILTRO,
    "luz_igualar": etapas_core.FILTRO, "luz_suavizar": etapas_core.FILTRO,
    "luz_chuvisco": etapas_core.FILTRO, "claro_no_escuro": etapas_core.FILTRO,
    "letras_com_a_cor": etapas_core.FILTRO, "reduzir_cores": etapas_core.FILTRO,
    "selecao": etapas_core.MARCAR,
    "conteudo_escala": etapas_core.MOVER, "conteudo_deslocamento": etapas_core.MOVER,
    "tamanho_folha_cm": etapas_core.MOVER,
}
MARCAS_DA_FOLHA = {
    "dividir": etapas_core.DIVIDIR, "posicao_corte": etapas_core.DIVIDIR,
    "dividir_como": etapas_core.DIVIDIR,
    "rotacao": etapas_core.GIRAR,
}
# Campos que, voltando a None, devolvem a etapa ao automatico ("usar o corte do
# programa", "usar o ângulo do programa"): a marca sai.
DEVOLVEM_AO_AUTOMATICO = ("recorte", "angulo_manual")


def _nome_do_retangulo(projeto) -> str:
    """D-094: a escolha do livro para o corte quando o angulo muda, em
    portugues (a parte "Para o livro todo" do Endireitar)."""
    jeito = getattr(projeto, "retangulo_do_corte", None)
    if jeito == "acompanha":
        return "acompanha o texto"
    if jeito == "fica":
        return "fica no mesmo lugar"
    return "o das Configurações"
