# Onde parei: Fase 2, itens que faltam, igual ao ScanTailor (implementador)

Pedido da gerente em 20/10/2026. Ramo `fase2-scantailor-itens-2026-10-19` (do `origin/fase-1` em `b8e9af7`),
worktree `D:\programas\EditorImpressao\.claude\worktrees\fase2-itens` (junções: `modelos`, `gabarito\paginas`,
`gabarito\scantailor-24-09` — nunca `Remove-Item -Recurse` nelas).

Regra (Samuel, 13/10): igual ao ScanTailor, ajustes de fábrica dele, desligado de fábrica quando muda a imagem.
Decisões já tomadas que valem aqui (conferência 10, 05/10, `relatorios/conferencia-samuel-2026-10-05-b.md`):
P8 (b) "Trazer os dez do ScanTailor como opções a mais"; P9 (a) caixinha por página "Letra clara em fundo escuro",
à mão; P10 (a) "letras com a cor delas" como opção desligada de fábrica.

Ordem (D1 de 02/10, depois a lista da gerente): 2.8 → 2.9 → 2.11 → 2.15 → 2.12 → 2.16 → 2.19 → 2.17.

## Estado por item

| Item | Estado | Commits | Rodada do GitHub |
|---|---|---|---|
| 2.8 preto e branco (os dez do ScanTailor) | **entregue à gerente** (falta verificador e Samuel) | `77e9446` (core), `34b3d0e` (tela), `b36b540` (script) | 39395632426: 2084 passaram, 0 falharam; botões 221 ações, 0 falhas |
| 2.9 claro no escuro | **entregue à gerente** | `4cec7a9` (core), `0f4ee58` (tela) | 39470347203: 2097 passaram, 0 falharam; botões 221 ações, 0 falhas |
| 2.11 cores | **entregue à gerente** | `b7dcc14`, `40a5ce1` (core), `02c2cea` (tela) | 39474481779: 2109 passaram, 0 falharam; botões 221, 0 falhas |
| 2.15 páginas diferentes | **entregue à gerente** (limiar de 1° da gerente) | `a8b1b2e`, `ebe017e` | 39553730620: 2124 passaram, 0 falharam; botões 221, 0 falhas |
| 2.12 desentortar | **em andamento** (21/10, novo implementador) | `e23f63e` (DLL v7), `fa8dd6c` (preparo), `81a950e` (tela) | suíte 39623234116 e velocidade 39623242157 disparadas 15:10 UTC (ler uma vez, no fim) |
| 2.16 todos os núcleos | não começado | | |
| 2.19 unidades e perfis | não começado | | |
| 2.17 iluminação e suavizar | não começado | | |

## Anotações

- `memoria/` ainda não existe no `fase-1` (20/10): nada a ler.
- Filtro de velocidade do GitHub (antes x depois) ainda **não existe**: outro agente está montando
  (`ONDE-PAREI-filtro-velocidade.md` no ramo `claude/list-server-files-gkos8v`, passo 1 de 9).
- A DLL `st_ferramentas` também muda no ramo `fase2-caixa-conteudo` (versão 4, não juntado). Aqui a versão
  pula para 5, para não brigar; quem juntar os dois recompila a DLL (`compilar_st_ferramentas.py`).

## 2.8 — o que foi feito e onde olhar

- Os dez jeitos do ScanTailor (Otsu, Sauvola, Wolf, Fox, Window, Bradley, Grad, EdgePlus, BlurDiv, EdgeDiv), com o
  código dele (`ligacao-ferramentas/saida.cpp`, `core/preto_e_branco_scantailor.py`), como opções a mais na lista
  "Algoritmo" da aba Filtro. De fábrica continua "Automático".
- Prova de "desligado de fábrica": `2.8/somas-antigo.json` (código `b8e9af7`) = `2.8/somas-novo.json` nas 32 páginas
  do gabarito × Original, Preto e branco, Melhorar (96 de 96 iguais, ponto a ponto).
