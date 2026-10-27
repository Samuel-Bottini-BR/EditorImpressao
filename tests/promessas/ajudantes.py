"""Ajudantes da prova das promessas dos botões (tests/test_promessas.py).

Bateria nova de 26/10/2026, parte 4 (D-010, Samuel: "eu acho que o botão tem que ser provado que
ele faz o que se diz que se faz, e não só se ele muda algo na tela."). Escritos pelo verificador,
que não construiu o programa.

Quatro coisas moram aqui, para o teste ficar curto e para a gerente ajustar UM lugar quando a tela
mudar (a etapa 3 da obra muda o jeito de abrir o livro):

1. O LIVRO DE TESTE (`criar_livro`): um PDF pequeno de verdade, papel amarelado, e em cada folha um
   bloco preto numa altura diferente — é por ele que se sabe, no PDF que sai, QUAL página é qual
   (`qual_pagina`). Sem lombada, capa ou couro (regra de 21/10: só o que vai ser impresso).
2. ABRIR, GRAVAR E GERAR: `abrir_livro_para_teste` (o único lugar que sabe como o livro chega à área
   de trabalho — hoje passa pela tela "O que fazer" sem marcar nada; depois da etapa 3, abre direto),
   `projeto_gravado`/`acoes_gravadas` (o que ficou no disco) e `gerar_pdf` (aperta o "Confirmar e
   processar" de verdade e espera o PDF).
3. MEDIR O PDF: `paginas_do_pdf` desenha cada página do PDF que saiu e as medidas dizem o que tem
   nela (branca? preto e branco? amarelada? deitada?).
4. A LISTA DE PROMESSAS (`ler_promessas`) e a VARREDURA dos botões (`chave_do_botao` e companhia):
   cada botão à vista ganha uma chave "tela/lugar/rótulo"; o teste confere que toda chave tem
   promessa escrita.

Nada aparece na tela (tests/conftest.py: offscreen e vigia nas caixas).
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_DAS_PROMESSAS = Path(__file__).resolve().parent / "promessas.md"

# --- 1. o livro de teste ------------------------------------------------------------------------

DPI_DO_LIVRO = 150
LARGURA_PX, ALTURA_PX = 600, 840            # 10,2 x 14,2 cm a 150 DPI
AMARELADO = (170, 215, 235)                  # BGR: papel velho
# altura do meio do bloco que identifica a página i (fração da altura)
ALTURA_DO_BLOCO = 0.05
PRIMEIRO_BLOCO = 0.14
PASSO_DO_BLOCO = 0.13
COLUNA_DO_BLOCO = (0.14, 0.44)               # x de começo e fim (fração da largura)


def imagem_da_folha(indice: int) -> np.ndarray:
    """Uma folha do livro de teste: papel amarelado, o bloco preto da folha `indice` (à esquerda,
    numa altura só dela) e seis "linhas de texto" à direita (para a página não parecer em branco)."""
    img = np.full((ALTURA_PX, LARGURA_PX, 3), AMARELADO, np.uint8)
    meio = PRIMEIRO_BLOCO + PASSO_DO_BLOCO * indice
    y0, y1 = int((meio - ALTURA_DO_BLOCO / 2) * ALTURA_PX), int((meio + ALTURA_DO_BLOCO / 2) * ALTURA_PX)
    x0, x1 = int(COLUNA_DO_BLOCO[0] * LARGURA_PX), int(COLUNA_DO_BLOCO[1] * LARGURA_PX)
    img[y0:y1, x0:x1] = 0
    for linha in range(6):
        y = int((0.12 + 0.12 * linha) * ALTURA_PX)
        img[y:y + 9, int(0.55 * LARGURA_PX):int(0.86 * LARGURA_PX)] = 30
    return img


def criar_livro(pasta: Path, folhas: int = 4, nome: str = "Livro de Teste") -> Path:
    """O PDF do livro de teste, com `folhas` folhas (no máximo 6: o bloco tem de caber)."""
    import cv2
    import fitz

    assert 1 <= folhas <= 6
    (pasta / "livros").mkdir(parents=True, exist_ok=True)
    caminho = pasta / "livros" / f"{nome}.pdf"
    doc = fitz.open()
    largura_pt, altura_pt = LARGURA_PX / DPI_DO_LIVRO * 72, ALTURA_PX / DPI_DO_LIVRO * 72
    for i in range(folhas):
        ok, png = cv2.imencode(".png", imagem_da_folha(i))
        assert ok
        pagina = doc.new_page(width=largura_pt, height=altura_pt)
        pagina.insert_image(fitz.Rect(0, 0, largura_pt, altura_pt), stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()
    return caminho


# --- 3. medir o PDF ---------------------------------------------------------------------------

@dataclass
class PaginaDoPdf:
    """Uma página do PDF que saiu: o tamanho (pontos) e a imagem desenhada (BGR)."""

    largura_pt: float
    altura_pt: float
    imagem: np.ndarray = field(repr=False)

    @property
    def deitada(self) -> bool:
        return self.largura_pt > self.altura_pt * 1.05

    @property
    def cinza(self) -> np.ndarray:
        return self.imagem.mean(axis=2)


def paginas_do_pdf(caminho: Path | str, dpi: int = 60) -> list[PaginaDoPdf]:
    """Desenha cada página do PDF (pelo PyMuPDF, como um leitor de PDF faria) e devolve as medidas."""
    import fitz

    saida = []
    with fitz.open(str(caminho)) as doc:
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
            img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)[:, :, ::-1]
            saida.append(PaginaDoPdf(pagina.rect.width, pagina.rect.height, img.copy()))
    return saida


def fracao_escura(img: np.ndarray, limite: int = 100) -> float:
    return float((img.mean(axis=2) < limite).mean())


def esta_branca(pagina: PaginaDoPdf) -> bool:
    """Página toda branca: nada mais escuro que 230 em mais de 0,1% da página."""
    return float((pagina.cinza < 230).mean()) < 0.001


def papel_amarelado(pagina: PaginaDoPdf) -> bool:
    """O papel continua amarelado (o filtro Original): o canto de cima à direita, onde só há papel,
    tem o azul bem mais baixo que o vermelho (BGR)."""
    h, w = pagina.imagem.shape[:2]
    canto = pagina.imagem[int(h * 0.02):int(h * 0.07), int(w * 0.88):int(w * 0.97)].reshape(-1, 3)
    b, _g, r = canto.mean(axis=0)
    return r - b > 35


def so_preto_e_branco(pagina: PaginaDoPdf) -> bool:
    """A página saiu em preto e branco: sem cor (os três canais iguais) e quase sem meio-tom
    (mais de 97% dos pontos abaixo de 60 ou acima de 200; o desenho do PDF suaviza as beiradas)."""
    img = pagina.imagem.astype(int)
    sem_cor = float(np.abs(img[:, :, 0] - img[:, :, 2]).mean()) < 4
    cinza = pagina.cinza
    extremos = float(((cinza < 60) | (cinza > 200)).mean())
    return sem_cor and extremos > 0.97


def qual_pagina(pagina: PaginaDoPdf) -> int | None:
    """Qual folha do livro de teste é esta página do PDF, pela altura do bloco preto (None: não
    tem bloco, por exemplo página em branco). Vale com a página no tamanho do livro (sem corte)."""
    h, w = pagina.imagem.shape[:2]
    faixa = pagina.cinza[:, int(w * 0.18):int(w * 0.40)]
    escuras = np.where((faixa < 90).mean(axis=1) > 0.8)[0]
    if escuras.size < 3:
        return None
    meio = float(escuras.mean()) / h
    indice = round((meio - PRIMEIRO_BLOCO) / PASSO_DO_BLOCO)
    if abs(PRIMEIRO_BLOCO + PASSO_DO_BLOCO * indice - meio) > 0.03:
        return None
    return int(indice)


# --- 2. abrir, gravar e gerar -----------------------------------------------------------------

# As caixinhas da tela "O que fazer" (ui/tela_opcoes.py). D-009 (26/10): "eu deveria conseguir abrir
# o livro sem escolher nenhuma opção para fazer tudo manualmente." O livro do teste abre SEM
# nenhuma, como vai abrir depois da etapa 3 (D-002: direto na área de trabalho).
CAIXINHAS_DA_TELA_O_QUE_FAZER = ("cx_dividir", "cx_cortar", "cx_endireitar", "cx_limpar", "cx_cadernos")


def assentar(vezes: int = 6) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def abrir_livro_para_teste(janela, caminho: Path | str, marcadas: tuple[str, ...] = ()):
    """Leva o livro até a área de trabalho e devolve a TelaConferir.

    O ÚNICO lugar do teste que sabe o caminho de abrir (pedido da gerente, 26/10: a etapa 3 muda
    tudo aqui). Hoje: `abrir_livro` vai à tela "O que fazer"; desmarca tudo (menos `marcadas`) e
    faz o que o "Conferir" faz, sem a tarefa de fundo (o detector de gravura desligado: precisa
    dos modelos, que não estão no GitHub). Depois da etapa 3 o livro abre direto na área de
    trabalho e este ajudante só espera."""
    from core import pipeline
    from ui.janela_principal import CONFERIR, OPCOES

    janela.abrir_livro(str(caminho))
    if janela.aviso_do_fundo is not None:          # "Este livro tem fundo separado?" (PDF com camadas)
        janela.aviso_do_fundo.done(0)
    if janela.telas.currentIndex() == OPCOES:
        opcoes = janela.tela_opcoes
        for nome in CAIXINHAS_DA_TELA_O_QUE_FAZER:
            caixa = getattr(opcoes, nome, None)
            if caixa is not None:
                caixa.setChecked(nome in marcadas)
        janela.projeto.detectar_regioes = False
        janela._analise_pronta(pipeline.analisar_projeto(janela.projeto))
    fim = time.monotonic() + 60
    while janela.telas.currentIndex() != CONFERIR and time.monotonic() < fim:
        assentar(2)
        time.sleep(0.02)
    assert janela.telas.currentIndex() == CONFERIR, "o livro não chegou à área de trabalho"
    janela.resize(1280, 760)
    janela.show()
    assentar()
    return janela.tela_conferir


def pasta_do_projeto(janela) -> Path:
    return Path(janela.resumo.pasta)


def projeto_gravado(janela) -> dict:
    """O projeto.json como ficou no disco, depois de o programa gravar o que tinha para gravar
    (o relógio de salvar junta a rajada em 0,6 s: aqui ele é adiantado, como ao fechar)."""
    import projetos

    janela._salvar_agora()
    projetos.esperar_gravacoes()
    return json.loads((pasta_do_projeto(janela) / "projeto.json").read_text(encoding="utf-8"))


def acoes_gravadas(janela) -> list[dict]:
    """As ações do acoes.jsonl (o Histórico gravado), na ordem."""
    caminho = pasta_do_projeto(janela) / "acoes.jsonl"
    if not caminho.exists():
        return []
    return [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines() if linha.strip()]


def pagina_gravada(janela, indice: int) -> dict:
    return projeto_gravado(janela)["paginas"][indice]


def gerar_pdf(janela, monkeypatch, destino: Path, segundos: float = 240) -> Path:
    """Aperta o "Confirmar e processar" da área de trabalho, como o Kaique: a janela "Antes de
    processar" (se aparecer) responde "continuar assim mesmo"; a janela "Confirmar e processar"
    recebe o destino e aperta "Processar". Espera a tela "Ficou pronto!" e devolve o PDF."""
    import ui.janela_confirmar as confirmar
    from ui.janela_dos_avisos import CONTINUAR
    from ui.janela_principal import CONFERIR, FINAL

    destino.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *_a, **_k: destino)
    tela = janela.tela_conferir
    monkeypatch.setattr(type(tela), "_mostrar_a_lista_dos_avisos",
                        lambda self, antes_de_processar=False: CONTINUAR)
    if janela.telas.currentIndex() == CONFERIR:
        tela.botao_processar.click()
    else:
        janela.processar()
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        assentar(2)
        if janela.telas.currentIndex() == FINAL:
            return Path(janela.tela_final.caminho)
        if janela.telas.currentIndex() == CONFERIR and getattr(janela, "avisos", None):
            raise AssertionError(f"o processamento falhou: {janela.avisos}")
        time.sleep(0.02)
    raise AssertionError(f"o PDF não ficou pronto em {segundos} s (tela {janela.telas.currentIndex()})")


def responder_caixa(monkeypatch, classe, clicar: str, antes=None, registro: list | None = None):
    """Quando uma caixa da `classe` abrir (exec), aperta o botão cujo texto começa com `clicar`
    (pelo clique de verdade do botão), depois de chamar `antes(caixa)` se houver. Anota o título
    e os botões em `registro`."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QAbstractButton

    original = classe.exec

    def _clicar(caixa) -> None:
        if antes is not None:
            antes(caixa)
        botoes = [b for b in caixa.findChildren(QAbstractButton) if b.isVisibleTo(caixa)]
        if registro is not None:
            registro.append((caixa.windowTitle(), [b.text() for b in botoes]))
        alvo = next((b for b in botoes if b.text().replace("&", "").startswith(clicar)), None)
        if alvo is None:
            caixa.reject()
            raise AssertionError(f"a caixa '{caixa.windowTitle()}' não tem o botão '{clicar}': "
                                 f"{[b.text() for b in botoes]}")
        alvo.click()

    def _exec(caixa, *args, **kwargs):
        QTimer.singleShot(0, lambda: _clicar(caixa))
        return original(caixa, *args, **kwargs)

    monkeypatch.setattr(classe, "exec", _exec)


