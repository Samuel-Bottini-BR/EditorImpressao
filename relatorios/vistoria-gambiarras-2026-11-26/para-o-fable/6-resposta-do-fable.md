# Resposta do Fable à vistoria da tela de trabalho (27/11/2026)

Colada pelo Samuel no chat da gerente em 27/11/2026, sem mudar nada. Vale junto com a `ordem-de-servico.md`; onde as
duas diferem, vale esta (é a mais nova).

---

Resposta do Fable à vistoria da tela de trabalho (27/11). Decisão do Samuel: a vistoria continua pelo programa inteiro, antes de qualquer conserto.

1. A lista da tela está aprovada como mapa. O Fable conferiu seis achados no código (G-03, G-06, G-12, SP-05, SP-15, DF-01): os seis batem. Nada a refazer nela.

2. Não espere: continue agora, com a mesma ordem de serviço, nesta ordem de pedaços (a sua divisão, reordenada: primeiro o que toca as raízes da tela):
   1 peças da tela de trabalho · 2 preparar a página · 3 filtros e limpeza · 5 Automático e avisos · 7 gerar o PDF e cadernos · 6 abrir, guardar e desfazer · 4 gravuras e marcações · 9 achar texto · 10 ferramentas do Samuel · 8 atualizador (só tipos 4 e 5: peças de proteção e código morto; o resto já passou por cinco rodadas).
   Cada pedaço grande da sua tabela pode ser partido em pedaços menores por assunto, como foi na tela. Começar pela suspeita aberta (core/pipeline._guardar_o_conteudo).

3. Fora da vistoria, como você sugeriu: os 33 scripts soltos de teste e régua, e regras_dos_agentes/.

4. Dois ajustes para os próximos pedaços (não refazer a tela):
   a) Quando o achado for "a mesma expressão em N lugares", contar por busca no programa inteiro e listar todas (o G-12 dizia 5 lugares; são 12).
   b) GRAVE só quando o conserto errado chega na tela do Kaique ou no PDF; "3 ou mais lugares" sozinho é médio. O resto da régua fica.

5. Em cada achado novo, além do item da Central, dizer a qual achado da tela ele é "outra cópia", quando for (ex.: "outra cópia do SP-03"). É isso que vai juntar os 81 + os novos em raízes.

6. Entrega: ao fim de cada pedaço grande da tabela, uma linha no chat com o tempo e as contagens. Ao fim de tudo, a mesma pasta para-o-fable refeita, com um resumo novo de duas páginas: as raízes (grupos de achados que são a mesma regra espalhada), quantos achados cada uma junta, e quais itens da Central cada uma explica. O Fable lê antes de qualquer conserto começar.

7. No fim, junto com o resumo das raízes: ler a Central DE NOVO, da página, como estiver naquele dia (não a cópia de 26/11), e entregar uma tabela com todos os itens em "pode consertar" / "na fila" — para cada um, uma de três respostas: "explicado pelo achado X", "nenhum achado ainda", ou "não é gambiarra: defeito simples, conserto próprio". O que o Samuel responder na Central durante a vistoria entra nessa tabela.

Nenhuma linha de código muda até lá.

---

## Os pedaços grandes, com os arquivos de cada um (a divisão da gerente, `para-o-fable/2-o-que-falta-vistoriar.md`)

Na ordem do item 2 acima. Os números são os da tabela da gerente.

1. **Peças da tela de trabalho** (27 arquivos, 15.041 linhas): `ui/widgets/paineis.py`, `visualizador.py`,
   `editor_selecao.py`, `tira_miniaturas.py`, `filtros_tela_cheia.py`, `todas_as_paginas.py`, `trilha_agrupada.py`,
   `paginas_rolando.py`, `paginas_lado_a_lado.py`, `barra_girar.py`, `escolhas_do_misto.py`, `miniaturas.py`,
   `trilha_ferramentas.py`, `menu_com_amostra.py`, `barra_opcoes.py`, `cartao_filtro.py`, `medidor.py`,
   `roda_de_lado.py`, `bolinha.py`; `ui/tela_ampliada.py`, `ui/desfazer_nesta_pagina.py`, `ui/barra_de_menu.py`,
   `ui/estilo.py`, `ui/rodinha.py`, `ui/perguntas.py`, `ui/janela_confirmar.py`, `ui/dialogo_escolher_paginas.py`.
   Mais os trechos de `ui/tela_conferir.py` que a vistoria da tela deixou sem ler (ver ONDE-PAREI).
