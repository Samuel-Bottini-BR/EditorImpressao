# Testes com os livros — onde parei

Ramo `testes-livros-2026-10-23` (a partir do `fase-1` em `1ba93cf`). Nenhuma linha do programa muda.

- Roteiro que pilota a janela: `roteiros/percurso.py` (uma configuração por livro em `roteiros/configs/`),
  rodado por `roteiros/rodar.ps1 <livro>` (guarda o PID em `testes-livros-saida\<livro>\pid.txt`).
- Saídas grandes (prints inteiros, PDFs): `D:\programas\EditorImpressao-arquivos\testes-livros-saida\<livro>\`.

## Andamento

| Livro | Situação |
|---|---|
| Boécio | até o fim — `boecio.md` |
| Palatino | até o fim — `palatino.md` |
| Righetti | até o fim, mas sem dividir (trava) — `righetti.md` |
| Siebmacher | até o fim — `siebmacher.md` |
| Pesel | até o fim — `pesel.md` |
| Matemática | até o fim — `matematica.md` |
| ljs47 | processado (montar não feito: janela minimizada por fora) — `ljs47.md` |
| Valadés | até o fim — `valades.md` |
| Escola de Jesus | até o fim — `escola.md` |
| Cursus | até o fim — `cursus.md` |
| Marial (folhas 1–200) | até o fim — `marial.md` |
| Horas (folhas 1–100) | até o fim — `horas.md` |
| Graduale (folhas 200–300) | até o fim — `graduale.md` |
| Antiphon (folhas 1–120) | até o fim — `antiphon.md` |

**Tudo feito.** Resumo: `resumo.md` (e `.html`, `.pdf`; cópia em `D:\programas\EditorImpressao-arquivos\testes-livros-relatorio\`).

## Aviso sobre a tela do Samuel (23/10, 17:48–18:11)

Nas primeiras rodadas do Boécio a janela "Antes de processar" (e por um instante a de escolher o PDF) **apareceu na
tela do Samuel**, no canto de cima à esquerda: o Qt põe a janela de aviso dentro da tela depois de aberta, e o
cuidado herdado do mapa só agia antes. Fechei só os meus processos (pelo PID guardado). Conserto no roteiro
(`roteiros/base.py`): toda janela nova vai para fora da tela no Show, no Move e num relógio de 20 ms; testado (zero
aparições na tela).

## Perguntas para o Samuel

(nenhuma por enquanto)
