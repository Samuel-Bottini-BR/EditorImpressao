# ONDE-PAREI — memória ao processar e gerar o PDF (04/11/2026)

Ramo `memoria-pdf-2026-11-04` (saiu de `obra-2026-10-26`), cópia `.claude/worktrees/memoria-pdf`.

Pedido do Samuel: "aquele problema de quando o pdf era grande demais, ou faltava memoria e ele cancelava a
geração do pdf ou o processamento foi resolvido?" → "Sim, quero que coloque um agente para tentar resolver
esse problema."

## Decisões que esta tarefa precisa cumprir

- **CLAUDE.md §3:** "Uma página por vez na memória. O pico não pode crescer com o tamanho do livro; há livro de
  300 MB no acervo. Nunca montar lista com todas as páginas processadas." · "Interface nunca congela." ·
  "Nenhuma exceção fecha a janela."
- **D-591 (31/10, Central 2-12):** escolheu "Frase certa + botão "tentar de novo" (recomendo)": "Faltou memória
  no computador: outros programas abertos estão usando quase toda a memória. Feche o que não estiver usando.
  Nada do seu trabalho no livro se perdeu.", com "tentar de novo" (processa de novo, mesmo nome e lugar) e
  "entendi".
- **D-304:** "o tamanho do arquivo depois não importa" — PDF sem perda.
- **D-549:** "os agentes estão mudando coisas que eu já tinha definido, é só para fazer o que eu já tinha
  mandado [...]" — a D-531 (limitar resolução) cancelada, o JPEG 92 desfeito. Não reduzir resolução nem
  comprimir sem perguntar.
- **D-364:** várias páginas ao mesmo tempo, de fábrica todos os núcleos, "cortado pela memória livre".
- **D-605 (03/11):** "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está
  escolhido e testado, coisas novas não podem criar novos problemas".
- **Bug de 05/10 (Lista de bugs):** cancelar com "substituir o antigo" apagava o PDF antigo. O PDF antigo de
  mesmo nome nunca pode sumir por um cancelamento ou erro.

## O que já está escolhido e testado aqui

- `core/pdf_io.EscritorPDF`: páginas em zlib nível 9, sem perda (D-304, etapa 9d);
  `tests/test_gravar_pdf_sem_parar_a_janela.py` (mesmos pixels, janela não para),
  `tests/test_etapa10b_imagem.py::test_d304_pagina_de_tons_vai_sem_perda`, `tests/test_duas_camadas.py`
  (duas camadas, opção desligada de fábrica).
- `core/pipeline.processar`: PDF novo num `~nome.pdf.parcial` e troca no fim; cancelar/erro nunca toca no
  antigo; antigo preso → "nome (2).pdf" (`tests/test_substituir_e_cancelar.py`).
- `core/nucleos.py` (D-364): PDF idêntico com 1 e com N trabalhadores (`tests/test_nucleos.py`).
- `core/cadernos.impor_pdf` ("Montar cadernos"): `tests/test_cadernos.py`, `tests/test_decisoes_montar_cadernos.py`,
  `tests/test_decisoes_caderno_tela_grande.py`.
- `core/impressao.montar_para_impressao` (livreto): `tests/test_impressao.py`, `tests/test_decisoes_impressao.py`,
  `tests/test_decisoes_livreto_ver.py`.
- `ui/tarefas._mensagem_amigavel` e `ui/janela_principal._falhou_no_processamento`: hoje a frase antiga
  ("Este livro ficou grande demais...") — é ela que a D-591 manda trocar.

## Andamento

- [x] 1. Medir. **Causa achada:** o PDF novo era montado inteiro na memória até o save do fim
  (`core/pdf_io.EscritorPDF`, `core/cadernos.impor_pdf`, `core/impressao.montar_para_impressao` e `_achatar`).
  Rhetorica, uma página por vez: 30 folhas 1.665 MB, 90 folhas 1.891 MB, 270 folhas caiu por falta de memória
  (`_ArrayMemoryError`, 16:21). Livreto: 30 folhas 2.142 MB, 90 folhas 3.102 MB. Mais: `caixa_da_tinta` (avisos
  do livreto) enchia o armazém do MuPDF (até 256 MB).
- [x] 2. Conserto: `core/pdf_io.PDFQueVaiParaODisco` (vai ao disco a cada 64 MB e reabre; um save normal no
  fim, mesmas opções). Depois: 30 folhas 1.652 MB, 90 folhas 1.664 MB.
- [x] 3. D-591: frase em `ui/tarefas.FRASE_FALTOU_MEMORIA`, `faltou_memoria()`, `TarefaProcessar.faltou_memoria`,
  `JanelaPrincipal._avisar_falta_de_memoria` ("tentar de novo" / "entendi") e `_comecar_a_processar`.
- [x] Testes novos: `tests/test_memoria_nao_cresce_com_o_livro.py` (11, os 4 de pico falham no código antigo:
  +46, +46, +46, +99 MB) e `tests/test_decisoes_aviso_de_memoria.py` (15; 14 falham no antigo).
- [x] 4. Medidas "depois" terminadas (05/11): Rhetorica 270 folhas pronto, pico 1.674 MB (antes caía);
  livreto 90 folhas 1.656 MB (antes 3.102 MB). Tabela: `tabela_das_medidas.py`; gráfico: `grafico.png`.
