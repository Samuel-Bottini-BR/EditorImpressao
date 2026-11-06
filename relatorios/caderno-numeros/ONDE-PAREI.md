# D-604: os números das páginas nas folhas do caderno (ONDE PAREI)

Ramo `caderno-numeros-2026-11-04` (saiu de `obra-2026-10-26`, `dac12a3f`). Cópia de trabalho
`.claude/worktrees/caderno-numeros`.

## Decisões que esta tarefa precisa cumprir

- **D-604** (03/11, print a-52): "o verso da folha 1 e 19 não podem ter a numeração de folha 1 - e 19 tem
  que dizer a numeração que elas realmente teriam." · pergunta: "Folha 1 de 19, frente: páginas 20 e 1
  [...] verso: páginas 2 e 19 [...] Ao virar para a folha 2, mostraria "frente: páginas 18 e 3", e assim
  por diante. É isso?" → "acredito que sim" · 04/11, print a-79: "é melhor colocar a numeração das paginas
  verdadeiras aqui". Página em branco do fim do caderno: "a confirmar com ele se aparecer" (a gerente:
  mostrar "em branco" no lugar do número, com print).
- **D-574**: as folhas do caderno nos três lugares (etapa 7 do Automático, tela grande de caderno,
  "Montar para imprimir"); "Folha N de M" troca na hora ao apertar a seta ("já troca").
- **D-603**: as folhas do caderno seguem as etapas marcadas (Dividir na prévia) antes do "Rodar".
- **D-615**: a ordem mudada à mão vale nos cadernos.
- **D-616**: "A 1ª folha é a capa aberta" (capa = página 1, contracapa = última).
- **D-614**: o "depois" com Dividir mostra uma página por vez (não muda aqui; só não pode quebrar).
- **D-605 / CLAUDE.md §11.8**: o novo não estraga o que já está escolhido e testado.

## O que já está escolhido e testado aqui

Telas e arquivos que vou tocar: `ui/widgets/folhas_do_caderno.py` (etapa 7 e tela grande de caderno),
`ui/dialogo_impressao.py` (o "Montar para imprimir"). Não vou mexer em `core/`.

Escolhido e testado (fica igual):
- O texto "Folha N de M — frente" / "— verso" (D-574, opção 1), o "folha N", o "(vira o papel)", as
  setas, o "tela cheia", a bolinha, a tela grande maximizada com <, >, –, +, "ajustar à tela", "fechar".
- O desenho da folha (mesma conta do PDF, D-473), uma folha por vez na memória, tela sem parar.
- A ordem da dobra (core/cadernos.montar_ordem, último caderno menor imp-4).
- No "Montar para imprimir": encadernação à direita troca os lados, folhas de/até, páginas de/até
  (com a branca de paridade), reverter, só frente/só verso.

Testes que já existem e que precisam continuar passando SEM MUDAR:
- `tests/test_cadernos.py` (11), `tests/test_decisoes_montar_cadernos.py` (11)
- `tests/test_caderno_segue_as_etapas.py` (4, D-603)
- `tests/test_decisoes_caderno_tela_grande.py` (15, D-574 etapa 7 e tela grande)
- `tests/test_decisoes_capa_aberta.py` (6, D-616), `tests/test_decisoes_ordem_folhas.py` (12, D-615)
- `tests/test_decisoes_livreto_ver.py` (13, D-574 no "Montar para imprimir")
- `tests/test_dialogo_impressao.py` (5), `tests/test_decisoes_impressao.py` (18), `tests/test_impressao.py` (17),
  `tests/test_decisoes_9b1.py` (21)
- `tests/test_promessas.py` (p211 setas da folha do caderno e a do livreto)
- `tests/test_decisoes*.py` (as provas das decisões)

