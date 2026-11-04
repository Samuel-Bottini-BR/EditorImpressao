"""Teste de reversão da D-603 (CLAUDE.md §4.7): as folhas do caderno da etapa 7 seguem o
"Dividir" marcado na janela do Automático, antes do "Rodar".

Bug (print do Samuel `relatorios/testes-guiados/2026-10-29-automatico/
a-49-dividir-marcado-caderno-sem-divisao.png`, 03/11/2026: etapa 1 "Dividir" marcada, etapa 7
aberta, o caderno com os scans inteiros): "eu fui lá e apertei o botão de dividir e nos cadernos
ainda aparece a folha sem divisão, era para ser com divisão, já que eu cliquei lá em cima, mesmo
que eu não tenha processado ainda, pois é o preview." -> D-603: "pode ser assim nos cadernos".

Causa: ui/widgets/folhas_do_caderno contava e distribuía as páginas do livro COMO ESTÁ
(Projeto.paginas_ativas): com o Dividir marcado num livro sem dividir, uma página por folha do
scan, e cada lugar do caderno recebia as duas metades coladas (a folha aberta).

No código antigo (`016ec37a`) este teste falha: "Folha 1 de 2" (6 folhas do scan) no lugar de
"Folha 1 de 3" (12 páginas), e cada metade da folha do caderno traz duas páginas.

Livro sintético: 6 folhas deitadas, cada uma com duas páginas lado a lado; a página k (0 a 11)
tem uma faixa preta numa altura só dela, para ler qual página caiu em cada metade.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from tests.test_decisoes_automatico import _pdf  # noqa: E402

LIMITE_S = 180
FOLHAS = 6
ALTURA, LARGURA = 840, 600        # uma página; a folha do scan tem duas lado a lado


def _pagina(k: int) -> np.ndarray:
    img = np.full((ALTURA, LARGURA, 3), 245, np.uint8)
    y = 30 + k * 60
    img[y:y + 40, 100:LARGURA - 100] = 20
    return img


def livro_de_folhas_abertas(tmp_path: Path) -> str:
    """6 folhas do scan, cada uma com as páginas 2i e 2i+1 lado a lado (deitadas)."""
    caminho = tmp_path / "abertas.pdf"
    if not caminho.exists():
        _pdf(caminho, [np.concatenate([_pagina(2 * i), _pagina(2 * i + 1)], axis=1)
                       for i in range(FOLHAS)])
    return str(caminho)


def paginas_na_metade(metade: np.ndarray) -> list[int]:
    """As páginas (1, 2, ...) cujas faixas estão nesta metade da folha do caderno."""
    cinza = metade if metade.ndim == 2 else metade.mean(axis=2)
    escuras = (cinza < 100).mean(axis=1) > 0.15
    achadas, y = [], 0
    while y < len(escuras):
        if escuras[y]:
            inicio = y
            while y < len(escuras) and escuras[y]:
                y += 1
            meio = (inicio + y) / 2 / cinza.shape[0] * ALTURA
            achadas.append(int(round((meio - 50) / 60)) + 1)
        y += 1
    return achadas


def paginas_do_lado(face: np.ndarray) -> tuple:
    meio = face.shape[1] // 2
    return paginas_na_metade(face[:, :meio]), paginas_na_metade(face[:, meio:])


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def janela(app, tmp_path, monkeypatch):
    import projetos
    from ui.automatico import _guardiao
    from ui.janela_principal import JanelaPrincipal

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    for tarefa in list(_guardiao().tarefas):
        tarefa.wait(60000)
    assentar(app)
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def assentar(app, vezes: int = 5) -> None:
    for _ in range(vezes):
        app.processEvents()


def esperar(app, painel) -> None:
    fim = time.monotonic() + LIMITE_S
    while time.monotonic() < fim:
        app.processEvents()
        if not painel.calculando():
            assentar(app)
            if not painel.calculando():
                return
        time.sleep(0.02)
    raise AssertionError("a folha do caderno não terminou")


def test_d603_dividir_marcado_o_caderno_mostra_as_paginas_divididas(janela, app, tmp_path):
    """D-603 (print a-49): livro sem dividir, "Dividir" e "Montar cadernos" marcados, etapa 7
    aberta, sem Rodar: 12 páginas em cadernos de 8 -> 3 folhas; folha 1: frente páginas 8 e 1,
    verso 2 e 7, UMA página em cada metade (antes: as duas metades da folha do scan coladas)."""
    janela.abrir_livro(livro_de_folhas_abertas(tmp_path))
    assentar(app)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR, A.CADERNOS}
    estado.opcoes["paginas_por_caderno"] = 8
    grande = janela.abrir_o_automatico(A.CADERNOS)
    assentar(app)
    folhas = grande.folhas_do_caderno
    esperar(app, folhas)
    assert folhas.rotulos["frente"].text() == "Folha 1 de 3 — frente"
    frente, verso = folhas.faces()
    assert paginas_do_lado(frente) == ([8], [1])
    assert paginas_do_lado(verso) == ([2], [7])
    # o livro não mudou (só mostra, D-577): continua com uma página por folha do scan
    assert len(janela.projeto.paginas_ativas) == FOLHAS


# --- a lista de páginas depois do Dividir, sem desenhar, é a do "Rodar" ------------------
#
# core/automatico.paginas_do_pdf_depois faz, sem copiar o projeto, o que o `_dividir` do "Rodar"
# faz com a lista de páginas (o `_dividir` numa cópia levava 0,35 s num livro de 700 folhas).
# Estas provas comparam as duas contas em livros com tudo o que muda a lista: folhas inteiras,
# já divididas, juntadas ("não dividir esta"), tiradas do livro, mexidas à mão (D-004), em pé,
# deitadas, quase quadradas (o ScanTailor divide, o jeito do programa não), giradas, "Rodar em"
# só algumas páginas, e os dois jeitos de dividir.

# (largura, altura) em pontos de cada folha do PDF de tamanhos
TAMANHOS = [(900, 600), (420, 600), (660, 600), (900, 600), (600, 900), (900, 600),
            (900, 600), (900, 600), (620, 600), (420, 600)]


def _pdf_de_tamanhos(tmp_path: Path) -> str:
    caminho = tmp_path / "tamanhos.pdf"
    if not caminho.exists():
        doc = fitz.open()
        for largura, altura in TAMANHOS:
            doc.new_page(width=largura, height=altura)
        doc.save(str(caminho))
        doc.close()
    return str(caminho)


def _livro_variado(caminho: str, jeito: str):
    """Folhas: 0 inteira deitada; 1 inteira em pé; 2 quase quadrada; 3 já dividida; 4 em pé
    girada 90 (fica deitada); 5 juntada ("não dividir esta": duas páginas, a direita fora);
    6 inteira tirada do livro; 7 dividida à mão (D-004); 8 quase quadrada dividida; 9 em pé
    com duas páginas (juntada, a direita fora)."""
    from core import etapas as E
    from modelos import (METADE_DIREITA, METADE_ESQUERDA, METADE_INTEIRA, ConfigFolha,
                         ConfigPagina, Projeto)

    projeto = Projeto(caminho_entrada=caminho)
    projeto.dividir_como = jeito
    paginas = []

    def inteira(f, **kw):
        paginas.append(ConfigPagina(indice=0, folha=f, metade=METADE_INTEIRA, **kw))

    def duas(f, direita_fora=False):
        paginas.append(ConfigPagina(indice=0, folha=f, metade=METADE_ESQUERDA))
        paginas.append(ConfigPagina(indice=0, folha=f, metade=METADE_DIREITA, apagada=direita_fora))

    for f in range(len(TAMANHOS)):
        folha = ConfigFolha(indice=f, dividir=False)
        if f in (0, 1, 2):
            inteira(f)
        elif f == 3:
            folha.dividir = True
            duas(f)
        elif f == 4:
            folha.rotacao = 90
            inteira(f)
        elif f in (5, 9):
            duas(f, direita_fora=True)
        elif f == 6:
            inteira(f, apagada=True)
        elif f == 7:
            folha.dividir, folha.posicao_corte, folha.mexida_a_mao = True, 0.47, [E.DIVIDIR]
            duas(f)
        elif f == 8:
            folha.dividir = True
            duas(f)
        projeto.folhas.append(folha)
    for n, pagina in enumerate(paginas):
        pagina.indice = n
    projeto.paginas = paginas
    return projeto


def _pelo_rodar(projeto, pedido) -> list[tuple]:
    """A lista de (folha, metade) do PDF pelo `aplicar` de verdade (o "Rodar"), numa cópia, com
    as medidas que a regra do tamanho dá (o que a medida acharia)."""
    import copy

    copia = copy.deepcopy(projeto)
    retangulos = A._retangulos_do_pdf(projeto.caminho_entrada)
    jeito = (pedido.opcoes or {}).get("dividir_como", projeto.dividir_como)
    medidas = {}
    for i in A.folhas_do_pedido(copia, pedido):
        f = copia.folhas[i]
        d = A.vai_dividir_pelo_tamanho(retangulos[i], f.rotacao, jeito)
        medidas[i] = A.MedidaDaFolha(i, d, 0.5, 1.0, d, None, 0.0, 0.0, [], [])
    A.aplicar(copia, pedido, medidas)
    return [(p.folha, p.metade) for p in copia.paginas_ativas]


@pytest.mark.parametrize("jeito", ["scantailor", "programa"])
@pytest.mark.parametrize("paginas", [None, "algumas"])
@pytest.mark.parametrize("pular", [True, False])
def test_d603_lista_sem_desenhar_e_a_mesma_do_rodar(tmp_path, jeito, paginas, pular):
    projeto = _livro_variado(_pdf_de_tamanhos(tmp_path), jeito)
    escolhidas = None if paginas is None else [p.indice for p in projeto.paginas
                                               if p.folha in (0, 2, 4, 5, 7)]
    pedido = A.Pedido(etapas=[A.DIVIDIR, A.CADERNOS], paginas=escolhidas, pular_mexidas=pular)
    lista = A.paginas_do_pdf_depois(projeto, pedido)
    assert [(f, m) for _o, f, m in lista] == _pelo_rodar(projeto, pedido)
    # cada página sai de uma página da mesma folha: a mesma metade, ou a inteira que é partida
    for origem, folha, metade in lista:
        de_onde = projeto.paginas[origem]
        assert de_onde.folha == folha and de_onde.metade in (metade, "inteira")
    # e o projeto não mudou
    assert [(p.folha, p.metade, p.apagada) for p in projeto.paginas] == \
        [(p.folha, p.metade, p.apagada) for p in _livro_variado(projeto.caminho_entrada, jeito).paginas]


def test_d603_sem_o_dividir_a_lista_e_o_livro_como_esta(tmp_path):
    """D-589/D-590: Dividir desmarcado (ou "Desligar as marcadas") → a lista é a do livro como
    está (Projeto.paginas_ativas): nada é partido nem juntado."""
    projeto = _livro_variado(_pdf_de_tamanhos(tmp_path), "scantailor")
    como_esta = [(p.indice, p.folha, p.metade) for p in projeto.paginas_ativas]
    for pedido in (A.Pedido(etapas=[A.CADERNOS], desmarcadas=[A.DIVIDIR]),
                   A.Pedido(etapas=[A.DIVIDIR, A.CADERNOS], desligar=True)):
        assert A.paginas_do_pdf_depois(projeto, pedido) == como_esta


def test_d603_a_regra_do_tamanho_e_a_da_medida(tmp_path):
    """A conta pelo tamanho (sem desenhar) diz o mesmo que a medida do "Rodar" (core/automatico.
    medir, que desenha a folha e pergunta ao ScanTailor ou à conta do programa), nos dois
    jeitos, em folhas deitadas, em pé, quase quadradas e giradas; e no Gradus Primus (as 12
    primeiras folhas), quando a cópia está em _tmp/livros."""
    caminho = tmp_path / "com_imagem.pdf"
    imagens = []
    for largura, altura in TAMANHOS:
        img = np.full((altura, largura, 3), 245, np.uint8)
        for y in range(60, altura - 60, 40):          # linhas de "texto" nas duas metades
            img[y:y + 12, 40:largura // 2 - 30] = 30
            img[y:y + 12, largura // 2 + 30:largura - 40] = 30
        imagens.append(img)
    _pdf(caminho, imagens)
    livros = [(str(caminho), list(range(len(TAMANHOS))))]
    gradus = Path(__file__).resolve().parents[1] / "_tmp" / "livros" / "gradus.pdf"
    if gradus.is_file():
        livros.append((str(gradus), list(range(12))))
    for livro, folhas in livros:
        retangulos = A._retangulos_do_pdf(livro)
        for jeito in ("scantailor", "programa"):
            for rotacao in (0, 90):
                foto = A.Fotografia(
                    caminho=livro, etapas=[A.DIVIDIR], dividir_como=jeito, cortar_sobra=False,
                    vai_endireitar=False, vai_cortar=False, vai_dividir=True, livro=None,
                    folhas=[A._FolhaParaMedir(i, rotacao, False, 0.5, True, {}, {}) for i in folhas])
                medidas = A.medir(foto)
                for i in folhas:
                    pelo_tamanho = A.vai_dividir_pelo_tamanho(retangulos[i], rotacao, jeito)
                    assert medidas[i].dividir == pelo_tamanho, (Path(livro).name, i, jeito, rotacao)
