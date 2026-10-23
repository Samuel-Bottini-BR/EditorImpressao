# Onde parei: verificador tp23, o papel da área "tinta com a cor" (item 2.18)

Pedido da gerente em 22/10/2026 (resposta do Samuel à tc23-1: "As duas: escolher o papel em cada área ('papel
branco' ou 'papel como o resto da página')").
Ramo `verif-tinta-papel-2026-10-23` (da ponta `0acf2c7` do `fase2-ferramentas-2026-10-22`; código em `b0af839` e
`3e95076`), worktree `.claude/worktrees/vtp23`. O "antes" é a worktree `.claude/worktrees/vtc23` (código `639136a`),
usada só para rodar, sem mexer no ramo dela. Junções `modelos` e `gabarito\paginas` (desfazer só com
`(Get-Item <junção>).Delete()`, nunca apagar a pasta).

## Situação

Tudo conferido. **PRONTO PARA CONFERIR**, com ressalvas (nunca "aprovado"). Relatório: `relatorio-tp23.html`.
Entrega: `conferencia.json` (id `tp23`, imagens em `img/`, fora do git).

- [x] Somas de fábrica (papel branco), antigo x novo: 36 de 36 iguais (`maquina/somas-comparacao.txt`)
- [x] Projeto antigo abre como "papel branco": 4 de 4 (`maquina/projeto-antigo/abrir-antigo.json`)
- [x] "papel como o resto da página" no Original e no Melhorar: o retângulo some (`img/numeros-papel.json`)
- [x] As quatro combinações com A e B: a tinta é 100% igual à do papel branco
- [x] A área de cima manda: 36 de 36 faixas; o "tirar" do pincel: 6 de 6 (`img/cruzadas.json`)
- [x] Teste novo: 10 passam no novo e 10 falham no antigo (`maquina/teste-*.txt`)
- [x] Janela de verdade: 28 de 28, depois 7 de 7 ao abrir de novo (uma conferida à mão, ver `maquina/janela/fase2/conferido-a-mao.txt`), e 11 de 11 no antigo
- [x] GitHub (lido): suíte 39877466484, 2195 passaram e 0 falharam; velocidade 39876068685 "igual"

## Perguntas para o Samuel

Nenhuma pergunta nova. As abertas b-10 (contorno preto no Preto e branco) e b-11 (nome do tipo) não são minhas e
não as decidi. Os casos estão nos prints: `img/escola_p007-preto_e_branco-letra-de-perto.jpg` (b-10),
`img/jan_03_papel_da_pagina_escolhido.jpg` e `img/jan_05_tres_areas_marcadas.jpg` (b-11; a linha "Marcado:" também
diz "papel branco").

## Ressalvas

Ver `relatorio-tp23.md`.
