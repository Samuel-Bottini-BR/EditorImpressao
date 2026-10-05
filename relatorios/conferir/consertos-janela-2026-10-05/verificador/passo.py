"""Um passo do piloto por chamada (verificador, 05/10/2026).

  passo.py iniciar
  passo.py fora                      -> janela fora da tela, 1600x821 px
  passo.py foco                      -> WM_SETFOCUS so na janela de teste
  passo.py mapa [titulo]             -> janelas e itens com texto
  passo.py clicar TEXTO [TITULO] [n] -> clique nativo (exato)
  passo.py duplo TEXTO [TITULO]
  passo.py menu MENU ITEM            -> menu pelo teclado (setas + Enter)
  passo.py print NOME [TITULO]
  passo.py sonda EXPR
  passo.py resposta_abrir CAMINHO / resposta_pasta CAMINHO
  passo.py fechar
"""
import ctypes
import sys
import time
from pathlib import Path

import piloto as P
import menus as M

SAIDA_PRINTS = P.BASE / "prints"
SAIDA_PRINTS.mkdir(exist_ok=True)


def _fora(h=None):
    h = h or P.principal()
    # moldura visivel 1600x821 px, fora da tela, sem ativar
    P.u32.ShowWindow(h, 4)
    alvo_w, alvo_h = round(P.LOGICO[0] * P.ESCALA), round(P.LOGICO[1] * P.ESCALA)
    import ctypes.wintypes as W
    for _ in range(3):
        r = W.RECT(); P.u32.GetWindowRect(h, ctypes.byref(r))
        l, t, rr, b = P.moldura(h)
        extra_w = (r.right - r.left) - (rr - l)
        extra_h = (r.bottom - r.top) - (b - t)
        P.u32.SetWindowPos(h, 0, -32000, -32000, alvo_w + extra_w, alvo_h + extra_h, 0x4 | 0x10)
        time.sleep(0.5)
    l, t, rr, b = P.moldura(h)
    return rr - l, b - t


def _hwnd(titulo):
    if not titulo:
        return P.principal()
    j = P.janela(titulo, contem=True)
    if j is None:
        raise LookupError(titulo)
    return j["hwnd"]


cmd, args = sys.argv[1], sys.argv[2:]
if cmd == "iniciar":
    h = P.iniciar(*args)
    time.sleep(2)
    print("hwnd", h, "tamanho", _fora(h))
elif cmd == "fora":
    print(_fora(_hwnd(args[0] if args else None)))
elif cmd == "foco":
    h = _hwnd(args[0] if args else None)
    P.u32.SendMessageW(h, 0x0007, 0, 0)   # WM_SETFOCUS
    print("ok")
elif cmd == "mapa":
    for j in P.mapa():
        if args and args[0] not in j["titulo"]:
            continue
        print(f"== {j['titulo']!r} {j['classe']} hwnd={j['hwnd']} {j['w']:.0f}x{j['h']:.0f}")
        for it in j["itens"]:
            t = (it["texto"] or "").replace("\n", " | ")
            if not t and not it.get("dica"):
                continue
            extra = "" if it["ativo"] else " [DESLIGADO]"
            if it.get("marcado") is not None:
                extra += f" marcado={it['marcado']}"
            print(f"  {it['classe']:14s} {t[:110]!r}{extra}")
elif cmd in ("clicar", "duplo"):
    titulo = args[1] if len(args) > 1 and args[1] else None
    n = int(args[2]) if len(args) > 2 else 0
    j, it = P.clicar(args[0], titulo=(P.janela(titulo, contem=True) or {}).get("titulo") if titulo else None,
                     n=n, duplo=(cmd == "duplo"), espera=1.0)
    print("clicado em", j["titulo"], it["classe"], it["texto"])
elif cmd == "menu":
    M.escolher_item(args[0], args[1])
    print("ok")
elif cmd == "print":
    h = _hwnd(args[1] if len(args) > 1 else None)
    f, w, hh = P.printar(args[0], h, pasta=SAIDA_PRINTS)
    print(f, w, hh)
elif cmd == "sonda":
    print(P.sonda(args[0]))
elif cmd == "resposta_abrir":
    (P.AQUI / "resposta_abrir.txt").write_text(args[0], encoding="utf-8")
elif cmd == "resposta_pasta":
    (P.AQUI / "resposta_pasta.txt").write_text(args[0], encoding="utf-8")
elif cmd == "tecla":
    vk = int(args[0], 16) if args[0].startswith("0x") else args[0]
    mods = tuple(args[1].split("+")) if len(args) > 1 and args[1] else ()
    P.tecla(vk, _hwnd(args[2] if len(args) > 2 else None), mods=mods)
    print("ok")
elif cmd == "mover":
    h = _hwnd(args[0])
    P.u32.SetWindowPos(h, 0, -30000, -30000, 0, 0, 0x1 | 0x4 | 0x10)
    print("movida")
elif cmd == "fechar":
    print("fechou" if P.fechar() else "NAO FECHOU")
elif cmd == "erros":
    print(P.erros_log()[-3000:])
else:
    raise SystemExit("comando?")