def caixas_durante(acao, clicar: str | None = None, antes=None) -> list[tuple[str, list[str]]]:
    """Faz `acao()` e anota cada caixa de pergunta ou de digitar (QMessageBox, QInputDialog) que
    abrir: (título, [botões]). Em cada uma, aperta o botão que começa com `clicar` (clique de
    verdade); sem `clicar`, ou sem esse botão, desiste dela (Esc). `antes(caixa)` roda antes do
    clique (para digitar num campo). Troca o exec só durante a chamada."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QAbstractButton, QInputDialog, QMessageBox

    vistas: list[tuple[str, list[str]]] = []

    def _responder(caixa) -> None:
        if isinstance(caixa, QMessageBox):
            botoes = [b for b in caixa.buttons()]
        else:
            botoes = [b for b in caixa.findChildren(QAbstractButton) if b.isVisibleTo(caixa)]
        vistas.append((caixa.windowTitle(), [b.text().replace("&", "") for b in botoes]))
        if antes is not None:
            antes(caixa)
        alvo = None
        if clicar is not None:
            alvo = next((b for b in botoes if b.text().replace("&", "").startswith(clicar)), None)
        if alvo is not None:
            alvo.click()
        else:
            caixa.reject()

    originais = {QMessageBox: QMessageBox.__dict__.get("exec"),
                 QInputDialog: QInputDialog.__dict__.get("exec")}
    base = {QMessageBox: QMessageBox.exec, QInputDialog: QInputDialog.exec}

    def _embrulhar(classe):
        def _exec(caixa, *args, **kwargs):
            QTimer.singleShot(0, lambda: _responder(caixa))
            return base[classe](caixa, *args, **kwargs)
        return _exec

    for classe in originais:
        classe.exec = _embrulhar(classe)
    try:
        acao()
    finally:
        for classe, original in originais.items():
            if original is None:
                try:
                    del classe.exec
                except AttributeError:
                    pass
            else:
                classe.exec = original
    return vistas


def acoes_de_menu_aberto(abrir, escolher: str | None = None) -> list[str]:
    """Os itens de um menu que a tela monta na hora do clique (os três pontinhos das miniaturas, o
    "Mais..." do livro aberto, o menu do cartão, o grupo da trilha): chama `abrir()` e devolve os
    textos ("Lugar > Embaixo" para os de um submenu), fechando o menu. Com `escolher`, aciona
    (trigger) depois o item cujo texto começa assim, como o clique.

    Por que um relógio e não trocar o QMenu.exec: no PySide6 6.11 o exec de um QMenu NÃO passa pelo
    atributo da classe (testado: o menu abria assim mesmo e o teste parava). O relógio acha o menu
    aberto (QApplication.activePopupWidget), anota e fecha."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QMenu

    vistos: list[str] = []
    escolhida = []

    def _percorrer(menu, antes: str = "") -> None:
        for acao in menu.actions():
            if acao.isSeparator() or not acao.isVisible():
                continue
            texto = antes + acao.text().replace("&", "").split("\t")[0]
            if acao.menu() is not None:
                _percorrer(acao.menu(), texto + " > ")
                continue
            if not acao.isEnabled() and not acao.isCheckable() and texto.endswith("direito"):
                continue                       # o título apagado do grupo da trilha
            vistos.append(texto)
            if escolher is not None and not escolhida and texto.startswith(escolher):
                escolhida.append(acao)

    def _pegar() -> bool:
        menu = QApplication.activePopupWidget()
        if isinstance(menu, QMenu):
            _percorrer(menu)
            menu.close()
            return True
        return False

    relogio = QTimer()
    relogio.setInterval(0)
    relogio.timeout.connect(lambda: _pegar() and relogio.stop())
    relogio.start()
    try:
        abrir()
        if not vistos:
            _pegar()                           # o menu do popup() não para a chamada
    finally:
        relogio.stop()
    if escolhida:
        escolhida[0].trigger()
    elif escolher is not None:
        raise AssertionError(f"o menu não tem '{escolher}': {vistos}")
    return vistos


