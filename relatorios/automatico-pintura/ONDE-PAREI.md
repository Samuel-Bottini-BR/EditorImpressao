# "Só as letras" no Automático e a pintura da capa (D-585) — onde parei

Ramo `automatico-pintura-2026-10-29` (saiu de `obra-2026-10-26`, commit `226536c`), worktree
`.claude/worktrees/auto-pintura`. Agente de consertos, 29/10/2026. Sem push, sem juntar.

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

Conferidas no `docs/plano/DECISOES.md` desta worktree:

- **D-144** (30/09/2026): "Mantém a cor original (como o ANTES); traço preto só se eu escolher" · 01/10, P1: "Sim,
  mantém a cor - [...] o resultado do preto e branco da iluminura não está bom." → no Preto e branco, moldura e
  iluminura ficam com a cor de fábrica.
- **D-147** (30/09/2026): P1a "Cinza (tons de cinza): BOM" → no Preto e branco, foto e pintura saem em tons de cinza,
  nunca pontilhadas.
- **D-148** (30/09 e 05/10/2026): "(a) Uma caixinha 'Só as letras' dentro do Preto e branco, para o livro (tela 'O que
  fazer') e para a página (aba Filtro) (recomendado)" → marcada, só as letras viram preto e branco; gravura, foto,
  moldura e iluminura ficam como no original. (A do livro mora hoje na janela do Automático.)
- **D-168** (05/10/2026): "(a) Fica apagada (cinza) enquanto 'Só as letras' estiver marcada, e volta como estava ao
  desligar (recomendado)" → a caixinha das molduras fica cinza com "Só as letras" ligada.
- **D-126** (28/09/2026): "Gravura e letras intactas, e todo o papel totalmente branco, inclusive o papel dentro da
  gravura [...]. Só pintura de verdade, como a roupa do anjo e o céu colorido, mantém a cor."
- **D-127** (28/09/2026): "Iluminura sai intacta: cores, figuras, fundos e dourados como no original. [...]"
- **D-128** (28/09 e 30/09/2026): moldura dourada mantida sem mudar a cor · "a borda dourada deveria sair sem alteração".
- **D-585** (29/10/2026): "enfeite colorido guarda a cor em todos os filtros. só se eu escolher né? se eu colocar filtro
  preto e branco só nas letras." Registro: defeito contra a D-147 na capa do *Na escola de Jesus* (a pintura, 82% da
  página, foi tratada como enfeite e guardou a cor no Preto e branco sem "Só as letras").
- **Pedido de 29/10** (palavras dele): "eu usei no painel automatico, mas não foi agora na ultima sessão e não lembro
  que ssessão foi, mas cofira se isso está funcionando" (o "Só as letras" do Automático).
- **D-583** (29/10, "c"): a escolha "o filtro respeita ou não as gravuras achadas" no painel do Filtro — decidida, não
  construída; **não é desta tarefa** (não mexer).
- **CLAUDE.md §3** (algoritmo consagrado, nada de fórmula inventada), **§4.7** (teste de reversão), **§4.10** (caminho
  inteiro; cada foto diz por onde passou), **§5** (medir antes, uma mudança, medir depois; tudo em
  `relatorios/melhorias.md`), **§11 regras 1 a 7** (só o que ele mandou; na dúvida, perguntar).

## A causa

### 1) "Só as letras" no Automático: funciona (não achei defeito)

Conferido na cópia do projeto dele ("Na escola de Jesus", em `_tmp/dados`; nada foi escrito na pasta de dados de teste
nem no `%LOCALAPPDATA%`), pelo programa de verdade sem janela na tela, como o Kaique faria: janela do Automático →
"Jeito de limpar: Preto e branco" → marcar "Só as letras" → só "Limpar a folha", livro todo → Rodar. Medida inteira em
`medida-so-as-letras.txt` (página 9: gravura de Adão e Eva em cima, texto embaixo).

- **a) grava e vale:** o livro fica com "Só as letras" (no programa e no `projeto.json`); a página passa a Preto e
  branco herdando a escolha do livro. Na **tela "Uma página"**, no **"antes / depois"**, no **desenho do tamanho do
  PDF** e no **PDF gerado**: letra com 0,0% de pontos coloridos (preto e branco) e gravura com 90% de pontos coloridos
  (como no original). Prints `1-so-as-letras-herdado-uma-pagina.jpg` e `2-so-as-letras-herdado-antes-depois.jpg`.
  (O "cinza do meio" de 14% na letra do "antes / depois" e do PDF lido de volta é só a borda das letras amaciada ao
  reduzir a imagem para comparar; no desenho do tamanho do PDF é 0,0%.)
- **b) o painel mostra:** logo depois de rodar, o painel "Filtro da página" mostra a caixinha "Só as letras"
  **marcada** e, à direita, "Guardar a tinta forte" (o jeito de fábrica); continua assim ao sair e voltar à página.
