# Antiphonal — página 46 do PDF

- Livro: [antiphonal](../livros/antiphonal.md) (Antiphonal 1547) · gabarito: não (89 páginas, rodada 3, id `antiphonal1547_p046`) · imagem: não está em `gabarito/paginas/`; print `ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/img/tela-engana-1-comparacao.jpg`.
- Música impressa em vermelho e preto, com a **letra T vermelha grande** ("Tunc invoca") e a palavra "sabbato". Página pequena (741 × 1079 pontos a 300 DPI). Gira 1,50°.

## O que ela tem de difícil

- No "Só as letras" de fábrica ("Guardar a tinta forte") a letra T vermelha some (o vermelho vira cinza claro).
- **A tela mostra o que o PDF não tem:** na prévia (110 DPI) a T fica inteira; no PDF (300 DPI) mais da metade some. Causa: na imagem pequena os pedaços da letra se juntam e o corte fica mais frouxo (76 em vez de 45).
- A medida da regra no livro novo ficou no fio (1,43 contra o limite 1,5) até o reacerto dos limites.

## Itens que a usam

- [Para revisar](../itens/para-revisar.md): "Letra grande que some (Antiphonal 46): botão 'Trazer de volta nesta página' e o lugar onde sumiu já aparece marcado".
- [1.4](../itens/1.4.md): reconhecer melhor a tinta colorida.

## O que já se viu nela, rodada a rodada

- 07/10/2026 → rodada 3: vai para revisar (veredito do agente: errada, a T sumiu). Samuel concordou.
- 09/10/2026 → rodada 5 (`rv5-erro-1-desenho`): botão "Trazer de volta" com o lugar marcado.
- 13/10/2026 → implementador: com o preparo do livro novo a T fica em 1,43 (limite 1,5); com os limites reacertados ela volta a ir. `conferir_na_tela.py` testou aviso, marca e "Trazer de volta" nela. `ramo fase2-para-revisar: relatorios/para-revisar-impl/ONDE-PAREI.md`
- 13/10/2026 → verificador: bug grave "a tela mostra o que o PDF não tem" (a T inteira na tela, sumida no PDF; já era assim antes). [plano, Lista de bugs 13/10/2026](../../docs/plano/PLANO-DEFINITIVO.md)
- 13/10/2026 → G6: igual.
- 20/10/2026 → hoje: pergunta ao Samuel pendente na conferência do "Para revisar" (`pergunta_tela_igual_ao_pdf`), aba 4 a montar (`ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/ONDE-PAREI.md`).

## O que o Samuel disse

- 07/10/2026, rodada 3, "Concordo": "nos dois jeitos vai para revisar , porque o preto e branco e o jeito de fabrica borraram a palavra sabbato" ([rodada 3](../../relatorios/revisar-decisoes/rodada-3/respostas-samuel.md)).
- 09/10/2026, rodada 5: "eu acho que pode ser a opção 1, mas onde sumiu, tem que aparecer selecionado automaticamente, como na opção 3" ([rodada 5](../../relatorios/revisar-decisoes/rodada-5/respostas-samuel.md)).

## De onde veio (fontes)

- Rodada 3 do "Para revisar" (06/10/2026), livro de `D:\Livros para editar` ([rodada 3, LEIA-ME](../../relatorios/revisar-decisoes/rodada-3/LEIA-ME.md)).
- [histórico, PARTE -15 §6](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md).
