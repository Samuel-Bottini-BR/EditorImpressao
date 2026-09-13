# Editor de Impressão — documento para colar no Claude

Atualizado em 07/09/2026. Versão **máxima**: reúne o histórico institucional, o
que o programa é, todas as funcionalidades pedidas, os 68 pedidos feitos até
hoje **palavra por palavra**, o que foi feito, o que falta, e os dois
documentos-fonte inteiros (a especificação original e o prompt de testes) em
apêndice. Feita para começar uma conversa nova — inclusive fora deste projeto,
para replanejar o aplicativo — sem perder nada.

Pasta do projeto: `D:\programas\EditorImpressao` (mudou de
`C:\Users\fotog\Desktop\EditorImpressao` em 07/09/2026; essa pasta antiga virou
o backup). Repositório git ligado a
`https://github.com/Samuel-Bottini-BR/EditorImpressao`.

---

# PARTE -3 — Checkpoint de 12-13/09/2026 (leia isto primeiro, é o mais novo)

A PARTE -2 abaixo (08/09) continua valendo como registro histórico, mas o
Samuel replanejou o trabalho nesta sessão porque sentiu que o projeto não
estava indo a lugar nenhum (com razão — ver "Descoberta dura" abaixo). Esta
parte é o novo protocolo e o estado real de agora.

## O replanejamento (decisões fechadas com o Samuel)

O Samuel mandou um documento (`explicações/Vamos recapitular o que o Editor
de Impressão precisa fazer para restaurar um livro.docx/.pdf`) recapitulando
os requisitos originais e mostrando, livro a livro, o resultado que quer
(usando imagens geradas por IA generativa **só como referência visual** de
comparação — nunca para o programa em si, que continua proibido de gerar
pixel, regra inalterada). A partir disso:

- **Stack: mantém Python + PySide6.** Discutido a fundo (o Samuel perguntou
  se valia trocar por C++, já que o ScanTailor - referência do Sauvola - é
  C++). Decisão: não trocar. O algoritmo já roda em C++ por baixo via
  `doxapy`/OpenCV; os bugs relatados são de lógica/interface, não da
  linguagem; reescrever jogaria fora ~12.500 linhas já funcionando.
- **OCR: adiado, não descartado.** Desenhamos a arquitetura definitiva caso
  seja retomado: **Tesseract** (rápido, sem treino) + **Calamari** (impresso
  histórico, mais adequado que Kraken para o caso do Samuel - texto
  impresso, não manuscrito à mão) + eventualmente **Kraken** para os livros
  que são manuscritos de verdade (o Samuel confirmou que existem mais
  manuscritos além do Graduale, ainda não identificados individualmente).
  **Decisão importante e definitiva: nenhum motor de OCR baseado em
  LLM/modelo generativo (Mistral OCR, Qwen2.5-VL, Nanonets, GPT-4V etc.) —
  eles podem "inventar" palavras plausíveis em texto ilegível, o mesmo risco
  que já proibimos para imagem.** Isso teria corrompido silenciosamente
  texto de livro raro. Motivo de adiar: treinar OCR de verdade dá trabalho
  grande (mesmo usando Tesseract para acelerar a criação do gabarito de
  treino do Calamari/Kraken), e o Samuel preferiu resolver primeiro o que já
  existe. Volume real de produção mencionado pelo Samuel: **100+ livros/mês**
  (bem mais que os ~20 mil páginas/mês que ele cogitou ao pesquisar preço do
  Transkribus - que custaria 12-25 mil EUR/ano nesse volume, inviável;
  motivo a mais para ir 100% local/grátis quando o OCR for retomado).
- **Novo protocolo de trabalho, pedido explicitamente pelo Samuel**: nada de
  "fiz 20 coisas e commitei". Agora é **um livro de cada vez**, sequencial
  (não paralelo - decisão explícita dele): eu testo a funcionalidade sozinho
  (pilotando a janela de verdade com `pywinauto`/`py-spy`, sem precisar que
  ele descreva passo a passo), trago prints reais do resultado, ele aprova
  ou reprova, só então seguimos pro próximo item/livro.