- Antes/depois (Original · Hoje · Otsu ST · Sauvola ST · Wolf ST), 32 páginas + recorte ampliado de cada:
  `relatorios/conferir/fase2-itens/2.8/` (fora do git, só neste PC). Números por página: `2.8/numeros/`.
  Script: `scripts/rodada_gabarito.py` (uma página por processo; `scripts/rodar_todas.sh` roda as 32).
- Horas 13 falhou uma vez por falta de memória do PC (outros agentes); rodada de novo sozinha, deu certo.

## 2.9 — o que foi feito e onde olhar

- Caixinha por página "Letra clara em fundo escuro" (aba Filtro, bloco AJUSTE). Igual ao ScanTailor: inverte na
  entrada, caminho de sempre, inverte no fim. Desmarcada de fábrica.
- Prova de fábrica: `2.9/somas-novo.json` = `2.8/somas-antigo.json` (código `b8e9af7`), 96 de 96.
- Página de verdade achada no acervo (script `scripts/procurar_claro_no_escuro.py`, 14 livros lidos): só uma,
  Livro de Horas p. 187 (a lombada de couro escuro com "HEURES DE LOVIS XIV" dourado). Antes/depois em
  `relatorios/conferir/fase2-itens/2.9/` (fora do git), números em `2.9/numeros/`.
- Filtro de velocidade do GitHub (b8e9af7 x 0f4ee58): rodada 39470417724, disparada.

## 2.11 — o que foi feito e onde olhar

- "Letras com a cor delas" (só Preto e branco) e "Reduzir cores", por página, desmarcadas de fábrica
  (`core/cores_scantailor.py`, `st_ferramentas_cores` na DLL versão 6).
- Prova de fábrica: `2.11/somas-novo.json` = `2.8/somas-antigo.json`, 96 de 96.
- Antes/depois em 7 páginas com cor (Horas 13, 26, 27, 47; Graduale 221; Palatino 67; Escola 7):
  `relatorios/conferir/fase2-itens/2.11/` (fora do git); números em `2.11/numeros/`.
- Próximo: 2.15 (destacar páginas diferentes).

## Conserto pedido pela gerente (verificador do 2.8): falha do ScanTailor no erros.log

`ba5eefe`: os quatro "avisar uma vez" (preto e branco, endireitar, limpar pontinhos, cores do ScanTailor) gravam
com `registro.registrar_erro` (`st_ferramentas.anotar_no_erros_log`). Teste de reversão
`tests/test_falha_do_scantailor_vai_ao_erros_log.py`: 5 falharam no código antigo, 5 passam no novo.
Suíte GitHub 39478778828: 2114 passaram, 0 falharam; botões 221 ações, 0 falhas.

## Velocidade (filtro do GitHub, rodada 39470417724: `b8e9af7` x `0f4ee58` = 2.8 + 2.9)

Veredito "igual (dentro do vai-e-vem)": abrir 36,2 → 36,3 s; trocar de página 1,99 → 1,97 s; Mágico pro 43,9 → 42,5 s;
Preto e branco 20,9 → 20,9 s. O 2.11 (`02c2cea`) ainda não passou no filtro.

## PAUSA (20/10, ~15h no PC) — pedida pela gerente para a suíte no PC

Parei num ponto limpo: tudo commitado e enviado, nada rodando no PC. Ao retomar:
1. disparar o filtro de velocidade `b8e9af7` x último commit (cobre 2.11 e o conserto do log);
2. entregar o 2.11 à gerente (já pronto: ver a seção do 2.11);
3. seguir com o 2.15 (destacar páginas diferentes: DeviationProvider.h do ScanTailor).

## Retomada (21/10)

- Velocidade do 2.11 + conserto do log (39482416807, `b8e9af7` x `d490c61`): "igual" (abrir 60,4 → 60,6 s).
- Velocidade do 2.15 (39553741406, `d490c61` x `a8b1b2e`): disparada, resultado ainda não lido.

## 2.15 — o que foi feito e a pergunta

- `core/paginas_diferentes.py` (DeviationProvider.h em Python, fábrica do ScanTailor). Só o ângulo do endireitar:
  conteúdo (2.5) e margens (2.4) estão em `fase2-caixa-conteudo`, fora do `fase-1`; as contas deles já estão prontas.
