# ONDE PAREI — etapa 3 da frente do Kaique (a atualização sozinha, com o Velopack)

Agente implementador, 16/11/2026. Cópia `.claude/worktrees/kaique-etapa3`, ramo `kaique-etapa3-2026-11-16`
(feito do `obra-2026-10-26`, `9414405f`).

## Decisões que esta tarefa precisa cumprir (número + palavras do Samuel)

- **D-706** "a atualização via internet tem que ser como funciona com apps, não pode ser ele ter que baixar de novo um
  instalador fazer tudo de novo" · "as atualizaçõpes não podem estar ligadas via api".
- **D-713** "não precisa ser privado" (o GitHub do projeto continua público; as versões vêm dele).
- **D-714** "1 - vamos seguir sua sugestão" (versão para o Kaique publicada de propósito, nunca a cada salvamento) ·
  "e sim o programa pega sozinho, toda vez que o pc inicializar em segundo plano, assim como os nossos testes acontecem."
- **D-715** "ele dá um aviso se o programa estiver aberto, um aviso para salvar o trabalho atual e reinicializar o
  programa".
- **D-718** "Sim, e tem que avisar a gente de alguma maneira" (se falhar, volta para a versão anterior).
- **D-719** "1" — na tela: "A atualização não deu certo. O programa voltou para a versão anterior e continua
  funcionando. Avise o Samuel."; o erro num registro que a gerente lê daqui; nenhuma senha dentro do programa.
- **D-720** "Sim" — o aviso tem "Reiniciar agora" e "Depois"; com "Depois", entra na próxima vez que o computador ligar.
- **D-722** "Sim" — testar antes no PC do Samuel e desfazer no fim (isto é a etapa 5; aqui nada é instalado de verdade).
- **D-723** "velopack" — o Inno Setup sai, entra o Velopack (Arquivos de Programas, pede administrador); a tarefa do
  Windows aplica ao ligar; a instalação de 28/10 sai; os testes antigos do instalador só mudam com o "sim" dele.
- **D-724** "gratis, mas o que é essa assinatura e é segura?" — o PC do Samuel assina cada versão com uma chave só dele;
  o programa confere antes de instalar; a que não bater não é instalada. A chave nunca no GitHub, com cópia de reserva.
- **D-727** "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né" — nada baixado na
  hora de instalar (o Visual C++ continua dentro).
- **D-605** (regra §11.8): o novo não estraga o que já está escolhido e testado.

## O que já está escolhido e testado aqui

- `empacotar.py` + `instalador.iss` (Inno): as travas dos modelos, das duas DLLs do ScanTailor, do motor do Kraken, do
  Tesseract com 6 idiomas e do Visual C++ oficial (assinatura da Microsoft), e a limpeza que só apaga o que o script gera.
  Testes: `tests/test_empacotar.py` (todos), `tests/test_empacotar_teste_velocidade.py`, `tests/test_requirements.py`,
  `tests/test_ocr_diagnostico.py`, `tests/test_botoes_em_portugues.py` (varre `ui/` e `main.py`).
- `main.py`: `--servidor-de-paginas` e `--conferir-ocr` atendidos antes de qualquer janela; `sys.excepthook`.
- `historico.pasta_de_dados` (`%LOCALAPPDATA%\EditorImpressao`): os projetos do Kaique. Desinstalar não apaga (CLAUDE.md §7).
- `ui/perguntas.py`: caixas com botões escritos por nós.
- **Nada disso muda.** O `instalador.iss` só deixa de ter o número da versão escrito nele: passa a recebê-lo do
  `empacotar.py` (um lugar só). Todos os textos que os testes antigos conferem continuam lá.

## Como fica para quem usa e no livro (o Kaique, passo a passo)

1. **Primeira vez:** ele recebe um instalador novo e dá dois cliques. O Windows pergunta "Deseja permitir...?"; ele
   clica "Sim". O programa vai para Arquivos de Programas. A instalação velha (a de 28/10) sai sozinha; os livros e
   projetos dele (`%LOCALAPPDATA%\EditorImpressao`) ficam como estão. Tudo vem dentro do instalador (sem internet).
2. **Todo dia:** o computador liga; uns minutos depois, por trás, sem janela, o programa procura a "versão para o
   Kaique" no GitHub. Se houver e a assinatura conferir, baixa só o que mudou e troca. Ele não vê nada; da próxima
   vez que abrir, já é a nova.
3. **Se ele estiver com o programa aberto** quando a versão nova chega: aparece "Chegou uma versão nova do programa..."
   com "Reiniciar agora" e "Depois". "Reiniciar agora": o programa grava o trabalho, fecha e abre na versão nova (o
   Windows pode perguntar "Deseja permitir...?" uma vez). "Depois": nada muda agora; entra quando o computador ligar.
4. **Se der errado** (assinatura que não confere, troca que falha, versão nova que não abre): o programa fica (ou volta)
   na versão anterior e, na próxima vez que ele abrir, aparece uma vez: "A atualização não deu certo. O programa voltou
   para a versão anterior e continua funcionando. Avise o Samuel."
