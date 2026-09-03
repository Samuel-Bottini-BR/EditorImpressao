# Handoff completo — Editor de Impressão

Documento de continuidade do projeto. Reúne tudo que foi discutido, decidido e construído até aqui. Serve para retomar o trabalho em qualquer conversa nova sem perder contexto.

Última atualização: 29/07/2026.

---

## 1. O projeto e as pessoas

**Idealizador:** Pe. Rosenei, sacerdote católico. Fundou um instituto de preservação de livros, cujo objetivo é (a) preservar livros que não são mais publicados, (b) reviver as formas tradicionais de fabricação de livros e (c) manter o espírito católico de guardar o conhecimento acumulado ao longo dos séculos.

**Situação do instituto:** ainda **não tem sede física**. É apoiado por uma empresa sementeira, a **Sementes Ponto Alto**, que dá ajuda mensal e cede um espaço no depósito para guardar livros. O padre conta com alguns colaboradores.

**Kaique:** o impressor do instituto. É o **usuário final** dos aplicativos. **Não tem conhecimento técnico** nenhum. Hoje ele usa o **CamScanner (no celular)** para limpar as páginas escaneadas antes de imprimir. Todo o design precisa levar isso em conta: a interface é para ele.

**Samuel:** coordena a parte digital do projeto, toma as decisões e faz a ponte com o Claude Code. (É quem conduz estas conversas.)

**Objetivo geral do trabalho no Claude:** organizar o projeto para captar mais recursos, conseguir uma sede, e criar as ferramentas de que o instituto precisa.

---

## 2. As frentes do projeto (visão macro)

1. **Institucional / captação** — formalizar (CNPJ, estatuto), material para doadores, meta de sede. Ideia levantada: parceria com uma universidade (de preferência católica) para acesso a equipamento de digitalização e a espaço.
2. **Produção do livro (fluxo do Kaique)** — do livro físico velho ao PDF limpo e ao livro reimpresso. **É a frente em andamento.**
3. **Biblioteca / catalogação** — cadastrar, separar por tema, saber o que existe e onde está. Descoberta relevante: existem programas prontos de catálogo de arquivo (**ArchivesSpace, PastPerfect, CollectiveAccess, Preservica**) que valem investigar antes de construir do zero.
4. **Transcrição** — passar textos antigos para digital.
5. **Site** — vitrine, catálogo público, canal de doação.

**Frente ativa: a nº 2.** As outras estão em espera.

---

## 3. Pesquisa de ferramentas de digitalização (contexto)

O Kaique já tinha pesquisado as ferramentas certas. O fluxo profissional de arquivistas é:

- **NAPS2** (v8.2.1) — escanear. Tem OCR embutido, versão portátil, compartilhamento de scanner por rede, e linha de comando.
- **ScanTailor Advanced / Experimental** — limpar e endireitar (o original, `scantailor.org` / 0.9.11.1, está congelado desde 2012; o repositório foi arquivado em 2020). É **manual**, C++/Qt, GPL v3.
- **OCRmyPDF** (v17.x, precisa Python 3.11+, Tesseract, Ghostscript) — camada de texto pesquisável. Traz o **unpaper** embutido com `--clean`.
- **PDF-XChange Editor** (v11) — 70% grátis, faz deskew/OCR/organização de páginas; tem desconto para caridade.

**Hardware (para preservação, captura não destrutiva):** scanner overhead (CZUR, ScanSnap SV600), filtro polarizador contra reflexo, 600–1200 DPI para captura. Bibliotecas universitárias às vezes emprestam scanner profissional de graça.

**Recuperação de cor:** GMIC (dentro do Krita) para livros ilustrados.

**Conclusão estratégica:** a maioria dessas ferramentas já existe pronta. O que o instituto precisa criar de novo é (a) o app "CamScanner para PC" do Kaique e, depois, (b) a catalogação e o site.

---

## 4. Histórico do aplicativo (por que refizemos)

1. `imposicao_cadernos.py` — script de imposição de cadernos (matemática correta).
2. v1/v2 (HTML no navegador) — só imposição; a v2 já montava páginas lado a lado.
3. v3 (HTML) — ganhou filtros e deskew, mas em JavaScript, lento.
4. v4/v5 (desktop, customtkinter) — 4 filtros e 4 modos, mas **travava** (memória e customtkinter) e a **qualidade dos filtros ficou ruim**.

