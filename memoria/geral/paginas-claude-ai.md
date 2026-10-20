# As páginas do claude.ai (onde o Samuel responde)

Escrito em 20/10/2026. Desde 06/10/2026 tudo o que o Samuel precisa ver ou responder vai numa página do claude.ai com banco de dados:
ele clica, comenta, e a resposta fica salva na hora. Antes disso eram formulários HTML em `relatorios/` com as respostas coladas no chat
(ver [conferencias.md](../conferencias.md)).

**O que vale:** a regra está no [CLAUDE.md](../../CLAUDE.md) §10 item 10 e no [plano](../../docs/plano/PLANO-DEFINITIVO.md) (Registro de mudanças).
Este arquivo junta endereços, banco, arquivos-fonte e o que já se descobriu publicando. Respostas de cada pergunta: [conferencias.md](../conferencias.md).

---

## 1. As páginas

| Página | Endereço | Para que serve | Aberto na última leitura conhecida |
|---|---|---|---|
| **Escolhas do Editor de Impressão** | https://claude.ai/artifact/EJoJq5mocxi3vbNxU8ZecV | Comportamento do programa: perguntas com opções em imagem, "Escolho esta", comentário. Abas "Para escolher" e "Já decidido". Criada em 05/10/2026 a pedido do Samuel (rodada 6 do layout: "eu quero ver a coisa quando eu for escolher algo") | `g7-borda-ate-onde` e `g9-folha-maior-impressao` (Registro 19/10/2026; histórico PARTE -16 §4). Na leitura de 20/10/2026 as duas continuavam vazias no banco |
| **Layout do Editor de Impressão** | https://claude.ai/artifact/QuzVaghq2tz2WVwJ1AyMWu | Escolhas de tela (rodadas 7 a 13). Abas: Para escolher · Já decidido (com imagens) · Botões e funções · Plano de layout (rascunho inteiro) · Todas as telas mostradas. Criada em 06/10/2026 ("podemos ter um artefato só para o layout?") | nada aberto (rodadas 12 e 13 decididas; PARTE -15 §8). A rodada 14 ainda não foi feita |
| **Quando revisar uma página** | https://claude.ai/artifact/NeCgyTotRfqsdXntn9vMUc | O estudo do "Para revisar" (06/10/2026) e as rodadas 1 a 5 de perguntas (`rv3-*`, `rv4-*`, `rv5-*`) | nada aberto (rodada 5: 10 de 10 `decidida`, 09/10/2026) |
| **Andamento do programa** | https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy | O que cada agente faz, esperando o Samuel, próximos, feito, o **plano completo** e os recados dele | atualizada em 14/10/2026 (PARTE -16 §8); a coleção `recados` estava vazia na leitura de 20/10/2026 |
| **Conferência** ("Conferir: endireitar antes de cortar e tela sem abas") | https://claude.ai/artifact/J8AwcyyUwrZ2n7kSevyGvX | Conferência de imagens: cada quadro com "Está bom / Melhorar / Está pior" + comentário, e uma decisão final por trabalho. Uma aba por trabalho: 1 G6 (`g6-*`), 2 layout (`layout3-*`; a antiga `layout2-*` ficou desatualizada), 3 conserto do corte (`cg6-*`), **4 "Para revisar" (a montar)** | `cg6` **reaberta** em 14/10/2026 até o conserto do Pesel 21 (Registro 14/10/2026); aba 4 ainda não publicada (PARTE -15 §4 item 6) |
| Página vazia | https://claude.ai/artifact/NwYyesZwRmQGvKnToYJLfW | Criada por engano na sessão na nuvem (PARTE -14 §3) | pergunta "posso apagar?" **sem resposta** (PARTE -15 §4 item 9; PARTE -16 §4). Não apagar sem o "sim" dele |

