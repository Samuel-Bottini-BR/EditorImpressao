"""A única exceção da K03 do porteiro: a função da peça do Windows que só ACRESCENTA a licença (D-837, 23/11/2026).

Palavras do Samuel (chat 23/11/2026, à pergunta 6 do plano do atualizador novo): "6 – opção 1" — a regra do porteiro
que proíbe mexer na licença de pasta passa a deixar uma única função da peça do Windows, e só para acrescentar
"Usuários podem modificar" (nunca tirar herança nem trocar dono); continua barrando em todo o resto. E a observação do
Fable que a gerente adotou: "um caminho só, o provado no experimento (`icacls /grant ... /T` pela peça), não
`SetNamedSecurityInfoW` com o provado de reserva."

Cada prova abaixo falha se a exceção ficar mais larga do que a decisão (outra função, outro arquivo, outra palavra da
K03 na mesma função, uma opção que tira ou nega). A última confere a função de verdade do `core/windows.py`.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from regras_dos_agentes import porteiro

RAIZ = Path(__file__).resolve().parent.parent


def k03(arquivos: dict[str, str]) -> list[tuple[str, int]]:
    """(arquivo, linha) dos achados da K03 nestes arquivos (caminho → texto)."""
    achados = porteiro.conferir_codigo(arquivos, lambda c: arquivos.get(c))
    return [(a.arquivo, a.linha) for a in achados if a.conferencia == "K03"]


def py(texto: str) -> str:
    """Tira a margem do exemplo."""
    return textwrap.dedent(texto).lstrip("\n")


CERTO = py('''
    """A peça."""


    def dar_licenca_aos_usuarios(raiz):
        """Acrescenta."""
        ferramenta = pasta_do_sistema() / "icacls.exe"
        feito = _rodar([ferramenta, raiz, "/grant", f"*{SID_USUARIOS}:(OI)(CI)M", "/T"], LIMITE_DA_LICENCA_DA_PASTA_S)
''')


def test_d837_a_funcao_que_so_acrescenta_passa_so_na_peca():
    """Na peça, na função `dar_licenca_aos_usuarios`, a linha da ferramenta sozinha passa. A mesma linha em outra
    função da peça, ou na mesma função em outro arquivo, é acusada (a exceção é uma função de um arquivo, nada mais)."""
    assert k03({"core/windows.py": CERTO}) == []
    outra_funcao = CERTO.replace("def dar_licenca_aos_usuarios", "def outra_coisa")
    assert k03({"core/windows.py": outra_funcao}) == [("core/windows.py", 6)]
    assert k03({"atualizacao.py": CERTO}) == [("atualizacao.py", 6)]


@pytest.mark.parametrize("opcao", ["/inheritance:r", "/inheritance:d", "/setowner a", "/remove *S-1-5-32-545",
                                   "/deny *S-1-5-32-545:F", "/reset", "/restore a", "/grant:r *S-1-5-32-545:M"])
def test_d837_tirar_negar_trocar_dono_ou_heranca_e_acusado_ate_na_funcao(opcao):
    """Dentro da própria função que acrescenta, qualquer opção que tira, nega, troca o dono, mexe na herança ou
    SUBSTITUI a licença (o ":r" do "/grant:r") é acusada, na linha da ferramenta e em qualquer outra linha da função."""
    na_linha = CERTO.replace('"/T"]', f'"/T", "{opcao}"]')  # a linha do experimento com uma opção a mais
    assert k03({"core/windows.py": na_linha}) == [("core/windows.py", 7)]
    em_outra = CERTO.replace('    feito = _rodar(', f'    extra = "{opcao}"\n    return _rodar(')
    assert ("core/windows.py", 7) in k03({"core/windows.py": em_outra})


@pytest.mark.parametrize("palavra", ["SetNamedSecurityInfoW(a)", "Set-Acl -Path a", "takeown /f a", "cacls a"])
def test_d837_outra_ferramenta_de_licenca_na_funcao_continua_acusada(palavra):
    """A exceção é só a ferramenta do experimento: as outras palavras da K03 (inclusive a função do Windows de mudar
    licença, que o Fable descartou) continuam acusadas dentro da função, sozinhas ou junto com a ferramenta."""
    sozinha = CERTO.replace('    feito = _rodar(', f'    x = "{palavra}"\n    return _rodar(')
    assert ("core/windows.py", 7) in k03({"core/windows.py": sozinha})
    junto = CERTO.replace('/ "icacls.exe"', f'/ "icacls.exe {palavra}"')
    assert k03({"core/windows.py": junto}) == [("core/windows.py", 6)]


def test_d837_a_peca_de_verdade_passa_e_so_tem_a_ferramenta_naquela_funcao():
    """O `core/windows.py` desta cópia passa na K03 sem item na lista de exceções, e a ferramenta de licença aparece
    nele (no código, sem comentário nem docstring) só dentro de `dar_licenca_aos_usuarios`."""
    fonte = (RAIZ / "core" / "windows.py").read_text(encoding="utf-8")
    assert k03({"core/windows.py": fonte}) == []
    arq = porteiro._Arquivo("core/windows.py", fonte)
    assert arq.ler()
    linhas = [n for n, linha in enumerate(arq.codigo, 1) if porteiro.LICENCA_A_MAO.search(linha)]
    assert linhas and {arq.funcao(n) for n in linhas} == {"dar_licenca_aos_usuarios"}