**Decisão:** reconstruir do zero em **Python + OpenCV + PySide6**, reaproveitando o que funcionava (matemática dos cadernos, processamento página a página) e resolvendo o que não funcionava (filtros e estabilidade).

---

## 5. Decisões técnicas firmadas

- **Objetivo:** um **CamScanner para PC** — programa único de desktop, sem jargão, à prova de erro.
- **Stack:** Python 3.11+ (a máquina tem 3.14, e roda tudo — **não rebaixar**), PySide6, PyMuPDF, OpenCV, numpy, Pillow, DoxaPy, scikit-image.
- **PySide6 sempre; tkinter/customtkinter nunca.**
- **DoxaPy (Sauvola/Wolf)** para o preto e branco — licença CC0. Plano B: scikit-image. **Nada de fórmula caseira de binarização.**
- **Processar uma página por vez** (ler → processar → escrever → soltar). Nunca acumular páginas em memória.
- **OCR adiado** para a v2.
- **Escanear direto do scanner:** fora de escopo (o Kaique usa outro programa).
- **Como os repositórios entram:**
  - DoxaPy e scikit-image = dependências reais.
  - Projetos de CamScanner em OpenCV (hasanfirnas/PDF_Magic-Color_filter, ArashNasrEsfahani, satvik007) = **receita** a estudar, não copiar.
  - ScanTailor = referência de algoritmo apenas (GPL, C++, não embutir).
  - OCRmyPDF e NAPS2 = futuro.
- **Regra de licença:** só incorporar código permissivo (CC0/MIT/BSD/Apache). Nada de GPL.
- **PyMuPDF é AGPL:** ok para uso interno do instituto; se distribuir fora, abrir o código, comprar licença, ou trocar por pypdfium2 (BSD). Toda a leitura de PDF está isolada em `core/pdf_io.py`, o que torna a troca simples.

---

## 6. Funções do aplicativo

Todas **independentes e marcáveis** — usar uma, várias ou todas.

1. **Dividir folhas ao meio** — muitos scans trazem duas páginas do livro numa folha (paisagem). Detecta a lombada pela faixa escura central; linha de corte **arrastável com o mouse**; "não dividir esta"; "usar em todas"; girar.
2. **Limpar a folha** — três filtros (ver seção 8):
   - **Preto e branco (Eco)** — Sauvola/Wolf; tira amarelado + bleed-through.
   - **Melhorar** — normaliza iluminação, preserva cor.
   - **Mágico pro** — Melhorar + realce (saturação, CLAHE, nitidez).
   - Mais **Original**.
   - **Filtro por página** (como o CamScanner): páginas diferentes podem ter filtros diferentes no mesmo PDF. Aplicar "só nesta", "usar em todas", "só nas próximas".
3. **Endireitar folhas tortas (deskew)** — perfil de projeção, limite ±5°.
4. **Cortar as bordas** — tira borda preta do scanner e sombra da lombada; retângulo com alças ajustáveis.
5. **Montar cadernos para impressão (imposição)** — múltiplo de 4, padrão 20; monta duas páginas por folha; se só isso estiver marcado, copia páginas direto sem rasterizar.

**Ajustes manuais** (o automático propõe, o usuário corrige):
- **Força do preto** — medidor deslizante (não três botões), mapeia o `k` do Sauvola.
- **Intensidade** (Mágico pro) e **Clareza do fundo** (Melhorar) — também deslizantes.
- **Apagar páginas** — em branco, tremidas, dedo do operador.
- **Ajustar o ângulo na mão.**
- **Desfazer/refazer ilimitado**, gravado em arquivo (`acoes.jsonl`), sobrevive a fechar o programa. Ctrl+Z / Ctrl+Shift+Z. "Usar em todas" conta como uma ação só.

**Regra de ouro:** o botão de sugestão do alerta **nunca substitui** o controle manual — tudo pode ser feito à mão, inclusive em páginas sem alerta. E o resultado do filtro **nunca pode ficar menos legível que o original**.

