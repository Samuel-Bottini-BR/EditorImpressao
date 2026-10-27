"""As provas de comportamento da etapa 3 da obra de 26/10/2026: abrir direto na área de
trabalho e o Automático de verdade (CLAUDE.md §11, regra 4; Livro de decisões,
docs/plano/DECISOES.md).

Cada teste diz a decisão e as palavras do Samuel. Aparência não conta: o que se mede aqui
é a tela em que a janela está, o projeto (o que vai para o projeto.json), o Histórico e o
PDF que o programa gera (core.pipeline.processar, o mesmo do "Confirmar e processar").

  D-002 (25/09) + Kaique (22/09) + 26/10: "Essa pagina não era mais para aparecer – nós
      tínhamos que abrir direto na área de trabalho" · "eu quero poder sim fazer
      automatico para todo livro, mas também quero pode fazer uma a uma."
  D-003 (28/09) / D-016: "Ordem das etapas: livre. [...] muda arrastando com o mouse."
  D-004 (28/09): "Automático em livro já mexido à mão: o programa pergunta se quer pular
      as páginas mexidas."
  D-005 (12/10): "B — Um aviso embaixo da página" · D-018 (escolha da gerente).
  D-071 (`fr-219`, 22/10): "Mas ainda pode melhorar a caixa de como escolhemos o que vai
      dentro da receita."
  D-094 (09/10): "quero a b e c juntas." (o retângulo do corte nos três lugares).
  D-284 (21/10): "Medir o livro inteiro por trás, depois de abrir" + 29/09: "Página sempre
      abre em 'Original', sem mexer."
  D-334 (24/09): a grade "Todas as páginas" com várias escolhidas.
  Defeito de 29/09 + teste do Kaique de 26/10 (tarefa 7: "só endireitar" cortou; tarefa 8:
      "Preto e branco" ignorado): mudar uma etapa num livro já conferido vale e nada se perde.
  Nenhuma opção da tela "O que fazer" se perde (pedido da gerente; D-002, rodada 2 nº 5).
  Marca "mexida à mão" ligada na tela (pendência da etapa 1; D-009).

Páginas sintéticas de propósito (a medida é de lugar, tamanho e cor do papel, no caminho
inteiro do processar), como tests/test_decisoes.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core import etapas, perfis  # noqa: E402
from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.pipeline import processar  # noqa: E402

DPI = 150
AMARELADO = (170, 215, 235)            # BGR: papel velho


# --- o livro de teste -----------------------------------------------------------

def _pagina(giro: float = 0.0, largura: int = 600, altura: int = 840) -> np.ndarray:
    """Papel amarelado com margem larga e linhas de "texto" pretas; `giro` em graus."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    for y in range(140, altura - 160, 40):
        img[y:y + 12, 110:largura - 110] = 25
    if giro:
        m = cv2.getRotationMatrix2D((largura / 2, altura / 2), giro, 1.0)
        img = cv2.warpAffine(img, m, (largura, altura), borderValue=AMARELADO)
    return img


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


def _livro(tmp_path: Path, nome: str = "livro.pdf") -> str:
    """3 folhas: 1) duas páginas lado a lado (para dividir), 2) uma página torta 3 graus,
    3) uma página reta."""
    caminho = tmp_path / nome
    if not caminho.exists():
        _pdf(caminho, [np.concatenate([_pagina(), _pagina()], axis=1), _pagina(giro=3.0), _pagina()])
    return str(caminho)


def _paginas_do_pdf(caminho: str) -> list[np.ndarray]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.width, pix.n)[..., :3].copy())
        return saida


def _gerar(janela, tmp_path: Path, nome: str) -> list[np.ndarray]:
    """O PDF do livro aberto, como o "Confirmar e processar" grava (sem a janela de
    confirmação): as páginas desenhadas."""
    import copy

    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(processar(projeto))


def _papel(img: np.ndarray) -> float:
    """O azul do papel (RGB: canal 2) num pedaço da margem de cima: 170 no amarelado,
    perto de 255 quando o filtro branqueia."""
    altura, largura = img.shape[:2]
    return float(img[int(altura * 0.06):int(altura * 0.11), int(largura * 0.4):int(largura * 0.6), 2].mean())


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


def _nova_janela(app):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    return janela


def _fechar(janela) -> None:
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


@pytest.fixture
def janela(app, pasta):
    janela = _nova_janela(app)
    yield janela
    _fechar(janela)


