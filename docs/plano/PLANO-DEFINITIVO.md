# Editor de Impressão — PLANO DEFINITIVO

Discutido ponto por ponto com o Samuel e aprovado por ele em 24/09/2026. **Este é o plano. Ele não muda sozinho.**

---

## 1. Regras do plano

1. **Uma fase de cada vez, na ordem.** Uma fase só começa quando todos os itens da anterior estão aprovados `[x]` ou descartados `[-]` pelo Samuel.
2. **Ideia nova não entra na fase atual.** Vai para a **Lista de espera** (seção 6), com data. O Samuel decide em que fase ela entra.
3. **Só o Samuel muda este plano.** Toda mudança vai para o **Registro de mudanças** (seção 7), com data e motivo. O Claude Code pode sugerir uma mudança, nunca aplicar.
4. **Todo item termina igual:**
   - o verificador gera uma página de antes/depois só das páginas-gabarito daquele item;
   - o Samuel confere em até 10 minutos, abrindo pelo atalho "(desenvolvimento)";
   - ele marca `[x]` (aprovado), `[~]` (melhorar) ou `[-]` (descartado);
   - se aprovado, o trabalho é salvo no git (commit) **na hora**.
5. **Bugs que aparecem no meio de outra tarefa:**
   - Se o bug **impede** a tarefa atual, é consertado na hora, como parte dela.
   - Se **não impede**, vai para a **Lista de bugs** (seção 5), com print e data.
   - A Lista de bugs é resolvida **no começo de cada fase**, antes do primeiro item novo.
6. **Nenhum item pode deixar o programa mais lento** (medido pelo teste de velocidade da Fase 0).
7. **Toda decisão tomada em qualquer conversa vira documento no projeto.** As conversas não enxergam umas às outras, só os documentos.
8. **Toda função automática tem botão de ligar e desligar.**
9. As regras técnicas do `CLAUDE.md` continuam valendo: PySide6, uma página por vez na memória, nenhum modelo que desenhe pixel, interface em português sem jargão.

---

## 2. O resultado-alvo

**O Mágico Pro do CamScanner, que o Kaique usa hoje.** Nas palavras do Kaique:

> "removeu o amarelado do fundo, manteve apenas as letras e imagens preservando suas cores originais, e alinhou a página que estava inclinada"

Critério do Samuel: *"Eu quero que o papel saia branco, e o desenho também saia perfeito."*

As fotos do CamScanner enviadas pelo Samuel em 24/09 (calendário Novembre/Decembre e "Na escola de Jesus" p. 37) são gabarito de comparação.

---

## 3. Como o trabalho é feito (agentes)

- **Uma conversa "gerente" no Claude Code.** Ela conversa com o Samuel, distribui o trabalho e junta tudo.
- **Agentes** (arquivos de regra em `.claude/agents/`):
  - **implementador**: escreve o código do processamento;
  - **verificador**: roda os testes, gera a página de antes/depois e nunca marca aprovado;
  - **pesquisador**: estuda o ScanTailor, OCRs etc.;
  - **agente de layout**: só mexe nos arquivos de tela (`ui/`).
- **Sem choque entre frentes:** cada frente trabalha na sua própria cópia do projeto (git worktree) e no seu ramo (branch). O processamento mexe em `core/` e o layout em `ui/`. Só o gerente junta as frentes.
- **Layout em paralelo:** a Fase 1 roda no Claude Code enquanto o Samuel discute o plano do layout numa conversa separada no projeto do claude.ai. Quando o plano do layout estiver pronto, ele vira documento e o Samuel entrega na conversa do Claude Code, que aciona o agente de layout. A partir daí, processamento e layout andam juntos, cada um na sua cópia.

---

## 4. As fases

### FASE 0 — Arrumar a casa

