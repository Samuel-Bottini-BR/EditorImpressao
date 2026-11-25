"""Conferência curta D-877, item 2: as frases do bilhete (guardar_frase) e os caminhos sem momento, no código dado.
Só a caixa de mentira. Uso: python -I bilhete_curto.py <raiz> <pasta de trabalho>"""
import json, os, shutil, sys
from pathlib import Path
CODIGO, BASE = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
os.environ["PROGRAMDATA"] = str(BASE / "ProgramData"); os.environ["LOCALAPPDATA"] = str(BASE / "LocalAppData")
os.environ["USERNAME"] = "Kaique"
sys.path.insert(0, str(CODIGO))
import atualizacao, historico, versao  # noqa
from core import fases_da_atualizacao as fases  # noqa
from tests.ajudante_do_atualizador import Prova, NOVA  # noqa
assert str(atualizacao.pasta_do_estado()).startswith(str(BASE)) and str(historico.pasta_de_dados()).startswith(str(BASE))
sys.stdout.reconfigure(encoding="utf-8")
CAIXA = "caixa_de_verdade" in Prova.__init__.__code__.co_varnames
horas = iter(f"2026-11-{d:02d}T10:00:00" for d in range(1, 29))
atualizacao._agora = lambda: next(horas)
R = {}
def limpar():
    for sub in ("ProgramData", "LocalAppData"):
        if (BASE / sub).exists():
            shutil.rmtree(BASE / sub)
    (BASE / "LocalAppData").mkdir()
def abrir(nome, *args, **kw):
    p = Prova(BASE / nome, **({"caixa_de_verdade": True} if CAIXA else {}), **kw)
    assert type(p.win).__name__ == "WindowsFalso"
    p.abrir(*args); p.ligar_a_tela()
    viu = [f"CAIXA: {t}" for _, t in getattr(p.win, "caixas", [])]
    viu += [f"JANELA: {atualizacao.frase_da_falha(e.tipo, e.motivo_da_tela)}" if isinstance(e, fases.MostrarFalha)
            else f"JANELA: {type(e).__name__}" for e in p.tela]
    return p, viu
# A: guardar_frase (o 'Sim' ao fechar que não trocou, motivo outra janela), mostrar, repetir noutro dia
limpar(); versao.VERSAO = "7.0.0"; a = []
atualizacao.guardar_frase(fases.NAO_DEU_AGORA, "7.0.1", fases.MOTIVO_HAVIA_OUTRA_JANELA)
a.append(("nome guardado", atualizacao.ler_estado().get("frase")))
a.append(("abertura 1 atalho", abrir("A1", publicar_nova=False)[1]))
a.append(("abertura 2 atalho", abrir("A2", publicar_nova=False)[1]))
atualizacao.guardar_frase(fases.NAO_DEU_AGORA, "7.0.1", fases.MOTIVO_HAVIA_OUTRA_JANELA)
a.append(("nome guardado noutro dia", atualizacao.ler_estado().get("frase")))
a.append(("abertura 3 atalho", abrir("A3", publicar_nova=False)[1]))
a.append(("abertura 4 atalho", abrir("A4", publicar_nova=False)[1]))
R["A guardar_frase"] = a
# B: a recusa do Windows na reabertura SEM janela ('Sim' ao fechar): GuardarFrase -> próxima abertura mostra uma vez
limpar(); b = []
p, viu = abrir("B1", atualizacao.ARG_CONFERIR_NOVA, "7.0.0", "7.0.1", atualizacao.ARG_SEM_JANELA, publicar_nova=False)
b.append(("reabertura sem janela viu", viu)); b.append(("bilhete", atualizacao.ler_estado().get("frase")))
b.append(("atalho 1", abrir("B2", publicar_nova=False)[1])); b.append(("atalho 2", abrir("B3", publicar_nova=False)[1]))
R["B recusa sem janela"] = b
# C: assinatura recusada na procura (frase 2): uma vez por versão, nunca a cada abertura
limpar(); versao.VERSAO = "0.1.0"; c = []
for i in range(3):
    p, viu = abrir(f"C{i}", chave_da_nova=b"x" * 32)
    c.append((f"abertura {i+1}", viu))
c.append(("vistos", sorted(atualizacao.ler_vistos())))
R["C assinatura recusada"] = c
# D: motor que falta: uma vez por versão
limpar(); d = []
for i in range(3):
    p, viu = abrir(f"D{i}", motores={NOVA: 2}, motores_no_lugar={1})
    d.append((f"abertura {i+1}", viu))
d.append(("vistos", sorted(atualizacao.ler_vistos())))
R["D motor"] = d
print(json.dumps(R, ensure_ascii=False, indent=1))
