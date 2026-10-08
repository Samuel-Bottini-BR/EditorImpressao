"""Rodada 4: a regra do "Para revisar" ajustada pelos "Nao concordo" da rodada 3,
contada nas 89 paginas (59 do estudo + 30 da rodada 3).

Tres contas, todas no resultado do fase-1 de hoje (sinais4.py):
  hoje      o aviso que o programa poe hoje (tinta forte fora do texto > 10%)
  regra3    a regra da rodada 3 (criterio.py), sem mudar nenhum limite
  regra4    a regra ajustada (abaixo)

A regra 4 = a regra 3 com:
  (1) desenho apagado: a mesma conta, agora medida no resultado de verdade
      (com o conserto do desenho claro), sem contar o que fica so na beirada
      (tarja da biblioteca, fundo do scanner); e um terceiro gatilho: um
      PEDACO apagado grande, com tinta de 1,5 altura de linha ao quadrado ou
      mais (a letra T vermelha do Antiphonal 46 some inteira, mas e pouca tinta
      perto da pagina toda, e as contas em fracao nao a pegavam)
  (4) NOVO texto falhado nos dois jeitos: 2 ou mais linhas compridas que o
      preto e branco deixa pela metade, ou todas as linhas da pagina
      (sinais4.letra_falhada) - Camoes 27, Camoes 104, Egenloff 3
  (5) NOVO pagina sem conteudo proprio (em branco ou so mancha do verso):
      quase nenhuma tinta forte (< 0,5% do miolo), no maximo 1 linha forte e
      (3 linhas fracas ou mais, ou nenhuma linha forte) - Egenloff 12, Rariora 8.
      O motivo na lista e outro: "pagina sem conteudo: trocar por pagina branca?"
  A faixa (3) fica como estava (vira aviso do livro quando esta em 70% ou mais
  das paginas do livro).

O GABARITO (o que deveria acontecer) de cada pagina, nesta ordem:
  1. a resposta do Samuel na rodada 3 (Concordo = o que a regra 3 dizia; Nao
     concordo = o contrario), com os acertos escritos em GABARITO_R3 abaixo
     (comentarios dele e o que o conserto mudou);
  2. a resposta dele na rodada 1 (16 paginas), com as 3 do Palatino que o
     conserto consertou (agora "nao vai");
  3. o veredito do estudo (veredito_estudo.py) para as outras: "errada" vai,
     "ok" e "leve" nao vao (na rodada 1 ele disse "nao precisa" para as leves
     que saem iguais ao Preto e branco).
Uso: python regra4.py   (grava <TRABALHO>/regra4.json e imprime as contas)
"""
from __future__ import annotations

import json

import comum
import criterio
from paginas_rodada3 import PAGINAS as P3
from veredito_estudo import VEREDITO

S = json.loads((comum.TRABALHO / "sinais-rodada4.json").read_text(encoding="utf-8"))
R3 = {f"rv3-pag-{b.split('__')[0].replace('_p', '-')}": b for (b, *_r) in P3}

PEDACO_GRANDE = 1.5     # tinta do maior pedaco apagado, em alturas de linha ao quadrado
SEM_CONTEUDO = 0.005

# Respostas literais da rodada 3 (respostas-samuel.md): pagina -> (resposta, o que a regra 3 dizia)
RESP3 = {
    "antiphonal1547_p006": ("concordo", True), "antiphonal1547_p031": ("concordo", True),
    "antiphonal1547_p046": ("concordo", True), "antiphonal1547_p076": ("concordo", True),
    "antiphonal1547_p192": ("concordo", False), "antiphonal1547_p252": ("concordo", True),
    "camoes_p006": ("concordo", True), "camoes_p009": ("concordo", True), "camoes_p011": ("concordo", True),
    "camoes_p027": ("nao", False), "camoes_p066": ("nao", False), "camoes_p104": ("nao", True),
    "egenloff_p003": ("nao", False), "egenloff_p007": ("concordo", False), "egenloff_p012": ("nao", False),
    "egenloff_p047": ("nao", False), "egenloff_p121": ("concordo", False), "egenloff_p131": ("concordo", False),
    "gladstone_p005": ("concordo", False), "gladstone_p018": ("concordo", False),
    "gladstone_p055": ("concordo", False), "gladstone_p096": ("concordo", False),
    "gladstone_p116": ("concordo", False), "gladstone_p136": ("concordo", False),
    "rariora_p008": ("concordo", False), "rariora_p099": ("concordo", False),
    "rariora_p155": ("concordo", False), "rariora_p169": ("nao", False),
    "rariora_p211": ("concordo", False), "rariora_p365": ("concordo", False),
}
# Acertos do gabarito da rodada 3 (por que):
GABARITO_R3 = {
    "camoes_p104": (True, "'Nao concordo' pelo motivo: 'por apagar o titulo do altor embaixo'; deve ir pelo titulo"),
    "rariora_p008": (True, "comentario: 'ele vai para revisao, mas nao pelo motivo da gravura'"),
    "rariora_p169": (False, "o conserto do desenho trouxe a concha de volta: agora sai certa"),
}
# Rodada 1 (respostas-samuel.md da rodada 1)
RESP1 = {
    "palatino_p076": True, "graduale_p222": False, "marial_p454": True, "horas_p014": False,
    "palatino_p067": True, "matematica_p032": True, "siebmacher_p007__esquerda": True,
    "antiphon_p260": True, "boecio_p007": False, "palatino_p066": True, "graduale_p588": False,
    "pesel_p021": True, "palatino_p010": False, "ljs47_p103": True, "horas_p175": False,
    "rhetorica_p034": False,
}
# o conserto do desenho claro trouxe o desenho de volta: o jeito de fabrica agora sai
# como o Preto e branco de sempre (Siebmacher 7 conferido no olho em 07/10: a faixa
# de ornamentos sai igual nos dois; os do Palatino, pelo relatorio do verificador do
# conserto, relatorios/conferir/misto-desenho-apagado-2026-10-06)
CONSERTADAS_PELO_CONSERTO = {"palatino_p076", "palatino_p067", "palatino_p066", "siebmacher_p007__esquerda"}