- [x] 0.1 Fazer uma cópia de segurança, num ramo separado (`trabalho-17-a-23-09`), do trabalho sem commit desde 17/09, e depois salvar esse trabalho no programa principal (ver Registro de mudanças, 25/09).
- [~] 0.2 Apagar o atalho antigo `C:\Users\Public\Desktop\Editor de Impressao.lnk` (o Samuel apaga à mão, precisa de admin).
- [x] 0.3 Montar a pasta `gabarito/` com as páginas fixas: as do "Vamos recapitular", as fotos do CamScanner e as do Opus Majus.
- [x] 0.4 Criar o script que gera a página de antes/depois de qualquer item.
- [x] 0.5 Criar o **teste de velocidade**: abrir livro de 300 páginas, trocar de página, processar 10 páginas.
- [~] 0.6 Rodar o teste de velocidade **uma vez** no notebook do Kaique (Samsung Galaxy Book2: i5-1235U, 32 GB, SSD NVMe, placa de vídeo integrada Iris Xe) e no PC do Samuel. A diferença entre os dois vira a régua. Daí em diante, o Samuel testa só no PC dele.
- [x] 0.7 Criar os arquivos dos agentes (`.claude/agents/`) e atualizar o `CLAUDE.md` com as regras deste plano.

### FASE 1 — Separar o escrito do fundo (automático)

- [ ] 1.1 **Tirar o fundo de PDF que já vem com camadas** (Internet Archive; o Opus Majus e o Palatino são assim). O programa detecta e tira sozinho. Páginas em que tudo está na camada de baixo ficam intactas.
- [ ] 1.2 **Trazer o seletor de gravura do ScanTailor Advanced, com o código original** compilado e ligado ao programa (caminho A, decisão de 24/09). Referência: `TESTE-SCANTAILOR-MISTO.md`.
- [ ] 1.3 **Comparar OCRs já treinados**, só para achar onde está o texto: Tesseract (modelos normais e os históricos da UB Mannheim), docTR, PaddleOCR e Kraken. Ficam os 2 melhores.
- [ ] 1.4 **Máscara de tinta como o Internet Archive:** achar a tinta só dentro das linhas de texto, guardando a **cor original** (resolve o texto colorido que o ScanTailor transforma em preto).
- [ ] 1.5 **Juntar os dois detectores** (ScanTailor + OCR) e montar a página: papel branco, letra com a cor original, gravura intacta, página endireitada.
- [ ] 1.6 **PDF de saída em duas camadas** (letra em cima, fundo embaixo), como opção.
- Gabarito: Palatino 5, 7, 9, 10; Escola de Jesus 7; Horas 11, 13, 47; Opus Majus; fotos do CamScanner.
- **Páginas obrigatórias da Fase 1 (28/09)**, além das acima: Palatino 5 (fundo do retrato branco), Escola 35 (anjo), Horas 11 (iluminura intacta, centro branco), Horas 13 (moldura da TABLE), Horas 26 e 27 (moldura dos calendários) e Opus Majus 20 (foto da estátua).
- **Regras do resultado da Fase 1 (Samuel, 28/09)**, valem para todas as páginas do gabarito da Fase 1:
  - **Gravura e letras intactas, e todo o papel totalmente branco**, inclusive o papel dentro da gravura (ex.: o fundo do retrato do Palatino 5). Só pintura de verdade, como a roupa do anjo e o céu colorido, mantém a cor.
  - **Iluminura sai intacta**: cores, figuras, fundos e dourados como no original. Só o papel em volta do texto que fica dentro dela é branqueado (ex.: o centro claro da Horas 11, com "HEURES DE LOUIS LE GRAND"). O texto mantém a cor.
  - **Moldura dourada** (1.2, 1.4 e 1.5): detectada como gravura e mantida sem mudar a cor. Opção de **manter ou tirar a moldura**: o botão simples entra na Fase 1; a aparência fica para o layout (Fase 4).
  - Até a Fase 1 ficar pronta, **toda conferência avisa que moldura e iluminura são defeito conhecido**.

### FASE 2 — As outras ferramentas do ScanTailor Advanced

Com o código original, como na 1.2.

