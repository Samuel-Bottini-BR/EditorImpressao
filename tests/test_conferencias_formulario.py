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
    respostas = {"111111111": github.Rodada("111111111", True, True, "x", commit),
                 "222222222": github.Rodada("222222222", True, True, "x", base)}
    monkeypatch.setattr(github, "ler_rodada", lambda numero, repositorio: respostas[numero])
    monkeypatch.setattr(formulario.git, "repositorio_no_github", lambda raiz: "dono/nome")
    pacote = gravar_pacote(r, pacote_de(s))
    resultado = formulario.conferir(r.raiz / PASTA / "ONDE-PAREI.md", "quebrar", r.raiz, pacote=pacote,
                                    consultar_github=True, olhar_o_github_do_ramo=False)
    assert not any("K21" in p for p in resultado.problemas + resultado.pendentes), resultado.explicar()
    respostas["111111111"] = github.Rodada("111111111", True, False, "x", commit)
    resultado = formulario.conferir(r.raiz / PASTA / "ONDE-PAREI.md", "quebrar", r.raiz, pacote=pacote,
                                    consultar_github=True, olhar_o_github_do_ramo=False)
    assert any("nenhuma rodada citada vale" in p for p in resultado.problemas)
