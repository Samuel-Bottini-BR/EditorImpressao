# Ramo `dados-de-teste`: a gaveta dos arquivos pesados dos testes

Este ramo **não é o programa**. É uma gaveta: guarda os arquivos pesados que os
testes precisam e que ficam fora do git do programa (estão no `.gitignore`),
para que a suíte de testes rode no **Windows das máquinas do GitHub**
(`.github/workflows/testes-windows.yml`, no ramo do programa).

- Fica separado do programa para **não pesar** o `fase-1` (quem baixa o
  programa não precisa baixar meio gigabyte de páginas e modelos).
- **Apagar este ramo não afeta o programa.** Só os testes no GitHub deixam de
  achar o gabarito e os modelos (os testes que dependem deles pulam ou falham).
- Publicado com autorização do Samuel em 09/10/2026 ("Pode publicar as
  páginas-gabarito e os modelos no ramo dados-de-teste do GitHub público",
  incluindo a Escola de Jesus).
- O workflow copia `gabarito/` e `modelos/` daqui para dentro da pasta do
  programa, onde o código espera achar.

## De onde veio cada pasta

Tudo copiado em 09/10/2026, **somente leitura**, de `D:\programas\EditorImpressao\`
no PC do Samuel (pela cópia do HD acessível à sessão do Claude na nuvem).

| Aqui | De onde | O que é |
|---|---|---|
| `gabarito/paginas/` | `gabarito\paginas\` | As páginas-gabarito (`.pdf` copiado do livro sem redesenhar + `.png`), ver `gabarito/LEIA-ME.md` no programa. |
| `gabarito/camscanner/` | `gabarito\camscanner\` | As 6 fotos do CamScanner do Kaique. |
| `gabarito/scantailor-24-09/` | `gabarito\scantailor-24-09\` | O teste do ScanTailor de 24/09 (entrada, `out/`, `comparacoes/`). **Faltando um arquivo:** `out/horas_p047.tif` (154 MB) passa do limite de 95 MB por arquivo e ficou de fora; nenhum teste o lê. |
| `gabarito/ocr-zonas.antes-*.json` | `gabarito\` | Versões antigas das zonas do OCR (o `ocr-zonas.json` atual já está no git do programa). |
| `gabarito/velocidade/marial_300.pdf` | `gabarito\velocidade\` | O livro do teste de velocidade (`teste_velocidade.py`): as 300 primeiras páginas do Marial de sermoens do acervo, copiadas como estão (71 MB). Acrescentado em 09/10/2026 com a autorização do Samuel ("2- pode"). |
| `modelos/doclayout.onnx` | `modelos\` | O detector de gravura e letra (`core/detectar_regioes.py`). |
| `modelos/doctr/` | `modelos\doctr\` | O detector de texto docTR (`core/ocr_doctr.py`). |
| `modelos/mobile_sam/` | `modelos\mobile_sam\` | A seleção por clique (`core/rede_selecao.py`). |
| `modelos/tessdata/` | `modelos\tessdata\` | Os idiomas do Tesseract (`core/ocr_tesseract.py`). O `tesseract.exe` em si não está aqui. |

Ficaram de fora, porque nenhum teste lê: `gabarito\conferir-samuel\`, `gabarito\opusmajus-candidatas.png`,
`modelos\mobile_sam.zip`, `modelos\doclayout_inference_referencia.py` e
`__pycache__`. A `gabarito/lista.json` e o `gabarito/LEIA-ME.md` também não
estão aqui: moram no git do programa.

## Para atualizar

Copiar de novo as pastas do PC do Samuel (nunca o contrário: este ramo nunca
escreve no PC dele), conferir que nenhum arquivo passa de 95 MB e fazer um
commit novo neste ramo.
