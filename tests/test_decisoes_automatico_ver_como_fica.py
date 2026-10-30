"""As provas de comportamento da D-577: na janela grande do Automático, ver como a página vai
ficar enquanto se escolhem as opções (CLAUDE.md §11, regra 4; Livro de decisões,
docs/plano/DECISOES.md).

  D-577 (29/10/2026). Samuel, sessão 2 dos testes, 2-11 (28/10): "eu queria poder nessa etapa
      do automatico poder ver como iria ficar conforme as opções que eu fosse escolhendo."
      Pergunta: "A página da direita passa a mostrar o antes e depois, com a linha que você
      arrasta. O lado do "depois" muda a cada opção que você marca ou desmarca. [...] Pode ser
      assim?" → "sim, mas coloca uma bolinha de carregamento como fez na area de trabalho,
      porque as vezes vai demorar para processar né?"
      No Livro: "Só mostra: não muda o projeto nem o histórico. Substitui a D-486."
  D-486 (27/10, escolha da gerente; substituída): a página da direita era a original.
  D-002, rodada 2 nº 5: "Na janela, ver a página ao lado, folhear e dar zoom." (continua).

O que se mede: a coluna da direita da janela grande (ui/automatico.PaginaAntesEDepois), as
imagens que ela mostra (o antes e o depois, em números), a bolinha, o projeto em memória e o
projeto.json/acoes.jsonl no disco, o Histórico, e o "depois" contra a página desenhada depois
do "Rodar" de verdade. Páginas sintéticas de propósito, as do tests/test_decisoes_automatico.py
(uma folha dupla, uma torta, uma reta, em papel amarelado).
"""

from __future__ import annotations

import copy
import dataclasses
import json
import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests.test_decisoes_automatico import AMARELADO, _livro  # noqa: E402

LIMITE_S = 180


# --- a janela ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    return tmp_path


@pytest.fixture
def janela(app, pasta):
    from ui.automatico import _guardiao
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 760)
    yield janela
    janela._fechar_a_janela_do_automatico()
    for tarefa in list(_guardiao().tarefas):       # nenhuma conta fica rodando depois do teste
        tarefa.wait(60000)
    _assentar(app)
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def _assentar(app, vezes: int = 5) -> None:
    for _ in range(vezes):
        app.processEvents()


def _esperar(app, painel) -> None:
    """Até a conta do antes e depois acabar (a bolinha parar)."""
    fim = time.monotonic() + LIMITE_S
    while time.monotonic() < fim:
        app.processEvents()
        if not painel.calculando():
            _assentar(app)
            if not painel.calculando():
                return
        time.sleep(0.02)
    raise AssertionError("a prévia do antes e depois não terminou")


def _abrir(janela, app, tmp_path, pagina: int = 0):
    """O livro aberto, a página da vez escolhida e a janela grande aberta, já com o antes e
    o depois calculados."""
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    janela.tela_conferir.ir_para_pagina(pagina)
    grande = janela.abrir_o_automatico()
    assert grande is not None
    _assentar(app)
    _esperar(app, grande.antes_e_depois)
    return grande


def _imagens(painel):
    """(antes, depois) que a coluna da direita mostra agora (numpy)."""
    antes = painel._antes[1] if painel._antes and painel._antes[0] == painel._indice else None
    depois = painel._depois[1] if painel._depois and painel._depois[0] == painel._indice else None
    return antes, depois


def _o_livro(janela) -> str:
    """O projeto aberto inteiro, em texto (tudo o que vai para o projeto.json)."""
    return json.dumps(dataclasses.asdict(janela.projeto), sort_keys=True, default=str)


def _no_disco(janela) -> tuple[bytes, bytes]:
    """O projeto.json e o acoes.jsonl como estão no disco agora (sem pedir para gravar)."""
    from tests.promessas.ajudantes import pasta_do_projeto

    pasta = pasta_do_projeto(janela)
    ler = (lambda nome: (pasta / nome).read_bytes() if (pasta / nome).exists() else b"")
    return ler("projeto.json"), ler("acoes.jsonl")


def _marcar(grande, etapas, filtro=None) -> None:
    """O que o Kaique faz na janela grande: marca as caixinhas das etapas na lista e, se
    pedido, clica o jeito de limpar."""
    from PySide6.QtCore import Qt

    for etapa in A.ETAPAS:
        item = grande.lista.item_da_etapa(etapa)
        querida = Qt.Checked if etapa in etapas else Qt.Unchecked
        if item.checkState() != querida:
            item.setCheckState(querida)
    if filtro is not None:
        grande.radios_de_filtro[filtro].click()


