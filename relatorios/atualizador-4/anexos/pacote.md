# Pacote de regras: Os 4 consertos do atualizador para a primeira entrega ao Kaique (D-824)

Papel: **implementador**. Tipo de trabalho (sai dos arquivos): git e arquivos, imagem, filtros e processamento do livro, tela (ui/), testes, Windows e instalador (e qualquer conversa com programa de fora).


Copie as duas seções abaixo, sem mudar nada, para o começo do seu ONDE-PAREI: o porteiro lê dali quais arquivos você pode mexer, e a gerente compara com este pacote.

## Pedido

- Papel: implementador
- Commit de partida: 4a775ba8
- Ramo: atualizador-4-consertos-2026-11-21

## Arquivos que vou mexer

- `atualizacao.py`
- `core/ocr_kraken.py`
- `ui/testes_a_distancia_ui.py`
- `configuracoes.py`
- `tests/test_decisoes_ajudante_da_atualizacao.py`
- `tests/conferencias_excecoes.json`
- `tests/test_atualizador_4.py` (novo)
- `relatorios/atualizador-4/`

## Lugares da lista de exceções nos seus arquivos

40 lugares. Cada um é identificado pela função e pelo texto da linha: mexer numa dessas linhas sem consertá-la, ou renomear ou mover a função onde ela está, vira erro novo (e nenhum item entra na lista por ramo de agente). Quem conserta tira o item no mesmo commit (`python -m regras_dos_agentes excecoes --diminuir`).

**Não renomeie nem mova estas funções neste trabalho (passo 3): elas guardam lugares de outros passos, e o lugar é a função e o texto.**

- `atualizacao.py`, função `ao_desinstalar` (lugares do passo 5)
- `atualizacao.py`, função `criar_as_tarefas` (lugares do passo 5)

- K01 `atualizacao.py` (_aplicar_pacote_quando_sair, passo 3, 1x): `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)`
- K01 `atualizacao.py` (_aplicar_pacote_quando_sair, passo 3, 1x): `| getattr(subprocess, "DETACHED_PROCESS", 0))`
- K01 `atualizacao.py` (_dono_do_arquivo, passo 3, 1x): `advapi32, kernel32 = ctypes.windll.advapi32, ctypes.windll.kernel32`
- K01 `atualizacao.py` (_dono_do_arquivo, passo 3, 1x): `if advapi32.GetNamedSecurityInfoW(wintypes.LPCWSTR(str(caminho)), 1, 1, ctypes.byref(dono)`
- K01 `atualizacao.py` (_dono_do_arquivo, passo 3, 1x): `if not advapi32.ConvertSidToStringSidW(dono, ctypes.byref(texto)):`
- K01 `atualizacao.py` (_dono_do_arquivo, passo 3, 1x): `kernel32.LocalFree(descritor)`
- K01 `atualizacao.py` (_dono_do_arquivo, passo 3, 1x): `kernel32.LocalFree(texto)`
- K01 `atualizacao.py` (_lancar_escondido, passo 3, 1x): `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)`
- K01 `atualizacao.py` (_lancar_escondido, passo 3, 1x): `subprocess.Popen(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "`
- K01 `atualizacao.py` (_lancar_escondido, passo 3, 1x): `| getattr(subprocess, "DETACHED_PROCESS", 0))`
- K01 `atualizacao.py` (_ler_chave_do_inno, passo 3, 1x): `for vista in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):`
- K01 `atualizacao.py` (_ler_chave_do_inno, passo 3, 1x): `import winreg`
- K01 `atualizacao.py` (_ler_chave_do_inno, passo 3, 1x): `return {nome: winreg.QueryValueEx(chave, nome)[0] for nome in ("UninstallString", "Install`
- K01 `atualizacao.py` (_ler_chave_do_inno, passo 3, 1x): `with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, CHAVE_DO_INNO, 0, winreg.KEY_READ | vista) `
- K01 `atualizacao.py` (_ler_versao_do_visual_c, passo 3, 1x): `achadas.append(tuple(int(winreg.QueryValueEx(chave, nome)[0]) for nome in ("Major", "Minor`
- K01 `atualizacao.py` (_ler_versao_do_visual_c, passo 3, 1x): `for vista in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):`
- K01 `atualizacao.py` (_ler_versao_do_visual_c, passo 3, 1x): `if winreg.QueryValueEx(chave, "Installed")[0] != 1:`
- K01 `atualizacao.py` (_ler_versao_do_visual_c, passo 3, 1x): `import winreg`
- K01 `atualizacao.py` (_ler_versao_do_visual_c, passo 3, 1x): `with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, CHAVE_DO_VISUAL_C, 0, winreg.KEY_READ | vis`
- K01 `atualizacao.py` (_linhas_da_janelinha, passo 3, 1x): `"$jPs = [powershell]::Create(); $jPs.Runspace = $jRun",`
- K01 `atualizacao.py` (_marca_existe, passo 3, 1x): `handle = kernel32.OpenMutexW(0x00100000, False, nome)`
- K01 `atualizacao.py` (_marca_existe, passo 3, 1x): `kernel32 = ctypes.windll.kernel32`
- K01 `atualizacao.py` (_marca_existe, passo 3, 1x): `kernel32.CloseHandle(handle)`
- K01 `atualizacao.py` (apagar_tarefa, passo 3, 1x): `codigo, saida = rodar(["schtasks", "/Delete", "/TN", NOME_DA_TAREFA, "/F"])`
- K01 `atualizacao.py` (comando_de_rodar_a_tarefa, passo 3, 1x): `return ["schtasks", "/Run", "/TN", NOME_DA_TAREFA]`
- K01 `atualizacao.py` (criar_tarefa, passo 3, 1x): `codigo, saida = rodar(["schtasks", "/Create", "/TN", NOME_DA_TAREFA, "/XML", str(arquivo),`
- K01 `atualizacao.py` (marcar_programa_aberto, passo 3, 1x): `_MARCA = ctypes.windll.kernel32.CreateMutexW(None, False, MARCA_DE_ABERTO) or None`
- K01 `atualizacao.py` (passo_de_preparar_o_computador, passo 3, 1x): `f" $p = Start-Process -FilePath {_aspas_do_powershell(str(exe))}"`
- K01 `atualizacao.py` (script_de_trocar_e_reabrir, passo 3, 1x): `f" $tarefa = (Get-ScheduledTask -TaskPath {_aspas_do_powershell(chr(92) + pasta + chr(92))`
- K01 `atualizacao.py` (script_de_trocar_e_reabrir, passo 3, 1x): `f"& schtasks {rodar} | Out-Null",`
- K01 `atualizacao.py` (script_de_trocar_e_reabrir, passo 3, 1x): `f"Start-Process -FilePath {_aspas_do_powershell(str(exe))}"`
- K01 `atualizacao.py` (script_de_trocar_e_reabrir, passo 3, 1x): `f"Wait-Process -Id {int(pid)} -Timeout 120",`
- K01 `atualizacao.py` (update_exe, passo 3, 1x): `return pasta_do_programa().parent / "Update.exe"`
- K02 `atualizacao.py` (_aplicar_pacote_quando_sair, passo 3, 1x): `| getattr(subprocess, "DETACHED_PROCESS", 0))`
- K02 `atualizacao.py` (_lancar_escondido, passo 3, 1x): `| getattr(subprocess, "DETACHED_PROCESS", 0))`
- K04 `atualizacao.py` (ao_desinstalar, passo 5, 1x): `registrar(f"desfazer os testes à distância (D-731): {'mandado' if feito.ok else 'NÃO manda`
- K04 `atualizacao.py` (criar_as_tarefas, passo 5, 1x): `registrar(f"criar a tarefa do desfazer (D-731): {'certo' if desfazer.ok else 'NÃO deu cert`
- K04 `atualizacao.py` (passo_de_preparar_o_computador, passo 3, 1x): `"antiga (D-733)",`
- K04 `atualizacao.py` (preparar_na_primeira_abertura, passo 3, 1x): `"atualização não foi criado; a pergunta volta na próxima abertura (D-741)")`
- K04 `atualizacao.py` (preparar_na_primeira_abertura, passo 3, 1x): `"bem; conta como não feita e a pergunta volta na próxima abertura (D-749)")`

