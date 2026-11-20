"""Provas da proteção do porteiro e da lista contra o próprio agente (achados 6 e 7 de quem tentou quebrar, 19/11).

Palavras do Samuel (D-791, 19/11): à pergunta "o que já está errado no código fica numa lista, que só diminui e só
ganha item com o seu "sim"?": "Sim".

No GitHub, em toda entrega, o ramo é comparado com a versão de teste (`obra-2026-10-26`, D-797): a lista só diminui
(item novo só com o "sim" próprio conferido no Livro), a situação e o "sim" não mudam, o passo de um item não muda, e
nenhum dado das buscas do porteiro some. As provas com exemplo usam um git de verdade numa pasta temporária, com um
"GitHub" que é outra pasta (D-767); a comparação do ramo de verdade busca a versão de teste no GitHub de verdade.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from regras_dos_agentes import protecao
from regras_dos_agentes.repositorio_de_prova import RepositorioDeProva

RAIZ = Path(__file__).resolve().parent.parent
LIVRO = ('| D-791 | 18/11/2026 | Chat: "o que já está errado no código fica numa lista" · "sim" | a lista de '
         'exceções do porteiro | x | x | x | x | x |\n')
SIM = {"decisao": "D-791", "em": "19/11/2026", "palavras": "o que já está errado no código"}
FORJADO = {"decisao": "D-791", "em": "19/11/2026", "palavras": "sim"}     # o ataque de quem quebrou (achado N1)


def _item(arquivo: str, texto: str, passo: str = "3", **extra) -> dict:
    """Um item da lista de exceções."""
    return dict({"arquivo": arquivo, "conferencia": "K01", "funcao": "", "texto": texto, "quantas": 1,
                 "data": "2026-11-19",
                 "passo": passo, "motivo": "prova"}, **extra)


def _lista(situacao: str = "proposta", itens: list | None = None, sim: dict | None = None) -> str:
    """O texto de uma lista de exceções."""
    return json.dumps({"situacao": situacao, "sim_do_samuel": sim, "itens": itens or [_item("atualizacao.py", "x")]})


@pytest.fixture
def repo(tmp_path) -> RepositorioDeProva:
    """Uma "versão de teste" no GitHub de prova, com o porteiro de hoje, uma lista e o Livro; a cópia parte dela."""
    r = RepositorioDeProva.novo(tmp_path)
    for nome in ("porteiro.py", "porteiro_mudancas.py"):
        r.escrever(f"regras_dos_agentes/{nome}", (RAIZ / "regras_dos_agentes" / nome).read_text(encoding="utf-8"))
    r.escrever("docs/plano/DECISOES.md", LIVRO)
    r.escrever("tests/conferencias_excecoes.json", _lista())
    r.commit("versão de teste")
    r.enviar(protecao.VERSAO_DE_TESTE)
    return r


def test_o_ramo_nao_afrouxa_o_porteiro_nem_a_lista_da_versao_de_teste():
    """O ramo de verdade contra a versão de teste de verdade (buscada no GitHub)."""
    frases = protecao.comparar(RAIZ)
    if frases is None:
        pytest.skip("a versão de teste ainda não tem o porteiro (antes de juntar o passo 0): não há com o que comparar")
    assert frases == [], "o ramo afrouxou o porteiro ou a lista:\n" + "\n".join(frases)


def test_sem_mudanca_nada_e_acusado(repo):
    """O ramo igual à versão de teste: nada acusado."""
    assert protecao.comparar(repo.raiz) == []


def test_tirar_palavra_da_busca_e_acusado(repo):
    """Tirar uma palavra da busca do Windows (o caso provado por quem tentou quebrar: o `schtasks`) é acusado."""
    caminho = repo.raiz / "regras_dos_agentes" / "porteiro.py"
    texto = caminho.read_text(encoding="utf-8")
    linha = next(l for l in texto.split("\n") if "schtasks" in l and l.strip().startswith("(r"))
    repo.escrever("regras_dos_agentes/porteiro.py", texto.replace(linha + "\n", ""))
    frases = protecao.comparar(repo.raiz)
    assert any("PALAVRAS_DO_WINDOWS" in f and "schtasks" in f for f in frases), frases


def test_acrescentar_palavra_na_busca_e_livre(repo):
    """Acrescentar uma palavra à busca não é acusado (deixa o porteiro mais rígido, não mais frouxo)."""
    caminho = repo.raiz / "regras_dos_agentes" / "porteiro.py"
    texto = caminho.read_text(encoding="utf-8")
    linha = next(l for l in texto.split("\n") if "o PowerShell 7" in l)
    novo = texto.replace(linha, linha + '\n    (r"\\bnovacoisa\\b", "prova", "x = \'novacoisa\'"),')
    assert novo != texto
    repo.escrever("regras_dos_agentes/porteiro.py", novo)
    assert protecao.comparar(repo.raiz) == []


def test_a_lista_so_diminui_e_a_situacao_o_sim_e_o_passo_nao_mudam(repo):
    """Item novo sem o "sim", a situação trocada, o "sim" inventado e o passo mudado: cada um é acusado."""
    repo.escrever("tests/conferencias_excecoes.json",
                  _lista(itens=[_item("atualizacao.py", "x", passo="5"), _item("main.py", "y")]))
    frases = protecao.comparar(repo.raiz)
    assert any("item novo" in f for f in frases) and any("passo" in f for f in frases)
    repo.escrever("tests/conferencias_excecoes.json", _lista("valendo", sim=SIM))
    assert any("situação" in f for f in protecao.comparar(repo.raiz))


def test_item_novo_com_qualquer_sim_e_acusado_e_tirar_item_e_livre(repo):
    """R1 da terceira volta (19/11): nenhum item entra por ramo de agente, nem com o "sim" (só a gerente, direto na
    versão de teste); tirar item (o conserto) é livre."""
    repo.escrever("tests/conferencias_excecoes.json",
                  _lista(itens=[_item("atualizacao.py", "x"), _item("main.py", "y", sim=SIM)]))
    assert any("item novo" in f for f in protecao.comparar(repo.raiz))
    repo.escrever("tests/conferencias_excecoes.json", json.dumps({"situacao": "proposta", "sim_do_samuel": None,
                                                                   "itens": []}))
    assert protecao.comparar(repo.raiz) == []


def test_sem_porteiro_na_versao_de_teste_nao_ha_o_que_comparar(tmp_path):
    """Antes de juntar o passo 0, a versão de teste não tem a lista: a comparação diz que não há com o que comparar."""
    r = RepositorioDeProva.novo(tmp_path)
    r.escrever("LEIAME.md", "x\n")
    r.commit("versão de teste antiga")
    r.enviar(protecao.VERSAO_DE_TESTE)
    assert protecao.comparar(r.raiz) is None


def test_o_que_afrouxou_compara_cada_tipo_de_dado():
    """Lista: o que some é acusado; "igual": qualquer mudança é acusada; dicionário: chave que some ou muda."""
    antes = 'A = ["x", "y"]\nB = "padrao"\nC = {"k": 1}\n'
    assert protecao.o_que_afrouxou(antes, 'A = ["x", "y", "z"]\nB = "padrao"\nC = {"k": 1, "j": 2}\n',
                                   [("A", "nao_some"), ("B", "igual"), ("C", "igual")]) == ["C mudou"]
    frases = protecao.o_que_afrouxou(antes, 'A = ["x"]\nB = "outro"\n', [("A", "nao_some"), ("B", "igual"),
                                                                          ("C", "nao_some")])
    assert frases == ["A: 'y' sumiu", "B mudou", "C sumiu (ou deixou de ser um valor escrito no arquivo)"]


def test_item_novo_com_o_sim_forjado_e_acusado(repo):
    """Achado N1 da segunda volta (19/11): o item novo com `"palavras": "sim"` passava na proteção do GitHub."""
    repo.escrever("tests/conferencias_excecoes.json",
                  _lista(itens=[_item("atualizacao.py", "x"), _item("main.py", "y", sim=FORJADO)]))
    assert any("item novo" in f for f in protecao.comparar(repo.raiz))


def test_o_livro_do_ramo_nao_vale_so_o_da_versao_de_teste(repo):
    """O agente que escreve no Livro do próprio ramo uma decisão para o "sim" dele também não passa: nenhum item entra
    por ramo de agente (R1)."""
    repo.escrever("docs/plano/DECISOES.md", LIVRO + '| D-990 | 19/11 | "pode pôr o meu erro na lista de exceções" | '
                                                    'a lista de exceções | x | x | x | x | x |\n')
    sim = {"decisao": "D-990", "em": "19/11", "palavras": "pode pôr o meu erro na lista"}
    repo.escrever("tests/conferencias_excecoes.json",
                  _lista(itens=[_item("atualizacao.py", "x"), _item("main.py", "y", sim=sim)]))
    assert any("item novo" in f for f in protecao.comparar(repo.raiz))


def test_afrouxar_a_busca_pelo_uso_e_acusado(repo, monkeypatch):
    """Achado N3 da segunda volta (19/11): a lista de palavras igual, mas o jeito de juntar as palavras deixando uma de
    fora (o caso provado: o `msiexec`). O porteiro deste ramo é trocado aqui por um afrouxado assim; a proteção usa o
    exemplo da própria lista da versão de teste e acusa."""
    import re

    from regras_dos_agentes import porteiro

    frouxa = re.compile("|".join(f"(?:{p})" for p, _, _ in porteiro.PALAVRAS_DO_WINDOWS if "msiexec" not in p), re.I)
    monkeypatch.setattr(porteiro, "CONVERSA_COM_O_WINDOWS", frouxa)
    frases = protecao.comparar(repo.raiz)
    assert any("msiexec" in f for f in frases), frases


# ---------------------------------------------------------------- K25 (D-809; pedido da gerente de 20/11)

def test_k25_tirar_linha_das_listas_e_acusado(repo):
    """K25: tirar o `gc` da lista do git que muda o .git (ou o `rm -r` da de apagar) é acusado; acrescentar é livre."""
    caminho = repo.raiz / "regras_dos_agentes" / "porteiro.py"
    texto = caminho.read_text(encoding="utf-8")
    linha = next(l for l in texto.split("\n") if l.strip().startswith('(_GIT + r"gc\\b"'))
    repo.escrever("regras_dos_agentes/porteiro.py", texto.replace(linha + "\n", ""))
    assert any("PALAVRAS_DO_GIT" in f and "sumiu" in f for f in protecao.comparar(repo.raiz))
    linha = next(l for l in texto.split("\n") if "apaga a pasta com tudo dentro (rm -r)" in l)
    repo.escrever("regras_dos_agentes/porteiro.py", texto.replace(linha, linha.replace("(rm -r)", "(rm)")))
    assert any("PALAVRAS_DE_APAGAR" in f for f in protecao.comparar(repo.raiz))
    repo.escrever("regras_dos_agentes/porteiro.py", texto.replace(
        'COMANDOS_DE_TERMINAL = (".sh",', 'COMANDOS_DE_TERMINAL = (".zsh", ".sh",'))
    assert protecao.comparar(repo.raiz) == []


@pytest.mark.parametrize("de, para, nome", [
    ('PECAS_DO_GIT = ("regras_dos_agentes/conversa_com_o_git.py",',
     'PECAS_DO_GIT = ("relatorios/meu_script.py", "regras_dos_agentes/conversa_com_o_git.py",', "PECAS_DO_GIT"),
    ('CONFERE_SE_E_ATALHO = (r"is_junction|', 'CONFERE_SE_E_ATALHO = (r"rm|is_junction|', "CONFERE_SE_E_ATALHO"),
])
def test_k25_crescer_a_excecao_ou_o_que_conta_como_conferir_e_acusado(repo, de, para, nome):
    """K25: pôr mais um arquivo nas peças do git, ou mais um jeito de "conferir o atalho", afrouxa a conferência: os
    dois ficam iguais aos da versão de teste."""
    texto = (repo.raiz / "regras_dos_agentes" / "porteiro.py").read_text(encoding="utf-8")
    assert de in texto
    repo.escrever("regras_dos_agentes/porteiro.py", texto.replace(de, para))
    assert any(nome in f and "mudou" in f for f in protecao.comparar(repo.raiz))


def test_k25_afrouxar_pelo_uso_e_acusado(repo, monkeypatch):
    """K25: as listas iguais, mas o porteiro deste ramo deixando de acusar (aqui, trocado por um que nunca acusa): a
    proteção passa cada exemplo das listas da K25 da versão de teste pelo porteiro de agora e acusa."""
    from regras_dos_agentes import porteiro

    monkeypatch.setattr(porteiro, "_o_que_o_comando_muda", lambda comando, antes: None)
    frases = protecao.comparar(repo.raiz)
    assert any("PALAVRAS_DO_GIT" in f and "K25" in f for f in frases), frases
    assert any("PALAVRAS_DE_APAGAR" in f and "K25" in f for f in frases), frases