def _papel(img: np.ndarray) -> float:
    """O azul do papel num pedaço da margem de cima (a imagem da tela é BGR, do OpenCV; a de
    Preto e branco é cinza): 170 no amarelado, perto de 255 quando o filtro branqueia."""
    altura, largura = img.shape[:2]
    pedaco = img[int(altura * 0.06):int(altura * 0.11), int(largura * 0.4):int(largura * 0.6)]
    return float((pedaco[..., 0] if pedaco.ndim == 3 else pedaco).mean())


def _diferenca(a: np.ndarray, b: np.ndarray) -> float:
    """A fração dos pontos que mudam mais de 64 tons (0 = iguais)."""
    assert a.shape == b.shape, (a.shape, b.shape)
    return float((np.abs(a.astype(np.int16) - b.astype(np.int16)) > 64).mean())


# --- D-577: a coluna da direita é o antes e depois ------------------------------------

def test_d577_a_pagina_da_direita_mostra_o_antes_e_depois_com_a_linha(janela, app, tmp_path):
    """D-577: "A página da direita passa a mostrar o antes e depois, com a linha que você
    arrasta." → "sim". O antes e o depois estão na mesma vista, com a linha (a do "antes /
    depois" da área de trabalho, VistaAntesDepois), e a linha se arrasta. O antigo saiu: a
    página da direita não é mais o livro original da D-486 (FolhearPDF, "O livro, como está
    agora")."""
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QLabel

    from ui.automatico import PaginaAntesEDepois
    from ui.widgets.filtros_tela_cheia import VistaAntesDepois
    from ui.widgets.folhear_pdf import FolhearPDF

    grande = _abrir(janela, app, tmp_path, pagina=2)
    painel = grande.antes_e_depois
    assert isinstance(painel, PaginaAntesEDepois)
    assert isinstance(painel.visor, VistaAntesDepois)
    antes, depois = _imagens(painel)
    assert antes is not None and depois is not None
    assert painel.visor.comparando and painel.visor.antes is not None and painel.visor.depois is not None
    assert painel.visor.rotulos == ("antes", "depois")
    # o antigo (D-486) saiu
    assert not grande.findChildren(FolhearPDF)
    assert not [r for r in grande.findChildren(QLabel) if r.text() == "O livro, como está agora"]
    # a linha se arrasta (no meio de fábrica; arrastada para a direita, anda)
    grande.resize(1400, 800)
    grande.show()
    _assentar(app)
    vista = painel.visor
    area = vista._area(vista.depois)
    x = int(area.left() + area.width() * vista.posicao)
    y = int(area.center().y())
    QTest.mousePress(vista, Qt.LeftButton, Qt.NoModifier, QPoint(x, y))
    QTest.mouseMove(vista, QPoint(x + int(area.width() * 0.2), y))
    QTest.mouseRelease(vista, Qt.LeftButton, Qt.NoModifier, QPoint(x + int(area.width() * 0.2), y))
    assert vista.posicao > 0.6, f"a linha não andou ({vista.posicao})"


def test_d577_sem_etapa_marcada_o_depois_e_o_antes(janela, app, tmp_path):
    """D-577: o "depois" é "como ela vai sair com as etapas e opções marcadas". Livro novo,
    nada marcado: rodar não muda nada, e o depois é igual ao antes (ponto por ponto)."""
    grande = _abrir(janela, app, tmp_path, pagina=2)
    assert not janela.estado_do_automatico.marcadas
    antes, depois = _imagens(grande.antes_e_depois)
    assert antes.shape == depois.shape and np.array_equal(antes, depois)


def test_d577_marcar_uma_opcao_muda_o_depois_e_desmarcar_volta(janela, app, tmp_path):
    """D-577: "O lado do "depois" muda a cada opção que você marca ou desmarca." Marcar
    "Limpar a folha" em Preto e branco: o papel do depois fica branco (o antes continua
    amarelado). Trocar para Original: o depois volta a ser o antes. Desmarcar: igual."""
    grande = _abrir(janela, app, tmp_path, pagina=2)
    painel = grande.antes_e_depois
    _marcar(grande, {A.LIMPAR}, PRETO_E_BRANCO)
    _esperar(app, painel)
    antes, depois = _imagens(painel)
    assert abs(_papel(antes) - AMARELADO[0]) < 8, "o antes mudou"
    assert _papel(depois) > 240, f"o depois não ficou em Preto e branco (papel {_papel(depois):.0f})"
    _marcar(grande, {A.LIMPAR}, ORIGINAL)
    _esperar(app, painel)
    antes, depois = _imagens(painel)
    assert np.array_equal(antes, depois), "no Original o depois tinha de ser a página como está"
    _marcar(grande, {A.LIMPAR}, PRETO_E_BRANCO)
    _esperar(app, painel)
    assert _papel(_imagens(painel)[1]) > 240
    _marcar(grande, set())                         # desmarcar a etapa
    _esperar(app, painel)
    antes, depois = _imagens(painel)
    assert np.array_equal(antes, depois), "desmarcar não voltou o depois"


