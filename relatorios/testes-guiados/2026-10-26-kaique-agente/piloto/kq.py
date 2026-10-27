"""Manda um comando ao piloto e espera a resposta.

  kq.py print NOME
  kq.py clique X Y   [-p NOME] [-a alvo] [-e espera]     (alvo: t=janela de cima, p=principal, n=índice)
  kq.py duplo X Y | direito X Y | mover X Y | rolar X Y N | arrastar X1 Y1 X2 Y2
  kq.py tecla NOME [VEZES] | digitar "texto" | janelas | fecharjanela -a N | esperar -e SEG
"""
import json
import sys
import time
import uuid
from pathlib import Path

TRAB = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\56a8699a-7d20-418a-a239-ac3228d49249\scratchpad\kaique-trabalho")


def recapturar_de_fora(nome, ponto=(None, None)):
    """Menus e listas suspensas saem pretos no PrintWindow feito de dentro do programa; daqui
    (outro processo, sem ajuste de DPI) saem certos e já no tamanho de 1280x657. Refaz os
    prints das janelas de cima e o 'junto'."""
    sys.path.insert(0, str(Path(__file__).parent))
    import piloto as P
    from PIL import ImageDraw, Image
    P.PID = int((TRAB / "pid.txt").read_text())
    import ctypes
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))   # ver em pixels de verdade (senão o menu sai cortado)
    pasta = TRAB / "telas"
    js = P.janelas()
    p = P.principal()
    outras = [j for j in js if p is None or j["hwnd"] != p["hwnd"]]
    if not outras:
        return
    base = pasta / f"{nome}.png"
    junto = Image.open(base).convert("RGB") if base.exists() else None
    pr = p["ret"] if p else [0, 0, 0, 0]
    for i, j in enumerate(reversed(outras)):
        popup = "Popup" in j["classe"] or "ToolTip" in j["classe"]
        im = P.captura(j["hwnd"], so_cliente=not popup)
        if im is None:
            continue
        k = len(outras) - 1 - i
        im.save(pasta / f"{nome}_cima{k}.png")
        print(f"  print (de fora) {nome}_cima{k}.png {im.size}")
        if junto is not None:
            if popup:
                # perto do ponto clicado (a posição de verdade se perde ao pôr fora da tela)
                if ponto[0] is not None:
                    x, y = int(ponto[0]), int(ponto[1]) + 6
                else:
                    x, y = junto.width // 2 - im.width // 2, junto.height // 2 - im.height // 2
            else:
                x, y = (junto.width - im.width) // 2, (junto.height - im.height) // 2
            x = max(0, min(x, junto.width - im.width)); y = max(0, min(y, junto.height - im.height))
            junto.paste(im, (x, y))
            ImageDraw.Draw(junto).rectangle([x - 1, y - 1, x + im.width, y + im.height], outline=(255, 0, 255))
    if junto is not None:
        junto.save(pasta / f"{nome}_junto.png")


def main(argv):
    opts, pos = {}, []
    i = 0
    while i < len(argv):
        if argv[i] in ("-p", "-a", "-e"):
            opts[argv[i]] = argv[i + 1]; i += 2
        else:
            pos.append(argv[i]); i += 1
    acao = pos[0]
    c = {"acao": acao, "id": uuid.uuid4().hex}
    nums = [int(round(float(v))) for v in pos[1:]] if acao in ("clique", "duplo", "direito", "mover", "rolar", "arrastar") else []
    if acao in ("clique", "duplo", "direito", "mover"):
        c["x"], c["y"] = nums[:2]
    elif acao == "rolar":
        c["x"], c["y"], c["n"] = nums[0], nums[1], int(nums[2])
    elif acao == "arrastar":
        c["x"], c["y"], c["x2"], c["y2"] = nums[:4]
    elif acao == "tecla":
        c["nome"] = pos[1]; c["vezes"] = int(pos[2]) if len(pos) > 2 else 1
    elif acao == "digitar":
        c["texto"] = pos[1]
    elif acao == "print":
        c["print"] = pos[1]; c["espera"] = 0.2
    if "-p" in opts:
        c["print"] = opts["-p"]
    if "-a" in opts:
        c["alvo"] = opts["-a"]
    if "-e" in opts:
        c["espera"] = float(opts["-e"])
    fila = TRAB / "fila"
    res = fila / "res.json"
    if res.exists():
        res.unlink()
    tmp = fila / "cmd.tmp"
    tmp.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    tmp.replace(fila / "cmd.json")
    fim = time.time() + 300
    while time.time() < fim:
        if res.exists():
            try:
                r = json.loads(res.read_text(encoding="utf-8"))
            except Exception:
                time.sleep(0.1); continue
            if r.get("id") == c["id"]:
                if not r.get("ok"):
                    print("ERRO", r.get("erro")); print(r.get("tb"))
                for j in r.get("janelas", []):
                    print(f"  janela {j['classe'][:38]:38} '{j['titulo'][:40]}' {j['ret']}")
                for p in r.get("prints", []):
                    print("  print", p)
                if c.get("print"):
                    recapturar_de_fora(c["print"], (c.get("x"), c.get("y")))
                return
        time.sleep(0.1)
    print("SEM RESPOSTA do piloto em 300 s")


if __name__ == "__main__":
    main(sys.argv[1:])
