# Juntar o `fase2-dividir` ao `fase-1` — 07/10/2026

Implementador, numa cópia separada (worktree `.claude/worktrees/juntar-dividir`,
ramo `juntar-dividir-2026-10-07`, saído do `fase-1` em `7d56cec`). O `fase-1` e o
`master` não foram tocados: quem junta é a gerente.

## Em uma frase

O ramo `fase2-dividir` (limpar pontinhos do ScanTailor + item 2.1 Dividir) entrou
no `fase-1` sem nenhum conflito de texto; o livro novo agora vem com "o do
ScanTailor" ao marcar "Dividir folhas ao meio"; e o limpar pontinhos do ScanTailor
**deixou de vir ligado de fábrica** (ver a ressalva 1: para isso tive de trocar o
`PADRAO`, que no ramo era o do ScanTailor "pouco").

## Commits do ramo

| commit | o quê |
|---|---|
| `3c1fafe` | merge do `fase2-dividir` (`eebe358`) no `fase-1` (`7d56cec`) |
| `b528f38` | decisão 1: livro novo divide com "o do ScanTailor" |
| `c951b70` | decisão 2: o do ScanTailor não vem mais de fábrica (`PADRAO = NOSSO`) |
| (este)    | este relatório |

## O que entrou (24 commits do ramo)

- **Limpar pontinhos do ScanTailor** (`fase2-misto-opcoes`, `a755087`): a DLL comum
  `core/nativo/st_ferramentas.dll` (código do ScanTailor Advanced v1.2.1 sem
  mudança, `terceiros/scantailor-advanced/`), `core/st_ferramentas.py`,
  `core/pontinhos_scantailor.py`, a escolha "Limpar pontinhos: desligado · o nosso
  · pouco · normal · muito" no livro (tela "O que fazer") e na página (aba Filtro,
  no lugar da caixinha "limpar poeirinha"), valendo no Preto e branco e no "Só as
  letras". Projeto antigo: o livro abre "o nosso" e a página com a caixinha
  desligada abre "desligado" (sai igual ponto a ponto).
- **Item 2.1 Dividir** (`fase2-dividir`, `eebe358`): `core/dividir_scantailor.py`
  (o `PageLayoutEstimator` do ScanTailor na mesma DLL), o jeito de dividir por livro
  e por folha, o "corte da sobra" (desligado de fábrica), o livro novo que não
  divide (G2 (a)), o conserto da folha repetida/sumida no "não dividir esta" e a
  janela "Confirmar e processar" contando o mesmo que vai para o PDF.
- A DLL está na worktree e confere: `st_ferramentas.dll` SHA-256
  `6f734df9…b728` (igual a `core/nativo/st_ferramentas.txt` e à do ramo);
  `st_gravura.dll` (item 1.2) continua `833d03db…193f`, a soma que
  `tests/test_st_ferramentas.py` cobra.

## Conflitos e como resolvi

**Nenhum conflito de texto**: o `git merge` juntou tudo sozinho. Seis arquivos
foram mexidos pelos dois lados; conferi cada um à mão para ver se nenhum conserto
do `fase-1` se perdeu e se as duas mudanças não se atrapalham:

| arquivo | `fase-1` mudou | o ramo mudou | resultado |
|---|---|---|---|
| `core/misto.py` | o desenho claro colado à tinta forte no "Só as letras" (`_desenho_colado_a_tinta_forte`, `RAIO_DO_DESENHO`…) | só a assinatura/docstring de `aplicar_misto` (`despeckle` aceita a escolha do limpar pontinhos) | lugares diferentes; os dois ficam |
| `historico_acoes.py` | Ctrl+Z depois de reabrir (`_regravar_tudo`, `_guardar_arquivo_errado`, arquivo errado de antes de 06/10) | campos `pagina:<i>.<campo>` numa ação de folha (o "não dividir esta" apaga a metade junto) e a tradução da ação antiga `despeckle` | funções diferentes; os dois ficam |
| `ui/janela_principal.py` | voltar das opções remonta os cartões (`_voltar_das_opcoes`) | trazer/gravar `dividir_como`, `cortar_sobra`, `limpar_pontinhos` | lugares diferentes; os dois ficam |
| `ui/tela_conferir.py` | girar "aplicar em" copiando o giro da folha da vez; aviso "vá a uma folha par"; frase do desfazer que espera | o jeito por folha, "não dividir esta", a lista do limpar pontinhos na aba Filtro | lugares diferentes. Conferi que `_registrar` e `_espera_pelas_marcacoes` (do `fase-1`) continuam valendo para as ações novas do ramo |
| `tests/test_girar_na_tela.py` | os testes do "aplicar em" e do aviso das pares | `_aberta(..., dividir=True)` (o livro novo não divide mais) | os dois ficam; os testes do `fase-1` não precisam do dividir |
| `tests/test_girar_cartoes_e_previas.py` | "todas" copia o giro; voltar pelas opções mostra a capa nova | tira `alternar_dividir` da lista do teste da pendência D2 (foi para `test_dividir_na_tela.py`) | os dois ficam |

Os consertos do `fase-1` que a gerente pediu para manter estão todos no ramo e os
testes deles passam: Ctrl+Z depois de reabrir (`test_historico_depois_de_reabrir`),
aviso "vá a uma folha par" e girar copiando o giro (`test_girar_na_tela`),
desenho claro no "Só as letras" (`test_misto_consertos`), pasta de dados dos
scripts (`pasta_de_dados_dos_scripts.py`, intacto).

## Decisão 1 — o jeito de dividir de fábrica é o do ScanTailor

