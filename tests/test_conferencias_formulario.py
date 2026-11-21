"""Provas do formulário da entrega (D-792; K19, K20, K21) e do relatório de quem tenta quebrar (D-775).

Palavras do Samuel (D-792, 18/11): "mas e o que vai determinar o que vai nesse formulario? vai ser feito um toda vez que
for enviado um trabalho para um agente?" · "ok". E (D-775): "o agente vai tentar quebrar antes de fazer o teste real na
tela né?" · "ok".

Cada prova monta, num repositório git de verdade numa pasta temporária, a entrega de um agente (o código, os commits
e o ONDE-PAREI) e confere: o formulário certo passa; cada falta ou erro feito de propósito volta ao agente. A rodada
do GitHub (K21) não é consultada aqui (ficaria dependendo da internet): sem consultar, ela fica "não conferida" e o
código de saída é 3, nunca 0. A leitura do registro do GitHub é provada com a linha de verdade de uma rodada.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from regras_dos_agentes import conversa_com_o_github as github
from regras_dos_agentes import formulario
from regras_dos_agentes.repositorio_de_prova import RepositorioDeProva

LIVRO = ("| D-605 | 03/11/2026 | \"A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode "
         "alterar o que já está escolhido e testado\" | o novo não estraga | x | x | x | x | x |\n")
TESTE_VELHO = '"""Teste antigo."""\n\n\ndef test_um():\n    """Um."""\n    assert 1 == 1\n'
TESTE_NOVO = '"""Teste novo do trabalho."""\n\n\ndef test_novo():\n    """Novo."""\n    assert 2 == 2\n'
PASTA = "relatorios/trabalho-x"


def secoes_certas(base: str, commit: str, arquivos: str = "- `tests/test_x.py`\n- `relatorios/trabalho-x/`",
                  papel: str = "implementador") -> dict[str, str]:
    """Um formulário preenchido do jeito certo (título → texto), para o trabalho de testes do repositório de prova."""
    return {
        "Pedido": f"- Papel: {papel}\n- Commit de partida: {base}\n- Ramo: trabalho-x",
        "Arquivos que vou mexer": arquivos,
        "Decisões que esta tarefa precisa cumprir":
            '- **D-605** (03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa" '
            "Aqui: nenhum teste antigo muda.",
        "O que já está escolhido e testado aqui": "- `tests/test_velho.py::test_um` continua como está.",
        "Como fica para quem usa e no livro": "O Kaique não vê diferença: nada muda na tela, e o PDF que sai é o mesmo.",
        "A causa, a regra e todos os caminhos": "Não se aplica: este trabalho só acrescenta um teste, não muda "
                                                "comportamento do programa.",
        "O que li da peça de fora e onde": "Não se aplica: este trabalho não usa peça de fora nova.",
        "O que foi feito": "Acrescentei um teste.",
        "Arquivos criados ou alterados": "- `tests/test_x.py` (novo)",
        "Como cumpri cada uma": "- D-605: nenhum teste antigo mudou; prova em `tests/test_x.py`.",
        "Testes": "No PC: `tests/test_x.py`. GitHub: rodada 44202459161, passou.",
        "Caminho e função": "Não se aplica: não há caminho de tela nem regra mudada; o teste novo é `tests/test_x.py`.",
        "Máquina ou olho": "Máquina: o teste novo.",
        "Ressalvas": "O teste só cobre o caso simples.",
        "Ideias e bugs": "Nenhum.",
        "Perguntas para o Samuel": "Nenhuma.",
        "Commit": f"Último commit do trabalho: {commit}.",
    }


def texto_de(secoes: dict[str, str]) -> str:
    """O ONDE-PAREI montado com estas seções."""
    return "# Trabalho x\n\n" + "\n\n".join(f"## {t}\n\n{c}" for t, c in secoes.items()) + "\n"


@pytest.fixture
def entrega(tmp_path):
    """A entrega de um implementador: partida com Livro e teste antigo; o trabalho acrescenta `tests/test_x.py`."""
    r = RepositorioDeProva.novo(tmp_path)
    r.escrever("docs/plano/DECISOES.md", LIVRO)
    r.escrever("tests/test_velho.py", TESTE_VELHO)
    base = r.commit("partida")
    r.enviar("obra-2026-10-26")      # a versão de teste no "GitHub" de prova: o Livro que vale é o dela (achado N1)
    r.escrever("tests/test_x.py", TESTE_NOVO)
    commit = r.commit("o teste novo")
    return r, base, commit


def pacote_de(secoes: dict[str, str], titulo: str = "um trabalho de testes") -> str:
    """O pacote da gerente com o mesmo pedido do formulário (o que o montador escreveria no começo)."""
    return f"# Pacote de regras: {titulo}\n\n" + texto_de({"Pedido": secoes["Pedido"],
                                                           "Arquivos que vou mexer": secoes["Arquivos que vou mexer"]})


def gravar_pacote(r: RepositorioDeProva, texto: str) -> Path:
    """O pacote fica fora da cópia (a gerente o guarda; não vai para o ramo do agente)."""
    caminho = r.raiz.parent / "pacote.md"
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def conferir(r: RepositorioDeProva, secoes: dict[str, str], etapa: str = "quebrar", pacote: str | None = None,
             sem_pacote: bool = False):
    """Grava o ONDE-PAREI, faz o commit e confere o formulário (sem consultar o GitHub nem o push).

    O pacote da gerente é obrigatório: sem `pacote`, usa o do mesmo pedido do formulário (`pacote_de`).
    """
    r.escrever(f"{PASTA}/ONDE-PAREI.md", texto_de(secoes))
    r.tentar_commit("ONDE-PAREI")   # sem mudança (o mesmo ONDE-PAREI de novo), o git não faz commit: tudo bem
    caminho_do_pacote = None if sem_pacote else gravar_pacote(r, pacote if pacote is not None else pacote_de(secoes))
    return formulario.conferir(r.raiz / PASTA / "ONDE-PAREI.md", etapa, r.raiz, pacote=caminho_do_pacote,
                               consultar_github=False, olhar_o_github_do_ramo=False)


def test_o_formulario_certo_passa_e_o_github_nao_consultado_fica_pendente(entrega):
    """O formulário certo não tem problema; a rodada do GitHub, não consultada, fica pendente (saída 3, nunca 0)."""
    r, base, commit = entrega
    resultado = conferir(r, secoes_certas(base, commit))
    assert resultado.problemas == [], resultado.explicar()
    assert [p for p in resultado.pendentes if "K21" in p]
    assert resultado.codigo_de_saida == 3


@pytest.mark.parametrize("titulo", ["Ressalvas", "Testes", "Como fica para quem usa e no livro", "Commit",
                                    "Decisões que esta tarefa precisa cumprir", "Perguntas para o Samuel"])
def test_campo_que_falta_volta_ao_agente(entrega, titulo):
    """Cada campo obrigatório que falta faz o formulário voltar (K19)."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    del s[titulo]
    assert any(titulo in p for p in conferir(r, s).problemas)


