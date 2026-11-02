# ONDE-PAREI — Dividir: "Uma página" mostra só a metade (D-601, 02/11/2026)

Cópia: `.claude/worktrees/dividir-metade`, ramo `dividir-metade-2026-11-02` (saiu de `obra-2026-10-26`, `110976f`).
Só `ui/` (e os testes). Outro construtor mexe ao mesmo tempo na faixa de baixo depois do "está certo"
(`_atualizar_faixa`, `_texto_tranquilo`), ramo `esta-certo-2026-11-02`: não mexo nessas funções.

## Decisões que esta tarefa precisa cumprir

- **D-601 (02/11/2026)** — Testando o Dividir no Gradus Primus: "eu dividi a pagina não era para ela virar só uma na
  hora que eu dividi, como funciona no scantailor?" · "ele não cortou, porque como pode ver as duas paginas ainda
  estão juntas, deveria então aparecer só metdade da pagina que era dupla, e eu pode mudar a opção lá embaixo de uma
  pagina, para pagina dupla." · pergunta: ""Uma página" (de fábrica): depois de dividir, aparece só a metade, uma
  página de cada vez, e as setas andam pelas páginas. "Duas lado a lado": aparece a folha inteira, com a linha azul
  para arrastar, como hoje. Pode ser assim?" → "ok, pode botar um agente para fazer isso".
  **Na ferramenta Dividir, com "Uma página" (de fábrica), a folha dividida mostra só uma metade (uma página por
  vez, as setas andam pelas páginas); com "Duas lado a lado", a folha inteira com a linha azul para arrastar.**
  Muda a D-007 só dentro do Dividir. Prova: Gradus Primus folha 1 dividida → "Uma página" mostra só a contracapa;
  seta → capa; "Duas lado a lado" → folha inteira com a linha.
- **D-007 (26/10)** — "quando eu escolher para começar no automatico e dividir as folhas o livro tem que aparecer em
  uma pagina por vez para mim." Fora do Dividir continua igual (uma página por vez). Dentro do Dividir muda pela
  D-601.
- **D-501 (27/10)** — o livro nunca abre no Dividir; o Automático que divide estando no Dividir leva à página.
  Não muda.
- **D-006 / D-015** — "Uma página / Duas lado a lado" na barra de baixo (e no menu Ver); o lado a lado é opção,
  não padrão; de fábrica "Uma página". Não muda (só passa a valer também dentro do Dividir, pela D-601).
- **D-046** — "deixar em branco" / "tirar do livro" em qualquer página ("Esta página" no Propriedades do Dividir).
  Não muda (age na página da vez).
- **D-051** — Propriedades do Dividir em "Só nesta folha" / "Para o livro todo". Não muda.
- **D-074 / D-080** — não dividir folha de uma página só; dividir só quando o Kaique pede. Não muda (folha não
  dividida continua a folha inteira, como hoje).
- **D-498** — "não dividir esta" junta as duas páginas; "dividir esta" devolve as duas como estavam. Não muda.
- **D-528** — marcações da folha inteira vão para a metade em que estão. Não muda (só a tela).
- **D-558** — "dividir" na grade "Todas as páginas". Não muda.
- **D-590** — "juntar todas" ao lado de "não dividir esta". Não muda.
- **D-568** — roda: sem zoom troca de página; com zoom anda pela página; Ctrl + roda dá zoom. No Dividir com
  "Uma página", a roda sem zoom passa a andar pelas páginas (D-601: "as setas andam pelas páginas").
- **D-599 / D-600** — Ctrl + roda dá zoom para onde está o mouse; Shift + roda para os lados com zoom. Não muda.
- **CLAUDE.md §11 item 7** — nenhum botão, aviso ou texto novo além do decidido.

## Andamento

- [ ] Mudança em `ui/tela_conferir.py`
- [ ] Prova (`tests/test_decisoes_dividir_metade.py`) + reversão no `110976f`
- [ ] Testes antigos que mediam a linha com "Uma página" (comportamento que a D-601 trocou)
- [ ] Prints antes/depois (cópia do Gradus Primus em `_tmp/`)
- [ ] Testes no PC, push, GitHub

## Escolhas pelo jeito que o código já tem (anotadas)

(preenchido durante o trabalho)

## Perguntas para o Samuel

(nenhuma ainda)
