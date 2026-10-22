"""Verificador 22/10: quais paginas do PDF mudaram entre antes e depois (desenho a 40 DPI) e os avisos."""
import json, sys
import fitz, numpy as np
t = sys.argv[1]
for livro in ("egenloff_1a14", "marial_300_100"):
    a, b = fitz.open(f"{t}/saida_{livro}_antes.pdf"), fitz.open(f"{t}/saida_{livro}_novo.pdf")
    ja = json.loads(open(f"{t}/tempo_{livro}_antes_2.json", encoding="utf-8").read())
    jb = json.loads(open(f"{t}/tempo_{livro}_novo_2.json", encoding="utf-8").read())
    mud = []
    for i in range(len(a)):
        pa, pb = a[i].get_pixmap(dpi=40), b[i].get_pixmap(dpi=40)
        if (pa.width, pa.height) != (pb.width, pb.height):
            mud.append((i + 1, "tamanho")); continue
        da = np.frombuffer(pa.samples, np.uint8).astype(int); db = np.frombuffer(pb.samples, np.uint8).astype(int)
        d = np.abs(da - db).mean()
        if d > 0.5: mud.append((i + 1, round(d, 1)))
    print(livro, len(a), len(b), "mudaram", len(mud), mud)
    print(" tamanhos antes", sorted(set(map(tuple, ja["tamanhos_mm"])))[:6], "depois", sorted(set(map(tuple, jb["tamanhos_mm"])))[:6])
    av = sorted(set(ja["avisos"]) | set(jb["avisos"]), key=int)
    for k in av:
        x, y = ja["avisos"].get(k), jb["avisos"].get(k)
        if x != y: print("  aviso mudou p", int(k) + 1, x, "->", y)
    print(" com 'Corte deixou algo de fora': antes", [int(k)+1 for k,v in ja["avisos"].items() if any("fora" in s.lower() or "tinta" in s.lower() for s in v)], "depois", [int(k)+1 for k,v in jb["avisos"].items() if any("fora" in s.lower() or "tinta" in s.lower() for s in v)])