@pytest.mark.parametrize("enchimento", ["-", "ver acima", "(a preencher)", "TODO", "Não se aplica."])
def test_campo_so_com_enchimento_volta_ao_agente(entrega, enchimento):
    """Enchimento e "não se aplica" sem o motivo não valem como resposta."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["O que li da peça de fora e onde"] = enchimento
    assert any("peça de fora" in p and "vazia" in p for p in conferir(r, s).problemas)


def test_k20_as_palavras_citadas_tem_de_estar_no_livro(entrega):
    """K20: palavras do Samuel que não estão no Livro, letra por letra, voltam; decisão que não existe, também."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["Decisões que esta tarefa precisa cumprir"] = ('- **D-605**: "A partir de hoje, nenhuma função nova pode mudar" '
                                                     'Aqui: x.\n- **D-999**: "uma decisão que não existe no Livro"')
    s["Como cumpri cada uma"] = "- D-605 e D-999: ver o teste `tests/test_x.py`."
    problemas = conferir(r, s).problemas
    assert any("D-605" in p and "não estão no Livro" in p for p in problemas)
    assert any("D-999 não existe" in p for p in problemas)


def test_decisao_pedida_sem_como_cumpri_volta(entrega):
    """Cada decisão de "Decisões que esta tarefa precisa cumprir" tem de voltar em "Como cumpri cada uma" (F10)."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["Como cumpri cada uma"] = "- Nenhum teste antigo mudou; prova em `tests/test_x.py`."
    assert any("D-605 pedida e sem" in p for p in conferir(r, s).problemas)


def test_arquivos_declarados_tem_de_bater_com_o_git(entrega):
    """F9: arquivo mexido e não declarado volta; arquivo declarado e não mexido também."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["Arquivos criados ou alterados"] = "- `tests/test_y.py`"
    problemas = conferir(r, s).problemas
    assert any("mexeu em tests/test_x.py e não declarou" in p for p in problemas)
    assert any("declarou tests/test_y.py" in p for p in problemas)


