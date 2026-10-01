# Folga de 1 mm no corte das bordas — 01/10/2026

Pedido: conferência 5 do Samuel, P2 — "O corte das bordas: 0,6 mm ou 1 mm de
papel depois da última letra?" — **"Sim, 1 mm (o corte das 32 páginas muda um pouco)"**.
Achado de origem: `relatorios/corte-crista-2026-10-01/LEIA-ME.md` (a folga era
contada em pontos inteiros da imagem reduzida e arredondada para baixo: 0,6 mm na
Escola 7, 0,4 mm no Boécio).

## O que mudou (core/recortar.py, core/pipeline.py)

- A folga do corte agora é de **pelo menos 1 mm** de cada lado (`FOLGA_MM`), contada
  em milímetros do PDF que sai (o programa passa o DPI da imagem: `projeto.qualidade_dpi`
  no PDF e na prévia, que usam o mesmo corte guardado). Mais 2 pontos: um que o
  `fatiar` perde ao arredondar, outro que a máscara reduzida perde na beirada da letra.
- O lado que **já tinha 1 mm ou mais** fica como estava (a folga é a maior entre 1 mm
  e a de antes). Diminuir para 1 mm nas páginas grandes foi medido e **piorou** o
  Graduale 223 (o número da folha saía partido): não ficou.
- A letra que a folga alcança (o reclamo "A i" do pé do Palatino 7, a ponta do fio da
  moldura do Palatino 67) passa a ter a folga **depois** dela também. Cisco (1–2 pontos
  na imagem reduzida) não ganha folga — senão a borda ia 3 mm para fora no Palatino 7.
- A folga a mais **nunca traz o fundo escuro do scanner** (mesma regra da folga do
  giro): sem isso, o Siebmacher 7 e 9 ganhavam faixa escura embaixo.
- `_parar_no_escuro` só calcula o nível do papel quando alguma coluna nova pode ser
  escura (resultado igual ponto por ponto; deixou o corte mais rápido).

## Antes × depois nas 32 páginas (folga real na página pronta, 300 DPI)

`medir_folga.py` (antes: código `615f05b`, numa cópia à parte; depois: código novo).
Folga = distância da beirada da página pronta (cortada e endireitada) até a peça de
tinta mais perto (6 pontos ou mais) — **inclui cisco**, por isso alguns lados ficam
abaixo de 1 mm mesmo com a folga certa (ver "Lados abaixo de 1 mm").
`*` = o corte já está na beirada do scan desse lado (não há papel para dar folga).
"partidas" = peças de tinta que a borda do corte atravessa (medidor de 01/10).
"na beirada" = peças de tinta encostando na beirada da página pronta.
"escuro" = faixa de 1 mm da beirada abaixo de 60% do papel (borda do scanner).