**Cuidado achado antes de mexer:** 25 asserts em testes antigos comparam o rótulo inteiro, por exemplo
`folhas.rotulos["frente"].text() == "Folha 1 de 3 — frente"`. Se as páginas entrassem no MESMO rótulo,
esses testes quebrariam. Jeito escolhido (detalhe técnico, sem mudar nada que ele decidiu): o rótulo
"Folha N de M — frente" fica como está, e logo depois dele, na mesma linha e no mesmo negrito, um
rótulo novo com ": páginas 20 e 1". Na tela lê-se "Folha 1 de 35 — frente: páginas 20 e 1".

## Como fica para quem usa e no livro (D-637, CLAUDE.md §11.9; escrito em 05/11 antes de mexer)

Pedido da gerente (05/11, achado C do verificador): quando a linha da frente não cabe no "Montar para
imprimir", a linha de baixo começava com ":" (": páginas 20 e 1"). Só a quebra muda; as palavras não.

- **O que o Kaique vê, antes desta mudança:** abre "Montar para imprimir" com o Gradus, Livreto 20 por
  caderno. Em cima da frente: "Folha 1 de 18 — frente" e, na linha de baixo, ": páginas 20 e 1". Em cima
  do verso, numa linha só: "Folha 1 de 18 — verso: páginas 2 e 19".
- **Depois:** a frente fica "Folha 1 de 18 — frente" e, na linha de baixo, "páginas 20 e 1" (sem os dois
  pontos). O verso, que cabe, continua "Folha 1 de 18 — verso: páginas 2 e 19", numa linha só. Ao
  apertar a seta, o texto troca na hora como antes (D-574). Na etapa 7 e na tela grande, onde a linha
  cabe, nada muda.
- **No PDF que sai:** nada muda. É só o texto em cima do desenho na tela; a conta que monta as folhas
  (core/impressao, core/cadernos) não é tocada.
- **Risco de problema novo:** a linha decidir "cabe / não cabe" de um jeito que fique pulando
  (tirar os dois pontos deixa o texto mais curto). Cuidado: a decisão usa sempre a largura do texto
  inteiro, com os dois pontos.

## Passos

1. [x] Ler CLAUDE.md, agentes, DECISOES (D-604, D-574, D-603, D-614, D-615, D-616).
2. [x] Teste novo que falha agora (livro de 40 páginas, 20 por caderno, ordem mudada) — `98dbe0a4`.
3. [x] Etapa 7 e tela grande — `cd5dc539`.
4. [x] "Montar para imprimir" — `cd5dc539`.
5. [x] 05/11: juntei o `obra-2026-10-26` (`f06e0c15`) sem conflito (`9e21350b`).
6. [x] Testes antigos, um arquivo por vez (abaixo).
7. [x] Janela de verdade com o Gradus (`piloto.py`, prints em `prints/`, anotações em `anotacoes.txt`).
8. [x] Achado na conferência: num livro de 300 páginas o texto novo era cortado no "Montar para
   imprimir" (coluna de largura fixa). Consertado: o que não cabe desce para a linha de baixo
   (`12407cd7`, 2 provas novas que falham em `cd5dc539`).
9. [x] Push e GitHub (abaixo).
10. [x] 05/11, achado C do verificador (pedido da gerente): na linha de baixo, sem os dois pontos.
    Juntei de novo o `obra-2026-10-26` (`d3b613b6`, só documentos) sem conflito; conserto em
    `b0e2edb1` (2 provas novas que falham em `23d2b157`); piloto de novo com o Gradus.

## Como cumpri cada decisão

