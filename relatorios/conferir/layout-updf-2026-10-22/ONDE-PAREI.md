# Onde parei: verificador do livro aberto (UPDF) e da tela cheia (22/10/2026)

- Conferido: ramo `layout-etapas4a7-2026-10-19`, commit `7843503` (o último código é o `b496573`; o `7843503` só muda o ONDE-PAREI).
- GitHub 39797331030 testou o `b496573`: 130 arquivos, 2194 passaram, 0 falharam, 73 pulados; teste_botoes 216 ações, 0 falhas. Vale para o commit final.
- Reversão: `tests/test_livro_aberto.py` no `2eeec20`: 8 falham, 5 passam (par 562 x 510 px; livro aberto nitidez 0,33; grade 0,62/0,67); no novo 13 passam.
  `tests/test_filtros_tela_cheia.py` no `d285b48`: 5 falham, 6 passam; no novo 11 passam.
- Janela de verdade: `scripts/vlu_livro.py` (18 de 18; no código antigo 4 de 4) e `scripts/vlu_tela_cheia.py` (10 de 11; a falha é o cartão do Mágico pro cortado em 1600x821). Medidas em `medidas/`.
- `scripts/vlu_dpi.py`: tinta a 150 x 300 DPI por jeito do Preto e branco (a ressalva principal).
- Conferência: `conferencia.json` + `img/` (montados por `scripts/vlu_imagens.py` e `scripts/montar_conferencia.py`). Os PNG brutos ficam em `prints/` (fora do git).
- Situação: entregue à gerente. PRONTO PARA CONFERIR, com ressalvas.
