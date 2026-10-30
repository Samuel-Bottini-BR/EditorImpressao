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
    nada marcado: rodar não muda nada, e o depois é igual ao antes (ponto por ponto; a página
    do livro novo está em Original, então o antes sem filtro é ela mesma)."""
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
    # (o livro sintético está todo em Original: o antes, sem filtro, é a página como está)
    assert np.array_equal(antes, depois), "no Original o depois tinha de ser o antes"
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


def test_d577_fechar_o_programa_com_a_conta_rodando_para_e_espera_a_conta(janela, app, tmp_path,
                                                                          monkeypatch):
    """Defeito D1 do verificador da D-577 (30/10/2026): fechar o PROGRAMA com a janela grande
    aberta e a conta da prévia rodando deixava a conta viva (presa no _Guardiao; o done() da
    janela grande nem era chamado) e o processo saía quebrado (código 127). CLAUDE.md §3:
    "Interface nunca congela" e nenhum erro na saída; como as outras tarefas, a do antes e
    depois tem de receber o pedido de parar e ser esperada no closeEvent. Teste de reversão
    (§4.7): no código de antes, logo depois de fechar, a conta ainda está rodando."""
    import threading

    from ui.automatico import _guardiao

    grande = _abrir(janela, app, tmp_path, pagina=2)
    painel = grande.antes_e_depois
    comecou = threading.Event()
    original = A.depois_da_pagina

    def devagar(*args, **kwargs):          # uma conta comprida, como a de um livro de verdade
        comecou.set()
        time.sleep(2.0)
        return original(*args, **kwargs)

    monkeypatch.setattr(A, "depois_da_pagina", devagar)
    _marcar(grande, {A.LIMPAR}, PRETO_E_BRANCO)
    painel.pedir(agora=True)
    assert comecou.wait(30), "a conta da prévia não começou"
    tarefas = [t for t in _guardiao().tarefas if t.isRunning()]
    assert tarefas
    janela.close()
    assert not [t for t in tarefas if t.isRunning()], "fechar o programa deixou a conta da prévia rodando"
    assert all(t.foi_cancelada for t in tarefas), "a conta não recebeu o pedido de parar"
    assert janela.janela_do_automatico is None


# --- D-577, o que o Samuel mandou depois do teste de 30/10 ------------------------------
#
# Samuel (30/10/2026), depois do teste (prints a-07 e a-08 em
# relatorios/testes-guiados/2026-10-29-automatico/): "ele não está funcionando, e não funciona em
# tela cheia também, como pode ver pelo print ele não muda no antes e depois conforme eu troco os
# filtros" · "na previa ali, ele mostra a mudança em todas as paginas mas só muda as que nós
# autorizarmos ( no caso as que foram mexidas a mão), segundo tem que dar para ver na previa em
# tela grande e poder dar zoom na previa em tela grande" · "quarta coisa, quando você mexe no
# antes e depois, ele começa a mostrar o antes de qual pagina, parece que ele troca o antes
# conforme se troca os perfis dos filtros."


def _mexida_no_filtro(janela, indice: int) -> None:
    """A página `indice` marcada como mexida à mão no filtro, como a capa e a página 17 do livro
    de teste do Samuel (`mexida_a_mao: ['filtro']`, dos testes de 29/10)."""
    from core import etapas

    etapas.marcar_mexida_a_mao(janela.projeto.paginas[indice], etapas.FILTRO)
    assert A.paginas_mexidas(janela.projeto, A.Pedido(etapas=[A.LIMPAR])) == [indice]


def test_d577_a_previa_mostra_a_mudanca_tambem_na_pagina_mexida_a_mao(janela, app, tmp_path,
                                                                        monkeypatch):
    """D-577, 30/10: "na previa ali, ele mostra a mudança em todas as paginas mas só muda as que
    nós autorizarmos ( no caso as que foram mexidas a mão)". Defeito do teste de 30/10 (print
    a-07): a prévia pulava a página mexida à mão (o pedido saía com pular_mexidas=True), e o
    "depois" da capa nunca mudava com o filtro. Agora a prévia mostra a mudança nela também; o
    "Rodar" de verdade continua perguntando (D-004) e o pedido dele continua pulando de fábrica.
    Teste de reversão (§4.7): no código de antes, o depois da página mexida fica igual ao antes
    (o papel continua amarelado)."""
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    _mexida_no_filtro(janela, 2)
    janela.tela_conferir.ir_para_pagina(2)
    grande = janela.abrir_o_automatico()
    painel = grande.antes_e_depois
    _esperar(app, painel)
    _marcar(grande, {A.LIMPAR}, PRETO_E_BRANCO)
    _esperar(app, painel)
    antes, depois = _imagens(painel)
    assert abs(_papel(antes) - AMARELADO[0]) < 8, "o antes mudou"
    assert _papel(depois) > 240, (f"a prévia pulou a página mexida à mão (papel do depois "
                                  f"{_papel(depois):.0f}, igual ao antes)")
    # o "Rodar" de verdade não muda: o pedido dele pula de fábrica e a pergunta da D-004 continua
    assert janela.estado_do_automatico.pedido().pular_mexidas is True
    perguntas = []
    monkeypatch.setattr(janela, "_perguntar_mexidas", lambda n: perguntas.append(n))   # = cancelar
    janela._fechar_a_janela_do_automatico()
    assert janela.rodar_o_automatico(esperar=True) is False
    assert perguntas == [1], "o Rodar deixou de perguntar das páginas mexidas à mão (D-004)"
    assert janela.projeto.paginas[2].filtro == ORIGINAL, "cancelar a pergunta mudou a página"


def test_d577_tela_cheia_mostra_o_antes_e_depois_da_previa_com_zoom_e_folhear(janela, app, tmp_path,
                                                                             monkeypatch):
    """D-577, 30/10: "tem que dar para ver na previa em tela grande e poder dar zoom na previa em
    tela grande". O "tela cheia" da página da direita abre o MESMO antes e depois (as mesmas
    imagens, com a linha que se arrasta), grande, com o zoom (–, + e "ajustar à tela") e o
    folhear (< > e as setas do teclado), como a tela cheia de antes já folheava. O antigo saiu:
    não abre mais a folha crua do PDF (TelaCheiaDoPDF, print a-08). Teste de reversão (§4.7): no
    código de antes, o "tela cheia" abre a TelaCheiaDoPDF."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from ui.widgets import folhear_pdf
    from ui.widgets.filtros_tela_cheia import VistaAntesDepois

    cruas = []

    class _FolhaCrua:                        # a tela cheia de antes, sem travar o teste no exec()
        def __init__(self, _doc, folha, _pai=None):
            cruas.append(folha)
            self.indice = folha

        def exec(self):
            return 0

    monkeypatch.setattr(folhear_pdf, "TelaCheiaDoPDF", _FolhaCrua)
    grande = _abrir(janela, app, tmp_path, pagina=1)
    painel = grande.antes_e_depois
    _marcar(grande, {A.LIMPAR}, PRETO_E_BRANCO)
    _esperar(app, painel)
    painel.botao_tela_cheia.click()
    _assentar(app)
    assert not cruas, "o tela cheia abriu a folha crua do PDF (TelaCheiaDoPDF), não a prévia"
    tela = painel.tela_cheia
    assert tela is not None and tela.isVisible()
    vista = tela.visor
    assert isinstance(vista, VistaAntesDepois)
    antes, depois = _imagens(painel)
    assert vista._crus[0] is antes and vista._crus[1] is depois, "não é o antes e depois da prévia"
    assert vista.comparando and vista.rotulos == ("antes", "depois")
    assert "página 2 de 3" in tela.contador.text()
    # o zoom
    tela.botao_mais.click()
    assert vista.zoom > 1.0 and not tela.rolagem.widgetResizable()
    tela.botao_menos.click()
    tela.botao_menos.click()
    assert vista.zoom < 1.0
    tela.botao_caber.click()
    assert vista.zoom == 1.0 and tela.rolagem.widgetResizable()
    # o folhear: a página seguinte, com o antes e depois DELA (calculado como na janela)
    tela.botao_proxima.click()
    assert painel._indice == 2
    _esperar(app, painel)
    antes2, depois2 = _imagens(painel)
    assert vista._crus[0] is antes2 and vista._crus[1] is depois2
    assert _papel(depois2) > 240
    assert "página 3 de 3" in tela.contador.text()
    QTest.keyClick(tela, Qt.Key_Left)
    assert painel._indice == 1
    _esperar(app, painel)
    QTest.keyClick(tela, Qt.Key_Escape)
    _assentar(app)
    assert not tela.isVisible() and painel.tela_cheia is None
    assert not cruas