# --- 4. a lista de promessas e a varredura dos botões ------------------------------------------

@dataclass
class Promessa:
    """Uma entrada de tests/promessas/promessas.md."""

    numero: str                       # "P-001"
    titulo: str
    chaves: list[str]
    campos: dict[str, str]

    @property
    def aguarda(self) -> str:
        """"etapa N, D-xxx" quando a promessa é de decisão ainda não construída (xfail estrito)."""
        return self.campos.get("aguarda", "").strip()

    @property
    def some_na(self) -> str:
        """Botão que vai sair do programa (ex.: os da tela "O que fazer", etapa 3)."""
        return self.campos.get("sai na", "").strip()


_CABECA = re.compile(r"^### (P-\d{3}) · (.+)$")
_CAMPO = re.compile(r"^- \*\*([^*]+):\*\* ?(.*)$")
_CHAVE = re.compile(r"`([^`]+)`")


def ler_promessas(caminho: Path = ARQUIVO_DAS_PROMESSAS) -> dict[str, Promessa]:
    """Lê promessas.md: cada "### P-NNN · título" seguido de linhas "- **campo:** texto" (o texto
    pode continuar nas linhas de baixo, com recuo). O campo "chaves" lista as chaves entre crases."""
    promessas: dict[str, Promessa] = {}
    atual: Promessa | None = None
    campo_atual = ""
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        cabeca = _CABECA.match(linha)
        if cabeca:
            numero = cabeca.group(1)
            assert numero not in promessas, f"{numero} repetido em promessas.md"
            atual = Promessa(numero, cabeca.group(2).strip(), [], {})
            promessas[numero] = atual
            campo_atual = ""
            continue
        if atual is None:
            continue
        if linha.startswith("#"):
            atual = None
            continue
        campo = _CAMPO.match(linha)
        if campo:
            campo_atual = campo.group(1).strip().lower()
            atual.campos[campo_atual] = campo.group(2).strip()
        elif linha.startswith("  ") and campo_atual:
            atual.campos[campo_atual] += " " + linha.strip()
        if campo_atual == "chaves" and (campo or linha.startswith("  ")):
            atual.chaves.extend(_CHAVE.findall(linha))
    return promessas


