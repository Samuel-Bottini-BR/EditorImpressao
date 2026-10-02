# Parecer do verificador: consertos da conferência 6 (A1 Horas 47, X2 Opus 20)

Verificador, 02/10/2026, ramo `fase-1`. Commits conferidos: `1b174e4` (A1) e `6748949` (X2).
Aqui só há **PRONTO PARA CONFERIR** ou **NÃO ESTÁ PRONTO** e a opinião; quem marca é o Samuel.

> **Defeito conhecido (decisão do Samuel, 28/09):** a moldura dourada e a iluminura ainda não saem
> como devem (itens 1.4 e 1.5, adiados). No Preto e branco a moldura dourada da Horas 14 continua
> virando barra preta grossa: isso **não** é deste conserto e não mudou.

## Em uma frase

- **A1, Horas 47 no Preto e branco: PRONTO PARA CONFERIR.** As letras do texto inteiro agora saem
  cheias e legíveis, perto do original; nenhuma letra fechou o miolo nem grudou na vizinha. Ressalva
  nova: o medidor "mais fraco / mais escuro" agora mexe nessas páginas, e no "mais escuro" máximo
  algumas letras voltam a falhar (ver ressalva 1).
- **X2, Opus Majus 20 no Mágico pro (forma "livre"): PRONTO PARA CONFERIR.** O rosto volta a
  aparecer, o vão da porta fica escuro e liso, sem os pontinhos e sem o retângulo branco; sai
  praticamente igual a "Este livro tem fotos". O rosto continua mais claro que no original.

## Como foi conferido

**Por máquina:**

- Rodei eu mesmo, de duas cópias limpas do código (o commit anterior aos consertos, `4a9c0e4`, e o de
  agora, `68d8159`), as 32 páginas do gabarito no **Preto e branco, no Mágico pro e no Melhorar**,
  pelo mesmo caminho do botão "Confirmar e processar". Sem janela na tela e sem gravar na pasta de
  dados do Samuel.
- As imagens do implementador (ANTES e AGORA, Preto e branco e Mágico pro) são **idênticas ponto a
  ponto** às minhas nas 32 páginas: o relatório dele mostra o código de hoje.
- Preto e branco: 22 páginas idênticas; Horas 11 com diferença desprezível; 9 páginas mudaram, e
  **sempre só para mais preto** (nenhum ponto clareou): Horas 47, 13 e 14; Escola 7 e 35;
  Graduale 221, 222 e 223; Opus 20 (a legenda). Bate com o que o implementador escreveu.
- Mágico pro e Melhorar: 31 páginas idênticas ponto a ponto; só o Opus 20 mudou. No Mágico pro, o
  Opus 20 de agora difere de "Este livro tem fotos" em 0,04% dos pontos (mais de 30 tons).
- Testes: ver o fim.

**Por olho:** abri as 96 comparações (32 páginas × 3 filtros): as que mudaram uma a uma, com o
detalhe da lista do gabarito e o lugar de maior mudança ampliados, e recortes em tamanho real
(1:1) da Horas 47, 13 e 14, da Escola 7 e 35, do Graduale 221 e 223 e do Opus 20; as idênticas em
folhas de contato (são as mesmas imagens ponto a ponto). Abri também os cartões do implementador.

## O que vi em cada página que mudou (Preto e branco)