| # | Ferramenta |
|---|---|
| 2.1 | Dividir a folha (sabe quando é uma página só; hoje o nosso tenta dividir folha que é claramente uma) |
| 2.2 | Endireitar (o nosso hoje funciona mal) |
| 2.3 | Orientação / girar (o nosso hoje funciona mal, na tela e no funcionamento) |
| 2.4 | Margens iguais em todas as páginas + alinhamento |
| 2.5 | Caixa da página e guias |
| 2.6 | Tamanho final da página em cm/mm |
| 2.7 | Limpar pontinhos, com controle de força |
| 2.8 | Preto e branco Sauvola e Wolf (conferir o que já existe) |
| 2.9 | Texto claro em fundo escuro |
| 2.10 | Separar a saída em duas camadas |
| 2.11 | Segmentação de cor / reduzir cores |
| 2.12 | Desentortar página curva perto da lombada |
| 2.13 | Detectar a página dentro da borda preta do scanner |
| 2.14 | Preencher o que sobra fora da página com branco |
| 2.15 | Destacar páginas diferentes das outras |
| 2.16 | Usar todos os núcleos do processador |
| 2.17 | Normalizar iluminação e suavizar |
| 2.18 | Edição manual das zonas de gravura (retângulo, polígono, laço, copiar, colar) |
| 2.19 | Unidades cm/mm, perfis de configuração, tema claro/escuro |

**Já no programa, a aperfeiçoar nesta fase** (feito de 17 a 23/09; ver Registro de mudanças, 25/09):
- [ ] Aba Bordas e margens: recorte com Espelhado e Proporção travada, medidas em cm enquanto arrasta, tamanho da folha (A4/A5/Carta), moldura e margem branca, mover e redimensionar o conteúdo na folha, qualidade da prévia. Entra junto de 2.4 a 2.6.
- [ ] Aba Filtro: três tipos de preto e branco (Sauvola, Otsu, Wolf), limpar pontinhos e o aviso de "escuro/apagado demais". Entra junto de 2.7 e 2.8. *(Fase sugerida pela gerente, a confirmar pelo Samuel: o Registro de 25/09 não diz a fase deste.)*

### FASE 3 — Seleção manual no nível do Photoshop

Para corrigir onde o automático errar.

- [ ] 3.1 Selecionar objeto com um clique (a IA só aponta, não desenha)
- [ ] 3.2 Seleção rápida (pincel que gruda na borda)
- [ ] 3.3 Varinha mágica com tolerância e "só a área encostada"
- [ ] 3.4 Intervalo de cores com suavidade (substitui o "pegar tudo desta cor" atual)
- [ ] 3.5 Laço, laço magnético, retângulo, oval
- [ ] 3.6 Refinar a borda da seleção
- [ ] 3.7 Somar, tirar e cruzar seleções; salvar seleção
- [ ] 3.8 Consertar o zoom que às vezes não funciona e o travamento com muitos cliques (inclui os dois bugs de zoom da Lista de bugs, de 15-16/09 e 24/09)
- [ ] 3.9 Tudo testado com mouse de verdade, não só com clique simulado

**Já no programa, a aperfeiçoar nesta fase** (feito de 17 a 23/09; ver Registro de mudanças, 25/09):
- [ ] Aba Marcar: detecção automática por botão (não detecta mais sozinha ao abrir) e "usar em todas" / "só nas próximas".

### FASE 4 — Layout Photoshop / After Effects

Feito pelo agente de layout, a partir do plano discutido na conversa separada (ver seção 3). **Começa em paralelo com a Fase 1**, assim que o plano do layout estiver pronto.

**Já no programa, a aperfeiçoar nesta fase** (feito de 17 a 23/09; ver Registro de mudanças, 25/09):
- [ ] Tela de Configurações com atalhos de teclado editáveis.

### FASE 5 — Desempenho

- [ ] 5.1 Atingir, no notebook do Kaique, os tempos combinados depois da Fase 0.
- [ ] 5.2 Rodar bem sem placa de vídeo dedicada.

### FASE 6 — O resto do resultado final

- [ ] 6.1 Mancha do verso (subtrair usando a frente e o verso da mesma folha)
- [ ] 6.2 Manchas vermelhas e marrons sem mexer no título (Palatino 66, 76)
- [ ] 6.3 Tinta vermelha não virar preto (Graduale, Horas)
- [ ] 6.4 Apagar texto repetido em todas as páginas (endereço de site, Escola de Jesus 7)
- [ ] 6.5 Cadernos: caminho rápido, marca de alceamento, numeração
- [ ] 6.6 Decidir: separar chapas vermelho/preto para as prensas de duas cores?
- [ ] 6.7 Comparação final com o CamScanner: o programa já substitui?
- [ ] 6.8 Instalador testado no notebook do Kaique

