"""As provas de comportamento da etapa 4 da obra de 26/10/2026: dividir à mão folha por
folha (CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Cada teste diz a decisão e as palavras do Samuel. Aparência não conta: o que se mede aqui
é a ferramenta em que a tela está, o projeto (o que vai para o projeto.json), o Histórico
e o PDF que o programa gera (core.pipeline.processar, o mesmo do "Confirmar e processar").

  Pedido da etapa 4 / D-007 (sessão 1, 26/10, print s1-10): "quando a tela está assim no
      dividir, é bom para mudar folhas que sairam erradas, eu posso entrar ali e mudar a
      marcação de folhas erradas, mas quando eu escolher para começar no automatico e
      dividir as folhas o livro tem que aparecer em uma pagina por vez para mim."
  Plano de 26/10, etapa 4: "'dividir esta' sempre ativo" (promessa P-059); dividir, não
      dividir e mover a linha de UMA folha mexem só nas páginas dela, sem recomeçar (D-489)
      e sem perder o feito nas outras.
  Lista única 3.1 (23/10): "Não dá para girar o livro antes de dividir: livro escaneado de
      lado não divide" (o Righetti).
  D-495 (escolha da gerente, D-014): "Righetti 96: a faixa preta da tampa do scanner sai
      quando a folha é girada e dividida à mão [...], não por regra geral." + "livro com
      moldura impressa preta não perde a moldura".
  Bug da etapa 9c (27/10): "Dividir do ScanTailor erra no 'La vida eterna' (folhas 4 e 5):
      divide a 10% da largura, na linha vertical escura da beirada".
  D-004 / D-009: a divisão à mão grava a marca "mexida à mão" e vale no PDF com o Dividir
      do livro desligado.
  D-016: a página dividida à mão é montada como a do Automático (a ordem obrigatória).

Páginas sintéticas na maior parte (a medida é de lugar, tamanho e cor do papel, no caminho
inteiro do processar); o Righetti e o "La vida eterna" de verdade quando estão no PC (só
lidos; o teste pula sem eles).
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import analise, etapas  # noqa: E402
from core import automatico as A  # noqa: E402
from core import dividir_scantailor as ds  # noqa: E402
from core import st_ferramentas as st  # noqa: E402
from core.endireitar import girar_90  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from core.girar import GIRO_ESQUERDA  # noqa: E402
from core.pipeline import achar_divisao, processar  # noqa: E402

DPI = 150
AMARELADO = (170, 215, 235)            # BGR: papel velho
precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")

RIGHETTI = Path(r"D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
                r"Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf")
LA_VIDA_ETERNA = Path(r"D:/Livros para editar/2 - TEOLOGIA/Escatologia/"
                      r"La vida eterna y La profundidad del alma.pdf")


# --- os livros de teste -----------------------------------------------------------

def _pagina(largura: int = 600, altura: int = 840) -> np.ndarray:
    """Papel amarelado com margem larga e linhas de "texto" pretas."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    for y in range(140, altura - 160, 40):
        img[y:y + 12, 110:largura - 110] = 25
    return img


def _aberto() -> np.ndarray:
    """Um livro aberto: duas páginas lado a lado (a dobra no meio)."""
    return np.concatenate([_pagina(), _pagina()], axis=1)


def _pdf(caminho: Path, imagens) -> str:
    doc = fitz.open()
    for img in imagens:
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _livro_aberto(tmp_path: Path, nome: str = "aberto.pdf", folhas: int = 3) -> str:
    return _pdf(tmp_path / nome, [_aberto() for _ in range(folhas)])


def _de_lado(img: np.ndarray) -> np.ndarray:
    """A folha como o scanner a deixou, deitada: "¼ à esquerda" (GIRO_ESQUERDA) a endireita."""
    return girar_90(img, 90)


def _righetti_sintetico() -> np.ndarray:
    """A folha do Righetti como ela fica depois de girada (medida no livro de verdade,
    folha 96 a 150 DPI): uma tira clara da tampa em cima, a faixa preta de ~2 cm
    atravessando a folha, o fundo preto do scanner à esquerda e o livro aberto."""
    altura, largura = 1275, 1650
    img = np.full((altura, largura, 3), 240, np.uint8)
    img[:, :270] = 12                     # o fundo preto do scanner, à esquerda
    img[105:235, :] = 12                  # a faixa preta da tampa
    img[:105, :] = 236                    # a tira clara da tampa, na beirada
    for y in range(300, 1200, 24):
        img[y:y + 8, 330:900] = 30        # o texto da página da esquerda
        img[y:y + 8, 1010:1580] = 30      # o da direita
    return img


