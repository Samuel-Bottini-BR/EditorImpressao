# Obra 26/10, etapa 9c — consertos de núcleo (ONDE-PAREI)

Ramo `obra-etapa9c-2026-10-26` (base `obra-2026-10-26` = 39b7d8a). Worktree `.claude/worktrees/obra-etapa9c`.

## Decisões que esta tarefa precisa cumprir

- **D-027** (30/09/2026): "essa é uma página que eu poderia simplesmente escolher a opção para virar uma folha branca,
  pois não tem nenhum conteúdo." — promessa P-078.
- **D-227** (05/10/2026): "[...] eu poderia ir lá e apagar ou botar branco por cima" · prova do Livro: "Clicar numa área
  laranja e 'pintar de branco' → no PDF sai branca" — promessa P-075.
- **D-134** (29/09/2026): "Página sempre abre em 'Original', sem mexer. [...] sem mudança escondida." (o Original continua
  sendo a página como veio: só o papel marcado à mão vai a branco).
- **D-342** (05/10/2026): "o programa quando estiver pronto, ele vai ter que ser capaz de abrir arquivos de versões
  anteriores." (item 3: projeto ilegível não pode sumir calado).
- **D-271 / D-288 / D-254 / D-474** ("Parece em branco"): "Tem que ter um tipo de aviso para cada coisa [...]" ·
  Gladstone 18 "Está bom" (página com título não recebe "Parece em branco") · "menos de 10% das páginas são marcadas
  para revisão — o alerta não vira ruído" (item 4).
- **D-082** (05/10/2026): "O do ScanTailor de fábrica; quando os dois discordarem mais de 0,3 grau, a página fica marcada
  'conferir'" (item 5: página reta não avisa).
- **D-365** (18/07/2026): "Corrija TODOS os textos da interface para português correto" (item 6).
- **D-479** (26/10/2026): "o do Editor" / "a do Editor" em todo lugar onde aparece o jeito ou a conta do próprio
  programa (item 6).

## Andamento — os 7 itens feitos

| Item | Situação | Commit |
|---|---|---|
| 1. folha em branco / pintar de branco no Original | feito | 53066df |
| 2. nome de saída sem acento | feito | 89e7c11 |
| 3. projeto.json ilegível | feito no núcleo (a frase na tela: troca 1, abaixo) | c090db3 |
| 4. "Parece em branco" falso | feito | 0227496 |
| 5. "contas discordam" em página reta | feito | d27bc69 |
| 6. textos do núcleo | feito no núcleo (os que moram na tela: trocas 2 a 4) | caba682 |
| 7. "Menor que o corte" com números iguais | feito no núcleo (o texto do aviso: troca 5) | 91f1f06 |

## Item 1 — "Deixar a folha em branco" e "pintar de branco" no Original

**Causa.** `core/filtros.aplicar_filtro_com_selecao`, ramo do Original/Tirar o fundo: devolvia a página como veio com só
os pedaços de "só neste pedaço" por cima (`aplicar_so_os_pedacos`). O papel marcado à mão (a folha inteira do menu Marcar,
`ui/tela_conferir._folha_em_branco`, e a área de "pintar de branco", `core/editar_zonas.pintada_de_branco`) é uma região
`tipo=papel, origem=mao, filtro=""`, que nos outros filtros ia a branco, mas no Original era ignorada. Vale com e sem
"Limpar a folha" (sem ela, `pipeline._so_a_marcacao_a_mao` chama o mesmo ramo).

**Conserto.** `core/filtros._papel_a_mao_em_branco`: depois dos pedaços, o papel marcado À MÃO e sem filtro próprio vai a
branco. O papel que a máquina marcou continua sem mudar o Original (D-134). Sem esse papel, devolve o mesmo objeto
(página sem marcação sai idêntica, sem conta a mais).