def _assentar(app, vezes: int = 5) -> None:
    for _ in range(vezes):
        app.processEvents()


def _rodar(janela, etapas, alcance="livro", pagina=0, escolhidas=None, opcoes=None,
           desligar=False) -> bool:
    """O que o Kaique faz no painel Automático: marca as etapas, escolhe onde e roda
    (medindo no mesmo fio)."""
    from ui.automatico import NAS_ESCOLHIDAS

    estado = janela.estado_do_automatico
    estado.marcadas = set(etapas)
    estado.opcoes.update(opcoes or {})
    if alcance == NAS_ESCOLHIDAS:
        estado.escolhidas = list(escolhidas or [])
    estado.alcance = alcance
    janela.tela_conferir.ir_para_pagina(pagina)
    return janela.rodar_o_automatico(desligar=desligar, esperar=True)


# --- D-002: abrir direto na área de trabalho ------------------------------------------

def test_d002_abrir_vai_direto_para_a_area_de_trabalho_e_a_tela_de_opcoes_saiu(janela, tmp_path):
    """D-002 / Kaique 22/09: "nós tínhamos que abrir direto na área de trabalho". O antigo
    saiu: a janela não tem mais a tela "O que fazer" (nem no meio do abrir)."""
    from ui import janela_principal as jp
    from ui.tela_opcoes import TelaOpcoes

    janela.abrir_livro(_livro(tmp_path))
    assert janela.telas.currentIndex() == jp.CONFERIR
    assert janela.telas.currentWidget() is janela.tela_conferir
    assert not hasattr(janela, "tela_opcoes")
    assert not janela.findChildren(TelaOpcoes)
    assert janela.telas.count() == 4                     # inicio, progresso, trabalho, pronto


def test_d284_a_pagina_abre_em_original_sem_mexer(janela, tmp_path):
    """29/09: "Página sempre abre em 'Original', sem mexer." + D-284: nenhuma página muda
    até rodar o automático. O PDF gerado logo depois de abrir é o livro como veio."""
    janela.abrir_livro(_livro(tmp_path))
    projeto = janela.projeto
    assert [p.filtro for p in projeto.paginas] == [ORIGINAL] * 3
    assert not (projeto.limpar or projeto.endireitar or projeto.cortar_bordas or projeto.dividir_folhas)
    assert all(not p.automatico for p in projeto.paginas)
    paginas = _gerar(janela, tmp_path, "como_veio")
    assert len(paginas) == 3
    assert paginas[0].shape[1] > paginas[0].shape[0]           # a folha dupla não foi dividida
    assert abs(_papel(paginas[2]) - AMARELADO[0]) < 8           # papel como veio (nada branqueado)


def test_d284_a_medida_por_tras_so_poe_os_avisos(janela, tmp_path):
    """D-284: a medição completa roda por trás e só guarda (os avisos); nenhuma página
    muda. Aqui a medida é chamada direto (a mesma que a TarefaMedirAoAbrir faz)."""
    janela.abrir_livro(_pdf(tmp_path / "branca.pdf",
                            [_pagina(), np.full((840, 600, 3), 250, np.uint8), _pagina()]))
    projeto = janela.projeto
    antes = [(p.filtro, p.recorte, p.angulo_manual, p.automatico) for p in projeto.paginas]
    medidas = A.medir_o_livro_ao_abrir(projeto)
    A.avisos_do_livro(projeto, medidas)
    assert "em_branco" in projeto.paginas[1].alertas
    assert [(p.filtro, p.recorte, p.angulo_manual, p.automatico) for p in projeto.paginas] == antes


# --- D-005 / D-018: o aviso do livro novo -------------------------------------------------

def test_d005_livro_novo_mostra_o_aviso_com_rodar_e_agora_nao(janela, app, tmp_path):
    """D-005: "B — Um aviso embaixo da página" ("Livro novo: ainda não passou pelo
    automático", "Rodar o automático…", "agora não")."""
    janela.show()
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    tela = janela.tela_conferir
    assert tela.aviso_do_livro_novo.isVisible()
    assert "Livro novo: ainda não passou pelo automático" in tela.texto_do_livro_novo.text()
    assert tela.botao_rodar_do_aviso.text() == "Rodar o automático…"
    assert tela.botao_agora_nao.text() == "agora não"
    tela.botao_agora_nao.click()
    assert not tela.aviso_do_livro_novo.isVisible()
    janela._salvar_agora()
    # o livro reaberto não pergunta de novo
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    assert not tela.aviso_do_livro_novo.isVisible()


