# Relatório para o Fable: o Editor de Impressão, o atualizador, os testes à distância e o jeito de trabalhar

23/11/2026. Montado pela conversa gerente do projeto.
- As Partes 1, 2 e 3 foram escritas por dois agentes que só leram o código.
- A Parte 4 foi escrita pela gerente.
- Ninguém mudou código para fazer este relatório.

**Para que serve.** O dono do projeto, o Samuel, quer uma opinião de fora. A conclusão dele: faz um mês que cada
volta de conserto cria erros novos e obriga a refazer o caminho, e cada vez que isso acontece se escreve uma regra
nova. As perguntas estão na Parte 5.

**Como ler.** Fato e opinião estão separados: a opinião fica no fim de cada parte, marcada. Cada fato aponta o
arquivo e a linha num link fixo do GitHub, num commit que não muda. O que o autor não conferiu está escrito "não
conferi".

---

# Parte 0. Onde está cada coisa

## O repositório

- GitHub, público: https://github.com/Samuel-Bottini-BR/EditorImpressao
- No PC do Samuel: `D:\programas\EditorImpressao`, com um worktree por trabalho em `.claude\worktrees\`.

| Ramo | Commit lido | O que é |
|---|---|---|
| `obra-2026-10-26` | `0f58346a` | **a versão de teste**, o programa de hoje (Parte 1); é onde está o Livro de decisões que vale |
| `atualizador-4-consertos-2026-11-21` | `aa1963b7` (código), `046c0271` (relatório 3) | o atualizador e os testes à distância (Partes 2 e 3); ainda não juntado |
| `fase-1` | `47394b4a` | a versão oficial: tem o plano e o histórico; o código dela parou em 23/10 |

## A árvore das pastas e as dependências

Estão no anexo "Árvore, dependências e montagem do .exe", no fim deste relatório.

## Os documentos

| O quê | Caminho | Observação |
|---|---|---|
| Regras do projeto | `CLAUDE.md` | 71 KB |
| Regras de cada agente | `.claude/agents/*.md` | 4 arquivos |
| Livro de decisões | `docs/plano/DECISOES.md` no ramo `obra-2026-10-26` | 618 KB; D-001 a D-829 |
| Plano (fases, Lista de bugs, Registro) | `docs/plano/PLANO-DEFINITIVO.md` no `fase-1` | 395 KB |
| Estado atual | `docs/plano/ESTADO-ATUAL.md` no `fase-1` | |
| Memória por assunto | `memoria/INDICE.md`; o catálogo de erros em `memoria/catalogo-de-erros.md` | o catálogo só no `obra-2026-10-26` |
| Histórico das sessões | `historico/Editor de Impressao - resumo para o Claude.md` | 784 KB, a PARTE mais nova no topo |
| O porteiro (barreira automática) | `regras_dos_agentes/` e `tests/conferencias_excecoes.json` | ver Parte 4 |
| Relatórios do atualizador | `relatorios/atualizador-4/` (ONDE-PAREI e `quem-quebrou/relatorio-1..3`), no ramo do atualizador | |
| Revisão de código de 10/11 | ramo `revisao-codigo-2026-11-10`, `relatorios/revisao-codigo-2026-11-10/relatorio.md` | os 17 remendos |
| Revisões de 18/11 | ramos `revisao-atualizador-2026-11-18` e `revisao-distancia-2026-11-18` | |

## O que não está no GitHub

- **A Central de decisões e as outras páginas de conferência.** São páginas do claude.ai e só abrem na conta do
  Samuel. O código delas não está no git.
- **A cópia do plano que o Samuel edita**, em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\`.
- **Os livros de teste**: nove livros e 2.903 folhas, que ficam fora do git.
- **As redes neurais** (`modelos/`).
- **Os comandos `/projeto` e `/checkpoint`**, que ficam na pasta do Claude Code do Samuel.

---

# Parte 5. O que queremos que você responda

1. **O atualizador e os testes à distância estão complicados demais?** A Parte 2 mostra que quase tudo vem de uma
   escolha: quem troca a versão é uma tarefa SYSTEM que roda o próprio `.exe` instalado. Dado o que o Samuel pediu
   (Parte 2.1, principalmente D-733 e D-736), qual seria o desenho mais simples? Vale a pena refazer, ou consertar os 5
   problemas e seguir?
2. **Por que o ciclo se repete?** A seção 4.8 descreve o mesmo padrão em seis casos. Qual é a causa de verdade: o
   código (regras espalhadas numa tela de 10 mil linhas, PowerShell montado como texto), o jeito de trabalhar (pedido
   por caso, conserto por volta, regra nova a cada falha) ou os dois?
3. **O jeito de trabalhar está pesado demais?** Cada agente lê cerca de 95 KB de regras antes de começar, e o Livro tem
   mais de 800 decisões. O que você cortaria, e o que manteria? O agente novo que tenta quebrar é o que mais acha
   defeito.
4. **O porteiro existe e não pegou o problema.** Como deixar essa barreira útil de verdade? Ampliar as palavras, diminuir
   as 164 exceções, ou outro tipo de conferência?
5. **Os 16 remendos conhecidos do programa** continuam no código, congelados até a entrega ao Kaique. Isso deve mudar de
   ordem?
6. **Algo que não perguntamos** e que você faria diferente.

**Como responder.** Sua resposta vai para a gerente, que vai explicar ao Samuel em português simples e levar as
escolhas a ele. Separe o que é certeza do que é palpite. Diga também o que você precisaria ler a mais para ter
certeza.