def test_d577_o_antes_nao_muda_ao_trocar_o_filtro_nem_na_pagina_mexida(janela, app, tmp_path):
    """D-577, 30/10: "quarta coisa, quando você mexe no antes e depois, ele começa a mostrar o
    antes de qual pagina, parece que ele troca o antes conforme se troca os perfis dos filtros."
    Pela D-577, o "antes" não muda com as opções (desde o 2º teste de 30/10 ele é a página sem
    filtro, em Original, cortada e endireitada como está no livro; antes era a página como está
    no livro, com o filtro dela; as duas coisas são iguais aqui, página em Original). Na
    página mexida à mão (como a capa do teste) e trocando os quatro jeitos de limpar e o "Só as
    letras", o antes é sempre o mesmo, ponto por ponto (o guardado e o que a vista mostra), e o
    depois muda. Esta prova NÃO é de reversão: a troca do antes não se reproduziu
    (relatorios/automatico-ver-como-fica/ONDE-PAREI.md); ela guarda que o antes não muda."""
    from core.filtros import MAGICO_PRO, MELHORAR

    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    _mexida_no_filtro(janela, 2)
    janela.tela_conferir.ir_para_pagina(2)
    grande = janela.abrir_o_automatico()
    painel = grande.antes_e_depois
    _esperar(app, painel)
    antes0 = _imagens(painel)[0].copy()
    vistos = set()
    trocas = [lambda f=f: grande.radios_de_filtro[f].click()
              for f in (PRETO_E_BRANCO, MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO)]
    estado = janela.estado_do_automatico          # o que a caixinha "Só as letras" faz (_mudou)
    trocas += [lambda: estado.definir_opcao("misto_so_as_letras", True),
               lambda: estado.definir_opcao("misto_so_as_letras", False)]
    _marcar(grande, {A.LIMPAR})
    for trocar in trocas:
        trocar()
        _esperar(app, painel)
        antes, depois = _imagens(painel)
        assert np.array_equal(antes, antes0), "o antes mudou com a opção"
        assert painel.visor._crus[0] is painel._antes[1], "a vista mostra outro antes"
        vistos.add(depois.tobytes())
    assert len(vistos) >= 3, "o depois não mudou com as opções"


