# ONDE-PAREI — conserto C dos quadrados brancos (D-668), agente de conserto, 10/11/2026

Ramo `quadrados-c-2026-11-10` (a partir de `obra-2026-10-26`, `58806f81`), cópia em
`D:\programas\EditorImpressao\.claude\worktrees\quadrados-c`. Tudo sem janela (`QT_QPA_PLATFORM=offscreen`),
dados num `LOCALAPPDATA` à parte, acervo só lido. Relatório: `relatorio.html` (e `.md`, `.pdf`).

## Decisões que esta tarefa precisa cumprir

- **D-668** (10/11, Central `quadrados-qual`: "Roxo: o conserto C (recomendo)"; chat: "c"): "Melhorar e Mágico pro
  voltam a proteger as pinturas: nas páginas com Melhorar ou Mágico pro e "Respeitar as gravuras achadas" marcada, o
  programa procura a gravura (como o Preto e branco, D-659) e não pinta de branco dentro dela; e a limpeza do papel só
  pinta de branco onde em volta também é papel (vale também com "Respeitar" desmarcada, print 10)." Conserta o "i" e o
  "t" finos. "Pela D-667, a procura da D-659 passa a valer nos três filtros por uma regra só."
- **D-667** (10/11): "Você devia ter mandado ele mudar a ferramenta, se mudou a ferramenta, muda em todos os lugares."
- **D-659** (09/11): "se estamos no manual e eu estou fazendo ajustes em uma pagina, ele vai procurar só naquela pagina
  se eu optar para que ele faça aquele ajuste em varias paginas ai sim o programa vai ler as outras paginas". Testada:
  "fiz os dois testes que você pediu e estão funcionando."
- **D-661** (09/11, "1- pode"): no aviso das páginas mexidas, "Pular" deixa a página feita à mão como ele deixou.
- **D-583 / D-586** (29/10): "Respeitar as gravuras achadas", ligada de fábrica; "Desligada, o filtro vale na página
  inteira".
- **D-473**: a mesma conta na tela, na prévia, nas miniaturas e no PDF.
- **D-605 / CLAUDE.md §11.8**: "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está
  escolhido e testado"; nunca mudar teste antigo para passar.
- **CLAUDE.md §9**: não desfazer a correção do "magic color". **§5**: medir antes e depois; o que piorar, os dois
  resultados.
- Pedido da gerente: não mudar o que sai no Original nem nas páginas que já têm gravura marcada à mão; não acrescentar
  botão, aviso ou texto (§11.7); não mexer nas prévias e miniaturas de `ui/`.

## O que já está escolhido e testado aqui

- `core/etapas.py` (`respeitar_procura`, `procura_por_dentro`, `marca_sozinho`): D-659, D-661, D-589, P4. Provas:
  `tests/test_decisoes_gravura_a_mao.py`, `tests/test_decisoes_gravura_pular.py`, `tests/test_decisoes_respeitar_gravuras.py`,
  `tests/test_decisoes_gravuras_cinza.py`, `tests/test_decisoes_so_as_letras.py`.
- `core/pipeline.py` (`garantir_selecao`, `marcacao_que_o_filtro_usa`): D-586/D-587/D-588.
- `core/filtros.py` (`_limpar_o_papel_de_verdade`): mancha do verso, "fundo meio amarelado", grão do pergaminho (lista
  4.12), papel de dentro da gravura (bug 202, `tests/test_papel_dentro_da_gravura.py`).

## Como fica para quem usa e no livro