O [CLAUDE.md](../../CLAUDE.md) §10 item 10 lista só as quatro primeiras; a página de conferência nasceu depois (09/10/2026, sessão na nuvem).
Outras páginas: não achei mais nenhuma nas fontes lidas (procurei os endereços `claude.ai/artifact/` no histórico, no CLAUDE.md e no plano).

---

## 2. O banco de dados de cada página

Lê e grava com a ferramenta **ArtifactData**, sempre com o `url` da página.

| Página | Coleções |
|---|---|
| Escolhas | `decisoes` (as perguntas), `respostas` (o que ele marcou) |
| Layout | `decisoes`, `respostas`, `textos` (`botoes` e `rascunho`, copiados inteiros), `telas` (galeria de prints por grupo) |
| Quando revisar | `decisoes`, `respostas` |
| Andamento | `agentes`, `itens`, `plano` (um documento por seção, por fase e por lista do plano), `recados` (recados do Samuel) |
| Conferência | só `respostas`. Os quadros ficam **dentro do HTML** (`G6`, `LAYOUT`, `CORTE`, `FIXADOS`; PARTE -15 §6) |

**Campos** (o `doc_id` é o id da pergunta, igual nas duas coleções):
- `decisoes/<id>`: `pergunta`, `explicacao` (respeita quebra de linha), `exemplos` (`[{src, legenda, largo}]`; `largo: true` ocupa a linha inteira), `opcoes`, `ordem` (número), `parte` (ex.: "Endireitar"), `quando`, `status` (`"decidida"` quando fechada), `decisao` (a decisão por extenso, com o comentário dele), `historico` (`[{quem: "samuel" | "gerente", em, texto}]`, aparece no alto como "Comentários anteriores desta pergunta (fixados)").
- `respostas/<id>`: `opcao` (código), `opcaoNome` (o texto que ele viu), `comentario`, `em` (data e hora em UTC). Pergunta reaberta = `opcao` e `opcaoNome` vazios.

Horas: o banco grava em UTC; o relógio do PC está em UTC-4 (PARTE -16 §6; PARTE -15 §6).

---

## 3. Onde estão os arquivos-fonte (para republicar)