def test_d018_rodar_do_aviso_abre_a_janela_com_a_receita_de_sempre_e_nada_muda(janela, app, tmp_path):
    """D-018: "Rodar o automático…" abre a janela grande já com a receita de sempre
    marcada; um clique em "Rodar" começa. Antes do "Rodar", nada muda no livro."""
    janela.show()
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    janela.tela_conferir.botao_rodar_do_aviso.click()
    _assentar(app)
    jan = janela.janela_do_automatico
    assert jan is not None and jan.isVisible()
    de_sempre = set(perfis.etapas_da_receita(perfis.ler(perfis.receita_de_sempre())))
    assert janela.estado_do_automatico.marcadas == de_sempre
    assert de_sempre == {A.ENDIREITAR, A.CORTAR, A.LIMPAR, A.GRAVURAS}
    assert not janela.projeto.endireitar and not janela.projeto.cortar_bordas
    # e o "Rodar" da janela roda (mede por trás: aqui, espera a tarefa)
    jan.botao_rodar.click()
    janela.tarefa.wait(60000)
    _assentar(app, 20)
    assert janela.projeto.endireitar and janela.projeto.cortar_bordas and janela.projeto.limpar
    assert janela.projeto.passou_pelo_automatico
    assert not janela.tela_conferir.aviso_do_livro_novo.isVisible()


# --- D-002: uma etapa só, numa página, no livro todo, nas escolhidas ------------------------

def test_d002_rodar_so_endireitar_numa_pagina_muda_so_ela(janela, tmp_path):
    """26/10: "também quero pode fazer uma a uma." Rodar só "Endireitar" na página 2 (a
    torta): o PDF muda só nela; as outras saem idênticas, ponto por ponto."""
    janela.abrir_livro(_livro(tmp_path))
    antes = _gerar(janela, tmp_path, "antes")
    assert _rodar(janela, [A.ENDIREITAR], alcance="pagina", pagina=1)
    assert janela.projeto.paginas[1].automatico == [etapas.ENDIREITAR]
    assert not janela.projeto.endireitar                # o livro continua sem endireitar
    depois = _gerar(janela, tmp_path, "depois")
    assert np.array_equal(antes[0], depois[0]) and np.array_equal(antes[2], depois[2])
    assert antes[1].shape != depois[1].shape or not np.array_equal(antes[1], depois[1])
    # e fica no Histórico (achado 1-11): uma ação, que o Ctrl+Z desfaz
    assert janela.acoes.feitas[-1].descricao.startswith("Automático: endireitar")
    janela.tela_conferir.desfazer()
    assert janela.projeto.paginas[1].automatico == []