def _com_moldura_impressa() -> np.ndarray:
    """Livro aberto com moldura impressa PRETA e grossa (4,5 mm) em cada página: tem de
    sobrar inteira (D-495)."""
    altura, largura = 1275, 1650
    img = np.full((altura, largura, 3), 240, np.uint8)
    for x0, x1 in ((60, 780), (870, 1590)):
        cv2.rectangle(img, (x0, 60), (x1, altura - 60), (15, 15, 15), 27)
        for y in range(160, altura - 160, 24):
            img[y:y + 8, x0 + 80:x1 - 80] = 30
    return img


def _la_vida_eterna_sintetica() -> np.ndarray:
    """A folha 4 do "La vida eterna" (medida no livro a 150 DPI): o livro aberto com a
    linha vertical escura da beirada da página da esquerda a 11% da largura e o branco do
    scanner antes dela. O ScanTailor corta nesse branco (bug achado pela etapa 9c)."""
    altura, largura = 1240, 1754
    img = np.full((altura, largura, 3), 250, np.uint8)
    for y in range(60, 950, 26):
        img[y:y + 9, int(largura * 0.19):int(largura * 0.51)] = 30
    for y in range(40, 560, 26):
        img[y:y + 9, int(largura * 0.60):int(largura * 0.92)] = 30
    img[340:1030, 199:203] = 20           # a linha escura da beirada do livro
    img[1020:1028, 199:1700] = 40         # e a de baixo
    return img


def _paginas_do_pdf(caminho: str) -> list[np.ndarray]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.width, pix.n)[..., :3].copy())
        return saida


def _gerar(janela, tmp_path: Path, nome: str) -> list[np.ndarray]:
    """O PDF do livro aberto, como o "Confirmar e processar" grava: as páginas desenhadas."""
    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(processar(projeto))


def _linhas_pretas_em_cima(img: np.ndarray, parte: float = 0.2, cheia: float = 0.6) -> int:
    """Quantas linhas, no alto da página, são quase todas pretas (a faixa da tampa).
    `cheia`: a parte da largura que tem de ser preta (etapa 9b-2: com o "cortar fora" da
    D-559 a página fica justa no texto, e as linhas de "texto" de mentira, de 83% da largura,
    entram no alto da página; 0,9 só conta a faixa, que atravessa a página inteira)."""
    cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    alto = cinza[: int(cinza.shape[0] * parte)]
    return int(((alto < 60).mean(axis=1) > cheia).sum())


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
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def _rodar(janela, etapas_, alcance="livro", opcoes=None) -> bool:
    """O que o Kaique faz no painel Automático: marca as etapas e roda (no mesmo fio)."""
    estado = janela.estado_do_automatico
    estado.marcadas = set(etapas_)
    estado.opcoes.update(opcoes or {})
    estado.alcance = alcance
    return janela.rodar_o_automatico(esperar=True, perguntar=False)


def _no_dividir(tela, folha: int) -> None:
    """Escolhe a ferramenta Dividir e vai à folha (como a trilha e as setas)."""
    tela.escolher_ferramenta("dividir")
    assert tela.trabalha_com_folhas
    tela._ir_para(folha)


def _estado_das_outras(projeto, folha: int) -> list[tuple]:
    """O que importa nas páginas das OUTRAS folhas (filtro, corte, "está certo", marca)."""
    return [(p.folha, p.metade, p.filtro, p.recorte, p.revisada, tuple(p.mexida_a_mao))
            for p in projeto.paginas if p.folha != folha]


# --- "dividir esta" sempre aceso (P-059), só nesta folha, sem recomeçar ---------------

