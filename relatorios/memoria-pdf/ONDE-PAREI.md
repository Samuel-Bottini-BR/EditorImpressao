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

- [ ] 1. Medir (3 tamanhos, processar + cadernos + livreto)
- [ ] 2. Consertar a causa (se for do programa)
- [ ] 3. D-591 (aviso + "tentar de novo")
- [ ] 4. Testes no PC, push, GitHub
- [ ] 5. Relatório em três formatos

## Perguntas para o Samuel

(nenhuma até agora)
