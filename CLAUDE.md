# CLAUDE.md — Editor de Impressão

Este arquivo fica na raiz do repositório. O Claude Code lê antes de qualquer coisa.

Escrito em 07/09/2026, ao retomar o projeto depois de um mês parado. Substitui
a versão anterior — a versão anterior media tudo por número e nunca chegava a
"aprovado pelo Samuel"; esta corrige isso (ver seção 4).

> **Leia primeiro, nesta ordem (desde 24/09/2026; o item 0 desde 26/10/2026):**
>
> 0. `docs/plano/DECISOES.md` — **o Livro de decisões do Samuel.** Antes de mexer em qualquer tela, botão ou etapa,
>    e antes de oferecer uma opção ao Samuel ou dizer que algo "não existe", procurar ali (regras na seção 11).
> 1. `docs/plano/ESTADO-ATUAL.md` — onde o projeto está, e o que vale quando
>    os documentos antigos se contradizem.
> 2. `docs/plano/PLANO-DEFINITIVO.md` — **o plano. Ele manda.** Fases, Lista de
>    bugs, Lista de espera e Registro de mudanças. Só o Samuel muda.
> 3. Este `CLAUDE.md` — as regras técnicas. **O que ele disser em contrário ao
>    plano, vale o plano.**
> 4. Consulta: `docs/plano/TESTE-SCANTAILOR-MISTO.md` e
>    `docs/plano/OCR-PESQUISA.md`.
>
> O `PEDIDOS.md` e o handoff em `historico/` viraram **histórico** em 24/09.
> Servem para consulta, não dizem mais o que fazer.

---

## 1. O que é este programa, e para quem

Aplicativo de desktop para Windows que recupera PDFs de livros antigos
escaneados e os prepara para reimpressão em cadernos. Um "CamScanner para PC".
Projeto do Instituto São Bento, do Pe. Rosenei, de preservação de livros
esgotados.

**Quem usa é o Kaique, impressor, sem formação técnica.** Ele nunca vê
"Sauvola", "k" ou "deskew" — vê "Força do preto", "Melhorar", "girar a folha".
Toda a interface é em português do Brasil, sem jargão.

**O fluxo:** arrasta o PDF → marca o que quer fazer → confere página a página →
escolhe onde salvar → processa.

**Quatro filtros:** Original · Preto e branco · Melhorar · Mágico pro.

**Duas versões anteriores fracassaram.** Uma travava (customtkinter), a outra
dava qualidade ruim (filtro de fórmula caseira). As regras da seção 3 vieram
daí. Nenhuma é preferência de estilo — cada uma é cicatriz.

**O critério final, em uma frase:**

> "Eu quero que o papel saia branco, e o desenho também saia perfeito."

---

## 2. Como trabalhar comigo (Samuel)

- **Não recomeçar do zero.** Não reescrever módulos inteiros, não reorganizar o
  que funciona. Testar não é permissão para reconstruir.
