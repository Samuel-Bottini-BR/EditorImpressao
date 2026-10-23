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

### 22/10 (noite) — feito: a proteção e o botão (commits `5e361ce`, `7d71b15`)

**O que mudou.** Com o desentortar ligado numa página, o programa agora confere o resultado antes de usar: se a tinta
do texto sairia da página (P1) ou se entraria na página o que estava fora dela — fundo do scanner, sombra, página
vizinha (P2) —, a página sai **sem desentortar** (igual à de hoje) e vai para o "Para revisar" com um aviso e um botão.
O botão faz a opção C só naquela página: desentorta e deixa a página **crescer** até caber o texto.

**Os nomes na tela** (escolhidos por mim; seguro trocar em `core/analise.py`):
- título do aviso: **"Desentortar não usado"**;
- frase: "O desentortar empurrava o texto para fora da página, ou trazia o fundo de fora para dentro dela. Por isso a
  página saiu sem desentortar. Se quiser, desentorte aumentando a página até caber o texto.";
- botão: **"Desentortar aumentando a página"** (o texto que a gerente passou);
- no Ctrl+Z: "Desentortar aumentando a página N".

**Como mede (sem olhar a imagem, olhando uma "marca").** A DLL ganhou a versão 9: o mesmo desentortar redesenha também
uma marca (onde estava a tinta do texto e onde acabava o corte) com o mesmo modelo, numa página 10 mm maior de cada
lado. Recusa quando 3 ou mais pedaços de tinta de 1 mm caem fora do corte, ou quando mais de 2% da página veio de fora
do corte. Dentro do corte, a página com e sem essa medida é a mesma, ponto por ponto (conferido nas 14 páginas do
acervo, nos dois modos). Medido nas 14 páginas: Righetti 96 automático 22 pedaços (recusa); Cursus 151 automático 7
(recusa); "pelas margens" no Cursus 176 e Matemática 31/63/65/66: 14% a 30% de fora (recusa); as que saem certas:
0 ou 1 pedaço e até 0,7%.

**Desligado de fábrica: idêntico.** 96 de 96 somas (32 páginas do gabarito x 3 filtros) iguais às do `b8e9af7`
(`2.12/somas-v9.json`). Desligado, o preparo nem passa pelo código novo (só tira o aviso, se houver).

**Reversão (§4.7)** — `tests/test_desentortar_protecao.py`, rodados no código antigo (`177f711`, worktree de rascunho
no scratchpad): **os dois falharam lá** (`2.12/reversao-protecao-no-177f711.txt`) e passam aqui:
- `test_reversao_righetti_96_a_tinta_nao_sai_mais_da_pagina`: margem esquerda do texto 15 pontos no antigo (a tinta
  saía da página: "mente" -> "te") -> 173 aqui (a de hoje), com o aviso; com o botão a página cresce (1385 -> 1600
  pontos de largura) e "mente" fica inteiro;
- `test_reversao_cursus_176_pelas_margens_nao_entorta_mais_a_pagina`: tinta no lugar 0,70 no antigo -> 1,00 aqui.
Mais 13 testes no mesmo arquivo (a DLL nova, as medidas, o aviso entra e sai, o campo no arquivo). No PC, um arquivo
por vez: `test_desentortar_protecao` 15 passaram; `test_desentortar_scantailor` 40; `test_desentortar_na_tela` 5;
`test_modelos` 4; `test_detectar_regioes` 9.

**Arquivos:** `terceiros/scantailor-advanced/ligacao-ferramentas/desentortar.cpp` e `st_ferramentas.h` (DLL v9, só a
ligação: nada dentro das marcas "COPIADO SEM MUDANCA"), `core/nativo/st_ferramentas.dll`, `core/st_ferramentas.py`,
`core/desentortar_scantailor.py` (`preparar_no_corte`, a marca, as medidas, o aumento), `core/pipeline.py` (o aviso),
`core/analise.py` (o aviso), `modelos.py` (`ConfigPagina.desentortar_aumentar`, falso de fábrica), `ui/tela_conferir.py`
(o botão: `_desentortar_aumentando`), `ui/tarefas.py` (chave da prévia), testes. A DLL foi compilada na pasta de
rascunho `build-st-ferramentas-fase2-itens` (a `build-st-ferramentas` padrão está com o CMake de outra worktree, `misto`;
não mexi nela).