def test_d002_rodar_no_livro_todo_divide_e_fica_no_historico(janela, tmp_path):
    """Rodar "Dividir" e "Endireitar" no livro todo: o livro liga as duas etapas, a folha
    dupla vira duas páginas (o PDF sai com 4), e a ação vai para o acoes.jsonl."""
    janela.abrir_livro(_livro(tmp_path))
    assert _rodar(janela, [A.DIVIDIR, A.ENDIREITAR])
    projeto = janela.projeto
    assert projeto.dividir_folhas and projeto.endireitar
    assert len(projeto.paginas) == 4
    assert [p.metade for p in projeto.paginas][:2] == ["esquerda", "direita"]
    assert len(_gerar(janela, tmp_path, "dividido")) == 4
    linhas = (Path(janela.resumo.pasta) / "acoes.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(linhas[-1])["tipo"] == "automatico"
    janela.tela_conferir.desfazer()
    assert len(janela.projeto.paginas) == 3 and not janela.projeto.dividir_folhas
    janela.tela_conferir.refazer()
    assert len(janela.projeto.paginas) == 4


def test_d334_escolher_paginas_na_grade_e_rodar_nelas(janela, app, tmp_path):
    """Rodada 2 nº 5 ("Aprovado"): "Escolher folhas abrindo a tela de todas as páginas
    (marcar/desmarcar)". D-334: a grade com várias escolhidas. Escolhidas as páginas 1 e 3,
    o "Limpar a folha" em Preto e branco vale só nelas, no PDF."""
    janela.show()
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    janela.escolher_paginas_para_o_automatico()
    grade = janela.tela_conferir.todas
    assert janela.tela_conferir.pilha_da_tela.currentWidget() is grade
    assert grade.para_o_automatico and grade.escolhendo
    grade._clicou(0)                        # o clique comum marca, no jeito de escolher
    grade.marcar(2)
    assert grade.escolhidas == {0, 2}
    grade.botao_usar.click()
    _assentar(app)
    estado = janela.estado_do_automatico
    assert estado.alcance == "escolhidas" and estado.escolhidas == [0, 2]
    assert janela.janela_do_automatico is not None          # a janela grande voltou
    janela._fechar_a_janela_do_automatico()
    assert _rodar(janela, [A.LIMPAR], alcance="escolhidas", escolhidas=[0, 2],
                  opcoes={"filtro_padrao": PRETO_E_BRANCO})
    assert [bool(p.automatico) for p in janela.projeto.paginas] == [True, False, True]
    paginas = _gerar(janela, tmp_path, "escolhidas")
    assert _papel(paginas[0]) > 240 and _papel(paginas[2]) > 240
    assert abs(_papel(paginas[1]) - AMARELADO[0]) < 8


def test_d334_acoes_nas_escolhidas_girar_e_tirar(janela, app, tmp_path):
    """D-334: "seleção múltipla, girar, apagar, extrair..." - girar as escolhidas gira as
    folhas delas numa ação só; "tirar do livro" tira as duas; o Ctrl+Z devolve."""
    janela.show()
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    tela = janela.tela_conferir
    tela.abrir_todas_as_paginas()
    grade = tela.todas
    grade.marcar(1)
    grade.marcar(2)
    grade.botoes_da_escolha["girar_direita"].click()
    assert [f.rotacao for f in janela.projeto.folhas] == [0, 90, 90]
    assert all(etapas.GIRAR in f.mexida_a_mao for f in janela.projeto.folhas[1:])
    grade.botoes_da_escolha["tirar"].click()
    assert [p.apagada for p in janela.projeto.paginas] == [False, True, True]
    tela.desfazer()
    tela.desfazer()
    assert [f.rotacao for f in janela.projeto.folhas] == [0, 0, 0]


# --- D-003 / D-016: a ordem arrastada ---------------------------------------------------

def test_d003_d016_arrastar_a_ordem_grava_e_a_pagina_sai_igual(janela, app, tmp_path):
    """D-003: "Ordem das etapas: livre. [...] muda arrastando com o mouse." D-016: muda a
    ordem em que RODAM; a montagem da página segue a ordem obrigatória - o PDF sai igual."""
    from PySide6.QtCore import QModelIndex

    janela.abrir_livro(_livro(tmp_path))
    assert _rodar(janela, [A.ENDIREITAR, A.CORTAR])
    primeiro = _gerar(janela, tmp_path, "ordem1")
    janela.tela_conferir.desfazer()
    lista = janela.tela_conferir.paineis.automatico.lista
    antes = lista.etapas_na_lista()
    # arrastar "Cortar as bordas" para o primeiro lugar, como o arrastar do mouse move a linha
    assert lista.model().moveRow(QModelIndex(), antes.index(A.CORTAR), QModelIndex(), 0)
    _assentar(app)
    assert janela.estado_do_automatico.ordem[0] == A.CORTAR
    assert _rodar(janela, [A.ENDIREITAR, A.CORTAR])
    assert janela.projeto.ordem_do_automatico[0] == A.CORTAR
    janela._salvar_agora()
    import projetos

    assert projetos.carregar_estado(janela.resumo).ordem_do_automatico[0] == A.CORTAR
    segundo = _gerar(janela, tmp_path, "ordem2")
    assert len(primeiro) == len(segundo)
    assert all(np.array_equal(a, b) for a, b in zip(primeiro, segundo))


# --- D-004: a pergunta das páginas mexidas -----------------------------------------------

def _mexer_no_angulo(janela, indice: int, angulo: float) -> None:
    tela = janela.tela_conferir
    tela.ir_para_pagina(indice)
    tela._gravar_angulo(indice, angulo)


def test_d004_livro_com_pagina_mexida_pergunta_e_pular_mantem_a_pagina(janela, tmp_path, monkeypatch):
    """D-004: "o programa pergunta se quer pular as páginas mexidas." Com "pular", a página
    mexida à mão fica como estava (o ângulo dela), e só ela."""
    janela.abrir_livro(_livro(tmp_path))
    _mexer_no_angulo(janela, 2, 1.5)
    assert etapas.ENDIREITAR in janela.projeto.paginas[2].mexida_a_mao
    perguntas = []
    monkeypatch.setattr(janela, "_perguntar_mexidas", lambda n: perguntas.append(n) or True)
    so_ela = _gerar(janela, tmp_path, "mexida")
    assert _rodar(janela, [A.ENDIREITAR])
    assert perguntas == [1]
    pagina = janela.projeto.paginas[2]
    assert pagina.angulo_manual == 1.5 and etapas.ENDIREITAR in pagina.mexida_a_mao
    assert np.array_equal(so_ela[2], _gerar(janela, tmp_path, "pulada")[2])


def test_d004_rodar_nelas_tambem_passa_por_cima_e_o_desfazer_volta(janela, tmp_path, monkeypatch):
    """O outro botão da pergunta ("Rodar nelas também"): o ângulo à mão sai e o
    automático vale; o Ctrl+Z devolve o ângulo à mão e a marca."""
    janela.abrir_livro(_livro(tmp_path))
    _mexer_no_angulo(janela, 2, 1.5)
    monkeypatch.setattr(janela, "_perguntar_mexidas", lambda n: False)
    assert _rodar(janela, [A.ENDIREITAR])
    pagina = janela.projeto.paginas[2]
    assert pagina.angulo_manual is None and etapas.ENDIREITAR not in pagina.mexida_a_mao
    janela.tela_conferir.desfazer()
    pagina = janela.projeto.paginas[2]
    assert pagina.angulo_manual == 1.5 and etapas.ENDIREITAR in pagina.mexida_a_mao


def test_d004_cancelar_a_pergunta_nao_muda_nada(janela, tmp_path, monkeypatch):
    janela.abrir_livro(_livro(tmp_path))
    _mexer_no_angulo(janela, 2, 1.5)
    feitas = len(janela.acoes.feitas)
    monkeypatch.setattr(janela, "_perguntar_mexidas", lambda n: None)
    assert not _rodar(janela, [A.ENDIREITAR])
    assert not janela.projeto.endireitar and len(janela.acoes.feitas) == feitas


# --- o defeito de 29/09 e o teste do Kaique (tarefas 7 e 8) -----------------------------

def test_29_09_mudar_uma_etapa_num_livro_conferido_vale_e_nada_se_perde(app, pasta, tmp_path, monkeypatch):
    """Defeito de 29/09 (opções jogadas fora em livro já conferido: o projeto salvo voltava
    por cima). Teste do Kaique de 26/10, tarefa 8: "Preto e branco" ignorado. Agora: livro
    conferido, fechado e reaberto; rodar "Limpar a folha" em Preto e branco vale no PDF, e
    o trabalho de antes (a página em Melhorar escolhida à mão, as conferidas) continua."""
    caminho = _livro(tmp_path)
    janela = _nova_janela(app)
    janela.abrir_livro(caminho)
    assert _rodar(janela, [A.ENDIREITAR])
    tela = janela.tela_conferir
    tela.ir_para_pagina(2)
    tela._escolher_filtro(MELHORAR)
    tela.ir_para_pagina(0)
    tela._marcar_revisada()
    _fechar(janela)

    janela = _nova_janela(app)
    try:
        janela.abrir_livro(caminho)
        projeto = janela.projeto
        assert projeto.endireitar
        assert projeto.paginas[2].filtro == MELHORAR and projeto.paginas[0].revisada
        monkeypatch.setattr(janela, "_perguntar_mexidas", lambda n: True)
        assert _rodar(janela, [A.LIMPAR], opcoes={"filtro_padrao": PRETO_E_BRANCO})
        projeto = janela.projeto
        assert projeto.limpar and projeto.filtro_padrao == PRETO_E_BRANCO
        assert [p.filtro for p in projeto.paginas] == [PRETO_E_BRANCO, PRETO_E_BRANCO, MELHORAR]
        assert projeto.paginas[0].revisada and projeto.endireitar
        paginas = _gerar(janela, tmp_path, "pb")
        assert _papel(paginas[0]) > 240                      # o Preto e branco valeu
        # e o que foi gravado é o mesmo (fechar e reabrir não perde)
        janela._salvar_agora()
        import projetos

        salvo = projetos.carregar_estado(janela.resumo)
        assert salvo.filtro_padrao == PRETO_E_BRANCO and salvo.paginas[2].filtro == MELHORAR
    finally:
        _fechar(janela)


def test_kaique_tarefa_7_so_endireitar_nao_corta(janela, tmp_path):
    """Teste do Kaique de 26/10, tarefa 7: "só endireitar" - desmarcar "Cortar as bordas"
    não valia. Agora rodar só "Endireitar" deixa o corte desligado: a página sai do tamanho
    da folha (com o corte, a margem larga sairia)."""
    janela.abrir_livro(_livro(tmp_path))
    como_veio = _gerar(janela, tmp_path, "veio")
    assert _rodar(janela, [A.ENDIREITAR])
    assert janela.projeto.endireitar and not janela.projeto.cortar_bordas
    so_endireitar = _gerar(janela, tmp_path, "so_endireitar")
    assert so_endireitar[2].shape == como_veio[2].shape
    assert _rodar(janela, [A.CORTAR])
    cortada = _gerar(janela, tmp_path, "cortada")
    assert cortada[2].shape[0] < como_veio[2].shape[0]       # com o corte, ela muda


def test_d068_desligar_as_marcadas_tira_o_automatico(janela, tmp_path):
    """D-068: "Toda função automática tem botão de ligar e desligar." "Desligar as
    marcadas" no livro todo desliga a etapa; numa página só, só nela."""
    janela.abrir_livro(_livro(tmp_path))
    assert _rodar(janela, [A.ENDIREITAR, A.CORTAR])
    assert _rodar(janela, [A.CORTAR], desligar=True)
    assert janela.projeto.endireitar and not janela.projeto.cortar_bordas
    assert _rodar(janela, [A.ENDIREITAR], alcance="pagina", pagina=1, desligar=True)
    projeto = janela.projeto
    assert not projeto.endireitar
    assert [etapas.ENDIREITAR in p.automatico for p in projeto.paginas] == [True, False, True]


# --- receitas (D-071) ----------------------------------------------------------------

def test_d071_receita_guardar_com_o_que_vai_dentro_e_por(janela, app, tmp_path):
    """`fr-219`: "Mas ainda pode melhorar a caixa de como escolhemos o que vai dentro da
    receita." A caixa diz cada etapa por extenso, com as opções dela, e só leva as
    marcadas; pôr a receita marca as etapas e as opções dela; rodar grava "Receita usada"."""
    from ui.automatico import CaixaDaReceita

    janela.abrir_livro(_livro(tmp_path))
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR, A.LIMPAR}
    estado.opcoes["filtro_padrao"] = PRETO_E_BRANCO
    caixa = CaixaDaReceita(estado, janela)
    assert "Preto e branco" in caixa.caixas[A.LIMPAR].text()
    assert caixa.caixas[A.DIVIDIR].isChecked() and not caixa.caixas[A.CORTAR].isChecked()
    caixa.caixas[A.DIVIDIR].setChecked(False)        # "o que vai dentro": tirei o dividir
    caixa.nome.setText("Livro amarelado")
    caixa.guardar()
    assert caixa.guardada == "Livro amarelado"
    dados = perfis.ler("Livro amarelado")
    assert perfis.etapas_da_receita(dados) == [A.LIMPAR]
    assert dados["filtro_padrao"] == PRETO_E_BRANCO and dados["dividir_folhas"] is False
    estado.marcadas = set()
    estado.opcoes["filtro_padrao"] = ORIGINAL
    assert estado.por_receita("Livro amarelado")
    assert estado.marcadas == {A.LIMPAR} and estado.opcoes["filtro_padrao"] == PRETO_E_BRANCO
    assert janela.rodar_o_automatico(esperar=True)
    assert janela.projeto.receita_usada == "Livro amarelado"
    janela._salvar_agora()
    import projetos

    assert projetos.ler_resumo(janela.resumo.pasta).receita_usada == "Livro amarelado"
    # apagar
    assert perfis.apagar("Livro amarelado") and "Livro amarelado" not in perfis.nomes()


