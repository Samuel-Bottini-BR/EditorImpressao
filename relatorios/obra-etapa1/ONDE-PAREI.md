# ONDE-PAREI — obra de 26/10/2026, etapa 1: "o que é feito à mão sempre vale no PDF"

Implementador · ramo `obra-etapa1-2026-10-26` (base `obra-2026-10-26` = `fase-1` `ddd4d74`) · worktree
`.claude/worktrees/obra-etapa1` · worktree de apoio (código antigo, só leitura, para a prova):
`.claude/worktrees/obra-etapa1-antes` (`ddd4d74`, solta, com as junções `modelos` e `gabarito\paginas`).

## Decisões que esta tarefa precisa cumprir (do Livro de decisões, `docs/plano/DECISOES.md`)

- **D-009 (26/10/2026):** "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo
  manualmente." → O que é feito à mão sempre vale no PDF, com a etapa do automático ligada ou não.
- **D-004 (28/09/2026):** "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas
  mexidas." → marca "mexida à mão" por página/folha e por etapa (esta etapa cria a marca; a pergunta é da etapa 3).
- **D-016 (escolha da gerente pela D-014):** a montagem da página segue a ordem obrigatória (endireita, depois corta
  uma vez só, no fim).
- **D-008 (parte de processamento; 22/09 e 26/10/2026):** "quero conseguir redimensionar o conteudo tambem" · "a
  ferramenta de mover não deveria estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" · "como
  é no photoshope, que você arrasta a hora que quiser e aumenta a hora que quiser" → mover/redimensionar o conteúdo
  chega ao PDF. Teste do Kaique (26/10, tarefa 5): "Mover conteúdo" arrastado para o meio não sai no meio do PDF
  (margens 15 × 53).
- **D-014 (26/10/2026):** obra até o fim sem pausas; os detalhes técnicos eu decido e anoto aqui.
- **D-017 (escolha da gerente):** aumentar além da beirada não corta nada escondido (o aviso e a marca na tela são da
  etapa 5) — tocada de leve aqui: o PDF não pode jogar o mover fora.

## Situação

**PRONTO PARA CONFERIR** (26/10/2026, ~22h). Falta: suíte inteira e `teste_botoes.py` (a gerente roda), verificador,
filtro de velocidade do GitHub, conferência do Samuel. Nada juntado.

## Escolhas técnicas (D-014: decido e anoto)

1. **Um lugar só: `core/etapas.py`.** Cada etapa separa "o automático mede" (a caixinha: `corta_sozinho`,
   `endireita_sozinho`, `marca_sozinho` = "Limpar a folha" + "Procurar gravura e letra") de "o feito à mão vale"
   (`recorte_a_mao`, `angulo_a_mao`, `filtro_a_mao`/`filtro_que_vale`, `marcacao_a_mao`, `conteudo_mexido`). A
   pergunta do pipeline é "vale nesta página?" = automático ligado OU feito à mão (`corta`, `endireita`, `filtra`).
   O automático **nunca** passa a medir com a caixinha desligada (é o que mantém o livro novo de fábrica igual).
2. **Projeto antigo sai igual — campo `Projeto.feito_a_mao_sempre_vale`.** Livro novo: `True`. `projeto.json`
   gravado antes desta etapa (sem o campo): `False` (`Projeto.de_dicionario`, `setdefault`, como o
   `ordem_do_preparo` de 09/10). No projeto antigo o valor à mão com a etapa desligada continua ignorado, a não ser
   que a página tenha a **marca** daquela etapa — isto é, que a pessoa mexa de novo pela tela (quando a etapa 2/3
   ligar as marcas). Assim nenhum PDF antigo muda ao abrir, e o que ele fizer daqui para frente segue a D-009. O
   projeto antigo regravado guarda `false` e continua antigo. (A janela, quando o trabalho salvo combina, usa o
   próprio objeto salvo — `ui/janela_principal._analise_pronta`, `projeto = salvo` —, então o campo atravessa sem
   mexer em `ui/`.)
