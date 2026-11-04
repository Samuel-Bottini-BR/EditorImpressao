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

- [ ] 1. D-606 motor na folha juntada
- [ ] 2. D-607 aviso depois do "juntar todas"
- [ ] 3. setas depois da lista "motor de corte"
- [ ] 4. tira depois do Ctrl+Z
- [ ] 5. "7 com dúvida" (investigar)
- [ ] 6. etapa 6 cortada em 1536 x 824

## Perguntas para o Samuel

(nenhuma ainda)