@precisa_da_dll
def test_dividir_esta_aceso_no_livro_sem_dividir_e_mexe_so_nesta_folha(janela, tmp_path):
    """Plano de 26/10, etapa 4 ("'dividir esta' sempre ativo"), D-009 ("abrir o livro sem
    escolher nenhuma opção para fazer tudo manualmente"), D-489 (nada recomeça). Livro
    aberto sem nada marcado: o botão está aceso e divide SÓ a folha 1; o filtro, o corte e
    o "está certo" das outras páginas ficam; o Histórico continua (não recomeçou); a folha
    ganha a marca "mexida à mão"; o PDF sai com a folha 1 em duas páginas em pé.
    No código antigo o botão ficava cinza ("aqui não dá para dividi-la")."""
    janela.abrir_livro(_livro_aberto(tmp_path))
    tela, projeto = janela.tela_conferir, janela.projeto
    assert len(projeto.paginas) == 3 and not projeto.dividir_folhas
    # trabalho nas outras folhas, pela tela
    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    tela.ir_para_pagina(2)
    tela._mover_recorte((0.05, 0.05, 0.95, 0.95))
    feitas = len(janela.acoes.feitas)
    antes = _estado_das_outras(projeto, 0)

    _no_dividir(tela, 0)
    assert tela.botao_nao_dividir.isEnabled(), tela.botao_nao_dividir.toolTip()
    assert tela.botao_nao_dividir.text() == "dividir esta"
    tela.botao_nao_dividir.click()

    assert projeto.folhas[0].dividir
    assert [p.metade for p in projeto.paginas if p.folha == 0] == ["esquerda", "direita"]
    assert len(projeto.paginas) == 4 and [p.indice for p in projeto.paginas] == [0, 1, 2, 3]
    assert _estado_das_outras(projeto, 0) == antes
    assert len(janela.acoes.feitas) == feitas + 1          # nada recomeçou
    assert etapas.DIVIDIR in projeto.folhas[0].mexida_a_mao
    assert not projeto.dividir_folhas                      # o Dividir do livro continua desligado
    assert tela.indice_folha == 0                          # a tela ficou na mesma folha
    paginas = _gerar(janela, tmp_path, "dividida")
    assert len(paginas) == 4
    assert all(p.shape[0] > p.shape[1] for p in paginas[:2])      # duas páginas em pé
    assert paginas[2].shape[1] > paginas[2].shape[0]              # a folha 2 continua deitada

    tela.desfazer()                                        # Ctrl+Z: volta só esta folha
    assert len(projeto.paginas) == 3 and not projeto.folhas[0].dividir
    assert _estado_das_outras(projeto, 0) == antes


@precisa_da_dll
def test_nao_dividir_e_dividir_de_novo_devolvem_as_paginas_como_estavam(janela, tmp_path):
    """Plano de 26/10, etapa 4: "não dividir esta" junta as duas páginas numa só (a lista
    muda só nesta folha: a página da direita não fica mais "apagada" na lista) e "dividir
    esta" de novo devolve as duas como estavam (o corte à mão de uma delas e o "tirar do
    livro" da outra)."""
    janela.abrir_livro(_livro_aberto(tmp_path))
    _rodar(janela, [A.DIVIDIR])
    tela, projeto = janela.tela_conferir, janela.projeto
    assert len(projeto.paginas) == 6
    tela.ir_para_pagina(2)                                 # a esquerda da folha 2
    tela._mover_recorte((0.1, 0.1, 0.9, 0.9))
    tela.ir_para_pagina(3)
    tela.apagar_pagina()                                   # "tirar do livro" a direita
    antes = _estado_das_outras(projeto, 1)

    _no_dividir(tela, 1)
    assert tela.botao_nao_dividir.text() == "não dividir esta"
    tela.botao_nao_dividir.click()
    assert [p.metade for p in projeto.paginas if p.folha == 1] == ["inteira"]
    assert len(projeto.paginas) == 5 and projeto.total_apagadas == 0
    assert _estado_das_outras(projeto, 1) == antes
    assert len(_gerar(janela, tmp_path, "juntada")) == 5

    tela.botao_nao_dividir.click()                         # "dividir esta"
    da_folha = [p for p in projeto.paginas if p.folha == 1]
    assert [p.metade for p in da_folha] == ["esquerda", "direita"]
    assert da_folha[0].recorte == (0.1, 0.1, 0.9, 0.9) and da_folha[1].apagada
    assert _estado_das_outras(projeto, 1) == antes


