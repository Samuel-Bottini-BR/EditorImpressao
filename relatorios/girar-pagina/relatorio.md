# Girar só a página numa folha dividida (D-618)

Ramo `girar-pagina-2026-11-04` (saiu de `obra-2026-10-26`). Teste de **máquina** (as medidas e os testes) e de
**olho** (os prints da janela de verdade, para o Samuel conferir).

## O defeito, em uma frase

O botão girava a folha inteira do scan e depois cortava de novo na mesma linha; por isso a página virava meia
folha deitada, com pedaços das duas páginas, e na meia volta aparecia a outra página (a branca).

## A prova (antes do conserto)

Janela de verdade, Gradus Primus, Cortar as bordas, página 14 (folha 7, dividida), "¼ à esquerda" do Propriedades
(prints `prints/antes-*.png`, números em `anotacoes-antes.txt`):

- Antes de girar: página 14 com 351 x 496 pontos (em pé), página 13 com 351 x 496 (a 13 é branca de verdade).
- Depois de um "¼ à esquerda": a **folha** ficou com giro 270; a página 14 virou uma tira de 248 x 702
  (proporção 0,35 em vez de 0,71) e a **página 13 também mudou** (o resumo da imagem dela mudou). É o print a-70.
- Depois do segundo: a página 14 ficou com 0% de tinta: mostrava a 13, a branca. É o print a-71 ("cai na folha branca").

A conta está em `core/pipeline.preparar_para_recorte`: girava a folha (`ConfigFolha.rotacao`) e só depois dividia
pela mesma fração da largura.

## O que mudou

- A página de uma folha dividida tem agora o giro dela (`ConfigPagina.giro_da_pagina`, 0/90/180/270), aplicado
  **depois** de dividir. A outra página e a linha da divisão não mudam.
- "¼ à esquerda", "¼ à direita" e "meia volta" do Propriedades (com "só esta folha"), os três botões do canto e
  Ctrl+Seta (menu Página) giram só a página da tela quando a folha está dividida. Uma ação do desfazer: o Ctrl+Z volta.
- O corte feito à mão nessa página gira junto (continua sobre o mesmo pedaço do papel).
- O giro da página entra em tudo que desenha a página: a prévia, o PDF de saída (e por ele os cadernos), a tira de
  baixo, a grade "ver todas", o Dividir em "Uma página", o "antes" do Automático e as marcações (zonas) da aba Marcar.
- Projeto antigo: não tem o campo, abre com 0 e sai igual.
- Folha inteira (não dividida): continua girando a folha, agora como uma foto (ver abaixo).

Arquivos: `core/girar.py` (também `campos_da_pagina_que_giram_junto`), `core/pipeline.py`, `core/zonas_na_folha.py`, `core/automatico.py`, `modelos.py`,
`ui/tela_conferir.py`, `ui/tarefas.py`, `ui/widgets/tira_miniaturas.py`; teste novo
`tests/test_decisoes_girar_pagina.py`.

## Depois do conserto (janela de verdade)

Mesmo caminho (prints `prints/depois-*.png`, números em `anotacoes-depois.txt`):

- A página 13 ficou **igual em todos os passos** (o mesmo resumo da imagem do começo ao fim).
- A página 14, a cada giro, ficou com a mesma tinta (1,91%) e só trocou de pé para deitada (351 x 496 ↔ 496 x 351).
- A folha continuou com giro 0 e a linha em 0,5.
- Canto, menu Página (o mesmo caminho do Ctrl+Seta) e meia volta: só a página 14. Ctrl+Z quatro vezes: tudo de volta.
- Ao redor: página 13, Endireitar, Dividir em "Uma página" (a metade girada) e em "Duas lado a lado" (a folha
  inteira com a linha, sem giro: a folha não girou) - prints 09 a 13.

## A folha inteira: gira como uma foto ("girar - sim", 04/11)

