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
- [ ] 2. abrir e processar no empacotado
- [ ] 3. projeto de 28/10 na versão nova
- [ ] 4. Velopack
- [ ] relatório

## Sobras para tirar no fim (criadas por mim)

- junção `D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos`
- cópia `D:\programas\EditorImpressao\.claude\worktrees\kaique-etapa2-antigo` (junções `modelos`, `gabarito\paginas`)
- área escondida do Windows `EditorTesteEtapa2` (some sozinha quando o último programa nela fecha)

## Perguntas para o Samuel

(nenhuma até agora)
