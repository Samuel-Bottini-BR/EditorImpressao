# Item 1.2, segunda etapa: parecer do verificador

Conferência de 30/09/2026 do detector de gravura do ScanTailor ligado ao programa (commits `71e14be`, `fe3cb9b`, `885353a`). Feita numa cópia limpa do commit `25aed39` (`.claude\worktrees\verificador`).

> **Aviso da Fase 1:** moldura dourada e iluminura continuam **defeito conhecido** até a Fase 1 ficar pronta (itens 1.2, 1.4 e 1.5). Abaixo eu digo se o 1.2 aproxima ou afasta do resultado combinado.

## Veredito

**NÃO ESTÁ PRONTO para aprovar como está, mas vale o Samuel olhar agora.** A direção é boa: a iluminura da Horas 11 volta inteira, a moldura dourada dos calendários sai cheia e as caixas cinza em volta de títulos somem. Mas, na forma de fábrica ("livre"), **uma página obrigatória piora** (a foto do Opus Majus 20), o **Graduale 222 piora**, a **moldura da Horas 13 fica preta no Preto e branco**, **ainda não há botão de ligar e desligar** (regra 8) e a **primeira prévia fica mais lenta** (regra 6 em risco). E quando a DLL falta, o aviso **não chega ao `erros.log`** do programa.

## Máquina ou olho

| O quê | Como | Resultado |
|---|---|---|
| Testes automáticos (`pytest tests -q`) | máquina | **1194 passaram, 1 pulado, 0 falharam** (inclui os 29 novos do 1.2, os 24 do núcleo e os 33 do Kraken). O pulado só roda com `OCR_22=1`. Na cópia faltavam `gabarito\paginas`, `saida_teste\ocr-*` e o motor do Kraken; liguei por junção, só leitura (sem isso: 1109 passaram e 86 pularam). |
| As imagens da rodada são do código de hoje? | máquina | **Sim.** Refiz 6 páginas (Horas 11 e 26, Opus 20, Graduale 222, Palatino 5, Marial 153) pelo `conferencia.py`, na cópia: **iguais ponto por ponto** às da pasta 2. |
| A prévia marca a mesma gravura que o PDF? | máquina | **Sim, quase igual** (110 × 300 DPI): Horas 26 23,3% × 23,3%; Opus 20 72,1% × 71,5%; Palatino 5 50,7% × 50,0%; Graduale 222 15,0% × 14,1%; Marial 153 0% × 0%. |
| DLL ausente | máquina | **Nada cai**: o programa volta sozinho ao detector antigo, e o resultado é **idêntico** ao "antes" (Horas 26 e Palatino 5, diferença zero). A DLL foi renomeada só na cópia e devolvida (mesma assinatura MD5 de antes). **Mas o aviso não vai para o `erros.log`** (ver Bugs). |
| Imagens da rodada | olho | Abri **todas**: as 21 máscaras, e todos os painéis diferentes entre si das 5 pastas (236 painéis únicos; os repetidos entre pastas, conferidos por assinatura, abri uma vez). Para comparar, montei folhas com as 6 versões de cada página lado a lado e ampliei os pontos duvidosos. |
| Velocidade | não rodei | Pedido da gerente: o teste oficial é dela, com a máquina parada. Opinião sobre os números do implementador abaixo. |

## Página por página

"antes" = detector antigo; "livre" = ScanTailor na forma de fábrica; "ret." = ScanTailor retangular. MP = Mágico pro; PB = Preto e branco.

