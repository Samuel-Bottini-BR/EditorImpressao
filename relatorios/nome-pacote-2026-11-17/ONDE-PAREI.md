# ONDE PAREI — o nome interno do pacote deixa de ser o da pasta dos projetos (implementador, 17/11/2026)

Cópia `.claude/worktrees/nome-pacote`, ramo `nome-pacote-2026-11-17`, a partir de `59678e22` (obra-2026-10-26).
Conserto autorizado pelo Samuel: "ok, pode fazer" (17/11/2026, D-763).

## Situação
**ENTREGUE à gerente, com uma pergunta para o Samuel** (um teste antigo, ver "Perguntas para o Samuel"). O teste
antigo **não** foi mudado. O relatório está em `relatorio.md/.html/.pdf` nesta pasta.

## Decisões que esta tarefa precisa cumprir (do Livro, com as palavras dele)
- **D-763** "ok, pode fazer": o nome interno do pacote do Velopack deixa de ser igual ao nome da pasta dos projetos
  (`%LOCALAPPDATA%\EditorImpressao`), antes da primeira instalação de verdade. Troca num lugar só
  (`versao.ID_DO_PACOTE`), que todo o resto lê; o Kaique continua vendo "Editor de Impressão". Uma prova cobra que o
  nome do pacote nunca é o da pasta dos projetos, e a prova da pasta de reserva e do desinstalar é repetida com o nome
  novo. O nome novo exato é detalhe técnico (D-014).
- **D-723** "velopack": a atualização usa o Velopack; instala em Arquivos de Programas, pede administrador.
- **D-724** "gratis, mas o que é essa assinatura e é segura?": só entra versão com a assinatura do Samuel.
- **D-727** "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né": tudo dentro do
  instalador.
- **D-731** "ok": desinstalar tira o que os testes à distância puseram; "Os projetos do Kaique
  (`%LOCALAPPDATA%\EditorImpressao`) continuam lá, como sempre (CLAUDE.md §7)".
- **D-732** "não, faz quando o programa é aberto": procurar a versão nova ao abrir.
- **D-733** "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?": Arquivos de Programas, ajudante como o sistema,
  janela sem administrador.
- **D-740** "Sim": os 3 testes antigos de `test_decisoes_atualizacao.py` cobram o jeito novo.
- **D-750** "pode sim, mas qual seria o problema de fazer o teste com um real?": desinstalar apaga a pasta vazia
  "EditorImpressao" do Agendador.
- **D-751** "sim": o teste da chave privada confere o lugar como num Windows comum.
- CLAUDE.md §7 (desinstalar não apaga `%LOCALAPPDATA%\EditorImpressao`), §11.8 (nunca mudar teste antigo para ele
  passar), §11.12 (uma regra, um lugar só).

## O plano (escrito antes de mexer) e o que mudou depois
**Por que acontece.** O Velopack usa `LocalAppData\<nome do pacote>` como pasta de reserva quando a pasta do programa
não aceita gravação, e o desinstalador do `.msi` apaga uma pasta `LocalAppData\<...>` inteira. O nosso nome
(`versao.ID_DO_PACOTE`) era `EditorImpressao`, igual ao da pasta dos dados (`historico.pasta_de_dados`), por acaso.

**Achado no meio (prova repetida, caso A e C2):** no `.msi` do vpk 1.2.161 a limpeza do desinstalador recebe o
**título** do pacote, não o nome (`RustAppId = {{AppTitle}}` no modelo do WiX). Na prova de 17/11 o título era igual
ao nome, por isso pareceu ser o nome. Com o título de verdade ("Editor de Impressão"), o desinstalador apaga
`%LOCALAPPDATA%\Editor de Impressão` e `%TEMP%\velopack_Editor de Impressão`. A regra ficou: **nem o nome nem o
título do pacote são o nome da pasta dos dados**. O título não mudou (ele já era diferente); a prova nova cobra os dois.

**O que mudou (commits `13e897d7`, `2f77ab69` e o desta entrega):**
1. `versao.py`: `ID_DO_PACOTE = "EditorImpressaoPrograma"`, e o comentário (a regra, por que agora pode trocar e por que
   nunca mais depois da primeira instalação).
2. `atualizacao.py`: a frase do topo "Os projetos do Kaique nunca sao tocados" virou a verdade (onde o Velopack grava,
   o que o desinstalador apaga, por que nome e título são outros). Só comentário.
