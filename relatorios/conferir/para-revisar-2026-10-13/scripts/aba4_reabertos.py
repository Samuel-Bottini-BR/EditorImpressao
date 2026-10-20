"""20/10/2026: os quatro quadros das paginas reabertas na janela (Opus Majus 20, Cursus 3, Antiphon 260,
Camoes 66), no formato da aba 4. Grava aba4_quadros_reabertos.json (lido pelo aba4.py e pelo terceira.py)."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ANTIGA = "tela antiga: refazer depois de juntar o fase-1 no ramo"
VALE = "vale"


def im(src, legenda, situacao=VALE):
    assert (AQUI.parent / src).exists(), src
    return {"src": src, "legenda": legenda, "situacao": situacao}


Q = [
    {
        "id": "pr-opus-20", "nome": "Opus Majus 20: a foto da estátua sai estragada, e o aviso pega",
        "explicacao": [
            "O que você está escolhendo: se está certo esta página ir para a lista com o aviso \"Figura além da gravura\".",
            "Caso real: a foto da estátua de Roger Bacon. No PDF que o programa gerou, com Preto e branco e \"Só as letras\", a estátua sai branca, com manchas e blocos pretos: a foto foi estragada. O aviso manda conferir, e está certo. É como um alarme que toca porque há fumaça de verdade.",
            "A foto já sai assim no programa de hoje (conferi: a mesma imagem, ponto por ponto). O que este trabalho muda é só o aviso, que antes dizia \"Tinta forte fora do texto\". Achar a foto inteira é o item 1.5 (detector de figuras), que você deixou no plano.",
        ],
        "olhar": "A estátua: inteira no livro, branca e manchada no PDF.",
        "texto": "Reabri em 20/10 como livro novo, na janela, e processei até \"Ficou pronto!\".",
        "ressalva": "Corrige o que eu tinha escrito em 13/10 (\"a foto sai intacta, a página não precisava ir\"): aquela foto era da imagem pequena da tela, não do PDF.",
        "tipo": "misto", "selo": "aviso certo; a foto estraga (já estragava)",
        "decisao_do_samuel": "rv5-erro-2-gravura (09/10): \"Fica no plano (1.5 e 2.18)\"; rv4-erro-2-gravura: \"ele tem que ser mais acertivo para achar as figuras\".",
        "bate_com_a_decisao": "sim (o aviso vale; o conserto da foto é o 1.5)",
        "imgs": [
            im("img/a4-opus-20.jpg", "Ampliado: a página no livro e no PDF que o programa gerou"),
            im("img/r3-opus-20-tela.jpg", "A janela: o aviso \"Figura além da gravura\" e, no cartão do Preto e branco, a estátua já estragada", ANTIGA),
        ],
    },
    {
        "id": "pr-cursus-3", "nome": "Cursus 3: a faixa preta da beirada vai para a lista",
        "explicacao": [
            "O que você está escolhendo: se está certo esta página ir para a lista com o aviso \"Faixa escura na beirada\".",
            "Caso real: no livro novo, o corte do Cursus 3 deixa uma faixa preta larga à direita e uma linha preta à esquerda. O aviso conta isso e manda conferir o corte.",
            "O defeito é do corte (o endireitar antes de cortar, já no programa), não do aviso. O conserto do corte está em outro trabalho, que você marcou \"Melhorar\" (decisão cg6). Se ele entrar antes, esta página muda.",
        ],
        "olhar": "A faixa preta à direita da página e a linha preta à esquerda.",
        "texto": "Reabri em 20/10 na janela: o aviso é só o da faixa.",
        "ressalva": "O livro inteiro do Cursus (402 folhas) parou duas vezes na análise, por falta de memória no PC (\"Aconteceu um problema inesperado\"); reabri pelas 10 primeiras folhas, como livro novo.",
        "tipo": "misto", "selo": "aviso certo",
        "decisao_do_samuel": "rv4-erro-3-faixa: \"Os dois jeitos estão bons\"; corte: cg6 \"Melhorar\" (13/10).",
        "bate_com_a_decisao": "sim",
        "imgs": [
            im("img/a4-cursus-3.jpg", "Ampliado: Original e Preto e branco com a faixa preta à direita, e o aviso", ANTIGA),
            im("img/cursus-3-1-pagina-recorte.jpg", "A página como sai em Preto e branco, de perto"),
        ],
    },
    {
        "id": "pr-antiphon-260", "nome": "Antiphon 260: a iluminura sai estragada e ninguém avisa",
        "explicacao": [
            "O que você está escolhendo: se aceita que esta página fique sem aviso da iluminura, até o detector de figuras (item 1.5).",
            "Caso real: no Preto e branco a iluminura sai chapada, quase toda preta, e há uma faixa preta embaixo. Na primeira visita aparece o aviso da faixa; depois de visitar mais três páginas, a faixa vira aviso do livro inteiro e a página 260 fica só com o aviso do Endireitar.",
            "Pela regra que você aprovou ela devia ir para a lista. É uma das cinco que decidem diferente do estudo.",
        ],
        "olhar": "A iluminura chapada no cartão do Preto e branco, e o aviso, que é só o do Endireitar.",
        "texto": "Reabri em 20/10 na janela, as folhas 256 a 264: 1ª visita, faixa + Endireitar; depois de visitar 259, 261 e 262, só Endireitar. A frase do livro (\"No livro inteiro: as páginas deste livro têm uma faixa...\") fica meio escondida embaixo do título do painel.",
        "ressalva": "O aviso da faixa aparece e some conforme a pessoa visita outras páginas (vira aviso do livro quando 70% das páginas medidas têm faixa). Cada página levou de 13 a 42 segundos para ser medida.",
        "tipo": "pior", "selo": "escapa",
        "decisao_do_samuel": "rv4-resumo: \"Fica assim\" (pela regra aprovada esta página vai); rv5-erro-2-gravura: \"Fica no plano (1.5 e 2.18)\".",
        "bate_com_a_decisao": "não: devia ir e não vai",
        "imgs": [
            im("img/a4-antiphon-260.jpg", "Ampliado: Original e Preto e branco (iluminura chapada), e o único aviso", ANTIGA),
            im("img/antiphon-260-1-pagina-recorte.jpg", "A página como sai em Preto e branco, de perto (primeira conferência)"),
            im("img/r3-antiphon-260-tela-depois.jpg", "A tela inteira depois de visitar outras páginas: a frase do livro meio escondida no alto do painel", ANTIGA),
        ],
    },
    {
        "id": "pr-camoes-66", "nome": "Camões 66: as linhas pretas da beirada, sem aviso",
        "explicacao": [
            "O que você está escolhendo: se pode esperar o corte (item 2.13) para este aviso existir.",
            "Você decidiu: \"São as linhas pretas: aviso no livro basta\". Hoje o Camões não recebe esse aviso, nem na página nem no livro: as linhas são finas demais para a conta da faixa. Elas continuam saindo no resultado.",
            "O único aviso da página 66 é o do Endireitar.",
        ],
        "olhar": "As linhas finas pretas nas beiradas do Preto e branco, e o aviso, que é só o do Endireitar.",
        "texto": "Reabri em 20/10 na janela e visitei também 65, 67, 27 e 104: em nenhuma veio aviso de faixa ou de linhas. O 27 e o 104 receberam a força sozinha (85), como esperado.",
        "ressalva": "O plano já diz que isto depende do corte (item 2.13).",
        "tipo": "igual", "selo": "sem aviso",
        "decisao_do_samuel": "rv4-pag-camoes-066: \"São as linhas pretas: aviso no livro basta\".",
        "bate_com_a_decisao": "não (depende do 2.13, como está no plano)",
        "imgs": [
            im("img/a4-camoes-66.jpg", "Ampliado: Original e Preto e branco com as linhas finas nas beiradas, e o único aviso", ANTIGA),
        ],
    },
]
(AQUI / "aba4_quadros_reabertos.json").write_text(json.dumps(Q, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(Q), "quadros")