_DIGITOS = re.compile(r"\b\d+\b")
_ESPACOS = re.compile(r"\s+")


def rotulo_do_botao(texto: str, dica: str = "") -> str:
    """O rótulo de um botão para a chave: o texto (ou, sem texto, a dica até o primeiro parêntese
    ou ponto), sem "&", sem a tecla escrita depois de vários espaços ("Voltar para os livros   Esc"),
    com os números trocados por N (contagens que mudam: "só as que precisam de atenção (3)")."""
    base = texto.replace("&", "").split("\n")[0]
    base = re.split(r" {3,}|\t", base)[0].strip()
    if not base:
        base = dica.split("\n")[0]
        base = re.split(r"\s+\(|\.\s|\.$|:", base)[0].strip()
    base = base.split(":")[0].strip() if base.startswith("cor de pintar") else base
    base = _DIGITOS.sub("N", base)
    return _ESPACOS.sub(" ", base)


def eh_botao_de_verdade(botao) -> bool:
    """Fica de fora o que é peça interna do Qt (as setinhas de rolar de uma QTabBar, o "x" de
    limpar de um campo de texto, os botões de uma barra de rolagem) e as caixinhas e bolinhas de
    escolha (QCheckBox, QRadioButton: são opções, não botões; ficam para a próxima leva)."""
    from PySide6.QtWidgets import QCheckBox, QLineEdit, QRadioButton, QTabBar

    if isinstance(botao, (QCheckBox, QRadioButton)):
        return False
    pai = botao.parentWidget()
    if isinstance(pai, (QTabBar, QLineEdit)):
        return False
    return not botao.objectName().startswith("qt_")


