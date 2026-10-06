"""Antes de trocar o arquivo, o que foi escrito e forcado ate o disco (O2
do verificador-2, 06/10/2026).

O risco: o projeto.json (e o resumo.json) e gravado num arquivo ao lado
(".novo") e depois trocado. Sem forcar a gravacao no disco antes da troca
(os.fsync), uma queda de energia ou um disco USB puxado logo depois pode
deixar a TROCA registrada e o CONTEUDO do arquivo novo ainda na memoria do
Windows: o projeto.json fica vazio ou com lixo. Matar o programa nao mostra
isso (o Windows termina de gravar o que ja recebeu), e queda de energia nao
da para testar aqui - entao o que se cobra (teste de maquina) e a ORDEM:
escrever, forcar (fsync) e so depois trocar, em todos os lugares que trocam
o projeto.json ou o resumo.json; e as copias de seguranca, que tem de estar
no disco antes de o projeto.json de antes ser trocado.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import projetos
from modelos import ConfigFolha, ConfigPagina, Projeto


def _nome_do_fd(fd: int) -> str:
    """O nome do arquivo aberto com este numero (fd), perguntado ao sistema."""
    if os.name == "nt":
        import ctypes
        import msvcrt

        buf = ctypes.create_unicode_buffer(1024)
        n = ctypes.windll.kernel32.GetFinalPathNameByHandleW(
            ctypes.c_void_p(msvcrt.get_osfhandle(fd)), buf, 1024, 0)
        return Path(buf.value[:n]).name if n else "?"
    return Path(os.readlink(f"/proc/self/fd/{fd}")).name


@pytest.fixture
def eventos(monkeypatch):
    """Anota, na ordem, cada fsync (com o nome do arquivo) e cada troca."""
    lista: list[tuple[str, str]] = []
    fsync, replace = os.fsync, os.replace

    def anotar_fsync(fd):
        lista.append(("fsync", _nome_do_fd(fd)))
        fsync(fd)

    def anotar_troca(origem, destino):
        lista.append(("troca", Path(origem).name))
        replace(origem, destino)

    monkeypatch.setattr(projetos.os, "fsync", anotar_fsync)
    monkeypatch.setattr(projetos.os, "replace", anotar_troca)
    return lista


def _forcado_antes_de_trocar(eventos, nome_novo: str) -> None:
    trocas = [i for i, (o, n) in enumerate(eventos) if o == "troca" and n == nome_novo]
    assert trocas, f"{nome_novo} nao foi trocado: {eventos}"
    for i in trocas:
        assert ("fsync", nome_novo) in eventos[:i], \
            f"{nome_novo} foi trocado sem ser forcado ao disco antes: {eventos}"


def _projeto(n=3) -> Projeto:
    projeto = Projeto(caminho_entrada="x.pdf", nome="livro")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(n)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(n)]
    return projeto


def _resumo(tmp_path) -> projetos.Resumo:
    pasta = tmp_path / "projeto"
    pasta.mkdir()
    return projetos.Resumo(pasta=str(pasta), nome="livro", caminho_entrada="x.pdf")


def test_projeto_json_e_forcado_ao_disco_antes_da_troca(tmp_path, eventos):
    resumo = _resumo(tmp_path)
    projetos.salvar_estado(resumo, _projeto())
    _forcado_antes_de_trocar(eventos, "projeto.json.novo")


def test_por_tras_tambem(tmp_path, eventos):
    resumo = _resumo(tmp_path)
    projetos.salvar_estado_por_tras(resumo, _projeto())
    projetos.atualizar(resumo, _projeto(), pagina_atual=1, por_tras=True)
    assert projetos.esperar_gravacoes(30)
    _forcado_antes_de_trocar(eventos, "projeto.json.novo")
    _forcado_antes_de_trocar(eventos, "resumo.json.novo")


def test_resumo_json_e_forcado_ao_disco_antes_da_troca(tmp_path, eventos):
    resumo = _resumo(tmp_path)
    projetos.gravar_resumo(resumo)
    _forcado_antes_de_trocar(eventos, "resumo.json.novo")


def test_anotar_no_estado_tambem(tmp_path, eventos):
    resumo = _resumo(tmp_path)
    projetos.salvar_estado(resumo, _projeto())
    eventos.clear()
    assert projetos.anotar_no_estado(resumo, perguntou_fundo=True)
    _forcado_antes_de_trocar(eventos, "projeto.json.novo")


def test_a_copia_das_zonas_esta_no_disco_antes_de_o_projeto_ser_trocado(tmp_path, eventos):
    """A copia de seguranca do projeto.json antigo (decisao D2) tem de estar
    no disco antes de o projeto.json de antes ser trocado pelo novo."""
    resumo = _resumo(tmp_path)
    antigo = _projeto().para_dicionario()
    for pagina in antigo["paginas"]:
        pagina.pop("geometria_das_zonas", None)
        pagina.pop("zonas_na_folha", None)
        pagina["selecao"] = [{"tipo": "gravura", "forma": "retangulo",
                              "pontos": [[0.1, 0.1], [0.5, 0.5]]}]
    (Path(resumo.pasta) / projetos.ARQUIVO_ESTADO).write_text(
        json.dumps(antigo), encoding="utf-8")
    projetos._JA_NO_FORMATO_NOVO.clear()
    projetos.salvar_estado(resumo, _projeto())
    copias = [n for o, n in eventos if o == "fsync" and n.startswith("projeto.antigo-")]
    assert copias, f"a copia nao foi forcada ao disco: {eventos}"
    primeira_troca = next(i for i, (o, n) in enumerate(eventos)
                          if o == "troca" and n == "projeto.json.novo")
    assert ("fsync", copias[0]) in eventos[:primeira_troca]