| Página | O que vi |
|---|---|
| Horas 47 | Texto inteiro cheio e legível ("Changeant", "ayez pitié de nous", "amour propre en amour divin", "Enseignez moy Seigneur"); em tamanho real o miolo de e, o, a, œ continua aberto, nada grudou. A borda da letra ainda é um pouco serrilhada (o scan é de 72 DPI). Os JESUS e o C dourados inteiros. Papel branco. |
| Horas 13 | Letras um pouco mais cheias. O fio na beirada de cima, à direita, que o implementador citou: ganhou poucos pontos (140 pontos numa página de 24 milhões); em tamanho real não se distingue do ANTES. **O Samuel não notaria.** O traço preto comprido na beirada esquerda já existia antes. |
| Horas 14 | Números e letras da tabela mais cheios, miolos (6, 8, 9, a, e) abertos. A moldura dourada como barra preta: igual ao antes (defeito conhecido). |
| Escola 7 | Texto mais encorpado que antes e um pouco mais forte que o original (o original é de traço fino); continua limpo e legível, sem letra fechada. A beirada da foto ganhou um fio escuro um pouco mais marcado; quase invisível. |
| Escola 35 | Texto um pouco mais cheio; a gravura em cinza igual. |
| Graduale 221 | Notas e letra góticas iguais a olho. Os riscos finos verticais da pauta (ponta seca) ficaram alguns pontos mais compridos: só se vê ampliando muito. **O Samuel não notaria na página inteira.** |
| Graduale 222 | Praticamente igual (0,07% da página); nada novo à vista. |
| Graduale 223 | Igual ao 221; e a linha pontilhada da margem direita (risco de régua do pergaminho) ficou um pouco mais contínua em alguns trechos. Já aparecia antes, tracejada; ampliado se nota, na página inteira dificilmente. |
| Opus 20 | A legenda "ROGER BACON / The Hope-Pinker Statue..." mais cheia e mais legível (ainda com falhas no "BACON"). Foto igual. |
| Horas 11 | Igual a olho. |
| As outras 22 | Idênticas ponto a ponto (Palatino 5, 7, 9, 10, 57, 66, 67; Marial 7; Horas 26 e 27; Siebmacher 7 e 9; Rhetorica 18 e 73; Boécio 3, 7, 8, 22; Opus 3, 11, 165, 256). |

**Mancha do verso e sujeira:** nenhuma página passou a mostrar mancha do verso nem sujeira em preto;
na Horas 13 (que tem o "TABLE" do verso aparecendo no original) o fundo continua branco. Não achei
página que piorou e não foi dita.

## Opus Majus 20 no Mágico pro e no Melhorar

- **Rosto:** volta a aparecer, com o nariz, o olho e o queixo desenhados pela retícula da foto; mas
  continua **mais claro que no original**, sem as sombras do rosto. É exatamente o mesmo resultado de
  "Este livro tem fotos" (comparei lado a lado em tamanho real). Se o Samuel ainda achar o rosto
  lavado, o pedido passa a valer para as duas formas, e é outro conserto (o jeito do Mágico pro
  clarear foto).
- **Atrás da estátua:** o vão da porta saiu escuro e liso, sem nenhum pontinho, e o retângulo branco
  sumiu.
- **O que sobra:** na parede de pedra à esquerda e em cima ficam umas linhas finas claras, onduladas,
  como contornos. Já estavam no ANTES e estão também em "Este livro tem fotos": não são deste
  conserto, mas o Samuel pode notar se ampliar.
- **Melhorar:** rodei as 32 páginas (o implementador não tinha rodado). Só o Opus 20 mudou, igual ao
  Mágico pro (rosto, vão escuro, sem pontinhos nem retângulo); as outras 31 idênticas ponto a ponto.
  Observação à parte, não deste conserto: nas páginas do gabarito o Melhorar e o Mágico pro saem
  quase iguais (diferença média de 0,02 a 0,55 tom).
- No Preto e branco o Opus 20 (F1, aprovado) não mudou na foto.

## Ressalvas

1. **O medidor de força do Preto e branco passou a mexer nas páginas de letra grossa, e de um jeito
   estranho na ponta.** Antes, nas páginas em que o programa usa o Otsu (Horas, Graduale, Escola,
   Opus 20), o medidor não fazia nada. Agora ele mexe na beirada da letra (testei só o filtro, na
   Horas 47, Graduale 221 e Escola 35, força 0, 50 e 100):
   - em **0 ("mais fraco")** a letra volta a ser exatamente a fina e falhada que o Samuel recusou;
   - em **50 (o padrão)** é o resultado bom deste conserto;
   - em **100 ("mais escuro")**, na Horas 47, algumas letras voltam a sair falhadas ("nous",
     "Prêchant"): o "mais escuro" deixa letras **mais claras** que o meio. Causa provável: com o
     medidor alto, o pedaço de tinta do Sauvola cresce e se junta a vizinhos, a parte do Otsu dentro
     dele cai abaixo de 50% e o pedaço inteiro é recusado.
   O padrão está bom; o problema só aparece se o Kaique puxar o medidor ao máximo. Sugiro ir para a
   Lista de bugs (ou o implementador limitar a histerese pela força), e avisar o Samuel. Imagem:
   `medidor/comparar-horas_p047.jpg`.