## 1. Sempre (todo trabalho)

1. **Só o que foi pedido e decidido.** Faça só o que o pedido e as decisões do Samuel mandam. Nada de botão, aviso, texto ou comportamento a mais. Se a decisão parecer impossível, contraditória ou pouco clara, ou se a única saída for um remendo: pare e escreva a pergunta (não faça diferente em silêncio, nem 'por enquanto'). *Por quê:* É a falha que mais se repetiu: decisões de 25/09 nunca construídas, e agentes mudando o que ele tinha definido (§11.7).
2. **O novo não estraga o que já funciona.** Antes de mexer, anote o que já está escolhido e testado ali. Teste antigo que quebra faz a entrega voltar; nunca mude um teste antigo para ele passar. *Por quê:* Ele disse: 'essa é uma nova regra que todos os agentes precisam ler' (D-605).
3. **Sem gambiarra, em tudo.** Ache a causa, a função que decide, e todos os caminhos que chegam nela (grep). Mude num lugar só e faça todos os caminhos usarem esse lugar. Nada de desvio para um caso, nem conta ou lista copiada. *Por quê:* 17 remendos achados em 10/11 e os 33 defeitos do atualizador em 18/11 têm a mesma causa (§11.12).
4. **Nada é feito sem conferir de verdade.** Só diga 'feito' do que você conferiu de verdade (abrindo o arquivo, olhando a imagem, perguntando ao Windows). Escreva toda ressalva. Nunca escreva 'APROVADO': só o Samuel aprova. *Por quê:* 57 commits 'feito' e zero aprovados; '10 de 10 corretas' com seis erradas; 'Desligado' gravado sem desligar.
5. **Leia a peça de fora antes de usar.** Antes de usar uma peça que não é nossa (biblioteca, função do Windows, PowerShell, Velopack, Qt), leia a documentação e, se não bastar, o código. Anote o que ela faz em cada caso que usamos, com a fonte. Separe o lido do deduzido. Quando o nosso código recusa, filtra ou procura algo, a leitura da peça de fora lista também tudo o que ela aceita como entrada, com a fonte (ex.: o Python importa `.py`, `.pyw`, `.pyd`, `.pyc`, pasta com e sem `__init__`, `.zip` no caminho; o Windows aceita `\\?\`, `\\localhost\C$`, nome curto), e a recusa compara a coisa de verdade, não o texto. *Por quê:* Na etapa 5 o atualizador foi escrito sem ler o Velopack nem o Windows (§11.12.6); no passo 1, a peça recusava C:\Windows e aceitava o mesmo lugar escrito de outros jeitos (D-813).
6. **Decisões do Livro: cumprir e provar cada uma.** As decisões que o pedido traz (número e palavras dele) vão no começo do ONDE-PAREI; na entrega, como cumpriu cada uma, com teste ou print. Aparência não é prova. Palavras dele sempre copiadas do Livro, nunca de memória. *Por quê:* As decisões se perdiam entre o pedido e o código (§11.3 e §11.4).
7. **Pense em quem usa e no livro que sai.** Antes de mexer, escreva o que o Kaique vê e faz, passo a passo, antes e depois, e o que muda no PDF. Na entrega, confira. *Por quê:* Regra do Samuel para todo agente (D-637).
8. **Pergunta ao Samuel: no ONDE-PAREI, na hora, no jeito dele.** Pergunta vai na seção 'Perguntas para o Samuel' do ONDE-PAREI assim que surge. Começa pelo que é e onde fica, sem palavra de dentro (número, arquivo, etapa), com print do caso real e 'O que você escolhe', com a sua sugestão. Você nunca grava na Central. *Por quê:* 106 perguntas voltaram com 'Ainda não entendi' (§11.13); 8 perguntas ficaram escondidas num ONDE-PAREI (22/10).
9. **Seu ramo, commit a cada passo, nada se apaga fora.** Trabalhe só na sua cópia e no seu ramo; commit e push a cada passo, com o ONDE-PAREI em dia. Fora de D:\programas\EditorImpressao nada se apaga; dentro, só o que você criou. Junção nunca com rm -rf. Acervo só para ler. *Por quê:* O limite da conta já derrubou agentes; em 29/09 um agente apagou D:\d inteira.
10. **Não abra agente, não use a tela dele, entregue à gerente.** Não abra outros agentes. Não abra janela nem pergunta do Windows na tela do Samuel, e não feche processo que não é seu, a não ser numa prova que a gerente combinou com ele. Entregue sempre à gerente. *Por quê:* Cinco agentes rodando sem ele saber (10/11); caixas abertas na tela dele (30/09, 23/10).

## 2. As regras do seu trabalho (62)

**Windows e instalador (e qualquer conversa com programa de fora)**
- A janela nunca congela: Todo trabalho demorado em QThread, com barra e cancelar que funciona; esperar o Windows também (na etapa 5 a janela ficou parada 14 min). (CLAUDE.md §3)
- Texto com acento, caminho sem acento: Texto de tela com acento (UTF-8); caminho de disco sem acento. (CLAUDE.md §3)
- core/ não importa ui/: core/ nunca importa ui/: o processamento roda por linha de comando, sem janela. (CLAUDE.md §7)
- Onde o programa guarda estado: %LOCALAPPDATA%\EditorImpressao guarda projetos e histórico; fechar e reabrir preserva tudo; desinstalar NÃO apaga essa pasta. (CLAUDE.md §7)
- Uma peça só para conversar com o que está fora: Windows, disco, rede, GitHub, Velopack, outro programa: uma peça só para cada conversa; ninguém escreve a sua versão (na etapa 5, cada função pedia licença do seu jeito). (CLAUDE.md §11.12.1)
- Antes de escrever, a lista das falhas: No ONDE-PAREI, para cada coisa que pode dar errado (sem licença, sem internet, disco cheio, 'Não', arquivo preso, desligar no meio), o que o programa faz; nunca pela metade. (CLAUDE.md §11.12.3)
- Peça de mentira não prova (D-767): Teste com peça de mentira só prova a lógica em volta. O que mexe no Windows só conta rodando de verdade, à vista, e funcionando. Nada em área escondida. (CLAUDE.md §11.12.4) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-785): à vista o que mexe com o Windows (a lista da D-785); escondidos os testes que não dependem dele.**
- O teste do Windows roda em três computadores diferentes: GitHub: Windows em inglês ('Everyone', 'Administrators'), licença de administrador já ligada (o dono do que se cria é o grupo Administradores), pasta temporária no D:. PC do Samuel: português, sem a licença, o D: dá controle total a 'Todos'. Notebook do Kaique: a conferir. O teste compara a conta pelo número dela, nunca pelo nome escrito, e não supõe o estado de hoje da lista ou da versão de teste. (Três rodadas do GitHub perdidas no passo 1.) (DECISOES.md D-810)

**Tela (ui/)**
- PySide6, nunca tkinter: PySide6, nunca tkinter nem customtkinter (uma versão anterior travava). (CLAUDE.md §3)
- Nenhuma exceção fecha a janela: Erro vira aviso em português numa caixa; o técnico vai para o log. (CLAUDE.md §3)
- Nenhum emoji em rótulo: Nenhum emoji em rótulo de tela (quebrou no Windows). (CLAUDE.md §3)
- Erro nunca como stack trace: sys.excepthook grava em erros.log e mostra 'Aconteceu um problema inesperado, mas o programa continua funcionando.' (CLAUDE.md §3)
- Modelo de dados em dois níveis: ConfigFolha (o que veio) e ConfigPagina (o que sai); ajustes de cada filtro separados; recorte e ângulo na página. (CLAUDE.md §7)
- Queixas do Kaique são requisito: Os .txt com print em 'Teste de livros' são fonte de requisito. (CLAUDE.md §7)
- Barra de rolagem cinza, de propósito: A barra de rolagem é cinza #a8a49e de propósito; não reverter sem decisão do Samuel. (CLAUDE.md §9)
- Layout: pista visual em toda área de clicar: Toda área de clicar ou arrastar tem cursor, alça ou contorno (um arrasto 'não funcionava' só porque ninguém via onde clicar). (layout.md 'Regras de tela')
- Toda função automática tem ligar e desligar: Toda função automática tem botão de ligar e desligar (regra 8 do plano). (layout.md 'Regras de tela')

**Imagem, filtros e processamento do livro**
- Critério final do livro: 'Eu quero que o papel saia branco, e o desenho também saia perfeito.' (CLAUDE.md §1)
- Uma página por vez na memória: O pico de memória não cresce com o livro (há livro de 300 MB). Nunca uma lista com todas as páginas processadas. (CLAUDE.md §3)
- Algoritmo consagrado: Algoritmo consagrado em vez de fórmula própria (a fórmula caseira deu qualidade ruim). (CLAUDE.md §3)
- Nenhum modelo generativo: Nada que desenhe pixel ou invente texto: inventaria detalhe numa gravura de 1579. Rede neural só aponta onde está a coisa. (CLAUDE.md §3)
- GPU sem float16 rápido: GTX 1650 4 GB, sem tensor cores: nada que dependa de float16 rápido. O notebook do Kaique não tem placa de vídeo. (CLAUDE.md §3)
- Filtro de velocidade no GitHub: Mudança em processamento passa pelo filtro de velocidade do GitHub (antes e depois na mesma máquina). Não rodar o teste_velocidade completo no PC. (CLAUDE.md §4.6) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-786): vale a regra de 19/10: velocidade no GitHub a cada mudança; no PC, no fim da fase.**
- Teste de imagem pelo caminho inteiro: Teste de imagem e conferência levam a página por dividir → endireitar → cortar → filtro, com ajustes de fábrica, até a ferramenta testada. (CLAUDE.md §4.10)
- Cada foto diz o caminho e as opções: Toda foto diz por onde a página passou ('endireitada, cortada, Preto e branco + Só as letras'). (CLAUDE.md §4.10)
- Só páginas que vão ser impressas: Nunca lombada, capa ou contracapa de couro ou papelão nos testes. (CLAUDE.md §4.10)
- Protocolo de mudança de imagem: Medir antes, uma mudança, medir de novo; piorou, reverter. Se valer mesmo assim, não reverter sozinho: apresentar os dois. (CLAUDE.md §5)
- Tudo o que foi tentado vai para melhorias.md: O que foi tentado, inclusive o que falhou, vai para relatorios/melhorias.md (para ninguém repetir caminho fechado). (CLAUDE.md §5)
- O que o agente decide sozinho: Pode decidir: limiar, janela, k, bloco, ordem interna do filtro, binarizador, cache, paralelismo, memória. (CLAUDE.md §6)
- Desempenho já resolvido, não refazer: Análise a 150 DPI e fundo estimado em miniatura de ~400 px: não refazer. (CLAUDE.md §7)
- Ordem obrigatória do processamento: Livro novo: dividir → endireitar → cortar → filtro → cadernos. Projeto de antes de 09/10 sem ordem_do_preparo: a ordem antiga, idêntica. (CLAUDE.md §7)
- Régua e velocidade; nada mais lento: Rodar a régua e o teste de velocidade; piorou, reverter ou apresentar os dois. Nenhum item deixa o programa mais lento. (CLAUDE.md §8 passo 5) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-786): vale a regra de 19/10: velocidade no GitHub a cada mudança; no PC, no fim da fase.**
- Mancha do verso: o defeito mais grave: O Preto e branco escurece a mancha do verso; a régua não pega. Caminho recomendado: espelhar o verso e subtrair. (CLAUDE.md §9)
- A régua precisa de critérios novos: Comparar onde havia mancha, olhar a moldura, medir sujeira guardada. (CLAUDE.md §9)
- Amarelado está na tinta: A tinta de 1579 é marrom; cuidado: rubricação desbotada também é marrom. (CLAUDE.md §9)
- Não há binarizador vencedor: Os 18 do DoxaPy se invertem de livro para livro. (CLAUDE.md §9)
- Não desfazer a correção do 'magic color': Dividir pelo fundo relativo ao papel, ganho igual nos três canais, curva de ombro no L: não desfazer (a receita comum estraga capa colorida). (CLAUDE.md §9)
- Scan de baixa resolução não se recupera: O remédio é reescanear; é o único lugar onde 'até ficar perfeito' não vale. (CLAUDE.md §9)

**Testes**
- Teste de máquina: o agente decide: O que tem resposta objetiva (fecha? páginas certas? memória? PDF estragado? cadernos? acento?) roda a cada mudança, sozinho. (CLAUDE.md §4.1)
- Máquina ou olho, item por item: Todo item diz se foi conferido por máquina ou por olho. (CLAUDE.md §4.3)
- Onde roda cada teste: No PC, um arquivo de teste por vez; a suíte inteira e o teste_botoes no GitHub (push antes); a entrega traz o número da rodada. (CLAUDE.md §4.6) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-787): vale a regra de 19/10: no PC, um arquivo de teste por vez; o conjunto inteiro no GitHub.**
- Teste de reversão em todo conserto: Todo bug consertado ganha teste que FALHA no código antigo e passa no novo, com o bug na docstring; o verificador prova no antigo. Bug de imagem: uma medida, ou ressalva escrita. (CLAUDE.md §4.7)
- Prova: caminho → função e o mesmo resultado em todos: Na entrega, a lista 'caminho → função' e uma prova em tests/ que cobra o mesmo resultado por todos os caminhos. (CLAUDE.md §11.12)
- Teste escrito antes do código, quando der: Teste automático do que é objetivo, escrito antes do código quando der. (implementador.md 'O que você faz')
- Toda conferência diz de onde vem cada dado: Toda conferência (do porteiro, de um teste ou do programa) diz de onde vem cada dado que usa; dado que o próprio conferido escreve ou pode trocar (o ramo do agente, o ONDE-PAREI, a anotação do programa, a pasta de troca, o arquivo da vez anterior) não serve de prova. (O 'sim' forjável e o juiz escolhido pelo ramo, no passo 0; o arquivo da vez anterior, no passo 1.) (DECISOES.md D-812)

**Git e arquivos**
- Handoff só com pedido do Samuel: Só atualizar o handoff de historico/ quando o Samuel pedir. (CLAUDE.md §7)
- Commit na hora com o defeito por extenso; nunca segredo: Commit com o defeito resolvido escrito por extenso e push; revisar o que vai no commit; nunca segredo; nunca desfazer o .gitignore sem avisar. (CLAUDE.md §8 passo 10)
- Cada papel no seu lugar: Implementador: core/ e scripts, não ui/ (salvo pedido). Layout: só ui/. Verificador e pesquisador: não mexem no código do programa. (CLAUDE.md §10.1) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-796): o agente de tela mexe em core/ só nos arquivos que o pedido nomear; sem isso, só ui/.**
- A cópia divide o .git com o Samuel: nada de comando que muda o .git inteiro: A sua cópia divide a pasta .git com o repositório do Samuel. Comando que muda o .git inteiro (fetch com --depth, gc, prune, stash, config, mexer em ramo que não é o seu) não roda na sua cópia, nem em script ou teste, a não ser num repositório de prova em pasta temporária (regras_dos_agentes/repositorio_de_prova.py). Atalho de pasta (junção) só sai com cmd /c rmdir ou com (Get-Item <atalho>).Delete(), que tiram só o atalho, contando os arquivos da pasta de verdade antes e depois. (O repositório do PC ficou raso em 19/11 com um git fetch --depth=1; a pasta modelos/ foi esvaziada em 18/11 ao tirar um atalho. O porteiro acusa, K25.) (DECISOES.md D-809)

**Todo trabalho**
- Ordem de leitura e quem manda: Quem manda: o Livro de decisões e o plano; o CLAUDE.md vem depois. O que ele disser contra o plano, vale o plano. (CLAUDE.md topo) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- PEDIDOS.md e handoff são histórico: PEDIDOS.md e o handoff em historico/ só servem de consulta; não dizem o que fazer. (CLAUDE.md topo)
- Não recomeçar do zero: Não reescrever módulo inteiro nem reorganizar o que funciona. Testar não é licença para reconstruir. (Duas versões já fracassaram.) (CLAUDE.md §2)
- Ir até o fim dentro da alçada: Decidir o que é da alçada e executar tudo, sem parar a cada passo. Se o contexto acabar, parar num commit com o programa rodando. (CLAUDE.md §2)
- Honesto: avisar erro e risco: Se o Samuel ou a gerente estiver enganado ou correndo risco, avisar. Não concordar para agradar. (CLAUDE.md §2)
- Python 3.14, não rebaixar: A máquina só tem Python 3.14. Nunca sugerir rebaixar. (CLAUDE.md §3)
- Ler a memória antes: Antes de começar, ler memoria/INDICE.md e as fichas do assunto. A memória nunca contradiz o plano. (CLAUDE.md §4.9)
- Item da fase atual, na ordem: O item vem da fase atual do plano; Lista de bugs no começo da fase. (CLAUDE.md §8 passo 1) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Ideia nova vai para a Lista de espera; bug que não impede, para a Lista de bugs: Ideia nova: não fazer, anotar para a Lista de espera. Bug que impede a tarefa: consertar e dizer. Bug que não impede: anotar com data e print. (CLAUDE.md §10.2) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Docstring em tudo o que tocar: Todo arquivo e função tocados ganham docstring: o que faz e o que é seguro ou arriscado mudar. (CLAUDE.md §10.5)
- Plano novo não apaga pendência: Plano novo diz o que resolve e o que deixa de fora; nunca apaga pendência por omissão. (CLAUDE.md §10.6)
- Prosa de checkpoint não é prova: Quando o estado importa, conferir o código e o git log, não o texto de checkpoint. (CLAUDE.md §10.8)
- Obra D-014: o que não vale durante a obra: Durante a obra não valem 'conferir cada item antes do próximo' nem 'uma fase por vez'; nada entra no fase-1 antes da conferência final; duas decisões que se contradizem: vale a mais recente. (CLAUDE.md fim) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**

## 3. As decisões que este trabalho precisa cumprir (copiadas do Livro)

- **D-718** (16/11/2026): Chat, pergunta 1 do plano da frente do notebook do Kaique ("se a atualização falhar, o programa volta para a versão antiga?"): "Sim, e tem que avisar a gente de alguma maneira"
  Na prática: Se a atualização falhar, o programa volta sozinho para a versão anterior e avisa o Samuel e a gerente. Como avisar: perguntado a ele (sugestão: aviso na tela do Kaique e registro que a gerente lê daqui pelo comando de longe).
- **D-719** (16/11/2026): Chat, como avisar a atualização que falhou (D-718): opção 1 "aviso na tela dele e um registro que eu leio daqui" (sem senha dentro do programa) ou opção 2 "a 1 e mais um recado automático no seu celular" → "1"
  Na prática: Quando a atualização falha: na tela do Kaique aparece "A atualização não deu certo. O programa voltou para a versão anterior e continua funcionando. Avise o Samuel.", e o erro vai para um registro que a gerente lê daqui pelo comando de longe (D-705). Nenhuma senha dentro do programa.
- **D-724** (16/11/2026): Chat, sobre a assinatura da versão nova ("Grátis: o seu PC assina cada versão, e o programa do Kaique confere antes de instalar [...] Grátis mais um certificado pago: tira esse aviso, mas custa todo ano."): "gratis, mas o que é essa assinatura e é segura?"
  Na prática: A versão para o Kaique leva a assinatura grátis: o PC do Samuel assina cada versão com uma chave que só ele tem, e o programa confere antes de instalar; versão sem a assinatura certa não é instalada. O certificado pago do Windows fica para depois, se ele quiser. Explicado no chat: é o mesmo método das atualizações do Mac e dos programas do Linux; o cuidado é a chave: nunca no GitHub, com uma cópia de reserva.
- **D-727** (16/11/2026): Chat, à pergunta "Posso instalar o .NET no seu PC para a etapa 3 começar?": "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né"
  Na prática: Tudo o que o programa precisa para funcionar no notebook do Kaique vai dentro do instalador; nada é baixado da internet na hora de instalar. Ex.: o Visual C++ continua dentro do instalador (o estudo previa baixá-lo com o Velopack: substituído). O .NET (só o empacotador usa, no PC do Samuel) foi instalado em 16/11 (SDK 8.0.428, winget).
- **D-732** (17/11/2026): Chat. Ele: "a atualização tinha que ser procurada quando ele abre o programa né? assim como todo aplicativo faz". A gerente citou a D-714 ("toda vez que o pc inicializar") e explicou por que (Arquivos de Programas pede administrador; ao ligar, a tarefa do Windows troca sem perguntar), e perguntou "Quer manter como está no Livro, procurando quando o computador liga?". Ele: "não, faz quando o programa é aberto"
  Na prática: A versão nova é procurada quando o programa abre, como os aplicativos fazem; não mais quando o computador liga. Substitui essa parte da D-714 (e o "entra na próxima vez que o computador ligar" do "Depois" da D-720, que depende dela). O resto continua: publicada de propósito (D-714), aviso para salvar e reiniciar (D-715, D-720), volta se falhar e avisa (D-718, D-719), assinatura (D-724). O jeito de trocar os arquivos sem a tarefa (licença de administrador, pergunta do Windows) vai num plano do agente, e o que só o Samuel decide vira pergunta.
- **D-733** (17/11/2026): Chat, à pergunta "para a versão nova entrar quando o programa abre, existem três jeitos: 1. (sugiro este) Na primeira vez que o Kaique abre o programa, o Windows pergunta "Deseja permitir...?" uma vez só. Depois disso, cada versão nova entra sozinha, sem perguntar mais nada [...] 2. O Windows pergunta [...] toda vez que chega uma versão nova. 3. Instalar o programa só na conta do Kaique [...] os testes de longe deixam de funcionar. Qual dos três?": "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?"
  Na prática: Jeito 1 (alternativa B do plano `relatorios/frente-kaique-2026-11-16/d731-desinstalar/plano-d732.md`): o programa continua em Arquivos de Programas; na primeira abertura, uma pergunta do Windows ("Deseja permitir...?") cria o ajudante (a tarefa do Windows que roda como o sistema) e faz o resto que pede licença (Visual C++, tirar o Inno antigo, a senha dos testes se houver). Depois, o programa, ao abrir, procura a versão nova (D-732) e chama o ajudante para trocá-la: nenhuma pergunta por atualização nem na volta (D-718). Muda a D-723 só nisto: a tarefa nasce na primeira abertura, não na instalação (resolve o achado B1 de 16/11). Os testes à distância continuam possíveis, porque o programa [...]
- **D-734** (17/11/2026): Chat, à pergunta "A versão nova chegou e o Kaique clicou "Depois" no aviso para reiniciar. Quando ela entra? Sugiro: quando ele fechar o programa. Ou: na próxima vez que ele abrir o programa, com uma espera curta antes da janela aparecer.": "quando ele abrir o programa de novo"
  Na prática: Com "Depois" (D-720), a versão nova entra na próxima vez que o Kaique abrir o programa, com uma espera curta antes da janela aparecer. Substitui o "entra na próxima vez que o computador ligar" da D-720 (que dependia da D-714, mudada pela D-732). Fechar o programa não troca nada.
- **D-735** (17/11/2026): Chat, à pergunta "Na primeira vez que o programa abre, aparece o "Deseja permitir...?" do Windows. Ele deve aparecer sempre, mesmo quando o Kaique não digitar a senha dos testes à distância? Sugiro que sim. Sem essa pergunta, a atualização sozinha não fica pronta e a instalação antiga do programa não sai do notebook." (antes, ele: "vai aparecer o deseja permitir sempre que ele for atualizar né?"; a gerente: "Não [...] uma vez só, na primeira vez [...] Depois disso, cada versão nova entra sozinha"): "Sim"
  Na prática: A pergunta do Windows da primeira abertura (D-733) aparece sempre, com ou sem a senha dos testes à distância. Ela prepara o ajudante da atualização, o Visual C++ e tira a instalação antiga; a senha, se digitada, entra na mesma pergunta. Nas atualizações seguintes, nenhuma pergunta.
- **D-741** (17/11/2026): Chat, à pergunta "Se o Kaique clicar "Não" [no "Deseja permitir...?" da primeira abertura], do jeito que está, a pergunta não volta, e ele fica sem a atualização sozinha. Faço a pergunta voltar toda vez que ele abrir o programa, até ele clicar "Sim"? Sugiro que sim.": "Sim"
  Na prática: Se o Kaique disser "Não" à pergunta do Windows da primeira abertura (D-733, D-735), ela volta a cada vez que ele abrir o programa, até ele dizer "Sim". Depois do "Sim", nunca mais aparece (as atualizações seguem sem perguntar). Na conta de testes, nada pergunta (D-736).
- **D-749** (17/11/2026): Chat, à pergunta "se o Kaique clicar "Sim" e a preparação der erro no meio, a pergunta volta na próxima abertura? Sugiro que sim.": "Sim"
  Na prática: Se o Kaique clicar "Sim" na pergunta do Windows e a preparação do computador (`--preparar-o-computador`, D-733) der erro no meio, a preparação conta como não feita: a pergunta do Windows volta na próxima abertura do programa, como quando ele não clica "Sim" (D-741).
- **D-763** (17/11/2026): Chat, à pergunta "Posso mandar um agente fazer esse conserto? Sugiro que sim." (prova de 17/11, ramo `velopack-pasta-2026-11-17`: o nome interno do pacote, "EditorImpressao", é igual ao da pasta dos projetos; a cada abertura o Velopack grava ali uma cópia do Update.exe, e o desinstalador do .msi apagou a pasta `%LOCALAPPDATA%\<nome do pacote>` inteira, com o projeto de mentira dentro): "ok, pode fazer"
  Na prática: O nome interno do pacote do Velopack deixa de ser igual ao nome da pasta dos projetos (`%LOCALAPPDATA%\EditorImpressao`), antes da primeira instalação de verdade. A troca é num lugar só (`versao.ID_DO_PACOTE`), que todo o resto lê; o Kaique continua vendo "Editor de Impressão". Uma prova cobra que o nome do pacote nunca é o da pasta dos projetos, e a prova da pasta de reserva e do desinstalar é repetida com o nome novo. O nome novo exato é detalhe técnico (escolha da gerente, D-014). A instalação no PC do Samuel (etapa 5) espera esse conserto.
- **D-767** (18/11/2026): Chat, na etapa 5, depois dos 7 defeitos achados no Windows de verdade (a gerente explicou que os testes automáticos trocam as peças do Windows por peças de mentira): "não faça mais nada escodindo ou de mentira" · logo depois: "não quero fazer consertos quero que funcione" · e: "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do atualizador e testes a distancias"
  Na prática: O que mexe no Windows (pergunta de administrador, PowerShell, tarefas, licenças de pasta, instalar e desinstalar, testes à distância) só conta como pronto quando roda de verdade no Windows, à vista, e funciona. Teste automático com peça de mentira não prova que funciona. Nada de área de trabalho escondida nos testes. O objetivo não é remendar cada defeito, é a parte do Windows funcionar inteira (CLAUDE.md §11.12). O alcance exato (por exemplo, as versões de teste servidas de uma pasta do D: em vez do GitHub) está sendo confirmado com o Samuel.
- **D-774** (18/11/2026): Chat, decisão 7 do plano da parte do Windows ("posso trocar os testes antigos que cobram o jeito errado?"; a gerente mostrou os 4 principais e os outros 5 do plano, seção 4.2): "ok"
  Na prática: Os testes antigos que cobram o jeito errado mudam para cobrar o jeito certo: o do "Reiniciar agora" (`DETACHED_PROCESS`), o do lugar da pasta (`C:\ProgramData\EditorImpressao\testes-a-distancia`), os dois da tranca da pasta (`/inheritance:r`, `/setowner`), e os outros cinco da seção 4.2 do plano. Cada teste novo falha no código de hoje e passa no consertado; nenhum muda só "para passar". Outro teste antigo que precise mudar vai ao Samuel antes, numa lista, um por um (CLAUDE.md §11.8).
- **D-779** (18/11/2026): Chat, decisão 11 do plano da parte do Windows ("a versão da ferramenta de atualizar"; A = ficar na 1.2.161 com a nossa proteção, sugestão; B = a versão de teste 1.3.39; C = esperar a final); ele perguntou "não tem outra peça que funcione melhor?" e a gerente comparou MSIX, tufup, WinSparkle e fazer a nossa: "ta vamos continuar com ele, mas o que fazemos para ele não dar defeito e porque nossa peças em voltadele deram defeito?"
  Na prática: Fica o Velopack 1.2.161, com a nossa proteção em volta dos dois defeitos dele: antes de trocar, o programa guarda a versão que funciona fora da pasta que é trocada e volta sozinho se a troca estragar; e a pasta que sobrava no desinstalar deixa de nascer. Nada muda para o Kaique. Quando sair a versão final da 1.3, ela é estudada e provada antes de trocar, com o "sim" do Samuel.
- **D-788** (18/11/2026): Chat, pergunta 1 de 3 do estudo do Kraken separado ("onde o motor fica no notebook do Kaique"; A = pasta própria dentro da pasta do programa, sugestão; B = um segundo programa só para o motor): "1" (a primeira opção)
  Na prática: O motor do Kraken mora numa pasta própria dentro da pasta do programa, `C:\Program Files\EditorImpressaoPrograma\motor-kraken\<versão>`, ao lado da parte que o Velopack troca: a atualização não toca nela, o desinstalar a tira junto, e na primeira instalação ele vem dentro do instalador (nada baixado na hora, D-727). Quando o motor mudar, o ajudante baixa só o motor, conferido pela assinatura do Samuel, e a versão nova só entra depois que ele chegou inteiro. Completa a D-768. Estudo no ramo `kraken-separado-2026-11-18`.
- **D-796** (19/11/2026): Chat, contradição X7 das regras dos agentes (o agente de layout "só mexe em ui/", CLAUDE.md §10.1 e `layout.md`, contra o §11.12, "de preferência em core/ (a tela só chama)"), explicada com o exemplo do Girar (sete jeitos na tela; o conserto é um jeito só por trás, que todos os botões usam): "não entendi" → "1, mas tem que ser explissito o pedido né" (opção 1: "Ele pode mexer nas duas partes, quando o pedido disser antes")
  Na prática: O agente de tela pode mexer também no processamento (`core/`) quando o conserto precisa levar a regra para um lugar só, mas só se o pedido da gerente disser isso explicitamente, antes, nomeando os arquivos de `core/` que ele pode mexer. Sem isso escrito no pedido, continua só em `ui/`. O porteiro barra (ele, logo depois: "o porteiro tem que bloquear"): se o agente de tela mexer num arquivo de `core/` que o pedido não nomeou, o trabalho não entra (a lista dos arquivos permitidos vai no pedido e no formulário da entrega, D-792, onde o porteiro lê). Resolve a contradição X7.
- **D-805** (19/11/2026): Chat, depois da sessão A do passo 1 do plano da parte do Windows (prova à vista, 16:11 a 16:19). Na pergunta do Windows apareceu o nome do arquivo (ele: "editordeimpressão.exe apareceu"; o print dele com o navegador na frente mostra "EditorImpressao.exe solicit..."). A gerente: "O que você escolhe: A (sugiro): fica 'EditorImpressao.exe'. Nada muda no programa. B: o arquivo passa a se chamar 'Editor de Impressao.exe', com espaços [...] C: comprar o certificado, que é pago todo ano [...] Qual?" Ele: "a"
  Na prática: Na pergunta de licença do Windows fica "EditorImpressao.exe" (com a faixa de editor desconhecido): sem certificado pago, o Windows mostra o nome do arquivo. O nome do arquivo não muda e não se compra certificado. Muda a D-782 ("Editor de Impressão" na pergunta). A explicação ao Kaique, quando houver, diz "EditorImpressao.exe".
- **D-806** (19/11/2026): Chat, depois da sessão A do passo 1 (risco 1 do plano-v3: com o navegador na frente, a pergunta do Windows só piscou no escudo da barra de tarefas; print dele, 16:19: "apareceu no canto e não no meio da tela"). A gerente explicou com o exemplo do Kaique (fecha o programa, "Quer atualizar?", "Sim": se a pergunta vem logo depois do clique, aparece no meio da tela; se vem segundos depois, pode só piscar) e sugeriu pedir a licença logo depois do clique. Ele: "não entendi" · "isso vai implicar em muito mais tempo de programação?" (resposta: não, é só a ordem, no passo 3) · "então pode ser opção A"
  Na prática: O programa pede a licença do Windows no mesmo instante do clique do Kaique (ex.: o "Sim" do "Quer atualizar?" ao fechar), enquanto a janela do programa ainda está na frente, para a pergunta vir no meio da tela. Nada de aviso novo na janelinha (a opção B, "clique no escudo piscando", não foi escolhida).
- **D-809** (19/11/2026): Chat, pergunta 1 de 6 do catálogo dos erros (família F9, "comando que muda o que é do Samuel sem ele ver": o repositório do PC cortado por um `git fetch --depth=1` em 19/11; a pasta `modelos/` esvaziada ao tirar um atalho em 18/11). Ele: "não entendi nada"; à versão curta ("A proposta é proibir esses comandos perigosos e fazer o porteiro barrar quando um agente tentar usar"): "ok, mas essas coisas foram recuperadas? e porque ele fez essa confusão se era regra ele não mexer? e tinha o porteiro para ele não fazer isso" (respostas: as duas recuperadas; não havia regra para esses casos; o porteiro ainda não existia e não confere esses comandos); "Fica assim?": "ok"
  Na prática: Regra nova dos agentes: a cópia do agente divide o `.git` com o repositório do Samuel; comando que muda o `.git` inteiro (`fetch --depth`, `gc`, `prune`, `stash`, `config`, mexer em ramo que não é o seu) não roda na cópia, nem em script ou teste, a não ser num repositório de prova em pasta temporária; atalho de pasta (junção) só sai com `cmd /c rmdir`, contando os arquivos da pasta de verdade antes e depois. Conferência nova do porteiro: acusa esses comandos em scripts e testes fora das peças de git que já existem (`conversa_com_o_git.py`, `repositorio_de_prova.py`).
- **D-810** (19/11/2026): Chat, pergunta 2 de 6 do catálogo dos erros (família F4, "o teste supõe o computador": três rodadas do GitHub perdidas no passo 1 por Windows em inglês, licença de administrador já ligada e pasta temporária no D:). A gerente: "Proposta: os agentes que escrevem testes recebem uma lista curta dessas diferenças entre o seu PC, o GitHub e o PC do Kaique, para já escrever o teste certo de primeira. Fica assim?" Ele: "ok"
  Na prática: Regra nova dos agentes (etiquetas Windows e testes): o teste do Windows roda em três computadores diferentes. GitHub: Windows em inglês ("Everyone", "Administrators"), licença de administrador já ligada (o dono do que se cria é o grupo Administradores), pasta temporária no D:. PC do Samuel: português, sem a licença, o D: dá controle total a "Todos". Notebook do Kaique: a conferir. O teste compara a conta pelo número dela, nunca pelo nome escrito, e não supõe o estado de hoje da lista ou da versão de teste. Só regra, sem conferência do porteiro (daria falso alarme).
- **D-811** (19/11/2026): Chat, pergunta 3 de 6 do catálogo dos erros (famílias F3 e F5: proteção sem teste e resultado não conferido; no passo 1, quem quebrou desligou proteções e nenhum teste reclamou). A gerente: "Proposta: na ficha de entrega, quem escreve passa a mostrar, para cada proteção, o teste que falha quando ela é desligada. [...] Fica assim?" Ele: "ok"
  Na prática: Pergunta nova no formulário da entrega (trabalho de Windows e de instalador): "Cada proteção e cada conferência do resultado (recusa, leitura de volta, desfazer) → o teste que falha quando ela é desligada, provado numa cópia." O programa do formulário confere que a lista existe e que cada teste citado existe; quem tenta quebrar confere se a lista está completa.
- **D-812** (19/11/2026): Chat, pergunta 4 de 6 do catálogo dos erros (família F1, "a conferência acredita num dado que não prova nada": o "sim" que o agente podia escrever sozinho, no passo 0; o arquivo de uma rodada anterior aceito como de agora, no passo 1). A gerente: "É como deixar o aluno corrigir a própria prova. Proposta: toda conferência diz de onde vem cada informação que usa. Informação que o conferido pode trocar não vale como prova. [...] Fica assim?" Ele: "ok"
  Na prática: Regra nova dos agentes: toda conferência (do porteiro, de um teste ou do programa) diz de onde vem cada dado que usa; dado que o próprio conferido escreve ou pode trocar (o ramo do agente, o ONDE-PAREI, a anotação do programa, a pasta de troca, o arquivo da vez anterior) não serve de prova. Pergunta nova no formulário, para trabalho que confere algo: "De onde vem cada dado que a sua conferência usa?"
- **D-813** (19/11/2026): Chat, pergunta 5 de 6 do catálogo dos erros (família F2, "a conferência olha o jeito mais comum e o vizinho passa": no passo 1, a peça recusava `C:\Windows` e aceitava o mesmo lugar escrito de outros jeitos; três voltas de quem quebra para fechar). A gerente: "Proposta: acrescentar à sua regra de 'ler antes de usar peça de fora' que, quando o programa recusa ou procura alguma coisa, o agente lista antes todos os jeitos que o Windows ou o Python aceitam para ela. E a proteção passa a comparar a coisa de verdade, não o texto escrito. Fica assim?" Ele: "ok"
  Na prática: Acréscimo à regra 6 do CLAUDE.md §11.12 (ler antes de usar peça de fora): "Quando o nosso código recusa, filtra ou procura algo, a leitura da peça de fora lista também tudo o que ela aceita como entrada, com a fonte (ex.: o Python importa `.py`, `.pyw`, `.pyd`, `.pyc`, pasta com e sem `__init__`, `.zip` no caminho; o Windows aceita `\\?\`, `\\localhost\C$`, nome curto), e a recusa compara a coisa de verdade, não o texto." Também vira foco de quem tenta quebrar.
- **D-814** (19/11/2026): Chat, pergunta 6 de 6 do catálogo dos erros (família F6, "o texto ao Samuel foge do combinado": pergunta que repetia o que ele já tinha decidido, ou "como você escolheu" sobre o que ele não escolheu). A gerente: "Proposta: antes de mandar qualquer pergunta para você, o agente anota em quais decisões suas procurou e por que essa ainda não está respondida. A pergunta só chega a você depois disso. Fica assim?" Ele: "ok"
  Na prática: Pergunta nova no formulário da entrega: "Para cada pergunta ao Samuel: as decisões do Livro que você procurou antes, e por que esta ainda não está respondida." A gerente confere antes de levar (§11.13, ponto 10). As famílias F7, F8 e F10 não viraram pergunta (o que já existe cuida delas, ou ficam em observação).
- **D-815** (20/11/2026): Chat. Ele: "pode conferir se não está ocorrendo alucinação por estar com contexto cheio" · "estou falando do agente que está trabalhando" · "esses agentes que você criou, sempre que vai fazer uma tarefa nova, chama outro com a mesmas instruções ou ifac rodando sempre o mesmo com memorias compactadas?". A gerente: tarefa nova sempre com agente novo, mas as voltas de conserto e de conferência da mesma tarefa reaproveitavam o mesmo agente, com a memória cheia e resumida; "Proposta: quem confere é sempre um agente novo em cada volta, com a memória limpa. Quem escreve pode ser o mesmo por até duas voltas. Depois disso, entra um novo, que começa pela ficha de onde o outro parou. Fica assim?" Ele: "ok"
  Na prática: Quem tenta quebrar (ou confere) é sempre um agente novo em cada volta, com o pacote e sem a memória da volta anterior. Quem escreve pode ser o mesmo agente por até duas voltas da mesma tarefa; da terceira em diante, um agente novo, que começa pelo ONDE-PAREI. Vale para a gerente em todos os trabalhos.
- **D-819** (21/11/2026): Chat, depois de a gerente aceitar sem perguntar o plano do agente da volta 9 (achar a pasta das ferramentas perguntando ao git), que trouxe um problema novo, quando havia um jeito mais simples (o lugar fixo `D:\programas\EditorImpressao-arquivos\ferramentas`). Ele: "não era melhor só ver se está instaldo no pc?" · "porque você escolheu o jeito mais dificil e nem perguntou para mim?" · "nova regra, sempre se deve se ver se é a coisa mais simples, ou melhor de se fazer, tem vezes que o mais simples é melhor e tem vezes que o mais complicado é melhor"
  Na prática: Regra de trabalho: antes de fazer (ou aceitar o plano de um agente), comparar o jeito mais simples com os outros e escolher o melhor para aquele caso, dizendo por quê; às vezes o mais simples é o melhor, às vezes o mais complicado. (Leitura da gerente, dita a ele: "Quando a escolha muda alguma coisa para você, eu pergunto".) Quando há mais de um caminho e eles mudam de verdade o trabalho, o risco ou o que ele vê, a gerente leva as opções a ele (a mais simples junto, com o que cada uma ganha e perde), e não decide sozinha como "detalhe técnico" (D-014 não cobre isso). Vale para a gerente e para todos os agentes: o plano do agente (D-709) traz o jeito mais simples e por que escolheu outro, se [...]
- **D-824** (21/11/2026): Chat (conversa nova, depois do checkpoint da noite). A gerente: "Hoje a gente já consegue mandar atualizações para o Kaique?" → não (o atualizador de 16/11 deu 4 defeitos: o "Reiniciar agora" não volta; o "Não" do Windows vira "deu certo"; a pergunta do Windows só pisca com o programa atrás; o publicar novo manda a atualização sem o motor do Kraken e o atualizador antigo espera o motor dentro dela). Ele: "mas basicamente ele já funciona?" · "não tem alguns desses que já tinhamos resolvido como o numero 3?" · "Se fizer esses 4 consertos, vamos conseguir mandar atualizações para o kaique?" · sobre tirar a janela da senha dos testes da primeira abertura: "esse item pode continuar lá, a gente troca ou tira nas proximas atualizações é só um detalhe" · à pergunta "Fica assim: os 4 consertos, e o Kaique clica em 'Agora não'?": "Sim, mas como vai ser feito esses 4 consertos, preciso que isso seja feito de forma rapida" · ao jeito de fazer (um agente, plano curto antes conferido pela gerente, testes no GitHub, um agente novo tenta quebrar, só grave ou médio volta, no máximo duas voltas, uma sessão de ~2 h na tela dele) e à oferta de dois agentes: "vamos fazer com um só, uma coisa de cade vez."
  Na prática: Entrega ao Kaique em duas vezes (proposta dele de 21/11, à tarde: "teriamos como entrar só o exe que eu posso atualizar e depois entregar em uma atulização futura só a parte de eu poder fazer testes a distancia?"). Primeira entrega: o programa que se atualiza, com só os 4 consertos acima (o pedido de licença do atualizador passa a usar a peça única do Windows, pedido no clique; o "Reiniciar agora" volta; o motor do Kraken continua no lugar dele depois da atualização). A janela da senha dos testes à distância continua na primeira abertura, e o Kaique clica "Agora não" (vai na lista da instalação). Ficam para atualizações depois: a pergunta "Atualizar agora?" ao fechar com o ícone, a [...]

## 4. O formulário da entrega (no seu ONDE-PAREI; um programa confere, campo vazio volta)

Use estes títulos de seção, exatamente assim. "Não se aplica" só vale com o motivo ("não se aplica: este passo não pede licença ao Windows"). Nas decisões, as palavras do Samuel vêm entre aspas logo depois do número, copiadas do Livro; o seu comentário vem depois de "Aqui:". Confira antes de entregar: `python -m regras_dos_agentes entrega relatorios/<pasta>/ONDE-PAREI.md --etapa quebrar`.

## Decisões que esta tarefa precisa cumprir

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que já está escolhido e testado aqui

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Como fica para quem usa e no livro

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## A causa, a regra e todos os caminhos

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que pode falhar e o que o programa faz

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Cada proteção e o teste que falha sem ela

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## De onde vem cada dado que a conferência usa

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que li da peça de fora e onde

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que foi feito

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Arquivos criados ou alterados

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Como cumpri cada uma

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Testes

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Caminho e função

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Máquina ou olho

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Ressalvas

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Velocidade

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Ideias e bugs

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Perguntas para o Samuel

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Decisões procuradas antes de cada pergunta

(a preencher; obrigatório antes de ir ao agente que tenta quebrar, se houver pergunta para o Samuel: um "###" por pergunta, com o mesmo título, as decisões do Livro procuradas e "Por que ainda não está respondida: ...")

## Commit

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que o agente que tentou quebrar achou

(a preencher; obrigatório antes da prova à vista)

## A prova de verdade

(a preencher; obrigatório antes do rótulo de pronto para conferir)

## Perguntas do Windows que o Samuel vê

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O print que prova

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Páginas em que foi conferido

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## 5. O que você não recebeu, e quando parar

Este pacote não traz as regras de: perguntas e relatórios ao Samuel, pesquisa de peça de fora. Se precisar mexer num arquivo fora da lista do pedido, pare e avise a gerente: o pacote muda. Se tiver pergunta para o Samuel, a regra 8 acima é o mínimo; a lista inteira está no CLAUDE.md §11.13, e a gerente devolve a pergunta que não passar. O texto que vale é o do CLAUDE.md (nas regras novas do catálogo dos erros, ainda não escritas lá, a decisão do Livro): a fonte de cada regra está entre parênteses; leia lá quando tiver dúvida.