3. **A marca "mexida à mão" (D-004):** `ConfigPagina.mexida_a_mao` e `ConfigFolha.mexida_a_mao` = lista de etapas
   (`cortar`, `endireitar`, `filtro`, `marcar`, `mover`; `dividir`, `girar` na folha). Funções para a tela:
   `etapas.marcar_mexida_a_mao(item, etapa)` / `desmarcar_mexida_a_mao`. Para a pergunta da etapa 3:
   `paginas_mexidas_a_mao(projeto, etapa=None)`, `folhas_mexidas_a_mao`, `mexida_a_mao`, `etapas_mexidas_a_mao`
   (marca OU valor que só a pessoa põe). Migração `marcar_pelos_valores` (chamada em `de_dicionario`): livro novo
   marca todo valor à mão; projeto antigo só onde o valor **já valia** (etapa ligada) e nunca `mover`.
4. **O que conta como valor à mão sem marca (livro novo):** corte = `recorte` gravado; ângulo = `angulo_manual`;
   marcação = região com origem `mao`; mover = escala ≠ 1, deslocamento ≠ 0 ou tamanho de folha; folha = girada.
   **Filtro e dividir: só pela marca da tela, nunca pelo valor.** Tentei primeiro "filtro da página ≠ filtro do
   livro" e os testes mostraram o risco: o filtro do livro pode mudar depois na tela "O que fazer" (o radio fica
   escolhido mesmo com "Limpar" desligado) e as páginas ficam com o de antes — o livro inteiro viraria "mexido à
   mão" e sairia filtrado com "Limpar" desligado (prova: `test_d009_filtro_do_livro_trocado_depois_...`). O mesmo
   com a folha dividida por uma análise antiga. Consequência: **até a etapa 2 ligar a marca, o filtro escolhido à
   mão numa página com "Limpar" desligado ainda não chega ao PDF** (o corte, o ângulo, a marcação e o mover já
   chegam). O resto (força do preto, linha de divisão arrastada) também só pela marca.
5. **Filtro com "Limpar a folha" desligado (livro novo):** página sem nada à mão sai como veio; filtro escolhido à
   mão → caminho inteiro com esse filtro e **só a marcação à mão** (o detector de gravura é automático e fica
   desligado); só marcação à mão → página no Original com só o marcado mudando (`_so_a_marcacao_a_mao`: pedaço,
   "pintar por cima"...). `filtro_que_vale` substitui todos os "`projeto.limpar and pagina.filtro == X`".
6. **Mover (D-008) — o que achei:** `compor_na_folha` jogava o mover fora em dois casos: (a) sem tamanho de folha
   (devolvia a página sem mexer); (b) folha do tamanho do corte arredondada a 0,01 cm (a janela "tamanho..." do
   teste do Kaique mostrou 16,23 × 21,01): a folha sai 1 ponto menor que o conteúdo e a "rede de segurança"
   desistia de compor — o deslocamento sumia. Conserto: parâmetro `mexido_a_mao` (= `etapas.conteudo_mexido`):
   sem folha, a folha é a própria página; com folha, não desiste por caber 1 ponto a menos — cola e corta só o que
   passa da beirada (D-017: a página fica do mesmo tamanho; o aviso é da etapa 5). Sem mover à mão, a conta de
   sempre, linha por linha. **Lado da tela (etapa 5, não mexi):** o `Visualizador._mover_conteudo` prende o
   retângulo dentro da folha — com a folha do tamanho do corte o conteúdo nem anda (no teste do Kaique o arrastar
   provavelmente não gravou deslocamento nenhum); a prévia (`TelaConferir`, `compor_na_folha` sem `mexido_a_mao`)
   precisa passar `mexido_a_mao=etapas.conteudo_mexido(...)` para a tela = PDF; `_mover_conteudo` da tela sai cedo
   sem tamanho de folha.
7. **Caminho rápido "só cadernos"** (`Projeto.so_cadernos`): não é usado se houver feito à mão que vale
   (`etapas.tem_feito_a_mao_que_vale`), senão a folha girada/dividida à mão, o corte etc. sumiam do PDF.
8. **Ordem obrigatória (D-016):** nada muda na montagem: o feito à mão entra nas mesmas contas (`_geometria`,
   `_geometria_endireitando_antes`, `_preparar_endireitando_antes`), endireita a página inteira e corta uma vez no
   fim. Prova: mesma página com as etapas ligadas ou desligadas, com ângulo e corte à mão (`test_d016_...`).
9. **A análise do livro** (`analisar_projeto`, `_analisar_a_folha`) continua olhando só as caixinhas: ali só existe
   o automático (o livro acabou de ser lido, não há nada à mão).
10. **Resumo da tela "O que fazer"** (`resumo_em_portugues`): acrescenta "manter o que você fez à mão em N páginas"
    só quando há feito à mão numa etapa desligada (sem isso, frase igual à de antes).

