# Parecer do verificador: medidor de força nas páginas de letra grossa e Horas 11 mais rápida

Verificador, 02/10/2026, ramo `fase-1`. Commits conferidos: `bf9680f` (medidor) e `7f50e70` (Horas 11),
comparados com o commit de antes, `a10e592`, em duas cópias limpas do código.
Aqui só há **PRONTO PARA CONFERIR** ou **NÃO ESTÁ PRONTO** e a opinião; quem marca é o Samuel.

> **Defeito conhecido (decisão do Samuel, 28/09):** a moldura dourada e a iluminura ainda não saem
> como devem (itens 1.4 e 1.5, adiados). Nada disso mudou aqui.

## Em uma frase

- **`bf9680f`, o medidor "mais fraco / mais escuro" nas páginas de letra grossa: PRONTO PARA CONFERIR.**
  Agora ele anda sempre no mesmo sentido: subir o medidor nunca clareia nenhum ponto, em nenhuma das
  12 páginas que testei. No 0 a Horas 47 não picota mais (fica quase igual ao 50, só um pouco mais
  fina); no 100 as letras ficam inteiras e mais cheias, sem grudar. No 50, que é o normal, nada mudou.
- **`7f50e70`, a Horas 11 mais rápida no Preto e branco: PRONTO PARA CONFERIR, com uma ressalva.** A
  Horas 11 processa em ~11,8 s contra ~17,3 s antes, e as 96 imagens (32 páginas × 3 filtros) saem
  idênticas ponto a ponto. Ressalva: o atalho tem um ponto fraco teórico (folha com foto em retícula
  fina cobrindo quase tudo), que montei numa folha artificial e que **não aparece em nenhuma das 2903
  folhas do acervo nem nas 450 do Opus Majus**; nenhum teste o protege.

## Como foi conferido

**Por máquina:**

- **(a) As 32 páginas nos três filtros, medidor no 50:** rodei eu mesmo, pelo mesmo caminho do botão
  "Confirmar e processar", o código de antes (`a10e592`) e o de agora (`2ff2d90`, que tem os dois
  commits; depois deles só mudaram relatórios e o plano). **Preto e branco 32 de 32, Mágico pro 32 de
  32, Melhorar 32 de 32 idênticas ponto a ponto.** Sem janela e sem tocar na pasta de dados do Samuel.
- **(b) O medidor em 0, 25, 50, 75 e 100**, nas 12 páginas pedidas (Horas 11, 13, 14, 26, 27, 47;
  Graduale 221, 222, 223; Escola 7 e 35; Opus 20). Diferente do implementador, que testou só o filtro,
  **passei pelo caminho do programa inteiro** (análise, corte, endireitar, marcação de gravura e letra,
  filtro, PDF) mudando só o valor do medidor em cada página. O 50 dessa rodada é idêntico ao da rodada
  normal nas 12 páginas (a montagem é fiel).
  - **Nenhum ponto clareia ao subir o medidor, em nenhuma das 12 páginas** (0→25→50→75→100).
  - No código de antes, do 50 para o 100 clareavam 4 525 pontos na Horas 47, 11 759 no Graduale 221,
    401 na Escola 35 e 295 na Horas 13. Agora, 0.
  - No 50, as páginas saem idênticas às de antes.
  - Horas 26 e 27: o medidor faz exatamente o que fazia antes (são páginas de letra fina, em que o
    programa usa outro jeito de passar a preto e branco; o conserto não mexe nelas). Ver ressalva 2.
- **(c) Tempo da Horas 11**, pelo caminho do programa, alternando antes e agora 5 vezes (3 com o antes
  primeiro, 2 com o agora primeiro), com a Horas 47 junto para controle:

| Página | ANTES (5 voltas) | AGORA (5 voltas) |
|---|---|---|
| Horas 11 | 17,3 · 17,2 · 17,3 · 17,4 · 17,3 s | 14,7 · 13,5 · 11,4 · 11,8 · 11,8 s |
| Horas 47 (controle) | 10,2 · 9,6 · 9,3 · 9,1 · 8,8 s | 10,9 · 10,1 · 9,5 · 9,1 · 10,8 s |

  A Horas 11 ganha uns 5,5 s (mediana 17,3 → 11,8 s); as duas primeiras voltas de agora foram mais
  lentas porque o PC estava ocupado (o outro agente e as minhas rodadas). A Horas 47 oscila ±1 s
  entre voltas; medi só o filtro dela no 50, alternando 3 vezes, e deu igual (1,19 · 1,23 · 1,21 s
  agora, 1,22 · 1,17 · 1,22 s antes). Os números batem com os do implementador (16 → 11 s).
- **Testes:** `pytest tests -q` (sem janela), uma vez, no código de agora: **1369 passaram, 1 pulado,
  nenhum falhou** (12 min).
- **Risco do atalho da Horas 11 nos outros livros:** varri o acervo inteiro (9 livros, 2903 folhas, + as 450 do Opus Majus,
  3353 folhas ao todo) com a página como o programa a entrega ao filtro (dividida, cortada, endireitada). Ver
  a seção própria abaixo.

**Por olho:** abri as folhas de contato das 96 imagens (32 páginas × 3 filtros; nenhuma página
faltando, em branco ou estranha; são idênticas ponto a ponto às que o verificador da conferência 6
já olhou uma a uma). Abri, **em tamanho real**, os recortes das 12 páginas no medidor 0, 50 e 100
(com o Melhorar ao lado como referência do original, e o ANTES no 0 e no 100 na Horas 47, 13, Escola
35 e Graduale 221), e os recortes de onde aparecem pontinhos novos no 100 (Graduale 221 e 223,
Horas 27, 47, Escola 7, Opus 20). Abri também os cartões do implementador.

## O que vi no medidor, página por página (tamanho real)

| Página | No 0 ("mais fraco") | No 100 ("mais escuro") |
|---|---|---|
| Horas 47 | Quase igual ao 50, um fio mais fina; **não picota** ("amour propre", "JESUS", "nous" inteiros). No ANTES o 0 era a letra falhada recusada. | Mais cheia, "Prêchant" e "nous" inteiros (no ANTES falhavam); nada grudou, miolos de e/o/a abertos. |
| Horas 13 | Um pouco mais fina, legível ("Confession", "priere que Salomon"). | Mais encorpada, sem grudar. |
| Horas 14 | Números e letras da tabela um pouco mais finos ("Cendres" com o "n" um pouco aberto), legível. | Mais cheios; miolos de 6, 8, 9, a, e abertos. |
| Horas 11 | Igual ao 50 (o medidor quase não mexe nela). | Igual ao 50 a olho (+0,07% de tinta). |
| Graduale 221/222/223 | Praticamente igual ao 50. | Notas e letras góticas um pouco mais grossas; **os riscos finos da pauta (ponta seca) e o pontilhado da margem ficam mais visíveis, como tracinhos** (ver ressalva 3). |
| Escola 7 e 35 | Letra um pouco mais fina, limpa. | Um pouco mais encorpada; dois ou três pontinhos novos minúsculos perto do texto na Escola 7. |
| Opus 20 | Legenda igual ao 50 ("ROGER BACON" com o E e o A falhados, como já era). | "ROGER BACON" sai inteiro; a foto não muda. |
| Horas 26 e 27 | **A letra sai bem falhada** ("S. Silveftre Evêque", "La Prefentation"), muito mais que no 50 (tinta 6,8% → 3,8%). **É igual ao que já era antes** destes commits. | Mais grossa; na Horas 27 alguns pontinhos novos perto da moldura dourada e letras quase encostando ("Victorie,"); também igual ao de antes. |

## Velocidade

- **Horas 11 no Preto e branco:** 17,3 → 11,8 s pelo caminho do programa (mediana de 5 voltas). Paga de
  sobra os 0,2–0,4 s que a conferência 6 tinha custado.
- **Medidor no 50 (o padrão):** sem mudança de tempo (Horas 47 só o filtro: igual).
- **Medidor fora do 50 nas páginas de letra grossa:** fica um pouco mais lento. Medi só o filtro, duas
  voltas alternadas: Horas 47 +0,22 a 0,28 s (0 e 100), Graduale 222 +0,15 a 0,20 s. O implementador
  escreveu +0,11 a 0,15 s; no meu PC, ocupado, deu um pouco mais. Pela regra 6 ao pé da letra é "mais
  lento" quando o Kaique mexe no medidor; já está como pergunta S2 no formulário 7.