### Como isto se encaixa com o ramo do "Para revisar" (`fase2-para-revisar`, ainda não juntado)

Lá os avisos têm até três botões (`Alerta.outra_acao`, `terceira_acao`, lidos por `Alerta.botoes`) e a tela usa
`_aplicar_correcao(codigo, correcao)`; aqui (base `fase-1`) o aviso só tem um botão e a tela usa `_aplicar_sugestao`.
Na junção:
1. `core/analise.py`: no `DESENTORTAR_SAIU_SEM`, acrescentar o segundo botão `"está bom assim", "revisar"`, como os
   outros avisos de lá (o "Trazer de volta nesta página" tem o mesmo par).
2. `ui/tela_conferir.py` (`_aplicar_correcao` de lá): acrescentar
   `elif correcao == "desentortar_aumentando": self._desentortar_aumentando()` (o método vem deste ramo).
3. `core/pipeline.py`: `_anotar_desentortar_saiu_sem` segue o mesmo jeito do `_anotar_conferir`, que é igual nos dois
   ramos (põe na frente e volta `revisada` para falso; tira quando não vale). Lá o "está bom" por motivo
   (`alertas_aceitos`) funciona sem mudança: o código do aviso é um texto novo.
4. `core/avisos.py` de lá lista os avisos pelo código: nada a mudar (o título vem de `analise.descrever`).
5. DLL: os dois ramos não mexem na DLL ao mesmo tempo (o "Para revisar" não tem DLL nova); quem juntar com o
   `fase2-caixa-conteudo` (versão 4) recompila, como já estava anotado.

### Antes/depois pelo caminho inteiro, com a régua (todas as imagens abertas)

Pasta `relatorios/conferir/fase2-itens/2.12/protecao/` (fora do git; `<nome>-pagina.jpg`, `<nome>-recorte.jpg`,
`<nome>.json`). Script `relatorios/fase2-itens/scripts/rodada_2_12.py`. Livro novo, de fábrica: (girar) → (dividir) →
endireitar → cortar → desentortar → filtro. Colunas: Hoje · Antes da proteção (automático) · Agora automático · Agora
com o botão · Antes da proteção (pelas margens) · Agora pelas margens · Hoje P&B · Agora automático P&B; a coluna
"foi para o Para revisar" diz quando o aviso entrou.

Acervo:
- **Righetti 96, direita** (girar 270°, dividir): antes o automático cortava o começo das linhas; agora sai como hoje e
  vai para o "Para revisar"; com o botão a página cresce (1385 → 1600 pontos) e o texto fica inteiro.
- **Cursus 176**: antes o "pelas margens" entortava a página inteira, com cunha preta; agora sai como hoje, com aviso.
- **Cursus 151**: antes o automático mexia na página reta e cortava pedaços da beirada; agora sai como hoje, com aviso.
- **Matemática 65**: antes o "pelas margens" entortava a página e trazia a sombra do livro; agora sai como hoje, com
  aviso. O automático mexe pouco e passa (não empurra tinta para fora).
- **Marial 41**: página reta; nada muda em coluna nenhuma (a proteção não atrapalha).

"Livros para editar" (só lidos):
- **Destino do socialismo, p. 18 do PDF, direita** (scanner, dividir): antes o automático fazia uma página monstruosa;
  agora sai como hoje, com aviso. **O botão traz o monstro de volta** (ver a P5).
- **Razões do Integralismo, pp. 57 e 46** (foto): linhas curvas de verdade, mas o automático **não mexe** (igual a hoje).
  Na última coluna, "só para mostrar a causa", o mesmo caminho dizendo ao desentortar o tamanho certo da página
  (1100 DPI): na p. 57 as linhas saem retas pela régua (ver a P4). Na p. 46 o "pelas margens" foi para o "Para revisar".
- **Santiago Ramírez, De Analogia 4, p. 155, direita** (foto, dividir): linhas bem curvas; nada muda em coluna nenhuma.
- **Haegy, Manuel de Liturgie v2, p. 521** (foto): idem, nada muda.
- **Atanásio (aula 18), p. 8** (foto): idem, nada muda.

### A procura em "Livros para editar" (P3)

