# Pacote de regras: Passo 2 do plano da parte do Windows, volta 8: os 2 defeitos da prova à vista (as peças procuradas no lugar errado numa cópia; a frase depois de apagar) e os 6 baixos do relatório 7

Papel: **implementador**. Tipo de trabalho (sai dos arquivos): git e arquivos, imagem, filtros e processamento do livro, testes, Windows e instalador (e qualquer conversa com programa de fora).


Copie as duas seções abaixo, sem mudar nada, para o começo do seu ONDE-PAREI: o porteiro lê dali quais arquivos você pode mexer, e a gerente compara com este pacote.

## Pedido

- Papel: implementador
- Commit de partida: 21f1fc50
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `publicar_versao_kaique.py`
- `empacotar.py`
- `montar_motor_kraken.py`
- `compilar_detector_gravura.py`
- `core/ocr_kraken.py`
- `core/windows.py`
- `atualizacao.py`
- `tests/test_windows_peca.py`
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py`
- `tests/test_motor_kraken*.py`
- `tests/test_ocr_kraken*.py`
- `relatorios/passo2-publicar/`

## Lugares da lista de exceções nos seus arquivos

40 lugares. Cada um é identificado pela função e pelo texto da linha: mexer numa dessas linhas sem consertá-la, ou renomear ou mover a função onde ela está, vira erro novo (e nenhum item entra na lista por ramo de agente). Quem conserta tira o item no mesmo commit (`python -m regras_dos_agentes excecoes --diminuir`).

**Não renomeie nem mova estas funções neste trabalho (passo 2): elas guardam lugares de outros passos, e o lugar é a função e o texto.**

- `atualizacao.py`, função `_aplicar_pacote_quando_sair` (lugares do passo 3)
- `atualizacao.py`, função `_dono_do_arquivo` (lugares do passo 3)
- `atualizacao.py`, função `_lancar_escondido` (lugares do passo 3)
- `atualizacao.py`, função `_ler_chave_do_inno` (lugares do passo 3)
- `atualizacao.py`, função `_ler_versao_do_visual_c` (lugares do passo 3)
- `atualizacao.py`, função `_linhas_da_janelinha` (lugares do passo 3)
- `atualizacao.py`, função `_marca_existe` (lugares do passo 3)
- `atualizacao.py`, função `ao_desinstalar` (lugares do passo 5)
- `atualizacao.py`, função `apagar_tarefa` (lugares do passo 3)
- `atualizacao.py`, função `comando_de_rodar_a_tarefa` (lugares do passo 3)
- `atualizacao.py`, função `criar_as_tarefas` (lugares do passo 5)
- `atualizacao.py`, função `criar_tarefa` (lugares do passo 3)
- `atualizacao.py`, função `marcar_programa_aberto` (lugares do passo 3)
- `atualizacao.py`, função `passo_de_preparar_o_computador` (lugares do passo 3)
- `atualizacao.py`, função `preparar_na_primeira_abertura` (lugares do passo 3)
- `atualizacao.py`, função `script_de_trocar_e_reabrir` (lugares do passo 3)
- `atualizacao.py`, função `update_exe` (lugares do passo 3)

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
5. **Leia a peça de fora antes de usar.** Antes de usar uma peça que não é nossa (biblioteca, função do Windows, PowerShell, Velopack, Qt), leia a documentação e, se não bastar, o código. Anote o que ela faz em cada caso que usamos, com a fonte. Separe o lido do deduzido. *Por quê:* Na etapa 5 o atualizador foi escrito sem ler o Velopack nem o Windows (§11.12.6).
6. **Decisões do Livro: cumprir e provar cada uma.** As decisões que o pedido traz (número e palavras dele) vão no começo do ONDE-PAREI; na entrega, como cumpriu cada uma, com teste ou print. Aparência não é prova. Palavras dele sempre copiadas do Livro, nunca de memória. *Por quê:* As decisões se perdiam entre o pedido e o código (§11.3 e §11.4).
7. **Pense em quem usa e no livro que sai.** Antes de mexer, escreva o que o Kaique vê e faz, passo a passo, antes e depois, e o que muda no PDF. Na entrega, confira. *Por quê:* Regra do Samuel para todo agente (D-637).
8. **Pergunta ao Samuel: no ONDE-PAREI, na hora, no jeito dele.** Pergunta vai na seção 'Perguntas para o Samuel' do ONDE-PAREI assim que surge. Começa pelo que é e onde fica, sem palavra de dentro (número, arquivo, etapa), com print do caso real e 'O que você escolhe', com a sua sugestão. Você nunca grava na Central. *Por quê:* 106 perguntas voltaram com 'Ainda não entendi' (§11.13); 8 perguntas ficaram escondidas num ONDE-PAREI (22/10).
9. **Seu ramo, commit a cada passo, nada se apaga fora.** Trabalhe só na sua cópia e no seu ramo; commit e push a cada passo, com o ONDE-PAREI em dia. Fora de D:\programas\EditorImpressao nada se apaga; dentro, só o que você criou. Junção nunca com rm -rf. Acervo só para ler. *Por quê:* O limite da conta já derrubou agentes; em 29/09 um agente apagou D:\d inteira.
10. **Não abra agente, não use a tela dele, entregue à gerente.** Não abra outros agentes. Não abra janela nem pergunta do Windows na tela do Samuel, e não feche processo que não é seu, a não ser numa prova que a gerente combinou com ele. Entregue sempre à gerente. *Por quê:* Cinco agentes rodando sem ele saber (10/11); caixas abertas na tela dele (30/09, 23/10).

## 2. As regras do seu trabalho (53)

**Windows e instalador (e qualquer conversa com programa de fora)**
- A janela nunca congela: Todo trabalho demorado em QThread, com barra e cancelar que funciona; esperar o Windows também (na etapa 5 a janela ficou parada 14 min). (CLAUDE.md §3)
- Texto com acento, caminho sem acento: Texto de tela com acento (UTF-8); caminho de disco sem acento. (CLAUDE.md §3)
- core/ não importa ui/: core/ nunca importa ui/: o processamento roda por linha de comando, sem janela. (CLAUDE.md §7)
- Onde o programa guarda estado: %LOCALAPPDATA%\EditorImpressao guarda projetos e histórico; fechar e reabrir preserva tudo; desinstalar NÃO apaga essa pasta. (CLAUDE.md §7)
- Uma peça só para conversar com o que está fora: Windows, disco, rede, GitHub, Velopack, outro programa: uma peça só para cada conversa; ninguém escreve a sua versão (na etapa 5, cada função pedia licença do seu jeito). (CLAUDE.md §11.12.1)
- Antes de escrever, a lista das falhas: No ONDE-PAREI, para cada coisa que pode dar errado (sem licença, sem internet, disco cheio, 'Não', arquivo preso, desligar no meio), o que o programa faz; nunca pela metade. (CLAUDE.md §11.12.3)
- Peça de mentira não prova (D-767): Teste com peça de mentira só prova a lógica em volta. O que mexe no Windows só conta rodando de verdade, à vista, e funcionando. Nada em área escondida. (CLAUDE.md §11.12.4) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-785): à vista o que mexe com o Windows (a lista da D-785); escondidos os testes que não dependem dele.**

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
- Modelo de dados em dois níveis: ConfigFolha (o que veio) e ConfigPagina (o que sai); ajustes de cada filtro separados; recorte e ângulo na página. (CLAUDE.md §7)
- Desempenho já resolvido, não refazer: Análise a 150 DPI e fundo estimado em miniatura de ~400 px: não refazer. (CLAUDE.md §7)
- Ordem obrigatória do processamento: Livro novo: dividir → endireitar → cortar → filtro → cadernos. Projeto de antes de 09/10 sem ordem_do_preparo: a ordem antiga, idêntica. (CLAUDE.md §7)
- Queixas do Kaique são requisito: Os .txt com print em 'Teste de livros' são fonte de requisito. (CLAUDE.md §7)
- Régua e velocidade; nada mais lento: Rodar a régua e o teste de velocidade; piorou, reverter ou apresentar os dois. Nenhum item deixa o programa mais lento. (CLAUDE.md §8 passo 5) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-786): vale a regra de 19/10: velocidade no GitHub a cada mudança; no PC, no fim da fase.**
- Mancha do verso: o defeito mais grave: O Preto e branco escurece a mancha do verso; a régua não pega. Caminho recomendado: espelhar o verso e subtrair. (CLAUDE.md §9)
- A régua precisa de critérios novos: Comparar onde havia mancha, olhar a moldura, medir sujeira guardada. (CLAUDE.md §9)
- Amarelado está na tinta: A tinta de 1579 é marrom; cuidado: rubricação desbotada também é marrom. (CLAUDE.md §9)
- Não há binarizador vencedor: Os 18 do DoxaPy se invertem de livro para livro. (CLAUDE.md §9)
- Não desfazer a correção do 'magic color': Dividir pelo fundo relativo ao papel, ganho igual nos três canais, curva de ombro no L: não desfazer (a receita comum estraga capa colorida). (CLAUDE.md §9)
- Scan de baixa resolução não se recupera: O remédio é reescanear; é o único lugar onde 'até ficar perfeito' não vale. (CLAUDE.md §9)
- Toda função automática tem ligar e desligar: Toda função automática tem botão de ligar e desligar (regra 8 do plano). (layout.md 'Regras de tela')

**Testes**
- Teste de máquina: o agente decide: O que tem resposta objetiva (fecha? páginas certas? memória? PDF estragado? cadernos? acento?) roda a cada mudança, sozinho. (CLAUDE.md §4.1)
- Máquina ou olho, item por item: Todo item diz se foi conferido por máquina ou por olho. (CLAUDE.md §4.3)
- Onde roda cada teste: No PC, um arquivo de teste por vez; a suíte inteira e o teste_botoes no GitHub (push antes); a entrega traz o número da rodada. (CLAUDE.md §4.6) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-787): vale a regra de 19/10: no PC, um arquivo de teste por vez; o conjunto inteiro no GitHub.**
- Teste de reversão em todo conserto: Todo bug consertado ganha teste que FALHA no código antigo e passa no novo, com o bug na docstring; o verificador prova no antigo. Bug de imagem: uma medida, ou ressalva escrita. (CLAUDE.md §4.7)
- Prova: caminho → função e o mesmo resultado em todos: Na entrega, a lista 'caminho → função' e uma prova em tests/ que cobra o mesmo resultado por todos os caminhos. (CLAUDE.md §11.12)
- Teste escrito antes do código, quando der: Teste automático do que é objetivo, escrito antes do código quando der. (implementador.md 'O que você faz')

**Git e arquivos**
- Handoff só com pedido do Samuel: Só atualizar o handoff de historico/ quando o Samuel pedir. (CLAUDE.md §7)
- Commit na hora com o defeito por extenso; nunca segredo: Commit com o defeito resolvido escrito por extenso e push; revisar o que vai no commit; nunca segredo; nunca desfazer o .gitignore sem avisar. (CLAUDE.md §8 passo 10)
- Cada papel no seu lugar: Implementador: core/ e scripts, não ui/ (salvo pedido). Layout: só ui/. Verificador e pesquisador: não mexem no código do programa. (CLAUDE.md §10.1) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-796): o agente de tela mexe em core/ só nos arquivos que o pedido nomear; sem isso, só ui/.**

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

- **D-605** (03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes precisam ler"
  Na prática: Nenhuma coisa nova (função ou escolha nova) muda o que já está escolhido e testado, nem cria problema novo. Antes de mexer, o agente lista o que já está escolhido e testado ali; se a coisa nova mudaria isso, para e pergunta; teste antigo que quebra faz a entrega voltar (nunca se muda o teste antigo para passar); o verificador confere também o que já funcionava ao redor.
- **D-727** (16/11/2026): Chat, à pergunta "Posso instalar o .NET no seu PC para a etapa 3 começar?": "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né"
  Na prática: Tudo o que o programa precisa para funcionar no notebook do Kaique vai dentro do instalador; nada é baixado da internet na hora de instalar. Ex.: o Visual C++ continua dentro do instalador (o estudo previa baixá-lo com o Velopack: substituído). O .NET (só o empacotador usa, no PC do Samuel) foi instalado em 16/11 (SDK 8.0.428, winget).
- **D-767** (18/11/2026): Chat, na etapa 5, depois dos 7 defeitos achados no Windows de verdade (a gerente explicou que os testes automáticos trocam as peças do Windows por peças de mentira): "não faça mais nada escodindo ou de mentira" · logo depois: "não quero fazer consertos quero que funcione" · e: "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do atualizador e testes a distancias"
  Na prática: O que mexe no Windows (pergunta de administrador, PowerShell, tarefas, licenças de pasta, instalar e desinstalar, testes à distância) só conta como pronto quando roda de verdade no Windows, à vista, e funciona. Teste automático com peça de mentira não prova que funciona. Nada de área de trabalho escondida nos testes. O objetivo não é remendar cada defeito, é a parte do Windows funcionar inteira (CLAUDE.md §11.12). O alcance exato (por exemplo, as versões de teste servidas de uma pasta do D: em vez do GitHub) está sendo confirmado com o Samuel.
- **D-773** (18/11/2026): Chat, decisão 6 do plano da parte do Windows ("de onde vêm as versões nas provas"; A = versões de verdade servidas por uma janela visível no PC do Samuel, mais uma versão de teste no GitHub como rascunho, liberada só na prova e apagada no fim, sugestão; B = tudo pelo GitHub; C = sem GitHub): "A"
  Na prática: Nas provas, as versões são versões de verdade do programa, baixadas pela rede de verdade de uma janela pequena e visível no PC do Samuel que faz o papel do GitHub (fechar a janela prova a internet caindo no meio). Para provar o publicar, uma versão de teste vai ao GitHub como rascunho, é liberada só durante a prova e apagada no fim (ninguém tem o programa instalado). Define o alcance da D-767 para as versões de prova; ajusta a D-713 (nada no GitHub nesta etapa) só para esse rascunho de prova.
- **D-776** (18/11/2026): Chat, decisão 8 do plano da parte do Windows ("montar a versão no disco de dentro do PC"; A = no C:, sugestão; B = continua no D:): "Sim, no C só tem que cuidar para não encher o disco C inteiro"
  Na prática: Publicar monta a versão no C: (o disco de dentro, muito mais rápido que o HD externo), com cuidado para nunca encher o C:: antes de começar, o publicar confere o espaço e não começa se, somando o que vai usar (6 a 10 GB), o C: ficaria com menos de 20 GB livres (Samuel, 18/11, à pergunta "Fica 20 GB?", depois de a gerente explicar as atualizações do Windows e a memória virtual: "ok"; a sugestão de 15 GB foi trocada por 20 GB a pedido dele: "acha que isso é suficiente?"); ele vigia o espaço durante o trabalho e para com aviso se cair perto da reserva; e o rascunho é apagado no fim, também quando dá erro. O Kaique recebe exatamente a mesma atualização.
- **D-777** (18/11/2026): Chat, decisão 9 do plano da parte do Windows ("o instalador só quando você pedir"; a gerente explicou com o exemplo 1.1 = atualização e instalador, 1.2 e 1.3 = só a atualização, instalador da 1.3 quando ele pedir): "mas dai vai fazer quais versões?" · "ok, fica assim"
  Na prática: Toda versão nova sai só com a atualização; o instalador (.msi) sai na primeira entrega ao Kaique e sempre que o Samuel pedir (computador novo, notebook formatado), já com a versão mais nova do dia; o zip portátil deixa de sair. O Kaique recebe todas as versões do mesmo jeito. (A ferramenta de atualização sempre faz também um Setup.exe pequeno, em 2 s; ele continua saindo.)
- **D-788** (18/11/2026): Chat, pergunta 1 de 3 do estudo do Kraken separado ("onde o motor fica no notebook do Kaique"; A = pasta própria dentro da pasta do programa, sugestão; B = um segundo programa só para o motor): "1" (a primeira opção)
  Na prática: O motor do Kraken mora numa pasta própria dentro da pasta do programa, `C:\Program Files\EditorImpressaoPrograma\motor-kraken\<versão>`, ao lado da parte que o Velopack troca: a atualização não toca nela, o desinstalar a tira junto, e na primeira instalação ele vem dentro do instalador (nada baixado na hora, D-727). Quando o motor mudar, o ajudante baixa só o motor, conferido pela assinatura do Samuel, e a versão nova só entra depois que ele chegou inteiro. Completa a D-768. Estudo no ramo `kraken-separado-2026-11-18`.
- **D-789** (18/11/2026): Chat, pergunta 2 de 3 do estudo do Kraken separado (a decisão 1 do plano da parte do Windows, reaberta pela D-768: "agora sem o motor, o Kaique baixa a versão inteira ou só o que mudou?"; A = inteira, ~460 MB, troca de 2 a 3 min, a assinatura confere tudo, sugestão; B = só a diferença): "mas iria demorar mais toda vez que eu fosse fazer a compilação né?" (a gerente: não, a A é mais rápida de montar, a B tem o passo a mais da diferença) · "A"
  Na prática: Cada atualização vai inteira (sem o motor do Kraken, que fica à parte pela D-768/D-788), sem o pacote de diferença: o Kaique baixa uns 460 MB, a troca leva uns 2 a 3 minutos, a assinatura do Samuel confere tudo o que é instalado (fecha a falha de segurança da diferença), e montar no PC do Samuel não tem o passo da diferença. Números de conta, a medir nas provas. Fecha a decisão 1 do plano.
- **D-795** (19/11/2026): Chat, ponto 1 do plano-v2 §6.3 (o Setup.exe que continua saindo, D-777, contra o motor sempre dentro do instalador, D-788/D-727). Ele: "porque fazer isso?" · "porque ter um instalador pequeno então?" · "não tem nenhuma documentação dizendo para o que isso serve?". A gerente corrigiu o "pequeno" (é rápido de fazer, 2 s, mas leva o pacote inteiro, ~826 MB, `relatorios/publicar-rapido-2026-11-18/relatorio.md`), explicou que é o instalador padrão do Velopack, que a 1.2.161 recusa `--noInst` com `--noPortable` (medido) e que usamos o .msi por instalar em Arquivos de Programas para todas as contas (`--msi --instLocation PerMachine`, `docs/pesquisa/atualizacao-e-testes-a-distancia.md`, ramo `estudo-kaique-2026-11-16`), e perguntou "Então ele vai continuar sendo feito, mas não precisa ir para o GitHub nem para o Kaique. Sugiro apagar no fim de cada publicação. Pode ser?": "ok"
  Na prática: O Setup.exe continua sendo feito pela ferramenta (ela não deixa tirar), mas não é publicado no GitHub nem mandado ao Kaique: o publicar o apaga no fim de cada publicação, também quando dá erro. O Kaique só recebe o .msi (primeira entrega e quando o Samuel pedir, D-777) e as atualizações. Responde o ponto 1 do plano-v2 §6.3; ajusta a D-777 ("ele continua saindo").
- **D-815**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)
- **D-816**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)
- **D-817**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)
- **D-818**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)

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

## Commit

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que o agente que tentou quebrar achou

(a preencher; obrigatório antes da prova à vista)

## A prova de verdade

(a preencher; obrigatório antes do rótulo de pronto para conferir)

## Perguntas do Windows que o Samuel vê

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Páginas em que foi conferido

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## 5. O que você não recebeu, e quando parar

Este pacote não traz as regras de: perguntas e relatórios ao Samuel, pesquisa de peça de fora, tela (ui/). Se precisar mexer num arquivo fora da lista do pedido, pare e avise a gerente: o pacote muda. Se tiver pergunta para o Samuel, a regra 8 acima é o mínimo; a lista inteira está no CLAUDE.md §11.13, e a gerente devolve a pergunta que não passar. O texto que vale é o do CLAUDE.md: a fonte de cada regra está entre parênteses; leia lá quando tiver dúvida.
