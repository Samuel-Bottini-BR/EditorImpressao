"""O resumo.json nunca faz o projeto sumir da lista (O1 do verificador-2,
06/10/2026).

O defeito: o resumo.json (o cartao da tela inicial) era escrito direto por
cima (write_text). Se a escrita ficasse pela metade, o projeto SUMIA da
lista: projetos.listar() pulava a pasta, com o projeto.json intacto ao lado,
e abrir o mesmo PDF tambem nao o achava (achar_por_assinatura usa a lista).
Demonstrado pelo verificador numa copia, cortando o resumo.json ao meio.

O que se cobra aqui (teste de maquina):
  - o resumo.json e escrito como o projeto.json: num arquivo ao lado
    (resumo.json.novo) e so entao trocado;
  - um resumo.json estragado (pela metade, vazio, lixo) e refeito a partir
    do projeto.json: o projeto continua na lista, com o livro, o nome, o
    total de paginas e as conferidas, e abrir o mesmo PDF o acha;
  - pasta sem resumo.json nenhum continua fora da lista (e o que sobra de um
    "Tirar da lista" que nao conseguiu apagar tudo: nao pode voltar).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

import projetos  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    monkeypatch.setattr(projetos.historico, "carregar", lambda: [])
    return pasta


def _livro(tmp_path, nome="Armorial de Siebmacher") -> Path:
    caminho = tmp_path / f"{nome}.pdf"
    doc = fitz.open()
    for i in range(3):
        pagina = doc.new_page(width=300, height=400)
        pagina.insert_text((30, 50), f"{nome} {i}", fontsize=12)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _projeto_salvo(tmp_path) -> tuple[projetos.Resumo, Path]:
    livro = _livro(tmp_path)
    projeto = Projeto(caminho_entrada=str(livro), nome=livro.stem)
    projeto.folhas = [ConfigFolha(indice=i) for i in range(3)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(3)]
    projeto.paginas[0].revisada = projeto.paginas[2].revisada = True
    resumo = projetos.criar(projeto, total_paginas=3)
    projetos.salvar_estado(resumo, projeto)
    projetos.atualizar(resumo, projeto, pagina_atual=2)
    return resumo, livro


def test_o_resumo_e_escrito_ao_lado_e_trocado(raiz, tmp_path, monkeypatch):
    trocas = []
    original = os.replace

    def anotar(origem, destino):
        trocas.append((Path(origem).name, Path(destino).name))
        original(origem, destino)

    monkeypatch.setattr(projetos.os, "replace", anotar)
    resumo, _livro_ = _projeto_salvo(tmp_path)
    projetos.gravar_resumo(resumo)
    assert ("resumo.json.novo", "resumo.json") in trocas
    assert not (Path(resumo.pasta) / "resumo.json.novo").exists()


@pytest.mark.parametrize("estrago", ["metade", "vazio", "lixo"])
def test_resumo_estragado_e_refeito_e_o_projeto_continua_na_lista(raiz, tmp_path, estrago):
    resumo, livro = _projeto_salvo(tmp_path)
    arquivo = Path(resumo.pasta) / projetos.ARQUIVO_RESUMO
    bom = arquivo.read_bytes()
    arquivo.write_bytes({"metade": bom[: len(bom) // 2], "vazio": b"",
                         "lixo": b"\x00\xff\xfe nao e json"}[estrago])

    lista = projetos.listar()
    assert len(lista) == 1, "o projeto sumiu da lista"
    refeito = lista[0]
    assert Path(refeito.pasta) == Path(resumo.pasta)
    assert refeito.caminho_entrada == str(livro)
    assert refeito.nome == livro.stem
    assert refeito.total_paginas == 3 and refeito.conferidas == 2
    assert refeito.assinatura == resumo.assinatura      # o livro esta la: confere de novo
    # e fica gravado direito, para a proxima vez
    assert json.loads(arquivo.read_text(encoding="utf-8"))["caminho_entrada"] == str(livro)
    # abrir o mesmo PDF acha este projeto (e nao cria outro ao lado)
    achado = projetos.achar_por_assinatura(str(livro))
    assert achado is not None and Path(achado.pasta) == Path(resumo.pasta)


def test_resumo_estragado_com_o_livro_fora_do_lugar_continua_na_lista(raiz, tmp_path):
    """Sem o PDF no lugar nao da para refazer a assinatura: o cartao aparece
    assim mesmo (a tela inicial oferece "procurar de novo")."""
    resumo, livro = _projeto_salvo(tmp_path)
    (Path(resumo.pasta) / projetos.ARQUIVO_RESUMO).write_text("{", encoding="utf-8")
    livro.unlink()
    lista = projetos.listar()
    assert len(lista) == 1 and lista[0].caminho_entrada == str(livro)
    assert lista[0].assinatura == ""


def test_resumo_estragado_sem_projeto_json_nao_derruba(raiz, tmp_path):
    resumo, _livro_ = _projeto_salvo(tmp_path)
    (Path(resumo.pasta) / projetos.ARQUIVO_ESTADO).unlink()
    (Path(resumo.pasta) / projetos.ARQUIVO_RESUMO).write_text("{", encoding="utf-8")
    assert projetos.listar() == []


def test_pasta_sem_resumo_continua_fora_da_lista(raiz, tmp_path):
    """O que sobra de um "Tirar da lista" que nao apagou tudo nao volta."""
    resumo, _livro_ = _projeto_salvo(tmp_path)
    (Path(resumo.pasta) / projetos.ARQUIVO_RESUMO).unlink()
    assert projetos.listar() == []