**Provas.**
- `tests/test_decisoes_nucleo.py`: `test_d027_folha_em_branco_no_original_sai_branca[com/sem limpar]`,
  `test_d227_pintar_de_branco_no_original_sai_branco_so_na_area[com/sem limpar]`,
  `test_papel_que_a_maquina_marcou_nao_branqueia_o_original`. No código antigo: 4 falham, 1 passa (a de "máquina" é a
  guarda do lado de lá). No novo: 5 passam.
- Promessas: `pytest tests/test_promessas.py -k "p075 or p078 or p073"` → 4 passed (2 vezes). No código antigo P-075 e
  P-078 falham. Tirei o campo "defeito" das duas em `tests/promessas/promessas.md`.
- A prova P-075 tinha uma falta própria, escondida pelo defeito do PDF: o terceiro clique ("apagar a área") vinha antes
  de a página chegar ao editor e não escolhia nada. Pus a mesma espera do clique de cima
  (`aj.esperar(lambda: editor._pixmap is not None ...)`), em `tests/test_promessas.py`. Não é defeito do programa (o
  clique de verdade só existe com a página na tela).

**Ressalva.** A página em "Tirar o fundo" de que o fundo FOI tirado vai por `pipeline._pedacos_na_pagina_sem_fundo`, que
não passa por este ramo: ali "Deixar a folha em branco" ainda não branqueia a tinta. Não pedido; anotado como bug.

## Item 2 — nome do PDF sugerido sem acento

**Causa.** `modelos.nome_de_saida_sugerido` montava o nome com o filtro do livro como está na tela
(`core.filtros.NOMES_AMIGAVEIS`, "Mágico pro") e o nome do livro como veio; só o nome "para imprimir" passava por
`ui/dialogo_impressao.sem_acento` (lista única 5.15).

**Conserto.** `modelos.sem_acento` (a mesma conta, no núcleo); o nome inteiro passa por ela:
"Ofício da Imaculada Conceição - magico pro.pdf" → "Oficio da Imaculada Conceicao - magico pro.pdf".

**Provas.** `test_nome_de_saida_sugerido_sai_sem_acento` (falha no antigo, passa no novo). Em `tests/test_core.py`,
`test_nome_de_saida_sugerido_descreve_o_que_foi_feito` ganhou o caso "Mágico pro" → "magico pro" (as linhas ~713-731
não esperavam acento, mas também não cobriam o caso).

## Item 3 — projeto.json ilegível

**Causa.** `projetos.carregar_estado` devolvia `None` tanto para "não há projeto" quanto para "não deu para ler". A
janela (`_analise_pronta`) recomeçava a conferência; a cópia "antigo" era feita, mas `paginas_perdidas` ficava 0 (o
salvo era None) e **nenhum aviso aparecia**.

