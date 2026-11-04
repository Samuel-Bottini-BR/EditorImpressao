"""Prova de comportamento da D-616 (04/11/2026): a caixinha "A 1ª folha é a capa aberta".

Samuel (print a-61: na folha 1 do caderno, a contracapa saiu na frente e a capa azul atrás, porque a
1ª folha do Gradus Primus é a capa escaneada aberta): "essa capa está no lugar certo?" · (a-62) "mas
qual seria o jeito para resolver esse problema sem ser na mão?" → proposta da gerente (caixinha "A 1ª
folha é a capa aberta" no Dividir do Automático) → "ok".
Livro de decisões: "Caixinha na etapa Dividir do Automático: "A 1ª folha é a capa aberta"
(desmarcada de fábrica; vale por livro). Marcada, ao dividir, a metade da direita da 1ª folha (a
capa) vira a página 1 e a metade da esquerda (a contracapa) vai para a última página."
Pedido da gerente: a prévia do Automático e a etapa 7 já mostram assim antes do "Rodar" (D-577,
D-603, D-614).

O que se mede: a caixinha na janela do Automático, a lista de páginas depois do "Rodar" (o que vai
para o projeto.json), o PDF de saída (core.pipeline.processar), o Ctrl+Z, a lista que a prévia e o
caderno da etapa 7 usam antes do "Rodar" (core/automatico.paginas_do_pdf_depois e os passos da
prévia, D-614), e que desmarcada nada muda (D-589).
O ANTIGO NÃO TINHA: no código de antes (a ponta da entrega 1) não há caixinha nem campo
(Projeto.capa_aberta), e a capa fica na página 2.

Livro sintético de 3 folhas de livro aberto (tests/test_decisoes_ordem_folhas._aberta: a página da
direita tem uma faixa a mais, para saber qual metade é qual). Motor de corte "o do Editor" (não
precisa da DLL do ScanTailor).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core import dividir_scantailor as ds  # noqa: E402
from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _paginas_do_pdf,
    _pdf,
    app,
    janela,
    pasta,
)
from tests.test_decisoes_ordem_folhas import _aberta, _gerar  # noqa: E402

DO_EDITOR = ds.JEITO_DO_PROJETO_ANTIGO          # "o do Editor": acha a lombada sem a DLL


def _livro(tmp_path: Path, folhas: int = 3) -> str:
    return _pdf(tmp_path / "abertas.pdf", [_aberta(n) for n in range(folhas)])


def _rodar(janela, etapas, opcoes=None) -> bool:
    """O que o Kaique faz: marca as etapas, escolhe as opções e roda (no mesmo fio)."""
    estado = janela.estado_do_automatico
    estado.marcadas = set(etapas)
    estado.opcoes.update({"dividir_como": DO_EDITOR, **(opcoes or {})})
    estado.alcance = "livro"
    return janela.rodar_o_automatico(esperar=True, perguntar=False)


def _lugares(projeto) -> list[tuple[int, str]]:
    return [(p.folha, p.metade) for p in projeto.paginas]


def _metade(img: np.ndarray) -> str:
    """"direita" se a página tem a faixa a mais da metade da direita (_aberta), senão "esquerda"."""
    cinza = img.mean(axis=2)
    linhas = np.where((cinza < 80).mean(axis=1) > 0.5)[0]
    grupos = np.split(linhas, np.where(np.diff(linhas) > 3)[0] + 1) if linhas.size else []
    return "direita" if len(grupos) >= 2 else "esquerda"


def test_d616_caixinha_desmarcada_de_fabrica_e_projeto_antigo_sem_ela(janela, tmp_path):
    """A caixinha está no Dividir da janela do Automático, com o texto do Livro, desmarcada de
    fábrica; projeto gravado antes (sem o campo) abre com ela desmarcada; e ela não vai na
    receita (vale por livro)."""
    from core import perfis
    from modelos import Projeto

    assert Projeto(caminho_entrada="").capa_aberta is False
    dados = Projeto(caminho_entrada="x.pdf").para_dicionario()
    dados.pop("capa_aberta")
    assert Projeto.de_dicionario(dados).capa_aberta is False
    assert "capa_aberta" in A.OPCOES[A.DIVIDIR] and "capa_aberta" not in perfis.CAMPOS

    janela.abrir_livro(_livro(tmp_path))
    jan = janela.abrir_o_automatico(A.DIVIDIR)
    try:
        caixa = jan.controles["capa_aberta"]
        assert caixa.text() == "A 1ª folha é a capa aberta"
        assert not caixa.isChecked()
        caixa.setChecked(True)
        assert janela.estado_do_automatico.opcoes["capa_aberta"] is True
    finally:
        janela._fechar_a_janela_do_automatico()


def test_d616_marcada_o_dividir_poe_a_capa_na_frente_e_a_contracapa_no_fim(janela, tmp_path):
    """Marcada, "Rodar" o Dividir: página 1 = a metade da direita da 1ª folha (a capa), última =
    a da esquerda (a contracapa); o PDF sai assim; a caixinha fica guardada no livro; o Ctrl+Z
    volta tudo (a ordem e a folha inteira)."""
    janela.abrir_livro(_livro(tmp_path))
    projeto = janela.projeto
    assert _rodar(janela, [A.DIVIDIR], {"capa_aberta": True})
    assert _lugares(projeto) == [(0, "direita"), (1, "esquerda"), (1, "direita"),
                                 (2, "esquerda"), (2, "direita"), (0, "esquerda")]
    assert [p.indice for p in projeto.paginas] == list(range(6))
    assert projeto.capa_aberta is True
    paginas = _gerar(janela, tmp_path, "capa")
    assert len(paginas) == 6
    assert _metade(paginas[0]) == "direita" and _metade(paginas[-1]) == "esquerda"

    janela.tela_conferir.desfazer()
    assert _lugares(projeto) == [(0, "inteira"), (1, "inteira"), (2, "inteira")]
    assert projeto.capa_aberta is False


def test_d616_desmarcada_nada_muda_de_lugar(janela, tmp_path):
    """D-589 ("se algo não está marcado, não é para fazer"): desmarcada, o Dividir deixa a ordem
    de sempre (esquerda, direita, folha por folha)."""
    janela.abrir_livro(_livro(tmp_path))
    assert _rodar(janela, [A.DIVIDIR], {"capa_aberta": False})
    assert _lugares(janela.projeto) == [(0, "esquerda"), (0, "direita"), (1, "esquerda"),
                                        (1, "direita"), (2, "esquerda"), (2, "direita")]


def test_d616_marcada_sem_o_dividir_marcado_nada_muda(janela, tmp_path):
    """Só o Dividir rodado muda a ordem: a caixinha marcada com a etapa Dividir desmarcada não
    faz nada (e não fica gravada no livro)."""
    janela.abrir_livro(_livro(tmp_path))
    assert _rodar(janela, [A.DIVIDIR])                     # divide sem a capa
    assert _rodar(janela, [A.CADERNOS], {"capa_aberta": True})
    assert _lugares(janela.projeto)[0] == (0, "esquerda")
    assert janela.projeto.capa_aberta is False


def test_d616_a_previa_e_o_caderno_mostram_a_capa_antes_de_rodar(janela, tmp_path):
    """D-603/D-614: antes do "Rodar", a lista das páginas que a prévia folheia e que o caderno da
    etapa 7 monta já tem a capa na frente e a contracapa no fim, e é a MESMA lista que o "Rodar"
    deixa. A prévia começa pela capa (o passo da metade da direita da 1ª folha)."""
    janela.abrir_livro(_livro(tmp_path))
    projeto = janela.projeto
    pedido = A.Pedido(etapas=[A.DIVIDIR], opcoes={"dividir_como": DO_EDITOR, "capa_aberta": True})
    previa = A.paginas_do_pdf_depois(projeto, pedido)
    assert [(f, m) for _o, f, m in previa] == [(0, "direita"), (1, "esquerda"), (1, "direita"),
                                               (2, "esquerda"), (2, "direita"), (0, "esquerda")]
    sem = A.paginas_do_pdf_depois(projeto, A.Pedido(etapas=[A.DIVIDIR],
                                                    opcoes={"dividir_como": DO_EDITOR}))
    assert [(f, m) for _o, f, m in sem][0] == (0, "esquerda")

    # a janela do Automático: caixinha marcada, os passos da prévia e o caderno da etapa 7
    jan = janela.abrir_o_automatico(A.DIVIDIR)
    try:
        estado = janela.estado_do_automatico
        estado.opcoes["dividir_como"] = DO_EDITOR
        estado.marcar(A.DIVIDIR, True)
        jan.controles["capa_aberta"].setChecked(True)
        passos = jan.antes_e_depois._passos()             # a prévia (D-614), folha 1 inteira
        assert passos[0] == (0, "direita") and passos[-1] == (0, "esquerda")
        folhas = jan.folhas_do_caderno                     # a etapa 7 (D-603)
        folhas.ligada = True                               # (sem desenhar: só a lista)
        lista = [(f, m) for _o, f, m in folhas._depois()]
        assert lista[0] == (0, "direita") and lista[-1] == (0, "esquerda")
        folhas.ligada = False
    finally:
        janela._fechar_a_janela_do_automatico()

    assert _rodar(janela, [A.DIVIDIR], {"capa_aberta": True})
    assert _lugares(projeto) == [(f, m) for _o, f, m in previa]


def test_d616_folha_ja_dividida_tambem_vai(janela, tmp_path):
    """Livro já dividido (como o Gradus da conferência): marcar a caixinha e rodar o Dividir de
    novo põe a capa na frente; rodar de novo não muda mais nada."""
    janela.abrir_livro(_livro(tmp_path))
    projeto = janela.projeto
    assert _rodar(janela, [A.DIVIDIR])
    assert _lugares(projeto)[:2] == [(0, "esquerda"), (0, "direita")]
    assert _rodar(janela, [A.DIVIDIR], {"capa_aberta": True})
    assert _lugares(projeto)[0] == (0, "direita") and _lugares(projeto)[-1] == (0, "esquerda")
    antes = _lugares(projeto)
    assert _rodar(janela, [A.DIVIDIR], {"capa_aberta": True})
    assert _lugares(projeto) == antes