---

## 7. Sistema de alertas

O programa faz tudo sozinho, mas **avisa onde teve dificuldade**, para o usuário não conferir 500 páginas uma a uma — só as marcadas em laranja com "!". Casos detectados: página colorida, lombada incerta, não parece dupla, muito torta, ângulo suspeito, página em branco, escura demais, apagada demais (texto sumiu), corte pegou conteúdo, resolução baixa, tamanho diferente.

Cada alerta **sugere a correção com um clique**. Painel agrupa por tipo. **Calibrar para menos de 10% das páginas marcadas** num livro bem escaneado — senão o alerta vira ruído.

---

## 8. Filtros — a armadilha já resolvida

A receita difundida de "magic color" (`img / GaussianBlur(img) * 255`, por canal) **estraga capas coloridas**: numa área azul uniforme o próprio azul é o fundo, a divisão lava a cor e desloca o matiz (o título azul virou vermelho no teste). Correção adotada em `core/filtros.py`:
1. dividir pelo fundo **relativo ao nível do papel**, não ao branco absoluto, com ganho igual nos 3 canais (preserva matiz);
2. **pesar** a correção por quanto o fundo local ainda parece papel — cai a zero em conteúdo escuro;
3. branquear com **curva de ombro** no canal L do LAB, nunca multiplicação linear.

Desempenho: fundo estimado numa miniatura de ~400 px e reescalado — ~10× mais rápido (5,0 s → 0,5 s por página a 300 DPI).

---

## 9. Interface — as 4 telas

Fluxo: **arrasta o PDF → marca o que fazer → confere página a página → escolhe onde salvar → processa.**

1. **Início** — área de arrastar + **histórico de projetos recentes** (nome, data, páginas, filtro, abrir, abrir pasta).
2. **O que fazer** — checkboxes independentes; filtros aparecem sob "Limpar"; resumo em português ao vivo.
3. **Conferir (a prévia mora aqui)** — uma tela só, com abas que aparecem conforme o marcado: **"Onde cortar"** (folha com linha de corte arrastável), **"Filtro"** (os 4 filtros lado a lado, página real), **"Bordas"** (retângulo com alças). Tira de miniaturas, alertas em laranja, contador clicável no topo. **Tela ampliada** com zoom/arrasto e modo comparar.
4. **Pronto** — onde salvou, instruções de impressão, abrir pasta / imprimir agora / fazer outro.

**Onde salvar:** o usuário escolhe a pasta ("Escolher pasta"), edita o nome do arquivo; lembra a última usada.

**Atalhos:** ← → navega; Espaço marca "está certo" e avança; Tab pula para a próxima laranja; 1 2 3 4 trocam filtro; R gira; Delete apaga; Ctrl+Z / Ctrl+Shift+Z desfaz/refaz; Ctrl+Enter processa.

**Regras rígidas de interface:** textos **com** acento (UTF-8); caminhos de disco **sem** acento; **nenhum emoji** em rótulo; layout empilhado de verdade (QVBoxLayout), controles **nunca** por cima da imagem; erro nunca vira stack trace na tela (grava em `erros.log`, mostra aviso amigável).

---

## 10. Arquitetura e estado (do briefing técnico)

`core/` não importa nada de `ui/` — processamento roda sem janela.

```
main.py             ponto de entrada; aceita um .pdf como argv[1]
modelos.py          ConfigFolha, ConfigPagina, Projeto, Acao
configuracoes.py    preferências (última pasta usada)
historico.py        projetos recentes
historico_acoes.py  desfazer/refazer ilimitado (acoes.jsonl)
registro.py         erros.log

core/pdf_io.py      PDF <-> ndarray, limite automático de DPI, EscritorPDF incremental
core/filtros.py     Original / Preto e branco (Sauvola) / Melhorar / Mágico pro
core/dividir.py     detecção da lombada (perfil de intensidade e de tinta)
core/endireitar.py  deskew por perfil de projeção + giro de 90°
core/recortar.py    detecção e corte das bordas pretas do scanner
core/cadernos.py    imposição, impor_pdf, instruções de impressão
core/analise.py     alertas, sugestões, detecção de cor, DPI estimado
core/pipeline.py    analisar_projeto() e processar(), uma página por vez

ui/                 PySide6: tela_inicio -> tela_opcoes -> tela_conferir -> tela_final
                    + tela_ampliada, tarefas.py (QThread), estilo.py, widgets/
```

