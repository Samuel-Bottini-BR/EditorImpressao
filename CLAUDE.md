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

Acervo de teste: `Desktop\BIBLIOTECA DO FIM DOS TEMPOS`, nove livros. Os `.txt`
soltos nas subpastas são queixas do Kaique e são fonte de requisito.

**Os PDFs do acervo são intocáveis.** Abrir somente para leitura, e gravar
sempre fora dessa pasta.

## Onde estão as coisas

- `core/filtros.py` — os três filtros e o Original
- `core/selecao.py` — onde cada tratamento vale dentro da página
- `core/detectar_regioes.py` — acha gravura, letra e papel sozinho
- `core/pipeline.py` — a ordem: dividir, cortar, endireitar, filtrar, impor
- `avaliar.py` — a régua
- `modelos/` — pesos de rede neural, fora do repositório