`relatorios/fase2-itens/scripts/procurar_curvas_livros_para_editar.py` (só lê; nada gravado na pasta do Samuel). A
pasta tem 10.550 PDFs (contando as subpastas); a procura mediu 3.255 (31%, 5 deram erro de leitura) em ~3 h e foi
parada por mim para não segurar o PC; as candidatas já bastavam. Resultado em
`relatorios/conferir/fase2-itens/2.12/procura-livros-para-editar/` (fora do git; `folha_0..2.jpg` são as miniaturas
das 24 mais curvas). Os livros usados, com o caminho:
- `D:\Livros para editar\2 - TEOLOGIA\Doutrina Social da Igreja\Corporativismo, Integralismo, Distributismo e Municipalismo à luz da DSI\22 - Olbiano de Mello\Razões do Integralismo [1935] - Olbiano de Mello.pdf` — pp. 57 e 46;
- `D:\Livros para editar\3 - TOMISMO\Santiago RamÃ_rez - De Analogia - 4.pdf` — p. 155 (direita);
- `D:\Livros para editar\2 - TEOLOGIA\Doutrina Social da Igreja\Corporativismo, Integralismo, Distributismo e Municipalismo à luz da DSI\9 - Octávio de Faria\Destino do socialismo - Octavio de faria.pdf` — p. 18 (direita);
- `D:\Livros para editar\2 - TEOLOGIA\Liturgia\d-Manuel de Liturgie et Ceremonial- v2- Haegy- 1922.pdf` — p. 521;
- `D:\Livros para editar\2 - TEOLOGIA\Patrologia\Patrística\aula_18_atanasio_de_alexandria_e_a_controversia_ar.pdf` — p. 8.

**Achado que importa:** quase todos os livros bem curvos dessa pasta são **fotos** (celular), e nos PDFs deles o tamanho
da página não é o de verdade (ex.: a página do Razões diz 115 cm de altura). O desentortar do ScanTailor reduz a
página para 200 DPI pelo tamanho que recebe; com o tamanho errado as letras ficam grandes demais para ele e ele não
acha linha nenhuma. Medido no Razões 57 (direto na ferramenta, só para achar a causa): com 300 DPI (o que o programa
diz) não acha curva; com ~1100 DPI acha e endireita. Outra coisa que atrapalha nas fotos: a caixa do texto
(`caixa_do_conteudo`, provisória até o 2.5) pega dedos, capa e sombra.

### Perguntas para o Samuel (novas, 22/10 noite)

**P4 — Livros fotografados: o desentortar não mexe, porque o PDF não diz o tamanho de verdade da página.**
Fotos: `protecao/razoes_p057-pagina.jpg` (última coluna: como fica com o tamanho certo; a régua vermelha mostra as
linhas retas), `protecao/ramirez_p155-direita-pagina.jpg`, `protecao/haegy2_p521-pagina.jpg`.
- (a) Deixar como está: nos livros fotografados o desentortar não faz nada (não estraga, mas não ajuda).
- (b) **(recomendo)** Como o ScanTailor faz quando o arquivo não diz o tamanho (a etapa "Fix DPI" dele): o livro
  ganha um campo "largura de verdade da página, em cm" (o Kaique mede com a régua). Muda a tela e o arquivo do
  projeto; vem vazio de fábrica (vazio = como hoje).
- (c) O programa adivinha o tamanho pela altura das letras. Não existe no ScanTailor (conta nossa) e pode errar.

**P5 — O botão "Desentortar aumentando a página" nem sempre ajuda.**
No Destino do socialismo 18 o automático faz uma página monstruosa; a proteção segura (a página sai como hoje), mas o
botão traz o monstro de volta, só maior (`protecao/destino_p018-direita-pagina.jpg`, 2ª e 4ª colunas). O mesmo vale
para o caso da P2 (o "pelas margens" que entorta): aumentar a página não desentorta nada. O Ctrl+Z desfaz.
- (a) Deixar assim: o botão aparece sempre no aviso; quem clica vê o resultado e desfaz se ficar ruim.
- (b) **(recomendo)** O botão só aparece quando o motivo foi a tinta empurrada para fora (o caso do Righetti); quando
  o motivo foi o fundo trazido para dentro (P2 e o Destino), o aviso fica só com "está bom assim" e a frase diz que
  o desentortar não deu certo nesta página.
- (c) O botão aparece sempre, mas depois de clicar a proteção confere de novo e, se a página continuar entortada,
  volta sozinha e avisa.

### Bugs para a Lista de bugs (não impedem; não consertei)

