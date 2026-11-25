"""Conferência curta D-877: o caso L1, só com a caixa de mentira (WindowsFalso), em pasta de trabalho própria.
Uso: python -I l1_curto.py <raiz do código> <pasta de trabalho> <pausa em segundos entre as aberturas>
Aberturas, na mesma conta: recusa 1, recusa 2 (mesma versão), atalho, atalho, recusa 3, atalho."""
import json, os, shutil, sys, time
from pathlib import Path
CODIGO, BASE, PAUSA = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), float(sys.argv[3])
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
os.environ["PROGRAMDATA"] = str(BASE / "ProgramData")
os.environ["LOCALAPPDATA"] = str(BASE / "LocalAppData")
os.environ["USERNAME"] = "Kaique"
(BASE / "LocalAppData").mkdir()
sys.path.insert(0, str(CODIGO))
import atualizacao, historico, versao  # noqa
from core import fases_da_atualizacao as fases  # noqa
from tests.ajudante_do_atualizador import Prova  # noqa
assert str(atualizacao.pasta_do_estado()).startswith(str(BASE))
assert str(historico.pasta_de_dados()).startswith(str(BASE))
assert str(atualizacao.caminho_do_registro()).startswith(str(BASE))
sys.stdout.reconfigure(encoding="utf-8")
CAIXA = "caixa_de_verdade" in Prova.__init__.__code__.co_varnames
versao.VERSAO = "7.0.0"
R = "--conferir"
seq = [("recusa 1", True), ("recusa 2", True), ("atalho", False), ("atalho", False), ("recusa 3", True), ("atalho", False)]
out = []
for i, (nome, recusa) in enumerate(seq):
    if i:
        time.sleep(PAUSA)
    p = Prova(BASE / f"a{i}", publicar_nova=False, **({"caixa_de_verdade": True} if CAIXA else {}))
    assert type(p.win).__name__ == "WindowsFalso"
    args = [atualizacao.ARG_CONFERIR_NOVA, "7.0.0", "7.0.1"] if recusa else []
    p.abrir(*args)
    p.ligar_a_tela()
    viu = [f"CAIXA: {t}" for _, t in getattr(p.win, "caixas", [])]
    viu += [f"JANELA: {atualizacao.frase_da_falha(e.tipo, e.motivo_da_tela)}" if isinstance(e, fases.MostrarFalha)
            else f"JANELA: {type(e).__name__}" for e in p.tela]
    out.append({"abertura": f"{i+1} {nome}", "viu": viu})
vistos = atualizacao.ler_vistos()
out.append({"vistos": sorted(vistos), "bilhete": atualizacao.ler_estado()})
print(json.dumps(out, ensure_ascii=False, indent=1))
