"""Verificador, 21/10/2026: conferencia em fotos das etapas 6 e 7 do layout e dos tres acertos, codigo 448299e do ramo
layout-etapas4a7-2026-10-19, para o Samuel (a gerente publica). Mesmo formato da conferencia das etapas 4 e 5
(scripts/montar_conferencia.py). Le os prints img/M*.png (janela de verdade, tirados e abertos por mim em 21/10).
Grava img/c67-*.jpg, conferencia-layout-6-7.json e conferencia-layout-6-7.md/.html/.pdf."""
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
    im.save(IMG / f"c67-{nome}.jpg", quality=90)
    return f"img/c67-{nome}.jpg"


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
    q("l67-tela-cheia", "Filtros em tela cheia",
      "O que você está escolhendo: se a tela cheia dos filtros ficou como você escolheu na rodada 11 (601).",
      "O ícone no canto do título do painel \"Filtro da página\" (e o menu Ver > \"Filtros em tela cheia\") abre a tela: a fila dos filtros à esquerda, o escolhido grande no meio, o ajuste dele à direita. A chave \"Comparar com o Original\" começa desligada; ligada, vira o antes e depois com a linha que se arrasta. Escolher na fila só mostra; \"Usar …\" grava, \"Fechar sem mudar\" não muda nada (conferido: a página continuou em Preto e branco).",
      "A linha do meio com \"antes: Original\" e \"depois: …\".",
      "601 (07/10): \"A — A “um grande”, com a chave “Comparar com o Original”\".", "sim",
      [(corte("comparar", "M10-tela-cheia-comparar", (160, 100, 1270, 740), 1100), "Ampliado: \"Comparar com o Original\" ligado"),
       (inteira("M09-tela-cheia"), "A tela cheia ao abrir (chave desligada)"),
       (inteira("M11-tela-cheia-melhorar"), "Melhorar escolhido na fila, comparando")],
      "O ajuste mexido aqui mostra só o filtro, sem o \"Só as letras\", até \"Usar\"; os outros ajustes do Preto e branco ficam no painel; o antes e depois não aproxima."),
    q("l67-config", "Configurações com a lista das partes à esquerda",
      "O que você está escolhendo: se a tela de Configurações e o lugar da troca de tema ficaram como você escolheu (807 e 707).",
      "\"Configurações\" (no alto da tela dos livros) abre uma janela com a lista das partes à esquerda, \"Aparência\" e \"Atalhos de teclado\". Em \"Aparência\": Escuro, Cinza (de fábrica), Claro. O tema também se troca pelo menu Ver > Tema.",
      "A lista à esquerda e os três temas.",
      "807 (12/10): \"B — Lista das partes à esquerda\"; 707 (12/10): \"C — Nos dois lugares\".",
      "em parte: faltam as partes \"Para todos os livros\" e \"Lado direito\" (ainda não existem)",
      [(inteira("M06-configuracoes"), "A janela de Configurações")]),
    q("l67-livros", "A tela dos livros",
      "O que você está escolhendo: se a tela dos livros ficou como você escolheu na rodada 6 e na página de escolhas (cartão \"+\").",
      "Só os cartões, sem barra de menus. O cartão \"+ Abrir um PDF novo\" vem no começo da grade (clique ou arraste o PDF). No alto: \"procurar pelo nome\", \"Configurações\" e \"Ajuda\". Um clique num livro abre o livro na tela inteira; \"continuar\" vai direto ao trabalho.",
      "O cartão \"+\" no começo e o alto da tela.",
      "\"Como abrir um livro novo?\" (06/10): \"Cartão “+” no começo da grade\"; rodada 6: Configurações e Ajuda no alto, sem barra de menus.",
      "sim",
      [(inteira("M01-tela-dos-livros"), "A tela dos livros")]),
    q("l67-livro-aberto", "O livro aberto na tela inteira",
      "O que você está escolhendo: se o livro aberto ficou como você escolheu na rodada 6.",
      "As páginas rolam uma embaixo da outra, com a coluna de miniaturas à esquerda e a pílula \"página 4 de 6 · ir para\" embaixo. No alto: \"Voltar para os livros (Esc)\", \"Continuar\", \"Rodar o automático…\", \"Ver todas as páginas\", \"Confirmar e processar…\", \"Mais…\" (continuar, começar de novo, renomear, abrir a pasta de saída, remover da lista) e \"Onde está\". \"Ver lado a lado\" é um botão (não vem ligado): mostra as páginas em pares, como o livro aberto.",
      "O botão \"Ver lado a lado\" e as duas páginas lado a lado.",
      "\"O livro aberto fica assim?\" (06/10): \"Sim, fica assim\" + \"quero ter a opção de clicar e ver como ia ficar as paginas lado a lado [...] eu não quero padrão eu quero como opção um botão que eu clique e veja pagina lado a lado.\"",
      "sim",
      [(corte("lado-a-lado", "M03-lado-a-lado", (440, 180, 1600, 821), 1100), "Ampliado: \"Ver lado a lado\" ligado"),
       (inteira("M13-livro-aberto-nitido"), "O livro aberto, uma página por vez (nítida, depois do acerto f963cfd)"),
       (corte("mais", "M04-menu-mais", None, 400), "O menu \"Mais…\"")],
      ""),
    q("l67-acertos", "Os três acertos da conferência anterior",
      "O que você está escolhendo: se os três acertos que eu pedi ficaram bons.",
      "1) O nome \"Melhorar\" cabe inteiro na fila do painel Filtro. 2) As páginas de \"Todas as páginas\" ficaram mais nítidas. 3) A frase de resumo da tela \"O que fazer\" diz \"(jeito: o do Editor)\", como a lista (907 B), com teste de reversão que falha no código de antes.",
      "\"Melhorar\" inteiro na fila; as páginas da grade.",
      "907 (20/10): \"B — “o do Editor”\".", "em parte: a grade continua mole",
      [(corte("melhorar", "M07-filtro-painel", (1180, 150, 1530, 305), 700), "Ampliado: a fila com \"Melhorar\" inteiro"),
       (inteira("M15-todas-30s"), "\"Todas as páginas\" no f963cfd")],
      "A grade de \"Todas as páginas\" continua mole mesmo depois do acerto f963cfd: a página é desenhada no tamanho certo (197 pontos), mas ao pintar ela é reduzida para 150 e aumentada de novo pela escala do Windows (125%)."),
]
OPC = ["Está bom", "Melhorar", "Está pior", "Ainda não entendi"]
RESSALVAS = [
    "Não está como no desenho: \"Para revisar\" e \"Receita usada\" no livro aberto (o resumo não tem esse dado; receitas não existem).",
    "Não está como no desenho: 804 B, o aviso de livro novo (\"ainda não passou pelo automático\"): o livro ainda não abre direto na tela de trabalho.",
    "Não está como no desenho: Configurações sem as partes \"Para todos os livros\" e \"Lado direito\" (não existem ainda).",
    "Tela cheia dos filtros: o ajuste mexido ali mostra só o filtro (sem \"Só as letras\") até \"Usar\"; o antes e depois não aproxima.",
    "\"Todas as páginas\": continua mole depois do acerto f963cfd (a página é reduzida ao tamanho lógico antes de pintar, e a escala de 125% do Windows a aumenta de novo).",
]
PERGUNTA = {"id": "ly-6-7", "titulo": "Layout: etapas 6 e 7: o que você decide?",
            "explicacao": ["O que você está escolhendo: se a tela cheia dos filtros, as Configurações, a tela dos livros e o livro aberto entram no programa.",
                           "Cada quadro é uma coisa que você decidiu, com a foto da janela de verdade. O que ainda não está como no desenho está na lista de ressalvas."],
            "opcoes": ["Aprovado", "Melhorar", "Ainda não entendi"]}