| Página | Antes × livre | Livre × retangular |
|---|---|---|
| **Palatino 5** (obrigatória) | Quase igual à vista. O título deixa de ser "gravura" (100% → 50%, só o retrato). Papel dentro do retrato branco nos dois. **Melhor por dentro, igual por fora.** | Igual. |
| **Palatino 7** | Igual (a caixa do "PAVLVS" deixa de ser gravura). | Igual. |
| **Palatino 9** | **Melhor:** some a tira creme entre os fios da moldura, à esquerda, no MP e no PB (`v05`). | Igual. |
| **Palatino 10** | Igual. | Igual. |
| **Escola 7** | Igual à vista (diferenças só na beirada da pintura). | Igual. |
| **Horas 11** (obrigatória) | **Muito melhor.** Antes, no MP a iluminura saía em pedaços e no PB virava um borrão preto. Agora sai inteira, com cores, e o centro com "HEURES DE LOUIS LE GRAND" fica branco, com as letras em vermelho e azul (`v01`). É a página que mais se aproxima da regra da Fase 1. | Igual (retangular marca um pouco mais). |
| **Horas 13** (obrigatória) | MP igual (moldura dourada nos dois). **PB pior:** o lado direito e o canto de baixo da moldura dourada saem **pretos**, porque essa parte ficou fora da gravura e foi para o preto e branco (`v04`). | **Retangular pior:** papel creme dentro e fora da moldura. |
| **Horas 47** | Igual (a moldura já era gravura). | Retangular um pouco mais creme. |
| **Opus Majus 3 e 11** | Idênticas. | Idênticas. |
| **Opus Majus 20** (obrigatória) | **Pior no livre:** o vão escuro da porta vira pontinhos pretos sobre branco, a cabeça e o peito da estátua saem lavados de branco, e aparece um **bloco retangular branco** ao lado da estátua; no PB, o vão vira um preto chapado e a estátua some em branco (`v02`). | **Retangular bem melhor**, quase igual ao "antes" e sem o degrau no alto. A estátua ainda sai mais clara que o original (bug já anotado para o 1.5); "perfeita" é exagero. |
| **Opus Majus 165** | **Melhor:** as figuras 7 e 8 passam a traço, e some o retângulo cinza em volta delas; papel branco (`v10`). | Igual. |
| **Opus Majus 256** (tabela) | Melhor ou igual: a tabela vira texto e fica limpa (antes 89% "gravura"). | Igual. |
| **Horas 26** (obrigatória) | **Moldura muito melhor:** antes era um contorno com furos e pontinhos; agora é uma faixa dourada cheia, como no original (`v07`, `v09`). **Ressalva:** o título "NOVEMBRE." e a primeira linha ficam dentro da gravura: o título sai azul-escuro quase preto (o original é azul médio; o "antes" era mais fiel) e, no PB, essa faixa fica colorida enquanto o resto do texto é preto. | **Retangular pior:** papel creme no miolo da moldura. |
| **Horas 27** (obrigatória) | **Moldura muito melhor:** dourada e cheia, no MP e no PB. | Igual à vista. |
| **Escola 35** (obrigatória) | Igual (anjo com a mesma cor). | Igual. |
| **Palatino 67** | **Melhor:** some a caixa cinza em volta de "5 ꝛ ꝑ ꝝ t9", no MP e no PB (`v06`). As duas manchas marrons continuam (são mancha, item 6.2). | Igual. |
| **Rhetorica 18** | Idêntica (0% de gravura nos dois). | Idêntica. |
| **Graduale 222** | **Pior:** pedaços da pauta viram gravura; no MP aparecem blocos cinza-claros com a mancha do verso e notas mais escuras; no PB esses blocos ficam em tons de cinza e vermelho, no meio do preto e branco (`v03`). Some a faixa preta da lombada no PB (isso melhorou). | **Retangular muito pior:** a página inteira vira gravura, papel creme e mancha do verso. |
| **Marial 146** | **Melhor:** some a caixa cinza do título corrido "Sermaõ do Nome...". | Igual. |
| **Marial 153** | **Melhor:** some a caixa cinza de "de Maria." (`v08`). | Retangular deixa a sombra da lombada e o papel cinza no canto. |

**Placar do livre contra o antes** (21 páginas, olhando MP e PB): **9 melhores** (Horas 11, 26, 27, Palatino 5 por dentro, Palatino 9, Palatino 67, Opus 165, Opus 256, Marial 146 e 153; conto Marial como uma só), **3 piores** (Opus 20, Graduale 222, Horas 13 no PB), o resto igual.

## Os bugs que a Lista mandou "para o 1.2"

| Bug | Estado com o livre |
|---|---|
| Palatino 67, caixa cinza | **Resolvido** (MP e PB). |
| Rhetorica 18, orla cinza das letras | **Não mudou**: a página sai idêntica ao "antes". O 1.2 não mexe nisso (não havia gravura ali); fica para o 1.5. |
| Palatino 9, tira creme entre os fios | **Resolvido** (MP e PB). |
| Marial 146 e 153, título corrido tomado por gravura | **Resolvido.** |
| Opus 20, degrau no alto da foto | **No livre, piorou** (vão com pontinhos, bloco branco). **No retangular, resolvido.** |
| Palatino 5, 100% gravura | **Resolvido** (50%, só o retrato). À vista, a página quase não muda. |
| Moldura dos calendários (Horas 26 e 27), 0% | **Resolvido**: a moldura sai dourada e cheia. Na Horas 26 o título "NOVEMBRE." entra na gravura junto (ver acima). |

**Regras da Fase 1:** o 1.2 **aproxima** do resultado na iluminura (Horas 11) e na moldura dourada (Horas 26 e 27), e **afasta** na foto do Opus Majus 20 (livre), no Graduale 222 e na moldura da Horas 13 no Preto e branco.

## A forma de fábrica e a escolha por livro

- **"Livre" de fábrica: concordo.** A retangular estraga o Graduale 222 (página inteira), a Horas 13 e 26 (papel creme) e o Marial 153. Só ganha no Opus 20.
- **Escolher por livro:** serve como remendo e, pelo que vi, **funciona no Opus Majus** (nas páginas 3, 11, 165 e 256 a retangular dá o mesmo que a livre, e na 20 dá bem melhor). Mas tem dois problemas: (1) o Kaique não vai saber qual escolher, e livro com foto e moldura juntos (catecismo ilustrado, por exemplo) não tem forma certa; (2) sem o campo e o botão, hoje nem dá para escolher. Sugestão: de fábrica livre; retangular escolhida por livro só como opção avançada; e, depois, a escolha automática por página que o implementador já pôs na Lista de espera (retangular quando a gravura livre tem um buraco claro grande dentro de uma foto).
- **Regra 8** ("toda função automática tem botão de ligar e desligar"): **ainda não cumprida.** Não há campo no projeto nem controle na tela.

