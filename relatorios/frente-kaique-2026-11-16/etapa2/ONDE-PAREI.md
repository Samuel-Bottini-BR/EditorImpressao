# ONDE-PAREI — Etapa 2 da frente do notebook do Kaique (verificador, 16/11/2026)

Ramo `kaique-etapa2-2026-11-16` (de `obra-2026-10-26` em `cb41a22a`), cópia `.claude\worktrees\kaique-etapa2`.
Cópia à parte do código de 28/10: `.claude\worktrees\kaique-etapa2-antigo` (HEAD solta em `3961fbff`, junções
`modelos` e `gabarito\paginas`). **Nenhuma linha do programa muda nesta tarefa.**

## Decisões que esta tarefa precisa cumprir

- **D-706** (16/11): "a atualização via internet tem que ser como funciona com apps, não pode ser ele ter que baixar de
  novo um instalador fazer tudo de novo" — aqui só se confere a base (empacotamento de hoje) antes de construir.
- **D-711** (16/11): "vai a versão de teste, mas atualizada para ele." — empacota-se a versão de teste de hoje.
- **D-714** (16/11): "e sim o programa pega sozinho, toda vez que o pc inicializar em segundo plano" — só leitura do
  código para dizer o que falta (item 4).
- **D-723** (16/11): "velopack" — o que o empacotamento de hoje precisa mudar para o Velopack (item 4).
- **D-724** (16/11): "gratis, mas o que é essa assinatura e é segura?" — idem, só apontar.
- **D-722** (16/11): "Sim" (testar no PC do Samuel e desfazer tudo) — esta etapa **não instala nada** no Windows; tudo
  numa pasta de teste dentro da cópia.
- **D-605** (03/11): "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e
  testado" — item 3: projeto salvo pela versão de 28/10 tem de abrir igual na de hoje; o que mudar é dito com a
  decisão que causou.
- **D-637** (05/11): "você tem que pensar na experiencia do usario e no resultado final do livro dentro do programa" —
  seção "Como fica para quem usa e no livro" abaixo.
- Pergunta 5 do plano (16/11): "a ultima vesão foi a que eu deixei na minha area de trabalho o .exe lá" = instalador de
  28/10, do `obra-2026-10-26` perto do `3961fbff` (conferido: o `.exe` da Área de Trabalho é de 28/10 18:10; o último
  commit de código antes dele é o `3961fbff`, 17:30; 26 min de empacotamento).
- Regras: CLAUDE.md §4.10 (caminho inteiro: dividir → endireitar → cortar → filtro; cada foto diz o caminho), §10.9
  (apagar só o que eu criei; junção nunca com `rm -rf`), §11.13 (como escrever para o Samuel); nunca abrir janela na
  tela dele.

## O que já está escolhido e testado aqui

- O empacotador (`empacotar.py --modo pasta`) com as travas de modelos, DLLs (`st_gravura`, `st_ferramentas`), motor do
  Kraken, Tesseract e `vc_redist` (testes em `tests/test_empacotar.py`).
- `--conferir-ocr` no empacotado (`core/ocr_diagnostico.py`, `tests/test_ocr_diagnostico.py`).
- Pasta de dados em `%LOCALAPPDATA%\EditorImpressao`, desinstalar não apaga (CLAUDE.md §7).
- Projeto antigo sem `ordem_do_preparo` segue a ordem antiga (CLAUDE.md §7); o projeto de 28/10 já tem o campo.
- Nada disso é mudado: só se roda e se olha.

## Como fica para quem usa e no livro

- **Hoje o Kaique** abre o programa de 28/10 (instalado pelo `.exe` da Área de Trabalho), e os projetos dele ficam em
  `%LOCALAPPDATA%\EditorImpressao` do notebook.
- **Depois da versão nova**, ele abre o programa e vê os mesmos livros na tela inicial; clica num livro e continua de
  onde parou; o PDF que sai tem as mesmas páginas, cortes e filtros de antes, salvo o que uma decisão nova mudou (e
  isso tem de estar escrito aqui, com o número da decisão).
- Esta etapa **não muda nada** para ele: só prova se a base aguenta.

## O plano (e por quê)