2. **Regra 6 (velocidade), Horas 11 no Preto e branco: +0,2 a 0,4 s (de ~13,1 para ~13,4 s, uns
   2–3%).** Ao pé da letra a regra diz "nenhum item pode deixar o programa mais lento", então
   **fere a regra nessa página**. Na soma, o Preto e branco ficou mais rápido: Horas 47 −5,4 s,
   Horas 13 −1 s, Escola 35 −0,9 s, e as outras iguais ou mais rápidas. Não refiz a medição
   completa (outro agente no PC); na minha rodada única das 32 páginas pelo caminho do botão, o
   total foi de 179 s antes para 153 s agora (Horas 47 de 20,8 para 13,9 s), o que bate com os
   números do implementador; a Horas 11 nessa rodada não serve de prova (a máquina estava ocupada).
   **Recomendação:** não segurar o conserto por isso, mas dizer ao Samuel com essas palavras e
   deixar a decisão com ele. E pedir ao implementador uma olhada barata: na Horas 11 a medida rápida
   falha só porque a tinta dá 60,4% contra uma trava de 60%, e por isso a medida lenta (~9,5 s) é
   feita. Resolver essa trava deixaria a Horas 11 bem mais rápida do que era, pagando de sobra os
   0,3 s.
3. **Graduale 221/223 (riscos da pauta) e Horas 13 (o fio):** existem, mas são de poucos pontos;
   na página inteira e no detalhe normal o Samuel não notaria.
4. **Letra mais forte que o original na Escola 7:** o texto, que no original é fino, ficou um pouco
   mais encorpado. Continua bom de ler; se o Samuel achar "grosso demais", é aqui.
5. Não pilotei a janela: o item é de imagem, e a rodada passa pelo mesmo caminho do botão
   "Confirmar e processar".

## As imagens que o Samuel deve ver no formulário

1. `para-o-samuel/a1-horas47-pb.jpg` (cópia de `../cartoes/a1-horas47-pb.jpg`, do implementador): **Horas 47, ORIGINAL · ANTES · AGORA**: leia o texto do AGORA e
   diga se está tão bom de ler quanto o original.
2. `para-o-samuel/horas47-tamanho-real.jpg`: **Horas 47 em tamanho real** (ANTES em cima, AGORA embaixo): veja se alguma
   letra ficou grossa demais ou fechou o miolo (e, o, a).
3. `para-o-samuel/x2b-opus20-mp-com-referencia.jpg` (cópia do cartão do implementador): **Opus Majus 20 no Mágico pro**, com "Este livro
   tem fotos" ao lado: o rosto aparece? o vão atrás da estátua ficou limpo? o rosto ainda está claro
   demais?
4. (opcional) `para-o-samuel/horas47-medidor.jpg`: **o medidor "mais escuro" no máximo** (última
   faixa): algumas letras voltam a falhar; diga se isso incomoda.

![Horas 47 no Preto e branco](para-o-samuel/a1-horas47-pb.jpg)

![Horas 47 em tamanho real: ANTES em cima, AGORA embaixo](para-o-samuel/horas47-tamanho-real.jpg)

![Opus Majus 20 no Mágico pro, com a referência](para-o-samuel/x2b-opus20-mp-com-referencia.jpg)

![O medidor na Horas 47: antes 50; agora 0, 50 e 100](para-o-samuel/horas47-medidor.jpg)

## Testes

`pytest tests -q` (sem janela), no código de agora, uma vez: **1359 passaram, 1 pulado, nenhum falhou** (10 min). São 4 a mais que os 1355 do implementador porque, enquanto eu conferia, outra frente juntou o conserto do "salvar como (2)" (`25d916e`, com testes novos; não mexe em `core/`). Os testes novos deste conserto (`tests/test_conferencia_6.py`) passam.

## Onde está tudo

- Este parecer e os scripts do verificador: `relatorios/conferir/conferencia-6-consertos-2026-10-02/verificador/`
  (`rodar_verificador.py`, `montar_verificador.py`, `medidor_verificador.py`, `zoom.py`, `folha.py`,
  `comparar_com_implementador.py`).
- Os cartões de cada página e filtro: `verificador/cartoes/<página>-<filtro>.jpg`; as folhas de
  contato: `verificador/cartoes/folha-*.jpg`; os números: `verificador/numeros-<filtro>.json`.
- Os recortes em tamanho real: `verificador/zoom/`; o teste do medidor: `verificador/medidor/`.
