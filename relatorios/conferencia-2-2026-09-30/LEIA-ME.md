# Segunda conferência do Samuel (30/09/2026)

Formulário: `relatorios/conferir-aqui-2.html` (as marcações ficam no navegador com a chave `conferir-2026-09-30-b`). Feito pelo implementador; o programa **não mudou**.

## 1. Zonas do gabarito do OCR corrigidas (`gabarito/ocr-zonas.json`)

A versão anterior está guardada em `gabarito/ocr-zonas.antes-2026-09-30.json`. Cada página alterada tem o campo `revisado_2026_09_30` dizendo o que mudou.

| Página | O que mudou |
|---|---|
| Horas 13 | Moldura dourada refeita em pedaços (~18 por lado) que abraçam o ouro e o contorno marrom dele, medidos pela cor do ouro. Antes o "buraco" de dentro cortava a borda interna da faixa. O subtítulo "CONTENU EN CE LIVRE." **já estava** no verde: o que parecia "apagar" era a imagem antiga, que só pintava o risco escuro. As letras que tocam o ouro ganharam caixinha verde própria. |
| Horas 26 | Moldura igual à Horas 13 (antes a linha de dentro cortava a faixa esquerda e a de baixo). As letras (inclusive os "A" dourados) já estavam no verde. |
| Horas 27 | Moldura igual; a lista dos dias entrava na faixa direita (torta) e o ouro contava como texto (3,5% do ouro era "texto"). Duas letras que encostam no ouro ganharam caixinha verde. |
| Horas 47 | Iluminura com folga de ~0,7% em volta (antes encostava na borda da pintura). A imagem antiga só mostrava o risco escuro da pintura. |
| Opus Majus 256 | A tabela vai até a borda direita e a de baixo (antes a última coluna e o canto de baixo à direita ficavam de fora). |
| Rhetorica 18 | Os filetes viraram tiras finas que seguem só o fio (o da direita é torto); o corpo virou 8 faixas de filete a filete, então letras e sílabas que tocam o fio contam como texto. Notas de margem com as pontas inteiras. |
| Escola 7 | Nada: a zona já pegava a gravura inteira (o "vermelho do lado" era o jeito de mostrar). |
| Escola 35 | A gravura desce até o fim da pintura (faltava uma tira de ~1 mm, em cima da legenda). |
| Horas 11 | A iluminura sobe até a ponta do enfeite de cima e pega a borda esquerda; o oval do meio ficou um fio menor (a moldura do oval caía no "buraco"). |
| Opus Majus 165 | Letrinhas dos diagramas: uma caixinha justa por letra (antes caixas grandes pegavam as linhas do desenho e cortavam o "d" de baixo da Fig. 7); figuras com mais folga. |
| Graduale 221–223 | O que faltava: as caixas das palavras eram justas e cortavam hastes, pernas e rubrica. Foram alargadas até pegar as letras inteiras, sem pegar notas. |

**A confusão da imagem antiga:** o painel da direita das imagens de `fase1-1.3-comparacao-ocr-2026-09-28/zonas/` mostrava só a tinta escura (Sauvola), pintada pela zona. Ouro, pintura e letra colorida quase não viram "tinta", então pareciam "apagados". As imagens novas contornam a zona por cima da página original.

## 2. A régua do 1.3 com as zonas novas

Script: `scripts/recalcular_regua.py` (lê as linhas dos OCRs já gravadas; não roda OCR). Números em `regua-1.3-recalculada.json`.

