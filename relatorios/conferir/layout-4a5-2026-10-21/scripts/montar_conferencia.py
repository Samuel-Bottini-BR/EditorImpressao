"""Verificador, 21/10/2026: a conferencia em fotos do layout (etapa 4, etapa 5 e a rodada 14 construida) para o
Samuel, codigo 60a0a3d do ramo layout-etapas4a7-2026-10-19. Um quadro por coisa decidida: a parte que muda,
ampliada, e a tela inteira; a decisao literal dele (Plano de layout (rascunho).md). Le os prints img/L*.png (janela
de verdade, 1600 x 821 com a barra de titulo, tirados por mim em 21/10 e abertos um a um). Grava img/c-*.jpg,
conferencia-layout.json (a gerente publica) e conferencia-layout.md/.html/.pdf."""
import json
import sys
from pathlib import Path

from PIL import Image

PASTA = Path(__file__).resolve().parent.parent
IMG = PASTA / "img"
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))


def corte(nome, origem, caixa, largura=1100):
    im = Image.open(IMG / f"{origem}.png").convert("RGB")
    if caixa:
        im = im.crop(caixa)
    if im.width != largura:
        im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    im.save(IMG / f"c-{nome}.jpg", quality=90)
    return f"img/c-{nome}.jpg"


def inteira(origem):
    return corte(f"{origem}-inteira", origem, None, 1600)


def q(id_, nome, escolhendo, caso, olhar, decisao, bate, imgs, ressalva=""):
    assert escolhendo.startswith("O que você está escolhendo:")
    d = {"id": id_, "nome": nome, "explicacao": [escolhendo, caso], "olhar": olhar,
         "decisao_do_samuel": decisao, "bate_com_a_decisao": bate,
         "imgs": [{"src": s, "legenda": l} for s, l in imgs]}
    if ressalva:
        d["ressalva"] = ressalva
    return d