- **c) desfazer:** Ctrl+Z volta o "Só as letras" do livro a desligado (e o filtro ao Original), também no
  `projeto.json`; Ctrl+Y põe de volta.
- D-168 na janela do Automático: a caixinha das molduras fica cinza com "Só as letras" e volta como estava.

**Por que o print dele (a-06) mostra "desligado":** no projeto gravado o livro está com "Só as letras" desligado e
nenhuma página tem a escolha só nela; o único Automático que ficou no histórico (`acoes.jsonl`) rodou sem trocar o
filtro, e a página 1 foi posta em Preto e branco à mão, no painel. Então o painel mostrava certo: naquele momento o
"Só as letras" não estava ligado no livro. Pelo que ficou gravado não dá para saber o que ele marcou na sessão em que
usou (ele desfez e refez depois).

### 2) D-585: por que a pintura da capa guardou a cor

No Preto e branco, cada gravura marcada passa por duas perguntas, nesta ordem (`core/filtros._tipos_das_zonas`):
1. **"É foto ou pintura?"** — é, se for grossa e tiver **pouco traço** (menos de 5% da caixa da gravura). Sim → tons
   de cinza (D-147).
2. Se não: **"É enfeite colorido?"** (moldura, iluminura: muita cor larga). Sim → fica com a cor (D-144).

O "traço" que o programa mede é, na prática, **a escrita que cai dentro da caixa da gravura**. Na capa, o título
"Jesus" e o "190 QUADROS ARTÍSTICOS" estão em cima da pintura: dá **12,7% de traço**, passa dos 5%, a pintura não é
reconhecida como pintura e, como é colorida, cai em "enfeite" e fica com a cor. Medido no livro (páginas ímpares, pelo
caminho inteiro): **95 pinturas saem certas, em cinza; 4 saem coloridas por esse motivo** — a capa e as páginas 19
(faixa com inscrição em latim), 45 (o Papa, com legenda e texto do lado) e 173 (casamento, com o texto dentro do
quadro), de 12% a 15% de traço. A iluminura da Horas 11 só fica com a cor pelo mesmo motivo: o texto dentro dela dá
20% de traço (as outras iluminuras das Horas, 29% a 89%).

**Por que não consertei sozinho:** a única medida que o programa tem para separar "pintura" de "iluminura" é essa, e
ela não é confiável. No PDF (300 dpi) daria para pôr um limite entre 15% (pinturas) e 20% (Horas 11), mas **na prévia
da tela (110 dpi) a ordem se inverte**: Horas 11 mede 5,4% e o Papa da página 45 mede 28,5%. Qualquer limite deixaria
a tela diferente do PDF (contra D-066/D-473) ou mandaria a iluminura das Horas para cinza (contra D-144). As outras
tentativas (ignorar o título, contar a cor, achar a retícula de impressão) também falharam — ver
`relatorios/melhorias.md`, entrada de 29/10/2026, e `medida-pintura-x-enfeite.txt`. Pela regra ("se não for seguro,
pergunte"), virou pergunta.

## O que mudou

**Nenhuma linha do programa** (`git diff 226536c --stat` só mostra `tests/` e `relatorios/`). Entraram:
- `tests/test_decisoes_so_as_letras.py` — 5 provas do pedido 1 (D-148 a, b, c e D-168), livro sintético;
- `relatorios/automatico-pintura/`: scripts das medidas (`conferir_so_as_letras.py`, `diagnostico_capa.py`,
  `medir_gabarito.py`, `opcoes_d585.py`), medidas (`medida-so-as-letras.txt`, `medida-pintura-x-enfeite.txt`,
  `prova-no-226536c.txt`), prints 1 e 2 e as imagens da pergunta `d585-*.jpg`;
- `relatorios/melhorias.md`: a entrada de 29/10 com as tentativas da D-585.

## Como cumpri cada uma

| Decisão | Como |
|---|---|
| D-148 | Conferida no livro dele e provada: `test_d148_*` (3 provas: grava/tela/PDF, painel, desfazer). Prints 1 e 2. |
| D-168 | `test_d168_na_janela_do_automatico_a_caixinha_das_molduras_apaga_e_volta` (com a caixinha marcada e desmarcada antes). |
| D-147 | Causa achada e medida (4 pinturas do *Na escola de Jesus* fora da regra); não consertado: vai como pergunta. |
| D-144, D-127, D-128 | Intocadas (nenhuma linha mudou); a pergunta mostra o que mudaria nas Horas 11, 13, 26 e 47. |
| D-126 | Intocada. Ressalva: na capa, partes do céu claro foram marcadas como **papel** pelo detector e vão a branco. |
| D-585 | Causa em "A causa", 2); pergunta abaixo, com imagens. |
| D-583 | Não tocada (não é desta tarefa). |
| §4.7 | Sem conserto não há reversão; as provas novas rodadas no 226536c passam (`prova-no-226536c.txt`). |
| §4.10 | Toda imagem passou pelo caminho inteiro (livro novo de uma página: endireitar, cortar, "Limpar a folha", "Gravuras e fotos", Preto e branco sem "Só as letras"), no tamanho do PDF; o título de cada quadro diz isso. |
| §5 | Medido nas 32 páginas-gabarito + capa + páginas ímpares do *Escola* e das *Horas*; nenhuma mudança entrou; tentativas em `melhorias.md`. |
| §11 regra 7 | Nenhum botão, texto ou comportamento novo. |

