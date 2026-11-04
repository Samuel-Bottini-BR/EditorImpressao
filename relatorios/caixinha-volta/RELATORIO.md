# Caixinha do Dividir que volta marcada: relatório (agente caixinha-volta, 04/11/2026)

Ramo `caixinha-volta-2026-11-04`, que saiu de `obra-2026-10-26` (`50b242c7`).

## Em uma frase

Quando você desmarcava "1 Dividir folhas ao meio" e ainda não tinha clicado em "Rodar", a caixinha voltava
marcada sozinha. Isso acontecia em qualquer Ctrl+Z ou Ctrl+Y, no "Desligar as marcadas" e na caixinha
"Margens iguais" do Cortar. Agora ela fica desmarcada, e nada muda nas folhas.

## O que o Samuel disse

- 03/11 (D-590): "Sim a caixinha continua desmacada."
- 04/11 (print a-67): "depois de usar o dividir e voltar ao automatico ele está marcado de novo."

## Como reproduzi

Usei a janela de verdade, pilotada por mensagens do Windows (`piloto.py`), numa cópia do Gradus.
O projeto veio de `dados-teste-rodada-de-consertos` e foi copiado para o scratchpad.

| Caminho (voltando ao Automático depois de cada um: painel e janela grande) | Dividir desmarcado **e Rodar** | Dividir desmarcado **sem Rodar** |
|---|---|---|
| "não dividir esta" | fica desmarcada | fica desmarcada |
| Ctrl+Z / Ctrl+Y depois dele | fica desmarcada | **volta marcada** |
| "dividir esta", "juntar todas", "dividir todas", aviso da D-613, arrastar a linha, motor de corte | fica desmarcada | **marcada** (desde o 1º Ctrl+Z) |
| os Ctrl+Z / Ctrl+Y de cada um | fica desmarcada | **volta marcada** |
| caixinha "Margens iguais" do Cortar | — | **volta marcada** |
| "Desligar as marcadas" | — | **volta marcada** |
| Rodar só o Limpar | fica desmarcada | (o Rodar desliga o Dividir no livro) |
| fechar e abrir | fica desmarcada | volta marcada (pergunta 1) |

As anotações estão em `anotacoes-antes-rodar.txt` e `anotacoes-antes-sem-rodar.txt` (código de antes).
Em `prints/` ficaram 16 prints, os do antes e os do depois nos mesmos passos.
Os outros 206 prints, um por passo, estão no scratchpad do agente:
`C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\caixinha\todos-os-prints`.
O print `prints/antes-sem-rodar-10-1-nao-dividir-esta-ctrl-z-janela-grande.png` é igual ao a-67 do
Samuel: "1 Dividir" marcado, "ligada no livro todo", "4 Limpar" em Preto e branco, só as letras,
"Rodar 2 etapas".

**Efeito grave, visto no piloto.** Depois que a caixinha voltava marcada sozinha, um "Desligar as
marcadas" desligava também o Dividir e **juntava as 70 folhas**
(`anotacoes-antes-sem-rodar.txt`, passo 8b).

**O histórico da pasta de teste combina com isso.** O `acoes.jsonl` do Gradus mostra só duas ações:
um Rodar às 14:39 e um Rodar com o Dividir marcado às 14:40. Entre 14:40 e o print das 14:53, nenhum
Rodar desmarcou o Dividir no livro.

## A causa

Esses caminhos releem o livro para mostrar no painel:

- `ui/tela_conferir._reacertar_as_opcoes`, no desfazer e no refazer;
- `ui/tela_conferir._mudar_margens_iguais`;
- `ui/janela_principal._aplicar_o_automatico`, no fim do Rodar e do "Desligar as marcadas".

A releitura (`ui/automatico.EstadoDoAutomatico.do_projeto`) marca toda etapa que está ligada no livro.
O Dividir desmarcado e ainda sem Rodar continua ligado no livro (`Projeto.dividir_folhas`), então
voltava marcado. O conserto de 03/11 só cobria o caso **com** Rodar.

## O conserto

