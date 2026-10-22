# Regras de trabalho: gerente e agentes

Montado em 20/10/2026. **O que manda é o [CLAUDE.md](../../CLAUDE.md) e o
[PLANO-DEFINITIVO](../../docs/plano/PLANO-DEFINITIVO.md)**; aqui está o resumo por assunto, com a data em que cada
regra nasceu e onde ela está escrita por extenso. Se este arquivo e o CLAUDE.md discordarem, vale o CLAUDE.md.
Os erros que fizeram nascer cada regra estão em [licoes.md](../licoes.md).

## 1. Quem faz o quê

- **Gerente** = a conversa do Claude Code com o Samuel. Conversa com ele, divide o trabalho, chama os agentes, confere
  o que eles entregam e junta no `fase-1`. Não escreve código linha por linha (CLAUDE.md §10.1; plano §3).
- **Agentes** (regras em `.claude/agents/`; desde 25/09/2026):
  - [implementador](../../.claude/agents/implementador.md): código de processamento (`core/`) e scripts de apoio; uma
    mudança por vez, com comentário do que faz e do que é arriscado mudar.
  - [verificador](../../.claude/agents/verificador.md): testes, velocidade, antes/depois nas páginas-gabarito, abre
    **todas** as imagens, pilota a janela real em item de tela, escreve a opinião com as ressalvas. **Nunca** marca
    aprovado.
  - [pesquisador](../../.claude/agents/pesquisador.md): estuda código e documentação de fora, resume e diz a licença;
    grava em `docs/pesquisa/`.
  - [agente de layout](../../.claude/agents/layout.md): só mexe em `ui/`, na própria worktree. Ver
    [itens/layout.md](../itens/layout.md).
- **Montador da memória** (19-20/10/2026): monta esta pasta `memoria/`.
- **Só o Samuel aprova.** O agente escreve no máximo "PRONTO PARA CONFERIR" e a opinião; nunca "APROVADO". Só ele
  marca `[x]`, `[~]` ou `[-]` no plano (CLAUDE.md §4.3). Todo item diz se foi teste de **máquina** ou de **olho**.

## 2. Quem conversa com quem (19/10/2026, "C: chefe + bilhetes")

- Os agentes **entregam sempre à gerente**; nunca passam trabalho direto a outro agente (CLAUDE.md §4.8).
- Outras janelas do Claude Code podem mandar recado à gerente, com as **palavras literais** do Samuel; a gerente
  repete ao Samuel e só muda o plano depois do "sim" dele; o recado fica anotado em
  [conferencias.md](../conferencias.md) e na ficha do item. Gerente fechada: o recado vai para
  [recados/](../recados/LEIAME.md).

## 3. O plano

- **Uma fase de cada vez**, na ordem; ideia nova vai para a Lista de espera, com data; **só o Samuel muda o plano**,
  e toda mudança vai para o Registro de mudanças com data e motivo (plano §1, regras 1 a 3).
- Exceções aprovadas por ele: a Fase 1 começou com 0.2 e 0.6 em aberto (28/09/2026); a **Fase 2 foi adiantada**
  (01/10/2026); "seguir sem esperar a aprovação item a item" (28/09/2026: cada item vira commit no `fase-1`; o
  `master` só recebe o aprovado).
- **Bug que impede a tarefa** é consertado na hora; o que não impede vai para a Lista de bugs, com print e data, e é
  resolvido no começo da fase seguinte (plano §1, regra 5).
- **Toda função automática tem botão de ligar e desligar** (regra 8).
- **Toda decisão vira documento** (regra 7). Nenhum plano novo apaga pendência por omissão (CLAUDE.md §10.6). Todo
  item resolvido guarda o pedido original, literal (§10.7).
