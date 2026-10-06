"""Trocar de livro logo depois de uma mudanca nao perde a mudanca (R-A do
verificador-2, 06/10/2026).

O defeito: com um livro na conferencia, mudar alguma coisa (o filtro de uma
pagina, por exemplo) e abrir outro livro pelo Ctrl+O menos de ~0,6 s depois
perdia a mudanca. O relogio de salvar (600 ms) ainda nao tinha disparado, e
abrir_livro so gravava o livro de antes se a conversao das zonas estivesse
rodando; quando o relogio disparava, o livro aberto ja era o outro. Medido
pelo verificador na janela real: perdeu com 0,05 s e 0,54 s; guardou com
0,63 s ou mais. Ja acontecia antes do 9a367de.

O que se cobra aqui (teste de maquina), por todos os caminhos que trocam de
livro ou voltam ao inicio:
  - "Abrir" (Ctrl+O, menu Arquivo, arrastar): abrir_livro;
  - o "continuar" do cartao da tela inicial (_continuar_projeto);
  - o "comecar de novo" do cartao de OUTRO livro (_recomecar_projeto);
  - o "Voltar" da conferencia (_sair_da_conferencia, ja gravava na hora).
E os dois cuidados do conserto:
  - "comecar de novo" no PROPRIO livro aberto joga o trabalho fora de
    verdade: gravar o livro de antes nao pode trazer o projeto.json de volta;
  - um projeto tirado da lista ("Tirar da lista") nao volta para a lista
    quando outro livro e aberto depois.

Pasta de dados propria em saida_teste\\ (fixtures de
tests/test_mesmo_livro_outro_caminho.py): nada na pasta de dados real.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402
from core.filtros import MAGICO_PRO  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    app,
    janela,
    pasta,
)


def _livro(pasta: Path, nome: str, folhas: int = 4) -> Path:
    """Um PDF pequeno de verdade; o texto leva o nome, para a assinatura dos
    dois livros ser diferente."""
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / f"{nome}.pdf"
    doc = fitz.open()
    for i in range(folhas):
        pagina = doc.new_page(width=400, height=560)
        pagina.insert_text((40, 60), f"{nome}, folha {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _abrir_e_conferir(janela, livro: Path) -> projetos.Resumo:
    janela.abrir_livro(str(livro))
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    _analisar(janela)
    return janela.resumo


def _mudar_sem_esperar_o_relogio(janela) -> None:
    """O Kaique troca o filtro da pagina 2: a tela avisa (trabalho_mudou) e o
    relogio de salvar comeca a contar 600 ms."""
    janela.projeto.paginas[1].filtro = MAGICO_PRO
    janela.tela_conferir.trabalho_mudou.emit()
    assert janela._relogio_de_salvar.isActive()


def _deixar_o_relogio_disparar(segundos: float = 1.2) -> None:
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        QApplication.processEvents()
        time.sleep(0.01)
    projetos.esperar_gravacoes(30)


def _filtro_no_disco(resumo: projetos.Resumo, pagina: int = 1) -> str:
    dados = json.loads((Path(resumo.pasta) / projetos.ARQUIVO_ESTADO)
                       .read_text(encoding="utf-8"))
    return dados["paginas"][pagina]["filtro"]


def test_abrir_outro_livro_logo_depois_de_mudar_guarda_a_mudanca(janela, pasta):
    """O caso do verificador: Ctrl+O (ou menu Arquivo > Abrir, ou arrastar)
    0,05 s depois da mudanca. Todos chegam em abrir_livro."""
    primeiro = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    _mudar_sem_esperar_o_relogio(janela)
    janela.abrir_livro(str(_livro(pasta, "Segundo")))      # antes dos 600 ms
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    # ja no disco quando abrir_livro volta, sem depender do relogio
    assert _filtro_no_disco(primeiro) == MAGICO_PRO
    _deixar_o_relogio_disparar()
    assert _filtro_no_disco(primeiro) == MAGICO_PRO
    assert janela.resumo.pasta != primeiro.pasta


def test_continuar_outro_projeto_pelo_cartao_guarda_a_mudanca(janela, pasta, monkeypatch):
    segundo = _abrir_e_conferir(janela, _livro(pasta, "Segundo"))
    primeiro = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    _mudar_sem_esperar_o_relogio(janela)
    monkeypatch.setattr(janela, "analisar", lambda: None)
    janela._continuar_projeto(projetos.ler_resumo(segundo.pasta))
    assert _filtro_no_disco(primeiro) == MAGICO_PRO
    _deixar_o_relogio_disparar()
    assert _filtro_no_disco(primeiro) == MAGICO_PRO


def test_comecar_de_novo_outro_livro_guarda_a_mudanca_do_aberto(janela, pasta):
    segundo = _abrir_e_conferir(janela, _livro(pasta, "Segundo"))
    primeiro = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    _mudar_sem_esperar_o_relogio(janela)
    janela._recomecar_projeto(projetos.ler_resumo(segundo.pasta))
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    assert _filtro_no_disco(primeiro) == MAGICO_PRO
    _deixar_o_relogio_disparar()
    assert _filtro_no_disco(primeiro) == MAGICO_PRO
    # o segundo, sim, foi limpo: nada de paginas gravadas
    estado = Path(segundo.pasta) / projetos.ARQUIVO_ESTADO
    assert not estado.exists() or not json.loads(estado.read_text(encoding="utf-8")).get("paginas")


def test_comecar_de_novo_o_proprio_livro_aberto_joga_o_trabalho_fora(janela, pasta):
    """Cuidado do conserto: gravar o livro de antes no comeco de abrir_livro
    nao pode regravar o projeto.json que o "comecar de novo" acabou de apagar."""
    primeiro = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    _mudar_sem_esperar_o_relogio(janela)
    janela._recomecar_projeto(projetos.ler_resumo(primeiro.pasta))
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    _deixar_o_relogio_disparar()
    estado = Path(primeiro.pasta) / projetos.ARQUIVO_ESTADO
    assert not estado.exists() or not json.loads(estado.read_text(encoding="utf-8")).get("paginas")
    assert janela.resumo.pasta == primeiro.pasta and not janela.trabalho_carregado


def test_voltar_logo_depois_de_mudar_guarda_a_mudanca(janela, pasta):
    primeiro = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    _mudar_sem_esperar_o_relogio(janela)
    janela._sair_da_conferencia()                           # "Voltar"
    assert _filtro_no_disco(primeiro) == MAGICO_PRO


def test_projeto_tirado_da_lista_nao_volta_ao_abrir_outro_livro(janela, pasta):
    """Cuidado do conserto: o livro de antes so e gravado se a pasta dele
    ainda existe. Abrir A, voltar ao inicio, "Tirar da lista" A e abrir B nao
    pode recriar a pasta de A (o cartao voltaria para a lista)."""
    primeiro = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    _mudar_sem_esperar_o_relogio(janela)
    janela._sair_da_conferencia()
    projetos.remover_da_lista(projetos.ler_resumo(primeiro.pasta))
    assert not Path(primeiro.pasta).exists()
    # o relogio contando (como quando a conversao das zonas termina com a
    # pessoa na tela inicial) e o pior caso: abrir_livro gravaria o de antes
    janela._marcar_para_salvar()
    janela.abrir_livro(str(_livro(pasta, "Segundo")))
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    _deixar_o_relogio_disparar()
    assert not Path(primeiro.pasta).exists()
    assert [r.nome for r in projetos.listar()] == ["Segundo"]
