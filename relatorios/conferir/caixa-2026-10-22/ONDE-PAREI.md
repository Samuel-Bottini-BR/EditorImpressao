# Conferência da caixa do conteúdo (2.5, 2.13, 2.14) — verificador, 22/10/2026 — ONDE PAREI

**PAUSADO a pedido do Samuel (via gerente), 22/10/2026.** Nenhuma janela do programa foi aberta; nenhum processo ficou rodando.
Nenhuma rodada do GitHub foi disparada por mim.

Código conferido: ramo `fase2-caixa-conteudo` em `49d1ed3` (o último código é `5bc5b33`; `4b37fc0` e `49d1ed3` só têm
imagens e ONDE-PAREI). "Antes" = `c66f28d`. Meu ramo: `verif-caixa-2026-10-22` (sai de `49d1ed3`).

Worktrees (com junções `modelos` e `gabarito\paginas`; **não apagar com Remove-Item -Recurse**):
`.claude/worktrees/vcx22-novo` (meu ramo), `vcx22-antes` (`c66f28d`), `vcx22-04b` (`04bcda2`).

## Já conferido (máquina)

| O quê | Resultado |
|---|---|
| GitHub 39788341137 (vale para `5bc5b33`, o código não mudou depois) | **2234 passaram, 0 falharam, 104 pulados**, 123 arquivos; botões e prints verdes. Filtro de velocidade 39788346337 (`c66f28d` x `5bc5b33`, opções desligadas): "igual (dentro do vai-e-vem)" |
| Reversão da etiqueta (`test_regressao_egenloff3_...`) | passa no novo; **falha no `c66f28d`**: corte termina em y 4683, no meio da etiqueta (4431–4807) |
| Reversão da passada (`test_regressao_a_passada_guarda_a_geometria_...`) | passa no novo; **falha no `04bcda2`** (geometria não guardada) |
| `tests/test_borda_preta.py` no novo | 29 passaram |
| "Só o preto" antes x depois em páginas de verdade a 300 DPI (14 Egenloff + 25 Marial, cor e cinza; `scripts/so_o_preto_igual.py`) | **0 diferenças em 78 contas**; 33,9 s → 8,8 s (**3,9×**; o implementador mediu 4,6×) |
| Velocidade no PC, alternado, um processo por vez, sem outros python rodando (`scripts/rodar_tempos.sh`, `tempo_total.py`; duas opções ligadas, até a moldura, Original, 300 DPI; passada + geração do PDF) | **Egenloff 14:** antes 118,1 e 85,6 s → depois 47,4 e 30,7 s. **Marial 100:** antes 312,7 e 307,3 s → depois 145,1 e 138,8 s (**~2,2× mais rápido**; passada 129 → 94–96 s, geração 178–183 → 45–49 s). Números em `dados/tempo_*.json` |
| PDFs antes x depois (`scripts/comparar_pdfs.py`) | tamanhos iguais nos dois (Egenloff miolo 252,5 x 379 mm; Marial 224 x 302,7 mm). **Egenloff: mudaram as págs. 3 e 12. Marial: mudaram 32 de 100** (4, 6, 7, 8, 16, 22, 23, 25, 28, 30, 32, 33, 36, 37, 40, 43, 45, 47, 50, 51, 64, 66, 71, 75, 78, 85, 86, 87, 88, 95, 96, 99 — contando de 1). Confirma o número do implementador |
| Aviso novo no Marial | a página que ganhou "Corte deixou algo de fora" é a **8 contando de 1** (o implementador escreveu "p. 7": provavelmente contou de 0; conferir na janela) |

## Achado que vira ressalva / pergunta (ainda sem imagem)

**O aviso "Corte deixou algo de fora" aparece em quase todas as páginas, antes e depois:** Marial 82 de 100
(depois; 81 antes), Egenloff 12 de 14. Com tanto aviso o Kaique não vai saber quais páginas olhar. Falta ver
nas imagens **o que** está ficando de fora em páginas comuns (anotações de margem? sujeira? sombra da lombada?)
antes de escrever a pergunta ao Samuel. Páginas sem mudança mas com aviso já capturadas: 2, 10, 50.

## O que falta, passo a passo

1. Conferir que a captura bate com o PDF: `trabalho/cap_<livro>_<lado>_pNNN_saida.png` contra a página do
   `trabalho/saida_<livro>_<lado>.pdf` (antes, a captura do `c66f28d` foi refeita com `_guardar_geometria`, como a
   geração do PDF faz; Egenloff 3 antes deu 849,207–3832,4683, igual ao do implementador).
   As capturas (`capturar_corte.py`) já estão feitas para Egenloff 2, 3, 6, 12 e Marial 2, 4, 6, 7, 8, 10 e as 32
   que mudaram, nos dois lados (pastas `trabalho/`, fora do git; caixas em `dados/cap_*_info.json`).
2. Desenhar as fotos: `scripts/desenhar.py trabalho <egenloff|marial> <pág> "<título>" "<caminho e opções>" img/<nome>`
   (dá `__perto.jpg` e `__inteira.jpg`; preto = fica, vermelho = tirado, amarelo = parte ampliada). Fazer para
   Egenloff 3 e 12 e para as 32 do Marial; abrir TODAS (folha de contato se preciso) e escrever uma linha por página.
3. Ver as páginas com aviso sem mudança (Marial 2, 10, 50; Egenloff 2, 6) para entender o excesso de avisos.
4. Janela de verdade: `scripts/janela.py <pdf> <rótulo> <págs>` (piloto copiado do verificador de 13/10:
   `piloto.py`, `g.py`, `v.py`, `lancador2.py`; janela fora da tela, mensagens nativas). Rodar no Marial 100
   (págs. 7, 8) e no Egenloff 1-14 (pág. 3): print do corte e do aviso, contador de avisos, erros.log. Fechar com WM_CLOSE.
5. Montar `conferencia.json` (formato da Central, ver pedido da gerente) com os quadros cx-etiqueta (Egenloff 3),
   cx-marial (o corte que andou; p. 8 com o aviso), cx-velocidade (números acima), cx-avisos-demais (ressalva) e,
   se for o caso, pergunta extra sobre o excesso de avisos; manter as ressalvas: carimbos do Egenloff 3 continuam
   partidos (o oval de cima e o "Fachschule" da direita; o lápis "Af 10" some), pergunta do carimbo aberta.
6. Commit (`git add -f` nas imagens), push, ler o GitHub uma vez (só disparar se o código mudar), entregar à gerente.