- **Uma mudança por vez** — um item do plano por vez, na fase atual. Eu aprovo
  pela página de antes/depois de cada item (regra 4 do plano), não pelo diff.
  Mexer em estrutura, em tela ou no que está na seção 6 ("precisa perguntar
  antes") continua exigindo perguntar antes.
- **Planejar antes de codar.** Perguntar antes de mexer em estrutura.
- **Ir até o fim dentro da alçada.** Decidir o que é da alçada e executar o
  protocolo inteiro, em vez de parar a cada passo. Se o contexto acabar, parar
  num commit com o programa rodando e dizer onde parou.
- **Português comum, sem jargão.** Primeiro a frase que se entende, depois o
  número. "O programa estava estragando a capa dos livros" — não "o balanço de
  branco eleva o ruído de 5,5 para 17,5". O número vem **depois** da frase,
  nunca no lugar dela.
- **Ser conciso.** O essencial no chat, o detalhe em arquivo.
- **Claro e direto (Samuel, 29/10/2026: "quando for falar comigo, seja mais direto como foi nessa mensagem,
  coloque isso nas regras, eu preciso de clareza e direto").** Poucas linhas; uma ideia por frase; os nomes que ele vê
  na tela; no máximo uma pergunta, de preferência "sim ou não" com a sugestão já feita. Nada de tabela, número de
  decisão ou nome de arquivo no meio da explicação (isso vai para o registro). Se ele disser "não entendi", encurtar,
  não explicar mais.
- **Ser honesto.** Se eu estiver enganado ou correndo um risco, me avisar. Não
  concordar só para agradar.
- **Não inventar detalhe** que eu não forneci.

### Todo relatório sai em três formatos

O Samuel **não abre `.md`** — o Acrobat recusa o arquivo. Relatório que a
pessoa não consegue abrir não é relatório.

Use `relatorio.gravar(texto, destino)`, que grava os três de uma vez:

| | para quem |
|---|---|
| `.md` | para o Claude Code, e para o git comparar linha a linha |
| `.html` | leitura rápida, abre com dois cliques no navegador |
| `.pdf` | arquivo e referência futura |

Nunca gravar só o `.md`. Isso vale para qualquer relatório de teste/conferência
(ver seção 4) — não vale para arquivos de controle do próprio repositório como
este `CLAUDE.md`, `PEDIDOS.md` ou o handoff em `historico/`.

---

## 3. As regras técnicas que não se negociam

- **PySide6, nunca tkinter nem customtkinter.**
- **Uma página por vez na memória.** O pico não pode crescer com o tamanho do
  livro; há livro de 300 MB no acervo. Nunca montar lista com todas as páginas
  processadas.
- **Interface nunca congela.** Todo processamento em QThread, com barra de
  progresso e botão de cancelar que funciona.
- **Nenhuma exceção fecha a janela.** Vira aviso em português numa caixa de
  diálogo; o erro técnico vai para o log, não para a tela.
- **Nenhum emoji em rótulo de interface.** Quebrou no Windows na versão
  anterior.
- **Textos de interface com acento (UTF-8). Caminhos de disco sem acento.**
- **Algoritmo consagrado em vez de fórmula própria.**
- **Nenhum modelo generativo.** Modelo que produz pixel pode inventar detalhe
  numa gravura de 1579, e detalhe inventado entra no PDF como se fosse o livro.
  Rede neural aqui só segmenta: aponta onde estão as coisas, nunca desenha.
- **A máquina só tem Python 3.14**, e todas as dependências funcionam nele
  (PySide6 6.11, PyMuPDF, OpenCV, numpy, Pillow, doxapy, scikit-image).
  **Não sugerir rebaixar a versão do Python.**
- **GPU: GTX 1650 4 GB, sem tensor cores** — nada que dependa de float16 rápido.
- **Erro nunca aparece como stack trace.** `sys.excepthook` grava em `erros.log`
  e mostra "Aconteceu um problema inesperado, mas o programa continua
  funcionando."

**Licença — decisão mudou em 17/09/2026.** Código GPL pode ser incorporado
direto agora (não só estudado de longe): o Samuel decidiu que, se um dia o
programa for liberado, é de graça com doação voluntária — então o programa
inteiro virar GPL (a obrigação que vem de usar código GPL) não é problema.
Isso também resolve a ressalva antiga do PyMuPDF: ele é AGPL (mais estrito
que GPL comum), e antes isso só valia "para uso interno está tudo certo, se
distribuir fora precisa rever" — agora, com a decisão de liberar com
código-fonte aberto, essa ressalva deixa de existir. PySide6 continua LGPL,
OpenCV/numpy Apache-2.0/BSD, DoxaPy CC0, scikit-image BSD, Pillow HPND — sem
mudança nenhuma nesses.

---

## 4. Testes — e a regra que existe por causa do que já deu errado

Foram 57+ commits com tudo marcado "feito" pelo próprio Claude Code, e **zero
itens aprovados por mim**. Já foi reportado "10 de 10 corretas" tendo olhado
uma imagem — seis estavam erradas. Por isso os testes agora têm dois tipos, e
só um deles o Claude Code decide.

### 4.1 Teste de máquina — o Claude Code faz e decide sozinho

Perguntas com resposta objetiva, que não dependem de gosto:

- O programa fecha ao clicar em algum botão, em qualquer tela, em qualquer
  tamanho de janela?
- O PDF de saída tem o mesmo número de páginas esperado? Alguma sumiu ou
  repetiu?
- A memória cresce com o tamanho do livro?
- PDF corrompido, protegido por senha, arquivo que some no meio, disco cheio,
  livro de 1010 páginas, cancelar no meio — o programa segura?
- Os cadernos saem na sequência certa quando se simula a dobra?
- Os textos da interface estão com acento?

Isso roda a cada mudança, automaticamente. **Essa é a aceleração do projeto** —
eu nunca preciso olhar.

### 4.2 Teste de olho — o Claude Code prepara, eu decido

"O papel saiu branco?" "O desenho ficou perfeito?" "A linha de corte está no
lugar certo?" Aqui o Claude Code já errou, e a régua também: hoje `avaliar.py`
dá número bom enquanto a mancha do verso piora. **Número que não pega o pior
defeito não pode dar veredito.**

O que o Claude Code faz:

1. Roda a mudança em **todos** os PDFs do conjunto de teste
2. Gera antes/depois e **abre todas as imagens** — não uma amostra
3. Monta `relatorios/para-conferir.html`: um quadro por mudança, já ampliado,
   com nome do livro e da página, o que olhar em uma frase, os números, e as
   ressalvas escritas
4. Escreve a própria opinião **junto com as ressalvas**
5. **Para. E me chama.**

**Ressalva escrita não é demérito. Ressalva escondida é.**

### 4.3 A regra de ouro

> O Claude Code pode escrever **"PRONTO PARA CONFERIR"** e a opinião dele.
> **Nunca "APROVADO".** Só eu marco, no `docs/plano/PLANO-DEFINITIVO.md`:
> `[x]` aprovado, `[~]` melhorar, `[-]` descartado.
>
> E todo item precisa dizer se foi teste de **máquina** ou de **olho**.

### 4.4 Auditoria por amostragem

De vez em quando eu confiro um item que o Claude Code deu como verificado por
máquina. Se bater, ele ganha mais autonomia. Se eu pegar um erro, a categoria
"máquina" encolhe. A confiança aqui é medida, não prometida.

### 4.5 Quantos testes existem de verdade

Conferido em 07/09/2026, direto no código (os documentos antigos divergiam
entre 59 e 150 — nenhum dos dois batia):

- **241 funções `def test_...`** escritas em `tests/` (15 arquivos).
- **279 casos** que o `pytest -q --collect-only` de fato coleta (a diferença
  vem de `@pytest.mark.parametrize`).
- **17 scripts `teste_*.py` soltos na raiz** (fora de `tests/`) — são testes
  manuais/exploratórios que geram relatório e imagem, não são coletados pelo
  pytest, e cada um cobre uma etapa ou bateria diferente. O principal para
  interface é o `teste_botoes.py` (clica em botões de verdade, via
  `botao.click()`/sinal `clicked` do Qt — não confundir com `teste_interface.py`,
  que dirige a lógica interna diretamente, sem clique real, e serve para outra
  coisa: validar o resultado de uma ação, não a fiação do botão).

### 4.6 Onde roda cada teste (decisões do Samuel, 19/10/2026)

As cinco perguntas foram respondidas uma por uma no chat; palavras dele no
Registro de mudanças do PLANO-DEFINITIVO (19/10).

| Onde | O que roda | Quando |
|---|---|---|
| **GitHub** (Windows da nuvem) | As ~2.050 conferências (`pytest`), o `teste_botoes.py` e os prints da janela real | Em **toda** entrega de agente, antes de ir ao verificador |
| **GitHub** | **Filtro de velocidade**: antes e depois **na mesma máquina, alternados** (`teste_velocidade.py` + Marial 300). Se acusar lentidão, volta para o agente | Em toda mudança que mexe em processamento (`core/`) |
| **PC do Samuel** | Um arquivo de teste por vez (`pytest tests\<arquivo> -q`) | Enquanto o agente trabalha |
| **PC do Samuel** | As ~2.050 conferências e o `teste_botoes.py` inteiros, com os outros agentes parados | **Antes de qualquer trabalho entrar no `fase-1`** (a gerente roda) |
| **PC do Samuel** | Janela de verdade pilotada pelo verificador | Nos trabalhos de tela |
| **PC do Samuel** | **Medida de velocidade que vale** para a regra 6 (alternada, PC sem agentes) | **No fim de cada fase** |
| **Notebook do Kaique** | Régua final de velocidade (item 0.6 / Fase 5) | Quando ele puder |

**Exceção (Samuel, 20/10: "opção 1"):** trabalho que **só acrescenta
documentos** (nenhuma linha do programa muda; no máximo um teste novo de um
script de documentos) entra no `fase-1` só com a rodada do GitHub passando, sem
a parada no PC. A parada no PC fica para quando o código do programa muda.

Decisões: suíte "B: GitHub e meu PC"; velocidade "opção 2" (filtro no
GitHub sempre, PC no fim de cada fase). Lentidão pequena achada no meio de uma
fase (ex.: Mágico pro +1,1% do "Para revisar") vai para a Fase 5, como o Samuel
mandou em 19/10: "vamos deixar esse concerto de lentidão para o final, para a
fase de desempenho".

**Filtro de velocidade (adotado em 20/10, validado contra o PC):**
`gh workflow run "Testes no Windows" -R Samuel-Bottini-BR/EditorImpressao --ref claude/list-server-files-gkos8v -f velocidade_ab=true -f ramo_antes=<ramo ou commit> -f ramo_depois=<ramo ou commit>`
(~1h55; veredito no topo da rodada; não vê diferença abaixo de 2% nem abaixo do vai-e-vem;
quando acusar "parece mais lento", disparar de novo uma vez antes de devolver ao agente).

Rodar no GitHub: `gh workflow run "Testes no Windows" -R Samuel-Bottini-BR/EditorImpressao
--ref claude/list-server-files-gkos8v -f ramo=<ramo>`; acompanhar com
`gh run watch <id> -R Samuel-Bottini-BR/EditorImpressao --exit-status`. O `gh`
fica em `C:\Program Files\GitHub CLI`.

### 4.7 Teste de reversão — obrigatório em todo conserto de bug (Samuel, 19/10/2026: "opção 1")

- Todo bug consertado ganha um teste em `tests/` que **falha no código antigo e
  passa no novo**. O nome ou a docstring do teste cita o bug (data e descrição
  da Lista de bugs).
- **O verificador prova**: roda o teste no código antigo (antes do conserto) e
  mostra que ele acusa o defeito. Teste que passa nos dois não vale.
- **Bug de imagem** (faixa preta, letra apagada, desenho que some) usa uma
  **medida** que pega o defeito (ex.: mm de preto na beirada do Cursus 3). Se
  não existir medida possível, isso vira **ressalva escrita**, nunca silêncio.
- Motivo, nas palavras da explicação aceita: "um defeito consertado nunca volta
  escondido, nem os de imagem".

### 4.8 Quem conversa com quem (Samuel, 19/10/2026: "C: chefe + bilhetes")

- **Os agentes entregam sempre à gerente.** Nunca passam trabalho direto a outro
  agente; a gerente confere o pedido e só então chama o próximo.
- **Outras janelas do Claude Code no PC** podem mandar recado direto à gerente
  (SendMessage), com três cuidados: (1) as **palavras literais** do Samuel, não
  resumo; (2) a gerente **repete o recado ao Samuel** e só muda o plano depois do
  "sim" dele; (3) todo recado fica **anotado na memória** (`memoria/conferencias.md`
  e a ficha do item), com data e de qual janela veio.
- Se a gerente estiver fechada, o recado vai para `memoria/recados/<data>-<origem>.md`
  e é lido ao abrir.

### 4.9 Memória do projeto (Samuel, 19/10/2026)

A memória organizada por assunto fica em `memoria/` (índice em
`memoria/INDICE.md`). Antes de começar um trabalho, cada agente lê o índice e
as fichas do assunto dele. **O plano continua mandando**: a memória organiza e
aponta, nunca contradiz o PLANO-DEFINITIVO. O `/checkpoint` atualiza as fichas
dos assuntos tocados na sessão. O histórico por data
(`historico/Editor de Impressao - resumo para o Claude.md`) continua inteiro.

---

### 4.10 Páginas de teste: caminho inteiro e só o que vai ser impresso (Samuel, 21/10/2026)

- **O teste segue a ordem das etapas** ("1 - recomendado"). Palavras dele: "Precisamos melhorar nossos testes porque
  as vezes o resultado de uma funcionalidade depende de ter passado por outra, por exemplo o cortar faixa preta, as
  vezes a folha precisa ter passado por endireitar antes de cortar, e você faz os testes sem pensar nisso, por favor o
  proximos testes tem que levar essa questão em conta." Todo teste de imagem e toda conferência levam a página pelo
  **caminho inteiro do programa**, na ordem do livro novo (dividir → endireitar → cortar → filtro), com os ajustes de
  fábrica, até a ferramenta testada. Teste da ferramenta sozinha só para achar causa de defeito, nunca na conferência.
- **Cada foto diz por onde a página passou e com quais opções** (ex.: "endireitada, cortada, Preto e branco + Só as
  letras"). Motivo: ele perguntou de onde vinha a letra T apagada e a estátua estragada sem saber a opção escolhida.
- **Só páginas que vão ser impressas** ("recomendado"). Palavras dele: "essa lombada de couro não seria impressa nunca,
  então não existe motivo para fazer teste nela e ficou muito ruim, não faça mais testes com lombadas de livros". Fora:
  lombada, capa e contracapa de couro ou papelão (o lado de fora do livro). Folha de rosto e guardas impressas valem.

---

## 5. O protocolo de qualquer mudança de imagem

**Medir antes — uma mudança por vez — medir de novo — reverter se qualquer
número piorar.**

Se parecer valer a pena mesmo assim, **não reverter sozinho**: registrar os dois
resultados e me apresentar.

Tudo que foi tentado, **inclusive o que falhou**, vai para
`relatorios/melhorias.md`. Isso existe para ninguém repetir caminho já fechado —
por exemplo, os cinco sinais medidos para separar escrita antiga de foto, em que
os números das duas se cruzam nos cinco.

---

## 6. Fronteira de autonomia

**Pode decidir sozinho:** limiar, janela, `k`, tamanho de bloco, ordem interna
de operações dentro de um filtro, troca de algoritmo de binarização, cache,
paralelismo, memória.

**Precisa perguntar antes:** criar ou remover filtro, mudar nome de filtro,
mudar qualquer tela, acrescentar ou tirar controle da interface, mudar o formato
dos arquivos de dados, alterar desfazer/refazer, trocar biblioteca.

---

## 7. Onde ficam as coisas

```
core/filtros.py            os quatro filtros
core/selecao.py             as regiões marcadas (gravura, letra, papel)
core/detectar_regioes.py    acha sozinho o que é o quê
core/rede_selecao.py        a rede neural de segmentação (só aponta, nunca desenha)
core/pipeline.py            dividir, cortar, endireitar, filtrar, impor
core/cadernos.py            imposição e conferência da sequência
core/analise.py             os alertas
projetos.py                 projetos salvos
avaliar.py                  a régua dos filtros
avaliar_selecao.py          a régua da seleção
conferir.py                 a tela de conferir amostras falando
teste_botoes.py              clica em botões de verdade, redimensiona a janela
docs/plano/                 o plano e o estado atual — leia primeiro (ver topo)
.claude/agents/             as regras dos agentes (ver seção 10)
gabarito/                   páginas fixas de conferência, fora do git (ver LEIA-ME)
PEDIDOS.md                  HISTÓRICO desde 24/09 — a lista que vale é o plano
relatorios/melhorias.md     tudo que foi tentado, inclusive o que falhou
relatorios/para-conferir.html   a entrega padrão
```

Regra de arquitetura: **`core/` não importa nada de `ui/`.** Todo o
processamento tem que rodar por linha de comando, sem abrir janela.

**O modelo de dados — a decisão que mais importa.** São dois níveis, de
propósito:

- **`ConfigFolha`** = o que veio no PDF de entrada. Guarda `dividir`,
  `posicao_corte`, `confianca_corte`, `rotacao`, `angulo_detectado`, `apagada`,
  `e_paisagem`, `alertas`, `revisada`.
- **`ConfigPagina`** = o que vai sair no PDF final. Uma folha dividida vira
  **duas** páginas (`metade` = inteira/esquerda/direita). Guarda `filtro`,
  `recorte`, `angulo_manual`, `tem_cor`, `apagada`, e os três ajustes
  **separados** (`forca_preto`, `clareza_melhorar`, `intensidade_magico`, 0–100
  com 50 no meio) — separados porque trocar de filtro e voltar tem que devolver
  o ajuste daquele filtro, sem herdar o do outro.

Recorte e ângulo moram na **página**, não na folha, porque o pipeline os aplica
*depois* de dividir. As abas da tela de conferir seguem essa separação: "Onde
cortar" edita folhas, "Filtro" edita páginas.

**Onde o programa guarda estado:** `%LOCALAPPDATA%\EditorImpressao` —
`historico.json`, `configuracoes.json`, `erros.log`, e por projeto
`projeto.json`, `acoes.jsonl`, `posicao.json`. Fechar e reabrir preserva o
projeto **e o histórico de ações**. Desinstalar **não apaga** essa pasta, de
propósito.

**Desempenho já resolvido, não refazer:** a análise roda a 150 DPI (lombada,
ângulo e cor aparecem de sobra) — livro inteiro em segundos. O fundo dos filtros
é estimado numa miniatura de ~400 px e reescalado: mesmo resultado ~10× mais
rápido (5,0 s → 0,5 s por página a 300 DPI).

**Ordem obrigatória do processamento** (mudou para os livros novos em
09/10/2026 — decisão do Samuel na pergunta `g6-endireitar-antes`, "Endireitar
antes de cortar (como o ScanTailor): pode começar?" → "Pode começar"):

- **Livro novo:** `dividir folhas → endireitar a página inteira → achar o
  corte na página reta e cortar → filtro → montar cadernos` (como o
  ScanTailor).
- **Projeto começado antes de 09/10/2026** (sem o campo `ordem_do_preparo`
  no `projeto.json`): `dividir folhas → cortar bordas → endireitar → filtro →
  montar cadernos`, como sempre, idêntico ponto por ponto.

O campo é `Projeto.ordem_do_preparo` (`core/ordem_do_preparo.py`). O giro de
90 em 90 vem antes de tudo nas duas. Páginas apagadas são descartadas logo
depois da etapa 1.

Comandos:

```
.venv\Scripts\python.exe main.py                 o programa
.venv\Scripts\python.exe -m pytest tests -q      os testes (666 casos em 26/09/2026)
.venv\Scripts\python.exe avaliar.py              a régua dos filtros
.venv\Scripts\python.exe avaliar_selecao.py      a régua da seleção
.venv\Scripts\python.exe conferir.py             conferir amostras falando
.venv\Scripts\python.exe teste_botoes.py         clica em botões de verdade, todas as telas
```

Acervo: `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE
IMPRESSAO\LIVROS PARA TESTE` — nove livros, 2903 folhas. **Somente leitura.**
Mudou da área de trabalho para lá em 07/09/2026; `avaliar.py` acha sozinho.

As queixas do Kaique: `D:\programas\EditorImpressao-arquivos\BIBLIOTECA DO FIM
DOS TEMPOS\Teste de livros` — `.txt` soltos com um print ao lado. **São fonte
de requisito.**

**Handoff:** `historico/Editor de Impressao - resumo para o Claude.md` virou
**histórico** em 24/09 — numa sessão nova, leia primeiro `docs/plano/` (ver
topo). O handoff continua útil para achados técnicos caros de redescobrir. Só
atualize esse arquivo (ou crie um novo) quando o Samuel pedir explicitamente.

---

## 8. O ciclo de uma mudança, do começo ao fim

1. O item vem da **fase atual** do `docs/plano/PLANO-DEFINITIVO.md`, na
   ordem. Nada de fase seguinte. No começo de cada fase, antes do primeiro
   item, resolve-se a **Lista de bugs**.
2. A conversa gerente passa o item ao **implementador** (seção 10).
3. Ele faz a mudança. Uma só.
4. Roda os testes de máquina. Se algum quebrar, conserta antes de seguir.
5. Roda a régua e o **teste de velocidade** (`teste_velocidade.py`). Se
   qualquer número piorar, reverte — ou apresenta os dois resultados. Nenhum
   item pode deixar o programa mais lento.
6. O **verificador** gera o antes/depois **só com as páginas-gabarito daquele
   item** (`gabarito/lista.json`) e abre **todas** as imagens. Item de tela:
   pilota a janela real com mensagens nativas de mouse.
7. Monta o relatório de conferência (três formatos) com a opinião e as
   ressalvas.
8. Marca o item como **PRONTO PARA CONFERIR** e me chama.
9. **Eu abro o programa pelo atalho "(desenvolvimento)", confiro em até 10
   minutos, e marco `[x]`, `[~]` ou `[-]` no plano.**
10. Se aprovado, commit **na hora**, com o defeito que resolveu escrito por
    extenso, e `git push` (o repositório tem GitHub remoto — não é preciso
    perguntar cada vez, mas sempre revisar o que está sendo commitado antes:
    nunca commitar segredo, nunca desfazer o `.gitignore` sem avisar).

---

## 9. O que já se sabe que está errado (não redescobrir)

- **A mancha do verso é o defeito mais grave aberto.** O Preto e branco não a
  remove — ele a escurece: no original é cinza fraco, depois do filtro vira
  marca preta legível. A régua não pega isso porque mede o fundo longe da tinta.
  Solução recomendada: o acervo tem as duas faces da mesma folha; espelhar o
  verso, alinhar sobre a frente e subtrair.
- **A régua precisa de dois critérios novos:** comparar na região onde havia
  mancha (não só no fundo limpo), e olhar a moldura da página (faixa escura nos
  últimos milímetros é fundo de scanner, nunca conteúdo). Falta um terceiro:
  medir sujeira guardada — o Otsu marca zero pioras mas guarda o dobro de tinta
  do Sauvola.
- **O amarelado não está no papel, está na tinta.** A tinta impressa de 1579 é
  marrom, e a orla de cada letra carrega essa cor. Cuidado: rubricação
  desbotada também é marrom.
- **Não existe binarizador vencedor único.** Os 18 do DoxaPy foram comparados em
  36 páginas. No Palatino o Otsu sai sólido e o Sauvola quebra o traço; noutras
  se inverte.
- **A receita difundida de "magic color" estraga capas coloridas.** Dividir por
  `GaussianBlur` canal a canal: numa área azul uniforme o próprio azul é o
  fundo, então a divisão lava a cor e desloca o matiz — o título azul virou
  vermelho no livro de teste. A correção já adotada em `core/filtros.py`:
  dividir pelo fundo **relativo ao nível do papel** com ganho igual nos três
  canais; **pesar** a correção por quanto o fundo local ainda parece papel; e
  branquear com **curva de ombro** no canal L do LAB, nunca multiplicação
  linear. **Não desfazer isso.**
- **Scan de baixa resolução não se recupera.** As páginas do Boécio já nascem
  fora da faixa saudável — 4 MB para 50 folhas. O remédio é reescanear. É o
  único ponto do projeto em que "até ficar perfeito" não se aplica.
- **A barra de rolagem não é mais preta.** Ficou quase-preta em 05/08 (a
  pedido do Kaique), e foi revertida para cinza médio (`#a8a49e`) em 08/08 —
  o preto puro lia como risco de erro atravessado no pé da tela. O estado
  atual (cinza) é intencional e documentado no próprio `ui/estilo.py`; não
  reverter sem decisão explícita do Samuel.
- **O bug do menu "Abrir" (achado 07/09/2026) já foi corrigido — esta seção
  estava desatualizada.** Era: a ação "Abrir" do menu (`ui/janela_principal.py`,
  `_montar_menu`) simulava um clique com `lambda:
  self.tela_inicio.area.mousePressEvent(None)`, o que levantava `AttributeError`
  (`evento.button()` em `evento=None`). Corrigido no mesmo dia, commit `9d27b76`
  ("Corrige o bug do menu Abrir: simulava evento de mouse com None") — hoje o
  menu chama `self.tela_inicio.area.abrir_dialogo_de_arquivo()` diretamente
  (`ui/widgets/area_arrastar.py`), o mesmo método usado pelo clique normal.
  Achado em 22/09/2026: a prosa do handoff (PARTE -1) já registrava a correção
  no mesmo dia; era só esta seção do `CLAUDE.md` que tinha ficado pra trás —
  ver seção 10, item 8.

---

## 10. Como este projeto trabalha agora (a partir de 25/09/2026)

1. **Conversa gerente + agentes** (PLANO-DEFINITIVO, seção 3). A conversa do Claude Code
   com o Samuel é a **gerente**: conversa com ele, divide o trabalho, chama os agentes e
   junta tudo. **Não escreve código linha por linha ali.** Os agentes têm as regras em
   `.claude/agents/`:
   - **`implementador`** — código de processamento (`core/`) e scripts de apoio. Uma
     mudança por vez, com comentário do que faz e do que é arriscado mudar.
   - **`verificador`** — testes, velocidade, antes/depois nas páginas-gabarito, abre
     todas as imagens, pilota a janela real quando o item é de tela, escreve a opinião
     com as ressalvas. **Nunca** marca aprovado.
   - **`pesquisador`** — estuda código e documentação de fora (ScanTailor Advanced,
     archive-pdf-tools, OCRs), resume com as próprias palavras e diz a licença de cada
     coisa. Grava em `docs/pesquisa/`.
   - **`layout`** — só mexe em `ui/`, na própria cópia do projeto (git worktree em
     `.claude/worktrees/layout`, ramo `layout`). **Só começa quando o Samuel entregar o
     plano de layout** (Fase 4).
2. **Uma fase por vez, na ordem do plano.** Ideia nova (de quem for) vai para a **Lista de
   espera** do plano, com data — nunca para a fase atual. Bug que **impede** a tarefa é
   consertado na hora; bug que **não impede** vai para a **Lista de bugs** do plano, com
   print e data, e é resolvido no começo da fase seguinte.
3. **Frentes em paralelo, uma cópia e um ramo cada.** Processamento (`core/`) e layout
   (`ui/`) trabalham cada um na sua cópia (git worktree) e no seu ramo, com commits
   pequenos e frequentes. Antes de mexer, conferir `git log` do `master` para ver o que a
   outra frente mudou. **Só a gerente junta as frentes** no `master`.
4. **O plano tem duas cópias** — `docs/plano/` (no git) e
   `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\` (onde o Samuel edita). No
   começo de cada conversa, a gerente compara as duas; se o Samuel mudou a dele, copia
   para `docs/plano/` e faz commit. Quando a gerente aplica uma mudança que o Samuel
   pediu, aplica **nas duas**. As duas nunca ficam diferentes.
5. **Documentação obrigatória de código.** Todo arquivo/função tocado a partir de agora
   precisa ter comentário/docstring explicando o que é, o que faz, e (quando não for óbvio)
   o que é seguro ou arriscado mudar ali. Vale tanto pra código novo quanto pra qualquer
   arquivo existente que for tocado por outro motivo.
6. **Nenhum plano novo substitui silenciosamente o que já estava pendente.** Antes de
   fechar qualquer plano (modo de planejamento), conferir o `PLANO-DEFINITIVO.md` (fases,
   Lista de bugs, Lista de espera) e a seção 9 acima
   — todo item em aberto continua valendo até ser resolvido ou descartado explicitamente
   pelo Samuel. Um plano novo declara o que resolve e o que deixa de fora; nunca apaga
   pendência por omissão.
7. **Todo item resolvido guarda o pedido original.** Ao marcar algo como implementado com
   sucesso (no `PLANO-DEFINITIVO.md` ou em qualquer registro equivalente), preservar a frase de quem
   pediu (Samuel ou Kaique, citação literal sempre que existir) junto com o que foi feito e
   onde — pra poder ser revisitado sem precisar garimpar o histórico de conversas.
8. **Cuidado com o handoff vs. o código real.** Já aconteceu de um checkpoint do handoff
   dizer "corrigido" e outro documento (`CLAUDE.md` seção 9) mostrar o oposto, escritos no
   mesmo dia (caso do menu "Abrir", acima). Prosa de checkpoint é registro histórico, não
   prova — quando o estado importar de verdade, checar o código e o `git log`, não só
   confiar no texto.
9. **Apagar arquivo ou pasta (regra do Samuel, 29/09/2026).** Vale para a conversa gerente e
   para todos os agentes:
   - **Fora da pasta do projeto** (`D:\programas\EditorImpressao`): **nada é apagado sem
     perguntar ao Samuel antes**, nem pasta que pareça criada por engano. O agente não
     pergunta direto: para, relata à gerente o caminho e o que há dentro, e a gerente
     pergunta ao Samuel.
   - **Dentro da pasta do projeto:** só se apaga o que o próprio agente criou naquela
     tarefa. O que já existia não se apaga sem perguntar.
   - Motivo: em 29/09 um agente apagou uma pasta inteira `D:\d` sem conferir o que havia
     nela, achando que era só um download dele. Apagado por comando não vai para a Lixeira.
10. **Conferências do Samuel: páginas que salvam sozinhas e abrem sozinhas (regra do Samuel,
    06/10/2026).** Tudo o que ele precisa ver ou responder vai numa página do claude.ai com banco
    de dados (imagens grandes, "Escolho esta", caixa de comentário; a resposta fica salva na hora):
    - "Escolhas do Editor de Impressão" (comportamento do programa):
      https://claude.ai/artifact/EJoJq5mocxi3vbNxU8ZecV
    - "Layout do Editor de Impressão" (telas): https://claude.ai/artifact/QuzVaghq2tz2WVwJ1AyMWu
    - "Quando revisar uma página" (o "Para revisar"): https://claude.ai/artifact/NeCgyTotRfqsdXntn9vMUc
    - **"Central de decisões"** (era "Andamento do programa"; refeita em 21/10/2026 a pedido do Samuel:
      "tem que ser como uma central de decições, para tornar as coisas mais rapidas e mais faceis"):
      https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy
      - **O que mostra:** Decidir agora · Quadro dos trabalhos · Etapas · Agentes · Defeitos · Velocidade
        · Ordens e ideias. Fonte: `docs/plano/central/fonte.json` (a gerente mantém) +
        `docs/plano/para_a_central.py` (junta com o plano, `memoria/bugs.md` e o git; avisa se um
        trabalho "no programa" não estiver no `fase-1`). Gravar o banco com ArtifactData `batch` a partir
        dos arquivos que o script gera (`D:\programas\EditorImpressao-arquivos\central-banco\`).
      - **Atualizar sempre** que um trabalho muda de situação, um agente começa/entrega/para e no
        `/checkpoint` (fonte.json → script → batch). Novidade para ele: acrescentar em `geral.novidades`.
      - **Ler as ordens dele primeiro, ao abrir cada conversa**, e entre uma tarefa e outra: coleções
        `ordens` (tipo juntar | continuar | parar | testar | comentar | resposta), `testes` (testei no PC
        bom/ruim), `ideias` e `config` (`prioridade.ordem` = fila dos agentes; `agentes.max` = quantos
        agentes ao mesmo tempo). Ao ler, marcar `estado: "vista"`; ao cumprir, `"feita"`, com `resposta` e
        `respondidaEm`. Registrar a ordem no Registro de mudanças com as palavras dele. "Pôr no programa
        como está" **não pula** a §4.6 (GitHub + PC antes de juntar). Ideia nova vai para a Lista de
        espera e fica `estado: "registrada"`.
      - Quando puser cartão novo em "Decidir agora", mandar aviso no celular (PushNotification).
      - **Pergunta de agente vai para a Central na hora, sem esperar a entrega** (falha de 22/10: as 8 perguntas do
        Implementador B ficaram no ONDE-PAREI dele e só foram vistas quando o Samuel perguntou "tem alguma coisa para
        responder já?"; ele: "na central, você não deveria atualizar sempre que ouver algo para responder? [...] regra
        falhou?"). A cada aviso de agente (inclusive "esperando os testes") e a cada pedido de andamento, a gerente lê a
        seção "Perguntas para o Samuel" do ONDE-PAREI de cada ramo ativo; pergunta nova vira aba na Conferência
        (`conferencias/perg-<agente>`), cartão em "Decidir agora", novidade no topo, aviso no celular e a página aberta
        no navegador dele com `start ""`.
      - **Aba Conferência (21/10, pedido dele: "os tipos de relatorio para conferencia tem que estar separados por abas
        dentro da aba de conferencia"; quadros grandes como na página de conferência antiga):** os relatórios ficam na
        coleção `conferencias` (um documento por aba), tirados por `docs/plano/central/extrair_conferencia.py` da página de
        conferência e das perguntas abertas da página de escolhas. **As respostas dele aos quadros e perguntas ficam na
        coleção `respostas` da Central** (`opcao`, `opcaoNome`, `comentario`, `em`, `relatorio`); ao ler, marcar `lida: true`.
        Relatório novo: acrescentar a variável em `RELATORIOS` do extrator (ou o JSON direto em `central/conferencias/`),
        copiar as fotos com `files: {artifact, path}` (lista em `_imagens.txt`) e rodar o gerador.

    **Quando uma página de conferência nova ficar pronta, a gerente abre sozinha no navegador do
    Samuel (com `start "" "<endereço>"`, que abre no navegador padrão do Windows; a ação `open` da
    ferramenta Artifact não chega ao navegador dele), sem perguntar — desde que ele já tenha feito a conferência anterior e dado ok no chat.**
    Se ainda houver conferência sem resposta, a gerente só avisa no chat que há outra pronta (e
    abre se ele pedir). Palavras dele: "sempre que tiver paginas de conferencia prontas, pode abrir
    automaticamente no meu pc, caso eu já tenha feito a ultima pagina de conferencia e te dado ok."
    A gerente não vê as respostas sozinha: lê o banco da página quando ele avisa ("respondi") e
    copia as respostas, palavra por palavra, para `relatorios/` e para o Registro de mudanças.

    **Comentário com dúvida ou questionamento se responde NA página, não no chat (regra do Samuel,
    07/10/2026).** O comentário dele vale como resposta: a gerente refaz a explicação da pergunta
    respondendo ao que ele escreveu (com desenho ou imagem quando ajudar), mostra a questão de novo
    com opções novas tiradas do comentário e, se surgir outra decisão, cria pergunta nova na mesma
    página. No chat, só um aviso curto de que a página mudou. Palavras dele: "não me responda no chat
    quando tiver questionamentos nas conferencias, responda nas conferencias." e "o meu comentario
    serve como resposta, porque você não responde ele e me mostra a questão de novo?"
    Quando a pergunta volta, o comentário dele **sobe e fica fixado** (pedido de 07/10: "eu acho que ele
    devia subir e virar um comentario fixado junto quando voltasse, para que dai eu colocasse outro e
    tivesse referencia do que foi colocado antes"): a gerente copia o comentário para o campo
    `historico` da pergunta (`[{quem: "samuel"|"gerente", em, texto}]`, mostrado no alto como
    "Comentários anteriores desta pergunta (fixados)") e esvazia o `comentario` da resposta.

## 11. Livro de decisões: nenhuma decisão do Samuel fica de fora (regras do Samuel, 26/10/2026)

Por que existe: na sessão 1 dos testes guiados (26/10/2026) apareceu que decisões dele de 25/09 nunca foram
construídas — "Photoshop puro, sem abas. Uma única tela com todas as ferramentas" foi feita só na aparência (a regra de
julho que esconde ferramentas continuou por baixo), e o painel Automático no lugar da tela "O que fazer" ficou "sem dono"
desde 12/10. Investigação: `relatorios/testes-guiados/2026-10-26-sessao-1/o-que-deu-errado.md`. Palavras dele: "Isso
tinha sido uma coisa falada expliccitamente [...] isso foi uma grande alucinação" e "já temos histórico planos, decisões
minhas anotadas, várias páginas de conferências, que continuam sendo desobedecidas." Regras aprovadas por ele ("Sim").
Valem para a gerente, para todos os agentes (`.claude/agents/`) e para qualquer conversa nova.

1. **Um Livro de decisões único: `docs/plano/DECISOES.md`.** Cada decisão: número, data, **palavras exatas dele**, o
   que quer dizer na prática, onde toca no programa, a prova de comportamento, a situação (construída / pela metade /
   não construída / a conferir), o dono e a fonte. Toda decisão nova entra **na hora**, venha do chat, da Central ou de
   uma conferência (e também no Registro de mudanças, como sempre). Ele tem duas cópias, como o plano (§10.4).
2. **Nenhuma decisão sem dono.** Cada linha aponta para uma etapa, um agente ou a Lista de espera, com data. Em todo
   `/checkpoint` a gerente procura linhas sem dono ou "pela metade" sem etapa e avisa o Samuel.
3. **Todo pedido a um agente leva as decisões que tocam o que ele vai mexer**, copiadas do Livro (número + palavras
   dele). Antes de começar, o agente escreve no ONDE-PAREI "Decisões que esta tarefa precisa cumprir"; ao entregar,
   "Como cumpri cada uma" (com print ou teste). Sem essa seção, a entrega não é aceita.
4. **Cada decisão tem uma prova de comportamento** em `tests/test_decisoes.py` (ex.: "abrir sem marcar nada → todas as
   ferramentas à vista"). **Nada se junta ao `fase-1` se a prova de uma decisão tocada falhar ou não existir.** Quando a
   decisão substitui um comportamento antigo, a prova confere também que o antigo saiu. Aparência não conta como prova.
5. **Quem confere nunca é quem construiu, e confere do zero.** Antes de juntar, um verificador separado compara a
   entrega com o Livro de decisões, e o teste do Kaique (agente que não sabe usar o programa) roda as tarefas sem nada
   preparado antes. Na conferência do Samuel, cada print aparece ao lado das palavras dele da decisão.
6. **Na dúvida, parar e perguntar — nunca fazer diferente em silêncio.** Se uma decisão parecer impossível,
   contraditória ou pouco clara, o agente para e a pergunta vai ao Samuel pela Central (cartão em "Decidir agora").
   A gerente também: antes de oferecer uma opção ou dizer que algo "não existe", procura no Livro de decisões, no
   rascunho do layout e na Central; se já está decidido, cita data e onde está escrito em vez de perguntar de novo.
7. **Só o que ele mandou (Samuel, 27/10/2026).** "os agentes estão mudando coisas que eu já tinha definido, é só para
   fazer o que eu já tinha mandado, fazer as ferramentas que colocamos no programa funcionem como deveriam e como eu
   tinha escolhido." Nem a gerente nem os agentes acrescentam comportamento, botão, aviso ou texto que ele não pediu,
   nem mudam o que ele decidiu — nem por causa de um achado de agente (ex.: o "PDF gigante" dos testes não vale contra
   a D-304, "o tamanho do arquivo depois não importa"). "Escolha da gerente" (D-014) só serve para detalhe técnico do
   que ele mandou; o que o Livro não responde fica como está e vira pergunta na Central.

8. **O novo não estraga o que já está escolhido e testado (Samuel, 03/11/2026).** "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes precisam ler". Vale para a gerente e para todos os agentes. Na prática:
   - Antes de mexer, escreva no ONDE-PAREI "O que já está escolhido e testado aqui": as decisões do Livro e os testes que já existem para a tela ou o arquivo que você vai tocar.
   - Se a coisa nova mudaria uma dessas escolhas, pare e pergunte (a gerente leva à Central). Nunca mude em silêncio, nem "por enquanto".
   - Antes de entregar, rode as provas das decisões (`tests/test_decisoes*.py`) e os testes dos arquivos que tocou; o GitHub roda todos. Teste antigo que quebra faz a entrega voltar: nunca mude um teste antigo para ele passar.
   - O verificador confere também o que já funcionava ao redor (clicando, nos trabalhos de tela), não só o item novo.

9. **Pensar em quem usa e no livro pronto, e deixar anotado (Samuel, 05/11/2026, D-637).** "só garanta que não crie mais problemas fazendo isso, você tem que pensar na experiencia do usario e no resultado final do livro dentro do programa, quando vai mudar algo, deixe isso anotado." Vale para a gerente e para todos os agentes. Na prática:
   - Antes de mexer, escreva no ONDE-PAREI a seção "Como fica para quem usa e no livro": o que o Kaique vê e faz, passo a passo, antes e depois da mudança, e o que muda (ou não) no PDF que sai.
   - Na entrega, confira essa seção clicando no programa e olhando o PDF, e diga se a mudança criou algum problema novo. Sem essa seção, a entrega não se junta.

10. **Mudou a ferramenta, muda em todos os lugares (Samuel, 10/11/2026, D-667).** "Você devia ter mandado ele mudar a ferramenta, se mudou a ferramenta, muda em todos os lugares." · "Isso me faz parecer que você está fazendo gambiarra no codigo". Falha de 10/11: a D-662 foi pedida e feita só no "todas as folhas" do Dividir; "daqui em diante", "só as pares" e "só as ímpares" ficaram do jeito antigo e precisaram de outra pergunta (D-666), como já tinha acontecido com a D-640/D-645. Na prática:
   - A gerente pergunta e pede **sobre a ferramenta inteira**, nunca sobre um item da lista dela. O pedido ao agente lista todos os lugares: todas as opções (ex.: todos os itens do "aplicar em"), todas as telas e ferramentas onde ela aparece (dentro e fora do Dividir), a tela grande, a tira de páginas e o PDF.
   - O agente muda **a regra da ferramenta num lugar só do código**, que todas as opções usam. Não acrescenta um desvio para um caso ("se for o Dividir e for 'todas as folhas', vai por aqui"): isso é remendo, e o próximo pedido vira outro remendo.
   - Só vira pergunta o lugar onde a mudança não faz sentido ou mudaria outra decisão dele (§11.8).

11. **Agente não abre agente (10/11/2026).** Falha de 10/11: o revisor de código abriu três ajudantes por conta própria e o Samuel viu cinco agentes rodando ("pera ai, tem 5 agentes trabalhando"). Todo pedido a agente diz: "não abra outros agentes". Quem decide quantos agentes rodam é a gerente, dentro do limite do Samuel (no máximo dois; em 10/11 ele deixou três, com o terceiro só lendo código: "pode deixar assim").

12. **Sem gambiarra: uma ferramenta, uma regra, um lugar só no código (Samuel, 13/11/2026).** Palavras dele: "Lembre de que o agente não pode fazer gambiarras como na outra ferramenta nossa que fazia várias gambiarras e funcionava de maneira diferente em vários lugares." · "Faça disso uma regra bem explica para os agentes" · "para saber bem o que aconteceu leia o histórico [...] Para a regra ficar bem escrita". Vale para a gerente e para todos os agentes. Completa a regra 10.

    **O que aconteceu (10/11/2026).** O Samuel testou o girar no Dividir com "Duas lado a lado" (Gradus, folha 10, páginas 18 e 19; prints a-70 a a-73). Com "todas as folhas", cada página deitava sozinha. Com "só as pares", a folha inteira deitava, com as duas páginas juntas e pedaço da vizinha. A causa: a D-662 tinha sido pedida e feita **só** no "todas as folhas". Palavras dele: "a pergunta é, quando eu mandei fazer, porque o gerente não fez em tudo?" · "Isso me faz parecer que você está fazendo gambiarra no codigo" · "Como a mesma função pode fazer coisas diferentes" · "Eu não quero remendos nesse código, gambiarras [...] eu quero as praticas de um programador senior na hora de codar". A revisão do código feita a pedido dele (`relatorios/revisao-codigo-2026-11-10/relatorio.md`, ramo `revisao-codigo-2026-11-10`) achou **17 remendos parecidos**. Os quatro que já saem diferentes para quem usa:
    - **O Girar tinha sete caminhos, um por decisão** (D-035, D-618, D-636, D-638, D-640, D-645, D-662). Cada decisão nova ganhou um `if` novo em `ui/tela_conferir.py`, e o caminho era escolhido pelo jeito de ver a tela ("Uma página" ou "Duas lado a lado"), não pelo que a folha é. A grade "Todas as páginas" ainda somava o giro com outra fórmula.
    - **As figurinhas do Filtro e o "comparar" da tela grande usavam uma conta mais simples que a da página.** Quando deu defeito, o "Só as letras" foi consertado só nas figurinhas e ficou errado no "comparar".
    - **O "usar em todas" queria dizer uma coisa em cada ferramenta.** O Cortar, o Dividir e o Mover deixam de fora o que foi feito à mão. O Marcar apaga a gravura marcada à mão nas outras páginas.
    - **O Automático e o botão "não dividir esta" deixavam a folha inteira de dois jeitos.** O comentário do código dizia "como o 'não dividir esta'", e isso já não era verdade.

    **O que é gambiarra aqui:**
    - Consertar só no lugar onde o defeito apareceu, com um desvio para aquele caso ("se for o Dividir e for 'todas as folhas', vai por aqui"; "se veio do Automático, faça X").
    - Copiar a mesma conta ou a mesma lista para outro arquivo e mudar só a cópia. Exemplo: a lista "o que é do filtro" estava escrita à mão em seis lugares e já divergia, porque a "Letra clara em fundo escuro" ia no Automático e não ia no "todas" do painel.
    - Tratar o sintoma em vez da causa: evitar que o defeito apareça naquele caso e deixar a causa pronta para o próximo.

    Tudo isso passa no teste daquele caso. Mas a ferramenta fica fazendo coisas diferentes em lugares diferentes, e o Samuel acha o mesmo defeito no lugar seguinte.

    **Antes de mexer, o agente escreve no ONDE-PAREI:**
    1. **por que** o defeito aconteceu: a causa, não só onde apareceu;
    2. qual é **a regra da ferramenta**: a função que decide o comportamento (ex.: quais páginas giram; se o fundo tirado fica quando o filtro muda);
    3. **todos os caminhos** que chegam nela, achados com busca no código (`grep`) pelo campo e pela função:
       - botões, menus, teclas e painéis;
       - cada item do "aplicar em";
       - Automático, grade "Todas as páginas", tela cheia e "comparar";
       - "só neste pedaço", desfazer e refazer;
       - prévia, figurinhas, miniaturas e PDF;
    4. para cada caminho, **se ele usa essa mesma função ou tem conta própria**.

    **Como conserta:**
    - Muda a regra **num lugar só**, de preferência em `core/` (a tela só chama), e faz os caminhos que tinham conta própria passarem a chamar essa função.
    - Um dado da página (ex.: "fundo tirado: sim ou não") é lido e gravado por uma função só.
    - Uma lista (campos do filtro, etapas, opções) é escrita uma vez e importada.
    - Dois botões que fazem a mesma coisa (menu e painel, botão e Automático) chamam a mesma função.
    - Comentário do código que diz "é a mesma conta de..." ou "como o botão X" é conferido na hora: se deixou de ser verdade, conserta-se o código ou o comentário.

    **Como prova.** Na entrega:
    - a lista "caminho → função que ele usa";
    - uma prova em `tests/` que passa pelos caminhos principais e cobra **o mesmo resultado em todos**, não só no caminho do defeito.

    **Quando não dá:**
    - Se a única saída for um remendo num lugar só (ex.: mudar a regra mudaria outra decisão dele, regra 8), o agente **para** e escreve o porquê em "Perguntas para o Samuel"; a gerente leva à Central. Remendo nunca entra calado, nem "por enquanto".
    - Se juntar os caminhos mexer em mais de uma ferramenta ou em coisas já testadas por ele (D-605), o agente escreve o plano antes e espera o "sim".

    **A gerente:**
    - Pede sempre sobre a ferramenta inteira (regra 10) e põe esta regra em todo pedido de conserto.
    - Não aceita entrega com desvio para um caso ou com conta duplicada. O verificador procura isso de propósito.

    As outras regras de código propostas pelo revisor em 10/11 (erro engolido, plano antes de mudança grande, etc.) continuam só como proposta, esperando o Samuel.

13. **Como perguntar e responder ao Samuel (Samuel, 13/11/2026).** Pedido dele: "precisa ajeitar para isso como regra, consegue pegar as perguntas e respostas que tu fez que eu não entendi, ver um padrão e fazer um conjunto de regras para responder e fazer perguntas." A gerente leu os 106 casos de "Ainda não entendi" e de reclamação da explicação na Central (21/10 a 13/11) e achou sete padrões. Cada regra abaixo tem as palavras dele que a originaram. Vale para a gerente e para todo agente que escreve pergunta, relatório ou resposta para ele: Central, chat e relatórios.

    **1. Comece pelo que é e onde fica.** A primeira frase diz de que tela, botão ou ferramenta se trata, com o caminho de clique (ex.: "Na janela Montar para imprimir, que abre em Arquivo > Montar para imprimir, há um quadro chamado..."), e para que ela serve. Só depois vem o problema.
    - Origem: "Que grade?" · "Que Obra?" · "Não sei de que arranjos está falando" · "Essa ferramenta é uma mão?" · "Como assim, o que vai sair? Quero um exemplo disso." · "e porque tem esse aviso [...] para que serve, e em que situação é disparado?" · "eu nem entendi para que serve esse botão" · "Você ainda não explicou o que está acontecendo".

    **2. Nenhuma palavra de dentro.** Para ele, nada de número de decisão (D-567), código (G2, 2.11, 601), nome de etapa ou de agente ("obra", "etapa 4", "agente de layout", "implementador B"), nome de arquivo ou de função, nem "escolha da gerente". Use o nome que aparece na tela do programa, e o livro e a página. O número da decisão só pode ir no fim, entre parênteses, para consulta.
    - Origem: "Que Obra?" · "Não sei de que obra está falando" · "Não se deve usar código na nomeação de coisas".

    **3. Toda pergunta e todo "está feito" têm prova em imagem, e a imagem prova exatamente o que o texto diz.**
    - Print do caso real, no modelo do girar (CLAUDE.md §10): faixas com nome (azul = antes ou como é hoje, verde = depois ou a outra opção), as mesmas páginas lado a lado, o que olhar circulado em vermelho e uma frase em cada imagem dizendo o que olhar.
    - Quando as opções dão resultados diferentes, há uma imagem para cada opção.
    - "Já funciona" ou "já existe" também vem com print.
    - Origem: "como eu vou responder algo sem provas ou exemplos?" · "Não estou vendo provas do que você diz" · "prints inconclusivos, qual é antes e depois?" · "Os prints não tem nada haver com a pergunta" · "não entendi nada, não tem exemplos" · "preciso de exemplos, não consegui visualizar" · "essa resposta não tem print provando que esse modo funciona".

    **4. O exemplo é o caso que o Kaique encontra, e o print é conferido antes de mandar.**
    - Use o livro e a página onde o problema acontece de verdade, no estado em que o Kaique os teria (dividido, se o caso pede dividido).
    - Nunca use uma página que nem vai ser impressa, nem um print com coisa cortada ou fora do lugar que distraia.
    - Abra o print e confira se ele mostra o que a frase diz.
    - Origem: "está fazendo teste com pagina de lombada que nem iria ser impressa" · "Porque usou uma folha sem estar divida?" · "Só não entendi porque cortou parte do livro ali no canto superior direito" · "Tem uma pagina maior que outra ali".

    **5. Diga o caminho e se é defeito ou escolha.**
    - Escreva o caminho que a página fez: livro, página, o que foi ligado, o filtro e as caixinhas, à mão ou pelo Automático.
    - Diga com todas as letras se é **defeito do programa** ou **efeito de uma escolha**. Se ainda não se sabe, diga "ainda não se sabe; vou investigar".
    - Origem: "qual opção foi pedida para ser feita que tirou a letra? anote ai para explicar melhor o processo que a pagina passou para poder me perguntar" · "que opção foi escolhida para sair assim?" · "não sei se foi erro seu ou do programa" · "tem que saber diferenciar bugue de erro".

    **6. Diga o que ele está escolhendo e o que muda em cada opção.**
    - Antes das opções, uma frase: "O que você escolhe: ...".
    - Cada opção diz o que acontece depois, para o Kaique e no livro que sai.
    - Diga se a coisa é nova ou se já existe hoje, se muda muito o programa e se dá para ligar e desligar.
    - Se é um erro, diga que é erro e o que vai acontecer com ele (entra na fila? quando?).
    - Uma pergunta é uma decisão. Lista de vários erros não é pergunta: cada erro vem com o seu print e com a explicação simples de como acontece.
    - Toda pergunta tem a opção "Só comentário" e a sugestão da gerente.
    - Origem: "não entendi o que tem que ser escolhido" · "então isso entra na lista de coisas para fazer?" · "No caso, isso é uma opção a mais do que a que temos hoje?" · "Isso que eu escolhi vai alterar muito o programa?" · "vai ser uma opção que eu posso desligar e ligar né?" · "isso é um erro? vai ser resolvido?" · "eu quero ver esses erros, as provas dele e uma explicação de como acontece".

    **7. Curto, sem ficha técnica, e respondendo o que ele perguntou.**
    - Poucas frases, uma ideia por frase, primeiro a frase que se entende, o número depois.
    - Nada de ficha com campos ("Situação", "Você pediu", "Solução na versão de teste", "Parte do programa"). Essas fichas da auditoria de 29/10 a 09/11 foram as que mais voltaram com "Ainda não entendi".
    - Se o comentário dele tem perguntas, responda cada uma, na ordem, repetindo a pergunta antes da resposta.
    - Toda resposta se explica sozinha, porque no "para responder" ele só vê a última fala dele e a da gerente. Formato: **Do que se trata · O que acontece hoje · Sua dúvida: "..." → resposta · O que você escolhe**.
    - Origem: "Um monte de texto e não consigo saber o que era para saber realmente" · "os relatorios continuam muito ruins e dificeis de entender" · "esse teste é totalmente inconslusivo para mim, não consigo ter visão clara do que o programa tentou fazer, ou de qual problema ele tentou reslver" · "nos para responder, não tem explicações sobre o que precisa ser respondido".

    **Depois de um "Ainda não entendi": mude o jeito, não só as palavras.**
    - Responda primeiro o que ele perguntou.
    - Faça a prova que faltou: print novo, exemplo de verdade, caso certo.
    - Confira no programa ou no print tudo o que afirmar (em 13/11, a gerente afirmou duas vezes que a palavra saía numa cor só, e o print mostrou que não).
    - Use o horário de verdade ao gravar na Central (em 13/11, um horário inventado sumiu com o comentário dele).
    - Se ele disse "não entendi" duas vezes na mesma pergunta, a gerente para e pergunta no chat qual parte não ficou clara.

    **Antes de mandar, a gerente confere a lista:**
    - (1) a primeira frase diz o que é e onde fica;
    - (2) nenhum código nem palavra de dentro;
    - (3) há print que prova, no modelo do girar;
    - (4) o exemplo é o caso real e o print foi aberto e conferido;
    - (5) há o caminho e se é defeito ou escolha;
    - (6) há "O que você escolhe" e o que muda em cada opção;
    - (7) está curto, responde o comentário dele e se explica sozinho.

    Pergunta de agente que não passa nessa lista volta para o agente antes de ir à Central.

**Obra de 26/10/2026 (D-014):** o Samuel mandou fazer a obra inteira (plano de 26/10, etapas 0 a 11) "até o final sem
pausas" e conferir tudo no fim. Durante essa obra **não valem** as regras de conferir cada item antes do próximo e de
uma fase por vez (§10, item 2; regras de 19/10): cada etapa é feita, testada e juntada no ramo `obra-2026-10-26`; nada
entra no `fase-1` antes da conferência final dele, item por item. Quando duas decisões dele se contradizem, vale a mais
recente.
