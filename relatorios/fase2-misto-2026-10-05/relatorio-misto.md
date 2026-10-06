# Fase 2, modo Misto: o núcleo, por linha de comando (05/10/2026)

**Implementador, ramo `fase2-misto`.** Não é "aprovado" nem "pronto para conferir": é o relatório do implementador, para a gerente e o verificador.

## Em uma frase

O modo Misto já monta a página por linha de comando: **as letras saem em preto e branco, e a gravura, a foto, a moldura e a iluminura ficam como no original, com o papel branco**. Ele ainda não está na tela nem no projeto salvo (isso é pergunta ao Samuel), e **o programa de hoje não mudou em nada**: 102 de 102 imagens idênticas.

## O que foi feito

- `core/misto.py`, função `aplicar_misto`: a página inteira passa pelo Preto e branco de sempre (com todas as regras aprovadas); onde o detector de gravura do 1.2 (ou a zona marcada à mão) diz que é imagem, volta o original:
  - **foto e pintura**: os pontos do original, sem mudar nada;
  - **moldura dourada e iluminura**: a cor original, só o papel a branco, e a letra solta dentro dela preta (exatamente como o Preto e branco de hoje já faz);
  - **gravura de traço** (retrato, xilogravura): o traço com o tom do original, **o papel de dentro dela a branco** (a conta do papel da própria gravura, feita para o retrato do Palatino 5).
- As **zonas feitas à mão** mandam: "letra" marcada à mão ganha da gravura achada sozinha; gravura tirada à mão vira preto e branco; gravura marcada à mão fica como está; "só neste pedaço" com outro filtro vale (no Preto e branco de hoje ele é ignorado: ver o achado); papel marcado vai a branco.
- `montar_misto.py`: o Misto de qualquer PDF por linha de comando, pelo mesmo caminho do programa (analisar, preparar a página, achar gravura e letra, Misto). Opções `--papel-creme` e `--foto-cinza` (as variantes das perguntas).
- 26 testes novos em `tests/test_misto.py` (os 20 do Misto mais 6 das opções experimentais da parte C).
- Plano: `docs/plano/fase2-misto-plano.md` (parte A).

## O caminho de hoje não mudou

- Nenhum arquivo do programa de hoje foi tocado (`core/filtros.py`, `core/pipeline.py`, `core/selecao.py`, `core/detectar_regioes.py`: sem diferença desde `aab746f`), e nada do programa importa o `core/misto.py`.
- **Imagens idênticas:** as 32 páginas do gabarito (34 páginas de saída) desenhadas pelo `renderizar_pagina` do programa, a 300 DPI, nos filtros Preto e branco, Melhorar e Mágico pro, antes e depois: **102 de 102 com a mesma soma sha256** (`dados/caminho-atual-antes.json` e `-depois.json`, script `scripts/caminho_atual.py`).
- **Tempo:** a rodada "depois" saiu 29% a 37% mais lenta nos três filtros. **Não é o código** (o código dessas contas é o mesmo arquivo, byte a byte): a máquina estava mais ocupada (os meus próprios testes e outros agentes rodando ao mesmo tempo; a máquina tem 15 GB e chegou a ter 3 livres). É a ressalva de sempre das medidas com agentes rodando.

## O que o Misto fez nas 32 páginas (`dados/rodada-misto.json`)

- **27 páginas saem idênticas ao Preto e branco de hoje.** É o esperado: nelas o detector não marcou gravura (texto, Graduale, Palatino 9, Opus 165, Opus 256...) ou só marcou moldura e iluminura, que o Preto e branco de hoje já deixa em cor (Horas 11, 13, 26, 27, 47).
- **5 páginas mudam**, todas onde há foto, pintura ou gravura de traço: Escola 7 e 35, Opus Majus 20, Palatino 5 e Marial 7.
- Tempo do Misto contra o Preto e branco de hoje na mesma página, mesma imagem e mesma marcação: igual dentro da variação (de -0,7 a +1,0 s; Horas 47 +1,0 s e Horas 11 +0,7 s, mas a imagem dessas duas é idêntica à do Preto e branco, então é variação da máquina).

## Minha opinião, página por página (abri as imagens)

Imagens: `paineis/<página>.jpg` (Original | Preto e branco hoje | Misto) e `-detalhe.jpg`; `variantes/` (Misto | papel da gravura creme | foto em cinza); `mascaras/` (onde o Misto deixa o original, em laranja).