| Pagina | esq (mm) | dir (mm) | topo (mm) | pe (mm) | corte andou (pt: esq,topo,dir,pe) | partidas | na beirada | escuro <0,6 |
|---|---|---|---|---|---|---|---|---|
| palatino_p005 | 0.42 → 0.76 | 1.10 → 1.78 | 1.27 → 1.61 | 1.19 → 1.19 | [4, 3, 8, 0] | 0 → 0 | 0 → 0 | - |
| palatino_p007 | 0.42 → 1.19 | 0.34 → 1.35 | 1.44 → 1.61 | 0.08 → 1.10 | [8, 2, 11, 11] | 0 → 0 | 0 → 0 | - |
| palatino_p009 | 0.59 → 1.27 | 0.34 → 1.02 | 0.85 → 1.10 | 0.85 → 1.02 | [8, 3, 8, 2] | 0 → 0 | 0 → 0 | - |
| palatino_p010 | 0.51 → 1.19 | 0.25 → 0.93 | 0.59 → 0.85 | 1.10 → 1.35 | [8, 3, 8, 3] | 0 → 0 | 0 → 0 | - |
| palatino_p057 | 0.51 → 1.19 | 0.51 → 1.19 | 1.02 → 1.19 | 0.93 → 1.10 | [8, 2, 8, 2] | 0 → 0 | 0 → 0 | - |
| palatino_p066 | 0.42 → 1.19 | 0.59 → 1.19 | 0.93 → 1.19 | 0.93 → 0.25 | [9, 3, 8, 10] | 0 → 0 | 0 → 0 | - |
| palatino_p067 | 0.42 → 0.85 | 0.17 → 0.25 | 0.93 → 1.19 | 0.85 → 0.08 | [5, 3, 12, 11] | 1 → 0 | 0 → 0 | - |
| marial_p007 | 0.68 → 0.68 | 0.34 → 0.34 | 0.93 → 0.93* | 0.17 → 0.17* | [0, 0, 0, 0] | 0 → 0 | 10 → 10 | - |
| graduale_p221 | 0.51 → 0.51* | 2.62 → 2.62 | 0.76 → 0.76 | 1.52 → 1.52 | [0, 0, 0, 0] | 1 → 1 | 6 → 6 | - |
| graduale_p222 | 5.50 → 5.50 | 5.42 → 5.42 | 0.42 → 0.42 | 3.98 → 3.98 | [0, 0, 0, 0] | 0 → 0 | 2 → 2 | - |
| graduale_p223 | 1.61 → 1.61 | 3.13 → 3.13 | 0.51 → 0.51 | 2.54 → 2.54 | [0, 0, 0, 0] | 1 → 1 | 4 → 4 | - |
| horas_p011 | 0.59 → 0.59 | 0.51 → 0.51 | 0.25 → 5.16 | 2.29 → 2.29 | [0, 15, 0, 0] | 0 → 0 | 3 → 3 | - |
| horas_p013 | 1.69 → 1.69 | 13.29 → 13.29 | 5.67 → 5.67 | 2.88 → 2.88 | [0, 0, 0, 0] | 0 → 0 | 1 → 1 | - |
| horas_p014 | 1.61 → 1.61 | 1.86 → 1.86 | 39.54 → 39.54 | 10.92 → 10.92 | [0, 0, 0, 0] | 0 → 0 | 0 → 0 | - |
| horas_p026 | 1.10 → 1.10 | 1.52 → 1.52 | 20.15 → 20.15 | 40.64 → 40.64 | [0, 0, 0, 0] | 0 → 0 | 1 → 1 | - |
| horas_p027 | 0.76 → 0.76 | 0.93 → 0.93 | 51.99 → 51.99 | 66.21 → 66.21 | [0, 0, 0, 0] | 0 → 0 | 1 → 1 | - |
| horas_p047 | 1.61 → 1.61 | 1.27 → 1.27 | 2.96 → 2.96 | 2.71 → 2.71 | [0, 0, 0, 0] | 0 → 0 | 0 → 0 | - |
| escola_p007 | 0.85 → 1.35 | 0.59 → 1.10 | 19.47 → 19.47 | 0.08 → 0.08* | [6, 0, 6, 0] | 0 → 0 | 2 → 2 | - |
| escola_p035 | 0.76 → 1.27 | 2.29 → 2.79 | 2.37 → 2.37 | 0.51 → 0.51 | [6, 0, 6, 0] | 3 → 3 | 2 → 2 | - |
| siebmacher_p007 | 0.85 → 1.35 | 3.39 → 3.39* | 1.95 → 1.95* | 2.54 → 2.54 | [6, 0, 0, 0] | 0 → 0 | 4 → 4 | dir 0.09→0.09, topo 0.10→0.10, pe 0.21→0.21 |
| siebmacher_p009 | 0.85 → 1.27 | 3.30 → 3.30 | 2.46 → 2.46* | 1.52 → 1.52 | [5, 0, 0, 0] | 0 → 0 | 4 → 4 | dir 0.10→0.10, topo 0.10→0.10, pe 0.25→0.25 |
| rhetorica_p018 | 0.76 → 1.35 | 0.51 → 1.10 | 1.27 → 1.61 | 1.61 → 1.61 | [7, 4, 7, 0] | 0 → 0 | 0 → 0 | - |
| rhetorica_p073 | 0.42 → 0.42* | 0.59 → 1.19 | 1.19 → 1.19 | 1.10 → 1.10 | [0, 0, 7, 0] | 0 → 0 | 1 → 1 | topo 0.40→0.40 |
| boecio_p003 | 0.34 → 0.34* | 0.17 → 0.17* | 0.76 → 0.59 | 0.51 → 1.10 | [0, 7, 2, 7] | 0 → 1 | 3 → 3 | - |
| boecio_p007 | 0.17 → 0.08* | 0.25 → 1.10 | 0.76 → 0.76 | 1.78 → 2.29 | [5, 6, 10, 6] | 0 → 0 | 2 → 0 | - |
| boecio_p008 | 4.66 → 4.66* | 0.76 → 0.76* | 1.95 → 2.29 | 0.51 → 1.02 | [0, 4, 0, 6] | 0 → 0 | 0 → 0 | - |
| boecio_p022 | 0.34 → 1.19 | 2.20 → 2.37 | 0.25 → 0.59 | 0.85 → 1.35 | [10, 4, 2, 6] | 0 → 0 | 0 → 0 | - |
| opusmajus_p011 | 0.51 → 1.10 | 0.51 → 1.10 | 1.35 → 1.35 | 1.19 → 1.19 | [7, 0, 7, 0] | 0 → 0 | 0 → 0 | - |
| opusmajus_p003 | 21.51 → 21.51* | 37.76 → 37.76* | 21.08 → 21.08* | 6.01 → 6.01* | [0, 0, 0, 0] | 0 → 0 | 0 → 0 | - |
| opusmajus_p020 | 0.34 → 0.85 | 0.25 → 0.68 | 1.35 → 1.35 | 0.93 → 0.93 | [6, 0, 5, 0] | 0 → 0 | 0 → 0 | - |
| opusmajus_p165 | 0.68 → 1.27 | 0.51 → 1.19 | 1.27 → 1.27 | 1.19 → 1.27 | [7, 0, 8, 1] | 0 → 0 | 0 → 0 | - |
| opusmajus_p256 | 0.85 → 1.19 | 7.11 → 7.45 | 1.19 → 1.52 | 0.85 → 1.44 | [4, 4, 4, 7] | 0 → 0 | 0 → 0 | - |