| Página | Arquivo que vale para republicar | Outras cópias |
|---|---|---|
| Escolhas | `D:\programas\EditorImpressao-arquivos\sessao-2026-10-13\paginas\pub-escolhas\escolhas-editor-impressao.html` (com `img\`, inclusive `img\imp\` de 14/10; PARTE -16 §0) | no git, mais antiga: [docs/plano/paginas-claude-ai/escolhas/index.html](../../docs/plano/paginas-claude-ai/escolhas/index.html) e os scripts de desenho ao lado; montadores de 14/10: `...\sessao-2026-10-14\escolhas\montar.py`, `montar2.py`; desenhos da impressão: `...\sessao-2026-10-14\desenhos_impressao.py` |
| Layout | `...\sessao-2026-10-13\paginas\pub-layout\layout-editor-impressao.html` (com `img\` e `telas\`) | no git: [docs/plano/paginas-claude-ai/layout/index.html](../../docs/plano/paginas-claude-ai/layout/index.html); conteúdo do banco feito por [docs/plano/para_a_pagina_de_layout.py](../../docs/plano/para_a_pagina_de_layout.py) (lê a pasta `plano-24-09-2026\layout\`) |
| Conferência | `...\sessao-2026-10-13\paginas\pub-conf\conferir-g6-layout3-corte.html` (com `img\`) | versões anteriores na mesma pasta; montadores em `...\sessao-2026-10-13\scripts\` (`montar_conferencia_layout3.py`, `montar_conferencia_corte.py`, `respostas_na_conferencia.py`) |
| Andamento | no git: [docs/plano/paginas-claude-ai/andamento/index.html](../../docs/plano/paginas-claude-ai/andamento/index.html) | plano para a coleção `plano`: [docs/plano/para_a_pagina_de_andamento.py](../../docs/plano/para_a_pagina_de_andamento.py) (rodar toda vez que o plano mudar) e o `...\sessao-2026-10-14\andamento\sincronizar_plano.py` (grava só as partes que mudaram) |
| Quando revisar | no git há só a versão do estudo, **sem banco**: [relatorios/revisar-criterios-2026-10-06/pagina-claude-ai/index.html](../../relatorios/revisar-criterios-2026-10-06/pagina-claude-ai/index.html). A versão publicada com as rodadas é mais nova | cópia da página publicada em 08/10: `D:\programas\EditorImpressao-arquivos\backup-artefatos-2026-10-08\quando-revisar\pagina\index.html`; perguntas de cada rodada em `relatorios/revisar-decisoes/rodada-N/rodada-N-perguntas.json` (formato da coleção `decisoes`) |

Leia-me das fontes no git: [docs/plano/paginas-claude-ai/LEIA-ME.md](../../docs/plano/paginas-claude-ai/LEIA-ME.md) (de 06/10/2026; os arquivos de `sessao-2026-10-13\paginas\` são mais novos).

**Cópias do banco** (só ler; servem para conferir o que ele escreveu num dia):
- 08/10/2026, as quatro primeiras páginas (HTML + banco): `D:\programas\EditorImpressao-arquivos\backup-artefatos-2026-10-08\` (`andamento\`, `escolhas\`, `layout\`, `quando-revisar\`, cada uma com `banco\` e `pagina\`).
- 12/10/2026: `D:\programas\EditorImpressao-arquivos\sessao-nuvem-2026-10-09\banco-das-paginas\`.
- 12/10/2026, layout antes da rodada 12 refeita: `...\plano-24-09-2026\layout\banco-antes-2026-10-12\` e `respostas-rodada12-2026-10-12\`.
- 13/10/2026: `D:\programas\EditorImpressao-arquivos\sessao-2026-10-13\banco-das-paginas\` (`conferencia\respostas\`, `escolhas\respostas\`).
- 14/10/2026: `D:\programas\EditorImpressao-arquivos\sessao-2026-10-14\escolhas\` (`decisoes\`, `respostas\`, `decididas\`).

---

## 4. Como publicar e ler (descobertas)

**Publicar**
- **Página feita em outra sessão:** a primeira publicação é recusada e devolve a versão no ar; a segunda, igual, também é recusada ("identical content"); a **terceira**, igual, passa (PARTE -16 §6). Em 13/10 tinha passado já na segunda (PARTE -15 §6). Antes, ler a página com `Artifact read`.
- **O arquivo local é só o miolo** (de `<title>` até o fim do `<script>`), sem o esqueleto que o serviço acrescenta (PARTE -15 §6).
- **Imagens novas vão em `files`, com `root`;** o resto dos arquivos publicados fica (PARTE -16 §6). Republicar sem `files` mantém as imagens que já estão lá (LEIA-ME das fontes).
- **Sem passar `contract`, o contrato da página se mantém** (0.2.69 / 0.2.70, em que as fotos aparecem). Página publicada com o contrato novo 0.2.75 pode não mostrar fotos (PARTE -14 §6; em 09/10 a de conferência foi republicada com 0.2.69 por isso).
- Depois de mexer no HTML por script, validar o JavaScript (`node -e "new Function(...)"`) e abrir no Chrome sem tela (PARTE -10 §4). Desenho SVG se confere com `chrome.exe --headless=new --screenshot=<png> --window-size=1220,760 file:///<svg>` (o Qt sem tela não tem fontes; PARTE -16 §6).

**Banco**
- Escrever **sempre com `if_version`** (a versão lida). O Samuel responde **enquanto a gerente trabalha**: um `batch` falhou porque ele comentou no meio; reler e refazer (PARTE -16 §6).
- A gerente lê quando ele avisa ("respondi", "feito"), copia palavra por palavra para `relatorios/` e para o Registro, e marca `status: "decidida"` (PARTE -12 §0). Passo a passo em [conferencias.md](../conferencias.md), "Como registrar uma resposta nova".
- A página de andamento ficou com o plano parado de 09/10 a 14/10: sincronizar a coleção `plano` sempre que o plano mudar (PARTE -16 §6).

**Abrir no navegador dele**
- Com `start "" "<endereço>"` no Windows. A ação `open` da ferramenta Artifact responde "Opened" mas **não chega ao navegador dele** — ele reclamou (PARTE -12 §0 e §4).
- Às vezes a página abre antes de o banco ser gravado e mostra a rodada velha: pedir F5 (PARTE -13 §5).
- **Quando abrir sozinha** (regra de 06/10/2026, [CLAUDE.md](../../CLAUDE.md) §10 item 10): "sempre que tiver paginas de conferencia prontas, pode abrir automaticamente no meu pc, caso eu já tenha feito a ultima pagina de conferencia e te dado ok." Se houver conferência sem resposta, só avisar no chat.

**Comentários dele**
- **Comentário com dúvida se responde NA página** (07/10/2026): "não me responda no chat quando tiver questionamentos nas conferencias, responda nas conferencias." e "o meu comentario serve como resposta, porque você não responde ele e me mostra a questão de novo?" A gerente refaz a explicação respondendo ao que ele escreveu, mostra a pergunta de novo com opções tiradas do comentário e, se surgir outra decisão, cria pergunta nova na mesma página. No chat, só um aviso curto.
- **Comentário fixado** (07/10/2026): "eu acho que ele devia subir e virar um comentario fixado junto quando voltasse, para que dai eu colocasse outro e tivesse referencia do que foi colocado antes." → copiar para `historico` da pergunta e esvaziar o `comentario` da resposta (a opção marcada fica).
- Ele também pediu, na sessão na nuvem, "quando tiver mais perguntas me chama aqui" (avisar no chat; a resposta continua na página; PARTE -14 §6).

**O formato de pergunta que ele entende**
- Começa por **"O que você está escolhendo: …"**; no máximo três parágrafos curtos; a primeira imagem é **só a parte que muda, ampliada**, depois a tela inteira; **sempre a opção "Ainda não entendi"** (PARTE -15 §6). Toda pergunta com **imagem por opção** — "o jeito rápido e o manual" sem imagem ele não entendeu (PARTE -13 §0 e §4).
- Em conferência de imagens, **cada quadro tem a sua pergunta e o seu comentário** (PARTE -14 §6). Um trabalho por aba: em 12/10 dois trabalhos um embaixo do outro o confundiram ("ele trouxe junto coisas do layout").
- Imagem de antes/depois: fileira de quadros lado a lado, **preto = fica no papel, vermelho = o programa tirou**, com a **folha inteira em cima**; nunca grade 3×3; nunca retângulo por cima do conteúdo (PARTE -12 §0; PARTE -9 §1).
- **Antes de publicar, comparar cada foto com as escolhas dele.** A aba do layout foi com fotos velhas e ele reclamou (PARTE -15 §5); em 20/10 o verificador achou o mesmo risco na aba 4 do "Para revisar".
- Pergunta já respondida não volta sem motivo: em 14/10 ele reclamou "Porque essa opção voltou ? eu já não tinha respondido?" (`g10-ajustar-todas`).

---

## 5. Antes das páginas: os formulários HTML (até 06/10/2026)

`relatorios/conferir-aqui.html`, `-2` a `-15` e `relatorios/decisoes-2026-10-01.html`: cartões com ORIGINAL · ANTES · AGORA, botões Bom/Ruim/Não sei e "Copiar respostas"; ele colava no chat e a gerente gravava em `relatorios/conferencia-samuel-*.md`. As exigências dele daquela época continuam valendo: toda pergunta com foto, dizer onde olhar, resultado ao lado do original, opções por extenso (PARTE -9 §1). Lista completa em [conferencias.md](../conferencias.md).
