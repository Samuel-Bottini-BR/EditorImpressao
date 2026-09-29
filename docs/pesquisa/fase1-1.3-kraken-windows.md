# Kraken direto no Windows, sem WSL, dentro do programa do Kaique

**Data:** 29/09/2026 · **Quem:** agente pesquisador · **Pedido:** gerente, a partir da decisão do Samuel no item 1.3 (29/09): "De fábrica, docTR fast_base + Kraken; o Kraken direto no Windows, sem WSL."

**O que o Kraken faz aqui:** só **achar onde estão as linhas de texto** (o segmentador `blla`). Não transcreve (isso é Fase 7).

**Como ler as marcas:** **[medido aqui]** = rodei neste PC (Ryzen 7 5800H, Windows 11). **[lido]** = está escrito na fonte (links na seção 9). **[dedução]** = conclusão minha, não conferida.

**Onde mexi:** nada em `core/`, `ui/`, `.venv` do programa, `gabarito/` ou acervo. Testes na pasta temporária da sessão (ambientes Python e o "motor" de 1,2 GB, que podem ser apagados) e uma cópia pequena dos scripts, do modelo ONNX e dos resultados em `D:\programas\EditorImpressao-arquivos\ferramentas\kraken-windows-pesquisa-2026-09-29\` (6,8 MB). Nada pediu reinício. As medidas de tempo foram feitas com outro agente usando a máquina: servem para comparar, não como número final.

---

## 1. A resposta em cinco frases

1. **Recomendação: trazer o segmentador do Kraken para dentro do programa, sem PyTorch.** A rede do `blla` roda no `onnxruntime` que o programa já tem, e o resto (transformar o mapa em linhas) é código do Kraken copiado (licença Apache-2.0, que permite). Custa **~13 MB** a mais no programa, e não 1,2 GB. **[medido aqui]**
2. **Testei o protótipo no Python 3.14, com as mesmas bibliotecas do programa, nas 22 páginas do 1.3.** Em 21 delas saiu **o mesmo número de linhas** do Kraken do WSL. Na tabela do Opus Majus 256 saiu uma a mais. A área coberta pelas linhas bate em 99,8% a 99,9% (98,4% no Opus 256). As diferenças são pontinhos de 5 a 17 pixels. **[medido aqui]**
3. **O "Kraken perde linhas no Python 3.14" não vale para achar linhas.** No 3.14 a segmentação saiu **idêntica** à do WSL nas 22 páginas (862 linhas). A perda era só na transcrição: a NumPy 2.5 tirou um recurso (`np.cross` com vetores de 2 coordenadas) que o Kraken usa para recortar linha curva. O erro é engolido e a linha sai vazia. Conserta-se com uma linha de código ou prendendo a NumPy abaixo da 2.5. **[medido aqui + lido]**
4. **O plano B também funciona: o "motor à parte"** (Python 3.12 embutível + Kraken + PyTorch, chamado como outro programa). Achou as mesmas linhas do WSL. Ocupa **1,18 GB instalado**, mas só **~205 MB** a mais no download do instalador. Leva **~6 a 7 s para abrir** cada vez. Precisa levar junto 2 DLLs da Microsoft que o PyTorch pede. **[medido aqui]**
5. **Velocidade: igual nas três formas**, ~9 a 10 s por página neste PC (o Kraken é lento em qualquer uma). A rede leva 2 a 2,5 s; o resto é o pós-processamento em Python, que é o mesmo código. No notebook do Kaique, estimo **15 a 25 s por página**, 1¼ a 2 horas num livro de 300 páginas, sempre em segundo plano. **[medido aqui + dedução]**

---

## 2. Tabela das opções

| Opção | O que é | Instalado | A mais no instalador | Tempo por página (este PC) | Memória | Mesmas linhas do WSL? | Risco | Licença | O Kaique faz algo? |
|---|---|---|---|---|---|---|---|---|---|
| **3. Porte ONNX (recomendado)** | rede `blla` em ONNX no `onnxruntime` do programa + pós-processamento copiado do Kraken | **~13 MB** (modelo 5 MB + `shapely` 8 MB) | ~8 MB [dedução] | ~10 s, igual ao Kraken [medido] | pico 0,9 GB [medido] | 21 de 22 páginas iguais; área 99,8–99,9% [medido] | médio: nós viramos donos de ~500 linhas de código copiado | Apache-2.0 (Kraken e modelo `blla`); `shapely` BSD-3; `onnxruntime` MIT | nada |
| **1. Motor à parte** (Python 3.12 embutível + Kraken 7.1.1 + PyTorch CPU) | outro programa dentro da pasta do Editor, chamado página a página | **1.176 MB** [medido] | **~205 MB** (7-Zip LZMA2; o Inno Setup usa o mesmo método) [medido] | ~9–10 s + **6–7 s para abrir** o motor [medido] | pico 1,3 GB [medido] | **sim, 22 de 22** (5 no motor pronto, 22 no mesmo ambiente) [medido] | médio: Kraken sem suporte a Windows; 2 DLLs da Microsoft a levar; um segundo Python para manter | PSF (Python), Apache-2.0 (Kraken), BSD/Apache/MIT (PyTorch e as outras 70 bibliotecas) | nada |
| 2a. Kraken no Python 3.14 do programa, no mesmo processo | `pip install kraken` forçado dentro do programa | ~0,9 GB [dedução] | ~160–180 MB [dedução] | ~9 s + 7 s na primeira vez [medido no 3.14] | +1,3 GB na janela do programa | **sim, 22 de 22** [medido] | **alto**: combinação sem suporte; o Kraken exige scipy 1.15 e scikit-image 0.25, e o programa usa 1.18 e 0.26 (instalar "sem dependências"); qualquer atualização de biblioteca do programa pode mudar o Kraken em silêncio (foi o que a NumPy 2.5 fez) | idem 1 | nada |
| 2b. Idem, mas processo à parte com um Python 3.14 embutível | = opção 1, só que 3.14 | ~1,2 GB | ~205 MB | idem 1 | idem 1 | sim [medido no 3.14] | maior que a 1 e sem vantagem | idem 1 | nada |
| 4a. Motor congelado com PyInstaller | a opção 1 virando `.exe` | ~1,2 GB [dedução] | ~200 MB [dedução] | idem 1 | idem 1 | não testei | maior que a 1: o PyTorch dá trabalho no PyInstaller [dedução] | idem 1 | nada |
| 4b. conda-pack | ambiente conda empacotado | — | — | — | — | — | **fora**: o Kraken largou o conda na versão 6.0 [lido] | — | — |
| 4c. WSL pelo instalador | Linux dentro do Windows | — | — | — | — | sim | **fora**: pede administrador **e reinício** e a virtualização ligada [lido, documento de 28/09] | — | aceitar aviso e reiniciar |

---

## 3. O que foi testado de verdade

### 3.1 Referência

As linhas que o Kraken 7.1.1 achou no WSL (Python 3.13) para o relatório do 1.3: `saida_teste/ocr-1.3/linhas/K1/` (22 páginas, 862 linhas). As imagens de entrada são as mesmas do 1.3: `saida_teste/ocr-1.3/imagens/`.

Para comparar, casei cada linha nova com a linha da referência que mais se sobrepõe e calculei a sobreposição dos contornos (interseção ÷ união: 1,000 = idêntica). Também comparei a área total coberta pelas linhas da página.

### 3.2 Kraken no Windows, Python 3.12 (o ambiente da sessão de 28/09)

**Resultado: idêntico ao WSL nas 22 páginas.** Mesmas 862 linhas, sobreposição 1,000 em todas **[medido aqui]**. Tempo: mediana de 9,7 s por página (de 5,1 a 19,7 s).

### 3.3 Kraken no Windows, Python 3.14

O ambiente `kraken314` da sessão de 28/09 (Kraken forçado com NumPy 2.5.3, scipy 1.18.1, scikit-image 0.26.0, PyTorch 2.14).

**Resultado da segmentação: idêntico ao WSL nas 22 páginas** (862 linhas, sobreposição 1,000). Mediana de 8,9 s por página **[medido aqui]**.

**Por que a sessão de 28/09 viu "2 de 13 linhas vazias" no 3.14:**

- As duas linhas vazias do Graduale 222 são exatamente as duas cuja linha de base tem 3 pontos (linha levemente curva). As retas, de 2 pontos, saíram certas.
- Linha curva passa por outro caminho em `extract_polygons` (`kraken/lib/segmentation.py`), que usa `np.cross` com vetores de duas coordenadas.
- A **NumPy 2.5.0 (21/06/2026) removeu esse uso**, que estava avisado como obsoleto desde a 2.0 **[lido, notas da versão]**. Agora dá erro (`ValueError`).
- A função do Kraken que recorta a linha para ler (`_extract_line`, em `kraken/models/ctc.py`) faz `except ValueError: return None`: **o erro some e a linha sai vazia, sem aviso** **[lido no código]**.
- Prova: no 3.14, o recorte quebra na linha 9 **[medido aqui]**. Trocando só o `np.cross` por uma conta de uma linha (`a[...,0]*b[...,1] - a[...,1]*b[...,0]`), as 13 linhas saem **iguais às do 3.12**, pixel por pixel no tamanho e na tinta **[medido aqui]**.
- O pedido de mudança #804 do Kraken ("Support Python 3.14", de 04/09/2026, **ainda aberto**) prende a NumPy abaixo da 2.5 "para evitar falhas". O autor do pedido escreveu que as versões novas de scipy, scikit-image e NumPy "podem ter efeitos colaterais que eu não notei" **[lido]**.

**Conclusão:** para **achar linhas** (item 1.3), o 3.14 não perde nada. A perda afeta só a **transcrição** (Fase 7) e tem conserto conhecido. Mas isso não torna o 3.14 "suportado": o Kraken 7.1.1 pede Python < 3.14 e trava versões mais velhas de scipy e scikit-image.

**Achado de passagem (vale para todas as versões):** na tabela do Opus Majus 256, o Kraken **joga fora 8 linhas em silêncio** porque não consegue desenhar o contorno ("Polygonizer failed"). Isso acontece igual no 3.12, no 3.14 e no WSL. No porte (3.4), essas falhas passam a ser contadas e podem mandar a página para "Para revisar".

### 3.4 Porte ONNX (sem PyTorch), no Python 3.14

**O que fiz:**

1. Exportei a rede `blla` (a que vem no Kraken 7.1.1) para ONNX com o exportador comum do PyTorch, no ambiente 3.12. Arquivo `blla.onnx` de **5,1 MB**.
2. Guardei os metadados do modelo num JSON: entrada com altura fixa de 1800 pontos e 3 canais; classes "início de linha", "fim de linha", "linha de base" e "região de texto"; sem preenchimento.
3. Copiei do Kraken (Apache-2.0), sem mudar nada, as 16 funções do pós-processamento: esqueleto das linhas, contorno de cada linha, regiões e escalas (~770 linhas com comentários).
4. Reescrevi em numpy e PIL, sem PyTorch, a preparação da imagem (redução para 1800 de altura, inversão) e a ampliação do mapa (vizinho mais próximo + sigmoide). São ~100 linhas novas.
5. Rodei no Python 3.14 com **exatamente as versões do `.venv` do programa**: NumPy 2.5.1, scipy 1.18.0, scikit-image 0.26.0, onnxruntime 1.28.0, Pillow 12.3.0, mais `shapely` 2.1.2, que o programa ainda não tem.

**Resultado nas 22 páginas [medido aqui]:**

| | |
|---|---|
| Páginas com o mesmo número de linhas do WSL | **21 de 22** |
| Opus Majus 256 (tabela) | 234 contra 233 |
| Linhas com sobreposição abaixo de 0,9 | 14 de 863 |
| Área coberta pelas linhas, comparada à do WSL | 99,8% a 99,9% (Opus 256: 98,4%) |

- As 14 linhas diferentes são quase todas **pontinhos**, com linha de base de 5 a 17 pixels (Horas 26 e Siebmacher 9). Uma no Siebmacher tem 68 px e se sobrepõe 82%. As outras estão na tabela do Opus 256, que o Kraken já errava (achava só 33% do texto).
- **De onde vem a diferença:** a conta da rede no onnxruntime difere da do PyTorch por arredondamento, no máximo 0,017 numa escala de 0 a 1. Isso muda de lado entre 0,001% e 0,003% dos pontos no limiar que decide "é linha". Desligar as otimizações do onnxruntime não mudou nada **[medido aqui]**. A preparação da imagem saiu **idêntica** à do Kraken.
- **Tempo:** igual ao Kraken, medido lado a lado no mesmo momento. Palatino 57: 10,1 s no porte e 10,1 s no Kraken. A rede leva 2,0 a 2,5 s nos dois; o esqueleto das linhas (filtro de sulcos `sato`) leva ~5 s nos dois **[medido aqui]**. Na rodada das 22 páginas o porte deu mediana de 12,4 s, mas rodou num momento de máquina mais carregada.
- **Memória:** pico de 0,9 GB, contra 1,3 GB do motor com PyTorch (Palatino 7) **[medido aqui]**.

### 3.5 Motor à parte: Python 3.12 embutível de verdade

**Como montei [medido aqui]:**

- Baixei o `python-3.12.10-embed-amd64.zip` oficial (11 MB).
- Instalei nele, com `pip install --target`, as **73 bibliotecas nas versões exatas** do ambiente que funcionou (lista em `travado312.txt`, na pasta de ferramentas).
- Liguei a pasta das bibliotecas no arquivo `python312._pth`.
- Rodei com `python.exe -I -X utf8`:
  - `-I` isola o motor: ele ignora variáveis de ambiente e as bibliotecas do usuário. Sem isso, uma pasta de bibliotecas do Python do usuário entrou no caminho;
  - `-X utf8` substitui o `PYTHONUTF8=1`, que o modo isolado ignora.

**Resultados [medido aqui]:**

- **Achou as mesmas linhas do WSL** nas 5 páginas testadas (Graduale 222, Horas 47, Palatino 57, Escola 35, Opus 11), com sobreposição 1,000.
- **Tamanho:** 1.176 MB instalado. PyTorch 539 MB, scipy 125, pyarrow 88, sympy 74, scikit-learn 45...
- **Comprimido** com 7-Zip LZMA2 (nível 7): **205 MB**, em 4,5 minutos. O instalador do programa usa `lzma2/max`, então o número real deve ficar perto disso [dedução].
- **Arranque:** 5,5 a 7,6 s para carregar o Kraken e 0,5 s para carregar o modelo, **toda vez que o motor abre**. Por isso ele deve abrir uma vez por livro e processar todas as páginas, e não uma vez por página [dedução].
- **Não dá para enxugar sem mexer no Kraken:** só para segmentar, ele já carrega pyarrow, sympy, scikit-learn, lightning, coremltools e outras.
- **Bibliotecas da Microsoft:** o PyTorch precisa de `MSVCP140.dll` e `VCRUNTIME140_THREADS.dll`, que **não vêm** no Python embutível (conferido nas importações das DLLs do PyTorch). O instalador teria de copiá-las para a pasta do motor, ou instalar o "Visual C++ Redistributable" (o instalador já pede administrador). Neste PC elas já existem, então **não testei numa máquina limpa**.

---

## 4. Cada opção em detalhe

### 4.1 Opção 3: porte ONNX dentro do programa (recomendada)

**Prós:**
- ~13 MB em vez de 1,2 GB; nenhum segundo Python e nenhum PyTorch no notebook do Kaique;
- roda no Python 3.14 do programa, com as bibliotecas que ele já tem (só entra o `shapely`, BSD-3, 8 MB);
- nada de 6 a 7 s para abrir o motor; menos memória;
- dá para **contar as linhas que o Kraken jogaria fora em silêncio** e mandar a página para "Para revisar";
- a mesma técnica serve na Fase 7: a sessão de 28/09 exportou os modelos de **leitura** (CATMuS, PP-OCRv6) para ONNX e eles deram o mesmo texto.

**Contras:**
- **Não é idêntico ao Kraken**: 1 página em 22 com uma linha a mais, e pontinhos com contorno um pouco diferente. Para a máscara de tinta do 1.4, não vejo efeito [dedução]. A régua do 1.3 (texto achado, figura tomada) **não foi recalculada** com o porte.
- Passamos a manter ~500 linhas de código do Kraken. Se o autor corrigir algo, temos de copiar à mão.
- Um modelo `blla` novo (existe um de 21/09/2026) tem de ser exportado de novo. Isso exige o ambiente com PyTorch **só no PC do Samuel**, uma vez; o Kaique nunca precisa dele.
- Entra uma biblioteca nova (`shapely`). Pela seção 6 do `CLAUDE.md`, isso é pergunta para o Samuel.

**Licença (lida no código):**
- Os arquivos do Kraken dizem "Licensed under the Apache License, Version 2.0" e o pacote declara `Apache-2.0`. O modelo `blla` vem no mesmo pacote.
- A Apache-2.0 **permite copiar e mudar**. Obriga a:
  - levar junto o texto da licença;
  - manter os avisos de autor (Benjamin Kiessling);
  - marcar os arquivos que mudamos.
- Ela combina com GPL-3/AGPL-3, que é o caminho do programa (PyMuPDF é AGPL) [lido/dedução].
- **Atenção:** a função `boundary_tracing` do Kraken diz ter sido "copiada" do projeto `deepwings`, que **não tem licença nenhuma** (conferido na API do GitHub: `license: null`). No porte de verdade, trocar essa função por `cv2.findContours` (o OpenCV já está no programa) e conferir que o resultado não muda.

**Trabalho (dedução):**
- 1 a 2 dias de implementador + verificador:
  - pôr o módulo em `core/`, com comentários;
  - trocar o `boundary_tracing`;
  - o `empacotar.py` e o `instalador.iss` levarem o `blla.onnx`, com a mesma trava dos outros modelos (lembrar do bug do instalador sem modelos, 25/09);
  - `shapely` no `requirements.txt`;
  - teste de máquina: as 22 páginas do 1.3 contra as linhas do Kraken guardadas, com tolerância;
  - rodar em segundo plano.
- O protótipo (`blla_onnx.py`) já está pronto na pasta de ferramentas.

### 4.2 Opção 1: motor à parte com Python 3.12 embutível

**Prós:**
- é o Kraken original, idêntico ao do Linux;
- serve também para transcrever na Fase 7, com os mesmos modelos;
- o programa continua no 3.14 (não é rebaixar o Python do programa: é um segundo Python só do motor).

**Contras:**
- +205 MB no download e +1,2 GB no disco;
- 6 a 7 s para abrir e 1,3 GB de memória;
- 2 DLLs da Microsoft a levar;
- 73 bibliotecas travadas para manter;
- o autor não dá suporte a Windows: já fechou sem aceitar os consertos para Windows (junho/2026, documento de 28/09).

**Como o instalador levaria [dedução]:**
- um script de montagem: baixa o zip embutível, faz `pip install --target` com a lista travada e copia as DLLs;
- o Inno Setup copia a pasta `motor\` para dentro da pasta do programa;
- o programa chama `motor\python\python.exe -I -X utf8 motor.py livro.json`, que devolve as linhas em JSON, em segundo plano, com cancelar.

**Trabalho (dedução):** ~1 dia, mais o teste numa máquina limpa (o notebook do Kaique ou uma máquina virtual).

### 4.3 Opção 2: Kraken no Python 3.14 do programa

- **Achar linhas: funciona e sai idêntico** (3.3).
- Mas o Kraken 7.1.1 **recusa** o 3.14, e trava `scipy~=1.15.3` e `scikit-image~=0.25.2` **[lido, PyPI]**. Teria de ser instalado "sem dependências", em cima das versões do programa.
- É o tipo de combinação que já falhou em silêncio (NumPy 2.5). A cada atualização das bibliotecas do programa, o Kraken teria de ser reconferido.
- No mesmo processo, põe 1,3 GB e o PyTorch dentro da janela do programa. O PyInstaller teria de empacotar o PyTorch.
- Não recomendo. Se o pedido #804 for aceito e sair um Kraken com suporte a 3.14, isso muda [dedução].

### 4.4 Outras

- **Motor congelado pelo PyInstaller** (4a): mesmo tamanho da opção 1, mais frágil com o PyTorch. Não vale a pena sobre o Python embutível [dedução].
- **conda-pack** (4b): o Kraken saiu do conda na 6.0 **[lido]**.
- **WSL** (4c): pede administrador e reinício **[lido]**. Descartado pelo próprio pedido.
- **Acelerar o Kraken** (qualquer opção): 70 a 80% do tempo é o pós-processamento em Python (filtro `sato` e contorno de cada linha), e não a rede. No porte (opção 3), dá para tentar depois:
  - rodar 2 ou 3 páginas ao mesmo tempo (0,9 GB cada, o notebook tem 32 GB);
  - calcular o filtro com menos escalas.

  Qualquer mudança dessas altera o resultado e teria de ser conferida [dedução].

---

## 5. Recomendação

1. **Para o 1.3 (achar linhas): opção 3, o porte ONNX dentro do programa.** Ela entrega ao Kaique o mesmo segmentador do Kraken, sem segundo Python, sem PyTorch, com +13 MB, na mesma velocidade. Diferença medida contra o Kraken: uma linha a mais em 1 de 22 páginas e pontinhos.
2. **Antes de ligar:** o verificador recalcula a régua do 1.3 (texto achado e figura tomada) com o porte, nas 22 páginas, para confirmar que o placar do Kraken não muda. A troca do `boundary_tracing` por `cv2.findContours` entra junto.
3. **Guardar a opção 1 (motor à parte) como plano B**, e para a Fase 7 se a leitura em ONNX não der o mesmo texto. Os passos para montá-la estão na seção 8. Levar a opção 1 se o Samuel preferir o Kraken original a qualquer custo (+205 MB no download).
4. **Não levar o Kraken para dentro do Python do programa** (opção 2), nem WSL.
5. **Decisões que são do Samuel:**
   - (a) porte ONNX ou motor à parte;
   - (b) entrar a biblioteca `shapely` (seção 6 do `CLAUDE.md`: "trocar biblioteca" pergunta antes).

---

## 6. Licenças

| Coisa | Licença | O que obriga |
|---|---|---|
| Kraken 7.1.1 (código) e modelo `blla` | Apache-2.0 | levar a licença, manter o aviso de autor e marcar o que foi mudado; combina com GPL-3/AGPL-3 |
| `boundary_tracing` (dentro do Kraken, vinda do `deepwings`) | **sem licença** | não copiar; reescrever com OpenCV |
| onnxruntime | MIT | levar o aviso |
| shapely | BSD-3-Clause | levar o aviso |
| NumPy, scipy, scikit-image, scikit-learn, sympy, torchvision, coremltools | BSD (3-Clause) | levar o aviso |
| PyTorch 2.14 | BSD-3 no principal; o pacote declara também Apache-2.0, MIT, BSD-2 e BSL-1.0 dos componentes embutidos | levar os avisos |
| lightning, pyarrow | Apache-2.0 | idem Kraken |
| Pillow | MIT-CMU (HPND) | levar o aviso |
| Python 3.12 embutível | PSF License | levar o `LICENSE.txt` que vem no zip |
| DLLs da Microsoft (MSVCP140 etc.) | licença do Visual C++ Redistributable | podem ir junto do programa (redistribuíveis) [lido de memória, **não reconferido hoje**] |

---

## 7. O que ficou em aberto

- **Nada foi medido no notebook do Kaique.** Os 15 a 25 s por página são estimativa (1,5 a 2 vezes este PC).
- **Tempos com a máquina dividida** com outro agente: a mesma página variou de 6,3 a 10,3 s de uma rodada para outra. A comparação justa (lado a lado, no mesmo momento) deu porte = Kraken.
- **A régua do 1.3 não foi recalculada com o porte.** Só comparei a geometria das linhas.
- **O porte não foi testado dentro do programa empacotado** (PyInstaller com `shapely`). Rodou num ambiente separado, com as mesmas versões do `.venv`.
- **O motor à parte não foi testado numa máquina limpa** (sem as DLLs da Microsoft e sem Python). O arranque "a frio", logo depois de instalar (antivírus lendo 1,2 GB), deve ser maior que 6 a 7 s [dedução].
- O tamanho comprimido de 205 MB foi medido com o 7-Zip, não com o Inno Setup.
- Não testei o `blla` novo (21/09/2026) nem a exportação dele.
- A troca do `boundary_tracing` por `cv2.findContours` não foi feita; o resultado pode mudar um pouco.

---

## 8. Método para refazer

Tudo em `D:\programas\EditorImpressao-arquivos\ferramentas\kraken-windows-pesquisa-2026-09-29\`:

| Arquivo | O que é |
|---|---|
| `seg.py` | roda o `blla` do Kraken nas páginas e grava linhas + tempo (`python seg.py <pasta_saida> [pagina ...]`) |
| `comparar.py` | compara uma pasta com a referência do WSL (`saida_teste/ocr-1.3/linhas/K1`) ou duas pastas entre si |
| `exportar.py` | no ambiente com Kraken + PyTorch: gera `blla.onnx`, `blla_meta.json` e copia as funções do Kraken para `kraken_pos_copiado.py` |
| `cabecalho.py` + `kraken_pos_copiado.py` + `rodape.py` = `blla_onnx.py` | o porte (juntar os três com `cat`) |
| `seg_onnx.py` | roda o porte (Python 3.14 com `onnxruntime scipy scikit-image shapely pillow numpy`) |
| `extr.py` / `extr_remendo.py` | mostram a linha curva quebrando no 3.14 e o conserto do `np.cross` |
| `mapa_cmp.py`, `perf2.py`, `perf2t.py`, `pico.py`, `quais.py` | diferença do mapa ONNX × PyTorch, tempo por etapa, pico de memória, bibliotecas que o Kraken carrega |
| `travado312.txt` | as 73 versões exatas do motor |
| `resultados/r312`, `r314`, `r_onnx` | as linhas das 22 páginas em cada forma |

**Montar o motor à parte:**

1. Baixar `https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip` e descompactar em `motor\python\`.
2. `py -3.12 -m pip install --target motor\python\Lib\site-packages -r travado312.txt`
3. Escrever o `motor\python\python312._pth` com as linhas `python312.zip`, `.`, `Lib\site-packages` e `import site`.
4. Rodar com `motor\python\python.exe -I -X utf8 seg.py ...`

---

## 9. Links consultados (29/09/2026)

- https://github.com/mittagessen/kraken/pull/804 (suporte a Python 3.14, aberto; NumPy < 2.5; "efeitos colaterais que eu não notei")
- https://github.com/mittagessen/kraken/releases (7.0 a 7.1.1)
- https://numpy.org/doc/2.5/release/2.5.0-notes.html (`np.cross` deixa de aceitar vetores de 2 coordenadas)
- https://docs.python.org/3.12/using/windows.html (pacote embutível: sem instalação, sem pip, "vendoring", arquivo `._pth`, não traz o runtime do C da Microsoft)
- https://github.com/machine-shop/deepwings e https://api.github.com/repos/machine-shop/deepwings (sem licença)
- Código lido (Kraken 7.1.1): `kraken/blla.py`, `kraken/lib/segmentation.py` (`vectorize_lines`, `calculate_polygonal_environment`, `extract_polygons`, `boundary_tracing`), `kraken/lib/vgsl/spred.py`, `kraken/lib/dataset/utils.py` (`ImageInputTransforms`), `kraken/lib/functional_im_transforms.py`, `kraken/models/ctc.py` (`_extract_line`)
- Metadados das licenças: `*.dist-info/METADATA` do motor montado
- Locais: `docs/pesquisa/fase1-ocr-manuscrito-no-windows.md` (28/09), `docs/pesquisa/fase1-1.3-ocr-para-achar-texto.md`, `relatorios/fase1-1.3-comparacao-ocr-2026-09-28/`, `saida_teste/ocr-1.3/`, `instalador.iss`, `requirements.txt`
