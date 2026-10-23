"""Reacerta os LIMITES da regra do "Para revisar" para o preparo do livro novo.

Por que: a regra foi acertada (rodada 4, 07/10/2026) em paginas preparadas como
o programa preparava naquele dia - cortar antes de endireitar, conta do
endireitar do programa. Desde 12/10 o livro novo endireita antes de cortar (G6)
e usa a conta do ScanTailor: as mascaras mudam um pouco e 7 das 89 paginas, na
beirada dos limites, trocavam de lado (a letra T do Antiphonal 46 dava 1,43
contra o limite 1,5). Decisao da gerente (13/10): o que o Samuel aprovou foi o
RESULTADO nas 89 paginas (21 vao, 78 certas), nao os numeros dos limites;
reacertar SO os limites, sem mexer na forma da regra.

O que le (nada aqui roda o programa):
  conferir-89-programa-dpi300-completo.json                    preparo do livro novo
  conferir-89-programa-dpi300-preparo-do-estudo-completo.json  preparo do dia do estudo
    (gravados por conferir_89.py --programa --dpi 300 --completo: os sinais
    de cada pagina SEM os atalhos de tempo e com a "guarda" de cada linha)
  <TRABALHO>/regra4.json   o gabarito e a decisao do estudo em cada pagina

Uso:
  python reacertar_limites.py --procurar   procura, limite a limite, os valores
        que mais repetem as decisoes do estudo (nos dois preparos juntos e em
        cada um), ficando o mais perto possivel dos limites originais
  python reacertar_limites.py              compara os limites ORIGINAIS com os
        que estao em core/revisar.py agora e grava reacerto-dos-limites.md
        (pagina por pagina, antes e depois, nos dois preparos)

A conta de decidir daqui (motivos_com) e um ESPELHO de core.revisar.motivos
com os limites soltos; o proprio script confere que, com os limites de
core/revisar.py, os dois dao o mesmo em todas as paginas.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import conferir_89 as C

AQUI = Path(__file__).resolve().parent

# os limites aprovados na rodada 4 (os de core/revisar.py ate 13/10/2026)
ORIGINAIS = {"junto": 0.02, "apagado": 0.025, "pedaco": 1.5, "vazou": 0.10, "beirada": 0.03,
             "sem_conteudo": 0.005, "guarda": 0.62, "guarda_minima": 0.20, "livro": 0.7}

# onde procurar cada limite (em volta do original)
GRADE = {
    "junto": [round(0.010 + 0.0025 * i, 4) for i in range(13)],
    "apagado": [round(0.015 + 0.0025 * i, 4) for i in range(15)],
    "pedaco": [round(0.9 + 0.05 * i, 2) for i in range(17)],
    "vazou": [round(0.06 + 0.01 * i, 2) for i in range(17)],
    "beirada": [round(0.015 + 0.0025 * i, 4) for i in range(27)],
    "sem_conteudo": [round(0.002 + 0.0005 * i, 4) for i in range(15)],
    "guarda": [round(0.50 + 0.01 * i, 2) for i in range(26)],
    "guarda_minima": [round(0.10 + 0.01 * i, 2) for i in range(21)],
}
PREPAROS = {"novo": "conferir-89-programa-dpi300-completo.json",
            "estudo": "conferir-89-programa-dpi300-preparo-do-estudo-completo.json"}
NOMES = {"novo": "preparo do livro novo (G6 + conta do ScanTailor)",
         "estudo": "preparo do dia do estudo (projeto antigo)"}


def limites_de_agora() -> dict:
    from core import revisar

    return {"junto": revisar.LIMITE_JUNTO, "apagado": revisar.LIMITE_APAGADO,
            "pedaco": revisar.PEDACO_GRANDE, "vazou": revisar.LIMITE_VAZOU,
            "beirada": revisar.LIMITE_BEIRADA, "sem_conteudo": revisar.LIMITE_SEM_CONTEUDO,
            "guarda": revisar.LIMITE_GUARDA, "guarda_minima": revisar.GUARDA_MINIMA,
            "livro": revisar.FRACAO_VIRA_AVISO_DO_LIVRO}


def ler(preparo: str) -> dict:
    return {b: v["sinais"] for b, v in json.loads(
        (AQUI / PREPAROS[preparo]).read_text(encoding="utf-8")).items()}


def motivos_com(s: dict, lim: dict, faixa_do_livro: bool) -> list[str]:
    """O espelho de core.revisar.motivos (jeito de fabrica) com os limites soltos."""
    m = []
    if s["apagado_junto"] >= lim["junto"] or s["apagado_a"] >= lim["apagado"] \
            or s["maior_pedaco"] >= lim["pedaco"]:
        m.append("desenho apagado")
    falhadas = sum(1 for g in s["guardas"] if lim["guarda_minima"] <= g < lim["guarda"])
    if falhadas >= 2 or (s["guardas"] and falhadas == len(s["guardas"])):
        m.append("texto falhado")
    if s["sem_conteudo"] < lim["sem_conteudo"] and s["linhas_fortes"] <= 1 \
            and (s["linhas_fracas"] >= 3 or s["linhas_fortes"] == 0):
        m.append("página sem conteúdo")
    if s["vazou_da_gravura"] >= lim["vazou"]:
        m.append("figura além da gravura")
    if s["beirada_a"] >= lim["beirada"] and not faixa_do_livro:
        m.append("faixa na beirada")
    return m


def decidir(sinais: dict, lim: dict) -> tuple[dict, list[str]]:
    """({pagina: motivos}, livros em que a faixa vira aviso do livro)."""
    por_livro: dict[str, list[bool]] = {}
    for base, s in sinais.items():
        por_livro.setdefault(C._livro(base), []).append(s["beirada_a"] >= lim["beirada"])
    faixa = {l: sum(v) / len(v) >= lim["livro"] for l, v in por_livro.items()}
    return ({b: motivos_com(s, lim, faixa[C._livro(b)]) for b, s in sinais.items()},
            sorted(l for l, v in faixa.items() if v))


def contas(motivos: dict, gab: dict) -> tuple[int, int, int]:
    """(vao, certas contra o gabarito, iguais a decisao do estudo)"""
    vao = sum(1 for b in gab if motivos[b])
    certas = sum(1 for b in gab if bool(motivos[b]) == gab[b]["gabarito"])
    iguais = sum(1 for b in gab if bool(motivos[b]) == gab[b]["regra4"])
    return vao, certas, iguais


def nota(lim: dict, dados: dict, gab: dict, quais) -> tuple:
    """Quanto estes limites repetem o estudo nos preparos `quais`: primeiro as
    paginas com a mesma decisao do estudo, depois as certas contra o gabarito."""
    iguais = certas = 0
    for p in quais:
        _v, c, i = contas(decidir(dados[p], lim)[0], gab)
        iguais += i
        certas += c
    return iguais, certas


def procurar(dados: dict, gab: dict, quais) -> dict:
    """Limite a limite (os outros parados), fica com o valor da GRADE de melhor
    nota; no empate, o mais perto do original. Repete ate nada mudar."""
    lim = dict(ORIGINAIS)
    for _volta in range(6):
        mudou = False
        for nome, valores in GRADE.items():
            melhor = max(valores + [ORIGINAIS[nome]], key=lambda v: (
                nota({**lim, nome: v}, dados, gab, quais),
                -abs(v - ORIGINAIS[nome]) / ORIGINAIS[nome]))
            if melhor != lim[nome]:
                lim[nome] = melhor
                mudou = True
        if not mudou:
            break
    return lim


def faixa_do_valor(nome: str, lim: dict, dados: dict, gab: dict, quais) -> tuple[float, float]:
    """Entre que valores da GRADE o limite `nome` pode andar (os outros
    parados) sem piorar a nota: a folga que o limite escolhido tem."""
    alvo = nota(lim, dados, gab, quais)
    bons = [v for v in sorted(set(GRADE[nome] + [lim[nome]]))
            if nota({**lim, nome: v}, dados, gab, quais) == alvo]
    # so o trecho seguido que contem o valor escolhido
    todos = sorted(set(GRADE[nome] + [lim[nome]]))
    a = b = todos.index(lim[nome])
    while a > 0 and todos[a - 1] in bons:
        a -= 1
    while b < len(todos) - 1 and todos[b + 1] in bons:
        b += 1
    return todos[a], todos[b]


# Por que cada pagina que continua diferente do estudo, no preparo do livro
# novo, nao se resolve mexendo so em limite (lido dos numeros das duas rodadas;
# as imagens NAO foram olhadas - isso e do verificador).
PORQUES = {
    "antiphon_p260__inteira": (
        "No preparo novo quase nada da figura fica fora da gravura achada (1,0% da tinta; no dia do "
        "estudo, 15,5%). Limite nenhum separa 1,0% das páginas boas. A página tem faixa na beirada "
        "(7,6%), mas no Antiphon a faixa está em todas as páginas medidas e é aviso do livro."),
    "cursus_p003__inteira": (
        "No preparo novo sobra faixa escura em 7,4% da página (no dia do estudo, 0,5%). Para ela não ir, o "
        "limite da faixa teria de subir de 3% para mais de 7,4%: aí a faixa deixaria de ser aviso do livro "
        "no Egenloff, a Egenloff 47 passaria a ir, e no preparo do projeto antigo duas páginas mudariam de "
        "decisão (medido com --procurar)."),
    "matematica_p072__inteira": (
        "No preparo novo o desenho quase não é apagado (0,3% da tinta; no dia do estudo, 16,6%) e a figura "
        "passa pouco da gravura (3,8%; antes 34%). O gabarito diz que ela não precisava ir: aqui o "
        "programa de hoje acerta e a regra do estudo mandava sem precisar."),
    "opusmajus_p020__inteira": (
        "No preparo novo a figura além da gravura dá 15,5% (no dia do estudo, 8,2%). O Marial 454, que tem "
        "de ir só por este motivo, dá 15,6%: limite nenhum separa os dois."),
    "palatino_p066__inteira": (
        "No preparo novo três linhas guardam 50%, 57% e 62% da tinta (no dia do estudo, uma só). Para ela "
        "não ir, o limite da guarda teria de cair abaixo de 0,57, e o Camões 11 e o Camões 27 (linhas "
        "entre 0,59 e 0,61), que têm de ir, sairiam junto."),
}


def conferir_o_espelho(dados: dict) -> None:
    """Com os limites de core/revisar.py, o espelho e a regra do programa tem
    de dar o mesmo em todas as paginas."""
    from core import analise, revisar

    nomes = {analise.DESENHO_APAGADO: "desenho apagado", analise.TEXTO_FALHADO: "texto falhado",
             analise.PAGINA_SEM_CONTEUDO: "página sem conteúdo",
             analise.FIGURA_ALEM_DA_GRAVURA: "figura além da gravura",
             analise.FAIXA_NA_BEIRADA: "faixa na beirada"}
    lim = limites_de_agora()
    for preparo, sinais in dados.items():
        for base, s in sinais.items():
            falhadas = sum(1 for g in s["guardas"]
                           if revisar.GUARDA_MINIMA <= g < revisar.LIMITE_GUARDA)
            do_programa = revisar.motivos(revisar.Sinais(
                apagado_a=s["apagado_a"], apagado_junto=s["apagado_junto"],
                maior_pedaco=s["maior_pedaco"], vazou_da_gravura=s["vazou_da_gravura"],
                beirada_a=s["beirada_a"], falhadas=falhadas, linhas_contadas=len(s["guardas"]),
                sem_conteudo=s["sem_conteudo"], linhas_fortes=s["linhas_fortes"],
                linhas_fracas=s["linhas_fracas"]), True, 0.0, False)
            assert [nomes[c] for c in do_programa] == motivos_com(s, lim, False), (preparo, base)


def main() -> int:
    gab = C._gabarito()
    dados = {p: ler(p) for p in PREPAROS}
    conferir_o_espelho(dados)

    if "--procurar" in sys.argv:
        for titulo, quais in (("os dois preparos juntos", ("novo", "estudo")),
                              ("so o preparo novo", ("novo",)), ("so o do estudo", ("estudo",))):
            lim = procurar(dados, gab, quais)
            print(f"\n== {titulo}: nota {nota(lim, dados, gab, quais)} "
                  f"(originais: {nota(ORIGINAIS, dados, gab, quais)})")
            print("   mudam:", {k: (ORIGINAIS[k], v) for k, v in lim.items() if v != ORIGINAIS[k]})
            print("   folga:", {k: faixa_do_valor(k, lim, dados, gab, quais) for k in GRADE})
            for p in PREPAROS:
                m, livros = decidir(dados[p], lim)
                print(f"   {p}: vao/certas/iguais ao estudo {contas(m, gab)}; faixa do livro {livros}; "
                      f"diferentes do estudo "
                      f"{[(b, m[b]) for b in sorted(gab) if bool(m[b]) != gab[b]['regra4']]}")
        return 0

    agora = limites_de_agora()
    linhas = ["# Reacerto dos limites do \"Para revisar\" para o preparo do livro novo", "",
              "Gerado por `reacertar_limites.py` (13/10/2026). 89 páginas do estudo, o programa de "
              "verdade a 300 DPI. \"Iguais ao estudo\" = páginas com a mesma decisão (vai / não vai) "
              "que a regra do estudo deu; \"certas\" = contra o gabarito (as respostas do Samuel e o "
              "veredito do estudo).", "",
              "## Os limites", "", "| Limite | Aprovado na rodada 4 | Agora | Folga (sem piorar) |",
              "|---|---|---|---|"]
    quais = tuple(PREPAROS)
    for nome in GRADE:
        a, b = faixa_do_valor(nome, agora, dados, gab, quais)
        marca = " **(mudou)**" if agora[nome] != ORIGINAIS[nome] else ""
        linhas.append(f"| {nome} | {ORIGINAIS[nome]} | {agora[nome]}{marca} | {a} a {b} |")
    linhas += ["", "## As contas", "",
               "| Preparo | Limites | Vão | Certas | Iguais ao estudo | Faixa vira aviso do livro |",
               "|---|---|---|---|---|---|"]
    decisoes = {}
    for p in PREPAROS:
        for rotulo, lim in (("aprovados na rodada 4", ORIGINAIS), ("de agora", agora)):
            m, livros = decidir(dados[p], lim)
            decisoes[(p, rotulo)] = m
            vao, certas, iguais = contas(m, gab)
            linhas.append(f"| {NOMES[p]} | {rotulo} | {vao} | {certas} | {iguais} de {len(gab)} | "
                          f"{', '.join(livros) or 'nenhum'} |")
    linhas += ["", "## Página por página", "",
               "Só as páginas que vão em algum dos casos, ou que deveriam ir. \"sim\" = vai para a "
               "lista; **negrito** = diferente do estudo.", "",
               "| Página | Gabarito | Estudo | Novo, antes | Novo, depois | Antigo, antes | Antigo, depois "
               "| Motivos (novo, depois) |", "|---|---|---|---|---|---|---|---|"]

    def celula(m: list, estudo: bool) -> str:
        texto = "sim" if m else "não"
        return f"**{texto}**" if bool(m) != estudo else texto

    for b in sorted(gab):
        colunas = [decisoes[("novo", "aprovados na rodada 4")][b], decisoes[("novo", "de agora")][b],
                   decisoes[("estudo", "aprovados na rodada 4")][b], decisoes[("estudo", "de agora")][b]]
        if not (gab[b]["gabarito"] or gab[b]["regra4"] or any(colunas)):
            continue
        estudo = gab[b]["regra4"]
        linhas.append(f"| {b.replace('__inteira', '').replace('__', ' ')} | "
                      f"{'sim' if gab[b]['gabarito'] else 'não'} | {'sim' if estudo else 'não'} | "
                      + " | ".join(celula(m, estudo) for m in colunas)
                      + f" | {', '.join(colunas[1]) or '-'} |")
    linhas += ["", "## As que continuam diferentes do estudo, e por quê", ""]
    for p in PREPAROS:
        m = decisoes[(p, "de agora")]
        for b in sorted(gab):
            if bool(m[b]) != gab[b]["regra4"]:
                s = dados[p][b]
                linhas.append(
                    f"- **{b.replace('__inteira', '')}**, {NOMES[p]}: o estudo "
                    f"{'mandava' if gab[b]['regra4'] else 'não mandava'} ({', '.join(gab[b]['motivos4']) or '-'}); "
                    f"agora {'vai' if m[b] else 'não vai'} ({', '.join(m[b]) or '-'}). Sinais: apagado "
                    f"{s['apagado_a']}, amontoado {s['apagado_junto']}, maior pedaço {s['maior_pedaco']}, "
                    f"figura além {s['vazou_da_gravura']}, beirada {s['beirada_a']}, guardas das linhas "
                    f"falhadas ou perto {[g for g in s['guardas'] if 0.1 <= g < 0.75]}. "
                    f"Gabarito: {'vai' if gab[b]['gabarito'] else 'não vai'}. "
                    + (f"**Por que limite não resolve:** {PORQUES[b]}" if p == "novo" and b in PORQUES
                       else "**Sem explicação escrita: conferir.**"))
    linhas += ["", "As imagens destas páginas não foram olhadas pelo implementador: os motivos acima saem "
               "dos números das duas rodadas. Vale o verificador olhar o Cursus 3, o Opus Majus 20 e o "
               "Palatino 66 no preparo novo (as três passaram a ir) e o Antiphon 260 (deixou de ir).", "",
               "## Como os limites foram escolhidos", "",
               "- `pedaco` (o maior pedaço apagado, em alturas de linha ao quadrado): entre 0,8 e 2,0 só "
               "existem duas páginas nas 89, nos dois preparos: a letra T do Antiphonal 46 (1,43 no preparo "
               "novo; 1,57 no do estudo) e a letra L do Antiphonal 76 (2,11 e 2,04). Com 1,5 a letra T "
               "ficava de fora no preparo novo; 1,2 pega as duas nos dois preparos, com folga dos dois lados.",
               "- `guarda_minima` (abaixo dela a linha é dada como \"sumiu inteira\"): entre 0,10 e 0,20 só há "
               "linhas do Egenloff 3 (0,121 e 0,148 no preparo novo; 0,143 no do estudo) e uma do Boécio 22 "
               "(0,15 e 0,199), que sozinha não manda a página. Com 0,20 o Egenloff 3 ficava com uma linha "
               "falhada só no preparo novo; com 0,13 volta a ter duas. **É o reacerto mais apertado: apoia-se "
               "numa linha de uma página.**",
               "- Um conjunto só de limites para os dois preparos (não foi preciso separar por ordem do "
               "preparo): no preparo do projeto antigo nada muda de decisão.",
               "- Não foi tentado mudar a forma da regra. Subir o limite da faixa de 3% para 7,5% daria 77 "
               "certas no preparo novo, mas mudaria as decisões do estudo no preparo antigo e deixaria de "
               "avisar faixas de 3% a 7%: não fiz."]
    (AQUI / "reacerto-dos-limites.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
