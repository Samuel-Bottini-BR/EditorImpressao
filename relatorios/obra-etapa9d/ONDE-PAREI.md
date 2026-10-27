# ONDE-PAREI — obra de 26/10/2026, etapa 9d: consertos de núcleo que sobraram

Implementador · ramo `obra-etapa9d-2026-10-26` (base `obra-2026-10-26` = `ad8df2b`, com as etapas 1-4, 9a, 9c, 10a,
10b) · worktree `.claude/worktrees/obra-etapa9d` · worktree de apoio (código antigo, só leitura, para o teste de
reversão): `.claude/worktrees/obra-etapa9d-antes` (`ad8df2b`, solta, com a junção `gabarito\paginas`; criada por mim —
**ao apagar, remover primeiro a junção** com `(Get-Item <junção>).Delete()`). Obra D-014. **Não mexi em `ui/`.**

**Situação: PRONTO PARA CONFERIR** (27/10/2026). Conferência: `relatorios/obra-etapa9d/conferencia/conferencia-etapa9d.html`
(também `.md` e `.pdf`; fotos em `conferencia/img/`). Falta: verificador separado, conferência do Samuel. Nada juntado.

## Mudanças de rumo no meio (mensagens da gerente, 27/10)

1. **Ordem do Samuel** (pela gerente): *"os agentes estão mudando coisas que eu já tinha definido, é só para fazer o que
   eu já tinha mandado"*. Daí: (a) **item 1 (D-531, 2× o scan) CANCELADO** — eu já tinha medido e escrito, sem commit;
   joguei fora (nada dele ficou no ramo); (b) **desfeito o JPEG 92 da etapa 10b** (D-304: "o tamanho do arquivo depois não
   importa"); (c) **itens 2 (D-532) e 6 (D-522, 40%) só como conta pronta e DESLIGADA**, sem mudar o que sai hoje, com
   pergunta para ele.
2. **Auditoria de 27/10:** desfeita a **D-496** da etapa 9c (contrariava a D-082).

## Decisões que esta tarefa precisa cumprir (palavras do Samuel e do Livro)

- **D-304** (01/10, P3): "Eu quero ter a opção 1.6, mas eu quero poder deixar como está também, o tamanho do arquivo
  depois não importa". **Ordem de 27/10:** "é só para fazer o que eu já tinha mandado".
- **D-082** (05/10, G4): "O do ScanTailor de fábrica; quando os dois discordarem mais de 0,3 grau, a página fica marcada
  'conferir'".
- **D-532** (escolha da gerente): "Gravura de fundo escuro (Palatino 70 e 74, fotos de retícula do Righetti) no Preto e
  branco sai em tons de cinza, como as fotos, em vez de 1 bit." → só conta desligada (ordem de 27/10).
- **D-528** (escolha da gerente): "Ao dividir uma folha pela primeira vez, as marcações feitas na folha inteira vão para
  a metade em que estão (hoje se perdem, como no Automático)."
- **D-027** (30/09): "essa é uma página que eu poderia simplesmente escolher a opção para virar uma folha branca, pois
  não tem nenhum conteúdo." · **D-227**: "eu poderia ir lá e apagar ou botar branco por cima" · **D-134**: o papel que a
  máquina marcou não muda a página.
- **Aviso de margem** (g11, 14/10): "o programa precisa avisar quando o corte deixar qualquer margem abaixo de 1 cm" ·
  **D-017**: "aumentar [...] não corta nada escondido".
- **D-522** (Central, `pd-versos-em-branco`): "Juntar num aviso só do livro quando forem muitas" ("muitas" = 40%,
  escolha da gerente) → só conta desligada.
- **D-497** (escolha da gerente): "Página que fica branca depois de mudar a divisão ganha o aviso 'Parece em branco', a
  não ser que a pessoa já tenha dito 'está certo' nesse aviso daquela página".
- **D-473** (tela e PDF da mesma conta), **D-118** ("o papel saia branco, e o desenho também saia perfeito"), **D-126**
  (papel dentro da gravura branco).
- CLAUDE.md §3, §4.7, §4.10, §5, §9, §11; regra fixa: nada do ScanTailor trocado (só **voltei** a `discordam()` de
  `core/endireitar_scantailor.py` ao que era antes da 9c).

## Como cumpri cada uma (causa → conserto → teste → medida)

| Item / decisão | Causa | Conserto | Prova (falha no `ad8df2b`, passa aqui) | Medida |
|---|---|---|---|---|
| **1. D-531** | — | **cancelado** (ordem de 27/10). Nada no ramo. | — | (medido antes do cancelamento, só para registro: Antiphon 56 Mágico pro 3,98 → 1,28 MB) |
| **JPEG 92 da 10b desfeito (D-304)** | A 10b gravava a página de tons em JPEG (`/DCTDecode`) | `core/pdf_io.py` volta ao de antes da 10b (zlib sem perda); comentário com o motivo | `test_etapa10b_imagem.py::test_d304_pagina_de_tons_vai_sem_perda` (página de tons lida do PDF = ponto a ponto a que entrou; falha no código da 10b) | os 4 testes que a 10b tinha relaxado voltaram à igualdade ponto a ponto: `test_gravar_pdf_sem_parar_a_janela` (de volta ao `ab38208`), `test_tirar_fundo_no_programa::test_pdf_final_sai_igual_a_previa`, `test_so_neste_pedaco_no_tirar_o_fundo::test_pdf_com_pedaco_sai_igual_a_previa`, `test_ajustar_pedaco_na_folha_girada::test_tirar_o_fundo_com_pedaco_na_folha_girada` — todos passam |
| **2. D-532 (desligada)** | No 1 bit o fundo manchado da gravura em madeira e a retícula da foto só saem como chuvisco | `filtros._e_gravura_escura_ou_reticula` + `GRAVURA_ESCURA_EM_CINZA = False`; em `_tipos_das_zonas`, só com a chave ligada, a zona de traço de fundo escuro (mediana < 0,665 do papel **e** alisada ≥ 37% abaixo de 0,6 do papel) ou de retícula (≥ 1,5 pecinhas escuras por quadradinho de 1%) vira "foto" (tons de cinza) | `test_d532_desligada_de_fabrica_nada_muda`, `test_d532_palatino_74_hoje_sai_em_1_bit` (guardas: hoje igual); com a chave ligada: `test_d532_ligada_*` (sintético; Palatino 74 e 70 viram cinza; Palatino 5 e 69 continuam 1 bit) | ligada: Palatino 74 84% da página em tons, 70 92%, Righetti 62 12%, 64 12%; Palatino 5, 69, Valadés 41, Pesel 51: continuam 1 bit. Medidas das zonas em `scripts/` (sonda) e na conferência |
| **3. D-528** | `dividir_a_mao.LIMPAR_AO_PARTIR` jogava fora a marcação ao partir a página | `zonas_na_folha.repartir_nas_metades` (cada zona vai para a metade onde está o centro dela, com a geometria da página inteira; a "folha em branco" vai para as duas) + `dividir_a_mao.metades_da_pagina(inteira, corte)`; vale no "dividir esta" e no Automático. Só a marcação **à mão** passa; a metade fica "provisória" e procura a da máquina de novo no tamanho do PDF | `test_reversao_d528_*` (à mão e Automático), `test_d528_*` (5) | Folha sintética: quadrado B "pintado de branco" na metade direita → no PDF, página da direita: B 0% escuro (antes 100%), C fora da marcação 100% escuro, A (esquerda) 100% |
| **4. folha em branco no "Tirar o fundo"** | a página sem o fundo ia por `pipeline._pedacos_na_pagina_sem_fundo`, que não branqueava o papel à mão | `pipeline._papel_a_mao_sem_fundo` (a mesma conta da 9c no Original), com a marcação que vale lá | `test_reversao_folha_em_branco_no_tirar_o_fundo_*` (2), `test_pintar_de_branco_no_tirar_o_fundo_so_na_area`; guarda `test_papel_da_maquina_nao_branqueia_a_pagina_sem_o_fundo` | Opus Majus 3 e 11, Palatino 5 (PDF de verdade): ponto mais escuro com "Deixar a folha em branco" 4–9 → 255 |
| **5. margem negativa** | `_avisos_de_margem` escrevia a distância negativa | "em cima nenhuma (o impresso passa da beirada do papel)" / "na costura nenhuma (o impresso passa da dobra)" | `test_reversao_aviso_de_margem_nunca_diz_numero_negativo`; guarda `test_aviso_de_margem_pequena_continua_com_o_numero` | livreto a 140%: sem número negativo |
| **6. D-522 (desligada)** | — | `analise.LIMIAR_DO_LIVRO = {EM_BRANCO: 0,40}` + `LIMIAR_DO_LIVRO_LIGADO = False`; `e_observacao_do_livro`. Desligada: 70% e a frase de antes, como hoje | `test_d522_desligada_de_fabrica_nada_muda` (5 de 10 brancas → 5 avisos, como hoje); ligada: `test_d522_ligada_*` (5 de 10 → 1 aviso do livro; 3 de 10 → 3 avisos; só o "em branco" tem 40%) | — |
| **7. D-497** | o aviso só era tirado (9c), nunca posto, depois de mudar a divisão | `pipeline._acertar_o_em_branco` (substitui o corpo de `_tirar_o_em_branco_falso`, que continua com o nome) + `precisa_medir_o_em_branco` + `medir_o_em_branco(doc, projeto, pagina)` para a tela. Mede só página de folha com a marca "mexida à mão" do Dividir, ainda não medida com a divisão de agora; não põe se "está certo" (alertas_aceitos), se a página está em branco/fora do livro, ou se já é aviso do livro | `test_reversao_d497_*`, `test_d497_*` (5) | Folha sintética: linha a 0,78 → a página da direita (só margem) ganha o aviso; "está certo" → linha ao meio (aviso sai) → linha a 0,8 → não volta |
| **D-082 / D-496 desfeita** | a 9c pôs "as duas a até 0,3° do reto não avisam" | `endireitar_scantailor.discordam` volta ao de antes da 9c (só a diferença > 0,3°) | `test_decisoes_nucleo.py::test_d082_perto_do_reto_tambem_avisa_*` (3 falham no código da 9c), `test_d082_ate_0_3_*`, `test_d082_*_longe_do_reto_*` | pela conta da 9c, o Boécio volta de 8 para 12 avisos (não medi de novo) |

## Somas "Desligado de fábrica" (32 páginas-gabarito × Original / Preto e branco / Melhorar, livro novo)

`relatorios/obra-etapa10b/scripts/somas_da_imagem.py` (a imagem que vai ao escritor do PDF), `ad8df2b` × ramo:
**96 de 96 somas iguais** (Original 32/32, Preto e branco 32/32, Melhorar 32/32). Nada muda na imagem de fábrica: D-532 e
D-522 estão desligadas; D-528, D-497 e o item 4 só agem com marcação à mão ou divisão à mão; o item 5 é texto de aviso.
(`_tmp/somas-antes.json` × `_tmp/somas-depois.json`, fora do git.)

O que muda no **arquivo** PDF (não na imagem): toda página de cor/cinza volta a ser guardada sem perda (D-304), então o
PDF lido de volta difere do `ad8df2b` em toda página de tons — é a volta ao que era antes da 10b, de propósito.

## Testes (no PC, um arquivo por vez, TEMP e `--basetemp` em `_tmp/`)

- `tests/test_decisoes_nucleo2.py` (novo): **27 passaram**. No código antigo (`ad8df2b`): **16 falham, 8 dão erro** (as
  chaves da D-522/D-532 não existem lá) **e 3 passam** (guardas: margem pequena com número, papel da máquina, a hachura
  sintética) — `_tmp/reversao.txt`.
- `test_decisoes` 28 · `test_decisoes_automatico` 24 · `test_decisoes_dividir` 19 · `test_decisoes_impressao` 22 ·
  `test_decisoes_nucleo` 38 · `test_decisoes_tela` 35 · `test_etapa10b_imagem` 23 · `test_etapa10a_nao_comer` 8 ·
  `test_trabalho_nao_se_perde` 82 · `test_core` 62 — **todos passam**.
- Também: `test_gravar_pdf_sem_parar_a_janela` 5, `test_so_neste_pedaco_no_tirar_o_fundo` 8,
  `test_ajustar_pedaco_na_folha_girada` 8, `test_tirar_fundo_no_programa` 54, `test_dividir_na_tela` 9,
  `test_zonas_na_folha` 25, `test_em_branco` 6, `test_revisar` 28, `test_avisos` 34, `test_reversao_para_revisar` 6,
  `test_para_revisar_na_tela` 25, `test_misto_consertos` 25, `test_endireitar_scantailor` 17,
  `test_endireitar_no_programa` 15 — todos passam.

## GitHub e velocidade

- **Rodada inteira `40590248124`** (no `5be7f0f`): partes 2, 3, 4 e 5 da suíte e "Botões e prints da janela real"
  **passaram**. Parte 1: **2 falhas, as mesmas que já falham no `obra-2026-10-26` sem esta etapa** (rodadas das etapas
  4 e 10b): `test_promessas::test_p085` (tique do menu Filtro, D-492, etapa 9b) e `::test_p127[menu/processar]`
  ("Antes de processar" pelo menu). 240 passaram, 7 xfail.
- **Filtro de velocidade `40590288221`** (`ad8df2b` × ramo): **ainda rodando na entrega** (disparado às 21:52 UTC, ~1h55;
  parei de acompanhar porque o limite de consultas da conta do GitHub estourou às 22:57 UTC). **A gerente lê o
  veredito no topo da rodada.** O que esperar: o Mágico pro/Melhorar de 10 páginas pode sair "parece mais lento" uns 5%
  — é a volta da gravação sem perda (zlib) que a ordem de 27/10 mandou (a etapa 10b tinha medido -5% a -7,5% com o
  JPEG); não é conta nova. As contas novas desta etapa não rodam no caminho de fábrica (D-532 e D-522 desligadas; D-497,
  D-528 e o item 4 só com divisão/marcação à mão).

## Perguntas para o Samuel (a gerente leva à Central)

1. **D-532 — gravura de fundo escuro no Preto e branco** (a conta está pronta e desligada; fotos na conferência, item 2):
   quer que a gravura em madeira de fundo escuro (Palatino 70, 71, 74, 75) e a foto impressa em pontinhos (Righetti 62,
   64) saiam em **tons de cinza** no Preto e branco, como as fotos já saem? Ou ficam em preto e branco puro, como hoje
   (com chuvisco)? *Recomendo tons de cinza: fica igual ao original e o texto da página continua preto e branco.* (O
   Palatino 69, mais claro, não entra na conta.)
2. **D-522 — quantas páginas em branco viram um aviso só do livro:** ele disse "Juntar num aviso só do livro quando forem
   muitas". Hoje o programa junta só com **70%** (regra antiga de todos os avisos). A gerente tinha escolhido **40%**
   (está pronto e desligado). Qual número? *Recomendo 40% (o livro de versos em branco, como o Egenloff com 49%, ganha
   um aviso só).* E a frase do aviso (hoje "quase todas as páginas parecem estar em branco") é da etapa 7.
3. **D-528 e D-497 também são escolhas da gerente (D-014), não dele.** Foram feitas e estão **ligadas** (a gerente só
   pediu desligadas a D-532 e a D-522). Se a regra de 27/10 vale para elas também: a D-528 (marcação à mão vai para a
   metade ao dividir) muda o que sai no PDF quando alguém marca a folha inteira e depois divide; a D-497 só mexe no aviso
   "Parece em branco" (e só no desenho grande; a tela liga na etapa 7). *Recomendo perguntar as duas; desligar cada uma
   é uma linha (posso fazer).*

## Trocas de tela para a gerente (não mexi em `ui/`)

- **D-497 (etapa 7):** depois de "dividir esta", "não dividir esta" ou mover a linha (em `ui/tela_conferir.py`, onde a
  ação é registrada), pedir por trás, para cada página da folha:
  `if pipeline.precisa_medir_o_em_branco(projeto, pagina): mudou = pipeline.medir_o_em_branco(doc, projeto, pagina)`
  (abre a folha a 150 DPI, uns décimos de segundo — fora do fio da tela, como `pedir_medida` em `ui/tarefas.py`) e, se
  `mudou`, redesenhar a lista do "Para revisar". Sem isso, a conta só roda no desenho do tamanho da análise ou maior
  (a "medida" por trás e o PDF).
- **D-522 / D-521 (etapa 7):** a observação do livro já aparece em `ui/tela_conferir.py` (`rotulo_observacoes`); o
  lugar novo (alto do "Para revisar" e livro aberto da tela inicial) é da etapa 7.

## Ressalvas

- **D-532 desligada:** nada muda hoje. Ligada: os limites foram medidos em 13 zonas de gravura de verdade (Palatino
  5, 68–75; Valadés 38, 41; Pesel 51; Righetti 62, 64; Horas 14, 26; Graduale 223); a margem entre "fundo escuro" e
  "traço" é pequena (mediana 0,63 × 0,70 do papel). Pode haver gravura de traço muito escura que vire cinza, ou o
  contrário (o Palatino 69 continua chuviscado).
- **D-528:** a zona que atravessa a linha vai inteira para a metade do centro dela (o pedaço do outro lado fica de fora,
  cortado pela beirada). A marcação da **máquina** não passa; a metade com marcação à mão mostra, na prévia pequena, só a
  marcação à mão até o desenho do tamanho do PDF procurar a gravura de novo (como toda marcação provisória). Página nunca
  desenhada (sem geometria anotada): conta aproximada (sem o corte e o giro da página inteira).
- **D-497:** a página de folha mexida à mão é medida de novo uma vez por sessão (ao reabrir o livro, se for branca e o
  aviso nunca foi aceito, ele aparece). A medida só roda no desenho de 142 DPI ou mais (a prévia de 110 não mede).
- **D-522:** com 40% ligado, a página em branco de um livro assim perde os botões por página ("Deixar em branco" /
  "Tirar do livro") — a decisão diz "um aviso só do livro em vez de um por página".
- **PDF sem perda:** o arquivo volta a ficar grande nos livros de página grande (Antiphon ~1,5 GB), como antes da 10b.
- **Pesel 51:** blocos pretos sobre o texto embaixo, no Preto e branco, já existem hoje (vistos nas fotos da D-532); não
  são desta etapa.
- **Velocidade:** contas novas fora do caminho de fábrica: D-532 e D-522 desligadas não custam nada; D-497 só em página
  de folha mexida no Dividir; item 4 só com papel marcado à mão; D-528 só ao dividir. A gravação do PDF volta a ser a de
  antes da 10b (zlib): o Mágico pro/Melhorar fica tão lento quanto antes da 10b (a 10b tinha medido ~5% mais rápido).

## Bugs para a Lista de bugs

- 27/10, Pesel 51 no Preto e branco: blocos pretos chapados sobre as linhas de texto embaixo da prancha
  (`relatorios/obra-etapa9d/conferencia/img/d532-pesel51.jpg`, as duas colunas).

## Commits (ramo `obra-etapa9d-2026-10-26`, com push)

`bffde6a` ONDE-PAREI inicial · `3bfb64a` item 5 · `e305881` item 4 · `6e9eea3` item 3 (D-528) · `ec95931` itens 6 e 7 ·
`9c48998` JPEG desfeito (D-304) · `44edf8d` D-522 desligada · `37c8a18` D-496 desfeita · `7e7890c` D-532 desligada ·
`9052272` conferência · `5be7f0f` Livro de decisões · (este) ONDE-PAREI final.