def botoes_a_vista(raiz) -> list:
    """Os botões (QAbstractButton) dentro de `raiz` que estão à vista agora."""
    from PySide6.QtWidgets import QAbstractButton

    return [b for b in raiz.findChildren(QAbstractButton)
            if eh_botao_de_verdade(b) and b.isVisibleTo(raiz) and b.window().isVisible()]


def lugar_de(botao, lugares: list[tuple[str, object]]) -> str:
    """O nome do primeiro lugar (na ordem da lista: os mais de dentro primeiro) que contém o botão."""
    for nome, widget in lugares:
        if widget is None:
            continue
        try:
            if widget is botao or widget.isAncestorOf(botao):
                return nome
        except RuntimeError:              # peça já destruída pelo Qt
            continue
    return "?"


def lugares_da_area_de_trabalho(tela) -> list[tuple[str, object]]:
    """Os lugares da área de trabalho, do mais de dentro para o mais de fora. QUANDO A TELA MUDAR
    (etapa 3: painel Automático novo; etapa 6: "Ver lado a lado"), é aqui que se acrescenta o lugar
    novo; botão em lugar desconhecido vira "?" e reprova a varredura até ganhar lugar e promessa."""
    paineis = tela.paineis
    props = getattr(tela, "propriedades_das_abas", {})
    pagina = None
    if getattr(tela, "botao_em_branco", None) is not None:
        pagina = tela.botao_em_branco.parentWidget()
    return [
        ("processar", getattr(tela, "botao_processar", None)),
        ("faixa do aviso", getattr(tela, "faixa", None)),
        ("girar do canto", getattr(tela, "girar_do_canto", None)),
        ("girar a folha", getattr(tela, "barra_girar", None)),
        ("esta página", pagina),
        ("dividir", props.get("corte")),
        ("cortar", props.get("bordas")),
        ("endireitar", props.get("angulo")),
        ("marcar", paineis.propriedades.conteudo_de_marcar),
        ("propriedades", paineis.propriedades),
        ("filtro da página", paineis.filtro_da_pagina),
        ("para revisar", paineis.para_revisar),
        ("automático", paineis.automatico),
        ("histórico", paineis.historico),
        ("lado direito", paineis),
        ("miniaturas", getattr(tela, "miniaturas", None)),
        ("barra de baixo", _barra_de_baixo(tela)),
        ("todas as páginas", getattr(tela, "todas", None)),
        ("área de trabalho", tela),
    ]