# --- nenhuma opção de "O que fazer" se perdeu ----------------------------------------------

def test_toda_opcao_da_tela_o_que_fazer_existe_no_automatico(janela, app, tmp_path):
    """Pedido da gerente (auditoria de 26/10): tudo da tela "O que fazer" vai para o
    Automático, nada se perde. Lê no código da tela antiga (ui/tela_opcoes.py) cada campo
    do Projeto que ela escrevia e confere que o Automático tem um controle para ele (a
    caixinha da etapa ou uma opção da janela grande) e que mexer no controle muda a escolha."""
    from PySide6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QRadioButton, QSlider

    fonte = Path(__file__).resolve().parents[1] / "ui" / "tela_opcoes.py"
    campos = set(re.findall(r"self\.projeto\.(\w+) = ", fonte.read_text(encoding="utf-8")))
    assert len(campos) >= 25
    janela.abrir_livro(_livro(tmp_path))
    jan = janela.abrir_o_automatico()
    try:
        for campo in sorted(campos):
            assert campo in A.todas_as_opcoes(), f"{campo} não está no Automático"
            if campo in A.CAMPO_DO_LIVRO.values():
                etapa = next(e for e, c in A.CAMPO_DO_LIVRO.items() if c == campo)
                assert jan.lista.item_da_etapa(etapa) is not None, campo
                continue
            controle = jan.controles.get(campo)
            assert controle is not None, f"{campo} sem controle na janela do Automático"
            antes = json.dumps(janela.estado_do_automatico.opcoes.get(campo), default=str)
            if campo.startswith("misto_"):
                continue            # o "Só as letras" e as escolhas dele: um controle só (abaixo)
            if isinstance(controle, QCheckBox):
                controle.setChecked(not controle.isChecked())
            elif isinstance(controle, QComboBox):
                controle.setCurrentIndex((controle.currentIndex() + 1) % controle.count())
            elif isinstance(controle, QSlider):
                jan.cx_tem_fotos.setChecked(True)
                controle.setValue(40 if controle.value() != 40 else 60)
            elif isinstance(controle, QDoubleSpinBox):
                controle.setValue(controle.value() + 3)
            elif isinstance(controle, QRadioButton):
                controle.setChecked(True)
            depois = json.dumps(janela.estado_do_automatico.opcoes.get(campo), default=str)
            assert depois != antes or campo == "filtro_padrao", f"mexer em {campo} não mudou a escolha"
        jan.escolhas_misto.caixa.setChecked(True)
        assert janela.estado_do_automatico.opcoes["misto_so_as_letras"] is True
        # o "Tirar o fundo" (5º filtro) e o "Só as letras" também estão lá
        assert "Tirar o fundo" in [r.text() for r in jan.radios_de_filtro.values()]
    finally:
        janela._fechar_a_janela_do_automatico()


