# ONDE PAREI — D-590 (a caixinha do "Dividir" volta marcada sozinha)

Ramo `dividir-caixinha-2026-11-03` (saiu de `obra-2026-10-26` em `8846017`), cópia
`.claude/worktrees/dividir-caixinha`. Construtor: implementador (pedido da gerente, 03/11/2026).
Outro agente mexe ao mesmo tempo em `core/automatico._dividir`, `paginas_mexidas` e no uso de `pular`
(ramo `automatico-pular-2026-11-03`): **não tocar nesses trechos**.

## Decisões que esta tarefa precisa cumprir

- **D-590 (30/10 e 03/11).** "desmarcar 'Dividir' no Automático não junta nada" + 03/11, à sugestão
  "a caixinha fica desmarcada como você deixou, e as folhas continuam divididas. Pode ser?":
  **"Sim a caixinha continua desmacada."** E: "isso não tinha sido revisto em todo programa, se tinha
  algum item que desmarcado voltava a funcionar sozinho ou se marcava sem precisar estar marcado, sem
  ser uma opção já colocada para ser assim."
- **D-589 (30/10).** "Sim, se algo não está marcado, não é para fazer , certo?" e "tem que ter certeza
  que o programa vai procurar as figuras mesmo com a opção desmarcada e que não vai remarcar ela de novo
  na caixinha" (não quebrar cadernos, margens, gravuras).
- **D-068.** "Toda função automática tem botão de ligar e desligar."
- **D-004.** "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas
  mexidas." (não quebrar)
- **D-002.** O Automático roda no livro todo, nas escolhidas, numa página (não quebrar).
- **Regra 7 (27/10): só o que ele mandou.** Nada de texto, botão ou comportamento novo. As etapas 2, 3 e
  4 só são OLHADAS (achados para o Samuel), sem conserto.

## Andamento

- [x] Li implementador.md, CLAUDE.md §11, D-002, D-004, D-068, D-589, D-590.
- [ ] Causa.
- [ ] Teste de reversão (falha em 8846017).
- [ ] Conserto.
- [ ] Testes no PC (um por vez).
- [ ] Olhar Endireitar, Cortar, Limpar (achados).
- [ ] Print da janela grande reaberta.
- [ ] GitHub: conjunto inteiro + botões; filtro de velocidade.

## Perguntas para o Samuel

(nenhuma por enquanto)