- `EstadoDoAutomatico.do_projeto(..., manter_o_dividir_desmarcado=False)`: com `True`, a caixinha do
  Dividir que a pessoa desmarcou continua desmarcada depois da releitura.
  Isso vale só para o Dividir e só quando ele está desmarcado. A caixinha marcada e as outras etapas
  seguem o livro, como antes.
- Desfazer/refazer: usa `True` quando a ação não mexe no Dividir do livro (`_mexe_no_dividir_do_livro`).
  O Ctrl+Z do próprio Rodar que mudou o Dividir continua mostrando o livro, como antes (pergunta 2).
- "Margens iguais" do Cortar e fim do Rodar / "Desligar as marcadas": `True`.
- A ferramenta Dividir não mudou em nada: dividir, juntar, linha, motor e aviso continuam iguais.

## Depois do conserto, na janela de verdade

As anotações estão em `anotacoes-depois-sem-rodar.txt` e `anotacoes-depois-rodar.txt`. Os prints
estão em `prints/depois-*`.

- **Sem Rodar.** Todos os caminhos deixam a caixinha desmarcada, inclusive o "Desligar as marcadas".
  Nele, as folhas continuam divididas (antes, o programa juntava todas).
  Só o "fechar e abrir" volta a marcar: é a pergunta 1.
- **Com Rodar.** Tudo continua desmarcado, como já era.
- **Ressalva.** No piloto, o clique na caixinha "Margens iguais" do Cortar não ligou as margens: a
  caixinha não estava ao alcance do clique. Então esse caminho foi provado só pelo teste fora da tela
  (`test_d590_dividir_desmarcado_e_margens_iguais_do_cortar_nao_o_marcam`).

## Testes

- Novo: `tests/test_caixinha_do_dividir_nao_volta.py`, com 9 testes.
  - No código de `50b242c7`, **8 falham**. O 9º confere o que já era e passa nos dois.
  - No conserto, os 9 passam.
- Antigos, um arquivo por vez no PC, todos passando:
  - `test_dividir_desmarcada_caixinha`: 3
  - `test_decisoes_juntar_todas`: 4
  - `test_decisoes_montar_cadernos`: 13
  - `test_opcoes_da_gravura_na_tela`: 15
  - `test_decisoes_dividir`: 21
  - `test_decisoes_dividir_aviso`: 11
  - `test_decisoes_dividir_arrastar`: 16
  - `test_decisoes_dividir_linha`: 13
  - `test_decisoes_dividir_metade`: 6
  - `test_dividir_ajustes_03_11`: 9
  - `test_dividir_na_tela`: 9
  - `test_decisoes_automatico`: 29
  - `test_decisoes_automatico_opcoes_do_filtro`: 21
  - `test_decisoes_automatico_ver_como_fica`: 22
  - `test_decisoes_automatico_margens_no_depois`: 5
  - `test_decisoes`: 26
  - `test_historico_depois_de_reabrir`: 11
  - `test_recomeco_limpa_o_historico`: 13
  - `test_automatico_pular_depois_de_dividir`: 4
  - `test_cartoes_seguem_as_caixinhas`: 5
  - `test_decisoes_previa_dividida`: 4
- Nenhum teste antigo mudou.

## Perguntas abertas (para o Samuel)

1. Você desmarca o Dividir, não clica em "Rodar" e fecha o livro. Ao abrir de novo, a caixinha aparece
   marcada, porque o livro ainda tem o Dividir ligado. Ela deve continuar desmarcada? Para isso, o
   programa precisaria guardar a caixinha desmarcada no trabalho.
2. Você desmarca o Dividir e clica em "Rodar". Depois aperta Ctrl+Z, que desfaz esse Rodar. O Dividir
   volta ligado no livro, e a caixinha volta marcada, como hoje. Está bom assim?
3. Achado: as caixinhas "Montar cadernos" e "Margens iguais" também voltam marcadas quando são
   desmarcadas sem Rodar e se aperta Ctrl+Z. Conferi isso fora da tela, com um livro de 3 folhas.
   "Gravuras e fotos" deve ser igual, mas não conferi. Isso não foi consertado, porque a tarefa era só o
   Dividir. Quer o mesmo conserto nelas?