SAIDA = {"aba": "layout etapas 6 e 7", "ramo": "layout-etapas4a7-2026-10-19", "commit": "f963cfd", "montado_em": "21/10/2026",
         "nota_para_a_gerente": "Prints da janela de verdade (1600 x 821), tirados e abertos por mim em 21/10. Não publicado.",
         "ressalvas": RESSALVAS, "quadros": QUADROS, "opcoes_de_cada_quadro": OPC, "pergunta": PERGUNTA}
(PASTA / "conferencia-layout-6-7.json").write_text(json.dumps(SAIDA, ensure_ascii=False, indent=1), encoding="utf-8")

m = ["# Conferência em fotos: layout etapas 6 e 7 e os três acertos (verificador, 21/10/2026)", "",
     "Ramo `layout-etapas4a7-2026-10-19`, código `f963cfd` (etapas 6 e 7 no `448299e`; acerto do livro aberto e da grade no `f963cfd`). Não marco nada como aprovado.", "",
     "## O que conferi", "",
     "- Fora de `ui/` e dos testes nada muda desde o `60a0a3d`.",
     "- Testes, um arquivo por vez: dividir na tela 9, filtros em tela cheia 5, configurações 2, miniaturas 4, menu Painéis 3, painéis na tela 22, barra de menu 20, livro aberto 2, tela de início 15: todos passam.",
     "- Reversão do \"o do Editor\" (`tests/test_dividir_na_tela.py`): falha no `9e6956d` (\"(jeito: o do programa)\"), passa no `448299e`.",
     "- Janela de verdade: tela dos livros, livro aberto (uma por vez e lado a lado, \"Mais…\", Esc volta), Configurações, filtros em tela cheia (abrir pelo ícone, comparar, escolher, \"Fechar sem mudar\" não muda), a fila do Filtro e \"Todas as páginas\". 12 prints, todos abertos.",
     "- Não abri as rodadas do GitHub citadas (39566066549, 39621726467).",
     "- Acerto `f963cfd`: os 2 testes de reversão (`test_a_folha_e_desenhada_na_resolucao_da_tela`, `test_a_grade_desenha_na_altura_do_quadro`) falham no `448299e` e passam no novo. Na janela: o livro aberto ficou nítido; a grade NÃO (nitidez medida 669 contra 1004 antes e 5371 da página desenhada direto nesse tamanho). Causa vista no código: `ui/widgets/todas_as_paginas.py` `_pintar` faz `pix.scaled(alvo.size())` em pontos lógicos (150) e a tela a 125% aumenta de novo; a imagem guardada já tem 197 pontos. O teste só olha a imagem guardada, não o que é pintado.", "",
     "## Ressalvas (o que ainda não está como no desenho)", ""] + [f"- {r}" for r in RESSALVAS] + ["",
     "## As fotos contra as decisões dele", "", "| Quadro | Decisão dele | Bate? |", "|---|---|---|"]
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

print(relatorio.gravar("\n".join(m), PASTA / "conferencia-layout-6-7.md"))
