# Editor de Impressão — árvore, dependências e montagem do .exe

Escrito em 23/11/2026 pelo agente pesquisador, só lendo o código (nenhuma linha mudou).
Código lido: ramo `obra-2026-10-26` (a "versão de teste", o programa de hoje), commit
`0f58346ae3c49f10a07ec5abc8411d9f441da946` (conferido: está em `origin/obra-2026-10-26`).
Links abaixo: `O/<caminho>#L<n>` = `https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/<caminho>#L<n>`.

## 1. Árvore (só o que importa)

Contado com `git ls-files` no commit acima (arquivos no git por pasta, entre parênteses).

```
EditorImpressao/
├─ main.py                ponto de entrada; excepthook; atende --servidor-de-paginas e --conferir-ocr antes de abrir janela
├─ modelos.py             ConfigFolha, ConfigPagina, Projeto, Acao (o modelo de dados)
├─ projetos.py            gravar/abrir projetos em %LOCALAPPDATA%\EditorImpressao (gravação por trás, cópias de segurança)
├─ historico_acoes.py     desfazer/refazer ilimitado (acoes.jsonl)
├─ historico.py, configuracoes.py, atalhos.py, registro.py   livros recentes, preferências, atalhos, erros.log
├─ versao.py              o número da versão (único lugar; hoje "1.1.0")
├─ atualizacao.py, assinatura.py, servidor_das_versoes.py, publicar_versao_kaique.py
│                         atualizador (Velopack) e publicação; ficam com outro agente, só cito que existem
├─ empacotar.py, instalador.iss, montar_motor_kraken.py, compilar_*.py   montar o .exe, o instalador, o motor do Kraken e as DLLs
├─ avaliar.py, avaliar_selecao.py, conferencia.py, conferir.py           réguas e páginas de conferência
├─ teste_*.py (19)      scripts de teste soltos na raiz, fora do pytest; o principal é teste_botoes.py (clica em todos os botões)
├─ core/ (67)             todo o processamento; não importa nada de ui/ (O/core/__init__.py#L3)
│  └─ nativo/             st_gravura.dll e st_ferramentas.dll: código original do ScanTailor Advanced compilado (GPL-3)
├─ ui/ (49)               as telas em PySide6; ui/widgets/ = peças (painéis, prévia, tira, grade, trilha de ferramentas)
├─ tests/ (269)           o pytest: 258 arquivos test_*.py, 64 deles test_decisoes*.py (provas das decisões do Samuel)
├─ terceiros/scantailor-advanced/ (268)   fonte original do ScanTailor Advanced v1.2.1 + a "cola" em C nossa (ligacao*/)
├─ motor_kraken/ (2)      servidor_kraken.py + requisitos-travados.txt do motor à parte (Python 3.12)
├─ docs/plano/ (69)       DECISOES.md (Livro de decisões), PLANO-DEFINITIVO.md, ESTADO-ATUAL.md, prints de bugs
├─ docs/pesquisa/ (8)     pesquisas de código de fora
├─ memoria/ (209)         memória por assunto (fichas de itens, livros, páginas de teste, catálogo de erros)
├─ relatorios/ (3912)     relatórios de cada trabalho e conferência (.md/.html/.pdf + prints)
├─ regras_dos_agentes/ (18), .claude/agents/   regras dos agentes de IA que trabalham no projeto
├─ gabarito/ (5)          lista das páginas-gabarito (as imagens ficam fora do git)
├─ modelos/               redes neurais, FORA do git: doclayout.onnx, mobile_sam/, doctr/, tessdata/
├─ recursos/, arte/       brasão e ícones
└─ velhos/                o EditorImpressao.spec antigo, guardado por decisão
```

## 2. Dependências externas

Fonte: [`requirements.txt`](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/requirements.txt)
(não há `pyproject.toml` nem `setup.py`). "No .venv" = versão instalada hoje em `D:\programas\EditorImpressao\.venv`
(lida nos `*.dist-info`). Python do programa: 3.14 (o GitHub usa 3.14.3, `.github/workflows/testes-windows.yml` L98, ramo
`claude/list-server-files-gkos8v`). Licenças: as marcadas (CLAUDE) vêm do CLAUDE.md §3; (req) do comentário do
requirements; (LICENSE) do arquivo no repositório; as outras são **de memória, não conferi** no arquivo da licença.