- [x] 4b. **Lentidão achada e consertada (05/11).** Ao comparar a velocidade, o conserto de 04/11 deixava
  livro grande mais lento: o `saveIncr` do MuPDF relê o arquivo ao lado inteiro a cada ida ao disco. Agora
  `core/pdf_io._acrescentar_so_o_novo` acrescenta só o que entrou (detalhe abaixo). Commit `df514cb4`.
- [x] 5. Junção com `obra-2026-10-26` (05/11, sem conflito; a obra não mexeu nos arquivos do conserto).
- [ ] 6. GitHub: testes 41951184818, velocidade 41951188321 (ver "Testes").

## A causa, em português simples

**O programa guardava o livro novo inteiro na memória até o fim, e só então gravava o PDF no disco.**
Quanto maior o livro, mais memória; num livro grande (Rhetorica) a memória do computador acabava e
aparecia "Este livro ficou grande demais para a memória do computador".

Os números: no Rhetorica, uma página por vez, a memória do programa foi a 1.665 MB com 30 folhas, 1.891 MB
com 90 folhas e, com 270 folhas, acabou a memória e caiu. No livreto ("Montar para imprimir") era pior:
2.142 MB com 30 folhas e 3.102 MB com 90. Era defeito do programa (regra do CLAUDE.md §3: "o pico não pode
crescer com o tamanho do livro").

**O conserto:** as páginas prontas vão para um arquivo de trabalho no disco de 64 em 64 MB, e no fim o
programa grava o PDF do mesmo jeito de antes. Depois do conserto a memória fica parada em ~1.650 MB, seja o
livro de 30, de 90 ou de 270 folhas (270 folhas: 1.674 MB, pronto). O PDF sai igual, sem perda.

**A lentidão achada no caminho (05/11):** a primeira versão do conserto usava a gravação "acrescentando no
fim" do MuPDF, que relê o arquivo de trabalho inteiro cada vez. Num livro de 935 MB cada ida ao disco passava
de 0,05 s para 3 s (21 s no total; antes do conserto, nada disso existia). Agora o programa acrescenta só o
que é novo: ~0,1 s por ida, qualquer que seja o tamanho (1,4 s no total no mesmo livro), mais ~2 s na
gravação do fim. Num livro que leva ~14 min para processar, isso é perto de 0,4%. Livro com PDF menor que
64 MB nunca vai ao disco antes do fim: caminho idêntico ao de antes.

## Como cumpri cada decisão

- **CLAUDE.md §3 ("uma página por vez na memória", "o pico não pode crescer com o tamanho do livro"):**
  `core/pdf_io.PDFQueVaiParaODisco` no processar, nos cadernos e no livreto. Prova: medidas do Rhetorica
  acima e `tests/test_memoria_nao_cresce_com_o_livro.py` (livro de N e de 3N páginas, mesmo pico; no código
  antigo o pico cresce 46, 46, 46 e 99 MB).
- **D-591 (frase + "tentar de novo" / "entendi"):** `ui/tarefas.FRASE_FALTOU_MEMORIA` tem a frase palavra por
  palavra; `_avisar_falta_de_memoria` mostra os dois botões; "tentar de novo" processa de novo para o mesmo
  arquivo, sem perguntar o destino. Prova: `tests/test_decisoes_aviso_de_memoria.py` (15 casos; 14 falham no
  código antigo); a frase antiga saiu (`test_d591_a_frase_antiga_saiu`).
- **D-304 (sem perda) e D-549 (não reduzir resolução nem comprimir sem perguntar):** nada muda na imagem; os
  dados vão como estão guardados. Prova: `test_*_o_pdf_e_o_mesmo_indo_ao_disco` e
  `test_ir_ao_disco_acrescenta_so_o_novo_sem_o_save_incremental` (mesmas imagens byte a byte, mesmo desenho,
  mesmo texto, indo ou não ao disco); `test_d304_pagina_de_tons_vai_sem_perda` continua passando.
- **D-364 (várias páginas ao mesmo tempo):** nada mudou na conta de trabalhadores; `tests/test_nucleos.py` passa.
- **D-605 (o novo não estraga o testado) e bug de 05/10 (o PDF antigo nunca some):** nenhum teste antigo foi
  mudado; cancelar ou falta de memória depois de ir ao disco deixa o antigo idêntico e não sobra arquivo
  (`test_cancelar_depois_de_ir_ao_disco_mantem_o_antigo`, `test_falta_de_memoria_depois_de_ir_ao_disco_mantem_o_antigo`).
- **Velocidade ("nenhuma mudança pode deixar o programa mais lento"):** a lentidão da primeira versão foi
  achada e consertada (acima); reserva testada em `test_se_o_acrescimo_falhar_volta_ao_do_mupdf_e_o_pdf_sai_o_mesmo`.
  Filtro do GitHub: rodada 41951188321.

## Bugs para a Lista de bugs (não consertados: ficam na tela, fora do processar)

- 05/11/2026, `ui/dialogo_impressao.py` ("Imprimir agora"): copia as páginas escolhidas para um PDF na memória
  (`insert_pdf`) antes de mandar à impressora. Escolhendo o livro inteiro, o PDF pronto todo vai para a memória
  (Rhetorica 270 folhas: 921 MB). Pode dar falta de memória num livro grande.
- 05/11/2026, `ui/tela_conferir.py` ("Extrair as páginas escolhidas"): o mesmo, com as folhas escolhidas do
  livro original.

## Perguntas para o Samuel

(nenhuma: tudo o que mudou é técnico, dentro da alçada de memória e velocidade do CLAUDE.md §6)