# --- D-577, depois do 2º teste do Samuel (30/10, 13:33) -----------------------------------
#
# Samuel: "está bem confuso, na verdade, porque eu já tinha colocado um filtro antes, eu acho que
# o antes deveria ser sempre o original e o filtro depois o que escolhemos, ai se quiser comparar
# faz isso na tela cheia." · "na tela cheia vai ter um botão de comparação , ai vão aparecer duas
# telas para comparar" · "nessa vai ter o filtro que estava antes, seja ele original ou que foi
# aplicado e o filtro que está selecionado no momento" · e, no lugar de "mostra já cortada e
# endireitada se tiver sido feito isso.": "o antes é sem filtro e sem cortar sem nada, o depois
# na tela de atualizar que aplica os filtros de endireitar cortar ou fazer qualquer outra coisa
# para ver como iria ficar." (prints a-12, a-13 e a-14 em
# relatorios/testes-guiados/2026-10-29-automatico/)


def _papel_mediano(img: np.ndarray) -> float:
    """O azul do papel pela mediana da página inteira (o papel é a maior parte dela; não depende
    de onde caiu o corte): 170 no amarelado, 255 no Preto e branco."""
    return float(np.median(img[..., 0] if img.ndim == 3 else img))


def _torta_ja_rodada(janela, app, tmp_path):
    """O livro com a página torta (índice 1) já endireitada, cortada e em Preto e branco NO
    LIVRO (o "Rodar" de verdade), e a janela grande aberta nela, com o antes e depois prontos."""
    from core import etapas

    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    janela.tela_conferir.ir_para_pagina(1)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.ENDIREITAR, A.CORTAR, A.LIMPAR}
    estado.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    _assentar(app)
    assert etapas.filtro_que_vale(janela.projeto, janela.projeto.paginas[1]) == PRETO_E_BRANCO
    janela.tela_conferir.ir_para_pagina(1)
    grande = janela.abrir_o_automatico()
    _esperar(app, grande.antes_e_depois)
    return grande


def test_d577_o_antes_e_a_folha_crua_sem_nada(janela, app, tmp_path):
    """D-577, depois do 2º teste (30/10): "o antes é sem filtro e sem cortar sem nada, o depois
    na tela de atualizar que aplica os filtros de endireitar cortar ou fazer qualquer outra
    coisa para ver como iria ficar." Na página que já está endireitada, cortada e em Preto e
    branco no livro, o "antes" é a folha como veio do PDF, ponto por ponto (sem filtro: o papel
    amarelado; sem corte: do tamanho da folha, maior que o depois cortado). O depois continua
    sendo o que o Rodar faria. O antigo saiu: o antes não é mais a página com o filtro e o corte
    do livro. Teste de reversão (§4.7): no código de antes, o antes sai em Preto e branco e
    cortado."""
    from core.pdf_io import abrir_pdf, pagina_para_array
    from ui.automatico import DPI_DA_PREVIA

    grande = _torta_ja_rodada(janela, app, tmp_path)
    painel = grande.antes_e_depois
    antes, depois = _imagens(painel)
    projeto = janela.projeto
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        crua = pagina_para_array(doc, projeto.paginas[1].folha, dpi=DPI_DA_PREVIA)
    finally:
        doc.close()
    assert antes.shape == crua.shape, f"o antes não é a folha crua (tamanho {antes.shape}, crua {crua.shape})"
    assert np.array_equal(antes, crua), "o antes não é a folha como veio do PDF"
    assert abs(_papel_mediano(antes) - AMARELADO[0]) < 8
    # o depois: endireitado, cortado e em Preto e branco (o que o Rodar faria), menor que o antes
    assert depois.shape[0] < antes.shape[0] and depois.shape[1] < antes.shape[1]
    assert _papel_mediano(depois) > 240


