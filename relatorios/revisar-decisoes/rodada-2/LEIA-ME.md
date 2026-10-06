# Rodada 2: o critério que saiu das respostas

06/10/2026 · agente das decisões do "Para revisar". Nada do programa foi mudado, e nada foi commitado.

## O critério, em português simples

No jeito de fábrica do "Só as letras" ("Guardar a tinta forte"), a página vai para "Para revisar" quando:

1. **o programa apagou parte de um desenho** que não reconheceu como figura (letra S do Palatino 76,
   moldura do Siebmacher 7);
2. **uma figura passou da beirada da gravura achada, ou uma mancha virou "gravura"** (Marial 454,
   Antiphon 260, Pesel 21);
3. **sobrou uma faixa escura encostada na beirada da página** (o fundo do scanner da Matemática 32). Se a
   faixa aparece em 70% ou mais das páginas do livro, ela vira **um aviso só, no livro**, e não manda cada
   página para a lista.

Moldura, música ou letra grande que sai em preto e branco, igual ao Preto e branco de sempre, **não** manda
mais a página para a lista.

## Em números (`scripts/criterio.py`)

| Sinal | Conta | Limite |
|---|---|---|
| (1) desenho apagado | tinta que o jeito de fábrica apagou, amontoada (janela de 2 alturas de linha com mais de 4% apagado) / toda a tinta | 2% |
| (1) ou muita tinta apagada | tinta apagada fora do texto e das gravuras / toda a tinta | 2,5% |
| (2) figura além da gravura | pedaços grandes (1,5 altura de linha ou mais) encostados por fora na gravura achada / toda a tinta | 10% |
| (3) faixa escura na beirada (novo) | mancha cheia de tinta (sobra de uma abertura de 1,5% do lado menor) encostada na beirada, fora da gravura achada / área da página | 3% |
| (3) vira aviso do livro | páginas do livro com a faixa / todas as páginas | 70% (a mesma regra que o programa já usa para "observação do livro") |

(1) e (2) são a **opção 1** do estudo `relatorios/revisar-criterios-2026-10-06`. O sinal (3) é novo.

## Contra as respostas do Samuel (16 páginas da rodada 1)

| Página | Resposta dele | Hoje | Opção 1 | Critério novo | Por quê |
|---|---|---|---|---|---|
| Palatino 76 | vai | vai | vai | vai | apagou desenho |
| Palatino 67 | vai | vai | vai | vai | apagou desenho |
| Palatino 66 | vai | vai | vai | vai | apagou desenho |
| Siebmacher 7 (esq.) | vai | vai | vai | vai | apagou desenho (3,4% apagado) |
| ljs47 103 | vai | vai | vai | vai | apagou desenho, faixa na beirada |
| Marial 454 | vai | vai | vai | vai | mancha fora da gravura |
| Antiphon 260 | vai | vai | vai | vai | figura além da gravura |
| Pesel 21 | vai | vai | vai | vai | figura além da gravura |
| Matemática 32 | vai | vai | vai | vai | figura além da gravura (por acaso: o detector marcou parte da faixa como gravura), faixa na beirada |
| Graduale 222 | não | **vai** | não | não | quase nada apagado |
| Horas 14 | não | **vai** | não | não | quase nada apagado |
| Graduale 588 | não | **vai** | não | não | quase nada apagado |
| Palatino 10 | não | **vai** | não | não | quase nada apagado |
| Boécio 7 | não | não | não | não | — |
| Horas 175 | não | não | não | não | — |
| Rhetorica 34 | não | não | não | não | — |

Hoje: 12 de 16 iguais à resposta dele. Opção 1: 16 de 16. Critério novo: 16 de 16.

- **A opção 1 já bate com as 16 respostas.** O Siebmacher 7 já ia na opção 1 (o jeito de fábrica apagou 3,4%
  da tinta, pedaços da moldura). A Matemática 32 ia **por acaso**: o detector de gravura marcou parte da faixa
  do scanner como gravura e o sinal (2) disparou. O sinal (3) pega a faixa de propósito.
