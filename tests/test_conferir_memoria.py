"""Testes do script que confere a memória do projeto (memoria/conferir_memoria.py).

O script foi pedido pela gerente em 19/10/2026 junto com a memória por assunto
(CLAUDE.md §4.9). Estes testes montam uma memória e um plano de mentira numa
pasta temporária e conferem as três coisas que ele procura: links quebrados,
entradas do Registro de mudanças sem ficha e perguntas abertas que o Registro
já dá como respondidas. Não abrem janela, não leem o acervo e rodam em menos de
um segundo.

Seguro mudar: os textos de mentira. Arriscado: trocar o formato do Registro de
mentira sem trocar o do plano de verdade (os testes deixariam de provar que o
script lê o plano real).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "memoria" / "conferir_memoria.py"


@pytest.fixture(scope="module")
def cm():
    spec = importlib.util.spec_from_file_location("conferir_memoria", _SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    # As dataclasses do script procuram o módulo em sys.modules.
    sys.modules[spec.name] = modulo
    try:
        spec.loader.exec_module(modulo)
        yield modulo
    finally:
        sys.modules.pop(spec.name, None)


PLANO = """# Plano

## 6. Lista de espera

| 01/01/2026 | ideia | x | y |

## 7. Registro de mudanças

| Data | O que mudou | Por quê | Aprovado por |
|---|---|---|---|
| 13/10/2026 | **Item 2.13**: busca de página na DLL | x | Samuel |
| 14/10/2026 | Página de escolhas: `g10-papel-ou-pagina` decidida pela explicação | x | Samuel |
| 19/10/2026 | `g7-borda-ate-onde` e `g9-folha` continuam sem resposta | x | Samuel |
| 20/10/2026 | Conferência 6.7: corte de bordas errado; teste com 1.600 MB e ScanTailor v1.2.1 | x | Samuel |
| 21/10/2026 | "Para revisar": rodada 6 | x | Samuel |
"""


def _montar(tmp_path: Path, fichas: dict[str, str], perguntas: str = "") -> Path:
    (tmp_path / "docs" / "plano").mkdir(parents=True)
    (tmp_path / "docs" / "plano" / "PLANO-DEFINITIVO.md").write_text(PLANO, encoding="utf-8")
    memoria = tmp_path / "memoria"
    (memoria / "itens").mkdir(parents=True)
    (memoria / "geral").mkdir()
    for nome, texto in fichas.items():
        destino = memoria / nome
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
    (memoria / "geral" / "perguntas-abertas.md").write_text(perguntas, encoding="utf-8")
    return tmp_path


def test_acha_link_quebrado_e_aceita_os_bons(cm, tmp_path):
    raiz = _montar(
        tmp_path,
        {
            "INDICE.md": (
                "[bom](itens/2.13.md) [pasta](itens/) [fora](https://claude.ai/x) [ancora](#topo)\n"
                "[com espaco](../docs/plano/PLANO-DEFINITIVO.md#registro)\n"
                "linha 3 com [quebrado](itens/9.9.md)\n"
                "`[entre crases](nao/existe.md)` nao conta\n"
            ),
            "itens/2.13.md": "13/10/2026",
        },
    )
    quebrados = cm.links_quebrados(raiz / "memoria")
    assert [(q.linha, q.alvo) for q in quebrados] == [(3, "itens/9.9.md")]


def test_link_com_espaco_codificado_e_angulos(cm, tmp_path):
    raiz = _montar(tmp_path, {"INDICE.md": "[a](<../docs/plano/PLANO-DEFINITIVO.md>)\n"})
    (raiz / "historico").mkdir()
    (raiz / "historico" / "resumo para o Claude.md").write_text("x", encoding="utf-8")
    indice = raiz / "memoria" / "INDICE.md"
    indice.write_text(
        indice.read_text(encoding="utf-8")
        + "[h](../historico/resumo%20para%20o%20Claude.md)\n[q](../historico/nao%20existe.md)\n",
        encoding="utf-8",
    )
    quebrados = cm.links_quebrados(raiz / "memoria")
    assert [q.alvo for q in quebrados] == ["../historico/nao%20existe.md"]


def test_le_so_as_linhas_do_registro(cm, tmp_path):
    raiz = _montar(tmp_path, {})
    entradas = cm.ler_registro(raiz / "docs" / "plano" / "PLANO-DEFINITIVO.md")
    assert [e.data for e in entradas] == [
        "13/10/2026",
        "14/10/2026",
        "19/10/2026",
        "20/10/2026",
        "21/10/2026",
    ]


def test_itens_da_entrada_ignora_milhar_versao_e_nome_de_conferencia(cm):
    texto = "Conferência 6.7: corte; 1.600 MB; ScanTailor v1.2.1; contrato 0.2.69; vc 14.44; item 2.13 e 1.5"
    assert cm.itens_da_entrada(texto) == {"2.13", "1.5"}


def test_itens_da_entrada_por_palavra(cm):
    assert "para-revisar" in cm.itens_da_entrada('"Para revisar": rodada 6')
    assert "2.2" in cm.itens_da_entrada("G6, endireitar antes de cortar")


def test_entrada_sem_ficha_e_com_ficha(cm, tmp_path):
    raiz = _montar(
        tmp_path,
        {
            "itens/2.13.md": "De onde veio: Registro 13/10/2026.",
            "itens/para-revisar.md": "Rodada 6 em 21/10.",
            "LINHA-DO-TEMPO.md": "| 14/10/2026 | ... |\n| 19/10/2026 | ... |",
        },
    )
    entradas = cm.ler_registro(raiz / "docs" / "plano" / "PLANO-DEFINITIVO.md")
    faltando = cm.entradas_sem_ficha(raiz / "memoria", entradas)
    # 13/10 tem ficha (2.13), 21/10 tem (para-revisar com "21/10"), 14 e 19/10 não falam de
    # item e estão na linha do tempo; 20/10 fala de "corte de bordas" sem item e de nenhuma
    # ficha: nenhum arquivo cita 20/10.
    assert [e.data for e, _ in faltando] == ["20/10/2026"]


def test_data_parecida_nao_conta(cm):
    assert cm._cita_a_data("dia 13/10", "13/10/2026")
    assert not cm._cita_a_data("dia 113/10", "13/10/2026")
    assert not cm._cita_a_data("dia 13/101", "13/10/2026")


def test_pergunta_aberta_ja_respondida(cm, tmp_path):
    perguntas = (
        "# Perguntas\n"
        "- `g10-papel-ou-pagina` — papel ou página?\n"
        "- `g7-borda-ate-onde` — até onde vai o corte?\n"
        "- `nunca-citada` — outra\n"
        "texto solto com `g9-folha` fora de lista\n"
    )
    raiz = _montar(tmp_path, {}, perguntas)
    entradas = cm.ler_registro(raiz / "docs" / "plano" / "PLANO-DEFINITIVO.md")
    respondidas = cm.perguntas_ja_respondidas(
        raiz / "memoria" / "geral" / "perguntas-abertas.md", entradas
    )
    assert [r.nome for r in respondidas] == ["g10-papel-ou-pagina"]
    assert respondidas[0].data == "14/10/2026"


def test_conferir_inteiro_e_codigo_de_saida(cm, tmp_path, capsys):
    raiz = _montar(
        tmp_path,
        {
            "itens/2.13.md": "13/10/2026",
            "itens/para-revisar.md": "21/10/2026",
            "LINHA-DO-TEMPO.md": "14/10/2026 19/10/2026 20/10/2026",
        },
        "- `g7-borda-ate-onde` — aberta\n",
    )
    relatorio, problemas = cm.conferir(raiz)
    assert problemas == 0, relatorio
    assert cm.main(["--raiz", str(raiz)]) == 0
    assert "Tudo certo." in capsys.readouterr().out

    (raiz / "memoria" / "INDICE.md").write_text("[x](nao-existe.md)", encoding="utf-8")
    assert cm.main(["--raiz", str(raiz)]) == 1


def test_plano_sem_registro_e_avisado(cm, tmp_path):
    raiz = _montar(tmp_path, {})
    (raiz / "docs" / "plano" / "PLANO-DEFINITIVO.md").write_text("# nada\n", encoding="utf-8")
    relatorio, problemas = cm.conferir(raiz)
    assert problemas >= 1
    assert "nenhuma linha do Registro" in relatorio


def test_o_plano_de_verdade_tem_registro_legivel(cm):
    """O script lê o PLANO-DEFINITIVO real (formato da seção 7 não mudou)."""
    plano = Path(__file__).resolve().parents[1] / "docs" / "plano" / "PLANO-DEFINITIVO.md"
    entradas = cm.ler_registro(plano)
    assert len(entradas) > 100
    assert entradas[0].data == "24/09/2026"
