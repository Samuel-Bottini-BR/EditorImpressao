"""Verificador, 21/10/2026: parecer do item 2.9 (letra clara em fundo escuro) e a conferencia em fotos para o
Samuel (conferencia-2.9.json; a gerente publica). Nao mede nada: le trabalho/somas-*.json (scripts/somas.py) e as
imagens de img/ (scripts/antes_depois.py e os prints da janela)."""
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))
a = json.loads((PASTA / "trabalho" / "somas-b8e9af7.json").read_text())
b = json.loads((PASTA / "trabalho" / "somas-0f4ee58.json").read_text())
diferentes = sorted(k for k in a if a[k] != b.get(k))
faltam = sorted(set(a) ^ set(b))
assert not diferentes and not faltam


def im(src, leg):
    assert (PASTA / src).exists(), src
    return {"src": src, "legenda": leg}


COMUM = ("Cada foto: a página como sai no PDF, sem a caixinha (\"Hoje\") e com a caixinha marcada, em Preto e branco e em "
         "Melhorar. A caixinha vem desmarcada: livro já começado sai igual.")
OPC = ["Está bom", "Melhorar", "Está pior", "Ainda não entendi"]
QUADROS = [
    {"id": "29-capa", "nome": "Capa com letra branca em fundo azul",
     "explicacao": ["O que você está escolhendo: se a caixinha faz o que você pediu numa capa de letra branca em fundo escuro.",
                    "Caso real: a capa do \"História do Direito Político Brasileiro\". Hoje o Preto e branco não mexe nela (fica igual ao original). Com a caixinha, sai letra branca em fundo preto puro, limpa, como o ScanTailor faz.",
                    COMUM],
     "olhar": "O título: em Preto e branco com a caixinha, branco limpo no fundo preto.",
     "imgs": [im("img/29-capa-direito.jpg", "Original, Hoje (Preto e branco), Preto e branco com a caixinha, Hoje (Melhorar), Melhorar com a caixinha")]},
    {"id": "29-slide", "nome": "Slide com parágrafos brancos em fundo escuro",
     "explicacao": ["O que você está escolhendo: se a caixinha resolve as páginas de texto claro em fundo escuro.",
                    "Caso real: um slide do \"O meio ambiente hoje\". Hoje o Preto e branco desenha só o contorno das letras, como letra vazada, com borrões; com a caixinha, o texto sai branco e inteiro no fundo preto.",
                    COMUM],
     "olhar": "As letras: vazadas no \"Hoje\", inteiras com a caixinha.",
     "imgs": [im("img/29-slide-perto.jpg", "Ampliado: o título e os parágrafos, nas cinco versões"),
              im("img/29-slide.jpg", "O slide inteiro")]},
    {"id": "29-horas", "nome": "Livro de Horas 187: a lombada de couro",
     "explicacao": ["O que você está escolhendo: se está bom o resultado na lombada (a página que o implementador achou).",
                    "Caso real: o título dourado \"HEURES DE LOVIS XIV\" na lombada escura. Hoje o Preto e branco vira uma página quase branca, sem título. Com a caixinha o título aparece em branco, mas o couro brilhante vira muitas manchas brancas.",
                    COMUM],
     "olhar": "O título dourado e o brilho do couro.",
     "imgs": [im("img/29-horas-187-perto.jpg", "Ampliado: o título na lombada"),
              im("img/29-horas-187.jpg", "A lombada inteira"),
              im("img/29-pdf-titulo.jpg", "O PDF gerado na janela de verdade, com a caixinha: letra branca no fundo preto")]},
    {"id": "29-cartoes", "nome": "Os cartões da tela não seguem a caixinha (defeito)",
     "explicacao": ["O que você está escolhendo: se isto precisa ser consertado antes de aprovar.",
                    "Caso real: com a caixinha marcada, só o cartão do filtro escolhido mostra a página invertida; os outros cartões (\"A mesma página nos quatro filtros\") mostram como se a caixinha estivesse desmarcada. Clicando no cartão Melhorar, que mostrava a lombada cinza, a página sai preta.",
                    "A tela \"Ver de perto\", no \"comparar\", mostra certo."],
     "olhar": "Em cima: o cartão Melhorar cinza. Embaixo, depois de clicar nele: preto.",
     "imgs": [im("img/29-cartoes.jpg", "Em cima: caixinha marcada, filtro Preto e branco. Embaixo: depois de escolher o Melhorar"),
              im("img/29-ver-de-perto.jpg", "\"Ver de perto\", comparar: o Melhorar com a caixinha, certo")]},
]
PERGUNTA = {"id": "29", "titulo": "A caixinha \"Letra clara em fundo escuro\": o que você decide?",
            "explicacao": ["O que você está escolhendo: se esta entrega entra no programa.",
                           "Você pediu em 05/10 (P9 (a)): \"Uma caixinha por página, 'Letra clara em fundo escuro', que o Kaique marca à mão\". Ela fica no AJUSTE da ferramenta Filtro, desmarcada. Igual ao ScanTailor: inverte a página, trata como letra escura em papel claro e inverte de novo no fim.",
                           "Falta consertar os cartões da tela (quadro acima) antes de aprovar."],
            "opcoes": ["Aprovado", "Melhorar", "Ainda não entendi"]}