- 22/10/2026, filtro Preto e branco em página fotografada: a sombra da mão/da página vira mancha preta grande
  (`protecao/razoes_p057-pagina.jpg` e `protecao/atanasio_p008-pagina.jpg`, colunas "Hoje · Preto e branco").
  Não é do desentortar (sai igual com ele desligado).

### Ressalvas

- O limite da proteção (3 pedaços de 1 mm; 2% de fora) foi medido em 14 páginas do acervo e 6 de "Livros para editar";
  o Razões 57 com o tamanho certo ficou com 1,9% de fora e passou raspando. Se a P4 entrar, conferir o limite de novo.
- Com o botão, a página que cresce traz junto o que estava em volta no scan (no Righetti, um pedaço da faixa preta de
  cima e riscos da beirada) e fica de tamanho diferente das outras (o tamanho do livro na impressão é outro item).
- As zonas da aba Marcar continuam não acompanhando o desentortar (já anotado).
- Ligado, a proteção redesenha a marca: o desentortar ligado fica mais lento (Righetti 96: ~2 s → ~3 s por página).
  Desligado (de fábrica) não muda nada.

### Fim (22/10, noite) — entregue à gerente

- GitHub, suíte 39875580608 (ramo no último commit): 2188 passaram, 0 falharam, 75 pulados (o acervo); botões 221
  ações, 0 falhas.
- Velocidade 39872493254 (`177f711` x `5e361ce`): "igual (dentro do vai-e-vem)" — abrir 42,5 → 40,6 s; trocar de
  página 2,20 → 2,09 s; Mágico pro 44,4 → 43,3 s; Preto e branco 22,0 → 21,9 s.
- Abertas: P4 (livros fotografados, tamanho da página) e P5 (quando o botão aparece).

## 23/10/2026 — Implementador A: respostas P4 e P5 do Samuel

