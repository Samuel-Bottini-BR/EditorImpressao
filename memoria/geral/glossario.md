# Glossário

Palavras e siglas que aparecem nos documentos do projeto, em português simples. Montado em 20/10/2026 a partir do
[plano](../../docs/plano/PLANO-DEFINITIVO.md), do [CLAUDE.md](../../CLAUDE.md) e do
[histórico](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md).
Quando um termo é nome de botão que o Kaique vê, está entre aspas, como aparece na tela.

> O Kaique nunca vê os termos técnicos desta lista (Sauvola, DPI, deskew...). Na tela tudo é em português comum
> (CLAUDE.md §1). Ver [kaique.md](kaique.md).

## Pessoas e lugares

| Termo | O que é |
|---|---|
| **Samuel** | Quem dirige o projeto e o único que aprova (marca `[x]`, `[~]`, `[-]` no plano). Ver [jeito-do-samuel.md](jeito-do-samuel.md). |
| **Kaique** | O impressor que vai usar o programa; sem formação técnica. Ver [kaique.md](kaique.md). |
| **Pe. Rosenei / Instituto São Bento** | Para quem o projeto existe: preservação de livros esgotados. |
| **gerente** | A conversa do Claude Code que fala com o Samuel, divide o trabalho, chama os agentes e junta tudo no `fase-1`. Não escreve código linha por linha. |
| **implementador, verificador, pesquisador, agente de layout** | Os quatro agentes (regras em `.claude/agents/`). O verificador nunca marca aprovado. Ver [regras-de-trabalho.md](regras-de-trabalho.md). |
| **acervo** | Os livros de teste, somente leitura: `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE` (nove livros, 2903 folhas). Ver [livros/](../livros/). |
| **pasta de dados** | `%LOCALAPPDATA%\EditorImpressao`: projetos salvos, `historico.json`, `configuracoes.json`, `erros.log`. Testes nunca podem gravar nela (regra de 29/09/2026). |
| **PC do Samuel / notebook do Kaique** | As duas máquinas que contam. O PC é a régua de velocidade de todo dia; o notebook é a régua final. Ver [pc-e-github.md](pc-e-github.md). |

## O programa

