# ONDE PAREI — verificador clicando (03/11/2026)

Cópia: `.claude/worktrees/verif-03-11` (destacada em `613d6833`). Dados isolados no scratchpad
`verif-03-11-dados\` (nunca a pasta de dados de verdade). Prints e anotações nesta pasta.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel, do Livro)
- **D-602** (03/11): "quando eu entro no dividir não aparece a linha azul [...] o programa deveria carregar com a conta
  que está escolhida, e dai eu conseguir ver a linha e dai eu clicar e dividir esta, dai ele reparte, se eu apertasse
  para todas as folhas ele carregaria para todas as folhas [...] o botão do jeito ( que eu acho um nome bem ruim, acho que
  o nome poderia ser motor de corte) ficou travado e não dava para mudar." · só nas folhas duplas → "pode ser assim na
  questão do divisor."
- **D-004** (28/09, defeito consertado 03/11): "Automático em livro já mexido à mão: o programa pergunta se quer pular as
  páginas mexidas." · "teve até uma folha que ficou colocada uma na outra".
- **D-590** (30/10 e 03/11): "juntar todas" ao lado de "não dividir esta"; "Dividir" desmarcada no Automático não junta
  nada · "Sim a caixinha continua desmacada."
- **D-601** (02/11): "Uma página" mostra só a metade da folha dividida; "Duas lado a lado" a folha inteira com a linha.
- **D-090**: "usar em todas" copia a linha desta folha (não muda).
- **D-498**: "não dividir esta" junta as duas páginas; "dividir esta" devolve como estavam; Ctrl+Z devolve.

## Andamento
- [x] Teste 1 — linha azul / Dividir (D-602): rodado (prints t1-*, anotacoes-t1.*), funciona com ressalvas; Boécio feito (boecio-*)
- [x] Teste 2 — funciona com ressalvas (t2-*, t2m-*)
- [x] Teste 3 — funciona com ressalva (t3-*, t3b-*, t3c-*)
- [x] Relatório nos três formatos: relatorio.md/.html/.pdf (o .pdf fica fora do git pelo .gitignore)

## Anotações (03/11)
- Teste 2, parte 1 (rodada `t2`, dados `t2b`): pergunta "Pular as 6" apareceu e foi respondida; 140 páginas, 70 folhas
  divididas, folhas 5-10 certas nas duas vistas (prints t2-04 a t2-25). 1ª tentativa (`t2-primeira-tentativa/`) travou
  porque o meu "porteiro" sumiu da memória (erro do meu roteiro, não do programa).
- O Samuel parou a rodada no meio da parte "Margens iguais"; retomada na fase `t2m` (reabre pela tela inicial).
- Tudo feito em 03/11. Programa fechado (WM_CLOSE) no fim de cada fase.

## Como cumpri cada decisão
Ver a tabela "Como cumpri cada decisão" em `relatorio.html` (print ao lado de cada uma).
