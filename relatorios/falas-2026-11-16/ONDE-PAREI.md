# ONDE-PAREI — conserto do programinha das falas (16/11/2026)

Agente: implementador (tarefa de apoio, não mexe no programa). Ramo `falas-2026-11-16`, cópia
`.claude/worktrees/falas`. Script consertado: `C:\Users\fotog\.claude\scripts\falas_da_conversa.py`
(cópia do original em `falas_da_conversa.antes-2026-11-16.py`, intocada).

## Decisões que esta tarefa precisa cumprir

- **D-708, item 34 (16/11):** "34 - Isso é urgente, tem que ser verificado se ele não perdeu, me mostre um plano de
  como consertar e de o que aconteceu para o erro." → plano abaixo (antes do código), conferência das falas perdidas.
- **CLAUDE.md §11.12 (13/11):** "o agente não pode fazer gambiarras [...] funcionava de maneira diferente em vários
  lugares." → uma regra só para "isto é uma fala do Samuel", usada por todos os jeitos em que a fala fica gravada.
- **Regra de 16/11 (pedido da gerente):** plano primeiro, depois seguir sem esperar.
- **§11.7 "Só o que ele mandou":** a saída e as opções de hoje ficam iguais (`--desde`, `--com-respostas`,
  `--conversa`, `--todas`); nada novo além do conserto.

## O que já está escolhido e testado aqui

- O `/checkpoint` (passo 2a) e o `/projeto` (passo 5) rodam
  `python -I falas_da_conversa.py --todas --desde <AAAA-MM-DDTHH:MM UTC>` e leem linhas
  `[hora] SAMUEL: ...` e `[hora] SAMUEL (no meio do trabalho): ...`, com `[+N print(s)]` quando havia imagem, e
  `CLAUDE: ...` com `--com-respostas`. Esse formato fica.
- Não há teste automático antigo do script (não está no git do projeto).

## Como fica para quem usa e no livro

Nada muda no Editor de Impressão nem no PDF. Muda só o que a gerente lê no `/checkpoint` e no `/projeto`: passam a
aparecer as falas que o Samuel mandou enquanto o Claude trabalhava, e somem da lista os relatórios de agentes e os
avisos do navegador que hoje saem como se fossem dele.

## Por que o defeito acontece (a causa)

O script decide o que é "fala do Samuel" olhando o **jeito** como a linha foi gravada, e cada jeito tem a sua conta:

1. Mensagem normal (`type: user`): vale se o texto não começa com uma lista de avisos. Se a mensagem tem um aviso do
   navegador **antes** do texto dele, ela sai inteira com o aviso (`SAMUEL: <browser_instruction>...`).
2. Mensagem do meio do trabalho: o script só olha a linha `queue-operation` `enqueue`. Na versão atual do Claude
   Code essa linha vem **sem texto**; o texto foi para outros três lugares que o script não lê:
   - a linha `queue-operation` `remove` com `reason: "absorbed_mid_turn"` (texto puro, com `commandUuid`);
   - o anexo `type: attachment`, `attachment.type: "queued_command"`, com `origin.kind: "human"`, o texto e os
     prints (`attachment.prompt`) e o mesmo id (`source_uuid`);
   - a cópia do pedido à API (`api-request-blob`, papel `user`, junto de um `tool_result`), num bloco que começa com
     "The user sent a new message while you were working:".
3. Na linha `enqueue` vêm também os relatórios de agentes (`<agent-message ...>`), e essa marca não está na lista de
   avisos: por isso saem como "SAMUEL (no meio do trabalho)" (defeito de 14/11).

Ou seja: não há uma regra; há uma lista de exceções por jeito de gravar, e cada jeito novo do Claude Code escapa.

## O conserto (uma regra só, §11.12)

- **A regra:** uma função só, `e_fala_do_samuel(origem, blocos)`. É fala dele o que tem **origem humana**
  (`origin.kind == "human"`, que o Claude Code grava na mensagem normal e no anexo `queued_command`); quando o
  registro não diz a origem (`remove`, `enqueue`, cópia da API), vale o texto não ser aviso do programa. Os avisos são
  **uma lista só** (`AVISOS`), aplicada **bloco por bloco**: o bloco de aviso cai e o texto dele fica.
- **Os caminhos que chegam nela** (cada jeito de gravar só tira origem, texto, prints e id; quem decide é a regra):

  | Jeito de gravar | Lê | Id para não repetir |
  |---|---|---|
  | mensagem normal `type: user` | `origin.kind`, blocos de texto, imagens | — (texto) |
  | anexo `queued_command` | `attachment.origin.kind`, `attachment.prompt` | `source_uuid` |
  | `queue-operation` `remove` (`absorbed_mid_turn`) | `content` | `commandUuid` |
  | `queue-operation` `enqueue` (versão antiga, com texto) | `content` | — (texto) |
  | cópia da API / `user` com `tool_result` e o bloco "The user sent a new message while you were working:" | o texto depois dessa frase | — (texto) |

- **Sem repetir:** a mesma fala do meio do trabalho aparece até em quatro lugares. Ordem de preferência: o anexo (tem
  os prints) > o `remove` (mesmo id) > as cópias sem id, que só saem se o texto não apareceu em nenhum outro lugar
  (nem numa mensagem normal, inclusive quando duas falas da fila foram juntadas numa mensagem só).
- **Saída e opções iguais:** mesmo formato de linha, mesmas quatro opções.

## Como vou provar

1. `relatorios/falas-2026-11-16/teste_falas.py` (rodado com `python -I`): uma conversa de mentira com uma linha de
   cada jeito (normal, normal com aviso do navegador, anexo com print, `remove`, `enqueue` antigo, cópia da API,
   relatório de agente, aviso de tarefa, resumo de conversa, comando). Cobra: cada fala sai uma vez, marcada "(no meio
   do trabalho)" quando é o caso; nenhum relatório ou aviso sai como fala; as opções funcionam. Rodado também no
   script antigo, para mostrar que lá ele falha.
2. Rodar o script novo na conversa de hoje (`52e3de14`) e mostrar as duas falas ("Outra nova regra..." e "pode abrir
   mais de um agente ao mesmo tempo também desde que não seja fable").
3. Contar as falas do meio do trabalho em todas as conversas.
4. Conferir cada fala do meio do trabalho das conversas do Editor de Impressão contra o handoff, o Plano, o Livro e a
   `memoria/`.

## Andamento

- [x] Plano (este arquivo).
- [ ] Script consertado.
- [ ] Teste.
- [ ] Prova na conversa de hoje e contagem.
- [ ] Conferência das falas.
- [ ] Relatório (três formatos), commit e push.

## Perguntas para o Samuel

Nenhuma até agora.