def test_d577_comparar_na_tela_cheia_mostra_o_livro_e_o_depois_lado_a_lado(janela, app, tmp_path):
    """D-577, depois do 2º teste (30/10): "na tela cheia vai ter um botão de comparação , ai vão
    aparecer duas telas para comparar" · "nessa vai ter o filtro que estava antes, seja ele
    original ou que foi aplicado e o filtro que está selecionado no momento". O botão
    "comparar" da tela cheia (o nome do "Ver de perto") mostra duas telas: à esquerda a página
    como está no livro (Preto e branco, como foi aplicado; igual ao desenho dela no livro), à
    direita o depois (Original, escolhido agora na janela), cada uma com o rótulo dela; o zoom
    e a posição andam juntos nas duas (como no "Ver de perto"); folhear continua; apertar de
    novo volta ao antes e depois com a linha. Teste de reversão (§4.7): no código de antes, a
    tela cheia não tem o botão "comparar"."""
    from PySide6.QtCore import QPoint
    from PySide6.QtWidgets import QPushButton

    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    from ui.automatico import DPI_DA_PREVIA

    grande = _torta_ja_rodada(janela, app, tmp_path)
    painel = grande.antes_e_depois
    grande.radios_de_filtro[ORIGINAL].click()       # o escolhido agora: Original
    _esperar(app, painel)
    painel.botao_tela_cheia.click()
    _assentar(app)
    tela = painel.tela_cheia
    botoes = [b for b in tela.findChildren(QPushButton) if b.text() == "comparar"]
    assert botoes, "a tela cheia não tem o botão \"comparar\""
    assert tela.rolagem.isVisible() and not tela.duas.isVisible()
    botoes[0].click()
    _esperar(app, painel)
    _assentar(app)
    assert tela.comparando and tela.duas.isVisible() and not tela.rolagem.isVisible()
    do_livro = painel._do_livro[1]
    depois = _imagens(painel)[1]
    # a da esquerda: a página como está no livro, desenhada como no livro
    projeto = janela.projeto
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        copia = A.copia_para_a_previa(projeto)
        ref, _ = renderizar_pagina(doc, copia, copia.paginas[1], dpi=DPI_DA_PREVIA)
    finally:
        doc.close()
    ref = A.como_sai_na_tela(ref, copia, copia.paginas[1], DPI_DA_PREVIA)
    assert do_livro.shape == ref.shape and _diferenca(do_livro, ref) < 0.005, \
        "a tela da esquerda não é a página como está no livro"
    assert _papel_mediano(do_livro) > 240, "a tela da esquerda não está em Preto e branco"
    assert abs(_papel_mediano(depois) - AMARELADO[0]) < 8, "a tela da direita não é o depois (Original)"
    for vista, img in ((tela.vista_a, do_livro), (tela.vista_b, depois)):
        assert vista._pixmap is not None and (vista._pixmap.height(), vista._pixmap.width()) == img.shape[:2]
    assert tela.rotulo_a.text() == "como está no livro: Preto e branco"
    assert tela.rotulo_b.text() == "depois: Original"
    # o zoom e a posição andam juntos
    tela.botao_mais.click()
    tela.botao_mais.click()
    assert tela.vista_a.zoom > 1.0 and tela.vista_b.zoom == tela.vista_a.zoom
    tela.vista_b.deslocamento = QPoint(30, -20)
    tela.vista_b.vista_mudou.emit(tela.vista_b.zoom, tela.vista_b.deslocamento)
    assert tela.vista_a.deslocamento == QPoint(30, -20)
    tela.botao_caber.click()
    assert tela.vista_a.zoom == 1.0 and tela.vista_b.zoom == 1.0
    # folhear com o comparar ligado: a página seguinte, as duas telas dela
    tela.botao_proxima.click()
    _esperar(app, painel)
    _assentar(app)
    assert painel._indice == 2 and painel._do_livro[0] == 2
    assert tela.rotulo_a.text() == "como está no livro: Preto e branco"   # rodou no livro todo
    # apertar de novo volta ao antes e depois com a linha
    botoes[0].click()
    _assentar(app)
    assert not tela.comparando and tela.rolagem.isVisible() and not tela.duas.isVisible()
    assert tela.visor.comparando
