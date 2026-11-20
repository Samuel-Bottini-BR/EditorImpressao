"""Provas do pacote de regras (D-784): a tabela cobre todo arquivo do git, o catálogo é coerente e o montador funciona.

Palavras do Samuel (D-784, 18/11): "ok, mas como vai saber que regras enviar para o agente?" · "ok". Na prática (o
Livro): cada agente recebe as regras "sempre" mais as das etiquetas dos arquivos que o trabalho mexe, pela tabela
"arquivo → etiquetas", montada por um programa; arquivo fora da tabela recebe todas e a gerente é avisada; quem tenta
quebrar recebe todas.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from regras_dos_agentes import catalogo, conversa_com_o_git as git, formulario, montar_pacote, pedido, tabela_arquivos
from regras_dos_agentes.livro import Livro

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVOS_DO_PASSO_1 = ["novo:core/windows.py", "main.py", "novo:tests/test_windows_peca_unica.py",
                       "novo:janela_de_prova.py", "relatorios/passo1/"]


def test_todo_arquivo_do_git_tem_linha_na_tabela():
    """Um teste cobra que todo arquivo do git tem linha na tabela (D-784; a tabela não pode ficar atrasada)."""
    sem = tabela_arquivos.sem_linha(git.arquivos_do_git(RAIZ))
    assert sem == [], "arquivos sem linha na tabela (a gerente acrescenta): " + ", ".join(sem[:20])


def test_arquivo_fora_da_tabela_recebe_todas_as_regras_e_a_gerente_e_avisada():
    """Arquivo que nenhuma linha pega recebe todas as etiquetas e vira aviso no pacote (nunca um pacote pequeno)."""
    tags, avisos = tabela_arquivos.etiquetas_do_trabalho(["novo:pasta_que_nao_existe/x.dat"], RAIZ)
    assert tags >= set(catalogo.ETIQUETAS) - {"GER"} and avisos


def test_o_conteudo_tambem_da_a_etiqueta_do_windows():
    """Um script cujo conteúdo chama o Windows ganha a etiqueta do Windows, mesmo que a tabela não diga."""
    assert "WIN" in tabela_arquivos.etiquetas_do_arquivo("docs/x.md", "subprocess.run(['powershell'])")[0]
    assert "WIN" not in tabela_arquivos.etiquetas_do_arquivo("docs/x.md", "texto")[0]


def test_as_linhas_novas_do_plano_da_parte_do_windows_estao_na_tabela():
    """As linhas dos arquivos novos do plano (o mostrador da troca, as janelas de prova, o publicar, o passo 0)."""
    for caminho, etiqueta in [("ui/mostrador_da_troca.py", "WIN"), ("janela_de_prova.py", "WIN"),
                              ("provas/servidor_das_versoes.py", "WIN"), ("tests/test_publicar_rapido.py", "WIN"),
                              ("core/windows.py", "WIN"), ("regras_dos_agentes/porteiro.py", "TESTE"),
                              ("ganchos/pre-commit", "GIT"), ("tests/conferencias_excecoes.json", "GER"),
                              (".github/workflows/testes-windows.yml", "TESTE")]:
        tags, casou = tabela_arquivos.etiquetas_do_arquivo(caminho)
        assert casou and etiqueta in tags, caminho


def test_o_catalogo_e_coerente():
    """Cada regra tem número único, etiquetas e papel conhecidos; o "sempre" tem no máximo 10 e cobre regras que existem."""
    ids = [r["id"] for r in catalogo.REGRAS]
    assert len(ids) == len(set(ids))
    papeis = {"todos", "codigo", "verif", "pesq", "layout", "gerente"}
    marcas = set(catalogo.CONTRADICOES) | set(catalogo.DIFERENCAS_PEQUENAS) | set(catalogo.VENCIDAS)
    for r in catalogo.REGRAS:
        assert set(r["tags"]) <= set(catalogo.ETIQUETAS) and r["papel"] in papeis and r["maq"] in ("sim", "em parte",
                                                                                                    "nao"), r["id"]
        assert not r.get("contra") or r["contra"] in marcas, r["id"]
    assert len(catalogo.SEMPRE) <= 10
    assert {i for s in catalogo.SEMPRE for i in s["cobre"]} <= set(ids)


def test_as_contradicoes_resolvidas_citam_decisoes_que_existem_no_livro():
    """Cada contradição resolvida aponta para a decisão do Samuel que a resolveu, e ela existe no Livro."""
    livro = Livro.do_repositorio(RAIZ)
    for codigo, (decisao, vale) in catalogo.RESOLVIDAS.items():
        assert codigo in catalogo.CONTRADICOES and vale
        assert livro.existe(decisao), decisao
        assert codigo in " ".join(livro.colunas(decisao)), f"{decisao} não fala da contradição {codigo}"


def test_as_secoes_do_claude_md_citadas_pelo_catalogo_existem():
    """A fonte de cada regra ("CLAUDE.md §4.6", "§11.12") ainda existe no CLAUDE.md (a regra não ficou órfã)."""
    texto = (RAIZ / "CLAUDE.md").read_text(encoding="utf-8")
    titulos = set(re.findall(r"^#{2,3}\s+(\d+(?:\.\d+)?)[.\s]", texto, re.M))

    def item_da_secao(n: str, sub: str) -> bool:
        """A seção N tem o subtítulo "### N.M" ou o item numerado "M. **..." (como as regras da seção 11)."""
        if f"{n}.{sub}" in titulos:
            return True
        partes = re.split(r"^## (\d+)\.", texto, flags=re.M)
        corpo = next((partes[i + 1] for i in range(1, len(partes) - 1, 2) if partes[i] == n), "")
        return bool(re.search(rf"^{sub}\.\s+\*\*", corpo, re.M))

    for r in catalogo.REGRAS:
        for onde in r["onde"]:
            m = re.match(r"CLAUDE\.md §(\d+)(?:\.(\d+))?", onde)
            if not m:
                continue
            n, sub = m.group(1), m.group(2)
            assert n in titulos, f"{r['id']}: §{n} não existe no CLAUDE.md"
            assert not sub or item_da_secao(n, sub), f"{r['id']}: §{n}.{sub} não existe no CLAUDE.md"


def test_o_pacote_do_passo_1_traz_as_regras_do_windows_e_o_formulario_do_windows():
    """O pacote da peça única do Windows: regras do Windows, decisões copiadas do Livro e os campos do Windows."""
    texto = montar_pacote.montar("implementador", "passo 1", ["D-767", "D-782"], ARQUIVOS_DO_PASSO_1, RAIZ,
                                 "746dbda6", "passo1")
    assert "Uma peça só para conversar com o que está fora" in texto
    assert "Peça de mentira não prova" in texto
    linha = Livro.do_repositorio(RAIZ).colunas("D-767")[2]
    assert linha[:80] in texto, "as palavras do Samuel vêm copiadas do Livro"
    for titulo in ("O que pode falhar e o que o programa faz", "A prova de verdade",
                   "Perguntas do Windows que o Samuel vê", "O print que prova"):
        assert f"## {titulo}" in texto, titulo
    assert "resolvido pelo Samuel (D-787)" in texto


def test_o_pedido_do_pacote_e_lido_de_volta_igual():
    """O bloco do pedido que o agente copia é lido de volta igual (o porteiro e a gerente comparam)."""
    texto = montar_pacote.montar("layout", "x", [], ARQUIVOS_DO_PASSO_1, RAIZ, "746dbda6", "passo1")
    lido = pedido.ler(texto)
    assert lido.problemas == []
    assert (lido.papel, lido.partida, lido.ramo) == ("layout", "746dbda6", "passo1")
    assert lido.arquivos == [a.removeprefix("novo:") for a in ARQUIVOS_DO_PASSO_1]


def test_quem_tenta_quebrar_recebe_todas_as_regras_e_os_seis_campos():
    """D-775 e D-784: quem tenta quebrar recebe todas as regras e o relatório de seis campos."""
    impl = montar_pacote.escolher_regras({"WIN", "TESTE", "GIT"}, "implementador")
    quebra = montar_pacote.escolher_regras({"WIN", "TESTE", "GIT"}, "quebrador")
    assert len(quebra) > len(impl) and {r["id"] for r in impl} <= {r["id"] for r in quebra} | {
        r["id"] for r in impl if r["papel"] == "codigo"}
    texto = montar_pacote.montar("quebrador", "x", [], ARQUIVOS_DO_PASSO_1, RAIZ, "746dbda6", "passo1")
    for _, titulo in formulario.CAMPOS_DE_QUEM_QUEBRA:
        assert f"## {titulo}" in texto


def test_arquivo_novo_so_da_linha_de_reserva_recebe_todas_as_regras():
    """Achado 12 (primeira volta) e N8 (segunda) de quem quebrou: `novo:core/registro_do_windows.py` saía só com imagem
    e git, e pelo título do pedido "desinstalar limpo" também não dava. Agora vale a tabela: o arquivo novo que só cai
    na linha de reserva (`core/*`) recebe todas as regras e a gerente é avisada para pôr a linha dele."""
    tags, avisos = tabela_arquivos.etiquetas_do_trabalho(["novo:core/registro_do_windows.py"], RAIZ)
    assert "WIN" in tags and any("linha de reserva" in a for a in avisos)
    tags, avisos = tabela_arquivos.etiquetas_do_trabalho(["novo:core/windows.py"], RAIZ)
    assert tags == {"WIN", "GIT"} and avisos == []


@pytest.mark.parametrize("arquivo", ["publicar_versao_kaique.py", "empacotar.py", "atualizacao.py",
                                     "core/testes_a_distancia.py", "core/_testes_a_distancia_windows.py",
                                     "ui/testes_a_distancia_ui.py"])
def test_os_arquivos_do_windows_ganham_as_regras_do_windows_pela_tabela(arquivo):
    """N8: as regras do Windows vêm do arquivo, pela tabela (não do título do pedido)."""
    assert "WIN" in tabela_arquivos.etiquetas_do_arquivo(arquivo)[0]


def test_a_lista_do_windows_da_tabela_e_a_do_porteiro():
    """Achado 13: o que é "conversa com o Windows" está escrito num lugar só (o porteiro); a tabela usa o mesmo."""
    from regras_dos_agentes import porteiro

    for linha in ("os.startfile(x)", "Register-ScheduledTask", "import winreg", "pwsh"):
        assert porteiro.CONVERSA_COM_O_WINDOWS.search(linha) and tabela_arquivos.fala_com_o_windows(linha), linha


def test_o_pacote_mostra_os_lugares_da_lista_nos_arquivos_do_pedido():
    """Achado 11: quem mexe num arquivo com lugares na lista recebe a lista deles e o aviso de como ela funciona."""
    texto = montar_pacote.montar("implementador", "atualizador", [], ["atualizacao.py"], RAIZ, "746dbda6", "x")
    assert "## Lugares da lista de exceções nos seus arquivos" in texto and "vira erro novo" in texto


def test_q3_o_pacote_do_passo_diz_as_funcoes_de_outros_passos_que_nao_se_mexem():
    """Achado Q3 (quarta volta, 19/11/2026): o lugar da lista é a função e o texto; o agente do passo 3 que renomeasse
    `criar_as_tarefas` (lugares do passo 5) faria o ramo barrar sem saber por quê. Com `passo`, o pacote lista essas
    funções; as do próprio passo não entram nessa lista."""
    texto = montar_pacote.montar("implementador", "passo 3", [], ["atualizacao.py"], RAIZ, "746dbda6", "x", "3")
    bloco = texto.split("Não renomeie nem mova", 1)[1].split("\n\n", 2)[1]
    assert "`criar_as_tarefas` (lugares do passo 5)" in bloco and "passo 3)" not in bloco
    assert "Não renomeie nem mova" not in montar_pacote.montar("implementador", "x", [], ["atualizacao.py"], RAIZ,
                                                               "746dbda6", "x")


# ---------------------------------------------------------------- as regras e perguntas do catálogo dos erros (19/11)

def test_as_regras_que_citam_o_livro_citam_decisoes_que_existem():
    """As regras novas do catálogo dos erros têm a fonte no Livro ("DECISOES.md D-809", até a gerente escrever no
    CLAUDE.md): cada decisão citada existe no Livro (a regra não fica órfã)."""
    livro = Livro.do_repositorio(RAIZ)
    citadas = [(r["id"], m.group(1)) for r in catalogo.REGRAS for onde in r["onde"]
               if (m := re.match(rf"{catalogo.LIVRO} (D-\d{{3,}})$", onde))]
    assert {d for _, d in citadas} >= {"D-809", "D-810", "D-812", "D-813"}
    for regra, decisao in citadas:
        assert livro.existe(decisao), f"{regra}: {decisao}"


def test_d813_o_acrescimo_a_regra_6_e_o_texto_do_livro_e_vai_em_todo_pacote():
    """D-813 (19/11): o acréscimo à regra 6 do §11.12, com o texto do Livro, letra por letra; vai na regra R118 e no
    "sempre" que a cobre, que todo pacote traz (inclusive o de quem tenta quebrar, que tem nele o seu foco)."""
    assert Livro.do_repositorio(RAIZ).tem_as_palavras("D-813", catalogo.ACRESCIMO_D813)
    r118 = next(r for r in catalogo.REGRAS if r["id"] == "R118")
    sempre = next(s for s in catalogo.SEMPRE if "R118" in s["cobre"])
    assert catalogo.ACRESCIMO_D813 in r118["curta"] and catalogo.ACRESCIMO_D813 in sempre["texto"]
    for papel in ("implementador", "layout", "verificador", "pesquisador", "quebrador"):
        assert catalogo.ACRESCIMO_D813 in montar_pacote.montar(papel, "x", [], ["core/filtros.py"], RAIZ, "746dbda6",
                                                               "x"), papel


def test_d809_d810_d812_as_regras_novas_vao_aos_trabalhos_certos():
    """D-809: a regra do .git vai a todo trabalho (todo trabalho faz commit). D-810 e D-812: vão a todo trabalho com
    teste, do Windows ou não; não vão ao trabalho sem teste."""
    nomes = {i: next(r["nome"] for r in catalogo.REGRAS if r["id"] == i) for i in ("R156", "R157", "R158")}
    windows = montar_pacote.montar("implementador", "x", [], ARQUIVOS_DO_PASSO_1, RAIZ, "746dbda6", "x")
    testes = montar_pacote.montar("implementador", "x", [], ["core/filtros.py", "tests/test_filtros.py"], RAIZ,
                                  "746dbda6", "x")
    pesquisa = montar_pacote.montar("pesquisador", "x", [], ["docs/pesquisa/"], RAIZ, "746dbda6", "x")
    assert all(n in windows and n in testes for n in nomes.values())
    assert nomes["R156"] in pesquisa and nomes["R157"] not in pesquisa
    assert "Everyone" in windows and "(DECISOES.md D-810)" in windows


def test_os_campos_em_branco_do_pacote_sao_os_que_o_formulario_cobra():
    """Sem gambiarra (§11.12): o pacote e o formulário escolhem os campos pela mesma função (`vale_para`). Para cada
    jeito de trabalho, os títulos em branco do pacote são os que o formulário cobra (os de "só com pergunta", à parte)."""
    from regras_dos_agentes.formulario import CAMPOS, Resultado, SO_COM_PERGUNTAS, _conferir_campos

    for tags in ({"TESTE", "GIT"}, {"WIN", "TESTE", "GIT"}, {"TESTE", "GER", "GIT"}, {"IMG", "TELA", "GIT"}):
        em_branco = {t.split("\n")[0].removeprefix("## ") for t in montar_pacote.formulario_em_branco(tags,
                                                                                                    "implementador")}
        r = Resultado("pronto")
        _conferir_campos({}, "pronto", tags, r)
        cobrados = {t for c, t, _, _ in CAMPOS if any(f"\"{t}\"" in p for p in r.problemas)}
        so_com_pergunta = {t for c, t, _, _ in CAMPOS if c in SO_COM_PERGUNTAS}
        ja_no_pedido = {t for c, t, _, _ in CAMPOS if c == "F1"}      # vem preenchido no pedido, não em branco
        assert em_branco | ja_no_pedido == cobrados | so_com_pergunta, tags


def test_d811_d812_d814_o_pacote_do_windows_traz_as_perguntas_novas_e_o_so_de_testes_nao():
    """As perguntas novas (D-811, D-812) vão no pacote do Windows; no pacote de um trabalho só de testes, não. A do
    D-814 vai em todos, dizendo que só vale quando há pergunta para o Samuel."""
    windows = montar_pacote.montar("implementador", "x", [], ARQUIVOS_DO_PASSO_1, RAIZ, "746dbda6", "x")
    testes = montar_pacote.montar("implementador", "x", [], ["tests/test_filtros.py"], RAIZ, "746dbda6", "x")
    for titulo in ("Cada proteção e o teste que falha sem ela", "De onde vem cada dado que a conferência usa"):
        assert f"## {titulo}" in windows and f"## {titulo}" not in testes, titulo
    for texto in (windows, testes):
        assert "## Decisões procuradas antes de cada pergunta\n\n(a preencher; obrigatório antes de ir ao agente que " \
               "tenta quebrar, se houver pergunta para o Samuel" in texto
