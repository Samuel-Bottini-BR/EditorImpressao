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

- **D-885 (26/11/2026), a ordem de serviço:** "Um agente NOVO, que só lê e não conserta nada, vistoria o programa e
  escreve uma lista. Nenhuma linha de código muda." · "se não achar, escrever 'não achei o motivo', nunca inventar" ·
  "Ele nunca para no meio de um pedaço" · "A LISTA NÃO FECHA NADA" · "Sem propostas de conserto na lista, sem plano."
- **D-886 (27/11/2026), a resposta do Fable:** "Decisão do Samuel: a vistoria continua pelo programa inteiro, antes de
  qualquer conserto." · "Nenhuma linha de código muda até lá." Ajustes para os pedaços novos (não para a tela já feita):
  a) "Quando o achado for 'a mesma expressão em N lugares', contar por busca no programa inteiro e listar todas (o G-12
  dizia 5 lugares; são 12)." b) "GRAVE só quando o conserto errado chega na tela do Kaique ou no PDF; '3 ou mais
  lugares' sozinho é médio. O resto da régua fica." c) "Em cada achado novo, além do item da Central, dizer a qual
  achado da tela ele é 'outra cópia', quando for (ex.: 'outra cópia do SP-03')."

## Programa inteiro (D-886): pedaço grande 1, peças da tela de trabalho

Agente novo, 27/11/2026, começou às 13:31 (relógio da máquina, `date`). Leu as regras, a ordem, a resposta do Fable,
este arquivo, a lista (modelo e os 81 achados, só os títulos), a fila da Central e o índice da memória.

Divisão em pedaços pequenos (escrita antes de começar):

| pedaço pequeno | arquivos | situação | começo | fim |
|---|---|---|---|---|
| 0. a suspeita aberta | `core/pipeline._guardar_o_conteudo` e a passada | feito (virou PP-01) | 27/11 13:34 | 27/11 13:35 |
| 1. painéis | `ui/widgets/paineis.py`, `barra_girar.py`, `escolhas_do_misto.py`, `cartao_filtro.py`, `medidor.py`, `barra_opcoes.py`, `menu_com_amostra.py` | feito (5 achados, PT-01 a PT-05) | 27/11 13:35 | 27/11 13:39 |
| 2. visualizador e lado a lado | `ui/widgets/visualizador.py`, `paginas_lado_a_lado.py`, `paginas_rolando.py`, `roda_de_lado.py`, `ui/rodinha.py` | feito (6 achados, PT-06 a PT-11) | 27/11 13:39 | 27/11 13:43 |
| 3. tira, miniaturas e grade | `ui/widgets/tira_miniaturas.py`, `miniaturas.py`, `todas_as_paginas.py`, `trilha_agrupada.py`, `trilha_ferramentas.py`, `bolinha.py` | a fazer | | |
| 4. tela cheia e comparar | `ui/tela_ampliada.py`, `ui/widgets/filtros_tela_cheia.py` | a fazer | | |
| 5. seleção à mão | `ui/widgets/editor_selecao.py` | a fazer | | |
| 6. menu, barras e o resto | `ui/barra_de_menu.py`, `estilo.py`, `perguntas.py`, `janela_confirmar.py`, `dialogo_escolher_paginas.py` (`ui/desfazer_nesta_pagina.py` já foi lido inteiro no pedaço desfazer: não se relê, só se confere o que os outros pedaços apontarem) | a fazer | | |
| 7. os trechos não lidos da `tela_conferir` | `_montar` e a barra de baixo (L766-1362), `_LugaresDeEncaixe`/`_RotuloDoLivro` (L432-590), o corpo de `_montar_aba_*` fora do já lido (L1916-3653), a "peça" nos pares (L8700-8800), o zoom (L8478-8560, L9006-9088) | a fazer | | |

Como leio cada arquivo: a lista das funções; as buscas por `projeto.`, `pagina.`/`folha.`, campos de
`ConfigPagina`/`ConfigFolha`, `import` de `core/`, contas (`%`, `round`, `int(`), `if` por caso e `getattr`/`hasattr`;
leio por inteiro as funções que essas buscas apontam. Desenho puro (montar botões, cores, `paintEvent` sem conta de
página) não vira achado. Linhas no `cbc9784f` (o mesmo código do `30920fe7`: os commits de depois só mexeram em
relatórios e no Livro).