**Modelo de dados em dois níveis** (evolução acertada feita pelo Claude Code):
- **ConfigFolha** = o que veio no PDF de entrada (`dividir`, `posicao_corte`, `confianca_corte`, `rotacao`, `angulo_detectado`, `apagada`, `e_paisagem`, `alertas`, `revisada`).
- **ConfigPagina** = o que vai sair no PDF final. Uma folha dividida vira **duas** páginas (`metade` = inteira/esquerda/direita). Guarda `filtro`, `recorte`, `angulo_manual`, `tem_cor`, `apagada`, e os três ajustes separados (`forca_preto`, `clareza_melhorar`, `intensidade_magico`, 0–100, 50 no meio — separados para que trocar de filtro e voltar devolva o ajuste daquele filtro).

Recorte e ângulo moram na **página**, não na folha, porque são aplicados *depois* de dividir (cada metade tem a sombra de um lado só e pode estar torta diferente). As abas de conferir seguem essa separação: "Onde cortar" edita folhas, "Filtro" edita páginas.

**Pipeline (ordem obrigatória):** 1. dividir → 2. cortar bordas → 3. endireitar → 4. filtro → 5. montar cadernos. Apagadas somem após a etapa 1. Análise roda a **150 DPI** (segundos); processamento final no DPI escolhido (padrão 300); caminho rápido `so_cadernos` quando nada altera imagem.

