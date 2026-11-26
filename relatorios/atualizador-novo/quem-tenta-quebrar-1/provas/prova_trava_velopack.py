"""Prova de quem tenta quebrar (24/11/2026): a trava do Velopack (so core/conversa_com_o_velopack.py importa velopack)
acusa os outros jeitos de carregar a biblioteca? Usa as funcoes de verdade da trava (tests/test_trava_windows.py) em
arquivos de exemplo, sem ler o disco. Uso: python prova_trava_velopack.py <raiz do worktree>"""
import sys

sys.path.insert(0, sys.argv[1])
from tests.test_trava_windows import _conferir, _programa  # noqa: E402

casos = {
    "import velopack (controle)": '"""x."""\nimport velopack\n',
    "importlib.import_module": '"""x."""\nimport importlib\nvp = importlib.import_module("velopack")\n',
    "__import__": '"""x."""\nvp = __import__("velopack")\n',
}
for nome, texto in casos.items():
    print(f"{nome}: {_conferir(_programa(core_P_usa=texto)) or 'PASSOU (a trava nao acusou)'}")