Respostas (Central, 23/10, pela gerente):
- **P4, fotos de celular:** "A — deixar como está" (+ "Mas eu vou poder tentar desentortar fotos né? a opção não vai
  sumir?" — sim). **Nada mudou:** a lista "Desentortar perto da lombada" continua em qualquer livro, foto ou scanner.
- **P5, o botão "Desentortar aumentando a página":** "C — Aparece sempre, mas depois do clique o programa confere de
  novo...", com o ajuste: "Mas o programa vai saber sempre que estiver deformada, o aviso deve perguntar e não fazer
  automaticamente."

### O que mudou (commits `a220c2d` e `2a42cfb`)

1. O botão aparece em toda página que a proteção segurou (já era assim).
2. Depois do clique, as mesmas duas medidas da proteção na página aumentada (`core/desentortar_scantailor.py`):
   **tinta saindo da página** = pedaços de tinta de 1 mm cortados pela beirada da página aumentada (3 ou mais =
   deformada); **fundo de fora entrando** = parte do lugar da página que veio de fora do corte (mais de 10% =
   deformada; a proteção usa 2%, mas com a página crescendo um pouco de papel de fora entra de propósito: Righetti
   5,7%, papel branco embaixo do rodapé).
3. Ainda deformada: a página **não volta sozinha**; entra o aviso novo, com dois botões.
4. Saiu boa: fica, sem aviso.
5. Ctrl+Z continua desfazendo (o "Desfazer" do aviso também é uma ação do desfazer).

Medido (23/10): Destino 18: 22 pedaços cortados, 39,6% de fora -> pergunta. Righetti 96: 0 e 5,7% -> sem pergunta.
Cursus 176 e Matemática 65 "pelas margens": 0 pedaços, 17,9% e 30,4% -> pergunta. Cursus 151 automático: 0 e 0% ->
sem pergunta.

**Rótulos (provisórios, sem emoji; seguro trocar em `core/analise.py`):**
- título do aviso: **"A página ainda saiu deformada"**;
- frase: "Mesmo aumentando a página, o desentortar deixou esta página deformada. Quer desfazer e voltar a página sem
  desentortar, como estava antes, ou manter assim?";
- botões: **"Desfazer"** (laranja; volta a página sem desentortar, como antes do clique, e o aviso "Desentortar não
  usado" volta) e **"Manter assim"** (é o "está certo" da faixa com outro nome: marca a página como conferida e ela
  fica aumentada);
- no Ctrl+Z: "Voltar a página N sem desentortar".

**Conserto que impedia a tarefa (§4.7):** nos prints da janela, o aviso "Desentortar não usado" aparecia e **sumia
antes do clique**. Causa: o desentortar do ScanTailor não acha as curvas em resolução baixa (Destino 18 e Righetti 96
a 100, 150 e 200 DPI: não mexe; a 300 mexe), e as prévias pequenas (cartões, miniaturas, prévia rápida) desenhavam a
página "sem estrago" e tiravam o aviso. Agora só o desenho na resolução do livro (`projeto.qualidade_dpi`) põe ou tira
os avisos do desentortar (`core/pipeline._julga_os_avisos_do_desentortar`). Reversão:
`test_reversao_previa_em_resolucao_baixa_nao_tira_os_avisos` e `test_reversao_destino_18_o_aviso_fica_depois_da_previa_rapida`
**falharam no `a220c2d`** (`2.12/reversao-previa-no-a220c2d.txt`) e passam aqui. Isso levou à pergunta P6 abaixo.

**Desligado de fábrica: idêntico.** 96 de 96 somas (32 páginas do gabarito x 3 filtros) iguais às do `b8e9af7`
(`2.12/somas-p5.json` = `2.8/somas-antigo.json`; rodado no `a220c2d`; o conserto seguinte só mexe no caminho com o
desentortar ligado).

**Testes (PC, um arquivo por vez):** `tests/test_desentortar_conferir_de_novo.py` 14 passaram (Destino 18: aparece a
pergunta; Righetti 96: não aparece; a faixa com "Desfazer" e "Manter assim"; o caminho na tela com o Ctrl+Z; as
medidas; as duas reversões); `test_desentortar_protecao` 15; `test_desentortar_scantailor` 40;
`test_desentortar_na_tela` 5; `test_paineis_na_tela` 22; `test_paineis` 33; `test_paginas_diferentes` 12;
`test_endireitar_no_programa` 15; `test_alerta_pb` 5.

### Fotos (todas abertas)

Antes/depois pelo caminho inteiro (`relatorios/fase2-itens/scripts/rodada_2_12_p5.py`; livro novo, de fábrica:
(girar) → (dividir) → endireitar → cortar → desentortar → filtro; régua vermelha), em
`relatorios/conferir/fase2-itens/2.12/p5/` (fora do git). Colunas: Hoje · Ligado (a proteção segura) · Com o botão ·
Depois de "Desfazer" (só quando a pergunta aparece) · Hoje P&B · Com o botão P&B.
- **Destino do socialismo 18, direita, automático:** a proteção segura; com o botão a página monstruosa volta e
  aparece "A página ainda saiu deformada"; "Desfazer" volta igual ao "Ligado".
- **Righetti 96, direita, automático:** com o botão a página cresce (1385 → 1600 pontos), o texto fica inteiro, sem
  pergunta.
- **Cursus 176, pelas margens:** com o botão a página continua entortada (cunha preta): aparece a pergunta.
- **Matemática 65, pelas margens:** com o botão a página continua entortada, com a sombra do livro: aparece a pergunta.
- **Cursus 151, automático:** com o botão a página fica um pouco maior (3238 → 3289 pontos de largura), reta, sem
  pergunta.
- **Marial 41, automático:** página reta; nenhum aviso em coluna nenhuma (o botão nem aparece).

Prints da janela de verdade, fora da tela (`relatorios/fase2-itens/scripts/janela_2_12_p5.py`, com a base do
verificador vlm22; toda janela nova vai para fora da tela antes de aparecer; cliques do Windows; 19 de 19 conferências
certas), em `relatorios/conferir/fase2-itens/2.12/p5/janela/`; cópias menores no git em
`relatorios/fase2-itens/2.12/fotos-p5/`:
- `destino18-0`: aba Endireitar, "Automático" escolhido, o aviso "Desentortar não usado" na faixa;
- `destino18-1`: aba Filtro, a proteção segurou, botão "Desentortar aumentando a página";
- `destino18-2`: depois do clique, **o aviso novo** com "Desfazer" e "Manter assim" (a página aumentada e deformada
  no cartão Original);
- `destino18-3`: depois de "Desfazer": voltam o aviso e a página de antes;
- `destino18-4`: depois do Ctrl+Z: volta a pergunta;
- `destino18-5`: depois de "Manter assim": a faixa calma, "1 de 2 conferidas", a página aumentada fica;
- `righetti96-0` e `-1`: o aviso "Desentortar não usado"; `righetti96-2`: depois do clique, sem pergunta, página maior.

### Perguntas para o Samuel (nova, 23/10)

**P6 — Na prévia de fábrica, o desentortar não aparece (nem os avisos dele).**
A tela de conferir desenha a página em resolução baixa para ser rápida (qualidade da prévia "Rápida", 110 DPI, a de
fábrica). Nessa resolução o desentortar do ScanTailor não acha as linhas curvas e **não mexe na página**; só na
resolução do livro (300 DPI, a do PDF final) ele mexe. Medido no Destino 18 e no Righetti 96: a 100, 150 e 200 DPI
nada muda; a 300 muda. Consequência: com a qualidade "Rápida", quem liga o desentortar vê a página como se ele não
existisse, e o aviso "Desentortar não usado" (com o botão) e o "A página ainda saiu deformada" só aparecem com a
qualidade "Alta" ou quando o livro é processado. Os prints acima foram feitos com a qualidade "Alta". E mesmo na
"Alta", os cartões Preto e branco, Melhorar e Mágico pro (que são pequenos) mostram a página sem desentortar
(`fotos-p5/destino18-2-pergunta.jpg`: o cartão Original deformado, os outros três retos).
Fotos: `fotos-p5/destino18-0-endireitar-automatico.jpg`, `fotos-p5/destino18-2-pergunta.jpg`,
`fotos-p5/destino_p018-direita-pagina.jpg`.
- (a) Deixar como está: na "Rápida" a pessoa não vê o desentortar; para ver, troca para "Alta".
- (b) **(recomendo)** Como o ScanTailor: o desentortar sempre é medido na resolução do livro, numa tarefa por trás
  (uns 3 a 8 s por página, só nas páginas com ele ligado), e a prévia rápida e os cartões usam essa medida, só
  reduzida. A página na tela fica igual à do PDF, e os avisos aparecem na hora. Desligado de fábrica: nada muda.
- (c) Ao ligar o desentortar numa página, o programa troca sozinho a qualidade da prévia para "Alta" enquanto ela
  estiver na tela.

### Bugs para a Lista de bugs (não impedem; não consertei)

- 23/10/2026, rodapé da tela de conferir ("N com dúvida"): fica atrasado quando o aviso entra ou sai pela prévia
  (`fotos-p5/destino18-1-protecao-segurou.jpg`: "0 com dúvida" com o aviso na faixa; `righetti96-2`: "1 com dúvida"
  sem aviso). A faixa, a miniatura e o sinal do painel acertam; só o texto do rodapé espera a próxima mudança.
- 23/10/2026, cartão "Preto e branco" do Righetti 96 (aba Filtro): sai quase em branco, só pontinhos
  (`fotos-p5/righetti96-2-sem-pergunta.jpg`), com o desentortar ligado ou não (print `righetti96-1`). Não é do
  desentortar.

### Ressalvas

- O limite novo (10% de fundo de fora, depois do botão) foi medido em 6 páginas; a mais perto do limite que sai boa é
  o Righetti (5,7%), a mais perto que sai deformada é o Cursus 176 (17,9%).
- Na junção com o `fase2-para-revisar`: lá os avisos têm até três botões (`Alerta.outra_acao`, `terceira_acao`); aqui
  o segundo botão é o campo novo `Alerta.confirmar` (o nome do "está certo"). Na junção, passar "Manter assim" para o
  jeito de lá e acrescentar `elif correcao == "desentortar_desfazer_aumento": self._desfazer_aumento_do_desentortar()`
  no `_aplicar_correcao` de lá.
- A assinatura da gravura no `pipeline` (zonas da aba Marcar) não leva o "aumentando a página" (a página aumentada
  muda de tamanho); já estava assim, não mexi.

### Rodando no GitHub (23/10, ~02:28 UTC)

- Velocidade 39889702446 (`7d71b15` x `2a42cfb`); suíte 39889712829 (ramo em `2a4ce76`). Ler uma vez, no fim.

### PAUSA (23/10, pedida pelo Samuel pela gerente) — estado exato

- Feito e no ramo: P5 (`a220c2d`), conserto dos avisos na prévia baixa (`2a42cfb`), ONDE-PAREI com fotos e P6 (`2a4ce76`).
- Suíte 39889712829 (ramo em `2a4ce76`): **2199 passaram, 0 falharam**, 78 pulados (o acervo); botões 221 ações, 0 falhas.
- Velocidade 39889702446 (`7d71b15` x `2a42cfb`): **ainda rodando** na pausa; falta só ler o veredito no topo da rodada.
- P6 está com o Samuel na Central: não mexer até a resposta.
- Nenhuma janela do programa aberta, nenhum processo meu rodando.
- Ao voltar: ler a rodada 39889702446, anotar aqui e entregar à gerente (o relatório já está nas seções de 23/10 acima).

## 23/10/2026 — Implementador A retoma: resposta P6 do Samuel

**Velocidade 39889702446 (`7d71b15` x `2a42cfb`), lida ao voltar:** "igual (dentro do vai-e-vem)" — abrir 39,2 → 39,9 s
(+1,7%); trocar de página 2,14 → 2,11 s; Mágico pro 44,6 → 44,1 s; Preto e branco 21,8 → 22,0 s.

**Resposta P6 (Samuel, 23/10, pela gerente): opção (b)** — "Como o ScanTailor: o desentortar sempre é medido na
resolução do livro (300 DPI), numa tarefa por trás (uns 3 a 8 s por página, só nas páginas com ele ligado), e a prévia
rápida e os cartões (Preto e branco, Melhorar, Mágico pro, Original) usam essa medida, só reduzida. A página na tela fica
igual à do PDF, e os avisos ('Desentortar não usado' com o botão, e 'A página ainda saiu deformada') aparecem na hora."
Desligado de fábrica: nada muda. A tela não trava (tarefa por trás; enquanto não termina, a página sem desentortar e um
sinal discreto em português simples). Reaproveitar a medida (não medir de novo a mesma página com os mesmos ajustes).

### O que mudou (commits `50a2826`, `6be1dbe`)

- **A medida** (`core/pipeline.py`, perto de `_desentortar_com_o_papel_em_volta`): a página desentortada na resolução do
  livro fica guardada na memória (`_DESENTORTADAS`), com o que a proteção decidiu. A chave é a do corte
  (`_chave_da_geometria`: arquivo, giro, divisão, corte, ângulo, ordem) + o modo + o "aumentando a página". Filtro e
  ajustes do filtro não entram (o desentortar vem antes do filtro): trocar de filtro não mede de novo. Limite de 400 MB
  (as mais antigas saem). Qualquer desenho menor (prévia "Rápida"/"Média", cartões, tela ampliada, miniaturas) usa essa
  página **reduzida**, com os avisos dela. Antes da medida, o desenho menor sai **sem desentortar** e nem chama a DLL
  (antes ela rodava à toa, ~1 s no fio da tela nos cartões) e não mexe nos avisos.
- **A tarefa por trás** (`ui/tarefas.py`, `_TarefaMedirDesentortar`, pool próprio de 1 fio): a tela pede a medida da
  página da vez (`GerenciadorPrevias.pedir_desentortar`); ao terminar, a chave da prévia e dos cartões muda sozinha
  (`estado_do_desentortar`) e a tela desenha de novo. Na qualidade "Alta" a própria prévia mede (não pede duas vezes).
- **O sinal** (barra de baixo, ao lado de "página N de M"): **"Desentortando esta página, um momento..."**, com o
  balão "A página na tela ainda está sem desentortar. Em alguns segundos ela aparece desentortada, igual vai sair no
  PDF." Só aparece com o desentortar ligado e a medida pendente. Texto escolhido por mim (seguro trocar:
  `TelaConferir.SINAL_DESENTORTANDO`).