def test_d577_cortar_e_dividir_mudam_o_tamanho_do_depois(janela, app, tmp_path):
    """D-577, as outras etapas da página: "Dividir folhas ao meio" na folha dupla mostra as
    duas páginas que ela vira (cada uma com metade da largura); "Cortar as bordas" deixa o
    depois menor que o antes. Antes e depois de tamanhos diferentes ficam na mesma escala,
    sem esticar (a vista põe os dois no meio de uma tela do tamanho do maior)."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    antes, _ = _imagens(painel)
    _marcar(grande, {A.DIVIDIR})
    _esperar(app, painel)
    _, depois = _imagens(painel)
    from ui.automatico import VAO_ENTRE_AS_METADES

    assert depois.shape[0] == antes.shape[0]
    assert abs(depois.shape[1] - (antes.shape[1] + VAO_ENTRE_AS_METADES)) <= 4, (antes.shape, depois.shape)
    # o vão branco no meio separa as duas páginas
    meio = depois.shape[1] // 2
    assert depois[:, meio - 2:meio + 2].min() >= 250
    _marcar(grande, {A.CORTAR})
    _esperar(app, painel)
    _, depois = _imagens(painel)
    assert depois.shape[0] < antes.shape[0] and depois.shape[1] < antes.shape[1]
    vista = painel.visor
    assert vista.antes.size() == vista.depois.size(), "antes e depois de tamanhos diferentes na vista"


def test_d577_a_bolinha_gira_enquanto_calcula_e_some_no_fim(janela, app, tmp_path):
    """D-577: "coloca uma bolinha de carregamento como fez na area de trabalho, porque as
    vezes vai demorar para processar né?" A bolinha é a da barra de baixo
    (BolinhaDeCarregamento, D-064); gira logo depois da troca e para quando o depois chega."""
    from ui.widgets.bolinha import BolinhaDeCarregamento

    grande = _abrir(janela, app, tmp_path, pagina=1)
    painel = grande.antes_e_depois
    assert isinstance(painel.bolinha, BolinhaDeCarregamento)
    assert not painel.bolinha.carregando, "a bolinha ficou girando sem conta nenhuma"
    _marcar(grande, {A.ENDIREITAR, A.LIMPAR}, PRETO_E_BRANCO)
    assert painel.bolinha.carregando, "a bolinha não apareceu ao trocar a opção"
    vista = []
    fim = time.monotonic() + LIMITE_S
    while painel.calculando() and time.monotonic() < fim:
        vista.append(painel.bolinha.carregando)
        app.processEvents()
        time.sleep(0.01)
    _assentar(app)
    assert vista and all(vista), "a bolinha parou antes de o depois chegar"
    assert not painel.bolinha.carregando, "a bolinha não sumiu no fim"
    assert _papel(_imagens(painel)[1]) > 240


def test_d577_mexer_e_fechar_deixa_o_livro_o_desfazer_e_o_disco_iguais(janela, app, tmp_path):
    """D-577, no Livro: "Só mostra: não muda o projeto nem o histórico." Pedido: "fechar sem
    rodar → o livro e o desfazer ficam iguais". Muitas trocas (etapas, filtro, ordem,
    receita, onde rodar, folhear), e "Fechar": o projeto em memória, o Histórico (feitas e
    desfeitas) e o projeto.json/acoes.jsonl no disco são os mesmos de antes de abrir."""
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    # a medida do livro por trás (D-284) põe os avisos sozinha logo depois de abrir: espera
    # ela acabar ANTES de fotografar o livro (não é a prévia)
    fim = time.monotonic() + LIMITE_S
    while getattr(janela, "medida_ao_abrir", None) is not None and time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)
    _assentar(app)
    janela._salvar_agora()
    import projetos

    projetos.esperar_gravacoes()
    livro, disco = _o_livro(janela), _no_disco(janela)
    feitas, desfeitas = list(janela.acoes.feitas), list(janela.acoes.desfeitas)
    objeto = janela.projeto
    grande = janela.abrir_o_automatico()
    _assentar(app)
    painel = grande.antes_e_depois
    _esperar(app, painel)
    _marcar(grande, {A.DIVIDIR, A.ENDIREITAR, A.CORTAR, A.LIMPAR, A.GRAVURAS}, PRETO_E_BRANCO)
    _esperar(app, painel)
    janela.estado_do_automatico.mover(0, 3)
    _esperar(app, painel)
    janela.estado_do_automatico.definir_alcance("pagina")
    _esperar(app, painel)
    grande.botao_mais_opcoes.setChecked(True)
    grande.controles["gravura_mais_sensivel"].setChecked(True)
    _esperar(app, painel)
    painel.virar(1)
    _esperar(app, painel)
    painel.virar(1)
    _esperar(app, painel)
    grande.botao_fechar.click()
    _assentar(app)
    projetos.esperar_gravacoes()
    assert janela.projeto is objeto
    assert _o_livro(janela) == livro, "a prévia mudou o projeto aberto"
    assert list(janela.acoes.feitas) == feitas and list(janela.acoes.desfeitas) == desfeitas
    assert _no_disco(janela) == disco, "a prévia mexeu no projeto.json ou no acoes.jsonl"
    assert not janela.projeto.dividir_folhas and not janela.projeto.limpar
    assert [p.filtro for p in janela.projeto.paginas] == [ORIGINAL] * 3


def test_d577_resultado_velho_nunca_cobre_o_novo(janela, app, tmp_path):
    """Pedido da gerente (item 3): "Trocas rápidas seguidas: só o último pedido vale (não
    empilhar cálculos; resultado velho não pode aparecer por cima do novo)." Duas trocas
    seguidas, sem esperar: no fim, o depois mostrado é o da ÚLTIMA (Original: igual ao
    antes), nunca o da primeira (Preto e branco); só uma conta roda de cada vez. E um
    resultado velho que chega depois do novo é jogado fora."""
    from ui.automatico import _guardiao

    grande = _abrir(janela, app, tmp_path, pagina=2)
    painel = grande.antes_e_depois
    rodando_juntas = []
    original = painel._comecar

    def comecar(pedido_da_vez):
        rodando_juntas.append(sum(1 for t in _guardiao().tarefas if t.isRunning()))
        original(pedido_da_vez)

    painel._comecar = comecar
    _marcar(grande, {A.LIMPAR}, PRETO_E_BRANCO)
    painel.pedir(agora=True)                       # a primeira começa já
    velha = painel._querida
    _marcar(grande, {A.LIMPAR}, ORIGINAL)
    painel.pedir(agora=True)                       # a segunda, logo em seguida
    assert painel._querida != velha
    _esperar(app, painel)
    antes, depois = _imagens(painel)
    assert np.array_equal(antes, depois), "apareceu o depois da troca velha (Preto e branco)"
    assert painel._feito == painel._querida
    assert all(n == 0 for n in rodando_juntas), f"duas contas ao mesmo tempo: {rodando_juntas}"
    # um resultado velho que chega agora (a conta da primeira troca) não cobre o novo
    branca = np.full_like(depois, 255)
    painel._chegou(velha, painel._indice, None, [branca])
    assert np.array_equal(_imagens(painel)[1], depois), "o resultado velho cobriu o novo"


def test_d577_o_depois_bate_com_o_rodar_de_verdade(janela, app, tmp_path):
    """Pedido da gerente (item 2): "a prévia tem de usar o MESMO caminho do rodar de verdade
    (senão a prévia mente)". Na página torta: endireitar, cortar e limpar em Preto e branco.
    O depois da janela é comparado com a página desenhada depois do "Rodar" de verdade
    (ui/janela_principal.rodar_o_automatico, a mesma conta da prévia da área de trabalho,
    core/pipeline.renderizar_pagina, na mesma resolução). Medida: a fração dos pontos que
    mudam mais de 64 tons. No Preto e branco o próprio programa desenha a mesma página com
    diferença dessa ordem entre a primeira e a segunda vez (a primeira vem reduzida da
    resolução do PDF; medido 0,08% em 29/10): o limite é 0,5%. Na folha dupla, só dividir
    (sem filtro): ponto por ponto igual."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    from ui.automatico import DPI_DA_PREVIA, _lado_a_lado

    def desenhado(projeto, indice_antes, folha, metade):
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            imagens = []
            for pagina in A.paginas_depois(projeto, folha, metade):
                img, _ = renderizar_pagina(doc, projeto, pagina, dpi=DPI_DA_PREVIA)
                imagens.append(A.como_sai_na_tela(img, projeto, pagina, DPI_DA_PREVIA))
            return _lado_a_lado(imagens)
        finally:
            doc.close()

    medidas = {}
    for pagina, etapas, filtro in ((1, {A.ENDIREITAR, A.CORTAR, A.LIMPAR}, PRETO_E_BRANCO),
                                   (0, {A.DIVIDIR}, None)):
        (tmp_path / f"p{pagina}").mkdir()
        grande = _abrir(janela, app, tmp_path / f"p{pagina}", pagina=pagina)
        painel = grande.antes_e_depois
        _marcar(grande, etapas, filtro)
        _esperar(app, painel)
        previa = _imagens(painel)[1]
        alvo_folha = janela.projeto.paginas[pagina].folha
        alvo_metade = janela.projeto.paginas[pagina].metade
        janela._fechar_a_janela_do_automatico()
        assert janela.rodar_o_automatico(esperar=True, perguntar=False)
        de_verdade = desenhado(janela.projeto, pagina, alvo_folha, alvo_metade)
        medidas[pagina] = _diferenca(previa, de_verdade)
        if filtro is None:
            assert np.array_equal(previa, de_verdade), "dividir: a prévia não é a página de verdade"
    print(f"\nD-577: diferença prévia x rodar de verdade: torta P&B {medidas[1]:.4%}, "
          f"folha dupla dividida {medidas[0]:.4%}")
    assert medidas[1] < 0.005, f"a prévia mente: {medidas[1]:.4%} dos pontos diferentes"


