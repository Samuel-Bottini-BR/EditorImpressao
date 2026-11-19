"""O catálogo de todas as regras do CLAUDE.md e dos 4 arquivos de agente (D-784; veio do esboço da proposta das regras).

Não muda o texto de nenhuma regra: cada linha só dá um nome curto, diz de onde vem, põe as etiquetas e diz se a máquina
pode cobrar. **O texto que vale continua sendo o do CLAUDE.md e dos agentes**; o pacote (`montar_pacote.py`) cita a fonte
de cada regra entre parênteses.

Campos de cada regra:
  id      R001...
  nome    nome curto
  onde    onde está escrita (todas as cópias; a primeira é a "principal")
  tags    etiquetas (ver ETIQUETAS)
  papel   para quem vale: todos | codigo (implementador e layout) | verif | pesq | layout | gerente
  maq     a máquina pode cobrar? sim | em parte | nao
  curta   o texto curto que vai no pacote, com o porquê
  rep     se repete: em que lugares e se dizem coisas um pouco diferentes
  contra  código da contradição (ver CONTRADICOES), se houver

Contradições já resolvidas pelo Samuel (`RESOLVIDAS`, 18 e 19/11/2026): o pacote passa a dizer qual texto vale, com a
decisão, em vez de "pergunte à gerente". O texto do CLAUDE.md e dos agentes ainda não foi corrigido (é da gerente, com
o "sim" dele); até lá, o aviso do pacote é o que mostra qual vale.

Seguro mexer: acrescentar regra, corrigir etiqueta, acrescentar contradição resolvida (com a decisão que existe no
Livro: um teste confere). Arriscado: mudar `curta` sem conferir o texto que vale; tirar uma regra (o agente deixa de
recebê-la).
"""

ETIQUETAS = {
    "TODO": "todo trabalho",
    "TELA": "tela (ui/)",
    "WIN": "Windows e instalador (e qualquer conversa com programa de fora)",
    "IMG": "imagem, filtros e processamento do livro",
    "PERG": "perguntas e relatórios ao Samuel",
    "TESTE": "testes",
    "GIT": "git e arquivos",
    "PESQ": "pesquisa de peça de fora",
    "GER": "só a gerente (não vai no pacote de agente)",
}

A, I, V, P, L = "CLAUDE.md", "implementador.md", "verificador.md", "pesquisador.md", "layout.md"
TODOS4 = [I, V, P, L]