SAIDA = {"item": "2.9", "ramo": "fase2-scantailor-itens-2026-10-19", "commit": "0f4ee58 (prova em 40a32c2)", "montado_em": "21/10/2026",
         "nota_para_a_gerente": ("Fotos da página pronta (300 DPI) e da tela nova de hoje. O quadro dos cartões é um defeito: "
                                 "melhor consertar antes de publicar, ou publicar com ele como aviso."),
         "quadros": QUADROS, "opcoes_de_cada_quadro": OPC, "pergunta": PERGUNTA}
(PASTA / "conferencia-2.9.json").write_text(json.dumps(SAIDA, ensure_ascii=False, indent=1), encoding="utf-8")

m = ["# Item 2.9: letra clara em fundo escuro - conferência do verificador (21/10/2026)", "",
     "Ramo `fase2-scantailor-itens-2026-10-19`, código `0f4ee58`, contra o `fase-1` em `b8e9af7`. Não mudei código; não marco nada como aprovado.", "",
     "## Veredito", "",
     "**NÃO ESTÁ PRONTO, por um defeito de tela:** com a caixinha marcada, os cartões dos filtros que não estão escolhidos mostram a página sem inverter, e o que se escolhe não é o que o cartão mostrava (`ui/tarefas.py` `_TarefaCartoes.run` chama `aplicar_filtro` direto, sem `claro_no_escuro`). "
     "O resto está certo: fábrica igual (128 de 128), a conta igual à do ScanTailor, o PDF sai invertido e o \"Ver de perto\" compara certo.", "",
     "## O que conferi", "", "| O que | Como | Resultado |", "|---|---|---|",
     f"| Desligado de fábrica: somas das 32 páginas-gabarito em Original, Preto e branco, Melhorar e Preto e branco com \"Só as letras\" (`scripts/somas.py`, uma página por processo; lado antigo = o que medi no 2.8) | máquina | **iguais: {len(a)} de {len(a)}** |",
     "| A conta igual à do ScanTailor | código | inverte na entrada e no fim, como `OutputGenerator.cpp` 1245-1249, 1344-1346, 1370-1372, 1497-1499 (conferido no arquivo de referência); Original e \"Tirar o fundo\" não passam por ela |",
     "| Testes do implementador (`test_claro_no_escuro.py`, `..._na_tela.py`) | máquina | 13 passaram |",
     "| Janela de verdade (Livro de Horas 186-188, tela nova) | olho | a caixinha aparece no AJUSTE (some no Original); marcar grava ação no desfazer; o cartão escolhido inverte; **os outros cartões não**; \"Ver de perto\" compara certo; o PDF sai com letra branca em fundo preto (12 s, erros.log vazio) |",
     "| Páginas de verdade | procura minha (`scripts/procurar.py`, 320 livros de D:\\Livros para editar e das pastas de teste; parei antes do fim) | achei casos melhores que a lombada: a capa do \"História do Direito Político Brasileiro\" e slides do \"O meio ambiente hoje\" (texto branco em fundo escuro) |",
     "| Antes/depois | `scripts/antes_depois.py` (caminho do programa, 300 DPI) | três páginas, abertas: ver os quadros |",
     "| Velocidade | - | não rodei (desligada de fábrica) |", "",
     "## Ressalvas", "",
     "- A procura do implementador leu só 14 livros e achou só a lombada; a minha achou capas e slides. Nenhuma página do gabarito é deste tipo.",
     "- Na lombada, com a caixinha, o couro brilhante vira manchas brancas: não é defeito da caixinha (a lombada não é texto em fundo uniforme).",
     "- Melhorar com a caixinha deixa uma moldura cinza em volta da lombada (o fundo claro do scanner, invertido).", "",
     "## Bugs para a Lista de bugs", "",
     "- 21/10/2026: com \"Letra clara em fundo escuro\" marcada, os cartões \"A mesma página nos quatro filtros\" (menos o escolhido) mostram a página sem inverter; escolher um deles dá outro resultado (`ui/tarefas.py` `_TarefaCartoes.run`).", ""]
for q in QUADROS:
    m += [f"## Quadro para o Samuel: {q['nome']}", ""] + [p + "\n" for p in q["explicacao"]]
    m += [f"**O que olhar:** {q['olhar']}", "", f"Opções: {' · '.join(OPC)} · e um comentário.", ""]
    for i in q["imgs"]:
        m += [f"![{i['legenda']}]({i['src']})", "", f"*{i['legenda']}*", ""]
m += [f"## Decisão: {PERGUNTA['titulo']}", ""] + [p + "\n" for p in PERGUNTA["explicacao"]] + [f"Opções: {' · '.join(PERGUNTA['opcoes'])}", ""]
import relatorio  # noqa: E402

print(relatorio.gravar("\n".join(m), PASTA / "2.9-verificado.md"))