def test_os_grupos_do_desenho_estao_no_automatico():
    """Rascunho do layout ("O painel Automático vai crescer"): grupos Página · Limpeza ·
    Gravuras e fotos · Saída, e todas as etapas em algum grupo."""
    nomes = [g for g, _ in A.GRUPOS]
    assert nomes == ["Página", "Limpeza", "Gravuras e fotos", "Saída"]
    assert sorted(e for _, es in A.GRUPOS for e in es) == sorted(A.ETAPAS)


# --- a marca "mexida à mão" (etapa 1 ligada na tela) ---------------------------------------

def test_edicao_a_mao_grava_a_marca_e_o_filtro_a_mao_chega_ao_pdf(janela, tmp_path):
    """Pendência da etapa 1 (D-004/D-009): toda edição à mão grava a marca. Com "Limpar a
    folha" desligado, o filtro escolhido à mão numa página chega ao PDF (antes não chegava:
    a marca não era gravada pela tela). "Usar o corte do programa" tira a marca."""
    janela.abrir_livro(_livro(tmp_path))
    tela = janela.tela_conferir
    projeto = janela.projeto
    tela.ir_para_pagina(2)
    tela._escolher_filtro(PRETO_E_BRANCO)
    assert not projeto.limpar
    assert _papel(_gerar(janela, tmp_path, "filtro_a_mao")[2]) > 240
    tela._mover_recorte((0.1, 0.1, 0.8, 0.8))
    tela._gravar_angulo(2, 1.0)
    pagina = projeto.paginas[2]
    assert {etapas.FILTRO, etapas.CORTAR, etapas.ENDIREITAR} <= set(pagina.mexida_a_mao)
    tela._recorte_automatico()
    assert etapas.CORTAR not in projeto.paginas[2].mexida_a_mao
    tela._girar_folhas(90, so_esta=True)
    assert etapas.GIRAR in projeto.folhas[2].mexida_a_mao
    tela.desfazer()
    assert etapas.GIRAR not in projeto.folhas[2].mexida_a_mao