**Conserto (núcleo).** `projetos.ler_estado(resumo) -> EstadoLido(projeto, ilegivel, copia)`, com `.aviso` (a frase):
"Não consegui ler o trabalho salvo deste livro; guardei uma cópia em:" + o caminho (ou "..., e não consegui guardar
uma cópia dele."). A cópia é `projeto.estragado-<data>.json`, ao lado; o original nunca é apagado nem mudado; ler várias
vezes o mesmo arquivo estragado guarda uma cópia só (a janela lê 2 a 3 vezes ao abrir). `carregar_estado` passa por
ela, então a cópia já é guardada antes de a tela ser ligada. Ilegível = não é JSON, não é dicionário,
`Projeto.de_dicionario` não entende (TypeError/ValueError/AttributeError/KeyError), ou erro de disco.

**Provas.** `test_d342_projeto_ilegivel_guarda_a_copia_e_avisa[json_quebrado|campos_errados|nao_e_um_projeto]`,
`test_projeto_ilegivel_lido_varias_vezes_guarda_uma_copia_so`, `test_projeto_legivel_ou_ausente_nao_avisa` (no antigo
falham: a função não existia). `tests/test_trabalho_nao_se_perde.py` 82 passed; `tests/test_projetos.py` 24 passed.

## Item 4 — "Parece em branco" falso em página com texto

**Causa (achada no livro de verdade, só lido; as 8 primeiras folhas copiadas para `_tmp/`).** O aviso é decidido **uma
vez, na análise**, na metade que a análise dividiu (`pipeline._analisar_a_folha`). No "La vida eterna" o ScanTailor
divide as folhas 4 e 5 a **10%** (na linha escura da beirada esquerda; a folha ganha "lombada incerta"): as "páginas"
7 e 9 da análise eram tiras de margem de 177 pontos, sem texto, e ganharam "Parece em branco" — exatamente as páginas
2, 7 e 9 do print do Kaique. No print dele (s1-06, s1-07) a linha da folha 4 está no meio (~0,55): com a divisão
acertada a página 7 virou a página de texto "8", e **nada media o aviso de novo**.
Achado junto: o verso branco de verdade da folha 5 (a página 9 com a divisão certa) tem 0,59% de "tinta forte", toda
na beirada do livro (uma linha comprida embaixo e outra do lado); por isso a conta não o daria como branco.

**Conserto.**
1. `core/pipeline._tirar_o_em_branco_falso` (chamado em `renderizar_pagina`, a prévia): na página com o aviso, mede de
   novo com a MESMA conta da análise, na MESMA etapa (girada e dividida, sem corte nem endireitar:
   `preparar_para_recorte`) e na MESMA escala (150 DPI; o desenho maior é reduzido; o de 55 DPI do arrasto não mede).
   Com conteúdo, o aviso sai. **Só tira, nunca põe** (o aviso que a pessoa tirou não volta; ver pergunta 2).
2. `core/analise.parece_em_branco`: linha reta comprida (mais de 15% do miolo, um pouco torta) não conta como conteúdo
   (`_sem_as_linhas_compridas`). Só é procurada quando a tinta forte fica entre 0,05% e 1% (as páginas com conteúdo
   do estudo têm 0,99% ou mais): nenhuma conta a mais nas páginas escritas.

**Provas.**
- `test_d271_parece_em_branco_sai_quando_a_divisao_muda_e_a_pagina_tem_texto` (falha no antigo).
- `test_parece_em_branco_continua_na_pagina_branca_de_verdade` (150, 300 e 55 DPI; a guarda, passa nos dois).
- `test_parece_em_branco_nao_conta_a_beirada_do_livro_como_conteudo` (página branca com as duas linhas = branca; com
  texto ou com o título "DA ORACAO" = não; falha no antigo).
- `test_la_vida_eterna_pagina_7_com_texto_perde_o_aviso_e_as_brancas_ficam` (livro de verdade, só lido; pula se não
  estiver no PC): análise de fábrica → avisos nas páginas [2, 7, 9]; divisão das folhas 4 e 5 a 0,55 → [2, 9]. Falha
  no antigo.
- As 67 páginas do estudo do "Para revisar" (`EditorImpressao-arquivos/revisar-decisoes-trabalho/paginas`, só lidas):
  **nenhuma** muda de resposta (Egenloff 12 continua branca; Gladstone 18, Rariora 8 e ljs47 26 continuam não).
- `test_em_branco` 6, `test_revisar` 28, `test_avisos` 34, `test_reversao_para_revisar` 6,
  `test_para_revisar_na_tela` 25 — passaram.

## Item 5 — "Endireitar: as contas discordam" em página reta

**Causa.** `core/endireitar_scantailor.discordam` só olhava a diferença (> 0,3°): uma conta +0,25 e a outra −0,1 (a
página reta para as duas) dava aviso. No Boécio (cópia de teste, 50 páginas, só lida) eram 4 dos 12 avisos.

**Conserto.** `ANGULO_QUASE_ZERO = LIMITE_DA_DISCORDANCIA` (0,3°, a tolerância da própria D-082): as duas contas a no
máximo 0,3° do reto → não discordam. Boécio: 12 avisos → 8 (com 0,5°: 6; com 0,7°: 5; ver pergunta 1). Mexi só em
`discordam()`, nada das funções de geometria de `core/pipeline.py`.

**Provas.** `test_d082_pagina_reta_nas_duas_contas_nao_avisa` (4 casos; 3 falham no antigo — o 0,3 × 0,0 já não
avisava), `test_d082_contas_que_discordam_de_verdade_continuam_avisando` (−2,2 × −0,25 etc.).
`test_endireitar_scantailor` 13 passed/4 pulados, `test_endireitar_no_programa` 15 passed.

## Item 6 — textos do núcleo que aparecem na tela

**Feito no núcleo:**
- `core/dividir_scantailor.NOMES_DOS_JEITOS`: "o do programa" → "o do Editor"; `core/endireitar_scantailor`: "a do
  programa" → "a do Editor" (D-479). A frase-resumo (`pipeline.resumo_em_portugues`) passa a dizer "(jeito: o do Editor)".
- `core/girar.descricao_do_giro` (Histórico e "Desfazer: ..."): "(1 folhas)" → "(1 folha)", "virada" no singular, "a
  única folha par/ímpar".
- `core/camadas.py` (explicação do "Tirar o fundo"): "1 figura(s)" / "2 delas é" → singular e plural certos.
- `core/cadernos.conferir_sequencia`: "Nao ha paginas para conferir." → "Não há páginas para conferir."
- "aba Marcar"/"aba Bordas": não há mais em texto do núcleo (só em comentários). Varri as frases do núcleo por palavras
  sem acento (`_tmp/textos.py`): as outras achadas são do log técnico (`erros.log`), não da tela.

**Provas.** `test_d479_o_jeito_do_proprio_programa_se_chama_o_do_editor`, `test_d479_resumo_do_livro_diz_o_do_editor`,
`test_textos_com_singular_no_1_e_acento` (os 3 falham no antigo). `test_girar` 53, `test_cadernos` 28,
`test_camadas` 64 (26 pulados), `test_dividir_na_tela` 9, `test_endireitar_na_tela` 5, `test_girar_na_tela` 22.

**Os que moram na tela** ("1 foram apagadas", "página(s)", "ação(ões)"): trocas 2 e 3, abaixo.

## Item 7 — "Menor que o corte" com os dois números iguais

**Causa.** A janela "Tamanho da folha" abre com os campos no tamanho do corte **arredondado às casas da unidade**
(`core.unidades.CASAS`: 13,944 cm → 13,94; em polegadas o passo é 0,0254 cm), e `core/folha.tamanho_da_folha_cabe`
exigia folga de só 0,001 cm: o arredondamento para baixo já virava "menor que o corte". O aviso escreve o corte com 1
casa ("13,9 × 20,0") e o campo mostra 13,94 — números iguais na tela (Lista de bugs de 02/10).

**Conserto.** A folga padrão passa a ser meio passo do campo mais grosso (`FOLGA_DO_ARREDONDAMENTO_CM`, ~0,013 cm,
invisível na impressão). Vale para a janela e para o aviso `FOLHA_MENOR_QUE_O_RECORTE` (a mesma função).

**Provas.** `test_folha_do_tamanho_do_corte_nao_avisa_menor_que_o_corte` (3 cortes × cm/mm/pol; 3 falham no antigo),
`test_folha_menor_de_verdade_continua_avisando` (1 mm menor continua avisando). `test_folha` 20,
`test_dialogo_tamanho_da_folha` 5, `test_unidades_e_perfis` 9.

## Trocas pendentes para a gerente aplicar na junção

**Troca 1 — `ui/janela_principal.py`, `_analise_pronta` (item 3, a frase na tela).** Hoje (linha ~1067):

```python
        if self.resumo is not None:
            salvo = projetos.carregar_estado(self.resumo)
```
trocar por:
```python
        ilegivel = ""             # etapa 9c: o projeto.json que nao deu para ler (projetos.ler_estado)
        if self.resumo is not None:
            lido = projetos.ler_estado(self.resumo)
            salvo = lido.projeto
            ilegivel = lido.aviso
```
e na cadeia de avisos do fim (linha ~1200), logo depois do bloco `if self.acoes.linhas_perdidas:` e antes do
`elif paginas_perdidas:`:
```python
        elif ilegivel:
            self.avisar(ilegivel)
```
(A cópia "projeto.antigo-<data>.json" que a janela já faz continua; "projeto.estragado-<data>.json" é a do arquivo
estragado em si. As duas ficam; nada é apagado.)

**Troca 2 — `ui/janela_confirmar.py`** (não estava na lista de "não mexa", mas é tela): em `_frase_do_livro`
(linhas 169-171), "1 foram apagadas":
```python
        frase = ("1 página vai para o PDF" if len(paginas) == 1
                 else f"{len(paginas)} páginas vão para o PDF")
        if apagadas:
            frase += (", e 1 foi apagada" if apagadas == 1 else f", e {apagadas} foram apagadas")
```
e na linha 200, `f"Ainda há <b>{faltam} página(s)</b> que você não conferiu. "` por:
```python
                ("Ainda há <b>1 página</b> que você não conferiu. " if faltam == 1 else
                 f"Ainda há <b>{faltam} páginas</b> que você não conferiu. ")
```

**Troca 3 — `ui/janela_principal.py` linha ~1203, "ação(ões)":**
```python
            perdidas = self.acoes.linhas_perdidas
            self.avisar(
                "O computador foi desligado no meio da última gravação, e "
                + ("1 ação do fim se perdeu. " if perdidas == 1
                   else f"{perdidas} ações do fim se perderam. ")
                + "O resto do trabalho está aqui.")
```

**Troca 4 — `ui/tela_opcoes.py`, `_com_o_nome_do_editor`:** com o núcleo dizendo "o do Editor", a função troca o
texto pelo mesmo; pode sair (com a chamada). Em `ui/widgets/paineis.py`, `nome_da_conta` e `nome_do_jeito_de_dividir`,
o caso especial de `JEITO_PROGRAMA` também pode sair (opcional; hoje dão o mesmo texto).

**Troca 5 — `ui/dialogo_tamanho_da_folha.py`, `_conferir_se_cabe` (item 7):** o aviso escreve o corte com 1 casa e o
campo tem 2; para os números baterem com o campo:
```python
            f"Esse tamanho é menor que o corte que você já fez "
            f"({unidades.texto(self._largura_recorte_cm, self.unidade)} × "
            f"{unidades.texto(self._altura_recorte_cm, self.unidade)}) - "
            "não vou mudar o seu corte, mas ele não vai caber inteiro na folha."
```
(Opcional: `ui/dialogo_impressao.sem_acento` pode virar `from modelos import sem_acento`.)

## Perguntas para o Samuel (a gerente leva à Central)

1. **"Quase reto" no aviso das contas (item 5).** Usei 0,3 grau (a mesma tolerância da D-082): se as duas contas dão a
   página a no máximo 0,3° do reto, não avisa. No Boécio: 12 avisos → 8. Com 0,5°: 6; com 0,7°: 5. Fica 0,3?
2. **Página que fica em branco DEPOIS de mudar a divisão (item 4).** Hoje o "Parece em branco" só SAI quando a página
   passa a ter texto; nunca é POSTO de novo (para o aviso que a pessoa tirou não voltar). Quer que a página que ficou
   branca depois de mexer na linha ganhe o aviso?

## Bugs para a Lista de bugs

- **27/10/2026 — Dividir do ScanTailor erra no "La vida eterna"** (folhas 4 e 5): divide a 10% da largura, na linha
  vertical escura da beirada esquerda; a página da esquerda vira uma tira de 177 pontos. A folha ganha "lombada
  incerta", mas o PDF sai assim se ninguém arrastar a linha. O "jeito do Editor" dá 0,527 e 0,48. Script:
  `_tmp/vida2.py`. Dono sugerido: quem cuida do Dividir (geometria).
- **27/10/2026 — "Deixar a folha em branco" numa página "Tirar o fundo" de que o fundo FOI tirado:** essa página vai
  por `pipeline._pedacos_na_pagina_sem_fundo`, que não passa pelo conserto do item 1; a tinta continua. Não testado.

## Como cumpri cada decisão

| Decisão | Como | Prova |
|---|---|---|
| D-027 | folha marcada inteira como papel (à mão) sai branca no Original, com e sem "Limpar a folha" | `test_d027_*` (2), P-078 |
| D-227 | área "pintada de branco" sai branca no Original; o resto fica como veio | `test_d227_*` (2), P-075 |
| D-134 | o papel que a máquina marcou não muda o Original | `test_papel_que_a_maquina_marcou_nao_branqueia_o_original` |
| D-342 | projeto ilegível: cópia guardada + sinal com a frase (na tela: troca 1) | `test_d342_*`, `test_projeto_ilegivel_*` |
| D-271 / D-288 | página com texto perde o "Parece em branco" falso; a branca de verdade fica; título não é branco | `test_d271_*`, `test_parece_em_branco_*`, `test_la_vida_eterna_*` |
| D-254 / D-474 | menos aviso falso; as 67 páginas do estudo sem mudança | `_tmp/estudo.py` |
| D-082 | diferença > 0,3° continua avisando, menos com as duas contas dando a página reta | `test_d082_*` (8 casos) |
| D-365 | textos do núcleo com acento e singular/plural | `test_textos_com_singular_no_1_e_acento` |
| D-479 | "o do Editor" / "a do Editor" no núcleo | `test_d479_*` (2) |

Coluna "Situação" do Livro atualizada em D-027, D-227, D-082, D-271, D-342, D-479.

## Rodada final (um arquivo por vez, no PC, na worktree, TEMP em `_tmp/`)

```
.venv\Scripts\python.exe -m pytest tests\test_decisoes_nucleo.py -q        -> 36 passed
.venv\Scripts\python.exe -m pytest tests\test_core.py -q                   -> 62 passed
.venv\Scripts\python.exe -m pytest tests\test_trabalho_nao_se_perde.py -q  -> 82 passed (2:44)
.venv\Scripts\python.exe -m pytest tests\test_promessas.py -q -k "p075 or p078 or p073" -> 4 passed
```
Suíte inteira no Windows do GitHub: rodada 40525179198 (resultado abaixo).

**Velocidade.** Não medi (regra de 19/10: a medida é o filtro do GitHub, pela gerente). O que entra a mais: o item 4
só roda na prévia de página com o aviso "Parece em branco" e, na análise, só em página com 0,05% a 1% de tinta forte;
o item 1 só em página com papel marcado à mão.

`_tmp/` (na worktree, fora do git) tem os scripts de medida e as imagens do "La vida eterna"; criado por mim, pode ser
apagado.

## Resultado no Windows do GitHub

- Rodada **40525179198** (antes do último commit): 3 falhas minhas, consertadas no commit seguinte —
  `test_dividir_no_programa::test_aviso_diz_o_que_mudou_na_divisao` esperava "o do programa" (agora "o do Editor",
  D-479) e `test_so_neste_pedaco_no_original` (papel) pedia que o papel marcado à mão NÃO mudasse o Original — o
  comportamento antigo que a D-027/D-227 substitui (regra 4 do §11: a prova agora confere que o antigo saiu; o papel do
  detector continua sem mudar o Original, e há um teste novo do papel à mão saindo branco no Original e no Tirar o fundo).
- Rodada **40528106792** (código final): partes 2, 3, 4, 5 e "Botões e prints" passaram. Parte 1: só falhas que **já
  existem na base** `obra-2026-10-26` (39b7d8a) — conferido no PC rodando as mesmas provas numa cópia da base:
  P-005 (continuar, 4 casos), P-080 (painel Preto e branco), P-085 (tique do menu Filtro, D-481), P-081 (todas),
  P-109 (usar Mágico pro), P-127 (Antes de processar). Os mesmos 9 falham na base e aqui; nenhum é desta etapa.