- **Escola 7 e Escola 35:** é o pedido do Samuel. Texto preto e nítido, papel branco, e a pintura colorida (o Paraíso, Adão e Eva com o anjo) como no original, em vez do cinza do Preto e branco.
- **Opus Majus 20:** a estátua sai como no original (tom creme da foto), o rosto e o vão da porta inteiros (a conta do "fecho da foto" da conferência 5 vale no Misto). A legenda sai preta.
- **Palatino 5:** o retrato sai com o traço marrom do original e o fundo **branco**, sem a mancha amarela; o Preto e branco de hoje tinha virado o retrato em desenho de 1 bit. **Na primeira versão** o fundo do retrato ficava amarelo e a mancha de fora do oval aparecia (usei a conta da moldura, que mede o papel da página); troquei pela conta do papel da própria gravura (teste em `teste-papel/`). Ressalva: o traço fica marrom, não preto; se o Samuel quiser traço preto no retrato, isso é outra pergunta.
- **Marial 7:** **piora visível**: o detector marca a mancha do canto de cima à esquerda como foto, e o Misto a deixa marrom, como no original (o Preto e branco de hoje a deixava cinza). É o risco 1 do plano: o Misto mostra direto cada erro do detector. Remédio: tirar a zona à mão na aba Marcar (já funciona no núcleo).
- **Horas 11, 13, 26, 47:** idênticas ao Preto e branco de hoje (iluminura e moldura em cor, letras pretas). Na Horas 26 continua a faixa preta da beirada direita do scan (já existia).
- **Palatino 9:** idêntica ao Preto e branco: o detector não marca a capitular Q nem as molduras, então elas saem em preto e branco (como no teste do ScanTailor de 24/09).
- **Graduale 221 e 222, Opus 165:** idênticas ao Preto e branco: sem gravura marcada; notas, pautas e diagramas em preto e branco.

Variantes (perguntas P2 e P3 do plano): com o **papel creme**, o retrato do Palatino 5 fica amarelo com a mancha em volta e o miolo da Horas 47 fica com blocos cinza-claros; com a **foto em cinza**, a estátua do Opus 20 sai em cinza como no Preto e branco. A minha recomendação continua: papel branco e foto como no original.

## Ressalvas

- O Misto **não está ligado** ao programa: nem prévia, nem PDF, nem tela. Não foi testado na janela.
- Rodei com a marcação que o programa acha sozinho; **as zonas à mão foram testadas só em páginas sintéticas** (testes), não em página do acervo.
- A letra do Misto é a do Preto e branco de hoje: o defeito A1 da Horas 47 (pontos apagados no meio das letras) continua.
- Página com gravura sai em cor: PDF pesado (já na Lista de bugs; o remédio é o 1.6/2.10).
- A gravura de traço sai com o tom do original (marrom), não em preto.
- Tempos medidos com a máquina dividida com outros agentes.
- Numa rodada de medida, a detecção de gravura da Horas 13 **falhou por falta de memória** (a máquina estava com 3 GB livres) e a página saiu **sem gravura, sem aviso** (o `garantir_selecao` engole o erro e devolve a marcação vazia). Refiz a página e saiu certa. No programa de verdade isso faria a moldura sair em preto e branco naquela página, calado.

## Bugs para a Lista de bugs

- 05/10: **No filtro Preto e branco, o "só neste pedaço" da aba Marcar é ignorado** (`core/filtros.aplicar_filtro_com_selecao` sai pelo ramo do Preto e branco antes de chamar `_filtro_so_no_pedaco`). Conferido numa página sintética: zona "só neste pedaço = Original" sai preta (letra) ou cinza (gravura); no Mágico pro sai em cor. Contradiz a Lista de espera de 01/10 ("Parte disso já existe na aba Marcar").
- 05/10: **Falta de memória na detecção de gravura vira "página sem gravura", sem aviso** (`core/pipeline.garantir_selecao` registra no log e devolve a marcação vazia; a moldura sai no tratamento de letra). Visto na Horas 13 com a máquina sem memória livre.
- 05/10 (só para agentes): numa worktree em `.claude/worktrees/`, o `core/ocr_kraken.lugares_do_motor` não acha o motor (procura em `.claude/worktrees/EditorImpressao-arquivos/...`). Não afeta o programa instalado nem a pasta principal.

## Ideias para a Lista de espera