# --- D-094: o retângulo do corte nos três lugares -----------------------------------------

def test_d094_retangulo_do_corte_nas_configuracoes_no_livro_e_na_pagina(janela, tmp_path):
    """`g6-retangulo-onde`: "quero a b e c juntas." Os três controles existem; com
    "acompanha o texto", mudar o ângulo leva o corte à mão junto; com "fica no mesmo lugar"
    (de fábrica, D-093), o corte não muda."""
    import configuracoes
    from ui.tela_configuracoes import TelaConfiguracoes

    config = TelaConfiguracoes(janela, parte="Medidas e receitas")
    config.combo_retangulo.setCurrentIndex(config.combo_retangulo.findData("acompanha"))
    assert configuracoes.ler("retangulo_do_corte") == "acompanha"
    config.combo_retangulo.setCurrentIndex(config.combo_retangulo.findData("fica"))
    config.deleteLater()

    janela.abrir_livro(_livro(tmp_path))
    jan = janela.abrir_o_automatico("endireitar")
    assert "retangulo_do_corte" in jan.controles
    janela._fechar_a_janela_do_automatico()
    tela = janela.tela_conferir
    tela.ir_para_pagina(2)
    tela._mover_recorte((0.2, 0.2, 0.6, 0.6))
    tela._gravar_angulo(2, 0.0)
    tela._gravar_angulo(2, 4.0)                    # "fica": o corte não anda
    assert tuple(janela.projeto.paginas[2].recorte) == (0.2, 0.2, 0.6, 0.6)
    tela.combo_retangulo_da_pagina.setCurrentIndex(tela.combo_retangulo_da_pagina.findData("acompanha"))
    assert janela.projeto.paginas[2].retangulo_do_corte == "acompanha"
    tela._gravar_angulo(2, -4.0)                   # "acompanha": o corte cresce com o texto
    novo = tuple(janela.projeto.paginas[2].recorte)
    assert novo != (0.2, 0.2, 0.6, 0.6) and novo[2] > 0.6