- **Desligado (de fábrica):** o preparo nem passa pelo código novo (só a chave da prévia ganhou um pedaço que é vazio
  quando desligado).

**Testes** — `tests/test_desentortar_medida_por_tras.py` (6): antes da medida o desenho pequeno não desentorta nem mexe
nos avisos; uma medida só (a 300), reaproveitada a 110, a 300 e ao trocar o filtro, com o mesmo tamanho do desligado;
desligado nada roda; limite de tamanho; na tela o sinal aparece, a medida vem por trás e o sinal some (e voltar à página
não mede de novo); **reversão (§4.7)** Righetti 96 com o botão: a prévia rápida tem a largura proporcional à do PDF
(no `2a42cfb`: 0,3175 em vez de 0,367 — falhou lá, `2.12/reversao-p6-no-2a42cfb.txt`; passa aqui). No PC, um arquivo por
vez: `test_desentortar_medida_por_tras` 6; `test_desentortar_conferir_de_novo` 14; `test_desentortar_protecao` 15;
`test_desentortar_na_tela` 5.

**Desligado de fábrica: idêntico.** 96 de 96 somas (32 páginas do gabarito x 3 filtros) iguais às do `b8e9af7`
(`2.12/somas-p6.json` = `2.8/somas-antigo.json`, rodado no `6be1dbe`).