@precisa_da_dll
def test_mover_a_linha_mexe_so_nesta_folha(janela, tmp_path):
    """Plano de 26/10, etapa 4: mover a linha de UMA folha não mexe nas outras folhas nem
    nas páginas delas, e grava a marca "mexida à mão" (D-004)."""
    janela.abrir_livro(_livro_aberto(tmp_path))
    _rodar(janela, [A.DIVIDIR])
    tela, projeto = janela.tela_conferir, janela.projeto
    linhas = [f.posicao_corte for f in projeto.folhas]
    antes = _estado_das_outras(projeto, 2)
    _no_dividir(tela, 2)
    tela._mover_corte(0.42)
    assert projeto.folhas[2].posicao_corte == pytest.approx(0.42)
    assert [f.posicao_corte for f in projeto.folhas[:2]] == linhas[:2]
    assert _estado_das_outras(projeto, 2) == antes
    assert etapas.DIVIDIR in projeto.folhas[2].mexida_a_mao


def test_o_aviso_nao_parece_dupla_nunca_divide(janela, tmp_path):
    """O botão "não dividir esta" do aviso "Não parece dupla" ("Esta folha parece ter uma
    página só") nunca divide a folha: agora que o botão da ferramenta divide a folha de uma
    página só, o do aviso só a dá como conferida (P-112)."""
    janela.abrir_livro(_livro_aberto(tmp_path))
    tela, projeto = janela.tela_conferir, janela.projeto
    projeto.folhas[0].alertas = [analise.NAO_PARECE_DUPLA]
    _no_dividir(tela, 0)
    tela._aplicar_correcao(analise.NAO_PARECE_DUPLA, "nao_dividir")
    assert not projeto.folhas[0].dividir and projeto.folhas[0].revisada
    assert len(projeto.paginas) == 3


@precisa_da_dll
def test_d489_a_divisao_a_mao_volta_ao_reabrir_sem_recomecar(janela, tmp_path):
    """D-489 (recomeço só quando o PDF mudou, o projeto.json não lê ou falta página): a
    folha dividida à mão volta dividida ao reabrir o livro, com o Histórico."""
    import projetos

    caminho = _livro_aberto(tmp_path)
    janela.abrir_livro(caminho)
    tela = janela.tela_conferir
    _no_dividir(tela, 1)
    tela.botao_nao_dividir.click()
    janela._salvar_agora()
    feitas = len(janela.acoes.feitas)
    janela.abrir_livro(caminho)
    projeto = janela.projeto
    assert projeto.folhas[1].dividir
    assert [p.metade for p in projeto.paginas] == ["inteira", "esquerda", "direita", "inteira"]
    assert len(janela.acoes.feitas) == feitas
    assert projetos.motivo_sem_analise(projeto, projeto) == ""


# --- D-007: uma página por vez fora do Dividir ------------------------------------------

@precisa_da_dll
def test_d007_dividido_pelo_automatico_aparece_uma_pagina_por_vez(janela, tmp_path):
    """D-007 (26/10): "quando eu escolher para começar no automatico e dividir as folhas o
    livro tem que aparecer em uma pagina por vez para mim." Rodar o Dividir com a tela no
    Dividir leva à página (uma por vez); a folha inteira com a linha continua no Dividir,
    quando a pessoa o escolhe, para consertar. O ANTIGO SAIU: a tela ficava no Dividir."""
    from ui.tela_conferir import ABA_CORTE

    janela.abrir_livro(_livro_aberto(tmp_path))
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    assert tela.aba_atual == ABA_CORTE
    _rodar(janela, [A.DIVIDIR])
    assert tela.aba_atual != ABA_CORTE and not tela.trabalha_com_folhas
    assert tela.item_atual.metade in ("esquerda", "direita")     # uma página, não a folha
    tela.escolher_ferramenta("dividir")                          # consertar: a folha volta
    assert tela.trabalha_com_folhas and tela.visualizadores[ABA_CORTE].corte_visivel


@precisa_da_dll
def test_d007_livro_dividido_nunca_abre_no_dividir(janela, tmp_path):
    """D-007: reabrir um livro dividido (com o Dividir ligado no livro) abre na página, uma
    por vez. O ANTIGO SAIU: abria na ferramenta Dividir (a folha inteira com a linha)."""
    from ui.tela_conferir import ABA_CORTE

    caminho = _livro_aberto(tmp_path)
    janela.abrir_livro(caminho)
    _rodar(janela, [A.DIVIDIR])
    assert janela.projeto.dividir_folhas
    janela._salvar_agora()
    janela.abrir_livro(caminho)
    tela = janela.tela_conferir
    assert tela.aba_atual != ABA_CORTE and not tela.trabalha_com_folhas
    assert janela.tela_conferir._aba_de_partida(janela.projeto) != ABA_CORTE