5. **No livro (PDF):** nada muda. Nenhum filtro, ferramenta ou tela de trabalho é tocado.

## O meu plano (o que vou fazer, onde, a regra num lugar só, como provo)

Por que assim: é o que o Samuel decidiu (D-714, D-723, D-724, D-727). O que é nosso é só a cola entre o Velopack e a
tarefa do Windows; a troca dos arquivos e a volta quando a troca falha são do próprio Velopack.

1. **`versao.py` (novo):** `VERSAO` — o único lugar do número. Usado por `empacotar.py` (Inno via `/DMinhaVersao=`,
   Velopack via `--packVersion`), pelo comando de publicar e pela atualização. Não há tela "Sobre": não crio nenhuma.
   A primeira versão do Velopack será a `1.1.0` (a de 28/10 do Kaique era a `1.0.0` do Inno).
2. **`assinatura.py` (novo):** Ed25519, o método da RFC 8032 (o mesmo do Mac, do minisign, do TUF), com o código de
   referência da própria RFC e os vetores de teste dela. Não há biblioteca de assinatura no `.venv` (`cryptography` não
   está instalada e só tenho licença para acrescentar o `velopack`). A chave pública do Samuel fica dentro do programa;
   a privada fora do repositório.
3. **`atualizacao.py` (novo; sem Qt):** a regra inteira num lugar só —
   `procurar_e_preparar` (confere a assinatura ANTES de baixar; baixa; se o programa está aberto, deixa "pendente";
   se fechado, pede ao Velopack para trocar e reabrir escondido em `--conferir-a-versao-nova`);
   `conferir_versao_nova` (teste rápido escondido; se falhar, volta para a anterior com o próprio `Update.exe` e um
   pacote assinado); `o_que_avisar` (o que a tela mostra); `registrar` (o registro em
   `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`, que a conta de testes lê); a tarefa do Windows
   (XML, criar, apagar); a marca de "programa aberto"; tirar a instalação do Inno; o Visual C++ de dentro do pacote.
   `atender_linha_de_comando(argv)` é a única entrada: `main.py` chama uma vez, antes de qualquer janela.
4. **`ui/aviso_de_atualizacao.py` (novo):** liga na janela (uma linha no `main.py`): a marca de aberto, um relógio que
   pergunta `atualizacao.o_que_avisar` e mostra o aviso com `ui.perguntas` ("Reiniciar agora" / "Depois") ou o aviso
   da falha (D-719, uma vez). Não toca nas Configurações nem na janela da senha (etapa 4).
5. **`empacotar.py`:** funções novas para o pacote do Velopack (põe o Visual C++ oficial dentro, monta o comando do
   `vpk pack --msi --instLocation PerMachine`, confere que o pacote leva modelos, DLLs, motor, Tesseract e Visual C++).
   A pasta continua sendo feita pela mesma `construir_pasta` (as mesmas travas). O Inno continua lá, sem mudar nada.
6. **`publicar_versao_kaique.py` (novo):** o comando de publicar de propósito: acha a chave (para se não houver),
   confere que a chave bate com a do programa, empacota, `vpk pack`, assina, confere a própria assinatura e publica no
   GitHub (`vpk upload github` + o arquivo da assinatura) ou numa pasta (o servidor de mentira). Token só no PC do
   Samuel, na hora (`gh auth token`), nunca no programa.
7. **Provas:** `tests/test_decisoes_atualizacao.py` (cada decisão) e `tests/test_assinatura.py` (vetores da RFC). E um
   ensaio de verdade: um programinha de mentira empacotado pelo PyInstaller e pelo Velopack (as mesmas funções), versão
   1 numa pasta de teste (pacote "portátil", sem instalar), versão 2 publicada numa pasta-servidor, a atualização
   de mentira 1 → 2, a assinatura errada recusada, e a volta.

**Regra num lugar só:** número da versão → `versao.VERSAO`; assinatura → `assinatura.conferir_versao`; "o que fazer
com a versão nova" → `atualizacao.procurar_e_preparar`; "o que a tela avisa" → `atualizacao.o_que_avisar`; falha →
`atualizacao.registrar_falha`; programa aberto → `atualizacao.ha_programa_aberto` / `marcar_programa_aberto`.

## Andamento (PARADO em 16/11/2026 a pedido da gerente: o Samuel vai desligar o PC)

- [x] plano (este arquivo) — `87e8c712`
- [x] `versao.py` (VERSAO = "1.1.0", ID_DO_PACOTE) + `instalador.iss` recebe a versão por `/DMinhaVersao=`
      (`empacotar.comando_do_inno`) — `16c838a7`
- [x] `assinatura.py` (Ed25519 da RFC 8032) + `tests/test_assinatura.py`: 16 passaram no PC (vetores da RFC certos).
- [x] Chave de verdade criada em `C:\Users\fotog\AppData\Roaming\EditorImpressao-publicar\chave-privada-da-assinatura.txt`
      (fora do repositório); a pública (`b2c4094c...f34a`) já está em `assinatura.CHAVE_PUBLICA_DO_SAMUEL`.
      A gerente precisa guardar a cópia de reserva no HD externo D: (eu não copiei).
