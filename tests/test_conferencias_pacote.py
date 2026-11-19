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
