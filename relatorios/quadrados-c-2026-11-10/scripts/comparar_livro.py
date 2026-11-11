import json, sys
S = sys.argv[1]
M = r"D:\programas\EditorImpressao\.claude\worktrees\quadrados-c\relatorios\quadrados-brancos-2026-11-10\medidas"
def cat(d):
    c = {"muito": [], "visivel": [], "poucos": []}
    for k, v in d.items():
        x = v["manchas_brancas_pct"]
        if x >= 1: c["muito"].append(int(k))
        elif x >= 0.25: c["visivel"].append(int(k))
        elif x >= 0.1: c["poucos"].append(int(k))
    return c
def resumo(nome, d):
    c = cat(d); tot = sum(len(v) for v in c.values())
    print(f"  {nome:22s} com quadrados: {tot:3d} (muito {len(c['muito'])}, visivel {len(c['visivel'])}, poucos {len(c['poucos'])})",
          {k: sorted(v) for k, v in c.items() if len(v) <= 6})
p2 = json.load(open(f"{M}/medida2_pintura_livro.json"))
p2_depois = json.load(open(f"{S}/out/medida_pintura.json"))
for var, hoje, simc in (("melhorar_forte_respeitar", "livro_melhorar_forte_respeitar", "livro_c_melhorar_forte_respeitar"),
                        ("magico_fraco_respeitar", "livro_magico_fraco_sem_respeitar", "livro_c_magico_fraco_respeitar")):
    print(var)
    resumo("hoje (investigacao)", json.load(open(f"{M}/{hoje}_mini.json")))
    resumo("C (simulacao)", json.load(open(f"{M}/{simc}_mini.json")))
    resumo("DEPOIS (programa)", json.load(open(f"{S}/out/livro_depois/{var}_mini.json")))
    for rot, d in (("hoje", p2[f"livro:{'magico_fraco_sem_respeitar' if 'magico' in var else var}"]),
                   ("C sim", p2[f"livro_c:{var}"]), ("DEPOIS", p2_depois[f"{S}/out/livro_depois:{var}"])):
        vals = [x for x in d.values() if x is not None]
        print(f"  medida 2 {rot:7s}: >=2%: {sum(1 for x in vals if x >= 2):3d}  >=0,5%: {sum(1 for x in vals if x >= 0.5):3d}  de {len(vals)}")
    seg = json.load(open(f"{S}/out/livro_depois/{var}.json"))
    s = [v["segundos"] for v in seg.values()]
    print(f"  segundos por pagina (depois, primeira vez, com a procura): media {sum(s)/len(s):.1f}, max {max(s):.1f}")
    try:
        h = json.load(open(f"{M}/{hoje}.json")); hs = [v["segundos"] for v in h.values()]
        print(f"  segundos por pagina (hoje): media {sum(hs)/len(hs):.1f}")
    except Exception as e:
        print("  sem tempo de hoje", e)
