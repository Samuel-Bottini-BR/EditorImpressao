# ONDE PAREI — etapa 5 (verificador)

## 17/11/2026, fases 0 e 1: PARADO no passo A2, antes da fase 0

Cópia `.claude/worktrees/etapa5`, ramo `etapa5-2026-11-17`, a partir de `a9d81030` (obra-2026-10-26). Sem push.

### Decisões que esta tarefa precisa cumprir
- D-722 "Sim" (testar no PC dele e desfazer tudo, com a lista do que foi desfeito).
- D-737 "ok" (o Samuel clica "Sim" nas perguntas do Windows e fotografa a primeira).
- D-738 "ok" (cópia de reserva da pasta dos projetos no D: antes da etapa 5; a original não é tocada).
- D-729 "pode" (o Editor antigo de 01/09 pode sair depois). D-730 "k" (o instalador antigo fica de reserva).
- D-724 (assinatura: só a chave do Samuel), D-713 (nada vai ao GitHub nesta etapa), D-727 (tudo dentro do instalador).

### O que já está escolhido e testado aqui
Nenhum código nem teste foi mudado. Só se mexeu nesta pasta (lista.md, comandos.md, relatório, este arquivo).

### Como fica para quem usa e no livro
Nada muda para o Kaique nem no PDF por esta tarefa. O achado abaixo muda o que ele teria no computador (pasta dos
projetos), se não for tratado antes de mandar o programa.

### Feito
- [x] A2: os nomes de verdade conferidos no código e escritos na `lista.md` e na `comandos.md`.
- [x] Relatório `relatorio.md/.html/.pdf` nesta pasta.

### PARADA (ordem da gerente: "se for dentro de %LOCALAPPDATA%\EditorImpressao, pare e avise")
O Velopack, quando o processo que roda não consegue gravar na pasta do programa (a janela do Kaique, sem
administrador, em Arquivos de Programas), usa `%LOCALAPPDATA%\EditorImpressao\packages` e copia o `Update.exe` para
`%LOCALAPPDATA%\EditorImpressao\`. Cria a pasta na hora em que o gerente do Velopack é montado
(`atualizacao.versao_que_roda`, chamado pelo aviso de versão nova). O `LocalAppData` vem do Windows
(`SHGetKnownFolderPath`), então trocar a variável `LOCALAPPDATA` no teste não protege a pasta do Samuel.
Fontes: `locator.rs` e `known_path.rs` do Velopack (ramo develop) e as mesmas frases dentro do `velopack.pyd` 1.2.161
do `.venv`. Não testado: se desinstalar apaga essa pasta.

### Não feito (por causa da parada)
- Fase 0: fotos (sem e com administrador), cópia de reserva (D-738), conferências rápidas.
- Fase 1: versões 1.1.0 a 1.1.5 e o servidor de mentira.
- Nenhuma pergunta do Windows, nada instalado, nenhum `fonte-de-teste.txt`.

### Para retomar (quando a gerente mandar)
- A fase 1 precisa: junção `modelos` → `D:\programas\EditorImpressao\modelos`; o motor do Kraken e o `DOWNLOADS`
  de `D:\programas\EditorImpressao-arquivos\ferramentas\` (o `empacotar.py` procura em `RAIZ.parent`, que na cópia é
  `.claude\worktrees`); a 1.1.0 pelo caminho inteiro do publicar (o `--pasta-pronta` não põe o Visual C++).
- Cópia de reserva: o pedido manda `D:\programas\EditorImpressao-arquivos\<data>\`; a `lista.md` C1 diz
  `$TRAB\reserva-dados-do-samuel`. Vale o pedido da gerente.

### Sobras encontradas (não apagadas)
- `%LOCALAPPDATA%\velopack\velopack_EditorImpressaoEnsaio.log` (ensaio da etapa 3).

### Perguntas para o Samuel
Fica com a gerente: o que fazer com a pasta de reserva do Velopack dentro da pasta dos projetos, antes da fase 0.
