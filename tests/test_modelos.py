"""Testes de `modelos.py` para o campo novo `tamanho_folha_cm` (Problema 1
do plano "corrigir bugs do teste do Boécio", secao 3a).

`tamanho_folha_cm` guarda o tamanho de folha ESCOLHIDO pelo usuario (cm),
separado do `recorte` (que continua sendo so a fracao da imagem original que
vira conteudo). None quer dizer "a folha tem o tamanho do recorte", que e o
comportamento de sempre - projetos salvos antes deste campo existir precisam
continuar abrindo exatamente iguais.
"""

from __future__ import annotations

from modelos import ConfigPagina, Projeto


def test_tamanho_folha_cm_comeca_none():
    """None = "a folha e do tamanho do recorte", igual ao programa de sempre."""
    pagina = ConfigPagina(indice=0, folha=0)
    assert pagina.tamanho_folha_cm is None


def test_projeto_antigo_sem_tamanho_folha_cm_continua_abrindo():
    """Arquivo de projeto salvo antes deste campo existir nao pode quebrar."""
    dados = {
        "caminho_entrada": "x.pdf",
        "paginas": [{"indice": 0, "folha": 0}],   # sem tamanho_folha_cm
    }
    projeto = Projeto.de_dicionario(dados)
    assert projeto.paginas[0].tamanho_folha_cm is None


def test_tamanho_folha_cm_sobrevive_ao_projeto_como_tupla():
    """JSON nao tem tupla (vira lista); a volta tem que reconstituir a tupla,
    igual ja acontece com `recorte` - senao comparar `== (w, h)` depois de
    reabrir um projeto falharia. `json.dumps`/`json.loads` (o caminho real de
    gravar/reabrir, ver `projetos.py`) e o que de fato transforma a tupla em
    lista - por isso o teste passa por eles, e nao so por `para_dicionario`."""
    import json

    pagina = ConfigPagina(indice=0, folha=0, tamanho_folha_cm=(21.0, 29.7))
    projeto = Projeto(caminho_entrada="x.pdf", paginas=[pagina])

    dados = json.loads(json.dumps(projeto.para_dicionario()))
    assert dados["paginas"][0]["tamanho_folha_cm"] == [21.0, 29.7]

    volta = Projeto.de_dicionario(dados)
    assert volta.paginas[0].tamanho_folha_cm == (21.0, 29.7)
    assert isinstance(volta.paginas[0].tamanho_folha_cm, tuple)


def test_tamanho_folha_cm_none_sobrevive_ao_projeto():
    pagina = ConfigPagina(indice=0, folha=0)
    projeto = Projeto(caminho_entrada="x.pdf", paginas=[pagina])
    volta = Projeto.de_dicionario(projeto.para_dicionario())
    assert volta.paginas[0].tamanho_folha_cm is None