- Aviso "Inclinação diferente das outras" posto na análise (livro novo); não muda imagem.
- Contagem (`2.15/livro1..5.json`): Boécio 9/50 (18%), Palatino 8/134 (6%), Siebmacher 8/134 (6%),
  Horas 15/191 (7,8%), Catecismo 33/199 (16,6%: páginas com só 0,4° a 0,9°, desvio do livro 0,28°).
- **Pergunta:** dois livros passam da regra "menos de 10% das páginas" (core/analise.py). No ScanTailor é só um
  asterisco; aqui vai para "Para revisar". Ver a entrega à gerente.

## 21/10, depois da decisão da gerente

- 2.15: mínimo de 1° da média (decisão da gerente, opção b), `ebe017e`. Antes x depois:
  `2.15/contagem-antes-depois.md` (Catecismo 33 → 0; Siebmacher 8 → 8, com as de 5°; Boécio 9 → 7 = 14%;
  Horas 15 → 6; Palatino 8 → 7). Suíte 39554612216: 2126 passaram, 0 falharam.
- Conserto dos cartões (bug do verificador do 2.9): `e49463c` (cartão com inverter e cores; chave com as três
  caixinhas; tela ampliada pela mesma função) e `e3c4d49` (cartão com o limpar pontinhos e o jeito de PB da
  página). Teste `tests/test_cartoes_seguem_as_caixinhas.py`. Prova em páginas de verdade (capa do "História
  do Direito Político Brasileiro" p. 1 e slide do "O meio ambiente hoje" p. 18):
  `relatorios/conferir/fase2-itens/conserto-cartoes/` (fora do git), cartão = página nos 3 filtros.
- Próximo: 2.12 (desentortar). Código do ScanTailor em
  `D:\programas\EditorImpressao-arquivos\ferramentas\scantailor-advanced-v1.2.1\src\dewarping` (5.073 linhas)
  + `OutputGenerator.cpp` 1532-1700, 2059-2105, 2608-2760; de fábrica desligado (`DewarpingOptions(OFF)`).

## Velocidade do 2.15 (rodada 39553741406, `d490c61` x `a8b1b2e`)

Veredito "igual (dentro do vai-e-vem)": abrir 61,3 → 61,4 s; trocar de página 4,64 → 4,32 s; Mágico pro 74,9 → 72,8 s;
Preto e branco 39,4 → 39,3 s. Suíte do conserto dos cartões (39562148188): 2131 passaram, 0 falharam; botões 221, 0 falhas.
O 2.12 ainda não começou no código (só a leitura de onde está o código do ScanTailor, ver acima).

## 2.12 — desentortar (retomado por outro implementador, 21/10)

- Parte 1 `e23f63e`: 79 arquivos do ScanTailor (todo `dewarping/`, `math/spfit`, `math/adiff` e o fecho dos
  `#include`) sem mudança, com soma; cola `ligacao-ferramentas/desentortar.cpp` (7 blocos copiados, conferidos
  por `tests/test_desentortar_scantailor.py`); DLL versão 7; `core/desentortar_scantailor.py`;
  `ConfigPagina.desentortar = "desligado"`. Modos: desligado (fábrica), automático, pelas margens. O MANUAL
  (malha) não veio. A `st_gravura` recompilada num rascunho (`ferramentasuild-st-gravura-fase2-desentortar`,
  fora do projeto, criado por mim) ainda compila; a guardada não foi tocada.
- Parte 2: ligado no fim de `_preparar_metade_e_geometria` (nas duas ordens) e na assinatura da gravura.
  Prova de fábrica: `2.12/somas-novo.json` = `2.8/somas-antigo.json` (código `b8e9af7`), 96 de 96.
- Ressalvas já sabidas: as zonas da aba Marcar não acompanham o desentortar; o "pelas margens" quase não mexe na
  página de mentira (ele usa as beiradas brancas, não as linhas).
- Tela `81a950e`: lista "Desentortar perto da lombada" no Propriedades do Endireitar (parte "Só nesta página",
  abaixo da "Conta"); chave do cache da prévia em `ui/tarefas.py`; linha acrescentada em
  `Botoes e funcoes para o layout.md`. Teste `tests/test_desentortar_na_tela.py`.
- GitHub: suíte 39623234116 (ramo, em `81a950e`) e velocidade 39623242157 (`25504fb` x `81a950e`), disparadas
  21/10 15:10 UTC. Ler o resultado UMA vez, no fim (o GitHub limita consultas).
- Em andamento: procura de páginas curvas no acervo (`scripts/procurar_paginas_curvas.py`, saída em
  `relatorios/conferir/fase2-itens/2.12/procura/`, fora do git), depois o antes/depois pelo caminho do programa.

## PAUSA do 2.12 (21/10, pedido do Samuel pela gerente) — onde parou exatamente

Feito e enviado: parte 1 `e23f63e` (DLL v7 + módulo + testes), parte 2 `fa8dd6c` (no preparo da página; prova de
fábrica 96 de 96 iguais ao `b8e9af7`), tela `81a950e` (lista no Propriedades do Endireitar), e o script
`rodada_gabarito.py` com `--item 2.12` (variantes: Original desligado / automático / pelas margens; Preto e branco
desligado / automático) — escrito, AINDA NÃO RODADO.

Rodando quando parei (deixado terminar): a procura de páginas curvas no acervo
(`scripts/procurar_paginas_curvas.py`, passo 5, saída `relatorios/conferir/fase2-itens/2.12/procura/achados.json` +
40 miniaturas antes|depois, fora do git).

Falta, nesta ordem:
1. Abrir as 40 miniaturas da procura e escolher 3 a 6 páginas curvas de verdade (e as R5: Graduale 221, Escola 7).
2. Antes/depois pelo caminho do programa: `rodada_gabarito.py <pid> --item 2.12 --pasta relatorios/conferir/fase2-itens/2.12/imagens`
   (gabarito) e, para as do acervo, copiar a página para um PDF de rascunho e usar `--pdf`. Abrir todas as imagens.
3. Ler UMA vez a suíte 39623234116 e a velocidade 39623242157 (`25504fb` x `81a950e`), disparadas 15:10 UTC.
4. Atualizar `memoria/itens/2.12.md`? (não: é da gerente) — entregar à gerente.

Ressalvas já sabidas: MANUAL (malha) não veio; as zonas da aba Marcar não acompanham o desentortar; o controle só
existe com "Endireitar" ligado no livro; ligado, o desentortar roda no fio da tela nos cartões/tela ampliada
(~1 s por página a 300 DPI na página de mentira); "pelas margens" quase não mexe na página de mentira. Pasta de
rascunho criada fora do projeto: `EditorImpressao-arquivoserramentasuild-st-gravura-fase2-desentortar`
(teste de compilação da st_gravura; não apaguei, regra 9).

Procura terminou (21/10): 828 páginas medidas, 40 miniaturas antes|depois em
`relatorios/conferir/fase2-itens/2.12/procura/` (fora do git), NÃO abertas ainda. As que mais mexeram: Righetti
p. 76, 106, 96 e Cursus philosophicus p. 176, 401, 186, 151, 166... A "diferença" muito alta (77 a 97) pode ser a
página inteira deslocada, e não curva: conferir a olho antes de escolher. Uma página deu "Faltou memória para
desentortar" (PC com outros agentes) — anotar como ressalva ou repetir sozinha. Nenhum processo meu ficou aberto.

## 22/10/2026 — Implementador A retoma o 2.12 (pedido da gerente) — PARADO numa escolha

**GitHub lido (uma vez):** suíte 39623234116 (ramo em `81a950e`): as 5 partes e os botões passaram (verde).
Velocidade 39623242157 (`25504fb` x `81a950e`): **"igual (dentro do vai-e-vem)"**.

**Desligado de fábrica sai idêntico:** somas de `ffa2463` x `2.8/somas-antigo.json` (código `b8e9af7`) em Escola 7,
Graduale 221 e Horas 13, nos três filtros: **9 de 9 iguais** (`saida_teste/2.12/somas-hoje.json`).

**A procura de 21/10 não existe mais no disco** (a pasta `relatorios/conferir/fase2-itens/2.12/procura/` não foi
achada; provavelmente o caminho perdeu as barras, como a pasta de compilação citada acima). E ela lia a página sem o
giro de 90° nem a divisão do programa: no Righetti (folha deitada) as miniaturas não valem.

**Antes/depois pelo caminho do programa** (`rodada_gabarito.py --item 2.12`; livro novo, ajustes de fábrica:
girar 90 → dividir → endireitar → cortar → desentortar → filtro; colunas Original · Hoje Original · Automático ·
Pelas margens · Hoje Preto e branco · Automático + Preto e branco). Imagens em
`relatorios/conferir/fase2-itens/2.12/imagens/` (fora do git), TODAS abertas:
- Graduale 221, Escola 7 (gabarito): Escola 7 sem mudança no automático (página reta: certo); Graduale 221 o
  automático desloca a página um pouco, nada curvo para endireitar.
- Cursus 151, 176, 401 (miolo, página única com a lombada à esquerda): o automático **empurra o texto e letras somem
  na beirada** (recorte do 151: começo das linhas cortado).
- Righetti: o programa NÃO gira nem divide esse livro sozinho (de fábrica livro novo não divide; o giro automático
  não pega). Para chegar à página que vai ser impressa, fiz o que o Kaique faria: PDF de rascunho girado 270° e
  "Dividir" ligado no livro (`scripts/rodada_trecho.py`, trecho das folhas 91-110). Folha 96 (`righetti_f096-*`):
  esquerda, o automático não acha curva (igual a hoje); **direita, o automático amplia o alto, achata o pé e corta
  o começo das linhas ("mente" → "nte")**. As imagens `righetti_p0xx-*` e `righettig_p0xx-*` (página deitada /
  página dupla sem dividir) NÃO valem como antes/depois (não é a página que vai ser impressa); ficam só como prova
  de que o desentortar estraga folha não dividida.

**A causa provável (achada, não consertada):**
1. Na Righetti 96 direita, com "lado = página única" o ScanTailor não acha curva e não mexe
   (`scripts/desentortar_lado_da_pagina.py`); com "lado = direita" a correção da beirada da lombada (código dele,
   sem mudança) monta curvas numa página quase reta e distorce. Limitar à caixa do conteúdo (sem a faixa preta do
   scanner) não mudou nada.
2. O ScanTailor "não só desenrola as linhas, também as estica nas partes curvas" (`DistortionModel::modelDomain`).
   Lá a página de saída é o conteúdo MAIS as margens do layout (~10 mm); aqui o desentortar vem depois do nosso corte
   rente (1 mm de folga), então o que estica sai da imagem: letras cortadas na beirada.

**A escolha que o ScanTailor não resolve** (por isso parei, regra da gerente): para não cortar letras, o desentortar
precisa de folga em volta antes de redesenhar — (a) dar uma margem branca antes e cortar de novo depois (a página
pode mudar de tamanho), ou (b) desentortar antes do corte e medir o corte na página já desentortada (muda a ordem do
preparo), ou (c) deixar como está, desligado de fábrica, com aviso de que pode cortar letras. Não decidi.

**Falta:** página curva DE VERDADE perto da lombada como exemplo bom (nenhuma das 8 que olhei é bem curva); depois da
escolha acima, o conserto e um teste de reversão com medida (ex.: nenhuma peça de tinta a menos de 1 mm da beirada
depois do desentortar).

## 22/10/2026 (tarde) — 2.12 refeito pela opção A do Samuel ("cortar uma vez só, no fim")

**Feito e enviado — `a44c668`:** DLL versão 8. O corte é medido como sempre e vira só a medida (`m_outRect`,
pelo `setPostCropArea` do próprio ScanTailor); a DLL lê a página endireitada inteira, com o papel do scan em volta,
e devolve a página já do tamanho do corte. `m_contentRect` = a caixa do conteúdo justa (o corte sem a folga de 1 mm,
`desentortar_scantailor.caixa_do_conteudo`). O endireitar depois do "pelas margens" gira com o papel em volta.
Desligado: o código de sempre, sem passo nenhum (`pipeline._desentortar_com_o_papel_em_volta` só roda ligado).

**Achado que importa (medido):** no Righetti 96 o que salvou foi a caixa do conteúdo justa; só o papel em volta com a
caixa = corte ainda ampliava o texto e cortava "mente" → "nte" (`saida_teste/2.12a/exp1_rg96.jpg` x `exp1_rg96_cd.jpg`,
fora do git). As duas coisas são o jeito do ScanTailor (`m_contentRect` e `m_outRect`), e as duas entraram.

**Reversão (§4.7):** `tests/test_desentortar_scantailor.py` — `test_reversao_pagina_reta_com_corte_rente_nao_mexe_nas_letras`
(0,971 no `8cb90a1` → 1,000) e `test_reversao_righetti_96_o_comeco_das_linhas_nao_some` (margem do texto 15 → 173
pontos; só com o acervo). Rodados no código antigo (worktree de rascunho `antigo-8cb90a1` no scratchpad): **os dois
falharam lá**; aqui 40 de 40 passam.

**Rodando:** somas de fábrica das 32 páginas (`2.12/somas-v8.json`, comparar com `2.8/somas-antigo.json`); procura de
páginas curvas (`scripts/procurar_linhas_curvas.py`); filtro de velocidade do GitHub 39841907268 (`8cb90a1` x `a44c668`).

**Falta:** antes/depois com régua (Righetti 96, Cursus 151 e as curvas achadas), rodada da suíte no GitHub, entrega.

**Depois (22/10, noite) — `177f711`:** a caixa do conteúdo passou a ser a da tinta dentro do corte
(`desentortar_scantailor.caixa_do_conteudo`), e não "o corte menos 1 mm": o corte do programa é muitas vezes a folha
inteira (Righetti, Marial) e "o corte menos 1 mm" destruía o Marial 498 (0,05 da tinta no lugar). Medido em seis
páginas (`saida_teste/2.12a/exp12.py`, fora do git): Marial 41 0,49 → 1,00; Cursus 176 0,97 → 1,00; Righetti 91
0,955 → 0,984; Cursus 151 0,966 → 0,962; Righetti 96 0,849 → 0,842 (igual); página de mentira 0,971 → 0,996.
Provisório até o 2.5 (o ContentBoxFinder do ScanTailor, em `fase2-ferramentas-2026-10-22`): quando juntar, a caixa
dele entra no lugar desta conta. Reversão agora: página de mentira (0,971 no `8cb90a1`) e **Marial 41** (0,493 no
`8cb90a1`); o teste do Righetti 96 saiu (ver a pergunta 1). Os dois falharam no código antigo; 40 de 40 passam aqui.

Fotos finais (todas abertas): `relatorios/conferir/fase2-itens/2.12/depois-do-conserto/` (fora do git).

### Perguntas para o Samuel

**P1 — Righetti 96: o começo das linhas ainda some no "automático". O que fazer?**
O conserto entrou (o desentortar lê a página com o papel em volta e corta uma vez, no fim), mas nessa página o
começo das linhas continua sumindo ("mente" → "te"). A causa não é mais o nosso corte: a página é reta, o automático
do ScanTailor inventa uma curva e amplia o texto. Fiz o ScanTailor de verdade (o código dele, com a caixa do texto
e as margens de fábrica dele, 10 mm dos lados e 5 mm em cima e embaixo) e ele corta igual:
`depois-do-conserto/righetti_p096-direita-como-o-scantailor-beirada.jpg` e `...-como-o-scantailor-pagina.jpg`.
- (a) Deixar como o ScanTailor: vem desligado de fábrica; quem liga numa página reta pode perder a beirada.
- (b) **(recomendo)** Proteção: se, depois de desentortar, houver tinta encostando na beirada do corte que antes não
  encostava, a página sai sem desentortar (como a coluna "Hoje") e vai para o "Para revisar" com o aviso "O
  desentortar empurrava o texto para fora; a página saiu sem ele". Não existe no ScanTailor.
- (c) A página cresce até caber o que o desentortar empurrou (muda o tamanho só dessa página).

**P2 — "Pelas margens" agora segue a beirada do papel no scan, e no Cursus 176 entortou a página inteira.**
Com o papel em volta (como o ScanTailor), o "pelas margens" procura a beirada de cima e de baixo da folha no scan
inteiro. Em página com fundo escuro, sombra da lombada ou tira da página vizinha ele entorta a página inteira, com
cunha preta: Cursus 176, Matemática 65 e 66 (`depois-do-conserto/cursus_p176-pagina.jpg`,
`matematica_p065-pagina.jpg`, `matematica_p066-pagina.jpg`, 4ª coluna). Antes do conserto ele quase não fazia nada.
- (a) Deixar como o ScanTailor (desligado de fábrica).
- (b) A mesma proteção da P1-(b) também para ele (mas a medida da P1 pode não pegar a página entortada).
- (c) **(recomendo)** Só o "pelas margens" volta a receber a página já cortada (sem papel em volta), como antes:
  quase não mexe, mas não estraga.

**P3 — Página curva de verdade para conferir.** Procurei no acervo inteiro (script
`scripts/procurar_linhas_curvas.py`, 2.900 páginas) e olhei as candidatas: não há página com as linhas **bem** curvas
perto da lombada. As que têm alguma curva: Matemática para vencer (pp. 31, 63, 65, 66: perto da lombada, na sombra)
e Marial (pp. 41, 201, 501, 701: curva pequena). O automático mexe pouco nas da Matemática e nada nas do Marial (não
acha curva que baste). Você tem um livro grosso escaneado aberto, com as linhas bem curvas, para eu testar?

### Fim (22/10, noite) — entregue à gerente

- GitHub suíte 39853809910 (ramo em `f75ddf1`): 2175 passaram, 0 falharam, 73 pulados; botões 221 ações, 0 falhas.
- Velocidade 39841907268 (`8cb90a1` x `a44c668`): "igual (dentro do vai-e-vem)". O `177f711` só muda o caminho
  ligado (desligado não passa por ele); não passou no filtro.
- Fábrica: 96 de 96 somas iguais ao `b8e9af7` no `a44c668` e no `177f711`.
- Fotos (todas abertas): `relatorios/conferir/fase2-itens/2.12/depois-do-conserto/` (fora do git), 14 páginas.
- Perguntas P1 a P3 acima, abertas.

## 22/10/2026 (noite) — Implementador A retoma o 2.12 com as respostas P1 a P3

Respostas do Samuel (22/10, pela gerente; `docs/plano/central/conferencias/perg-a.json`, `a-212-p1` a `a-212-p3`):
P1 "B — Proteção" (+ "Ainda vou poder selecionar a opção c para as paginas que entrarem para revisão?" — sim: botão
no aviso, a opção C só naquela página); P2 "B — A mesma proteção da pergunta anterior"; P3 "Na pasta livros para
editar, procure lá" (`D:\Livros para editar`, SÓ LEITURA).

Plano: (1) DLL v9: o mesmo desentortar redesenhado numa página maior (`crescer`) e uma "marca" (onde estava a tinta
e onde acabava o corte) redesenhada com o mesmo modelo, para medir; (2) proteção no `aplicar_no_corte`: tinta
empurrada para fora do corte ou o de fora do corte trazido para dentro -> sai sem desentortar + aviso no "Para
revisar"; (3) botão do aviso = opção C só na página (campo novo `ConfigPagina.desentortar_aumentar`);
(4) procura de páginas curvas em `D:\Livros para editar` (`scripts/procurar_curvas_livros_para_editar.py`,
rodando, saída fora do git em `relatorios/conferir/fase2-itens/2.12/procura-livros-para-editar/`).
