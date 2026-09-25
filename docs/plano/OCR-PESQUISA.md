# OCR — pesquisa e benchmark real (24/09/2026)

Resultado de uma conversa de pesquisa sobre OCR, com um teste medido nos livros do acervo. Nada aqui foi implementado. No `PLANO-DEFINITIVO.md`, o OCR entra na Fase 1 (só para achar onde está o texto) e na Fase 7 (transcrever).

---

## 1. OCR treinado pode ser tão bom quanto IA?

Para livro impresso, sim, e normalmente melhor. Um OCR treinado roda offline, sem custo por página, e **nunca inventa**: erra de forma previsível e auditável. Uma IA de visão acerta mais em página degradada, mas "corrige" o texto em silêncio, moderniza ortografia e às vezes pula linhas.

| Material | Fonte | Acerto de caractere |
|---|---|---|
| Impresso séc. XV (incunábulo) | GT4HistOCR / OCRopus | 95% |
| Impresso séc. XIX (Fraktur) | GT4HistOCR / OCRopus | 98% |
| Manuscrito latino medieval, mesmo domínio | CREMMA Medii Aevi / Kraken | 90% |
| Manuscrito latino medieval, fora do domínio | CREMMA Medii Aevi / Kraken | 72–85% |

Ninguém publica 100%. Onde a transcrição é perfeita, ela ficou perfeita por correção humana.

## 2. Benchmark real — 8 páginas do acervo

Tesseract 5.3.4, modelos `tessdata_best`, uma página por livro, ~2400 px, sem pré-processamento. Referência transcrita à mão.

| Livro | Material | Modelo | Acerto |
|---|---|---|---|
| Na escola de Jesus | impresso moderno, PT | `por` | **99,4%** |
| Points d'anciennes broderies (Pesel) | impresso moderno, FR | `fra` | **99,6%** |
| Rhetorica Christiana (1579) | impresso antigo, latim | `lat` | 88,0% |
| Siebmacher (1597), recortado | Fraktur | `Fraktur` | 76,0% |
| Livre d'Heures de Louis XIV | manuscrito caligráfico, FR | `fra` | 81,8% |
| Boécio, *De Consolatione* | impresso antigo em itálico | `lat` | 56,1% |
| Palatino, *cancelleresca* (c. 1540) | xilogravura caligráfica | `ita` | inutilizável |
| Graduale, saec. XIV | manuscrito gótico + notação | `lat` | inutilizável |

- **A moldura estragou mais que a letra gótica.** No Siebmacher, a página inteira deu lixo; recortando só o bloco de texto (`--psm 6`), o mesmo modelo leu certo. O OCR deve entrar **depois** do corte de bordas.
- **O erro do latim impresso é sistemático:** o s longo (ſ) lido como f. Tabela de substituição + dicionário resolvem boa parte.
- **Boécio:** 56%. Scan de baixa resolução não se recupera; o remédio é reescanear.
- **Manuscrito não é caso para Tesseract:** Graduale e Palatino precisam de HTR treinado (Kraken + modelos CREMMA).
- **O modelo de idioma importa muito:** o programa precisa perguntar ou detectar o idioma.

## 3. Repositórios de modelos prontos

- `tessdata_best` — modelos LSTM mais precisos por idioma (`por`, `lat`, `fra`, `deu`, `ita`); os únicos bons para fine-tuning. https://github.com/tesseract-ocr/tessdata_best
- Modelos do Tesseract para impressos históricos (UB Mannheim) — testar antes do padrão em livro anterior a ~1900. https://zenodo.org/records/10125246
- `script/Fraktur.traineddata` — usado no Siebmacher.
- **Kraken** — modelos medievais no Zenodo (`kraken list` / `kraken get`). Só Linux/macOS; no Windows, WSL2.
- **OCR-D** — `ocrd resmgr`: `qurator-gt4hist-1.0` (Calamari) e `LatinHist`. https://ocr-d.de/en/models
- **GT4HistOCR** — 313.173 linhas impressas + transcrição, séc. XV–XIX, CC-BY. https://zenodo.org/records/1344132
- **CREMMA-Medieval-LAT** — 21 manuscritos latinos + ALTO XML. https://github.com/HTR-United/CREMMA-Medieval-LAT

Para a Fase 1 (achar texto) também entram na comparação: **docTR** e **PaddleOCR** (detecção de linhas de texto, modelos já treinados).

## 4. Hardware

- OCR (Tesseract, Calamari) roda em CPU. Não precisa de placa de vídeo.
- Modelo de linguagem local para correção não cabe numa placa de 4 GB. Se um dia for preciso, alugar GPU por hora em vez de comprar.

## 5. Decisão pendente para a Fase 7: IA corrigindo texto?

A regra do projeto é "nenhum modelo generativo". Três leituras, para o Samuel decidir antes da Fase 7:

- **a) A regra vale como está:** Tesseract + Calamari com votação; onde discordam, revisão humana.
- **b) A regra é sobre pixel, não texto:** um modelo de linguagem corrige o texto. Risco: inventar palavra latina "corrigida".
- **c) Meio-termo (recomendação):** o modelo só **escolhe** entre as leituras que os OCRs produziram e marca a linha quando nenhuma convence. Não gera texto novo.

## 6. Ferramenta

`teste_ocr.py` (no projeto do claude.ai): renderiza uma página, roda o Tesseract e calcula o erro contra uma transcrição de referência. Abaixo de 2% de erro não vale treinar; de 2% a 8%, trocar modelo e melhorar a imagem; acima de 8%, modelo errado ou imagem ruim.