QUADROS = [
    q("ly-paineis", "O menu novo \"Painéis\"",
      "O que você está escolhendo: se o menu \"Painéis\" ficou como você pediu na rodada 14 (903).",
      "Entre \"Ver\" e \"Ajuda\" há o menu \"Painéis\": Propriedades, Filtro da página, Para revisar, Automático, Histórico, \"Fechar o painel\" e \"Ícones da direita\". Os quatro \"Painel: …\" saíram do Ver.",
      "O menu aberto e o nome \"Painéis\" na linha dos menus.",
      "903 (20/10): \"B — Um menu novo, “Painéis”\".", "sim",
      [(corte("menu-paineis", "L02-menu-Paineis", None, 500), "Ampliado: o menu \"Painéis\" aberto"),
       (inteira("L01-conferir"), "A tela inteira: \"Painéis\" entre \"Ver\" e \"Ajuda\"")]),
    q("ly-ver", "As peças novas no menu Ver",
      "O que você está escolhendo: se as peças novas da tela ganharam item no menu Ver, como na rodada 14 (904).",
      "O menu Ver tem Aproximar, Afastar, Ajustar à tela, e agora \"Miniaturas\", \"Ícones da direita\", \"Todas as páginas\" e \"Filtros em tela cheia\", depois \"Modo comparar\" e \"Tema\". \"Ver lado a lado\" ainda não existe no programa.",
      "Os quatro itens do meio do menu.",
      "904 (20/10): \"A — Sim, no menu Ver\".", "sim (falta \"Ver lado a lado\", que ainda não existe)",
      [(corte("menu-ver", "L02-menu-Ver", None, 550), "Ampliado: o menu Ver aberto")]),
    q("ly-pedaco", "\"Só neste pedaço\" sem \"o mesmo da página\"",
      "O que você está escolhendo: se o \"Só neste pedaço\" ficou como você escolheu na rodada 14b (909).",
      "No painel Filtro da página, a parte \"Só neste pedaço\" mostra Original, Preto e branco, Melhorar e Mágico pro, nenhum aceso, e não tem mais o botão \"o mesmo da página\". O pedaço só ganha filtro se o Kaique clicar num.",
      "A lista embaixo de \"Só neste pedaço\": nenhum botão aceso.",
      "909 (20/10): \"B — Sem o botão de cima, nenhum aceso\".", "sim",
      [(corte("pedaco", "L07-so-neste-pedaco", (1170, 500, 1545, 821), 600), "Ampliado: \"Só neste pedaço\" aberto"),
       (inteira("L07-so-neste-pedaco"), "A tela inteira")]),
    q("ly-angulo", "Ângulo posto à mão: as contas continuam à vista",
      "O que você está escolhendo: se o Endireitar com o ângulo à mão ficou como você pediu na rodada 14b (910).",
      "Girei a página à mão (−2,1°). A linha \"ScanTailor −2,0° · Editor −2,0°\" continua embaixo da lista \"Conta\". A frase \"Você girou à mão: −2,1°. As contas voltam com “usar o ângulo do programa”.\" aparece só no balão, quando o mouse passa em cima da linha ou da lista.",
      "A linha \"ScanTailor · Editor\" embaixo da \"Conta\" (o balão só aparece com o mouse em cima; não sai na foto).",
      "910 (20/10): \"A — Os dois ângulos e, embaixo, o seu\" + \"a opção 1, podia aparecer só na hora que passasse o mouse em cima, os angulos continuam embaixo mas a mensagem só aparece quando bota o mouse em cima\".", "sim",
      [(corte("angulo", "L17-angulo-a-mao", (1170, 300, 1545, 700), 600), "Ampliado: o painel do Endireitar depois de girar à mão"),
       (inteira("L17-angulo-a-mao"), "A tela inteira")]),
    q("ly-editor", "\"o do Editor\" no Dividir e no Endireitar",
      "O que você está escolhendo: se as palavras \"o do Editor\" e \"Editor\" ficaram como você escolheu (805 e 907).",
      "No Dividir, a lista \"jeito:\" diz \"o do Editor\" e \"o do ScanTailor\", no painel e na tela \"O que fazer\". No Endireitar, a linha da conta diz \"ScanTailor +0,2° · Editor +0,3°\".",
      "A lista \"jeito:\" do Dividir e a linha da conta do Endireitar.",
      "907 (20/10): \"B — “o do Editor”\"; 805 (12/10): \"C — A conta vira “Editor”\".",
      "em parte: a frase de resumo da tela \"O que fazer\" ainda diz \"(jeito: o do programa)\"",
      [(corte("dividir", "L20-dividir-propriedades", (1170, 300, 1545, 600), 600), "Ampliado: o Dividir, \"jeito: o do Editor\""),
       (corte("o-que-fazer", "L18-o-que-fazer-dividir", (56, 230, 940, 720), 1000), "A tela \"O que fazer\": a lista diz \"o do Editor\", a frase de baixo ainda diz \"o do programa\""),
       (corte("endireitar-conta", "L03-endireitar", (1170, 560, 1545, 800), 600), "O Endireitar: \"ScanTailor +0,2° · Editor +0,3°\"")],
      "A frase de resumo embaixo das opções (\"Vou dividir as 6 folhas em 12 páginas (jeito: o do programa)…\") ficou com a palavra antiga."),
    q("ly-propriedades", "Propriedades em duas partes (Endireitar e Dividir)",
      "O que você está escolhendo: se o painel Propriedades separa o que é da página e o que é do livro, como você escolheu (706).",
      "No Endireitar e no Dividir, o painel tem \"Girar a folha\" no alto, depois \"Só nesta página\" (ou folha) e, embaixo, a caixa \"Para o livro todo\" com \"mudar nas opções do livro…\".",
      "As duas partes, com títulos em letras maiúsculas.",
      "706 (12/10): \"B — Propriedades com duas partes: “Só nesta página” e “Para o livro todo”\".", "sim",
      [(corte("duas-partes", "L03-endireitar", (1170, 86, 1545, 800), 600), "Ampliado: o painel do Endireitar"),
       (inteira("L03-endireitar"), "A tela inteira")]),
    q("ly-marcar", "Propriedades do Marcar",
      "O que você está escolhendo: se o painel Propriedades do Marcar ficou como você escolheu (402 e 701).",
      "Com o Retângulo, o painel mostra \"Girar a folha\", \"Marcar como\" (gravura ou foto, letra e traço, papel), \"Marcação desta página\" (detectar automaticamente, usar em todas, daqui em diante) e \"Foto\". A fila embaixo da página ficou vazia.",
      "As partes do painel e a contagem \"Marcado: 6 de letra e traço e 8 de papel.\"",
      "402 (06/10): \"C — Muda conforme a ferramenta (como no Photoshop)\".",
      "sim (\"Marcar como\" ainda com 3 jeitos: a 705, iluminura e moldura, mexe no processamento)",
      [(corte("marcar", "L05-marcar", (1170, 86, 1545, 760), 600), "Ampliado: Propriedades do Retângulo"),
       (inteira("L05-marcar"), "A tela inteira")]),
    q("ly-filtro", "O painel \"Filtro da página\"",
      "O que você está escolhendo: se o painel Filtro ficou como você escolheu na rodada 9 (403).",
      "No alto, a fila com a página pequena nos cinco filtros e a tecla de cada um. Embaixo, partes que abrem e fecham: Ajuste, Só as letras, Limpar a sujeira (lista com amostra), Mais ajustes, Só neste pedaço. Depois \"apagar página\", separado, e no pé \"Aplicar em: só nesta · todas · daqui em diante\". O ícone do canto do título abre os filtros em tela cheia.",
      "A fila dos filtros, as partes e o pé \"Aplicar em\".",
      "403 (06/10): \"B — Filtros numa fila + partes que abrem e fecham\" + \"Mas eu vou querer uma opção para conseguir abrir os filtros para ver um review de como ficaria com cada filtro, abrir em tela cheia, com as opções de cada filtro nessa tela cheia.\"",
      "sim (a tela cheia é a etapa 6, não conferida aqui)",
      [(corte("filtro", "L08-limpar", (1170, 86, 1545, 821), 600), "Ampliado: o painel com \"Limpar a sujeira\" aberto"),
       (inteira("L06-filtro"), "A tela inteira")],
      "Na fila, o nome \"Melhorar\" sai cortado (\"Melhora\"). Acerto pendente."),
    q("ly-cabecalho", "O cabeçalho das miniaturas e \"ver todas\"",
      "O que você está escolhendo: se o cabeçalho das miniaturas e o botão de \"Todas as páginas\" ficaram onde você escolheu (808).",
      "Em cima das miniaturas há o cabeçalho \"PÁGINAS\" (\"FOLHAS\" no Dividir): a alça de arrastar, a seta, os três pontinhos (\"Ver em pares\", \"Lugar\", \"Fechar as miniaturas\") e \"ver todas\".",
      "A linha \"PÁGINAS ˅ ••• ver todas\" e o menu dos três pontinhos.",
      "808 (12/10): \"A — No cabeçalho das miniaturas\".", "sim",
      [(corte("cabecalho", "L01-conferir", (56, 640, 1600, 821), 1200), "Ampliado: o cabeçalho e as miniaturas"),
       (corte("menu-miniaturas", "L12-menu-lugar", None, 450), "O menu dos três pontinhos")]),
    q("ly-todas", "\"Todas as páginas\" abre uma a uma",
      "O que você está escolhendo: se a tela \"Todas as páginas\" ficou como você escolheu na rodada 14 (901).",
      "\"ver todas\" abre a tela com uma página em cada quadro (\"uma a uma\" aceso), com \"em pares\", \"todas\" e \"só as que precisam de atenção\". Clicar numa página leva até ela; \"voltar ao trabalho\" fecha.",
      "\"uma a uma\" aceso no alto.",
      "901 (20/10): \"A — Uma a uma\".", "sim",
      [(inteira("L09-todas-as-paginas"), "A tela \"Todas as páginas\"")],
      "As páginas pequenas desta tela saem borradas. Acerto pendente."),
    q("ly-pares", "Miniaturas em pares e em outro lugar",
      "O que você está escolhendo: se as miniaturas em pares e o lugar delas ficaram como você escolheu (rodada 7 e 801).",
      "\"Ver em pares\" junta as miniaturas como no livro aberto: a 1 sozinha, depois 2-3, 4-5. Com as miniaturas à esquerda (ou fechadas), o \"Confirmar e processar\" desce para a barra de baixo, no canto direito. \"Ver > Miniaturas\" traz de volta as miniaturas fechadas.",
      "O botão azul \"Confirmar e processar\" no canto de baixo quando as miniaturas saem de baixo.",
      "801 (12/10): \"A — Desce para a barra de baixo, no canto direito\".", "sim",
      [(corte("pares", "L11-em-pares", (56, 640, 1600, 821), 1200), "Ampliado: em pares, embaixo"),
       (inteira("L14-miniaturas-a-esquerda"), "Miniaturas à esquerda: o \"Confirmar e processar\" na barra de baixo"),
       (inteira("L15-miniaturas-fechadas"), "Miniaturas fechadas")]),
]
OPC = ["Está bom", "Melhorar", "Está pior", "Ainda não entendi"]
PERGUNTA = {"id": "ly-4a5", "titulo": "Layout: etapa 4, etapa 5 e a rodada 14: o que você decide?",
            "explicacao": ["O que você está escolhendo: se estas partes da tela nova entram no programa.",
                           "Cada quadro acima é uma coisa que você decidiu, com a foto da janela de verdade. Ficaram dois acertos pequenos (o nome \"Melhorar\" cortado e as páginas borradas em \"Todas as páginas\") e uma palavra antiga na frase da tela \"O que fazer\"."],
            "opcoes": ["Aprovado", "Melhorar", "Ainda não entendi"]}