| Pacote | Pedido | No .venv | Para que o programa usa | Licença |
|---|---|---|---|---|
| PySide6 | >=6.9 | 6.11.1 | toda a interface (Qt); as DLLs do ScanTailor usam o mesmo Qt 6.11.1 | LGPL-3 (CLAUDE) |
| PyMuPDF | >=1.24 | 1.28.0 | única porta de PDF: ler páginas, escrever o PDF final, cadernos (`core/pdf_io.py`, `core/cadernos.py`) | AGPL-3 (CLAUDE) |
| opencv-python | >=4.10 | 5.0.0.93 | operações de imagem em todo `core/` | Apache-2.0 (CLAUDE) |
| numpy | >=2.0 | 2.5.1 | imagens como matrizes | BSD (CLAUDE) |
| Pillow | >=10.0 | 12.3.0 | ler/gravar imagens, prints | HPND (CLAUDE) |
| doxapy | >=0.9.9 | 0.9.9 | binarização (Sauvola e outros) do Preto e branco | CC0 (CLAUDE) |
| scikit-image | >=0.24 | 0.26.0 | operações morfológicas e de medida (traz o scipy) | BSD (CLAUDE) |
| onnxruntime | >=1.28.0 | 1.28.0 | roda as redes que só apontam: doclayout (gravura/letra) e MobileSAM (seleção por clique) | MIT (de memória) |
| onnxtr | ==0.9.0 (travado) | 0.9.0 | detector de texto docTR `fast_base` (`core/ocr_doctr.py`; usa método interno, por isso travado) | Apache-2.0 (de memória) |
| pyclipper | ==1.4.0 (travado) | 1.4.0 | alarga as caixas do docTR, por dentro do OnnxTR | MIT (de memória) |
| velopack | ==1.2.161 (travado) | 1.2.161 | atualização pela internet (`atualizacao.py`); travado na mesma versão do `vpk` | MIT (req) |
| markdown | >=3.10.3 | 3.10.3 | relatórios `.md` → `.html`/`.pdf` (`relatorio.py`) | BSD (de memória) |
| pytest | >=8.0 | 9.1.1 | testes | MIT (de memória) |
| pyinstaller | >=6.0 | 6.21.0 | monta o `.exe` | GPL-2 com exceção do bootloader (de memória) |

Fora do `requirements.txt`:

| Peça | Versão | Para que | Onde | Licença |
|---|---|---|---|---|
| ScanTailor Advanced (código-fonte) | v1.2.1 | detector de gravura, limpar pontinhos, dividir, endireitar, caixas, compilados em `core/nativo/*.dll` e chamados por `ctypes` | `terceiros/scantailor-advanced/` | GPL-3 (LICENSE) |
| Motor do Kraken | kraken 7.1.1, torch 2.14.0 (CPU), Python 3.12 embutível | segunda opinião das linhas de texto do "Só as letras"; processo à parte | `motor_kraken/requisitos-travados.txt`, `montar_motor_kraken.py` | Kraken Apache-2.0, PyTorch BSD (de memória) |
| Tesseract (UB Mannheim) | 5.4.0 | OCR instalado, desligado de fábrica | levado por `empacotar.py` (L64) | Apache-2.0 (de memória) |
| Visual C++ Redistributable | oficial Microsoft | DLLs que o programa precisa; conferido pela assinatura digital | `empacotar.py` (L68-80) | licença da Microsoft |
| Redes neurais | doclayout.onnx, MobileSAM, docTR rep_fast_base | só apontam onde está gravura, letra, texto (nunca desenham) | `modelos/`, fora do git; caminhos em `core/detectar_regioes.py` L158, `core/rede_selecao.py` L29-31, `core/ocr_doctr.py` L100 | não conferi |
| Inno Setup 6 | — | instalador antigo da "pasta portátil" (`ISCC.exe`) | `instalador.iss` | licença própria do Inno (de memória) |
| vpk (Velopack) + WiX | vpk 1.2.161 | pacote de atualização e o `.msi` | `empacotar.py` L1192 (`VERSAO_DO_VPK`) | MIT / MS-RL (de memória) |

Roda no PC do Samuel (Windows 11, Python 3.14, GTX 1650; o pacote é o `onnxruntime` comum, não o `-gpu`, então as redes rodam no processador: dedução pelo nome do pacote) e no notebook do
Kaique (i5-1235U, sem placa de vídeo) **pelo que o código diz**; o notebook só recebeu o teste de velocidade da Fase 0
(não conferi o resultado).

## 3. Como o `.exe` e o instalador são montados

- **Script único:** [`empacotar.py`](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/empacotar.py)
  (2036 linhas). Modos `tudo | pasta | arquivo | instalador | entrega` (`main`, L1971).
- **PyInstaller** monta a versão em pasta (`onedir`, `--contents-directory _internal`) e o arquivo único do pendrive
  (`comando_do_pyinstaller`, L859; `_pyinstaller`, L907). O script põe junto os modelos, as DLLs do ScanTailor, o
  docTR, o motor do Kraken, o Tesseract e o Visual C++, e **para antes de gerar** se faltar alguma peça; depois confere
  que cada peça chegou (cabeçalho, L29-106).
- **Três saídas, descritas num lugar só** (`Saida`, `PORTATIL`, `ATUALIZACAO`, `INSTALADOR`, L228-268): a pasta
  portátil (o Inno Setup a empacota em `dist\EditorImpressao-Setup.exe`, `instalador.iss`); a atualização do Velopack
  (sem o motor do Kraken, que é publicado à parte); e o instalador `.msi` feito pelo `vpk` (que chama o WiX). O `vpk`
  roda só por `rodar_vpk` (L1530).
- **Publicar** uma versão para o Kaique é outro script, `publicar_versao_kaique.py` (assina, sobe ao GitHub); é do
  agente do atualizador.
- **DLLs do ScanTailor:** `compilar_detector_gravura.py` e `compilar_st_ferramentas.py` (CMake + Visual Studio 2022
  Build Tools, Qt 6.11.1 qtbase e Boost 1.78 baixados e conferidos pela soma).
