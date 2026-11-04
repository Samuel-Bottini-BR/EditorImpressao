# ONDE-PAREI — "mover e dimensionar para de funcionar" (04/11/2026)

Ramo `mover-parou-2026-11-04` (saiu de `obra-2026-10-26`, ponta `249922d2`). Cópia:
`D:\programas\EditorImpressao\.claude\worktrees\mover-parou`.

## Decisões que esta tarefa precisa cumprir

- **D-605** (03/11): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que
  já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os
  agentes precisam ler".
- **D-008** (22/09 e 26/10): "quero conseguir redimensionar o conteudo tambem" · "a ferramenta de mover não deveria
  estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" · "como é no photoshope, que você
  arrasta a hora que quiser e aumenta a hora que quiser".
- **D-541** (27/10, apoiada na D-008): arrastar em qualquer lugar da área branca ou da página move (ao vivo); o meio
  do conteúdo fica dentro da área branca; puxar um canto aumenta/diminui na mesma proporção, de 5% até 4 vezes; o
  número "Tamanho do conteúdo (%)" faz o mesmo.
- **D-540** (tecla F), **D-542** (Centralizar e ímã olham o impresso), **D-543**/**D-017** (aviso da parte de fora,
  "Avisar e não reduzir"), **D-544** (Mover separado do Cortar), **D-545** ("usar em todas..."), **D-546**/**D-547**
  (o que cada tela mostra), **D-056** (linhas de apoio).
- Vista da área de trabalho: **D-006**/**D-015** ("Duas lado a lado" = pares rolando, na barra de baixo e no menu
  Ver), **D-601**/**D-609**/**D-610** (no Dividir o "Duas lado a lado" é a folha inteira com a linha; D-610: dividir em
  "Duas lado a lado" passa para "Uma página").

## O que já está escolhido e testado aqui

- `tests/test_decisoes_mover.py` (13 provas da etapa 5: tecla F, área branca, arrastar → PDF, canto, Centralizar,
  %, voltar como veio, D-017, linhas de apoio, "usar em todas...", letra F com foco na página de marcar).
- `tests/test_previa_composta.py`, `tests/test_paineis_na_tela.py`, `tests/test_visualizador.py` (modo do conteúdo).
- Vista: `tests/test_decisoes_ver.py` (fora do Dividir, "Duas lado a lado" = os pares; `test_no_dividir_a_folha_
  inteira_continua`: com a ferramenta "mao", os pares voltam), `tests/test_decisoes_dividir_metade.py`
  (`escolher_ferramenta("mao")` em "Duas lado a lado" → os pares).

## Andamento

(ver abaixo; atualizado a cada passo)
