# Vistoria das gambiarras: onde parei

Agente vistoriador (só lê código e escreve a lista). Ramo `obra-2026-10-26`, cópia `obra-juncao`. Nenhuma linha de
código mudou; os únicos arquivos mexidos são este e `lista.md`.

## Decisões que esta tarefa precisa cumprir

- **A ordem de serviço do Samuel (26/11/2026)**, em `ordem-de-servico.md`: "Um agente NOVO, que só lê e não conserta
  nada, vistoria o programa e escreve uma lista. Nenhuma linha de código muda." Os cinco tipos; GRAVE/médio/leve; uma
  linha por achado com onde, tipo, gravidade, cópias, POR QUÊ ("se não achar, escrever 'não achei o motivo', nunca
  inventar"), item da Central e o que o Kaique perderia; certeza na lista, dúvida em "Suspeitas"; "Ele nunca para no
  meio de um pedaço"; "A LISTA NÃO FECHA NADA"; "Sem propostas de conserto na lista, sem plano."
- **CLAUDE.md §11.12** (13/11 e 18/11/2026): "o agente não pode fazer gambiarras como na outra ferramenta nossa que
  fazia várias gambiarras e funcionava de maneira diferente em vários lugares" · "eu acho que tinhamos que atualizar a
  regra de gambiarras para que ela se aplicasse a tudo né?". O que a vistoria procura é o que essa regra chama de
  gambiarra: conserto só no lugar do defeito, conta copiada, sintoma tratado em vez da causa.

## Pedaços

| pedaço | situação | começo | fim | tempo |
|---|---|---|---|---|
| girar | feito (12 achados, G-01 a G-12) | 26/11 15:40 | 26/11 15:51 | ~11 min (relógio da máquina, `date`) |
| dividir | feito (16 achados, DV-01 a DV-16) | 26/11 17:25 | 26/11 17:38 | ~13 min de código (relógio da máquina, `date`; antes, ~10 min lendo as regras e os insumos) |
| desfazer | feito (8 achados, DF-01 a DF-08) | 26/11 17:38 | 26/11 17:43 | ~5 min (relógio da máquina, `date`) |
| aplicar-em / "o que vai junto" | feito (8 achados, AP-01 a AP-08) | 26/11 17:44 | 26/11 17:53 | ~9 min de código (relógio da máquina, `date`; antes, ~3 min lendo as regras e os insumos; agente novo) |
| como-fica (as renderizações) | feito (5 achados, CF-01 a CF-05) | 26/11 17:54 | 26/11 17:58 | ~5 min (relógio da máquina, `date`) |
| marcações | feito (5 achados, MC-01 a MC-05) | 26/11 17:59 | 26/11 18:02 | ~3 min (relógio da máquina, `date`) |
| contagens e situação da página | **próximo** | | | |
| o resto da tela | | | | |

O que o pedaço girar leu (não reler): `core/girar.py` inteiro; em `ui/tela_conferir.py` os métodos do girar
(L6554-6917), `_registrar` e os ajudantes dele (L5942-6081), `_espera_pelas_marcacoes` (L6938-6996), a grade
(`_acao_nas_escolhidas`, `_girar_as_escolhidas_que_sao_metade`, `_pagina_dentro_da_folha`), `_atualizar_previa` só no
ramo do Dividir, `_giros_das_paginas`/`_giros_das_folhas`, `_proporcao_da_pagina`, `_tamanhos_estimados`,
`MARCAS_DA_*`; `ui/widgets/tira_miniaturas.py` (giros e `_metade`); `ui/janela_principal._acertar_a_capa` e a fiação
do menu do girar; `core/etapas.py` (marcas, L95-245 e L587-615); `core/pipeline.preparar_para_recorte` e o fim de
`preparar_metade`; `core/automatico.antes_da_pagina` e o começo de `_dividir`; `ui/tarefas._folha_crua` e
`_giro_da_folha`.

O que o pedaço dividir leu (não reler): `core/dividir_a_mao.py` inteiro; `core/dividir.py` inteiro; em
`core/pipeline.py` `_analisar_a_folha` (L209-276), `jeito_de_dividir`, `achar_divisao`, `_lombada_do_editor`,
`achar_sobra`, `folga_do_giro_na_sobra`, `faixa_da_sobra`, `_cortar_a_sobra`, `recalcular_divisao`,
`trazer_divisao_da_analise`, `_partes_da_folha`, `preparar_para_recorte`; em `core/automatico.py` `fotografar`
(L535-570), `medir` (L578-672), `_a_tampa`, `_dividir` (L932-990), o ramo Dividir de `_desligar` (L1130-1160),
`paginas_depois`, `paginas_juntadas` (L396-416), `vai_dividir_pelo_tamanho` e `paginas_do_pdf_depois` (L1590-1757);
`core/girar.gira_so_a_pagina`/`giro_da_pagina`; `core/zonas_na_folha._corte_efetivo` e `repartir_nas_metades`;
`core/analise.analisar_folha` (só o Dividir); `modelos.Projeto.paginas_ativas`, `_de_folha_nao_dividida`,
`metade_sobrando`, `_tem_metade_de_folha_dividida`; em `ui/tela_conferir.py` L4040-4306 (passos do Dividir, linha do
motor, `_volta_como_estava`, `_linha_arrastada`, `_acertar_a_linha_do_dividir`, leituras), L6083-6552 (`_mover_corte`
até `_trocar_jeito_da_folha`), L7396-7541 (o "dividir" da grade), o trecho dos botões em `_atualizar_botoes`
(L5447-5470) e o botão "nao_dividir" do aviso (L9379-9382); `ui/tarefas.TarefaDividirFolhas` e `TarefaLerLinhas`
(L418-520); `ui/tela_ampliada._corte_movido` e a linha (L289); as chaves de `ui/automatico.py` L1738-1755 e
`ui/widgets/folhas_do_caderno.py` L458-472.

O que o pedaço desfazer leu (não reler): `ui/desfazer_nesta_pagina.py` inteiro; `historico_acoes.py` L1-130 e
L398-683 (`HistoricoAcoes` até `_regravar_tudo`, `aplicar`, os prefixos, `_restaurar_tipo`, `montar_acao`); em
`ui/tela_conferir.py` `_voltar_no_historico` (L1552-1567), `_gravar_no_livro` (L2262-2271), `_gravar_o_conteudo` e
`_conteudo_como_veio` (L2498-2554), `CAMPOS_DA_MARCACAO`, `_selecao_mudou`, `_registrar_a_marcacao`,
`_desfazer_marcacao` (L3050-3130), `_sem_recorte` (L7018), o fim de `_aceitar_avisos` (L9496-9514), `desfazer`,
`refazer`, `_medir_o_em_branco_ao_refazer`, `_reacertar_as_opcoes` (L9661-9755) e o Ctrl+Z de `tratar_tecla`
(L9856-9861); `ui/widgets/editor_selecao.py` (a pilha `_marcos`, `desfazer`, `event`, o Ctrl+Z do `keyPressEvent`);
`ui/barra_de_menu._montar_editar`; `ui/janela_principal.py` L270-280, L397-410, L940-980 e `keyPressEvent`
(L2046-2053); `modelos._migrar_folha`/`_migrar` (L1130-1160).

O que o pedaço aplicar-em leu (não reler): `ui/dialogo_escolher_paginas.py` L1-104; `core/fundo_tirado.py` inteiro;
em `core/girar.py` L100-170 e L340-420 (alcance, avisos, `paginas_do_alcance`, os campos do giro das páginas); em
`core/etapas.py` L140-200, L260-300 e L560-600 (`_tem_valor_a_mao`, `mexida_a_mao`, `recorte_a_mao`,
`conteudo_fora_do_padrao`); `core/automatico.py` L120-200 (`CAMPOS_DA_PAGINA`, `campos_da_pagina_no_filtro`) e
L1040-1056 (o "Rodar nelas também" do Endireitar e do Cortar); `core/perfis.py` L40-100; `core/pipeline.py`
L1375-1425 (`recorte_depois_de_mudar_o_angulo`), L2375-2410 (o "refazer a gravura" das opções do livro) e
L2443-2560 (`garantir_selecao`); `modelos.py` L395-425 e `guardar_selecao` (L513-533); em `ui/tela_conferir.py`
L2085-2150 (tamanho da folha), L2490-2650 (`_gravar_o_conteudo`, `_mover_em_todas`, `_escolher_paginas_do_mover`,
conferência por trás), L2875-2925 (os botões do Marcar e da Foto), L3190-3345 (`_preparar_para_trocar_forma`, `_forma_nas`,
`_marcacao_em_todas`, `_marcacao_nas_proximas`), L3462-3485 (a caixinha da letra clara), L3590-3610 (o "Aplicar em"
do Filtro), L7025-7240 (`_recorte_em_todas`, `_escolher_paginas_do_corte`, `_paginas_do_alcance_do_angulo`,
`_mudar_o_angulo`, `_jeito_do_retangulo`, `_com_o_retangulo_do_corte`), L7570-7600 e L7640-7760 (os caminhos do
ângulo), L8355-8410 (`usar_da_tela_cheia`, `_gravar_opcao_da_tela_cheia`), L9100-9240 (`_campos_do_aplicar_em`,
`desfazer_o_tirar_o_fundo`, `_filtro_em_todas`, `_filtro_nas_proximas`), `_marcar_revisada` (L9315),
`CAMPOS_SO_DO_MOVER` (L10040-10070) e `MARCAS_DA_*` (L10140-10187); `ui/tarefas.py` L1140-1180 (a chave, só para
ver os campos do filtro); `ui/automatico.py` L405-440, L660-700 e L2575-2600; `ui/widgets/filtros_tela_cheia.py` L79 e
L498-515; `ui/janela_principal.py` L935-980.

O que o pedaço como-fica leu (não reler): `ui/tarefas.py` L360-415 (`TarefaConferirOImpressoDeFora`), L792-852
(`_TarefaCartoes`), L895-1036 (`_TarefaPrevia`: `run`, `_para_recorte`, `_folha_crua`), L1135-1260 (a chave, `pegar`,
`pedir`, a chave da medida) e L1395-1470 (`chave_com_filtro`, `pegar_com_filtro`, `chave_para_recorte`,
`pedir_cartoes`); em `core/pipeline.py` L690-770 (o fim de `preparar_metade`), L3407-3545 (`_filtrar`,
`_filtrar_a_pagina`, `_so_a_marcacao_a_mao`), L3546-3580 (`filtro_com_as_caixinhas`), L3696-3708, L4245-4265
(`_misto_vale`), L4447-4525 (`renderizar_com_filtro`, `renderizar_pagina_para_recorte`) e L4865-4925
(`compor_como_no_pdf`); `core/zonas_na_folha.geometria_do_desenho` (docstring, L131-161); `core/automatico.py`
L1288-1310 (`como_sai_na_tela`) e L1527-1575 (`depois_da_pagina`); em `ui/tela_conferir.py` L4797-5160 (as
figurinhas: `_atualizar_cartoes`, `_como_sai_no_pdf`, `_sai_diferente_da_previa`, `_assinatura_do_como_sai`,
`_chave_dos_cartoes`, `_cartao_sem_fundo`, `_cartao_pb_pelo_misto`, `_cartoes_a_pintar`, `_cartao_do_misto`,
`_cartoes_prontos`, `_conferir_qualidade_do_preto_e_branco`, `_imagem_sem_filtro`) e L5666-5760
(`_miniatura_branca`, `_acertar_as_miniaturas_movidas`); `ui/tela_ampliada._imagem_do_outro_filtro` (L304-350);
`ui/widgets/filtros_tela_cheia.py` L82-170 e L800-835.

O que o pedaço marcações leu (não reler): em `ui/tela_conferir.py` L2855-2875, L3042, L3132-3197 (`_limpar_marcacao`,
`_folha_em_branco`, `_detectar_de_novo`), L4619-4730 (`_atualizar_marcacao`, `_pagina_sem_filtro_para_o_ajuste`,
`_avaliar_os_pedacos`); `ui/widgets/editor_selecao.py` (os `selecao_mudou.emit` e `limpar_o_que_a_maquina_marcou`,
L244, L345, L447-455); `ui/barra_de_menu.py` L202 e L260; `core/zonas_na_folha.py` (lista das funções, `_converter`
L420-463, `acompanhar` L560-583); `core/selecao.py` L100-175 e L370-390 (`Regiao.de_dicionario`, `Selecao.de_lista`);
`core/etapas.py` L533-544; `core/pipeline.py` L3708-3712; `core/filtros.py` L4300-4308; `core/misto.py` L676-681; e a
busca por `origem` em `core/`, `ui/` e `modelos.py`.

## Suspeitas (dúvidas de outros pedaços; quem ler o pedaço confirma ou descarta)

### Abertas

- (contagens e situação) O aviso "Ficou escura" / "Texto quase sumiu" é posto pela tela
  (`ui/tela_conferir._conferir_qualidade_do_preto_e_branco` L5086-5121), medindo a figurinha do Preto e branco (a conta
  simples do CF-01, sem a marcação nem o "Só as letras"), e grava `pagina.alertas` direto, fora do Histórico;
  `core/analise.py` L778 tem outra regra que devolve o mesmo aviso. Confirmar se são duas regras para o mesmo aviso.
- (contagens e situação) "Parte do impresso fica de fora" (D-017) é medida em três lugares: `core/pipeline.
  compor_como_no_pdf` (com `anotar_o_de_fora`, o PDF), `ui/tarefas.TarefaConferirOImpressoDeFora` (L382-410, que
  refaz à mão a mesma sequência: margens e `parte_impressa_de_fora`) e a ferramenta Mover na tela (o docstring de
  `compor_como_no_pdf` diz "a ferramenta Mover anota na tela"). Conferir se as três dão o mesmo número.
- (contagens e situação) `ui/tela_conferir._medir_o_em_branco_por_tras` (L2610-2636) ainda procura a conta com
  `getattr(pipeline, "medir_o_em_branco", None)` e diz "ENQUANTO ELA NÃO ESTIVER NA OBRA, nada acontece aqui"; a
  conta já existe (`core/pipeline.py` L3062). Conferir se a guarda virou código morto.
- (contagens e situação) No girar de formato "pagina" com `folha:<f>.rotacao` (G-04), `_com_os_avisos_de_agora` guarda
  os avisos das páginas e não os da folha; no formato "folha", o contrário. Conferir se o desfazer devolve os avisos
  certos nos dois.
- (contagens e situação) Na grade "Todas as páginas", "trazer de volta" desfaz o "em branco" e o "tirar do livro" de
  uma vez; na página sozinha, só o "tirar do livro"; e "deixar em branco"/"tirar do livro" têm a regra escrita duas
  vezes (a gerente achou isso em 17/11, Central `au-d-487`). Confirmar no código.
- (contagens e situação) Os avisos "Lombada incerta" e "Não parece dupla" só são refeitos pela análise e pelo
  Automático (`analise.analisar_folha`); "dividir esta", "dividir todas", a grade e a troca de motor não os refazem (o
  "dividir todas" nem marca conferida, D-627). Conferir se a folha fica com o aviso de antes depois de dividida à mão.

### Fechadas

- (marcações, aberta no aplicar-em) O "refazer a gravura" em três lugares → **virou o achado MC-02**.
- (marcações, aberta no dividir) Mover a linha de uma folha dividida não reparte as marcações → **virou o achado
  MC-03**: as zonas seguem pela geometria da folha, sem mudar de página.

- (como-fica, aberta no girar) A chave das prévias montada em dois lugares de `ui/tarefas.py` → **virou parte do
  achado CF-04**: a chave da imagem do Cortar é cópia de parte da chave da prévia, e o docstring dela não conta o ângulo
  que o livro novo usa.
- (como-fica / marcações, aberta no girar) `geometria_do_desenho` em três ramos, só o primeiro com `ordem=` → **virou o
  achado leve CF-05**: não é defeito (a `ordem` só conta no "endireitar antes"); o que fica é a mesma chamada escrita
  três vezes.

- (aplicar-em, aberta no dividir) O "aplicar em" do Endireitar repete a conta de páginas da D-636? → **descartada**:
  `_paginas_do_alcance_do_angulo` chama `girar.folhas_do_alcance` sobre a lista de páginas, a mesma conta que
  `girar.paginas_do_alcance` (D-636) usa por dentro; a D-636 só acrescenta o filtro "é metade de folha dividida", que
  é do girar. O aviso em duas funções já está no G-10; a conta à mão do "todas"/"daqui em diante" das outras
  ferramentas ficou no AP-06.
- (aplicar-em, aberta no dividir) O "usar em todas" do Dividir deixa todas as folhas que recebem a linha como "linha
  própria" na vez seguinte; o Cortar e o Mover também? → **virou o achado AP-02**: sim, nos três (o Cortar e o Mover
  pelo valor gravado, o Dividir pela marca).

