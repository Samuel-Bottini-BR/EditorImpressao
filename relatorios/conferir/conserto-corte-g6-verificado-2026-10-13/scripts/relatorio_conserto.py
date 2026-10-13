"""Monta a conferencia do conserto do corte do G6: o conferencia.json (resumo
e quadros para a pagina do Samuel) e o relatorio nos tres formatos
(relatorio.gravar). Os textos sao do verificador, escritos depois de abrir
todas as imagens; os numeros vem dos arquivos de medida desta pasta
(dados-hoje.json, dados-conserto.json, escuro-na-beirada-mm.json,
velocidade/velocidade.json, conferencias.json).

USO   python relatorio_conserto.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402


def br(valor: float, casas: int = 1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def sinal(valor: float, casas: int = 1) -> str:
    return f"{valor:+.{casas}f}".replace(".", ",")


TRES = "Sempre nesta ordem: como era antes do endireitar novo, como sai hoje, como sai com o conserto."

QUADROS = [
    {
        "id": "cg6-cursus-3", "nome": "Cursus 3: a faixa preta da direita", "tipo": "melhor", "selo": "faixa sumiu",
        "olhar": "A beirada direita da página: a faixa preta larga do meio some na imagem da direita.",
        "texto": "A faixa preta de 1,5 cm que aparecia à direita sumiu. No lugar dela sobra um fio preto fino, "
                 "que vai de quase nada em cima a uns 4 mm embaixo. Nenhuma letra foi cortada.",
        "ressalva": "O fio que sobra é maior que antes do endireitar novo (ali era menos de 1 mm). O risco preto "
                    "em pé perto da beirada esquerda e o fio preto de até 2 mm embaixo existem nas três versões: "
                    "não são deste conserto.",
        "imgs": [("cg6-cursus-3-perto.jpg", "O canto de cima, à direita, de perto. " + TRES),
                 ("cg6-cursus-3-perto2.jpg", "O canto de baixo, à direita, de perto: é onde o fio que sobra é mais largo (uns 4 mm)."),
                 ("cg6-cursus-3-pagina.jpg", "A página inteira nas três versões.")],
    },
    {
        "id": "cg6-matematica-32", "nome": "Matemática 32: a faixa preta mais larga", "tipo": "melhor", "selo": "faixa sumiu",
        "olhar": "O lado direito da folha: hoje há uma faixa preta de quase 4 cm; com o conserto, só o papel.",
        "texto": "A faixa preta de quase 4 cm à direita sumiu; sobra um fio de 1 mm. A folha volta a ter a largura "
                 "do papel (16,7 cm em vez de 20,9 cm). Nada impresso foi cortado.",
        "ressalva": "O preto de baixo (uns 5 cm) continua: ele já existia antes do endireitar novo e aparece nas três "
                    "versões. Em cima fica um fio preto de 1,5 mm (antes do endireitar novo era uma tira de 7 mm).",
        "imgs": [("cg6-matematica-32-perto.jpg", "O canto de cima, à direita, de perto. " + TRES),
                 ("cg6-matematica-32-pagina.jpg", "A página inteira nas três versões: o preto de baixo está nas três.")],
    },
    {
        "id": "cg6-antiphon-260", "nome": "Antiphon 260: o preto de baixo", "tipo": "melhor", "selo": "voltou ao de antes",
        "olhar": "A parte de baixo da folha: a tira preta do meio é bem mais alta que as outras duas.",
        "texto": "A tira preta de baixo, que tinha passado para quase 5 cm, volta para 2 cm, como era antes do "
                 "endireitar novo. A pintura e as letras continuam inteiras.",
        "ressalva": "Os 2 cm de preto que sobram embaixo já existiam antes: tirar isso é outro trabalho "
                    "(seguir a beirada do papel), que está no plano.",
        "imgs": [("cg6-antiphon-260-perto.jpg", "O canto de baixo, à esquerda, de perto. " + TRES),
                 ("cg6-antiphon-260-pagina.jpg", "A página inteira nas três versões.")],
    },
    {
        "id": "cg6-antiphon-88", "nome": "Antiphon 88: o preto da direita", "tipo": "melhor", "selo": "melhor que antes",
        "olhar": "A beirada direita, ao lado do número azul \"II\": quanto preto sobra depois do papel.",
        "texto": "O preto da direita, que estava com 2,6 cm, fica com 2 mm. Ficou melhor até do que antes do "
                 "endireitar novo, quando sobrava quase 1 cm e o número azul saía cortado.",
        "ressalva": "O preto de cima e o de baixo (uns 2,5 cm cada) continuam nas três versões: não são deste conserto.",
        "imgs": [("cg6-antiphon-88-perto.jpg", "O canto de cima, à direita, de perto. " + TRES),
                 ("cg6-antiphon-88-pagina.jpg", "A página inteira nas três versões.")],
    },
    {
        "id": "cg6-camoes-104", "nome": "Camões 104: o fio escuro da esquerda", "tipo": "melhor", "selo": "fio sumiu",
        "olhar": "A beirada esquerda: na imagem do meio há um fio escuro colado na borda.",
        "texto": "O fio escuro de 2 mm que aparecia à esquerda sumiu; fica como era antes do endireitar novo. "
                 "A moldura do desenho continua inteira.",
        "ressalva": "",
        "imgs": [("cg6-camoes-104-perto.jpg", "O canto de cima, à esquerda, de perto. " + TRES),
                 ("cg6-camoes-104-pagina.jpg", "A página inteira nas três versões.")],
    },
    {
        "id": "cg6-pesel-21", "nome": "Pesel 21: o cartão escuro passa a sair cortado rente", "tipo": "misto",
        "selo": "para você decidir",
        "olhar": "A parte de baixo: com o conserto, a legenda fica quase encostada na borda da folha.",
        "texto": "Esta página é um cartão marrom-escuro. Hoje ela sai inteira; com o conserto, o programa corta rente "
                 "ao que está impresso: tira 1 cm à esquerda e 3 cm embaixo, e a legenda fica a 1 ou 2 mm da borda de "
                 "baixo. Nada impresso se perde, e somem as cunhas brancas dos cantos.",
        "ressalva": "Não foi isso que se pediu ao conserto: é efeito de lado. Ele toma o cartão escuro por fundo do "
                    "scanner. Na minha opinião a folha inteira de hoje era melhor para esta página; a legenda colada "
                    "na borda é o mesmo tipo de defeito já anotado no plano (título colado na borda). Só há uma página "
                    "de cartão escuro entre as 89, então não sei como ficam as outras páginas desse livro.",
        "imgs": [("cg6-pesel-21-perto.jpg", "A parte de baixo, de perto. " + TRES),
                 ("cg6-pesel-21-pagina.jpg", "A página inteira nas três versões: as duas primeiras são iguais.")],
    },
    {
        "id": "cg6-egenloff-3", "nome": "Egenloff 3: meio milímetro a menos embaixo", "tipo": "igual", "selo": "quase nada",
        "olhar": "A tarja cinza de baixo, com o nome da biblioteca: a segunda linha de letras miúdas, à direita.",
        "texto": "A folha fica meio milímetro mais curta embaixo. O que fica um pouco mais cortado é a tarja cinza "
                 "que a biblioteca pôs no pé da imagem, não o livro.",
        "ressalva": "A tarja da biblioteca já saía cortada nas três versões.",
        "imgs": [("cg6-egenloff-3-perto2.jpg", "O pé da página, lado direito, de perto. " + TRES),
                 ("cg6-egenloff-3-perto.jpg", "O pé da página, lado esquerdo."),
                 ("cg6-egenloff-3-pagina.jpg", "A página inteira nas três versões.")],
    },
    {
        "id": "cg6-outras-tres", "nome": "Camões 66, Antiphonal 252 e Rariora 155: menos de 1 mm", "tipo": "igual",
        "selo": "quase nada",
        "olhar": "A beirada de cima do Camões 66: o fio escuro do meio some. Nas outras duas, só papel em branco.",
        "texto": "Nestas três o corte anda menos de 1 mm. No Camões 66 some o fio escuro de cima. No Antiphonal 252 "
                 "sai um pouco de papel em branco embaixo, e no Rariora 155 entra um pouco em cima. Nada impresso muda.",
        "ressalva": "No Rariora 155 a folha continua 3,5 cm mais curta do que era antes do endireitar novo (o papel "
                    "em branco de baixo é cortado). Isso já acontece hoje e o conserto não mexe.",
        "imgs": [("cg6-camoes-66-perto.jpg", "Camões 66, o canto de cima, à esquerda. " + TRES),
                 ("cg6-antiphonal1547-252-perto.jpg", "Antiphonal 252, a parte de baixo."),
                 ("cg6-rariora-155-perto.jpg", "Rariora 155, a parte de cima."),
                 ("cg6-camoes-66-pagina.jpg", "Camões 66, a página inteira."),
                 ("cg6-antiphonal1547-252-pagina.jpg", "Antiphonal 252, a página inteira."),
                 ("cg6-rariora-155-pagina.jpg", "Rariora 155, a página inteira: a folha mais curta já vem de hoje.")],
    },
    {
        "id": "cg6-graduale-221", "nome": "Graduale 221: o que tinha melhorado continua bom", "tipo": "igual",
        "selo": "idêntica",
        "olhar": "O número da folha, no alto à direita (\"Cvij\"): inteiro nas duas imagens da direita.",
        "texto": "Com o endireitar novo o número da folha passou a sair inteiro (antes saía cortado). Com o conserto "
                 "a página sai idêntica à de hoje, ponto por ponto: a melhora foi mantida.",
        "ressalva": "O implementador avisa que esta melhora depende de a página estar torta para aquele lado; "
                    "o conserto foi feito de modo a não desfazê-la, e nas páginas conferidas não desfez.",
        "imgs": [("cg6-graduale-221-perto.jpg", "O canto de cima, à direita, de perto. " + TRES),
                 ("cg6-graduale-221-pagina.jpg", "A página inteira nas três versões: as duas da direita são idênticas.")],
    },
    {
        "id": "cg6-marial-7", "nome": "Marial 7: página do gabarito, idêntica", "tipo": "igual", "selo": "idêntica",
        "olhar": "As duas imagens da direita: são a mesma, ponto por ponto.",
        "texto": "Esta é uma das páginas que você aprovou em 12/10. Com o conserto ela sai idêntica à de hoje, "
                 "ponto por ponto. O mesmo vale para todas as páginas do gabarito.",
        "ressalva": "",
        "imgs": [("cg6-marial-7-perto.jpg", "O canto de baixo, à direita, de perto. " + TRES),
                 ("cg6-marial-7-pagina.jpg", "A página inteira nas três versões.")],
    },
]


def velocidade_em_texto(v: dict | None) -> tuple[str, list[str], str]:
    """(frase curta, linhas da tabela em markdown, frase para o item do resumo)."""
    if not v or not v.get("medidas"):
        return ("A velocidade não foi medida (as rodadas não terminaram).", [],
                "RESSALVA: a velocidade não foi medida.")
    linhas = ["| Medida | Hoje | Com o conserto | Diferença | Variação entre rodadas iguais (hoje / conserto) |",
              "|---|---|---|---|---|"]
    piorou = []
    for m in v["medidas"]:
        casas = 2 if "troca" in m["chave"] else 1
        linhas.append(f"| {m['nome']} | {br(m['antes'], casas)} s | {br(m['depois'], casas)} s | "
                      f"{sinal(m['diferenca'], casas)} s ({sinal(m['em_pct'])}%) | "
                      f"{br(m['vai_e_vem_antes'], casas)} s / {br(m['vai_e_vem_depois'], casas)} s |")
        if m["diferenca"] > max(m["vai_e_vem_antes"], m["vai_e_vem_depois"]):
            piorou.append(m["nome"])
    if piorou:
        frase = ("Em " + "; ".join(piorou) + " a diferença foi MAIOR que a variação entre duas rodadas iguais: "
                 "pode ser lentidão de verdade.")
        item = "RESSALVA GRAVE (velocidade): " + frase
    else:
        frase = ("Nenhuma medida ficou mais lenta além da variação entre duas rodadas iguais do mesmo programa: "
                 "nesta medição não apareceu lentidão.")
        item = "BOM (velocidade): " + frase
    return frase, linhas, item


def main() -> int:
    hoje = json.loads((PASTA / "dados-hoje.json").read_text(encoding="utf-8"))
    conserto = json.loads((PASTA / "dados-conserto.json").read_text(encoding="utf-8"))
    arq_vel = PASTA / "velocidade" / "velocidade.json"
    vel = json.loads(arq_vel.read_text(encoding="utf-8")) if arq_vel.exists() else None
    arq_conf = PASTA / "conferencias.json"
    conf = json.loads(arq_conf.read_text(encoding="utf-8")) if arq_conf.exists() else {}
    custo = json.loads((PASTA / "velocidade" / "custo-da-busca-do-corte.json").read_text(encoding="utf-8"))
    import statistics
    a_mais = statistics.median(r["a_mais_ms"] for r in custo.values())

    total = len(hoje)
    mudam = [b for b in sorted(hoje) if hoje[b]["C"]["md5"] != conserto[b]["C"]["md5"]]
    gab_mudam = [b for b in mudam if hoje[b].get("no_gabarito")]
    n_gab = sum(1 for b in hoje if hoje[b].get("no_gabarito"))
    frase_vel, tabela_vel, item_vel = velocidade_em_texto(vel)

    antigo = conf.get("projeto_antigo")
    testes = conf.get("testes")
    item_antigo = (f"BOM: livro começado antes do endireitar novo continua igual: {antigo['identicas']} de "
                   f"{antigo['total']} casos saem idênticos, ponto por ponto, com o conserto."
                   if antigo else "RESSALVA: não conferi por minha conta o livro começado antes (só o implementador).")
    item_testes = (f"BOM: os testes de máquina do corte e da ordem do preparo passam no ramo do conserto "
                   f"({testes['passaram']} passaram, {testes['falharam']} falharam)."
                   if testes else "RESSALVA: não rodei os testes de máquina no ramo do conserto (o implementador rodou).")

    resumo = {
        "paragrafos": [
            "Desde 12/10 o programa endireita a página antes de cortar. Em página torta com borda preta do scanner, "
            "isso deixava a borda preta dentro da folha: uma faixa preta de até 4 cm, que antes era cortada. "
            "Aconteceu em 5 das 89 páginas conferidas.",
            "O conserto ensina o corte a reconhecer a borda preta mesmo depois de a página ser endireitada. "
            "Nas cinco páginas a faixa larga sumiu; sobra, no máximo, um fio preto de 1 a 4 mm na beirada. "
            "Nada impresso foi cortado em nenhuma delas.",
            f"O resto ficou como estava: das {total} páginas, {total - len(mudam)} saem idênticas às de hoje, ponto por "
            "ponto, entre elas todas as do gabarito e 7 das 8 que tinham melhorado com o endireitar novo. "
            "Uma página muda de um jeito que precisa do seu olho: o Pesel 21, um cartão escuro, que passa a sair "
            "cortado rente ao que está impresso.",
        ],
        "veredito": "PRONTO PARA CONFERIR. Na minha opinião o conserto resolve a faixa preta sem estragar o que "
                    "estava bom; a dúvida que fica é o Pesel 21, que eu preferia como sai hoje.",
        "itens": [
            "BOM: nas cinco páginas (Cursus 3, Matemática 32, Antiphon 260, Antiphon 88 e Camões 104) a faixa preta "
            "larga sumiu. Olhei as cinco de perto e na página inteira.",
            "BOM: nada impresso foi cortado nas cinco (Matemática 32, Antiphon 88 e Camões 104, que o implementador "
            "não tinha aberto, incluídas).",
            f"BOM: {total - len(mudam)} das {total} páginas saem idênticas às de hoje, ponto por ponto; as {n_gab} "
            "páginas do gabarito estão entre elas. Medi de novo por minha conta e bateu com o implementador.",
            "BOM: 7 das 8 páginas que tinham melhorado com o endireitar novo saem idênticas (o número da folha do "
            "Graduale 221 e 223 continua inteiro); a oitava, Egenloff 3, muda meio milímetro.",
            item_antigo,
            item_testes,
            item_vel,
            "PARA DECIDIR: Pesel 21 (cartão escuro) passa a sair cortado rente ao conteúdo, com a legenda a 1 ou 2 mm "
            "da borda de baixo. Nada impresso se perde, mas eu preferia a folha inteira de hoje.",
            "RESSALVA: no Cursus 3 sobra um fio preto à direita, de quase nada em cima a uns 4 mm embaixo. "
            "Antes do endireitar novo esse fio tinha menos de 1 mm.",
            "RESSALVA: o conserto só tira o preto que o endireitar novo tinha trazido. O preto que já sobrava antes "
            "(embaixo na Matemática 32, em volta nos Antiphon) continua: é outro trabalho, que está no plano.",
            "RESSALVA: o corte que come os números da margem na Escola 197 (a outra causa, achada na mesma "
            "conferência) não é deste conserto e continua igual.",
            "RESSALVA: são 89 páginas soltas, nenhum livro inteiro, e tudo foi medido sem abrir a janela do programa.",
            "CORREÇÃO do meu relatório de antes: eu tinha escrito que no Cursus 3 havia também uma faixa preta de "
            "0,6 cm embaixo que a ordem antiga cortava. Medindo direto, embaixo há um fio preto de até 2 ou 3 mm "
            "nas três versões; a diferença de verdade é só a faixa da direita.",
        ],
        "tabela": {
            "cab": ["O que foi conferido", "Como", "Resultado"],
            "linhas": [
                ["A faixa preta nas cinco páginas", "olho + máquina",
                 "Sumiu nas cinco. Sobra um fio de 1 a 4 mm (Cursus 3: até 4 mm; Matemática 32: 1 mm; "
                 "Antiphon 88: 2 mm; Camões 104: meio milímetro; Antiphon 260: volta aos 2 cm de antes)."],
                ["Se algo impresso foi cortado nas cinco", "olho", "Nada foi cortado."],
                [f"As {total} páginas, hoje contra o conserto", "máquina",
                 f"{total - len(mudam)} idênticas ponto por ponto; {len(mudam)} mudam (as mesmas dez do implementador)."],
                ["As dez que mudam", "olho", "Cinco melhoram, quatro quase não mudam (menos de 1 mm), "
                                             "uma muda muito (Pesel 21)."],
                ["As páginas do gabarito", "máquina + olho",
                 f"As {n_gab} saem idênticas. Abri as 14 do gabarito do endireitar novo nas três versões."],
                ["As 8 que tinham melhorado", "máquina + olho", "7 idênticas; Egenloff 3 muda meio milímetro embaixo."],
                ["Livro começado antes", "máquina",
                 (f"{antigo['identicas']} de {antigo['total']} idênticos com o conserto." if antigo
                  else "Não conferi por minha conta.")],
                ["Testes de máquina no ramo", "máquina",
                 (f"{testes['passaram']} passaram, {testes['falharam']} falharam ({testes['arquivos']})." if testes
                  else "Não rodei.")],
                ["Velocidade (Marial, 300 folhas)", "máquina", frase_vel],
                ["Custo da busca do corte", "máquina",
                 f"{br(a_mais, 0)} milésimos de segundo a mais por página que gira (valor do meio de 43 páginas)."],
            ],
        },
    }
    quadros = [{**{k: q[k] for k in ("id", "nome", "olhar", "texto", "tipo", "selo", "ressalva")},
                "imgs": [{"src": f"img/{src}", "legenda": leg} for src, leg in q["imgs"]]} for q in QUADROS]
    faltam = [i["src"] for q in quadros for i in q["imgs"] if not (PASTA / i["src"]).exists()]
    assert not faltam, faltam
    conferencia = {"conferencia": "conserto-corte-g6-verificado-2026-10-13",
                   "ramo": "conserto-corte-g6-2026-10-13", "commit": "d97b937",
                   "resumo": resumo, "quadros": quadros}
    (PASTA / "conferencia.json").write_text(json.dumps(conferencia, indent=1, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------ o relatorio
    t: list[str] = []
    t.append("# Conserto do corte do livro novo: conferência do verificador (13/10/2026)\n")
    t.append("Conferi o conserto do implementador (ramo `conserto-corte-g6-2026-10-13`, commit `d97b937`). "
             "Não mudei código e **não marco nada como aprovado**: quem aprova é o Samuel.\n")
    t.append("## Em uma frase\n")
    t.append(f"**{resumo['veredito']}**\n")
    for p in resumo["paragrafos"]:
        t.append(p + "\n")
    t.append("## O que achei\n")
    for item in resumo["itens"]:
        t.append(f"- {item}")
    t.append("")
    t.append("## O que foi conferido e como\n")
    t.append("| " + " | ".join(resumo["tabela"]["cab"]) + " |")
    t.append("|---|---|---|")
    for linha in resumo["tabela"]["linhas"]:
        t.append("| " + " | ".join(linha) + " |")
    t.append("")
    t.append("## As dez páginas que mudam\n")
    mm = json.loads((PASTA / "escuro-na-beirada-mm.json").read_text(encoding="utf-8"))
    t.append("Tamanho da folha em centímetros. \"Escuro na beirada\" é a largura do preto encostado no lado que "
             "mudou (valor do meio, medido direto na página pronta).\n")
    t.append("| Página | Folha: antes do endireitar novo → hoje → conserto | Escuro na beirada: antes → hoje → conserto | O que vi |")
    t.append("|---|---|---|---|")
    antes = json.loads((PASTA.parent / "corte-g6-2026-10-13" / "dados.json").read_text(encoding="utf-8"))
    lado_que_mudou = {"cursus_p003__inteira": ("dir", "direita"), "matematica_p032__inteira": ("dir", "direita"),
                      "antiphon_p260__inteira": ("pe", "embaixo"), "antiphon_p088__inteira": ("dir", "direita"),
                      "camoes_p104__inteira": ("esq", "esquerda"), "camoes_p066__inteira": ("topo", "em cima")}
    vi = {"cursus_p003__inteira": "Faixa sumiu; sobra fio de até 4 mm embaixo. Nenhuma letra cortada.",
          "matematica_p032__inteira": "Faixa sumiu; sobra fio de 1 mm. O preto de baixo (5 cm) está nas três.",
          "antiphon_p260__inteira": "A tira de baixo volta ao tamanho de antes. Pintura e letras inteiras.",
          "antiphon_p088__inteira": "Melhor que antes do endireitar novo; o número azul sai inteiro.",
          "camoes_p104__inteira": "O fio da esquerda sumiu. Moldura inteira.",
          "pesel_p021__inteira": "PARA DECIDIR: cartão escuro cortado rente; legenda a 1 ou 2 mm da borda de baixo. Nada impresso perdido.",
          "egenloff_p003__inteira": "Meio milímetro a menos embaixo; é a tarja da biblioteca, não o livro.",
          "camoes_p066__inteira": "Some o fio escuro de cima.",
          "antiphonal1547_p252__inteira": "Menos de 1 mm de papel em branco a menos embaixo.",
          "rariora_p155__inteira": "Menos de meio milímetro a mais em cima."}
    nomes = {"cursus_p003__inteira": "Cursus 3", "matematica_p032__inteira": "Matemática 32",
             "antiphon_p260__inteira": "Antiphon 260", "antiphon_p088__inteira": "Antiphon 88",
             "camoes_p104__inteira": "Camões 104", "pesel_p021__inteira": "Pesel 21",
             "egenloff_p003__inteira": "Egenloff 3", "camoes_p066__inteira": "Camões 66",
             "antiphonal1547_p252__inteira": "Antiphonal 252", "rariora_p155__inteira": "Rariora 155"}
    assert sorted(nomes) == mudam, (sorted(nomes), mudam)

    def folha(r):
        return f"{br(r['tamanho_mm'][0] / 10)} × {br(r['tamanho_mm'][1] / 10)}"

    for b in nomes:
        tam = f"{folha(antes[b]['B'])} → {folha(hoje[b]['C'])} → {folha(conserto[b]['C'])}"
        if b in lado_que_mudou:
            k, onde = lado_que_mudou[b]
            esc = (f"{onde}: {br(mm[b]['antiga'][k]['mediana'])} → {br(mm[b]['hoje'][k]['mediana'])} → "
                   f"{br(mm[b]['conserto'][k]['mediana'])} mm")
        else:
            esc = "não se aplica"
        t.append(f"| {nomes[b]} | {tam} | {esc} | {vi[b]} |")
    t.append("")

    t.append("## Os quadros\n")
    for q in quadros:
        t.append(f"### {q['nome']}\n")
        t.append(f"**O que olhar:** {q['olhar']}\n")
        t.append(q["texto"] + "\n")
        if q["ressalva"]:
            t.append(f"**Ressalva:** {q['ressalva']}\n")
        for i in q["imgs"]:
            t.append(f"![{i['legenda']}]({i['src']})\n\n*{i['legenda']}*\n")

    t.append("## Velocidade\n")
    t.append(frase_vel + "\n")
    if vel and vel.get("rodadas"):
        t.append("Teste de velocidade do programa com o Marial de 300 folhas, o programa de hoje (`fase-1`) contra o "
                 "ramo do conserto, alternando. Cada rodada repete tudo 3 vezes; o número é o valor do meio.\n")
        t.append("| Rodada | Programa | Hora | Processador antes | Memória livre antes | Outro agente rodando | "
                 "Abrir o livro | Trocar de página | Mágico pro, 10 pág. | Preto e branco, 10 pág. | Durou |")
        t.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in vel["rodadas"]:
            t.append(f"| {r['nome']} | {'hoje' if r['braco'] == 'antes' else 'conserto'} ({r['commit']}) | {r['hora']} | "
                     f"{r['processador_antes_pct']}% | {br(r['memoria_livre_antes_gb'])} GB | "
                     f"{'sim' if (r.get('outros_python_antes') or r.get('outros_python_depois')) else 'não'} | "
                     f"{br(r['abrir_total_s']['mediana'])} s | {br(r['troca_media_s']['mediana'], 2)} s | "
                     f"{br(r['processar_magico_pro_s']['mediana'])} s | {br(r['processar_preto_e_branco_s']['mediana'])} s | "
                     f"{br(r['minutos'])} min |")
        t.append("")
        t.extend(tabela_vel)
        t.append("")
        t.append(conf.get("nota_da_velocidade", "") + "\n")
    t.append(f"Medida direta da busca do corte, nas 43 páginas que giram: o conserto custa {br(a_mais, 0)} milésimos "
             "de segundo a mais por página (valor do meio; a pior, 74). O implementador mediu 18. É uma vez por página.\n")

    t.append("## O que não conferi\n")
    t.append("- Nenhum livro inteiro: são 89 páginas soltas de 19 livros.\n"
             "- Não abri a janela do programa; tudo por linha de comando, a 300 DPI, sem filtro.\n"
             "- Só há uma página de cartão escuro (Pesel 21): não sei como ficam as outras páginas desse tipo.\n"
             "- A regra do conserto que o próprio implementador chama de mais frágil (pedaço grande colado na beirada, "
             "limite de 20%) só foi vista nas 43 páginas que giram.\n"
             "- Não li o código do conserto linha por linha como revisor; conferi o resultado.\n"
             + ("" if testes else "- Não rodei os testes de máquina no ramo.\n")
             + ("" if antigo else "- Não conferi por minha conta o livro começado antes.\n"))
    t.append("## Arquivos\n")
    t.append("- `conferencia.json`: o resumo e os dez quadros para a página do Samuel.\n"
             "- `img/cg6-*.jpg`: de perto e página inteira das dez que mudam, do Graduale 221 e do Marial 7; "
             "`cg6-identicas-01` a `07`: as 19 páginas do gabarito e das que tinham melhorado, nas três versões.\n"
             "- `dados-hoje.json`, `dados-conserto.json`: a minha medida das 89 páginas no livro novo, com o md5 da página pronta.\n"
             "- `escuro-na-beirada-mm.json`: o preto encostado em cada beirada, em milímetros.\n"
             "- `velocidade/`: `rodar_uma.ps1`, `juntar.py`, `velocidade.json`, `rodadas/`, `custo-da-busca-do-corte.json`.\n"
             "- `scripts/`: `medir_conserto.py`, `quadros.py`, `regioes.json`, `relatorio_conserto.py`.\n")
    saida = relatorio.gravar("\n".join(t), PASTA / "conserto-corte-g6-verificado",
                             titulo="Conserto do corte do livro novo: conferência")
    for chave, caminho in saida.items():
        print(chave, caminho.name, caminho.stat().st_size)
    print("quadros:", len(quadros), "imagens nos quadros:", sum(len(q["imgs"]) for q in quadros))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
