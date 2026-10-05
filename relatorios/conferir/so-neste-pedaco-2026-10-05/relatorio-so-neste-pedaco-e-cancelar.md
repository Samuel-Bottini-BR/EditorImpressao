# Consertos de 05/10: "só neste pedaço" no Preto e branco e o cancelar que apagava o PDF antigo

Ramo `consertos-cancelar-pedaco-2026-10-05` (criado do `fase-1` em `044a7c1`). Dois consertos autorizados pelo Samuel na conferência 11. Teste de **máquina** nos dois; o "só neste pedaço" também precisa do teste de **olho** do Samuel (as imagens abaixo). Nada foi juntado ao `fase-1`.

## 1. Cancelar depois de "substituir o antigo" não apaga mais o PDF antigo (commit `880bf70`)

**O que estava errado:** sem "Montar cadernos", o programa gravava direto no arquivo final. Com "substituir o antigo" e depois "cancelar", o PDF antigo era sobrescrito pelas páginas feitas até ali e depois apagado. Sumia, sem aviso.

**O que mudou:** o PDF novo é gravado num arquivo à parte, na mesma pasta (`~nome.pdf.parcial`, que não parece PDF), e só troca de lugar com o antigo quando termina. Cancelou ou deu erro: some só o arquivo à parte, e o antigo fica igual, byte a byte. Vale também com "Montar cadernos" e no caminho rápido "só cadernos". Se o programa cair no meio, a sobra é apagada na próxima vez que o mesmo PDF for gerado.

**PDF antigo aberto em outro programa** (no Windows a troca falha): o programa tenta de novo por cerca de 1 segundo. Se continuar preso, o PDF novo vai para `nome (2).pdf` e aparece o aviso: *"Não consegui substituir o arquivo antigo "X.pdf": ele parece estar aberto em outro programa (o leitor de PDF, por exemplo). O arquivo antigo ficou como estava, e o PDF novo foi gravado ao lado dele, na mesma pasta, com o nome "X (2).pdf"."* Nada mudou na tela: o aviso usa a caixa que já existia.

**Testes:** 21 novos (`tests/test_substituir_e_cancelar.py`): cancelar em vários pontos, terminar, erro numa página, disco cheio ao gravar, com cadernos, só cadernos, sobra de queda, arquivo parecido de outro livro (não é apagado), e o PDF antigo aberto de verdade no Windows.

## 2. "Só neste pedaço" passa a valer no Preto e branco (commit `60d8c58`)

**O que estava errado:** numa página em Preto e branco, a pintura marcada com "só neste pedaço: Original" saía cinza. O programa ignorava o pedaço sem avisar.

**O que mudou:** a área marcada obedece **inteira** ao filtro escolhido para ela (Original, Melhorar ou Mágico pro), inclusive as partes claras, como o céu e as nuvens. Isso inclui o papel que a pessoa pegar junto ao desenhar o retângulo: no Original, esse papel sai creme, e a borda é exatamente a que foi desenhada. Só mudam as páginas que têm pedaço marcado.

**Prova de que as outras páginas não mudaram:** as 32 páginas do gabarito, processadas pelo mesmo caminho do botão "Confirmar e processar", em Preto e branco, Melhorar e Mágico pro: **96 de 96 imagens idênticas** ao `044a7c1`, ponto por ponto (`comparacao-32-paginas.json`). Essa rodada também passa pelo conserto do cancelar.

### As imagens (abrir para conferir)

- `escola7-pagina.jpg`: a página inteira. Original (em laranja, o pedaço marcado), Preto e branco antes, Preto e branco depois.
- `escola7-pedaco.jpg`: a pintura de perto.
- `escola7-detalhe1.jpg`: o céu e as nuvens. Antes saíam cinza; agora saem como no original, sem manchas.
- `escola7-detalhe2.jpg`: o leão e o pé da pintura.
- `escola7-detalhe3.jpg`: a beirada do pedaço. Repare na **faixa creme fina** em cima da pintura: é o papel que ficou dentro do retângulo marcado.
- `opus20-pagina.jpg`, `opus20-pedaco.jpg`, `opus20-detalhe1.jpg` (rosto) e `opus20-detalhe2.jpg` (parede e pé da foto): a foto da Opus Majus 20, com um retângulo em volta dela.
- `descartado/`: a primeira tentativa, que deixava a margem do retângulo seguir a página. Na Escola 7 ficava bom, mas na Opus 20 a parede clara da foto virava **manchas brancas recortadas** (`tentativa-margem-ligada-opus20-pagina.jpg`). Por isso foi descartada.

### Números (`medidas.json`)

| | Escola 7 | Opus 20 |
|---|---|---|
| parte do pedaço igual ao original, antes | 0% | 0,2% |
| parte do pedaço igual ao original, depois | 99,9% | 99,9% |
| pontos diferentes fora do pedaço | 0 | 0 |
| processar a página, antes (s) | 1,8 e 1,4 | 2,2 e 1,7 |
| processar a página, depois (s) | 2,1 e 2,1 | 2,1 e 2,1 |

## Opinião do implementador

O conserto faz o que foi pedido. Na Escola 7, a pintura sai inteira como no original, com o céu, as nuvens e o leão limpos, sem os cinzas e as manchas da simulação. A borda é reta, no lugar desenhado. Na Opus 20 a foto sai como veio, e o rosto da estátua volta a aparecer, quando antes ficava estourado de branco. O que pode incomodar é a faixa creme do papel que fica dentro do retângulo. Ela é fina quando o Kaique desenha justo em volta da foto, e fica maior se ele deixar folga. Isso é consequência direta de "obedece inteira". PRONTO PARA CONFERIR, a decidir pelo Samuel.

## Ressalvas

- **Velocidade:** havia outros agentes rodando no PC, então os tempos oscilam. Nas 32 páginas sem pedaço, o caminho do código é o mesmo, e as diferenças medidas estão dentro do ruído: Preto e branco 144,8 → 134,3 s, Melhorar 215,9 → 224,6 s, Mágico pro 244,2 → 249,6 s. Numa página **com** pedaço em Original, o processar ficou cerca de 0,3 a 0,6 s mais lento na Escola 7 (pouco nítido na Opus 20), porque a página passa a ser gravada em cor. O teste oficial de velocidade (`teste_velocidade.py`) não foi rodado.
- A regra antiga "o papel de dentro da região segue a página" (07/08) **deixa de valer no Preto e branco**, que agora obedece ao pedaço inteiro. No Melhorar e no Mágico pro ela continua como sempre. O teste que a cobria usava o Preto e branco e passava sem testar nada, porque o pedaço era ignorado. Ele agora roda no Melhorar e no Mágico pro.
- Numa página em **Original**, o "só neste pedaço" continua ignorado. Não foi pedido aqui e vai para a Lista de bugs.
- As imagens foram geradas com o filtro do `044a7c1` posto no lugar do de hoje, dentro do programa de hoje, e não com uma cópia inteira do código antigo. A prova das 32 páginas, essa sim, usou uma cópia inteira do `044a7c1`.
- Cancelar: o arquivo à parte de uma queda só é apagado quando o **mesmo** PDF é gerado de novo. Se o Kaique nunca mais gerar aquele livro, a sobra `~nome.pdf.parcial` fica na pasta.
- Cancelar com cadernos: o arquivo temporário em ordem normal continua indo para a pasta temporária do Windows (disco C). Isso não mudou.