def _barra_de_baixo(tela):
    """A barra fina de baixo (página N de M, desfazer, refazer, Histórico): o pai do "‹"."""
    botao = getattr(tela, "botao_anterior", None)
    return botao.parentWidget() if botao is not None else None


def chaves_dos_botoes(raiz, prefixo: str, lugares: list[tuple[str, object]] | None = None,
                      especiais: dict | None = None) -> dict[str, object]:
    """chave -> botão, para os botões à vista em `raiz`. `especiais`: botão -> rótulo fixo (os de
    texto que muda conforme o livro, como os motivos do "Para revisar"). Dois botões DIFERENTES
    com o mesmo rótulo no mesmo lugar (os dois "usar em todas" das ferramentas de marcar) ganham,
    os dois, o começo da dica depois de " — ", para cada um ter a sua promessa."""
    por_chave: dict[str, list] = {}
    for botao in botoes_a_vista(raiz):
        rotulo = (especiais or {}).get(botao) or rotulo_do_botao(botao.text(), botao.toolTip())
        lugar = lugar_de(botao, lugares) if lugares else ""
        chave = "/".join(p for p in (prefixo, lugar, rotulo) if p)
        por_chave.setdefault(chave, [])
        if botao not in por_chave[chave]:
            por_chave[chave].append(botao)
    saida: dict[str, object] = {}
    for chave, botoes in por_chave.items():
        if len(botoes) == 1 or any(b in (especiais or {}) for b in botoes):
            saida[chave] = botoes[0]          # os de rótulo fixo de propósito ficam juntos
            continue
        for botao in botoes:
            dica = " ".join(botao.toolTip().split()[:8])
            saida[f"{chave} — {dica}" if dica else chave] = botao
    return saida
