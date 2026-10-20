"""20/10/2026: o que o verificador viu na retomada (as 19 imagens, as quatro paginas reabertas, o
teclado, as fotos contra as decisoes) - grava imagens_vistas_20-10.json, que o terceira.py le.
Os textos sao escritos aqui, a mao, depois de abrir cada imagem. Nao mede nada."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent

DEZENOVE = [
    ("duplo-clique-1-aviso-continua-recorte", "Antiphonal 46 (pedaço de 6 páginas): cinco cartões com o quadrado laranja no T, o aviso \"Pode ter sumido parte de um desenho...\" de pé e os botões \"Trazer de volta nesta página\" e \"está bom assim\". O aviso continuou depois dos dois cliques. Bate com o parecer."),
    ("duplo-clique-2-ver-de-perto", "\"Ver de perto\", página 3 de 6, Preto e branco: a letra T aparece (é a tela que engana). Bate."),
    ("teclado-1-recorte", "Egenloff, página 13 escolhida na tira (moldura azul) e \"Esta página vai sair em Preto e branco\": a barra de espaço avançou da 12 para a 13. Bate."),
    ("teclado-2-tela", "A mesma tela inteira, 1280 x 657 (com as abas da tela antiga). Bate."),
    ("forca-1-camoes-recorte", "Camões 27: aviso \"O texto desta página saía falhado: escureci a força do preto só nela\", medidor em \"bem forte\", \"Desfazer\" e \"está bom assim\". Bate. (Print da primeira conferência; o comportamento no Camões 27 não mudou.)"),
    ("forca-2-camoes-tela", "Camões 27 na tela inteira, painel \"Para revisar 35\", \"Desfazer\". Bate."),
    ("forca-4-egenloff-3-recorte", "Egenloff 3 (folha de rosto): só o aviso \"Texto falhado\" (aviso 1 de 2), força \"normal\", botões \"usar mais escuro\" e \"está bom assim\"; marcas laranja na linha do carimbo embaixo. Bate: a força não mexe mais sozinha."),
    ("sem-conteudo-1-egenloff-recorte", "Egenloff 12 (verso só com o carimbo): aviso \"Esta página parece não ter nada do livro\" (aviso 1 de 2) e os três botões. Bate."),
    ("sem-conteudo-2-egenloff-tela", "A mesma tela inteira, painel \"Para revisar 6\". Bate."),
    ("sem-conteudo-5-rariora-recorte", "Rariora 8 (folha de rosto com o título muito fraco): o mesmo aviso, com os três botões. Bate. Repare: o cartão do Preto e branco ainda mostra a página amarelada, quase igual ao Original (a prévia talvez ainda não tivesse chegado)."),
    ("janela-diferente-1-graduale-221-recorte", "Graduale 221 (página 3 do pedaço): quatro cartões e a faixa \"Esta página vai sair em Preto e branco\", sem aviso. Bate."),
    ("janela-diferente-2-graduale-221-tela", "A mesma tela inteira: a página 3 sem \"!\" na tira (a 1 tem). Bate."),
    ("marcar-2-antes-tela", "Aba Marcar, Graduale 221: \"Marcado: 4 de letra e traço e 5 de papel\" (9 áreas). Bate. Repare: na aba Marcar o painel diz \"Para revisar: nada pendente\"."),
    ("marcar-3-depois-tela", "A mesma página uns 10 s depois: \"Marcado: 7 de letra e traço e 11 de papel\" (18 áreas); a diferença à vista é pequena (faixas à esquerda). Bate."),
    ("palatino-66-3-tela", "Palatino 66: marcas laranja na linha \"Palatinus Romae\", aviso \"Texto falhado\", força \"normal\", \"usar mais escuro\". Bate."),
    ("parece-em-branco-2-tela", "Gladstone 18: os cartões com o título \"DA ORAÇÃO\" pequeno e o aviso \"Esta página parece estar em branco...\", com os três botões. Bate (o aviso é o erro conhecido)."),
    ("contagens-2-painel-tela", "Camões 66: painel \"Para revisar 39\", aviso do Endireitar e só \"está bom assim\". Bate (o 39 da pergunta)."),
    ("contagens-3-salvar", "Janela \"Onde salvar o livro pronto\": \"Ainda há 106 página(s) que você não conferiu\" e \"106 páginas vão para o PDF\". Bate (o 106 da pergunta)."),
    ("bug-duplo-clique-tira-o-aviso-tela", "Apesar do nome, é a tela DEPOIS do conserto: pedaço do Antiphonal, página 3 com o aviso de pé e os dois botões. Bate com o quadro dos dois cliques (o nome do arquivo vem da primeira conferência e engana)."),
]

QUATRO = [
    ("Opus Majus 20", "livro novo (a página do gabarito), janela + PDF processado até \"Ficou pronto!\"",
     "Avisos \"Figura além da gravura\" e \"Endireitar\". No PDF a foto da estátua sai DESTRUÍDA (estátua branca, manchas e blocos pretos). "
     "O parecer de 13/10 estava ERRADO (\"a foto sai intacta, não precisava ir\"): aquela imagem era da prévia pequena. O aviso está certo. "
     "O programa de hoje (fase-1) desenha a mesma página igual, ponto por ponto: o estrago já existia; só o aviso mudou."),
    ("Cursus 3", "pedaço das folhas 1 a 10, livro novo, janela",
     "Só o aviso \"Faixa escura na beirada\"; faixa preta larga à direita e linha à esquerda. Confirma o parecer. "
     "O livro inteiro (402 folhas) parou 2 vezes na análise com MemoryError (\"Aconteceu um problema inesperado\")."),
    ("Antiphon 260", "pedaço das folhas 256 a 264, livro novo, janela, visitando 259, 261 e 262",
     "1ª visita: \"Faixa\" + \"Endireitar\"; depois das outras: só \"Endireitar\" (a faixa virou frase do livro, meio escondida no alto do painel). "
     "Iluminura chapada no Preto e branco, sem aviso. Confirma o parecer."),
    ("Camões 66", "livro inteiro, livro novo, janela, visitando 65, 67, 27 e 104",
     "Só o aviso do Endireitar; nenhum aviso das linhas pretas (página ou livro). 27 e 104 com a força sozinha em 85. Confirma o parecer."),
]

TECLADO = ("Em parte, e agora explicado. O botão do aviso não fica com o teclado e a barra de espaço faz \"está certo e avança\". "
           "A seta: o programa só troca de página quando a tecla chega à janela principal (ui/janela_principal.py, keyPressEvent); "
           "antes ela passa por quem está com o teclado, e a tira de miniaturas (rola) e o medidor da força (muda a força da página, "
           "que o programa grava sozinho uns instantes depois) usam a seta. Isso não depende da janela estar ativa, e é igual no fase-1. "
           "Não testei com o teclado de verdade (não tomo o teclado do Samuel).")

VEREDITO = ("PRONTO PARA CONFERIR no que o ramo faz: os consertos valem na janela, confirmados de novo em 20/10 (as 19 imagens e as quatro páginas). "
            "MAS a conferência NÃO deve ir ao Samuel com estas fotos: elas são da tela de antes do layout que ele aprovou (no fase-1 desde 14/10), "
            "e o ramo não se junta ao fase-1 sem conflito (ui/tela_conferir.py e ui/widgets/paineis.py). Antes: juntar, acertar as palavras dos avisos e refazer as fotos. "
            "Corrigido o parecer do Opus Majus 20: a foto sai estragada no PDF e o aviso está certo.")

ITENS_ANTES = [
    "RETOMADA 20/10: abri as 19 imagens que faltavam, uma a uma (todas batem com o parecer), e, para comparar com as decisões do Samuel, as 66 imagens citadas nos quadros.",
    "RETOMADA 20/10: reabri na janela, com o ce2b835, Opus Majus 20, Cursus 3, Antiphon 260 e Camões 66. Três confirmam o parecer; o Opus Majus 20 o desmente (ver abaixo).",
    "RESSALVA GRAVE: as fotos da janela são da tela antiga (abas Bordas/Endireitar/Marcar/Filtro, \"só nas próximas\", painel antigo). O layout aprovado está no fase-1 desde 14/10 e a junção dá conflito em ui/tela_conferir.py e ui/widgets/paineis.py (git merge-tree). Mostrar estas fotos ao Samuel repetiria o erro de 09 e 12/10.",
    "RESSALVA: os textos novos dos avisos dizem \"aba Marcar\" e \"aba Bordas\"; o layout já trocou \"aba Endireitar\" por \"ferramenta Endireitar\" e \"programa\" por \"Editor\".",
    "RESSALVA: as quatro fotos do quadro \"está bom\" (esta-bom-1 a 4, da primeira conferência) mostram o que o ce2b835 já não faz: Egenloff 3 com a força escurecida sozinha e \"usar mais escuro\" com a força em \"bem forte\". Trocar.",
    "EM PARTE (contra as decisões do Samuel): letra grande que some (rv5-erro-1-desenho): o lugar aparece marcado, mas a marca laranja é só desenho, não uma seleção da aba Marcar que se ajusta, e o botão traz de volta a página inteira. \"Guardar só o texto\" (rv5-erro-6-so-texto): a marca contorna a página toda, não a pauta como na opção que ele apontou. Regra: 22 vão e 75 certas, contra 21 e 78 aprovados.",
    "CORREÇÃO: Opus Majus 20. Em 13/10 escrevi \"a foto sai intacta, a página não precisava ir\". Reaberto e processado em 20/10: no PDF a foto da estátua sai destruída; o aviso \"Figura além da gravura\" está certo. O fase-1 desenha a página igual (o estrago já existia).",
]
ITENS_DEPOIS = [
    "VELOCIDADE: o Mágico pro +1,1% foi mandado pelo Samuel para a Fase 5 (19/10: \"vamos deixar esse concerto de lentidão para o final, para a fase de desempenho\"). Não medi de novo.",
    "AMBIENTE: o Cursus inteiro (402 folhas, livro novo) parou duas vezes na análise com MemoryError (alocar 1,4 MB) e o aviso genérico \"Aconteceu um problema inesperado\"; logo depois o PC tinha 4 GB livres, com outros 7 agentes trabalhando. Não sei dizer se é do programa ou do PC; o pedaço de 10 folhas abriu normal.",
]

TABELA_NOVA = [
    ("As 19 imagens novas (20/10)", "olho", "Abertas uma a uma; todas batem com o parecer. Lista em \"Retomada de 20/10\"."),
    ("Opus Majus 20, reaberto (20/10)", "janela + PDF + máquina", "Aviso certo; a foto sai destruída no PDF (já saía no fase-1). Corrige o parecer de 13/10."),
    ("Cursus 3, Antiphon 260, Camões 66, reabertos (20/10)", "janela", "Confirmam o parecer."),
    ("As fotos contra as decisões do Samuel (20/10)", "olho", "Fotos de tela antiga (layout aprovado não está no ramo); 4 desatualizadas; 2 escolhas dele \"em parte\". Ver conferencia-aba4."),
]

NAO_CONFERI = [
    "A seta do teclado com a janela ativa e o teclado de verdade (não tomo o teclado do Samuel). Conferida na janela inativa e pelo código: a conclusão não depende de a janela estar ativa.",
    "O programa juntado (ramo + fase-1 com o layout): a junção tem conflito e não é papel do verificador resolver. Nenhuma foto do jeito que o Samuel vai ver.",
    "O Cursus inteiro (402 folhas): parou duas vezes na análise por falta de memória; conferi pelo pedaço das folhas 1 a 10.",
    "Aba Marcar: só testei marcar uma área nova à mão enquanto o programa procurava. Não testei apagar ou mudar uma área do programa nesse intervalo.",
    "A segunda metade da força sozinha (\"só fica se as falhas caírem\"): não achei página que a exercite na janela.",
    "Projeto de antes de 09/10: só existe na pasta de dados do Samuel.",
    "A roda do mouse; a suíte inteira e o `teste_botoes.py` (não rodei; a velocidade foi para a Fase 5).",
]

BUGS = [
    ("20/10/2026", "Opus Majus 20 (página do gabarito), livro novo, Preto e branco com \"Só as letras\": a foto da estátua sai destruída no PDF (estátua branca, manchas e blocos pretos). Igual no fase-1 (mesma imagem, ponto por ponto). O aviso novo do \"Para revisar\" pega; o conserto é do detector de figuras (1.5).", "img/a4-opus-20.jpg"),
    ("20/10/2026", "Na junção com o fase-1: os textos novos dos avisos (core/analise.py do ramo) ainda dizem \"aba Marcar\" e \"aba Bordas\"; o layout não tem mais abas (\"ferramenta Endireitar\").", ""),
    ("20/10/2026", "A seta do teclado não troca de página quando o teclado está na tira (ela rola) ou no medidor da força (a seta muda a força do preto da página, e o programa grava). Igual no fase-1.", ""),
    ("20/10/2026", "Cursus inteiro (402 folhas), livro novo: a análise parou duas vezes com MemoryError (alocar 1,4 MB) e só a frase \"Aconteceu um problema inesperado\"; o Kaique fica na tela \"O que fazer\" sem saber o que houve. PC com outros 7 agentes; a causa pode ser do PC.", "trabalho/prints/r3-cursus-travou.png"),
    ("20/10/2026", "Nomes diferentes para desfazer o mesmo tipo de coisa: \"voltar a página\" (depois de \"Deixar em branco\") e \"restaurar página\" (depois de \"Tirar do livro\"). E a lista \"Antes de processar\" mistura \"Folha N\" e \"Página N\".", "img/sem-conteudo-4-tirar-do-livro-recorte.jpg"),
    ("20/10/2026", "O contador da tira diz \"2 páginas para você olhar\" num livro de 1 página (Opus Majus 20: conta a folha e a página); no Camões, o contador diz 96 a 98 e o painel 33 a 37. Faz parte da pergunta das contagens.", "img/r3-opus-20-tela.jpg"),
]


def md():
    m = ["## Retomada de 20/10/2026", "",
         "A pedido da gerente, no mesmo `ce2b835`, numa pasta de dados nova (`trabalho/dados_teste3`). Não medi velocidade (Fase 5, decisão do Samuel de 19/10).", "",
         "### As 19 imagens que faltavam abrir (uma linha por imagem)", ""]
    m += [f"{i}. `{n}.jpg`: {t}" for i, (n, t) in enumerate(DEZENOVE, 1)] + [""]
    m += ["### As quatro páginas reabertas na janela", "", "| Página | Como | O que vi |", "|---|---|---|"]
    m += [f"| {a} | {b} | {c} |" for a, b, c in QUATRO] + [""]
    m += ["![Opus Majus 20: a página no livro e no PDF](img/a4-opus-20.jpg)", "",
          "*Opus Majus 20: a página no livro e no PDF que o programa gerou (20/10, ce2b835).*", ""]
    m += ["### O teclado", "", TECLADO, ""]
    m += ["### As fotos contra as decisões do Samuel", "",
          "Conferência para a aba 4 em `conferencia-aba4.json` (e `.html`). Das 40 fotos dos quadros, 25 são de tela antiga (refazer depois de juntar o fase-1 no ramo) "
          "e 3 estão desatualizadas (quadro \"está bom\"). Duas escolhas do Samuel ficaram em parte (a marca laranja; o \"Guardar só o texto\"), e a regra dá 22/75 contra 21/78. "
          "**Recomendação: não publicar a aba 4 antes da junção e das fotos novas.** As três perguntas podem ir antes, se a gerente quiser separar.", ""]
    return "\n".join(m)


dados = {
    "dezenove": [{"img": f"img/{n}.jpg", "vi": t} for n, t in DEZENOVE],
    "veredito": VEREDITO, "itens_antes": ITENS_ANTES, "itens_depois": ITENS_DEPOIS,
    "tirar_itens_que_comecam_com": ["RESSALVA: a seta do teclado"],
    "teclado": TECLADO, "tabela_nova": TABELA_NOVA, "nao_conferi": NAO_CONFERI,
    "bugs": BUGS, "tirar_bugs_que_comecam_com": ["A seta do teclado"],
    "md": md(),
    "json": {"dezenove": [{"img": f"img/{n}.jpg", "vi": t} for n, t in DEZENOVE],
             "quatro_paginas": [{"pagina": a, "como": b, "vi": c} for a, b, c in QUATRO],
             "teclado": TECLADO, "aba4": "conferencia-aba4.json"},
    "como": ["- **Retomada de 20/10:** `scripts/r3_quatro_paginas.py` (as quatro páginas; Cursus e Antiphon por pedaços em `trabalho/livros/`), "
             "`r3_processar_opus.py` (o PDF do Opus Majus 20), `r3_render_raiz.py` (a mesma página com o código do fase-1, worktree `velocidade-antes-pr`), "
             "`a4_recortes.py` e `aba4_reabertos.py` (recortes ampliados), `aba4.py` (a conferência da aba 4), `vistas_20_10.py` e `terceira.py` (este parecer). "
             "As 67 imagens da segunda conferência foram todas abertas uma a uma até 20/10; as de 20/10 (`a4-*`, `r3-*`) também."],
}
(AQUI / "imagens_vistas_20-10.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(DEZENOVE), "imagens;", len(QUATRO), "paginas")