- **D-604** — cada lado da folha diz as páginas do livro que estão nele, da esquerda para a direita,
  nos três lugares. Gradus (70 páginas, 20 por caderno), janela de verdade:
  - etapa 7, folha 1: "Folha 1 de 18 — frente: páginas 20 e 1" / "— verso: páginas 2 e 19"
    (`prints/02-etapa7-folha-1.png`); folha 2: "frente: páginas 18 e 3" / "verso: páginas 4 e 17"
    (`prints/03-etapa7-folha-2.png`), o texto troca logo depois do clique (anotado).
  - tela grande: "Folha 2 de 35 — frente: páginas 18 e 3" (`prints/09-tela-grande-folha-2.png`).
  - "Montar para imprimir": as mesmas palavras (`prints/10-...folha-1.png`, `prints/11-...folha-2.png`).
  - Livro de 300 páginas no "Montar para imprimir": as páginas descem para a linha de baixo, sem
    cortar e sem os dois pontos: "Folha 43 de 75 — frente" / "páginas 196 e 165"
    (`prints/12-montar-para-imprimir-livro-300-paginas.png`).
  - Gradus no "Montar para imprimir" (05/11, depois do achado C): "Folha 1 de 18 — frente" e embaixo
    "páginas 20 e 1"; o verso cabe: "Folha 1 de 18 — verso: páginas 2 e 19" (`prints/10-...folha-1.png`).
  - Provas: `tests/test_decisoes_caderno_numeros.py` (7): folhas 1 e 2 com a ordem mudada à mão, o
    lugar em branco do fim, Dividir + capa aberta, "Montar para imprimir" (folhas 1 e 2, costura à
    direita, branca de paridade), e a linha que desce nos dois lugares. O número escrito é conferido
    contra a página que está DESENHADA naquele lugar. Reversão: as 5 primeiras falham em `02aeef59`
    (o código de antes), as 2 da linha que desce falham em `cd5dc539`.
- **D-574** — o "Folha N de M — frente" continua igual e troca na hora ao apertar a seta; as páginas
  vêm num rótulo só delas, logo depois. `tests/test_decisoes_caderno_tela_grande.py` e
  `tests/test_decisoes_livreto_ver.py` passam sem mudar nada.
