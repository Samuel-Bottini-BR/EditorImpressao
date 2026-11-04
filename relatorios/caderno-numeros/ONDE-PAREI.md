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

## Passos

1. [x] Ler CLAUDE.md, agentes, DECISOES (D-604, D-574, D-603, D-614, D-615, D-616).
2. [ ] Teste novo que falha agora (livro de 40 páginas, 20 por caderno, ordem mudada).
3. [ ] Etapa 7 e tela grande.
4. [ ] "Montar para imprimir".
5. [ ] Testes antigos, um arquivo por vez.
6. [ ] Janela de verdade com o Gradus (prints).
7. [ ] Push, GitHub, relatório.

## Perguntas para o Samuel

(nenhuma por enquanto)
