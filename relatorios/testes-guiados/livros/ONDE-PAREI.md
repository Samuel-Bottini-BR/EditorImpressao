# Testes com os livros â€” onde parei

Ramo `testes-livros-2026-10-23` (a partir do `fase-1` em `1ba93cf`). Nenhuma linha do programa muda.

- Roteiro que pilota a janela: `roteiros/percurso.py` (uma configuraÃ§Ã£o por livro em `roteiros/configs/`),
  rodado por `roteiros/rodar.ps1 <livro>` (guarda o PID em `testes-livros-saida\<livro>\pid.txt`).
- SaÃ­das grandes (prints inteiros, PDFs): `D:\programas\EditorImpressao-arquivos\testes-livros-saida\<livro>\`.

## Andamento

| Livro | SituaÃ§Ã£o |
|---|---|
| BoÃ©cio | atÃ© o fim â€” `boecio.md` |
| Palatino | até o fim — `palatino.md` |
| Righetti | em andamento |

## Aviso sobre a tela do Samuel (23/10, 17:48â€“18:11)

Nas primeiras rodadas do BoÃ©cio a janela "Antes de processar" (e por um instante a de escolher o PDF) **apareceu na
tela do Samuel**, no canto de cima Ã  esquerda: o Qt pÃµe a janela de aviso dentro da tela depois de aberta, e o
cuidado herdado do mapa sÃ³ agia antes. Fechei sÃ³ os meus processos (pelo PID guardado). Conserto no roteiro
(`roteiros/base.py`): toda janela nova vai para fora da tela no Show, no Move e num relÃ³gio de 20 ms; testado (zero
apariÃ§Ãµes na tela).

## Perguntas para o Samuel

(nenhuma por enquanto)