- A faixa do scanner é assunto do **corte das bordas** (item 2.13 do plano, "Detectar a página dentro da borda
  preta"), não do Misto: o Preto e branco de sempre a imprime igual.
- Nas 59 páginas do estudo: hoje vão 35, a opção 1 manda 18 e o critério novo 19 (a mais: Antiphon 88, pela
  beirada escura). As 7 erradas do jeito de fábrica continuam todas na lista.

## No livro novo (Righetti, *Historia de la Liturgia*, vol. 2, parte 2)

Livro que não entrou no estudo nem na rodada 1. Moderno, com fotos de mosaicos e de manuscritos, e com a
borda preta do scanner em todas as folhas. Cada folha do PDF tem duas páginas deitadas: girei 1/4 à esquerda
e dividi na lombada, como a pessoa faria na tela. Rodei 12 folhas (24 páginas), uma por vez, pelo caminho do
programa.

- **Hoje: as 24 vão para a lista** (a faixa do scanner conta como "tinta forte fora do texto": 44% a 95%).
- **Critério novo: 3 de 24** (folha 52 dir., folha 50 dir., folha 6 dir.). A faixa aparece nas 24 páginas,
  então vira um aviso só, no livro.
- Sem a regra do "aviso no livro", as 24 iriam pela faixa.
- No meu olho: as folhas 52 e 50 estão **erradas** (o jeito de fábrica apagou o meio dos mosaicos, que o Preto
  e branco de sempre guarda). A folha 6 é **leve** (sumiram o fundo cinza e alguns tracinhos). As outras 21
  estão certas. Olhei de perto 8 delas; as outras só em miniatura.

## As perguntas (`rodada-2-perguntas.json`)

1. **Resumo:** "Este é o critério que saiu das suas respostas. Fica assim?", com a tabela (`img/criterio-tabela.jpg`).
2. **Respostas às perguntas dele, uma por cartão** ("Entendi" / "Não entendi"):
   - Graduale 222: não afeta outros livros, porque o critério olha o que foi apagado, não se tem música.
   - Horas 14: sim, o aviso só existe com "Só as letras" marcada (conferido em `core/pipeline.py`).
   - Marial 454: o pedido já está na Lista de espera (05/10, "Mostrar as áreas que o programa achou
     sozinho", Fase 2, item 2.18). Hoje já dá à mão: aba Marcar, "gravura ou foto", botão "tirar", retângulo
     sobre o remendo. Testei pelo caminho do programa.
   - Graduale 588: dá hoje, na aba Marcar, com "gravura ou foto". Testei: a letra sai colorida, mas o papel e
     as pautas dentro do retângulo também ficam como no original.
   - Matemática 32: a faixa entra no critério, mas quem deve tirá-la é o corte (2.13).
3. **"Só o texto achado":** Palatino 10 ("Os dois" / "Só o aviso no livro" / "Só página por página") e o
   texto do aviso único ("Fica assim" / "Quero mudar o texto" / "Não precisa de aviso").
4. **8 páginas do Righetti:** "Pelo critério novo, esta página vai / não vai. Você concorda?"

Os campos `hoje`, `criterio_novo` e `veredito_agente` não aparecem na página; servem para a análise depois.

## Ressalvas

- **Os limites foram acertados em poucas páginas.** O Righetti é um só livro, e moderno; falta um livro antigo
  novo.
- **A regra do "aviso no livro" para a faixa foi medida só no Righetti.** Na Matemática só rodei 2 páginas,
  então não sei se ela também viraria aviso do livro.
- **Graduale 588 marcado como gravura:** a zona colorida é tratada como foto/pintura, que fica toda como no
  original (pedido P3 da conferência 12). Por isso o papel não vai a branco dentro do retângulo. Não é
  defeito novo, mas o Samuel pode estranhar.
- **Marial 454:** marcar o remendo como "papel" não resolve no "Só as letras" (ele continua marrom); o que
  funciona é "tirar" da gravura. Vale avisar o agente de layout.
- **Item de tela não pilotado na janela real.** As marcações foram simuladas pelo mesmo caminho do programa,
  acrescentando a zona à marcação, como a aba Marcar faz.

## Para refazer

Rode de dentro de `scripts/`, com o Python do projeto e uma página por vez:

1. `rodar.py <página>`
2. `sinais.py`
3. `marcar_teste.py`
4. `figuras.py`
5. `tabela_img.py`
6. `perguntas.py`

Os dados ficam em `%TEMP%\revisar_decisoes_rodada1` (a mesma pasta da rodada 1).
