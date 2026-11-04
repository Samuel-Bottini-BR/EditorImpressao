# ONDE-PAREI — ajustes do Dividir e da janela do Automático (03/11/2026)

Ramo `dividir-ajustes-2026-11-03`, saiu de `obra-2026-10-26` em `75ed04af`. Cópia (worktree):
`D:\programas\EditorImpressao\.claude\worktrees\dividir-ajustes`. Quem chama: a gerente.

## Decisões que esta tarefa precisa cumprir

- **D-605 (03/11):** "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já
  está escolhido e testado, coisas novas não podem criar novos problemas".
- **D-606 (03/11):** "Ele deve fazer a conta novamente com o novo motor" (na folha juntada de volta, trocar o motor de
  corte refaz a conta e a linha vai para onde o motor novo acha).
- **D-607 (03/11):** "só temos que mudar o aviso, avisar que as páginas foram juntadas e que vão ser separadas se o
  processar continuar."
- **D-602 (03/11):** linha azul na folha inteira, "dividir esta" corta nela, "dividir todas" corta cada folha na sua
  linha, a lista do motor nunca trava (`tests/test_decisoes_dividir_linha.py` continua passando sem mudança).
- **D-498:** "não dividir esta" devolve a linha de antes. **D-090:** "usar em todas" copia a linha desta folha.
  **D-601:** arrastar a linha em "Duas lado a lado".
- **D-004:** "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas mexidas." (só o texto do
  aviso muda). **D-590:** caixinha do Dividir desmarcada fica desmarcada.

## O que já está escolhido e testado aqui (D-605, escrito antes de mexer)

Telas e arquivos que vou tocar: ferramenta Dividir (`ui/tela_conferir.py`), a tira de miniaturas
(`ui/widgets/tira_miniaturas.py`), a pergunta das mexidas (`ui/janela_principal.py._perguntar_mexidas`,
`core/automatico.paginas_mexidas`), a etapa 6 da janela grande do Automático (`ui/automatico.py._opcoes_margens`).

Decisões que já valem ali e não podem mudar:
- D-602 (linha antes de cortar; "dividir esta"; "dividir todas"; lista nunca cinza; "motor de corte").
- D-498 ("não dividir esta" junta e guarda; "dividir esta" devolve como estava, na linha de antes) — continua valendo
  enquanto o motor não é trocado.
- D-090 ("usar em todas" abre a lista, copia a linha desta folha, exceções desmarcadas).
- D-601 ("Uma página" mostra a metade; "Duas lado a lado" a folha com a linha para arrastar; tira com duas miniaturas
  por folha dividida).
- D-590 ("juntar todas" numa ação; caixinha desmarcada fica desmarcada).
- D-004 / D-485 (a pergunta "Pular as N" / "Rodar nelas também" / "cancelar", a contagem e o que cada botão faz).
- D-373 (nomes das opções do motor: "o do Editor", "o do ScanTailor").
- D-021 e etapa 9b-1 (as setas, Page Up/Down, Home/End trocam de página/folha; "o teclado fica com a página": as listas
  da área de trabalho não roubam as setas — `setFocusPolicy(Qt.NoFocus)` nos outros combos).
- D-577 / D-603 (janela grande do Automático: três colunas, prévia antes/depois à direita).

Testes que já existem e têm de continuar passando sem mudança:
`tests/test_decisoes_dividir_linha.py`, `tests/test_decisoes_dividir.py`, `tests/test_decisoes_dividir_metade.py`,
`tests/test_decisoes_juntar_todas.py`, `tests/test_dividir_desmarcada_caixinha.py`, `tests/test_dividir_na_tela.py`,
`tests/test_dividir_no_programa.py`, `tests/test_automatico_pular_depois_de_dividir.py`,
`tests/test_decisoes_automatico*.py`, `tests/test_decisoes_9b1.py`, `tests/test_decisoes_9b2.py`,
`tests/test_miniaturas_novas.py`, `tests/test_decisoes_avisos.py`, `tests/test_decisoes_caderno_tela_grande.py`.

## Andamento

- [x] 1. D-606 motor na folha juntada (commit "D-606: ...")
- [x] 2. D-607 aviso depois do "juntar todas"
- [x] 3. setas depois da lista "motor de corte"
- [x] 4. tira depois do Ctrl+Z
- [x] 5. "7 com dúvida": são os "Parece em branco" (D-497) das metades esquerdas brancas das folhas
  2, 3, 7, 8, 62, 63, 69; "dividir esta" nessas mesmas folhas dá os mesmos 7. Não é defeito: nada mudou.
- [x] 6. etapa 6 cortada em 1536 x 824
- [x] testes antigos no PC, um por vez (23 arquivos, todos passaram; nenhum teste antigo mudou)
- [x] reversão: os testes novos falham em 75ed04af
- [x] GitHub, conjunto inteiro + teste_botoes: 41759151010 passou (na 1ª tentativa a parte 5 falhou em
  `test_gravura_na_aba_marcar.py::test_pagina_de_projeto_antigo_que_muda_de_forma_e_refeita`, que passa 3 de 3 no PC
  e passou ao repetir só a parte que falhou: tempo, área não tocada)
