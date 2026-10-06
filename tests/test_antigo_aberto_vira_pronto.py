"""PDF antigo aberto em outro programa: o novo vai para "(2)" e isso e SUCESSO.

Achado do verificador (Lista de bugs, 05/10/2026; relatorios/conferir/
so-neste-pedaco-2026-10-05/verificador/, ressalva 1): com "substituir o
antigo" e o PDF antigo aberto (no leitor de PDF, por exemplo), o programa
grava o novo como "nome (2).pdf" - certo -, mas o ErroPDFSalvoComOutroNome ia
pelo caminho de FALHA da TarefaProcessar: a tela voltava para Conferir em vez
de "Ficou pronto!", o cartao nao virava "PDF gerado", o destino guardado
ficava com o nome antigo e o erros.log ganhava o rastro tecnico.

O que se cobra (pedido da gerente, 05/10):
    - a tela "Ficou pronto!" aparece, com o nome "(2)" e uma frase em
      portugues dizendo que o antigo estava aberto noutro programa;
    - nenhuma caixa de erro;
    - o cartao do livro vira "PDF gerado", e o destino guardado (projeto e
      resumo) passa a ser o "(2)";
    - nada no erros.log;
    - o antigo fica intacto;
    - sem o antigo preso, a tela "Ficou pronto!" fica como sempre (sem frase).

Processamento DE VERDADE (TarefaProcessar em QThread); so a troca do arquivo
(os.replace) finge que o antigo esta aberto. Nada aparece na tela.
"""

from __future__ import annotations

import errno
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

import projetos  # noqa: E402
from core import pipeline  # noqa: E402
from tests.test_ja_existe_arquivo_com_esse_nome import (  # noqa: E402
    _destino_ja_escolhido,
    _escolher_na_caixa,
    _esperar_o_fim,
    _livro_conferido,
    _paginas,
    _pdf_antigo,
)
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    app,
    janela,
    pasta,
)


def _antigo_sempre_aberto(monkeypatch, antigo: Path) -> None:
    """os.replace falha para o destino `antigo`, como no Windows com o PDF
    aberto no leitor (PermissionError, "Acesso negado")."""
    de_verdade = pipeline.os.replace

    def replace(origem, destino):
        if Path(destino) == antigo:
            raise PermissionError(errno.EACCES, "Acesso negado", str(destino))
        return de_verdade(origem, destino)

    monkeypatch.setattr(pipeline.os, "replace", replace)
    monkeypatch.setattr(pipeline, "ESPERA_DA_TROCA_S", 0.0, raising=False)


def _erros_log() -> str:
    from registro import caminho_do_log

    caminho = caminho_do_log()
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


def test_antigo_aberto_mostra_ficou_pronto_com_o_2(janela, pasta, monkeypatch):
    from ui.janela_principal import FINAL

    _livro_conferido(janela, pasta)
    antigo = pasta / "saida" / "pronto.pdf"
    bytes_do_antigo = _pdf_antigo(antigo, "o antigo")
    _destino_ja_escolhido(monkeypatch, antigo)
    _escolher_na_caixa(monkeypatch, "substituir o antigo", [])
    _antigo_sempre_aberto(monkeypatch, antigo)
    log_antes = _erros_log()

    janela.processar()
    _esperar_o_fim(janela)          # reprova se voltar para Conferir com aviso

    novo = pasta / "saida" / "pronto (2).pdf"
    assert janela.telas.currentIndex() == FINAL
    assert not janela.avisos, janela.avisos            # nenhuma caixa de erro
    final = janela.tela_final
    assert final.nome.text() == "pronto (2).pdf"
    assert final.caminho == str(novo)                  # "abrir a pasta" e "imprimir" vao no (2)
    frase = final.aviso.text()
    assert not final.aviso.isHidden()
    assert "pronto.pdf" in frase and "aberto em outro programa" in frase, frase
    assert "Traceback" not in frase and "Errno" not in frase

    assert novo.exists() and _paginas(novo) == 4
    assert antigo.read_bytes() == bytes_do_antigo, "o antigo foi mexido"

    # o destino guardado e o (2): projeto, e o resumo do cartao em disco
    assert Path(janela.projeto.caminho_saida) == novo
    resumo = projetos.ler_resumo(janela.resumo.pasta)
    assert resumo is not None and resumo.pdf_gerado, "o cartao nao virou 'PDF gerado'"
    assert Path(resumo.caminho_saida) == novo

    assert _erros_log() == log_antes, "o (2) foi parar no erros.log"


def test_sem_o_antigo_preso_a_tela_pronto_fica_como_sempre(janela, pasta, monkeypatch):
    _livro_conferido(janela, pasta)
    saida = pasta / "saida" / "pronto.pdf"
    _destino_ja_escolhido(monkeypatch, saida)

    janela.processar()
    _esperar_o_fim(janela)

    final = janela.tela_final
    assert final.nome.text() == "pronto.pdf"
    assert final.aviso.isHidden() and final.aviso.text() == ""


def test_a_frase_some_no_livro_seguinte(janela, pasta, monkeypatch):
    """Antigo preso uma vez, depois um processamento normal: a frase nao
    pode ficar de sobra na tela "Ficou pronto!"."""
    _livro_conferido(janela, pasta)
    antigo = pasta / "saida" / "pronto.pdf"
    _pdf_antigo(antigo, "o antigo")
    _destino_ja_escolhido(monkeypatch, antigo)
    _escolher_na_caixa(monkeypatch, "substituir o antigo", [])
    _antigo_sempre_aberto(monkeypatch, antigo)
    janela.processar()
    _esperar_o_fim(janela)
    assert not janela.tela_final.aviso.isHidden()

    janela.tela_final.mostrar(janela.projeto, str(antigo), 4, 4)
    assert janela.tela_final.aviso.isHidden() and janela.tela_final.aviso.text() == ""


def test_a_tarefa_entrega_o_2_como_concluida(monkeypatch):
    """TarefaProcessar.run: o ErroPDFSalvoComOutroNome vira `concluida` com o
    caminho do (2) e o nome do antigo em `antigo_preso`; nao chama `falhou`
    nem grava no erros.log. (E o que o conferencia.py e o teste de velocidade
    tambem usam.)"""
    import ui.tarefas as tarefas
    from modelos import Projeto

    novo = Path("C:/livros/pronto (2).pdf")
    antigo = Path("C:/livros/pronto.pdf")

    def _processar(*_a, **_k):
        raise pipeline.ErroPDFSalvoComOutroNome("aviso", novo, antigo)

    gravados: list = []
    monkeypatch.setattr(tarefas, "processar", _processar)
    monkeypatch.setattr(tarefas, "registrar_erro", lambda *a: gravados.append(a))
    tarefa = tarefas.TarefaProcessar(Projeto(caminho_entrada="x.pdf"))
    vistos: dict = {}
    tarefa.concluida.connect(lambda c: vistos.setdefault("concluida", c))
    tarefa.falhou.connect(lambda m: vistos.setdefault("falhou", m))
    tarefa.run()
    assert vistos == {"concluida": str(novo)}
    assert tarefa.antigo_preso == "pronto.pdf"
    assert not gravados


def test_a_tarefa_normal_nao_tem_antigo_preso(monkeypatch):
    import ui.tarefas as tarefas
    from modelos import Projeto

    monkeypatch.setattr(tarefas, "processar", lambda *_a, **_k: "C:/livros/pronto.pdf")
    tarefa = tarefas.TarefaProcessar(Projeto(caminho_entrada="x.pdf"))
    tarefa.run()
    assert tarefa.antigo_preso == ""
