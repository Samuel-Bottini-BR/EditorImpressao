"""Prova de quem tenta quebrar (24/11/2026): a K03 do porteiro deixa passar o que a D-837 proíbe?

Roda o porteiro de verdade (regras_dos_agentes.porteiro.conferir_codigo) em arquivos de exemplo, sem gravar nada.
Uso: python prova_porteiro_k03.py <raiz do worktree>"""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from regras_dos_agentes import porteiro  # noqa: E402


def k03(arquivos):
    achados = porteiro.conferir_codigo(arquivos, lambda c: arquivos.get(c))
    return [(a.arquivo, a.linha, a.texto[:60]) for a in achados if a.conferencia == "K03"]


def py(t):
    return textwrap.dedent(t).lstrip("\n")


casos = {
    "0 controle: a funcao certa (deve passar)": {"core/windows.py": py('''
        def dar_licenca_aos_usuarios(raiz):
            ferramenta = pasta_do_sistema() / "icacls.exe"
            return _rodar([ferramenta, raiz, "/grant", "*S-1-5-32-545:(OI)(CI)M", "/T"], 1800)
        ''')},
    "1 Todos (Everyone) com Controle total, na funcao da excecao": {"core/windows.py": py('''
        def dar_licenca_aos_usuarios(raiz):
            ferramenta = pasta_do_sistema() / "icacls.exe"
            return _rodar([ferramenta, raiz, "/grant", "*S-1-1-0:(OI)(CI)F", "/T"], 1800)
        ''')},
    "2 cortar a heranca escrito em dois pedacos, na funcao da excecao": {"core/windows.py": py('''
        def dar_licenca_aos_usuarios(raiz):
            ferramenta = pasta_do_sistema() / "icacls.exe"
            return _rodar([ferramenta, raiz, "/inh" + "eritance:r", "/T"], 1800)
        ''')},
    "3 tirar Usuarios em OUTRA funcao, com o nome da ferramenta em pedacos": {"core/windows.py": py('''
        def outra(raiz):
            return _rodar([pasta_do_sistema() / ("ica" + "cls.exe"), raiz, "/remove", "*S-1-5-32-545"], 60)
        ''')},
    "4 trocar o dono em OUTRA funcao, reaproveitando uma variavel": {"core/windows.py": py('''
        FERRAMENTA = "ica" "cls.exe"
        def outra(raiz):
            return _rodar([pasta_do_sistema() / FERRAMENTA, raiz, "/setown" "er", "*S-1-5-32-545"], 60)
        ''')},
    "5 chamar a funcao da excecao com OUTRA pasta, de outro arquivo": {"atualizacao.py": py('''
        from core import windows
        def liberar_o_windows():
            return windows.dar_licenca_aos_usuarios(Path("C:/Windows"))
        ''')},
}
for nome, arquivos in casos.items():
    r = k03(arquivos)
    print(f"{nome}: {'ACUSADO ' + str(r) if r else 'PASSOU (o porteiro nao acusou)'}")
