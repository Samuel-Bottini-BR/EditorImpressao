"""20/10/2026: fecha a SEGUNDA CONFERENCIA do "Para revisar" (retomada a pedido da gerente).

Roda o segunda.py sem gravar (para montar tudo o que ele monta) e acrescenta o que foi feito em 20/10:
as 19 imagens abertas, as quatro paginas reabertas na janela (Opus Majus 20, Cursus 3, Camoes 66,
Antiphon 260), o teclado conferido pelo codigo, as fotos comparadas com as decisoes do Samuel, a
velocidade mandada para a Fase 5. Grava o conferencia.json e o relatorio nos tres formatos.
Nao mede nada e nao muda o programa."""
import json
import runpy
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import montar_conferencia as M  # noqa: E402

BASE = M.BASE
_main = M.main
M.main = lambda: None                       # o segunda.py so monta; quem grava e este
runpy.run_path(str(AQUI / "segunda.py"), run_name="segunda")
M.main = _main

R3 = json.loads((AQUI / "aba4_quadros_reabertos.json").read_text(encoding="utf-8"))
VISTO = json.loads((AQUI / "imagens_vistas_20-10.json").read_text(encoding="utf-8"))

M.TITULO = "# Segunda conferência do \"Para revisar\" (Fase 2), 13/10/2026, terminada em 20/10/2026"
M.NOTA_COMMIT = ("A primeira conferência (commit `2d820d6` deste ramo) foi em `36b9e32`. A retomada de 20/10 (as imagens, as quatro "
                 "páginas e a aba 4) foi no mesmo `ce2b835`, numa pasta de dados nova (`trabalho/dados_teste3`).")
M.VEREDITO = VISTO["veredito"]
M.ITENS = VISTO["itens_antes"] + M.ITENS + VISTO["itens_depois"]
M.ITENS = [i for i in M.ITENS if not any(i.startswith(t) for t in VISTO["tirar_itens_que_comecam_com"])]

# os quadros das quatro paginas reabertas: o texto novo (o do aba4_quadros_reabertos.json) e as imagens de 20/10
por_id = {q["id"]: q for q in M.QUADROS}
for q in R3:
    velho = por_id[q["id"]]
    velho.update({"nome": q["nome"], "tipo": q["tipo"], "selo": q["selo"], "olhar": q["olhar"],
                  "texto": " ".join(q["explicacao"][1:]) + " " + q["texto"], "ressalva": q["ressalva"],
                  "imgs": [{"src": i["src"], "legenda": i["legenda"]} for i in q["imgs"]]})

# cada quadro ganha, na ressalva, a decisao do Samuel e se a foto bate com ela (feito pelo aba4.py)
ABA4 = json.loads((BASE / "conferencia-aba4.json").read_text(encoding="utf-8"))
for q in ABA4["quadros"]:
    alvo = por_id[q["id"]]
    fotos = sorted({i["situacao"].split(":")[0] for i in q["imgs"]})
    extra = f" Decisão do Samuel: {q['decisao_do_samuel']} Bate com a decisão: {q['bate_com_a_decisao']}. Fotos: {', '.join(fotos)}."
    if q.get("nota_para_a_gerente"):
        extra += " " + q["nota_para_a_gerente"]
    alvo["ressalva"] = (alvo.get("ressalva") or "").strip() + extra

_tabela = M.tabela


def tabela3(vel):
    linhas = _tabela(vel)
    for t in linhas:
        if t["o_que"].startswith("4. Teclado"):
            t["como"] = "janela (nunca ativa) + código"
            t["resultado"] = VISTO["teclado"]
        if t["o_que"].startswith("Velocidade"):
            t["resultado"] += " Decidido pelo Samuel em 19/10: fica para a Fase 5 (\"vamos deixar esse concerto de lentidão para o final\")."
    linhas += [{"o_que": a, "como": b, "resultado": c} for a, b, c in VISTO["tabela_nova"]]
    return linhas


M.tabela = tabela3
M.NAO_CONFERI = VISTO["nao_conferi"]
M.BUGS = [tuple(b) for b in VISTO["bugs"]] + [b for b in M.BUGS if not any(b[1].startswith(t) for t in VISTO["tirar_bugs_que_comecam_com"])]
M.EXTRA_MD = M.EXTRA_MD + "\n" + VISTO["md"]
M.EXTRA_JSON = dict(M.EXTRA_JSON, retomada_20_10=VISTO["json"])
M.EXTRA_COMO = M.EXTRA_COMO + VISTO["como"]
M.main()
