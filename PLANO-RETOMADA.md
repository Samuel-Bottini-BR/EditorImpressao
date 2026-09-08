# Plano de retomada — Editor de Impressão

07/09/2026. O projeto estava parado desde 08/08/2026.

---

## O diagnóstico, curto

**O projeto não parou por falta de código.** São 57+ commits, centenas de
testes passando, quatro filtros, sete ferramentas de seleção, instalador,
projetos salvos. É muito trabalho feito.

**Parou porque nada disso chegou até você.** Três fatos, e juntos eles explicam
tudo:

1. **Zero itens aprovados por você em 57+ commits.** Tudo marcado "feito" foi
   julgado pelo próprio Claude Code.
2. **Você abriu o programa e viu a tela antiga** — sem barra de menu, com a
   barra preta que já tinha sido corrigida. Ou seja: o programa que você abre
   pode não ser o programa que foi alterado.
3. **A régua não pega o pior defeito.** `avaliar.py` dá número bom enquanto a
   mancha do verso piora. Passa no teste e sai errado.

O risco de retomar sem consertar isso: mais 57 commits e a mesma sensação de não
sair do lugar.

**Atualização de 07/09/2026, depois de investigar a Fase 0:** o item 2 já foi
investigado — não há tela legada no código-fonte atual (o `main.py` só tem um
caminho, e a barra de menu é montada sempre). A causa mais provável é ter
rodado um dos instaladores `.exe` antigos que ficaram soltos na área de
trabalho, construídos numa janela de tempo específica (depois da barra
quase-preta, antes da barra de menu). Esses `.exe` já foram arquivados. Ver
`CLAUDE.md`, seção 9, para o relatório completo.

---

## As duas decisões que mudaram o plano

Nesta conversa você decidiu duas coisas, e elas são a espinha do plano:

**1. Você mesmo testa cada funcionalidade** — melhorada, adicionada ou
modificada. Uma por vez, com PDFs diferentes, aprovando, mandando melhorar ou
descartando.

**2. O Claude Code também testa, para acelerar** — mas com uma linha no meio.

Essa linha é a parte mais importante do plano:

| Tipo de teste | Exemplo | Quem decide |
|---|---|---|
| **Máquina** | O programa fecha ao clicar? Sumiu alguma página? A memória cresce? | O Claude Code, sozinho |
| **Olho** | O papel saiu branco? O desenho ficou perfeito? O corte está no lugar? | **Só você** |

O Claude Code roda em todos os PDFs, abre **todas** as imagens, monta o
`para-conferir.html` com a opinião e as ressalvas dele — e para.
**A aceleração é essa: ele vasculha 2903 folhas para você olhar 15.**

E a regra que mantém isso honesto:

> O Claude Code pode escrever **"PRONTO PARA CONFERIR"**. Nunca **"APROVADO"**.

---

## As 5 fases

### Fase 0 — Fazer o programa que você abre ser o programa de verdade

**Nada avança enquanto isso não estiver de pé.** Se o que você abre não é o que
foi mudado, seu teste não vale nada — você reprovaria um conserto que existe.

O que o Claude Code faz:

1. Cria um **atalho na sua Área de Trabalho** que roda o programa direto da
   pasta do projeto (`.venv\Scripts\pythonw.exe main.py`). Sempre a versão mais
   nova, sem reconstruir nada.
2. **Varre o computador atrás de cópias duplicadas** da pasta do projeto e de
   `.exe` antigos, e lista o que achou.
3. Monta o **teste de tela automatizado**: abre o programa, clica em
   **todos** os botões de **todas** as telas, redimensiona a janela em vários
   tamanhos, e reporta qualquer travamento.

**Como você testa:** clica no atalho. Se abrir com barra de menu no topo, deu
certo. Se abrir a tela antiga de quatro linhas de botões, achamos a cópia
fantasma — e aí sim consertamos, antes de qualquer outra coisa.

> O teste de tela vale o investimento porque o travamento que você reportou em
> 18/07 (o programa fechando ao clicar nos botões da tela de conferir) era
> exatamente desse tipo. Uma vez construído, roda de graça a cada mudança.

**Status em 07/09/2026: Fase 0 concluída, os três itens.**
- Item 1 (causa da tela antiga): investigado — ver `CLAUDE.md` seção 9.
- Item 2 (atalho de desenvolvimento): criado na área de trabalho.
- Item 3 (clicar em tudo, redimensionar, reportar travamento): `teste_botoes.py`
  agora cobre todas as telas (antes só a de conferir) — 118 ações, 0 falhas,
  rodado de verdade contra um PDF sintético isolado (nunca use um livro do
  acervo real aqui: cada um já tem projeto de rodada de teste anterior, e a
  limpeza no fim apagaria esse histórico — o próprio script gera o PDF de
  teste sozinho se você não passar nenhum).