def test_teste_citado_que_nao_existe_volta(entrega):
    """Teste citado (arquivo ou função) que não existe volta."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["O que já está escolhido e testado aqui"] = "- `tests/test_velho.py::test_que_nao_existe`"
    assert any("test_que_nao_existe" in p for p in conferir(r, s).problemas)


def test_commit_citado_tem_de_ser_o_ultimo_do_trabalho(entrega):
    """F18: depois do commit citado, só o relatório pode ter mudado."""
    r, base, commit = entrega
    r.escrever("tests/test_x.py", TESTE_NOVO.replace("2 == 2", "3 == 3"))
    r.commit("mudou depois")
    assert any("depois do commit" in p for p in conferir(r, secoes_certas(base, commit)).problemas)


def test_pergunta_para_o_samuel_fora_do_jeito_dele_volta(entrega):
    """F17: pergunta com palavra de dentro, sem "O que você escolhe", sem print e sem sugestão volta (§11.13)."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["Perguntas para o Samuel"] = "### A lista\n\nPosso ligar o porteiro da D-791 no formulario.py?"
    problemas = conferir(r, s).problemas
    for falta in ("palavra de dentro", "O que você escolhe", "sem print", "sem a sugestão"):
        assert any(falta in p for p in problemas), falta


def test_o_pedido_tem_de_ser_o_do_pacote_da_gerente(entrega):
    """D-796: a lista de arquivos do ONDE-PAREI tem de ser a do pacote; o agente que a muda é devolvido."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    pacote = pacote_de({"Pedido": s["Pedido"], "Arquivos que vou mexer": "- `tests/test_x.py`"})
    assert any("não é o do pacote" in p for p in conferir(r, s, pacote=pacote).problemas)
    assert not any("não é o do pacote" in p for p in conferir(r, s).problemas)


def test_sem_o_pacote_da_gerente_o_formulario_volta(entrega):
    """Achado 3 de quem tentou quebrar (19/11): sem o pacote, o papel e a lista eram só o que o agente escrevia, e a
    saída era 0. Agora volta ao agente."""
    r, base, commit = entrega
    resultado = conferir(r, secoes_certas(base, commit), sem_pacote=True)
    assert any("falta o pacote" in p for p in resultado.problemas) and resultado.codigo_de_saida == 1


def test_o_papel_que_vale_e_o_do_pacote(entrega):
    """O agente que escreve outro papel no ONDE-PAREI (ex.: o de tela que se diz implementador) é devolvido."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    pacote = pacote_de(dict(s, Pedido=s["Pedido"].replace("implementador", "layout")))
    assert any("(papel)" in p for p in conferir(r, s, pacote=pacote).problemas)


