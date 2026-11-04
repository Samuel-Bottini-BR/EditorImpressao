# Caixinha do Dividir que volta marcada (agente caixinha-volta, 04/11/2026)

Ramo `caixinha-volta-2026-11-04` (saiu de `obra-2026-10-26`, `50b242c7`).

## O defeito

Samuel, 04/11 (print a-67): "depois de usar o dividir e voltar ao automatico ele está marcado de novo."
D-590, 03/11: "Sim a caixinha continua desmacada."

## Decisões que esta tarefa precisa cumprir

- D-590: "Dividir" desmarcada no Automático não junta nada; Dividir desmarcada + Rodar → as folhas continuam
  divididas e a caixinha fica desmarcada ("Sim a caixinha continua desmacada.").
- D-589: o que está desmarcado não é feito e não volta marcado sozinho.
- D-601, D-602, D-606, D-607, D-609, D-610, D-613: o que a ferramenta Dividir faz nas folhas (metade, linha azul,
  "dividir esta", "dividir todas", motor de corte, aviso do "juntar todas", arrastar a linha, ir para "Uma
  página", aviso das juntadas à mão). Nada disso muda.
- D-605 (CLAUDE.md §11.8): o novo não estraga o que já está escolhido e testado.

## O que já está escolhido e testado aqui

- `core/automatico._desligar_as_desmarcadas` desliga o Dividir desmarcado no Rodar (só `dividir_folhas`,
  nunca as folhas): `tests/test_dividir_desmarcada_caixinha.py` (3 testes).
- O Ctrl+Z do Rodar que desligou o Dividir traz o Dividir "ligado no livro todo" de volta
  (`test_d590_dividir_desmarcada_o_desfazer_volta_a_ligar`).
- "O Automático acompanha o desfazer e o refazer" (verificador 30/09, r15): depois do Ctrl+Z/Ctrl+Y o painel
  relê o livro (`ui/tela_conferir._reacertar_as_opcoes` → `EstadoDoAutomatico.do_projeto`);
  `tests/test_opcoes_da_gravura_na_tela.py::test_o_automatico_acompanha_o_desfazer` (o filtro do livro).
- Caixinhas da D-589: `tests/test_decisoes_montar_cadernos.py`.
- Ferramenta Dividir: `tests/test_decisoes_dividir*.py`, `tests/test_decisoes_juntar_todas.py`,
  `tests/test_dividir_na_tela.py`.
- Automático: `tests/test_decisoes_automatico*.py`.

## Andamento

1. Sonda rápida (fora da tela, livro de 4 folhas): com "Dividir" desmarcado E Rodar, nenhum caminho da
   ferramenta Dividir (não dividir esta, dividir esta, juntar todas, dividir todas, arrastar a linha, motor,
   Ctrl+Z, Ctrl+Y, Rodar só Limpar, fechar e abrir) volta a marcar a caixinha.
   Com "Dividir" desmarcado SEM Rodar: qualquer Ctrl+Z ou Ctrl+Y (de qualquer ação) e o fechar e abrir
   voltam a marcar (o painel relê o livro, que ainda tem o Dividir ligado).
2. A seguir: piloto na janela de verdade com a cópia do Gradus.