3. `empacotar.py`: `VERSAO_DO_VPK = "1.2.161"` e `COMO_INSTALAR_O_VPK` (o "instale com" de `empacotar.py` e de
   `publicar_versao_kaique.py` diz `--version 1.2.161`), com o aviso de repetir a prova antes de subir.
   `requirements.txt`: `velopack==1.2.161` já estava preso; ganhou o mesmo aviso.
4. Comentários que citavam `EditorImpressao-<versao>...` (`assinatura.py`, `empacotar.nupkg_inteiro`,
   `publicar_versao_kaique.py`) passam a citar `<versao.ID_DO_PACOTE>-<versao>...`.
5. `tests/test_nome_do_pacote.py` (novo, 5 testes).

## Caminho → de onde lê o nome do pacote (busca `grep ID_DO_PACOTE|packId|"EditorImpressao"`)
- `empacotar.comando_do_vpk` (`--packId`) → `versao.ID_DO_PACOTE`.
- `empacotar.nupkg_inteiro` (o nome do `.nupkg`) → `versao.ID_DO_PACOTE`.
- `publicar_versao_kaique.assinar_pacote` (a assinatura e o nome do `.assinatura`) → `versao.ID_DO_PACOTE`.
- `publicar_versao_kaique.ja_publicada` → `versao.ID_DO_PACOTE`.
- `atualizacao.voltar_para_a_anterior` (o pacote da anterior e a assinatura dele) → `versao.ID_DO_PACOTE`.
- `atualizacao.conferir_assinatura_do` / `procurar_e_preparar` → o `PackageId` do pacote publicado (gravado pelo vpk a
  partir do `--packId`), nunca um nome escrito.
- `assinatura.py` → recebe o nome de quem chama.
- O programa instalado (pasta de reserva, chave `MSI:<nome>` no registro, log `velopack_<nome>.log`) → o nome gravado
  no pacote pelo `--packId`.
- O que o desinstalador do `.msi` 1.2.161 apaga e a pasta em Arquivos de Programas → o **título**
  (`empacotar.TITULO_DO_PACOTE`, `--packTitle`), não o nome.
- Ensaio da etapa 3 (`relatorios/frente-kaique-2026-11-16/etapa3/ensaio_velopack.py`) → lê `versao.ID_DO_PACOTE` e
  troca por `EditorImpressaoEnsaio` só no ensaio.
- **Nenhum lugar do programa tem o nome escrito à mão.** Os `"EditorImpressao"` que sobram são outra coisa: a pasta dos
  dados (`historico.py`), o `.exe` (`empacotar.NOME`), a pasta das tarefas do Windows
  (`core/testes_a_distancia.PASTA_DAS_TAREFAS`, `atualizacao.NOME_DA_TAREFA`), as marcas de "programa aberto", a pasta
  do ProgramData, o endereço do GitHub.
- **Teste antigo com o nome escrito à mão:** `tests/test_decisoes_atualizacao.py:448`
  (`test_d724_o_que_o_publicar_assina_o_programa_aceita`, de 16/11, commit `3e0e8893`):
  `assert arquivo.name == "EditorImpressao-1.2.0.assinatura"`. Falha com o nome novo. **Não mudado** (pergunta abaixo).
  Os outros `"EditorImpressao"` dos testes são dados de exemplo que não dependem do nome do pacote e passam.

## O que já está escolhido e testado aqui
- D-723, D-724, D-731, D-732, D-733, D-740, D-750, D-751 (acima): nenhuma mudou.
- Testes (PC, um por vez, código novo): `test_decisoes_atualizacao` 37 passaram e 1 falhou (o da pergunta);
  `test_assinatura` 16; `test_decisoes_desinstalar` 46; `test_decisoes_desinstalar_pasta` 6;
  `test_decisoes_ajudante_da_atualizacao` 37; `test_decisoes_preparo_d749` 8; `test_decisoes_testes_a_distancia` 13;
  `test_empacotar` 41; `test_sem_janela_na_tela` 8; `test_nome_do_pacote` 5 (`provas/testes-no-pc.txt`).

