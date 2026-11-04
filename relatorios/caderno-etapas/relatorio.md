# As folhas do caderno seguem as etapas marcadas (D-603) — relatório do implementador

04/11/2026 · ramo `caderno-etapas-2026-11-04` · PRONTO PARA CONFERIR (não juntado: quem junta é a gerente)

## O que foi feito

Agora, com "Dividir" marcado na janela do Automático, as folhas do caderno da etapa 7 (e a tela
grande de caderno) mostram as páginas já divididas, antes do "Rodar": uma página em cada metade da
folha, e a conta das folhas usa o número de páginas depois de dividir (Gradus: "Folha 1 de 35" com
o Dividir, "Folha 1 de 18" sem). As outras etapas marcadas (margens, cortar, limpar...) já entravam
no desenho de cada página; continuam entrando. Continua sendo montada só a folha à vista.

**Por que saía inteiro:** a lista das páginas do caderno vinha do livro como está, sem o Dividir do
pedido. Cada lugar do caderno recebia a folha do scan inteira (as duas metades coladas lado a lado)
e a conta usava uma página por folha do scan.

**O conserto, na causa:** a lista das páginas do caderno passa a ser a do livro depois das etapas
marcadas, feita sem desenhar nada. Quais folhas o Dividir vai partir sai da mesma regra que a medida
do "Rodar" usa no modo automático, que só olha o tamanho da folha (ScanTailor: mais larga que alta;
jeito do programa: mais larga que 1,2 vez a altura), lido do PDF sem desenhar. Cada lugar do caderno
recebe só a sua metade.

## Arquivos

- `core/automatico.py`: `paginas_do_pdf_depois` (a lista depois do pedido, sem desenhar),
  `vai_dividir_pelo_tamanho`, `_retangulos_do_pdf`; `folha_do_caderno` ganhou `metades` (opcional;
  sem ele, igual a antes) e desenha uma vez a folha que dá duas posições.
- `core/paginas_em_outro_processo.py`: leva `metades` ao servidor de páginas.
- `ui/widgets/folhas_do_caderno.py`: a conta das folhas e as páginas de cada lado vêm da lista nova
  (só com a etapa 7 aberta; fechada, como antes).
- `tests/test_caderno_segue_as_etapas.py` (novo: reversão + 10 provas da conta sem desenhar).
- `tests/test_decisoes_caderno_tela_grande.py` (4 provas novas no fim; as 11 antigas sem mudança).
- `relatorios/caderno-etapas/` (ONDE-PAREI, prints, prints.py, prints.json, este relatório).

## Como cumpri cada decisão

| Decisão | Como | Prova |
|---|---|---|
| D-603 "era para ser com divisão [...] mesmo que eu não tenha processado ainda" | Dividir marcado → folhas com páginas divididas, sem Rodar | `test_d603_dividir_marcado_o_caderno_mostra_as_paginas_divididas` (reversão), `test_d603_marcar_e_desmarcar_o_dividir_muda_o_caderno_na_hora`, `test_d603_gradus_...`; prints 02 |
| D-603 "seguir todas as etapas marcadas (dividir, cortar, margens e as outras)" | o desenho de cada página é o "depois" (já era); agora com a página certa | `test_d603_margens_marcadas_entram_nas_folhas_do_caderno`; print 04 |
| D-603 "a bolinha de carregamento aparece enquanto ele monta" | a mesma bolinha de antes | provas acima (`calculando()` logo depois de marcar); prints.json `*_bolinha: true` |
| 04/11 "ele só carrega a folha que está aparecendo né?" | sim: só a folha à vista; a conta do livro é só de números | `folha_do_caderno` recebe só as 4 posições da folha |
| D-589 etapa desmarcada não entra | Dividir desmarcado → lista do livro como está; margens desmarcadas → sem margem | `test_d603_marcar_e_desmarcar...`, `test_d603_margens...`, `test_d603_sem_o_dividir_a_lista_e_o_livro_como_esta`; print 03 |
| D-590 Dividir desmarcado não junta | livro já dividido + Dividir desmarcado → continua dividido | `test_d603_dividir_desmarcado_nao_junta_as_folhas_ja_divididas` |
| D-577 / D-574 só mostra, não muda o livro; tamanho do scan; folha 1 | nada disso mudou | as 11 provas antigas da D-574 passam; provas novas conferem o livro sem mudar |
| D-064 bolinha | igual | idem |
| D-605 o novo não estraga o que já estava | etapa 7 fechada ou Dividir desmarcado: exatamente o caminho antigo; nenhum teste antigo mudado | testes antigos abaixo |
| D-604 | não feita (próxima tarefa) | — |