- **Os 3 livros escolhidos para este ciclo, nesta ordem**: **1) Sobre a
  Consolação da Filosofia - Severino Boécio, 2) Rhetorica Christiana - Fray
  Diego Valadés, 3) Na escola de Jesus - Catecismo explicado com imagens.**
  Testar função E interface juntas em cada um (o Samuel insistiu: "não
  quero problemas nela, hoje o aplicativo é travado demais").
- Plano completo escrito em
  `C:\Users\fotog\.claude\plans\d-programas-editorimpressao-explica-es-d-temporal-whale.md`
  (fora do repositório, é um arquivo de plano do Claude Code).

## Descoberta dura (por que o replanejamento era necessário)

Investigação objetiva confirmou a desconfiança do Samuel, com números:
**dos 109 itens do `PEDIDOS.md`, zero foram aprovados por ele (`[x]`), zero
sequer preparados para conferência (`[?]`)** - a Fase 4 (varredura com o
olho dele) nunca começou de verdade, apesar de 89 commits e ~279 testes
automáticos. Ritmo de commits mostra retrabalho (pico de 20 num dia, depois
quase um mês parado). As 3 correções de travamento da sessão de 08/09
(cartões, trava do MuPDF, painel torto) foram commitadas como resolvidas
nos testes de máquina, mas **o Samuel testou de verdade e voltou a
travar** - é o que a Fase 0 desta sessão investigou e corrigiu (ver abaixo).

## Fase 0 desta sessão: travamento re-investigado e corrigido de verdade

Reproduzi o travamento **ao vivo**, sozinho, sem precisar que o Samuel
descrevesse passo a passo: rodei o programa com `pythonw.exe main.py <pdf>`,
pilotei a janela real com `pywinauto` (livro Boécio, aba Conferir, ~60
navegações rápidas de página com seta direita + troca de filtro), e o
cartão "Preto e branco" ficou preso em "preparando..." por **mais de 70
segundos**, confirmado com 3 amostras de `py-spy dump --pid <PID>` (zero
threads ativas todas as vezes) e zero linha nova em
`%LOCALAPPDATA%\EditorImpressao\erros.log`.

**Duas causas reais achadas, cada uma com teste automático que falha antes
da correção e passa depois** (`tests/test_cartoes_e_previas.py`, novo):

1. **Os cartões de filtro dividiam o mesmo pool de threads (2 no máximo) que
   o carregamento de prévia de página.** Navegar rápido — uso normal do
   Samuel folheando um livro — enche essa fila sem nenhum cancelamento de
   pedido obsoleto, e como os cartões entravam na MESMA fila, ficavam presos
   atrás dela por tempo desproporcional. Corrigido em `ui/tarefas.py`:
   `GerenciadorPrevias` ganhou um `QThreadPool` **separado e dedicado**
   (`self._pool_cartoes`, 1 thread) só para `_TarefaCartoes` - não compete
   mais com `_TarefaPrevia`.
2. **`RuntimeError: Signal source has been deleted`** - achado no
   `erros.log` de 08/09/2026, 8+ ocorrências seguidas em
   `ui/tarefas.py:178`. Acontece quando a tela fecha (ou troca de livro)
   enquanto uma tarefa de fundo ainda está calculando: o objeto de sinais já
   foi destruído pelo Qt quando a tarefa tenta avisar, e o próprio
   tratamento de erro (`self.sinais.falhou.emit(...)`) quebra de novo com o
   mesmo erro, silenciosamente (thread morre sem novo log). Corrigido com
   uma função `_emitir_se_vivo()` que checa `shiboken6.isValid(dono)` antes
   de emitir qualquer sinal de `_TarefaPrevia`/`_TarefaCartoes` - se a tela
   já não existe mais, descarta em silêncio (não é erro de verdade, é uma
   corrida de desligamento esperada).

**Verificação feita, não só alegada:**
- Os dois testes novos falham isoladamente sem a correção (confirmado
  revertendo cada mudança separadamente) e passam com ela.
- Suíte inteira: **281 testes passando**, nenhuma regressão.
- Repeti a MESMA navegação agressiva no programa de verdade depois da
  correção: o cartão que travava agora resolve em **~2 segundos**.

**Nada foi commitado ainda** - `core/pdf_io.py`, `ui/tarefas.py`,
`ui/tela_conferir.py`, `ui/widgets/paineis.py` e `PEDIDOS.md` seguem
modificados sem stage (mistura as 3 correções da sessão de 08/09 + as 2
novas desta sessão). Regra do `CLAUDE.md` seção 8 continua valendo: **o
Samuel precisa abrir pelo atalho, testar navegação rápida + troca de
filtro/aba, e confirmar que não trava mais antes do commit.**

## Pontas soltas que continuam, sem mudança

- `empacotar.py` com a mudança não commitada de antes (tirou `"scipy"` da
  lista de exclusão do instalador) - ainda não perguntado ao Samuel
  especificamente sobre isso.
- `historico/handoff-editor-de-impressao 2.md` órfão, não commitado, mesma
  suspeita de sincronizador do Google Drive.
- `.pytest_cache/` não rastreado, ainda não está no `.gitignore`.

## Próximo passo recomendado

1. Perguntar ao Samuel se ele já testou (atalho "Editor de Impressao
   (desenvolvimento)") e confirmou que não trava mais navegando rápido.
2. Se confirmado: commitar as 5 correções (3 de 08/09 + 2 desta sessão),
   cada uma separada se possível.
3. Depois disso, começar a Fase 1 do novo protocolo: testar o livro
   **Boécio** primeiro (função + interface juntas), trazer prints reais,
   pedir aprovação item a item no `PEDIDOS.md` - só então passar para
   Rhetorica Christiana e depois Na escola de Jesus.

## Como rodar e testar (confirmado nesta sessão)

```
cd D:\programas\EditorImpressao

.venv\Scripts\python.exe -m pytest tests -q                 # 281 casos, confirmado passando
.venv\Scripts\python.exe -m pytest tests/test_cartoes_e_previas.py -v   # os 2 testes novos desta sessão
```

Reproduzir o travamento/verificar a correção ao vivo (o que fiz nesta
sessão, sem precisar o Samuel):
```
.venv\Scripts\pythonw.exe main.py "<caminho do PDF de teste>"
# pywinauto (Python 3.12 do sistema, fora do venv do projeto):
# Application(backend="uia").connect(process=PID) -> clicar "Conferir",
# depois "Filtro", enquanto navega rapido com send_keys("{RIGHT}")
```

Abrir para o Samuel testar: atalho "Editor de Impressao (desenvolvimento)"
na área de trabalho, ou `.venv\Scripts\pythonw.exe main.py`.

## Ambiente — nada novo instalado nesta sessão

`py-spy` e `pywinauto` já estavam instalados (sessão de 08/09, Python 3.12
do sistema, `pip install --user`) e foram reusados sem mudança. Nenhum
pacote novo no `.venv` do projeto.

---

# PARTE -2 — Checkpoint de 08/09/2026

A PARTE -1 abaixo (07/09) ainda vale como registro histórico da retomada, mas
o estado dela está desatualizado nalguns pontos — esta parte corrige e
substitui. `CLAUDE.md`, `PEDIDOS.md` e `PLANO-RETOMADA.md` continuam sendo os
arquivos de regra, lidos primeiro.

## Estado atual

- **Fase 1 do `PLANO-RETOMADA.md` está fechada, com 7 livros em vez de 5**
  (o Samuel preferiu ampliar). Nomes e o defeito que cada um representa estão
  no topo do `PEDIDOS.md`. Nenhum item do `PEDIDOS.md` foi conferido ainda
  (Bloco 1 em diante continua tudo `[ ]`) — a varredura de verdade não
  começou, porque o Samuel esbarrou em bugs reais só de abrir o programa.
- **Três defeitos achados e corrigidos nesta sessão, todos com teste de
  máquina passando (279 casos do pytest + 118 cliques do `teste_botoes.py`)
  — mas AINDA SEM o "abri, testei, aprovei" do Samuel.** Ver "Pergunta em
  aberto" abaixo antes de fazer commit.
  1. **Cálculo síncrono dos cartões de filtro travava a tela.**
     `ui/tela_conferir.py::_atualizar_cartoes` chamava `aplicar_filtro` para
     os 3 filtros não-escolhidos direto no thread da interface —
     `k_para_a_letra` usa `skimage.morphology.skeletonize`, medido em 4,4s
     numa página comum do Rhetorica Christiana. Corrigido: `ui/tarefas.py`
     ganhou `_TarefaCartoes`/`_SinaisCartoes` (mesmo padrão de
     `_TarefaPrevia`), rodando em `QThreadPool`; `_atualizar_cartoes` mostra
     "preparando..." e pinta quando o sinal `cartoes_prontos` chega.
  2. **O travamento "de verdade" (o que o Samuel viu, tela toda travada,
     "Não está respondendo") tinha causa raiz diferente e mais grave: MuPDF
     não aguenta duas threads lendo o mesmo arquivo PDF ao mesmo tempo —
     pode travar para sempre dentro de `fz_run_display_list`, sem erro
     nenhum no log.** Achado ao vivo com `py-spy` (duas vezes, dois livros
     diferentes: Rhetorica Christiana e Giovambattista Palatino, sempre a
     mesma pilha travada). Corrigido em duas partes:
     - `ui/tela_conferir.py::_montar_tira` parou de refazer a tira de
       miniaturas do livro inteiro toda vez que a aba troca — só remonta
       quando o conjunto de páginas/folhas muda de verdade (guarda uma
       "assinatura" em `self._tira_assinatura`).
     - `core/pdf_io.py` ganhou uma trava global (`_TRANCA =
       threading.Lock()`) em volta de toda chamada nativa ao MuPDF
       (`abrir_pdf`, `info_paginas`, `dpi_real_da_pagina`,
       `pagina_para_array`, e os métodos de `EscritorPDF`) — só uma parte do
       programa lê/escreve PDF por vez agora.
  3. **O painel da direita (Para revisar / Marcar como / Filtro da página /
     Histórico) saía com o dobro da largura do desenho (172px → ~320-380px),
     cortando o texto pela metade e mostrando só o final de cada rótulo**
     (ex.: "gravura ou foto" virava "u foto"). Causa: `QPushButton` não
     encolhe sozinho abaixo do que precisa pra mostrar o texto inteiro sem
     quebrar linha, e um item de histórico comprido ("Filtro da página 12:
     Preto e branco para Melhorar") forçava a coluna inteira a alargar.
     **Só apareceu agora porque este projeto (Palatino) já tinha histórico
     acumulado o bastante pra disparar isso** — projeto novo não mostra o
     bug. Corrigido em `ui/widgets/paineis.py`: nova classe
     `_BotaoDoPainel` (corta o próprio texto com reticências, guarda o texto
     inteiro na dica do mouse, `minimumSizeHint` não depende mais do
     tamanho do texto); `Painel` ganhou `setMaximumWidth(LARGURA)` como
     trava definitiva; dois rótulos em `PainelFiltroDaPagina` que tinham
     escapado do `setWordWrap(True)` (nome do filtro, "tecla N") ganharam.

## Decisões fechadas nesta sessão, e por quê

- **7 livros de teste, não 5** — o Samuel escolheu ampliar depois de ver os
  9 disponíveis. Lista e motivo de cada um no topo do `PEDIDOS.md`.
- **Trava global em vez de reescrever o acesso a PDF.** Trocar biblioteca ou
  redesenhar como o programa lê PDF estava fora de cogitação (`CLAUDE.md`
  proíbe "trocar biblioteca" sem perguntar); um `threading.Lock()` em volta
  das chamadas nativas resolve o mesmo problema com uma mudança pequena e
  reversível. Isso está dentro da alçada de decidir sozinho (`CLAUDE.md`
  seção 6: "paralelismo" é item que o Claude Code pode decidir).
- **Cache de assinatura em vez de remontar a tira sob demanda de outro
  jeito** — mantém o comportamento (remonta quando precisa) sem inventar
  mecanismo novo.

## Caminhos tentados e descartados, e por quê

- **Hipótese "o modelo ONNX de detecção de layout carrega devagar e trava"**
  — medido direto (fora da tela): 1,57s a primeira vez, 0,71s depois. Rápido
  demais para explicar o travamento. Descartada.
- **Hipótese "é um glitch de repintura da tela"** (para o painel torto) —
  forcei a janela a maximizar e restaurar (repaint completo) e o defeito
  continuou idêntico, pixel a pixel. Descartada; confirmou que é um bug de
  layout de verdade, não um problema visual passageiro.
- **Reproduzir o travamento com um script isolado, uma thread só** — rodei
  a geração de miniatura (dpi=20) nas 134 páginas do Palatino, sequencial,
  sem nenhuma outra tarefa rodando junto: **nunca travou**, todas as páginas
  abaixo de 0,5s. Só reproduz com VÁRIAS threads batendo no mesmo arquivo ao
  mesmo tempo (o cenário real do programa rodando). **Lição para quem for
  investigar um travamento parecido: testar em isolamento não basta — o
  bug só aparece com concorrência de verdade.**

## Descobertas de comportamento real, caras de redescobrir

- **MuPDF (PyMuPDF/fitz) não é seguro para uso concorrente entre threads**,
  mesmo cada thread abrindo o seu próprio `fitz.Document` — a biblioteca
  guarda estado global (cache de fontes/imagens) por baixo, e duas chamadas
  nativas ao mesmo tempo podem travar dentro de `fz_run_display_list` para
  sempre, sem exceção, sem log. Não é um bug de UMA página específica: é a
  concorrência em si.
- **`QPushButton` não elide nem quebra texto sozinho.** Se o texto não
  cabe, o botão simplesmente pede mais espaço (via `minimumSizeHint`) em vez
  de cortar — e um `QVBoxLayout`/`QScrollArea` com `setWidgetResizable(True)`
  deixa isso vazar: a coluna inteira alarga, sem aviso, sem erro.
- **`py-spy` é a ferramenta certa para travamento de app PySide6.** Instalado
  fora do projeto (`pip install --user py-spy`, python do sistema 3.12, não
  o `.venv` do projeto que é 3.14) — o binário fica em
  `C:\Users\fotog\AppData\Roaming\Python\Python312\Scripts\py-spy.exe`.
  `py-spy dump --pid <PID>` mostra a pilha de TODAS as threads; `--locals`
  mostra variáveis locais também. Não precisa reiniciar o programa nem
  adicionar instrumentação: funciona no processo já travado.
- **`pywinauto` (mesma instalação `--user`) consegue pilotar a janela de
  verdade já aberta**, sem precisar escrever script de teste separado —
  `Application(backend="uia").connect(process=pid)`, depois
  `.child_window(title=..., control_type=...).click_input()`. Serviu para
  reproduzir o travamento ao vivo clicando exatamente como o Samuel clicou.
  Cuidado: `capture_as_image()` pega o que estiver na FRENTE da tela nesse
  retângulo, não necessariamente o conteúdo da janela-alvo — sempre
  `.set_focus()` antes de tirar print. `GetWindowRect` via PowerShell (sem
  DPI awareness) devolve coordenadas escaladas, não confiar no valor
  absoluto — só comparar proporções, ou usar a `.rectangle()` do próprio
  pywinauto.

## Pergunta em aberto — a mais importante deste checkpoint

**As três correções acima passam nos testes automáticos e eu reproduzi e
confirmei cada uma ao vivo (com `py-spy`/`pywinauto`, não só olhando o
código) — mas o Samuel ainda NÃO abriu o programa pelo atalho normal e
confirmou com as próprias mãos que ficou bom.** A última coisa que perguntei
a ele, sem resposta ainda quando este checkpoint foi escrito: *"Agora é sua
vez de testar de verdade: abra a janela que já deixei aberta, mexa no
Palatino como antes... e me diga se travou ou se o painel voltou a ficar
torto."*

**Por isso: NADA foi commitado ainda.** `git status` mostra
`core/pdf_io.py`, `ui/tarefas.py`, `ui/tela_conferir.py`,
`ui/widgets/paineis.py` e `PEDIDOS.md` modificados, sem stage. Isso é de
propósito — `CLAUDE.md` seção 8 diz "eu abro pelo atalho, testo, e marco
aprovado" ANTES do commit (passo 9 antes do passo 10), e a razão de existir
dessa regra é justamente não deixar o Claude Code se autoaprovar de novo
(era o problema original de 57+ commits sem nenhum aprovado). **Quem pegar
esta sessão: pergunte ao Samuel se ele já testou e aprovou antes de
commitar.** Se ele já confirmou (em uma mensagem que não chegou a entrar
neste arquivo), pode seguir direto para o commit.

## Pontas soltas, ainda não resolvidas

- **`empacotar.py` tem uma mudança não commitada de ANTES desta sessão**
  (tirou `"scipy"` da lista de bibliotecas excluídas do instalador) — não fui
  eu quem fez, encontrei já assim no início da sessão, avisei o Samuel, e
  ele não respondeu sobre isso especificamente. Não commitar misturado com
  as correções de hoje sem perguntar primeiro.
- **`historico/handoff-editor-de-impressao 2.md`** continua órfão, não
  commitado (mencionado na PARTE -1 abaixo — mesma suspeita de sincronizador
  do Google Drive, ainda não investigada).
- **`.pytest_cache/`** apareceu como pasta não rastreada e não está no
  `.gitignore` — inofensivo (é regenerável), mas vale adicionar ao
  `.gitignore` num commit de limpeza futuro.

## Próximo passo recomendado

1. Confirmar com o Samuel se as três correções acima passaram no teste real
   dele (perguntar, não supor).
2. Commitar as três correções (uma vez confirmado), cada uma como commit
   separado se possível — travamento (cartões), travamento (MuPDF/trava
   global + tira de miniaturas), painel torto.
3. Depois disso, a fila já combinada com o Samuel:
   - **Investigar os pontinhos pretos no filtro Preto e branco** (defeito
     visual visto ao vivo no Rhetorica Christiana, página 6 — plano de
     ataque de 4 tentativas já desenhado numa sessão de plan mode desta
     mesma conversa: quantificar primeiro, depois despeckle maior, depois
     pré-processamento, depois trocar binarizador só se precisar).
   - Retomar a Fase 4 do `PLANO-RETOMADA.md`: varredura bloco a bloco do
     `PEDIDOS.md`, começando pelo Bloco 1 e Bloco 4.

## Como rodar e testar (confirmado nesta sessão)

```
cd D:\programas\EditorImpressao

.venv\Scripts\python.exe -m pytest tests -q          # 279 casos, confirmado passando
.venv\Scripts\pythonw.exe teste_botoes.py             # 118 acoes, 0 falhas (usar QT_QPA_PLATFORM=offscreen no bash)
```

Abrir o programa de verdade para o Samuel testar: atalho "Editor de
Impressao (desenvolvimento)" na área de trabalho, ou
`.venv\Scripts\pythonw.exe main.py` (aceita opcionalmente um caminho de PDF
como argumento, que abre direto — `janela.abrir_livro(caminho)`).

## Ambiente — instalado nesta sessão (fora do `.venv` do projeto)

Ferramentas de diagnóstico, no Python do sistema (3.12, `pip install
--user`), não no `.venv` do projeto (3.14) — não afetam o programa em si:

- `py-spy` 0.4.2
- `pywinauto` 0.6.9 (+ `pywin32`, `comtypes`, `six`)
- `pillow` 12.3.0 (pywinauto precisa para `capture_as_image`)

---

# PARTE -1 — Checkpoint de 07/09/2026 (leia isto primeiro)

Esta parte é o resumo de continuação mais recente. O resto do documento
(PARTE 0 em diante) é o handoff máximo gerado mais cedo no mesmo dia — ainda
vale como referência histórica e institucional, mas **os processos de
trabalho que ele descreve foram substituídos** pelos três arquivos abaixo,
adicionados à raiz do projeto depois dele:

- **`CLAUDE.md`** — regras de trabalho atuais. Lê primeiro, sempre.
- **`PEDIDOS.md`** — a lista de conferência (~80 itens, 10 blocos). **Só o
  Samuel marca `[x]` APROVADO.**
- **`PLANO-RETOMADA.md`** — o diagnóstico e as 5 fases da retomada.

## Estado atual — o que está validado ao vivo, não só no código

- **Fase 0 do `PLANO-RETOMADA.md` está completa**, os três itens:
  1. Causa da "tela antiga" (sem menu, barra já preta) investigada: não há
     tela legada no código-fonte — a causa mais provável eram três
     instaladores `.exe` soltos na área de trabalho, construídos numa janela
     de tempo entre o commit da barra quase-preta e o da barra de menu. Já
     arquivados (não estão mais soltos).
  2. Atalho **"Editor de Impressao (desenvolvimento)"** criado na área de
     trabalho do Samuel — roda `.venv\Scripts\pythonw.exe main.py` direto do
     código em `D:\programas\EditorImpressao`, sempre a versão mais nova.
  3. `teste_botoes.py` ampliado para clicar de verdade em **todas** as telas
     (antes só cobria a de conferir): tela inicial, opções, conferir,
     ampliada, o diálogo de confirmar, tela final e o menu inteiro.
     **Rodado de verdade: 118 ações, 0 falhas.** Os 279 casos de
     `pytest tests` continuam passando.
- Um bug real de produção foi achado e **corrigido**: a ação "Abrir" do menu
  simulava um clique de mouse com `evento=None`, o que levantava
  `AttributeError` toda vez que alguém clicasse nela pelo menu (não pelo
  clique normal na área de arrastar). Corrigido extraindo a lógica para
  `AreaArrastar.abrir_dialogo_de_arquivo()`, usado pelos dois caminhos.
- O handoff máximo (PARTE 0 em diante) e os três novos documentos foram
  escritos **antes** da migração de hoje e precisaram ter os caminhos
  corrigidos (Desktop → `D:\programas\...`) ao serem adotados — já feito.

## Decisões fechadas nesta sessão, e por quê

- **O projeto vive em `D:\programas\EditorImpressao`, não mais em
  `C:\Users\fotog\Desktop\EditorImpressao`.** A pasta do C: virou o backup
  (`backup_path` no registro de projetos). Motivo: pedido direto do Samuel,
  depois de uma investigação mostrar que o C: era a cópia realmente ativa e o
  D: (que ele achava que era a ativa) estava com ~13 commits de atraso.
- **As pastas de apoio (acervo de teste, mockups, queixas do Kaique) foram
  para `D:\programas\EditorImpressao-arquivos\`**, separadas do repositório
  git. Motivo: tirar arquivos grandes e não-código da área de trabalho, a
  pedido do Samuel. Os 4 scripts com caminho fixo para essas pastas
  (`gerar_prints.py`, `relatorio.py`, `montar_para_conferir.py`,
  `teste_completo.py`) e a busca automática do `avaliar.py` foram
  atualizados.
- **Adotado o novo `CLAUDE.md`/`PEDIDOS.md`/`PLANO-RETOMADA.md`** trazidos
  pelo Samuel de uma conversa de replanejamento (fora deste Claude Code),
  mesclando duas regras do `CLAUDE.md` antigo que a nova versão tinha
  perdido: "relatório sempre em três formatos" (o Samuel não abre `.md`) e o
  ponteiro para este handoff.
- **`teste_botoes.py` foi expandido, não reescrito, e não fundido com
  `teste_interface.py`.** Os dois continuam existindo porque testam coisas
  diferentes: `teste_botoes.py` clica de verdade (`.click()`/`.trigger()`,
  passa pelo sinal do Qt); `teste_interface.py` chama métodos internos direto,
  para validar o *resultado* de uma ação, não a fiação do botão.

## Caminhos tentados e descartados

- **Detectar o diálogo aberto via `QApplication.activeModalWidget()`** —
  não funciona sob `QT_QPA_PLATFORM=offscreen` (usado para rodar o programa
  sem abrir janela de verdade neste ambiente): o diálogo nunca vira "ativo"
  de verdade, e o `.exec()` trava para sempre. **Substituído por**:
  interceptar o próprio método `.exec()` da classe do diálogo
  (`TelaAmpliada.exec`, `JanelaConfirmar.exec`), que aponta direto para a
  instância certa, sem depender de estado de janela ativa.
- **Fechar um `QMessageBox` com `.close()` sem clicar em nada, achando que
  seria neutro** — o Qt trata isso como clicar no botão de `RejectRole`. Numa
  caixa tipo "conferir" / "processar assim mesmo", isso sempre escolhia
  "conferir" e o fluxo de processar nunca avançava. **Substituído por**:
  clicar de propósito no botão de `AcceptRole` quando ele existir.
- **Testar `teste_botoes.py` contra um PDF do acervo real** (`TESTES EDITOR
  DE IMPRESSAO\LIVROS PARA TESTE`) — **não fazer isso.** Cada um dos nove
  livros já tem um projeto de rodada de teste anterior salvo em
  `%LOCALAPPDATA%\EditorImpressao\projetos\`, e a limpeza automática no fim
  do script (`remover da lista`) apagaria esse histórico. Descoberto na
  prática: a primeira tentativa quase apagou um projeto do Boécio de 05/08
  (só não apagou porque o script travou antes de chegar na limpeza).
  **Substituído por**: o script agora gera seu próprio PDF sintético de duas
  páginas quando rodado sem argumento.

## Descobertas de comportamento real (Qt/PySide6), caras de redescobrir

- `botao.click()` / `acao.trigger()` **não propagam** uma exceção levantada
  dentro do slot conectado para um `try/except` em volta da chamada — ela vai
  direto para `sys.excepthook` e o processo continua normalmente. Detecção de
  falha em teste de clique real **tem** que ser via `sys.excepthook` global,
  não `try/except`.
- `QAction.isEnabled()` continua `True` mesmo quando o `QMenu` inteiro
  (dropdown) está desabilitado — só o `menuAction()` do menu-pai reflete
  isso. Um varrimento "clique em toda ação habilitada" tem que checar os
  dois níveis, senão aciona coisas que um clique de mouse de verdade nunca
  alcançaria.
- Bytecode cache (`__pycache__`) copiado junto com o código (via
  `robocopy /COPY:DAT`, que preserva timestamp) **não recompila**, mesmo que
  o arquivo tenha vindo de outro caminho — o `co_filename` embutido no
  `.pyc` antigo aparece em tracebacks/warnings, mostrando o caminho de
  origem (C:) mesmo já rodando do D:. Inofensivo, mas confunde debug. Já
  limpo; se acontecer de novo depois de outra cópia/robocopy, apagar
  `__pycache__` resolve.

## Perguntas em aberto

- **A barra de rolagem: preta ou cinza médio?** O código hoje está em cinza
  médio (`#a8a49e`, revertido de propósito em 08/08 — o preto puro lia como
  risco de erro atravessado no pé da tela; ver `CLAUDE.md` seção 9). O novo
  `PEDIDOS.md`/`CLAUDE.md` (Bloco 9, queixa do Kaique) presumem "preta" como
  o estado correto — desatualizado. **Pergunta exata feita ao Samuel:** "A
  barra de rolagem: o código hoje está em cinza médio (revertido de
  propósito em 08/08, porque o preto puro lia como risco de erro na tela). O
  novo PEDIDOS.md/CLAUDE.md que você trouxe presume que 'preta' ainda é o
  certo. Qual fica?" — **resposta do Samuel: "isso é irrelevante agora,
  deixe para depois."** Ainda sem decisão; não mexer na cor sem perguntar de
  novo quando for a hora.
- Achado, mencionado ao Samuel mas **não perguntado diretamente**: existe um
  arquivo `historico/handoff-editor-de-impressao 2.md`, sozinho, criado às
  15:19 de 07/09 sem ninguém pedir — parece cópia de conflito de algum
  sincronizador rodando em segundo plano (o Samuel tem uma pasta de backup
  no Google Drive, `D:\Backup_GoogleDrive\`). Não commitado, não apagado.
  Vale perguntar ao Samuel se algo está sincronizando essa pasta sem ele
  saber.
- A pasta duplicada `LIVROS PARA FAZER TESTE (duplicata)` (~1,5 GB) dentro de
  `D:\programas\EditorImpressao-arquivos\` ainda não foi apagada — o Samuel
  não confirmou se quer apagar.

## Próximo passo recomendado

**Fase 1 do `PLANO-RETOMADA.md`: escolher os 5 PDFs fixos de teste** (folha
dupla amarelada, capa colorida, página com gravura, folha com mancha do
verso, scan ruim/baixa resolução) e preencher os nomes no topo do
`PEDIDOS.md`. Depois disso, começar a varredura pelo Bloco 1 e o Bloco 4
(filtros) do `PEDIDOS.md` — são os que mais importam, por essa ordem.

## Como rodar e testar (comandos exatos, confirmados nesta sessão)

```
cd D:\programas\EditorImpressao

.venv\Scripts\python.exe main.py                          # o programa
.venv\Scripts\python.exe -m pytest tests -q                # 279 testes (confirmado passando)
.venv\Scripts\python.exe teste_botoes.py                   # clica em tudo; gera PDF de teste sozinho
.venv\Scripts\python.exe avaliar.py                         # a régua dos filtros
.venv\Scripts\python.exe avaliar_selecao.py                 # a régua da seleção
```

Para rodar sem abrir janela de verdade (usado nesta sessão, roda em
segundo plano/CI): prefixar com `QT_QPA_PLATFORM=offscreen` (bash) ou
`$env:QT_QPA_PLATFORM="offscreen"` (PowerShell) antes do comando.

## Ambiente — nada novo instalado nesta sessão

Nenhum pacote novo foi instalado (`pytest-qt` foi considerado e
**descartado** para o `teste_botoes.py` — ver justificativa no próprio
commit; `PySide6.QtTest` já incluso no PySide6 já instalado bastou). A
migração de disco não mudou o `.venv` nem a versão do Python (3.14.3).

---

# PARTE 0 — Quem está envolvido, e por quê

**Pe. Rosenei**, sacerdote católico, fundou um **instituto de preservação de
livros** com três objetivos: (a) preservar livros que não são mais publicados,
(b) reviver as formas tradicionais de fabricação de livros, (c) manter o
espírito católico de guardar o conhecimento acumulado ao longo dos séculos.

**O instituto ainda não tem sede física.** É apoiado por uma empresa
sementeira, a **Sementes Ponto Alto**, que dá ajuda mensal e cede espaço num
depósito para guardar livros.

**Kaique** é o impressor do instituto — o **usuário final** deste aplicativo.
Sem formação técnica nenhuma. Hoje ele usa o **CamScanner no celular** para
limpar as páginas escaneadas antes de imprimir; é a régua real de comparação.

**Samuel** coordena a parte digital do projeto, toma as decisões e conduz as
conversas com o Claude.

**Objetivo geral:** organizar o projeto para captar mais recursos, conseguir
uma sede, e criar as ferramentas de que o instituto precisa.

## As frentes do projeto (visão macro)

1. **Institucional / captação** — formalizar (CNPJ, estatuto), material para
   doadores, meta de sede. Ideia levantada: parceria com uma universidade (de
   preferência católica) para acesso a equipamento de digitalização e a
   espaço.
2. **Produção do livro** (fluxo do Kaique) — do livro físico velho ao PDF
   limpo e ao livro reimpresso. **É a frente deste aplicativo, e a que está em
   andamento.**
3. **Biblioteca / catalogação** — cadastrar, separar por tema, saber o que
   existe e onde está. Já foram levantados programas prontos de catálogo de
   arquivo (**ArchivesSpace, PastPerfect, CollectiveAccess, Preservica**) —
   vale investigar antes de construir algo do zero.
4. **Transcrição** — passar textos antigos para digital.
5. **Site** — vitrine, catálogo público, canal de doação.

As frentes 1, 3, 4 e 5 estão em espera; só a 2 está ativa.

## Ferramentas de digitalização já pesquisadas (contexto para o planejamento)

O fluxo profissional de arquivistas, levantado antes de decidir construir este
app:

- **NAPS2** (v8.2.1) — escanear. OCR embutido, versão portátil,
  compartilhamento de scanner por rede, linha de comando.
- **ScanTailor Advanced / Experimental** — limpar e endireitar. Manual,
  C++/Qt, GPL v3. (O original, `scantailor.org`, está congelado desde 2012 e o
  repositório foi arquivado em 2020.)
- **OCRmyPDF** (v17.x) — camada de texto pesquisável, com **unpaper** embutido
  (`--clean`). Adiado para uma v2 deste app.
- **PDF-XChange Editor** (v11) — 70% grátis, faz deskew/OCR/organização de
  páginas; tem desconto para caridade.
- **Hardware** (para preservação, captura não destrutiva): scanner overhead
  (CZUR, ScanSnap SV600), filtro polarizador contra reflexo, 600–1200 DPI para
  captura. Bibliotecas universitárias às vezes emprestam scanner profissional
  de graça.
- **GMIC** (dentro do Krita) — recuperação de cor em livros ilustrados.

**Conclusão estratégica registrada na época:** a maioria dessas ferramentas já
existe pronta. O que o instituto precisa criar de novo é (a) o "CamScanner
para PC" do Kaique — este app — e, depois, (b) a catalogação e o site.

---

# PARTE 1 — O que é o programa

Aplicativo de desktop para Windows que **recupera PDFs de livros antigos
escaneados e os prepara para reimpressão em cadernos**. Um "CamScanner para
PC".

**Quem usa é o Kaique, impressor, sem formação técnica.** Toda a interface é em
português do Brasil, sem jargão: ele nunca vê "Sauvola", "k" ou "deskew" — vê
"Força do preto", "Melhorar", "girar a folha".

**Duas versões anteriores fracassaram.** Uma travava (feita em customtkinter), a
outra dava qualidade ruim (fórmula caseira de filtro). Daí vêm as regras rígidas
abaixo, e nenhuma delas é preferência de estilo: cada uma é cicatriz.

## As regras que não se negociam

- **PySide6, nunca tkinter.** Foi o que travou a versão anterior.
- **Uma página por vez na memória.** Ler, processar, escrever, soltar. O pico
  não pode crescer com o tamanho do livro; há livro de 300 MB no acervo.
- **Nenhum emoji em rótulo de interface.**
- **Textos de interface com acento. Caminhos de disco sem acento** — uma vez a
  pasta de saída sumiu da vista por causa disso.
- **Algoritmo consagrado em vez de fórmula própria.** A binarização é o Sauvola
  do DoxaPy, o mesmo caminho do ScanTailor.
- **Nenhum modelo generativo.** Modelo que produz pixel pode inventar detalhe
  numa gravura de 1579, e detalhe inventado entra no PDF como se fosse o livro.
  Rede neural aqui só segmenta: aponta onde estão as coisas, nunca desenha.

## Os quatro filtros

| Filtro | O que faz |
|---|---|
| Original | não mexe |
| Preto e branco | binarização local de Sauvola: tira o amarelado e o texto do verso |
| Melhorar | divide pelo fundo estimado: limpa a iluminação sem tocar na cor |
| Mágico pro | Melhorar + contraste local + cor + nitidez, para capas e gravuras |

## O fluxo

Arrasta o PDF → marca o que quer fazer → confere página a página → escolhe onde
salvar → processa. Atalhos: setas navegam, Espaço marca "está certo", Tab pula
para a próxima dúvida, 1 2 3 4 trocam o filtro, Ctrl+Z desfaz.

## As duas réguas

O projeto mede antes de mexer. São dois programas de medição:

- **`avaliar.py`** — a régua dos filtros. Roda sobre os nove livros do acervo e
  responde: alguma página saiu **pior** do que entrou? O critério de aceitação é
  que esse número seja **zero**.
- **`avaliar_selecao.py`** — a régua da seleção, criada em 06/08/2026. Mede se o
  programa acertou o que é gravura, o que é letra e o que é papel, em 26 páginas
  escolhidas.

## O protocolo de trabalho

**Medir antes, uma mudança por vez, medir de novo, reverter se qualquer número
piorar.** Se a mudança parecer valer a pena mesmo assim, não reverter por conta
própria: apresentar os dois resultados.

E antes de julgar qualquer resultado visual: **abrir todas as imagens.**
Percentual não é veredito. Essa regra existe porque já foi reportado "10 de 10
corretas" tendo olhado uma imagem — seis estavam erradas.

## Fronteira de autonomia

**Pode decidir sozinho:** limiar, janela, `k`, tamanho de bloco, ordem interna
de operações dentro de um filtro, troca de algoritmo de binarização, cache,
paralelismo, memória.

**Precisa perguntar antes:** criar ou remover filtro, mudar nome de filtro,
mudar qualquer tela, acrescentar ou tirar controle da interface, mudar o formato
dos arquivos de dados, alterar desfazer/refazer, trocar biblioteca.

## Onde ficam as coisas

```
core/filtros.py            os quatro filtros
core/selecao.py            as regiões marcadas (gravura, letra, papel)
core/detectar_regioes.py   acha sozinho o que é o quê
core/rede_selecao.py       a rede neural de segmentação (só aponta, nunca desenha)
core/pipeline.py           a ordem: dividir, cortar, endireitar, filtrar, impor
core/cadernos.py           imposição e conferência da sequência
avaliar.py                 a régua dos filtros
avaliar_selecao.py         a régua da seleção
conferir.py                a tela de conferir amostras falando
relatorios/melhorias.md    o histórico de tudo que foi tentado, inclusive o que falhou
```

**Mudou em 07/09/2026:** as pastas de apoio (acervo de teste, mockups,
queixas do Kaique) saíram da área de trabalho e foram para
`D:\programas\EditorImpressao-arquivos\`, numa pasta separada do código
(que fica em `D:\programas\EditorImpressao\`, o repositório git). Os scripts
que tinham caminho fixo — `gerar_prints.py`, `montar_para_conferir.py`,
`relatorio.py`, `teste_completo.py` — foram atualizados para o novo caminho, e
`avaliar.py` ganhou o novo caminho na lista de candidatos de busca automática
(antes só olhava dentro da área de trabalho).

**Acervo de teste:**
`D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA
TESTE`, nove livros, 2903 folhas. As queixas do Kaique estão em
`D:\programas\EditorImpressao-arquivos\BIBLIOTECA DO FIM DOS TEMPOS\Teste de
livros` — são `.txt` soltos com um print ao lado, e **são fonte de
requisito**.

**A pasta duplicada** (`LIVROS PARA FAZER TESTE`, ~1,5 GB, byte a byte
idêntica aos nove livros de dentro de `TESTES EDITOR DE IMPRESSAO\LIVROS PARA
TESTE` — sobra do prompt de testes original de 18/07) foi levada junto para
`D:\programas\EditorImpressao-arquivos\LIVROS PARA FAZER TESTE (duplicata)`,
sem apagar. Nenhum script aponta para ela; fica ali só até o Samuel decidir se
apaga.

Como rodar:

```
.venv\Scripts\python.exe main.py                 o programa
.venv\Scripts\python.exe -m pytest tests -q      os 150 testes
.venv\Scripts\python.exe avaliar.py              a régua dos filtros
.venv\Scripts\python.exe avaliar_selecao.py      a régua da seleção
.venv\Scripts\python.exe conferir.py             conferir amostras falando
```

---

# PARTE 1B — Todas as funcionalidades: o que o app faz, o que falta

Lista mestra, cruzando a especificação original (18/07), os 68 pedidos feitos
desde então e uma conferência direta no código em 07/09/2026 — não só no que
este documento dizia. `[x]` feito e conferido, `[~]` parcial, `[ ]` falta.

## Processamento da página

- `[x]` Dividir a folha ao meio, detectando a lombada sozinho — corrigir
  arrastando a linha, "não dividir esta", "usar em todas", girar 90°
- `[x]` Endireitar sozinho (perfil de projeção, até ±5°, não mexe abaixo de
  0,1°) — ajuste manual arrastando o mouse, com linhas-guia
- `[x]` Cortar bordas sozinho, com alças arrastáveis na prévia
- `[x]` Apagar página, com opção de restaurar
- `[x]` Aplicar filtros diferentes em páginas diferentes, saindo num PDF só
- `[x]` Transformar uma capa inteira em página branca ("marcar como papel")
- `[~]` Filtro só numa parte da página — existe ("Filtro só neste pedaço", aba
  Marcar) mas nunca foi conferido ponta a ponta num livro real

## Os quatro filtros

- `[x]` Original / Preto e branco (Sauvola) / Melhorar / Mágico pro
- `[ ]` Escolher o binarizador certo por página — hoje usa um só para tudo;
  comparados os 18 do DoxaPy, não existe vencedor único
- `[ ]` Rubricação vermelha não virar barra preta no Preto e branco

## Ferramenta de seleção (aba Marcar) — conferido direto no código hoje

- `[x]` Marcar à mão: gravura, letra, papel (`core/selecao.py`)
- `[x]` Detecção automática das três (`core/detectar_regioes.py`,
  `core/rede_selecao.py`)
- `[x]` "Pegar tudo desta cor" (compara por matiz, não vaza como a varinha)
- `[x]` Marcar a folha inteira como papel = fica em branco
- `[x]` Selecionar por cor manualmente, para quando o automático errar
- `[~]` Reconhecer letra antiga — 23 de 26 na régua da seleção; os 3 que
  faltam pedem um modelo treinado em documento histórico (Eynollah, dhSegment
  ou Kraken/eScriptorium), o que por sua vez pede marcar 30-40 páginas à mão
  como gabarito primeiro

## Sistema de alertas (onze tipos — "o princípio central do app")

- `[x]` página colorida, lombada incerta, não parece dupla, muito torta,
  ângulo suspeito, em branco, escura demais, apagada demais, corte pegou
  conteúdo, resolução baixa, tamanho diferente
- `[x]` Contador clicável, miniatura laranja, faixa explicativa com botão de
  correção, painel "Páginas para revisar" agrupado por tipo, aviso antes de
  processar
- `[ ]` Critério "menos de 10% das páginas marcadas" nunca foi conferido —
  hoje só "ângulo suspeito" já passa de 12% do acervo

## Ajustes manuais

- `[x]` Medidores deslizantes: Força do preto, Intensidade, Clareza do fundo
  (0 a 100, prévia ao vivo)
- `[x]` Desfazer ilimitado gravado em arquivo, sobrevive fechar e reabrir

## Navegação e tela

- `[x]` Zoom, arrastar, atalhos (setas, Espaço, Tab, 1-4, R, Delete, Ctrl+Z,
  Ctrl+Shift+Z, Ctrl+Enter)
- `[x]` Modo comparar: dois filtros lado a lado, zoom sincronizado
- `[x]` Barra de rolagem preta
- `[x]` Regras de fundo respeitadas: sem emoji, acento certo, PySide6
- `[ ]` Ver PARTE 1C — lista antiga de pedidos de navegação (roda do mouse
  trocar página, campo "ir para página", Page Up/Down, Home/End) cujo status
  não foi reconfirmado nesta rodada

## Salvar o resultado

- `[x]` Escolher pasta, editar nome, lembrar última pasta usada, avisar
  duplicata ou pasta sem permissão

## Cadernos (o objetivo final)

- `[x]` Montar cadernos (imposição), caminho rápido sem rasterizar quando só
  isso está marcado
- `[x]` Conferir a sequência simulando a dobra
- `[ ]` Critério "filtros diferentes por página, um PDF só" nunca foi
  conferido ponta a ponta num livro de verdade

## Instalador

- `[x]` Inno Setup: instala em Arquivos de Programas, atalhos, aparece em
  Adicionar/remover programas, assistente em português, desinstalador

## Medição e testes (para o Claude, não para o Kaique)

- `[x]` `avaliar.py` (régua dos filtros) — 4 motivos de reprovação restantes,
  3 deles a mesma página (Graduale 126, uma partitura manuscrita)
- `[x]` `avaliar_selecao.py` (régua da seleção) — 3 de 26 restantes
- `[x]` `conferir.py`, com ditado por voz (Win+H)
- `[ ]` Falta um número na régua: "guardou a sujeira" — o Otsu passa zero
  pioras mas guarda o dobro de tinta do Sauvola, e nenhum critério pega isso
- `[ ]` **A pergunta decisiva, pendente desde 18/07:** comparar com o
  CamScanner nas 5 páginas difíceis já preparadas em `para_comparar/`, e
  responder em uma frase — sim, não, ou ainda não substitui

---

# PARTE 1C — Itens antigos cujo status não foi reconfirmado nesta rodada

Vêm de um handoff de 29/07/2026, escrito antes das últimas rodadas de
conserto. Podem já estar resolvidos — não foram checados de novo em
07/09/2026. Quem for replanejar deve **verificar o código antes de assumir**
que ainda valem.

## Preto e branco pior que o original em papel manchado (grave, se ainda valer)

Em impressos antigos (ex.: `bleed_through_pag0575`), o Sauvola estava
**quebrando as letras** e enchendo o fundo de pontinhos — o original amarelado
ficava mais legível que o resultado. Causa provável: janela do Sauvola pequena
demais, pegando a textura do papel como texto.

Caminhos levantados para testar: janela bem maior (calculada por DPI/altura),
trocar para **Wolf** (ou Gatos/NICK/ISauvola), pré-processar (normalizar
iluminação + leve desfoque + CLAHE) antes de binarizar, despeckle mais
agressivo, e **ajuste automático de parâmetro por página** (um livro do século
XIV e um do século XX não deveriam usar o mesmo valor — isto pode já estar
coberto pelo item "escolher o binarizador por página" da PARTE 1B/1, que segue
pendente).

## Navegação entre páginas (pedidos específicos, não confirmados como feitos)

- Setas fixas nas pontas da tira de miniaturas
- Roda do mouse **sobre a tira** rola a tira
- Roda do mouse **sobre a imagem** troca de página (com zoom ativo, dá zoom)
- Miniatura da página atual sempre visível (não sair da vista ao rolar)
- Campo "ir para página" (digitar o número)
- Page Up / Page Down pula 10 páginas
- Home / End vai para a primeira / última página
- Barra de rolagem mais alta (mais fácil de clicar)

## Regra proposta que talvez nunca tenha sido implementada

Criar uma verificação automática que compara a legibilidade antes/depois de um
filtro e **avisa quando o próprio filtro piora a página** — não só quando
piora em relação às outras réguas já existentes.

---

# PARTE 2 — Todos os 68 pedidos, palavra por palavra

Tirados dos transcritos de todas as conversas, do primeiro ao último.

## Pedido 1 — 18/07/2026 14:53

*Documento longo (40.566 caracteres). Está inteiro no **Apêndice A — A
especificação original**, no fim deste arquivo.*

> # Editor de Impressão — especificação completa e prompt para o Claude Code

## Pedido 2 — 18/07/2026 14:58

> sim, siga no modo automatico e faça todo app

## Pedido 3 — 18/07/2026 16:19

> você terminou?

## Pedido 4 — 18/07/2026 16:23

> onde está o arquivo .exe?

## Pedido 5 — 18/07/2026 16:30

> dsfsdfDuas coisas:
>
> 1. A pasta dist está vazia — não achei o .exe. Confira o que
> aconteceu e gere de novo.
>
> 2. Quero um INSTALADOR de verdade, não só o programa portátil.
> Use Inno Setup para gerar um "EditorImpressao-Setup.exe" que:
> - instale em "Arquivos de Programas"
> - crie atalho no menu Iniciar e na área de trabalho
> - apareça na lista "Adicionar ou remover programas" do Windows
> - tenha o assistente em português
> - inclua desinstalador
> Deixe o script .iss no repositório e um comando pra gerar tudo
> de uma vez (empacotar + instalador).
> Continue gerando também a versão portátil em pasta, pra quem
> preferir rodar de pendrive.
>
> 3. FALTOU uma função importante: escolher onde salvar o PDF.
> Hoje ele salva sempre em Documentos. Quero:
> - na tela final (ou antes de processar), um botão "Escolher pasta"
>   abrindo o seletor de pastas do Windows
> - campo mostrando o caminho escolhido, com opção de editar o nome
>   do arquivo
> - lembrar a última pasta usada e sugerir ela na próxima vez
>   (guardar nas configurações)
> - avisar se já existir arquivo com o mesmo nome, oferecendo
>   substituir ou renomear
> - se a pasta não tiver permissão de escrita, avisar em português
>   e sugerir outr

## Pedido 6 — 18/07/2026 16:54

> onde está o .exe?

## Pedido 7 — 18/07/2026 16:57

> [Image #3] não estou achando o .exe, eu quero que faça uma nova pasta e faça o .exe

## Pedido 8 — 18/07/2026 17:17

> Quero limpar tudo e ficar só com o instalador. Faça nesta ordem:
>
> 1. CORRIJA O TRAVAMENTO
> Ao clicar nos botões da tela de conferir ("esta certo",
> "nao cortar esta", "voltar ao automatico", "usar em todas"),
> o programa fecha sozinho. Encontre a causa e corrija.
> Depois, envolva os handlers de evento com tratamento de erro:
> nenhuma exceção pode fechar a janela — deve virar aviso em
> português e registrar no log.
>
> 2. CORRIJA O LAYOUT SOBREPOSTO
> A caixa azul de explicação e os botões estão sendo desenhados
> POR CIMA da imagem da página, escondendo o conteúdo.
> Empilhe na tela de conferir, de cima para baixo, sem nenhuma
> sobreposição:
>   1. cabeçalho (título + alertas + desfazer/refazer)
>   2. abas
>   3. área da imagem  ← ocupa o espaço que sobrar (stretch)
>   4. caixa azul de explicação
>   5. linha de botões
>   6. tira de miniaturas
>   7. rodapé (voltar / confirmar e processar)
> Use QVBoxLayout de verdade. NÃO usar setGeometry, move() nem
> widget flutuando sobre o visualizador.
> Teste redimensionando a janela em vários tamanhos.
>
> 3. TESTE VOCÊ MESMO antes de me entregar
> Abra o programa, carregue um PDF, clique em TODOS os botões de
> todas as abas, redimensione a janela. Só me chame quando não
> travar mais e o layout estiver correto.
>
> 4. LIMPE TUDO E ME ENTREGUE SÓ O INSTALADOR
> - apague as pastas build/ e dist/ e qualquer .exe ou versão
>   portátil anterior
> - gere APENAS o instalador com Inno Setup
> - coloque o arquivo final na minha Área de Trabalho, dentro de
>   uma pasta chamada "Editor de Impressao"
> - dentro dessa pasta quero SÓ o "EditorImpressao-Setup.exe",
>   nada mais — sem _internal, sem pastas de bibliotecas
> - o instalador deve instalar em Arquivos de Programas, criar
>   atalho no menu Iniciar e na área de trabalho, aparecer em
>   "Adicionar ou remover programas", e ter desinstalador
> - assistente em português
>
> Pode usar as versões de teste durante o desenvolvimento, mas o
> que sobra pra mim no final é só o instalador.

## Pedido 9 — 18/07/2026 17:54

> Três coisas para ajustar:
>
> ════════════════════════════════════════════════
> 1. AMPLIAR A PÁGINA EM TELA GRANDE
> ════════════════════════════════════════════════
> Quero poder ver a página em tamanho grande para conferir de perto.
>
> - Clicar em qualquer um dos quatro cartões de filtro abre a
>   página AMPLIADA, ocupando a janela inteira
> - Duplo clique numa miniatura da tira também abre ampliado
> - Na tela ampliada:
>   · zoom com a roda do mouse, mais botões + / - / "ajustar à tela"
>   · arrastar com o mouse para mover a imagem quando com zoom
>   · setas ← → continuam mudando de página
>   · teclas 1 2 3 4 trocam o filtro sem sair da tela ampliada
>   · Esc ou X volta para a tela normal
>   · nome do filtro visível num canto
> - Modo COMPARAR na tela ampliada: dois filtros lado a lado, com
>   zoom e posição sincronizados, para eu comparar de perto
> - Mesma coisa nas abas "Onde cortar" e "Bordas": clicar amplia,
>   e a linha de corte / as alças continuam arrastáveis ampliadas
> - A imagem ampliada deve ser gerada em resolução maior que a da
>   prévia — não basta esticar a miniatura, fica pixelada
>
> ════════════════════════════════════════════════
> 2. REORGANIZAR OS CONTROLES + MEDIDORES DESLIZANTES
> ════════════════════════════════════════════════
>
> 2.1 Separar AJUSTES de AÇÕES
> Hoje "Força do preto" está na mesma linha que "só nesta / usar em
> todas / apagar página" — são coisas diferentes e confunde.
> Reorganize em blocos empilhados:
>
>   [ caixa azul de explicação ]
>
>   ┌─ Ajuste ───────────────────────────────────┐
>   │  Força do preto   fraco ──●──── escuro  leve│
>   └─────────────────────────────────────────────┘
>
>   Aplicar em:  [só nesta] [todas] [só nas próximas] | [apagar página]
>
> - O bloco "Ajuste" tem fundo e borda próprios, separado visualmente
> - "apagar página" afastado dos outros por um separador — é ação
>   destrutiva, não pode ficar colada nas demais
> - "só nesta" é o botão primário (destacado)
>
> 2.2 Trocar os três botões por medidor deslizante (QSlider)
> Em vez de "mais fraco / normal / mais escuro":
>
> - PRETO E BRANCO → slider "Força do preto", 0 a 100, padrão 50
>   · mapeia o k do Sauvola: 0 → k=0.40 (bem fraco),
>     50 → k=0.20 (normal), 100 → k=0.06 (bem escuro)
>   · rótulos "mais fraco" e "mais escuro" nas pontas
>   · texto ao lado em palavras: bem fraco / leve / normal / forte /
>     bem forte
>
> - MÁGICO PRO → slider "Intensidade", 0 a 100, padrão 50
>   · controla junto: saturação (1.0 a 2.2), clipLimit do CLAHE
>     (1.0 a 3.5) e força da nitidez
>   · rótulos "suave" e "bem forte"
>
> - MELHORAR → slider "Clareza do fundo", 0 a 100, padrão 50
>   · quanto empurra o fundo em direção ao branco
>
> Cada slider só aparece quando o filtro correspondente está
> selecionado. O valor é por página, e vale também para "todas" e
> "só nas próximas".
>
> 2.3 Prévia ao vivo
> Ao arrastar o slider a prévia atualiza em tempo real. Para não
> travar: processar em resolução baixa durante o arrasto e refazer
> em resolução normal ao soltar. Debounce de ~150ms.
>
> ════════════════════════════════════════════════
> 3. ACENTOS (já pedi duas vezes e continua errado)
> ════════════════════════════════════════════════
> A interface ainda mostra: "Impressao", "pagina", "Magico",
> "so nesta", "proximas", "Forca", "Espaco", "duvida", "nao",
> "laranjas eu nao tive certeza".
>
> Corrija TODOS os textos da interface para português correto:
> Impressão, página, Mágico, só nesta, próximas, Força, Espaço,
> dúvida, não.
>
> Verifique se os arquivos .py estão salvos em UTF-8 e se as
> strings estão sendo lidas corretamente pelo Qt. Passe por todos
> os arquivos de ui/ conferindo cada texto.
>
> ════════════════════════════════════════════════
> Faça na ordem 3 → 2 → 1 (do mais simples ao mais complexo) e me
> mostre funcionando ao final.

## Pedido 10 — 18/07/2026 19:02

> a parta com o arquivo .exe sumiu

## Pedido 11 — 18/07/2026 19:28

> Coloquei vários PDFs de teste reais na pasta pdfs_teste/ do
> projeto. Use TODOS eles na bateria de testes, em vez dos PDFs
> sintéticos.
>
> Para cada arquivo, me diga:
> - qual o tipo (folhas duplas ou simples, colorido ou P&B,
>   qualidade do scan)
> - o que o programa detectou e se acertou
> - onde ele errou
>
> E me traga as imagens comparativas dos quatro filtros de cada
> um, escolhendo as páginas mais difíceis de cada arquivo — as
> mais amareladas, as mais tortas, as com texto do verso
> transparecendo.
>
> Importante: adicione pdfs_teste/ ao .gitignore, para os
> arquivos não irem para o repositório.

## Pedido 12 — 18/07/2026 19:55

> você continua não fazendo o .exe, cade?

## Pedido 13 — 18/07/2026 20:02

> INSTALA NO MEU COMPUTADOR E COLOCA NA MINHA AREA DE TRABALHO

## Pedido 14 — 18/07/2026 20:24

*Documento longo (9.195 caracteres). Está inteiro no **Apêndice B — O prompt
de testes**, no fim deste arquivo.*

> # Prompt de testes — colar no Claude Code

## Pedido 15 — 29/07/2026 14:35

> vamos fazer mudanças no projeto do editor de impressão?

## Pedido 16 — 29/07/2026 14:46

> faça um resumo do programa para o claude que eu possa colar lá na conversa

## Pedido 17 — 29/07/2026 16:27

> consegue olhar essa pasta "C:\Users\fotog\Desktop\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros" ver o que eu escrevi nos blocos de notas e ver e comparar as fotos que estão lá, para ver quais problemas quero resolver, depois me de uma lista aqui do que você leu, para eu poder ver se fez certo.

## Pedido 18 — 01/08/2026 17:19

> eu fechei sem querer o trabalho que estavamos fazendo, pode recuperar, tambem tinha escrito algumas coisas no na barra recupera o trabalho estamos no editor de impressão

## Pedido 19 — 01/08/2026 17:24

> 2

## Pedido 20 — 01/08/2026 17:46

> ok e agora?

## Pedido 21 — 01/08/2026 18:05

> explique eu não entendi

## Pedido 22 — 01/08/2026 18:06

> eu quero que o papel saia branco, e o desenho também saia perfeito.

## Pedido 23 — 01/08/2026 18:22

> não entendi, o jeito que você escreve fica dificil para eu entender as informações, seja mais direto por favor

## Pedido 24 — 01/08/2026 18:26

> ok, continue os testes.

## Pedido 25 — 01/08/2026 18:31

> aqui não está aparecendo que você está trabalhando

## Pedido 26 — 01/08/2026 18:32

> não era para aparecer um contador enquanto você está trabalhando ?

## Pedido 27 — 01/08/2026 18:34

> você consegue me mandar notificação pop up quando tiver alguma coisa nova? ou quando precisar de alguma informação? aplique isso para os três projetos que estão rodando no claude code.

## Pedido 28 — 01/08/2026 18:51

> quando terminar vai fazer o pop up?

## Pedido 29 — 01/08/2026 18:53

> aparece nas notificações mas não pula na minha tela

## Pedido 30 — 01/08/2026 18:59

> quando eu clicar na janelinha eu quero ir direto para o terminal que está enviando a notificação, e quero que seja notificado só quando tiver responder alguma coisa e não enquanto está trabalhando codificando

## Pedido 31 — 01/08/2026 19:03

> ok

## Pedido 32 — 01/08/2026 19:04

> eu quero pode ver algum tipo de carregamento aqui no terminal enquanto você trabalha

## Pedido 33 — 01/08/2026 19:08

> vou olhar as imagens

## Pedido 34 — 02/08/2026 11:39

> pode continuar fazendo outras coisas enquanto eu não vejo os ultimos testes?

## Pedido 35 — 02/08/2026 11:48

> vai concertar os filtros e depois a gente volta para parte de seleção.

## Pedido 36 — 03/08/2026 21:35

> por favor, confira os teste que você fez sozinho, não vou ter como fazer isso.[

## Pedido 37 — 03/08/2026 21:57

> deixa eu ver os testes que você fez

## Pedido 38 — 04/08/2026 03:05

> recuperar

## Pedido 39 — 04/08/2026 03:07

> pq estava pedindo para resumir a sessão?

## Pedido 40 — 04/08/2026 03:09

> o que tem para fazer agora no programa?

## Pedido 41 — 04/08/2026 03:11

> pq o melhoramento dos filtros não está nesta lista?

## Pedido 42 — 04/08/2026 12:35

> opa e agora, o que está fazendo?

## Pedido 43 — 04/08/2026 13:12

> manda print dos testes para eu ver

## Pedido 44 — 04/08/2026 13:39

> ok, o que falta ainda fazer, acho que estamos quase chegando no perfeito na seleção.

## Pedido 45 — 04/08/2026 17:22

> vamos continuar o trabalho do editor de impressão

## Pedido 46 — 04/08/2026 18:22

> porque você continua travando , porque não vai até o final?

## Pedido 47 — 04/08/2026 18:44

> me da um resumo de tudo que tu fez agora em arquivo md, as perguntas que me fez os prints que eu te mandei, os pedidos que eu te fiz em toda a conversa, as questões que tu perguntou para mim e o que falta para o programa estar pronto de acordo com o que eu quero e como ele deve funcionar

## Pedido 48 — 04/08/2026 19:10

> você esqueceu de colocar os meus pedidos que eu fiz ao longo da conversa no relatorio só me da um relatorio em md para eu mandar para o claude

## Pedido 49 — 05/08/2026 14:53

> o que falta agora? porque você parou?

## Pedido 50 — 05/08/2026 16:26

> ok, o que falta fazer ainda de tudo que eu já pedi e apontei?

## Pedido 51 — 05/08/2026 16:42

> muita coisa para eu ler, seja mais consigo por favor, fale em quatro linhas o que eu preciso escolher

## Pedido 52 — 05/08/2026 16:44

> continue 1 e depois 2 e termine tudo, só me chame quando terminar tudo

## Pedido 53 — 06/08/2026 13:04

> pera ai, faz um resumo pra mim

## Pedido 54 — 06/08/2026 13:06

> o que falta fazer?

## Pedido 55 — 06/08/2026 13:17

> a ferramenta de seleção está finalizada também?

## Pedido 56 — 06/08/2026 13:23

> ok, vamos continuar os testes do selecionador, além disso pesquise sobre como treinar selecionadores como programar esse tipo de coisas, procure também respositorios no reddit e como grandes apps como photoshop e adobe pdf fazem isso para nos ajudar a testar nosso programa e deixar ele zero, só pare quando estiver 99% de certeza e dai quando chegar nesse numero deixe amostras do seu trabalho lá na pasta de testes. depois disso continue a aplicar esse selecionador em conjunto com nossos filtros para que com o selecionador possamos aplicar filtro só em uma parte selecionada, ou melhorar o trabalho de um filtro, entendeu?

## Pedido 57 — 06/08/2026 14:07

> consegue ativar o modo voz

## Pedido 58 — 06/08/2026 14:08

> É explica para mim poucas palavras O que falta fazer no Programa

## Pedido 59 — 06/08/2026 14:09

> Tambão conserta todas essas coisas e só volta aqui a me chamar quando terminar tudo isso

## Pedido 60 — 06/08/2026 17:38

> não entendi do que você está falando, seja mais simples

## Pedido 61 — 06/08/2026 17:40

> eu quero ter opção de transformar uma capa em branco. 2 - pode continuar mexendo no programa, precisa treinar o programa poder selecionar cores né? e tambem letras antigas tambem.

## Pedido 62 — 06/08/2026 17:47

> eu quero que ele reconheça cores mesmo, para eu ter uma ferramenta a mais de seleção para eu poder selecionar por cor quando o programa dar errado.

## Pedido 63 — 06/08/2026 20:13

> sim, pode continuar

## Pedido 64 — 06/08/2026 23:09

> resolva

## Pedido 65 — 08/08/2026 02:32

> me faz um resumo de tudo que tu fez, tudo que já pedi coloca tudo em documento texto para eu mandar no claude, o prompt inicial tudo bem explicado e o que falta fazer.

## Pedido 66 — 08/08/2026 02:37

> você anexou todos os meus pedidos durante a conversa nesse relatorio?

## Pedido 67 — 08/08/2026 02:40

> não, eu fiz varios outros pedidos sobre o programa sobre funcionalidades, apotamentos sobre os testes que você fez, leia a conversa inteira antiga para lembrar

## Pedido 68 — 08/08/2026 02:46

> ta faz um novo relatorio e agora, coloca todos os meus pedidos dentro dele por favor, durante a conversa, junto com o relatorio da conversa completa

## Pedidos desta sessão (07/09/2026), fora da numeração acima

Continuação depois do relatório de 08/08 — ainda não numerada junto aos 68
porque veio numa conversa separada, sobre organização e planejamento, não
sobre o código:

- Retomada do projeto via o fluxo `/projeto`, escolhendo o Editor de Impressão.
- "quero saber todas as funcionalidades que eu já pedi para ter nesse app."
- "você leu as conversas passadas e o claude.md para saber disso, verificou
  nossas conversas passadas?" — cobrança para verificar direto na fonte, não
  confiar em resumo já pronto.
- "quero que verifique diretamente."
- "Seleção de letras e gravuras está aí?" — pediu confirmação direto no
  código, não só no handoff.
- "ok, então me da o handoff completo com todas as funcionalidades e coisas
  que o aplicativo vai fazer." — motivou a criação da PARTE 1B deste
  documento.
- "mas o editor de impressão não está mais no dico local c, agora ele está no
  disco local d" — motivou a investigação que achou o C: como cópia ativa e o
  D: como backup desatualizado.
- "que é um hd externo" — pergunta de esclarecimento, respondida à parte.
- "então vamos mudar tudo para o disco local D" — motivou a migração:
  C:\Users\fotog\Desktop\EditorImpressao → D:\programas\EditorImpressao,
  registro atualizado, C: virou o backup.
- "Ta bom, agora cria um handolf bem completo com tudo, com o maximo de
  informação possivel, até as mensagens e pedidos que eu fiz, para eu ir para
  a conversa com claude e tentar melhorar o planejamento desse aplicativo." —
  gerou esta própria versão do documento.
- "eu acho que poderia arquivar tudo em uma pasta unica no disco local D,
  tirar o que for do editor de impressão da area de trabalho." — pedido de
  consolidação das pastas soltas na área de trabalho (acervo de testes,
  instaladores, relatórios antigos) para dentro do D:, ainda em andamento.

## Os pedidos que valem como regra permanente

Estes seis não são tarefa: são o modo de trabalhar. **Quem pegar este projeto
deve ler esta lista primeiro.**

- **"seja mais direto"** e **"seja mais conciso — em quatro linhas"** — texto
  curto no chat. O detalhe vai para arquivo, não para a conversa.
- **"não entendi do que você está falando, seja mais simples"** — e não é o
  mesmo que ser curto. É falar em português comum: "o programa estava estragando
  a capa dos livros", e não "o balanço de branco eleva o ruído de 5,5 para 17,5".
  O número entra depois da frase que se entende, nunca no lugar dela.
- **"confira os testes que você fez sozinho, não vou ter como fazer isso"** —
  abrir todas as imagens antes de dizer que funcionou. Percentual não é veredito.
- **"porque não vai até o final?"** — decidir sozinho dentro da alçada e
  executar o protocolo inteiro, em vez de parar a cada passo perguntando por
  onde seguir.
- **"vai consertar os filtros e depois a gente volta para a seleção"** — a ordem
  de trabalho combinada.
- **"eu quero que o papel saia branco, e o desenho também saia perfeito"** — o
  critério final, em uma frase.

---

# PARTE 3 — As dez queixas do Kaique, e onde está cada uma

| Queixa, nas palavras dele | Situação |
|---|---|
| "as letras estão ficando pixeladas, precisamos que fiquem mais arredondadas" | **Feito e conferido na imagem** |
| "o mágico pro está deixando muito pixelado a imagem" | **Feito e conferido** |
| "às vezes a parte de trás fica com uma mancha da parte da frente" | **Feito e conferido** |
| "o programa não localizou as bordas corretamente" | **Feito e conferido em dois casos** |
| "o livro já foi recortado ao meio, sobra dos lados uma parte branca" | **Feito** — trocado o limiar global por Sauvola local |
| "colocar botão clicável nas páginas que o programa não tem certeza" | **Existe** |
| "a barra de scroll devia ser preta" | **Feito em 06/08** |
| "como ter certeza que os cadernos estão na sequência correta sem olhar folha por folha?" | **Feito em 06/08** — o programa simula a dobra e confere |
| "no mágico pro o fundo deveria remover o amarelado e deixar totalmente branco" | **Em grande parte feito**; ver o que falta |
| "queremos que fique branco a página e só as letras pretas" (Preto e branco) | **Atendido em número**, mas falta escolher o binarizador por página |

---

# PARTE 4 — O que foi feito nesta rodada (04 a 07/08/2026)

São 12 commits. O placar: **a régua dos filtros saiu de 27 motivos de
reprovação para 4**, e a seleção ganhou régua própria e está em 23 de 26.

## Os filtros

**A causa do fundo que escurece, achada e medida.** Sete das oito reprovações
vinham de um passo só: o realce de cor do Mágico pro multiplica o S do HSV
mantendo o V — isso preserva o brilho, mas não a luminância, e papel velho é
sempre amarelo-pardo. Três saídas foram implementadas e medidas no acervo
inteiro (cor em LAB, cor em YCrCb, devolver o cinza pixel a pixel) e **as três
foram revertidas**: todas consertavam o papel e engrossavam a rubricação
vermelha, que é entupimento de letra — o defeito mais grave que existe aqui.
O que resolveu foi não realçar quando a única cor da folha é o amarelado do
próprio papel: papel velho é sempre âmbar, uma capa colorida pode ser de
qualquer matiz.

**A capa não é papel.** Depois que o detector passou a marcar capa como gravura,
as capas caíram no caminho de branqueamento — e numa capa não há papel a
branquear, o que ali parece papel é o couro. Três passos tiveram de sair, e cada
um custou uma medição própria:

| Passo retirado | Medido |
|---|---|
| branqueamento e ponto de preto | ruído do Boécio 5,5 → 17,5 |
| achatamento da iluminação | couro verde do Horas 219 → 194 |
| recomposição da rampa | couro vermelho do Graduale 47,4 → 43,9 |

## A régua

**A rampa da borda passou a ser rampa de verdade.** Ela contava pixels de tom
intermediário perto do contorno, e o grão do papel entrava na conta: limpar o
papel — que é o certo — aparecia como estragar a letra. Agora é contraste
dividido pela inclinação, medida em cima do contorno, e sai em pixels. Validada
contra casos extremos: imagem binarizada dá exatamente 1,00, desfocada com sigma
4 dá 3,19.

**A régua parou de medir letra onde não há letra.** Uma estampa colorida de
página inteira era reprovada por "as letras entupiram" — numa página sem uma
letra. As páginas em que a régua afrouxa saem **nomeadas** no relatório, de
propósito.

**Um erro meu, achado abrindo as imagens.** A primeira versão dessa regra
desligava a cobrança em 30 das 63 páginas medidas, incluindo uma partitura
manuscrita cheia de texto. Apertei a regra e caiu para 13, e abri as treze.

## A seleção

**Ganhou régua própria** (`avaliar_selecao.py`), com 26 páginas e uma expectativa
escrita olhando cada uma.

**O defeito que ela achou de cara: o Preto e branco apagava a capa dos livros.**
Página sem marcação nenhuma é binarizada inteira — a capa de pergaminho do
Boécio saía uma folha branca, sobrando só a etiqueta da biblioteca. A regra
antiga do projeto mandava o contrário do que devia. Capa e folha em branco pedem
coisas opostas, e isso foi medido: sem marcação a capa some e a folha em branco
vai a branco; marcada como gravura a capa sai inteira e a folha para no creme.
O detector passou a perguntar se aquilo é **objeto ou folha** — objeto tem
textura, ou está sobre fundo mais escuro.

## Ferramentas novas

**"Pegar tudo desta cor"** — a sétima ferramenta da aba Marcar. Clica numa cor e
ela pega **tudo daquela cor na página**, não só a mancha onde clicou. A varinha
antiga é preenchimento por semente: na partitura do Graduale ela vaza pelo
pergaminho e leva 99,8% da folha. A nova pega 7,7% — as vinte pautas vermelhas e
as letras rubricadas. Compara só o **matiz**, então a parte iluminada e a parte
na sombra da mesma tinta contam como a mesma cor.

**"Filtro só neste pedaço"** — a folha inteira vai a Preto e branco e a gravura
fica no Original. Testado na xilogravura da Rhetorica: o texto sai com 2 tons e a
gravura mantém os 256 da hachura.

**Marcar a folha inteira como papel = folha em branco.** Serve para a capa que
não se quer no livro reimpresso. Sai com zero pixels que não sejam brancos.

**A tela de conferir** (`conferir.py`) — mostra as amostras uma a uma, com uma
caixa para dizer o que está errado. A caixa aceita o **ditado do Windows: Win+H
e falar**. Nenhuma biblioteca nova entrou por causa disso.

## Fora da imagem

**A barra de rolagem ficou preta**, a pedido do Kaique.

**A sequência dos cadernos passou a ser conferida**, e não só instruída: o
programa simula a dobra e verifica que a leitura sai 1, 2, 3 até o fim, que as
folhas saem em pares de frente e verso, e que nenhuma página sumiu ou repetiu. O
resultado aparece na tela final, em verde ou em vermelho com "não imprima assim".

**Um travamento sério consertado:** o gerador de relatório entrava em laço
infinito com tabela grande e deixava um PDF de zero byte. O `Story` do PyMuPDF
devolve "ainda tem mais" sem consumir nada quando um elemento não cabe. Isso
podia travar o programa na mão do Kaique, sem mensagem e sem fim.

**O aviso "tem cor" parou de ser decidido na navalha.** O limiar de 5% caía
dentro da faixa das páginas coloridas: a estampa do Catecismo dá 0,0499 a 150
DPI e 0,0500 a 300. Passou para 2%, no meio do vão medido.

---

# PARTE 5 — O que falta

## 1. A régua dos filtros: 4 motivos

- **Três são a mesma página** — a 126 do Graduale, uma partitura manuscrita que
  o detector marca como desenho. O ruído sobe porque ela é tratada como gravura.
  **Conserta-se consertando a detecção.**
- **Um é o Pesel 76** — o fundo escurece de 156 para 148 no Mágico pro.

## 2. A régua da seleção: 3 de 26

As três têm a mesma raiz: o modelo de layout foi treinado em documento moderno.

- **Graduale 126** — partitura manuscrita marcada 100% gravura.
- **Siebmacher 45** — as legendas impressas da prancha não viram letra.
- **Pesel 73** — o título impresso sai como foto; as quatro legendas do pé, não.

**Cinco sinais foram medidos para separar escrita antiga de foto** — pedaços de
glifo, papel à vista, meio-tom, periodicidade do perfil de linhas e uniformidade
da parte clara — e **em todos os cinco os números das duas se cruzam**. Está
tudo em `relatorios/melhorias.md`, para ninguém repetir.

Como não dá para decidir pela imagem, o programa agora **admite a dúvida**: a
página fica laranja com "Desenho ou escrita? Não tenho certeza. Confira na aba
Marcar". Acende em 2 de 7 páginas testadas — as duas genuinamente difíceis.

**O conserto de verdade é somar um modelo treinado em documento histórico.** A
pesquisa apontou três abertos que fazem exatamente isso: **Eynollah**,
**dhSegment** e **Kraken/eScriptorium**. E existe dataset anotado pixel a pixel
para validar: o **DIVA-HisDB**, 150 páginas de manuscritos medievais da
competição ICDAR 2017.

## 3. A rubricação vermelha virando preta

No Preto e branco, a rubricação vermelha do Graduale e do Livro de Horas vira
barra preta. A causa suspeita já está escrita: a conversão para cinza trata
vermelho como escuro, e o DoxaPy oferece oito métodos de conversão a investigar.

## 4. Escolher o binarizador por página

Foram comparados os 18 binarizadores do DoxaPy em 36 páginas. A conclusão: **não
existe vencedor único**. No Palatino, de letra gótica pesada, o Otsu sai sólido
enquanto o Sauvola quebra o traço; noutras páginas se inverte. Hoje o programa
usa um só para tudo.

## 5. Falta um número na régua: "guardou a sujeira"

O Otsu marca zero pioras mas guarda o dobro de tinta do Sauvola — em papel
envelhecido isso quer dizer manter a mancha como se fosse letra, e **nenhum
critério atual pega isso**. Enquanto esse número não existir, a régua pode
aprovar o filtro errado.

## 6. A pergunta que ficou sem resposta desde 18/07

No prompt de testes você pediu, com todas as letras:

> "Ao final, me diga em uma frase: **o programa já substitui o CamScanner para o
> trabalho do Kaique? Sim, não, ou ainda não.**"

**Isso nunca foi respondido.** A pasta `para_comparar/` foi montada, com as dez
imagens — as cinco páginas difíceis antes e depois — mas a comparação lado a
lado com o CamScanner nunca foi feita nem o veredito dado.

É o teste que você chamou de decisivo, e é o único que mede o programa contra o
que o Kaique usa hoje. Devia vir antes de qualquer refinamento novo.

## 7. Dois critérios de aceitação que ainda não foram conferidos

Dos quinze da especificação original, estes dois nunca foram medidos:

- **"menos de 10% das páginas marcadas para revisão"** — hoje o acervo tem 349
  páginas com "ângulo suspeito" e 305 com "tem cor" em 2903 folhas. Só o
  primeiro já passa de 12%. O alerta corre o risco de virar ruído, que é
  exatamente o que a especificação mandava evitar.
- **"aplicar filtros diferentes em páginas diferentes, gerando um PDF só"** — o
  filtro é por página no modelo de dados, mas isso nunca foi conferido ponta a
  ponta num livro de verdade.

## 8. O caminho para treinar

Para reconhecer letra antiga o programa precisa de gabarito, e **a aba Marcar já
é a ferramenta que o produz**: cada página corrigida à mão é um exemplo do
certo. O caminho combinado:

1. Marcar à mão 30 ou 40 páginas difíceis, das que ele erra.
2. Guardar essas marcações como gabarito.
3. Com gabarito dá para **medir de verdade** — Interseção sobre União por
   classe, que é como a competição ICDAR avalia — em vez de julgar no olho.
4. E aí dá para treinar, ou validar um dos três modelos prontos.

O passo 1 é o único que o programa não faz sozinho.

---

# Estado hoje

- **150 testes** automatizados passam.
- **20 de 20 casos de robustez**: PDF corrompido, protegido por senha, arquivo
  que some no meio, disco cheio, livro de 1010 páginas, cancelar no meio. Em
  nenhum o programa fecha, e em nenhum se perde trabalho.
- **58 commits** (o mais recente, de 07/09/2026, adicionou a lista mestra de
  funcionalidades — PARTE 1B deste documento), cada um com o defeito que
  resolveu escrito por extenso.
- Memória sob controle: o pico não cresce com o tamanho do livro.
- **Mudança de local em 07/09/2026:** o projeto vive agora em
  `D:\programas\EditorImpressao`, com o GitHub ligado normalmente. A pasta
  antiga, `C:\Users\fotog\Desktop\EditorImpressao`, virou o backup.
- **Arrumação da área de trabalho, feita em 07/09/2026:** tudo que sobrava do
  projeto na área de trabalho foi arquivado em
  `D:\programas\EditorImpressao-arquivos\` — o acervo de testes
  `TESTES EDITOR DE IMPRESSAO`, a pasta duplicada `LIVROS PARA FAZER TESTE`
  (mantida, não apagada), `BIBLIOTECA DO FIM DOS TEMPOS`, `pasta do prompt`,
  os instaladores soltos e as cópias antigas destes documentos de handoff. Os
  caminhos fixos em `gerar_prints.py`, `relatorio.py`, `montar_para_conferir.py`
  e `teste_completo.py` foram atualizados, e `avaliar.py` ganhou o novo caminho
  na busca automática. A pasta `C:\Users\fotog\Desktop\EditorImpressao`
  (código antigo, agora só backup) **não foi mexida** nesta arrumação — segue
  onde estava.

---

# APÊNDICE A — A especificação original

Pedido 1, de 18/07/2026. É a lista de funcionalidades do programa, e vale reler inteira.

---

# Editor de Impressão — especificação completa e prompt para o Claude Code

Projeto do Pe. Rosenei — Instituto de preservação de livros.
Aplicativo de desktop para recuperar livros antigos escaneados e preparar para reimpressão.
Usuário final: **Kaique** (impressor, sem conhecimento técnico).

---

# PARTE 1 — Recapitulação das decisões

## Objetivo
Um **"CamScanner para PC"**: programa único de desktop que limpa o amarelado, endireita páginas tortas, divide folhas escaneadas com duas páginas e monta os cadernos prontos para impressão.

## Histórico do projeto (por que estamos refazendo)
1. Começou com um script Python de imposição de cadernos (`imposicao_cadernos.py`) — a matemática estava correta
2. Virou app de navegador (v1, v2) — só imposição
3. v3 no navegador — ganhou filtros e deskew, mas em JavaScript, lento
4. v4/v5 desktop com customtkinter — ganhou 4 filtros e 4 modos, mas **travava** e a **qualidade dos filtros ficou insatisfatória**

**Conclusão:** refazer do zero em Python/OpenCV, mantendo o que funcionava e resolvendo o que não funcionava.

## O que reaproveitar (já comprovado)
- A **matemática da imposição de cadernos** (arquivo `imposicao_cadernos.py`)
- O **processamento página a página** — resolveu o travamento com livros de 500+ páginas a 400 DPI
- A **cópia direta de páginas** no modo "só cadernos" (não rasteriza)

## O que trocar
- **customtkinter → PySide6**: o customtkinter foi a origem dos erros de abrir e dos travamentos
- **Filtros feitos à mão → DoxaPy + receitas OpenCV consagradas**

## Como os projetos do GitHub entram
| Projeto | Papel | Licença |
|---|---|---|
| **DoxaPy** (brandonmpetty/Doxa) | **Dependência real.** Sauvola/Wolf para o Preto e branco | CC0 (domínio público) |
| **scikit-image** | Plano B se DoxaPy não compilar no Windows | BSD |
| **hasanfirnas/PDF_Magic-Color_filter** | Receita de referência para o Mágico Pro | — |
| **ArashNasrEsfahani/Python-Document-Scanner-OpenCV** | Receita (vibração de cor + nitidez) | — |
| **ScanTailor Advanced / Experimental** | Referência de algoritmo apenas. **Não embutir** (C++/Qt, GPL) | GPL v3 |
| **OCRmyPDF** | Adiado para a v2 | — |

## Fora do escopo da v1
- OCR / texto pesquisável
- Escanear direto do scanner

---

# PARTE 2 — Prompt para colar no Claude Code

> Cole tudo daqui até o fim da Parte 2.

---

Quero construir um aplicativo de desktop em Python chamado **Editor de Impressão**. Ele recupera PDFs de livros antigos escaneados e prepara para reimpressão em cadernos. O usuário final é um impressor sem conhecimento técnico nenhum — a interface precisa ser à prova de erro, em português do Brasil, sem jargão.

Leia esta especificação inteira antes de escrever qualquer código.

---

## 1. Stack obrigatória

- **Python 3.11+**
- **PySide6** para a interface — NÃO usar tkinter nem customtkinter (foram a causa de travamentos na versão anterior)
- **PyMuPDF (fitz)** para ler e escrever PDF
- **OpenCV (cv2)** + **numpy** para processamento de imagem
- **DoxaPy** (`pip install doxapy`, licença CC0) para binarização adaptativa. Se não compilar no Windows, cair automaticamente para `skimage.filters.threshold_sauvola`
- **Pillow** para conversões auxiliares
- Empacotamento: **PyInstaller** → um `.exe` único, sem instalador, sem dependência externa

---

## 1.1 Projetos de referência (consulte antes de implementar os filtros)

Estes projetos já resolveram partes deste problema. **Estude-os antes de escrever os filtros** — não reinvente o que já está resolvido.

**Para usar de verdade (dependência):**
- **brandonmpetty/Doxa** → `pip install doxapy`. Licença **CC0 (domínio público)** — uso livre, sem restrição. Implementa Otsu, Niblack, **Sauvola**, **Wolf**, Gatos, NICK, ISauvola, Su. É a base do filtro Preto e branco.
- **scikit-image** (`skimage.filters.threshold_sauvola`, `threshold_niblack`) — licença BSD. Plano B se o DoxaPy não compilar no Windows.

**Para ler a receita e implementar a nossa versão (NÃO copiar código, apenas estudar a abordagem):**
- **hasanfirnas/PDF_Magic-Color_filter** — efeito Magic Color do CamScanner em OpenCV, trabalhando sobre PDF. É a referência mais direta para o filtro **Mágico pro**.
- **ArashNasrEsfahani/Python-Document-Scanner-OpenCV** — pipeline que reforça vibração de cor e nitidez para deixar documento limpo e legível, replicando o CamScanner.
- **satvik007/Scanner_OP** — receita clássica de "magic color"; código de protótipo, útil para entender a matemática.
- **andrewdcampbell/OpenCV-Document-Scanner** — detecção automática de bordas/cantos e realce; boa referência para o deskew e para uma futura função de corrigir foto tirada torta.

**Referência de algoritmo, NÃO embutir no projeto:**
- **ScanTailor Advanced** e **ScanTailor Experimental** (forks vivos do ScanTailor) — é o padrão-ouro de limpeza de livro escaneado, usado por bibliotecas. Usa **binarização local Sauvola e Wolf** para papel amarelado e filtros específicos para remover **bleed-through** (texto do verso transparecendo). **Atenção:** é C++/Qt sob licença **GPL v3** — não dá para fundir com este projeto Python, e a licença é incompatível. Serve apenas como confirmação de que Sauvola/Wolf são o caminho certo. O ScanTailor original (repositório `scantailor/scantailor`) está arquivado desde 2020 — ignorar.

**Adiado para a v2, não implementar agora:**
- **OCRmyPDF** — camada de texto pesquisável. Já traz o **unpaper** embutido (limpeza de artefatos) quando usado com `--clean`.
- **NAPS2** — captura direto do scanner; tem linha de comando (CLI), útil se um dia quisermos integrar o escaneamento.

**Regra de licença:** só incorporar código de projetos com licença permissiva (CC0, MIT, BSD, Apache). Nada de GPL. Quando a referência for GPL ou de linguagem diferente, implementar a nossa própria versão a partir da descrição do algoritmo.

---

## 2. Arquitetura obrigatória

Separação total entre processamento e interface. O `core/` NÃO pode importar nada de `ui/` — quero poder rodar todo o processamento por linha de comando, sem abrir janela.

```
editor_impressao/
├── core/
│   ├── __init__.py
│   ├── pdf_io.py           # abrir/salvar PDF, página → imagem, imagem → página
│   ├── filtros.py          # os 3 filtros + original
│   ├── dividir.py          # detectar lombada, dividir folha
│   ├── endireitar.py       # deskew
│   ├── cadernos.py         # imposição
│   ├── analise.py          # detectar cor, confiança, sugestões
│   └── pipeline.py         # orquestra tudo, página por página
├── ui/
│   ├── __init__.py
│   ├── janela_principal.py # QMainWindow + QStackedWidget das 4 telas
│   ├── tela_inicio.py
│   ├── tela_opcoes.py
│   ├── tela_conferir.py
│   ├── tela_final.py
│   └── widgets/
│       ├── area_arrastar.py
│       ├── visualizador.py      # prévia com linha de corte arrastável
│       ├── tira_miniaturas.py
│       └── cartao_filtro.py
├── modelos.py              # dataclasses: Projeto, Pagina, Config, Acao
├── historico_acoes.py      # pilhas de desfazer/refazer + gravação em acoes.jsonl
├── historico.py            # projetos anteriores (JSON local)
├── recursos/               # ícones
└── main.py
```

---

## 3. REGRAS CRÍTICAS (não violar)

### 3.1 Memória
Livros têm 500+ páginas a 400 DPI. **Processar sempre uma página por vez**: ler → processar → escrever no PDF de saída → liberar da memória. **NUNCA** montar uma lista com todas as páginas processadas. Isso travou a versão anterior.

Limitar o DPI automaticamente: se `largura_px * altura_px > 40_000_000`, reduzir o DPI até caber.

### 3.2 Interface nunca congela
Todo processamento roda em `QThread` (ou `QThreadPool`), nunca na thread da interface. Sempre com barra de progresso e botão de cancelar funcional.

### 3.3 Nunca travar com erro
Qualquer exceção vira aviso amigável em português numa caixa de diálogo. O programa continua aberto. Registrar o erro técnico num arquivo de log, não na tela.

### 3.4 Nada de emoji no código da interface
A versão anterior quebrou no Windows por causa de emojis em labels. Usar ícones vetoriais ou texto puro.

---

## 4. Funcionalidades

Cada função é **independente, marcável por checkbox**. O usuário pode ligar uma, várias ou todas, em qualquer combinação. Nunca forçar combinação.

Ordem obrigatória do processamento (quando várias estão ligadas):
```
1. dividir folhas → 2. cortar bordas → 3. endireitar → 4. filtro → 5. montar cadernos
```
Páginas marcadas como **apagadas** são descartadas logo após a etapa 1.

### 4.1 Dividir folhas ao meio

Muitos escaneamentos trazem duas páginas do livro numa folha só (formato paisagem).

**Detecção automática:**
1. Verificar se a página é paisagem (`largura > altura * 1.2`)
2. Converter para escala de cinza
3. Somar a intensidade dos pixels por coluna → vetor de perfil vertical
4. Suavizar o perfil (filtro de média móvel)
5. Procurar o **mínimo de intensidade** (faixa mais escura = sombra da lombada) dentro da faixa central (entre 35% e 65% da largura)
6. Calcular a **confiança**: quão pronunciado é o vale em relação à média, e quão perto do centro está

**Confiança baixa quando:** o vale é raso, está longe do centro, ou a página não é paisagem. Marcar essas páginas para revisão.

**Controle manual obrigatório:**
- Arrastar a linha de corte com o mouse
- Botão "não dividir esta página" (capa, ilustração de página inteira)
- Botão "usar em todas" — aplica a posição relativa ajustada ao livro inteiro
- Botão "girar" (90° horário/anti-horário)

**Saída:** cada folha dividida vira duas páginas, na ordem esquerda → direita.

### 4.2 Limpar a folha — os três filtros

Todos precisam remover o fundo amarelado do papel envelhecido.

#### a) Preto e branco (Eco)
```python
# Usar DoxaPy com Sauvola ou Wolf
# Parâmetros de partida (deixar ajustáveis em constantes no topo do arquivo):
JANELA = 75          # tamanho da janela local (ímpar); ~1/20 da altura da página
K_SAUVOLA = 0.2      # sensibilidade
```
- Converter para escala de cinza
- Aplicar binarização adaptativa local (Sauvola ou Wolf via DoxaPy)
- Opcional: despeckle (remover componentes conectados com menos de ~8 px)
- Salvar como **1 bit** no PDF (arquivo fica minúsculo)

**Por que Sauvola/Wolf:** é o que o ScanTailor usa. Resolve amarelado E bleed-through (texto do verso transparecendo) de uma vez — que era o problema não resolvido nas versões anteriores.

#### b) Melhorar
Normalização de iluminação, preservando cor:
```python
# 1. Estimar o fundo: desfoque forte
fundo = cv2.GaussianBlur(img, (0,0), sigmaX=altura/20)
# 2. Dividir a imagem pelo fundo, por canal
normalizada = (img.astype(float) / (fundo.astype(float) + 1)) * 255
# 3. Cortar em 0-255 e normalizar contraste suavemente
```
- Fundo fica branco limpo, **cores originais preservadas**
- NÃO saturar nem realçar — apenas limpar
- Para documentos coloridos que precisam ficar fiéis

#### c) Mágico pro
Base do "Melhorar" + realce estilo magic color:
```python
# 1. Mesma normalização de iluminação do Melhorar
# 2. CLAHE no canal L (espaço LAB), clipLimit=2.0, tileGridSize=(8,8)
# 3. Saturação: converter para HSV, multiplicar canal S por 1.6
# 4. Nitidez (unsharp mask): img + 0.6 * (img - GaussianBlur(img))
# 5. Empurrar o branco: pixels acima de ~230 viram 255
```
- Resultado: cor viva, texto nítido, fundo branco
- Para capas e páginas ilustradas

#### d) Original
Não processa. Copia a página como está.

**Filtro por página (obrigatório):** igual ao CamScanner — o filtro vale **por página**, e páginas diferentes podem ter filtros diferentes dentro do mesmo livro, gerando **um PDF só** no final.

Casos reais que precisam funcionar:
- Livro inteiro em Preto e branco, **só a capa** em Mágico pro
- Miolo em Preto e branco, **as páginas com gravura** em Melhorar
- Uma página específica que ficou ruim no filtro geral, trocada só ela

Como o usuário aplica:
- **"só nesta página"** — muda apenas a página atual
- **"usar em todas"** — aplica ao livro inteiro
- **"só nas próximas"** — aplica desta página em diante (útil quando o livro muda de característica no meio, tipo um caderno de fotos)

O filtro escolhido fica salvo em `ConfigPagina.filtro` de cada página. O "filtro padrão" da tela 2 é apenas o valor inicial de todas — a partir daí cada página é independente.

### 4.3 Sistema de alertas — o programa avisa onde pode ter errado

Princípio central do aplicativo: **o programa faz tudo sozinho, mas é honesto sobre onde teve dificuldade.** O usuário não deve conferir 500 páginas uma a uma — deve conferir só as que o programa marcou. Isso é o que separa este app do ScanTailor (onde tudo é manual) e do CamScanner (que não avisa nada).

Em `core/analise.py`, cada página recebe uma lista de alertas. Casos a detectar:

| Alerta | Como detectar | Mensagem ao usuário |
|---|---|---|
| **Página colorida** | HSV: saturação média e % de pixels com S > 40 acima do limiar | "Esta página tem cor. Quer usar Mágico pro em vez de preto e branco?" |
| **Lombada incerta** | Vale de intensidade raso, ou longe do centro (fora de 40–60%) | "Não tenho certeza de onde cortar. Confira a linha." |
| **Não parece dupla** | Página em retrato num livro onde as outras são paisagem | "Esta folha parece ter uma página só. Confirme se devo dividir." |
| **Muito torta** | Ângulo de deskew detectado acima de 3° | "Esta página estava bem torta. Veja se ficou certa." |
| **Ângulo suspeito** | Detecção de ângulo com baixa confiança (variância pouco definida) | "Não consegui achar o alinhamento do texto direito." |
| **Página em branco** | Quase nenhum pixel escuro após binarizar | "Esta página parece estar em branco. Quer apagar?" |
| **Página escura demais** | Após o filtro, > 40% de pixels pretos | "Ficou muito escura. Tente 'mais fraco' na força do preto." |
| **Página apagada demais** | Após o filtro, < 1% de pixels pretos (texto sumiu) | "O texto quase sumiu. Tente 'mais escuro'." |
| **Corte pegou conteúdo** | O recorte automático de bordas encostou em pixels escuros | "O corte da borda pode ter pegado parte do texto." |
| **Resolução baixa** | Menos de ~150 DPI estimados | "Esta página foi escaneada em qualidade baixa. O resultado pode não ficar bom." |
| **Tamanho diferente** | Dimensões destoando das demais páginas do livro | "Esta folha tem tamanho diferente das outras." |

**Como mostrar:**

1. **Contador no topo da tela de conferir**, clicável:
   ```
   ⚠ 7 páginas para você olhar
   ```
   Clicar leva para a primeira delas. `Tab` pula para a próxima.

2. **Miniatura destacada em laranja** com "!" na tira inferior. Página sem alerta fica normal.

3. **Faixa explicativa** na página atual, em português simples, dizendo o motivo e **sugerindo a correção**:
   ```
   ⚠ Esta página tem cor — o preto e branco vai perder a ilustração.
     [ usar Mágico pro nesta ]   [ está bom assim ]
   ```
   O botão de sugestão aplica a correção com um clique.

4. **Painel "Páginas para revisar"** — lista todas as páginas com alerta, agrupadas por tipo:
   ```
   Páginas para revisar (7)
   ├ Têm cor (2) ................. págs. 1, 68
   ├ Lombada incerta (3) ......... folhas 12, 34, 51
   ├ Muito tortas (1) ............ pág. 89
   └ Parecem em branco (1) ....... pág. 136
   ```
   Clicar num item leva direto à página.

5. **Aviso antes de processar:** se ainda houver páginas não revisadas, perguntar:
   "Ainda tem 3 páginas que eu não tive certeza. Quer conferir antes ou processar assim mesmo?"
   Nunca bloquear — apenas avisar. O usuário pode processar sem revisar.

**Nunca alertar à toa:** página comum, só de texto, bem escaneada, não gera alerta nenhum. Se o programa marcar tudo, o alerta perde a função. Calibrar os limiares para que, num livro bem escaneado, menos de 10% das páginas sejam marcadas.

**REGRA IMPORTANTE — o botão de sugestão NÃO substitui o controle manual.**
O botão do alerta é apenas um atalho para a correção mais provável. **Todos** os controles manuais da seção 4.6 continuam disponíveis o tempo todo, com ou sem alerta:

| O alerta oferece | O usuário também pode, sempre |
|---|---|
| "usar Mágico pro nesta" | escolher qualquer um dos 4 filtros, inclusive um não sugerido |
| "aceitar o corte" | arrastar a linha de corte para onde quiser |
| "tente mais fraco" | usar o controle de força do preto livremente |
| "quer apagar?" | apagar ou manter, por decisão própria |
| "confira se ficou reta" | ajustar o ângulo na mão, arrastando |

E o contrário também vale: **páginas sem alerta nenhum podem ser ajustadas normalmente**. O usuário navega por qualquer página e muda o que quiser, mesmo que o programa tenha achado que estava tudo certo. O alerta chama atenção, nunca restringe.

### 4.4 Endireitar folhas tortas (deskew)
- Detectar o ângulo pelo **perfil de projeção**: rotacionar de -5° a +5° em passos de 0.1°, calcular a variância das somas por linha, escolher o ângulo de maior variância (texto alinhado = picos e vales bem marcados)
- Alternativa mais rápida: `cv2.minAreaRect` sobre os pixels de texto
- Rotacionar preenchendo com branco
- **Limitar a ±5°** — não mexer se o ângulo detectado for maior (provavelmente é erro de detecção)
- Se o ângulo for menor que 0.1°, não fazer nada (evita perda de qualidade à toa)

### 4.5 Montar cadernos para impressão (imposição)

- Reorganizar as páginas em cadernos (assinaturas) para imprimir frente e verso, dobrar ao meio e fechar
- Páginas por caderno configurável, **múltiplo de 4**, padrão **20**
- Completar com páginas em branco quando não fechar a conta
- Para um caderno de N páginas, a ordem de cada folha é:
  ```
  folha i (0-based), frente: [N - 2i]  [1 + 2i]
  folha i,           verso:  [2 + 2i]  [N - 1 - 2i]
  ```
- **Montar duas páginas por folha já no PDF de saída** (folha A4 paisagem com duas páginas lado a lado). O usuário só manda imprimir frente e verso — sem configurar nada no Acrobat
- Ao final, gerar instruções de impressão em português na tela final

**OTIMIZAÇÃO IMPORTANTE:** se **apenas** esta opção estiver marcada (sem filtro, sem dividir, sem endireitar), copiar as páginas direto com PyMuPDF **sem rasterizar** — preserva qualidade e texto vetorial, e é muito mais rápido.

### 4.6 Ajustes manuais (o automático propõe, o usuário corrige)

Filosofia: o programa faz tudo sozinho e mostra o resultado. Quando erra, o usuário corrige **sem precisar entender de técnica**. Nada de campos numéricos ou termos como "limiar" — sempre linguagem do dia a dia.

**a) Força do preto e branco**
- Controle de três posições na aba Filtro, visível apenas quando "Preto e branco" está selecionado:
  ```
  Força do preto:   [ mais fraco ]  [ normal ]  [ mais escuro ]
  ```
- Internamente ajusta o `k` do Sauvola: mais fraco ≈ 0.34, normal ≈ 0.2, mais escuro ≈ 0.1
- Resolve os dois casos comuns: texto que sumiu (papel muito claro) e página que ficou suja de manchas (papel muito escuro)
- Prévia atualiza na hora
- Vale por página, com os mesmos botões "usar em todas" / "só nas próximas"

**b) Cortar as bordas**
- Detectar automaticamente a área útil da página e recortar: borda preta do scanner, sombra que sobra da lombada, faixa escura da margem
- Método: binarizar, achar o retângulo que contém o conteúdo, deixar uma folga de ~2% e cortar
- Na prévia, mostrar um **retângulo com alças arrastáveis** — o usuário puxa se o corte pegou texto ou deixou sujeira
- Checkbox próprio na tela 2: "Cortar as bordas — tira a borda preta e a sombra do scanner"
- Botão "usar em todas" (é o caso mais comum: a borda é igual no livro inteiro)

**c) Apagar páginas**
- Na tira de miniaturas, botão para **excluir uma página do resultado**
- Casos reais: páginas em branco no fim do caderno, folha que saiu tremida, dedo do operador aparecendo no scan
- Páginas excluídas ficam acinzentadas na tira, com opção de restaurar
- O contador do topo atualiza ("136 páginas · 2 apagadas")
- **Importante:** se "Montar cadernos" estiver ligado, recalcular a imposição depois das exclusões

**d) Ajustar o ângulo na mão**
- Quando o endireitar automático errar, permitir girar a página **arrastando com o mouse** sobre a prévia
- Mostrar linhas-guia horizontais sobre a imagem para o usuário alinhar com o texto
- Indicador discreto do ângulo atual
- Botão "voltar ao automático"

**e) Desfazer / refazer — ilimitado e salvo em arquivo**

- **Ctrl+Z** desfaz, **Ctrl+Shift+Z** refaz (aceitar também Ctrl+Y como alternativa de refazer)
- **Sem limite de ações.** O usuário pode desfazer quantas vezes quiser, até o começo do projeto
- **O histórico é gravado em arquivo**, não só na memória. Se o programa for fechado no meio de um livro e reaberto depois, o histórico de ações continua disponível e ainda dá para desfazer

**Como implementar (padrão Command):**
NÃO guardar cópias do estado inteiro a cada mexida — com centenas de páginas isso fica pesado. Guardar apenas a **ação**, que ocupa pouquíssimo espaço e torna o desfazer ilimitado viável:

```python
@dataclass
class Acao:
    momento: str          # ISO datetime
    tipo: str             # mudar_filtro | mover_corte | girar | apagar |
                          # restaurar | ajustar_angulo | recortar |
                          # forca_preto | nao_dividir | aplicar_em_todas
    paginas: list[int]    # índices afetados (uma, várias ou todas)
    antes: dict           # valores anteriores dos campos alterados
    depois: dict          # valores novos
    descricao: str        # texto em português: "Filtro da página 42: P&B → Mágico pro"
```

- Manter duas pilhas: `desfeitas` e `refazer`
- Desfazer = aplicar o `antes`; refazer = aplicar o `depois`
- Nova ação depois de um desfazer **limpa** a pilha de refazer (comportamento padrão)
- Ações em lote ("usar em todas") são **uma única ação** com muitos índices — um Ctrl+Z desfaz o lote inteiro, não página por página

**Arquivo de projeto:**
Cada projeto ganha uma pasta própria em `<dados_do_usuario>/EditorImpressao/projetos/<nome>/` contendo:
```
projeto.json     # o Projeto e a lista de ConfigPagina (estado atual)
acoes.jsonl      # uma ação por linha (JSON Lines) — o histórico completo
thumbs/          # miniaturas em cache
```
- Usar **JSON Lines** (uma ação por linha): permite acrescentar ao fim do arquivo sem reescrever tudo, e é seguro se o programa fechar de repente
- Gravar a ação no arquivo assim que ela acontece (append), não só ao sair
- Ao reabrir o projeto, ler `projeto.json` para o estado e `acoes.jsonl` para o histórico
- Registrar também a posição atual na pilha, para o refazer sobreviver ao fechamento

**Na interface:**
- Botões ↶ ↷ no canto da tela de conferir, desabilitados quando não há o que desfazer/refazer
- Ao passar o mouse, mostrar a descrição da ação: "Desfazer: Filtro da página 42"
- Painel opcional "Histórico de ações" (lista com hora e descrição em português), com a possibilidade de clicar numa ação e voltar o projeto àquele ponto

**Fora de escopo (não implementar):** seleção de conteúdo e margens uniformes ao estilo ScanTailor. É a etapa mais trabalhosa daquele programa, dá pouco retorno para reimpressão e é onde os usuários desistem. Fica para uma versão futura, se fizer falta.

---

### 4.7 Atalhos de teclado

Para quem processa muitos livros, atalho economiza horas:

| Tecla | Ação |
|---|---|
| `←` `→` | página anterior / próxima |
| `Espaço` | marcar como "está certo" e ir para a próxima |
| `Tab` | pular para a próxima página marcada em laranja |
| `1` `2` `3` `4` | aplicar Original / P&B / Melhorar / Mágico pro |
| `R` | girar 90° |
| `Delete` | apagar a página |
| `Ctrl+Z` | desfazer |
| `Ctrl+Shift+Z` ou `Ctrl+Y` | refazer |
| `Ctrl+Enter` | confirmar e processar |

Mostrar uma legenda discreta dos atalhos no rodapé da tela de conferir.

---

## 5. Interface — layout de cada tela

Janela: mínimo 1000x680, redimensionável. Tema claro por padrão.

### TELA 1 — Início

```
┌──────────────────────────────────────────────────────────────┐
│  [icone] Editor de Impressão                      – ▢ ✕      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│      ┌────────────────────────────────────────────────┐      │
│      │                                                │      │
│      │              [ícone de arquivo]                │      │
│      │                                                │      │
│      │        Arraste o PDF do livro aqui             │      │
│      │         ou clique para procurar                │      │
│      │                                                │      │
│      └────────────────────────────────────────────────┘      │
│              (borda tracejada, aceita drag & drop)           │
│                                                              │
│   Projetos recentes                            [ver todos]   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [min] Gradus Primus            10/07/2026 · 136 págs   │  │
│  │       Preto e branco                  [abrir] [pasta]  │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [min] Missal Romano 1962       08/07/2026 · 232 págs   │  │
│  │       Mágico pro                      [abrir] [pasta]  │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [min] Catecismo de Trento      02/07/2026 · 180 págs   │  │
│  │       Melhorar                        [abrir] [pasta]  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

- Área de arrastar: borda tracejada, muda de cor ao arrastar por cima
- Cada linha do histórico: miniatura da primeira página, nome, data, nº de páginas, filtro usado
- "abrir" recarrega o projeto com as mesmas configurações; "pasta" abre a pasta do arquivo gerado
- Se não houver histórico, mostrar mensagem simpática no lugar da lista

### TELA 2 — O que fazer

```
┌──────────────────────────────────────────────────────────────┐
│  [icone] Editor de Impressão      Gradus Primus.pdf · 68 f.  │
├──────────────────────────────────────────────────────────────┤
│  Marque o que você quer fazer                                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [x]  [ic] Dividir folhas ao meio                       │  │
│  │           esta folha tem 2 páginas do livro            │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [x]  [ic] Limpar a folha                               │  │
│  │           tira o amarelado                             │  │
│  │                                                        │  │
│  │      ( ) Original  (o) Preto e branco                  │  │
│  │      ( ) Melhorar  ( ) Mágico pro                      │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [x]  [ic] Endireitar folhas tortas                     │  │
│  │           corrige páginas inclinadas                   │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [x]  [ic] Cortar as bordas                             │  │
│  │           tira a borda preta e a sombra do scanner     │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [ ]  [ic] Montar cadernos para impressão               │  │
│  │           páginas por caderno: [ 20 ▾]                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ (i) Vou dividir as 68 folhas em 136 páginas, endireitar│  │
│  │     as tortas e deixar tudo em preto e branco.         │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  [ voltar ]                        [   Conferir  →   ]       │
└──────────────────────────────────────────────────────────────┘
```

- Os filtros só aparecem quando "Limpar a folha" está marcada
- O campo de páginas por caderno só aparece quando "Montar cadernos" está marcada
- A caixa (i) é um resumo em português, **atualizado ao vivo** conforme as marcações
- Se nada estiver marcado, o botão fica desabilitado

### TELA 3 — Conferir (a prévia mora aqui)

Uma tela só, com abas internas. As abas aparecem conforme o marcado na tela 2.

```
┌──────────────────────────────────────────────────────────────┐
│  Conferir antes de processar        ⚠ 3 folhas para olhar    │
├──────────────────────────────────────────────────────────────┤
│  ┌ Onde cortar ┐ ┌ Filtro ┐                                  │
│  └─────────────┘ └────────┘                                  │
│                                                              │
│                      [ arraste ]                             │
│        ┌──────────────────┊───────────────────┐              │
│        │                  ┊                   │              │
│   ‹    │   página esq.    ┊   página dir.     │    ›         │
│        │                  ┊                   │              │
│        │                  ┊                   │              │
│        └──────────────────┊───────────────────┘              │
│                    (linha tracejada azul,                    │
│                     arrastável com o mouse)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ (i) Achei a lombada e vou cortar na linha azul.        │  │
│  │     Se estiver errado, arraste a linha.                │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  [✓ está certo] [✕ não dividir esta] [↻ girar] [⧉ usar em todas]│
│                                                              │
│  Folhas — as laranjas eu não tive certeza                    │
│  ┌──┐┌──┐┌██┐┌!!┐┌──┐┌──┐┌!!┐┌──┐┌──┐┌──┐┌──┐  ...          │
│  └──┘└──┘└██┘└!!┘└──┘└──┘└!!┘└──┘└──┘└──┘└──┘               │
│                                                              │
│  [ voltar ]                  [  Confirmar e processar  ]     │
└──────────────────────────────────────────────────────────────┘
```

**Aba "Filtro":**

```
┌──────────────────────────────────────────────────────────────┐
│  Conferir o filtro              ⚠ 2 páginas coloridas        │
├──────────────────────────────────────────────────────────────┤
│  ┌ Onde cortar ┐ ┌ Filtro ┐                                  │
│                 └────────┘                                   │
│      A mesma página nos quatro filtros — toque no que preferir│
│                                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐             │
│  │ [pág.]  │ │ [pág.]  │ │ [pág.]  │ │ [pág.]  │             │
│  │amarelada│ │  P&B    │ │ colorida│ │ vibrante│             │
│  ├─────────┤ ├─────────┤ ├─────────┤ ├─────────┤             │
│  │Original │ │ P&B ✓   │ │Melhorar │ │Mágico pro│            │
│  │sem mexer│ │tira amar│ │mantém cor│ │cor viva │             │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘             │
│                (selecionado com borda azul)                  │
│                                                              │
│  Força do preto:  [mais fraco] [ normal ▪] [mais escuro]     │
│         (só aparece com Preto e branco selecionado)          │
│                                                              │
│  [✓ só nesta] [⧉ usar em todas] [→ só nas próximas] [🔍 ampliar]│
│                                        [🗑 apagar página]     │
│                                                              │
│  Páginas — laranja: achei cor, confira                       │
│  ┌──┐┌──┐┌██┐┌!!┐┌──┐┌──┐┌──┐┌!!┐┌──┐┌──┐  ...              │
│  └──┘└──┘└██┘└!!┘└──┘└──┘└──┘└!!┘└──┘└──┘                   │
│                                                              │
│  ↶ ↷        ← → páginas · Espaço ok · Tab próxima dúvida     │
│  [ voltar ]                  [  Confirmar e processar  ]     │
└──────────────────────────────────────────────────────────────┘
```

**Comum às duas abas:**
- Setas ‹ › e teclas de seta do teclado navegam entre páginas
- Tira de miniaturas embaixo, clicável, com rolagem horizontal
- Páginas com **baixa confiança** destacadas em laranja com "!"
- Contador no topo: "3 folhas para você olhar" — permite pular direto para elas
- Os quatro cartões de filtro mostram a **página real processada**, não exemplos genéricos

**DESEMPENHO OBRIGATÓRIO:**
- Gerar prévia apenas das páginas visíveis, em resolução baixa (~150 DPI, máx. 900 px de altura)
- Pré-carregar as 3 próximas em segundo plano
- Cache em memória limitado (LRU, ~30 páginas)
- Miniaturas em resolução bem baixa (~80 px), geradas em lote em segundo plano
- A tela precisa abrir em poucos segundos mesmo com 500 páginas

### TELA 4 — Pronto

```
┌──────────────────────────────────────────────────────────────┐
│                        [ícone de check]                      │
│                                                              │
│                      Ficou pronto!                           │
│                                                              │
│         Gradus Primus — preto e branco.pdf                   │
│         136 páginas · 4,2 MB · 7 cadernos                    │
│         Salvo em: Documentos / Editor de Impressão           │
│                                                              │
│   ┌────────────────────────────────────────────────────┐     │
│   │ Como imprimir:                                     │     │
│   │ 1. Imprima frente e verso, virando na borda curta  │     │
│   │ 2. Separe as folhas em grupos de 5                 │     │
│   │ 3. Dobre cada grupo ao meio — cadernos prontos     │     │
│   └────────────────────────────────────────────────────┘     │
│                                                              │
│  [ abrir a pasta ]  [ imprimir agora ]  [ fazer outro ]      │
└──────────────────────────────────────────────────────────────┘
```

- O bloco "Como imprimir" só aparece se "Montar cadernos" foi usado
- Registrar o trabalho no histórico ao chegar nesta tela

### Tela de progresso (durante o processamento)

```
        Processando o livro...

        ████████████████░░░░░░░░░░░  62%

        Página 84 de 136 · faltam ~40 segundos

              [ cancelar ]
```

- Estimativa de tempo baseada na média das páginas já processadas
- Cancelar precisa funcionar de verdade e deixar o programa em estado limpo

---

## 6. Modelos de dados

```python
@dataclass
class ConfigPagina:
    indice: int
    dividir: bool = True
    posicao_corte: float = 0.5      # 0.0 a 1.0, relativo à largura
    confianca_corte: float = 0.0    # 0.0 a 1.0
    rotacao: int = 0                # 0, 90, 180, 270
    angulo_manual: float | None = None   # deskew ajustado na mão; None = automático
    recorte: tuple | None = None    # (x, y, w, h) relativo 0-1; None = automático
    filtro: str = "preto_e_branco"  # original | preto_e_branco | melhorar | magico_pro
    forca_preto: str = "normal"     # mais_fraco | normal | mais_escuro
    apagada: bool = False
    tem_cor: bool = False
    alertas: list[str] = field(default_factory=list)  # ver seção 4.3
    revisada: bool = False          # usuário já olhou e aprovou
    precisa_revisao: bool = False

@dataclass
class Projeto:
    caminho_entrada: str
    caminho_saida: str
    dividir_folhas: bool
    limpar: bool
    filtro_padrao: str
    endireitar: bool
    cortar_bordas: bool
    montar_cadernos: bool
    paginas_por_caderno: int = 20
    paginas: list[ConfigPagina] = field(default_factory=list)
```

**Histórico de ações:** ver seção 4.6(e). Guardar **ações** (padrão Command), não cópias de estado — isso permite desfazer ilimitado. Persistir em `acoes.jsonl` dentro da pasta do projeto.

**Histórico** (`historico.json` na pasta de dados do usuário):
```json
{
  "projetos": [
    {
      "nome": "Gradus Primus",
      "caminho_entrada": "C:/.../gradus.pdf",
      "caminho_saida": "C:/.../Gradus Primus - preto e branco.pdf",
      "data": "2026-07-10T14:32:00",
      "num_paginas": 136,
      "filtro": "preto_e_branco",
      "funcoes": ["dividir", "limpar", "endireitar"],
      "miniatura": "thumbs/gradus.png"
    }
  ]
}
```

---

## 7. Linguagem da interface

Português do Brasil, sem jargão técnico. Obrigatório:

| Nunca escrever | Escrever assim |
|---|---|
| imposição | montar para impressão |
| deskew | endireitar folhas tortas |
| DPI / resolução | qualidade: normal / alta |
| split / binarização | dividir folhas ao meio / preto e branco |
| threshold, kernel, pipeline | (nunca aparecem na interface) |

Mensagens de erro sempre gentis:
- ❌ "FileNotFoundError: [Errno 2]"
- ✅ "Não consegui abrir esse arquivo. Ele pode ter sido movido ou não ser um PDF."

---

## 8. Ordem de construção

Vá por etapas e **me mostre o resultado de cada uma antes de seguir para a próxima**.

**Etapa 1 —** Estrutura de pastas + `core/pdf_io.py`
Abrir PDF, extrair página como array numpy, escrever imagem de volta como página. Script de teste por linha de comando.

**Etapa 2 —** `core/filtros.py` com os três filtros
Antes de escrever, **releia a seção 1.1** e estude as abordagens dos projetos de referência.
**Testar em páginas reais e me mostrar as imagens antes de qualquer interface.** Esta é a parte mais importante do projeto — foi onde as versões anteriores falharam. Gere um comparativo lado a lado (original / P&B / melhorar / mágico pro) para eu avaliar.

**Etapa 3 —** `core/dividir.py` + `core/endireitar.py`
Testar a detecção de lombada num PDF real com folhas duplas e mostrar onde ele cortaria.

**Etapa 4 —** `core/cadernos.py`
Imposição. Reaproveitar a lógica do `imposicao_cadernos.py` que vou anexar.

**Etapa 5 —** `core/analise.py` + `core/pipeline.py`
Amarra tudo, página por página, com callback de progresso.

**Etapa 6 —** Interface PySide6, uma tela por vez, na ordem 1 → 2 → 3 → 4.

**Etapa 7 —** Histórico.

**Etapa 8 —** Empacotamento com PyInstaller e teste do `.exe` em máquina limpa.

---

## 9. Qualidade

- Escrever testes simples para o `core/` conforme for construindo (pytest)
- Usar `git` desde o primeiro commit, com um commit por etapa. A versão anterior virou uma bagunça de arquivos duplicados (`app__1_.html`, `app__2_.html`, cinco `.exe` idênticos) por não ter controle de versão
- Type hints no `core/`
- Comentários em português nas partes de algoritmo, explicando o *porquê*

---

## 10. Critérios de aceitação

O aplicativo está pronto quando:

1. Abre um PDF de 500+ páginas sem travar e sem estourar memória
2. Detecta e divide corretamente folhas com duas páginas, permitindo correção manual
3. O filtro Preto e branco remove o amarelado **e** o texto do verso transparecendo
4. O filtro Mágico pro deixa capas coloridas vivas e nítidas, com fundo branco
5. É possível usar cada função isoladamente ou em qualquer combinação
6. É possível aplicar filtros diferentes em páginas diferentes do mesmo livro, gerando um PDF só
7. O programa avisa onde teve dificuldade (cor, lombada, torta, branca, escura demais) e sugere a correção com um clique
8. Num livro bem escaneado, menos de 10% das páginas são marcadas para revisão — o alerta não vira ruído
9. A tela de conferir abre em poucos segundos mesmo com livros grandes
10. O PDF de cadernos imprime corretamente em frente e verso, sem configurar nada no Acrobat
11. O histórico guarda e reabre projetos anteriores
12. Todo ajuste automático pode ser corrigido na mão: linha de corte, ângulo, recorte, filtro, força do preto
13. Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz
14. Fechar e reabrir o programa preserva o projeto **e o histórico de ações** — ainda é possível desfazer
15. Roda como `.exe` único numa máquina sem Python instalado

---

**Comece pela Etapa 1 e me mostre o resultado antes de continuar.**

---

# PARTE 3 — Material de apoio

Anexar ao Claude Code junto com o prompt:

1. **`imposicao_cadernos.py`** — a lógica de imposição que já funcionava
2. **PDF do Gradus Primus** (Paulo Rónai, Cultrix) — arquivo de teste ideal:
   - 68 folhas, todas em paisagem com duas páginas do livro por folha
   - sombra de lombada bem visível no meio
   - capa colorida azul, miolo em preto e branco
   - papel envelhecido, levemente amarelado
   - cobre os casos de dividir + filtro por página + detecção de corC:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf

---

# APÊNDICE B — O prompt de testes

Pedido 14, de 18/07/2026. Define os quatro casos que são o critério de sucesso do Kaique, e o teste decisivo contra o CamScanner.

---

# Prompt de testes — colar no Claude Code

---

## ⚠ IMPORTANTE — LEIA ANTES DE COMEÇAR

Isto é uma bateria de **TESTES no aplicativo que VOCÊ JÁ CONSTRUIU**, que está em `C:\Users\fotog\Desktop\EditorImpressao`.

- **NÃO** recomece o projeto do zero
- **NÃO** reescreva módulos que já funcionam
- **NÃO** mude a arquitetura

O que eu quero é:
1. **RODAR** o programa existente com esses livros
2. **MEDIR e RELATAR** o que acontece
3. **CORRIGIR** apenas os problemas específicos que os testes revelarem, com a menor alteração possível

Antes de mexer em qualquer arquivo, me diga **o que pretende alterar e por quê**. Ajuste de parâmetro (janela e `k` do Sauvola, limiares de detecção de cor, ângulo de deskew) é bem-vindo. Reescrita de módulo, só se eu autorizar.

**Faça commit no git antes de começar os testes**, para dar para voltar atrás se algo quebrar.

---

## ONDE ESTÃO OS ARQUIVOS

Os PDFs de teste estão em:

```
C:\Users\fotog\Desktop\LIVROS PARA FAZER TESTE
```

Use essa pasta em todos os testes (ignore qualquer menção anterior a `pdfs_teste/`).

**Atenção:** o nome da pasta tem espaços — use aspas nos caminhos para não dar erro.

**NÃO modifique nem sobrescreva os PDFs originais.** São digitalizações de manuscritos e impressos históricos, arquivos do acervo do instituto. Trabalhe sempre gerando cópias em outra pasta.

Salve os relatórios `.txt` e as imagens **dentro dessa mesma pasta**, ao lado dos PDFs, para eu conferir tudo junto.

---

## PARTE 1 — O QUE O USUÁRIO FINAL PRECISA (critério de sucesso)

O Kaique é o impressor que vai usar este programa. Ele descreveu com as próprias palavras os problemas reais que enfrenta. **Isto é o critério de sucesso** — se o programa resolver estes quatro casos, está pronto; se não, não serve.

### Caso 1 — Folha amarelada com texto preto
Palavras dele: *"remover o amarelo e deixar as letras"*
→ filtro **Preto e branco**

### Caso 2 — Livro antigo amarelado COM imagens coloridas
Palavras dele: *"tem que preservar... ele vai remover o fundo amarelo e vai deixar as partes coloridas, as pinturas, e ele dá até uma melhorada nas cores"*
→ filtros **Melhorar** e **Mágico pro**
→ Note que ele espera **remover o amarelo E preservar a cor ao mesmo tempo** — não é "ou um ou outro"

### Caso 3 — Páginas tortas
→ **endireitar (deskew)**

### Caso 4 — O MAIS DIFÍCIL: bleed-through
Palavras dele: *"a folha é tão antiga que ela já está quase transparente, então as letras da parte de trás acabam aparecendo. Esses filtros no scanner, ele remove."*

→ O papel envelheceu tanto que ficou translúcido e o texto do verso aparece por trás.
→ **O CamScanner que ele usa hoje JÁ RESOLVE isso.** Nosso programa precisa resolver pelo menos tão bem.
→ É exatamente para isso que está o **DoxaPy com Sauvola/Wolf** na especificação.
→ **Se este caso não for resolvido, o programa não substitui o CamScanner e o projeto falha.**

---

## PARTE 2 — FICHA ESCRITA DE CADA LIVRO

Para cada PDF da pasta, gere um arquivo `.txt` com o **mesmo nome do PDF**, salvo na mesma pasta.
Exemplo: `Graduale - Saeculum XIV.txt`

Escreva em português, de forma legível para quem **não é técnico**. Modelo:

```
ARQUIVO: Graduale - Saeculum XIV.pdf
Testado em: 18/07/2026 16:30

O QUE ESTE ARQUIVO É
- 320 páginas · 277 MB · ~400 DPI
- folhas duplas: sim / não
- colorido / cinza / preto e branco
- estado do papel: amarelado / manchado / translúcido

O QUE O PROGRAMA DETECTOU
- páginas com cor: 45  (págs. 1, 3, 7, ...)
- páginas tortas: 12   (maior ângulo: 4,2°)
- páginas em branco: 2
- lombada incerta: 5
- alertas disparados: [lista por tipo]
- os alertas faziam sentido? [sua avaliação honesta]

DESEMPENHO
- tempo total: 4 min 12 s
- tempo por página: 0,8 s
- PICO DE MEMÓRIA: 1,2 GB
- tamanho do arquivo final: 18 MB (redução de 93%)

RESULTADO DE CADA FUNÇÃO
- dividir folhas: acertou 315 de 320 — errou nas págs. X, Y
- endireitar: ok / problemas em...
- cortar bordas: ok / cortou texto na pág...
- filtro preto e branco: tirou o amarelo? tirou o bleed-through?
                         o texto ficou nítido ou empastelado?
- filtro melhorar: preservou as cores? removeu o amarelo?
- filtro mágico pro: melhorou ou exagerou?
- montar cadernos: 16 cadernos · numeração conferida: sim/não

OS 4 CASOS DO KAIQUE NESTE ARQUIVO
1. amarelado com texto preto: resolvido / parcial / não resolvido
2. amarelado com imagem colorida: resolvido / parcial / não
3. páginas tortas: resolvido / parcial / não
4. bleed-through: resolvido / parcial / NÃO RESOLVIDO
   (se não resolveu, explique o porquê e o que tentou)

PROBLEMAS ENCONTRADOS
- [lista honesta, sem suavizar]

IMAGENS GERADAS
- pasta: resultados/Graduale/
```

Gere também um **`RELATORIO_GERAL.txt`** na pasta, contendo:
- tabela comparando os 9 livros (páginas, tamanho, tempo, memória, acertos)
- ranking: o que o programa resolve bem, o que resolve mal, o que não resolve
- sua recomendação do que ajustar primeiro, em ordem de prioridade

---

## PARTE 3 — TESTES POR FUNÇÃO

Rode cada função **isoladamente**, para saber exatamente qual falha:

1. só dividir folhas
2. só endireitar
3. só cortar bordas
4. só filtro — os quatro, um de cada vez
5. só montar cadernos
6. tudo junto

Reporte o resultado de cada combinação por livro.

---

## PARTE 4 — ATENÇÃO ESPECIAL A ESTES ARQUIVOS

### Memória — os arquivos grandes
`Graduale` (277 MB), `Marial de sermoens` (209 MB), `Livro de Horas` (108 MB).

São o teste real da regra de memória. Meça o pico e **reporte com honestidade** — se estourar ou demorar demais, é exatamente o que preciso saber agora.

### Manuscritos iluminados
`Graduale - Saeculum XIV` e `Livro de Horas - Luís XIV` têm iluminuras: letras capitulares em ouro e vermelho, miniaturas coloridas.

- O filtro **Preto e branco destruiria** essas páginas
- A **detecção automática de cor precisa marcar** todas elas
- Verifique se está acertando e reporte a taxa de acerto
- Me mostre **uma iluminura ampliada** no Original, Melhorar e Mágico pro — quero ver se preserva o ouro e o vermelho sem exagerar na saturação

### Xilogravuras
`Rhetorica Christiana` e `Schön Neues Modell Buch` têm gravuras em preto e branco com traço muito fino.

- Teste se o filtro P&B **preserva o traço ou empastela**
- Ampliação obrigatória de pelo menos duas gravuras

### Bleed-through (o caso 4 do Kaique)
Procure em todos os livros páginas onde o texto do verso aparece por trás.

- Recorte um pedaço onde dê para ver o texto de trás
- Me mostre **o mesmo pedaço ampliado, antes e depois**
- Se ainda der para ler o texto do verso, o filtro **não está bom o suficiente**
- Ajuste janela e `k` do Sauvola até resolver, e me diga quais valores funcionaram melhor para cada tipo de papel

---

## PARTE 5 — TESTES DE ROBUSTEZ

Teste e relate cada um:

1. **cancelar** o processamento no meio — o programa fica em estado limpo?
2. **fechar e reabrir** — o projeto e o histórico de desfazer sobreviveram?
3. **processar o mesmo arquivo duas vezes** — o resultado é idêntico?
4. **PDF protegido por senha** — avisa em português ou trava?
5. **PDF corrompido** — avisa ou trava?
6. **PDF com páginas de tamanhos diferentes** misturados
7. **PDF de 1 página só**
8. **arquivo que não é PDF**, renomeado para `.pdf`
9. **pasta de destino sem permissão** de escrita
10. **espaço em disco insuficiente**

### Vazamento de memória
Processe **5 livros seguidos sem fechar o programa**. Meça a memória depois de cada um. Se só sobe e nunca baixa, tem vazamento — investigue e corrija.

### Integridade da contagem
Confirme que **N folhas duplas viram exatamente 2N páginas**. Confira que nenhuma página se perdeu nem duplicou. Erro aqui passa despercebido e estraga o livro inteiro na impressão.

### Imposição — simular a dobra
Para um caderno de 20 páginas, verifique **programaticamente** que ao dobrar as folhas a sequência sai 1, 2, 3... 20. Me mostre a conta.

### Interface
Abra o programa e: clique em todos os botões de todas as abas, use todos os atalhos de teclado, redimensione a janela em vários tamanhos, desfaça e refaça 20 vezes seguidas, amplie e feche várias vezes, troque de página rapidamente. Anote tudo que travou ou ficou estranho.

---

## PARTE 6 — COMPARAÇÃO COM O CAMSCANNER (teste decisivo)

O CamScanner é o que o Kaique usa hoje. É a régua real.

Prepare o material para eu fazer a comparação:

1. Escolha **5 páginas difíceis**, uma de cada tipo:
   - papel bem amarelado, só texto
   - com bleed-through visível
   - com iluminura colorida
   - com xilogravura de traço fino
   - bem torta
2. Exporte cada uma como **imagem em alta resolução, ANTES do processamento**, numa pasta `para_comparar/`
3. Gere também o **resultado do nosso programa** para cada uma, com o filtro mais adequado
4. Nomeie de forma clara: `01_amarelada_ORIGINAL.png`, `01_amarelada_NOSSO.png`, etc.

Assim eu processo as mesmas páginas no CamScanner e comparo lado a lado.

---

## COMO QUERO O RETORNO

- Seja **crítico e honesto**. Prefiro descobrir agora o que está ruim.
- Não suavize resultado ruim. Se o bleed-through não foi resolvido, diga com todas as letras.