- **As duas cópias do plano** (`docs/plano/` e `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\`) nunca
  ficam diferentes; a gerente compara no começo de cada conversa (CLAUDE.md §10.4). Em 09/10/2026 o Samuel pediu:
  "ok, por favor tome muito cuidado, porque não quero apagar as varias rodadas que eu fiquei respondendo relatorios,
  quero que isso continue salvo e que o plano não mude, só seja acrescentado coisas." (Registro 09/10/2026).
- **Fase 2: igual ao ScanTailor, sem perguntar antes** (13/10/2026): ajustes de fábrica do ScanTailor; desligado de
  fábrica quando muda a imagem; botão no lugar que o layout decidido manda; o Samuel só confere no fim. Pergunta
  antes só quando houver escolha de verdade que o ScanTailor não resolve. Palavras dele: "mas eu preciso responder o
  que? não dá para simplismente implementar no programa?" e "ok" (plano, Fase 2).
- **Botão novo já decidido entra com aparência provisória**, sem esperar o layout, e vai para a lista
  `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\Botoes e funcoes para o layout.md` (conferência 15,
  06/10/2026).

## 4. O ciclo de uma mudança (CLAUDE.md §8, com as regras de 19/10/2026)

1. O item vem da fase atual do plano, na ordem.
2. A gerente passa ao implementador; ele faz **uma** mudança, na **própria worktree e ramo**.
3. Testes de máquina: **no PC, um arquivo de teste por vez**; a suíte inteira e o `teste_botoes.py` rodam **no
   Windows do GitHub** em toda entrega (decisão "B: GitHub e meu PC", 19/10/2026; CLAUDE.md §4.6).
4. **Velocidade:** em toda mudança de `core/`, o **filtro de velocidade no GitHub** (antes e depois na mesma máquina,
   alternados); se acusar lentidão, volta ao agente. A medida que vale (regra 6) é a do PC do Samuel, alternada, sem
   agentes, **no fim de cada fase** (decisão "opção 2", 19/10/2026). Lentidão pequena achada no meio da fase vai
   para a Fase 5 ("vamos deixar esse concerto de lentidão para o final, para a fase de desempenho.", 19/10/2026).
5. **Todo conserto de bug ganha teste de reversão**: falha no código antigo, passa no novo; o nome ou a docstring cita
   o bug; o verificador prova no código antigo; bug de imagem usa uma medida, ou vira ressalva escrita ("opção 1",
   19/10/2026; CLAUDE.md §4.7).
6. O verificador gera o antes/depois só com as páginas-gabarito do item (`gabarito/lista.json`) e **abre todas as
   imagens**; item de tela: janela real com mensagens nativas de mouse.
7. Relatório em **três formatos** (`.md`, `.html`, `.pdf`, com `relatorio.gravar`): o Samuel não abre `.md`
   (CLAUDE.md §2).
8. "PRONTO PARA CONFERIR" → a gerente monta a conferência numa página do claude.ai (§6 abaixo).
9. Antes de qualquer trabalho entrar no `fase-1`, a gerente roda **no PC** a suíte inteira e o `teste_botoes.py`, com
   os outros agentes parados (CLAUDE.md §4.6).
10. Aprovado: commit na hora, com o defeito resolvido escrito por extenso, e push.

## 5. Git, worktrees e o PC (detalhe em [pc-e-github.md](pc-e-github.md) e [ramos.md](../ramos.md))

- **Cada frente na sua worktree e no seu ramo** (`.claude\worktrees\<nome>`); só a gerente junta no `fase-1`
  (CLAUDE.md §10.3). Push do `fase-1` é só da gerente; cada agente dá push no próprio ramo depois de cada commit
  (08/10/2026).
- **Commit e push a cada passo e um `ONDE-PAREI.md`**: o limite de uso da conta já derrubou agentes três vezes
  (PARTE -15 §6; regra de 19/10/2026 nos agentes).
- **No máximo 3 a 4 agentes ao mesmo tempo**, um arquivo de pytest por vez, TEMP/TMP e `--basetemp` dentro da
  worktree, esperar com menos de 3 GB livres (Registro 07/10/2026, depois de dois acidentes).
- **Nunca mover nem apagar uma árvore de pastas sem listar as junções antes**; nunca `Remove-Item -Recurse` numa
  junção; desfazer só com `(Get-Item <junção>).Delete()` (07/10/2026).
- **Apagar** (regra do Samuel, 29/09/2026; CLAUDE.md §10.9): fora da pasta do projeto, nada se apaga sem perguntar ao
  Samuel (o agente relata à gerente, a gerente pergunta); dentro, só o que o próprio agente criou naquela tarefa.
- **Testes nunca gravam na pasta de dados real** do Samuel nem abrem janela na tela dele (`tests/conftest.py`,
  29-30/09/2026 e 08/10/2026).
- PowerShell 5.1: commit com `git commit -F arquivo`; `&&` não existe; `Set-Content -Encoding utf8` põe BOM.

## 6. Conferências com o Samuel (CLAUDE.md §10.10; detalhe em [paginas-claude-ai.md](paginas-claude-ai.md))

- Tudo o que ele precisa ver ou responder vai numa **página do claude.ai com banco de dados** (imagens grandes,
  "Escolho esta", caixa de comentário; a resposta fica salva na hora) (06/10/2026).
- **Abrir sozinha** no navegador dele (`start "" "<endereço>"`) quando uma conferência nova fica pronta, desde que ele
  já tenha feito a anterior e dado ok: "sempre que tiver paginas de conferencia prontas, pode abrir automaticamente
  no meu pc, caso eu já tenha feito a ultima pagina de conferencia e te dado ok." (06/10/2026).
- **Comentário com dúvida se responde NA página**, não no chat; o comentário dele vale como resposta; a pergunta volta
  com o comentário **fixado** no alto: "não me responda no chat quando tiver questionamentos nas conferencias,
  responda nas conferencias." e "o meu comentario serve como resposta, porque você não responde ele e me mostra a
  questão de novo?" (07/10/2026).
- As respostas são copiadas **palavra por palavra** para `relatorios/` e para o Registro de mudanças; agora também
  para [conferencias.md](../conferencias.md) e a ficha do item.
- **Antes de publicar**, um conferente abre todas as fotos contra as decisões dele (lição de 12/10/2026: a rodada 12
  do layout usou fotos desatualizadas).
- Como ele entende melhor uma pergunta: [jeito-do-samuel.md](jeito-do-samuel.md).

## 7. A memória (CLAUDE.md §4.9, 19/10/2026)

- Antes de começar um trabalho, cada agente lê o [INDICE](../INDICE.md) e as fichas do seu assunto.
- **O plano continua mandando**: a memória organiza e aponta, nunca contradiz o PLANO-DEFINITIVO.
- O `/checkpoint` atualiza as fichas dos assuntos tocados na sessão; o histórico por data continua inteiro.
- Depois de mexer na memória: `.venv\Scripts\python.exe memoria\conferir_memoria.py` (links, Registro sem ficha,
  perguntas já respondidas).

## 8. Regras técnicas que não se negociam (CLAUDE.md §3; cada uma é cicatriz)

PySide6, nunca tkinter · uma página por vez na memória · a interface nunca congela (QThread, barra, cancelar) ·
nenhuma exceção fecha a janela · nenhum emoji em rótulo · textos com acento, caminhos sem acento · algoritmo
consagrado em vez de fórmula própria · **nenhum modelo generativo** (rede neural só aponta, nunca desenha) · Python
3.14, não rebaixar · GPU GTX 1650 sem float16 rápido · erro nunca como stack trace · `core/` não importa `ui/` · o
programa novo abre projetos de versões anteriores ("o programa quando estiver pronto, ele vai ter que ser capaz de
abrir arquivos de versões anteriores.", conferência 14, 05/10/2026).

**Fronteira de autonomia** (CLAUDE.md §6). Pode decidir sozinho: limiar, janela, `k`, bloco, ordem interna de um
filtro, troca de binarizador, cache, paralelismo, memória. **Precisa perguntar antes:** criar/remover/renomear
filtro, mudar tela, pôr ou tirar controle, mudar formato dos dados, mexer no desfazer, trocar biblioteca.

## 9. Regras e hábitos novos de 19 a 21/10/2026 ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md))

- **Testes, "B: GitHub e meu PC" (19/10/2026):** as ~2.100 conferências e o `teste_botoes.py` rodam no GitHub em toda entrega e, antes de qualquer trabalho entrar no `fase-1`, também no PC com os outros agentes parados. **Exceção (20/10/2026, "opção 1"):** trabalho que só acrescenta documentos entra só com o GitHub.
- **Velocidade, "opção 2":** filtro no GitHub em toda mudança de processamento (adotado em 20/10/2026, ver [pc-e-github](pc-e-github.md)); medida que vale no PC no fim de cada fase; o notebook do Kaique é a régua final. Lentidão pequena no meio da fase vai para a Fase 5.
- **Teste de reversão, "opção 1":** todo bug consertado ganha teste que falha no código antigo e passa no novo; o verificador prova; bug de imagem usa medida (mm de preto etc.).
- **Sessões, "C: chefe + bilhetes":** agentes entregam sempre à gerente; recados de outras janelas com as palavras literais, a gerente repete e só muda o plano depois do "sim".
- **Memória, "Opção D completa":** montada e publicada em 20/10/2026 (https://claude.ai/artifact/TmMnggDtL2wtyeXVs1RvcE); MemPalace "Testar depois" (Lista de espera, 19/10/2026), só depois da `memoria/`.
- **Mensagem de commit na própria worktree (aprendido em 20/10/2026):** um agente pegou a mensagem de outro pelo scratchpad compartilhado. Cada agente grava a mensagem num arquivo dentro da **própria** worktree.
- **Ler o GitHub uma vez só (aprendido em 20/10/2026):** vários agentes com `gh run watch` ao mesmo tempo esgotam a API (HTTP 403). Disparar a rodada e ler o resultado **uma vez, no fim**.
- **Limite de uso da conta com muitos agentes:** com 5 a 8 agentes juntos a conta bateu o limite três vezes (20/10 de manhã, 20/10 à tarde, 21/10 de madrugada). Commit + `ONDE-PAREI.md` a cada passo; retomar com SendMessage depois do horário que o erro informa.
- **Pedido novo sobre testes (20/10/2026):** testar cada ferramenta sobre a página que já passou pelas etapas anteriores. Como aplicar: pergunta ainda não feita a ele.
- **Decisão da gerente dentro da alçada de limiar (`CLAUDE.md` §6):** no 2.15 a página só vai ao "Para revisar" se também se afastar 1° da média do livro; o Samuel confere na aba 8.
- **Antes de apagar uma worktree:** as junções `modelos` e `gabarito` se removem com `(Get-Item …).Delete()` (muitas worktrees novas em 20-21/10; ver [ramos](../ramos.md)).
- **Pausa de 21/10/2026:** a pedido dele ("quando os agentes acabarem, pode parar todos os serviços e esperar meu proximo comando"), todos os agentes pararam, com commit, push e `ONDE-PAREI.md` em dia. Agentes de uma sessão não existem numa conversa nova: para continuar uma frente, chame um agente novo apontando ramo, worktree e `ONDE-PAREI.md`.

## Regras de 21/10/2026 (decisões do Samuel na Central; CLAUDE.md §4.10)
- **Caminho inteiro:** todo teste de imagem e toda conferência levam a página pela ordem do livro novo (dividir →
  endireitar → cortar → filtro), com os ajustes de fábrica, até a ferramenta testada. Nunca a página crua só com a
  ferramenta (isso fica para achar causa de defeito, fora da conferência).
- **Cada foto diz o caminho e as opções** ("endireitada, cortada, Preto e branco + Só as letras").
- **Só páginas que vão ser impressas:** nunca lombada, capa ou contracapa de couro/papelão.
- Quantos agentes: dois implementadores (as 4 ferramentas começadas; as 7 não começadas) + verificador quando entregarem (Samuel, 22/10).
- Juntar no fim: quando o layout 4 a 7 e as 11 ferramentas terminarem, junta tudo num ramo de junção → GitHub → PC → `fase-1` (Samuel, 22/10; ajuste de segurança da gerente no plano aprovado).
