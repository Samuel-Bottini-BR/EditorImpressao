# Vistoria das gambiarras: onde parei

Agente vistoriador (só lê código e escreve a lista). Ramo `obra-2026-10-26`, cópia `obra-juncao`. Nenhuma linha de
código mudou; os únicos arquivos mexidos são este e `lista.md`.

## Decisões que esta tarefa precisa cumprir

- **A ordem de serviço do Samuel (26/11/2026)**, em `ordem-de-servico.md`: "Um agente NOVO, que só lê e não conserta
  nada, vistoria o programa e escreve uma lista. Nenhuma linha de código muda." Os cinco tipos; GRAVE/médio/leve; uma
  linha por achado com onde, tipo, gravidade, cópias, POR QUÊ ("se não achar, escrever 'não achei o motivo', nunca
  inventar"), item da Central e o que o Kaique perderia; certeza na lista, dúvida em "Suspeitas"; "Ele nunca para no
  meio de um pedaço"; "A LISTA NÃO FECHA NADA"; "Sem propostas de conserto na lista, sem plano."
- **CLAUDE.md §11.12** (13/11 e 18/11/2026): "o agente não pode fazer gambiarras como na outra ferramenta nossa que
  fazia várias gambiarras e funcionava de maneira diferente em vários lugares" · "eu acho que tinhamos que atualizar a
  regra de gambiarras para que ela se aplicasse a tudo né?". O que a vistoria procura é o que essa regra chama de
  gambiarra: conserto só no lugar do defeito, conta copiada, sintoma tratado em vez da causa.

## Pedaços

| pedaço | situação | começo | fim | tempo |
|---|---|---|---|---|
| girar | feito (12 achados, G-01 a G-12) | 26/11 15:40 | 26/11 15:51 | ~11 min (relógio da máquina, `date`) |
| dividir | **próximo** | | | |
| desfazer | | | | |
| aplicar-em / "o que vai junto" | | | | |
| como-fica (as renderizações) | | | | |
| marcações | | | | |
| contagens e situação da página | | | | |
| o resto da tela | | | | |

O que o pedaço girar leu (não reler): `core/girar.py` inteiro; em `ui/tela_conferir.py` os métodos do girar
(L6554-6917), `_registrar` e os ajudantes dele (L5942-6081), `_espera_pelas_marcacoes` (L6938-6996), a grade
(`_acao_nas_escolhidas`, `_girar_as_escolhidas_que_sao_metade`, `_pagina_dentro_da_folha`), `_atualizar_previa` só no
ramo do Dividir, `_giros_das_paginas`/`_giros_das_folhas`, `_proporcao_da_pagina`, `_tamanhos_estimados`,
`MARCAS_DA_*`; `ui/widgets/tira_miniaturas.py` (giros e `_metade`); `ui/janela_principal._acertar_a_capa` e a fiação
do menu do girar; `core/etapas.py` (marcas, L95-245 e L587-615); `core/pipeline.preparar_para_recorte` e o fim de
`preparar_metade`; `core/automatico.antes_da_pagina` e o começo de `_dividir`; `ui/tarefas._folha_crua` e
`_giro_da_folha`.

## Suspeitas (dúvidas de outros pedaços; quem ler o pedaço confirma ou descarta)

- (dividir) Ler a folha girada a 150 DPI para medir está escrito em quatro lugares: `core/pipeline.py` L477,
  `core/automatico.py` L609-610, `core/dividir_a_mao.py` L562 e L620-622 (este com `int(rotacao) % 360` próprio).
- (dividir) `core/automatico.py` L1158 também põe `apagada` na direita, fora do `_dividir`; ver se é outra cópia da
  regra de juntar a folha.
- (dividir) `core/automatico._dividir` (L964-968), com duas páginas na folha e a medida "não dividir": põe a direita
  como tirada e deixa `giro_da_pagina` guardado nas duas metades (a folha deixa de ser dividida, o giro fica escondido).
  Ver se algum caminho divide de novo sem passar por `LIMPAR_AO_PARTIR` (`core/dividir_a_mao.py` L84) e faz o giro
  escondido voltar (o achado `b12d6f61` citado em `core/girar.py` L462). Família do remendo A4.
- (desfazer) "Desfazer nesta página" (`ui/desfazer_nesta_pagina.py`) não tem o giro da página entre as etapas
  (Endireitar, Cortar, Mover, Filtro, Marcar). Ver se é decisão (D-621) ou caminho esquecido.
- (como-fica) A chave das prévias é montada em dois lugares de `ui/tarefas.py` (L1150-1157 e L1430-1434), as duas com
  `rotacao` e `giro_da_pagina`; conferir se são a mesma regra.
- (como-fica / marcações) `core/pipeline.preparar_metade` chama `geometria_do_desenho` em três ramos (L713-718,
  L730-735, L761-766); só o primeiro passa `ordem=ordem_do_livro(projeto)`.
- (contagens e situação) No girar de formato "pagina" com `folha:<f>.rotacao` (G-04), `_com_os_avisos_de_agora` guarda
  os avisos das páginas e não os da folha; no formato "folha", o contrário. Conferir se o desfazer devolve os avisos
  certos nos dois.
- (aplicar-em) O "aplicar em" do Endireitar (`_paginas_do_alcance_do_angulo`, `ui/tela_conferir.py` L7118) usa
  `girar.folhas_do_alcance` e `aviso_fora_do_alcance(coisa="página")`; conferir se repete a conta de páginas da D-636.
