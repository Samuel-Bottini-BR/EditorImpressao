# ONDE PAREI — margens no "depois" do Automático (ramo `margens-depois-2026-11-02`)

Cópia: `D:\programas\EditorImpressao\.claude\worktrees\margens-depois`. Ramo novo, saído da versão de teste
`obra-2026-10-26` em `110976f`. Não juntar em `obra-2026-10-26` nem em `fase-1` (quem junta é a gerente).

## O defeito (Samuel, 02/11/2026)

"coloquei margem e ela não apareceu no preview." No Automático do Gradus Primus (duas páginas por folha, dividido),
etapa 6 "Margens iguais" marcada com 10 / 5 / 10 / 5 mm: o lado "depois" de "A página, antes e depois" não mostra as
margens.

## Decisões que esta tarefa precisa cumprir

- **D-577 (29-31/10/2026):** "o antes é sem filtro e sem cortar sem nada, o depois na tela de atualizar que aplica os
  filtros de endireitar cortar ou fazer qualquer outra coisa para ver como iria ficar." No Livro: o "depois" é como a
  página vai sair com as etapas e opções marcadas e muda a cada opção trocada; enquanto calcula, a bolinha de
  carregamento ("sim, mas coloca uma bolinha de carregamento como fez na area de trabalho, porque as vezes vai demorar
  para processar né?"). Vale na janela, na tela cheia e nos dois lados do "comparar".
- **D-329 (22/10/2026):** "Sim, a tela mostra igual ao que sai (recomendado)" → com margens iguais ligadas, a tela
  mostra a página com elas, como no PDF (`ui/tela_conferir.py` `_com_as_margens`, `ui/tarefas.py`).
- **D-311 (05/10/2026):** "Todas as páginas do tamanho da maior: Sim".
- **D-075:** "(a) As do ScanTailor (10 mm dos lados, 5 mm em cima e embaixo) - Mas eu vou conseguir alterar isso né?"
  (margens alteráveis).
- **D-484:** Margens iguais vale sempre para o livro todo.
- **D-546 / D-473 / D-066:** "precisamos que o pdf saia que nem está na tela" — tela e PDF saem da mesma conta.
- **D-594:** as opções do Automático (e no "comparar"); as opções novas começam pela receita.
- **§3 do CLAUDE.md:** a interface nunca congela; uma página por vez na memória.
- **§11 item 7:** só o que ele mandou.

## O que fazer (pedido da gerente)

1. Com "Margens iguais" marcada, o "depois" (janela, tela cheia, dois lados do "comparar") mostra a página com as
   margens e no tamanho final, igual ao PDF, e muda quando se muda um número de margem. Mesma conta do PDF.
2. Se medir o livro todo demorar: sem congelar, com a bolinha que já existe. Caso sem resposta nas decisões → pergunta.
3. Só isso.
4. Prova + teste de reversão (falha no `110976f`); prints antes/depois do Gradus; testes no PC; GitHub; filtro de
   velocidade se mexer em `core/`.

## Andamento

- [ ] Reproduzir no Gradus e medir quanto custa medir o livro.
- [ ] Conserto.
- [ ] Provas e teste de reversão.
- [ ] Prints antes/depois.
- [ ] Testes no PC, push, GitHub, filtro de velocidade.

## Perguntas para o Samuel

### P1 (02/11/2026) — enquanto o programa mede o livro para as margens

Print: `relatorios/margens-depois/depois-1-medindo-o-livro-bolinha.png` (a bolinha girando ao lado de "A página,
antes e depois"; o lado "depois" ainda sem a margem).

Texto para a Central:

"Para mostrar as margens iguais no "depois", o programa precisa medir todas as páginas do livro (todas saem do tamanho
da maior). Isso só acontece na primeira vez que você marca "Margens iguais", ou quando troca Dividir, Endireitar ou
Cortar. No Gradus (70 folhas): com o livro já dividido e só "Margens iguais" marcada, leva uns 15 segundos; com Dividir,
Endireitar, Cortar e Margens marcadas de uma vez, leva uns 1 minuto e meio. Depois disso, trocar um número da margem
muda o "depois" em menos de 2 segundos. Enquanto mede, a bolinha gira e o "depois" continua mostrando a página como
estava antes (sem a margem); a janela não trava e dá para mexer em tudo. Quando termina, o "depois" aparece com as
margens. É o mesmo jeito da área de trabalho, que também mostra sem margem até terminar de medir. Pode ficar assim?"

Sugestão: sim, fica assim (é o que está construído agora; nada a mais). Outra opção, se ele quiser: escrever ao lado
da bolinha "Medindo o livro para as margens: 12 de 70" (isso seria coisa nova, só com o "sim" dele).

Situação: construído do jeito sugerido; espera a resposta.