tempo detectar_bordas, 32 paginas: 2.436 -> 2.354 s

(`folga-antes.json`, `folga-depois.json`; tabela feita por `comparar.py`.)

### O que a tabela diz

- **Nenhuma peça de tinta passa a ser cortada**, com uma exceção que não é conteúdo:
  Boécio 3, um traço de 2 × 8 pontos da linha da beirada da folha, colado na
  beirada esquerda do scan, passa 2 pontos da borda de baixo (a borda desceu 7 pontos).
  O Palatino 67 **deixa** de ter a ponta do fio da moldura cortada (1 → 0).
- **Nenhuma página ganha faixa escura do scanner.** Siebmacher 7 e 9 já tinham faixa
  escura à direita e em cima (antes e depois iguais); embaixo, sem a proteção nova,
  ficavam mais escuros — com ela, iguais a antes.
- **Páginas grandes (Graduale, Horas, Marial) iguais a antes** — a folga delas já
  passava de 1 mm — exceto **Horas 11**, em cima: a borda subiu 15 pontos (1,3 mm)
  porque a folha de cima da iluminura (encostada na beirada do papel) agora ganha
  folga; entra 1,3 mm a mais do fundo claro do scanner acima da beirada do papel (não escuro).
- Corte mudou em 22 das 32 páginas, sempre **para fora** (só cresce), até 15 pontos
  por lado (1,3 mm, Horas 11 em cima); quase sempre 5 a 8 pontos dos lados (o que
  faltava para 1 mm); Palatino 7 e 67, 11–12 pontos à direita e embaixo.
- O ângulo medido mudou em 2 páginas, porque é medido na página já cortada:
  Palatino 7 −0,1° → +0,1° (os dois no limite de girar) e Boécio 3 0,7° → 0,6°.

### Lados abaixo de 1 mm, depois (e por quê)

- Cisco perto da beirada, que o corte ignora de propósito: Palatino 66 e 67 embaixo
  (pontinho embaixo da moldura), Palatino 10 em cima, Boécio 3 e 22 em cima.
- Página endireitada (o giro tira um pouco da folga dos cantos; a folga do giro dá
  só 2 pontos): Palatino 5 à esquerda (0,4°, 0,76 mm), Opus 20 (−0,4°, a foto, 0,68–0,85 mm).
- Lado já colado na beirada do scan (`*`) ou com conteúdo encostado (Marial 7, Graduale
  221/223, Horas 11 à esquerda e direita, Escola 35 embaixo — o endereço do site,
  item 6.4): iguais a antes; ali a folga não chega por regra (o descarte da tinta de
  fora, o limite de esticar 2%).

## Velocidade (regra 6)

`tempo_corte.py`: `_geometria` (corte + ângulo + folga do giro) nas 32 páginas a
300 DPI, menor de 5 repetições, alternando antes e depois, 3 vezes:
antes 3,20 / 3,21 / 3,08 s — depois 3,08 / 2,86 / 2,92 s. **Não ficou mais lento**
(ficou ~5% mais rápido pela porta rápida do `_parar_no_escuro`). O outro implementador
rodava ao mesmo tempo; o teste_velocidade.py completo não foi rodado.

## Para o Samuel ver

- `bordas/bordas-<página>.jpg`: a beirada da página pronta (filtro Original),
  ampliada 2×, ANTES à esquerda e DEPOIS à direita, nos lados que mudaram. A beirada
  da página é o lado onde está a régua vermelha de 1 mm (desenhada **fora** da
  página, na faixa branca de baixo). Nada desenhado em cima da página.
  Graduale 221 e 223: nenhum lado mudou (sem folha).
- Conferência completa: `relatorios/conferir/corte-folga-1mm-2026-10-01/2-depois/`
  (`conferencia-fase1.html`, coluna "Rodada anterior" = antes, filtro Original;
  o antes em `1-antes/`). Atenção: o painel da página inteira da conferência tem o
  retângulo rosa do "detalhe" desenhado em cima (é assim o `conferencia.py`); para a
  beirada, olhar as `bordas-*.jpg`.

## Testes

`tests/test_corte_folga_1mm.py` (6): a folga é ≥ 1 mm e ≤ 2,5 mm de cada lado a 150,
300, 400 e 600 DPI; a mesma em mm a 150 e a 600 DPI; o PDF final (processar, 300 DPI)
tem ≥ 1 mm de papel de cada lado e a prévia de 110 DPI mostra o mesmo corte.
Falhavam antes (PDF final: 0,51 mm à esquerda).