## Testes

- **Reversão:** no código antigo (`016ec37a`) o teste falha ("Folha 1 de 2" no lugar de "Folha 1 de
  3") e passa no novo. As 3 provas novas da D-603 com o Dividir/margens também falham no antigo; a da
  D-590 passa nos dois (é guarda: o antigo já não juntava).
- **Prova de que a conta sem desenhar dá o mesmo que o "Rodar":** 8 combinações (dois jeitos de
  dividir, livro todo ou algumas páginas, pular ou não as mexidas à mão) num livro com folhas
  inteiras, já divididas, juntadas, tiradas, mexidas à mão, em pé, deitadas, quase quadradas e
  giradas: a lista é igual à do `aplicar` de verdade.
- **Prova de que a regra do tamanho é a da medida:** comparada com a medida de verdade (que desenha e
  pergunta ao ScanTailor) em folhas sintéticas e nas 12 primeiras folhas do Gradus, nos dois jeitos,
  sem giro e girada: igual em todas.
- **No PC, um arquivo por vez (todos passaram):** test_decisoes_caderno_tela_grande 15,
  test_caderno_segue_as_etapas 11, test_cadernos 28, test_decisoes_automatico_ver_como_fica 22,
  test_decisoes_automatico_margens_no_depois 5, test_decisoes_automatico 29,
  test_decisoes_montar_cadernos 13, test_decisoes_livreto_ver 13 (+1 pulado), test_previa_composta
  10, test_decisoes_juntar_todas 4, test_automatico_pular_depois_de_dividir 4,
  test_decisoes_impressao 22, test_decisoes_automatico_opcoes_do_filtro 21,
  test_decisoes_filtro_automatico 4, test_decisoes_dividir 21, test_promessas (caderno/p211) 1,
  test_promessas p083 6.
- **GitHub:** ver "Rodadas do GitHub" no fim.

## Tempos medidos (PC do Samuel)

- **A conta das páginas depois do Dividir** (sem desenhar, no fio da tela):
  - Gradus Primus (70 folhas → 140 páginas): 144 ms na primeira vez da sessão (67 ms são abrir a
    DLL do ScanTailor, uma vez só; 9 ms ler os tamanhos do PDF); depois 1 ms.
  - Livro grande (o Gradus repetido 10 vezes: 700 folhas → 1400 páginas, 108 MB): 75 ms na primeira
    vez (58 ms ler os tamanhos), depois 13 ms. Sem o Dividir: 0,2 ms.
  - A primeira versão usava o próprio `_dividir` do Rodar numa cópia: 0,35 s nas 700 folhas (a tela
    pararia); trocada pela conta direta.
- **Na janela de verdade, Gradus** (prints.json): folha 1 com o Dividir em 1,0 a 1,4 s; desmarcar
  0,8 s; maior parada da tela 0,025 s (limite 0,3 s).
- **Com "Margens iguais" marcada: ~45-50 s por folha**, igual no código antigo (medido: antigo 45,0
  e 44,7 s; novo 44,7 e 50,4 s, folhas 1 e 2). Não é desta mudança: ver Bugs.

## Prints (janela de verdade fora da tela, pasta de dados própria `_tmp/dados-prints-caderno-etapas`)

- `01-etapa-1-marcada-montando.png`: abrindo a etapa 7 com a etapa 1 marcada, a bolinha girando.
- `02-etapa-1-marcada-folha-1-dividida.png`: "Folha 1 de 35"; frente: página de exercícios e a
  contracapa, cada uma numa metade; verso: a capa azul e o vocabulário.
- `03-etapa-1-desmarcada-scans-inteiros.png`: "Folha 1 de 18"; cada metade com o scan inteiro (como
  o print a-49).
- `04-etapas-1-e-6-marcadas-com-margens.png`: Dividir e Margens marcadas; páginas divididas com a
  margem branca.
- `05-etapas-1-e-6-folha-2.png`: a seta para a folha 2, com as margens.

## Ressalvas

1. **A conta das folhas usa a regra do tamanho, não a medida da imagem.** É a mesma regra que a
   medida usa no modo automático (provado), mas se um dia a medida passar a olhar o conteúdo (ou se a
   DLL do ScanTailor recusar a imagem num processo e aceitar no outro), a conta e o desenho podem
   discordar numa folha. Nesse caso a folha mostra o scan inteiro naquele lugar (como antes), sem
   erro.
2. Se o `_dividir` do "Rodar" mudar, `paginas_do_pdf_depois` tem de mudar junto (está escrito no
   código; a prova `test_d603_lista_sem_desenhar_e_a_mesma_do_rodar` acusa a diferença).
3. A primeira vez que a etapa 7 abre com o Dividir marcado custa até ~0,15 s no fio da tela (DLL +
   tamanhos do PDF); num livro de 900 folhas a leitura dos tamanhos deve ficar por volta de 0,1 s.
   Abaixo do limite de 0,3 s, mas não é zero.
4. A bolinha aparece pelo mesmo caminho de antes; nos prints ela está presente na hora de montar
   (`01`), mas a foto pega um instante só.

## Bugs para a Lista de bugs (não consertados: não impedem a tarefa)

- **04/11/2026 — Etapa 7 com "Margens iguais" marcada: cada folha do caderno leva ~45-50 s no
  Gradus, e a segunda folha não aproveita a conta da primeira.** Já era assim antes desta mudança
  (código antigo: 45,0 s e 44,7 s). Cada página da folha mede o livro inteiro para as margens; a
  folha é feita no servidor de páginas, e a conta guardada de uma folha não serve à seguinte. A
  bolinha gira o tempo todo, a tela não para. Onde: `core/automatico.depois_da_pagina` /
  `folha_do_caderno` (servidor de páginas). Prints 04 e 05 (`04_margens_s`, `05_seta_com_margens_s`
  em prints.json).
- **GitHub, rodada 41777456037:** `test_promessas.py::test_p083_jeitos_no_automatico[Guardar
  tudo-tudo]` deu ERROR na limpeza do teste (a prévia da tela de conferir, `ui/tarefas.py` linha 900,
  tentou abrir o PDF do teste depois de ele ser apagado). No PC o teste passa (6 de 6). O caminho
  não passa pelas folhas do caderno; mesmo assim tirei da abertura da janela a única conta nova
  (agora só com a etapa 7 aberta) e rodei de novo — ver abaixo.

## Rodadas do GitHub

- **41777456037** (conjunto inteiro + `teste_botoes.py`, commit `8bf6356a`): 1 ERROR na parte 1,
  `test_promessas.py::test_p083_jeitos_no_automatico[Guardar tudo-tudo]` (prévia da tela de conferir
  abrindo o PDF do teste já apagado, na limpeza do teste); as outras 4 partes e os botões passaram.
  No PC o p083 passa.
- **41780218098** (conjunto inteiro + `teste_botoes.py`, commit `14c512a2`, o final): a parte 1 (com o
  p083) passou; 1 falha na parte 2, `test_decisoes_so_as_letras.py::test_d148_desfazer_o_automatico_
  devolve_o_so_as_letras_do_livro` ("não aconteceu a tempo": o projeto.json gravado depois de 15 s;
  nada de caderno nem de Dividir; na rodada anterior a mesma parte passou; no PC 5 de 5). Rodei de
  novo só a parte que falhou: **passou. Rodada inteira verde** (todas as 5 partes, botões e prints).
- **41777458962** (filtro de velocidade, `016ec37a` x `8bf6356a`, a última mudança em `core/`):
  **"igual (dentro do vai-e-vem)"** — abrir o livro -0,5%, trocar de página +0,4%, Mágico pro -0,4%,
  Preto e branco +0,5%.
- As duas falhas soltas (p083 e d148) parecem de tempo da máquina do GitHub, não desta mudança; ficam
  anotadas para o verificador olhar se voltarem.