Ele disse: "hoje quando gira a folha altera a proporção dela para girar ela". A gerente levou a proposta ("girar a
folha inteira é como girar uma foto. A folha larga, com as duas páginas, fica em pé, inteira, sem esticar, sem
apertar e sem cortar nada") e ele respondeu "girar - sim".

O que a medida mostrou (folha 1 do Gradus, capa e contracapa, 29,7 x 21 cm; prints `prints/folha-*.png`):

- Sem corte à mão e sem tamanho escolhido, a folha **já** girava como foto: 702 x 496 → 496 x 702 na conta, 855 x 605
  → 427 x 605 na tela, e o PDF também (proporção exatamente invertida). O Mover diz "29,7 × 21,0 cm" antes e
  "21,0 × 29,7 cm" depois.
- Onde a proporção mudava de verdade: (1) **o corte feito à mão** ficava com os mesmos números e passava a cortar
  outro pedaço da folha deitada (no teste, a página sai com proporção 0,36 em vez de 1,37); (2) **o tamanho de folha
  escolhido** ("tamanho..." / Mover) ficava deitado e a folha em pé era apertada dentro dele (a página do PDF não
  mudava de forma: 1,42 em vez de 0,71); e, na folha dividida, o defeito da D-618 (a página virando tira).

O conserto: ao girar a folha inteira (Propriedades, canto, Ctrl+Seta, "aplicar em" e a grade "ver todas"), a página
dela leva junto, na mesma ação do desfazer, o corte à mão (sobre o mesmo pedaço do papel), o tamanho de folha
escolhido (deita junto) e o lugar do conteúdo (gira junto). Na janela de verdade (`prints/foto-*.png`): corte à mão só
na contracapa, "¼ à esquerda" → a folha fica em pé e o corte continua na contracapa; Ctrl+Z volta o corte e o giro.

## Testes

No PC, um arquivo por vez (`rodar_testes.ps1`; saída em `resultado-testes.txt`). Nenhum teste antigo foi mudado.

- `test_girar.py`: 53 passed in 15.87s
- `test_girar_na_tela.py`: 22 passed in 72.91s (0:01:12)
- `test_girar_cartoes_e_previas.py`: 23 passed in 59.93s
- `test_ajustar_pedaco_na_folha_girada.py`: 8 passed in 7.55s
- `test_zonas_na_folha.py`: 25 passed in 24.88s
- `test_converter_zonas_ao_abrir.py`: 14 passed in 38.69s
- `test_decisoes_dividir.py`: 21 passed in 57.26s
- `test_decisoes_dividir_arrastar.py`: 16 passed in 16.93s
- `test_decisoes_dividir_metade.py`: 6 passed in 6.82s
- `test_decisoes_dividir_linha.py`: 13 passed in 16.21s
- `test_decisoes_dividir_aviso.py`: 11 passed in 14.62s
- `test_dividir_na_tela.py`: 9 passed in 21.61s
- `test_dividir_no_programa.py`: 19 passed in 14.83s
- `test_pipeline_folha.py`: 7 passed in 3.52s
- `test_corte_previa_igual_pdf.py`: 4 passed in 3.51s
- `test_cadernos.py`: 28 passed in 0.31s
- `test_caderno_segue_as_etapas.py`: 11 passed in 5.06s
- `test_decisoes_montar_cadernos.py`: 13 passed in 73.20s (0:01:13)
- `test_decisoes_impressao.py`: 22 passed in 21.03s
- `test_decisoes_tira_em_pares.py`: 4 passed in 10.58s
- `test_decisoes_tira_pares_juntas.py`: 3 passed in 8.16s
- `test_decisoes_previa_dividida.py`: 4 passed in 15.57s
- `test_paineis_na_tela.py`: 22 passed in 59.82s
- `test_decisoes_nucleo.py`: 38 passed in 4.93s
- `test_decisoes_automatico.py`: 29 passed in 54.74s
- `test_decisoes_automatico_ver_como_fica.py`: 22 passed in 61.52s (0:01:01)
- `test_decisoes.py`: 26 passed in 4.24s
- `test_decisoes_girar_pagina.py`: 16 passed in 9.55s
- `test_cartoes_e_previas.py`: 2 passed in 2.22s
- `test_decisoes_mover.py`: 13 passed in 10.46s
- `test_decisoes_ver.py`: 11 passed in 20.07s
- `test_previa_composta.py`: 10 passed in 3.37s
- `test_decisoes_tela.py`: 35 passed, 4 warnings in 30.47s

De novo depois do "girar - sim" (a folha inteira como foto):

- `test_decisoes_girar_pagina.py`: 19 passed in 15.28s
- `test_girar.py`: 53 passed in 11.17s
- `test_girar_na_tela.py`: 22 passed in 93.24s (0:01:33)
- `test_girar_cartoes_e_previas.py`: 23 passed in 53.45s
- `test_decisoes_automatico.py`: 29 passed in 72.50s (0:01:12)
- `test_decisoes_dividir.py`: 21 passed in 45.44s
- `test_decisoes_dividir_arrastar.py`: 16 passed in 24.98s
- `test_decisoes_mover.py`: 13 passed in 11.43s
- `test_decisoes_mover_lado.py`: 7 passed in 5.35s
- `test_decisoes.py`: 26 passed in 5.51s
- `test_decisoes_tela.py`: 35 passed, 4 warnings in 38.91s

O teste novo `tests/test_decisoes_girar_pagina.py` foi rodado também no código de antes (ce086bb6, numa cópia à parte): os de reversão falham lá pelo defeito ("a folha não gira: 270 == 0"; "é a página da direita de cabeça para baixo - não a outra página"). Os dois da folha inteira
(`test_reversao_d618_folha_inteira_com_*`) também falham lá pela medida: com o corte à mão a página sai com proporção
0,36 em vez de 1,37; com o tamanho escolhido, 1,42 em vez de 0,71 (apertada).

GitHub: rodada 41903363460 (último commit 06b80752): partes 1, 3, 4 e 5 e os botões/prints da janela real passaram; a parte 2 falhou só em `tests/test_recomeco_limpa_o_historico.py` (5 testes, "assert 0 == 90"), que contradiz a D-618 (ver "Para a gerente" no ONDE-PAREI; o teste não foi mudado). A rodada 41900193119 (commit 3b6f998c) deu o mesmo. Filtro de velocidade 41900198976 (obra-2026-10-26 → 3b6f998c): **igual** em tudo (abrir +0,9%, trocar de página +0,5%, Mágico pro +0,9%, Preto e branco -1,0%, todos dentro do vai-e-vem). O último commit só acrescentou contas chamadas no clique de girar (nada no processamento).

## Perguntas para o Samuel

1. **O "aplicar em" e o nome do bloco numa folha dividida.** Hoje, numa folha dividida, só "só esta folha" gira a
   página; "todas as folhas", "daqui em diante", "só as pares" e "só as ímpares" continuam girando as folhas inteiras,
   como antes (o que, numa folha dividida, ainda faz a confusão do a-70). Sugestão: numa folha dividida o bloco
   passa a se chamar "Girar a página", a lista diz "só esta página / todas as páginas / daqui em diante / só as pares
   / só as ímpares", e cada página gira sozinha, virada como a da tela. O mesmo para o girar da grade "ver todas"
   (hoje gira as folhas das páginas escolhidas). Pode ser assim?

## Um teste antigo contradiz a D-618

`tests/test_recomeco_limpa_o_historico.py`: o ajudante divide o livro, gira a página 1 com "só esta folha" e cobra
que a FOLHA 1 ficou girada (`folhas[0].rotacao == 90`). Com a D-618 é a página 1 que gira, e a folha fica em 0. O teste
trata de outra coisa (o Ctrl+Z depois de recomeçar). Não foi mudado: a gerente decide (sugestão: cobrar o giro da
página 1, ou girar antes de dividir).

## Ressalvas

- No Dividir com "Duas lado a lado" a tela mostra a folha inteira com a linha: ali o giro continua sendo o da
  folha (o que aparece é a folha). Uma página já girada sozinha aparece em pé nessa vista (a folha não girou).
- O Ctrl+Seta não pôde ser apertado na janela do piloto: ela fica fora da tela, sem foco, e o atalho do menu só vale
  com a janela ativa (o mesmo acontece no código de antes; a tecla cai na troca de página). Foi testado pelo caminho
  do menu (o mesmo que a tecla chama) e pelo teste antigo `test_a_tecla_do_menu_gira_de_verdade`.
- O Automático mede o ângulo e os avisos na metade como veio (sem o giro da página); o corte e o ângulo da prévia
  e do PDF são medidos de novo na página girada. Página girada sozinha que passe de novo pelo Dividir do Automático
  continua com o giro dela.
- A fase "folha" do piloto abriu o Gradus como livro novo (sem o trabalho salvo), o que serviu para ter folhas
  inteiras; a causa não foi investigada (só o piloto).
