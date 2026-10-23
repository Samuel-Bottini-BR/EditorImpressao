"""Gera o conferencia.json do d212 (formato da Central) e o relatório nos três formatos;
confere que toda imagem citada existe em img/."""
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
RAIZ = AQUI.parents[2]
os.chdir(AQUI)
sys.path.insert(0, str(RAIZ))


def i(f, legenda):
    return {"src": "d212/img/" + f, "legenda": legenda}


COLUNAS = ("Como ler estas fotos, coluna por coluna: 1 = como a página sai HOJE (desentortar desligado, o de "
           "fábrica), filtro Original; 2 = com o desentortar LIGADO na página (Automático, pelas linhas do texto); "
           "3 = depois do botão \"Desentortar aumentando a página\"; 4, 5 e 6 = as mesmas três, no filtro Preto e "
           "branco. Em cima de cada coluna está escrito se apareceu aviso. As linhas vermelhas são retas, só para "
           "comparar com as linhas do texto. Caminho: livro novo, ajustes de fábrica (girar quando o livro precisa, "
           "dividir quando a folha é dupla), endireitar, cortar, desentortar, filtro; a imagem é tirada do PDF de saída.")

D_A = "\"A — Como o ScanTailor: cortar uma vez só, no fim\" (22/10)"
D_P1 = "P1 \"B — Proteção\" e P2 \"B — A mesma proteção da pergunta anterior\" (22/10)"
D_P5 = ("P5 \"C — Aparece sempre, mas depois do clique o programa confere de novo...\" + \"o aviso deve perguntar e "
        "não fazer automaticamente\" (23/10)")
D_P4 = "P4 \"A — deixar como está\" (fotos de celular; a opção continua) (23/10)"
D_P6 = "P6 (b) \"Como o ScanTailor: o desentortar sempre é medido na resolução do livro [...] numa tarefa por trás\" (23/10)"

