# Rodada 1 — "Esta página deveria ir para 'Para revisar'?"

06/10/2026 · agente das decisões do "Para revisar". Nada do programa foi mudado.

## O que é

Em vez de pedir ao Samuel que escolha um critério abstrato, mostramos **16 páginas de verdade** e
perguntamos, uma a uma, se cada uma deveria ir para a lista "Para revisar". No fim, uma pergunta sobre
o jeito "Só o texto achado". Com as respostas, acertamos o critério pelo olho dele.

Cada imagem tem: **Original · Resultado (jeito de fábrica, "Guardar a tinta forte") · Preto e branco
de sempre**, recortados e ampliados na parte que importa; embaixo, a **página inteira** (a parte
ampliada pintada de amarelo) e o quadro **"Onde olhar"** (uma cópia do original com o que importa
pintado em cor transparente). Nada é desenhado por cima do resultado.

As perguntas estão em `rodada-1-perguntas.json` (a página do claude.ai lê esse arquivo; quem publica
é a gerente). As imagens estão em `img/`.

## As perguntas

"Hoje" = vai para a lista com o aviso de hoje (10% de tinta forte fora do texto). "Opção 1" = vai
com a opção 1 do estudo `relatorios/revisar-criterios-2026-10-06` (medir o que foi apagado).
"Meu olho" = como o jeito de fábrica saiu, no veredito do estudo (conferido de novo nesta rodada).

| # | Página | O que mostra | Hoje | Opção 1 | Meu olho |
|---|---|---|---|---|---|
| 1 | Palatino 76 | a letra S gravada some quase inteira | vai | vai | errada |
| 2 | Graduale 222 | música sai certa, mas conta como "tinta fora do texto" | vai | não | certa |
| 3 | Marial 454 | remendo e mancha do verso viram "gravura" e saem marrons | vai | vai | errada |
| 4 | Horas 14 | moldura dourada sai preta e grossa (igual ao Preto e branco) | vai | não | leve |
| 5 | Palatino 67 | o fundo desenhado da letra M some | vai | vai | errada |
| 6 | Matemática 32 | só a faixa escura do scanner | vai | vai | certa |
| 7 | Siebmacher 7 (esq.) | moldura sai em preto e branco, com pedaços apagados | vai | vai | leve (talvez errada: a faixa de baixo sai mais picotada que no Preto e branco) |
| 8 | Antiphon 260 | a zona de gravura pega as pautas: notas marrons e desbotadas | vai | vai | errada |
| 9 | Boécio 7 | letra Q e sinais de métrica ficam | não | não | certa |
| 10 | Palatino 66 | a letra enfeitada "M." do pé fica pela metade | vai | vai | errada |
| 11 | Graduale 588 | letra S azul sai preta (igual ao Preto e branco) | vai | não | leve |
| 12 | Pesel 21 | legenda no papel escuro vira tarja preta | vai | vai | errada (o Preto e branco faz o mesmo) |
| 13 | Palatino 10 | moldura de fios sai preta (igual ao Preto e branco) | vai | não | certa |
| 14 | ljs47 103 | diagrama de traço fino fica picotado | vai | vai | errada |
| 15 | Horas 175 | letra S colorida vira bloco preto (igual ao Preto e branco) | não | não | leve |
| 16 | Rhetorica 34 | gravura achada, fica como no original | não | não | certa |
| 17 | fechamento | "Só o texto achado": a música, a letra Q e os números somem | — | — | errada (43 de 59) |

## Como as respostas serão usadas

- Página a página, comparamos a resposta dele com "Hoje" e "Opção 1":
  - as **erradas** (1, 3, 5, 8, 10, 12, 14): se ele disser "Sim", o critério tem que pegá-las;
  - as **leves** (4, 7, 11, 15): dizem se "sai em preto e branco igual ao de sempre" merece lista,
    marca discreta ou nada (é a diferença entre a opção 1 e a opção 3 do estudo);
  - as **certas que hoje vão** (2, 6, 13): se ele disser "Não precisa", confirma tirar o aviso de
    hoje; a 6 (faixa do scanner) diz se beirada do scanner deve avisar;
  - as **certas que não vão** (9, 16): conferem que ele não quer lista em página boa.
- Muitas respostas "Só uma marca discreta" apontam para a opção 3 (marca nova na tela, que precisa
  da aprovação dele antes).
- A pergunta 17 decide como avisar no "Só o texto achado".
- Com isso, a rodada 2 mostra o critério que sai das respostas aplicado em páginas novas (de livro que
  não entrou no estudo), para ele conferir.

## Para refazer ou continuar (rodada 2)

- `scripts/` tem cópias dos scripts do estudo (`comum.py`, `rodar.py`, `medir.py`; o do estudo não
  foi tocado) mais `figuras.py`, `figuras_lista.py` (recortes e legendas) e `perguntas.py` (monta o
  JSON). Rodar com o Python do projeto, de dentro de `scripts/`, **uma página por vez**:
  `..\..\..\..\.venv\Scripts\python.exe rodar.py palatino_p076`, depois `figuras.py`, depois
  `perguntas.py`.
- Os dados pesados (imagens a 4000 px e máscaras) ficam fora do projeto, em
  `%TEMP%\revisar_decisoes_rodada1\dados`; se sumirem, o `rodar.py` refaz.
- Nesta rodada a "tinta forte fora do texto" e o aviso de hoje deram exatamente os números do estudo
  nas 17 páginas rodadas.
- Ressalvas: no Marial 454, no Antiphon 260 e no Pesel 21 o problema também aparece no Preto e branco
  de sempre (ele também lê as gravuras achadas); as explicações dizem isso. O veredito "Meu olho" é o
  do estudo; só o Siebmacher 7 me pareceu pior do que "leve" ao ampliar.