- Gravura de traço no Misto com o traço em preto (em vez do marrom do original), como opção.
- Aviso na aba Marcar quando o detector marca como foto uma área com cor de mancha (o caso do Marial 7).

## Parte C (acréscimo da gerente): as opções A, B e C lado a lado

O que foi feito: em `core/misto.py`, a opção experimental `fora_do_texto` (de fábrica `"tudo"` = B, o Misto acima; nada muda para quem não pede): **A** `"rede"` (rede de segurança da pesquisa, seção 4: dentro das linhas, o preto e branco de sempre; fora delas e fora das gravuras, fica cada pedaço de tinta com um ponto tão escuro quanto a mediana da tinta de dentro das linhas e área de pelo menos (altura da linha / 6)²; o resto vai a branco), **C** `"apagar"` (só as linhas). Linhas = união do docTR `fast_base` e do Kraken, alargadas 15% da altura da linha (`mascara_das_linhas`). Sem linha nenhuma, A e C viram B. Detector de gravura do 1.2 ligado. 6 testes novos.

Rodada: 7 páginas do gabarito, a 300 DPI (`relatorios/conferencia-8-2026-10-05/`, script `scripts/rodada_abc.py`). Formulário: **`relatorios/conferir-aqui-8.html`**.

| Página | Tinta forte fora das linhas (guardada pelo A) | docTR | Kraken | A | B | C |
|---|---|---|---|---|---|---|
| Graduale 222 | 75,7% | 2,5 s | 80,9 s | 1,37 s | 1,12 s | 1,11 s |
| Palatino 9 | 46,5% | 1,0 s | 13,8 s | 0,18 s | 0,15 s | 0,16 s |
| Opus Majus 165 | 5,8% | 1,0 s | 15,9 s | 0,26 s | 0,20 s | 0,23 s |
| Boécio 22 | 1,7% (de 3,1% fora) | 1,0 s | 18,2 s | 0,16 s | 0,14 s | 0,15 s |
| Marial 7 | 5,1% (de 6,8% fora) | 1,2 s | 25,7 s | 1,65 s | 1,65 s | 1,67 s |
| Horas 11 | 0,4% | 1,3 s | 11,2 s | 7,06 s | 6,44 s | 6,53 s |
| Horas 13 | 4,0% | 1,2 s | 14,4 s | 4,36 s | 4,04 s | 4,07 s |

(Tempos com a máquina dividida com outros agentes; o Kraken mediu ~10 s por página no 1.3.)

Minha opinião (abri todas as imagens):

- **Graduale 222:** A e B guardam todas as notas e pautas; A tira o pontilhado fino do alto que o B deixa. **C apaga a música inteira: inaceitável aqui.** O "Cvij" não aparece em nenhuma (já é cortado pelo corte das bordas, antes do filtro).
- **Palatino 9:** o detector não marca a capitular nem a moldura. A guarda as duas, mas **perde hachuras claras do fundo do Q** (como a pesquisa previu); B guarda mais. C apaga capitular e moldura e deixa pedaços soltos da moldura. Aqui B ≥ A > C.
- **Opus 165:** A ≈ B (no A some o pontinho do "f" da figura 7); C apaga as figuras.
- **Boécio 22:** A e C tiram mais pontinhos do verso que o B; os colados ao fim das linhas ficam nas três. **C apaga a primeira capitular "Q"**; A a guarda. Aqui A é o melhor.
- **Marial 7:** A tira as faixas pretas da beirada do livro e riscos da margem que o B deixa; C parecido com o A. A mancha do canto (tomada por foto) aparece nas três.
- **Horas 11 e 13:** iluminura e moldura iguais nas três (protegidas pelo detector). Só a faixa preta da beirada esquerda do scan fica no A e no B e sai no C.
- **Em resumo:** A nunca perdeu nada importante e limpou mais que o B em 4 das 7 páginas; o custo dele é perder hachura clara de capitular não detectada (Palatino 9). C perde música, capitular e desenho: não serve de fábrica. O custo grande de A e C é o leitor de texto (o Kraken), não a opção.

Ressalvas da parte C: um limiar só (a mediana), não calibrado; as páginas são as do gabarito (o Boécio 22 tem escaneamento ruim); a "tinta forte fora das linhas" do aviso não foi calibrada (o 10% do formulário é exemplo); os rótulos das colunas dentro das imagens ficam pequenos no formulário (a ordem é sempre Original | A | B | C, dita no topo).