## Para as etapas 2, 3 e 5 (o que a tela precisa ligar)

- Ao mexer à mão: chamar `core.etapas.marcar_mexida_a_mao(pagina_ou_folha, etapa)` (corte, ângulo, filtro da
  página e seus ajustes, marcação, mover/tamanho da folha; dividir/girar na folha). Ao "voltar ao automático":
  `desmarcar_mexida_a_mao`. Sem isso, no **projeto antigo** o feito à mão novo com a etapa desligada não vale (no
  livro novo vale pelo valor).
- Pergunta "pular as páginas mexidas?" (D-004, etapa 3): `etapas.paginas_mexidas_a_mao(projeto, etapa)`.
- Etapa 5: prévia com `mexido_a_mao`; mover sem tamanho de folha (a folha é a página: em `conteudo_como_retangulo`
  / `deslocamento_do_retangulo` passar o tamanho da própria página em cm); não prender o retângulo na folha.

## Passos

- [x] Prova "Desligado de fábrica" no código antigo (somas das 32 páginas × 3 filtros).
- [x] `core/etapas.py` (um lugar só) + marca "mexida à mão" no modelo, com migração.
- [x] `core/pipeline.py`: checagens de caixinha trocadas por `core/etapas.py`.
- [x] Mover/redimensionar chegando ao PDF (`core/folha.compor_na_folha`).
- [x] `tests/test_decisoes.py` (18 provas).
- [x] Prova "Desligado de fábrica" no código novo + prova do projeto antigo com valores à mão.
- [x] Testes por arquivo; commits; push.

## Como cumpri cada decisão (com o teste)

| Decisão | Como | Prova (`tests/test_decisoes.py`, gera o PDF e mede) |
|---|---|---|
| **D-009** "abrir o livro sem escolher nenhuma opção para fazer tudo manualmente" | `core/etapas.py`; o pipeline pergunta "vale nesta página?" = automático OU feito à mão | `test_d009_corte_a_mao_...` (PDF com metade da largura), `test_d009_angulo_a_mao_...` (linha sai inclinada), `test_d009_filtro_da_pagina_...` (papel sai branco; com a marca da tela), `test_d009_marcacao_a_mao_...` (só o pedaço muda), `test_d009_resumo_...`, `test_caminho_rapido_so_cadernos_...`. **O antigo saiu:** os mesmos testes no `ddd4d74` falham por asserção (feito: 16 de 16 falharam lá) |
| **D-004** marca "mexida à mão" | `mexida_a_mao` em página e folha, gravado no projeto, migração `marcar_pelos_valores`, funções para a tela e para a pergunta da etapa 3 | `test_d004_marca_mexida_a_mao_por_pagina_folha_e_etapa`, `test_d004_marca_nasce_dos_valores_...`, `test_d004_projeto_antigo_sem_os_campos_abre_e_funciona` |
| **D-016** ordem obrigatória | o feito à mão entra nas mesmas contas (endireita a página inteira, corta uma vez no fim) | `test_d016_feito_a_mao_com_etapa_desligada_monta_igual_a_etapa_ligada` (PDF idêntico ponto a ponto) |
| **D-008** (processamento) mover/redimensionar no PDF | `compor_na_folha(..., mexido_a_mao=)`: sem folha = a própria página; não desiste por 1 ponto de arredondamento | `test_d008_mover_sem_tamanho_...` (+20% = +120 pontos), `test_d008_mover_para_o_meio_mede_as_margens_iguais` (diferença ≤ 2 pontos; no Kaique era 15 × 53), `test_d008_aumentar_...` (120%), `test_d008_folha_do_tamanho_do_corte_arredondada_...` (teste de reversão do defeito do Kaique: falha no `ddd4d74`) |
| Projeto antigo sai igual | `feito_a_mao_sempre_vale` False no `projeto.json` antigo | `test_projeto_antigo_com_valores_a_mao_e_etapas_desligadas_sai_igual` (PDF idêntico ao do livro sem nada à mão), `test_projeto_antigo_mexido_de_novo_pela_tela_vale`, `test_projeto_antigo_o_que_ja_valia_continua_e_ganha_a_marca` |

## Prova de projetos antigos iguais (números)