def test_d577_folhear_e_zoom_continuam(janela, app, tmp_path):
    """D-002, rodada 2 nº 5: "Na janela, ver a página ao lado, folhear e dar zoom." (o pedido:
    "Continua dando para folhear as páginas do livro e dar zoom"). ">" vai para a página
    seguinte e calcula o antes e depois DELA (uma página por vez na memória); "+" aproxima,
    "–" afasta, "ajustar à tela" volta a caber."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    antes0, _ = _imagens(painel)
    painel.botao_proxima.click()
    assert painel._indice == 1
    assert painel._antes is None or painel._antes[0] == 1   # o da página anterior saiu
    _esperar(app, painel)
    antes1, depois1 = _imagens(painel)
    assert antes1 is not None and depois1 is not None and antes1.shape != antes0.shape
    assert "página 2 de 3" in painel.contador.text()
    painel.botao_anterior.click()
    _esperar(app, painel)
    assert painel._indice == 0
    zoom = painel.visor.zoom
    grande._zoom(1.25)
    assert painel.visor.zoom > zoom and not painel.rolagem.widgetResizable()
    grande._zoom(0.8)
    grande._zoom(0.8)
    assert painel.visor.zoom < zoom * 1.25
    grande._zoom(None)
    assert painel.visor.zoom == 1.0 and painel.rolagem.widgetResizable()


def test_d577_core_a_previa_nao_toca_no_projeto(tmp_path):
    """core/automatico.depois_da_pagina trabalha na CÓPIA (copia_para_a_previa): o projeto
    de onde ela saiu fica igual, e a folha fora do "Rodar em" não é medida nem mexida (só a
    página escolhida muda; a folha dupla, fora do pedido, continua inteira)."""
    from core.pdf_io import abrir_pdf, info_paginas
    from modelos import Projeto

    caminho = _livro(tmp_path)
    doc = abrir_pdf(caminho)
    try:
        projeto = Projeto(caminho_entrada=caminho)
        A.livro_leve(projeto, [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)])
        antes = json.dumps(dataclasses.asdict(projeto), sort_keys=True, default=str)
        pedido = A.Pedido(etapas=[A.DIVIDIR], opcoes=A.opcoes_do_livro(projeto), paginas=[2])
        imagens = A.depois_da_pagina(doc, A.copia_para_a_previa(projeto), copy.deepcopy(pedido), 0, 110)
        assert len(imagens) == 1, "a folha fora do pedido foi dividida na prévia"
        assert json.dumps(dataclasses.asdict(projeto), sort_keys=True, default=str) == antes
    finally:
        doc.close()