### Fotos antes/depois, prévia "Rápida" (todas abertas)

Janela de verdade, fora da tela (`relatorios/fase2-itens/scripts/janela_2_12_p6.py`, base do verificador vlm22; o "antes"
é o mesmo roteiro numa worktree de rascunho do `2a42cfb`, já removida). Qualidade da prévia "Rápida" (a de fábrica);
página da direita, "Dividir" ligado, livro novo de fábrica, aba Endireitar -> "Automático" -> aba Filtro. Originais em
`relatorios/conferir/fase2-itens/2.12/p6/antes|depois/` (fora do git); cópias menores no git em
`relatorios/fase2-itens/2.12/fotos-p6/` (`antes-*` e `depois-*`):
- `-0-logo-depois-de-ligar`: depois, a barra de baixo mostra "Desentortando esta página, um momento..." e a página
  sai sem desentortar; antes, nada.
- `-1-depois-da-medida`: **depois, o aviso "Desentortar não usado" com o botão aparece na "Rápida"** (Destino 18 e
  Righetti 96); antes, nunca aparecia (as conferências do roteiro: depois 12 de 12, antes 10 de 12 — as 2 que faltam
  são exatamente "apareceu o aviso na Rápida").
- `-2-depois-do-botao`: **Destino 18 depois: a página deformada na prévia e nos QUATRO cartões, com "A página ainda saiu
  deformada" (Desfazer / Manter assim)**; antes, a página e os cartões continuavam retos, sem aviso. Righetti 96 depois:
  a página aumentada, reta, sem pergunta, nos quatro cartões; antes, a página do tamanho de antes.