---

### Fase 1 — Escolher os cinco PDFs de teste

Fixos, sempre os mesmos, para o resultado ser comparável entre um dia e outro.
Cada um representa um problema diferente:

1. **Folha dupla amarelada** — o caso mais comum
2. **Capa colorida** — onde os filtros estragam mais
3. **Página com gravura** — onde a seleção precisa acertar
4. **Folha quase transparente** — a mancha do verso, o pior defeito
5. **Scan ruim, baixa resolução** — o Boécio, para saber o que não dá para
   recuperar

**Como você testa:** os cinco abrem sem erro. Os nomes vão para o topo do
`PEDIDOS.md`.

---

### Fase 2 — O caderno de conferência (`PEDIDOS.md`)

Já está pronto, no arquivo ao lado. São **cerca de 80 itens** em 10 blocos, cada
um com: o que fazer · o que esperar · quem confere · como marcar.

Cinco estados: pendente · pronto para conferir · **APROVADO** · melhorar ·
descartado.

**"Descartado" é opção de verdade.** Pode ter coisa ali que ninguém precisa, e
tirar da lista é ganho, não perda.

---

### Fase 3 — `CLAUDE.md` na raiz do repositório

Já está pronto, no arquivo ao lado. Suas regras fixas + o contexto do programa +
os dois tipos de teste + a fronteira de autonomia + os defeitos já conhecidos,
para ninguém redescobrir o que já foi medido.

---

### Fase 4 — A varredura, bloco por bloco

Nesta ordem — a ordem do que o Kaique usa todo dia. Se você parar no meio, já
terá coberto o que mais importa:

| Ordem | Bloco | Itens | Você olha |
|---|---|---|---|
| 1 | Abrir e carregar | 15 | 8 |
| 2 | Dividir folhas | 8 | 7 |
| 3 | Cortar e endireitar | 8 | 7 |
| 4 | **Os filtros** | 24 | 22 |
| 5 | Alertas | 7 | 5 |
| 6 | Seleção | 16 | 15 |
| 7 | Cadernos | 6 | 5 |
| 8 | Salvar e instalar | 16 | 13 |
| 9 | As queixas do Kaique | 10 | 10 |
| 10 | O veredito do CamScanner | 1 | 1 |

**Um bloco por sessão.** Você marca cada item. O que virar "melhorar" eu
transformo em tarefa para o Claude Code — **uma por vez**, com diff antes de
mexer.

Sugestão: comece pelo bloco 1 e pelo bloco 4. O bloco 1 porque, se o programa
não abrir certo, nada mais vale. O bloco 4 porque os filtros são o coração do
programa e é onde estão quase todos os defeitos abertos.

---

### Fase 5 — Git

- **Uma branch por conserto.** Se um conserto estragar outra coisa, dá para
  voltar sem perder o resto.
- `.gitignore` com `pdfs_teste/`, `build/`, `dist/`, `.venv/`, `relatorios/*.png`
- Cada commit com o defeito que resolveu escrito por extenso — isso já vinha
  sendo feito e é bom, manter.

---

## O ciclo de uma mudança

1. Você escolhe um item do `PEDIDOS.md`
2. O Claude Code mostra o diff e espera confirmação
3. Faz a mudança — **uma só**
4. Roda os testes de máquina
5. Roda a régua nos cinco PDFs; se qualquer número piorar, reverte ou apresenta
   os dois resultados
6. Abre **todas** as imagens
7. Monta o `para-conferir.html` com opinião e ressalvas
8. Marca `[?]` PRONTO PARA CONFERIR e te chama
9. **Você abre pelo atalho, testa, e marca `[x]`, `[~]` ou `[-]`**
10. Commit

---

## Um aviso honesto

São ~80 itens, e uns 60 precisam do seu olho. Isso é muita coisa — não dá para
fazer numa sentada, e tentar fazer numa sentada é o jeito mais rápido de
abandonar de novo.

**Uma sessão por bloco, no seu ritmo.** A tabela de histórico no fim do
`PEDIDOS.md` existe para você ver o projeto andando mesmo em dia de pouco tempo.

E se em algum bloco você descobrir que metade do que está marcado "feito" não
está de pé — isso não é fracasso, é o plano funcionando. É exatamente a
informação que faltava.