Pedido (07/10/2026, página de escolhas, "Ao marcar 'Dividir folhas ao meio', qual
jeito vem escolhido?"): **"O do ScanTailor"**.

- `core/dividir_scantailor.py`: nova constante `JEITO_DO_LIVRO_NOVO = JEITO_SCANTAILOR`,
  com o pedido e a data no comentário.
- `modelos.py`: `Projeto.dividir_como` de fábrica = `JEITO_DO_LIVRO_NOVO`.
- **Projeto antigo abre exatamente como antes**: `Projeto.de_dicionario` continua
  com `setdefault("dividir_como", JEITO_DO_PROJETO_ANTIGO)` = "programa". Todo
  projeto gravado pelo `fase-1` (que não tem o campo) reabre com "o do programa";
  um projeto gravado com "programa" escrito continua "programa".
- O do programa continua na lista, como opção, no livro e por folha.
- Testes: `test_livro_novo_nao_divide_e_o_jeito_e_o_do_scantailor` e o trecho novo
  de `test_livro_novo_nao_divide_e_o_jeito_so_aparece_marcado` **falharam antes**
  (`JEITO_DO_LIVRO_NOVO` não existia; a lista vinha em "programa") e passam
  depois. Novos de guarda: `test_projeto_gravado_com_o_do_programa_continua_com_ele`
  e `test_projeto_antigo_reaberto_continua_com_o_do_programa` (abre na janela um
  `projeto.json` sem o campo, marca "Dividir" e confere "o do programa").
  Dois testes que medem o jeito do programa (`test_jeito_do_programa_e_o_de_sempre`,
  `test_recalcular_divisao_de_uma_folha`) passaram a pedir o do programa
  explicitamente, porque dependiam do de fábrica.

O que muda para quem usa: **livro novo**, ao marcar "Dividir", vem com o do
ScanTailor (se a DLL faltar, a análise cai no do programa, como já fazia).
**Livro antigo**: nada muda.

## Decisão 2 — o limpar pontinhos do ScanTailor não vem ligado de fábrica

Palavras do Samuel (07/10/2026): "o limpar pontinhos, só deve ser usado se for
selecionado junto, e não como automatico junto do preto e branco. e ele já entra
hoje, com essa ressalva, além disso eu quero poder usar o pouco o o medio e muito".

**O que achei:** no ramo `fase2-dividir`, `core/pontinhos_scantailor.PADRAO` era
`POUCO` (o do ScanTailor "pouco", decisão P7 de 06/10). Ou seja, deixar o `PADRAO`
como estava = o do ScanTailor ligado de fábrica em todo livro novo com Preto e
branco, o contrário do que o Samuel pediu. **Por isso troquei o `PADRAO` para
`NOSSO`**, num commit separado (`c951b70`, fácil de desfazer): é o que o `fase-1`
faz hoje (o livro novo sempre limpa com o nosso), então nada muda para o Kaique em
relação ao programa de hoje enquanto o Samuel não responde. Se a gerente preferir
outro valor provisório, é a mesma linha.

**Onde trocar quando o Samuel responder (uma linha só):**
`core/pontinhos_scantailor.py`, linha 202:

    PADRAO = NOSSO        ->        PADRAO = DESLIGADO

Nada mais precisa mudar: `modelos.Projeto.limpar_pontinhos`, a tela "O que fazer"
e a aba Filtro leem dali.

**Testes que dependem do padrão:** só os do próprio limpar pontinhos
(`tests/test_limpar_pontinhos_no_programa.py` e `tests/test_limpar_pontinhos_na_tela.py`)
— no ramo eles cravavam "pouco" como o de fábrica. Agora usam `ps.PADRAO` e, onde
precisam de um valor diferente do de fábrica, usam "normal"/"muito" (nunca
"nosso" nem "desligado"), então valem para os dois. Teste novo
`test_o_do_scantailor_nunca_vem_de_fabrica` (falha com `PADRAO = POUCO`, passa com
`NOSSO` e com `DESLIGADO`) e o da tela
`test_o_livro_comeca_no_de_fabrica_e_nunca_no_do_scantailor`. Rodei a bateria
inteira com `PADRAO = DESLIGADO` (troca temporária, desfeita): ver "Testes".

**O que muda num livro novo, em cada caso** (só nas páginas em Preto e branco e
no "Só as letras"; Original, Melhorar e Mágico não usam o limpar pontinhos):

| | `NOSSO` (como hoje) | `DESLIGADO` |
|---|---|---|
| O que sai | o mesmo Preto e branco do `fase-1` de hoje: tira toda mancha preta pequena, pelo tamanho (às vezes come pingo, vírgula, pedaço de letra fina: "o nosso muitas vezes acaba comendo muito as letras", Samuel, 06/10) | a binarização sem limpar nada: a poeira e a sujeira do scanner ficam, e os pingos/acentos/pedaços que o nosso comia também ficam |
| Quanto muda (medido nas páginas-gabarito, Preto e branco puro) | — | a mais de tinta preta que fica: Palatino 67 +494 pontos (0,09% da tinta; 112 manchinhas), Siebmacher 9 +703 (0,13%; 172), Marial 7 +1111 (1,2%; 426), Horas 47 +2933 (0,6%; 1267), Graduale 221 +394 (0,3%; 161), Boécio 3 +1501 (2,7%; 600) |
| Tempo | igual ao de hoje | um pouco mais rápido: o nosso custa de 5 a 29 ms por página nessas imagens |
| Livro antigo | nada muda (abre "o nosso", página com a caixinha desligada abre "desligado") | nada muda (idem: o antigo não usa o `PADRAO`) |
| Valor estranho no `projeto.json` | vira o nosso | vira desligado (`escolha_valida` cai no `PADRAO`) |

Em nenhum dos dois casos o Preto e branco fica mais lento que hoje: o custo
medido pelo verificador para o do ScanTailor (+0,08 s por página comum, +0,5 a
0,9 s nas grandes de "72 DPI") só aparece quando a pessoa escolhe pouco, normal
ou muito.

Script da medição (só leitura das páginas-gabarito): fora do projeto, no
rascunho da sessão (`medir_nosso_x_desligado.py`); a conta é
`filtro_preto_e_branco(img, despeckle=False)` contra `despeckle=True`.

## Testes

Todos rodados **arquivo por arquivo** (`.venv\Scripts\python.exe -m pytest tests/<arquivo> -q`),
com a pasta de dados de mentira do `tests/conftest.py`.

- **Estado final (`PADRAO = NOSSO`)**: 105 arquivos, **1898 passaram, 0 falharam,
  59 pulados** (os pulados são só de OCR: `test_ocr_comparar` 23, `test_ocr_doctr`
  23, `test_ocr_kraken` 6, `test_ocr_tesseract` 7 — motores/modelos que não estão
  instalados, como antes). Os testes da DLL não foram pulados. 11 min no total.
- **Com `PADRAO = DESLIGADO`** (troca temporária, desfeita): os mesmos 105
  arquivos, **1898 passaram, 0 falharam, 59 pulados**. A troca de uma linha não
  quebra nenhum teste.
- **Com `PADRAO = POUCO`** (o do ramo; só os dois arquivos do limpar pontinhos):
  falham exatamente os dois testes de guarda novos
  (`test_o_do_scantailor_nunca_vem_de_fabrica` e
  `test_o_livro_comeca_no_de_fabrica_e_nunca_no_do_scantailor`); o resto passa.
- **`teste_botoes.py`** numa cópia `git archive` do commit final
  (`saida_teste\copia-botoes`, com `saida_teste` própria): **166 ações, 0 falhas** (cópia do commit `c951b70`; inclui marcar/desmarcar "Dividir", trocar "Jeito de dividir" para os dois jeitos, o jeito por folha e "não dividir esta"). O `teste_botoes.py` não mexe na lista do limpar pontinhos (já era assim no ramo); ela está coberta pelos testes de tela do pytest
- **`erros.log` real do Samuel** (`%LOCALAPPDATA%\EditorImpressao\erros.log`):
  antes 7989 linhas / 443369 bytes (última mudança 06/10 21:40); depois
  **7989 linhas / 443369 bytes, a mesma data**: não ganhou nenhuma linha (conferido depois das duas baterias, do `teste_botoes.py` e da medição).

## Ressalvas

1. **Troquei o `PADRAO` do limpar pontinhos, contra a letra do pedido** ("não troque
   o `PADRAO` agora"), porque no ramo ele era `POUCO` (o do ScanTailor ligado de
   fábrica) e deixar assim contrariava o pedido do Samuel de 07/10. Pus `NOSSO`
   (o comportamento do `fase-1` de hoje), num commit só (`c951b70`). Se a gerente
   não concordar, `git revert c951b70` volta ao `POUCO` do ramo.
2. **Scripts da raiz que ligam o dividir** (`teste_criterios.py`, `teste_pipeline.py`,
   `teste_robustez.py`) criam `Projeto(dividir_folhas=True)`
   sem dizer o jeito: com a decisão 1 eles passam a dividir pelo do ScanTailor
   (com a DLL presente). Não os mudei; números antigos deles não comparam direto.
3. **Projeto que existe na lista mas nunca foi gravado** (ou depois do "começar de
   novo", que apaga o `projeto.json`) abre com as opções de fábrica, então com o do
   ScanTailor ao marcar "Dividir". É o comportamento de sempre para "sem opções
   salvas"; registro porque é o único caso de livro "não novo" que pega o de
   fábrica.
4. Projeto gravado por uma versão do ramo `fase2-misto-opcoes`/`fase2-dividir`
   (só nas conferências) tem `"limpar_pontinhos": "st_pouco"` escrito e continua
   com o pouco ao reabrir (é escolha gravada, não o de fábrica).
5. Teste de máquina só. O "ficou bom" do dividir do ScanTailor e do limpar pontinhos
   já foi conferido pelo verificador nos pareceres dos ramos; esta junção não mexe
   no processamento de imagem além do de fábrica.

## Ideias para a Lista de espera

- Nenhuma nova.

## Bugs para a Lista de bugs

- Nenhum achado nesta tarefa.