def test_rotulo_de_pronto_no_formulario_de_quem_construiu_volta(entrega):
    """D-798, pelo formulário: o rótulo de pronto para conferir escrito pelo implementador volta (K10)."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["O que foi feito"] = "Acrescentei um teste. PRONTO PARA CONFERIR."
    assert any("K10" in p for p in conferir(r, s).problemas)


def test_trabalho_do_windows_cobra_as_falhas_e_as_perguntas_do_windows(entrega):
    """Etiqueta Windows: os seis casos de falha e o número de perguntas do Windows (D-792) são obrigatórios."""
    r, base, commit = entrega
    s = secoes_certas(base, commit, arquivos="- `tests/test_x.py`\n- `atualizacao.py`")
    problemas = conferir(r, s).problemas
    assert any("O que pode falhar" in p for p in problemas)
    assert any("Perguntas do Windows que o Samuel vê" in p for p in problemas)
    s["O que pode falhar e o que o programa faz"] = "- sem internet: avisa."
    s["Perguntas do Windows que o Samuel vê"] = "0."
    problemas = conferir(r, s).problemas
    assert any("sem licença" in p for p in problemas) and any("disco cheio" in p for p in problemas)
    assert not any("Perguntas do Windows" in p for p in problemas)


def test_antes_da_prova_a_vista_exige_o_relatorio_de_quem_quebrou(entrega):
    """Etapa "prova": sem o relatório de quem tentou quebrar (F19) volta; com ele e cada achado com destino, passa."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    assert any("tentou quebrar" in p for p in conferir(r, s, etapa="prova").problemas)
    r.escrever(f"{PASTA}/quem-quebrou/relatorio.md", texto_de({
        "Pedido": f"- Papel: quebrador\n- Commit de partida: {base}\n- Ramo: trabalho-x",
        "Arquivos que vou mexer": "- `relatorios/trabalho-x/`",
        "O que li": "O teste novo e o commit.", "O que conferi nas falhas, nas peças de fora e nos caminhos": "Li tudo.",
        "Caminhos que o outro não listou": "Nenhum caminho a mais.", "Falhas não pensadas e resultado não conferido":
            "Nenhuma.", "As regras que conferi": "R102 e R076.",
        "Achados": "1. O teste novo não tem mensagem no assert (`tests/test_x.py:6`)."}))
    s["O que o agente que tentou quebrar achou"] = "Relatório: `quem-quebrou/relatorio.md`.\n\n1. Mensagem do assert: não é defeito, " \
                                                   "o pytest mostra os dois lados."
    resultado = conferir(r, s, etapa="prova")
    assert resultado.problemas == [], resultado.explicar()


def test_relatorio_de_quem_quebra_tem_os_seis_campos_e_o_lugar_de_cada_achado(entrega):
    """O relatório de quem tenta quebrar: falta um dos seis campos, ou achado sem arquivo:linha, volta."""
    r, base, _ = entrega
    s = {"Pedido": f"- Papel: quebrador\n- Commit de partida: {base}\n- Ramo: trabalho-x",
         "Arquivos que vou mexer": "- `relatorios/trabalho-x/`", "O que li": "Tudo.",
         "Caminhos que o outro não listou": "Nenhum.", "Falhas não pensadas e resultado não conferido": "Nenhuma.",
         "As regras que conferi": "Todas.", "Achados": "1. Falta um aviso."}
    problemas = conferir(r, s).problemas
    assert any("O que conferi nas falhas" in p for p in problemas)
    assert any("achado sem o lugar" in p for p in problemas)


def test_pronto_no_windows_exige_a_prova_de_verdade(entrega):
    """Etapa "pronto" num trabalho do Windows: "falta a sessão" na prova de verdade (F20) não é pronto."""
    r, base, commit = entrega
    s = secoes_certas(base, commit, arquivos="- `tests/test_x.py`\n- `atualizacao.py`")
    s["A prova de verdade"] = "Falta a sessão A."
    assert any("ainda falta" in p for p in conferir(r, s, etapa="pronto").problemas)