d = {
    "id": "d212",
    "nome": "Desentortar a página curva perto da lombada (item 2.12), igual ao ScanTailor",
    "trabalho": "fase2-scantailor-itens-2026-10-19 (2.12: e23f63e ... 6be1dbe; ponta c3b66fb)",
    "origem": "verif-2.12-2026-10-23 (antes = b8e9af7, a base do ramo; antes da P6 = 2a42cfb)",
    "resumo": {
        "titulo": "Desligado, nada muda; ligado numa página curva limpa, as linhas saem retas; a tela mostra igual ao "
                  "PDF; os avisos e o botão funcionam na janela. Mas nos livros de teste ele quase nunca endireita nada.",
        "paragrafos": [
            "De fábrica (desligado) o programa sai igual ao de antes, ponto por ponto: 96 de 96 PDFs iguais (32 "
            "páginas-gabarito x Original, Preto e branco e Melhorar). Projeto antigo abre com o desentortar desligado.",
            "Ligado numa página curva de verdade perto da lombada, as linhas ficam retas e nenhuma letra some (foto do "
            "quadro 1). Essa página eu mesmo encurvei a partir de uma página reta do Righetti, porque nos livros de "
            "teste não existe página escaneada bem curva (o implementador procurou em 2.900 páginas e eu confirmei nas "
            "que ele achou).",
            "Nas páginas de verdade: Destino 18, Righetti 96, Cursus 151 e Cursus 176 (pelas margens) o desentortar "
            "estragaria a página; a proteção segura, a página sai como hoje e aparece o aviso \"Desentortar não usado\" "
            "com o botão. Marial 41, Cursus 176, Matemática 31 e 65: quase nada muda. Fotos de celular (Razões 57): "
            "nada muda, como você decidiu na P4.",
            "A prévia Rápida e os quatro cartões mostram a mesma página do PDF, só menor (6 de 6 iguais). Nos "
            "primeiros segundos aparece \"Desentortando esta página, um momento...\" e a tela não trava (a maior parada "
            "foi 37 milésimos de segundo).",
            "Na janela de verdade (cliques do mouse do Windows): o aviso e o botão aparecem na Rápida; no Destino 18 o "
            "botão traz a pergunta \"A página ainda saiu deformada\" com \"Desfazer\" e \"Manter assim\" e a página "
            "NÃO volta sozinha; \"Desfazer\" volta, o Desfazer (Ctrl+Z) traz de novo, \"Manter assim\" deixa conferida "
            "e aumentada, e fechando e abrindo o projeto tudo continua. 38 de 38 conferências certas.",
            "Testes no GitHub: 2204 passaram, 0 falharam; botões 221 ações, 0 falhas (rodada 39902142935). Velocidade: "
            "igual (rodada 39902159919). No meu PC os 80 testes do desentortar que precisam dos livros (o GitHub não "
            "tem os livros) passaram; o teste de reversão da P6 falha no código de antes, como deve.",
        ],
        "veredito": "PRONTO PARA CONFERIR, com ressalvas (a mais importante: na prática, nos livros de teste, ele "
                    "quase nunca endireita; ver as duas perguntas).",
    },
    "ressalvas": [
        "Página curva com a moldura escura do scanner em volta (o caso comum no acervo): o Automático não acha a curva "
        "e não mexe (quadro 1, foto da Marial encurvada). Achei a causa olhando a ferramenta sozinha: a \"caixa do "
        "texto\" que o programa passa ao ScanTailor pega a moldura escura junto; com a caixa só do bloco de texto ele "
        "acha a curva. O implementador já tinha anotado que essa caixa é provisória até o item 2.5 (a caixa do "
        "ScanTailor). Ver a pergunta 1.",
        "Righetti 96 com o botão: a página cresce, o texto fica inteiro e não aparece a pergunta, mas a página sai um "
        "pouco deformada (as linhas de cima ficam maiores e a margem esquerda fica ondulada). A medida do programa não "
        "pega isso. Ver a pergunta 2.",
        "Nos livros de teste não há página escaneada bem curva; a prova de que endireita é numa página que eu "
        "encurvei. Ela imita o livro aberto, mas não é um escaneamento de verdade.",
        "O Ctrl+Z pelo teclado não chega a uma janela que não está ativa (a do meu roteiro fica fora da tela para não "
        "atrapalhar o seu PC). Testei com o clique no botão \"Desfazer (Ctrl+Z)\" da barra de baixo, que é a mesma "
        "ação que o Ctrl+Z e o menu Editar > Desfazer chamam.",
        "A escolha na lista \"Desentortar perto da lombada\" o roteiro fez pelo programa (a lista abre um menu solto "
        "que o roteiro não alcança); todos os botões foram clicados com o mouse do Windows.",
        "Defeito antigo, já anotado pelo implementador: o rodapé \"N com dúvida\" fica atrasado (\"0 com dúvida\" com "
        "o aviso na tela no Destino 18; \"1 com dúvida\" sem aviso no Righetti 96 depois do botão).",
        "A medida por trás é só da página da vez e fica só na memória: cada página ligada espera de 1 a 6 segundos na "
        "primeira vez, e fechar e abrir o livro mede de novo.",
        "Velocidade: \"igual\", mas o Mágico pro ficou +5,2% com vai-e-vem de 5,5%, perto do limite. O caminho "
        "desligado não mudou (96 de 96 iguais); a medida que vale é a do seu PC no fim da fase.",
        "Com o desentortar ligado e a proteção segurando, a página sai igual à de hoje a menos de 1 tom de cinza em "
        "alguns pontos (diferença máxima 1 de 255, invisível).",
    ],
    "quadros": [
        {
            "id": "d212-endireita",
            "nome": "1. Página curva: as linhas saem retas? (e por que às vezes não)",
            "explicacao": [
                "Primeira foto: o alto da página curva, de perto. Coluna 1: hoje, desligado; as linhas sobem perto da "
                "lombada (à esquerda). Coluna 2: com o desentortar ligado (Automático). Caminho: livro novo, de fábrica, "
                "endireitar, cortar, desentortar, filtro Original; imagem tirada do PDF de saída.",
                COLUNAS,
                "A última foto não é o caminho do programa: é a ferramenta do ScanTailor sozinha, só para achar a causa "
                "de a Marial encurvada não endireitar. Da esquerda para a direita: a página curva; a ferramenta com a "
                "caixa = página inteira; com a caixa do programa (pega a moldura escura); com a caixa só do bloco de "
                "texto, feita por mim.",
            ],
            "olhar": "Na primeira foto, se na coluna 2 as linhas acompanham as linhas vermelhas retas e se nenhuma letra "
                     "da beirada sumiu.",
            "texto": "Página limpa encurvada: a parte perto da lombada passou de \"linhas tortas\" para \"linhas "
                     "retas\" (na minha medida da nitidez das linhas no terço da lombada, 0,37 para 0,76; quanto maior, "
                     "mais retas), nenhum pedaço de letra cortado pela beirada, sem aviso. Marial encurvada (com a "
                     "moldura escura): nada muda (0,59 para 0,59). Marial encurvada mais de leve: nada muda.",
            "selo": "Bom, com ressalva",
            "ressalva": "Só endireita quando não há moldura escura do scanner em volta (pergunta 1).",
            "decisao_do_samuel": D_A,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("curvada3-de-perto.jpg", "Página curva (Righetti 96 encurvada por mim), de perto. Coluna 1: hoje. "
                  "Coluna 2: desentortar ligado; as linhas ficam retas"),
                i("ligado-curvada3-pagina.jpg", "A mesma página inteira, as seis colunas (1 hoje, 2 ligado, 3 com o "
                  "botão; 4 a 6 o mesmo em Preto e branco)"),
                i("ligado-curvada2-pagina.jpg", "Marial 41 encurvada por mim, com a moldura escura do scanner: nas "
                  "seis colunas a curva continua (o desentortar não achou a curva)"),
                i("ligado-curvada-pagina.jpg", "Marial 41 encurvada mais de leve: nada muda"),
                i("causa-curvada2-moldura.jpg", "Só para achar a causa (ferramenta sozinha): com a caixa do programa "
                  "(3ª) nada muda; com a caixa só do texto (4ª) a curva é achada"),
            ],
        },
        {
            "id": "d212-protecao",
            "nome": "2. Páginas de verdade: a proteção e o botão",
            "explicacao": [COLUNAS],
            "olhar": "Se na coluna 2 a página sai igual à coluna 1 quando aparece \"Desentortar não usado\", e o que a "
                     "coluna 3 (o botão) faz.",
            "texto": "Destino 18: a proteção segura (coluna 2 = coluna 1); com o botão a página fica monstruosa e "
                     "aparece a pergunta \"A página ainda saiu deformada\". Righetti 96: a proteção segura; com o botão "
                     "a página cresce (1385 para 1600 pontos), o texto fica inteiro, sem pergunta (mas um pouco "
                     "deformada: pergunta 2). Cursus 176 pelas margens: segura; o botão entorta a página e pergunta. "
                     "Cursus 151: segura; o botão quase não muda nada, sem pergunta. Cursus 176 automático, Marial 41, "
                     "Matemática 31 e 65: sem aviso, quase nada muda. Razões 57 (foto de celular): nada muda (P4). "
                     "Nenhuma página perdeu texto: a tinta da página é a mesma, ou maior quando a página cresce.",
            "selo": "Bom, com ressalva",
            "ressalva": "Righetti 96 com o botão sai um pouco deformada sem a pergunta.",
            "decisao_do_samuel": D_P1 + "; " + D_P5 + "; " + D_P4,
            "bate_com_a_decisao": "sim, com a ressalva do Righetti",
            "imgs": [
                i("ligado-destino18-pagina.jpg", "Destino do socialismo 18, direita: 2 a proteção segura; 3 o botão "
                  "deixa a página monstruosa e pergunta"),
                i("ligado-righetti96-pagina.jpg", "Righetti 96, direita: 2 a proteção segura; 3 a página cresce, sem "
                  "pergunta (veja a margem esquerda ondulada)"),
                i("ligado-cursus176m-pagina.jpg", "Cursus 176, pelas margens: 2 segura; 3 a página entortada, com a "
                  "pergunta"),
                i("ligado-cursus151-pagina.jpg", "Cursus 151: 2 segura; 3 quase igual, sem pergunta"),
                i("ligado-cursus176-pagina.jpg", "Cursus 176, automático: nada muda"),
                i("ligado-matematica65-pagina.jpg", "Matemática 65: muda muito pouco, sem aviso"),
                i("ligado-matematica31-pagina.jpg", "Matemática 31: muda muito pouco, sem aviso"),
                i("ligado-marial41-pagina.jpg", "Marial 41 (página reta): nada muda"),
                i("ligado-razoes57-pagina.jpg", "Razões do Integralismo 57 (foto de celular): nada muda (P4)"),
            ],
        },
        {
            "id": "d212-tela",
            "nome": "3. A tela e os cartões mostram o mesmo que o PDF",
            "explicacao": [
                "Cada foto tem três colunas. Coluna 1: a prévia Rápida (a de fábrica) nos primeiros segundos, antes da "
                "medida terminar (sem desentortar). Coluna 2: a prévia Rápida depois da medida, que é o que a tela "
                "mostra. Coluna 3: o PDF de saída. A prévia foi ampliada até a altura do PDF para comparar.",
            ],
            "olhar": "Se a coluna 2 é a mesma página da coluna 3.",
            "texto": "Nos 6 casos (Destino 18, Righetti 96 e a página curva, ligado e com o botão) a prévia depois da "
                     "medida é exatamente o PDF reduzido (diferença 0), inclusive o tamanho da página aumentada. A "
                     "medida levou de 1 a 6 segundos; depois disso, trocar de filtro não mede de novo. Na janela, os "
                     "quatro cartões mostram a página desentortada (ou monstruosa) igual à prévia.",
            "selo": "Bom",
            "ressalva": "",
            "decisao_do_samuel": D_P6,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("previa-curvada3-ligado-previa.jpg", "Página curva, ligado: 1 antes da medida, 2 a tela, 3 o PDF"),
                i("previa-curvada3-botao-previa.jpg", "Página curva, com o botão: 1, 2, 3"),
                i("previa-destino18-botao-previa.jpg", "Destino 18 com o botão: a tela já mostra a página monstruosa, "
                  "igual ao PDF"),
                i("previa-righetti96-botao-previa.jpg", "Righetti 96 com o botão: a tela mostra a página maior, igual "
                  "ao PDF"),
                i("previa-destino18-ligado-previa.jpg", "Destino 18 ligado (a proteção segura): as três iguais"),
                i("previa-righetti96-ligado-previa.jpg", "Righetti 96 ligado (a proteção segura): as três iguais"),
            ],
        },
        {
            "id": "d212-janela",
            "nome": "4. Na janela de verdade: aviso, botão, Desfazer / Manter assim, Desfazer (Ctrl+Z), abrir de novo",
            "explicacao": [
                "Prints da janela do programa, prévia Rápida (a de fábrica), qualidade e tamanho de fábrica. O nome do "
                "arquivo diz o momento. Os botões foram clicados com o mouse do Windows.",
            ],
            "olhar": "Se a faixa embaixo dos cartões diz o aviso certo em cada momento, e se a página dos cartões muda "
                     "junto.",
            "texto": "38 de 38 conferências certas. Sinal \"Desentortando esta página, um momento...\" na barra de "
                     "baixo enquanto mede (5 s no Destino, 1 s nas outras) e a tela sem travar (maior parada 37 "
                     "milésimos). Destino 18: aviso \"Desentortar não usado\" + botão; clique: \"A página ainda saiu "
                     "deformada\" com \"Desfazer\" e \"Manter assim\", página aumentada (não volta sozinha); "
                     "\"Desfazer\": volta o aviso de antes; Desfazer (Ctrl+Z): volta a pergunta; \"Manter assim\": "
                     "página conferida e aumentada; fechar e abrir o projeto: continua Automático, aumentada e "
                     "conferida, e o Desfazer ainda desfaz a última ação. Righetti 96: aviso, botão, página maior sem "
                     "pergunta. Página curva: desentortada nos quatro cartões, sem aviso.",
            "selo": "Bom",
            "ressalva": "Ctrl+Z testado pelo botão da barra de baixo (a tecla não chega a uma janela inativa).",
            "decisao_do_samuel": D_P5 + "; " + D_P6,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("janela-curvada3-1-logo-depois-de-ligar.jpg", "Logo depois de ligar: o sinal \"Desentortando esta "
                  "página, um momento...\" na barra de baixo"),
                i("janela-curvada3-2-depois-da-medida.jpg", "Página curva depois da medida: desentortada nos quatro "
                  "cartões"),
                i("janela-destino18-2-aviso-desentortar-nao-usado.jpg", "Destino 18: o aviso \"Desentortar não "
                  "usado\" e o botão \"Desentortar aumentando a página\""),
                i("janela-destino18-3-pergunta-ainda-deformada.jpg", "Depois do clique: \"A página ainda saiu "
                  "deformada\", com \"Desfazer\" e \"Manter assim\""),
                i("janela-destino18-4-depois-do-desfazer.jpg", "Depois de \"Desfazer\": volta a página de antes e o "
                  "aviso de antes"),
                i("janela-destino18-5-depois-do-ctrl-z.jpg", "Depois do Desfazer (Ctrl+Z): volta a pergunta"),
                i("janela-destino18-6-depois-do-manter-assim.jpg", "Depois de \"Manter assim\": \"1 de 2 "
                  "conferidas\", a página aumentada fica"),
                i("janela-destino18-7-aberto-de-novo.jpg", "Projeto fechado e aberto de novo: tudo continua"),
                i("janela-destino18-8-aberto-de-novo-ctrl-z.jpg", "Aberto de novo, o Desfazer ainda desfaz o "
                  "\"Manter assim\""),
                i("janela-righetti96-1-logo-depois-de-ligar.jpg", "Righetti 96 logo depois de ligar"),
                i("janela-righetti96-2-depois-da-medida.jpg", "Righetti 96: o aviso e o botão"),
                i("janela-righetti96-3-depois-do-botao.jpg", "Righetti 96 depois do botão: página maior, sem pergunta "
                  "(o rodapé ainda diz \"1 com dúvida\": defeito antigo)"),
            ],
        },
    ],
    "pergunta": {
        "id": "d212",
        "titulo": "Desentortar perto da lombada (2.12): o que você decide?",
        "explicacao": ["O que você está escolhendo: se o desentortar entra no programa como está.",
                       "O que mais pesa: o quadro 1 (endireita a página curva limpa, mas não a que tem moldura escura) "
                       "e as perguntas 1 e 2."],
        "opcoes": ["Aprovado", "Melhorar", "Ainda não entendi"],
    },
    "perguntas": [
        {
            "id": "d212-1",
            "titulo": "Página curva com a moldura escura do scanner: o desentortar não acha a curva. O que fazer?",
            "explicacao": [
                "Na Marial encurvada (com a moldura escura que o scanner deixa em volta) o Automático não mexe. A causa: "
                "a caixa do texto que o programa passa ao ScanTailor pega a moldura junto. Com a caixa só do texto ele "
                "acha a curva. Essa caixa é provisória até o item 2.5 (a caixa do ScanTailor, que está em outro ramo).",
                "Foto: quadro 1, \"ligado-curvada2-pagina.jpg\" e \"causa-curvada2-moldura.jpg\".",
            ],
            "opcoes": [
                "A — (recomendo) Esperar o 2.5: quando a caixa do ScanTailor entrar, o verificador refaz esta página",
                "B — Voltar ao implementador agora, para a caixa do texto não pegar a moldura",
                "C — Deixar como está",
            ],
        },
        {
            "id": "d212-2",
            "titulo": "Righetti 96 com o botão: a página sai um pouco deformada e o programa não pergunta. Conta como "
                      "deformada?",
            "explicacao": [
                "Você pediu: \"o programa vai saber sempre que estiver deformada\". No Righetti 96 o botão deixa as "
                "linhas de cima um pouco maiores e a margem esquerda ondulada; o texto fica inteiro, e a pergunta não "
                "aparece.",
                "Foto: quadro 2, \"ligado-righetti96-pagina.jpg\", coluna 3; e quadro 3, "
                "\"previa-righetti96-botao-previa.jpg\".",
            ],
            "opcoes": [
                "A — Está bom assim: o texto inteiro basta",
                "B — Também deveria perguntar \"Desfazer / Manter assim\" nesse caso (volta ao implementador)",
            ],
        },
    ],
}

