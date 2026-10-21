# Pesel — página 21 do PDF

- Livro: [pesel](../livros/pesel.md) · gabarito: não (está nas 89 páginas do estudo, id `pesel_p021`) · imagem: não está em `gabarito/paginas/`; imagens do conserto em `ramo conserto-corte-g6-2026-10-13: relatorios/conferir/conserto-corte-g6-2026-10-13/img/` (fora do git).
- Página de **cartão escuro** (bordado colado num cartão), com a legenda miúda impressa no papel escuro. Livro do Internet Archive (com camadas). Gira -2,00° no livro novo.

## O que ela tem de difícil

- O papel é escuro de verdade: o programa pode confundir o cartão com fundo de scanner e cortar rente.
- A legenda no papel escuro vira tarja preta no Preto e branco e no "Só as letras".
- Faixa escura na beirada medida: 47,3% (o próprio cartão).

## Itens que a usam

- [2.2 Endireitar / G6](../itens/2.2.md) e o conserto do corte do G6: efeito de lado do conserto (ver abaixo).
- [2.13 Borda preta](../itens/2.13.md): o cartão escuro não pode ser tratado como borda.
- [Para revisar](../itens/para-revisar.md): rodada 1.

## O que já se viu nela, rodada a rodada

- 06/10/2026 → estudo do "Para revisar": errada nos dois jeitos do "Só as letras" ("a legenda no papel escuro vira tarja preta (o Preto e branco faz o mesmo; nao e do Misto)"); ia para revisar (21%). [estudo](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md)
- 13/10/2026 → investigação do G6: gira, mas sai igual nas duas ordens (157 × 241 mm). `ramo verif-corte-g6-2026-10-13: relatorios/conferir/corte-g6-2026-10-13/corte-g6.md`
- 13/10/2026 → conserto do corte do G6 (`d97b937`): o Pesel 21 passou a sair cortado rente (15,7 × 24,1 → 14,5 × 20,6 cm, legenda a 1 ou 2 mm da borda). Efeito de lado, para o Samuel decidir. [plano, Registro 13/10/2026](../../docs/plano/PLANO-DEFINITIVO.md)
- 13/10/2026 → Samuel: "Está pior" (ver abaixo). Decisão da gerente: o implementador acerta o Pesel 21 (tem de sair como sai hoje) no mesmo ramo; a decisão `cg6` foi reaberta na página até isso.
- 19/10/2026 → agente liberado pelo Samuel para o Pesel 21 ("Implementador 1 - ok", [plano, Registro 19/10/2026](../../docs/plano/PLANO-DEFINITIVO.md)).
- 20/10/2026 → hoje, **EM ANDAMENTO** no ramo `conserto-corte-g6-2026-10-13` (`3283012`): causa achada (a pergunta "há o que recortar?" era feita na página girada; o branco da cunha mudava a mediana do cartão de 102 para 125); conserto feito (`detectar_bordas(..., como_veio=)`); testes de reversão `test_cartao_escuro_sai_inteiro_no_livro_novo` e `test_pesel_21_sai_como_no_fase_1` falham no código antigo. Faltam: medida das 89, projeto antigo 40 de 40, antes/depois, suíte no GitHub. `ramo conserto-corte-g6-2026-10-13: relatorios/conserto-corte-g6/ONDE-PAREI.md`

- 20/10/2026 → quadro da `cg6`: "Está bom"; o Pesel 21 sai idêntico ao `fase-1` (15,7 × 24,1 cm) e as cinco melhorias de 13/10 saem idênticas ao `d97b937`. Juntado ao `fase-1` (`f418cc3`). 21/10/2026: pergunta para levar com a caixa do conteúdo: "Pesel 21: só o preto ou até a moldura nesse livro?" ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §5).

## O que o Samuel disse

- 06/10/2026, rodada 1 do "Para revisar": "Sim, deveria ir" ([rodada 1](../../relatorios/revisar-decisoes/rodada-1/respostas-samuel.md)).
- 13/10/2026, quadro `cg6-pesel-21`, "Está pior": "Ele chega a quase cortar as letras. Nós estamos olhando o endireitar com o cortar ou só o endireitar?" ([conferência 13/10/2026](../../relatorios/conferencia-samuel-2026-10-13.md))

- 20/10/2026, quadro `cg6-pesel-21`, "Está bom", com o comentário da `cg6`: "pode entrar como está, mas vamos melhorar ele ainda, e descobri uma coisa [...] deveriamos ter indireitado a folha antes de cortar [...]" (Registro 20/10/2026; texto inteiro na ficha [2.2](../itens/2.2.md)).

## De onde veio (fontes)

- Estudo do "Para revisar" (06/10/2026): `relatorios/revisar-decisoes/rodada-3/scripts/comum.py`, `EXTRAS["pesel_p021"] = ("POINTS*.pdf", 21)`.
- [plano, Registro 13/10/2026 e 19/10/2026](../../docs/plano/PLANO-DEFINITIVO.md); [histórico, PARTE -15 §4 e PARTE -16 §4](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md).

- [PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) e Registro 20/10/2026 (ver [2.2](../itens/2.2.md), [2.13](../itens/2.13.md)).
