# O fundo tirado não volta mais (D-646, D-699)

13/11/2026 · ramo `fundo-2026-11-13` · teste de máquina (provas automáticas) e de olho (prints). Só o Samuel aprova.

## Em uma frase

Depois de "Sim, tirar o fundo", nenhum filtro e nenhum Automático trazem mais o papel velho de volta; só o botão novo
"Desfazer o tirar o fundo" traz.

## O que estava errado e por quê

No Siebmacher, depois do "Sim, tirar o fundo", o papel ficava branco. Rodando o Automático, o papel velho voltava em
todas as páginas, sem aviso. A causa: o programa guardava o "fundo tirado" só no filtro da página. Qualquer troca de
filtro (o "Original" que o Automático põe, a figurinha, a tecla, o menu, a tela cheia, o "Aplicar em") apagava essa
marca, e o fundo voltava.

## O que mudou

- Cada página guarda agora "fundo tirado: sim ou não", separado do filtro. Uma regra só no programa decide o que
  acontece quando o filtro muda: o fundo tirado fica.
- Preto e branco, Melhorar e Mágico pro passam a ser feitos em cima da página já sem o fundo. O Original é a página
  sem o fundo, sem filtro.
- As figurinhas do painel, a tela cheia dos filtros e o "comparar" da tela grande mostram isso mesmo.
- Botão novo **"Desfazer o tirar o fundo"**: no painel "Filtro da página", logo abaixo das figurinhas, e no menu
  Filtro, embaixo dos quatro filtros. Os dois fazem a mesma coisa, na página da vez; o "Aplicar em" leva às outras.
  Só aparecem em livro com o "Tirar o fundo" e só ficam acesos na página sem o fundo. Ctrl+Z desfaz.
- Projeto antigo com páginas em "Tirar o fundo" abre com o fundo tirado e o filtro Original, e sai igual.

## Como fica para quem usa e no livro

1. O Kaique abre o livro com camadas e responde "Sim, tirar o fundo": papel branco (como antes).
2. Roda o Automático: o filtro vira Original e o papel continua branco (antes, o papel velho voltava).
3. Troca para Preto e branco (figurinha, tecla 2, menu, tela cheia, "Aplicar em" ou Automático): o preto e branco
   sai da página sem o fundo.
4. Quer o papel de volta numa página: botão "Desfazer o tirar o fundo" (painel, embaixo das figurinhas) ou menu
   Filtro > "Desfazer o tirar o fundo". Para várias: depois do botão, "Aplicar em" > "todas" ou "daqui em diante".
5. No PDF: as páginas sem o fundo saem sem o fundo, com o filtro escolhido por cima; as outras não mudam. Tela e PDF
   saem da mesma conta.

Problema novo visto: numa página "Original com o fundo tirado" (todo projeto antigo em "Tirar o fundo" abre assim),
a faixa de baixo diz "Esta página vai sair em Original." (pergunta 3).

## Prints

- `prints/fundo-1-automatico.png`: Siebmacher 3 a 6, Automático em Original. Azul (antes): o papel velho voltou.
  Verde (depois): continua branco.
- `prints/fundo-2-desfazer.png`: "Desfazer o tirar o fundo" na página 3: só ela volta com o papel.
- `prints/fundo-3-preto-e-branco.png`: Preto e branco em cima da página sem o fundo.
- `prints/fundo-4-botao-e-menu.png`: onde ficam o botão e o item do menu.

## Medidas (Siebmacher, páginas 3 a 6)

Brilho do papel (255 = branco; o papel velho fica entre 146 e 175):

| Passo | Antes do conserto | Depois do conserto |
|---|---|---|
| "Sim, tirar o fundo" | 255 · 255 · 255 · 255 | 255 · 255 · 255 · 255 |
| Automático em Original | 147 · 166 · 171 · 175 | 255 · 255 · 255 · 255 |
| "Desfazer o tirar o fundo" na página 3 | (não existia) | 146 na página 3; 255 nas outras |

{{TESTES}}

## Perguntas para o Samuel

1. Uma prova antiga do jeito velho quebrou (fora das três autorizadas): ela cobra que, depois de "Tirar o fundo",
   escolher "Original" tire o aviso "Conferir o fundo tirado". Agora o fundo fica, e o aviso também. Posso mudar essa
   prova também? Sugestão: sim.
2. O "só neste pedaço": numa página em "Tirar o fundo", um pedaço marcado em "Original" mostra o papel velho dentro
   do pedaço (decidido em 05/10, com prova). Deve deixar de trazer o papel velho, como manda "nenhum filtro deve fazer
   o fundo voltar"? Sugestão: sim.
3. Na página "Original com o fundo tirado", a faixa diz "Esta página vai sair em Original." Quer que diga a frase do
   fundo ("Vou tirar o fundo desta página...")? Sugestão: sim.
4. O menu Filtro não tem "Tirar o fundo"; o "Desfazer o tirar o fundo" ficou no fim do menu. Quer também o "Tirar o
   fundo" no menu, logo acima? Sugestão: sim.

Detalhe técnico (a regra, todos os caminhos, a reversão): `ONDE-PAREI.md`.
