# Fontes das páginas do claude.ai (artifacts com banco de dados)

Cópia da fonte (`index.html`) de cada página, para uma conversa nova poder republicar sem depender da pasta temporária da sessão de 06/10/2026. As **imagens e telas** publicadas ficam no próprio artifact (um republish sem `files` mantém as que já estão lá); as originais estão em `relatorios/` e em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`.

| Página | Endereço | Fonte aqui |
|---|---|---|
| Escolhas do Editor de Impressão (comportamento) | https://claude.ai/artifact/EJoJq5mocxi3vbNxU8ZecV | `escolhas/index.html` |
| Layout do Editor de Impressão | https://claude.ai/artifact/QuzVaghq2tz2WVwJ1AyMWu | `layout/index.html` (conteúdo: `docs/plano/para_a_pagina_de_layout.py`) |
| Andamento do programa | https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy | `andamento/index.html` (plano: `docs/plano/para_a_pagina_de_andamento.py`) |
| Quando revisar uma página | https://claude.ai/artifact/NeCgyTotRfqsdXntn9vMUc | `relatorios/revisar-criterios-2026-10-06/pagina-claude-ai/` (o `modelo.html` com `__DADOS__` está no scratchpad; a versão publicada já tem os dados) |

Para republicar: Artifact `publish` com `url` da página e `file_path` deste `index.html` (copiado para o scratchpad da sessão nova). Antes, ler a página (`Artifact read` sem `path`) — publish num artifact não lido nesta conversa é recusado. Conteúdo (perguntas, respostas, plano) fica no banco: ler/escrever com ArtifactData. Abrir no navegador do Samuel com `start "" "<endereço>"`.