# --- lista única 3.1: girar o livro antes de dividir -----------------------------------

@precisa_da_dll
def test_lista_3_1_girar_a_folha_e_dividir_a_mao(janela, tmp_path):
    """Lista única 3.1: "livro escaneado de lado não divide". Girar a folha ¼ e "dividir
    esta": a lombada é achada na folha GIRADA e o PDF sai com duas páginas em pé. No código
    antigo o "dividir esta" ficava cinza depois de girar."""
    janela.abrir_livro(_pdf(tmp_path / "de_lado.pdf", [_de_lado(_aberto()), _de_lado(_aberto())]))
    tela, projeto = janela.tela_conferir, janela.projeto
    _no_dividir(tela, 0)
    tela._girar_folhas(GIRO_ESQUERDA, so_esta=True)
    assert projeto.folhas[0].rotacao == GIRO_ESQUERDA
    assert tela.botao_nao_dividir.isEnabled()
    tela.botao_nao_dividir.click()
    assert projeto.folhas[0].dividir
    assert projeto.folhas[0].posicao_corte == pytest.approx(0.5, abs=0.06)
    paginas = _gerar(janela, tmp_path, "girada")
    assert len(paginas) == 3
    assert all(p.shape[0] > p.shape[1] for p in paginas[:2])      # em pé
    # as linhas de "texto" saem deitadas (a folha foi girada antes de dividir)
    linhas = (cv2.cvtColor(paginas[0], cv2.COLOR_RGB2GRAY) < 100).mean(axis=1)
    assert linhas.max() > 0.5


@precisa_da_dll
def test_lista_3_1_girar_o_livro_e_dividir_no_automatico(janela, tmp_path):
    """Lista única 3.1, no Automático: girar todas as folhas e rodar o Dividir no livro
    todo divide cada folha na lombada da folha girada."""
    janela.abrir_livro(_pdf(tmp_path / "de_lado.pdf", [_de_lado(_aberto()) for _ in range(3)]))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._acao_nas_escolhidas("girar_esquerda", [0, 1, 2])      # a grade: girar ¼ ← as três
    assert [f.rotacao for f in projeto.folhas] == [GIRO_ESQUERDA] * 3
    _rodar(janela, [A.DIVIDIR])
    assert all(f.dividir for f in projeto.folhas)
    assert all(abs(f.posicao_corte - 0.5) < 0.06 for f in projeto.folhas)
    paginas = _gerar(janela, tmp_path, "girado_automatico")
    assert len(paginas) == 6 and all(p.shape[0] > p.shape[1] for p in paginas)


@precisa_da_dll
@pytest.mark.skipif(not RIGHETTI.is_file(), reason="sem o acervo (só no PC do Samuel)")
def test_lista_3_1_righetti_de_verdade_girado_e_dividido(janela, tmp_path):
    """Lista única 3.1 no Righetti (folhas 1, 96 e 135, só lidas): girar todas ¼ à esquerda
    e rodar o Dividir: cada folha é dividida na dobra (medida em 27/10: 0,58 da largura) e
    sai em duas páginas em pé."""
    pdf = tmp_path / "righetti.pdf"
    with fitz.open(str(RIGHETTI)) as origem, fitz.open() as novo:
        for i in (0, 95, 134):
            novo.insert_pdf(origem, from_page=i, to_page=i)
        novo.save(str(pdf))
    janela.abrir_livro(str(pdf))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._registrar("girar", "folha", [0, 1, 2], {"rotacao": {"0": 270, "1": 270, "2": 270}},
                    "Girar todas")
    _rodar(janela, [A.DIVIDIR])
    assert all(f.dividir for f in projeto.folhas)
    assert all(0.55 < f.posicao_corte < 0.62 for f in projeto.folhas), \
        [f.posicao_corte for f in projeto.folhas]
    paginas = _gerar(janela, tmp_path, "righetti")
    assert len(paginas) == 6 and all(p.shape[0] > p.shape[1] for p in paginas)


# --- D-495: a tampa do scanner sai ao dividir à mão; a moldura impressa fica ------------

