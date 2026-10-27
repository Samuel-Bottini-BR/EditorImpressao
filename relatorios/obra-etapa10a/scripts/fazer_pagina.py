"""Escreve a página de conferência da etapa 10a (md, html e pdf, por relatorio.gravar).

Lê os tamanhos de relatorios/obra-etapa10a/conferencia/img/<id>.json (feitos por
fazer_conferencia.py) e o texto dos casos abaixo. USO: python fazer_pagina.py
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
PASTA = RAIZ / "relatorios" / "obra-etapa10a" / "conferencia"

CAMINHO = ("Caminho: o programa inteiro (análise do livro, dividir, endireitar, cortar, filtro), como o botão "
           "\"Confirmar e processar\"; imagem tirada da página pronta.")

# (id, título, palavras do Samuel / de onde veio, opções do livro, o que olhar, opinião/ressalva)
CASOS = [
    ("cursus3", "Cursus 3 — o corte comia o começo das linhas (lista única 4.2)",
     "Lista única 4.2 / C-1 (23/10): \"o corte da esquerda comeu a primeira letra ou duas das linhas do bloco de "
     "baixo\". D-104 (22/10): \"Tem mais alguma função que pode fazer essa mesma coisa de comer parte da pagina sem "
     "que a gente queira no nosso programa?\"",
     "Projeto do teste dos 14 livros: livro novo, \"Cortar a beirada da folha vizinha\", \"Achar a página dentro da "
     "borda preta\" (até a moldura), endireitar, cortar; filtro Original (para ver só o corte).",
     "Na esquerda do ANTES falta um quarto da página (o corte da beirada da vizinha ficou colado no texto, o giro "
     "levou o canto, e a caixa do ScanTailor jogou fora o resto). No DEPOIS o texto está inteiro.",
     "Ressalva: no alto à esquerda continua um fio preto da lombada ao lado do \"A\" de \"AD\" (existe também sem o "
     "corte da beirada da vizinha; tirar ele cortaria o \"A\"). Projeto já analisado guarda o corte da beirada "
     "antigo: a folga nova vale numa análise nova do livro."),
    ("siebmacher74", "Siebmacher 74 — folha quase em branco virava uma tira (4.10 / 4.8)",
     "Lista única 4.10 / S-1: \"Faixa preta grossa na beirada esquerda (a lombada não foi cortada mesmo com 'borda "
     "preta' marcada) e borrões pretos espalhados\". A tira era o corte: 2,6 x 8,6 cm.",
     "Projeto do teste: borda preta até a moldura, endireitar, cortar; filtro Preto e branco (o do livro).",
     "ANTES: só uma tira da beirada da folha, que no Preto e branco virou faixa preta. DEPOIS: a folha inteira, sem "
     "o preto do scanner.",
     "Ressalva: a lombada do lado direito (a beirada das outras folhas, castanha) ainda aparece fininha; e esta "
     "folha sai cinza no Preto e branco (é o filtro com uma folha quase sem tinta, não o corte)."),
    ("ljs47-2", "ljs47 2 — a guarda virava uma tira só com a etiqueta (4.8)",
     "Lista única 4.8 / L-3: \"a 2 virou uma tira deitada de 21 × 11 cm só com a etiqueta da biblioteca\".",
     "Projeto do teste: borda preta até a moldura; filtro Original.",
     "ANTES: só a etiqueta. DEPOIS: a guarda inteira, dentro da borda preta.",
     "Ressalva: a beirada larga das outras folhas, à direita, fica (é larga demais para a regra segura)."),
    ("antiphon2", "Antiphon 2 — guarda manchada e o \"usar o corte alargado\" (1.4)",
     "Lista única 1.4 / A-2: \"O corte ficou menor: a página virou uma tira estreita (do meio para a direita) e "
     "perdeu a metade esquerda\". D-098 (13/10): \"ele avisa e da opção e de mudar o corte e mostrar ele alargado "
     "com o que foi tirado.\"",
     "Projeto do teste: borda preta até a moldura, cortar a beirada da vizinha; filtro Original.",
     "ANTES: a caixa do ScanTailor abraçava as manchas (do meio para a direita) e cortava o número \"19\" e o carimbo. "
     "DEPOIS: a folha inteira; não aparece mais o aviso \"Corte deixou algo de fora\", então o botão nem é preciso. "
     "E o corte alargado agora nunca fica menor que o corte que a página tem (teste de máquina).",
     "Ressalva: o lado da tela (o que a prévia mostra antes de a medida chegar) é da etapa 9."),
    ("boecio2", "Boécio 2 — o fio preto na beirada (4.10)",
     "Lista única 4.10 / B-6: \"Ficou um risco preto fino em toda a beirada esquerda\".",
     "Projeto do teste: de fábrica (endireitar, cortar); filtro Preto e branco (o do livro).",
     "Olhar a beirada esquerda: no ANTES o fio preto de cima a baixo; no DEPOIS, nada.",
     ""),
    ("escola197", "Escola 197 — o corte comia os números 1, 2 e 3 da margem",
     "Lista de bugs, 13/10 (verificador do corte): \"Escola 197: na ordem nova o corte come os números 1, 2 e 3 dos "
     "itens, na margem esquerda\".",
     "Livro novo de fábrica só com esta página; filtro Original.",
     "Na esquerda: ANTES os itens começam no travessão; DEPOIS aparecem \"1\", \"2\" e \"3\".",
     "Regra nova (a coluna de números da margem): peças do tamanho das letras da linha ao lado, em coluna (duas ou "
     "mais). Um número sozinho na margem continua de fora."),
    ("boecio8", "Boécio 8 — cunhas brancas do giro (ressalva do G6)",
     "D-095 (12/10): \"Se esse trabalho não mexe nele, porque estamos avaliando isso? o resultado aqui dessa pagina "
     "não seria cortar as bordas pretas?\" — cunhas brancas com corte até a beirada (Boécio 8, Marial 7, Graduale "
     "221).",
     "Livro novo de fábrica; filtro Original.",
     "Nos cantos do ANTES, triângulos brancos (o giro de 1,1 grau); no DEPOIS, com a cor do papel.",
     "Muda as somas de fábrica desta página (só os pontos da cunha, até 1,3 mm da beirada: medido)."),
    ("graduale221", "Graduale 221 — beirada escura e cunha (ressalva do G6)",
     "D-095 (ver acima).", "Livro novo de fábrica; filtro Original.",
     "Na esquerda, o ANTES vai até a beirada escura da folha; o DEPOIS para no papel. O \"Cvij\" do alto continua "
     "inteiro.", "Muda as somas de fábrica desta página (de propósito)."),
    ("marial7", "Marial 7 — cunhas e o fio escuro de cima e de baixo (ressalva do G6)",
     "D-095 (ver acima).", "Livro novo de fábrica; filtro Original.",
     "Em cima e embaixo: o ANTES tinha o fio escuro da beirada e as cunhas brancas.", ""),
    ("siebmacher7", "Siebmacher 7 — a faixa preta do scanner em cima e embaixo",
     "Lista única 4.10 (\"A sombra da lombada fica como faixa preta na beirada\") e D-097 (\"tem que ficar rente a "
     "folha de papel, não pode ter preto ali.\").", "Livro novo de fábrica; filtro Original.",
     "Em cima e embaixo do ANTES, a faixa preta do scanner; no DEPOIS, o papel. A moldura de riscos fica inteira.",
     "Muda as somas de fábrica desta página (de propósito)."),
    ("horas18", "Horas 18 — sobra branca do lado direito (4.4)",
     "Lista única 4.4 / H-2: \"O corte tirou o lado esquerdo da moldura e deixou sobra branca do lado direito: a "
     "página ficou torta no papel\".",
     "Projeto do teste: de fábrica (endireitar, cortar); filtro Melhorar (o do livro).",
     "ANTES: a moldura colada na esquerda e 2 a 3 cm de sobra (com a beirada da folha) na direita. DEPOIS: a moldura "
     "no meio, com folga dos dois lados.",
     "Achado: a moldura NÃO era cortada (está inteira no PDF do teste, conferido ponto por ponto); o defeito era a "
     "sobra da direita. Muda o corte de fábrica de 4 páginas do Livro de Horas do gabarito (13, 14, 26, 27): ver as "
     "três abaixo."),
    ("horas13", "Horas 13 (gabarito) — o mesmo conserto", "Lista única 4.4 (ver acima).",
     "Livro novo de fábrica; filtro Original.", "A direita perde a sobra; a moldura fica inteira.",
     "Ressalva: a esquerda ainda guarda a sobra (há manchas do tamanho de letra perto da beirada)."),
    ("horas14", "Horas 14 (gabarito) — o mesmo conserto", "Lista única 4.4 (ver acima).",
     "Livro novo de fábrica; filtro Original.", "A tabela fica no meio; a moldura inteira.", ""),
    ("horas27", "Horas 27 (gabarito) — o mesmo conserto", "Lista única 4.4 (ver acima).",
     "Livro novo de fábrica; filtro Original.", "Embaixo perde a sobra; a moldura inteira.", ""),
    ("righetti96", "Righetti 96 (folha dupla girada e dividida) — o dividir reto",
     "D-104, quinto lugar: \"Dividir as duas páginas é uma linha reta em pé: numa folha dupla torta, a ponta das "
     "letras perto do meio pode ir para a outra página (suspeita)\".",
     "Livro novo de fábrica com dividir; a folha girada e dividida como na tela; filtro Original; página da direita.",
     "Perto da dobra (esquerda da página) nenhuma letra cortada nem levada para a outra página (provado em três "
     "folhas: 96, 100 e 123). Antes e depois iguais no meio.",
     "Ressalva: a faixa preta do scanner em cima (a tampa branca do scanner vem antes dela) continua. A regra que a "
     "tiraria confundiria uma moldura impressa preta: ficou anotada para a etapa do Righetti."),
]


def main():
    from relatorio import gravar

    linhas = [
        "# Conferência da etapa 10a — o corte não come a página",
        "",
        "Obra de 26/10/2026 (D-014: feita até o fim, você confere tudo no fim). Implementador, ramo "
        "`obra-etapa10a-2026-10-26`. Em cada quadro: o scan, ANTES (o código de 26/10, `11f9ed3`) e DEPOIS, na mesma "
        "escala. " + CAMINHO,
        "",
        "**O que muda no livro de fábrica:** 17 das 32 páginas do gabarito mudam (somas: 45 de 96 iguais). Em 5 só a "
        "cunha do giro, até 1,3 mm da beirada (Boécio 3, Escola 7 e 35, Graduale 222, Siebmacher 9: medido ponto a "
        "ponto); em 12 o corte (Boécio 8 e 22, Graduale 221 e 223, Horas 13, 14, 26 e 27, Marial 7, Rhetorica 18 e "
        "73, Siebmacher 7), as maiores mostradas aqui. O projeto começado antes de 09/10/2026 não muda nada (32 de "
        "32 cortes iguais).",
        "",
        "**Opinião:** PRONTO PARA CONFERIR (não aprovado: só você aprova). O mais grave era a borda preta \"até a "
        "moldura\" comendo páginas inteiras (Cursus 3, Siebmacher 74, ljs47 2, Antiphon 2); está consertado. As "
        "ressalvas estão escritas em cada quadro.",
        "",
    ]
    for id_, titulo, palavras, opcoes, olhar, ressalva in CASOS:
        info_p = PASTA / "img" / f"{id_}.json"
        if not (PASTA / "img" / f"{id_}.jpg").is_file():
            continue
        linhas += [f"## {titulo}", "", f"**De onde veio:** {palavras}", "", f"**Por onde a página passou:** {opcoes}",
                   "", f"**O que olhar:** {olhar}", ""]
        if info_p.is_file():
            info = json.loads(info_p.read_text(encoding="utf-8"))
            a, d = info["antes_cm"], info["depois_cm"]
            def cm(v):
                return f"{v:.1f}".replace(".", ",")
            linhas += [f"Tamanho da página pronta: antes {cm(a[0])} x {cm(a[1])} cm; depois {cm(d[0])} x {cm(d[1])} cm.",
                       ""]
        if ressalva:
            linhas += [f"**Ressalva / nota:** {ressalva}", ""]
        linhas += [f"![{titulo}](img/{id_}.jpg)", ""]
    linhas += [
        "## Imprimir aumentado: agora avisa que CORTA (oitavo lugar da D-104)",
        "",
        "**De onde veio:** Lista de bugs, 22/10: \"Imprimir com escala acima de 100% corta o que passa da metade da "
        "folha; avisa só pela margem pequena\". D-017 (13/10): aumentar \"não corta nada escondido\".",
        "",
        "**O que olhar:** a folha montada em A4 (livreto) com as duas páginas da Escola 7 e 8 a 140%: o que passa da "
        "metade da folha não sai. O aviso novo, palavra por palavra:",
        "",
    ]
    avisos = RAIZ / "relatorios" / "conferir" / "obra-etapa10a" / "imprimir-avisos.txt"
    if avisos.is_file():
        for t in avisos.read_text(encoding="utf-8").splitlines():
            if "CORTADO" in t:
                linhas += [f"> {t}", ""]
    linhas += ["![Folha montada a 140%](img/imprimir140.jpg)", ""]
    linhas += [
        "## Moldura escura antes de desentortar (D-113, `d212-1`)",
        "",
        "**De onde veio:** \"Mas fica anotado para depois da junção isso ser resolvido, porque na verdade, eu acho que "
        "o primeiro passo em uma pagina dessas seria tirar essa moldura preta transformando a pagina em totalmente "
        "branca sem mexer nas letras, ai o desentortador não iria confundir as letras com moldura preta. não é?\"",
        "",
        "**O que foi feito:** o desentortar mede a caixa do texto numa cópia da página com a moldura escura do scanner "
        "pintada de branco (as letras não mudam; a página que sai é a de sempre).",
        "",
        "**Resposta honesta à sua pergunta (\"não é?\"):** em parte. Na página de teste (Marial 41 encurvada, com a "
        "moldura) a curva ainda NÃO é achada, e a foto abaixo mostra igual desligado (esquerda) e ligado (direita). "
        "Medi a causa: com a caixa só do bloco do texto, o desentortar acha a curva; com a caixa que pega também as "
        "notas da margem (\"Prou. 8\", \"Mat. 5. 8\"), não acha - com ou sem a moldura. Ficou como pergunta para você "
        "(no ONDE-PAREI): deixar as notas da margem de fora da caixa que o desentortar segue.",
        "",
        "![Marial 41 encurvada, desligado e ligado](img/d212-curvada2.jpg)",
        "",
    ]
    gravar("\n".join(linhas), PASTA / "conferencia-etapa10a", titulo="Conferência da etapa 10a")


main()