- De quebra: o cartão "Preto e branco" do Righetti 96, que saía quase em branco (bug anotado em 23/10, antes desta
  mudança, ver `antes-righetti96-2-depois-do-botao.jpg`), agora sai certo (o cartão é a página medida a 300 DPI,
  reduzida). Só observado com o desentortar ligado; desligado, o cartão é o de sempre (o bug continua na lista).

### Ressalvas

- Página com o filtro "Tirar o fundo": fica no caminho de antes (a medida não é guardada nem pedida por trás; a página
  desentortada lá é a folha sem o fundo). Na "Rápida" o desentortar continua sem aparecer nessas páginas.
- A medida é só da página da vez (não adianta as próximas): cada página com o desentortar ligado espera 3 a 8 s na
  primeira vez. Guardada só na memória, nesta sessão (fechar e abrir o livro mede de novo), até 400 MB.
- Na qualidade "Alta" a própria prévia mede (como antes); o sinal aparece até ela chegar.
- O rodapé "N com dúvida" continua atrasado (bug já anotado em 23/10; visto de novo em `depois-destino18-1`).

### Fim (23/10) — entregue à gerente

- GitHub, suíte 39902142935 (ramo em `6be1dbe`): **2204 passaram, 0 falharam**, 79 pulados (acervo e "Livros para
  editar"); botões 221 ações, 0 falhas.
- Velocidade 39902159919 (`2a42cfb` x `6be1dbe`): **"igual (dentro do vai-e-vem)"** — abrir 36,8 → 36,8 s; trocar de
  página 2,01 → 2,11 s (+5,4%, vai-e-vem 8,2%); Mágico pro 44,2 → 46,5 s (+5,2%, vai-e-vem 5,5%); Preto e branco 21,4 →
  22,0 s (+2,6%). Ressalva honesta: Mágico pro e trocar de página ficaram perto do limite do vai-e-vem. O caminho
  desligado (o que o teste mede) não mudou no código: o preparo desligado nem passa pelo código novo e a prova de
  fábrica deu 96 de 96 iguais; parece vai-e-vem da máquina, mas só a medida no PC no fim da fase decide.
- Perguntas abertas: nenhuma.