1. **Empacotar a versão de hoje** com `empacotar.py --modo pasta` na minha cópia (saída no `dist\` dela). Por quê: é o
   mesmo programa que o instalador leva, sem precisar de administrador. Para o empacotador achar o motor do Kraken e o
   Visual C++ de dentro de uma cópia, uma junção temporária `.claude\worktrees\EditorImpressao-arquivos` →
   `D:\programas\EditorImpressao-arquivos` (o mesmo jeito do empacotamento de 28/10; tirada no fim com
   `(Get-Item).Delete()`). Anotar tempo e tamanho.
2. **O empacotado abre e trabalha, fora da tela.** Achado de hoje: dá para rodar o programa numa **área de trabalho
   escondida do Windows** (`CreateDesktop`): a janela existe de verdade, com fonte, os prints saem pelo `PrintWindow`, e
   os botões são apertados pelo leitor de tela do Windows (UI Automation, "Invoke"), sem mexer no mouse nem no teclado
   dele, e **nada aparece na tela dele** (testado com uma janelinha: botão apertado, print com texto). Por quê: é o
   único jeito de pilotar o `.exe` empacotado (o modo `offscreen` do Qt não tem janela para apertar). Passos: pasta de
   dados própria (LOCALAPPDATA trocado), `ultima_pasta_de_saida` apontando para uma pasta minha, cópia de um livro do
   acervo, abrir, rodar o Automático (dividir, endireitar, cortar, filtro), processar, conferir o PDF. Depois,
   `--conferir-ocr` nos três leitores de texto.
3. **Projeto do Kaique na versão nova.** Na cópia de 28/10, rodando pelo código (fora da tela, pasta de dados
   própria), criar um projeto de verdade com as ferramentas do programa de 28/10: livro dividido, corte, filtro, uma
   página marcada à mão, uma tirada do livro, cadernos; processar o PDF lá (o "antes"). Depois copiar a pasta de dados
   para a pasta de dados do empacotado de hoje, abrir pelo cartão da tela inicial, comparar campo por campo as
   configurações de cada página e processar o PDF (o "depois"). Comparar número de páginas e imagem de cada página.
   Ressalva já sabida: o "antes" roda pelo código de 28/10 (`.venv` de hoje), não pelo `.exe` instalado de 28/10 (não
   se instala nada).
4. **O que impede a etapa 3 (Velopack)**: conferir no código real cada ponto do estudo (versão do programa, `main.py`,
   `.iss`, `tests/test_empacotar.py`, `--onefile`, pastas ao lado do `.exe`), sem mudar.
5. Relatório nos três formatos, prints abertos um por um, commit e push.

## Andamento

- [x] Leitura (verificador.md, CLAUDE.md, memória, plano, estudo, Livro D-705 a D-726, histórico).
- [x] Junção temporária criada; cópia de 28/10 criada com as junções.
- [x] Teste da área escondida (janelinha): funciona.
- [ ] 1. empacotar (rodando desde 10:54)
## TERMINADO (retomado às ~12:05 de 16/11, ordem da gerente; entregue ~12:25)

- [x] Imagens que faltavam abertas (novo3: n03-1, n05, n06, n07, n02b).
- [x] **2a feito** no empacotado, na área escondida: Righetti folhas 21-30 (cópia de pé) > "Rodar o automático..." >
      Dividir, Endireitar, Cortar, Limpar em Preto e branco (Gravuras desmarcada) > "Rodar 4 etapas" (17 s) >
      "Confirmar e processar" > "Processar": PDF de 20 páginas em 11 s. Janela aparece ~23 s depois de abrir.
      Achado do piloto: o "Toggle" do leitor de tela não marca as etapas do Automático; marcado por clique de verdade.
      Ressalva/bug: faixa preta na beirada esquerda das páginas da esquerda (igual em 28/10). Antes, duas rodadas com a
      receita de fábrica (sem Dividir, Original) guardadas em `saida_teste/etapa2/novo2-receita-de-fabrica` e
      `tentativas/`.
- [x] Item 4 escrito por extenso no relatório.
- [x] Relatório nos três formatos: `relatorio.md`, `relatorio.html`, `relatorio.pdf` (fora do git). PRONTO PARA CONFERIR.
- [x] Sobras tiradas: junção `EditorImpressao-arquivos` (Delete(); a pasta original continua com o motor e o
      vc_redist); cópia `kaique-etapa2-antigo` (junções tiradas com Delete(): `modelos` 18 -> 18 arquivos,
      `gabarito\paginas` 64 -> 64; depois `git worktree remove`); `build/` e `_tmp/` desta cópia (o log foi para
      `saida_teste/etapa2/`). Nenhum `EditorImpressao.exe` aberto. Ficam de propósito, fora do git: `dist/` (o
      empacotado, 1,9 GB) e `saida_teste/etapa2/` (dados, PDFs e prints), para a gerente ou a etapa 3.

## PAUSA (ordem da gerente, ~11:25 de 16/11: o Samuel vai desligar o PC). Nenhum programa meu ficou aberto
(o empacotado do item 2a foi fechado com WM_CLOSE; os servidores de páginas saíram junto; conferido).

- [x] **1. Empacotar** (`empacotar.py --modo pasta`): **10 min 53 s** (646 s no script), **1889 MB** (603 MB de
      `_internal`, o resto motor do Kraken e Tesseract), saiu 0; as duas DLLs do ScanTailor, os 4 modelos, o motor e o
      Tesseract conferidos pelo próprio script. Um aviso do PyInstaller: `scipy.special._cdflib` não achado. Saída:
      `dist/EditorImpressao/` desta cópia (fora do git). Log: `_tmp/empacotar-pasta.log`.
- [x] **2b. `--conferir-ocr` no empacotado** (Palatino 57 e Horas 11; `saida_teste/etapa2/ocr/*.json`): os três
      leitores disponíveis, achados dentro do `dist`; as mesmas contagens de linhas do empacotado de 29/09 (docTR
      24/12, Tesseract 16/0, Kraken 17/16); detector de gravura do ScanTailor abre e lê. Kraken: 90-98 s para abrir o
      motor (PC ocupado com outro teste ao mesmo tempo).
- [x] **3a. Projeto feito pelo programa de 28/10** (código `3961fbff`, área escondida, dados em
      `saida_teste/etapa2/antigo/dados`): Righetti 14 folhas (cópia), girar 1/4 à esquerda todas, Automático (Dividir,
      Endireitar, Cortar, Limpar em Preto e branco, Montar cadernos) = 28 páginas; à mão: página 6 Mágico pro, página 8
      corte à mão, página 10 gravura marcada à mão, página 2 tirada do livro. PDF em 61,6 s: "27 páginas, 2 cadernos,
      14 folhas para imprimir". Cópia do PDF: `antigo/pdf-antes.pdf`. Prints `antigo/prints/01..04` (abertos).
- [x] **3b. O mesmo projeto no EMPACOTADO de hoje** (pasta de dados copiada para `novo3/dados`): cartão "pronto, PDF
      gerado"; tela do livro; "Continuar"; área de trabalho com a página 2 "apagada" e as conferidas com tique;
      "Confirmar e processar" > "Antes de processar" > "continuar assim mesmo" > "Processar" > "Já existe" > "salvar
      como ... (2)" > "Ficou pronto!" em 38 s; fechou com WM_CLOSE (saiu 0).
      **Resultado (máquina):** PDF com as mesmas 14 folhas, mesmo tamanho, **imagem idêntica em todas** (diferença
      0,0); no projeto.json nada mudou nem sumiu em folha ou página (só o caminho do PDF, pela escolha "(2)"); 8 campos
      novos com valor neutro (capa_aberta false, linha_a_mao null, fundo_tirado null, giro_da_pagina 0,
      gravura_achada_a_mao false, gravuras_em_tons_de_cinza false, inserida 0, respeitar_gravuras_achadas true).
      Arquivos: `item3/projeto-comparado.txt`, `item3/pdf-comparado.json`, `item3/pdf-antes-depois.png` (aberto).
      Prints do empacotado: `saida_teste/etapa2/novo3/prints/n01..n07` (abertos n02 e n03; faltam os outros).
      Ressalva (igual antes e depois, não é regressão): sobra faixa preta na beirada esquerda das folhas 1 e 3 do PDF.
- [ ] **2a. Livro novo no empacotado pelo caminho inteiro**: NÃO FEITO. Começou (`item2_novo.py`) e foi parado pela
      ordem da gerente; `saida_teste/etapa2/novo2` ficou pela metade (criada por mim, pode ser apagada).
- [ ] **4. Velopack** (achados só lendo, falta escrever por extenso): não há `.NET` nem `vpk` no PC; o programa não
      sabe a própria versão (só `MinhaVersao` no `.iss`); `main.py` atende `--servidor-de-paginas` e `--conferir-ocr`
      antes da janela (o `App().run()` do Velopack entra antes, e os servidores usam o mesmo `.exe`); `empacotar.py`
      acha motor e Visual C++ por `RAIZ.parent/EditorImpressao-arquivos` (numa cópia de trabalho precisa de junção);
      9 testes de `tests/test_empacotar.py` dependem do Inno; o programa só LÊ ao lado do `.exe` (motor-kraken,
      tesseract), não grava ali (bom para a troca de pasta do Velopack).
- [ ] relatório nos três formatos.

## Próximo passo, ao recomeçar

1. Conferir que nenhum `EditorImpressao.exe` ficou aberto; abrir as imagens de `novo3/prints` que faltam.
2. Item 2a: apagar `saida_teste/etapa2/novo2` e rodar na área escondida:
   `<py312> scripts/lancar.py EditorTesteEtapa2 l2.log <py312> scripts/item2_novo.py <dist>/EditorImpressao.exe
   saida_teste/etapa2/novo2 saida_teste/etapa2/livros/righetti-folhas-21-a-30-de-pe.pdf` (caminhos absolutos;
   py312 = Python 3.12 do sistema, que tem pywinauto). O `item2_novo.py` ainda não rodou até o fim: a janela
   "Automático" pode precisar de ajuste (diálogos aparecem dentro da janela dona no leitor de tela).
3. Item 4 por extenso; relatório com `relatorio.gravar`; commit e push; tirar as sobras abaixo.

## Sobras para tirar no fim (criadas por mim)

- junção `D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos`
- cópia `D:\programas\EditorImpressao\.claude\worktrees\kaique-etapa2-antigo` (junções `modelos`, `gabarito\paginas`)
- área escondida do Windows `EditorTesteEtapa2` (some sozinha quando o último programa nela fecha)

## Perguntas para o Samuel

(nenhuma até agora)