## O atalho da Horas 11 é arriscado em outros livros?

**Como ele funciona:** para escolher o jeito de passar a preto e branco, o programa mede a grossura da
letra numa cópia pequena da página. Se essa cópia tem mais de 60% de tinta, a medida desiste. Antes,
o programa então media a página inteira em tamanho cheio (~9,5 s na Horas 11). Agora ele refaz a
medida pequena sem a trava; se der "letra grossa com folga" e a página inteira tiver no máximo 60%
de tinta, responde "Otsu" sem a medida cheia.

**O que achei no acervo (máquina):** varri as 3353 folhas dos 10 livros (o acervo e o Opus Majus); 303 páginas passaram na
peneira e foram desenhadas pelo programa a 300 DPI. A trava age em **53 páginas**; o atalho só chega a
decidir **em uma: a própria Horas 11** (e decide igual à medida cheia). Nas outras 52 a página inteira
tem mais de 60% de tinta (capas, a Pesel inteira, folhas escuras), e aí a resposta é a mesma de antes
por construção. **Nenhuma escolha mudou no acervo.**

**O ponto fraco (máquina, folha artificial):** o atalho confia que a cópia pequena e a página inteira
"enxergam" a mesma tinta. Numa foto em **retícula** (pontinhos de impressão), a cópia pequena vê
cinza liso (muita tinta, "grossa") e a página inteira vê pontinhos finos (pouca tinta, "fina"). No
acervo isso existe: a última folha do Opus Majus tem 96,5% de tinta na cópia pequena e 74% na página
inteira. Montei uma folha com uma retícula de 1 ponto cobrindo 85% da folha e texto fino embaixo:
**antes o programa escolhia Sauvola; agora escolhe Otsu** (script `contraexemplo_reticula.py`). Com a
retícula cobrindo 70% ou com pontos de 2 pixels, não troca.

**O que isso daria na prática:** só numa página quase toda foto em retícula fina, com pouca margem, e
no Preto e branco: o texto sairia pelo Otsu com a borda do Sauvola em vez do Sauvola (letra um pouco
diferente, não sumida). Não vi página assim no acervo. **Risco baixo, mas real.** Sugestão barata para
o implementador, se a gerente quiser: só usar o atalho quando a tinta da cópia pequena e a da página
inteira forem parecidas (na Horas 11: 60,4% e 59,7%; no Opus 450: 96,5% e 74%).

**Teste que protege:** `tests/test_escolha_sem_a_trava_de_tinta.py` (4 testes, folhas sintéticas de
linhas) protege o mecanismo: o atalho age em traço grosso, a página com mais de 60% de tinta continua
Sauvola, o traço fino continua indo para a medida cheia, e o k não muda. **Nenhum teste usa a Horas
11 de verdade nem cobre o caso da retícula** (cópia pequena e página inteira discordando da tinta).

## Ressalvas

1. **Graduale no "mais escuro" (75 e 100):** além das notas e letras mais grossas, aparecem tracinhos
   novos onde a pauta e as linhas de régua são muito fracas (Graduale 221: 406 → 513 pedaços no 75;
   223: 511 → 688). São pedacinhos da pauta de ponta seca e do pontilhado da margem que já estavam
   quase passando no 50; não é sujeira solta. O implementador já tinha dito isso. Só aparece se o
   Kaique puxar o medidor para cima.
