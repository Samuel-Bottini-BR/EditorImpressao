# ONDE-PAREI — obra de 26/10/2026, etapa 1: "o que é feito à mão sempre vale no PDF"

Implementador · ramo `obra-etapa1-2026-10-26` (base `obra-2026-10-26` = `fase-1` `ddd4d74`) · worktree
`.claude/worktrees/obra-etapa1` · worktree de apoio (código antigo, só leitura, para a prova):
`.claude/worktrees/obra-etapa1-antes` (`ddd4d74`, solta, com as junções `modelos` e `gabarito\paginas`).

## Decisões que esta tarefa precisa cumprir (do Livro de decisões, `docs/plano/DECISOES.md`)

- **D-009 (26/10/2026):** "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo
  manualmente." → O que é feito à mão sempre vale no PDF, com a etapa do automático ligada ou não.
- **D-004 (28/09/2026):** "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas
  mexidas." → marca "mexida à mão" por página/folha e por etapa (esta etapa cria a marca; a pergunta é da etapa 3).
- **D-016 (escolha da gerente pela D-014):** a montagem da página segue a ordem obrigatória (endireita, depois corta
  uma vez só, no fim).
- **D-008 (parte de processamento; 22/09 e 26/10/2026):** "quero conseguir redimensionar o conteudo tambem" · "a
  ferramenta de mover não deveria estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" · "como
  é no photoshope, que você arrasta a hora que quiser e aumenta a hora que quiser" → mover/redimensionar o conteúdo
  chega ao PDF. Teste do Kaique (26/10, tarefa 5): "Mover conteúdo" arrastado para o meio não sai no meio do PDF
  (margens 15 × 53).
- **D-014 (26/10/2026):** obra até o fim sem pausas; os detalhes técnicos eu decido e anoto aqui.
- **D-017 (escolha da gerente):** aumentar além da beirada não corta nada escondido (o aviso e a marca na tela são da
  etapa 5) — tocada de leve aqui: o PDF não pode jogar o mover fora.

## Situação

Em andamento (começado 26/10/2026).

## Escolhas técnicas (D-014: decido e anoto)

(preenchido ao longo do trabalho; ver abaixo)

## Passos

- [ ] Prova "Desligado de fábrica" no código antigo (somas das 32 páginas × 3 filtros), por trás.
- [ ] `core/etapas.py` (um lugar só) + marca "mexida à mão" no modelo, com migração.
- [ ] `core/pipeline.py`: checagens de caixinha trocadas por `core/etapas.py`.
- [ ] Mover/redimensionar chegando ao PDF (`core/folha.compor_na_folha`).
- [ ] `tests/test_decisoes.py` (D-009, D-004/marca, D-008, projeto antigo igual).
- [ ] Prova "Desligado de fábrica" no código novo + prova do projeto antigo com valores à mão.
- [ ] Testes por arquivo; commits; push.

## Perguntas para o Samuel

Nenhuma até agora.