- **Texto achado:** igual (docTR `fast_base` 98,7%, Kraken 95,5%, média das 19 páginas). Só o Graduale caiu, porque as caixas cresceram: docTR 221/222/223 = 97,5 / 97,5 / 95,7% (antes 98,1 / 99,0 / 97,2); Kraken 98,1 / 96,5 / 91,1% (antes 98,7 / 98,6 / 94,8).
- **Figura tomada por texto (com o alargamento de 15%):** sobe onde a moldura cresceu. Kraken na Horas 13: 0,90% → **1,39%** (passa de 1% numa obrigatória). docTR na Horas 13: 8,2% → 11,6%; na Horas 27: 0,1% → 1,3%. Opus 165: docTR 0% → 5,4%, Kraken 6,6% → 9,3% (as linhas do desenho agora são figura).
- **Sem o alargamento de 15%**, o Kraken continua com 0% em todas as 7 obrigatórias; o docTR passa a ter 2 acima de 1% (Palatino 5 e Horas 13).
- **Kraken + docTR onde os dois concordam:** pior obrigatória 0,68% → 1,19% (Horas 13), páginas acima de 1%: 0 → 2 (Horas 13, Opus 165).
- **Recomendação (docTR + Kraken): não muda.** O Kraken continua o único que não pisa em figura nas obrigatórias sem o alargamento, e o que passou de 1% na Horas 13 é a caixa alargada encostando na moldura (letra colada no ouro), não caixa em cima da figura. Os outros pioram mais (P3, P2, P1, T* passam a ter Horas 26/27 acima de 1%).
- **Comparação automática (revisar/concorda):** a decisão de cada página não depende das zonas, então é a mesma. O que muda é o "erro conhecido" pela régua: com as zonas novas, **Horas 27** (docTR 1,3% de figura) e **Graduale 221 e 222** (texto abaixo de 98%) passam a ser erro que a comparação **não pega** (antes só o Graduale 223). Ou seja: de 22 páginas, a decisão bate em 18 (antes 21; o Palatino 7 conta como acerto pelo erro visto de olho em 29/09). Vale reavaliar a calibração da comparação quando o Samuel aprovar as zonas.

## 3. Arquivos

- `zonas/`, `decisoes/`, `fotos-pb/`, `pb-novo/`, `vermelho/`, `refazer/`, `gravuras/`: imagens do formulário (fora do git; refazer com os scripts).
- `scripts/util_imagens.py`: rótulos, marcas, zona por cima da página.
- `scripts/montar_imagens.py`: todas as imagens do formulário (rodar antes `print_o_que_fazer.py` e `simular_vermelho.py`).
- `scripts/print_o_que_fazer.py`: print da tela "O que fazer" sem janela visível (Qt offscreen).
- `scripts/simular_vermelho.py`: Preto e branco pelo caminho inteiro do programa, trocando só dentro do processo a conversão para cinza. **Achado:** a pauta vermelha do Graduale já sai preta hoje (221 e 222 idênticos nas duas contas); o que muda é só a rubrica (títulos da Horas 13, palavra vermelha do Graduale 223).
- `scripts/recalcular_regua.py`: a régua do 1.3 com as zonas antigas e novas.

## 4. Resultado ao lado da zona (pedido do Samuel, 30/09)

"nessa conferência, tu tem que colocar não só a seleção, mas o resultado da seleção como ela ficou depois de retirar o fundo, junto do que você já colocou."

Todos os cartões de zona (Z6–Z12, Z16–Z18, Z20–Z22) ganharam o painel azul **RESULTADO**, com a página já processada, no mesmo recorte. Nenhuma página foi processada de novo: só imagens prontas, alinhadas à página original por pontos em comum (ORB + ECC, `resultado_alinhado` em `montar_imagens.py`).

- Mágico pro: `relatorios/conferir/fase1-1.2-opcoes-2026-09-30/resultado/*-magico_pro-A.png` (programa de hoje) quando há; senão `fase1-1.2-ligacao-2026-09-30/2-depois-magico-pro/1.2-2026-09-30-0023/resultado/`; senão `fase1-2026-09-29-0212/resultado/` (29/09, detector antigo: **Graduale 221 e 223**).
- "Tirar o fundo" (Opus 165, Opus 256, Rhetorica 18): `fase1-2026-09-29-1826/resultado/`.
- Nenhuma página ficou sem resultado pronto.
