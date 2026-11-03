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

- [x] Reproduzir no Gradus: no `110976f`, marcar "Margens iguais" deixa o "depois" do mesmo tamanho (1488 x 1052
      pontos, sem margem); mudar a margem não muda nada (`antes-*.png`).
- [x] Conserto (`core/automatico.py`, `ui/tarefas.py`, `ui/automatico.py`).
- [x] Provas e teste de reversão: `tests/test_decisoes_automatico_margens_no_depois.py`, 5 provas; as 5 falham no
      `110976f` e passam no ramo.
- [x] Prints antes/depois do Gradus (`antes-*.png`, `depois-*.png`, script `prints_margens.py`).
- [ ] Testes no PC, GitHub, filtro de velocidade (ver "Testes" abaixo).

## O que mudou e onde

- `core/automatico.py`: `depois_da_pagina` — com as margens ligadas depois do pedido (`_margens_ligadas_depois`, que
  pergunta ao próprio `aplicar`), mede também as outras folhas do pedido com a mesma `medir` do "Rodar"
  (`_medidas_das_outras_folhas`, guardadas por folha em `_MEDIDAS_GUARDADAS`, sem o filtro na chave) e faz a primeira
  passada do PDF na cópia (`_medir_o_livro` → `pipeline.medir_o_livro_para_as_margens`). Depois, `como_sai_na_tela`
  monta a mesma conta do PDF/`_com_as_margens`. `pagina_como_esta` (o "como está no livro" do comparar) mede o livro
  quando ele já tem as margens ligadas. Os dois avisam o andamento (`andamento`).
- `ui/tarefas.py`: `TarefaPreviaDoAutomatico.andamento` (sinal) e o `cancelado` no `pagina_como_esta`.
- `ui/automatico.py`: `PaginaAntesEDepois._andou` / `dica_da_bolinha` (o balão da bolinha, D-064) e o balão da tela
  cheia (`TelaCheiaDoAntesEDepois._acertar_lados`).

## Quanto custa (Gradus, 70 folhas, neste PC)

- Livro já dividido, só "Margens iguais": 14,4 s na primeira vez; mudar a margem: 0,4 s.
- Livro sem dividir, Dividir + Endireitar + Cortar + Limpar + Margens de uma vez: 92,5 s na primeira vez; mudar a
  margem: 1,4 s; trocar o filtro: 2,2 s; desmarcar e marcar de novo as margens: 1,3 s e 1,4 s.

## Como cumpri cada decisão

- **D-577** (o depois muda a cada opção, na janela, na tela cheia e nos dois lados do comparar):
  `test_margens_iguais_marcadas_aparecem_no_depois_como_no_pdf`, `test_mudar_um_numero_da_margem_muda_o_depois`,
  `test_margens_na_tela_cheia_e_nos_dois_lados_do_comparar`; prints `depois-2`, `depois-3`, `depois-4`, `depois-5`.
- **D-329 / D-473 / D-546** (tela = PDF, mesma conta): o depois é ponto por ponto a página que a tela mostra depois do
  "Rodar" e tem a proporção da página do PDF (1ª prova); "como está no livro" com margens ligadas = a tela (4ª prova).
- **D-311** (todas do tamanho da maior): 1ª prova (a torta e a reta saem do mesmo tamanho no PDF; o depois tem essa
  proporção).
- **D-075** (10/5 mm, alteráveis): 2ª prova (10 → 30 mm alarga 20 mm; 5 → 15 mm alonga 10 mm).
- **D-484** (margens para o livro todo): a medida é do livro todo, qualquer que seja o "Rodar em".
- **D-594**: não mexido (as opções do comparar continuam as mesmas; a 3ª prova usa os dois lados).
- **D-064 / §3** (não congela; bolinha com balão de % e páginas): a conta é no fio de fundo de sempre; 5ª prova.
- **§11 item 7**: nada de botão, frase ou opção nova; só o balão que a D-064 manda.

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

Situação: **respondida pela D-064** (gerente, 02/11/2026, sem perguntar de novo ao Samuel). D-064 (22/10), palavras
dele: "não precisa do mostrado como sai no pdf, é só colocar uma bolinha de carregamento, pode ter uma pro livro
inteiro e outra para a pagina que estamos, quando passsamos o mouse em cima mostra a mensagem de porcentagem e quantas
paginas carregaram já." Então: (1) fica o jeito construído (a bolinha gira, o "depois" sem margem até medir, depois
troca sozinho); (2) nada de frase ao lado da bolinha; (3) o balão da bolinha, enquanto mede, mostra a porcentagem e
quantas folhas/páginas já foram, no formato do balão da bolinha do livro da barra de baixo ("Livro: 42% (59 de 140
páginas já carregadas)."). Feito (`ui/automatico.PaginaAntesEDepois.dica_da_bolinha`; prova
`test_enquanto_mede_o_livro_a_bolinha_gira_e_o_balao_diz_quanto_falta`).
