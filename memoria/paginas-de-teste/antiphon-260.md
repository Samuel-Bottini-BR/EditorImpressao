# Antiphon — página 260 do PDF

- Livro: [antiphon](../livros/antiphon.md) · gabarito: não (89 páginas do estudo, id `antiphon_p260`) · imagem: não está em `gabarito/paginas/`. Imagens: `ramo verif-corte-g6-2026-10-13: relatorios/conferir/corte-g6-2026-10-13/img/lado-antiphon_p260__inteira.jpg`, `causa-antiphon_p260__inteira.jpg`; [estudo, `gravura-errada-antiphon260.jpg`](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md); `ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/img/antiphon-260-1-pagina-recorte.jpg`.
- Antifonário com **iluminura colorida**, pautas e notas (música), **borda preta** do scanner em 2–3 lados. Folha muito grande (~38 milhões de pontos). Gira 0,50°.

## O que ela tem de difícil

- A zona de gravura achada pela iluminura escorre pelas pautas ao lado: as notas dentro dela saem marrons e desbotadas, as de fora saem pretas.
- A iluminura sai chapada no Preto e branco, sem aviso.
- Borda preta embaixo: na ordem nova do G6 a faixa de baixo passa de 2,1 cm para 4,9 cm.
- É das páginas mais lentas de medir (20 a 31 s a 300 DPI, junto com a Antiphon 88).

## Itens que a usam

- [2.2 Endireitar / G6](../itens/2.2.md) e [2.13 Borda preta](../itens/2.13.md): uma das 6 que pioraram com o G6.
- [2.18 Edição manual das zonas](../itens/2.18.md): gravura achada além da iluminura (pautas).
- [Para revisar](../itens/para-revisar.md): rodada 1; uma das 5 páginas que decidem diferente do estudo no livro novo.
- [1.5 Juntar os detectores](../itens/1.5.md): detector de figuras mais certeiro.

## O que já se viu nela, rodada a rodada

- 06/10/2026 → estudo: **errada** nos dois jeitos ("a zona de gravura cobre pautas inteiras: a musica fica desbotada, como no original, e a borda de folhas sai picotada"); vai para revisar (12%). Lista de bugs de 06/10: o detector marca como gravura "a mancha do verso (Marial 454, Antiphon 260)". [estudo](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md)
- 13/10/2026 → verificador do "Para revisar": "a iluminura sai chapada em preto e branco e nenhum aviso fala disso" (Lista de bugs 13/10). [plano, Lista de bugs](../../docs/plano/PLANO-DEFINITIVO.md)
- 13/10/2026 → investigação do G6: **PIOROU** (faixa 3,2% → 7,6%; folha 464 × 590 → 463 × 618 mm). `ramo verif-corte-g6-2026-10-13: relatorios/conferir/corte-g6-2026-10-13/corte-g6.md`
- 13/10/2026 → conserto (`d97b937`): preto embaixo 18,7 mm (antes do G6) → 46,6 mm (G6) → 21,0 mm (conserto); faixa 3,4%. Samuel: "Está bom", com ressalva (abaixo).
- 13/10/2026 → "Para revisar" com os limites reacertados: no livro novo decide diferente do estudo (uma das 5 que não se resolvem com limite). `ramo fase2-para-revisar: relatorios/para-revisar-impl/ONDE-PAREI.md`
- 20/10/2026 → hoje: o verificador do "Para revisar" tem esta página para reabrir na janela (`ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/ONDE-PAREI.md`, passo 2, a fazer).

- 20/10/2026 → quadro da `cg6`: "Melhorar". Conserto do corte juntado (`f418cc3`); o 2.13 é quem tira o resto. Na borda preta, "qualquer cinza neutro escuro" como borda de scanner cortou as notas desta página; ficou "faixa cinza neutra que atravessa ≥ 70% do lado" ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §3).

## O que o Samuel disse

- 06/10/2026, rodada 1: "Sim, deveria ir" ([rodada 1](../../relatorios/revisar-decisoes/rodada-1/respostas-samuel.md)).
- 13/10/2026, quadro `cg6-antiphon-260`, "Está bom": "Mas sobrou preto embaixo." ([conferência 13/10/2026](../../relatorios/conferencia-samuel-2026-10-13.md))

- 20/10/2026, quadro da `cg6`, "Melhorar": "tem que cortar a faixa inteira." (Registro 20/10/2026)

## De onde veio (fontes)

- Estudo do "Para revisar": `relatorios/revisar-decisoes/rodada-3/scripts/comum.py`, `EXTRAS["antiphon_p260"] = ("Antiphon_25.pdf", 260)` ("música com capitular", escolhida olhando miniaturas).
- [plano, Lista de bugs 06/10 e 13/10, Registro 13/10/2026](../../docs/plano/PLANO-DEFINITIVO.md); [histórico, PARTE -15 §5](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (incluir no gabarito do corte).

- [PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) e Registro 20/10/2026 (ver [2.2](../itens/2.2.md), [2.13](../itens/2.13.md)).
