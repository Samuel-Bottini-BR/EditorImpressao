# Rodada 5: as três perguntas confusas refeitas, e respostas aos comentários da rodada 4

08/10/2026 · agente das decisões do "Para revisar". Nada do programa foi mudado e nada rodou o programa de
novo: as imagens saem dos dados da rodada 4 (`fase-1` de hoje, em
`D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\dados4`) e, para o "Guardar só o texto" do
Graduale 222, da rodada 3 (`...\dados`; o conserto do desenho não mexe nesse jeito).

As respostas literais da rodada 4 estão em `../rodada-4/respostas-samuel.md`; os pedidos de funcionalidade que
saíram delas, em `../rodada-4/pedidos-funcionalidade.md`.

## As perguntas (`rodada-5-perguntas.json`, 10)

| # | id | O que é |
|---|---|---|
| 1 | rv5-erro-1-desenho | Refeita: some uma letra grande; o que o aviso oferece (botão / o programa traz sozinho / marcar à mão) |
| 2 | rv5-erro-5-sem-conteudo | Refeita: página sem conteúdo; que botões o aviso mostra |
| 3 | rv5-erro-6-so-texto | Refeita: no "Guardar só o texto" some a música; o que o aviso oferece |
| 4 | rv5-erro-2-gravura | Detector de figuras mais certeiro: estudar agora ou seguir o plano (1.5, 2.18) |
| 5 | rv5-erro-4-tintas | Reconhecer melhor a tinta: adiantar o item 1.4 ou seguir com a força sozinha |
| 6 | rv5-conserto-gravura | O delineado: como aumentar ou diminuir a área (quadradinhos / pincel) |
| 7 | rv5-conserto-faixa | O corte da borda preta: botões rápidos do seletor de páginas |
| 8 | rv5-aviso-so-texto | Avisos por página/motivo/todos; o que a janela "Antes de processar" mostra |
| 9 | rv5-em-branco | Um aviso para cada coisa, dois botões separados: fica assim? |
| 10 | rv5-pag-egenloff-047 | Tarja e moldura: cortar fora ou pintar de branco |

Todas respondem a um comentário: começam com "RESPOSTA AO SEU COMENTÁRIO:" e trazem `historico` com a cadeia
(rodada 3 e rodada 4), com a hora lida do banco.

**Imagem por opção:** nas três refeitas, e onde há escolha visual, cada opção tem `imgs: [{src, legenda}]`.
A página, na versão lida em 08/10, não mostra `opcoes[].imgs`; por isso as mesmas imagens também estão em
`exemplos`, na ordem das opções, com o nome da opção na legenda. Se a gerente fizer a página mostrar as imagens
das opções, dá para tirar as repetidas de `exemplos`.

## Imagens (`img\`, 19; fora do git)

- Novas (`r5-*`): o que acontece em cada caso (Antiphonal 46, Egenloff 12, Graduale 222) e uma imagem por opção.
  Os avisos, o seletor e os botões são **desenhos da proposta**: a legenda diz isso, e a aparência fica com o
  agente de layout. Os quadros "simulação" foram feitos colando, numa cópia, o resultado de outro jeito do
  programa dentro de um retângulo (o que a marcação faria) ou cortando pela beirada do papel claro (Egenloff 47).
- Da rodada 4 (copiadas): `faixa-cortes`, `gravura-delineado-1`, `c4-texto-camoes027`, `p-egenloff-003`.
- Abri todas; corrigi o retângulo da letra T (estava fora da letra), o rótulo pequeno do Graduale e a cor do
  pincel "tirar" (vermelho, não azul).

## Fatos do código usados nas respostas

- A janela "Antes de processar" já existe (`ui/tela_conferir.py`, `_pedir_processamento`).
- O aviso do "Só as letras" é refeito a cada desenho da página e sai quando o motivo some
  (`core/pipeline.py`, `_anotar_tinta_forte_fora` e `_acertar_alerta_do_misto`); editar a página pelas abas
  (corte, ângulo, filtro) já a marca como conferida (`revisada: True`).
- Na aba Bordas, o corte feito à mão fica só naquela página; "usar em todas" (`_recorte_em_todas`) copia para
  todas e apaga as exceções.

## Para refazer

De dentro de `scripts\`, com o Python do projeto: `figuras5.py`, depois `perguntas5.py`. `comum.py` e
`desenho.py` são cópias da rodada 4 (nada aqui roda o programa).