| Termo | O que é |
|---|---|
| **os filtros** | Original · Preto e branco · Melhorar · Mágico pro, e "Tirar o fundo" (só em PDF com camadas, desde 29/09/2026). Página nova abre sempre em Original. |
| **Mágico pro** | O nosso filtro que imita o "Mágico Pro" do CamScanner, que o Kaique usa hoje (o resultado-alvo do plano, §2). |
| **"Tirar o fundo"** | Filtro do item [1.1](../itens/1.1.md): em PDF do Internet Archive (duas camadas), joga fora a camada de baixo (papel) e fica com a de cima (tinta). |
| **camadas** | PDF que já vem com o fundo separado da tinta (Internet Archive: Opus Majus, Palatino). Ver [referencias/internet-archive.md](../referencias/internet-archive.md). |
| **"Só as letras" / modo Misto** | Caixinha dentro do Preto e branco: só as letras viram preto e branco; gravuras, fotos, molduras e iluminuras ficam como no original. Vem do modo Misto do ScanTailor. Item [1.5](../itens/1.5.md). |
| **"Guardar a tinta forte" · "Guardar tudo" · "Guardar só o texto"** | Os três jeitos do "Só as letras" (nomes da rodada 10 do layout, 07/10/2026). De fábrica, "Guardar a tinta forte". |
| **"Limpar a sujeira"** | O limpar pontinhos (item [2.7](../itens/2.7.md)): "Sem limpeza" (de fábrica desde 07/10/2026) · "Limpeza bruta" (o nosso) · "Limpeza cuidadosa: leve / média / forte" (a do ScanTailor). |
| **"Para revisar"** | A lista de páginas que o programa acha que o Kaique deve olhar, com o motivo. Ficha [para-revisar.md](../itens/para-revisar.md). |
| **"Trazer de volta nesta página"** | Botão no aviso do "Para revisar" que devolve o desenho que o "Só as letras" apagou, com o lugar já marcado em laranja. |
| **"Deixar em branco" / "Tirar do livro"** | Os dois jeitos de apagar uma página: o primeiro põe uma folha branca no lugar (a encadernação não muda); o segundo tira de vez. |
| **prévia** | A imagem da página na tela (110 a 150 DPI). O PDF final sai a 300 DPI; às vezes os dois decidem diferente ("a tela mostra o que o PDF não tem", Lista de bugs 13/10/2026). |
| **folha × página** | Folha = o que veio no PDF de entrada (`ConfigFolha`); página = o que vai sair no PDF final (`ConfigPagina`). Uma folha dividida vira duas páginas. CLAUDE.md §7. |
| **ordem do preparo** | A ordem das etapas. Livro novo (desde 09/10/2026): dividir → endireitar → cortar → filtro → cadernos. Projeto antigo: dividir → cortar → endireitar. Campo `Projeto.ordem_do_preparo`. |
| **corte / caixa do conteúdo / busca de página** | O corte de bordas é o nosso (`core/recortar.py`). A "busca de página" (PageFinder) e a "caixa do conteúdo" (ContentBoxFinder) são do ScanTailor, prontas no ramo `fase2-caixa-conteudo`, não ligadas. Itens [2.5](../itens/2.5.md) e [2.13](../itens/2.13.md). |
| **borda preta** | Faixa escura do scanner em volta da página. Tirar é o [2.13](../itens/2.13.md); pintar de branco o que sobra é o [2.14](../itens/2.14.md). |
| **cunha do giro** | Os triângulos brancos que aparecem nos cantos quando se endireita a página. No livro novo, escondiam a borda preta da busca do corte (defeito do G6). |
| **cadernos / imposição / livreto** | Montar as páginas na ordem de dobrar e costurar. Livreto = A4 deitada com duas A5. Itens [6.5](../itens/6.5.md) e [2.6](../itens/2.6.md). Ver [referencias/embaralhador.md](../referencias/embaralhador.md). |
| **projeto salvo** | O trabalho de um livro: `projeto.json`, `acoes.jsonl` (o histórico do Ctrl+Z), `posicao.json`, `resumo.json`. Cópia `projeto.antigo-*` antes de recomeçar. |
| **recomeço** | Quando as opções mudam e a conferência começa de novo (com cópia do trabalho antigo). |
| **servidor de páginas** | Processos à parte que desenham as páginas do PDF, para a janela não congelar (desde 30/09/2026). |
| **DLL do ScanTailor** | `core/nativo/st_gravura.dll` (detector de gravura, 1.2) e `core/nativo/st_ferramentas.dll` (limpar pontinhos, dividir, endireitar e, no ramo, a caixa do conteúdo), compiladas do código ORIGINAL do ScanTailor Advanced v1.2.1. Ver [referencias/scantailor.md](../referencias/scantailor.md). |
| **docTR, Kraken, Tesseract, PP-OCR** | Os leitores de texto (OCR). Hoje só servem para achar onde está o texto. De fábrica: docTR + Kraken; Tesseract instalado e desligado. Item [1.3](../itens/1.3.md). Transcrever é a Fase 7. |
| **DocLayout / MobileSAM** | As duas redes neurais que só apontam (nunca desenham): leiaute da página (`modelos/doclayout.onnx`) e seleção por clique (`modelos/mobile_sam`). Ficam fora do git. |
| **Sauvola, Otsu, Wolf** | Jeitos de transformar cinza em preto e branco (binarização). Não existe um vencedor único (CLAUDE.md §9). Item [2.8](../itens/2.8.md). |
| **DPI** | Pontos por polegada. A análise roda a 150, a prévia a 110-150, o PDF a 300. PDF que "diz" 72 DPI engana o ScanTailor (Registro 13/10/2026). |
| **erros.log** | Onde o programa grava o erro técnico; na tela aparece só "Aconteceu um problema inesperado, mas o programa continua funcionando." |
| **atalho "(desenvolvimento)"** | O atalho que abre o programa da pasta principal (ramo `fase-1`); é por ele que o Samuel confere. O atalho antigo (item [0.2](../itens/0.2.md)) abre código velho. |

## O plano e as decisões