## Regra 6 (velocidade)

Pelos números do implementador (medida isolada, máquina dividida), **a regra 6 está em risco no "trocar de página"**:

- No Marial (o livro do teste oficial), a primeira prévia ficou mais lenta em **18 das 20 páginas** medidas: mediana 2,82 → 3,33 s (+18%, meio segundo). O teste oficial de 29/09 deu "trocar de página" com 2,3 s de média; meio segundo a mais ali deve aparecer.
- "Processar 10 páginas" no Marial: igual (Mágico pro e Preto e branco dentro da variação).
- Fora do teste oficial, há **páginas bem mais lentas**: Graduale 222 (Mágico pro 19 → 30 s; Preto e branco 6 → 23 s), Horas 11 (Preto e branco 17 → 30 s), Horas 26 (prévia 3,6 → 5,9 s), Opus 20 no Preto e branco (8,6 → 13,2 s). Nas páginas de texto do Palatino e do Opus 256 ficou mais rápido.

O teste oficial com a máquina parada é que decide.

## Ressalvas

- Não rodei o `teste_velocidade.py` (pedido da gerente).
- Não pilotei a janela: os cartões e a prévia na tela não foram vistos; conferi a prévia pela função (mesma gravura que o PDF).
- A aba Marcar e o item 1.1 continuam com o detector antigo: o que o Kaique vê na aba Marcar não é o que vai para o PDF.
- Projetos já abertos antes guardam a marcação antiga nas páginas já vistas.
- A pasta 3 ("antes" no Preto e branco) e a pasta 1 dão a mesma imagem no Palatino 5 (a página inteira era gravura no "antes"); não é erro da rodada.
- As folhas e ampliações que montei para comparar ficaram fora do projeto; as que citam `v01` a `v10` estão nesta pasta.

## Bugs para a Lista de bugs (30/09/2026)

1. **O aviso de "DLL faltando ou falhando" não vai para o `erros.log`.** O código usa o `logging` do Python, e o programa não liga o `logging` a nenhum arquivo: rodando pelo console, o aviso aparece no terminal; no programa instalado (sem console), **se perde**. O `selecao.aviso_gravura` também não é mostrado em nenhuma tela. Conferido na cópia com a DLL renomeada: nenhum `erros.log` foi criado. `core/detectar_regioes.py` e `core/gravura_scantailor.py` (`_log.warning`). Sem print (é do log).
2. **Horas 13, Preto e branco, forma livre: o lado direito e o canto de baixo da moldura dourada saem pretos** (antes saía dourada). Print: `v04-horas13-pb-moldura-preta.jpg`.
3. **Horas 26, forma livre: o título "NOVEMBRE." entra na gravura** e sai azul-escuro quase preto no Mágico pro (o original é azul médio) e colorido no meio do Preto e branco. Print: `v07-horas26-moldura-e-titulo.jpg`.
4. Opus 20 (livre) e Graduale 222: já estão na Lista (30/09); confirmo os dois. Acrescento ao do Opus 20 o **bloco retangular branco** ao lado da estátua. Prints: `v02`, `v03`.

## Imagens (ampliações do verificador)

Folhas com 6 versões: original · MP antes · MP livre / MP retangular · PB antes · PB livre.

**v01. Horas 11: a iluminura volta inteira (MP livre, em cima à direita).**

![v01](v01-horas11-iluminura.jpg)

**v02. Opus Majus 20: livre (em cima à direita) com pontinhos no vão e estátua lavada; retangular (embaixo à esquerda) quase como o antes.**

![v02](v02-opus20-livre-x-retangular.jpg)

**v03. Graduale 222: blocos da pauta tratados como gravura (MP livre e PB livre).**

![v03](v03-graduale222-pauta-vira-gravura.jpg)

**v04. Horas 13, lado direito: PB antes (moldura dourada) · PB livre (moldura preta) · MP livre.**

![v04](v04-horas13-pb-moldura-preta.jpg)

**v05. Palatino 9, fios da esquerda: MP antes (tira creme) · MP livre (branco) · PB antes · PB livre.**

![v05](v05-palatino9-tira-creme.jpg)

**v06. Palatino 67: a caixa cinza do "antes" some no livre.**

![v06](v06-palatino67-caixa-cinza.jpg)

**v07. Horas 26, alto da moldura: MP antes (furos) · MP livre (cheia; título escurecido) · PB antes · PB livre.**

![v07](v07-horas26-moldura-e-titulo.jpg)

**v08. Marial 153: a caixa cinza de "de Maria." some no livre.**

![v08](v08-marial153-titulo.jpg)

**v09. Horas 26 inteira.**

![v09](v09-horas26-inteira.jpg)

**v10. Opus Majus 165: o retângulo cinza em volta da figura some no livre.**

![v10](v10-opus165-figura.jpg)
