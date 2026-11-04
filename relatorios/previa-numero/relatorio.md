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

## GitHub

Rodada 41884336233 (Testes no Windows, ramo previa-numero-2026-11-04): passou, todos os testes.

---

# Parte 2 (04/11/2026): com o Dividir marcado, o número é o da página como o livro vai sair

**Em uma frase:** com o Dividir marcado, cada metade tem o seu número, o da página no livro como vai
sair; no Gradus, a metade da esquerda da folha 68 é a "página 135 de 140" e a da direita a "136 de 140".

Pedido do Samuel, testando a parte 1: "funciona , mas com o dividir marcado o numero de pagina tem que
corresponder com a pagina que está sendo passada."

## Como cumpri cada ponto do pedido

- **Número da página como sai, com o Dividir marcado.** Gradus (70 folhas, sai com 140 páginas):
  135 + Enter mostra a metade da esquerda da folha 68, "página 135 de 140"; ">" mostra a da direita,
  "136 de 140" (prints `dividir-02` e `dividir-03`). Marcar o Dividir estando na página 30 já mostra
  "página 59 de 140". Prova `test_d617_com_dividir_o_numero_e_a_pagina_como_o_livro_vai_sair`.
- **Escrever um número leva a essa página.** 45 + Enter com o Dividir: a metade da esquerda da folha
  23, "página 45 de 140" (print `dividir-05`). Fora do intervalo continua ficando onde está.
- **Sem o Dividir marcado, como sempre.** "página 30 de 70"; desmarcar o Dividir volta a "de 70"
  (prints `dividir-01` e `dividir-08`).
- **A ordem do livro como vai sair.** É a mesma lista das setas e do caderno
  (`core/automatico.paginas_do_pdf_depois`). Ordem mudada à mão (D-615): prova
  `test_d617_com_dividir_o_numero_segue_a_ordem_mudada_a_mao`. Capa aberta (D-616): a capa é a
  "página 1 de 140" e a contracapa a "140 de 140" (prints `dividir-06` e `dividir-07`; prova
  `test_d617_com_dividir_e_a_capa_aberta_a_capa_e_a_pagina_1`).
- **O "tela cheia" mostra o mesmo número:** "página 136 de 140" (print `dividir-04`).

Janela de verdade: 11 de 11 conferências certas (`anotacoes-dividir.txt`).

## Testes antigos mudados (com autorização da gerente, em commits separados)

- `tests/test_decisoes_previa_dividida.py` (D-614), linhas 76, 84, 89 e 137 e uma frase da docstring:
  "página 1 de 3" nas duas metades passou a "1 de 4", "2 de 4", "3 de 4" (commit `9ad1d87c`).
- `tests/test_decisoes_previa_numero.py` (D-617 parte 1),
  `test_d617_com_dividir_as_setas_continuam_pelas_metades`: só os números (commit `3007f97d`).
- Cada linha tem um comentário com a D-617 de 04/11 e as palavras dele. Nenhum outro teste mudou.

## Arquivos

- `ui/automatico.py`: `PaginaAntesEDepois._com_o_dividir`, `_numero_e_total` (novas), `ir_para`,
  `_numero_escrito`, `_acertar_o_passo` (o número se acerta ao marcar ou desmarcar o Dividir ou a capa
  aberta, e o "tela cheia" acompanha).
- `tests/test_decisoes_previa_numero.py`: 3 provas novas, que falham no código da parte 1.

## Ressalvas

- Com o Dividir marcado, numa página tirada do livro (que não vai para o PDF), o número de
  escrever é sempre o de uma página que sai; não dá para ir a uma página tirada. Sem o Dividir,
  como antes.
- Com o Dividir marcado num livro já dividido, a numeração é a do PDF: se houver página tirada do
  livro, os números passam a não contar com ela (antes contavam). No Gradus nenhuma foi tirada.

## Para o Samuel testar

1. Gradus, Automático, marque "Dividir folhas ao meio", escreva 135 e Enter: aparece a metade da
   esquerda da folha 68 como "página 135 de 140"; ">" mostra "136 de 140".
2. Marque também "A 1ª folha é a capa aberta" e escreva 1: a capa aparece como "página 1".