O Kaique abre um livro novo, escolhe Melhorar ou Mágico pro no painel "Filtro da página" (com "Respeitar as gravuras
achadas" marcada, como vem): a pintura sai inteira, sem buracos brancos, e as letras finas inteiras, na tela e no PDF.
Na primeira vez que cada página é desenhada assim, o programa procura a gravura (uns 5 s a mais no *Na escola de
Jesus*; até uns 10 s nas páginas grandes do Livro de Horas). Com "Respeitar" desmarcada, nada é procurado e a pintura
também sai sem os buracos grandes (o "i" fino, nesse caso, fica como hoje). Nenhum botão, aviso ou texto novo.

## Andamento

- [x] código (commit `cbdc7e4c`): uma lista só, `core.filtros.FILTROS_QUE_RESPEITAM_AS_GRAVURAS`, para a procura
      (`core/etapas.respeitar_procura`) e para a caixinha desmarcada (`core/pipeline.marcacao_que_o_filtro_usa`); a
      quarta pergunta da limpeza (`core/filtros._em_volta_e_papel`)
- [x] igual à simulação C ponto por ponto (página 13, prévia e PDF; livro inteiro com os mesmos números)
- [x] teste de reversão: `tests/test_decisoes_quadrados_brancos.py` (17 provas); no `58806f81` 12 falham e 5 passam (as
      que guardam o que não muda); no ramo, 17 passam (`reversao-no-58806f81.txt`)
- [x] medidas: 24 páginas (gabarito Fase 1 e 3, Escola 13/97/119, Boécio 33), livro inteiro (Melhorar e Mágico pro),
      Horas 47, a medida da origem (print 10), página com gravura marcada à mão (`medidas/`)
- [x] prints (`imagens/1` a `5`)
- [x] GitHub, testes: rodada 42932052865 — só as 3 provas antigas da D-659 falham (ver Perguntas); a prova nova 13
      passam e 4 pulam (sem acervo no GitHub); botões e prints da janela real: ok
- [x] GitHub, velocidade: rodada 42932057632 — **"igual (dentro do vai-e-vem)"**
- [x] testes no PC, um por vez: 78 arquivos (os 56 `test_decisoes*.py` e 22 dos arquivos tocados): 1419 passaram, 2 pularam, 3
      falharam (as mesmas 3 provas antigas da D-659; `medidas/testes_no_pc.txt`)
- [x] relatório nos três formatos; `relatorios/melhorias.md`

## Como cumpri cada uma

- **D-668**: as duas partes estão no programa; medido no livro inteiro: 110 → 2 páginas com quadrados (Melhorar) e
  112 → 2 (Mágico pro), as mesmas da simulação (119 e 68); página 13: 23,5% → 1,4% e 27,4% → 1,4% (medida da origem);
  água ampliada 63,9% → 0,2%; "Vivia": tinta apagada 3,3% → 0,0%; print 10: 27,4% → 5,8%; Horas 47: 2,6% → 0,07%.
  Provas: `test_d668_pagina_13_sem_buracos_e_vivia_com_o_i_inteiro`, `test_d668_print_10_...`,
  `test_d668_a_agua_da_pintura_...` (sintética, roda no GitHub). Imagens 1 a 4.
- **D-667**: uma regra, num lugar (`FILTROS_QUE_RESPEITAM_AS_GRAVURAS`), lida pelas duas perguntas da caixinha; nenhum
  "se for Melhorar". Vale em todos os lugares da ferramenta: "só nesta", "Aplicar em: todas" e "daqui em diante",
  tela e PDF (`test_d668_so_nesta_...`, `test_d668_aplicar_em_...`, `test_d668_a_conta_...`). Os pares/ímpares e a
  grade não têm "pôr filtro" (ressalva 1 do ONDE-PAREI da D-659): seguem a mesma conta, por página.
- **D-659**: só a página onde a opção vale é procurada (provas acima contam as páginas procuradas). No Preto e branco,
  igual ponto por ponto (`test_d668_preto_e_branco_a_mao_igual_ponto_por_ponto`, página 13 do livro dele; e as 14
  provas da D-659 que não falam do Melhorar continuam passando).
- **D-661**: a página procurada no Melhorar à mão também guarda `gravura_achada_a_mao` (o "Pular" vale igual);
  `tests/test_decisoes_gravura_pular.py` passa.
- **D-583/D-586**: desmarcada, nada é procurado (`test_d668_respeitar_desmarcada_nada_e_procurado`); a regra da
  caixinha desmarcada não mudou (mesma lista, `tests/test_decisoes_respeitar_gravuras.py` passa).
- **D-473**: a prévia e o PDF saem pela mesma conta; na página 13 os dois saíram iguais aos da simulação; a prova de
  tela compara o desenho da tela com o do Automático, ponto por ponto.
- **D-605**: nenhuma prova antiga foi mudada; as 3 que falham estão em "Perguntas". Original: não procura e não usa a
  limpeza (`test_d659_g_...[original]` passa). Gravura marcada à mão antes do filtro: igual ponto por ponto (página 13,
  Melhorar e Mágico pro, `scripts/marcada_a_mao.py`).
- **§9**: a correção do "magic color" não foi tocada (só o último passo da limpeza).
- **§5**: antes e depois medidos; o que piorou está no relatório ("Números que pioraram"), com imagem.

## Perguntas para o Samuel

1. **Três provas antigas da D-659 dizem o contrário da D-668 e falham.** Elas guardam "Melhorar e Mágico pro
   escolhidos à mão não procuram a gravura e saem iguais a antes" (`tests/test_decisoes_gravura_a_mao.py`:
   `test_d659_a_conta_quem_procura_com_limpar_desligado`, linhas 242-243, e
   `test_d659_g_outros_filtros_a_mao_nada_e_procurado_e_sai_igual_ao_de_antes[melhorar]` e `[magico_pro]`). A D-668
   manda justamente isso mudar. Pela regra, não mexi nelas. Sugestão: tirar o Melhorar e o Mágico pro dessas três
   provas (o Original fica nelas), já que a prova nova `tests/test_decisoes_quadrados_brancos.py` guarda o
   comportamento novo. Pode? (sim ou não)