## Como fica para quem usa e no livro
- **O Kaique não vê diferença.** A pasta em Arquivos de Programas ("Editor de Impressão"), o nome na lista de programas
  ("Editor de Impressão") e os atalhos vêm do título, que não muda (lido no `.msi` montado pelo mesmo comando do
  programa: `provas/msi-com-o-titulo-de-verdade.txt`). A tarefa ajudante continua `EditorImpressao\Procurar versao nova`.
  Os projetos continuam em `%LOCALAPPDATA%\EditorImpressao`.
- **O que muda sem ele ver:** a pasta de reserva do Velopack passa a ser `%LOCALAPPDATA%\EditorImpressaoPrograma`
  (fora da pasta dos projetos); os arquivos publicados passam a se chamar `EditorImpressaoPrograma-<versão>-full.nupkg`
  e `EditorImpressaoPrograma-<versão>.assinatura`.
- **No PDF:** nada muda.

## Feito
- [x] Worktree, ramo, ONDE-PAREI (`991d8784`).
- [x] Prova nova: falha no código antigo (4 de 5; o do `--packId` passa nos dois, é a trava do "um lugar só") e passa no
      novo (5 de 5) (`provas/prova-nova-no-codigo-antigo.txt`, `provas/prova-nova-no-codigo-novo.txt`).
- [x] Código e comentários (`13e897d7`).
- [x] Prova de 17/11 repetida sem administrador (`provas/fotos/`, `provas/comandos.txt`, `provas/trechos-do-msi.txt`,
      `provas/registro-do-app.txt`, `provas/montar_e_provar.py`, `provas/ProvaNome.py`) (`2f77ab69`).
- [x] Leitura do `.msi` com o título de verdade (sem instalar).
- [x] Testes no PC, um por vez.
- [x] GitHub, 1ª rodada (44190676442, código de `13e897d7`): só a parte 3 falhou, com o teste antigo da pergunta.
- [x] Relatório nos três formatos.
- [x] GitHub, rodada final (44193535388, `b076169e`): só a parte 3 falhou, com o mesmo teste antigo da pergunta.

## Sobras fora do projeto (criadas por esta tarefa)
- `D:\agente_temp_testes\nome-pacote\` (~185 MB): o programa de mentira, os pacotes, os registros do `.msi`, as fotos.
  Deixado para o verificador repetir; pode ser apagado inteiro.
- Apagados por mim: `C:\Users\fotog\AppData\Local\EditorImpressaoProva` e `...\EditorImpressaoProgramaProva` (a pasta
  dos dados de mentira e a de reserva de mentira); a worktree destacada `D:\agente_temp_testes\nome-pacote\antigo`
  (`git worktree remove`); as pastas temporárias do pytest.
- Tirados pelo próprio desinstalador: as duas instalações de teste, `...\Local\Prova do nome do pacote`,
  `%TEMP%\velopack_Prova do nome do pacote` e a entrada nos programas instalados (conferido no registro).
- `D:\Config.Msi` (do sistema, já existia de 17/11): o Windows Installer de novo deu o erro 1926 nela ao desinstalar.
  Não mexi.
- `%TEMP%\velopack` (vazia, de 16/11, não é minha): a data mudou, não mexi.

## Perguntas para o Samuel (formato do CLAUDE.md §11.13)
**Do que se trata:** é a troca do nome interno da peça que atualiza o programa no notebook do Kaique, que você mandou
fazer hoje ("ok, pode fazer"). Esse nome também vai no nome de um arquivo pequeno que acompanha cada versão nova, a
"assinatura" que prova que a versão é sua. Com o nome novo, o arquivo passa de `EditorImpressao-1.2.0.assinatura` para
`EditorImpressaoPrograma-1.2.0.assinatura`.

**O que acontece hoje:** um teste antigo, de 16/11, confere esse nome escrito à mão, com o nome antigo. Por isso ele
acusa erro. **Não é defeito do programa:** é efeito da troca de nome. O mesmo teste continua mostrando que o programa
aceita a versão assinada.

**O que você escolhe:** posso mudar esse teste antigo para conferir o nome novo, lido do mesmo lugar que o programa usa?
- **Sim (sugiro):** o teste continua cobrando o mesmo (a versão assinada é aceita e o arquivo tem o nome certo). Nada
  que o Kaique vê muda.
- **Não:** o nome interno não pode trocar, e a peça de atualização continua usando a pasta dos projetos do Kaique.
- **Só comentário.**

**Situação:** feito na cópia de teste, esperando este "sim" para juntar à versão de teste (a etapa 5 espera este conserto).