2. **Preparar a página** (21, 13.290): `core/pipeline.py`, `girar.py`, `dividir.py`, `dividir_a_mao.py`,
   `dividir_scantailor.py`, `recortar.py`, `corte_pelo_conteudo.py`, `borda_preta.py`, `endireitar.py`,
   `endireitar_scantailor.py`, `desentortar_scantailor.py`, `folha.py`, `etapas.py`, `ordem_do_preparo.py`,
   `caixas_scantailor.py`, `margens_scantailor.py`, `ajustar_pedaco.py`, `guias.py`, `linhas_do_texto.py`,
   `unidades.py`, `paginas_diferentes.py` (todos em `core/`).
3. **Filtros e limpeza** (14, 9.346): `core/filtros.py`, `misto.py`, `camadas.py`, `duas_camadas.py`,
   `fundo_tirado.py`, `claro_no_escuro.py`, `preto_e_branco_scantailor.py`, `cores_scantailor.py`, `luz_scantailor.py`,
   `pontinhos_scantailor.py`, `st_ferramentas.py`, `perfis.py`, `nucleos.py`, `aquecimento.py`.
5. **Automático e avisos** (7, 7.088): `ui/automatico.py`, `core/automatico.py`, `core/analise.py`, `core/revisar.py`,
   `core/avisos.py`, `core/paginas_em_branco.py`, `ui/janela_dos_avisos.py`.
7. **Gerar o PDF e cadernos** (8, 4.748): `core/impressao.py`, `core/cadernos.py`, `core/impressora.py`,
   `core/ordem_das_paginas.py`, `ui/dialogo_impressao.py`, `ui/widgets/folhas_do_caderno.py`, `ui/tela_final.py`,
   `ui/dialogo_tamanho_da_folha.py`.
6. **Abrir, guardar e desfazer** (19, 13.021): `projetos.py`, `modelos.py`, `historico_acoes.py`, `historico.py`,
   `configuracoes.py`, `atalhos.py`, `registro.py`, `core/pdf_io.py`, `core/paginas_em_outro_processo.py`,
   `ui/tela_inicio.py`, `ui/janela_principal.py`, `ui/tarefas.py`, `ui/tela_opcoes.py`, `ui/tela_configuracoes.py`,
   `ui/dialogos_de_arquivo.py`, `ui/tela_de_carregamento.py`, `ui/widgets/area_arrastar.py`, `ui/widgets/folhear_pdf.py`,
   `ui/widgets/destino.py`.
4. **Gravuras e marcações** (6, 3.860): `core/detectar_regioes.py`, `selecao.py`, `zonas_na_folha.py`,
   `editar_zonas.py`, `gravura_scantailor.py`, `rede_selecao.py`.
9. **Achar texto** (7, 2.551): `core/ocr_kraken.py`, `ocr_tesseract.py`, `ocr_doctr.py`, `ocr_comum.py`,
   `ocr_comparar.py`, `ocr_diagnostico.py`, `motor_kraken/servidor_kraken.py`.
10. **Ferramentas do Samuel** (9, 5.624): `empacotar.py`, `publicar_versao_kaique.py`, `servidor_das_versoes.py`,
    `montar_motor_kraken.py`, `compilar_detector_gravura.py`, `compilar_st_ferramentas.py`,
    `core/pasta_das_ferramentas.py`, `gerar_brasao.py`, `relatorio.py`.
8. **Atualizador** (13, 8.220), **só tipos 4 e 5**: `atualizacao.py`, `main.py`, `versao.py`, `assinatura.py`,
   `brasao.py`, `core/windows.py`, `core/fases_da_atualizacao.py`, `core/conversa_com_o_velopack.py`,
   `core/testes_a_distancia.py`, `core/_testes_a_distancia_windows.py`, `ui/aviso_de_atualizacao.py`,
   `ui/testes_a_distancia_ui.py`, `ui/brasao_girando.py`.