## Achados para a gerente

- **A ressalva do tempo, medida no programa:** no *Na escola de Jesus*, uns 5 s a mais na primeira vez de cada página
  (2,6 s → 7,4 s na página 13), como dito ao Samuel. Mas nas páginas grandes do Livro de Horas são 8 a 11 s a mais
  (Horas 47: 6,5 s → 16,6 s). O filtro de velocidade do GitHub deu "igual" porque mede o caminho do Automático, que já
  procurava a gravura (o livro com "Limpar a folha" ligado); ele não pega a primeira vez do filtro escolhido à mão.
  Lá, o Mágico pro de 10 páginas deu +3,5% (dentro do vai-e-vem de 4,1%): é a quarta pergunta da limpeza. Vale dizer
  ao Samuel que em livro de página grande a espera da primeira vez é maior.
- **Com "Respeitar" desmarcada (print 10), o "i" e o "t" continuam quebrados**: a quarta pergunta tira os buracos da
  pintura, mas a letra só volta inteira com a gravura achada. É o C como foi simulado; o Samuel pode não esperar isso.
- **Letras no tom do original com "Respeitar" marcada** (já dito a ele): numa página de texto com a letra achada, a
  orla da letra fica com um pouco do tom do papel (saturação média do papel 0,0 → 0,5 a 0,8 no Opus Majus 11 e 165;
  o "contorno bege" da Rhetorica 73 na investigação).
- **Gravura marcada à mão DEPOIS de escolher o Melhorar**: a marcação da máquina já foi achada e a mão vai por cima,
  como no Preto e branco (D-659). Antes de escolher, sai igual a hoje.
- A worktree precisa das junções `modelos\` e `gabarito\paginas\` (sem `modelos\` o detector cai no antigo e a
  página sai diferente; criei as duas nesta cópia). Uma cópia de trabalho do `58806f81` foi criada só para a prova da
  reversão, fora do projeto, no scratchpad (`...\scratchpad\antes`, registrada no `git worktree list`); não apaguei.