| Termo | O que é |
|---|---|
| **plano / PLANO-DEFINITIVO** | `docs/plano/PLANO-DEFINITIVO.md`. **Ele manda.** Só o Samuel muda. Tem as fases, a Lista de bugs (§5), a Lista de espera (§6) e o Registro de mudanças (§7). Cópia no HD dele: `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\` (as duas nunca ficam diferentes). |
| **`[x]` `[~]` `[-]` `[ ]`** | Aprovado · melhorar · descartado · a fazer. Só o Samuel marca. |
| **PRONTO PARA CONFERIR** | O máximo que um agente pode escrever. Nunca "APROVADO" (CLAUDE.md §4.3). |
| **teste de máquina / teste de olho** | Máquina: pergunta objetiva, o Claude decide. Olho: "o papel saiu branco?", só o Samuel decide (CLAUDE.md §4). |
| **teste de reversão** | Teste que falha no código antigo e passa no novo; obrigatório em todo conserto de bug desde 19/10/2026 (CLAUDE.md §4.7). Ver [bugs.md](../bugs.md). |
| **regra 6** | "Nenhum item pode deixar o programa mais lento." Exceções só pelo Samuel; lentidão pequena no meio da fase vai para a Fase 5 (19/10/2026). |
| **filtro de velocidade** | Antes e depois na mesma máquina do GitHub, alternados, em toda mudança de `core/` (decisão "opção 2", 19/10/2026). |
| **suíte** | Todos os testes (`pytest tests`): ~2.050 conferências em 14/10/2026. No PC, um arquivo por vez; a suíte inteira roda no GitHub. |
| **`teste_botoes.py`** | Script que clica nos botões de verdade da janela (sem tela). |
| **régua** | `avaliar.py` (filtros) e `avaliar_selecao.py` (seleção). "Número que não pega o pior defeito não pode dar veredito" (CLAUDE.md §4.2). |
| **gabarito / páginas-gabarito** | As páginas fixas de conferência (`gabarito/lista.json`; imagens fora do git, cópia no ramo `dados-de-teste`). Ver [paginas-de-teste/](../paginas-de-teste/). |
| **R1 a R9** | Os nove resultados que o Samuel quer (ESTADO-ATUAL §2). Ver [resultados-R1-a-R9.md](../resultados-R1-a-R9.md). |
| **"Vamos recapitular..."** | O documento do Samuel de 12/09/2026 com os prints das páginas e os resultados R1-R9. |
| **conferência N** | Os formulários de conferência de 28/09 a 06/10/2026 (conferência 1 a 15). "Conferência 6.7" é o nome de uma conferência de 28/09, não o item 6.7. Ver [conferencias.md](../conferencias.md). |
| **página de escolhas / de layout / "Quando revisar" / de andamento / de conferência** | As páginas do claude.ai onde o Samuel responde e a resposta fica salva. Ver [paginas-claude-ai.md](paginas-claude-ai.md). |
| **banco** | O banco de dados de cada página do claude.ai, onde ficam as respostas dele (coleção `respostas`). |
| **comentário fixado / `historico`** | O comentário dele que sobe para o alto da pergunta quando ela volta (regra de 07/10/2026). |
| **rodada N** | Uma leva de perguntas. "Rodada 12 do layout", "rodada 5 do Para revisar". |
| **r12, r13** | Rodadas 12 e 13 do layout; ids `r12-*` / `r13-*`, perguntas 701-710 e 801-808. |
| **ids das perguntas** | `g6-retangulo`, `g7-borda-ate-onde`, `pontinhos-de-fabrica`, `apagar-quando` (página de escolhas); `rv4-*`, `rv5-*` (rodadas 4 e 5 do "Para revisar"); `layout3`, `cg6`, `pr-*` (página de conferência). |
| **G1 a G10** | As perguntas de geometria das conferências 9 e 14 (05/10/2026): G1 girar, G2 dividir, G3 corte da sobra, G4 endireitar do ScanTailor, G5 tela do endireitar, **G6 endireitar antes de cortar**, G7 página dentro da borda preta, G8 seguir a moldura, G9 margens (G9b todas do tamanho da maior), G10 avisar e não reduzir. |
| **G6** | Endireitar antes de cortar, como o ScanTailor. Aprovado e juntado em 12/10/2026 (item [2.2](../itens/2.2.md)). |
| **cg6** | A decisão "conserto do corte do G6" na página de conferência (faixa preta em página torta com borda preta). Marcada "Melhorar" em 13/10/2026; reaberta até o conserto do Pesel 21. |
| **layout3** | A decisão da etapa 3 do layout na página de conferência ("Aprovado", 13/10/2026). |
| **etapa 1 a 7 do layout** | A obra do layout no programa: 1 temas; 2 tela sem abas; 3 coluna da direita e painel Propriedades; 4 Marcar no Propriedades e painel Filtro; 5 miniaturas; 6 tela cheia dos filtros; 7 tela inicial. Ver [layout.md](../itens/layout.md). |
| **D1-D3, M1-M3, O1-O4** | Perguntas do formulário de decisões de 01-02/10/2026 (M1-M3 = aprovação de 1.1, 1.2 e 1.3). |
| **A1, X2, P1-P11, V1, S1-S2, Z1-Z2, C1...** | Cartões das conferências de 30/09 a 06/10/2026; o significado de cada um está em [conferencias.md](../conferencias.md). |
| **Lista de bugs / Lista de espera** | Plano §5 (bugs que não impedem a tarefa; resolvidos no começo de cada fase) e §6 (ideias novas, com data; o Samuel decide a fase). |
| **Fase 2 adiantada** | Em 01/10/2026 a Fase 2 começou antes de a Fase 1 terminar (1.4, 1.5, 1.6 ficaram para depois). |
| **"igual ao ScanTailor, sem perguntar"** | Regra da Fase 2 de 13/10/2026: cada ferramenta vem igual à do ScanTailor, desligada de fábrica quando muda a imagem; o Samuel só confere no fim. |

## Git e o jeito de trabalhar

| Termo | O que é |
|---|---|
| **ramo** | Uma linha de trabalho no git (branch). Cada agente trabalha no seu. Ver [ramos.md](../ramos.md). |
| **`fase-1`** | O ramo principal de trabalho: é o programa que o atalho "(desenvolvimento)" abre. Só a gerente junta coisas nele. |
| **`master`** | Só recebe o que o Samuel aprovou (Registro 28/09/2026). |
| **worktree** | Uma cópia do projeto numa pasta própria (`.claude\worktrees\<nome>`), presa a um ramo, para os agentes não se atrapalharem. |
| **junção** | Atalho de pasta do Windows dentro de uma worktree (`modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`) que aponta para a pasta de verdade. **Nunca** `Remove-Item -Recurse` nela: apaga o original. Desfazer só com `(Get-Item <junção>).Delete()`. |
| **juntar** | Levar o trabalho de um ramo para o `fase-1` (merge). |
| **commit / push** | Guardar uma etapa no git / mandar para o GitHub. Cada agente faz push no próprio ramo a cada passo. |
| **checkpoint / PARTE -N** | O resumo de cada sessão no histórico (`historico/...resumo para o Claude.md`); a PARTE com o número mais negativo é a mais nova. |
| **ONDE-PAREI.md** | O arquivo que cada trabalho longo mantém para retomar se a sessão cair (limite de uso da conta). |
| **recados** | Bilhetes de outras janelas do Claude Code para a gerente (CLAUDE.md §4.8). Pasta [recados/](../recados/LEIAME.md). |
| **Windows do GitHub / rodada** | Os testes rodando num Windows da nuvem (workflow "Testes no Windows"); cada execução tem um número de rodada. |
| **sessão na nuvem** | 09 a 12/10/2026: trabalho numa cópia no Linux da nuvem, sem Windows, sem DLLs e sem o D:. |
| **UTC-4** | O relógio do PC do Samuel (America/Cuiaba). O GitHub e as páginas do claude.ai mostram UTC. |
| **MemPalace** | Programa de memória para o Claude Code que o Samuel quer testar depois desta memória ficar pronta (Lista de espera, 19/10/2026). |

## Programas de fora

| Termo | O que é |
|---|---|
| **ScanTailor Advanced** | Programa livre de tratar páginas escaneadas; a Fase 2 traz as ferramentas dele com o código original. [referencias/scantailor.md](../referencias/scantailor.md). |
| **CamScanner** | O aplicativo que o Kaique usa hoje (filtro Mágico Pro); é o gabarito de comparação (fotos de 24/09/2026). |
| **UPDF** | O leitor de PDF do Samuel; a janela de imprimir dele é a referência da fase de impressão (14/10/2026). [referencias/updf.md](../referencias/updf.md). |
| **embaralhador antigo** | O primeiro programa de imposição de cadernos. [referencias/embaralhador.md](../referencias/embaralhador.md). |
| **Internet Archive** | Biblioteca on-line de onde vêm os PDFs com camadas. [referencias/internet-archive.md](../referencias/internet-archive.md). |
| **ExtratorPDF** | **Outro programa**, em `D:\programas\Scan Tailor`. Não misturar (ESTADO-ATUAL §5). |
