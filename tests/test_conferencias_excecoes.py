"""Provas da lista de exceções do porteiro (D-791, D-800, D-802) e do teste que barra o repositório quando ela valer.

Palavras do Samuel (D-791, 19/11): à pergunta "o que já está errado no código fica numa lista, que só diminui e só
ganha item com o seu "sim"?": "Sim". E (D-800): "esses consertos deixa para depois". E (D-802), à pergunta "esses 56
ficam para depois da entrega ao Kaique? Sugiro que sim.": "ok, continuamos assim e vamos proceguir".

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
# Os lugares que o Samuel deixou para depois da entrega, (arquivo, conferência, função), escritos aqui à parte da
# tabela do programa de propósito: a prova não pode ler a resposta da própria coisa que ela confere.
# D-800: as dicas do Automático (qualquer função), o teste de velocidade lendo a placa de vídeo e o disco, e a régua.
DEPOIS_D800 = {("ui/automatico.py", "K04", "*"), ("teste_velocidade.py", "K01", "_placas_de_video"),
               ("teste_velocidade.py", "K01", "tipo_do_disco"), ("teste_velocidade.py", "K01", "_powershell"),
               ("teste_velocidade.py", "K01", "_caminho_do_powershell"), ("avaliar.py", "K01", "achar_acervo")}
# D-802: os 56 da busca ampliada, pelas funções onde estavam em 19/11 ("" = fora de função).
DEPOIS_D802 = {("teste_velocidade.py", "K01", f) for f in (
    "_classe_da_janela", "_entrada_da_janela_preta", "_esvaziar_a_entrada_pelo_windows", "_janela_do_console",
    "_ler_modo_da_janela_preta", "_ler_registro", "_memoria_gb", "_mudar_modo_da_janela_preta", "_pedir_ao_windows",
    "_pico_pelo_windows", "_sozinho_no_console")} | {
    ("ui/brasao_girando.py", "K01", f) for f in ("_programa_vivo", "rodar_sozinho", "rodar_sozinho.vigiar")} | {
    ("core/ocr_comum.py", "K01", "abrir_processo"), ("historico.py", "K01", "abrir_pasta"),
    ("historico.py", "K01", "imprimir"), ("core/nucleos.py", "K01", "memoria_livre_mb"),
    ("empacotar_teste_velocidade.py", "K01", "")}


def _depois_por_decisao(i: dict) -> str | None:
    """De qual decisão é o lugar, pela lista desta prova (não pela tabela do programa)."""
    for decisao, lugares in (("D-800", DEPOIS_D800), ("D-802", DEPOIS_D802)):
        if any(i["arquivo"] == a and i["conferencia"] == c and f in ("*", i["funcao"]) for a, c, f in lugares):
            return decisao
    return None


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
    """D-800 e D-802: "depois da entrega" é exatamente o que o Samuel deixou para depois, e nada fica "a perguntar".

    Mudou com a D-802 (19/11, "ok, continuamos assim e vamos proceguir"): antes, o que a busca ampliada achou nos
    arquivos da D-800 (o resto do teste de velocidade) tinha de esperar a pergunta ("fora do plano"); agora os 56 são
    "depois da entrega" e a lista não tem nenhum "fora do plano" (a prova escrita na D-802). A cobrança passou de
    arquivo para função: um lugar "depois da entrega" fora das funções que ele deixou para depois falha aqui.
    """
    lista = excecoes.ler(RAIZ)
    depois = [i for i in lista.itens if i["passo"] == excecoes.DEPOIS_DA_ENTREGA]
    assert all(_depois_por_decisao(i) for i in depois), [i for i in depois if not _depois_por_decisao(i)]
    # Todo lugar que ele deixou para depois e ainda está na lista é "depois da entrega" (nem no plano, nem a perguntar).
    assert all(i["passo"] == excecoes.DEPOIS_DA_ENTREGA for i in lista.itens if _depois_por_decisao(i))
    # D-802: "A lista de exceções não tem nenhum item 'fora do plano, a perguntar'".
    assert [i for i in lista.itens if i["passo"] == excecoes.FORA_DO_PLANO] == []
    # Na lista gerada em 19/11, os grupos têm o tamanho das decisões: 13 da D-800 (os 5 de então, com as linhas que a
    # busca maior achou nos mesmos pedaços) e os 56 da D-802. A lista só diminui: cada conta só pode cair.
    lugares = {d: sum(int(i["quantas"]) for i in depois if _depois_por_decisao(i) == d) for d in ("D-800", "D-802")}
    assert lugares["D-800"] <= 13 and lugares["D-802"] <= 56, lugares


def test_d802_a_tabela_do_programa_poe_cada_lugar_dele_depois_da_entrega_com_a_decisao_certa():
    """D-802: cada lugar que o Samuel deixou para depois sai "depois da entrega" na tabela do programa (o lugar único
    da conta, `excecoes.regra_do_lugar`), e a decisão que o texto dele usa é a mesma da prova."""
    for decisao, lugares in (("D-800", DEPOIS_D800), ("D-802", DEPOIS_D802)):
        for arquivo, conferencia, funcao in lugares:
            funcao = "PainelAutomatico.__init__" if funcao == "*" else funcao
            assert excecoes.passo_do_lugar(arquivo, conferencia, funcao)[0] == excecoes.DEPOIS_DA_ENTREGA, funcao
            assert excecoes.decisao_que_deixou_para_depois(arquivo, conferencia, funcao) == decisao, funcao


def test_d802_lugar_novo_que_ninguem_classificou_continua_fora_do_plano_a_perguntar():
    """D-802 não abriu a porta para o que vier depois: um lugar novo, que nenhuma linha classifica, continua "fora do
    plano, a perguntar ao Samuel" (CLAUDE.md §11.12, ponto 2: nada dá como certo o que não conferiu), mesmo dentro de
    um arquivo que já tem lugares "depois da entrega" (uma função nova no teste de velocidade, no brasão, na tela de
    início) ou com outra conferência numa função que já está na lista."""
    for arquivo, conferencia, funcao in (("teste_velocidade.py", "K01", "_funcao_nova_de_depois"),
                                         ("ui/brasao_girando.py", "K01", "outra_funcao"),
                                         ("historico.py", "K01", ""),
                                         ("core/nucleos.py", "K02", "memoria_livre_mb"),
                                         ("empacotar_teste_velocidade.py", "K01", "empacotar"),
                                         ("main.py", "K01", "principal")):
        assert excecoes.passo_do_lugar(arquivo, conferencia, funcao)[0] == excecoes.FORA_DO_PLANO, (arquivo, funcao)
        assert excecoes.decisao_que_deixou_para_depois(arquivo, conferencia, funcao) is None
    # E pelo caminho inteiro: o porteiro acha o erro numa função nova do teste de velocidade e a lista gerada o põe
    # "fora do plano", não "depois da entrega".
    novo = 'import ctypes\n\ndef _funcao_nova_de_depois():\n    """Nova."""\n    return ctypes.windll.kernel32\n'
    gerada = excecoes.gerar(achados({"teste_velocidade.py": novo}), "abc")
    assert gerada["itens"] and {i["passo"] for i in gerada["itens"]} == {excecoes.FORA_DO_PLANO}


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
