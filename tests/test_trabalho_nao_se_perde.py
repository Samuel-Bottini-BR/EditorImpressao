"""O trabalho salvo nunca se perde de vez.

Bug GRAVE achado pelo implementador em 29/09/2026 (Lista de bugs; decisao da
gerente, commit 2856987): livro que mudou de pasta (ou copia do mesmo PDF em
outra pasta) perdia o trabalho de vez. O projeto era achado pela assinatura
do arquivo, mas `projetos.combina_com` via o caminho antigo e o novo como
livros diferentes; aparecia "Voce mudou as opcoes... outro numero de
paginas" (falso) e o `projeto.json` era regravado na hora, sem copia.

O que se cobra aqui (teste de maquina):

    - rede de seguranca: antes de a conferencia recomecar por cima de um
      projeto salvo, o projeto.json antigo (e o acoes.jsonl e o posicao.json)
      e guardado ao lado, com data e hora no nome, sem nunca sobrescrever
      copia anterior;
    - (os testes do livro que mudou de pasta e da mensagem vem nos commits
      seguintes, neste mesmo arquivo).

Pasta de dados propria em saida_teste\\ (LOCALAPPDATA trocado): nada e criado
na pasta de dados real do Samuel. Os ajudantes e as fixtures vem de
tests/test_mesmo_livro_outro_caminho.py.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

import projetos
from historico_acoes import ARQUIVO_ACOES, ARQUIVO_POSICAO
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401 - fixtures
    _analisar,
    _pdf,
    _trabalhar_e_fechar,
    app,
    janela,
    pasta,
)


def _copias(pasta_do_projeto: Path, prefixo: str) -> list[Path]:
    return sorted(pasta_do_projeto.glob(f"{prefixo}.antigo-*"))


# --- a copia, direto ------------------------------------------------------------------


def test_sem_projeto_salvo_nao_ha_o_que_copiar(pasta):
    resumo = projetos.Resumo(pasta=str(pasta / "vazio"))
    assert projetos.guardar_copia_do_trabalho(resumo) is None


def test_a_copia_leva_o_trabalho_e_o_historico(pasta):
    projeto = pasta / "proj"
    projeto.mkdir()
    (projeto / projetos.ARQUIVO_ESTADO).write_text('{"trabalho": 1}', encoding="utf-8")
    (projeto / ARQUIVO_ACOES).write_text('{"acao": 1}\n', encoding="utf-8")
    (projeto / ARQUIVO_POSICAO).write_text('{"aplicadas": 1}', encoding="utf-8")
    resumo = projetos.Resumo(pasta=str(projeto))

    copia = projetos.guardar_copia_do_trabalho(resumo, agora=datetime(2026, 9, 29, 19, 30))
    assert copia == projeto / "projeto.antigo-2026-09-29-1930.json"
    assert copia.read_text(encoding="utf-8") == '{"trabalho": 1}'
    assert (projeto / "acoes.antigo-2026-09-29-1930.jsonl").read_text(
        encoding="utf-8") == '{"acao": 1}\n'
    assert (projeto / "posicao.antigo-2026-09-29-1930.json").is_file()
    # nada e apagado nem mudado
    assert (projeto / projetos.ARQUIVO_ESTADO).read_text(encoding="utf-8") == '{"trabalho": 1}'
    assert (projeto / ARQUIVO_ACOES).is_file()


def test_a_copia_nunca_sobrescreve_outra(pasta):
    projeto = pasta / "proj"
    projeto.mkdir()
    resumo = projetos.Resumo(pasta=str(projeto))
    agora = datetime(2026, 9, 29, 19, 30)

    (projeto / projetos.ARQUIVO_ESTADO).write_text("primeiro", encoding="utf-8")
    primeira = projetos.guardar_copia_do_trabalho(resumo, agora=agora)
    (projeto / projetos.ARQUIVO_ESTADO).write_text("segundo", encoding="utf-8")
    segunda = projetos.guardar_copia_do_trabalho(resumo, agora=agora)   # mesmo minuto

    assert primeira != segunda
    assert primeira.read_text(encoding="utf-8") == "primeiro"
    assert segunda.read_text(encoding="utf-8") == "segundo"
    assert segunda.name == "projeto.antigo-2026-09-29-1930-2.json"


def test_so_o_que_existe_e_copiado(pasta):
    """Projeto sem acoes gravadas: so o projeto.json vai para a copia."""
    projeto = pasta / "proj"
    projeto.mkdir()
    (projeto / projetos.ARQUIVO_ESTADO).write_text("{}", encoding="utf-8")
    projetos.guardar_copia_do_trabalho(projetos.Resumo(pasta=str(projeto)))
    assert len(_copias(projeto, "projeto")) == 1
    assert not _copias(projeto, "acoes")


# --- na janela de verdade: o recomeco guarda a copia -------------------------------------


def _estado(janela) -> Path:
    return Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO


def test_recomecar_a_conferencia_guarda_o_trabalho_antigo(janela, pasta):
    """O trabalho salvo nao serve (aqui: uma pagina a menos, como quando se
    muda "Dividir folhas ao meio"); a conferencia recomeca, e o trabalho
    antigo fica guardado ao lado, igualzinho."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = _estado(janela)
    dados = json.loads(estado.read_text(encoding="utf-8"))
    dados["paginas"] = dados["paginas"][:3]
    estado.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    antes = estado.read_bytes()
    acoes_antes = (estado.parent / ARQUIVO_ACOES).read_bytes()

    janela.abrir_livro(str(livro))
    _analisar(janela)

    assert janela.avisos, "recomecou sem avisar"
    copias = _copias(estado.parent, "projeto")
    assert len(copias) == 1, "o trabalho antigo nao foi guardado"
    assert copias[0].read_bytes() == antes
    assert _copias(estado.parent, "acoes")[0].read_bytes() == acoes_antes
    # o projeto.json agora e o da conferencia nova (4 paginas)
    assert len(json.loads(estado.read_text(encoding="utf-8"))["paginas"]) == 4


def test_projeto_ilegivel_tambem_e_guardado_antes_de_ser_regravado(janela, pasta):
    """Um projeto.json que nao da para ler e regravado ao abrir: o que estava
    la fica guardado (pode ser recuperado a mao)."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = _estado(janela)
    estado.write_text("{ isto nao e json", encoding="utf-8")

    janela.abrir_livro(str(livro))
    _analisar(janela)

    copias = _copias(estado.parent, "projeto")
    assert len(copias) == 1
    assert copias[0].read_text(encoding="utf-8") == "{ isto nao e json"


def test_abrir_o_mesmo_livro_sem_mudar_nada_nao_faz_copia(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _analisar(janela)
    assert not janela.avisos
    assert not _copias(Path(janela.resumo.pasta), "projeto")


def test_livro_novo_nao_faz_copia(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    _analisar(janela)
    assert not _copias(Path(janela.resumo.pasta), "projeto")
