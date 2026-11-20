# Regras novas do catálogo dos erros (D-809 a D-814) — ONDE-PAREI

Implementador. Ramo `regras-catalogo-2026-11-19`, worktree `.claude/worktrees/regras-catalogo`. Pacote:
`relatorios/regras-catalogo-2026-11-19/anexos/pacote.md`.

## Pedido

- Papel: implementador
- Commit de partida: 0fe54cb3
- Ramo: regras-catalogo-2026-11-19

## Arquivos que vou mexer

- `regras_dos_agentes/catalogo.py`
- `regras_dos_agentes/porteiro.py`
- `regras_dos_agentes/formulario.py`
- `regras_dos_agentes/montar_pacote.py`
- `regras_dos_agentes/leitura_do_codigo.py`
- `tests/test_conferencias_codigo.py`
- `tests/test_conferencias_formulario.py`
- `tests/test_conferencias_pacote.py`
- `relatorios/regras-catalogo-2026-11-19/`

## Onde parei

- 19/11: li o pedido, o CLAUDE.md, a memória, o catálogo dos erros, o Livro (D-791 a D-814) e o código do pacote.
  Começando pela D-809 (a conferência K25).

## Decisões que esta tarefa precisa cumprir

- **D-791** (18/11/2026): "não sei do que você está falando" · "b". Aqui: a K25 barra desde o primeiro dia; a prova é
  "acusa o exemplo errado e não acusa o certo"; o que ela achar no código de hoje NÃO entra na lista de exceções.
- **D-792** (18/11/2026): "mas e o que vai determinar o que vai nesse formulario? vai ser feito um toda vez que for enviado um trabalho para um agente?" · "ok". Aqui: as perguntas novas entram no formulário único, pela etiqueta do trabalho, e o programa confere.
- **D-798** (19/11/2026): "fechou". Aqui: não escrevo o rótulo de pronto para conferir.
- **D-803** (19/11/2026): "pera ai, quando acontece esses erros, eles são catalogados para virarem regras depois?" · "ok". Aqui: as regras saem do catálogo, só com o "sim" dele (D-809 a D-814).
- **D-804** (19/11/2026): "como vai ser organizado esse catologo de erros?" · "ok". Aqui: as famílias F9, F4, F3+F5, F1, F2 e F6 do catálogo.
- **D-808** (19/11/2026): "1- pode". Aqui: o que ele aprovou nas seis perguntas é feito junto, por um agente (este).
- **D-809** (19/11/2026): "ok, mas essas coisas foram recuperadas? e porque ele fez essa confusão se era regra ele não mexer? e tinha o porteiro para ele não fazer isso" · "ok". Aqui: regra nova no catálogo (git e arquivos) e a conferência K25 do porteiro.
- **D-810** (19/11/2026): a gerente: "Proposta: os agentes que escrevem testes recebem uma lista curta dessas diferenças entre o seu PC, o GitHub e o PC do Kaique, para já escrever o teste certo de primeira. Fica assim?" Ele: "ok". Aqui: regra nova (Windows e testes), só regra.
- **D-811** (19/11/2026): a gerente: "Proposta: na ficha de entrega, quem escreve passa a mostrar, para cada proteção, o teste que falha quando ela é desligada." Ele: "ok". Aqui: pergunta nova no formulário (Windows e instalador); o programa confere que a lista existe e que cada teste citado existe.
- **D-812** (19/11/2026): a gerente: "É como deixar o aluno corrigir a própria prova. Proposta: toda conferência diz de onde vem cada informação que usa. Informação que o conferido pode trocar não vale como prova." Ele: "ok". Aqui: regra nova e pergunta nova no formulário.
- **D-813** (19/11/2026): a gerente: "Proposta: acrescentar à sua regra de 'ler antes de usar peça de fora' que, quando o programa recusa ou procura alguma coisa, o agente lista antes todos os jeitos que o Windows ou o Python aceitam para ela." Ele: "ok". Aqui: o acréscimo vai no catálogo, na regra 6 (e no "sempre" que a cobre); o CLAUDE.md fica com a gerente.
- **D-814** (19/11/2026): a gerente: "Proposta: antes de mandar qualquer pergunta para você, o agente anota em quais decisões suas procurou e por que essa ainda não está respondida." Ele: "ok". Aqui: pergunta nova no formulário, para entrega com perguntas ao Samuel.

## O que já está escolhido e testado aqui

- O porteiro tem 24 conferências com a numeração da tabela da proposta:
  `tests/test_conferencias_codigo.py::test_as_24_conferencias_tem_a_numeracao_da_tabela_da_proposta`.
- Cada conferência acusa o errado e não acusa o certo (D-791): os testes de `tests/test_conferencias_codigo.py`.
- A lista de exceções só diminui e nada entra por ramo de agente:
  `tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` (a lista está "valendo").
- O formulário certo de um trabalho só de testes passa:
  `tests/test_conferencias_formulario.py::test_o_formulario_certo_passa_e_o_github_nao_consultado_fica_pendente`.
- O trabalho do Windows cobra as falhas e as perguntas do Windows:
  `tests/test_conferencias_formulario.py::test_trabalho_do_windows_cobra_as_falhas_e_as_perguntas_do_windows`.
- O catálogo é coerente e o "sempre" tem no máximo 10: `tests/test_conferencias_pacote.py::test_o_catalogo_e_coerente`.
- O pacote do passo 1 traz as regras e o formulário do Windows:
  `tests/test_conferencias_pacote.py::test_o_pacote_do_passo_1_traz_as_regras_do_windows_e_o_formulario_do_windows`.

(o resto do formulário a preencher)
