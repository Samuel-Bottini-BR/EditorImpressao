# Provas dos 13 erros do Lusíadas (verificador, 14/11/2026) — onde parei

Tarefa só de estudo e prova: nenhuma linha do programa muda. Versão testada: `obra-2026-10-26`, ponta `c7e34fd8`.
Cópia: `.claude/worktrees/lusiadas-provas`, ramo `lusiadas-provas-2026-11-14`.
Dados do programa: `relatorios/lusiadas-provas-2026-11-14/_dados` (LOCALAPPDATA própria, fora do git).
Livro: cópia de `teste-kaique-lusiadas/saida_teste/livro/lusiadas.pdf` em `_livro/lusiadas.pdf` (67 folhas deitadas, 6,8 MB).
Janela: só fora da tela (SetWindowPos -32000 + PrintWindow) ou `QT_QPA_PLATFORM=offscreen`. Nada na tela do Samuel.

## Decisões que esta tarefa precisa cumprir (palavras dele)
- D-691: "Quero escolher um por um" · "eu quero ver esses erros, as provas dele e uma explicação de como acontece, explique de forma simples. quero antes de dar inicio."
- D-678 remendos nos rostos da p. 14: "tem que verificar o que aconteu".
- D-679 números: prévia "de 134" e saem 133; sino 24 → 28 sozinho.
- D-680 miniatura não fica branca depois de "deixar em branco".
- D-681 barra de baixo cortada com Propriedades aberto: "não é urgente."
- D-682 página deitada no arquivo para imprimir depois de Dividir que partiu o título (folha 7).
- D-683 Mão + "Uma página" logo depois de dividir no Automático: folha espremida (conferir se D-649 já resolveu).
- D-684 marcações laranja à vista com a Mão (contra a D-584: "desliga sozinho ao voltar para o Zoom ou a Mão").
- D-685 aviso "será substituído" não some ao trocar o nome: "Eu quero saber porque aconteceu esse bugue, que regra o agente errou".
- D-686 faixa "vai sair em Preto e branco" depois de "tirar do livro": "para que serve, e em que situação é disparado?"
- D-687 "(G2)" na tela: "Não se deve usar código na nomeação de coisas."
- D-688 lista do Automático volta ao topo ao marcar "Margens iguais".
- D-689 p. 22 suja: "tem que saber diferenciar bugue de erro. vamos investigar."
- D-690 pintura da p. 8 some: "se foi por mal uso ou bugue, se o programa não reconheceu a gravura".
- §11.13 (como explicar), §10 (modelo de print do girar), §4.10 (caminho inteiro), §11.12 (causa por todos os caminhos).

## O que já está escolhido e testado aqui
Nada é mexido (só leitura). As decisões citadas: D-584 (marcações), D-547/D-649 (tela = PDF), D-605.

## Como fica para quem usa e no livro
Nada muda: tarefa sem código.

## Andamento
- [x] leitura das regras (verificador.md, CLAUDE.md, INDICE, bugs.md, D-678..D-691 e citadas)
- [x] piloto fora da tela: `scripts/piloto.py` (base.py da obra-etapa3; janela em -32000, PrintWindow)
- [x] lista de códigos na tela: `scripts/codigos_na_tela.py` -> `scripts/codigos_na_tela.txt`
- [ ] fase a rodando (abrir, Automático como a rodada 1, tela, branco/tirar, processar 2x, montar)
- [ ] erro por erro (abaixo)
- [ ] relatório nos três formatos

## Erro por erro
Achados de código (antes de rodar):
- D-687: `ui/automatico.py:2285` "(G2)" (texto à vista); balões com "D-068" (`ui/automatico.py:765`) e "D-094" (`:2304`). Vieram do commit e2321b16 (26/10, etapa 3 da obra).
- D-685: `ui/widgets/destino.py` o campo do nome (`textEdited`) só chama `_conferir()`; o sinal `alterado` só sai em `escolher_pasta`; a faixa laranja da `JanelaConfirmar._reavaliar` só escuta `alterado`. Faixa nasceu em 765a56f3 (08/08, "Secao 2, etapa 1"); o seletor é de c3840ebd (18/07); a docstring falsa "Chamado toda vez que o destino muda" é de c8ae8b6a (25/09). O teste `tests/test_barra_de_menu.py::test_a_janela_de_confirmar_avisa_que_vai_substituir` chama `_reavaliar()` à mão.
- D-686: `ui/tela_conferir._atualizar_faixa` tem ramo para `em_branco`, não para `apagada`.
- D-680: `_acertar_as_miniaturas_movidas` pinta branca só a `inserida` (D-623); `em_branco` não; grade `_pagina_dentro_da_folha` também não.
- D-688: `ListaDeEtapas.refazer` faz `clear()` e monta tudo de novo a cada `estado.mudou`.
- D-684: o laranja é o "Mostrar as áreas achadas" (D-237), ligado sozinho em toda página com aviso (`_mostrar_as_achadas`: `mostrar or pagina.precisa_revisao`); o botão "marcações" (D-580/D-584) só mexe nas cores.

## Perguntas para o Samuel
(nenhuma por enquanto)