2. **O 0 continua picotando a letra nas páginas de letra fina (Horas 26 e 27):** não é destes commits
   (antes e agora idênticos ponto a ponto nos 5 valores), mas é **o mesmo defeito que o Samuel recusou
   na Horas 47** ("Ainda está apagando as letras"), agora só nas páginas em que o programa usa o
   Sauvola: no 0 a tinta cai de 6,8% para 3,8% e "Silvestre", "Prefentation" saem falhados. O conserto
   `bf9680f` só vale para as páginas de letra grossa. Sugiro ir para a **Lista de bugs** (o "mais
   fraco" das páginas de letra fina é forte demais). Imagem: `para-o-samuel/horas26-medidor-tamanho-real.jpg`.
3. **O alcance do medidor nas páginas de letra grossa é pequeno** (Horas 47: tinta 34,6% no 0, 34,9%
   no 50, 35,1% no 100; na Horas 11 quase nada). Foi de propósito, para não picotar; mas quem puxar o
   medidor esperando mudança grande vai ver pouca.
4. **Custo fora do 50:** +0,15 a 0,28 s por página de letra grossa só no filtro (regra 6, pergunta S2).
5. **O atalho da Horas 11:** ver a seção acima (folha artificial com retícula troca a escolha; acervo
   não).
6. **Não pilotei a janela:** os dois commits não mexem na tela. Os botões laranja "usar mais fraco /
   mais escuro" e o deslizante do painel continuam quebrados (já na Lista de bugs de 02/10); o
   medidor foi testado mudando o valor direto no projeto, pelo caminho do botão "Confirmar e processar".
7. **Tempos com o PC ocupado** (outro agente usando o programa na tela): a Horas 11 oscilou de 11,4 a
   14,7 s no agora; a diferença para o antes (sempre 17,2–17,4 s) aparece em todas as voltas.

## As imagens que o Samuel deve ver

1. `para-o-samuel/horas47-medidor-tamanho-real.jpg`: **Horas 47 em tamanho real**, referência, AGORA no
   0, 50 e 100, ANTES no 0 e no 100. Veja se o 0 de agora ainda está bom de ler e se o 100 não ficou
   grosso demais.
2. `para-o-samuel/horas26-medidor-tamanho-real.jpg`: **Horas 26**, o 0 ainda picota nas páginas de
   letra fina (já era assim; ressalva 2).
3. `para-o-samuel/graduale222-medidor-tamanho-real.jpg`: **Graduale 222** no 0, 50, 100: os tracinhos
   da pauta fraca no 100 (ressalva 1).

![Horas 47: referência, AGORA 0, 50, 100, ANTES 0 e 100](para-o-samuel/horas47-medidor-tamanho-real.jpg)

![Horas 26: o 0 ainda picota nas páginas de letra fina](para-o-samuel/horas26-medidor-tamanho-real.jpg)

![Graduale 222: tracinhos da pauta no 100](para-o-samuel/graduale222-medidor-tamanho-real.jpg)

## Bugs para a Lista de bugs

- **02/10, achado pelo verificador:** no Preto e branco, nas páginas de letra fina (as que o programa
  passa pelo Sauvola; ex.: Horas 26 e 27), o medidor no 0 ("mais fraco") deixa a letra bem falhada
  (Horas 26: tinta 6,8% → 3,8%; "S. Silveftre", "La Prefentation"). Não é de `bf9680f` (igual antes),
  mas é o mesmo tipo de defeito recusado na Horas 47. `core/filtros.py`, `k_do_sauvola` (K_FRACO 0,40).
  Imagem: `relatorios/conferir/medidor-e-horas11-2026-10-02/verificador/para-o-samuel/horas26-medidor-tamanho-real.jpg`.

## Onde está tudo

- Este parecer e os scripts: `relatorios/conferir/medidor-e-horas11-2026-10-02/verificador/`
  (`rodar_verificador.py`, `rodar_tudo.sh`, `comparar.py`, `medidor_programa.py`,
  `analisar_medidor.py`, `pecas_novas.py`, `medir_tempo.sh`, `tempo_filtro.py`,
  `varrer_trava_programa.py`, `contraexemplo_reticula.py`).
- Números: `comparacao-verificador.json` (96 imagens antes × agora), `medidor-verificador.json`
  (medidor nas 12 páginas), `varredura-programa-todos.json` (o acervo inteiro), `pytest.log`.
- Recortes em tamanho real: `zoom/`; folhas de contato: `folha-*.jpg`.
- As imagens grandes das rodadas (PNG em resolução cheia) foram apagadas no fim, para não ocupar disco.
