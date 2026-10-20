# Conserto do corte com borda preta: acerto do Pesel 21 (implementador, 20/10/2026)

**PRONTO PARA CONFERIR** (o verificador confere; nada aprovado). Ramo `conserto-corte-g6-2026-10-13`.

## Em uma frase

O Pesel 21 voltou a sair exatamente como no `fase-1` (folha inteira, 15,7 × 24,1 cm, idêntico ponto por ponto), e as
cinco melhorias do conserto de 13/10 continuam exatamente iguais.

## O que estava errado

O corte primeiro pergunta "há o que recortar nesta página?". O cartão pardo do livro de bordados da Pesel responde
"não" (é como uma capa: só o cartão e o tecido), e a folha sai inteira. No livro novo a pergunta era feita na página já
endireitada, e o branco que o giro põe nos cantos mudava a conta (a mediana do cinza pulava do cartão para o tecido:
102 → 125). Até 12/10 o erro ficava escondido por outro efeito do mesmo branco, que segurava o corte na folha
inteira; o conserto de 13/10 tirou esse efeito e o Pesel 21 passou a ser cortado rente.

## O que mudou

- `core/recortar.py`: `detectar_bordas` ganhou `como_veio` (a página antes do giro). Com ele, a pergunta "há o que
  recortar?" é feita na página como veio, a mesma resposta da ordem antiga. Comentário novo no bloco "A cunha do
  giro" (caminho 4). Sem `girada` nada muda (projeto antigo idêntico).
- `core/pipeline.py`: só a chamada passa `como_veio=em_cinza()`.
- Tentado e descartado: fazer a pergunta na página girada sem contar os pontos do branco do giro. Acerta o Pesel 21
  real, mas não a página de teste a 2°: os cantos do cartão que o giro leva embora também mudam a mediana.
- Custo: nenhum a mais. A conta (11 a 15 ms numa página de 300 DPI) já era feita, só que na página girada; agora é
  feita na página antes do giro, que tem o mesmo tamanho.

## Teste de reversão (CLAUDE.md §4.7)

- `test_cartao_escuro_sai_inteiro_no_livro_novo` (3 ângulos; página de mentira que imita o Pesel 21; roda no GitHub).
  Medida: tamanho da página pronta em mm, livro novo contra a ordem antiga (no máximo 1 mm de diferença).
- `test_pesel_21_sai_como_no_fase_1` (a página de verdade; só no PC do Samuel, pula no GitHub). Medida: 157 × 241 mm.
- No código antigo (o `core/` do `d97b937`) os quatro **falharam**: 105 × 171 mm contra 148 × 210 mm nos três de
  mentira; 144,7 × 206,1 mm no Pesel 21 (`relatorios/conserto-corte-g6/pesel21/reversao-no-codigo-antigo.txt`).
  No novo, passam. `tests/test_ordem_do_preparo.py` inteiro: 56 passaram, entre eles os 6 de página torta com borda
  preta.

## As 89 páginas (livro novo, 300 DPI, sem filtro; `comparacao-pesel21.json`)

- Contra o `d97b937`: **muda só o Pesel 21**. As outras 88 saem idênticas ponto por ponto.
- Contra o `fase-1`: mudam 9, as mesmas 9 do conserto de 13/10 (sem o Pesel 21), idênticas ponto por ponto ao
  `d97b937`.
- Projeto antigo: **40 de 40 idênticos** ponto por ponto.

| Página | fase-1 | d97b937 | agora | igual ao fase-1? | igual ao d97b937? |
|---|---|---|---|---|---|
| Pesel 21 | 15,7 × 24,1 | 14,5 × 20,6 | 15,7 × 24,1 | sim | não |
| Cursus 3 | 21,2 × 27,9 | 19,8 × 27,8 | 19,8 × 27,8 | não | sim |
| Matemática 32 | 20,9 × 29,0 | 16,7 × 29,0 | 16,7 × 29,0 | não | sim |
| Antiphon 260 | 46,3 × 61,8 | 46,3 × 59,1 | 46,3 × 59,1 | não | sim |
| Antiphon 88 | 45,6 × 62,4 | 43,1 × 62,3 | 43,1 × 62,3 | não | sim |
| Camões 104 | 9,5 × 13,1 | 9,3 × 13,1 | 9,3 × 13,1 | não | sim |
| Camões 66 | 9,2 × 13,0 | 9,2 × 13,0 | 9,2 × 13,0 | não | sim |
| Antiphonal 252 | 6,5 × 10,0 | 6,5 × 9,9 | 6,5 × 9,9 | não | sim |
| Egenloff 3 | 33,8 × 45,4 | 33,8 × 45,4 | 33,8 × 45,4 | não | sim |
| Rariora 155 | 13,3 × 11,3 | 13,3 × 11,3 | 13,3 × 11,3 | não | sim |

## Imagens (abertas uma a uma)

`img/tres-<página>.jpg`: fase-1 | d97b937 | agora, na mesma escala; `img/perto-pesel_p021__inteira.jpg`: o pé do Pesel
21 de perto. O git guarda só este `.md`; as imagens se refazem com
`relatorios/conserto-corte-g6/scripts/montar_pesel21.py`.

- Pesel 21: agora igual ao fase-1; a legenda volta a ter uns 3 cm de cartão embaixo. Os cantos brancos do giro
  continuam como no fase-1 (é o defeito já anotado das cunhas brancas quando o corte vai até a beirada).
- As outras nove: a terceira coluna é igual à segunda, como o md5 diz.

## Os comentários do Samuel de 13/10 (só registro; a borda preta inteira é o item 2.13)

- Antiphon 260 ("Mas sobrou preto embaixo.") e Antiphon 88 ("mas ainda sobrou preto embaixo."): continuam como no
  `d97b937`: a tira preta de baixo do 260 (uns 2 cm, a mesma de antes do G6) e a do 88 seguem lá. Não mexi.
- Cursus 3 (fio de até 4 mm à direita): continua igual ao `d97b937`. Não mexi.

## Ressalvas

- O "sem conteúdo" do Pesel 21 é por pouco: 2,1% de pontos escuros contra o limite de 3% (regra de
  `core/detectar_regioes`, a mesma de sempre). Outro cartão do mesmo livro pode cair do outro lado, nas duas ordens
  iguais. Não é deste conserto.
- O teste da página de verdade só roda no PC do Samuel; no GitHub quem cobre é a página de mentira.
- 89 páginas soltas, nenhum livro inteiro; nada visto na janela do programa.

## Suíte no Windows do GitHub

Rodada 39396681554 (o ramo em `bd193d4`; o código de `core/` e `tests/` é o de agora): **passou**. 114 arquivos, 2061 passaram,
0 falharam, 0 erros, 73 pulados (entre eles o teste do Pesel 21 de verdade, que só roda no PC); botões e prints da
janela real: passou.