def bases_89() -> list[str]:
    """As 89 paginas, todas rodadas com o fase-1 de hoje (dados4). O Siebmacher 7
    e 9 foi dividido a mao (comum._dividir), como nas rodadas 1 a 3."""
    return sorted(j.stem for j in comum.DADOS.glob("*.json") if j.stem.split("__")[0] in comum.as_89())


def gabarito(base: str) -> tuple[bool, str]:
    pid = base.split("__")[0]
    if pid in GABARITO_R3:
        return GABARITO_R3[pid]
    if pid in RESP3:
        r, regra = RESP3[pid]
        return (regra if r == "concordo" else not regra), f"resposta da rodada 3 ({r})"
    chave = base if base in RESP1 else pid
    if chave in RESP1:
        if pid in CONSERTADAS_PELO_CONSERTO or base in CONSERTADAS_PELO_CONSERTO:
            return False, "rodada 1 dizia 'vai', mas o conserto trouxe o desenho de volta"
        return RESP1[chave], "resposta da rodada 1"
    v = VEREDITO.get(base, ("ok",))[0]
    return v == "errada", f"veredito do estudo ({v})"


def faixas(bases) -> dict[str, bool]:
    por_livro: dict[str, list] = {}
    for b in bases:
        por_livro.setdefault(b.split("_p")[0], []).append(S[b])
    return {l: criterio.faixa_no_livro(v) for l, v in por_livro.items()}


def motivos4(s: dict, faixa_livro: bool) -> list[str]:
    m = []
    if (s["apagado_junto"] >= criterio.LIMITE_JUNTO or s["apagado_a"] >= criterio.LIMITE_APAGADO
            or s.get("maior_pedaco", 0) >= PEDACO_GRANDE):
        m.append("desenho apagado")
    if s["vazou_da_gravura"] >= criterio.LIMITE_VAZOU:
        m.append("figura além da gravura achada")
    if s.get("beirada_a", 0.0) >= criterio.LIMITE_BEIRADA and not faixa_livro:
        m.append("faixa escura na beirada")
    if s["falhadas_pb"] >= 2 or (s["linhas_contadas"] and s["falhadas_pb"] == s["linhas_contadas"]):
        m.append("texto falhado nos dois jeitos")
    if (s["sem_conteudo"] < SEM_CONTEUDO and s["linhas_fortes"] <= 1
            and (s["linhas_fracas"] >= 3 or s["linhas_fortes"] == 0)):
        m.append("página sem conteúdo")
    return m


def main() -> None:
    bases = bases_89()
    fx = faixas(bases)
    linhas, tab = [], {}
    for b in bases:
        s = S[b]
        livro = b.split("_p")[0]
        g, porque = gabarito(b)
        r3 = criterio.vai_para_a_lista(s, fx[livro])
        m4 = motivos4(s, fx[livro])
        tab[b] = {"gabarito": g, "por_que": porque, "hoje": s["aviso_hoje"], "regra3": r3,
                  "regra4": bool(m4), "motivos4": m4, "dados_da_rodada3": s.get("dados_da_rodada3", False)}
        linhas.append((b, g, s["aviso_hoje"], r3, bool(m4), m4))
    n = len(bases)
    for nome, i in (("hoje", 2), ("regra3", 3), ("regra4", 4)):
        vai = sum(1 for x in linhas if x[i])
        certo = sum(1 for x in linhas if x[i] == x[1])
        falta = [x[0] for x in linhas if x[1] and not x[i]]
        sobra = [x[0] for x in linhas if x[i] and not x[1]]
        print(f"{nome}: vao {vai} de {n}; acertam {certo} de {n}; escapam {len(falta)} {falta}; "
              f"vao sem precisar {len(sobra)} {sobra}")
    print("gabarito: vao", sum(1 for x in linhas if x[1]), "de", n)
    print("faixa vira aviso do livro:", [l for l, v in fx.items() if v])
    for parte, filtro in (("59 do estudo", lambda b: b.split("__")[0] not in RESP3),
                          ("30 da rodada 3", lambda b: b.split("__")[0] in RESP3)):
        sub = [x for x in linhas if filtro(x[0])]
        print(parte, len(sub), {nome: (sum(1 for x in sub if x[i]), sum(1 for x in sub if x[i] == x[1]))
                                for nome, i in (("hoje", 2), ("regra3", 3), ("regra4", 4))})
    for x in linhas:
        if x[2] != x[1] or x[3] != x[1] or x[4] != x[1] or x[5]:
            print(f"  {x[0]:30s} gab={int(x[1])} hoje={int(x[2])} r3={int(x[3])} r4={int(x[4])} {x[5]}")
    (comum.TRABALHO / "regra4.json").write_text(json.dumps(tab, indent=1, ensure_ascii=False),
                                               encoding="utf-8")


if __name__ == "__main__":
    main()
