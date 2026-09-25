# Editor de Impressão — ESTADO ATUAL (leia primeiro)

Escrito em 24/09/2026. A ordem de autoridade é:

1. este documento
2. `PLANO-DEFINITIVO.md` (o que fazer e em que ordem)
3. `CLAUDE.md` (regras técnicas)

O resto é histórico. O `PEDIDOS.md` virou histórico em 24/09: a lista que vale é o Plano Definitivo.

---

## 1. O que é o programa

Programa de Windows que restaura PDFs de livros antigos escaneados e monta os cadernos para reimpressão. Projeto do Instituto São Bento (Pe. Rosenei). Quem usa é o **Kaique**, impressor, sem formação técnica. Feito em Python + PySide6.
Código: `D:\programas\EditorImpressao` (GitHub `Samuel-Bottini-BR/EditorImpressao`). Material de apoio: `D:\programas\EditorImpressao-arquivos\`.

**O critério final, nas palavras do Samuel:** "Eu quero que o papel saia branco, e o desenho também saia perfeito."

## 2. O resultado que o Samuel quer (fonte: "Vamos recapitular...", 12/09/2026)

| # | Resultado | Página de exemplo |
|---|---|---|
| R1 | Papel branco, **letras e gravura intactas** (nada de amarelado) | Palatino p. 5, 7 e 9 |
| R2 | **Sumir com a mancha do verso** (texto da folha de trás) | Palatino p. 10 e Marial p. 862 |
| R3 | **Margens iguais em todas as folhas** / centralizar o texto, pensando na costura. Esquerda e direita diferentes | Palatino p. 57, Graduale p. 222-223, Horas p. 14 |
| R4 | Tirar manchas (vermelhas, marrons) **sem mexer no título** | Palatino p. 66 e 76 |
| R5 | Endireitar linhas tortas | Graduale p. 221, Escola de Jesus p. 7 |
| R6 | Manter cores de verdade (rubricação, iluminura, borda prata) | Horas p. 11, 13 e 47; Graduale p. 221 |
| R7 | Tamanho final A4, com margem certa para encadernar | Siebmacher p. 7 |
| R8 | Apagar em todas as páginas um texto repetido (ex.: endereço de site) | Escola de Jesus p. 7 |
| R9 | Seleção de letra / gravura / cor que funcione de verdade | TESTE 1 (Boécio) |

**OCR (mudou em 24/09):** volta ao plano na **Fase 1**, só para *achar onde está o texto* (fazer a máscara de tinta como o Internet Archive), não para transcrever. A transcrição fica na Fase 7.

## 3. Onde o projeto está de verdade (23/09/2026)

- **434 testes automáticos passando.** Isso só prova que "não quebra", não que "ficou bom".
- **Zero itens aprovados pelo Samuel.**
- **Tem trabalho sem commit desde 17/09** (~34 arquivos). O plano (Fase 0.1) manda guardar isso num ramo separado.
- Dos resultados R1-R9, **nenhum foi conferido e aprovado.**

### Por que o projeto parou

- O trabalho foi para a tela, não para a imagem.
- Muita coisa por vez; a sessão acabava antes do Samuel testar, e o trabalho acumulava sem commit.
- Testar era difícil: atalho antigo abrindo código velho, janelas antigas abertas.
- O plano mudava a cada conversa: 5 versões de handoff, ~110 itens, nenhum aprovado.
- O seletor de gravura foi **recriado** duas vezes a partir da descrição do ScanTailor (31/07 e 16/09) e falhou. O seletor **original** do ScanTailor, testado em 24/09, funciona bem melhor (ver `TESTE-SCANTAILOR-MISTO.md`).

## 4. Contradições resolvidas (o que vale hoje)

| Assunto | Vale hoje | Documentos antigos diziam |
|---|---|---|
| Pasta do código | `D:\programas\EditorImpressao` | `C:\Users\fotog\Desktop\EditorImpressao` |
| Licença | **GPL liberado** (17/09): se um dia distribuir, é grátis com código aberto | "nada de GPL", "ScanTailor não embutir" |
| Mancha do verso | **NÃO corrigida** | "feito e conferido" (PARTE 3 do resumo, **errado**) |
| Filtro padrão de página nova | **Original** | Preto e branco |
| Barra de rolagem | cinza médio `#a8a49e` (decisão adiada) | preta |
| Testes | 434 (`pytest tests -q`) | 51 / 59 / 150 / 279 / 349 |
| Stack | Python 3.14 + PySide6. **Nunca** tkinter/customtkinter | `Instalar_Editor_Impressao.md` e `genesis` usam customtkinter: **versão velha, ignorar** |
| Modo de trabalho | Conversa gerente + agentes (ver plano, seção 3) | "ir até o fim sem chamar" |
| Menu "Abrir" | corrigido (commit `9d27b76`) | "não corrigido" |
| Seletor de gravura do ScanTailor | **usar o código original** (decisão de 24/09) | recriar em Python a partir da descrição |

## 5. Não confundir com outro programa

O **ExtratorPDF** (em `D:\programas\Scan Tailor`) é **outro programa**, separado deste. Não misturar pastas nem pedidos. A pasta `D:\programas\Scan Tailor\Testes de ajuste\` guarda os testes do ScanTailor de 24/09.