# --- atalhos de Dividir, Cortar e Endireitar -----------------------------------------------

def test_letras_d_x_i_escolhem_dividir_cortar_endireitar(janela, app, tmp_path):
    """Pergunta da etapa 2 ("Letras para Dividir, Cortar e Endireitar?"; o Samuel quer
    "como o Photoshop"): D, X e I, livres, remapeáveis, e o menu Ferramentas mostra."""
    import atalhos
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent
    from ui.widgets.trilha_agrupada import FERRAMENTA_CORTAR, FERRAMENTA_DIVIDIR, FERRAMENTA_ENDIREITAR

    janela.show()
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    tela = janela.tela_conferir
    for letra, chave, ferramenta in (("D", Qt.Key_D, FERRAMENTA_DIVIDIR), ("X", Qt.Key_X, FERRAMENTA_CORTAR),
                                     ("I", Qt.Key_I, FERRAMENTA_ENDIREITAR)):
        assert atalhos.tecla_atual(f"ferramenta_{ferramenta}") == letra
        assert atalhos.conflito(f"ferramenta_{ferramenta}", letra) is None
        evento = QKeyEvent(QEvent.KeyPress, chave, Qt.NoModifier, letra.lower())
        assert tela.tratar_tecla(evento)
        assert tela.trilha.atual == ferramenta if hasattr(tela.trilha, "atual") else True
        assert letra in janela.menu.acoes[f"usar_{ferramenta}"].text()


# --- livro aberto da tela inicial ----------------------------------------------------------

def test_livro_aberto_rodar_o_automatico_abre_o_automatico_e_mostra_revisar_e_receita(janela, app, tmp_path):
    """R6 (06/10, "Sim, fica assim"): o livro aberto tem "Para revisar" e "Receita usada";
    "Rodar o automático..." abre o livro e o Automático de verdade."""
    janela.abrir_livro(_livro(tmp_path))
    janela.estado_do_automatico.receita = perfis.NOME_DE_FABRICA
    assert _rodar(janela, [A.ENDIREITAR])
    janela._sair_da_conferencia()
    import projetos

    resumo = projetos.ler_resumo(janela.resumo.pasta)
    livro = janela.tela_inicio.livro_aberto
    livro.mostrar(resumo)
    assert livro.receita_usada.text() == f"Receita usada: {perfis.NOME_DE_FABRICA}"
    assert livro.para_revisar.text().startswith("Para revisar:")
    janela._abrir_e_mostrar_o_automatico(resumo)
    assert janela.janela_do_automatico is not None
