# Mapa do código

Montado em 20/10/2026 lendo o código do ramo `fase-1` (`b8e9af7`), as docstrings e os comentários "seguro / arriscado
mudar" (regra do [CLAUDE.md §10, item 5](../CLAUDE.md)). **O plano manda**
([PLANO-DEFINITIVO](../docs/plano/PLANO-DEFINITIVO.md)); este mapa só diz onde está cada coisa.

Como usar: ache o assunto, abra o arquivo, leia a docstring do topo. Os arquivos grandes (`core/filtros.py`, 3758
linhas; `ui/tela_conferir.py`, 4218 linhas; `core/pipeline.py`, 2507 linhas) **não se leem inteiros**: procure com
`Grep "^def |^class |^    def "` e leia só a função.

---

## 1. Regras de arquitetura (valem para todo o código)

- **`core/` não importa nada de `ui/`.** Todo o processamento roda por linha de comando, sem abrir janela
  ([CLAUDE.md §7](../CLAUDE.md); o próprio [`core/__init__.py`](../core/__init__.py) repete: "Este pacote NAO pode
  importar nada de ui/. Tudo aqui roda por linha de comando.").
- **Uma página por vez na memória.** Nenhuma função monta lista de páginas processadas: ler → processar → escrever →
  soltar ([`core/pipeline.py`](../core/pipeline.py), topo; [`core/pdf_io.py`](../core/pdf_io.py) é "a única porta de
  entrada e saida de PDF do projeto").
- **A janela nunca congela.** Tudo que demora roda em QThread/QThreadPool ([`ui/tarefas.py`](../ui/tarefas.py)); o
  desenho das páginas do PDF roda em outro processo ([`core/paginas_em_outro_processo.py`](../core/paginas_em_outro_processo.py), §6).
- **Nenhuma exceção fecha a janela.** `sys.excepthook` em [`main.py`](../main.py) grava em `erros.log`
  ([`registro.py`](../registro.py)) e mostra "Aconteceu um problema inesperado, mas o programa continua funcionando."
- **Nenhum modelo desenha pixel.** As redes (doclayout, MobileSAM, docTR, Kraken) só apontam onde estão as coisas.
- **Toda função automática tem botão de ligar e desligar** (regra 8 do plano). Ferramenta do ScanTailor que muda a
  imagem vem **desligada de fábrica**, para livro já começado sair igual (regra da Fase 2, Samuel, 13/10/2026).
- **Projeto antigo sai igual ponto por ponto.** Campo novo no `projeto.json` sempre com valor que reproduz o
  comportamento antigo quando o campo falta (ex.: `ordem_do_preparo`, `dividir_como`, `endireitar_como`).

## 2. O modelo de dados: `ConfigFolha` e `ConfigPagina` ([`modelos.py`](../modelos.py))

Dois níveis, de propósito ([CLAUDE.md §7](../CLAUDE.md)):

- **`ConfigFolha`** = o que veio no PDF de entrada. Campos: `indice`, `dividir`, `posicao_corte`, `confianca_corte`,
  `rotacao` (0/90/180/270), `angulo_detectado`, `confianca_angulo`, `apagada`, `e_paisagem`, `alertas`, `revisada`;
  e, desde a Fase 2, `dividir_como` (o jeito de dividir desta folha) e `sobra` (o corte da sobra do ScanTailor).
- **`ConfigPagina`** = o que vai sair no PDF final. Uma folha dividida vira **duas** páginas (`metade` =
  inteira/esquerda/direita). Campos: `filtro`, `recorte` (None = automático), `angulo_manual`, `endireitar_como`,
  `algoritmo_preto_branco`, `limpar_pontinhos`, os três ajustes **separados** (`forca_preto`, `clareza_melhorar`,
  `intensidade_magico`, 0–100 com 50 no meio), `apagada`, `tem_cor`, `alertas`, `revisada`, `selecao` (as zonas),
  `gravura_forma`, `gravura_feita_com`, `geometria_das_zonas`, os `misto_*` (None = segue o livro),
  `conteudo_escala`, `conteudo_deslocamento`, `tamanho_folha_cm`.
- **Recorte e ângulo moram na página**, não na folha, porque o pipeline os aplica depois de dividir.
- **`Projeto`** = o livro. Além das listas `folhas` e `paginas`: as caixinhas da tela "O que fazer" (`dividir_folhas`,
  `limpar`, `filtro_padrao`, `endireitar`, `cortar_bordas`, `montar_cadernos`, `paginas_por_caderno`, `qualidade_dpi`
  = 300, `detectar_regioes`), e os campos que vieram com cada item: `tem_camadas` e `perguntou_fundo` (1.1);
  `gravura_forma` ("livre"), `gravura_sensibilidade` (100), `gravura_mais_sensivel`, `gravura_normalizar` (1.2);
  `pb_decoracao_em_preto_e_branco` (regra do Preto e branco, 30/09); `misto_so_as_letras`, `misto_fora_do_texto`,
  `misto_papel_da_gravura`, `misto_letras_na_moldura` (1.5); `limpar_pontinhos` (2.7); `dividir_como`,
  `cortar_sobra` (2.1); `endireitar_como` e **`ordem_do_preparo`** (2.2).
- `Acao` (mesmo arquivo) = uma alteração do usuário, para o desfazer ([`historico_acoes.py`](../historico_acoes.py)).
- **Arriscado** ([`modelos.py`](../modelos.py), comentários nas linhas ~275, ~293, ~303): "trocar o setdefault de
  de_dicionario" — é ele que faz o projeto antigo abrir com o comportamento antigo. Mudar o formato dos arquivos de
  dados **precisa perguntar ao Samuel antes** ([CLAUDE.md §6](../CLAUDE.md)).

## 3. A ordem do processamento e o campo `ordem_do_preparo`

Desde 09/10/2026 (G6, item [2.2](itens/2.2.md); pergunta `g6-endireitar-antes`, "Pode começar"), a ordem depende do
livro ([`core/ordem_do_preparo.py`](../core/ordem_do_preparo.py), [`core/pipeline.py`](../core/pipeline.py), topo):

- **Livro novo** (`"endireitar_antes"`, de fábrica): girar 90 → dividir → **endireitar a página inteira** → achar o
  corte na página reta e cortar → filtro → montar cadernos. É a ordem do ScanTailor.
- **Projeto gravado antes de 09/10/2026** (sem o campo; `"cortar_antes"`): girar 90 → dividir → cortar → endireitar
  (com o corte alargado para o giro, `recortar.alargar_para_o_giro`) → filtro → cadernos. Idêntico ponto por ponto
  (teste em `tests/test_ordem_do_preparo.py`).
- Páginas apagadas somem logo depois de dividir. O filtro "Tirar o fundo" (1.1) roda **antes** de tudo, na folha
  inteira do PDF, e nenhum outro filtro vai por cima.
- **Arriscado** (docstring de `ordem_do_preparo.py`): "Os códigos ORDEM_*: estão gravados nos projetos e na
  geometria das zonas"; "ORDEM_DO_PROJETO_ANTIGO: tem de ser CORTAR_ANTES"; o que vier estranho "cai em
  CORTAR_ANTES ... nunca na nova". E a ordem tem de ser a mesma em `pipeline._preparar_metade_e_geometria` e em
  `zonas_na_folha._matriz_folha_para_pagina` ("mudou uma, muda a outra", `pipeline.preparar_metade`).

## 4. Onde o programa guarda estado

`%LOCALAPPDATA%\EditorImpressao` ([`historico.py`](../historico.py) `pasta_de_dados`; [`registro.py`](../registro.py);
[`configuracoes.py`](../configuracoes.py)):

- `historico.json` (livros abertos), `configuracoes.json` (preferências, tema, atalhos), `erros.log`;
- por projeto, numa subpasta: `projeto.json`, `acoes.jsonl` (o desfazer, uma ação por linha), `posicao.json`,
  `resumo.json` (o cartão da tela inicial), `capa.png`, e as cópias de segurança `projeto.antigo-*`.
- Fechar e reabrir preserva o projeto **e o histórico de ações**. Desinstalar **não apaga** essa pasta, de propósito.
- Os testes nunca gravam nela: `tests/conftest.py` troca a pasta no pytest e
  [`pasta_de_dados_dos_scripts.py`](../pasta_de_dados_dos_scripts.py) faz o mesmo nos `teste_*.py` da raiz (regra de
  29/09/2026). A gravação é por trás, num fio só (`projetos._Gravador`), porque o disco D: é USB giratório.

## 5. As DLLs nativas do ScanTailor Advanced (`core/nativo/`)

Código original do **ScanTailor Advanced v1.2.1** (commit `5eaac188…`, GPL-3), copiado sem mudança para
`terceiros/scantailor-advanced/src/` (132 arquivos, soma de cada um em `somas-v1.2.1.txt`, conferida por
`tests/test_st_ferramentas.py`); só a "cola" em C é nossa. Chamadas por `ctypes`; usam o Qt 6.11.1 do PySide6.

| DLL | O que tem | Ponte em Python | Compilar | Item |
|---|---|---|---|---|
| [`st_gravura.dll`](../core/nativo/st_gravura.txt) (167 KB, 28/09/2026) | o detector de gravura do modo Misto | [`core/gravura_scantailor.py`](../core/gravura_scantailor.py) | [`compilar_detector_gravura.py`](../compilar_detector_gravura.py) (cola em `terceiros/scantailor-advanced/ligacao/`) | [1.2](itens/1.2.md) |
| [`st_ferramentas.dll`](../core/nativo/st_ferramentas.txt) (215 KB, 06/10/2026) | limpar pontinhos (Despeckle), dividir (PageLayoutEstimator), endireitar (SkewFinder + limpeza das sombras) | [`core/st_ferramentas.py`](../core/st_ferramentas.py) | [`compilar_st_ferramentas.py`](../compilar_st_ferramentas.py) (cola em `ligacao-ferramentas/`) | [2.7](itens/2.7.md), [2.1](itens/2.1.md), [2.2](itens/2.2.md) |

- O `.txt` ao lado de cada DLL diz versão, compilador (MSVC 19.44), data e SHA-256 (a GPL-3 pede dizer de onde veio).
- Os dois scripts acham o CMake e o Visual Studio 2022 Build Tools, baixam (com `--baixar`) e conferem pela soma o Qt
  6.11.1 (só o qtbase) e o Boost 1.78 em `D:\programas\EditorImpressao-arquivos\ferramentas\`, compilam em
  `ferramentas\build-st-*`, copiam a DLL para `core/nativo/` e testam uma página sintética. Nada pede administrador.
  Recompilar só se o código de `terceiros/` mudar ou o PySide6 trocar de Qt.
- **Sem a DLL o programa não quebra**: cai no detector ou na conta antiga e diz por quê no `erros.log`.
- **Arriscado** (`core/st_ferramentas.py`, `core/gravura_scantailor.py`): "ASSINATURAS: os tipos de cada função em C.
  O ctypes não confere nada; um tipo errado aqui vira travamento, não mensagem"; `VERSAO_API` tem de bater com o
  `.h`; a trava de DPI e de tamanho ("ali o código do ScanTailor corrompe a memória e derrubaria o programa") — "Não
  afrouxar sem medir em processo filho".
- **Achado ao ler o código (20/10/2026, não conferido rodando):** o [`empacotar.py`](../empacotar.py)
  (`nativos_do_programa`) e o [`instalador.iss`](../instalador.iss) só levam e só conferem a `st_gravura.dll`; a
  `st_ferramentas.dll` não aparece em nenhum dos dois. Se for isso mesmo, o programa instalado cairia no "nosso"
  limpar pontinhos, dividir e endireitar, sem avisar. Não achei isso no plano (procurei "st_ferramentas" no
  PLANO-DEFINITIVO). Ver [geral/ambiente.md](geral/ambiente.md).
- No ramo `fase2-caixa-conteudo` a `st_ferramentas.dll` ganhou as caixas (298 KB, interface versão 4); ver §11.

## 6. Outros processos à parte

- **Servidor de páginas** ([`core/paginas_em_outro_processo.py`](../core/paginas_em_outro_processo.py), 30/09/2026):
  dois processos auxiliares desenham as páginas do PDF, porque o PyMuPDF segura o GIL e a janela ficava ~16 s parada.
  Empacotado, é o próprio `EditorImpressao.exe --servidor-de-paginas` ([`main.py`](../main.py) atende esse argumento
  antes de abrir janela). `EDITOR_PAGINAS_AQUI=1` desliga. Se o servidor cai, sobe outro; se não der, desenha aqui.
  **Arriscado**: "fazer o servidor desenhar de outro jeito que nao pdf_io.pagina_para_array (a previa deixaria de ser
  igual ao PDF final); tirar o CREATE_NO_WINDOW ...; tirar o recomeco quando o servidor cai."
- **Motor do Kraken** ([`core/ocr_kraken.py`](../core/ocr_kraken.py) + `motor_kraken/servidor_kraken.py`): Python 3.12
  embutível com o Kraken original e PyTorch para processador, aberto como outro processo uma vez por sessão (6 a 7 s).
  Montado por [`montar_motor_kraken.py`](../montar_motor_kraken.py) (versões travadas em
  `motor_kraken/requisitos-travados.txt`, cada download conferido pela soma) em
  `D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken\`. **Arriscado**: `VERSAO_PROTOCOLO` (tem de bater
  com o servidor), o `-I -X utf8` do comando, ler o erro do motor num fio próprio (senão os dois processos se esperam
  para sempre). Item [1.3](itens/1.3.md).
- **Tesseract** ([`core/ocr_tesseract.py`](../core/ocr_tesseract.py)): chama o `tesseract.exe` a cada página e lê o hOCR.
  Instalado, mas **desligado de fábrica** (Samuel, 29/09/2026).
- `main.py --conferir-ocr <imagem> <saida.json>` ([`core/ocr_diagnostico.py`](../core/ocr_diagnostico.py)): prova, sem
  janela, que o programa empacotado acha os três OCRs e a DLL de gravura.

## 7. Relatórios: `relatorio.gravar` (três formatos)

[`relatorio.py`](../relatorio.py) `gravar(texto, destino)` grava `.md` (para o Claude e o git), `.html` (abre com
dois cliques) e `.pdf` (arquivo). **O Samuel não abre `.md`**: nunca gravar só o `.md` em relatório de teste ou
conferência ([CLAUDE.md §2](../CLAUDE.md)). `converter_pasta` gera o par que faltar; `pasta_de_teste` cria a pasta
no padrão combinado. Depende da biblioteca `markdown` (sem ela as tabelas e imagens somem do `.html`).

---

## 8. `core/` — arquivo por arquivo

Formato: o que faz · funções principais · item do plano · o que é arriscado mexer (citado do código).

### Filtros e montagem da página

- [`core/filtros.py`](../core/filtros.py) (3758 linhas) — **os filtros**: Original, Preto e branco (Sauvola pelo
  DoxaPy, com a regra do Samuel de 30/09/2026 para moldura e gravura), Melhorar (divisão pelo fundo), Mágico pro
  (Melhorar + CLAHE + saturação + nitidez) e o nome "Tirar o fundo" (quem faz é `camadas.py`). Principais:
  `filtros_do_livro`, `filtro_preto_e_branco`, `filtro_melhorar`, `filtro_magico_pro`, `tirar_o_amarelado_da_tinta`,
  `aplicar_filtro`, `aplicar_filtro_com_selecao` (cada área da página do seu jeito), `aplicar_so_os_pedacos` ("só
  neste pedaço"), `k_do_sauvola`/`k_para_a_letra` (medidor de força), `binarizar`, `escolher_algoritmo_automatico`.
  Itens: regras do resultado da Fase 1, [1.5](itens/1.5.md), [2.8](itens/2.8.md) (três tipos de preto e branco),
  [6.1](itens/6.1.md)–[6.3](itens/6.3.md). **Arriscado** (44 avisos no arquivo): o valor `TIRAR_FUNDO` ("é o que fica
  gravado em ConfigPagina.filtro nos projetos salvos"); a correção de cor do Mágico pro ([CLAUDE.md §9](../CLAUDE.md):
  "dividir pelo fundo relativo ao nível do papel ... curva de ombro no canal L ... **Não desfazer isso.**"); "tratar
  Pontinhos pela verdade (`if despeckle:`)"; "tirar a trava da cor: pedacos da moldura dourada viravam blocos
  pretos". Código morto conhecido nas linhas ~2978–2985 (Lista de bugs, 08/10).
- [`core/pipeline.py`](../core/pipeline.py) (2507 linhas) — **orquestra tudo, uma página por vez**. Principais:
  `analisar_projeto` (lê o livro a 150 DPI e propõe corte, ângulo, filtro), `preparar_metade` /
  `preparar_metade_e_geometria` (gira, divide, corta, endireita, nas duas ordens), `garantir_selecao` (acha gravura,
  letra e papel uma vez por página), `renderizar_pagina` (a página como vai sair: prévia = PDF),
  `renderizar_com_filtro`, `processar` (gera o PDF final), `usa_tirar_fundo`, `escolha_da_gravura`,
  `pontinhos_da_pagina`, `angulo_da_pagina`, `recorte_depois_de_mudar_o_angulo`, `converter_zonas_do_livro`,
  `resumo_em_portugues`. Itens [2.2](itens/2.2.md), [1.1](itens/1.1.md), [1.2](itens/1.2.md),
  [para-revisar](itens/para-revisar.md). **Arriscado**: `preparar_metade` "alimenta a previa da tela, o PDF final e o
  avaliar.py"; em `processar`, "guardar aqui qualquer lista de paginas processadas"; "voltar a abrir o EscritorPDF no
  arquivo final, ou apagar" (o arquivo é gravado com outro nome e trocado no fim, para uma queda não estragar o PDF
  antigo).
- [`core/camadas.py`](../core/camadas.py) (1708 linhas) — **"Tirar o fundo" de PDF que já vem em camadas**
  (Internet Archive: Palatino, Opus Majus, Rhetorica, Siebmacher). Começa de uma página branca e põe a camada de cima
  só onde a máscara deixa. Principais: `pdf_tem_camadas`, `resumo_do_pdf`, `ler_camadas`, `compor`, `tirar_fundo`.
  Item [1.1](itens/1.1.md) (aprovado 02/10/2026). **Arriscado** (topo): "TOM_DE_FIGURA, COR_DE_FIGURA,
  TINTA_SO_NO_FUNDO e AREA_DE_FIGURA_ESQUECIDA (medidos nas 14 páginas do gabarito e no livro da Pesel; afrouxar faz
  foto virar pontilhado e xilogravura virar mancha, apertar faz mancha e dobra voltarem)"; `PAPEL_EM_VOLTA_TOM/COR`.
  Seguro: `DPI_DA_ANALISE`, `LINHAS_POR_FAIXA`.
- [`core/misto.py`](../core/misto.py) — **o modo Misto, "Só as letras"**: o Preto e branco só nas letras; gravuras,
  fotos, molduras ficam como no original. Principais: `aplicar_misto`, `opcoes_da_pagina`, `escolhas_da_pagina`,
  `mascara_das_linhas`. Item [1.5](itens/1.5.md) (juntado ao `fase-1` em 06/10/2026). **Arriscado**: "_peso_da_imagem:
  e ela que diz que a marcacao A MAO ganha da maquina"; "Usar outro preto e branco no passo 1" (as regras aprovadas
  moram em `filtro_preto_e_branco`). Bug aberto: marcar "letra e traço" à mão não protege a tinta (`_fora_do_texto`,
  Lista de bugs 12/10).
- [`core/linhas_do_texto.py`](../core/linhas_do_texto.py) — onde estão as linhas de texto para o Misto (opções A e C):
  docTR de fábrica, Kraken como segunda opinião. `linhas_da_pagina`, `aquecer_em_segundo_plano`, `soltar`. Itens
  [1.5](itens/1.5.md), [1.3](itens/1.3.md). **Arriscado**: "Guardar sem a geometria na chave"; mandar a página
  inteira em 300 DPI (prévia e PDF achariam linhas diferentes).
- [`core/pontinhos_scantailor.py`](../core/pontinhos_scantailor.py) — **limpar pontinhos do ScanTailor** (Despeckle,
  pela `st_ferramentas.dll`): pontinho perto da letra fica, solto sai. `limpar_pontinhos`,
  `preto_e_branco_com_pontinhos_do_scantailor`, `escolha_da_pagina`, `dpi_para_os_pontinhos`,
  `limpar_conforme_a_escolha`. Item [2.7](itens/2.7.md). De fábrica "Não limpa nada (desligado)" (decisão de
  07/10/2026). **Arriscado**: "pôr POUCO, NORMAL ou MUITO [como padrão] (contra a decisão de 07/10)"; os códigos vão
  para o `projeto.json`; `FORCAS`. Seguro: os textos da tela (nomes da Rodada 10 do layout: "Sem limpeza · Limpeza
  bruta · Limpeza cuidadosa leve/média/forte").
- [`core/analise.py`](../core/analise.py) — **os alertas** ("onde o programa avisa que pode ter errado"; meta: menos
  de 10% das páginas). `Alerta`, `descrever`, `analisar_folha`, `analisar_pagina`, `analisar_resultado`,
  `avaliar_preto_e_branco`, `detectar_cor`, `agrupar_por_tipo` (painel "Páginas para revisar"). Item
  [para-revisar](itens/para-revisar.md). Seguro: os textos. Bug aberto: o aviso das linhas 80-81 ainda manda à "aba
  Marcar", que não existe mais (13/10).
- [`core/ajustar_pedaco.py`](../core/ajustar_pedaco.py) — "Ajustar o pedaço à figura" e o aviso de papel demais em
  volta (conferência 13, S3, 05/10/2026). `caixa_justa`, `medir_folga`, `avaliar_os_pedacos`, `ajustar_os_pedacos`.
  Só sugere; não muda a marcação sozinho. Perto de [2.18](itens/2.18.md). Seguro: os limiares, dentro das faixas
  escritas.
- [`core/aquecimento.py`](../core/aquecimento.py) — importa o scipy/skimage em segundo plano ao abrir, para não
  travar a primeira prévia (achado de 15/09/2026). Item [5.1](itens/5.1.md).

### Geometria (dividir, girar, endireitar, cortar, folha)

- [`core/recortar.py`](../core/recortar.py) (933 linhas) — **cortar as bordas**: procura a massa da tinta (não a
  beirada do papel), dá 1 mm de folga (decisão P2, 01/10/2026) e não deixa a borda passar no meio de uma peça de
  tinta. `detectar_bordas`, `alargar_para_o_giro`, `aplicar_recorte`, `fatiar`, `caixa_em_pontos`, `Recorte`. Itens
  [2.13](itens/2.13.md)/[2.5](itens/2.5.md) (a caixa da página "seguindo a beirada" fica para o ScanTailor) e **o
  defeito do G6** em [2.2](itens/2.2.md) (faixa preta em página torta com borda de scanner; conserto no ramo
  `conserto-corte-g6-2026-10-13`, §11). **Arriscado** (vale o arquivo todo): "este corte roda em TODA pagina de TODO
  livro. Cada numero aqui foi acertado contra uma queixa real ... Mexer em qualquer um exige medir de novo as paginas
  do gabarito". Seguro: `FOLGA_MM`. Bugs abertos: Escola 197 (`SOBRA_DE_TINTA`) e `_apagar_riscas_de_dobra` no
  Cursus 3 (Lista de bugs, 13/10).
- [`core/ordem_do_preparo.py`](../core/ordem_do_preparo.py) — a ordem cortar antes / endireitar antes (§3). Item
  [2.2](itens/2.2.md).
- [`core/endireitar.py`](../core/endireitar.py) — o endireitar "do programa" (perfil de projeção), `rotacionar`,
  `rotacionar_e_cortar`, `girar_90`. Item [2.2](itens/2.2.md). **Arriscado**: "girar em volta do centro da CAIXA
  (seria a ordem antiga)".
- [`core/endireitar_scantailor.py`](../core/endireitar_scantailor.py) — o endireitar do ScanTailor (SkewFinder),
  **de fábrica** (G4 (b), 05/10/2026). `medir`, `medir_na_pagina`, `discordam` (aviso C1 quando as duas contas
  diferem mais de 0,3°). Item [2.2](itens/2.2.md). **Arriscado**: "SINAL_DO_SCANTAILOR: errado, a página sai duas
  vezes mais torta"; os códigos `JEITO_*` estão gravados nos projetos. `LIMITE_DA_DISCORDANCIA` (0,3°) é decisão do
  Samuel.
- [`core/dividir.py`](../core/dividir.py) — o dividir "do programa": acha a lombada pela faixa escura.
  `detectar_lombada`, `dividir_imagem`. Item [2.1](itens/2.1.md).
- [`core/dividir_scantailor.py`](../core/dividir_scantailor.py) — o dividir do ScanTailor (PageLayoutEstimator) e o
  "corte da sobra" (G3). `achar`, `posicao_da_divisao`, `sobra_da_folha`. Item [2.1](itens/2.1.md); de fábrica "o do
  ScanTailor" (07/10/2026). **Arriscado**: `MODO_*`/`TIPO_*` têm de ser os números do ScanTailor; o DPI passado.
- [`core/girar.py`](../core/girar.py) — girar de 90 em 90 com "aplicar em" (só esta / todas / daqui em diante / pares /
  ímpares). Só contas. Item [2.3](itens/2.3.md). **Arriscado**: "o sentido dos giros (GIRO_DIREITA = +90 ...)";
  "pares/impares" contam o número da folha que a tela mostra (índice + 1).
- [`core/zonas_na_folha.py`](../core/zonas_na_folha.py) — guarda as zonas da marcação **em relação à folha original**
  (decisão D2, 02/10/2026), para sobreviver a mudanças de corte, ângulo, divisão e giro. `pagina_para_folha`,
  `folha_para_pagina`, `acompanhar`, `geometria_do_desenho`. Itens [2.18](itens/2.18.md), [2.2](itens/2.2.md).
  **Arriscado**: a ordem das etapas em `_matriz_folha_para_pagina` "tem de ser a MESMA de
  core/pipeline._preparar_metade_e_geometria"; "gravar zonas_na_folha sem geometria_das_zonas".
- [`core/folha.py`](../core/folha.py) — tamanho físico da folha final e onde o recorte fica dentro dela
  (`compor_na_folha`, `medidas_do_recorte_em_cm`). Itens [2.6](itens/2.6.md), [2.4](itens/2.4.md). Pela explicação
  de 14/10/2026, formato e margens passam para a hora de imprimir (ver o item 2.6).

### Seleção (gravura, letra, papel)

- [`core/selecao.py`](../core/selecao.py) — **a seleção**: uma lista de regiões por página, que os filtros leem. As
  três formas de marcar (automático, rede, à mão) produzem a mesma coisa. `Regiao`, `Selecao` (`mascara`, `peso`,
  `peso_do_filtro`), `retangulo`, `poligono`, `traco`, `de_mascara`. Itens [2.18](itens/2.18.md),
  [3.1](itens/3.1.md)–[3.7](itens/3.7.md).
- [`core/detectar_regioes.py`](../core/detectar_regioes.py) (1661 linhas) — **acha sozinho o que é o quê**: layout
  (doclayout.onnx) + cor + tinta, e a gravura pelo ScanTailor (`GRAVURA_SCANTAILOR`, forma "livre" de fábrica).
  `detectar`, `OpcoesDaGravura`, `DetectorDeLayout`, `mascara_de_cor`, `mascara_de_tinta`, `refinar_para_tinta`,
  `explicar_em_portugues`. Itens [1.2](itens/1.2.md), [1.5](itens/1.5.md). **Arriscado**: "tirar o dpi_do_scan traz
  de volta o caso do Marial 150"; "subir o teto devolve a lentidao"; "engordar BARRA_FINA tira a borda de foto que
  encosta na beirada".
- [`core/gravura_scantailor.py`](../core/gravura_scantailor.py) — ponte até a `st_gravura.dll` (§5). `detectar_gravura`,
  `DetectorGravuraScanTailor`, `motivo_de_recusa`, `figuras_pelo_scantailor`. Item [1.2](itens/1.2.md) (aprovado
  02/10/2026). A aba Marcar e o item 1.1 ainda não a usam (docstring).
- [`core/rede_selecao.py`](../core/rede_selecao.py) — "Selecionar objeto" por clique (MobileSAM, sem placa de vídeo:
  0,5 s por página, 40 ms por clique). "A rede só aponta, nunca desenha." `preparar`, `recortar_no_ponto`. Item
  [3.1](itens/3.1.md).

### OCR (só acha onde está o texto; transcrever é a Fase 7)

- [`core/ocr_comum.py`](../core/ocr_comum.py) — o formato comum (`ResultadoOCR`, `LinhaOCR`, `PalavraOCR`,
  `abrir_processo`).
- [`core/ocr_doctr.py`](../core/ocr_doctr.py) — docTR `fast_base` pelo OnnxTR, dentro do programa
  (`modelos\doctr\rep_fast_base-1b89ebf9.onnx`, 42 MB). **Arriscado**: usa um método interno do OnnxTR, "Por isso a
  versão do OnnxTR está travada no requirements.txt (0.9.0)".
- [`core/ocr_kraken.py`](../core/ocr_kraken.py) — ponte até o motor do Kraken (§6).
- [`core/ocr_tesseract.py`](../core/ocr_tesseract.py) — ponte até o `tesseract.exe`; desligado de fábrica.
- [`core/ocr_comparar.py`](../core/ocr_comparar.py) — compara os OCRs ligados; onde discordam, a página vai para
  "Para revisar". **Arriscado**: `TOLERANCIA`, `ESPESSURA_MINIMA`, `AREA_MINIMA`, `COBERTURA_PARA_CONFIRMAR`,
  `LADO_DE_TRABALHO` "foram calibrados juntos nas 22 páginas do 1.3".
- [`core/ocr_diagnostico.py`](../core/ocr_diagnostico.py) — o `--conferir-ocr` (§6).
- Todos: item [1.3](itens/1.3.md) (aprovado 02/10/2026; o ligar/desligar na tela fica para quando 1.4/1.5 voltarem).
  O docstring de `ocr_doctr.py` e `ocr_tesseract.py` diz "Nem o pipeline, nem a tela ... usam este módulo ainda":
  hoje só o Misto usa o docTR (e o Kraken como segunda opinião), por `linhas_do_texto.py`.

### Entrada, saída e base

- [`core/pdf_io.py`](../core/pdf_io.py) — a única porta de PDF: `abrir_pdf`, `info_paginas`, `pagina_para_array`,
  `dpi_real_da_pagina`, `dpi_seguro`, `EscritorPDF` (monta o PDF de saída página por página). **Arriscado**: mudar a
  conversão da imagem comprimida (o PDF sairia diferente).
- [`core/paginas_em_outro_processo.py`](../core/paginas_em_outro_processo.py) — o servidor de páginas (§6). Itens
  [5.1](itens/5.1.md).
- [`core/cadernos.py`](../core/cadernos.py) — **imposição em cadernos** (a conta da dobra: frente `[N-2i] [1+2i]`,
  verso `[2+2i] [N-1-2i]`) e `conferir_sequencia` (simula a dobra sem ninguém olhar folha por folha). `impor_pdf`,
  `montar_ordem`, `instrucoes_de_impressao`. Item [6.5](itens/6.5.md); referência da fase de impressão
  ([2.6](itens/2.6.md)). A pesquisa de 20/10/2026 (ramo `pesquisa-impressao-2026-10-19`) achou que "hoje o último
  caderno sai do tamanho cheio (23 págs em cadernos de 20 = 17 brancas)".
- [`core/st_ferramentas.py`](../core/st_ferramentas.py) — abre a `st_ferramentas.dll` (§5).

## 9. `ui/` — as telas

Fluxo ([`ui/janela_principal.py`](../ui/janela_principal.py)): Início → O que fazer → (análise) → Conferir →
(processamento) → Pronto. O layout novo (etapas 2 e 3, painel Propriedades, textos das rodadas 12 e 13) entrou no
`fase-1` em 14/10/2026 (`ccc84aa`); quem mexe em `ui/` é o agente de layout ([layout](itens/layout.md),
[4](itens/4.md)). Mudar tela **precisa perguntar antes** ([CLAUDE.md §6](../CLAUDE.md)).

- [`ui/janela_principal.py`](../ui/janela_principal.py) (1623) — a janela única (QStackedWidget), abrir livro,
  analisar, processar, perguntar "Este livro tem fundo separado. Quer tirar o fundo?" (1.1), gravar e recomeçar com
  cópia. **O arquivo mais citado na Lista de bugs** (§12): perda de trabalho, `_analise_pronta`, `pdf_gerado`.
  **Arriscado**: ~28 avisos, quase todos sobre a ordem de gravar ("apagar antes de gravar o livro aberto", "refazer
  sem a copia", "chamar isto no closeEvent ...").
- [`ui/tela_conferir.py`](../ui/tela_conferir.py) (4218) — a tela de trabalho: prévia, ferramentas, miniaturas,
  desfazer. `TelaConferir` (`carregar`, `escolher_ferramenta`, `ir_para_pagina`, `apagar_pagina`, `desfazer`,
  `refazer`, `tratar_tecla`), `protegido` (nenhum botão fecha a janela). **Arriscado**: "mudar a marcacao sem passar
  por _registrar (o desfazer nao ...)"; "pintar nele a amostra pura (o Kaique escolheria às cegas)". Textos sem
  acento conhecidos (linhas ~265 e ~2359, Lista de bugs).
- [`ui/tela_inicio.py`](../ui/tela_inicio.py) — cartões dos livros (capa, andamento, continuar, recomeçar, renomear,
  tirar da lista). [`ui/widgets/area_arrastar.py`](../ui/widgets/area_arrastar.py) — arrastar o PDF;
  `abrir_dialogo_de_arquivo` (o conserto do menu "Abrir", [CLAUDE.md §9](../CLAUDE.md)).
- [`ui/tela_opcoes.py`](../ui/tela_opcoes.py) — "O que fazer": caixinhas ligadas ao `Projeto` em tempo real.
  **Arriscado**: "ligar self.projeto antes dos setChecked".
- [`ui/tela_final.py`](../ui/tela_final.py) — progresso e "Pronto" (com a conferência dos cadernos). Item [6.5](itens/6.5.md).
- [`ui/tela_ampliada.py`](../ui/tela_ampliada.py) — a página grande e o "comparar dois filtros".
- [`ui/tela_configuracoes.py`](../ui/tela_configuracoes.py) — atalhos editáveis (Fase 4, "já no programa"; [2.19](itens/2.19.md)).
- [`ui/tarefas.py`](../ui/tarefas.py) — `TarefaAnalise`, `TarefaProcessar`, `TarefaConverterZonas`,
  `GerenciadorPrevias` (fila e cache das prévias). **Arriscado**: "passar uma folha girada=True ao preparar_metade";
  "guardar o que chega de uma geracao velha".
- [`ui/barra_de_menu.py`](../ui/barra_de_menu.py) — os menus (uma tabela só, que também gera a lista de atalhos).
- [`ui/estilo.py`](../ui/estilo.py) — os três temas (escuro, cinza de fábrica, claro; rodada 7, 06/10/2026); barra de
  rolagem cinza `#a8a49e` de propósito ([CLAUDE.md §9](../CLAUDE.md)). Nada de emoji.
- [`ui/perguntas.py`](../ui/perguntas.py) — caixas com botões em português ("entendi", não "OK").
- [`ui/janela_confirmar.py`](../ui/janela_confirmar.py) — "Confirmar e processar": pasta, nome e avisos.
- [`ui/dialogo_tamanho_da_folha.py`](../ui/dialogo_tamanho_da_folha.py) — tamanho físico da folha (só devolve o
  tamanho; não mexe no corte). Item [2.6](itens/2.6.md).
- `ui/widgets/`: [`paineis.py`](../ui/widgets/paineis.py) (1602; coluna de ícones da direita e os painéis Para revisar,
  Automático, Marcar como, Propriedades, Filtro da página, Histórico), [`visualizador.py`](../ui/widgets/visualizador.py)
  (1193; a prévia com corte, recorte, ângulo, linha-guia do G5 — **arriscado**: o sinal do giro desenhado),
  [`editor_selecao.py`](../ui/widgets/editor_selecao.py) (marcar à mão: retângulo, elipse, laço, pincel; itens
  [3.5](itens/3.5.md), [2.18](itens/2.18.md)), [`trilha_agrupada.py`](../ui/widgets/trilha_agrupada.py) (ferramentas
  agrupadas como no Photoshop, rodada 8), [`trilha_ferramentas.py`](../ui/widgets/trilha_ferramentas.py) (a trilha
  antiga; `tests/test_trilha_e_opcoes.py` ainda a testa — Lista de bugs, 09/10), [`barra_opcoes.py`](../ui/widgets/barra_opcoes.py),
  [`barra_girar.py`](../ui/widgets/barra_girar.py) (girar no painel e no canto; [2.3](itens/2.3.md)),
  [`escolhas_do_misto.py`](../ui/widgets/escolhas_do_misto.py) (a caixinha "Só as letras"; "PROVISÓRIO ATÉ O
  LAYOUT"), [`cartao_filtro.py`](../ui/widgets/cartao_filtro.py) (os cartões mostram a página real),
  [`medidor.py`](../ui/widgets/medidor.py) (o deslizante sem número), [`tira_miniaturas.py`](../ui/widgets/tira_miniaturas.py),
  [`folhear_pdf.py`](../ui/widgets/folhear_pdf.py), [`destino.py`](../ui/widgets/destino.py).

## 10. Raiz do repositório

**O programa e os dados**
- [`main.py`](../main.py) — ponto de entrada; atende `--servidor-de-paginas` e `--conferir-ocr` antes de abrir janela.
- [`modelos.py`](../modelos.py) — `ConfigFolha`, `ConfigPagina`, `Projeto`, `Acao` (§2).
- [`projetos.py`](../projetos.py) (1227) — os projetos salvos: assinatura do PDF (nunca copia o livro), gravar por
  trás (`salvar_estado_por_tras`, `_Gravador`), cópias de segurança (`guardar_copia_do_trabalho`), `remover_da_lista`
  (guarda as cópias). **Arriscado**: "escrever direto em destino; tirar o fsync" (queda de energia); "mais de um fio".
- [`historico_acoes.py`](../historico_acoes.py) — desfazer/refazer ilimitado em `acoes.jsonl` (padrão Command).
  Mexer no desfazer **precisa perguntar antes** ([CLAUDE.md §6](../CLAUDE.md)).
- [`historico.py`](../historico.py) — lista de livros recentes e a pasta de dados. [`configuracoes.py`](../configuracoes.py)
  — preferências. [`atalhos.py`](../atalhos.py) — registro único dos atalhos. [`registro.py`](../registro.py) —
  `erros.log`. [`relatorio.py`](../relatorio.py) — §7.

**Montar, compilar, empacotar**
- [`empacotar.py`](../empacotar.py) + [`instalador.iss`](../instalador.iss) — pasta, arquivo único (pendrive) e
  instalador; ver [geral/ambiente.md](geral/ambiente.md). Item [6.8](itens/6.8.md). **Arriscado**: o destino de cada
  modelo, o `--contents-directory _internal`, os nomes `motor-kraken\` e `tesseract\`.
- [`empacotar_teste_velocidade.py`](../empacotar_teste_velocidade.py) — o pacote do teste de velocidade para o
  notebook do Kaique (item [0.6](itens/0.6.md)). O `dist\TesteVelocidade-notebook-do-Kaique.zip` **não pode ser
  apagado nem refeito** (Registro, 28/09/2026).
- [`compilar_detector_gravura.py`](../compilar_detector_gravura.py), [`compilar_st_ferramentas.py`](../compilar_st_ferramentas.py)
  — §5. [`montar_motor_kraken.py`](../montar_motor_kraken.py) — §6.

**Medir e conferir**
- [`teste_velocidade.py`](../teste_velocidade.py) (2356) — item [0.5](itens/0.5.md): abrir o livro de 300 folhas,
  trocar de página, processar 10 páginas (Mágico pro e Preto e branco), memória. Ver [geral/pc-e-github.md](geral/pc-e-github.md).
- [`conferencia.py`](../conferencia.py) — página de antes/depois de qualquer item (item [0.4](itens/0.4.md)), pelas
  páginas de `gabarito/lista.json`.
- [`avaliar.py`](../avaliar.py) — a régua dos filtros ([CLAUDE.md §4.2](../CLAUDE.md): "dá número bom enquanto a mancha
  do verso piora"). [`avaliar_selecao.py`](../avaliar_selecao.py) — a régua da seleção.
- [`conferir_gravura_scantailor.py`](../conferir_gravura_scantailor.py) — a DLL dá a mesma máscara que o ScanTailor
  de verdade (gabarito de 24/09). [`rodada_gravura_1_2.py`](../rodada_gravura_1_2.py),
  [`rodada_opcoes_gravura.py`](../rodada_opcoes_gravura.py) (1.2), [`rodada_pontinhos_scantailor.py`](../rodada_pontinhos_scantailor.py)
  (2.7), [`montar_misto.py`](../montar_misto.py) (1.5, por linha de comando) — rodadas de antes/depois de itens já feitos.
- [`conferir.py`](../conferir.py) — conferência guiada de amostras. [`gerar_prints.py`](../gerar_prints.py) e
  [`montar_para_conferir.py`](../montar_para_conferir.py) — os prints da tela e o `relatorios/para-conferir.html` antigo.
- [`teste_botoes.py`](../teste_botoes.py) (1332) — **clica em todos os botões de todas as telas, de verdade**, sem
  abrir janela na tela (desde 30/09/2026). Roda no GitHub ("janela") e no PC. Cuidado: clica também em botões
  escondidos (PARTE -15 §6).
- Os outros 17 `teste_*.py` da raiz (`teste_acervo`, `teste_bateria`, `teste_completo`, `teste_robustez*`,
  `teste_filtros`, `teste_interface`, `teste_livros`, `teste_pipeline`, ...) são testes manuais antigos, de agosto e
  setembro: geram imagem e relatório, **não são coletados pelo pytest** ([CLAUDE.md §4.5](../CLAUDE.md)).
- [`pasta_de_dados_dos_scripts.py`](../pasta_de_dados_dos_scripts.py) — isola a pasta de dados dos scripts.

**Pastas que não são código Python do programa**: `terceiros/scantailor-advanced/` (§5), `motor_kraken/` (§6),
`velhos/` (o `EditorImpressao.spec` velho, guardado por decisão de 28/09), `docs/`, `relatorios/`, `gabarito/` (só o
`LEIA-ME.md`, a `lista.json` e as `ocr-zonas*.json` estão no git), `modelos/` (fora do git).

## 11. `tests/` (o pytest)

- **115 arquivos `test_*.py`** no `fase-1` de hoje, 1672 funções `def test_` (contadas em 20/10/2026); com o
  `parametrize`, a suíte coleta **~2.050 casos** (2049 passaram na rodada 38662254297, 14/10/2026). `conftest.py`
  põe o Qt sem tela, pasta de dados própria e falha em 20 s em vez de travar numa caixa sem resposta.
- Rodar **um arquivo por vez** no PC; a suíte inteira no GitHub ([geral/pc-e-github.md](geral/pc-e-github.md)).
- Por assunto (os principais):
  - filtros e imagem: `test_filtros_algoritmos`, `test_preto_e_branco_regra_30_09`, `test_decoracao_no_preto_e_branco`,
    `test_medidor_nas_paginas_otsu`, `test_papel_dentro_da_gravura`, `test_melhorar_em_volta_da_gravura`,
    `test_limpar_papel`, `test_alerta_pb`;
  - 1.1 camadas: `test_camadas` (precisa do `gabarito\`), `test_tirar_fundo_no_programa`, `test_so_neste_pedaco_no_tirar_o_fundo`;
  - 1.2 gravura: `test_gravura_scantailor`, `test_gravura_no_processamento`, `test_gravura_na_aba_marcar` (tem um teste
    instável, Lista de bugs 09/10), `test_opcoes_da_gravura_na_tela`, `test_detectar_regioes`;
  - 1.3 OCR: `test_ocr_doctr`, `test_ocr_kraken`, `test_ocr_tesseract`, `test_ocr_comparar`, `test_ocr_diagnostico`
    (pulam sem modelo ou motor: são os ~59–72 "pulados");
  - 1.5 Misto: `test_misto*` (6 arquivos), `test_so_neste_pedaco_*`;
  - Fase 2: `test_dividir_*` (2.1), `test_endireitar_*` e `test_ordem_do_preparo` (2.2), `test_girar*` (2.3),
    `test_pontinhos_scantailor`, `test_limpar_pontinhos_*` (2.7), `test_st_ferramentas`, `test_corte_*`;
  - zonas e seleção: `test_zonas_na_folha`, `test_converter_zonas_ao_abrir`, `test_selecao`, `test_editor_selecao`,
    `test_ajustar_pedaco*` (5 arquivos), `test_marcacao_em_todas`;
  - trabalho salvo (os bugs graves de 29/09 a 06/10): `test_trabalho_nao_se_perde`, `test_salva_sozinho`,
    `test_gravar_por_tras`, `test_gravacao_aguenta_queda_de_energia`, `test_recomeco_limpa_o_historico`,
    `test_historico_depois_de_reabrir`, `test_tirar_da_lista_nao_volta`, `test_mesmo_livro_outro_caminho`,
    `test_ja_existe_arquivo_com_esse_nome`, `test_gerar_o_mesmo_livro_de_novo`, `test_projetos`;
  - tela: `test_paineis*`, `test_trilha_agrupada`, `test_visualizador`, `test_tela_inicio`, `test_janela_cabe_na_tela`,
    `test_botoes_em_portugues`, `test_sem_janela_na_tela`, `test_barra_de_menu`;
  - conferências do Samuel viradas teste: `test_conferencia`, `test_conferencia_5`, `test_conferencia_6`;
  - ferramentas: `test_empacotar`, `test_empacotar_teste_velocidade`, `test_teste_velocidade`, `test_relatorio`,
    `test_requirements`, `test_pasta_de_dados_dos_*`.
- Regra nova (19/10/2026, [CLAUDE.md §4.7](../CLAUDE.md)): todo conserto de bug ganha um teste que **falha no código
  antigo e passa no novo**, com a data e o bug no nome ou na docstring.

---

## 12. Em ramos, ainda não no `fase-1`

Comparado em 20/10/2026, ~04h40 (hora do PC), `git ls-tree` e `git diff origin/fase-1...origin/<ramo>` em `core/` e `ui/`.

| Ramo | Arquivos novos (core/ui) | Arquivos mudados | Últimos commits (`git log --oneline`) | Estado |
|---|---|---|---|---|
| `fase2-para-revisar` (`ce2b835`, 13/10) | `core/revisar.py` (a regra ajustada: desenho apagado, figura além da gravura, faixa escura na beirada, texto falhado, página sem conteúdo), `core/avisos.py` (a lista do "Para revisar" e o "está bom" em cada nível), `ui/janela_dos_avisos.py` (o seletor grande e a janela "Antes de processar") | `core/pipeline.py` (+649), `core/analise.py`, `core/misto.py`, `core/linhas_do_texto.py`, `modelos.py` (campos novos, ex. `alertas_aceitos`, `marcacao_provisoria`), `ui/tela_conferir.py`, `ui/tarefas.py`, `ui/tela_opcoes.py`, `ui/widgets/paineis.py`, `cartao_filtro.py`, `editor_selecao.py`, `teste_botoes.py` | `ce2b835` Para revisar: a marcacao do tamanho do PDF procurada por tras e a forca sozinha (P3) fechadas · `bdc8142` EM ANDAMENTO: a busca por tras so comeca com as previas paradas · `36a6549` · `a841fd0` · `0541236` Forca do preto sozinha | PRONTO PARA CONFERIR; **não contém o `fase-1` de hoje** (falta o layout de 14/10: não tem `ui/widgets/trilha_agrupada.py`). Suíte no GitHub: 2101 passaram. Ver [para-revisar](itens/para-revisar.md); ONDE-PAREI em `ramo fase2-para-revisar: relatorios/para-revisar-impl/ONDE-PAREI.md` |
| `fase2-caixa-conteudo` (`a67e1f0`, 20/10) | `core/caixas_scantailor.py` (caixa da página e caixa do conteúdo do ScanTailor: `achar`, `achar_na_pagina`) | `core/st_ferramentas.py`, `core/nativo/st_ferramentas.dll` (215 → 298 KB) e `.txt`, `compilar_st_ferramentas.py` | `a67e1f0` Merge remote-tracking branch 'origin/fase-1' into fase2-caixa-conteudo · `b8e9af7` (fase-1) | PRONTO PARA CONFERIR por máquina (76 testes), **ninguém chama o módulo** (há um teste que falha se alguém ligar sem querer); ligar só depois da `g7` (19/10/2026). Itens [2.13](itens/2.13.md), [2.5](itens/2.5.md). ONDE-PAREI em `ramo fase2-caixa-conteudo: relatorios/caixa-conteudo-impl/ONDE-PAREI.md` |
| `conserto-corte-g6-2026-10-13` (`3283012`, 20/10) | — | `core/recortar.py` (+327: "A cunha do giro", `detectar_bordas(..., girada=, como_veio=)`), `core/pipeline.py` (só a chamada) | `3283012` EM ANDAMENTO: Pesel 21 volta a sair inteiro no livro novo · `3e1cc3a` Junta o fase-1 (b8e9af7 ...) ao conserto do corte, sem conflito · `b8e9af7` | Samuel deu "Melhorar" em 13/10/2026; hoje o implementador acerta o Pesel 21 (passos 5 a 8 do ONDE-PAREI ainda abertos: medida das 89 páginas, projeto antigo, antes/depois, suíte). Item [2.2](itens/2.2.md). ONDE-PAREI em `ramo conserto-corte-g6-2026-10-13: relatorios/conserto-corte-g6/ONDE-PAREI.md` |
| `layout-impl-2026-10-08` (`e94fe8c`, 13/10) | — | — | `e94fe8c` Layout: "a do Editor" tambem na tela "O que fazer" · `35eb5a6` · `79c85f2` teste_botoes passa com o layout novo (221 acoes) · `b9f2788` · `e7be755` | Já está inteiro dentro do `fase-1` (juntado em 14/10/2026). As etapas 4 a 7 seguem no ramo novo `layout-etapas4a7-2026-10-19` (só o começo do ONDE-PAREI, sem código ainda) |
| `pesquisa-impressao-2026-10-19` (`05efc56`, 20/10) | — | — (só `docs/pesquisa/`) | `05efc56` Pesquisa da impressao: prova do livreto com margens e figuras · `c522919` comeco e ONDE-PAREI · `b8e9af7` | Pesquisa em andamento, sem código do programa. Itens [2.6](itens/2.6.md), [6.5](itens/6.5.md). ONDE-PAREI em `ramo pesquisa-impressao-2026-10-19: docs/pesquisa/ONDE-PAREI-impressao.md` |
| `claude/list-server-files-gkos8v` (`0e614f5`, 20/10) | — (não tem `core/ordem_do_preparo.py` nem `trilha_agrupada.py`: o código do programa ali é velho, de 09/10; o que importa é a `.github/`) | `.github/workflows/testes-windows.yml`, `.github/scripts/velocidade_ab.py` (novo), `preparar_versao.sh` | `0e614f5` Filtro de velocidade: ONDE-PAREI (passos 2 a 4) · `c47a0e2` modo velocidade_ab · `3e4960b` · `060b615` · `0f0145c` | O ramo do workflow "Testes no Windows". Filtro de velocidade em construção (passos 5 a 9 abertos). Ver [geral/pc-e-github.md](geral/pc-e-github.md) |

Também apareceu hoje o ramo `fase2-scantailor-itens-2026-10-19` (Fase 2 a partir do 2.8, "igual ao ScanTailor"; só o
ONDE-PAREI, 2.8 "em andamento", sem código ainda).

## 13. Arquivos que mais quebram

Contei quantas vezes o **nome do arquivo** aparece na Lista de bugs do plano (seção 5, linhas 190–394 do
[PLANO-DEFINITIVO](../docs/plano/PLANO-DEFINITIVO.md)), em 20/10/2026. Muitos bugs citam a tela ("aba Bordas", "tela O
que fazer") e não o arquivo; esses não entraram na conta.

| Arquivo | Citações | Do que são, quase sempre |
|---|---|---|
| [`ui/janela_principal.py`](../ui/janela_principal.py) | 23 | perda de trabalho ao reabrir, fechar, recomeçar (29/09–06/10, quase todos consertados "a conferir"); `pdf_gerado` do cartão; `_analise_pronta` |
| [`core/filtros.py`](../core/filtros.py) | 22 | cores e moldura no Preto e branco e no Mágico pro; código morto (08/10) |
| [`core/camadas.py`](../core/camadas.py) | 12 | o "Tirar o fundo" (1.1): perda de manuscrito claro (Siebmacher), papel azulado, faixa cinza, ferrugem rosada |
| [`core/recortar.py`](../core/recortar.py) | 9 | corte que parte letras, faixa preta, Escola 197, Cursus 3 |
| [`ui/tela_conferir.py`](../ui/tela_conferir.py) | 8 | textos sem acento, observações escondidas, "a tela mostra o que o PDF não tem" |
| [`core/pipeline.py`](../core/pipeline.py) | 6 | prévia × PDF, avisos |
| [`core/detectar_regioes.py`](../core/detectar_regioes.py) | 6 | gravura achada a mais ou a menos |
| [`projetos.py`](../projetos.py) | 5 | trabalho salvo |
| [`relatorio.py`](../relatorio.py) | 5 | PDF dos relatórios (resolvido em 28/09) |
| [`empacotar.py`](../empacotar.py) | 5 | instalador sem os modelos (25/09) |
| `tests/conftest.py` | 4 | testes escrevendo no `erros.log` de verdade (08/10) |
| [`core/analise.py`](../core/analise.py) | 4 | avisos errados ou com frase velha |

Leitura: mexer em `janela_principal.py` (gravar e reabrir), `filtros.py` e `camadas.py` pede o maior cuidado e os
testes de "trabalho salvo" da §11. Ver também [bugs.md](bugs.md).
