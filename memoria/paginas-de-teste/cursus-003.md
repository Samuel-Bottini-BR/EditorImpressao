# Cursus — página 3 do PDF

- Livro: [cursus](../livros/cursus.md) · gabarito: não (está nas 89 páginas do estudo do "Para revisar", id `cursus_p003`) · imagem: não está em `gabarito/paginas/`; a página sai do livro na hora (ver "De onde veio"). Imagens prontas: `ramo verif-corte-g6-2026-10-13: relatorios/conferir/corte-g6-2026-10-13/img/lado-cursus_p003__inteira.jpg` e `.../img/causa-cursus_p003__inteira.jpg` (fora do git, só no disco da worktree).
- Página de microfilme, texto denso, com **borda preta do scanner** dos dois lados e capitular xilográfica. Gira -0,69° no endireitar.

## O que ela tem de difícil

- É a página do achado do defeito do G6 (endireitar antes de cortar): com a ordem nova, sobra uma **faixa preta larga** à direita (1,6 cm) e embaixo (0,6 cm) que a ordem antiga cortava. Faixa escura na beirada: 0,5% (ordem antiga) → 7,5% (ordem nova).
- Causa: o giro pinta de branco as cunhas das beiradas e esse branco esconde a borda preta da busca do corte (`core/recortar.py`, `_apagar_bordas_solidas`).
- Risco à parte: com a faixa contando como tinta, linhas de texto são apagadas da conta como "risca de dobra" (`_apagar_riscas_de_dobra`). Não cortou texto nesta página.
- No "Só o texto achado" a capitular xilográfica e o "AD" do título somem.
- O verificador sugeriu incluí-la no gabarito do corte (ainda não está na `lista.json`).

## Itens que a usam

- [2.2 Endireitar / G6](../itens/2.2.md): página que mostrou o defeito do corte na ordem nova.
- [2.13 Borda preta](../itens/2.13.md): a faixa preta do scanner só some de vez com a busca da página/caixa do conteúdo.
- [Para revisar](../itens/para-revisar.md): o aviso "Faixa escura na beirada" pegou esta página.

## O que já se viu nela, rodada a rodada

- 06/10/2026 → estudo do "Para revisar": "Guardar a tinta forte" certa; "Só o texto achado" errada (capitular e "AD" somem); o aviso de hoje mandava para revisar (17%). [estudo](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md)
- 13/10/2026 → verificador do "Para revisar" achou a faixa preta larga à direita no livro novo (Lista de bugs, "entrou no programa com o G6 em 12/10"). Print: `ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/img/cursus-3-1-pagina-recorte.jpg`. [plano, Lista de bugs 13/10/2026](../../docs/plano/PLANO-DEFINITIVO.md)
- 13/10/2026 → investigação do corte nas 89 páginas: **PIOROU** (faixa 0,5% → 7,5%; folha 201 × 268 → 212 × 279 mm). `ramo verif-corte-g6-2026-10-13: relatorios/conferir/corte-g6-2026-10-13/corte-g6.md`
- 13/10/2026 → conserto no ramo `conserto-corte-g6-2026-10-13` (`d97b937`): preto na beirada 0,4 mm (antes do G6) → 14,9 mm (G6) → 1,5 mm (conserto); faixa 1,0%. Ressalva: sobra um fio de até 4 mm. [plano, Registro 13/10/2026](../../docs/plano/PLANO-DEFINITIVO.md)
- 13/10/2026 → Samuel marcou o quadro `cg6-cursus-3` como "Está pior" (ver abaixo).
- 20/10/2026 → hoje: o defeito do G6 continua no `fase-1` (livro novo). O conserto continua no ramo, não juntado; o implementador está acertando o Pesel 21 no mesmo ramo (`ramo conserto-corte-g6-2026-10-13: relatorios/conserto-corte-g6/ONDE-PAREI.md`, "EM ANDAMENTO"). O verificador do "Para revisar" tem esta página na lista para reabrir na janela (`ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/ONDE-PAREI.md`).

## O que o Samuel disse

- 13/10/2026, quadro `cg6-cursus-3`, "Está pior": "como vamos resolver isso dentro do programa então?" ([conferência 13/10/2026](../../relatorios/conferencia-samuel-2026-10-13.md))

## De onde veio (fontes)

- Escolhida olhando miniaturas para o estudo do "Para revisar" (06/10/2026): `relatorios/revisar-decisoes/rodada-3/scripts/comum.py`, `EXTRAS["cursus_p003"] = ("Cursus philosophicus*.pdf", 3)`.
- Livro copiado em 05/10/2026 para o acervo de testes como livro de borda preta (`LEIA-ME borda preta (05-10-2026).txt`).
- [plano, Lista de bugs e Registro 13/10/2026](../../docs/plano/PLANO-DEFINITIVO.md); [histórico, PARTE -15 §5](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) ("Incluir no gabarito do corte: Cursus 3, Matemática 32, Antiphon 260, Escola 197").