SAIDA = {"aba": "layout etapas 4 e 5 + rodada 14", "ramo": "layout-etapas4a7-2026-10-19", "commit": "60a0a3d",
         "montado_em": "21/10/2026",
         "nota_para_a_gerente": ("Prints da janela de verdade (1600 x 821), tirados e abertos por mim em 21/10. As etapas 6 e 7a "
                                 "estão no mesmo código e não entram aqui. Formato: o do 2.8/2.9 (quadros com \"O que você está escolhendo\", "
                                 "a parte ampliada e a tela inteira, a decisão literal)."),
         "ressalvas": ["Na fila do painel Filtro, \"Melhorar\" sai cortado.",
                       "Em \"Todas as páginas\" as páginas pequenas saem borradas.",
                       "A frase de resumo da tela \"O que fazer\" diz \"(jeito: o do programa)\" (devia ser \"o do Editor\", 907 B)."],
         "quadros": QUADROS, "opcoes_de_cada_quadro": OPC, "pergunta": PERGUNTA}
(PASTA / "conferencia-layout.json").write_text(json.dumps(SAIDA, ensure_ascii=False, indent=1), encoding="utf-8")

m = ["# Conferência em fotos: layout etapa 4, etapa 5 e rodada 14 (verificador, 21/10/2026)", "",
     "Ramo `layout-etapas4a7-2026-10-19`, código `60a0a3d`. Para a gerente publicar. Não marco nada como aprovado.", "",
     "## Ressalvas", ""] + [f"- {r}" for r in SAIDA["ressalvas"]] + ["", "## As fotos contra as decisões dele", "",
     "| Quadro | Decisão dele | Bate? |", "|---|---|---|"]
for x in QUADROS:
    m.append(f"| {x['nome']} | {x['decisao_do_samuel']} | {x['bate_com_a_decisao']} |")
for x in QUADROS:
    m += ["", f"## {x['nome']}", ""] + [p + "\n" for p in x["explicacao"]]
    m += [f"**O que olhar:** {x['olhar']}", "", f"**Sua decisão:** {x['decisao_do_samuel']}", ""]
    if x.get("ressalva"):
        m += [f"*Ressalva:* {x['ressalva']}", ""]
    m += [f"Opções: {' · '.join(OPC)} · e um comentário.", ""]
    for i in x["imgs"]:
        m += [f"![{i['legenda']}]({i['src']})", "", f"*{i['legenda']}*", ""]
m += [f"## Decisão: {PERGUNTA['titulo']}", ""] + [p + "\n" for p in PERGUNTA["explicacao"]] + [f"Opções: {' · '.join(PERGUNTA['opcoes'])}", ""]
import relatorio  # noqa: E402

print(relatorio.gravar("\n".join(m), PASTA / "conferencia-layout.md"))
