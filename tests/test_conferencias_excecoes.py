"""Provas da lista de exceções do porteiro (D-791, D-800) e do teste que barra o repositório quando ela valer.

Palavras do Samuel (D-791, 19/11): à pergunta "o que já está errado no código fica numa lista, que só diminui e só
ganha item com o seu "sim"?": "Sim". E (D-800): "esses consertos deixa para depois".

- A exceção é **por lugar** (arquivo, conferência, texto, quantas), nunca o arquivo inteiro (correção 2 do plano-v3,
  passo 0): erro novo no mesmo arquivo é barrado.
- A lista **só diminui**: lugar consertado tem de sair da lista; lugar novo não entra sozinho.
- **Enquanto o Samuel não disser "sim"** (`situacao: "proposta"`), o teste que barra o repositório fica parado, com o
  motivo escrito; os outros testes deste arquivo rodam sempre.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from regras_dos_agentes import excecoes, porteiro, texto_para_o_samuel

RAIZ = Path(__file__).resolve().parent.parent
PASSOS_DO_PLANO = {"1", "2", "3", "4", "5", "6"}
PASSOS_VALIDOS = PASSOS_DO_PLANO | {excecoes.DEPOIS_DA_ENTREGA, excecoes.FORA_DO_PLANO}
ARQUIVOS_DE_FORA_D800 = {"ui/automatico.py", "teste_velocidade.py", "avaliar.py"}


def lista_de(itens: list[dict], situacao: str = "valendo") -> excecoes.Lista:
    """Uma lista de exceções feita aqui, para provar a comparação."""
    sim = {"decisao": "D-791", "em": "19/11/2026", "palavras": "o que já está errado no código"} if (
        situacao == "valendo") else None
    return excecoes.Lista(situacao, sim, itens, {"situacao": situacao, "sim_do_samuel": sim, "itens": itens})


def item(arquivo: str, conferencia: str, texto: str, quantas: int = 1, funcao: str = "") -> dict:
    """Um item da lista (o lugar é arquivo, conferência, função e texto)."""
    return {"arquivo": arquivo, "conferencia": conferencia, "funcao": funcao, "texto": texto, "quantas": quantas,
            "data": "2026-11-19", "passo": "3", "motivo": "prova"}


DEFEITO_1 = 'import subprocess\n\ndef f(c):\n    """Lança."""\n    subprocess.Popen(c, creationflags=subprocess.DETACHED_PROCESS)\n'


def achados(arquivos: dict[str, str]) -> list[porteiro.Achado]:
    """O porteiro nestes arquivos."""
    return porteiro.conferir_codigo(arquivos, arquivos.get)


# ---------------------------------------------------------------- o arquivo da lista

def test_a_lista_do_repositorio_tem_o_formato_e_cada_item_tem_data_e_passo():
    """Cada item da lista tem arquivo, conferência, texto, quantas, data e o passo do plano que o conserta."""
    lista = excecoes.ler(RAIZ)
    assert lista.itens, "a lista de partida não pode estar vazia antes dos consertos"
    for i in lista.itens:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", i["data"]), i
        assert i["passo"] in PASSOS_VALIDOS, i
        assert porteiro.POR_CODIGO.get(i["conferencia"]), i


def test_so_os_lugares_que_o_samuel_deixou_para_depois_ficam_depois_da_entrega():
    """D-800: só as dicas do Automático, o teste de velocidade e a régua dos filtros ficam "depois da entrega"."""
    lista = excecoes.ler(RAIZ)
    de_fora = {i["arquivo"] for i in lista.itens if i["passo"] == excecoes.DEPOIS_DA_ENTREGA}
    assert de_fora <= ARQUIVOS_DE_FORA_D800
    # Nos arquivos da D-800, o que não é dos 5 lugares dele (achado pela busca ampliada) espera a pergunta.
    assert all(i["passo"] in (excecoes.DEPOIS_DA_ENTREGA, excecoes.FORA_DO_PLANO)
               for i in lista.itens if i["arquivo"] in ARQUIVOS_DE_FORA_D800)


def test_o_repositorio_so_tem_os_erros_que_a_lista_deixa():
    """O porteiro no repositório inteiro: barra todo erro fora da lista e todo item que o código já não tem.

    Parado enquanto a lista for "proposta": D-791, "nada entra nela sem o 'sim' dele". A gerente liga trocando a
    situação para "valendo" e escrevendo o "sim" do Samuel.
    """
    lista = excecoes.ler(RAIZ)
    if not lista.vale:
        pytest.skip("a lista de exceções espera o 'sim' do Samuel (D-791); o porteiro ainda não barra o repositório")
    _, encontrados = porteiro.achados_do_repositorio(RAIZ)
    comparacao = excecoes.comparar(encontrados, lista)
    assert comparacao.passa, "o porteiro barrou:\n" + "\n".join(comparacao.explicar())


def test_a_lista_valendo_sem_o_sim_do_samuel_nao_abre():
    """"valendo" sem o "sim" (ou com ele pela metade) não abre a lista. Monta a lista com dados próprios: vale nos
    dois estados da lista, antes e depois do "sim" (achado 1 da primeira volta de quem quebrou)."""
    import json

    base = {"situacao": "valendo", "itens": [item("atualizacao.py", "K02", "x")]}
    for sim in (None, {"em": "19/11/2026", "palavras": "sim"}):
        with pytest.raises(excecoes.ListaErrada):
            excecoes.ler(RAIZ, json.dumps(dict(base, sim_do_samuel=sim)))
    assert not excecoes.ler(RAIZ, json.dumps(dict(base, situacao="proposta", sim_do_samuel=None))).vale


def test_r1_qualquer_item_novo_ou_ligar_e_mudanca_que_so_a_gerente_faz():
    """R1 da terceira volta de quem quebrou (19/11): nenhum item entra, e a lista não é ligada, por ramo de agente.
    Item novo (com qualquer "sim", até um que esteja no Livro), "quantas" maior, passo, situação e "sim" mudados são
    sempre mudanças que só a gerente faz, direto na versão de teste."""
    from regras_dos_agentes.porteiro_mudancas import mudancas_na_lista

    antes = lista_de([item("a.py", "K01", "x")], "proposta")
    sim = {"decisao": "D-791", "em": "19/11/2026", "palavras": "não sei do que você está falando"}
    for depois in (lista_de([item("a.py", "K01", "x"), dict(item("b.py", "K01", "y"), sim=sim)], "proposta"),
                   lista_de([item("a.py", "K01", "x", 2)], "proposta"),
                   lista_de([dict(item("a.py", "K01", "x"), passo="5")], "proposta"),
                   lista_de([item("a.py", "K01", "x")], "valendo")):
        assert mudancas_na_lista(antes, depois), depois.itens
    assert mudancas_na_lista(antes, lista_de([], "proposta")) == []     # tirar item (o conserto) é livre


def test_correcao_2_erro_novo_no_mesmo_arquivo_e_barrado():
    """Correção 2: um arquivo com exceção não fica livre. Outro texto, ou o mesmo texto uma vez a mais, é barrado.

    O esboço isentava o arquivo inteiro (`atualizacao.py` livre de K01 e K02): o erro novo passaria.
    """
    hoje = achados({"atualizacao.py": DEFEITO_1})
    lista = lista_de([item(a.arquivo, a.conferencia, a.texto, funcao=a.funcao) for a in hoje])
    assert excecoes.comparar(hoje, lista).passa

    outro_texto = DEFEITO_1 + '\ndef g():\n    """Outro."""\n    return ["schtasks", "/Run"]\n'
    r = excecoes.comparar(achados({"atualizacao.py": outro_texto}), lista)
    assert [(a.conferencia, a.linha) for a in r.novos] == [("K01", 9)]

    duas_vezes = DEFEITO_1 + "    subprocess.Popen(c, creationflags=subprocess.DETACHED_PROCESS)\n"
    r = excecoes.comparar(achados({"atualizacao.py": duas_vezes}), lista)
    assert sorted((a.conferencia, a.linha) for a in r.novos) == [("K01", 6), ("K02", 6)]


def test_lugar_consertado_tem_de_sair_da_lista():
    """A lista só diminui: o lugar que o código já não tem faz o porteiro reclamar até sair da lista."""
    hoje = achados({"atualizacao.py": DEFEITO_1})
    lista = lista_de([item(a.arquivo, a.conferencia, a.texto, funcao=a.funcao) for a in hoje])
    consertado = DEFEITO_1.replace(", creationflags=subprocess.DETACHED_PROCESS", "")
    r = excecoes.comparar(achados({"atualizacao.py": consertado}), lista)
    assert not r.novos and len(r.consertados) == 2 and not r.passa
    nova = excecoes.diminuir(lista, achados({"atualizacao.py": consertado}))
    assert nova["itens"] == []


def test_diminuir_nunca_acrescenta_e_recusa_erro_novo():
    """`diminuir` tira o que foi consertado e mantém o resto; erro novo não entra (levanta, para ser consertado)."""
    hoje = achados({"atualizacao.py": DEFEITO_1})
    lista = lista_de([item(a.arquivo, a.conferencia, a.texto, funcao=a.funcao) for a in hoje])
    assert excecoes.diminuir(lista, hoje)["itens"] == lista.itens
    with pytest.raises(excecoes.ListaErrada):
        excecoes.diminuir(lista, achados({"atualizacao.py": DEFEITO_1, "main.py": DEFEITO_1}))


def test_item_acrescentado_e_quantas_maior_sao_achados():
    """`itens_acrescentados` acha o lugar novo e o "quantas" que subiu (o agente que faz isso é barrado, K17)."""
    antes = lista_de([item("a.py", "K01", "x"), item("b.py", "K04", "y", 2)])
    depois = lista_de([item("a.py", "K01", "x"), item("b.py", "K04", "y", 3), item("c.py", "K02", "z")])
    assert [(i["arquivo"], i["quantas"]) for i in excecoes.itens_acrescentados(antes, depois)] == [("b.py", 3),
                                                                                                   ("c.py", 1)]
    assert excecoes.itens_acrescentados(depois, antes) == []


def test_arquivo_ilegivel_nunca_e_excecao():
    """K00 (arquivo que o porteiro não leu) nunca passa pela lista, nem pode ser gerado nela."""
    ilegivel = achados({"core/x.py": "def f(:\n"})
    lista = lista_de([item("core/x.py", "K00", "core/x.py")])
    assert excecoes.comparar(ilegivel, lista).novos
    with pytest.raises(excecoes.ListaErrada):
        excecoes.gerar(ilegivel, "abc")


def test_lugar_que_o_plano_nao_conserta_fica_para_o_samuel_decidir():
    """Um lugar fora do que o plano conserta nunca ganha um passo inventado: fica "fora do plano, a perguntar"."""
    gerada = excecoes.gerar(achados({"main.py": DEFEITO_1}), "abc")
    assert {i["passo"] for i in gerada["itens"]} == {excecoes.FORA_DO_PLANO}
    gerada = excecoes.gerar(achados({"atualizacao.py": DEFEITO_1}), "abc", "2026-11-19")
    assert {i["passo"] for i in gerada["itens"]} == {"3"} and gerada["situacao"] == "proposta"


# ---------------------------------------------------------------- o texto para o Samuel

def test_o_texto_para_o_samuel_sai_da_lista_e_nao_tem_palavra_de_dentro():
    """O texto do "sim" tem os números da própria lista e nenhuma palavra de dentro (CLAUDE.md §11.13, regra 2)."""
    lista = excecoes.ler(RAIZ)
    texto = texto_para_o_samuel.texto(lista)
    r = excecoes.resumo(lista)
    assert f"achou {r['lugares']} lugares" in texto
    for passo, n in r["por_passo"].items():
        assert str(n) in texto, passo
    assert not re.search(r"\bD-\d{3}\b|\.py\b|\bK\d\d\b|\betapa \d|\bpasso \d", texto)
    assert "O que você escolhe" in texto and "Sugestão" in texto
