# Item 2.9 (letra clara em fundo escuro) - verificador, onde parei (21/10/2026)

Ramo `fase2-scantailor-itens-2026-10-19`, código `0f4ee58` (worktree `v29-novo`, ramo meu `verif-2.9-2026-10-21`).
REFEITO (21/10) no 839bf1f: cartões consertados (e49463c), veredito PRONTO PARA CONFERIR; conferencia-2.9.json atualizado.

Feito:
- Fábrica igual: `scripts/rodar_somas.sh` (32 páginas x Original, PB, Melhorar, PB com "Só as letras"): **128 de 128 iguais**
  ao `b8e9af7` (o lado antigo é o que medi no 2.8).
- Código: inverter na entrada e na saída bate com o ScanTailor (`OutputGenerator.cpp` 1245-1249, 1344-1346, 1370-1372,
  1497-1499, conferido no arquivo de referência). Testes do implementador: 13 passaram.
- Janela (Horas 186-188, programa de verdade): a caixinha aparece no AJUSTE; marcar grava ação do desfazer; o cartão do
  filtro escolhido inverte; o PDF gerado sai com letra branca em fundo preto (`trabalho/pdf-p2-titulo.png`).
- **ACHADO:** os OUTROS cartões ("A mesma página nos quatro filtros") não seguem a caixinha: com ela marcada e o
  filtro em Preto e branco, o cartão Melhorar mostra a lombada sem inverter; ao clicar nele a página sai preta
  (`trabalho/c03-*.png` e `c04-*.png`). Causa: `ui/tarefas.py` `_TarefaCartoes.run` chama `aplicar_filtro` direto.
- Procura minha (`scripts/procurar.py`, ~240 livros em D:\Livros para editar e TESTES): páginas de verdade melhores que a
  lombada: a capa do "História do Direito Político Brasileiro" e slides do "PARTE 4 - O MEIO AMBIENTE" (paragrafos
  brancos em fundo escuro). Antes/depois meu: `scripts/antes_depois.py` -> `img/29-*.jpg` (abertas: capa e Horas;
  falta abrir `29-slide.jpg` de novo depois do conserto de cor e `29-horas-187.jpg`, `29-slide-perto.jpg`).

Falta: abrir as imagens que faltam; terminar a procura (rodando em segundo plano: `trabalho/procura.log`);
conferência em fotos para o Samuel (`conferencia-2.9.json`) e o parecer (`2.9-verificado.*`).
