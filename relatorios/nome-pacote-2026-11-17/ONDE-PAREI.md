# ONDE PAREI — o nome interno do pacote deixa de ser o da pasta dos projetos (implementador, 17/11/2026)

Cópia `.claude/worktrees/nome-pacote`, ramo `nome-pacote-2026-11-17`, a partir de `59678e22` (obra-2026-10-26).
Conserto autorizado pelo Samuel: "ok, pode fazer" (17/11/2026, D-763).

## Decisões que esta tarefa precisa cumprir (do Livro, com as palavras dele)
- **D-763** "ok, pode fazer": o nome interno do pacote do Velopack deixa de ser igual ao nome da pasta dos projetos
  (`%LOCALAPPDATA%\EditorImpressao`), antes da primeira instalação de verdade. Troca num lugar só
  (`versao.ID_DO_PACOTE`), que todo o resto lê; o Kaique continua vendo "Editor de Impressão". Uma prova cobra que o
  nome do pacote nunca é o da pasta dos projetos, e a prova da pasta de reserva e do desinstalar é repetida com o nome
  novo. O nome novo exato é detalhe técnico (D-014).
- **D-723** "velopack": a atualização usa o Velopack; instala em Arquivos de Programas, pede administrador.
- **D-724** "gratis, mas o que é essa assinatura e é segura?": só entra versão com a assinatura do Samuel. Nesta tarefa
  a chave dele não é usada (a prova usa a chave de mentira de 17/11).
- **D-727** "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né": tudo dentro do
  instalador. Não tocada.
- **D-731** "ok": desinstalar tira o que os testes à distância puseram; "Os projetos do Kaique
  (`%LOCALAPPDATA%\EditorImpressao`) continuam lá, como sempre (CLAUDE.md §7)". **É esta promessa que o conserto faz
  valer também para o desinstalador do Velopack.**
- **D-732** "não, faz quando o programa é aberto": procurar a versão nova ao abrir. Não tocada.
- **D-733** "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?": programa em Arquivos de Programas, ajudante como o
  sistema, janela sem administrador. Não tocada (o nome da tarefa `EditorImpressao\Procurar versao nova` não muda).
- **D-740** "Sim": os 3 testes antigos de `test_decisoes_atualizacao.py` cobram o jeito novo. Não tocados.
- **D-750** "pode sim, mas qual seria o problema de fazer o teste com um real?": desinstalar apaga a pasta vazia
  "EditorImpressao" do Agendador. Não tocada (é o nome da pasta das tarefas, não o do pacote).
- **D-751** "sim": o teste da chave privada confere o lugar como num Windows comum. Não tocado.
- CLAUDE.md §7: desinstalar **não apaga** `%LOCALAPPDATA%\EditorImpressao`, de propósito.
- CLAUDE.md §11.8 (D-605): nunca mudar teste antigo para ele passar; se precisar, parar e perguntar.
- CLAUDE.md §11.12: uma regra, um lugar só.
- Regras do pedido: nenhuma pergunta do Windows; nenhuma janela na tela do Samuel; não abrir agentes; nunca gravar,
  mudar ou apagar em `%LOCALAPPDATA%\EditorImpressao` (só olhar os nomes do primeiro nível).

## O plano (escrito antes de mexer)
**Por que acontece.** O Velopack usa `LocalAppData\<id do pacote>` para a pasta de reserva (quando a pasta do programa
não aceita gravação) e na limpeza do desinstalador do `.msi` (`CleanupDeferred`; na versão mais nova também
`UserCleanupDeferred`, que apaga a pasta inteira). O nosso id (`versao.ID_DO_PACOTE`) era `EditorImpressao`, igual ao
nome da pasta dos dados (`historico.pasta_de_dados`). Os dois nomes caíram iguais por acaso.

**A regra (um lugar só):** o nome do pacote nunca é o nome da pasta dos dados. Ela mora em `versao.ID_DO_PACOTE`, e a
prova nova em `tests/` cobra a regra contra `historico.pasta_de_dados()`.

**O que muda:**
1. `versao.py`: `ID_DO_PACOTE = "EditorImpressaoPrograma"` e o comentário (por que agora pode trocar e por que nunca
   mais depois da primeira instalação).
2. `atualizacao.py`: a frase do topo "Os projetos do Kaique nunca sao tocados" passa a dizer a verdade (onde o Velopack
   grava e por que o id é outro). Só comentário.
