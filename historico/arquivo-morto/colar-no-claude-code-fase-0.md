# Colar no Claude Code — Fase 0

*(arquivado em 07/09/2026: este é o prompt de kickoff que originou a Fase 0
do `PLANO-RETOMADA.md`. Os itens 1 e 2 já foram executados nesta mesma sessão
— ver `CLAUDE.md` seção 9 para o relatório da investigação. Mantido aqui como
registro, com o caminho já corrigido para o local atual do projeto.)*

Abra o Claude Code na pasta `D:\programas\EditorImpressao` e cole o texto
abaixo, da linha tracejada até o fim.

Antes de colar, copie para a raiz do repositório os dois arquivos que estão
junto deste: **`CLAUDE.md`** e **`PEDIDOS.md`**.

---

Estamos retomando o Editor de Impressão depois de um mês parado. Leia o
`CLAUDE.md` na raiz antes de qualquer coisa — ele mudou, e as regras de teste
são novas.

O resumo do que mudou: eu (Samuel) passo a testar cada funcionalidade eu mesmo,
uma por vez, e a lista de conferência vive no `PEDIDOS.md`. Você pode marcar
"PRONTO PARA CONFERIR", nunca "APROVADO".

Esta é a **Fase 0**, e ela tem um objetivo só: **garantir que o programa que eu
abro é o programa que você alterou.** Isso é o problema número um do projeto — na
última verificação eu abri o programa e vi a tela antiga, sem barra de menu, com
uma barra preta que você já tinha corrigido. Enquanto isso não estiver
resolvido, meu teste não vale nada e nenhum desenvolvimento novo faz sentido.

Faça estas três coisas, nesta ordem:

**1. Encontre a causa da tela antiga.**
Varra o computador atrás de cópias duplicadas da pasta do projeto, de `.exe`
antigos, de pastas `build/` e `dist/` sobrando, e de atalhos apontando para
lugares diferentes. Me traga a lista do que achou, com o caminho e a data de
cada um. Não apague nada ainda — me mostre primeiro.

Confira também a hipótese de tela nova criada sem o programa carregá-la — foi o
que aconteceu com o `projetos.py`, que ficou pronto sem chamador. Verifique se
todas as telas novas estão realmente ligadas ao fluxo do programa.

**2. Crie um atalho na minha Área de Trabalho que roda direto do código.**
Chame de "Editor de Impressao (desenvolvimento)". Deve rodar
`.venv\Scripts\pythonw.exe main.py` a partir da pasta do projeto, para eu abrir
sempre a versão mais nova, sem reconstruir nada.
Cuidado com o caminho: **caminho de disco sem acento**, mesmo que a Área de
Trabalho esteja no OneDrive.

**3. Amplie o teste de tela que já existe.**
Já existe `teste_interface.py`, que dirige a interface de verdade e salva
capturas. **Não refaça — amplie.** Ele precisa: abrir o programa, clicar em
**todos** os botões de **todas** as telas, redimensionar a janela em vários
tamanhos, e reportar qualquer travamento ou exceção. Se pytest-qt facilitar,
use; se o que já existe der conta, aproveite.

Esse teste teria pego sozinho o travamento que eu reportei em 18/07, quando o
programa fechava ao clicar nos botões da tela de conferir. Deixe ele rodando
junto com os testes que já existem em `tests/`.

Me diga também **quantos testes existem hoje de verdade** — os documentos
divergem: um diz 59, outro diz 150.

**Regras para esta fase:**

- Uma mudança por vez. Antes de alterar um arquivo, me mostre o diff e espere eu
  confirmar.
- Não reescreva nada que funciona. Testar não é permissão para reconstruir.
- Português comum, sem jargão. Primeiro a frase que se entende, depois o número.
- Seja conciso no chat; o detalhe vai para arquivo.

**Quando terminar**, me diga em poucas linhas:

1. O que você achou de cópias duplicadas e qual é a causa provável da tela
   antiga
2. Que o atalho está criado e onde
3. Se o teste de tela achou algum travamento

E marque no `PEDIDOS.md` só o que for teste de máquina. O primeiro item do Bloco
1 — "abrir pelo atalho e ver a tela nova" — é meu, e eu marco.