## Testes (um arquivo por vez, offscreen, `--basetemp` em `_tmp`)

- `tests/test_decisoes_so_as_letras.py`: **5 passed in 19.44s** (no ramo) e **5 passed in 24.60s** no `226536c`.
- Não rodei outros arquivos: nenhum arquivo do programa mudou.
- Velocidade: não rodei `teste_velocidade.py` — nada em `core/` mudou.

## Ressalvas

- O print dele foi feito numa sessão que não ficou no histórico; conferi o caminho, não aquela sessão.
- As provas do pedido 1 usam um livro sintético com a marcação posta direto (sem o detector); o caso real foi medido
  no livro dele, fora do pytest (`medida-so-as-letras.txt`).
- **Achado à parte (não consertado, regra 7):** na prévia da tela (110 dpi) a iluminura da Horas 11 mede 5,4% de
  traço, a um fio dos 5% em que viraria "pintura" e sairia cinza na tela (no PDF mede 20%). E a pintura da página 3 do
  *Escola* mede 4,96% no PDF, a um fio de virar "enfeite". A régua de hoje está no limite dos dois lados.
- Na capa, o detector marcou partes do céu claro como **papel** (14% da página), que vão a branco em todos os filtros
  (a mancha branca atrás de Jesus no "HOJE"). Isso é da marcação, não do filtro; não mexi.
- A "opção B" é só protótipo de imagem: nele, o texto dentro da iluminura da Horas 11 sai cinza-escuro em vez de
  preto; se ele escolher B, precisa de um ajuste a mais (a letra dentro do enfeite continuar preta, como hoje).
- Não medi os outros livros do acervo (Graduale, ljs47, Antiphon...): parei a medida para não pesar o PC, já que nada
  mudou no programa.

## Perguntas para o Samuel

1. **D-585 — a pintura colorida que o programa confunde com enfeite.** Hoje, no Preto e branco sem "Só as letras", a
   pintura sai em cinza (D-147) e a moldura/iluminura fica com a cor (D-144). O programa decide qual é qual pela
   quantidade de escrita dentro da imagem, e erra quando a pintura tem título ou legenda em cima: no *Na escola de
   Jesus*, a capa e as páginas 19, 45 e 173 saem coloridas (as outras 95 pinturas saem certas, em cinza). Não achei
   jeito seguro de o programa separar sozinho: na tela e no PDF a medida dá resultados opostos. Imagens:
   `d585-escola-capa-do-samuel.jpg`, `d585-escola-p19.jpg`, `d585-escola-p45.jpg`, `d585-escola-p173.jpg` e, das
   Horas, `d585-horas-p011.jpg`, `-p013`, `-p026`, `-p047` (cada uma: Original · Preto e branco hoje · opção B).
   - **A — Deixar como está** e, quando a pintura sair colorida, trocar o filtro da página ou usar "Só neste
     pedaço". (Hoje o "Só neste pedaço" não tem "tons de cinza"; sairia em preto e branco de traço.)
   - **B — No Preto e branco sem "Só as letras", nada fica colorido:** pintura, foto, moldura e iluminura saem em tons
     de cinza; com "Só as letras", tudo fica com a cor. Funciona sempre (o programa não precisa adivinhar), mas
     **muda a D-144** de 30/09 ("Mantém a cor original"): as molduras douradas e as iluminuras das Horas passam a sair
     em cinza (terceira coluna das imagens das Horas).
   - **C — Você escolhe, na página:** no painel "Filtro da página", uma escolha para a imagem colorida daquela página
     ("em tons de cinza" ou "com a cor"). Precisa de um controle novo na tela (pergunta de layout).
   - **D — Pesquisar um detector novo** de "pintura × iluminura" (Lista de espera); até lá, fica como A.
   Opinião do agente: **B** é a única que nunca erra e é o que as palavras de 29/10 parecem dizer; mas troca uma
   decisão de 30/09, por isso só com o "sim" dele.
2. **Para confirmar a D-585:** "enfeite colorido guarda a cor em todos os filtros. só se eu escolher né? se eu colocar
   filtro preto e branco só nas letras." — vale **só para a pintura** (como a gerente anotou: moldura e iluminura
   continuam com a cor de fábrica) ou **também para a moldura e a iluminura** (que é a opção B)?