- [x] `atualizacao.py` escrito (procurar_e_preparar, situacao, o_que_avisar, registrar_falha, voltar_para_a_anterior,
      XML da tarefa, Visual C++, tirar o Inno, ganchos do Velopack, atender_linha_de_comando). AINDA SEM TESTE, NUNCA RODADO.
- [x] `ui/aviso_de_atualizacao.py` + as duas chamadas no `main.py`. AINDA SEM TESTE.
- [x] `empacotar.py`: funções do Velopack (achar_vpk, preparar_pasta_para_o_velopack, comando_do_vpk,
      conferir_pacote_do_velopack, construir_pacote_do_velopack). Sem teste; nenhum modo novo no argparse.
- [x] `publicar_versao_kaique.py` (--criar-chave, --pasta, --pasta-pronta, --chave). Sem teste.
- [ ] PRÓXIMO PASSO 1: `requirements.txt` ganha `velopack==1.2.161` (já instalado no `.venv`; o `vpk` 1.2.161 já está
      em `%USERPROFILE%\.dotnet\tools`, precisa de `DOTNET_ROOT=C:\Program Files\dotnet`).
- [ ] PRÓXIMO PASSO 2: `tests/test_decisoes_atualizacao.py` com gerente falso (sem velopack): versão num lugar só;
      assinatura errada recusada ANTES de baixar; programa aberto → "pendente" e aviso com os dois botões; "Depois" não
      troca; falha → FRASE_DA_FALHA uma vez + registro em PROGRAMDATA (monkeypatch); volta com pacote assinado; nenhum
      token no código; publicar para sem a chave e recusa chave dentro do repositório; portátil nunca tira o Inno; XML da
      tarefa. Depois, um arquivo por vez no PC: esse, `test_empacotar.py`, `test_botoes_em_portugues.py`, `test_requirements.py`.
- [ ] PRÓXIMO PASSO 3: ensaio 1 → 2 com programinha de mentira (PyInstaller + vpk pack; ver se pede `--skipVeloAppCheck`),
      Portable.zip numa pasta de teste, versão 2 numa pasta-servidor, `--procurar-atualizacao --fonte <pasta>`; a volta
      (`Update.exe apply --package` com versão mais velha) e a assinatura errada. Nunca instalar em Arquivos de Programas
      nem criar tarefa (etapa 5).
- [ ] PRÓXIMO PASSO 4: GitHub (conjunto + filtro de velocidade), relatório em três formatos, entrega.

Sobra minha fora do projeto (não apaguei, regra §10.9): `C:\Users\fotog\AppData\Local\Temp\x_never\` com um
`velopack-1.2.161-...whl` baixado por engano às 11:05 de 16/11.

Lembrete: o GitHub não instala o velopack (`.github/requisitos-windows.txt`, ramo claude/list-server-files-gkos8v);
por isso os testes usam gerente falso e o programa só importa o velopack quando foi instalado por ele.

## Perguntas para o Samuel

**1. O instalador antigo sai do programa agora, ou fica de reserva até o teste no seu PC?**

Do que se trata: o programa tinha um jeito antigo de montar o instalador (o "Inno Setup", o que fez o instalador que o
Kaique tem de 28/10). Você escolheu trocá-lo pelo Velopack (16/11). O Velopack já está no programa e o ensaio da
atualização deu certo numa pasta de teste. O jeito antigo continua lá, sem mudar nada, e nove conferências automáticas
dele continuam passando.

O que você escolhe:
- **Deixar o antigo de reserva até o teste da instalação no seu PC (sugestão).** Nada muda agora. Se o Velopack der
  problema na instalação de verdade, ainda dá para fazer um instalador do jeito antigo. Depois do teste, eu pergunto de
  novo para tirar.
- **Tirar já.** Saem o arquivo do instalador antigo e as nove conferências que só olham para ele (as que conferem que
  cada modelo, peça e DLL entrou no instalador antigo). As mesmas peças continuam conferidas no instalador novo.
- **Só comentário.**

Para quem usa: nada muda nas duas opções; o Kaique recebe o instalador novo. Situação de agora: o novo está pronto
na versão de teste, esperando o teste de instalação de verdade.

As nove conferências (para a gerente, `tests/test_empacotar.py`): `test_registro_do_inno_tem_de_listar_cada_modelo`,
`test_o_script_do_inno_recusa_pasta_sem_os_modelos`, `test_registro_do_inno_tem_de_listar_cada_peca`,
`test_registro_do_inno_com_versao_no_fim_da_linha`, `test_o_script_do_inno_recusa_pasta_sem_as_pecas`,
`test_registro_do_inno_tem_de_listar_a_dll_da_gravura`, `test_o_script_do_inno_recusa_pasta_sem_a_dll_da_gravura`,
`test_regressao_o_pacote_leva_as_duas_dlls_do_scantailor` (a parte do `.iss`) e `test_modo_entrega_nao_apaga_o_teste_do_kaique`
(o modo "entrega" leva o instalador antigo à Área de Trabalho). Nenhuma foi mudada nem apagada.

## Ressalvas (para a etapa 5)

(a preencher)