def test_d495_a_regra_da_tampa_na_folha_e_na_moldura():
    """D-495, na conta (core/dividir_a_mao.achar_a_tampa): a folha do Righetti (girada)
    tem a tampa achada (o papel começa depois da faixa preta e do fundo da esquerda); o
    livro com moldura impressa preta grossa não tem tampa nenhuma."""
    from core.dividir_a_mao import achar_a_tampa      # (não existe no código antigo)

    tampa = achar_a_tampa(_righetti_sintetico(), 270, DPI)
    assert tampa is not None and tampa[0] == 270
    assert tampa[2] == pytest.approx(235 / 1275, abs=0.01)       # depois da faixa preta
    assert tampa[1] == pytest.approx(270 / 1650, abs=0.01)       # depois do fundo da esquerda
    assert tampa[3:] == [1.0, 1.0]                               # direita e embaixo: nada
    assert achar_a_tampa(_com_moldura_impressa(), 0, DPI) is None
    assert achar_a_tampa(_aberto(), 0, DPI) is None


@precisa_da_dll
def test_d495_a_faixa_da_tampa_sai_ao_girar_e_dividir_a_mao(janela, tmp_path):
    """D-495: a faixa preta da tampa do scanner sai quando a folha é girada e dividida à
    mão. A mesma folha (de lado): a 2 girada e dividida à mão sai sem a faixa preta em cima
    nas duas páginas. No código antigo nem dava para dividir à mão.
    Etapa 9b-2 (D-559, 27/10/2026, `ac-tampa`: "sumir em todo o livro, e o Kaique escolhe por
    livro cortar ou pintar de branco"; substitui a D-495/D-499 "só à mão"): a 1, girada e
    dividida pelo AUTOMÁTICO, também sai sem a faixa (até a etapa 9b-2 ela continuava)."""
    janela.abrir_livro(_pdf(tmp_path / "tampa.pdf",
                            [_de_lado(_righetti_sintetico()), _de_lado(_righetti_sintetico())]))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._registrar("girar", "folha", [0, 1], {"rotacao": {"0": 270, "1": 270}}, "Girar")
    _no_dividir(tela, 1)
    tela.botao_nao_dividir.click()                       # folha 2 à mão
    assert len(projeto.folhas[1].tampa_do_scanner) == 5  # a tampa achada
    # a folha 1 pelo Automático (só ela): o Dividir nas páginas escolhidas
    from ui.automatico import NAS_ESCOLHIDAS

    estado = janela.estado_do_automatico
    estado.escolhidas = [0]
    _rodar(janela, [A.DIVIDIR], alcance=NAS_ESCOLHIDAS)
    assert projeto.folhas[0].dividir and len(projeto.folhas[0].tampa_do_scanner) == 5   # D-559
    paginas = _gerar(janela, tmp_path, "tampa")
    assert len(paginas) == 4
    assert all(_linhas_pretas_em_cima(p, cheia=0.9) == 0 for p in paginas)   # saiu das quatro


@precisa_da_dll
def test_d495_acertar_a_linha_a_mao_tambem_tira_a_tampa(janela, tmp_path):
    """D-495, no caminho do Kaique: o Automático dividiu as folhas giradas; ele entra no
    Dividir para consertar a folha 1 e arrasta a linha - acertar a linha à mão não traz a
    faixa de volta. Etapa 9b-2 (D-559: "sumir em todo o livro"): o Automático já tira a
    faixa de todas as folhas (até a etapa 9b-2 só a folha da linha acertada a perdia)."""
    janela.abrir_livro(_pdf(tmp_path / "tampa.pdf",
                            [_de_lado(_righetti_sintetico()), _de_lado(_righetti_sintetico())]))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._acao_nas_escolhidas("girar_esquerda", [0, 1])
    _rodar(janela, [A.DIVIDIR])
    assert all(f.dividir and len(f.tampa_do_scanner) == 5 for f in projeto.folhas)   # D-559
    _no_dividir(tela, 0)
    tela._mover_corte(projeto.folhas[0].posicao_corte + 0.01)
    assert all(len(f.tampa_do_scanner) == 5 for f in projeto.folhas)
    paginas = _gerar(janela, tmp_path, "linha")
    assert [_linhas_pretas_em_cima(p, cheia=0.9) == 0 for p in paginas] == [True] * 4