REGRAS = [
    # ---------------- topo e §1 ----------------
    dict(id="R001", nome="Ordem de leitura e quem manda", onde=[f"{A} topo", f"{I} 'Leia antes'", f"{V} 'Leia antes'", f"{P} 'Leia antes'", f"{L} 'Leia antes'"],
         tags=["TODO"], papel="todos", maq="nao",
         curta="Quem manda: o Livro de decisões e o plano; o CLAUDE.md vem depois. O que ele disser contra o plano, vale o plano.",
         rep="5 lugares; o CLAUDE.md põe o Livro como item 0, os agentes começam pelo ESTADO-ATUAL e só mais abaixo dizem 'Livro antes de tudo'",
         contra="X10"),
    dict(id="R002", nome="PEDIDOS.md e handoff são histórico", onde=[f"{A} topo", f"{A} §7"], tags=["TODO"], papel="todos", maq="nao",
         curta="PEDIDOS.md e o handoff em historico/ só servem de consulta; não dizem o que fazer.", rep="2 lugares no CLAUDE.md, iguais"),
    dict(id="R003", nome="Tela em português sem jargão", onde=[f"{A} §1", f"{L} 'Regras de tela'"], tags=["TELA", "PERG"], papel="todos", maq="em parte",
         curta="O Kaique vê 'Força do preto', nunca 'Sauvola' ou 'k'. Toda a tela em português do Brasil, sem jargão.", rep="2 lugares, iguais"),
    dict(id="R004", nome="Critério final do livro", onde=[f"{A} §1"], tags=["IMG"], papel="todos", maq="nao",
         curta="'Eu quero que o papel saia branco, e o desenho também saia perfeito.'"),
    # ---------------- §2 ----------------
    dict(id="R005", nome="Não recomeçar do zero", onde=[f"{A} §2"], tags=["TODO"], papel="codigo", maq="em parte",
         curta="Não reescrever módulo inteiro nem reorganizar o que funciona. Testar não é licença para reconstruir. (Duas versões já fracassaram.)"),
    dict(id="R006", nome="Uma mudança por vez", onde=[f"{A} §2", f"{A} §8 passo 3", f"{I} 'O que você faz'"], tags=["TODO"], papel="codigo", maq="nao",
         curta="Uma mudança só, a pedida. Nada da fase seguinte.", rep="3 lugares; a Obra (D-014) suspende o 'conferir cada item antes do próximo'", contra="X9"),
    dict(id="R007", nome="Planejar antes; perguntar antes de mexer em estrutura", onde=[f"{A} §2"], tags=["TODO"], papel="codigo", maq="nao",
         curta="Planejar antes de escrever. Mexer em estrutura, em tela ou no que o §6 diz, só perguntando antes."),
    dict(id="R008", nome="Ir até o fim dentro da alçada", onde=[f"{A} §2"], tags=["TODO"], papel="todos", maq="nao",
         curta="Decidir o que é da alçada e executar tudo, sem parar a cada passo. Se o contexto acabar, parar num commit com o programa rodando."),
    dict(id="R009", nome="Primeiro a frase, depois o número", onde=[f"{A} §2", f"{I} 'Como entregar'", f"{V} 'Como entregar'", f"{P} 'Como entregar'", f"{L} 'Como entregar'", f"{A} §11.13.7"],
         tags=["PERG"], papel="todos", maq="nao", curta="Primeiro a frase que se entende ('estava estragando a capa'), o número depois, nunca no lugar.",
         rep="6 lugares, iguais no sentido"),
    dict(id="R010", nome="Conciso: essencial no chat, detalhe em arquivo", onde=[f"{A} §2"], tags=["PERG"], papel="todos", maq="nao",
         curta="O essencial no chat; o detalhe em arquivo."),
    dict(id="R011", nome="Claro e direto com o Samuel", onde=[f"{A} §2", f"{A} §11.13.7"], tags=["PERG"], papel="todos", maq="em parte",
         curta="Poucas linhas, uma ideia por frase, os nomes da tela, no máximo uma pergunta sim/não com a sugestão; nada de tabela, número de decisão ou nome de arquivo.",
         rep="2 lugares, parecidos", contra="X11"),
    dict(id="R012", nome="Honesto: avisar erro e risco", onde=[f"{A} §2"], tags=["TODO"], papel="todos", maq="nao",
         curta="Se o Samuel ou a gerente estiver enganado ou correndo risco, avisar. Não concordar para agradar."),
    dict(id="R013", nome="Não inventar detalhe", onde=[f"{A} §2"], tags=["TODO"], papel="todos", maq="em parte",
         curta="Não inventar detalhe que ninguém forneceu (inclui as palavras do Samuel: copiar do Livro, nunca de memória)."),
    dict(id="R014", nome="Relatório em três formatos", onde=[f"{A} §2", f"{A} §8 passo 7", f"{V} passo 7"], tags=["TODO", "PERG"], papel="todos", maq="sim",
         curta="Todo relatório sai com relatorio.gravar (.md, .html, .pdf). O Samuel não abre .md.", rep="3 lugares, iguais"),
    # ---------------- §3 ----------------
    dict(id="R015", nome="PySide6, nunca tkinter", onde=[f"{A} §3", f"{L} 'Regras de tela'"], tags=["TELA"], papel="codigo", maq="sim",
         curta="PySide6, nunca tkinter nem customtkinter (uma versão anterior travava).", rep="2 lugares, iguais"),
    dict(id="R016", nome="Uma página por vez na memória", onde=[f"{A} §3"], tags=["IMG"], papel="codigo", maq="em parte",
         curta="O pico de memória não cresce com o livro (há livro de 300 MB). Nunca uma lista com todas as páginas processadas."),
    dict(id="R017", nome="A janela nunca congela", onde=[f"{A} §3", f"{L} 'Regras de tela'"], tags=["TELA", "WIN"], papel="codigo", maq="em parte",
         curta="Todo trabalho demorado em QThread, com barra e cancelar que funciona; esperar o Windows também (na etapa 5 a janela ficou parada 14 min).",
         rep="2 lugares, iguais"),
    dict(id="R018", nome="Nenhuma exceção fecha a janela", onde=[f"{A} §3"], tags=["TELA"], papel="codigo", maq="em parte",
         curta="Erro vira aviso em português numa caixa; o técnico vai para o log."),
    dict(id="R019", nome="Nenhum emoji em rótulo", onde=[f"{A} §3", f"{L} 'Regras de tela'"], tags=["TELA"], papel="codigo", maq="sim",
         curta="Nenhum emoji em rótulo de tela (quebrou no Windows).", rep="2 lugares, iguais"),
    dict(id="R020", nome="Texto com acento, caminho sem acento", onde=[f"{A} §3"], tags=["TELA", "GIT", "WIN"], papel="codigo", maq="sim",
         curta="Texto de tela com acento (UTF-8); caminho de disco sem acento."),
    dict(id="R021", nome="Algoritmo consagrado", onde=[f"{A} §3"], tags=["IMG"], papel="codigo", maq="nao",
         curta="Algoritmo consagrado em vez de fórmula própria (a fórmula caseira deu qualidade ruim)."),
    dict(id="R022", nome="Nenhum modelo generativo", onde=[f"{A} §3", f"{I} 'nunca'", f"{P} 'nunca'"], tags=["IMG", "PESQ"], papel="todos", maq="em parte",
         curta="Nada que desenhe pixel ou invente texto: inventaria detalhe numa gravura de 1579. Rede neural só aponta onde está a coisa.",
         rep="3 lugares; o pesquisador acrescenta 'OCR generativo proibido'"),
    dict(id="R023", nome="Python 3.14, não rebaixar", onde=[f"{A} §3", f"{I} 'nunca'"], tags=["TODO"], papel="todos", maq="sim",
         curta="A máquina só tem Python 3.14. Nunca sugerir rebaixar.", rep="2 lugares, iguais"),
    dict(id="R024", nome="GPU sem float16 rápido", onde=[f"{A} §3", f"{P} 'roda aqui?'"], tags=["IMG", "PESQ"], papel="todos", maq="em parte",
         curta="GTX 1650 4 GB, sem tensor cores: nada que dependa de float16 rápido. O notebook do Kaique não tem placa de vídeo.",
         rep="2 lugares; o pesquisador acrescenta o notebook do Kaique"),
    dict(id="R025", nome="Erro nunca como stack trace", onde=[f"{A} §3"], tags=["TELA"], papel="codigo", maq="em parte",
         curta="sys.excepthook grava em erros.log e mostra 'Aconteceu um problema inesperado, mas o programa continua funcionando.'"),
    dict(id="R026", nome="Licença: GPL pode entrar", onde=[f"{A} §3", f"{P} 'O que você faz'"], tags=["PESQ"], papel="todos", maq="nao",
         curta="Código GPL pode ser incorporado (17/09); a licença de cada peça tem de estar escrita.", rep="2 lugares; o pesquisador cobra escrever sempre"),
    # ---------------- §4 ----------------
    dict(id="R027", nome="Teste de máquina: o agente decide", onde=[f"{A} §4.1"], tags=["TESTE"], papel="todos", maq="sim",
         curta="O que tem resposta objetiva (fecha? páginas certas? memória? PDF estragado? cadernos? acento?) roda a cada mudança, sozinho."),
    dict(id="R028", nome="Teste de olho: prepara, abre tudo, para e chama", onde=[f"{A} §4.2", f"{V} passos 3 e 4"], tags=["TESTE", "IMG"], papel="verif", maq="nao",
         curta="Antes/depois, abrir TODAS as imagens (nunca amostra: '10 de 10' com seis erradas), opinião com ressalvas, parar e chamar.",
         rep="2 lugares; dizem coisas diferentes sobre quais páginas", contra="X3"),
    dict(id="R029", nome="Número que não pega o pior defeito não dá veredito", onde=[f"{A} §4.2"], tags=["TESTE", "IMG"], papel="todos", maq="nao",
         curta="A régua já deu número bom com a mancha piorando: número sozinho não aprova."),
    dict(id="R030", nome="Ressalva escrita, nunca escondida", onde=[f"{A} §4.2", f"{I} 'Como entregar'", f"{V} 'nunca'"], tags=["TODO"], papel="todos", maq="em parte",
         curta="Ressalva escrita não é demérito; ressalva escondida é.", rep="3 lugares, iguais"),
    dict(id="R031", nome="Nunca 'APROVADO'", onde=[f"{A} §4.3", f"{A} §8", f"{I} 'nunca'", f"{V} 'regra de ouro'", f"{V} 'nunca'"], tags=["TODO"], papel="todos", maq="sim",
         curta="No máximo 'PRONTO PARA CONFERIR' e a opinião. Só o Samuel marca [x], [~] ou [-] (57 commits 'feito', zero aprovados).",
         rep="5 lugares; dizem coisas diferentes sobre quem pode escrever 'PRONTO PARA CONFERIR'", contra="X4"),
    dict(id="R032", nome="Máquina ou olho, item por item", onde=[f"{A} §4.3", f"{V} 'regra de ouro'", f"{V} 'Como entregar'"], tags=["TESTE"], papel="todos", maq="sim",
         curta="Todo item diz se foi conferido por máquina ou por olho.", rep="3 lugares, iguais"),
    dict(id="R033", nome="Auditoria por amostragem", onde=[f"{A} §4.4"], tags=["GER"], papel="gerente", maq="nao",
         curta="O Samuel confere às vezes um item 'de máquina'; erro achado encolhe a categoria."),
    dict(id="R034", nome="Onde roda cada teste", onde=[f"{A} §4.6", f"{I} 19/10", f"{V} 19/10", f"{P} 19/10", f"{L} 19/10"], tags=["TESTE"], papel="todos", maq="sim",
         curta="No PC, um arquivo de teste por vez; a suíte inteira e o teste_botoes no GitHub (push antes); a entrega traz o número da rodada.",
         rep="5 lugares; nos agentes contradiz o texto mais antigo do próprio arquivo", contra="X2"),
    dict(id="R035", nome="Só documentos: entra com o GitHub", onde=[f"{A} §4.6"], tags=["GER"], papel="gerente", maq="sim",
         curta="Trabalho que só acrescenta documentos entra no fase-1 só com a rodada do GitHub."),
    dict(id="R036", nome="Filtro de velocidade no GitHub", onde=[f"{A} §4.6", f"{I} 19/10", f"{V} 19/10", f"{P} 19/10", f"{L} 19/10"], tags=["TESTE", "IMG"], papel="codigo", maq="sim",
         curta="Mudança em processamento passa pelo filtro de velocidade do GitHub (antes e depois na mesma máquina). Não rodar o teste_velocidade completo no PC.",
         rep="5 lugares", contra="X1"),
    dict(id="R037", nome="Lentidão pequena vai para a Fase 5", onde=[f"{A} §4.6"], tags=["GER"], papel="gerente", maq="nao",
         curta="Lentidão pequena achada no meio da fase vai para a fase de desempenho.", contra="X1"),
    dict(id="R038", nome="Teste de reversão em todo conserto", onde=[f"{A} §4.7", f"{I} 19/10", f"{V} 19/10", f"{L} 19/10"], tags=["TESTE"], papel="todos", maq="em parte",
         curta="Todo bug consertado ganha teste que FALHA no código antigo e passa no novo, com o bug na docstring; o verificador prova no antigo. Bug de imagem: uma medida, ou ressalva escrita.",
         rep="4 lugares, iguais (o pesquisador não tem)"),
    dict(id="R039", nome="Agente entrega sempre à gerente", onde=[f"{A} §4.8", f"{I} 19/10", f"{V} 19/10", f"{P} 19/10", f"{L} 19/10"], tags=["TODO"], papel="todos", maq="em parte",
         curta="Entregue sempre à gerente; nunca passe trabalho direto a outro agente.", rep="5 lugares, iguais"),
    dict(id="R040", nome="Recados de outras janelas", onde=[f"{A} §4.8"], tags=["GER"], papel="gerente", maq="nao",
         curta="Palavras literais; a gerente repete ao Samuel e só muda o plano com o 'sim'; anotar na memória."),
    dict(id="R041", nome="Ler a memória antes", onde=[f"{A} §4.9", f"{I} 19/10", f"{V} 19/10", f"{P} 19/10", f"{L} 19/10"], tags=["TODO"], papel="todos", maq="nao",
         curta="Antes de começar, ler memoria/INDICE.md e as fichas do assunto. A memória nunca contradiz o plano.",
         rep="5 lugares; nos agentes ainda diz 'se a pasta já existir (está sendo montada a partir de 19/10)'"),
    dict(id="R042", nome="Teste de imagem pelo caminho inteiro", onde=[f"{A} §4.10", f"{I} 21/10", f"{V} 21/10", f"{L} 21/10", f"{A} §11.13.4"], tags=["IMG", "TESTE"], papel="todos", maq="em parte",
         curta="Teste de imagem e conferência levam a página por dividir → endireitar → cortar → filtro, com ajustes de fábrica, até a ferramenta testada.",
         rep="5 lugares, iguais"),
    dict(id="R043", nome="Cada foto diz o caminho e as opções", onde=[f"{A} §4.10", f"{I} 21/10", f"{V} 21/10", f"{L} 21/10", f"{A} §11.13.5"], tags=["IMG", "PERG"], papel="todos", maq="em parte",
         curta="Toda foto diz por onde a página passou ('endireitada, cortada, Preto e branco + Só as letras').", rep="5 lugares, iguais"),
    dict(id="R044", nome="Só páginas que vão ser impressas", onde=[f"{A} §4.10", f"{I} 21/10", f"{V} 21/10", f"{L} 21/10", f"{A} §11.13.4"], tags=["IMG", "TESTE", "PERG"], papel="todos", maq="em parte",
         curta="Nunca lombada, capa ou contracapa de couro ou papelão nos testes.", rep="5 lugares, iguais"),
    # ---------------- §5 e §6 ----------------
    dict(id="R045", nome="Protocolo de mudança de imagem", onde=[f"{A} §5"], tags=["IMG"], papel="codigo", maq="em parte",
         curta="Medir antes, uma mudança, medir de novo; piorou, reverter. Se valer mesmo assim, não reverter sozinho: apresentar os dois."),
    dict(id="R046", nome="Tudo o que foi tentado vai para melhorias.md", onde=[f"{A} §5", f"{P} 'Leia antes'"], tags=["IMG", "PESQ"], papel="todos", maq="em parte",
         curta="O que foi tentado, inclusive o que falhou, vai para relatorios/melhorias.md (para ninguém repetir caminho fechado).", rep="2 lugares"),
    dict(id="R047", nome="O que o agente decide sozinho", onde=[f"{A} §6"], tags=["IMG"], papel="codigo", maq="nao",
         curta="Pode decidir: limiar, janela, k, bloco, ordem interna do filtro, binarizador, cache, paralelismo, memória."),
    dict(id="R048", nome="O que precisa perguntar antes", onde=[f"{A} §6", f"{I} 'nunca'"], tags=["TODO"], papel="todos", maq="em parte",
         curta="Perguntar antes: filtro novo ou removido, nome de filtro, qualquer tela, controle novo ou tirado, formato dos dados, desfazer, trocar biblioteca.",
         rep="2 lugares; o implementador só repete 'trocar biblioteca'"),
    # ---------------- §7 ----------------
    dict(id="R049", nome="core/ não importa ui/", onde=[f"{A} §7", f"{I} 'nunca'"], tags=["IMG", "WIN"], papel="codigo", maq="sim",
         curta="core/ nunca importa ui/: o processamento roda por linha de comando, sem janela.", rep="2 lugares, iguais"),
    dict(id="R050", nome="Modelo de dados em dois níveis", onde=[f"{A} §7"], tags=["IMG", "TELA"], papel="codigo", maq="em parte",
         curta="ConfigFolha (o que veio) e ConfigPagina (o que sai); ajustes de cada filtro separados; recorte e ângulo na página."),
    dict(id="R051", nome="Onde o programa guarda estado", onde=[f"{A} §7"], tags=["WIN"], papel="codigo", maq="em parte",
         curta="%LOCALAPPDATA%\\EditorImpressao guarda projetos e histórico; fechar e reabrir preserva tudo; desinstalar NÃO apaga essa pasta."),
    dict(id="R052", nome="Desempenho já resolvido, não refazer", onde=[f"{A} §7"], tags=["IMG"], papel="codigo", maq="nao",
         curta="Análise a 150 DPI e fundo estimado em miniatura de ~400 px: não refazer."),
    dict(id="R053", nome="Ordem obrigatória do processamento", onde=[f"{A} §7"], tags=["IMG"], papel="codigo", maq="em parte",
         curta="Livro novo: dividir → endireitar → cortar → filtro → cadernos. Projeto de antes de 09/10 sem ordem_do_preparo: a ordem antiga, idêntica."),
    dict(id="R054", nome="Acervo e originais só para ler", onde=[f"{A} §7", f"{I} 'nunca'", f"{V} 'nunca'"], tags=["TODO", "GIT"], papel="todos", maq="em parte",
         curta="Nunca alterar, mover ou apagar o acervo e os originais do Samuel (EditorImpressao-arquivos, Scan Tailor, Área de Trabalho). Copiar pode.",
         rep="3 lugares; o implementador lista mais pastas"),
    dict(id="R055", nome="Queixas do Kaique são requisito", onde=[f"{A} §7"], tags=["IMG", "TELA"], papel="todos", maq="nao",
         curta="Os .txt com print em 'Teste de livros' são fonte de requisito."),
    dict(id="R056", nome="Handoff só com pedido do Samuel", onde=[f"{A} §7"], tags=["GIT"], papel="todos", maq="sim",
         curta="Só atualizar o handoff de historico/ quando o Samuel pedir."),
    # ---------------- §8 ----------------
    dict(id="R057", nome="Item da fase atual, na ordem", onde=[f"{A} §8 passo 1", f"{A} §10.2", f"{I} 'O que você faz'"], tags=["GER", "TODO"], papel="todos", maq="nao",
         curta="O item vem da fase atual do plano; Lista de bugs no começo da fase.", rep="3 lugares", contra="X9"),
    dict(id="R058", nome="Testes quebrados: conserta antes de seguir", onde=[f"{A} §8 passo 4", f"{I} 'O que você faz'"], tags=["TESTE"], papel="codigo", maq="sim",
         curta="Se algum teste quebrar, consertar antes de seguir (sem mudar teste antigo, R102).", rep="2 lugares"),
    dict(id="R059", nome="Régua e velocidade; nada mais lento", onde=[f"{A} §8 passo 5", f"{I} 'O que você faz'", f"{V} passo 2"], tags=["TESTE", "IMG"], papel="codigo", maq="em parte",
         curta="Rodar a régua e o teste de velocidade; piorou, reverter ou apresentar os dois. Nenhum item deixa o programa mais lento.",
         rep="3 lugares", contra="X1"),
    dict(id="R060", nome="Antes/depois só nas páginas-gabarito do item", onde=[f"{A} §8 passo 6", f"{V} passo 3"], tags=["TESTE", "IMG"], papel="verif", maq="em parte",
         curta="O verificador gera o antes/depois só com as páginas-gabarito do item (gabarito/lista.json) e abre todas.", rep="2 lugares", contra="X3"),
    dict(id="R061", nome="Item de tela: janela real com mouse nativo", onde=[f"{A} §8 passo 6", f"{V} passo 5", f"{L} 'Como provar'"], tags=["TELA", "TESTE"], papel="verif", maq="em parte",
         curta="Item de tela se prova pilotando a janela real com mensagens nativas de mouse; clique simulado do Qt sozinho não vale (passou duas vezes com o uso real falhando).",
         rep="3 lugares"),
    dict(id="R062", nome="Commit na hora com o defeito por extenso; nunca segredo", onde=[f"{A} §8 passo 10"], tags=["GIT"], papel="todos", maq="em parte",
         curta="Commit com o defeito resolvido escrito por extenso e push; revisar o que vai no commit; nunca segredo; nunca desfazer o .gitignore sem avisar.",
         contra="X12"),
    # ---------------- §9 (o que já se sabe) ----------------
    dict(id="R063", nome="Mancha do verso: o defeito mais grave", onde=[f"{A} §9"], tags=["IMG"], papel="todos", maq="nao",
         curta="O Preto e branco escurece a mancha do verso; a régua não pega. Caminho recomendado: espelhar o verso e subtrair."),
    dict(id="R064", nome="A régua precisa de critérios novos", onde=[f"{A} §9"], tags=["IMG"], papel="todos", maq="nao",
         curta="Comparar onde havia mancha, olhar a moldura, medir sujeira guardada."),
    dict(id="R065", nome="Amarelado está na tinta", onde=[f"{A} §9"], tags=["IMG"], papel="todos", maq="nao",
         curta="A tinta de 1579 é marrom; cuidado: rubricação desbotada também é marrom."),
    dict(id="R066", nome="Não há binarizador vencedor", onde=[f"{A} §9"], tags=["IMG"], papel="todos", maq="nao",
         curta="Os 18 do DoxaPy se invertem de livro para livro."),
    dict(id="R067", nome="Não desfazer a correção do 'magic color'", onde=[f"{A} §9"], tags=["IMG"], papel="codigo", maq="em parte",
         curta="Dividir pelo fundo relativo ao papel, ganho igual nos três canais, curva de ombro no L: não desfazer (a receita comum estraga capa colorida)."),
    dict(id="R068", nome="Scan de baixa resolução não se recupera", onde=[f"{A} §9"], tags=["IMG"], papel="todos", maq="nao",
         curta="O remédio é reescanear; é o único lugar onde 'até ficar perfeito' não vale."),
    dict(id="R069", nome="Barra de rolagem cinza, de propósito", onde=[f"{A} §9"], tags=["TELA"], papel="codigo", maq="sim",
         curta="A barra de rolagem é cinza #a8a49e de propósito; não reverter sem decisão do Samuel."),
    # ---------------- §10 ----------------
    dict(id="R070", nome="Gerente não escreve código", onde=[f"{A} §10.1"], tags=["GER"], papel="gerente", maq="nao",
         curta="A gerente conversa, divide, chama agentes e junta; não escreve código linha por linha."),
    dict(id="R071", nome="Cada papel no seu lugar", onde=[f"{A} §10.1", f"{I} 'O que você faz'", f"{V} 'nunca'", f"{P} 'nunca'", f"{L} 'Onde você trabalha'"], tags=["TODO", "GIT"], papel="todos", maq="sim",
         curta="Implementador: core/ e scripts, não ui/ (salvo pedido). Layout: só ui/. Verificador e pesquisador: não mexem no código do programa.",
         rep="5 lugares", contra="X7"),
    dict(id="R072", nome="Layout só começa com o plano de layout", onde=[f"{A} §10.1", f"{L} 'Antes de tudo'"], tags=["TELA"], papel="layout", maq="nao",
         curta="O layout só começa com o plano de layout entregue; sem ele, responder 'O plano de layout ainda não foi entregue. Não comecei.'",
         rep="2 lugares", contra="V1"),
    dict(id="R073", nome="Ideia nova vai para a Lista de espera; bug que não impede, para a Lista de bugs", onde=[f"{A} §10.2", f"{I} 'Ideias e bugs'", f"{L} 'Como entregar'"], tags=["TODO"], papel="todos", maq="em parte",
         curta="Ideia nova: não fazer, anotar para a Lista de espera. Bug que impede a tarefa: consertar e dizer. Bug que não impede: anotar com data e print.",
         rep="3 lugares", contra="X9"),
    dict(id="R074", nome="Uma cópia e um ramo por frente", onde=[f"{A} §10.3", f"{L} 'Onde você trabalha'"], tags=["GIT"], papel="todos", maq="sim",
         curta="Cada frente na sua cópia (worktree) e no seu ramo; conferir o git log antes; só a gerente junta.", rep="2 lugares", contra="X5"),
    dict(id="R075", nome="Plano em duas cópias", onde=[f"{A} §10.4"], tags=["GER"], papel="gerente", maq="sim",
         curta="docs/plano/ e a cópia do Samuel nunca ficam diferentes."),
    dict(id="R076", nome="Docstring em tudo o que tocar", onde=[f"{A} §10.5", f"{I} 'O que você faz'", f"{L} 'Regras de tela'"], tags=["TODO"], papel="codigo", maq="sim",
         curta="Todo arquivo e função tocados ganham docstring: o que faz e o que é seguro ou arriscado mudar.", rep="3 lugares, iguais"),
    dict(id="R077", nome="Plano novo não apaga pendência", onde=[f"{A} §10.6"], tags=["TODO"], papel="todos", maq="nao",
         curta="Plano novo diz o que resolve e o que deixa de fora; nunca apaga pendência por omissão."),
    dict(id="R078", nome="Item resolvido guarda o pedido original", onde=[f"{A} §10.7"], tags=["GER"], papel="gerente", maq="em parte",
         curta="Ao marcar feito, guardar a frase literal de quem pediu."),
    dict(id="R079", nome="Prosa de checkpoint não é prova", onde=[f"{A} §10.8", f"{A} §9 (menu Abrir)"], tags=["TODO"], papel="todos", maq="nao",
         curta="Quando o estado importa, conferir o código e o git log, não o texto de checkpoint.", rep="2 lugares"),
    dict(id="R080", nome="Apagar: fora do projeto nada; dentro só o seu; junções", onde=[f"{A} §10.9", f"{I} 'Apagar'", f"{V} 'Apagar'", f"{P} 'Apagar'", f"{L} 'Apagar'"], tags=["GIT"], papel="todos", maq="sim",
         curta="Fora de D:\\programas\\EditorImpressao nada se apaga (pare e relate). Dentro, só o que você criou nesta tarefa. Junção nunca com rm -rf: (Get-Item x).Delete().",
         rep="5 lugares; os agentes acrescentam 'conferir o que há dentro' e as junções"),
    # §10.10 Central
    dict(id="R081", nome="Conferências em página do claude.ai com banco", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="nao",
         curta="Tudo o que o Samuel vê ou responde vai numa página com banco (as quatro páginas e a Central)."),
    dict(id="R082", nome="Aba Respostas: gerente responde no documento", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="sim",
         curta="Campos gerente, gerenteEm, lida."),
    dict(id="R083", nome="Responder de novo guardando a antiga", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="sim",
         curta="reabrir, anteriores (nunca apagar), 'Ainda não entendi' conta como respondida."),
    dict(id="R084", nome="Modelo de print (o do girar)", onde=[f"{A} §10.10", f"{A} §11.13.3"], tags=["PERG"], papel="todos", maq="em parte",
         curta="Imagem-resumo; faixas azul (antes), laranja e verde (as opções); as mesmas páginas em todas; o que olhar circulado em vermelho; imagens separadas com legenda.",
         rep="2 lugares; o §11.13.3 resume com azul e verde só"),
    dict(id="R085", nome="Central: um jeito de ver e celular", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="sim",
         curta="Testar as 9 abas em 360 e 300 px antes de publicar."),
    dict(id="R086", nome="Central: atualizar sempre", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="em parte",
         curta="fonte.json → script → batch a cada mudança de situação e no /checkpoint."),
    dict(id="R087", nome="Central: ler as ordens dele primeiro", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="em parte",
         curta="Coleções ordens, testes, ideias, config; marcar vista/feita."),
    dict(id="R088", nome="Aviso no celular ao pôr cartão", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="nao",
         curta="Cartão novo em Decidir agora → aviso no celular."),
    dict(id="R089", nome="Pergunta de agente vai à Central na hora", onde=[f"{A} §10.10", f"{I} 26/10", f"{V} 26/10", f"{P} 26/10", f"{L} 26/10"], tags=["PERG"], papel="todos", maq="em parte",
         curta="Pergunta para o Samuel vai no ONDE-PAREI na hora em que surge (não só na entrega); a gerente leva à Central.",
         rep="5 lugares; os agentes dizem 'na dúvida, pare e pergunte'", contra="X13"),
    dict(id="R090", nome="Agente não grava na Central", onde=[f"{A} §10.10"], tags=["PERG"], papel="todos", maq="sim",
         curta="Agente nunca grava na Central: entrega a pergunta pronta no ONDE-PAREI, com os prints."),
    dict(id="R091", nome="Aba Conferência", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="em parte",
         curta="Relatórios na coleção conferencias, tirados pelo extrator."),
    dict(id="R092", nome="Abrir a conferência sozinha no navegador", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="nao",
         curta="start \"\" <endereço>, desde que ele tenha feito a anterior.", contra="X13"),
    dict(id="R093", nome="Comentário dele se responde na página", onde=[f"{A} §10.10"], tags=["GER"], papel="gerente", maq="nao",
         curta="Refazer a pergunta respondendo ao comentário; fixar o comentário em historico."),
    # ---------------- §11 ----------------
    dict(id="R094", nome="Livro de decisões único", onde=[f"{A} §11.1"], tags=["GER"], papel="gerente", maq="em parte",
         curta="Toda decisão nova entra na hora, com as palavras exatas dele."),
    dict(id="R095", nome="Nenhuma decisão sem dono", onde=[f"{A} §11.2"], tags=["GER"], papel="gerente", maq="sim",
         curta="Cada linha do Livro tem etapa, agente ou Lista de espera."),
    dict(id="R096", nome="Pedido leva as decisões; ONDE-PAREI diz como cumpriu", onde=[f"{A} §11.3", f"{I} 26/10", f"{V} 26/10", f"{P} 26/10", f"{L} 26/10"], tags=["TODO"], papel="todos", maq="sim",
         curta="No começo do ONDE-PAREI, 'Decisões que esta tarefa precisa cumprir' (número + palavras); na entrega, 'Como cumpri cada uma', com print ou teste.",
         rep="5 lugares, iguais"),
    dict(id="R097", nome="Cada decisão tem prova de comportamento; aparência não é prova", onde=[f"{A} §11.4", f"{A} §11.8", f"{I} 26/10", f"{V} 26/10", f"{P} 26/10", f"{L} 26/10"], tags=["TESTE"], papel="todos", maq="em parte",
         curta="Cada decisão tocada tem prova em tests/test_decisoes*.py passando; se substitui comportamento antigo, prova que o antigo saiu.",
         rep="6 lugares; o §11.4 e os agentes dizem test_decisoes.py, o §11.8 diz test_decisoes*.py"),
    dict(id="R098", nome="Quem confere não construiu, e confere do zero", onde=[f"{A} §11.5", f"{V} 26/10"], tags=["TESTE"], papel="verif", maq="em parte",
         curta="Quem confere nunca é quem construiu; abre o programa do zero; para cada decisão: cumprida / pela metade / não cumprida, com print ao lado das palavras.",
         rep="2 lugares"),
    dict(id="R099", nome="Na dúvida, parar e perguntar", onde=[f"{A} §11.6", f"{I} 26/10", f"{V} 26/10", f"{P} 26/10", f"{L} 26/10"], tags=["TODO"], papel="todos", maq="nao",
         curta="Decisão impossível, contraditória ou pouco clara: parar e perguntar. Nunca fazer diferente em silêncio, nem 'por enquanto'.",
         rep="5 lugares, iguais"),
    dict(id="R100", nome="Gerente procura no Livro antes de perguntar", onde=[f"{A} §11.6", f"{A} §11.13.10"], tags=["GER"], papel="gerente", maq="em parte",
         curta="Antes de oferecer opção ou dizer 'não existe', procurar no Livro, no rascunho do layout e na Central.", rep="2 lugares"),
    dict(id="R101", nome="Só o que ele mandou", onde=[f"{A} §11.7"], tags=["TODO"], papel="todos", maq="em parte",
         curta="Nada de comportamento, botão, aviso ou texto que ele não pediu; achado de agente não vale contra decisão dele."),
    dict(id="R102", nome="O novo não estraga o escolhido e testado (D-605)", onde=[f"{A} §11.8", f"{I} 03/11", f"{V} 03/11", f"{P} 03/11", f"{L} 03/11"], tags=["TODO", "TESTE"], papel="todos", maq="sim",
         curta="Antes, 'O que já está escolhido e testado aqui'. Se a coisa nova mudaria isso, pare e pergunte. Nunca mude teste antigo para ele passar.",
         rep="5 lugares, iguais", contra="X14"),
    dict(id="R103", nome="Verificador confere o que funcionava ao redor", onde=[f"{A} §11.8", f"{I} 03/11", f"{V} 03/11", f"{P} 03/11", f"{L} 03/11"], tags=["TESTE"], papel="verif", maq="nao",
         curta="O verificador confere também o que já funcionava ao redor (clicando, em trabalho de tela).", rep="5 lugares, iguais"),
    dict(id="R104", nome="Como fica para quem usa e no livro (D-637)", onde=[f"{A} §11.9", f"{I} D-637", f"{V} D-637", f"{P} D-637", f"{L} D-637"], tags=["TODO"], papel="todos", maq="sim",
         curta="Antes, o que o Kaique vê e faz, passo a passo, e o que muda no PDF; na entrega, conferir clicando e olhando o PDF.",
         rep="5 lugares, iguais"),
    dict(id="R105", nome="Mudou a ferramenta, muda em todos os lugares (D-667)", onde=[f"{A} §11.10"], tags=["TODO", "TELA"], papel="todos", maq="em parte",
         curta="Mudança vale em todas as opções, telas, tela grande, tira e PDF; a regra da ferramenta num lugar só do código."),
    dict(id="R106", nome="Agente não abre agente", onde=[f"{A} §11.11"], tags=["TODO"], papel="todos", maq="sim",
         curta="Nunca abrir outro agente. Quem decide quantos rodam é a gerente.", contra="X6"),
    dict(id="R107", nome="Sem gambiarra: a causa, a regra, todos os caminhos", onde=[f"{A} §11.12", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["TODO"], papel="todos", maq="em parte",
         curta="Antes de mexer: por que aconteceu, qual função decide, todos os caminhos que chegam nela (grep) e se cada um usa essa função ou tem conta própria.",
         rep="5 lugares; cada agente tem um resumo diferente para o seu papel"),
    dict(id="R108", nome="Como conserta: um lugar só", onde=[f"{A} §11.12"], tags=["TODO"], papel="codigo", maq="em parte",
         curta="A regra num lugar só (de preferência em core/); um dado lido e gravado por uma função; lista escrita uma vez; botões iguais chamam a mesma função; comentário 'como o X' conferido.",
         contra="X7"),
    dict(id="R109", nome="Prova: caminho → função e o mesmo resultado em todos", onde=[f"{A} §11.12", f"{I} 13/11", f"{V} 13/11"], tags=["TESTE"], papel="todos", maq="em parte",
         curta="Na entrega, a lista 'caminho → função' e uma prova em tests/ que cobra o mesmo resultado por todos os caminhos.", rep="3 lugares"),
    dict(id="R110", nome="Quando só der remendo: parar", onde=[f"{A} §11.12"], tags=["TODO"], papel="todos", maq="nao",
         curta="Se a única saída for remendo, parar e perguntar; se juntar caminhos mexer em mais de uma ferramenta ou no testado, plano antes e esperar o 'sim'."),
    dict(id="R111", nome="Gerente pede sobre a ferramenta inteira", onde=[f"{A} §11.12", f"{A} §11.10"], tags=["GER"], papel="gerente", maq="nao",
         curta="Pedido sempre sobre a ferramenta inteira; não aceita desvio nem conta duplicada.", rep="2 lugares"),
    dict(id="R112", nome="Sem gambiarra vale para tudo", onde=[f"{A} §11.12 (18/11)", f"{I} 18/11", f"{V} 18/11", f"{P} 18/11", f"{L} 18/11"], tags=["TODO"], papel="todos", maq="nao",
         curta="Telas, core/, instalador, desinstalar, atualizador, publicar, testes à distância, scripts e testes: onde diz 'ferramenta', leia 'qualquer coisa que o programa faz'.",
         rep="5 lugares; os agentes dizem 'os cinco pontos' e listam seis"),
    dict(id="R113", nome="Uma peça só para conversar com o que está fora", onde=[f"{A} §11.12.1", f"{I} 18/11", f"{V} 18/11", f"{P} 18/11", f"{L} 18/11"], tags=["WIN"], papel="todos", maq="sim",
         curta="Windows, disco, rede, GitHub, Velopack, outro programa: uma peça só para cada conversa; ninguém escreve a sua versão (na etapa 5, cada função pedia licença do seu jeito).",
         rep="5 lugares, iguais"),
    dict(id="R114", nome="Nada dá como feito o que não conferiu", onde=[f"{A} §11.12.2", f"{I} 18/11", f"{V} 18/11", f"{P} 18/11", f"{L} 18/11"], tags=["WIN", "TODO"], papel="todos", maq="em parte",
         curta="Depois de pedir algo, conferir o resultado de verdade; a tela mostra a conferência, nunca a anotação. 'Não' ou falha nunca vira 'deu certo'.",
         rep="5 lugares, iguais"),
    dict(id="R115", nome="Antes de escrever, a lista das falhas", onde=[f"{A} §11.12.3", f"{I} 18/11", f"{V} 18/11", f"{P} 18/11", f"{L} 18/11"], tags=["WIN"], papel="codigo", maq="em parte",
         curta="No ONDE-PAREI, para cada coisa que pode dar errado (sem licença, sem internet, disco cheio, 'Não', arquivo preso, desligar no meio), o que o programa faz; nunca pela metade.",
         rep="5 lugares, iguais"),
    dict(id="R116", nome="Peça de mentira não prova (D-767)", onde=[f"{A} §11.12.4", f"{I} 18/11", f"{V} 18/11", f"{P} 18/11", f"{L} 18/11"], tags=["WIN", "TESTE"], papel="todos", maq="em parte",
         curta="Teste com peça de mentira só prova a lógica em volta. O que mexe no Windows só conta rodando de verdade, à vista, e funcionando. Nada em área escondida.",
         rep="5 lugares, iguais", contra="X8"),
    dict(id="R117", nome="Gerente não aceita 'pronto' sem prova", onde=[f"{A} §11.12.5", f"{I} 18/11", f"{V} 18/11", f"{P} 18/11", f"{L} 18/11"], tags=["GER", "TESTE"], papel="verif", maq="em parte",
         curta="O verificador procura de propósito: peça duplicada, resultado não conferido, falha não pensada.", rep="5 lugares, iguais"),
    dict(id="R118", nome="Ler a peça de fora antes de usar", onde=[f"{A} §11.12.6", f"{I} 18/11", f"{V} 18/11", f"{P} 18/11", f"{L} 18/11"], tags=["WIN", "PESQ", "TODO"], papel="todos", maq="em parte",
         curta="Antes de usar Velopack, função do Windows, PowerShell ou biblioteca: ler a documentação (e o código, se preciso) e anotar o que ela faz em cada caso que usamos, com a fonte.",
         rep="5 lugares, iguais"),
    dict(id="R119", nome="Perguntar: comece pelo que é e onde fica", onde=[f"{A} §11.13.1", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="em parte",
         curta="A primeira frase diz a tela, o botão e o caminho de clique, e para que serve.", rep="5 lugares, iguais"),
    dict(id="R120", nome="Perguntar: nenhuma palavra de dentro", onde=[f"{A} §11.13.2", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="sim",
         curta="Nada de número de decisão, código, nome de etapa, de agente, de arquivo ou de função; o nome que aparece na tela.", rep="5 lugares, iguais"),
    dict(id="R121", nome="Perguntar: print que prova", onde=[f"{A} §11.13.3", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="em parte",
         curta="Toda pergunta e todo 'está feito' com print do caso real no modelo do girar; uma imagem por opção.", rep="5 lugares, iguais"),
    dict(id="R122", nome="Perguntar: o caso que o Kaique encontra, print conferido", onde=[f"{A} §11.13.4", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="nao",
         curta="O livro e a página onde acontece de verdade, pelo caminho inteiro; abrir o print e conferir.", rep="5 lugares, iguais"),
    dict(id="R123", nome="Perguntar: o caminho, e se é defeito ou escolha", onde=[f"{A} §11.13.5", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="em parte",
         curta="Dizer o caminho que a página fez e, com todas as letras, se é defeito ou efeito de escolha (ou 'ainda não se sabe').", rep="5 lugares, iguais"),
    dict(id="R124", nome="Perguntar: o que você escolhe e o que muda", onde=[f"{A} §11.13.6", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="em parte",
         curta="'O que você escolhe: ...'; o que acontece em cada opção; se é novo; o que muda no que já funciona; 'Só comentário' e a sugestão.", rep="5 lugares, iguais"),
    dict(id="R125", nome="Perguntar: curto, sem ficha", onde=[f"{A} §11.13.7", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="em parte",
         curta="Poucas frases; nada de ficha com campos; responder cada pergunta dele na ordem; a resposta se explica sozinha.", rep="5 lugares, iguais"),
    dict(id="R126", nome="Perguntar: ele continua no controle?", onde=[f"{A} §11.13.8", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="nao",
         curta="Dá para ligar e desligar? ajustar? onde aparece? quando age?", rep="5 lugares, iguais"),
    dict(id="R127", nome="Perguntar: de onde veio", onde=[f"{A} §11.13.9", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="em parte",
         curta="Pedido dele (data e palavras), ScanTailor, ou escolha de agente sem pedido (dito com todas as letras); como outros programas fazem.", rep="5 lugares, iguais"),
    dict(id="R128", nome="Perguntar: a situação de agora, sem repetir", onde=[f"{A} §11.13.10", f"{I} 13/11", f"{V} 13/11", f"{P} 13/11", f"{L} 13/11"], tags=["PERG"], papel="todos", maq="em parte",
         curta="Em que pé está; procurar no Livro e na Central antes; se já respondeu, citar data e palavras.", rep="5 lugares, iguais"),
    dict(id="R129", nome="Depois de 'Ainda não entendi': mudar o jeito", onde=[f"{A} §11.13"], tags=["GER"], papel="gerente", maq="nao",
         curta="Responder primeiro, prova que faltou, conferir o que afirma, horário de verdade; dois 'não entendi', perguntar no chat."),
    dict(id="R130", nome="A lista de conferência antes de mandar", onde=[f"{A} §11.13", f"{A} §10.10"], tags=["GER", "PERG"], papel="gerente", maq="em parte",
         curta="A gerente confere as 10 regras e devolve ao agente a pergunta que não passar.", rep="2 lugares"),
    dict(id="R131", nome="Obra D-014: o que não vale durante a obra", onde=[f"{A} fim"], tags=["GER", "TODO"], papel="todos", maq="nao",
         curta="Durante a obra não valem 'conferir cada item antes do próximo' nem 'uma fase por vez'; nada entra no fase-1 antes da conferência final; duas decisões que se contradizem: vale a mais recente.",
         contra="X9"),
    # ---------------- só nos arquivos dos agentes ----------------
    dict(id="R132", nome="Teste escrito antes do código, quando der", onde=[f"{I} 'O que você faz'"], tags=["TESTE"], papel="codigo", maq="nao",
         curta="Teste automático do que é objetivo, escrito antes do código quando der."),
    dict(id="R133", nome="Nunca commit no master", onde=[f"{I} 'nunca'", f"{L} 'Onde você trabalha'"], tags=["GIT"], papel="codigo", maq="sim",
         curta="Nunca commit no ramo principal; quem junta é a gerente.", rep="2 lugares", contra="X5"),
    dict(id="R134", nome="Nunca fechar à força janela que o Samuel usa", onde=[f"{I} 'nunca'", f"{V} 'Como pilotar'", f"{L} 'Como provar'"], tags=["TODO", "TELA"], papel="todos", maq="em parte",
         curta="Nunca fechar à força janela ou processo que não é seu; anotar o PID do que abriu e fechar só esse (WM_CLOSE).", rep="3 lugares"),
    dict(id="R135", nome="Como entregar (lista do papel)", onde=[f"{I} 'Como entregar'", f"{V} 'Como entregar'", f"{P} 'Como entregar'", f"{L} 'Como entregar'"], tags=["TODO"], papel="todos", maq="sim",
         curta="Entrega com: o que foi feito, arquivos, testes, ressalvas, ideias e bugs (cada papel tem a sua lista).",
         rep="4 lugares, cada um com itens diferentes (vira o formulário único)"),
    dict(id="R136", nome="Commit e push a cada passo; ONDE-PAREI", onde=[f"{I} 19/10", f"{V} 19/10", f"{P} 19/10", f"{L} 19/10"], tags=["GIT"], papel="todos", maq="sim",
         curta="Commit e push a cada passo no seu ramo e um ONDE-PAREI.md na pasta do relatório (o limite da conta já derrubou agentes).",
         rep="4 lugares, iguais", contra="X12"),
    dict(id="R137", nome="Verificador: não conserta código", onde=[f"{V} passo 1", f"{V} 'nunca'"], tags=["TESTE"], papel="verif", maq="sim",
         curta="Achou falha: relate. Nunca altere core/ ou ui/.", rep="2 lugares no verificador"),
    dict(id="R138", nome="Verificador: skill conferir-testes-visuais", onde=[f"{V} passo 4"], tags=["TESTE", "IMG"], papel="verif", maq="nao",
         curta="Abrir as imagens uma por uma seguindo a skill .claude/skills/conferir-testes-visuais."),
    dict(id="R139", nome="Defeitos conhecidos da Fase 1 em destaque", onde=[f"{V} passo 6"], tags=["IMG", "PERG"], papel="verif", maq="nao",
         curta="Até a Fase 1 ficar pronta, avisar que moldura dourada e iluminura são defeito conhecido; conferir as regras do resultado da Fase 1.",
         contra="V2"),
    dict(id="R140", nome="Pilotar: instância nova, nunca a dele", onde=[f"{V} 'Como pilotar'"], tags=["TELA", "TESTE"], papel="verif", maq="nao",
         curta="Abrir uma instância nova (pythonw main.py) e fechar a sua com WM_CLOSE."),
    dict(id="R141", nome="Pilotar: mouse por mensagem nativa ao hwnd", onde=[f"{V} 'Como pilotar'"], tags=["TELA", "TESTE"], papel="verif", maq="nao",
         curta="SendMessage/PostMessage direto no hwnd: funciona sem foco e não rouba o mouse dele."),
    dict(id="R142", nome="Pilotar: nunca pywinauto click_input/send_keys", onde=[f"{V} 'Como pilotar'"], tags=["TELA", "TESTE"], papel="verif", maq="sim",
         curta="click_input e send_keys tomam o mouse e o teclado do Samuel."),
    dict(id="R143", nome="Pilotar: roda do mouse não funciona sem foco", onde=[f"{V} 'Como pilotar'"], tags=["TELA", "TESTE"], papel="verif", maq="nao",
         curta="WM_MOUSEWHEEL sem foco não funciona (100 tentativas); se depender de roda, dizer na ressalva."),
    dict(id="R144", nome="Pilotar: print fora da tela", onde=[f"{V} 'Como pilotar'"], tags=["TELA", "TESTE"], papel="verif", maq="nao",
         curta="Janela em -32000 com SW_SHOWNOACTIVATE e PrintWindow com PW_RENDERFULLCONTENT (minimizada sai preta).", contra="X8"),
    dict(id="R145", nome="offscreen não tem fonte", onde=[f"{V} 'Como pilotar'"], tags=["TELA", "TESTE"], papel="verif", maq="nao",
         curta="QT_QPA_PLATFORM=offscreen serve para geometria e imagem, não para conferir texto."),
    dict(id="R146", nome="Verificador: prova de reversão numa cópia à parte", onde=[f"{V} 19/10"], tags=["TESTE"], papel="verif", maq="em parte",
         curta="Rodar o teste novo no código antigo numa cópia à parte e mostrar que falha; teste que passa nos dois é ressalva grave."),
    dict(id="R147", nome="Pesquisador: não repetir caminho fechado", onde=[f"{P} 'Leia antes'"], tags=["PESQ"], papel="pesq", maq="nao",
         curta="Ler antes TESTE-SCANTAILOR-MISTO, OCR-PESQUISA, melhorias.md e docs/pesquisa/."),
    dict(id="R148", nome="Pesquisador: resumir com as próprias palavras", onde=[f"{P} 'O que você faz'"], tags=["PESQ"], papel="pesq", maq="nao",
         curta="Pode citar arquivo, função e trecho curto para localizar; o resumo é seu."),
    dict(id="R149", nome="Pesquisador: roda aqui e no notebook do Kaique?", onde=[f"{P} 'O que você faz'"], tags=["PESQ", "WIN"], papel="pesq", maq="nao",
         curta="Windows, Python 3.14, GTX 1650; notebook i5-1235U, 32 GB, Iris Xe. Se precisar de Linux/WSL, dizer."),
    dict(id="R150", nome="Lido na fonte separado de dedução", onde=[f"{P} 'O que você faz'", f"{P} 'nunca'"], tags=["PESQ", "TODO"], papel="todos", maq="em parte",
         curta="Separar o que foi lido na fonte do que é dedução; nunca apresentar dedução como fato.", rep="2 lugares no pesquisador"),
    dict(id="R151", nome="Pesquisa gravada em docs/pesquisa/ com data e links", onde=[f"{P} 'O que você faz'"], tags=["PESQ"], papel="pesq", maq="sim",
         curta="As conversas não se enxergam: só os documentos ficam."),
    dict(id="R152", nome="Não instalar no .venv sem pedido", onde=[f"{P} 'nunca'"], tags=["PESQ", "TODO"], papel="todos", maq="em parte",
         curta="Nunca instalar nada no .venv do projeto sem a gerente pedir."),
    dict(id="R153", nome="Layout: pista visual em toda área de clicar", onde=[f"{L} 'Regras de tela'"], tags=["TELA"], papel="codigo", maq="nao",
         curta="Toda área de clicar ou arrastar tem cursor, alça ou contorno (um arrasto 'não funcionava' só porque ninguém via onde clicar)."),
    dict(id="R154", nome="Toda função automática tem ligar e desligar", onde=[f"{L} 'Regras de tela'", f"{I} 'O que você faz' (exceção da tela)"], tags=["TELA", "IMG"], papel="todos", maq="em parte",
         curta="Toda função automática tem botão de ligar e desligar (regra 8 do plano).", rep="2 lugares"),
    dict(id="R155", nome="Layout: ler a Lista de espera e as referências", onde=[f"{L} 'Leia antes'"], tags=["TELA"], papel="layout", maq="nao",
         curta="Há ideias de layout do Samuel na Lista de espera, com imagens em docs/plano/referencias-layout/."),
]

# Itens que estão no meio das regras mas são informação (não se cumprem, se consultam).
INFORMACAO = [
    ("§4.5", "Quantos testes existem (241 funções, 279 casos em 07/09)", "desatualizado: §7 diz 666 casos (26/09), §4.6 diz ~2.050, a memória ~2.100"),
    ("§4.5", "teste_botoes.py clica de verdade; teste_interface.py dirige a lógica", "útil para trabalho de tela"),
    ("§4.6", "Comandos do GitHub e do filtro de velocidade", "útil para testes"),
    ("§7", "Mapa de onde ficam as coisas e comandos", "útil para todos"),
    ("§7", "Acervo e queixas do Kaique: onde ficam", "útil para imagem"),
    ("§9", "O bug do menu Abrir já foi corrigido", "história"),
    ("§10.10", "Endereços das páginas do claude.ai", "só a gerente"),
    ("§11", "Por que o Livro existe (sessão 1 dos testes guiados)", "história"),
    ("§11.12", "O que aconteceu em 10/11 e na etapa 5", "o porquê da regra; vai resumido no pacote"),
]

# Contradições (o texto diz coisas que não dá para cumprir juntas) e regras que parecem vencidas.
CONTRADICOES = {
    "X1": "Velocidade. §8 passo 5, o implementador e o verificador (passo 2) mandam rodar o teste_velocidade antes e depois e dizem "
          "'nenhum item pode deixar o programa mais lento'. §4.6 e as regras de 19/10 dos quatro agentes dizem: não rode o completo no PC, "
          "use o filtro do GitHub, e lentidão pequena achada no meio da fase vai para a Fase 5.",
    "X2": "Testes no PC. O implementador ('rode pytest tests -q antes de entregar'), o layout ('pytest tests -q passando') e o verificador "
          "(passo 1) mandam rodar a suíte inteira; o §4.6 e o bloco de 19/10 do mesmo arquivo dizem 'só um arquivo por vez no PC'. "
          "O bloco de 19/10 diz que vale sobre o de cima, mas o de cima continua escrito.",
    "X3": "Páginas do antes/depois. §4.2 passo 1: 'roda a mudança em TODOS os PDFs do conjunto de teste'. §8 passo 6 e o verificador "
          "(passo 3): 'só com as páginas-gabarito daquele item'.",
    "X4": "Quem escreve 'PRONTO PARA CONFERIR'. §4.3: 'o Claude Code pode escrever'. O implementador: 'quem escreve isso é o verificador'.",
    "X5": "Ramo principal. §10.3 ('só a gerente junta no master', 'conferir git log do master'), o implementador e o layout falam do "
          "master; o resto do CLAUDE.md (§4.6, §11.4) fala do fase-1, e a obra (D-014) junta no obra-2026-10-26.",
    "X6": "Quantos agentes. §11.11: 'no máximo dois; em 10/11 deixou três'. A memória (geral/pc-e-github.md §2 e "
          "geral/regras-de-trabalho.md §5): 'no máximo 3 a 4 agentes ao mesmo tempo'. A Central tem config agentes.max.",
    "X7": "Layout e core/. O layout 'só mexe em ui/' e 'não escreve em core/' (§10.1 e layout.md); o §11.12 manda mudar a regra 'num lugar "
          "só, de preferência em core/ (a tela só chama)', e o próprio resumo do layout diz 'de preferência em core/'.",
    "X8": "Janela escondida. O verificador manda tirar print com a janela fora da tela (-32000) e os testes rodam offscreen (memória da "
          "gerente: 'testes offscreen, nunca abrir na tela'); o §11.12.4 (D-767) diz 'só conta rodando de verdade, à vista; nada em área "
          "escondida', e o plano da parte do Windows: 'nenhuma janela empurrada para fora da tela'. O texto não diz que uma vale para "
          "tela e a outra para Windows.",
    "X9": "Ritmo do trabalho. §2, §8 e §10.2 (uma fase por vez, conferir cada item antes do próximo, bug que impede se conserta na hora); "
          "a Obra (D-014, fim do CLAUDE.md) suspende 'conferir cada item' e 'uma fase por vez', e a D-765 suspende todo conserto até a "
          "entrega ao Kaique. Os arquivos dos agentes não citam nem a obra nem a D-765.",
    "X10": "Ordem de leitura. O CLAUDE.md põe o Livro de decisões como item 0; os quatro agentes começam por ESTADO-ATUAL → PLANO → "
           "CLAUDE.md e só no bloco de 26/10 dizem 'leia o Livro antes de tudo'; o INDICE da memória põe o Livro no item 5.",
}
DIFERENCAS_PEQUENAS = {
    "X11": "Tabela: o §2 diz 'nada de tabela' (para o Samuel); o pesquisador entrega 'Tabela: o que é · licença...' (para a gerente).",
    "X12": "Commit: o §8 passo 10 diz 'se aprovado, commit na hora'; os agentes dizem 'commit e push a cada passo no seu ramo'.",
    "X13": "Abrir a página: pergunta de agente abre no navegador dele na hora; conferência só abre se ele já fez a anterior (§10.10).",
    "X14": "Teste antigo: o §11.8 diz 'nunca mude um teste antigo para ele passar'; o plano da parte do Windows e a D-774 dizem 'só com o "
           "sim dele'; a D-644 e a D-663 abriram exceções. Não é contradição, mas o texto da regra não diz como se pede a exceção.",
    "X15": "test_decisoes.py (§11.4 e agentes) e test_decisoes*.py (§11.8).",
    "X16": "Os resumos de 18/11 nos agentes dizem 'os cinco pontos' e listam seis.",
}
VENCIDAS = {
    "V1": "Layout: 'só começa quando o Samuel entregar o plano de layout' e worktree .claude/worktrees/layout no ramo layout. Hoje há a "
          "obra do layout (memoria/itens/layout.md) e as frentes usam outras cópias e ramos.",
    "V2": "Verificador: 'até a Fase 1 ficar pronta, avisar que moldura dourada e iluminura são defeito conhecido' (28/09). Não diz se ainda vale.",
    "V3": "Agentes: 'memória: leia o INDICE se a pasta já existir no fase-1 (está sendo montada a partir de 19/10)'. Ela existe.",
    "V4": "CLAUDE.md §7 'os testes (666 casos em 26/09/2026)' e §4.5 '241 funções'.",
}

# Contradições resolvidas pelo Samuel: código → (decisão do Livro, o que vale, em poucas palavras).
RESOLVIDAS = {
    "X1": ("D-786", "vale a regra de 19/10: velocidade no GitHub a cada mudança; no PC, no fim da fase"),
    "X2": ("D-787", "vale a regra de 19/10: no PC, um arquivo de teste por vez; o conjunto inteiro no GitHub"),
    "X4": ("D-798", "só quem confere (verificador ou quem tenta quebrar) escreve PRONTO PARA CONFERIR, nunca quem construiu"),
    "X5": ("D-797", "dois lugares só: a versão de teste (obra-2026-10-26) e a oficial (fase-1); o master sai das regras"),
    "X7": ("D-796", "o agente de tela mexe em core/ só nos arquivos que o pedido nomear; sem isso, só ui/"),
    "X8": ("D-785", "à vista o que mexe com o Windows (a lista da D-785); escondidos os testes que não dependem dele"),
}


def aviso_de_contradicao(regra: dict) -> str:
    """O aviso que o pacote põe ao lado de uma regra com contradição: qual vale (resolvida) ou "pergunte à gerente"."""
    codigo = regra.get("contra", "")
    if codigo in RESOLVIDAS:
        decisao, vale = RESOLVIDAS[codigo]
        return f" **Outro texto das regras diz diferente; resolvido pelo Samuel ({decisao}): {vale}.**"
    if codigo in CONTRADICOES:
        return " **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**"
    return ""


# As regras que vão em todo pacote (no máximo 10), com o que cada uma cobre do catálogo.
SEMPRE = [
    dict(n=1, titulo="Só o que foi pedido e decidido", cobre=["R101", "R099", "R048", "R006", "R007", "R110"],
         texto="Faça só o que o pedido e as decisões do Samuel mandam. Nada de botão, aviso, texto ou comportamento a mais. "
               "Se a decisão parecer impossível, contraditória ou pouco clara, ou se a única saída for um remendo: pare e escreva a "
               "pergunta (não faça diferente em silêncio, nem 'por enquanto').",
         porque="É a falha que mais se repetiu: decisões de 25/09 nunca construídas, e agentes mudando o que ele tinha definido (§11.7)."),
    dict(n=2, titulo="O novo não estraga o que já funciona", cobre=["R102", "R058"],
         texto="Antes de mexer, anote o que já está escolhido e testado ali. Teste antigo que quebra faz a entrega voltar; nunca mude "
               "um teste antigo para ele passar.",
         porque="Ele disse: 'essa é uma nova regra que todos os agentes precisam ler' (D-605)."),
    dict(n=3, titulo="Sem gambiarra, em tudo", cobre=["R107", "R108", "R112", "R105"],
         texto="Ache a causa, a função que decide, e todos os caminhos que chegam nela (grep). Mude num lugar só e faça todos os caminhos "
               "usarem esse lugar. Nada de desvio para um caso, nem conta ou lista copiada.",
         porque="17 remendos achados em 10/11 e os 33 defeitos do atualizador em 18/11 têm a mesma causa (§11.12)."),
    dict(n=4, titulo="Nada é feito sem conferir de verdade", cobre=["R114", "R030", "R031", "R029"],
         texto="Só diga 'feito' do que você conferiu de verdade (abrindo o arquivo, olhando a imagem, perguntando ao Windows). "
               "Escreva toda ressalva. Nunca escreva 'APROVADO': só o Samuel aprova.",
         porque="57 commits 'feito' e zero aprovados; '10 de 10 corretas' com seis erradas; 'Desligado' gravado sem desligar."),
    dict(n=5, titulo="Leia a peça de fora antes de usar", cobre=["R118", "R150"],
         texto="Antes de usar uma peça que não é nossa (biblioteca, função do Windows, PowerShell, Velopack, Qt), leia a documentação "
               "e, se não bastar, o código. Anote o que ela faz em cada caso que usamos, com a fonte. Separe o lido do deduzido.",
         porque="Na etapa 5 o atualizador foi escrito sem ler o Velopack nem o Windows (§11.12.6)."),
    dict(n=6, titulo="Decisões do Livro: cumprir e provar cada uma", cobre=["R096", "R097", "R013"],
         texto="As decisões que o pedido traz (número e palavras dele) vão no começo do ONDE-PAREI; na entrega, como cumpriu cada uma, "
               "com teste ou print. Aparência não é prova. Palavras dele sempre copiadas do Livro, nunca de memória.",
         porque="As decisões se perdiam entre o pedido e o código (§11.3 e §11.4)."),
    dict(n=7, titulo="Pense em quem usa e no livro que sai", cobre=["R104", "R003"],
         texto="Antes de mexer, escreva o que o Kaique vê e faz, passo a passo, antes e depois, e o que muda no PDF. Na entrega, confira.",
         porque="Regra do Samuel para todo agente (D-637)."),
    dict(n=8, titulo="Pergunta ao Samuel: no ONDE-PAREI, na hora, no jeito dele", cobre=["R089", "R090", "R119", "R120", "R124"],
         texto="Pergunta vai na seção 'Perguntas para o Samuel' do ONDE-PAREI assim que surge. Começa pelo que é e onde fica, sem "
               "palavra de dentro (número, arquivo, etapa), com print do caso real e 'O que você escolhe', com a sua sugestão. "
               "Você nunca grava na Central.",
         porque="106 perguntas voltaram com 'Ainda não entendi' (§11.13); 8 perguntas ficaram escondidas num ONDE-PAREI (22/10)."),
    dict(n=9, titulo="Seu ramo, commit a cada passo, nada se apaga fora", cobre=["R136", "R074", "R080", "R054", "R133"],
         texto="Trabalhe só na sua cópia e no seu ramo; commit e push a cada passo, com o ONDE-PAREI em dia. Fora de "
               "D:\\programas\\EditorImpressao nada se apaga; dentro, só o que você criou. Junção nunca com rm -rf. Acervo só para ler.",
         porque="O limite da conta já derrubou agentes; em 29/09 um agente apagou D:\\d inteira."),
    dict(n=10, titulo="Não abra agente, não use a tela dele, entregue à gerente", cobre=["R106", "R039", "R134"],
         texto="Não abra outros agentes. Não abra janela nem pergunta do Windows na tela do Samuel, e não feche processo que não é "
               "seu, a não ser numa prova que a gerente combinou com ele. Entregue sempre à gerente.",
         porque="Cinco agentes rodando sem ele saber (10/11); caixas abertas na tela dele (30/09, 23/10)."),
]


def contar():
    """Os números da proposta: regras, repetidas, contraditórias, por máquina."""
    total = len(REGRAS)
    repetidas = [r for r in REGRAS if len(r["onde"]) >= 2]
    com_contra = [r for r in REGRAS if r.get("contra", "").startswith("X") and r["contra"] in CONTRADICOES]
    maq = {k: sum(1 for r in REGRAS if r["maq"] == k) for k in ("sim", "em parte", "nao")}
    return dict(total=total, repetidas=len(repetidas), contradicoes=len(CONTRADICOES),
                regras_em_contradicao=len(com_contra), diferencas=len(DIFERENCAS_PEQUENAS),
                vencidas=len(VENCIDAS), maq=maq, informacao=len(INFORMACAO))


if __name__ == "__main__":
    print(contar())