## Pedaços (tela de trabalho, 26/11)

| pedaço | situação | começo | fim | tempo |
|---|---|---|---|---|
| girar | feito (12 achados, G-01 a G-12) | 26/11 15:40 | 26/11 15:51 | ~11 min (relógio da máquina, `date`) |
| dividir | feito (16 achados, DV-01 a DV-16) | 26/11 17:25 | 26/11 17:38 | ~13 min de código (relógio da máquina, `date`; antes, ~10 min lendo as regras e os insumos) |
| desfazer | feito (8 achados, DF-01 a DF-08) | 26/11 17:38 | 26/11 17:43 | ~5 min (relógio da máquina, `date`) |
| aplicar-em / "o que vai junto" | feito (8 achados, AP-01 a AP-08) | 26/11 17:44 | 26/11 17:53 | ~9 min de código (relógio da máquina, `date`; antes, ~3 min lendo as regras e os insumos; agente novo) |
| como-fica (as renderizações) | feito (5 achados, CF-01 a CF-05) | 26/11 17:54 | 26/11 17:58 | ~5 min (relógio da máquina, `date`) |
| marcações | feito (5 achados, MC-01 a MC-05) | 26/11 17:59 | 26/11 18:02 | ~3 min (relógio da máquina, `date`) |
| contagens e situação da página | feito (15 achados, SP-01 a SP-15) | 26/11 18:04 | 26/11 18:18 | ~14 min de código (relógio da máquina, `date`; antes, ~5 min lendo as regras e os insumos; agente novo) |
| o resto da tela | feito (12 achados, RT-01 a RT-12) | 26/11 18:19 | 26/11 18:29 | ~10 min (relógio da máquina, `date`) |

**Tela de trabalho terminada (26/11, 18:29).** Os oito pedaços estão feitos. Total da lista: **81 achados**. Por
tipo: 53 do tipo 1 (a mesma regra em mais de um lugar), 6 do tipo 2 (conta na tela), 10 do tipo 3 (desvio por caso),
7 do tipo 4 (peça que só protege outra) e 5 do tipo 5 (código morto). Por gravidade: 30 GRAVE, 31 médios, 20 leves.
Por pedaço: girar 12 (6 GRAVE), dividir 16 (6), desfazer 8 (2), aplicar-em 8 (2), como-fica 5 (3), marcações 5 (1),
contagens e situação 15 (7), o resto da tela 12 (3). Suspeita aberta: uma, de fora da tela de trabalho (abaixo).
Quem continuar a vistoria, fora da tela (a ordem de serviço só fala da tela primeiro; o resto do programa não foi
pedido em pedaços), começa pela suspeita aberta.

O que o pedaço o resto da tela leu (não reler): `configuracoes.espaco_livre_mb` (L185-206) e as buscas por
`disk_usage`/`espaco_livre` no programa; a busca mecânica de métodos e constantes de nível de módulo de
`ui/tela_conferir.py` sem uso em `ui/`, `core/` e na raiz; em `ui/tela_conferir.py` L395-432 (`protegido`),
L1916-1987 e L1987-2069 só pelas leituras do projeto, `_mudar_margens_iguais` (L2069-2088), L2274-2320 (as linhas de
apoio), L3005-3040 (`_mexer_na_area`, `_escolher_operacao`, `_escolher_ferramenta`), `carregar` e as partidas
(L3653-3787), `eventFilter` (L3788-3822), `_limpar_abas` (L3850-3884), `_navegar` (L4012-4040), `atualizar` e
`_atualizar_paineis` (L4476-4535), `_atualizar_previa` (L4535-4619, fora do ramo do Dividir), L4945-4975
(`_sai_diferente_da_previa`, `_assinatura_do_como_sai`), L5572-5666 (os pares da tira, `_ir_para_o_quadro_da_tira`,
`_mover_da_tira`), L5796-5896 (`_pagina_da_previa`, `_previa_chegou`), L7665-7700 (o fim de
`_atualizar_conta_do_endireitar`), L7761-7830 (`_escolher_filtro`, `_mudar_algoritmo_pb`, `_mudar_cores`), L8031-8200
(o medidor inteiro), L8598-8700 (`_acertar_a_vista_da_pagina`, `_acertar_o_lado_a_lado`, `_onde_vai_a_peca`),
L8804-8830 e L8947-8970 (a roda), `lista_de_paginas_mudou` (L9635-9660), L9770-9933 (as teclas), L9934-9995
(`_avisar_problema`, `_pedir_processamento`, `miniaturas_guardadas`), a busca por `pagina.filtro`, por
`hasattr(self`/`getattr(self, "` e por `projeto.limpar`/`cortar_bordas`/`endireitar` em `ui/`; `main.py` L55-95;
`ui/tarefas._mensagem_amigavel` (L115-130); `ui/janela_principal.py` L1995-2035; `ui/automatico.py` L277-330 e
`core/automatico.campos_da_pagina_no_filtro` (L145-200); `core/etapas.corta_sozinho`/`endireita_sozinho` (L284-313);
`core/pipeline.py` L1714-1720 e L1958-1968 (`DPI_DA_PASSADA`, `_guardar_o_conteudo`); os pares em
`ui/widgets/tira_miniaturas.py` L760-830, `ui/widgets/paginas_rolando.py` L305-320 e `ui/widgets/todas_as_paginas.py`
L630-640. **Não lido** (só montagem de botões e desenho, sem conta achada pelas buscas): `_montar` e a barra de baixo
(L766-1362), o corpo de `_montar_aba_*` (L1916-3653, fora das linhas acima), os `_LugaresDeEncaixe`/`_RotuloDoLivro`
(L432-590), a "peça" nos pares (L8700-8800) e o zoom (L8478-8560, L9006-9088).