- [ ] GitHub, filtro de velocidade 41759125497: rodando na entrega (limite de consultas do GitHub esgotado pelos meus vigias); a gerente confere
- [x] prints na janela de verdade (Gradus): p01 a p08
- [x] relatório: relatorio.md

## Perguntas para o Samuel

1. Botões do painel ficam com o teclado: depois de clicar em "dividir esta", "juntar todas" etc. (e nos botões das
   outras ferramentas, como "não cortar esta"), as setas passam de um botão a outro em vez de trocar de folha. A lista
   "motor de corte" já não faz isso. Fazer os botões do painel também deixarem o teclado com a página, em todas as
   ferramentas? (Não feito: muda todas as ferramentas.)

---

# Tarefa nova (03/11/2026, pedido da gerente depois da leitura do Samuel)

Samuel: "cara, ele burlou a regra, colocou um defeito novo, concerta isso ai, pode fazer o teste no meu pc mesmo se
não está dando certo no git hub".

## 1. Ctrl+Y depois do "dividir todas" perdia os 7 "Parece em branco"

- Prova de onde vem (Gradus, mesmo caminho, offscreen, pasta própria):
  - `75ed04af`: dividir todas 7 → Ctrl+Z 0 → Ctrl+Y **0** (perdia).
  - `abd8cd0a`: dividir todas 7 → Ctrl+Z 0 → Ctrl+Y **0** (perdia igual).
  - "dividir esta" só na folha 7 (abd8cd0a): 1 → 0 → **0**. Ou seja: já existia antes destes ajustes e antes da
    D-602; vem da etapa 7 (27/10), quando a medida do em branco por trás entrou (o refazer nunca mediu).
- Conserto: `TelaConferir.refazer` → `_medir_o_em_branco_ao_refazer` (mede como o `_registrar`). Commit `046c5b3b`.
  Depois: Ctrl+Y 7 de novo, nas mesmas folhas. Teste `test_reversao_refazer_devolve_o_parece_em_branco` (2 casos),
  falha em abd8cd0a/75ed04af.
- Ida e volta completa (14 Ctrl+Z/Ctrl+Y comparando páginas, avisos, linha e motor): no novo, 14 de 14 iguais; em
  75ed04af, 5 diferentes (todas pela mesma causa). Print p09.

## 2. D-608 (03/11): botões do painel não seguram as setas

Pergunta: "Quer que, depois de clicar num botão do painel, as setas continuem passando de página, em todas as
ferramentas? As caixas de número continuam como estão." → "ok".

### O que já está escolhido e testado sobre teclado (escrito antes de mexer)
- D-021: Page Up/Down andam 10 páginas, Home/End, a roda; `tests/test_decisoes_ver.py::test_d021_*`.
- Etapa 9b-1 (foco preso): a lista do painel Automático e a tira não seguram o teclado;
  `tests/test_decisoes_9b1.py::test_teclas_chegam_a_pagina_depois_de_clicar_na_lista_do_automatico`,
  `test_page_down_chega_a_pagina_depois_de_clicar_numa_miniatura`.
- Lista única 1.10 (etapa 9b-2): Tab vai à próxima dúvida mesmo com o foco num botão (filtro único `_FiltroDaTab`);
  `tests/test_decisoes_9b2.py::test_lista_1_10_*`.
- Botões dos avisos não ficam com o teclado (13/10); `tests/test_para_revisar_na_tela.py::test_os_botoes_do_aviso_nao_ficam_com_o_teclado`.
- D-083: Endireitar com o ângulo em número (setas de 0,1°); `tests/test_endireitar_g5.py` (inclui
  `test_setas_giram_e_gravam_numa_acao_so`, `test_numero_digitado_grava`).
- Atalhos e teclas: `tests/test_atalhos.py`, `tests/test_girar_na_tela.py::test_as_teclas_do_giro_*`,
  `tests/test_decisoes_mover.py::test_letra_f_*`, `tests/test_promessas.py` (p163, p211 setas),
  `tests/test_decisoes_dividir_metade.py::test_d601_*_setas_andam_pelas_paginas`.
- Espaço = "Marcar como certo e avançar" (atalho); num botão com o teclado, o Espaço aperta o botão (do Qt). Não muda.

### Feito (D-608)
- `ui/tela_conferir.py`: `TECLAS_DE_ANDAR_NUM_BOTAO`, `_FiltroDaTab` (também as teclas de andar),
  `TelaConferir._tecla_de_andar_num_botao`. Último commit `42f359a4`. Testes `test_reversao_d608_*` (2, falham
  em 75ed04af) e `test_d608_caixa_de_numero_do_angulo_continua_com_as_setas`. Prints p10, p11.

## 3. Testes no PC (sem GitHub)
- 36 arquivos, um por vez, todos passaram (lista no relatório). Nenhum teste antigo mudou.
- Velocidade: não medida no PC (Samuel: "se está medindo lá porque medir aqui..."). O GitHub 41759125497 fica com a
  gerente. Nada novo em `core/` nesta segunda parte.

## Perguntas para o Samuel
(nenhuma aberta; a dos botões virou D-608 e foi feita)