- **Desligado de fábrica** (32 páginas do gabarito × Original/Preto e branco/Melhorar, livro novo pelo
  `core.pipeline.processar`, script da junção): `ddd4d74` × `8abd3e8` = **96 de 96 somas iguais**
  (`somas-antes-ddd4d74.json`, `somas-depois-8abd3e8.json`; também 96/96 no `175addb`).
- **Projeto antigo com valores à mão** (novo, `scripts/prova_projeto_antigo.py`): `projeto.json` sem os campos
  novos, 6 páginas do gabarito (Escola 7, Horas 13, Marial 7, Opus Majus 11, Boécio 22, Graduale 221) com corte,
  ângulo, filtro, pedaço "só neste pedaço" e mover à mão, em 4 combinações de caixinhas (tudo desligado nas duas
  ordens, tudo ligado, só "Limpar"): `ddd4d74` × `8abd3e8` = **24 de 24 somas iguais**
  (`projeto-antigo-antes-ddd4d74.json`, `projeto-antigo-depois-8abd3e8.json`).

## Testes rodados (um arquivo por vez, no PC)

Todos passando no fim: `test_decisoes` 18, `test_trabalho_nao_se_perde` 82, `test_mesmo_livro_outro_caminho` 17, os 7
`test_corte_*` (76), `test_core` 62, `test_girar` 53, `test_zonas_na_folha` 25, `test_ordem_do_preparo` 56,
`test_tirar_fundo_no_programa` 54, `test_so_neste_pedaco_no_original` 20, `test_so_neste_pedaco_no_tirar_o_fundo` 8,
`test_misto_no_programa` 41, `test_limpar_pontinhos_no_programa` 42, e mais 50 arquivos que tocam as funções mudadas
(lista e resultados em `relatorios/conferir/obra-etapa1/testes-1.txt` a `testes-4.txt`, fora do git).
Na primeira rodada falharam 34 testes (zonas, girar, core, pontinhos, misto, trabalho): todos por causa da primeira
versão da regra do filtro (ver escolha 4) — consertado no `core/etapas.py`, não nos testes. Mudados de propósito
(D-009 substitui o comportamento antigo): `test_so_neste_pedaco_no_original.py` e
`test_so_neste_pedaco_no_tirar_o_fundo.py` — o teste antigo continua, agora no projeto antigo, e ganhou o par no
livro novo. **Não rodei** a suíte inteira nem o `teste_botoes.py` (pedido da gerente).

## Commits (ramo `obra-etapa1-2026-10-26`, com push)

- `175addb` core/etapas.py, modelo, pipeline, folha, test_decisoes, prova de fábrica antiga.
- `8abd3e8` filtro e dividir só pela marca; testes do pedaço ajustados à D-009; provas.
- (o último) ONDE-PAREI final e provas no `8abd3e8`.

## Ressalvas

- **Filtro à mão com "Limpar" desligado só chega ao PDF quando a tela gravar a marca** (etapa 2). Corte, ângulo,
  marcação à mão e mover já chegam hoje no livro novo.
- **No projeto antigo**, o feito à mão novo com a etapa desligada só vale com a marca da tela (etapa 2/3).
- **Mover: a tela ainda não deixa** (prende o retângulo na folha e exige tamanho de folha) e a prévia não usa
  `mexido_a_mao` — a prévia pode diferir do PDF num conteúdo movido até a etapa 5. O que passa da beirada fica de
  fora sem aviso até a etapa 5 (D-017).
- Livro novo com "Limpar" desligado e filtro escolhido à mão: o "Só as letras" do livro (caixinha escondida)
  pode valer nessa página (`misto.opcoes_da_pagina` segue o livro). Não testado.
- `ConfigFolha.apagada` continua ignorado no caminho rápido "só cadernos" (era assim; não é etapa desta tarefa).
- Velocidade: não medi (regra de 19/10: filtro do GitHub / gerente). As funções novas só leem campos.
- Worktree de apoio `.claude/worktrees/obra-etapa1-antes` (`ddd4d74`, solta) com junções `modelos` e
  `gabarito\paginas`: para remover, primeiro `(Get-Item <junção>).Delete()`. A worktree `obra-etapa1` também tem as
  duas junções (criadas por mim).

## Ideias para a Lista de espera

- A tela de opções guarda o filtro do livro escondido com "Limpar" desligado; quando ela sair (etapa 3), o filtro
  "do livro" com "Limpar" desligado poderia virar Original de vez, simplificando `filtro_que_vale`.

## Perguntas para o Samuel

Nenhuma até agora.
