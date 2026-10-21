# Marial — "Marial de sermoens - Frei Balthasar Paez"

- Arquivo: `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE\Marial de sermoens - Frei Balthasar Paez. (1).pdf` (somente leitura).
- Tamanho: 214.631.915 bytes (~205 MB). Folhas: 907 (ficha de 18/07/2026).
- **É o livro do teste de velocidade**: o `teste_velocidade.py` usa um recorte de 300 folhas (`marial_300.pdf`, publicado no ramo `dados-de-teste`).

## Como ele é

| Pergunta | Resposta |
|---|---|
| Tem camadas? | Não (scan comum, uma imagem por página). |
| Borda preta de scanner? | Não; beirada escura em algumas páginas (p. 454). |
| Folha grande? | Não. |
| Moldura? | Não achada nas fontes. |
| Iluminura / cor? | Não: 0 de 907 páginas com tinta colorida. |
| Manuscrito? | Não (impresso). |
| Música? | Não. |
| DPI declarado errado? | **Sim: o PDF diz 72 DPI.** O programa usa ~93 DPI nas ferramentas do ScanTailor (`core.caixas_scantailor.dpi_para_as_caixas`). |
| Baixa resolução? | Sim ("qualidade BAIXA" na ficha de 18/07; "o livro inteiro foi escaneado em qualidade baixa"). |
| Livro aberto? | Não. |
| Outro | Papel bem amarelado e **translúcido**: o texto do verso aparece muito (verso 23,1%, o maior do acervo). Manchas e remendos. |

## Páginas de teste

- Gabarito: [7](../paginas-de-teste/marial-007.md) (R2, mancha do verso; item 6.1).
- Estudo do "Para revisar": [454](../paginas-de-teste/marial-454.md) (remendo e mancha tomados por gravura), [840](../paginas-de-teste/marial-840.md).
- Citadas de passagem: [146](../paginas-de-teste/marial-146.md) e [153](../paginas-de-teste/marial-153.md) (título tomado por gravura), [151](../paginas-de-teste/marial-151.md) (mancha de canto), [862](../paginas-de-teste/marial-862.md) (saiu do gabarito em 25/09). Também: p. 8 do "Vamos recapitular" ("cortar a lombada", não extraída, [lista.json](../../gabarito/lista.json) `pendencias`); páginas 575, 846, 906 nas imagens da ficha de 18/07.

## O que o programa faz bem ou mal nele

- **Mal / aberto:** a **mancha do verso** (R2, item 6.1, o defeito mais grave aberto; no Misto "o original ainda fica melhor para ler"); manchas que o detector toma por gravura saem em cor (p. 7, 454); papel não totalmente branco atrás do título (p. 153).
- **Velocidade:** abrir o livro de 300 folhas leva 50 a 60 s no PC do Samuel (em setembro, 25 a 44 s) — na Lista de bugs de 12/10/2026, causa não investigada. Aceito em 30/09: primeira prévia ~0,5 s mais lenta pelo detector do 1.2.

## O que o Samuel e o Kaique disseram

- Samuel, 05/10/2026, M7: "Nenhuma - o original ainda fica melhor para ler. Nesta folha o original continua guanhando, mas acredito que é porque tem um teto que o programa consegue atingir, gostaria de continuar proceguindo com testes para melhorar, mas não quero ficar preso nisso." ([conferência 8](../../relatorios/conferencia-samuel-2026-10-05-f.md))
- Samuel, 05/10/2026, RISCO: "Temos que ter uma opção para retirar essas manchas, não sei se o modo com o scantailor resolve isso, me responda sobre isso." ([conferência 10](../../relatorios/conferencia-samuel-2026-10-05-b.md))
- Kaique: o caso 4 dele ("a folha é tão antiga que ela já está quase transparente, então as letras da parte de trás acabam aparecendo") é exatamente o deste livro ([histórico, APÊNDICE B](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)); não cita o Marial pelo nome.

## Projetos salvos do Samuel

- Não achado nas fontes lidas (o Registro de 29/09 e a Lista de bugs de 29/09 não citam projeto do Marial).

## De onde veio

- Acervo desde 18/07/2026; ficha `LIVROS PARA FAZER TESTE (duplicata)\Marial de sermoens - Frei Balthasar Paez..txt`; [relatório por livro](../../relatorios/por-livro/Marial%20de%20sermoens%20-%20Frei%20Balthasar%20Paez.md). O "Vamos recapitular" o chama de "Livro 4", sem nome ([lista.json](../../gabarito/lista.json)).

## Atualização de 21/10/2026 ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md))

- Com as opções da caixa do conteúdo ligadas, a passada que mede o livro ficou 2 a 3 vezes mais lenta: Marial de 100 folhas ~140 → ~300 s (ramo `fase2-caixa-conteudo`; rodada de velocidade 39623840809 não lida). O Marial 300 é o livro da régua de velocidade (ver [pc-e-github](../geral/pc-e-github.md) §10).