def test_a_leitura_do_commit_testado_no_registro_do_github():
    """K21: a linha de verdade do registro da rodada 44202459161 (17/11) dá o commit testado; sem ela, nada."""
    linha = ("Suite (parte 1 de 5)\tUNKNOWN STEP\t2026-11-17T23:48:21.9751063Z codigo trocado pelo de "
             "nome-pacote-2026-11-17 (052be0452e5cfe3f16fb073648a4820667b3b204); .github/ continua a deste ramo")
    assert github.commit_do_registro(linha) == "052be0452e5cfe3f16fb073648a4820667b3b204"
    assert github.commit_do_registro("testando o proprio commit " + "a" * 40) == "a" * 40
    assert github.commit_do_registro("nada aqui") is None


def test_k21_vale_a_rodada_do_ultimo_commit_mesmo_citada_antes_de_uma_antiga(entrega, monkeypatch):
    """Teste de reversão (bug achado em 19/11/2026 rodando o formulário na própria entrega do passo 0): com duas rodadas
    citadas em "Testes", a K21 conferia só a última citada (a de um commit do meio) e devolvia a entrega, mesmo com a
    rodada do último commit passando. Agora vale se alguma rodada citada testou o último commit e passou.

    A leitura do GitHub é trocada aqui por respostas fixas (`ler_rodada`): o que se prova é a escolha entre as rodadas,
    não a conversa com o GitHub (essa é provada com a rodada de verdade na entrega, ver o ONDE-PAREI do passo 0).
    """
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["Testes"] = "GitHub: rodada 111111111 (o último commit), passou. Antes, a rodada 222222222 (de um commit do meio)."
    r.escrever(f"{PASTA}/ONDE-PAREI.md", texto_de(s))
    r.commit("ONDE-PAREI")
    respostas = {"111111111": github.Rodada("111111111", True, True, "x", commit, "CONFERIDO"),
                 "222222222": github.Rodada("222222222", True, True, "x", base, "CONFERIDO")}
    monkeypatch.setattr(github, "ler_rodada", lambda numero, repositorio: respostas[numero])
    monkeypatch.setattr(formulario.git, "repositorio_no_github", lambda raiz: "dono/nome")
    pacote = gravar_pacote(r, pacote_de(s))
    resultado = formulario.conferir(r.raiz / PASTA / "ONDE-PAREI.md", "quebrar", r.raiz, pacote=pacote,
                                    consultar_github=True, olhar_o_github_do_ramo=False)
    assert not any("K21" in p for p in resultado.problemas + resultado.pendentes), resultado.explicar()
    respostas["111111111"] = github.Rodada("111111111", True, False, "x", commit, "CONFERIDO")
    resultado = formulario.conferir(r.raiz / PASTA / "ONDE-PAREI.md", "quebrar", r.raiz, pacote=pacote,
                                    consultar_github=True, olhar_o_github_do_ramo=False)
    assert any("nenhuma rodada citada vale" in p for p in resultado.problemas)



@pytest.mark.parametrize("marca, onde", [(None, "pendentes"), ("NAO CONFERIDO (a lista ainda espera o sim)", "pendentes"),
                                         ("BARROU", "problemas"), ("CONFERIDO", None)])
