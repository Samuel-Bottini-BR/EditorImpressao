# ONDE-PAREI — girar só a página numa folha dividida (D-618)

Ramo `girar-pagina-2026-11-04` (saiu de `obra-2026-10-26`). Cópia: `.claude/worktrees/girar-pagina`.

## Decisões que esta tarefa precisa cumprir

- **D-618** (04/11, prints a-70 a a-73): "quando ele gira a pagina ele faz ela caber no A4, ele deveria girar o conteudo só
  que é da pagina cortada, mas ele gira a pagina verdadeira do scan. tanto que quando você vai girando ele cai na folha
  branca. Ele gira as duas folhas ao mesmo tempo, faz uma confusão com as paginas." → numa folha já dividida, ¼ e meia
  volta (Propriedades, canto, Ctrl+Seta) giram só a página da tela, já cortada; a outra página e a linha não mudam.
- **Correção do Samuel na D-618 (04/11, recado da gerente):** "não a folha inteira não continua girando como hoje, pois
  hoje quando gira a folha altera a proporção dela para girar ela, e eu não quero que aconteça isso, não sei como deveria
  ser a opção girar duas folhas, mas não deveria ser assim." → investigar onde a proporção muda e escrever o teste que
  mede; **só mudar o comportamento da folha inteira depois da confirmação da gerente.**
- D-030 (girar por botões e menu), D-035 ("Todas ficam viradas como a folha da vez"), D-036 / D-556 (aviso "vá a uma
  folha par"), D-049 (bloco no Propriedades + canto), D-053 (canto gira só esta folha), D-361 (R é só Retângulo; girar
  é Ctrl+Seta), D-367 (lista do girar diz "folha"), D-371 ("daqui em diante"), D-487 (girar na grade), D-601 (Dividir
  "Uma página" mostra a metade), D-609 (linha arrastada na folha inteira, com a rotação anotada).
- CLAUDE.md §6 (campo novo no projeto só com aprovação: o Samuel pediu o conserto; projeto antigo tem de abrir igual),
  §7 (recorte e ângulo moram na página; o giro de 90 vem antes de tudo), §11.8 / D-605.

## O que já está escolhido e testado aqui

Testes do girar: `tests/test_girar.py` (contas, "aplicar em", desfazer, zonas acompanham, prévia = PDF),
`tests/test_girar_na_tela.py` (Propriedades, canto, menu, teclas, aviso pares/ímpares),
`tests/test_girar_cartoes_e_previas.py` (cartões, tira, cache das prévias),
`tests/test_ajustar_pedaco_na_folha_girada.py`, `tests/test_decisoes_automatico.py::test_d334_acoes_nas_escolhidas_girar_e_tirar` (grade),
`tests/test_decisoes_dividir.py::test_lista_3_1_*` e `test_d495_*` (girar a folha inteira e depois dividir),
`tests/test_decisoes_dividir_arrastar.py::test_d609_girar_a_folha_depois_de_arrastar_mostra_a_linha_do_motor`,
`tests/test_paineis_na_tela.py::test_o_bloco_girar_a_folha_fica_no_alto_do_propriedades`,
`tests/test_decisoes.py::test_d095_*`, `tests/test_borda_preta.py::test_regressao_so_o_preto_em_pagina_girada_cunha_branca`,
`tests/test_camadas.py::test_pagina_girada_*`, `tests/test_impressao.py::test_pagina_deitada_gira_de_pe_e_avisa`.

Dividir: `tests/test_decisoes_dividir*.py`, `tests/test_dividir_*.py`, `tests/test_decisoes_dividir_metade.py`.
PDF: `tests/test_pipeline_folha.py`, `tests/test_corte_previa_igual_pdf.py`, `tests/test_cartao_pdf_gerado.py`,
`tests/test_gravar_pdf_sem_parar_a_janela.py`, `tests/test_folhear_pdf.py`.
Cadernos: `tests/test_cadernos.py`, `tests/test_caderno_segue_as_etapas.py`, `tests/test_decisoes_montar_cadernos.py`,
`tests/test_decisoes_caderno_tela_grande.py`, `tests/test_decisoes_impressao.py`.

Regra: nenhum desses muda. A folha inteira (não dividida) continua girando como hoje até a gerente confirmar.

## Perguntas para o Samuel

(abertas conforme o trabalho anda; ver o fim deste arquivo)

## Andamento

- [ ] reproduzir na janela de verdade (antes)
- [ ] provar a causa
- [ ] teste de reversão
- [ ] conserto
- [ ] prints depois, e o que funcionava ao redor
- [ ] investigar a proporção da folha inteira (sem mudar)
- [ ] GitHub
