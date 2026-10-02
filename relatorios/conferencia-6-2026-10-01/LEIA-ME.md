# Sexta conferência do Samuel (01/10/2026)

Os consertos que o Samuel pediu na conferência 5 (respostas literais em
`relatorios/conferencia-samuel-2026-10-01.md`). Formulário: `relatorios/conferir-aqui-6.html`
(marcações no navegador com a chave `conferir-2026-10-01-f`). Feito pelo implementador; o
programa **não mudou** e **nenhuma página foi processada**.

## De onde vêm as imagens (só imagens prontas)

- **ANTES** = a rodada da conferência 5: `relatorios/conferir/pb-mp-decoracao-2026-10-01/`
  (`depois-pb/…0144`, `depois-mp/…0145`).
- **AGORA** = a rodada dos consertos: `relatorios/conferir/conferencia-5-consertos-2026-10-01/`
  (`depois-pb/…2059`, `depois-mp/…2101`).
- **ORIGINAL** = `gabarito/paginas/<id>.png`.
- Corte de 1 mm: `relatorios/corte-folga-1mm-2026-10-01/bordas/` (as folhas de ANTES × DEPOIS
  com a régua de 1 mm fora da página); só ganham um rótulo grande em cima (o título pequeno de
  dentro, que saía cortado, foi trocado) e as estreitas foram ampliadas para 900 pontos.

As imagens de `conferencia-5-consertos-2026-10-01/ampliados/` (ANTES | AGORA, sem ORIGINAL) não
foram usadas diretamente: os cartões foram refeitos a partir dos mesmos resultados, com o
ORIGINAL ao lado. Como o corte mudou um pouco entre ANTES e AGORA (folga de 1 mm), ORIGINAL e
ANTES são redesenhados no enquadramento do AGORA pelos pontos em comum (ORB + ECC, `alinhar.py`
da conferência 4), para o mesmo recorte valer nas três partes.

## Cartões

| Código | O quê | Imagem |
|---|---|---|
| A2 | Horas 11, papel dentro e em volta das letras douradas branco (Mágico pro e Preto e branco) | `cartoes/a2-horas11-mp.jpg`, `a2-horas11-pb.jpg` |
| P4 | Horas 11 no PB, título do oval preto e cheio | `cartoes/p4-horas11-pb.jpg` |
| M2 | Horas 26 no PB, "NOVEMBRE." e a coluna de letras pretas, sem cinza dentro | `cartoes/m2-horas26-pb.jpg` |
| A1 | Horas 47 no PB, os dois "JESUS" e o "C" de "C'est" inteiros | `cartoes/a1-horas47-pb.jpg` |
| M1 | Horas 13, barra de baixo da moldura perto de "pag. 54" (MP e PB) | `cartoes/m1-horas13-mp.jpg`, `m1-horas13-pb.jpg` |
| M3 | Horas 27, barra de cima da moldura perto do canto esquerdo (MP e PB) | `cartoes/m3-horas27-mp.jpg`, `m3-horas27-pb.jpg` |
| F1 | Opus 20 no PB, forma "livre": o rosto volta em cinza | `cartoes/f1-opus20-pb.jpg` |
| C1–C4 | Corte com 1 mm: Escola 7, Escola 35, Palatino 67, Rhetorica 73 | `corte/corte-*.jpg` |
| N1–N6 | Nada piorou: Palatino 5, Escola 35, Graduale 222, PB e MP | `cartoes/n*.jpg` |
| X1 | Entendi: o ponto final azul de "LXXXVIII." (Horas 11 PB), encostado na moldura | `cartoes/x1-horas11-ponto-azul.jpg` |
| X2 | Entendi: Opus 20 no Mágico pro, forma "livre", rosto ainda lavado | `cartoes/x2-opus20-mp.jpg` |

## Observações ao montar

- Palatino 67, borda de baixo: a medida diz 0,8 → 0,1 mm, mas é um pontinho de sujeira embaixo
  do fio (o corte ignora cisco de propósito; LEIA-ME do corte, "Lados abaixo de 1 mm"). Avisado no
  cartão C3.
- Horas 27, M3: a mancha escura no canto da barra de cima também está no original.

## Arquivos

- `scripts/montar_imagens.py`: todas as imagens (usa as peças de desenho da conferência 4).
- `cartoes/`, `corte/`: imagens (fora do git; refazer com o script).