- (dividir, aberta no girar) Ler a folha girada a 150 DPI em quatro lugares → **virou o achado DV-01**.
- (dividir, aberta no girar) `core/automatico.py` L1158 põe `apagada` na direita fora do `_dividir` → **virou parte do
  DV-03** (é o "Desligar" do Automático: um terceiro jeito de juntar a folha).
- (dividir, aberta no girar) O giro só da página escondido na folha juntada pelo Automático voltaria ao dividir de novo
  → **descartada como achado próprio**: os dois caminhos que dividem de novo (`campos_para_dividir` com duas páginas, e
  com as metades guardadas) devolvem as páginas "como estavam", com o giro de cada uma, que é o que a D-498 diz e o
  comentário de `LIMPAR_AO_PARTIR` (L94-100) descreve; o `b12d6f61` é o caso da página nova partida, que passa por
  `LIMPAR_AO_PARTIR`. O que sobra é a diferença entre os jeitos de juntar, que já está no DV-03 e no DV-05.
- (desfazer, aberta no girar) O "Desfazer nesta página" não tem o giro da página → **descartada**: é a decisão. A D-621
  do Livro lista exatamente as cinco etapas ("Endireitar, Corte das bordas, Mover e tamanho, Filtro, Gravuras e
  fotos"), e o cabeçalho do arquivo diz "A divisão não entra".
- (desfazer, aberta no dividir) A metade decidida pelo clique (`_metade_clicada_no_dividir` L423) → **virou o achado
  DF-08**: usa a linha da tela (presa entre 2% e 98%, a mesma do DV-07) e um laço próprio que não pula a página posta
  à mão.