### FASE 7 — Treinar os OCRs para transcrever

- [ ] 7.1 Decidir a regra da IA no OCR (opções a, b, c do documento `OCR-PESQUISA.md`)
- [ ] 7.2 Treinar mais de um OCR (Tesseract, Calamari e Kraken; o Kraken precisa do WSL no Windows)
- [ ] 7.3 Decidir se os manuscritos (Graduale, Palatino) entram

---

## 5. Lista de bugs (resolvida no começo de cada fase)

| Data | Bug | Onde | Print |
|---|---|---|---|
| 15-16/09 | **Movido para o item 3.8 em 28/09.** Travamento ao usar o zoom muitas vezes; roda do mouse não funciona às vezes | aba Marcar | — |
| 24/09 | **Movido para o item 3.8 em 28/09.** Zoom não funciona em algumas sessões | — | — |
| 25/09 | **`[~]` Consertado em 28/09; o Samuel vai instalar no PC dele e testar a detecção na aba Marcar antes de aprovar.** **O instalador não leva os modelos**: nem o detector de gravura e letra (`modelos/doclayout.onnx`) nem a seleção por clique (`modelos/mobile_sam`), que ficam fora do git. O `empacotar.py` só junta a pasta `recursos/` (que nem existe) e o `instalador.iss` só copia `dist/EditorImpressao/*`. **Confirmado** no programa instalado no PC do Samuel (instalador de 01/09): não tem a pasta `_internal\modelos` nem nenhum `.onnx`, então roda sem o detector e sem a seleção por clique, sem avisar. O instalador de 23/09 (o do Kaique) tem o mesmo tamanho (120,5 MB) e quase certamente também não tem; o Samuel vai conferir no notebook. | `empacotar.py`, `instalador.iss` | `bugs/2026-09-25-instalador-sem-modelos.txt` |
| 25/09 | **Resolvido em 28/09: o arquivo foi movido para a pasta `velhos/`** (decisão do Samuel: guardar, não apagar). `EditorImpressao.spec` velho (aponta para a Área de Trabalho e deixa o scipy de fora): quem empacotar por ele gera um programa quebrado. | `EditorImpressao.spec` | — |
| 25/09 | **Resolvido em 28/09 (aprovado pelo Samuel).** PDF dos relatórios: faixas cinzas atravessando o texto e uma última página só com o rodapé. O conteúdo sai todo legível. | `relatorio.py` (`gravar_pdf`) | `bugs/2026-09-25-relatorio-pdf-faixas-e-pagina-vazia.png` |
| 25/09 | **Resolvido em 28/09 (aprovado pelo Samuel).** `relatorio.gravar` corta o nome do arquivo no último ponto: o destino `conferencia-6.7` gravava `conferencia-6.md` (o `conferencia.py` contorna trocando o ponto por hífen). | `relatorio.py` (`gravar`) | — |
| 25/09 | **Resolvido em 28/09 (aprovado pelo Samuel).** A biblioteca `markdown` não está no `requirements.txt`: numa instalação do zero, os relatórios `.html` perdem as tabelas e as imagens. | `requirements.txt` | — |
| 28/09 | **Consertado em 28/09 (só o "não comer conteúdo"), a conferir pelo Samuel.** Conferência 6.7 (Mágico pro): **corte de bordas errado nas 3 páginas**. Escola 35: o corte comeu o começo das linhas à esquerda, o "37" do pé virou "3" e o alto da gravura. Horas 26 e 27: o corte não seguiu a margem do papel e cortou por dentro da moldura. Achado pelo Samuel. Investigado em 28/09: `relatorios/investigacao-bugs-6-7-2026-09-28/`. | corte de bordas (`core/`) | `bugs/2026-09-28-corte-de-bordas-6-7.jpg` |
| 28/09 | **Consertado em 28/09, a conferir pelo Samuel** (`relatorios/conferir/fase1-2026-09-28-1927-2`; commit no ramo `fase-1`). Conferência 6.7 (Mágico pro): **quadradinhos brancos na roupa do anjo** (Escola 35): o filtro tratou partes do pano branco como papel, em blocos. Achado pelo Samuel. Investigado em 28/09: `relatorios/investigacao-bugs-6-7-2026-09-28/`. | filtro Mágico pro (`core/filtros.py`) | `bugs/2026-09-28-quadradinhos-roupa-do-anjo.jpg` |
| 28/09 | **Vai para os itens 1.2, 1.4 e 1.5 (decisão do Samuel, 28/09); o conserto simples foi descartado: satura as cores e põe pontos brancos no azul.** Conferência 6.7 (Mágico pro): **moldura dourada com furinhos** (Horas 26 e 27): a faixa dourada ficou branca por dentro, só com o contorno e pontinhos. Achado pelo Samuel. Investigado em 28/09: `relatorios/investigacao-bugs-6-7-2026-09-28/`. | filtro Mágico pro (`core/filtros.py`) | `bugs/2026-09-28-moldura-dourada-furinhos.jpg` |
| 28/09 | **Consertado em 28/09, a conferir pelo Samuel.** A biblioteca `onnxruntime` também não está no `requirements.txt`: numa instalação do zero, o detector de gravura e letra e a seleção por clique ficam desligados, sem avisar. | `requirements.txt` | — |
| 28/09 | **Consertado em 28/09, a conferir pelo Samuel.** `python relatorio.py arquivo.md` quebra: o fim do arquivo espera 2 resultados do `gravar`, que devolve 3. | `relatorio.py` (fim do arquivo) | — |
| 28/09 | **Consertado em 28/09, a conferir pelo Samuel.** **`empacotar.py --modo entrega` apaga a pasta `dist\` inteira**, o que levaria junto `dist\TesteVelocidade\` e o `COMO RODAR NO NOTEBOOK DO KAIQUE.txt` da Fase 0 (o `.zip` só escaparia por estar como somente leitura). Não foi rodado de verdade; achado lendo o código. | `empacotar.py` | — |
| 28/09 | **Vai para os itens 1.2, 1.4 e 1.5 (decisão do Samuel, 28/09); o conserto simples foi descartado: satura as cores e põe pontos brancos no azul.** **O Mágico pro apaga quase toda a iluminura da Horas 11** (página obrigatória da Fase 1, R6): a pintura é vista como "pedaços do tamanho de letra" e descartada como mancha. Mesma família da moldura com furinhos. Achado na investigação. | filtro Mágico pro / seleção (`core/`) | `bugs/2026-09-28-horas11-iluminura-apagada.jpg` |
| 28/09 | **Consertado junto com o corte, a conferir** (o verificador contou 94 → 25 peças partidas; ainda sobram letras: fim do número da folha do Graduale 221 e 223, pé do endereço do site da Escola 35). O corte de bordas parte peças de tinta em 13 das 33 páginas do gabarito (77 peças: claves e primeiras notas do Graduale 222, número de página do Opus Majus 11 e 165...). Ampliação do bug do corte. | `core/recortar.py` | `bugs/2026-09-28-corte-parte-pecas-de-tinta.jpg` |
| 28/09 | **Consertado junto com os quadradinhos, a conferir.** A mesma limpeza que faz os quadradinhos no anjo lava a branco a foto da estátua do Opus Majus 20. Ampliação do bug do anjo. | `core/filtros.py` | ver a investigação |
| 28/09 | **Decisão da gerente (regra de 28/09): consertar agora.** A prévia (110 DPI) e o PDF final (300 DPI) às vezes dão cortes diferentes: até 8% no Palatino 5. Medido pela função; a tela não foi testada. | `core/recortar.py` / prévia | `bugs/2026-09-28-corte-previa-x-pdf.jpg` |
| 28/09 | **Decisão da gerente: vai para a Fase 2, junto da aba Bordas a aperfeiçoar.** A aba Bordas mostra a folha inteira quando o corte é automático. Deduzido do código; a tela não foi testada. | `ui/` aba Bordas | — |
| 28/09 | **Decisão da gerente: vai para os itens 1.2 e 1.5 (mesma família da moldura e da iluminura).** O Mágico pro é sensível ao enquadramento: no Palatino 67, a página um pouco maior depois do conserto do corte fez o detector marcar a linha "5 ꝛ ꝑ ꝝ t9" de outro jeito, e o filtro pôs uma caixa cinza-clara em volta dela, tratando-a como gravura. | detector + filtro (`core/`) | `relatorios/conferir/fase1-2026-09-28-1644`, página palatino_p067 |
| 28/09 | **Piora trazida pelo conserto do corte: faixa escura de 1,5 a 2,5 mm na borda direita do Marial 7.** Decisão da gerente: consertar agora, junto com o bug da prévia × PDF. | `core/recortar.py` | `bugs/2026-09-28-marial7-faixa-escura-direita.jpg` |
| 28/09 | Sobras do "não partir peça" (já existiam antes do conserto): a ponta de cima da primeira clave do Graduale 222 e o fim do número da folha no alto à direita do Graduale 221 e 223. Decisão da gerente: tentar junto com a faixa do Marial 7; se não for simples, fica para o corte do ScanTailor (2.5/2.13). | `core/recortar.py` | `bugs/2026-09-28-graduale-sobras-do-corte.jpg` |
| 28/09 | A orla das letras da Rhetorica 18 ficou mais cinza depois do conserto do corte: provavelmente o detector vê a página de outro jeito quando o enquadramento muda (mesma família do Palatino 67). Decisão da gerente: vai para os itens 1.2 e 1.5. | detector + filtro (`core/`) | `bugs/2026-09-28-rhetorica18-orla-cinza.jpg` |
| 28/09 | Papel ainda cinza-claro (cerca de 241 de 255) **dentro de gravura pequena de traço** (figuras 7 e 8 do Opus Majus 165, caixa "PAVLVS PAPA III" do Palatino 7, o "O" do Boécio 8): a limpeza tem uma trava de 200 peças. Contraria a regra da Fase 1. Decisão da gerente: item 1.5. | `core/filtros.py` (`PECAS_DE_TEXTO_MINIMAS`) | `bugs/2026-09-28-papel-cinza-em-gravura-pequena.jpg` |
| 28/09 | Opus Majus 20: a **estátua sai mais clara** que no original, com **halo claro** em volta da cabeça e contornos ondulados na pilastra (o Melhorar dentro da foto; já existia, escondido pela foto lavada). Decisão da gerente: item 1.5. | `core/filtros.py` | `bugs/2026-09-28-opus20-halo-e-estatua-clara.jpg` |
| 28/09 | Escola 35: a **roupa do anjo sai branco-azulada**, e no original é creme (balanço de branco dentro da gravura; já existia). A regra pede que pintura mantenha a cor. Decisão da gerente: item 1.5. | `core/filtros.py` | `bugs/2026-09-28-escola35-roupa-azulada.jpg` |
| 28/09 | Opus Majus 20: **degrau no alto da foto**: a caixa do detector começa uns 67 pontos abaixo do topo, e essa faixa sai lavada (mais forte no Preto e branco). Decisão da gerente: item 1.2 (o seletor do ScanTailor substitui a caixa do detector). | detector (`core/detectar_regioes.py`) | `bugs/2026-09-28-opus20-degrau-no-alto.jpg` |
| 28/09 | Teste instável: `tests/test_marcacao_em_todas.py::test_usar_em_todas_copia_a_marcacao_para_as_outras_paginas` falhou uma vez na bateria e passou nas outras. Decisão da gerente: consertar quando a Fase 1 mexer na tela (botões de ligar e desligar). | `tests/` | — |

## 6. Lista de espera (ideias novas)

| Data | Ideia | Quem pediu | Fase sugerida |
|---|---|---|---|
| 24/09/2026 | Ver todas as páginas do livro em grade, como o "Organizar páginas" do UPDF: seleção múltipla, girar, apagar, extrair, inserir, dividir. Referência: `referencias-layout/updf-todas-as-paginas.jpg` | Samuel | Fase 4 (layout), a confirmar |
| 24/09/2026 | Layout limpo como o do UPDF: página no centro, poucas ferramentas em ícones numa barra fina no topo, miniaturas numa coluna à esquerda que dá para esconder, navegação e zoom num canto de baixo. Referência: `referencias-layout/updf-tela-de-leitura.jpg` | Samuel | Fase 4 (layout), a confirmar |
| 24/09/2026 | Aviso que o Kaique pediu (ainda sem descrição: o áudio enviado não fala disso) | Kaique | a definir |
| 25/09/2026 | Prévia mais rápida: mostrar a página primeiro e achar gravura e letra depois. Hoje toda prévia nova roda essa detecção (cerca de 1 s por página), mesmo no filtro Original, que não usa o resultado. Deduzido do código, não medido. | agente implementador (achado no teste de velocidade) | Fase 5, a confirmar |
| 25/09/2026 | PDF de saída em Mágico pro muito pesado: cerca de 8 MB por página (imagem sem perda a 300 DPI), perto de 2,4 GB num livro de 300 páginas. Pensar em JPEG de alta qualidade ou na saída em duas camadas (1.6). Medido em 2 páginas só. | agente implementador (achado no teste de velocidade) | Fase 1 (junto do 1.6) ou Fase 5, a confirmar |
| 25/09/2026 | Script `montar_gabarito.py` no repositório, que remonta a pasta `gabarito/` a partir da `lista.json` (hoje, se a pasta se perder, só dá para refazer seguindo o método do LEIA-ME; os scripts usados ficaram numa pasta temporária). | agente implementador (achado ao montar o gabarito) | a definir |
| 25/09/2026 | Teste de velocidade: o relatório dizer também se o Windows aceitou o pedido de manter o computador acordado durante a medição. | agente implementador (ajustes da 0.6) | a definir |
| 25/09/2026 | Teste de velocidade: um "Atenção" no topo do relatório quando a medição não rodou na janela clássica. | agente implementador (ajustes da 0.6) | a definir |
| 25/09/2026 | Pôr `relatorios/conferir/` no `.gitignore`: cada rodada de conferência tem dezenas de MB de imagem (a da Fase 1 inteira, 100 MB), e hoje `relatorios/` vai para o git. | agente implementador (item 0.4) | a definir |
| 28/09/2026 | Teste de máquina "nenhuma peça de tinta partida pelo corte" nas páginas do gabarito, rodando a cada mudança. | agente (investigação 6.7) | a definir (o medidor já existe como script, `medir_pecas.py`, feito no conserto do corte) |
| 28/09/2026 | Dentro de foto, ancorar o Melhorar no papel da página, para a estátua do Opus Majus 20 manter o cinza claro do original. | agente (conserto dos quadradinhos) | Fase 1 (1.5), a confirmar |
| 28/09/2026 | Guardar na seleção se a caixa do detector é "traço" ou "meio-tom" (o detector já decide isso), para o filtro não medir de novo. | agente (conserto dos quadradinhos) | a definir |

## 7. Registro de mudanças

| Data | O que mudou | Por quê | Aprovado por |
|---|---|---|---|
| 24/09/2026 | Plano criado e discutido ponto por ponto | projeto parado há mais de 1 mês | Samuel |
| 25/09/2026 | As mudanças feitas de 17 a 23/09 (aba Bordas, Configurações, três tipos de preto e branco, aba Marcar, página nova em "Original") **ficam no programa principal**, marcadas como "a aperfeiçoar": Bordas/margens na Fase 2, aba Marcar na Fase 3, Configurações/atalhos na Fase 4. O ramo `trabalho-17-a-23-09` fica só como cópia de segurança. Os comentários de código de 22/09 entram no programa principal (pedido do Samuel: código comentado para manutenção futura). | o Samuel quer manter essas melhorias e não perder o trabalho | Samuel |
| 25/09/2026 | Item 0.3: as fotos do CamScanner (Mágico Pro, feitas pelo Kaique) estão em `camscanner/`. O calendário é do **Livro de Horas de Luís XIV, páginas 26 (NOVEMBRE) e 27 (DECEMBRE)**; a outra é a página 37 da "Na escola de Jesus". As três entram no gabarito para comparar o nosso resultado com o CamScanner. | resultado-alvo do plano (seção 2) | Samuel |
| 25/09/2026 | Gabarito: páginas escolhidas conferindo com os prints do "Vamos recapitular": Palatino 67 (o print marcado "76"), Siebmacher 9 (o marcado "7"), Marial 7 (no lugar da 862); Opus Majus 11 + 3, 20, 165 e 256; Escola = p. 35 do PDF ("37" impresso). O ESTADO-ATUAL guarda a tabela original e ganhou uma linha com as páginas que valem. | os números pedidos não batiam com as páginas dos prints | Samuel |
| 26/09/2026 | Teste de velocidade: o livro é aberto com o filtro Mágico pro (o programa começa em Original). Mantido. | uma lentidão de filtro aparece também em "trocar de página" | Samuel |
| 28/09/2026 | Fase 0 conferida: 0.1, 0.3, 0.4, 0.5 e 0.7 `[x]`; 0.2 e 0.6 `[~]` (o teste no notebook do Kaique fica para outro dia). **A Fase 1 começa mesmo com 0.2 e 0.6 em aberto** (exceção à regra 1). `CLAUDE.md` novo aprovado. | decisão do Samuel | Samuel |
| 28/09/2026 | O `dist\TesteVelocidade-notebook-do-Kaique.zip` (fora do git) é a versão da Fase 0: **não pode ser apagado nem refeito**. Identificação (SHA-256): `65ef4db543e5faa6b091436f88d0542fb9484d768911d4a84f9f80a1a855dd04`. O arquivo ficou marcado como somente leitura no Windows. | a rodada no notebook tem de medir o mesmo programa medido no PC do Samuel em 26/09 | Samuel |
| 28/09/2026 | Começo da Fase 1 pela Lista de bugs: os dois bugs do zoom vão para o item 3.8; o `EditorImpressao.spec` velho vai para a pasta `velhos/` (guardado, não apagado); os bugs de imagem da conferência 6.7 são investigados antes de decidir se o conserto é agora ou no item que vai substituir aquele código. | plano de execução aprovado | Samuel |
| 28/09/2026 | Lista de bugs, grupo A: faixas cinzas no PDF, nome cortado no ponto e `markdown` no `requirements.txt` aprovados `[x]`; instalador com os modelos `[~]` até o Samuel instalar e testar. Os 3 bugs pequenos novos (`onnxruntime`, `relatorio.py` direto, `empacotar.py --modo entrega` apagando `dist\`) serão consertados, começando pelo que apaga `dist\`. Grupo B: corte de bordas e quadradinhos na gravura consertados agora ("não comer conteúdo"; limpeza do papel fora da pintura); moldura e iluminura ficam para 1.2, 1.4 e 1.5. Na Fase 1 entram as **regras do resultado**, as **páginas obrigatórias** e o **botão de manter ou tirar a moldura** (seção 4, Fase 1). | decisão do Samuel após a investigação da conferência 6.7 | Samuel |
| 28/09/2026 | **Seguir sem esperar a aprovação item a item.** Quando terminarem os consertos da Fase 0 e da Lista de bugs, a gerente segue para os itens da Fase 1 sem esperar o Samuel; cada item termina como PRONTO PARA CONFERIR, com o relatório (antes/depois) deixado em `relatorios/`. Exceção às regras 1 e 4. Para o trabalho não se acumular sem commit (o que parou o projeto antes), cada item vira um commit separado no ramo `fase-1`, que vai ao GitHub; o ramo principal (`master`) só recebe o que o Samuel aprovar, e o que ele recusar é desfeito no ramo antes de juntar. Bugs novos sem decisão do Samuel: a gerente decide pela recomendação e registra aqui, para ele rever. | o Samuel quer que o trabalho ande enquanto ele confere depois | Samuel |
| 28/09/2026 | Decisões da gerente sobre bugs novos (regra acima, para o Samuel rever): prévia × PDF, faixa do Marial 7 e sobras do Graduale: consertar agora; caixa cinza do Palatino 67 e orla da Rhetorica 18: itens 1.2 e 1.5; aba Bordas mostrando a folha inteira: Fase 2. Conserto do corte PRONTO PARA CONFERIR em `relatorios/conferir/fase1-2026-09-28-1745/` (commit no ramo `fase-1`). | recomendações das investigações | gerente (a rever pelo Samuel) |
