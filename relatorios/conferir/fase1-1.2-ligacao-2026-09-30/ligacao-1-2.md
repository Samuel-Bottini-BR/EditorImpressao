# Item 1.2, segunda etapa: o detector de gravura do ScanTailor ligado ao programa

Rodada de 30/09/2026 (madrugada), pelo implementador. **Não é o parecer do verificador**: é o material para ele e para o Samuel. Teste de **olho** (as imagens) e de **máquina** (testes automáticos e tempos).

**Aviso da Fase 1:** moldura e iluminura continuam defeito conhecido até a Fase 1 ficar pronta (itens 1.4 e 1.5).

## O que mudou, em uma frase

O programa passou a perguntar ao código original do ScanTailor **onde está a gravura** de cada página (na prévia e no PDF, depois de cortar e endireitar). A letra e o papel continuam sendo achados como antes, agora em volta da gravura nova. De fábrica: ScanTailor na forma **"livre"**.

## Onde olhar

| Pasta | O que é |
|---|---|
| `mascaras\` | Uma imagem por página: original · **antes** (azul) · **ScanTailor livre** (vermelho) · **ScanTailor retangular** (vermelho). Verde claro = letra. A porcentagem é quanto da página virou gravura. |
| `1-antes-magico-pro\` | Mágico pro com o detector antigo. |
| `2-depois-magico-pro\` | Mágico pro com o ScanTailor livre (coluna "Rodada anterior" = o antes). |
| `3-antes-preto-e-branco\` | Preto e branco com o detector antigo. |
| `4-depois-preto-e-branco\` | Preto e branco com o ScanTailor livre (coluna "Rodada anterior" = o antes). |
| `5-retangular-magico-pro\` | Mágico pro com o ScanTailor **retangular** (coluna "Rodada anterior" = o livre). |
| `scripts\` | Os scripts e os números dos tempos, para refazer. |

Páginas (21): as 16 da Fase 1 (inclui as obrigatórias Palatino 5, Escola 35, Horas 11, 13, 26, 27 e Opus Majus 20), mais Palatino 67, Rhetorica 18, Graduale 222 e Marial 146 e 153 (copiadas do acervo; não estão no gabarito).

## O que o implementador viu (opinião, com ressalvas)

**Melhorou:**

- **Horas 11 (iluminura):** no Mágico pro, antes a pintura saía quase toda apagada; agora sai inteira, com cores. O detector antigo não marcava nada dela (0%); o ScanTailor marca 81% da página.
- **Horas 26 e 27 (moldura dourada):** a moldura agora é gravura e sai dourada e cheia (antes 1% da página; agora 23% e 6%).
- **Palatino 5:** a página inteira era "gravura" (100%); agora só o retrato (50%). O título volta a ser letra.
- **Título corrido tomado por gravura (Marial 146 e 153):** sumiu (0%); o "de Maria." não sai mais numa caixa cinza.
- **Opus Majus 256 (tabela):** antes 89% "gravura"; agora 0%, tratada como texto.
- **Palatino 9 e 67 (a família "sensível ao enquadramento"):** as caixas do detector antigo sumiram (Palatino 9: 10% da página era "gravura", agora 0%; Palatino 67: a caixa em volta do "M" vira a forma do próprio "M"). A Rhetorica 18 continua sem gravura (0% nos dois). Conferir a tira creme entre os fios da moldura do Palatino 9 e a orla da Rhetorica 18 nas pastas 2 e 4.

**Piorou ou continua errado:**

- **Opus Majus 20 na forma livre: PIOROU.** A estátua branca fica fora da gravura (como o relatório do núcleo já dizia) e sai lavada; o vão escuro da porta sai com pontinhos. **Na forma retangular sai perfeita** (pasta 5). Por isso a forma tem de ser escolhida **por livro**.
- **Graduale 222: PIOROU.** O ScanTailor marca pedaços da pauta como gravura (14% da página); no Mágico pro aparecem blocos cinza-claros com a mancha do verso e notas mais escuras nesses blocos; no Preto e branco, esses blocos saem em tons de cinza em vez de preto e branco.
- **Horas 13:** a moldura é achada, mas continua o triângulo sobre "pag. 54" (já conhecido).
- **Horas 26 (forma livre):** o ScanTailor enche o miolo da moldura; o programa devolve o bloco do calendário à letra (onde o modelo de layout vê texto, o texto ganha), mas o papel liso dentro da moldura, fora do bloco, fica marcado como gravura. Ver `mascaras\horas_p026.jpg`.
- **Opus Majus 165:** as figuras 7 e 8 (desenho de traço) não são mais gravura: saem como traço (preto e branco). Parece melhor (o papel fica branco), mas é uma mudança a conferir.

**Forma de fábrica proposta: "livre".** A "retangular" marca 100% do Graduale 222, 49% da Horas 26 (com o texto do calendário), 34% da Horas 13 e 31% do Marial 153 (texto), e deixa o papel creme nessas páginas. Ela só serve para livro de **foto** (Opus Majus), escolhida no livro.

## Tempo (regra 6): medido com a máquina dividida com outro agente

Medida isolada, antes e depois alternados página a página, caches esvaziados entre um e outro. **A gerente precisa rodar o teste oficial com a máquina parada.**

**Marial (o livro do teste de velocidade):**

- **Primeira prévia de uma página (trocar de página): ficou uns 0,5 s mais lenta** (20 páginas espalhadas, uma por vez, 110 DPI): mediana 2,82 s → 3,33 s (+18%). A mais lenta: 4,5 s depois; antes, 9,2 s (a primeira página, aquecendo).
- **Processar 10 páginas: igual.** Mágico pro 126,5 s → 120,0 s; Preto e branco 56,7 s → 58,0 s (+2%, dentro da variação entre rodadas).

**As 21 páginas desta rodada (somadas):** prévia 69,1 s → 74,8 s (+8%); Mágico pro 285 s → 300 s (+5%); Preto e branco 201 s → 220 s (+10%). Onde ficou mais lento: páginas que agora têm gravura grande (Horas 11: Mágico pro 24 → 34 s, Preto e branco 17 → 30 s; Horas 26 e 27; Opus 20 no Preto e branco, 8,6 → 13,2 s) e o Graduale 222 (Mágico pro 19 → 30 s; Preto e branco 6 → 23 s), por causa da pauta marcada como gravura. Onde ficou mais rápido: Palatino 5, 7, 9, 10, Rhetorica 18, Opus 256, Marial 146 e 153 no Preto e branco.

O que já foi feito para devolver tempo (sem isso, a prévia do Marial ficava 0,6 a 1,3 s mais lenta): o ScanTailor roda ao mesmo tempo que o resto do detector; e as páginas que o PDF diz ter 72 DPI (Marial, Horas, Graduale), que viram folhas gigantes, vão ao ScanTailor num tamanho de trabalho limitado.

## Ressalvas

- A aba Marcar ("detectar automaticamente" / "Procurar de novo") **continua com o detector antigo**: ela não sabe o DPI da prévia. Falta uma linha em `ui/tela_conferir.py` (fora da alçada do implementador).
- O item 1.1 ("Tirar o fundo") continua usando o detector antigo para as zonas que ficam intactas.
- Projetos já abertos antes guardam a marcação do detector antigo nas páginas já vistas; só páginas novas (ou sem marcação) usam o ScanTailor.
- Não há ainda o botão de ligar/desligar nem o campo "forma por livro" (regra 8): hoje é um valor fixo no código.
- Tempos medidos com outro agente usando a máquina ao mesmo tempo: servem para comparar antes e depois, não como número oficial.