@precisa_da_dll
def test_d495_a_moldura_impressa_preta_nao_some_ao_dividir_a_mao(janela, tmp_path):
    """D-495: "livro com moldura impressa preta não perde a moldura". Dividir à mão o livro
    aberto com moldura preta grossa: nenhuma tampa, e a moldura sai no PDF (a linha de
    cima da moldura continua preta)."""
    janela.abrir_livro(_pdf(tmp_path / "moldura.pdf", [_com_moldura_impressa()]))
    tela, projeto = janela.tela_conferir, janela.projeto
    _no_dividir(tela, 0)
    tela.botao_nao_dividir.click()
    assert projeto.folhas[0].dividir and projeto.folhas[0].tampa_do_scanner == [0]   # procurada: nada
    paginas = _gerar(janela, tmp_path, "moldura")
    assert len(paginas) == 2
    assert all(_linhas_pretas_em_cima(p, 0.12) >= 10 for p in paginas)


@precisa_da_dll
@pytest.mark.skipif(not RIGHETTI.is_file(), reason="sem o acervo (só no PC do Samuel)")
def test_d495_righetti_96_de_verdade(janela, tmp_path):
    """D-495 no Righetti 96 (só lido): girar ¼ à esquerda e "dividir esta". REVERSÃO: no
    código antigo o botão ficava cinza; dividida à mão, a página da direita sai sem a faixa
    preta em cima. Etapa 9b-2 (D-559: "sumir em todo o livro"): dividida pelo Automático
    também (até a etapa 9b-2: ~125 linhas pretas a 150 DPI)."""
    pdf = tmp_path / "righetti96.pdf"
    with fitz.open(str(RIGHETTI)) as origem, fitz.open() as novo:
        novo.insert_pdf(origem, from_page=95, to_page=95)
        novo.insert_pdf(origem, from_page=95, to_page=95)
        novo.save(str(pdf))
    janela.abrir_livro(str(pdf))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._registrar("girar", "folha", [0, 1], {"rotacao": {"0": 270, "1": 270}}, "Girar")
    _no_dividir(tela, 1)
    tela.botao_nao_dividir.click()
    from ui.automatico import NAS_ESCOLHIDAS

    janela.estado_do_automatico.escolhidas = [0]
    _rodar(janela, [A.DIVIDIR], alcance=NAS_ESCOLHIDAS)
    paginas = _gerar(janela, tmp_path, "righetti96")
    assert len(paginas) == 4
    assert _linhas_pretas_em_cima(paginas[1]) == 0       # Automático: saiu (D-559)
    assert _linhas_pretas_em_cima(paginas[3]) == 0       # à mão: saiu
    assert _linhas_pretas_em_cima(paginas[2]) == 0


# --- bug da etapa 9c: a linha da beirada não é a lombada ---------------------------------

@precisa_da_dll
def test_bug_9c_a_linha_escura_da_beirada_nao_e_lombada():
    """REVERSÃO do bug achado pela etapa 9c (27/10/2026, "La vida eterna" folhas 4 e 5): o
    jeito do ScanTailor dividia a 10% da largura, no branco antes da linha escura da beirada
    do livro (a página da esquerda virava uma tira de margem). Agora o corte na beirada
    (fora de 20% a 80%, a regra do próprio ScanTailor para as linhas) não vale: a divisão
    fica perto do meio e a folha vai para o "Para revisar" ("Lombada incerta")."""
    img = _la_vida_eterna_sintetica()
    resultado = ds.achar(img, DPI, ds.MODO_AUTOMATICO)
    assert ds.posicao_da_divisao(resultado) < 0.2          # o ScanTailor erra aqui (a causa)
    for forcar in (False, True):
        lombada = achar_divisao(img, ds.JEITO_SCANTAILOR, DPI, forcar=forcar)
        assert lombada.e_paisagem and 0.4 < lombada.posicao < 0.65, lombada
        assert lombada.confianca < analise.CONFIANCA_LOMBADA_MIN
    # a folha boa (dobra no meio) continua pela conta do ScanTailor, com confiança cheia
    boa = achar_divisao(_aberto(), ds.JEITO_SCANTAILOR, DPI)
    assert boa.posicao == pytest.approx(0.5, abs=0.05) and boa.confianca == 1.0


