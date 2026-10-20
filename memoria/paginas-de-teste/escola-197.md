# Escola — página 197 do PDF

- Livro: [escola](../livros/escola.md) · gabarito: não (89 páginas do estudo, id `escola_p197`) · imagem: não está em `gabarito/paginas/`; `ramo verif-corte-g6-2026-10-13: relatorios/conferir/corte-g6-2026-10-13/img/lado-escola_p197__inteira.jpg`, `zoom-escola_p197-margem-esquerda.jpg`, `causa-escola_p197__inteira.jpg`; [estudo, `c-escola197.jpg`](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md).
- Página que parece só de texto, com **números de itens na margem esquerda** ("1 -", "2 -", "3 -"). Gira 0,50°.

## O que ela tem de difícil

- No "Só o texto achado" os números da margem perdem pedaços.
- Na ordem nova do G6 o corte **come os números 1, 2 e 3** da margem (tinta de fora 0,03% → 0,28%). Causa: a regra que descarta de cada lado os primeiros 0,2% da tinta (`SOBRA_DE_TINTA = 0.002`, `core/recortar.py`); os três números somam 0,197%. Existe nas duas ordens; a antiga escapava por um triz.

## Itens que a usam

- [2.2 Endireitar / G6](../itens/2.2.md): uma das 6 que pioraram (causa 2, sem borda preta).
- [2.5 Caixa da página](../itens/2.5.md) e [2.13](../itens/2.13.md): pode valer esperar a caixa do conteúdo do ScanTailor, que substitui essa busca.
- [Para revisar](../itens/para-revisar.md): o que o "Só o texto achado" apaga.

## O que já se viu nela, rodada a rodada

- 06/10/2026 → estudo: "Guardar a tinta forte" certa; "Só o texto achado" errada ("os numeros '1 -', '2 -', '3 -' perdem pedacos"); não ia para revisar. [estudo](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md)
- 13/10/2026 → investigação do G6: **PIOROU** (160 × 243 → 155 × 243 mm). Lista de bugs 13/10: "na ordem nova o corte come os números 1, 2 e 3 dos itens". [plano, Lista de bugs](../../docs/plano/PLANO-DEFINITIVO.md)
- 13/10/2026 → o conserto do corte do G6 **não mexeu** nela ("continua igual a hoje"). `ramo conserto-corte-g6-2026-10-13: relatorios/conserto-corte-g6/ONDE-PAREI.md`
- 20/10/2026 → hoje: defeito aberto na Lista de bugs; sem conserto.

## O que o Samuel disse

- Não achado nas fontes lidas (procurei nas conferências de 30/09 a 13/10, rodadas 1 a 5 do "Para revisar" e na página de conferência do conserto).

## De onde veio (fontes)

- Estudo do "Para revisar": `relatorios/revisar-decisoes/rodada-3/scripts/comum.py`, `EXTRAS["escola_p197"]`.
- `ramo verif-corte-g6-2026-10-13: relatorios/conferir/corte-g6-2026-10-13/corte-g6.md` (seção "Causa 2"); [plano, Registro 13/10/2026](../../docs/plano/PLANO-DEFINITIVO.md).
