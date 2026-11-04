# D-614: a prévia do Dividir no Automático, como se já tivesse dividido (04/11/2026)

Ramo `previa-dividida-2026-11-04` (saiu de `obra-2026-10-26`, `ad563c35`). Pronto para conferir; não juntado.

## O que o Samuel pediu

Print a-60: "o dividir folha está escolhido era para aparecer uma folha divida ali né, e não duas folhas coladas,
está errado" · "era para eu ter um preview de como vai ficar a folha separada" · "é para aparecer como se já tivesse
sido feita a separação" · "você já sabe como é".

## O que mudou

Na janela grande do Automático, com "1 Dividir" marcado, o "depois" mostra **uma página por vez**, cortada na
linha, como a área de trabalho no Dividir com "Uma página" (D-601):

- na página 68 do Gradus, o depois é a página 128 (a metade da esquerda);
- ">" mostra a 129 (a outra metade da mesma folha), sem conta nova (0,05 s);
- ">" de novo vai para a folha 69; "<" volta pelo mesmo caminho;
- o contador continua "página 68 de 70" nas duas metades, como o rodapé da área de trabalho continua
  "folha 68 de 70" (D-601);
- o "antes" continua a folha inteira crua; a linha, a bolinha, o zoom, a tela cheia e o comparar continuam;
  a tela cheia e o comparar mostram a mesma metade;
- sem o Dividir marcado, nada muda; folha já dividida também não muda.

Arquivos: `ui/automatico.py` (PaginaAntesEDepois: os passos das setas, a metade da vez, a escolha da imagem;
o lado do comparar segue a metade), `ui/tarefas.py` (a conta diz a metade de cada imagem).

## Prints (Gradus Primus, cópia do projeto, janela de verdade)

Em `relatorios/previa-dividida/prints/`:

| print | o que mostra |
|---|---|
| 01 | sem etapa marcada: o depois é a folha inteira |
| 02 | Dividir marcado, linha no meio |
| 03 | Dividir marcado, linha toda para a direita: só a página 128 |
| 04 | ">" : a página 129 (a outra metade) |
| 05 | ">" : a folha 69, metade da esquerda ("página 69 de 70") |
| 07, 08 | o comparar: à direita a metade (128, depois 129) |
| 09 | Dividir desmarcado: a folha inteira de novo |
| 10, 11 | Limpar em Preto e branco; com o Dividir junto, a metade em Preto e branco |
| 12 | Dividir + Margens iguais (a metade com as margens) |
| 13 | etapa 7 aberta: "Folha 1 de 35" |
| 14 | depois do "Rodar" com o Dividir: o livro com 140 páginas, a página 135 é a 128 |
| 15, 16 | a tela cheia: metade da esquerda e da direita (print pelo próprio Qt; o do Windows sai branco nessa janela fora da tela) |

## Como cumpri cada decisão

- **D-614**: prova `tests/test_decisoes_previa_dividida.py` (4). No código de antes, 3 falham; a da folha já
  dividida passa nos dois, de propósito. A metade é igual, ponto por ponto, à que o "Rodar" desenha. Prints 02 a 08, 15 e 16.
- **D-577** (o resto): as 22 provas passam. Quatro delas pediam as duas metades lado a lado; só essa conferência
  foi trocada por "uma metade", com autorização da gerente (04/11), e cada uma ganhou um comentário da D-614.
  O resto de cada uma (o antes inteiro, o Cortar, desmarcar volta) ficou igual.
- **D-601**: as setas andam pelas páginas e o contador não muda nas duas metades, como na área de trabalho.
- **D-603**: etapa 7 com o Dividir: "Folha 1 de 35" (print 13; provas do caderno passam, inclusive a do Gradus).
- **D-589 / D-590**: desmarcar o Dividir volta a folha inteira (print 09); as provas da caixinha passam.
- **D-004 / D-607**: a prévia não pula as páginas mexidas; o "Rodar" perguntou ("70 páginas foram juntadas no
  Dividir e vão ser separadas...") e, com "Rodar nelas também", dividiu as 70 folhas (print 14).

## Velocidade (Gradus, página 68, 9 rodadas alternadas)

- ir à página: antes 0,21 a 0,32 s; agora 0,22 a 0,31 s (igual);
- marcar o Dividir até o depois chegar: antes 0,70 a 0,99 s; agora 0,75 a 0,95 s (igual);
- ">" para a outra metade: 0,05 a 0,07 s.

## Ressalvas

1. **A linha no meio.** Pela regra da D-577 (à esquerda da linha o depois, à direita o antes), com a linha no meio
   a metade (no meio da tela) fica ao lado da metade direita da folha crua: de relance parece a folha inteira de
   novo, e na metade da direita o mesmo texto aparece duas vezes (prints 02, 15 e 16). Com a linha toda para a
   direita, só a página (print 03). Não mudei: é a regra da linha e o jeito de pôr páginas de tamanhos
   diferentes no meio. Pode ser assunto para perguntar ao Samuel.
2. **Comparar com o Dividir só num lado.** Se só um lado do comparar tem o Dividir marcado, esse lado mostra a
   metade da esquerda (o folhear é o da janela). Ficou assim, como a gerente mandou.

## Testes

- GitHub, "Testes no Windows", rodada 41862922577 (ramo no commit `ce734945`): **passou** (as 5 partes da suíte, a
  velocidade e o resumo).
- No PC, as 31 `tests/test_decisoes*.py`, um arquivo por vez: todas passam (1 pulada em `test_decisoes_livreto_ver`,
  por falta de livro no PC). Também: `test_caderno_segue_as_etapas` (11), `test_zoom_no_ponteiro` (5),
  `test_dividir_desmarcada_caixinha` (3), `test_automatico_pular_depois_de_dividir` (4).
- Teste antigo mudado: só as 4 conferências "lado a lado" da D-577, com autorização da gerente.

No PC, um arquivo por vez: ver `ONDE-PAREI.md`.