O que o pedaço contagens e situação leu (não reler): `core/avisos.py` inteiro; em `modelos.py` `alertas_pendentes`,
`_alertas_pendentes` (L1097-1104), `ConfigFolha` L45-56 e `ConfigPagina` L310-345, L490-505; em `core/pipeline.py`
L180-195 (as observações da análise), L244-276 (os avisos da análise), `_anotar_aviso_da_pagina` (L1070-1093),
L1530-1575 (`_anotar_contas_discordam` no desenho, `_anotar_corte_encostou`), L1641-1682 (`marcar_paginas_diferentes`,
`_anotar_contas_discordam`, `acertar_alerta_do_endireitar`), `_anotar` (L2009), `_anotar_conferir` (L2711),
L2995-3086 (`precisa_medir_o_em_branco` até `precisa_do_desenho_do_pdf`), L4030-4070 (`acertar_aviso_do_reforco`,
`_esquecer_aceitos`), L4126-4220 (os avisos do "Só as letras", `acertar_faixa_do_livro`), `acertar_alertas_de_cor`
(L4279-4316), L4840-4935 (o fim de `_pagina_pronta`, `compor_como_no_pdf`, `anotar_o_impresso_de_fora`), L4985-5012
(o laço do PDF) e `_anotar_folha_maior` (L5187); em `core/analise.py` L320-332, L434-446, L463-500
(`avaliar_preto_e_branco`) e L750-781 (`analisar_resultado`); `core/etapas.limpa_sozinho` e `filtro_que_vale`
(L328-345); em `core/automatico.py` L678-683 (`_DA_FOLHA`...), `_juntar_avisos` (L803), `_avisos_medidos`
(L1173-1221) e `avisos_do_livro` (L1849-1888); `core/dividir_a_mao.py` L84-96 e L228-300 (`campos_para_dividir`,
`campos_para_juntar`); `core/folha.tamanho_da_folha_cabe` (L130-150); em `ui/tela_conferir.py` L1385-1500 (bolinhas,
`_atualizar_barra_de_baixo`), L2150-2195 (`_conferir_tamanho_da_folha`), L2395-2475 (o fim de `_atualizar_o_mover`,
`_acertar_o_painel_do_mover`), L2600-2650 (`_medir_o_em_branco_por_tras`, `_impresso_conferido*`), L3885-3930
(`_montar_tira`), `_total` (L3998), L4300-4470 (`ir_para_pagina`, `_ir_para_proximo_alerta`, `_avisos_do_item`,
`_itens_com_duvida`, `esta_certo`, `_ir_do_para_revisar`, `abrir_so_as_que_precisam`), L4580-4596, L5075-5121
(`_conferir_qualidade_do_preto_e_branco`), L5158-5450 (a faixa inteira: `_atualizar_faixa` até `_mostrar_sugestao`),
L5490-5565 (`_atualizar_tira`, `_atualizar_tira_do_dividir`), `_atualizar_contador` (L5763-5790), `_alertas_da_previa`
(L5897-5941), `_com_os_avisos_de_agora` (L6021-6045), o `_registrar` de novo (L5942-5985, só para ver a ordem),
`_acao_nas_escolhidas` (L7285-7345, os ramos em branco/tirar/trazer), `_dividir_as_medidas` (L7510-7541),
`abrir_todas_as_paginas` (L8412-8432), `restaurar_pagina` (L9089), L9218-9470 (`apagar_pagina` até
`_desfazer_o_reforco`, com `_marcar_revisada`, `_aplicar_sugestao`, `_aplicar_correcao`, `_escolher_forca`,
`_deixar_em_branco`), L9470-9590 (`_aceitar_avisos` inteiro, `_aceitar_o_motivo_em_todas`, `_aceitar_tudo`,
`_ir_para_o_aviso`, `_mostrar_a_lista_dos_avisos`) e a tecla Delete de `tratar_tecla` (L9905-9915); a busca por
`revisada` (todas as linhas) e pelas ações de `_registrar` (os 60 tipos); `ui/tarefas.TarefaConferirOImpressoDeFora`
(L345-416); `ui/widgets/todas_as_paginas.py` L78-100, L555-575 e L630-660 (`ItemDaGrade`, o número "só as que
precisam"); `ui/automatico.py` L1530-1565 e L1785-1870 (o "página N de M"); `ui/tela_ampliada._total`;
`ui/janela_principal.py` L700-720 e L1940-1960; `ui/janela_confirmar.py` L155-190; `ui/tela_inicio.py` L960-980;
`projetos.py` L330-360 e L410-440; `ui/dialogo_impressao.py` L845-866; o cabeçalho de `core/ordem_das_paginas.py`.

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

- (pedaço grande 2, preparar a página; vista no pedaço 0 de 27/11) `core/pipeline._geometria` mede o conteúdo com
  `em_branco=analise.EM_BRANCO in pagina.alertas` (L1206 e L1359), e o aviso "Parece em branco" não está na chave da
  geometria (`_chave_da_geometria` L1469). Conferir se o corte guardado pode ficar o de antes do aviso mudar (a mesma
  família do CF-04: a chave que não conta um campo de que a conta depende).

### Fechadas

- (fora da tela, achada no pedaço 8; fechada no pedaço 0 de 27/11) `core/pipeline._guardar_o_conteudo` e o
  `_TAMANHOS.setdefault` → **virou o achado leve PP-01**: a proteção foi posta pelo mesmo commit que tirou a causa
  (`57de8af4`, 21/10); desde 22/10 (`8e237efe`) todas as nove chamadas medem na resolução do livro, e a chave tem a
  resolução; não achei caso hoje em que ela mude o resultado. A "reserva" da passada (L2229-2256) entra no mesmo achado.

- (contagens e situação, suspeita 1) "Ficou escura" / "Texto quase sumiu" com duas regras → **virou o achado SP-08**:
  a tela mede e grava; a regra do núcleo (`analise.analisar_resultado`) nunca foi chamada (código morto).
- (contagens e situação, suspeita 2) "Parte do impresso fica de fora" medida em três lugares → **virou o achado
  SP-10**: a mesma função, em três imagens diferentes (filtrada, sem filtro a 75 DPI, a prévia da tela).
- (contagens e situação, suspeita 3) A guarda `getattr(pipeline, "medir_o_em_branco", None)` → **virou o achado leve
  SP-11**: a conta existe desde o mesmo dia; a guarda nunca mais é falsa.
- (contagens e situação, suspeita 4) Os avisos guardados para o desfazer nos dois formatos do girar → **virou o achado
  SP-12**: só os do lado do alvo; não achei hoje o caso em que isso some com um aviso.
- (contagens e situação, suspeita 5) A grade e a página com o "trazer de volta" diferente e a regra duas vezes →
  **virou o achado SP-07**: confirmado; e a regra da D-650 só no aceso do botão.
- (contagens e situação, suspeita 6) "Lombada incerta" / "Não parece dupla" depois de dividir à mão → **virou o achado
  SP-13**: somem ou ficam conforme o botão põe o tique na folha, não por medida nova.


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