@precisa_da_dll
@pytest.mark.skipif(not LA_VIDA_ETERNA.is_file(), reason="o 'La vida eterna' não está neste computador")
def test_bug_9c_la_vida_eterna_folhas_4_e_5_de_verdade(tmp_path):
    """O "La vida eterna" de verdade (só lido): as folhas 4 e 5 eram divididas a 0,10 pelo
    jeito do ScanTailor; agora perto do meio e com "Lombada incerta". As folhas 1 a 3 e 6 a
    10 continuam onde o ScanTailor as divide."""
    from core.pdf_io import abrir_pdf, pagina_para_array
    from core.pipeline import DPI_ANALISE

    doc = abrir_pdf(str(LA_VIDA_ETERNA))
    try:
        for indice in range(10):
            img = pagina_para_array(doc, indice, dpi=DPI_ANALISE)
            lombada = achar_divisao(img, ds.JEITO_SCANTAILOR, DPI_ANALISE)
            if indice in (3, 4):
                assert 0.4 < lombada.posicao < 0.65 and lombada.confianca < 0.5, (indice, lombada)
            else:
                st_ = ds.posicao_da_divisao(ds.achar(img, DPI_ANALISE, ds.MODO_AUTOMATICO))
                assert lombada.posicao == pytest.approx(st_) and lombada.confianca == 1.0
    finally:
        doc.close()


@precisa_da_dll
@pytest.mark.skipif(not LA_VIDA_ETERNA.is_file(), reason="o 'La vida eterna' não está neste computador")
def test_bug_9c_la_vida_eterna_a_analise_ja_nao_faz_a_tira_de_margem(tmp_path):
    """O efeito do conserto no caminho inteiro (análise com "Dividir" pelo jeito do
    ScanTailor, as 6 primeiras folhas copiadas): a página 7 (texto da folha 4) não ganha
    mais "Parece em branco" (era uma tira de margem de 177 pontos), e as folhas 4 e 5 ficam
    em "Lombada incerta" para o Kaique conferir a linha."""
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    copia = tmp_path / "vida6.pdf"
    with fitz.open(str(LA_VIDA_ETERNA)) as livro, fitz.open() as novo:
        novo.insert_pdf(livro, from_page=0, to_page=5)
        novo.save(str(copia))
    projeto = Projeto(caminho_entrada=str(copia), caminho_saida=str(tmp_path / "s.pdf"), nome="vida")
    projeto.dividir_folhas, projeto.dividir_como = True, ds.JEITO_SCANTAILOR
    analisar_projeto(projeto)
    assert all(0.4 < projeto.folhas[i].posicao_corte < 0.65 for i in (3, 4))
    assert all(analise.LOMBADA_INCERTA in projeto.folhas[i].alertas for i in (3, 4))
    assert analise.EM_BRANCO not in projeto.paginas[6].alertas


# --- D-016: a página dividida à mão é montada como a do Automático ----------------------

@precisa_da_dll
def test_d016_dividida_a_mao_sai_igual_a_dividida_pelo_automatico(janela, tmp_path):
    """D-016 (a montagem da página segue a ordem obrigatória: girar, dividir, endireitar,
    cortar uma vez no fim). Duas folhas iguais, com Endireitar e Cortar do Automático no
    livro: a 1 dividida pelo Automático, a 2 dividida à mão na mesma linha. As páginas
    saem IGUAIS no PDF (a divisão à mão entra no mesmo caminho da montagem)."""
    from ui.automatico import NAS_ESCOLHIDAS

    janela.abrir_livro(_livro_aberto(tmp_path, folhas=2))
    tela, projeto = janela.tela_conferir, janela.projeto
    _rodar(janela, [A.ENDIREITAR, A.CORTAR])
    janela.estado_do_automatico.escolhidas = [0]
    _rodar(janela, [A.DIVIDIR], alcance=NAS_ESCOLHIDAS)
    assert projeto.folhas[0].dividir and not projeto.folhas[1].dividir
    _no_dividir(tela, 1)
    tela.botao_nao_dividir.click()
    tela._mover_corte(projeto.folhas[0].posicao_corte)
    assert projeto.folhas[1].posicao_corte == pytest.approx(projeto.folhas[0].posicao_corte)
    paginas = _gerar(janela, tmp_path, "d016")
    assert len(paginas) == 4
    for a, b in ((paginas[0], paginas[2]), (paginas[1], paginas[3])):
        assert a.shape == b.shape and int(np.abs(a.astype(int) - b.astype(int)).max()) <= 2