- **D-603** — com o Dividir marcado, os números são os do livro dividido ("Folha 1 de 35 — frente:
  páginas 20 e 1", `prints/07-etapa7-dividir-folha-1.png`); `test_caderno_segue_as_etapas.py` passa.
- **D-615 / D-616** — os números seguem a ordem mudada à mão e a capa aberta (provas acima);
  `test_decisoes_ordem_folhas.py` e `test_decisoes_capa_aberta.py` passam.
- **D-605** — nenhum teste antigo foi mudado; todos os que tocam estas telas passam (abaixo).
- **D-637** (Como fica para quem usa e no livro, conferido em 05/11): clicando na janela de verdade
  (piloto com o Gradus, prints 02 a 11) a tela é a descrita lá em cima: a linha de baixo diz
  "páginas 20 e 1", a que cabe continua numa linha só, a seta troca o texto na hora. O PDF que sai não
  muda: nenhum arquivo de `core/` foi tocado (`git diff obra-2026-10-26 -- core` vazio); as provas de
  "gravar" do "Montar para imprimir" (`test_decisoes_impressao`, `test_impressao`) passam. Problema
  novo: nenhum achado.

## Testes

No PC, um arquivo por vez (05/11): os 40 `tests/test_decisoes*.py` passaram, mais `test_cadernos`,
`test_caderno_segue_as_etapas`, `test_dialogo_impressao`, `test_impressao` e `test_promessas`
(267 passaram, 1 já marcado como falha esperada). `test_decisoes_montar_cadernos.py` teve 1 falha
na primeira volta (com o PC carregado) e passou inteiro (13) ao rodar de novo sozinho, sem mudar nada.
Depois do conserto da linha que desce (`12407cd7`), um por vez: `test_decisoes_caderno_numeros` 7,
`test_decisoes_caderno_tela_grande` 14 (+1 pulado, como antes), `test_decisoes_livreto_ver` 13 (+1 pulado),
`test_dialogo_impressao` 5, `test_decisoes_impressao` 22, `test_impressao` 17, `test_caderno_segue_as_etapas` 11,
`test_decisoes_capa_aberta` 6, `test_decisoes_ordem_folhas` 12, `test_decisoes_montar_cadernos` 13,
`test_decisoes_9b1` 25, `test_cadernos` 28, `test_decisoes_automatico_ver_como_fica` 22, `test_decisoes_automatico` 29:
todos passaram.

GitHub ("Testes no Windows"): rodada 41948429688 (merge `9e21350b`) passou. Depois do conserto:
rodada 41958485208 (ponta `76329644`, com o conserto) passou.

05/11, depois do achado C (sem os dois pontos, `b0e2edb1`): no PC, um por vez, passaram
`test_decisoes_caderno_numeros` 9, `test_decisoes_caderno_tela_grande` 14 (+1 pulado), `test_decisoes_livreto_ver`
13 (+1 pulado), `test_dialogo_impressao` 5, `test_decisoes_impressao` 22, `test_impressao` 17,
`test_caderno_segue_as_etapas` 11, `test_decisoes_capa_aberta` 6, `test_decisoes_ordem_folhas` 12,
`test_decisoes_montar_cadernos` 13, `test_decisoes_9b1` 25, `test_cadernos` 28,
`test_decisoes_automatico_ver_como_fica` 22, `test_decisoes_automatico` 29, `test_decisoes_9b2` 30,
`test_decisoes_automatico_opcoes_do_filtro` 21, `test_decisoes_gravuras_cinza` 20, `test_decisoes_previa_dividida` 4,
`test_decisoes_previa_numero` 8, `test_decisoes_so_as_letras` 5, `test_decisoes_tela` 35.
GitHub: rodada 41974099823 (ponta `45d7a5e7`) passou.

## Perguntas para o Samuel

1. **Lugar sem página no fim do caderno** (D-604: "a confirmar com ele se aparecer" — apareceu).
   No Gradus (70 páginas, 20 por caderno) o último caderno tem 10 páginas em 12 lugares; a folha 16
   fica assim: "Folha 16 de 18 — frente: páginas em branco e 61" / "Folha 16 de 18 — verso:
   páginas 62 e em branco" (print `prints/06-etapa7-folha-com-lugar-em-branco.png`). Foi a
   sugestão da gerente (04/11: "em branco" no lugar do número). Pergunta: "Na folha que tem
   lugar sem página, pode ficar escrito 'páginas em branco e 61'?"
2. **"Folha 2 de 32" enquanto monta** (resposta dele na Central, 04/11, cartão
   `d574-texto-enquanto-monta`: "Porque que é folha 2 de 32? e não a real numeração das
   paginas?"). Não mudei esse texto. Onde aparece:
   - no "Montar para imprimir" (`ui/dialogo_impressao.py`, `texto_da_face`), em cima da frente e
     do verso: "Folha 2 de 32 — frente"; troca na hora ao apertar a seta (D-574, "já troca");
   - igual na etapa 7 do Automático e na tela grande de caderno (`ui/widgets/folhas_do_caderno.py`);
   - na tela grande há também o contador de baixo, entre "<" e ">": "Folha 2 de 35" (sem páginas).
   O que a D-604 já cobre: agora, logo depois do "Folha 2 de 32 — frente", vem, por exemplo com 20 por caderno, ": páginas 18 e 3"
   (as páginas de verdade), também na hora em que a seta é apertada, antes de a folha ficar pronta
   (anotado no `anotacoes.txt`: "logo depois do clique"). O que a D-604 NÃO cobre: tirar o
   "Folha 2 de 32" (ele escolheu esse texto na D-574, opção 1) e o contador de baixo da tela grande.
   A gerente responde a ele.
3. (Resolvido em 05/11, achado C) a linha de baixo começava com ": páginas 222 e 219"; agora é
   "páginas 196 e 165" na linha de baixo (print 12). No Gradus, no "Montar para imprimir", a
   frente da folha 1 desce ("páginas 20 e 1" na linha de baixo) e o verso cabe numa linha (print 10): a coluna tem só uns 310 pontos. Antes do
   conserto o texto empurrava a coluna para a direita, para fora da parte visível.
