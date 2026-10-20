# Ambiente: o que está instalado, onde, e o instalador

Montado em 20/10/2026. Fontes: [CLAUDE.md §3 e §7](../../CLAUDE.md), [plano, Registro 28/09/2026, 29/09/2026 e
30/09/2026](../../docs/plano/PLANO-DEFINITIVO.md), as seções "Ambiente" e "Como rodar e testar" de cada PARTE do
[histórico](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md), o código
([`requirements.txt`](../../requirements.txt), [`empacotar.py`](../../empacotar.py), [`instalador.iss`](../../instalador.iss))
e uma conferência leve no PC em 20/10/2026 (`pip list`, `py -0p`, `Test-Path`, `Get-ChildItem`). O PC em si (memória,
disco, regras de uso) está em [pc-e-github.md](pc-e-github.md). O mapa do código está em [../mapa-do-codigo.md](../mapa-do-codigo.md).

---

## 1. Os três Pythons (não confundir)

| Python | Onde | Para quê |
|---|---|---|
| **3.14.3** | `D:\programas\EditorImpressao\.venv` (criado de `C:\Users\fotog\AppData\Local\Python\pythoncore-3.14-64`) | **o programa**. "A máquina só tem Python 3.14 ... **Não sugerir rebaixar a versão do Python.**" ([CLAUDE.md §3](../../CLAUDE.md)) |
| **3.12.10 embutível** | dentro do motor do Kraken, `D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken\python\` | só o Kraken, que não roda no 3.14. Processo à parte (item [1.3](../itens/1.3.md); decisão do Samuel de 29/09/2026: "motor à parte") |
| **3.12 do sistema** | `C:\Users\fotog\AppData\Local\Programs\Python\Python312\` | só ferramentas de diagnóstico, instaladas com `pip install --user` em 08/09/2026 (PARTE -2 do histórico): `pywinauto` 0.6.9 (+ pywin32, comtypes, six), `py-spy` 0.4.2, `pillow`. Usadas para pilotar a janela real com mouse de verdade (PARTE -3) |

- Rodar sempre com `.venv\Scripts\python.exe` (ou `pythonw.exe` para abrir sem console).
- Ainda existe `D:\programas\EditorImpressao\.venv-ocr\` (OnnxTR 0.9, RapidOCR 3.9.2, pytesseract; da comparação dos
  OCRs de 28-29/09/2026), fora do git. Não é usado pelo programa.

## 2. As bibliotecas do `.venv` (conferido em 20/10/2026)

O [`requirements.txt`](../../requirements.txt) pede só o mínimo (`PySide6>=6.9`, `PyMuPDF>=1.24`, `opencv-python>=4.10`,
`numpy>=2.0`, `Pillow>=10.0`, `doxapy>=0.9.9`, `scikit-image>=0.24`, `pytest>=8.0`, `pyinstaller>=6.0`,
`markdown>=3.10.3`, `onnxruntime>=1.28.0`) e **trava** duas: `onnxtr==0.9.0` e `pyclipper==1.4.0` (a ponte do docTR usa
um método interno do OnnxTR; trocar a versão pede rodar `tests/test_ocr_doctr.py` com o modelo presente).

O que está instalado de fato (`pip list --format=freeze`, 20/10/2026), as principais:

| Biblioteca | Versão | Para quê |
|---|---|---|
| PySide6 (+ Addons, Essentials, shiboken6) | 6.11.1 | a janela; o Qt 6.11.1 dela é o mesmo que as DLLs do ScanTailor usam |
| pymupdf | 1.28.0 | ler e escrever PDF (AGPL; ressalva resolvida pela decisão de 17/09/2026, [CLAUDE.md §3](../../CLAUDE.md)) |
| opencv-python | 5.0.0.93 | imagem |
| numpy | 2.5.1 | |
| pillow | 12.3.0 | |
| doxapy | 0.9.9 | o Sauvola do Preto e branco (CC0) |
| scikit-image / scipy | 0.26.0 / 1.18.0 | plano B do binarizador, morfologia |
| onnxruntime | 1.28.0 | as redes (doclayout, MobileSAM, docTR) |
| onnxtr / pyclipper | 0.9.0 / 1.4.0 | docTR (travadas) |
| Markdown | 3.10.3 | o `.html` dos relatórios |
| pytest | 9.1.1 | testes |
| pyinstaller (+ hooks-contrib 2026.6) | 6.21.0 | empacotar |
| psutil | 7.2.2 | memória no teste de velocidade |

Outras que vieram de arrasto: rapidfuzz, pypdfium2, langdetect, huggingface_hub, httpx, PyYAML, tifffile, imageio,
networkx, protobuf, flatbuffers, tqdm. O Windows do GitHub usa **as mesmas versões**, travadas em
`ramo claude/list-server-files-gkos8v: .github/requisitos-windows.txt`, com Python 3.14.3.

## 3. Programas instalados no Windows (fora do `.venv`)

Instalados em 28/09/2026 para o item 1.3 e o 1.2, "sem reinício" ([plano, Registro 28/09/2026](../../docs/plano/PLANO-DEFINITIVO.md);
PARTE -8 §10 do histórico):

- **Tesseract 5.4 da UB Mannheim** (winget) em `C:\Program Files\Tesseract-OCR\` (lá só tem `eng` e `osd`). Os
  idiomas do programa ficam em `D:\programas\EditorImpressao\modelos\tessdata\` (fora do git): os **seis da comparação
  e do instalador** — `lat`, `ita`, `por`, `fra`, `eng` e `script/Fraktur` (tessdata_best) — e mais `deu`, `frak2021`,
  `GT4HistOCR` e `osd`. Desligado de fábrica na detecção (Samuel, 29/09/2026).
- **CMake** (4.4) em `C:\Program Files\CMake\bin\cmake.exe`.
- **Visual Studio 2022 Build Tools** ("Desenvolvimento para desktop com C++", MSVC 14.44 / compilador 19.44.35229) —
  o `vcvars64.bat` em `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\`.
- **Ubuntu no WSL** (26.04, usuário root; Kraken 7.1.1 em `/root/ocr-kraken/.venv`, Python 3.13) — usado só na
  comparação do 1.3. O Kraken do programa **não usa WSL** (decisão de 29/09/2026: "o Kraken direto no Windows, sem WSL").
- **Inno Setup 6** (o `ISCC.exe` do instalador) em `C:\Users\fotog\AppData\Local\Programs\Inno Setup 6\` (achado em
  20/10/2026; o `empacotar.py` procura nos lugares usuais e no PATH).
- **gh (GitHub CLI)** em `C:\Program Files\GitHub CLI\` (no Git Bash: `export PATH="$PATH:/c/Program Files/GitHub CLI"`).
- **Chrome** — usado sem janela para conferir desenho SVG (`chrome.exe --headless=new --screenshot=...`, PARTE -16 §6).

## 4. Ferramentas e dados fora do git

### `D:\programas\EditorImpressao-arquivos\` (pasta de apoio; "Não é código", diz o `LEIA-ME.md` de lá)

Primeiro nível em 20/10/2026: `backup-artefatos-2026-10-08`, `backups`, `BIBLIOTECA DO FIM DOS TEMPOS`,
`Claude outputs`, `Contexto para Claude (24-09-2026)`, `explicacoes-do-samuel`, `ferramentas`,
`LIVROS PARA FAZER TESTE (duplicata)`, `logs-de-backup`, `pasta do prompt`, `plano-24-09-2026` (a cópia do plano que o
Samuel edita, [CLAUDE.md §10 item 4](../../CLAUDE.md)), `revisar-decisoes-trabalho`, `sessao-2026-10-13`,
`sessao-2026-10-14`, `sessao-nuvem-2026-10-09`, `soltos-area-de-trabalho`, `temp-sessoes-antigas-2026-10-07` (25 GB
de temporários antigos do Claude), `TESTES EDITOR DE IMPRESSAO`, `testes-cadernos-gradus-primus`, e o `LEIA-ME.md`.

`ferramentas\` em 20/10/2026:

| Pasta | O que é |
|---|---|
| `motor-kraken\` | **o motor do Kraken** que vai no programa: `python\` (3.12.10 embutível, Kraken 7.1.1, PyTorch para processador, 73 versões travadas em `motor_kraken/requisitos-travados.txt`), `servidor_kraken.py`, `LEIA-ME-MOTOR.txt`. Sem as DLLs do Visual C++ dentro (trocado em 30/09/2026 com autorização do Samuel). ~1.147 MB no disco, 211 MB comprimido. Remontar: `.venv\Scripts\python.exe montar_motor_kraken.py --destino <pasta>` |
| `downloads\` | `python-3.12.10-embed-amd64.zip`, `pip-26.2.1`, `qtbase-6.11.1-msvc2022_64.7z` (+ `.sha1`), `boost_1_78_0.7z`, **`vc_redist.x64.exe`** (14.44, o oficial da Microsoft, conferido pela assinatura digital) |
| `qt\6.11.1\` e `boost\` | o Qt de desenvolvimento (só qtbase) e os cabeçalhos do Boost 1.78, para compilar as DLLs |
| `scantailor-advanced-v1.2.1\` | o código do ScanTailor Advanced v1.2.1 (o que está em `terceiros/` é a cópia só dos arquivos usados, com as somas) |
| `scantailor-advanced-2019.8.16\` | a versão antiga do ScanTailor (pesquisa) |
| `build-st-gravura`, `build-st-gravura-endireitar`, `build-st-ferramentas`, `build-st-ferramentas-dividir`, `-endireitar`, `-endireitar-2`, `-fase2-itens` | **onde as DLLs se compilam** (pastas de rascunho do CMake; `compilar_detector_gravura.py` e `compilar_st_ferramentas.py`) |
| `pesquisa-fase2-2026-10-01\` | protótipos do pesquisador da Fase 2 (34 MB) |
| `kraken-windows-pesquisa-2026-09-29\`, `treino-ocr-2026-09-29\`, `geometria-d3-2026-10-05\` | pesquisas e experimentos |

Como se compila: ver [../mapa-do-codigo.md §5](../mapa-do-codigo.md). Achado de 06/10/2026 (Lista de bugs): o
`compilar_detector_gravura.py` não acha a pasta de ferramentas quando roda numa worktree; o `compilar_st_ferramentas.py`
contorna.

### `modelos/` (dentro do projeto, fora do git, ~120 MB)

`D:\programas\EditorImpressao\modelos\`: `doclayout.onnx` (detector de gravura e letra, `core/detectar_regioes.py`),
`mobile_sam\` (seleção por clique, `core/rede_selecao.py`; o `mobile_sam.zip` e o script de referência não vão para o
programa), `doctr\rep_fast_base-1b89ebf9.onnx` (42 MB, docTR), `tessdata\` (Tesseract, acima). Sem eles o programa
segue, mas os detectores se desligam (foi o defeito do instalador de 25/09, consertado em 28/09).

### `gabarito/` (dentro do projeto, fora do git, ~450 MB)

As páginas fixas de conferência (item [0.3](../itens/0.3.md)): `paginas\`, `scantailor-24-09\` (329 MB, o teste do
ScanTailor de 24/09), `camscanner\` (as fotos do Mágico Pro do Kaique), `velocidade\marial_300.pdf` (o livro do teste de
velocidade), `conferir-samuel\`. No git só entram [`gabarito/LEIA-ME.md`](../../gabarito/LEIA-ME.md),
[`gabarito/lista.json`](../../gabarito/lista.json) (páginas por item) e as `ocr-zonas*.json`. **Numeração = página
do PDF, começando em 1** (não o número impresso).

- **Cópia no GitHub:** ramo `dados-de-teste` (`12bbb01`, publicado com autorização do Samuel em 09/10/2026; o
  repositório é público): páginas-gabarito, modelos e o `marial_300.pdf`. Fica de fora só
  `gabarito/scantailor-24-09/out/horas_p047.tif` (154 MB, acima do limite), que nenhum teste lê.
- Nas worktrees, `modelos`, `gabarito\paginas` e `gabarito\scantailor-24-09` costumam ser **junções** para as pastas da
  principal: nunca `Remove-Item -Recurse` (ver [pc-e-github.md](pc-e-github.md)).

### O acervo de livros e as queixas do Kaique

- **Acervo** ([CLAUDE.md §7](../../CLAUDE.md)): `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS
  PARA TESTE` — **somente leitura**. O CLAUDE.md diz "nove livros, 2903 folhas" (contagem de 07/09/2026); em 20/10/2026
  a pasta tem **15 PDFs**: Antiphon_25, Cursus philosophicus Tomo 2, Palatino, Graduale (270 MB), Livro de Horas,
  ljs47, Marial de sermoens (205 MB), Righetti, Matemática Para vencer, Na escola de Jesus, Pesel, Rhetorica Christiana,
  Siebmacher, Boécio — e um `LEIA-ME borda preta (05-10-2026).txt`. Os do Internet Archive (Palatino, Opus Majus,
  Rhetorica, Siebmacher) vêm em camadas. Onde ficam os outros livros do estudo das 89 páginas (Opus Majus, Camões,
  Egenloff, Rariora, Gladstone, Antiphonal): não achado nas fontes lidas (procurei só nessa pasta; as páginas usadas estão
  em `gabarito\paginas\`). Há uma duplicata antiga em `LIVROS PARA FAZER TESTE (duplicata)` (~1,5 GB, nenhum script usa).
- **Queixas do Kaique** ("são fonte de requisito", [CLAUDE.md §7](../../CLAUDE.md)): `...\BIBLIOTECA DO FIM DOS
  TEMPOS\Teste de livros` — em 20/10/2026: `Observação do programa 1`, `observações 2`, `teste 1` a `teste 5`. As dez
  queixas literais estão na PARTE 3 do histórico; ver [kaique.md](kaique.md). Cuidado: a PARTE 3 diz "Feito e conferido"
  para a mancha do verso, e o [ESTADO-ATUAL](../../docs/plano/ESTADO-ATUAL.md) diz que isso está **errado** (vale o
  ESTADO-ATUAL: a mancha do verso **não** foi corrigida, item [6.1](../itens/6.1.md)).
- **Outro programa, não misturar:** o ExtratorPDF em `D:\programas\Scan Tailor` (lá ficam também os testes do ScanTailor
  de 24/09, em `Testes de ajuste\`).

## 5. A pasta de dados do programa

`%LOCALAPPDATA%\EditorImpressao` (existe no PC, conferido em 20/10/2026): `historico.json`, `configuracoes.json`,
`erros.log` e uma subpasta por projeto (`projeto.json`, `acoes.jsonl`, `posicao.json`, `resumo.json`, `capa.png`, cópias
`projeto.antigo-*`). Desinstalar **não apaga**, de propósito. Testes e scripts nunca gravam nela (regra de 29/09/2026;
`tests/conftest.py` e `pasta_de_dados_dos_scripts.py`). Detalhe em [../mapa-do-codigo.md §4](../mapa-do-codigo.md).

## 6. O instalador

Feito por [`empacotar.py`](../../empacotar.py) (PyInstaller) + [`instalador.iss`](../../instalador.iss) (Inno Setup):

```
.venv\Scripts\python.exe empacotar.py                     tudo: pasta + arquivo único + instalador (~21 min)
.venv\Scripts\python.exe empacotar.py --modo pasta        dist\EditorImpressao\ (abre em ~8 s)
.venv\Scripts\python.exe empacotar.py --modo arquivo      dist\EditorImpressao.exe, o arquivo único do pendrive (~12 s)
.venv\Scripts\python.exe empacotar.py --modo instalador   dist\EditorImpressao-Setup.exe
.venv\Scripts\python.exe empacotar.py --modo entrega      só o instalador, na pasta "Editor de Impressão" da Área de Trabalho
dist\EditorImpressao\EditorImpressao.exe --conferir-ocr <imagem> <saida.json>   prova que o empacotado acha os 3 OCRs
```

**O que vai dentro** (docstring do `empacotar.py`; Registro de 29/09/2026, "os três OCRs no instalador"):
- o programa (pasta do PyInstaller, `_internal\`);
- os modelos: `doclayout.onnx`, `mobile_sam\` (encoder e decoder), `doctr\rep_fast_base-1b89ebf9.onnx`;
- a DLL `core\nativo\st_gravura.dll` e o `.txt` dela (item 1.2);
- `motor-kraken\` inteiro, ao lado do `.exe` (~1,2 GB no disco);
- `tesseract\` (os 27 arquivos do `tesseract.exe` 5.4.0, `LICENSE`, `AUTHORS`) com os seis idiomas em `tesseract\tessdata\`;
- o **`vc_redist.x64.exe` oficial da Microsoft**, que o instalador roda em silêncio só se o Visual C++ 2015-2022 x64
  faltar ou for mais velho que o 14.44 (decisão do Samuel, 29/09/2026: "O instalador roda o instalador oficial da
  Microsoft, e pula se ja estiver instalado").
- **Trava**: faltando qualquer peça (modelo, DLL, motor, idioma, licença, vc_redist) ou o motor sendo do jeito velho, o
  script **para antes de gerar**; depois confere que cada peça chegou na pasta e dentro do instalador.
- Instala em `C:\Program Files\Editor de Impressao\`, atalho no menu Iniciar e (opcional) na Área de Trabalho.

**Tamanhos:** instalador **209 MB → 561 MB** com os OCRs; **instalado, ~1,9 GB** (Registro, 29/09/2026). O
`dist\EditorImpressao-Setup.exe` de hoje no disco é esse: 561 MB, de 29/09/2026 21:30. O arquivo único
`dist\EditorImpressao.exe` tem 268 MB (28/09/2026) e **só leva o docTR** (não leva o Kraken nem o Tesseract, que somam
~1,4 GB). Na pasta da Área de Trabalho `Editor de Impressão\` ainda está um `EditorImpressao-Setup.exe` de 115 MB, de
23/09/2026 (anterior aos modelos e aos OCRs).

**Nunca testado de verdade** (Registro, 29/09/2026): "instalar, rodar o `vc_redist`, máquina sem Visual C++, notebook do
Kaique. Licenças das 26 DLLs do Tesseract a conferir uma por uma." O Samuel lembrou em 29/09/2026: "o instalador novo
(561 MB, com os OCRs e o `vc_redist`) ainda não foi instalado de verdade; isso entra no teste do notebook do Kaique (0.6 /
6.8)". Itens [0.6](../itens/0.6.md) e [6.8](../itens/6.8.md).

**Achado ao ler o código em 20/10/2026 (não conferido rodando):** `empacotar.nativos_do_programa` diz "Hoje so o
detector de gravura do ScanTailor" e o `instalador.iss` só confere a `st_gravura.dll`. A `st_ferramentas.dll` (limpar
pontinhos, dividir e endireitar do ScanTailor, desde 06/10/2026) **não aparece no empacotador**. O instalador de 29/09 é
anterior a ela; um instalador novo, gerado hoje, provavelmente sairia sem ela e o programa cairia no "nosso" sem avisar.
Não está no plano (procurei "st_ferramentas" no PLANO-DEFINITIVO). Para a gerente decidir se vira bug.

**Separado do instalador:** `dist\TesteVelocidade-notebook-do-Kaique.zip` (308 MB, 26/09/2026), feito por
[`empacotar_teste_velocidade.py`](../../empacotar_teste_velocidade.py). É a versão da Fase 0 e **não pode ser apagado nem
refeito** (Registro, 28/09/2026; SHA-256 `65ef4db5…55dd04`, marcado como somente leitura).

## 7. Os atalhos

- **"Editor de Impressao (desenvolvimento)"** — `C:\Users\fotog\Desktop\Editor de Impressao (desenvolvimento).lnk`
  (conferido em 20/10/2026): abre `D:\programas\EditorImpressao\.venv\Scripts\pythonw.exe main.py` na pasta principal,
  isto é, **o ramo `fase-1` que estiver na pasta principal**. É por ele que o Samuel confere cada item (regra 4 do plano).
  Avançar o `fase-1` na pasta principal precisa do "pode atualizar o programa" do Samuel (PARTE -13 §0).
- **O atalho antigo** — `C:\Users\Public\Desktop\Editor de Impressao.lnk`: aponta para
  `C:\Program Files\Editor de Impressao\EditorImpressao.exe`, **o programa instalado em 01/09/2026** (código velho).
  Item [0.2](../itens/0.2.md) está `[~]`: "o Samuel apaga à mão, precisa de admin". **Em 20/10/2026 ele ainda existe**
  (`Test-Path` = True). Risco: abrir o programa velho achando que é o novo (foi o que confundiu os itens 1 e 3 do teste do Boécio, PARTE -6 do histórico).
- Programa por linha de comando: `.venv\Scripts\python.exe main.py` (aceita um caminho de PDF como argumento).

## 8. Como rodar (resumo; detalhes em [pc-e-github.md](pc-e-github.md))

```
.venv\Scripts\python.exe main.py                                  o programa
.venv\Scripts\python.exe -m pytest tests\<arquivo> -q -p no:cacheprovider --basetemp <pasta da worktree>
.venv\Scripts\python.exe teste_botoes.py                          clica nos botões de verdade
.venv\Scripts\python.exe teste_velocidade.py "gabarito\velocidade\marial_300.pdf" --saida <pasta>
.venv\Scripts\python.exe conferencia.py fase1                     antes/depois do gabarito
.venv\Scripts\python.exe compilar_detector_gravura.py [--baixar]  recompila a st_gravura.dll
.venv\Scripts\python.exe compilar_st_ferramentas.py [--baixar]    recompila a st_ferramentas.dll
.venv\Scripts\python.exe montar_motor_kraken.py --destino <pasta> remonta o motor do Kraken
```