# confere as imagens
faltam = [im["src"] for q in d["quadros"] for im in q["imgs"] if not (AQUI / "img" / im["src"].split("/")[-1]).is_file()]
assert not faltam, faltam
(AQUI / "conferencia.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

# relatório nos três formatos
L = [f"# Conferência do item 2.12 — {d['nome']}", "",
     f"Trabalho: {d['trabalho']}. Verificador: ramo {d['origem']}. Data: 23/10/2026.", "",
     f"**Veredito: {d['resumo']['veredito']}**", "", "## Em poucas palavras", ""]
L += [p + "\n" for p in d["resumo"]["paragrafos"]]
L += ["## Ressalvas", ""] + [f"- {r}" for r in d["ressalvas"]] + [""]
for q in d["quadros"]:
    L += [f"## {q['nome']}", ""] + [e + "\n" for e in q["explicacao"]]
    L += [f"**O que olhar:** {q['olhar']}", "", q["texto"], "", f"Selo: {q['selo']}. Decisão: {q['decisao_do_samuel']}.", ""]
    L += [f"- `img/{im['src'].split('/')[-1]}` — {im['legenda']}" for im in q["imgs"]] + [""]
L += ["## Perguntas para o Samuel", ""]
for p in d["perguntas"]:
    L += [f"### {p['titulo']}", ""] + [e + "\n" for e in p["explicacao"]] + [f"- {o}" for o in p["opcoes"]] + [""]
L += ["## Teste de máquina (o verificador decide) e de olho (o Samuel decide)", "",
      "- Máquina: somas de fábrica 96/96 (`maquina/somas-comparacao.txt`); projeto antigo abre desligado "
      "(`maquina/reabrir/reabrir.json`); prévia = PDF 6/6 (`previa/previa.json`); janela 31/31 + 7/7 "
      "(`janela/conferencias.txt`, `janela-curvada3/conferencias.txt`); testes do desentortar no PC 80 passaram "
      "(`maquina/testes-novo.txt`); reversão da P6 falha no 2a42cfb (`maquina/reversao-p6-no-2a42cfb.txt`); GitHub "
      "(`maquina/github.txt`).",
      "- Olho: se as linhas ficam retas (quadro 1), se a coluna 3 do Righetti conta como deformada (pergunta 2).", ""]
import relatorio  # noqa: E402
relatorio.gravar("\n".join(L), AQUI / "relatorio-d212", titulo="Conferência do item 2.12 — desentortar")
print("ok", len(d["quadros"]), "quadros")
