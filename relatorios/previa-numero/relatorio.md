# D-617: escrever o número da página na prévia do Automático (04/11/2026)

**Em uma frase:** no "página 30 de 70" da prévia "A página, antes e depois", o 30 virou uma caixinha
de escrever; escreve 45, Enter, e a prévia vai direto para a página 45.

Ramo `previa-numero-2026-11-04` (saiu de `obra-2026-10-26`). Mexi só no contador da prévia.

## Decisões e como cumpri cada uma

- **D-617**, "queria poder escrever o numero da folha aqui para ir direto." Feito: "página [45] de 70",
  Enter vai direto (print `prints/novo-02-escreveu-45.png`; prova
  `test_d617_escrever_o_numero_e_enter_vai_direto_para_a_folha`).
  - Vazio, 0, número maior que o livro (99 num livro de 70) ou letras: fica na página e o número
    volta ao atual, sem mensagem (print `prints/novo-03-fora-do-intervalo-fica.png`; prova
    `test_d617_vazio_ou_fora_do_intervalo_volta_ao_numero_atual_sem_mensagem`). As letras nem entram.
  - Setas < >: iguais. Com o Dividir marcado continuam pelas metades (D-614): 30 + Enter dá a metade
    da esquerda da 30, ">" a da direita, ">" a esquerda da 31 (prints `novo-04` a `novo-07`; prova
    `test_d617_com_dividir_as_setas_continuam_pelas_metades`).
  - Visual: o mesmo dos números de escrever do programa (a caixa da folha de estilo de
    `ui/estilo.py`, larga como o "ir para" da tela inicial).
- **D-605** (o novo não estraga o testado): nenhum teste antigo mudou; os 6 arquivos da prévia
  passaram no PC. O `contador.text()` continua "página N de M" (o tela cheia e as provas da D-577
  e da D-614 leem assim).

## O teclado: medido antes e depois na janela de verdade (Gradus)

Hoje as setas Direita/Esquerda **não** viram a página dentro da janela grande: ao abrir, o foco fica
na caixa da receita; depois de clicar ">", as setas passam o foco entre os botões; o Page Down/Up
vira a página depois de clicar num botão da barra da prévia (`anotacoes-base.txt`).
Depois da mudança, igual (`anotacoes-novo.txt`): o foco ao abrir é o mesmo, a caixinha não entra na
fila do Tab nem na das setas (só pega o foco com o clique) e, dentro dela, o Page Down/Up vira a
página como nos botões ao lado. Dentro da caixinha, Direita/Esquerda andam no texto.

## Achado que virou cuidado

O "Rodar" é o botão padrão da janela: um Enter que a caixinha deixasse passar apertaria o "Rodar".
A caixinha segura o Enter. Prova `test_d617_o_enter_do_numero_nao_aperta_o_rodar` (ela falha se a
caixinha soltar o Enter: conferi). Na janela de verdade, com 4 e 5 etapas marcadas, nenhum Enter
rodou nem fechou a janela.

## Arquivos

- `ui/automatico.py`: `_CampoDoNumero` e `ContadorDaPagina` (novos), `PaginaAntesEDepois`
  (`contador` agora é o `ContadorDaPagina`, `campo_pagina`, `_numero_escrito`, `ir_para`).
- `tests/test_decisoes_previa_numero.py` (novo, 5 provas; as 5 falham no código de antes).
- `relatorios/previa-numero/`: ONDE-PAREI, piloto da janela de verdade, anotações e prints.

## Ressalvas

- Sair da caixinha com um número novo sem apertar Enter (clicar em outro lugar) também vai para a
  página, como nos outros números de escrever do programa (o "ir para" da tela inicial, o ângulo).
- Página que não vai para o PDF (tirada do livro): escrever o número dela leva à página mais perto,
  como as setas e o abrir da janela já fazem. No Gradus todas vão.
- O "tela cheia" continua com o número só de ler (o pedido era a prévia). Se ele quiser lá também, é
  pergunta para ele.
- O Gradus da pasta de teste já está dividido (140 páginas); para o print igual ao a-63 (70 páginas)
  o piloto abre a cópia do PDF como livro novo.

## Para o Samuel testar

1. Gradus, Automático: clique no número de "página 30 de 70", escreva 45 e Enter: a prévia mostra a página 45.
2. Marque "Dividir folhas ao meio" e use < >: as setas continuam andando pelas metades.
