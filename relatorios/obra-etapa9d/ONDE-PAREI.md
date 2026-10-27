# ONDE-PAREI — obra de 26/10/2026, etapa 9d: consertos de núcleo que sobraram

Implementador · ramo `obra-etapa9d-2026-10-26` (base `obra-2026-10-26` = `ad8df2b`, com as etapas 1-4, 9a, 9c, 10a,
10b) · worktree `.claude/worktrees/obra-etapa9d`. Obra D-014: até o fim sem pausas; o Samuel confere tudo no fim.
**Não mexo em `ui/`** (a etapa 5 está na tela): o que precisar de tela vai em "Trocas de tela para a gerente".

**Situação: EM ANDAMENTO** (começada em 27/10/2026).

## Decisões que esta tarefa precisa cumprir (do pedido da gerente e do Livro, `docs/plano/DECISOES.md`)

- **D-531** (escolha da gerente, pela regra "vale a mais recente": o defeito 4.5 "PDF pronto gigante", 23/10, é mais
  novo que a D-304, "o tamanho do arquivo depois não importa", 01/10): "**PDF menor sem perda visível:** página de
  cor/cinza em JPEG 92 (feito na 10b) **e** guardada com no máximo 2 vezes a resolução do scan nos livros de página
  grande. Página em 1 bit continua sem perda." Prova do Livro: "Antiphon 56 → PDF 2 a 4× menor que depois da 10b,
  diferença de imagem ≤ 3 tons, texto igual a olho".
- **D-532** (escolha da gerente): "**Gravura de fundo escuro (Palatino 70 e 74, fotos de retícula do Righetti) no Preto
  e branco sai em tons de cinza**, como as fotos, em vez de 1 bit." Prova: "Palatino 74 no Preto e branco → gravura em
  cinza sem chuvisco; texto da página continua preto e branco". Apoio: regra do Preto e branco de 30/09 (fotos e
  pinturas em tons de cinza, conferência 2, P1: "Cinza (tons de cinza): BOM").
- **D-528** (escolha da gerente): "**Ao dividir uma folha pela primeira vez, as marcações feitas na folha inteira vão
  para a metade em que estão** (hoje se perdem, como no Automático)." Prova: "Marcar uma gravura na metade direita da
  folha inteira, dividir → a marcação aparece na página da direita, no lugar certo". Substitui parte da D-498 ("as
  duas páginas herdam o filtro [...] mas não [...] a marcação").
- **D-027** (30/09): "essa é uma página que eu poderia simplesmente escolher a opção para virar uma folha branca, pois
  não tem nenhum conteúdo." + **D-227** ("eu poderia ir lá e apagar ou botar branco por cima") — item 4: valer também
  na página "Tirar o fundo" com o fundo já tirado (bug achado na 9c). **D-134**: o papel que a máquina marcou não muda
  a página.
- **Aviso de margem da impressão** (g11, 14/10: "o programa precisa avisar quando o corte deixar qualquer margem abaixo
  de 1 cm") — item 5: a frase não pode dizer "-2,2 cm" (ressalva da etapa 10a). **D-017** (13/10): "aumentar [...] não
  corta nada escondido" (o aviso "CORTADO" da 10a continua).
- **D-522** (Central, `pd-versos-em-branco`: "Juntar num aviso só do livro quando forem muitas"): "**Livro com muitas
  páginas em branco (versos): um aviso só do livro em vez de um por página.** 'Muitas' = 40% ou mais das páginas".
  Prova: "Livro com metade das páginas brancas → 1 aviso do livro e nenhum por página; livro com 3 brancas → 3 avisos".
  A frase e o lugar ficam para a etapa 7 (D-521).
- **D-497** (escolha da gerente): "**Página que fica branca depois de mudar a divisão ganha o aviso 'Parece em
  branco', a não ser que a pessoa já tenha dito 'está certo' nesse aviso daquela página** (o aviso que ela tirou não
  volta)." Núcleo aqui; a tela liga na etapa 7.
- **D-271 / D-288 / D-254 / D-474** ("Parece em branco": um aviso para cada coisa; título não é branco; menos de 10% das
  páginas no "Para revisar").
- **D-473** (tela e PDF da mesma conta) e **D-118** ("Eu quero que o papel saia branco, e o desenho também saia
  perfeito.").
- **CLAUDE.md** §3 (uma página por vez na memória), §4.7 (teste de reversão), §4.10 (caminho inteiro; só páginas que
  vão ser impressas), §5 (medir antes, uma mudança por vez, medir de novo), §9 (não desfazer o "magic color"), §11.
- **Regra fixa do pedido:** não trocar nada do ScanTailor (`core/nativo/*.dll`, `core/*_scantailor.py`) nem módulo
  inteiro que funciona.

## Andamento

| Item | Situação | Commit |
|---|---|---|
| 1. D-531 PDF menor (2× o scan) | a fazer | |
| 2. D-532 gravura de fundo escuro em cinza | a fazer | |
| 3. D-528 marcações ao dividir | a fazer | |
| 4. folha em branco no "Tirar o fundo" | a fazer | |
| 5. aviso de margem negativo | a fazer | |
| 6. D-522 aviso do livro (40%) | a fazer | |
| 7. D-497 "Parece em branco" depois da divisão | a fazer | |