**Onde guarda estado:** `%LOCALAPPDATA%\EditorImpressao\` com `historico.json`, `configuracoes.json`, `erros.log` e `projetos\<nome>\` (`projeto.json`, `acoes.jsonl`, `posicao.json`). Fechar e reabrir preserva projeto **e** histórico de ações. Desinstalar não apaga essa pasta, de propósito.

---

## 11. Testes e empacotamento

- `pytest tests -q` — **59 testes** (`tests/test_core.py`, `tests/test_cadernos.py`).
- Scripts de linha de comando na raiz (não abrem janela, recebem um PDF): `teste_pdf_io.py`, `teste_filtros.py`, `teste_dividir.py`, `teste_pipeline.py`, `teste_criterios.py`, `teste_bateria.py`, `teste_robustez.py`, `teste_livros.py`, `teste_acervo.py`. `teste_interface.py` dirige a interface e salva capturas.
- **`empacotar.py`** gera três formatos em `dist\`: instalador (`EditorImpressao-Setup.exe`, via Inno Setup 6 + `instalador.iss`), portátil em pasta, e arquivo único. Nenhum precisa de Python na máquina do Kaique.
- Observação de empacotamento: `.exe` fica grande (150–300 MB), antivírus pode dar alerta falso (sem assinatura digital), e OpenCV/PySide6/DoxaPy às vezes precisam de ajuste no PyInstaller. Pedir o `.exe` só no fim, depois que tudo roda pelo Python. Testar em máquina **sem** Python.

**Máquina:** Python 3.14; GPU GTX 1650 4 GB (sem tensor cores — nada que dependa de float16 rápido). Pasta do projeto: `C:\Users\fotog\Desktop\EditorImpressao` (venv em `.venv`).

---

## 12. Arquivos de teste (acervo real)

Pasta: `C:\Users\fotog\Desktop\LIVROS PARA FAZER TESTE` (nome com espaços — usar aspas; **não sobrescrever originais**). Contém 9 livros históricos, entre eles:
- **Graduale - Saeculum XIV** (277 MB) — manuscrito iluminado; teste de memória e de preservação de cor.
- **Livro de Horas - Luís XIV** (108 MB) — iluminuras (ouro e vermelho).
- **Marial de sermoens - Frei Balthasar Paez** (209 MB) — grande, teste de memória.
- **Rhetorica Christiana - Fray Diego Valadés**, **Schön Neues Modell Buch** — xilogravuras de traço fino.
- **Giovambattista Palatino**, **Na escola de Jesus**, **POINTS d'ANCIENNES BRODERIES**, **Sobre a Consolação da Filosofia (Boécio)**.

PDF de teste menor: `pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf` (70 folhas duplas, capa azul — bom caso para capa colorida).

---

## 13. Os 4 casos do Kaique (critério de sucesso)

Ditos pelo próprio Kaique. Se o programa resolver estes quatro, substitui o CamScanner:
1. **Folha amarelada com texto preto** → tirar o amarelo, deixar as letras → Preto e branco.
2. **Livro amarelado COM imagens coloridas** → tirar o amarelo **e** preservar as cores (e melhorar um pouco) → Melhorar / Mágico pro.
3. **Páginas tortas** → deskew.
4. **Bleed-through** — papel tão velho que ficou translúcido e o texto do verso aparece. **O CamScanner já resolve isso; o nosso precisa resolver pelo menos igual.** É o teste decisivo.

---

## 14. Estado atual e problemas em aberto

**Estado:** programa funcional de ponta a ponta, bateria de testes em livros reais já rodada. Último commit: "Bateria do acervo: detectar_cor corrigida e três bugs de teste".

**Problemas identificados nos testes com o acervo (a resolver):**

1. **Preto e branco pior que o original em papel manchado (grave).** Em impressos antigos (ex.: `bleed_through_pag0575`), o Sauvola está **quebrando as letras** e enchendo o fundo de pontinhos — o original amarelado fica mais legível. Causa provável: janela do Sauvola pequena demais, pegando a textura do papel como texto. Caminhos a testar: janela bem maior (calculada por DPI/altura), algoritmo **Wolf** (e Gatos/NICK/ISauvola), **pré-processamento** (normalizar iluminação + leve desfoque + CLAHE) antes de binarizar, despeckle mais agressivo, e **ajuste automático de parâmetro por página** (livro do séc. XIV e livro do séc. XX não usam o mesmo valor).

2. **Navegação entre páginas ruim.** Pedidos: setas fixas nas pontas da tira; roda do mouse rola a tira; roda do mouse sobre a imagem **troca de página** (com zoom ativo, dá zoom); miniatura atual sempre visível; campo "ir para página"; Page Up/Down 10 páginas; Home/End; barra de rolagem mais alta.

3. **Acentos** vinham falhando na interface ("Impressao", "Magico", "pagina") — reforçado várias vezes; verificar se foi resolvido de fato.

**Regra que vale para os ajustes de filtro:** criar verificação que compara legibilidade antes/depois e avisa quando o filtro **piora** a página.

---

## 15. Documentos de referência já criados

- **`prompt-claude-code-editor-impressao.md`** — especificação completa e prompt para construir o app (stack, arquitetura, regras críticas, funções, wireframes das telas, parâmetros dos filtros, modelos de dados, ordem de construção, 15 critérios de aceitação, projetos de referência do GitHub).
- **`prompt-testes-livros.md`** — bateria de testes com o acervo real (fichas `.txt` por livro, testes por função, atenção a iluminuras/xilogravuras/bleed-through, robustez, vazamento de memória, integridade da contagem, comparação com o CamScanner). Traz no topo o aviso de **não recomeçar do zero — só ajustar o que existe**.

---

## 16. Como continuar em outra conversa

1. Continuar **dentro deste Projeto** (a memória do Projeto me dá o contexto automaticamente).
2. Na primeira mensagem, anexar este handoff **e** colar o texto dele (os anexos às vezes chegam vazios; colar garante a leitura).
3. Mandar os prints do programa rodando, com uma frase dizendo o que incomodou em cada um.
4. Agrupar os prints por assunto (filtro, navegação, etc.) para atacar um problema de cada vez.
5. Ao pedir mudanças ao Claude Code, sempre reforçar: **alterar o app existente, não refazer do zero**; dizer o que pretende mudar e por quê antes de mexer; commit antes de começar.

**Próximo passo mais importante:** resolver o filtro Preto e branco em papel manchado (problema 1 da seção 14) e a comparação lado a lado com o CamScanner nas páginas difíceis do acervo. É o que decide se o programa substitui o celular do Kaique.
