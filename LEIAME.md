# Editor de Impressão

Recupera PDFs de livros antigos escaneados e prepara para reimpressão em cadernos.
Feito para o Kaique usar sem precisar entender de técnica.

## Para usar (o programa pronto)

`dist\EditorImpressao.exe` — arquivo único, não precisa instalar nada e não
precisa de Python na máquina. Basta copiar e dar dois cliques.

O fluxo é: arraste o PDF → marque o que quer fazer → confira → processar.
Os PDFs prontos vão para **Documentos \ Editor de Impressão**.

### Atalhos de teclado

| Tecla | O que faz |
|---|---|
| ← → | página anterior / próxima |
| Espaço | marca "está certo" e vai para a próxima |
| Tab | pula para a próxima página marcada em laranja |
| 1 2 3 4 | Original / Preto e branco / Melhorar / Mágico pro |
| R | girar a folha |
| Delete | apagar a página |
| Ctrl+Z | desfazer (sem limite) |
| Ctrl+Shift+Z ou Ctrl+Y | refazer |
| Ctrl+Enter | confirmar e processar |

## Para mexer no código

```
.venv\Scripts\python.exe -m pytest tests -q      # 42 testes
.venv\Scripts\python.exe main.py                 # abre o programa
.venv\Scripts\python.exe empacotar.py            # gera o .exe
```

### Testes por linha de comando (não abrem janela)

```
python teste_pdf_io.py    "livro.pdf"   # leitura e escrita de PDF, memória
python teste_filtros.py   "livro.pdf"   # comparativo dos 4 filtros lado a lado
python teste_dividir.py   "livro.pdf"   # lombada, deskew e recorte por folha
python teste_pipeline.py  "livro.pdf"   # ponta a ponta, com o painel de alertas
python teste_interface.py "livro.pdf"   # dirige a interface e salva capturas
```

## Como está organizado

`core/` não importa nada de `ui/` — todo o processamento roda sem janela.

```
core/pdf_io.py      abrir/salvar PDF, página <-> imagem, limite automático de DPI
core/filtros.py     os 3 filtros + original
core/dividir.py     detecção da lombada
core/endireitar.py  deskew por perfil de projeção
core/recortar.py    corte das bordas
core/cadernos.py    imposição (a matemática dos cadernos)
core/analise.py     os alertas e as sugestões
core/pipeline.py    orquestra tudo, uma página por vez
modelos.py          ConfigFolha (entrada), ConfigPagina (saída), Projeto, Ação
historico_acoes.py  desfazer/refazer ilimitado, gravado em acoes.jsonl
historico.py        projetos recentes e pastas de dados
ui/                 PySide6: 4 telas + widgets
```

### Duas decisões que valem explicação

**Dois níveis de configuração.** A especificação previa uma lista só de
`ConfigPagina`. Na prática existem duas unidades diferentes: a **folha** que veio
no PDF (onde mora a linha de corte) e a **página** que vai sair (onde moram o
filtro, o recorte e o ângulo). Uma folha dividida vira duas páginas, e cada uma
pode ter filtro próprio — que é o requisito de "filtro por página". As abas da
tela de conferir seguem exatamente essa separação.

**Recorte e ângulo são por página, não por folha.** O pipeline aplica os dois
*depois* de dividir, então cada metade tem sua própria sombra de lombada e pode
estar torta de um jeito diferente.

## Onde o programa guarda as coisas

```
%LOCALAPPDATA%\EditorImpressao\
├── historico.json              projetos recentes
├── erros.log                   erros técnicos (nunca aparecem na tela)
└── projetos\<nome>\
    ├── projeto.json            o estado atual
    ├── acoes.jsonl             o histórico completo, uma ação por linha
    └── posicao.json            onde a pilha de desfazer parou
```

Fechar e reabrir o programa preserva o projeto **e o histórico de ações**: ainda
dá para desfazer.

## Bibliotecas

| O quê | Para quê | Licença |
|---|---|---|
| PySide6 | interface | LGPL |
| PyMuPDF | ler e escrever PDF | AGPL/comercial |
| OpenCV, numpy | processamento de imagem | Apache 2.0 / BSD |
| **DoxaPy** | binarização Sauvola (o Preto e branco) | **CC0** |
| scikit-image | plano B do Sauvola | BSD |
| Pillow | codificação PNG, inclusive 1 bit | HPND |

O ScanTailor serviu só como referência de algoritmo — é GPL v3 e C++/Qt, então
nada dele foi incorporado. O que se aproveitou foi a confirmação de que
Sauvola/Wolf é o caminho certo para papel amarelado e bleed-through.

> Atenção sobre licença: o PyMuPDF é **AGPL**. Para uso interno do instituto está
> tudo certo. Se um dia o programa for distribuído fora, ou o código-fonte
> precisa acompanhar, ou é preciso comprar a licença comercial, ou trocar por
> pypdfium2 (BSD).