def test_k21_o_juiz_do_porteiro_tem_de_ter_conferido(entrega, monkeypatch, marca, onde):
    """R2 da terceira volta de quem quebrou (19/11): "parado" nunca vale como "passou". A rodada só vale se o juiz do
    porteiro (o código da versão de teste) deixou "PORTEIRO: CONFERIDO" no registro; sem o juiz ou com "NAO CONFERIDO",
    fica pendente (código 3); com "BARROU", volta."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["Testes"] = "GitHub: rodada 111111111, passou."
    r.escrever(f"{PASTA}/ONDE-PAREI.md", texto_de(s))
    r.commit("ONDE-PAREI")
    monkeypatch.setattr(github, "ler_rodada",
                        lambda numero, repositorio: github.Rodada(numero, True, True, "x", commit, marca))
    monkeypatch.setattr(formulario.git, "repositorio_no_github", lambda raiz: "dono/nome")
    resultado = formulario.conferir(r.raiz / PASTA / "ONDE-PAREI.md", "quebrar", r.raiz, pacote=gravar_pacote(r, pacote_de(s)),
                                    consultar_github=True, olhar_o_github_do_ramo=False)
    k21 = {"pendentes": [p for p in resultado.pendentes if "K21" in p],
           "problemas": [p for p in resultado.problemas if "K21" in p]}
    if onde is None:
        assert not k21["pendentes"] and not k21["problemas"], resultado.explicar()
    else:
        assert k21[onde], resultado.explicar()


def test_a_marca_do_juiz_e_lida_no_registro_da_rodada():
    """A marca que o juiz escreve é achada no registro, no formato que o GitHub devolve (trabalho, passo e hora antes
    do texto). Mudou na quarta volta (achado Q1): texto que só CONTÉM a marca no meio da linha não conta mais."""
    juiz = "Porteiro (juiz da versao de teste)\tJulgar\t"
    assert github.marca_do_porteiro(juiz + "2026-11-20T01:00:00.1234567Z PORTEIRO: CONFERIDO\n") == "CONFERIDO"
    assert github.marca_do_porteiro("2026-11-20T01:00Z PORTEIRO: CONFERIDO\n") == "CONFERIDO"
    assert github.marca_do_porteiro(
        juiz + "2026-11-20T01:00:00Z PORTEIRO: NAO CONFERIDO (a versão de teste ainda não tem o porteiro)\r\n") == \
        "NAO CONFERIDO (a versão de teste ainda não tem o porteiro)"
    assert github.marca_do_porteiro(juiz + "2026-11-20T01:00:00Z echo 'PORTEIRO: CONFERIDO'\n") is None
    assert github.marca_do_porteiro("nada aqui") is None


# O registro de uma rodada falsa, como o de quem quebrou (quarta volta, Q1): o código do agente roda na suíte e escreve
# uma marca "CONFERIDO" antes; o juiz, no trabalho dele, escreve "NAO CONFERIDO".
TRABALHOS = [{"name": "Testes (pytest)", "databaseId": 1, "conclusion": "success"},
             {"name": "Porteiro (juiz da versao de teste)", "databaseId": 2, "conclusion": "success"}]
REGISTROS = {1: "Testes (pytest)\tpytest\t2026-11-20T01:00:00Z PORTEIRO: CONFERIDO\n",
             2: "Porteiro (juiz da versao de teste)\tJulgar\t2026-11-20T01:05:00Z PORTEIRO: NAO CONFERIDO (proposta)\n"}


def test_q1_a_marca_so_vale_lida_no_trabalho_do_juiz():
    """Achado Q1 (quarta volta de quem quebrou, 19/11/2026): a K21 lia a primeira marca de qualquer trabalho, e o
    código do agente, que roda na suíte, podia escrever "PORTEIRO: CONFERIDO" antes do juiz. Agora só vale a marca do
    trabalho de nome "Porteiro (juiz da versao de teste)"; sem esse trabalho, não há marca (e a K21 fica pendente)."""
    assert github.marca_do_juiz(TRABALHOS, lambda j: REGISTROS[j["databaseId"]]) == "NAO CONFERIDO (proposta)"
    assert github.marca_do_juiz(TRABALHOS[:1], lambda j: REGISTROS[j["databaseId"]]) is None
    pulado = [TRABALHOS[0], dict(TRABALHOS[1], conclusion="skipped")]
    assert github.marca_do_juiz(pulado, lambda j: REGISTROS[j["databaseId"]]) is None


# ---------------------------------------------------------------- as perguntas novas do catálogo dos erros (19/11/2026)

ARQUIVOS_DO_WINDOWS = "- `tests/test_x.py`\n- `atualizacao.py`"
PROTECOES = "- A recusa da pasta de troca de outra conta → `tests/test_x.py::test_novo` falha sem ela (numa cópia)."
DE_ONDE = "- O commit testado: do registro da rodada no GitHub (o agente não escreve)."


def test_d811_trabalho_do_windows_sem_as_protecoes_e_os_testes_volta(entrega):
    """D-811 (19/11): "na ficha de entrega, quem escreve passa a mostrar, para cada proteção, o teste que falha quando
    ela é desligada". Trabalho do Windows sem a lista volta; item sem teste (arquivo::função) volta; teste citado que
    não existe volta; com a lista certa, a pergunta passa."""
    r, base, commit = entrega
    s = secoes_certas(base, commit, arquivos=ARQUIVOS_DO_WINDOWS)
    assert any("Cada proteção e o teste que falha sem ela" in p for p in conferir(r, s).problemas)
    s["Cada proteção e o teste que falha sem ela"] = "- A recusa da pasta de troca: tem teste."
    assert any("proteção sem o teste" in p for p in conferir(r, s).problemas)
    s["Cada proteção e o teste que falha sem ela"] = "- A recusa: `tests/test_x.py::test_que_nao_existe`."
    assert any("test_que_nao_existe" in p and "não existe" in p for p in conferir(r, s).problemas)
    s["Cada proteção e o teste que falha sem ela"] = PROTECOES
    assert not any("F21" in p for p in conferir(r, s).problemas)


@pytest.mark.parametrize("arquivos", [ARQUIVOS_DO_WINDOWS, "- `tests/test_x.py`\n- `regras_dos_agentes/porteiro.py`"])
def test_d812_trabalho_que_confere_tem_de_dizer_de_onde_vem_cada_dado(entrega, arquivos):
    """D-812 (19/11): "De onde vem cada dado que a sua conferência usa?" no trabalho do Windows e no do porteiro: sem a
    resposta volta; com ela, a pergunta passa."""
    r, base, commit = entrega
    s = secoes_certas(base, commit, arquivos=arquivos)
    assert any("De onde vem cada dado que a conferência usa" in p for p in conferir(r, s).problemas)
    s["De onde vem cada dado que a conferência usa"] = DE_ONDE
    assert not any("F22" in p for p in conferir(r, s).problemas)


def test_as_perguntas_novas_nao_valem_para_o_trabalho_so_de_testes(entrega):
    """Pergunta nova não quebra entrega antiga: o trabalho só de testes, sem pergunta para o Samuel, não recebe as
    perguntas novas (F21, F22, F23); nem o pacote dele as traz."""
    r, base, commit = entrega
    problemas = conferir(r, secoes_certas(base, commit)).problemas
    assert not any(c in p for p in problemas for c in ("F21", "F22", "F23")), problemas


PERGUNTA_CERTA = ("### Onde fica o aviso\n\nNa tela de conferir, o aviso aparece em cima. O que você escolhe: em cima ou "
                  "embaixo. Minha sugestão: em cima. ![o aviso](prova.png)")


def test_d814_pergunta_ao_samuel_sem_as_decisoes_procuradas_volta(entrega):
    """D-814 (19/11): "antes de mandar qualquer pergunta para você, o agente anota em quais decisões suas procurou e por
    que essa ainda não está respondida". Sem a seção volta; sem o "###" da pergunta, sem decisão, com decisão que não
    existe ou sem o porquê volta; com tudo, passa."""
    r, base, commit = entrega
    r.escrever(f"{PASTA}/prova.png", "imagem")
    s = secoes_certas(base, commit)
    s["Perguntas para o Samuel"] = PERGUNTA_CERTA
    titulo = "Decisões procuradas antes de cada pergunta"
    assert any(titulo in p for p in conferir(r, s).problemas)
    casos = {"### Outra pergunta\n\n- Procurei: D-605.\n- Por que ainda não está respondida: a D-605 não fala do aviso.":
             "falta o \"### Onde fica o aviso\"",
             "### Onde fica o aviso\n\n- Procurei no Livro.\n- Por que ainda não está respondida: nenhuma fala do aviso.":
             "quais decisões do Livro",
             "### Onde fica o aviso\n\n- Procurei: D-999.\n- Por que ainda não está respondida: a D-999 não fala dele.":
             "D-999 não existe",
             "### Onde fica o aviso\n\n- Procurei: D-605.": "por que ela ainda não está respondida"}
    for corpo, falta in casos.items():
        s[titulo] = corpo
        assert any(falta in p and "F23" in p for p in conferir(r, s).problemas), falta
    s[titulo] = "### Onde fica o aviso\n\n- Procurei: D-605.\n- Por que ainda não está respondida: a D-605 é sobre testes."
    assert not any("F23" in p for p in conferir(r, s).problemas), conferir(r, s).explicar()


# ---------------------------------------------------------------- achados 6 e 7 de quem quebrou (20/11/2026)

ARQUIVO_COM_AJUDA = ('"""Y."""\n\n\ndef ajuda():\n    """Ajuda, não é teste."""\n\n\n'
                     'EXEMPLO = """\ndef test_escrito_num_texto():\n    pass\n"""\n\n\n'
                     'def test_de_verdade():\n    """Teste."""\n')


def test_achado_6_so_conta_como_teste_um_def_test_do_codigo(entrega):
    """Achado 6 (20/11): "o teste existe" aceitava a função de ajuda e o `def` escrito dentro de um texto de exemplo.
    Agora só vale a função `test_...` do código do arquivo."""
    r, base, commit = entrega
    r.escrever("tests/test_y.py", ARQUIVO_COM_AJUDA)
    r.adicionar("tests/test_y.py")
    s = secoes_certas(base, commit)
    s["O que já está escolhido e testado aqui"] = ("- `tests/test_y.py::ajuda`\n- `tests/test_y.py::test_escrito_num_texto`"
                                                   "\n- `tests/test_y.py::test_de_verdade`")
    problemas = conferir(r, s).problemas
    assert any("tests/test_y.py::ajuda" in p and "não existe" in p for p in problemas)
    assert any("tests/test_y.py::test_escrito_num_texto" in p and "não existe" in p for p in problemas)
    assert not any("test_de_verdade" in p for p in problemas), problemas


def test_achado_7_nenhuma_com_pergunta_embaixo_nao_desliga_a_conferencia(entrega):
    """Achado 7 (20/11): começar "Perguntas para o Samuel" com "Nenhuma" desligava a conferência das perguntas escritas
    embaixo (e a das decisões procuradas, D-814). Agora "Nenhuma" só vale sem pergunta embaixo."""
    r, base, commit = entrega
    s = secoes_certas(base, commit)
    s["Perguntas para o Samuel"] = "Nenhuma por enquanto, mas:\n\n### Uma pergunta\n\nPosso fazer assim?"
    problemas = conferir(r, s).problemas
    assert any("O que você escolhe" in p for p in problemas)
    assert any("Decisões procuradas antes de cada pergunta" in p for p in problemas)
    s["Perguntas para o Samuel"] = "Nenhuma."
    assert not any("F17" in p or "F23" in p for p in conferir(r, s).problemas)


def test_volta2_achado_3_protecao_escrita_sem_traco_tambem_e_cobrada(entrega):
    """Volta 2 de quem quebrou, achado 3 (20/11): uma proteção escrita numa linha sem "-", embaixo do primeiro item,
    virava continuação dele e passava sem teste. Agora é cobrada; a linha com espaço no começo continua o item."""
    r, base, commit = entrega
    s = secoes_certas(base, commit, arquivos=ARQUIVOS_DO_WINDOWS)
    s["De onde vem cada dado que a conferência usa"] = DE_ONDE
    s["Cada proteção e o teste que falha sem ela"] = PROTECOES + "\nA conferência da licença, sem teste nenhum."
    assert any("proteção sem o teste" in p and "licença" in p for p in conferir(r, s).problemas)
    s["Cada proteção e o teste que falha sem ela"] = PROTECOES + "\n  (continuação do item de cima, com espaço.)"
    assert not any("F21" in p for p in conferir(r, s).problemas)
