# Recados entre janelas

Regra do Samuel de 19/10/2026 ("C: chefe + bilhetes"; `CLAUDE.md` §4.8).

- Os agentes entregam sempre à gerente. Outras janelas do Claude Code no PC podem mandar recado direto à gerente
  (SendMessage). **Se a gerente estiver fechada, o recado vem para esta pasta.**
- Nome do arquivo: `<data>-<origem>.md`, por exemplo `2026-10-20-janela-renomeador.md`.
- Dentro: de qual janela veio, a data e a hora (relógio do PC, UTC-4), e **as palavras literais do Samuel** entre
  aspas, nunca um resumo.
- A gerente lê esta pasta ao abrir, **repete o recado ao Samuel** e só muda o plano depois do "sim" dele.
- Depois de tratado, o recado fica anotado em [conferencias.md](../conferencias.md) e na ficha do item
  (pasta [itens/](../itens/)), com a data e a origem. O arquivo do recado não se apaga: ganha no fim uma linha
  "Tratado em <data>: <onde foi anotado>".
