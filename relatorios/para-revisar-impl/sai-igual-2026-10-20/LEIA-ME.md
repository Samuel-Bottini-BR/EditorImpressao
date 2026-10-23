# Livro já começado sai igual ao fase-1 (20/10/2026)

Teste de máquina, implementador. Roteiro: `../sai_igual_projeto_antigo.py`.

**O que foi feito:** as 32 páginas-gabarito, em dois jeitos ("pb_letras" = Preto e branco com "Só as letras";
"magico_pro"), foram analisadas pelo programa do `fase-1` (`b6fd091`) e gravadas como projeto (o mesmo JSON do
projeto.json, sem nenhum campo do "Para revisar"). Cada projeto foi aberto e processado até o PDF duas vezes: com o
`fase-1` e com o ramo juntado (`adf4e69`). De cada página do PDF, a soma sha256 dos pontos.

**Resultado:** 64 de 64 iguais.
- Na primeira passada, 63 de 64 iguais (`somas-fase1.json` × `somas-ramo.json`). A que diferia, Horas p. 11 em
  Mágico pro, foi repetida quatro vezes, alternando (fase-1, ramo, fase-1, ramo): as quatro deram a mesma soma
  (`b85e5b05…`), que é a do ramo. A soma diferente era do próprio `fase-1`, na passada longa (que teve três paradas
  por falta de memória no PC e foi retomada). Ver `horas-p011-repeticao-*.json`.
- Em todas, o projeto aberto pelo ramo ficou com a força do preto sozinha desligada (`reforcar_texto_falhado`
  falso) e a força do preto de cada página igual à do fase-1.

**Ressalvas:** o programa do `fase-1` deu, uma vez, uma soma diferente para a mesma página (Horas 11, Mágico pro):
há alguma coisa que não sai igual de uma execução para outra, nos dois códigos; não investiguei. Só as
páginas-gabarito, um livro de uma página por vez; não abri as imagens (é prova por soma). O PC ficou sem memória três
vezes no meio (outros agentes trabalhando); as páginas que falharam foram refeitas.
