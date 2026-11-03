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
- [x] Causa (abaixo).
- [x] Teste de reversão `tests/test_dividir_desmarcada_caixinha.py` (3 testes): os 3 FALHARAM em 8846017
      (`assert 'ligada no livro todo' == 'desligada'`; `dividir_folhas` continuava True). Passam no novo.
- [x] Conserto (commits `0f8663d` e `51edcca`: o "só cadernos" conta a página que é metade de folha dividida;
      a 1ª versão olhava só `folha.dividir`, que é True de fábrica, e quebrava `test_core::test_caminho_rapido_so_com_cadernos`).
- [x] Prova da D-590 em `tests/test_decisoes_juntar_todas.py::test_d590_dividir_desmarcada_a_caixinha_continua_desmarcada`
      (falha em 8846017, passa no novo).
- [x] Testes no PC (um por vez): test_decisoes_montar_cadernos 13, test_decisoes_juntar_todas 4,
      test_decisoes_automatico 24, test_decisoes_dividir 19, test_dividir_no_programa 19, test_core 62,
      test_dividir_desmarcada_caixinha 3: todos passaram.
- [x] Olhar Endireitar, Cortar, Limpar: achados em `relatorio.md` (o mesmo defeito; e Gravuras desmarca sozinha).
- [x] Prints da janela grande reaberta: `2-…`, `3-…` (pasta de dados isolada `_tmp/dividir-caixinha-dados`).
- [ ] GitHub: conjunto inteiro + botões (rodada 41690519031); filtro de velocidade (41689838943). Em andamento.

## Causa

`core/automatico._desligar_as_desmarcadas` deixava o Dividir de fora de propósito (`DESLIGAM_DESMARCADAS` só com
Gravuras, Margens, Cadernos: "Dividir desligado juntaria as folhas de novo"). Então `Projeto.dividir_folhas` (o
"ligada no livro todo" do Dividir) continuava True depois do Rodar; o painel relê o livro
(`ui/automatico.EstadoDoAutomatico.do_projeto` → `A.etapas_ligadas` → `ligada_no_livro`), a caixinha volta marcada
e a frase, que sai das marcadas, diz "Vou dividir as folhas".

## Conserto

1. `core/automatico.py`: `DESLIGAM_DESMARCADAS` ganha o DIVIDIR + docstrings de `_desligar_as_desmarcadas` e de
   `Pedido.desmarcadas`. O desligar grava só `dividir_folhas = False` (o ramo `else` que já existia); **nenhuma folha
   é tocada** (`ConfigFolha.dividir` e as páginas ficam). Longe de `_dividir`, `paginas_mexidas` e `pular`.
2. `modelos.py`, `Projeto.so_cadernos`: `and not any(f.dividir for f in self.folhas)`. Sem isso, com o Dividir
   desligado e só "Montar cadernos", o caminho rápido montava os cadernos com as folhas cruas do PDF (juntava as
   folhas: medido, 2 folhas de 1152 pt no lugar de 4 de 576 pt). O teste 3 prova.

## Perguntas para o Samuel

(nenhuma por enquanto)

- P1 e P2 do `relatorio.md` (achados das etapas 2-4 e da etapa 5). Não consertei: esperam a decisão dele.
