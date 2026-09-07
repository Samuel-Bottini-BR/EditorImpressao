# Editor de Impressão

Recupera PDFs de livros antigos escaneados e prepara para reimpressão em
cadernos. Projeto do Pe. Rosenei, instituto de preservação de livros.

**Quem usa é o Kaique, impressor, sem formação técnica.** Toda a interface é em
português do Brasil, sem jargão. Duas versões anteriores fracassaram — uma
travava, a outra dava qualidade ruim — e daí vêm as regras rígidas abaixo.

## Regras que não se negociam

- **PySide6**, nunca tkinter. Foi o que travou a versão anterior.
- **Uma página por vez na memória.** Ler, processar, escrever, soltar. O pico
  não pode crescer com o tamanho do livro; há livro de 300 MB no acervo.
- **Nenhum emoji em rótulo de interface.**
- Textos de interface **com** acento (UTF-8). Caminhos de disco **sem** acento.
- Algoritmo consagrado em vez de fórmula própria. Sauvola vem do DoxaPy.
- **Nenhum modelo generativo.** Modelo que produz pixel pode inventar detalhe
  numa gravura de 1579, e detalhe inventado entra no PDF como se fosse o livro.
  Rede neural aqui só segmenta: aponta onde estão as coisas, nunca desenha.

## Todo relatório sai em três formatos

O Samuel **não abre `.md`** — o Acrobat recusa o arquivo. Relatório que a pessoa
não consegue abrir não é relatório.

Use `relatorio.gravar(texto, destino)`, que grava os três de uma vez:

| | para quem |
|---|---|
| `.md` | para mim, e para o git comparar linha a linha |
| `.html` | leitura rápida, abre com dois cliques no navegador |
| `.pdf` | arquivo e referência futura |

Nunca gravar só o `.md`.

## Onde guardar um teste

Use `relatorio.pasta_de_teste(assunto, filtro)`, que produz:

```
D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\
    MAGICO PRO\
        2026-08-01 14h30 - contraste local no papel
    PRETO E BRANCO\
        2026-07-30 22h52 - comparacao dos 18 binarizadores
        2026-07-31 07h25 - rubricacao vermelha preservada
```

**O filtro é uma pasta de verdade**, não um pedaço do nome. Assim tudo do
Mágico pro fica junto e dá para percorrer a história de um filtro só. Dentro
dela, data e hora no começo ordenam sozinho e deixam comparar duas rodadas do
mesmo dia.

Dentro de cada teste vai sempre `o que foi testado.pdf`, contando o que estava
errado, como foi descoberto, o que mudou, o resultado medido e qual imagem
abrir primeiro. A pasta precisa se explicar sozinha daqui a seis meses.

## Antes de julgar qualquer resultado visual

Leia a skill `conferir-testes-visuais`. Resumo: **abra todas as imagens antes
de dizer que funcionou.** Percentual não é veredito, e expectativa escrita por
quem implementou não é critério de acerto. Esta regra existe porque eu já
reportei "10 de 10 corretas" tendo olhado uma imagem — seis estavam erradas.

## Antes de mudar qualquer filtro

O protocolo do projeto exige medir antes. `avaliar.py` roda sobre o acervo e
grava `relatorios/`. Uma mudança por vez, remedir, e reverter se qualquer
número piorar. Se achar que valeu a pena mesmo assim, não reverter por conta
própria: apresentar os dois resultados ao Samuel.

O histórico de tentativas, incluindo as revertidas e os caminhos descartados,
está em `relatorios/melhorias.md`. Leia antes de propor algo que já foi testado.

**Número que piora não é a única prova de estrago, e número que melhora não é
prova de acerto.** Duas vezes a régua reprovou coisa que estava certa — letra
entupida numa página sem letra, borda serrilhada numa letra redonda — e uma vez
ela aprovou uma folha que saía amarelo-forte, porque mais amarelo pode ser mais
claro. Antes de aceitar um veredito da régua, abra a página e olhe.

## Fronteira de autonomia

**Pode decidir sozinho:** limiar, janela, `k`, `clipLimit`, tamanho de bloco,
ordem interna de operações dentro de um filtro, troca de algoritmo de
binarização, cache, paralelismo, memória.

**Precisa perguntar antes:** criar ou remover filtro, mudar nome de filtro,
mudar qualquer tela, acrescentar ou tirar controle da interface, mudar o
formato dos arquivos de dados, alterar desfazer/refazer, trocar biblioteca.

## Como rodar

```
.venv\Scripts\python.exe main.py                      # o programa
.venv\Scripts\python.exe -m pytest tests -q           # os testes
.venv\Scripts\python.exe avaliar.py                   # a régua, sobre o acervo
.venv\Scripts\python.exe teste_robustez_completo.py   # os 18 casos de falha
```

Acervo de teste: `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE
IMPRESSAO\LIVROS PARA TESTE`, nove livros. Mudou da área de trabalho para lá em
07/09/2026 — o `avaliar.py` acha sozinho, com o novo caminho já na lista de
candidatos; não passar `--acervo` à toa.

As queixas do Kaique ficaram na pasta antiga, agora em
`D:\programas\EditorImpressao-arquivos\BIBLIOTECA DO FIM DOS TEMPOS\Teste de
livros`: são os `.txt` soltos nas subpastas, cada um com o print ao lado.
**São fonte de requisito**, e é a única coisa que sobrou lá — os PDFs mudaram
de lugar.

**Os PDFs do acervo são intocáveis.** Abrir somente para leitura, e gravar
sempre fora dessa pasta.

## Onde estão as coisas

- `core/filtros.py` — os três filtros e o Original
- `core/selecao.py` — onde cada tratamento vale dentro da página
- `core/detectar_regioes.py` — acha gravura, letra e papel sozinho
- `core/pipeline.py` — a ordem: dividir, cortar, endireitar, filtrar, impor
- `avaliar.py` — a régua
- `modelos/` — pesos de rede neural, fora do repositório
- `historico/` — os pedidos e handoffs de todas as conversas, incluindo a
  conversa gênesis (a versão antiga em customtkinter que travava)

**Handoff:** `historico/Editor de Impressao - resumo para o Claude.md` é o
mais completo e atualizado — leia primeiro numa sessão nova. Só atualize
esse arquivo (ou crie um novo) quando o Samuel pedir explicitamente.

## Commit e push regulares

Este repositório tem GitHub remoto (`origin`, https://github.com/Samuel-Bottini-BR/EditorImpressao).
Faça commit do progresso relevante regularmente e dê `git push` — não é
preciso perguntar cada vez, mas sempre revise o que está sendo commitado
antes (nunca commitar segredo, nunca desfazer o `.gitignore` sem avisar).
