# Medidor de força nas páginas de letra grossa e Horas 11 mais rápida

Implementador, 02/10/2026, ramo `fase-1`. Dois consertos pedidos pelo parecer do verificador da
conferência 6. Aqui é só **PRONTO PARA CONFERIR** na opinião do implementador; quem marca é o Samuel.
Commits: `bf9680f` (medidor) e `7f50e70` (Horas 11).

## Em uma frase

- **O medidor "mais fraco / mais escuro" voltou a ser coerente nas páginas de letra grossa** (Horas,
  Graduale, Escola, Opus 20): o "mais escuro" nunca deixa uma letra mais clara que o meio, e o "mais
  fraco" afina um pouco sem voltar às letras falhadas que o Samuel recusou. No 50 (o normal) nada mudou.
- **A Horas 11 no Preto e branco ficou uns 5 segundos mais rápida** pelo caminho do programa (de ~16 s
  para ~11 s), sem mudar nenhuma imagem: as 32 páginas saem idênticas no Preto e branco, no Mágico pro e
  no Melhorar.
- Nada mudou na tela.

## 1. O medidor de força nas páginas de letra grossa

**O que estava errado.** Depois do conserto da Horas 47 (`1b174e4`), com o filtro só: no 0 ("mais
fraco") a letra voltava a ser a fina e falhada que o Samuel recusou; no 100 ("mais escuro") algumas
letras da Horas 47 ("nous", "Prêchant") voltavam a falhar, mais claras que no meio.

**Por quê.** O valor do medidor ia direto para a escolha dos pedaços de letra que o programa completa.
No 0 essa escolha não completava nada (ficava a letra falhada); no 100 os pedaços cresciam, grudavam
no vizinho e eram recusados inteiros.

**O que mudou.** Os pedaços são escolhidos sempre como no 50 (o resultado bom, intocado), e o medidor
só afina ou engrossa a letra que já saiu:

- **mais fraco:** tira só um pouco da beirada mais clara da letra; o miolo fica todo;
- **mais escuro:** a letra cresce no máximo 2 pontos (a 300 DPI) para onde o papel em volta é escuro;
  engrossa e enche a falha curta, sem puxar risco solto.

Por construção, o que é preto num valor do medidor continua preto em todo valor mais escuro.

**Provas (máquina).** Só o filtro, 32 páginas a 300 DPI, medidor em 0, 25, 50, 75 e 100:

- **o 50 idêntico ponto a ponto** ao de antes nas 32 páginas;
- **em nenhuma página algum ponto clareia ao subir o medidor** (antes, do 50 para o 100, clareavam de
  316 a 12 155 pontos em cada uma das 10 páginas de letra grossa);
- nas 22 páginas de letra fina (Sauvola) o medidor não mudou.

Tinta da página inteira da Horas 47 (a moldura pesa muito): 40,39% / 40,46% / 40,54% / 40,67% /
40,78% nos cinco valores. No quadro de texto: 10,5% no 0, 11,2% no 50, 11,9% no 100.

**O que olhar (olho).** Horas 47, ORIGINAL · ANTES · AGORA, com o medidor no 0, no 50 e no 100 (o mesmo
trecho do texto, em tamanho real):

![Horas 47 no medidor 0](cartoes/horas47-medidor-000.jpg)

![Horas 47 no medidor 50](cartoes/horas47-medidor-050.jpg)

![Horas 47 no medidor 100](cartoes/horas47-medidor-100.jpg)

Opinião: no 0, o AGORA é a letra do 50 um pouco mais fina, sem os buracos do ANTES ("Prêchant",
"nous", "dedans" inteiros); no 50, igual; no 100, o AGORA é mais cheio que o 50 e "Prêchant" e "nous"
saem inteiros (no ANTES falhavam).

**Graduale 221 no "mais escuro":** as notas, as letras e as linhas da pauta engrossam um pouco mais que
no ANTES, e um pontinho aqui e ali aparece. É o que "mais escuro" promete; fica como ressalva.

![Graduale 221 no medidor 100](cartoes/graduale221-medidor-100.jpg)

**Os botões laranja e o deslizante do painel.** Os botões "usar mais fraco" / "usar mais escuro" (o
aviso "Ficou escura" / "Texto quase sumiu") continuam quebrados como na Lista de bugs de 02/10: chamam
uma função que não existe e aparece "Não consegui fazer isso agora". O deslizante do painel "Filtro da
página" continua sem gravar o valor (só redesenha). **Este conserto não muda nenhum dos dois bugs.** O
que muda é o que o valor faz quando chegar ao filtro: quando os botões forem consertados (os projetos
antigos usavam 15 para "mais fraco" e 85 para "mais escuro"), nas páginas de letra grossa o "mais
escuro" vai de fato escurecer (antes podia clarear letras) e o "mais fraco" vai afinar sem picotar.
Atenção: nas páginas de letra grossa o alcance do medidor é pequeno (só a beirada da letra mexe), então
"usar mais escuro" ali não salva uma página em que o texto realmente sumiu.

## 2. Horas 11 no Preto e branco (regra 6)

**O que estava errado.** Com `1b174e4` a Horas 11 ficou 0,2 a 0,4 s mais lenta, pagando uma etapa que
não muda a imagem dela.

**Por quê.** Para escolher o jeito de passar a preto e branco, o programa mede a grossura da letra numa
cópia pequena da página; na Horas 11 essa cópia tem 60,4% de tinta (a moldura e a iluminura enchem
metade da folha), um pouco acima de uma trava de 60%, e o programa desistia e media a página inteira
(~9,5 s a 300 DPI) só para descobrir que a letra é grossa.

**O que mudou.** Quando a medida pequena desiste por causa da trava, ela é refeita sem a trava (~0,3 s).
Se der "letra grossa com folga" (na Horas 11 deu 44, e o limite é 16), a resposta sai sem a medida
grande, com a mesma conferência de tinta da folha inteira que a medida grande faria. Senão, a medida
grande decide, como antes. O número que regula a força do preto (o k) continua vendo a medida com a
trava, por isso a imagem não muda.

**Provas (máquina).** As 32 páginas pelo caminho do botão "Confirmar e processar", código de antes
(`a10e592`) contra o de agora (com os dois consertos): **Preto e branco, Mágico pro e Melhorar: 96 de
96 idênticas ponto a ponto.**

**Tempos** (PC sem outro agente, caminho do programa, alternado ANTES, AGORA, ANTES, AGORA, ANTES,
AGORA; segundos de "processar"):

| Página | ANTES (3 voltas) | AGORA (3 voltas) |
|---|---|---|
| Horas 11 | 16,1 · 15,9 · 16,3 | **11,2 · 11,0 · 11,1** |
| Horas 47 | 8,5 · 8,6 · 8,7 | 8,7 · 8,7 · 8,6 |
| Graduale 222 | 4,1 · 4,3 · 4,1 | 4,0 · 4,1 · 4,1 |
| Palatino 5 | 1,9 · 1,8 · 1,9 | 1,8 · 1,9 · 1,9 |

Só o filtro, na imagem que o programa entrega a ele (mediana de 3 voltas alternadas): Horas 11 **6,3 s
antes do conserto da Horas 47 (`4a9c0e4`), 6,5 s com ele, 1,4 s agora**; Horas 47 4,8 / 1,1 / 1,1 s;
Graduale 222 0,8 / 0,6 / 0,6 s; Palatino 5 0,26 / 0,16 / 0,16 s.

## Ressalvas

1. **O medidor fora do 50 ficou um pouco mais lento nas páginas de letra grossa:** +0,11 a 0,15 s por
   página (só o filtro, Horas 47 e Graduale 222, medidor no 0 e no 100), porque o "mais fraco" e o
   "mais escuro" fazem uma conta a mais. No 50 (o padrão) nada muda; na prévia (110 DPI) a conta é bem
   menor. Pela regra 6 ao pé da letra isso é "mais lento" quando o Kaique mexe no medidor; a Horas 11
   ganhou ~5 s. Decisão da gerente/Samuel.
2. **O "mais fraco" nas páginas de letra grossa mexe pouco** (no quadro de texto da Horas 47, de 11,2%
   para 10,5% de tinta). Foi de propósito: com mais força a letra volta a picotar (medido e descartado,
   `relatorios/melhorias.md`, tentativa 66). Se o Kaique esperar um "mais fraco" forte nessas páginas,
   não vai ter.
3. **Graduale 221 no 100:** linhas da pauta e notas mais grossas que no ANTES, e alguns pontinhos
   novos; o pontilhado da margem direita (risco de régua do pergaminho) fica um pouco mais visível.
4. **Horas 11:** a resposta rápida vale para páginas grandes (mais de 2500 pontos de altura) com mais de
   60% de tinta na cópia pequena e letra bem grossa. Nas 32 páginas do gabarito todas as escolhas ficaram
   iguais (as 96 imagens idênticas), mas a folga de 1,6 vez foi medida no gabarito; uma página de outro
   livro, exatamente nessa situação e com letra perto do limite, poderia trocar de jeito. O teste de
   máquina cobre folhas sintéticas.
5. O medidor foi conferido **só no filtro** (sem marcação, 300 DPI) e nos valores 0, 25, 50, 75 e 100;
   não pilotei a janela (o item não mexe na tela). As rodadas pelo caminho do programa usam o 50.

## Testes

`pytest tests -q`: **1369 passaram, 1 pulado** (eram 1359; +6 do medidor em
`tests/test_medidor_nas_paginas_otsu.py`, +4 da Horas 11 em `tests/test_escolha_sem_a_trava_de_tinta.py`).

## Onde está tudo

- Este relatório e os scripts: `relatorios/conferir/medidor-e-horas11-2026-10-02/` (`rodar_gabarito.py`,
  `comparar.py`, `medidor_32.py`, `tempo_filtro.py`, `medir_tempo.sh`, `montar_cartoes.py`,
  `cartao_graduale.py`).
- Números: `medidor-32.json` (medidor nas 32 páginas), `comparacao.json` (96 imagens antes × agora),
  `tempo-filtro.json` (tempo só do filtro).
- Cartões: `cartoes/`.
- Tentado e descartado: `relatorios/melhorias.md`, tentativas 66 e 67.

## Bugs para a Lista de bugs

Nenhum novo. Os dois bugs da tela citados acima (botões laranja; deslizante do painel) já estão na
Lista de bugs de 02/10 e não foram tocados.