3. Prender as versões: `requirements.txt` já tem `velopack==1.2.161`; o comentário ganha o aviso de repetir a prova.
   O `vpk` passa a ter a versão escrita num lugar só (`empacotar.VERSAO_DO_VPK`) e o "instale com" diz
   `--version 1.2.161`.
4. `tests/test_nome_do_pacote.py` (novo): id ≠ nome da pasta dos dados (sem diferenciar maiúsculas), a pasta de reserva
   `LocalAppData\<id>` nunca é a dos dados nem fica dentro dela, `--packId` = `versao.ID_DO_PACOTE`, e o
   `requirements.txt` preso na mesma versão do `vpk`.

**As provas:** a nova no código antigo (falha) e no novo (passa); a prova de 17/11 repetida sem administrador com um
pacote de mentira cujo nome sai da mesma regra; os testes antigos um arquivo por vez; a rodada do GitHub.

## Caminho → de onde lê o nome do pacote (busca `grep ID_DO_PACOTE|packId|"EditorImpressao"`)
- `empacotar.comando_do_vpk` (`--packId`) → `versao.ID_DO_PACOTE`.
- `empacotar.nupkg_inteiro` (o nome do `.nupkg`) → `versao.ID_DO_PACOTE`.
- `publicar_versao_kaique.assinar_pacote` (a assinatura e o nome do arquivo `.assinatura`) → `versao.ID_DO_PACOTE`.
- `publicar_versao_kaique.ja_publicada` → `versao.ID_DO_PACOTE`.
- `atualizacao.voltar_para_a_anterior` (o pacote da versão anterior e a assinatura dele) → `versao.ID_DO_PACOTE`.
- `atualizacao.conferir_assinatura_do` / `procurar_e_preparar` → o `PackageId` do pacote publicado (que o vpk gravou a
  partir do `--packId`), não um nome escrito.
- `assinatura.py` → recebe o nome de quem chama (só o comentário cita `versao.ID_DO_PACOTE`).
- O programa instalado (pasta de reserva, limpeza do desinstalador) → o id gravado no pacote pelo `--packId`.
- Ensaio da etapa 3 (`relatorios/frente-kaique-2026-11-16/etapa3/ensaio_velopack.py`) → lê `versao.ID_DO_PACOTE` e
  troca por `EditorImpressaoEnsaio` só no ensaio.
- **Nenhum lugar do programa tem o id escrito à mão.** Os `"EditorImpressao"` que sobram são outra coisa: a pasta dos
  dados (`historico.py`), o nome do `.exe` (`empacotar.NOME`), a pasta das tarefas do Windows
  (`core/testes_a_distancia.PASTA_DAS_TAREFAS`, `atualizacao.NOME_DA_TAREFA`), as marcas de "programa aberto", a pasta
  do ProgramData, o endereço do GitHub.
- **Teste antigo com o id escrito à mão:** ver "Perguntas para o Samuel".

## O que já está escolhido e testado aqui
- D-723, D-724, D-731, D-732, D-733, D-740, D-750, D-751 (acima).
- Testes: `tests/test_decisoes_atualizacao.py`, `test_assinatura.py`, `test_decisoes_desinstalar.py`,
  `test_decisoes_desinstalar_pasta.py`, `test_decisoes_ajudante_da_atualizacao.py`, `test_decisoes_preparo_d749.py`,
  `test_decisoes_testes_a_distancia.py`, `test_empacotar.py`.

## Como fica para quem usa e no livro
- **O Kaique não vê diferença.** O nome da pasta em Arquivos de Programas, o nome na lista de programas do Windows e os
  atalhos vêm do título do pacote ("Editor de Impressão", `--packTitle`), que não muda. A tarefa ajudante continua
  `EditorImpressao\Procurar versao nova`. Os projetos continuam em `%LOCALAPPDATA%\EditorImpressao`.
- **O que muda, sem ele ver:** a pasta de reserva do Velopack passa a ser `%LOCALAPPDATA%\EditorImpressaoPrograma`
  (uma pasta só dela), e o desinstalador limpa essa pasta, nunca a dos projetos.
- **No PDF:** nada muda.

## Feito
- [x] Worktree e ramo; leitura do pedido inteiro.

## Perguntas para o Samuel
(nenhuma ainda)
