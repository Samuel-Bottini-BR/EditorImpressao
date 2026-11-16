# Etapa 3 da frente do Kaique: a atualização sozinha, com o Velopack

**O que é:** a parte do programa que faz a versão nova chegar sozinha ao notebook do Kaique, sem ele reinstalar nada.
Feita em 16/11/2026, na versão de teste (ramo `kaique-etapa3-2026-11-16`). **Nada foi instalado de verdade no
Windows do Samuel e nenhuma tarefa do Windows foi criada.** A instalação de verdade é a etapa 5.

**Situação de agora:** pronto para a gerente juntar e para a etapa 5. O ensaio da atualização deu certo numa pasta de
teste. O GitHub não rodou hoje (estava com problema); por isso rodei no PC, um arquivo de teste por vez. O conjunto
inteiro e o filtro de velocidade ficam para a gerente, com os agentes parados.

## 1. Como fica para o Kaique

1. **Primeira vez:** ele recebe um instalador novo e dá dois cliques. O Windows pergunta "Deseja permitir...?"; ele
   clica "Sim". O programa vai para Arquivos de Programas. A instalação velha, a de 28/10, sai sozinha. Os livros e
   os projetos dele ficam como estão. Tudo vem dentro do instalador, sem baixar nada.
2. **Todo dia:** uns minutos depois de o computador ligar, por trás e sem janela, o programa procura a "versão para o
   Kaique" no GitHub do projeto. Se houver uma e a assinatura do Samuel conferir, baixa só o que mudou e troca. Da
   próxima vez que ele abrir o programa, já é a nova.
3. **Com o programa aberto:** aparece "Chegou uma versão nova do Editor de Impressão. Salve o seu trabalho e reinicie
   o programa para usar a versão nova." com os botões "Reiniciar agora" e "Depois".
   - "Reiniciar agora": o programa grava o trabalho, fecha e abre na versão nova.
   - "Depois": nada muda agora; a versão nova entra quando o computador ligar de novo.
4. **Se der errado:** o programa volta (ou fica) na versão anterior. Na próxima vez que ele abrir, aparece uma vez só:
   "A atualização não deu certo. O programa voltou para a versão anterior e continua funcionando. Avise o Samuel." O
   erro fica num registro que a gerente lê de longe.
5. **No livro (PDF):** nada muda. Nenhum filtro, ferramenta ou tela de trabalho foi tocado.

## 2. O ensaio de verdade (a atualização de mentira, numa pasta de teste)

Um programinha de mentira foi empacotado do mesmo jeito que o programa: pelo PyInstaller e pelo Velopack, com os
mesmos arquivos da atualização. Ele recebeu outro nome de pacote e outra chave de assinatura, e o pacote "portátil"
ficou só numa pasta, sem instalar. Script: `relatorios/frente-kaique-2026-11-16/etapa3/ensaio_velopack.py`.

| Passo | O que aconteceu | Resultado |
|---|---|---|
| 0 | versão 1.1.0 posta numa pasta de teste | abriu na 1.1.0 |
| A | publicada a 1.2.0 → "procurar a versão nova" | trocou para a 1.2.0; o teste rápido passou; estado "ok" |
| B | publicada a 1.3.0 **estragada** (o teste rápido dela falha) | trocou, o teste falhou e **voltou para a 1.2.0** com o pacote assinado |
| C | publicada a 1.4.0 com a assinatura de **outra chave** | **recusada**; nada baixado; continua a 1.2.0 |

O registro do ensaio (o mesmo que a gerente lerá no notebook):

```
12:47:50 versão 1.2.0 publicada e assinada pelo Samuel: baixando
12:47:52 versão 1.2.0 baixada; trocando (o programa está fechado)
12:48:14 versão 1.2.0 instalada e conferida (teste rápido certo)
12:51:22 versão 1.3.0 baixada; trocando (o programa está fechado)
12:51:32 FALHOU (teste) a atualização para a 1.3.0; continua a 1.2.0
12:51:38 voltando para a versão 1.2.0
12:54:32 FALHOU (recusada) a atualização para a 1.4.0; continua a 1.2.0: a assinatura não confere com a chave do Samuel
```

O pacote "só o que mudou" funcionou: da 1.1.0 para a 1.2.0, 3 arquivos mudaram e 525 ficaram iguais. O instalador
`.msi` também ficou pronto na primeira versão.

Depois do ensaio conferi o Windows: nenhuma tarefa criada, nenhum atalho novo, nada no registro do Windows, nada no
ProgramData de verdade.

**Dois achados do ensaio, já consertados:**
- Sem a opção de 64 bits, o Velopack montava o pacote como 32 bits: o instalador iria para "Arquivos de Programas
  (x86)". Consertado: o comando agora pede 64 bits, e um teste cobra isso.
- No pacote portátil (o do ensaio), o gancho "depois de atualizar" tentou criar a tarefa do Windows no PC do Samuel.
  O Windows negou e nada foi criado (conferido). Consertado com uma regra só: pacote portátil nunca mexe no Windows.
  O teste de reversão falha no código antigo, e mostrei que o código antigo tentava criar a tarefa.

## 3. Arquivos

Novos:
- `versao.py`: o número da versão, num lugar só.
- `assinatura.py`: a assinatura grátis (D-724).
- `atualizacao.py`: a regra inteira da atualização.
- `ui/aviso_de_atualizacao.py`: os dois avisos na tela.
- `publicar_versao_kaique.py`: o comando de publicar.
- `tests/test_assinatura.py`.
- `tests/test_decisoes_atualizacao.py`.
- `relatorios/frente-kaique-2026-11-16/etapa3/ensaio_velopack.py`, `ONDE-PAREI.md` e este relatório.

Alterados:
- `main.py`: duas chamadas, depois dos modos que já existiam.
- `empacotar.py`: funções do Velopack e a versão passada ao Inno.
- `instalador.iss`: a versão não fica mais escrita nele; recebe-a do `empacotar.py` e recusa compilar sem ela.
- `requirements.txt`: `velopack==1.2.161`.

Instalado no PC (autorizado): o `velopack` 1.2.161 no `.venv` e o `vpk` 1.2.161 (`dotnet tool install -g vpk`).

## 4. Testes, no PC, um arquivo por vez (código final)

| Arquivo | Resultado |
|---|---|
| `tests/test_assinatura.py` (novo; exemplos oficiais da RFC 8032) | 16 passaram |
| `tests/test_decisoes_atualizacao.py` (novo; uma prova por decisão) | 38 passaram |
| `tests/test_empacotar.py` (antigo, nenhum mudado) | 41 passaram |
| `tests/test_empacotar_teste_velocidade.py` | 28 passaram |
| `tests/test_requirements.py` | 2 passaram |
| `tests/test_botoes_em_portugues.py` (varre `ui/` e `main.py`) | 5 passaram |
| `tests/test_ocr_diagnostico.py` | 6 passaram |
| `tests/test_decisoes.py` | 27 passaram |
| `tests/test_salva_sozinho.py` (varre `ui/` e `main.py`) | 11 passaram |
| Ensaio da atualização 1.1.0 → 1.2.0 → estragada → assinatura errada | CERTO (2ª rodada; a 1ª achou o erro do script) |

Não rodei o conjunto inteiro nem o filtro de velocidade (ordem da gerente; o GitHub estava com problema).
Sobre a velocidade: pelo código e nos testes, a atualização só faz uma conferência de arquivo, sem importar o Velopack.
Só o programa instalado pelo Velopack importa o Velopack (0,1 s medido).

## 5. A regra num lugar só (caminho → função)

- **número da versão:** `instalador.iss` (`empacotar.comando_do_inno`), `vpk pack` (`empacotar.comando_do_vpk`), o comando de publicar e a atualização → `versao.VERSAO`
- **conferir a assinatura:** antes de baixar (`atualizacao.conferir_assinatura_do`), antes de voltar (`atualizacao.voltar_para_a_anterior`) e antes de publicar (`publicar_versao_kaique.assinar_pacote`) → `assinatura.conferir_versao`
- **o que fazer com a versão nova:** a tarefa ao ligar (`rodar_ao_ligar`) → `atualizacao.procurar_e_preparar`
- **em que pé está a atualização:** a tarefa (`rodar_ao_ligar`) e a tela (`o_que_avisar`) → `atualizacao.situacao`
- **o que a tela mostra:** o relógio da janela (`VigiaDaAtualizacao.olhar`) → `atualizacao.o_que_avisar`
- **toda falha** (assinatura recusada, troca desfeita, teste rápido que falhou) → `atualizacao.registrar_falha`
- **mexer no Windows ou não:** os três ganchos do Velopack e `preparar_o_computador` → `atualizacao.e_portatil`
- **programa aberto:** a janela → `marcar_programa_aberto`; a tarefa → `ha_programa_aberto` (a mesma marca)
- **de onde vêm as versões:** o GitHub ou a pasta do ensaio → `atualizacao.Fonte`
- **entrada pela linha de comando:** `main.py` → `atualizacao.atender_linha_de_comando` (uma chamada); o aviso na tela → `ui.aviso_de_atualizacao.ligar_na_janela` (uma chamada)
- **o que vai dentro do pacote:** a mesma `empacotar.construir_pasta` com todas as travas, mais o Visual C++ (`preparar_pasta_para_o_velopack`); a conferência é `conferir_pacote_do_velopack`

## 6. Como cumpri cada decisão

- **D-706** ("como funciona com apps"): o instalador só na primeira vez; depois o Velopack baixa só o que mudou e troca. Prova: ensaio passo A (525 de 528 arquivos não baixados de novo).
- **D-713** (GitHub público): `Fonte.padrao()` é o GitHub do projeto, sem token. Prova: `test_d719_nenhum_token_dentro_do_programa`.
- **D-714** ("toda vez que o pc inicializar em segundo plano"; publicar de propósito):
  - A tarefa roda ao ligar, como o próprio sistema, em prioridade baixa e sem janela (`xml_da_tarefa`). Ela é criada pela instalação (`ao_instalar`).
  - Publicar só acontece quando alguém roda `publicar_versao_kaique.py`.
  - Provas: `test_d714_*` e o ensaio passo A.
- **D-715 / D-720** (aviso; "Reiniciar agora" e "Depois"):
  - Com o programa aberto, a versão fica "pendente" e não troca.
  - O aviso tem os dois botões; o Enter fica no "Depois".
  - "Depois" não troca, não fecha e não volta a perguntar na mesma abertura.
  - "Reiniciar agora" fecha pela janela (que grava o trabalho) e só então troca.
  - Provas: `test_d715_*`, `test_d720_*`.
- **D-718 / D-719** (volta e avisa):
  - A versão nova passa por um teste rápido escondido. Se falha, volta para a anterior, só com pacote assinado.
  - A frase da D-719, palavra por palavra, aparece uma vez só.
  - O erro vai para `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`, que a conta de testes consegue ler.
  - Provas: `test_d718_*`, `test_d719_*` e o ensaio passo B.
- **D-723** (Velopack; a instalação de 28/10 sai):
  - O instalador `.msi` vai "para a máquina toda", em Arquivos de Programas (pede administrador).
  - A tarefa do Windows, rodando como o sistema, tira o Inno pelo desinstalador dele, em silêncio, recusando caminho perigoso. Nunca tira no pacote portátil.
  - Os testes antigos do Inno não foram mudados (ver a pergunta).
  - Provas: `test_d723_*`.
- **D-724** (assinatura grátis): Ed25519, conferida ANTES de baixar. Se não confere, é recusada e nada é baixado. Publicar para sem a chave, e a chave nunca fica dentro do repositório. Provas: `test_assinatura.py`, `test_d724_*` e o ensaio passo C.
- **D-727** (tudo dentro do instalador): o Visual C++ oficial vai dentro do pacote e é conferido nele. A tarefa o instala se faltar, sem internet. O Velopack não baixa nada na instalação (sem `--framework`). Provas: `test_d727_*`.
- **D-605** (o novo não estraga o testado): nenhum teste antigo mudou, e todos os que rodei passaram. Pelo código, o programa abre igual. Prova: `test_pelo_codigo_a_linha_de_comando_nao_faz_nada_nem_importa_o_velopack`.

## 7. A chave privada

- **Onde está:** `C:\Users\fotog\AppData\Roaming\EditorImpressao-publicar\chave-privada-da-assinatura.txt`, fora do repositório.
- **A chave pública:** está dentro do programa (`assinatura.CHAVE_PUBLICA_DO_SAMUEL`, `b2c4094c…f34a`).
- **Falta:** a gerente guardar uma cópia desse arquivo no HD externo D:, fora de qualquer pasta do git. Eu não copiei.
- **Se a chave se perder:** é preciso uma chave nova e uma versão nova do programa com a chave pública nova. As versões já instaladas no Kaique não aceitariam mais as atualizações.

## 8. Ressalvas (o que só se prova na etapa 5)

1. **Licença de administrador na instalação.** Não se sabe se os ganchos do `.msi` "para a máquina toda" rodam com licença de administrador. É deles que depende criar e rodar a tarefa na instalação. Se não rodarem, a tarefa não é criada e o registro mostra "criar a tarefa: NÃO deu certo".
2. **A troca ao ligar o computador.** Não foi provado que a tarefa, rodando como o sistema, troca a versão em Arquivos de Programas sem perguntar nada. O código do Velopack diz que sim.
3. **"Reiniciar agora":** o Windows pode perguntar "Deseja permitir...?".
   - Se o Kaique clicar "Não", o programa já fechou gravado e não reabre sozinho.
   - Ele abre de novo, e a versão nova entra quando o computador ligar.
4. **O programa de verdade ainda não foi empacotado pelo Velopack.** O ensaio usou o programinha, e o empacotamento do programa leva uns 25 minutos.
   - A conferência das peças dentro do pacote só foi testada com um pacote de mentira.
   - O PyInstaller levou o Velopack sozinho no programinha; espera-se o mesmo no programa.
5. **No PC do Samuel há uma instalação do Inno de 01/09, com o mesmo identificador.** Instalar o `.msi` novo no PC dele, na etapa 5, vai tirar essa instalação velha (a de `C:\Program Files\Editor de Impressao`). Os projetos dele não são tocados. É preciso avisá-lo antes e pôr isso na lista do que se desfaz (D-722).
6. **A versão que falhou fica guardada.** Depois de uma volta, o pacote da versão estragada continua na pasta `packages` do programa: ocupa disco, mas não é usado.
7. **A primeira atualização pode vir inteira.** Segundo um problema conhecido do Velopack (consertado na versão 1.3 dele), a primeira atualização depois de instalar pelo `.msi` pode baixar o pacote inteiro.
8. **A mesma frase para toda falha.** A frase da D-719 aparece também quando a assinatura é recusada. Nesse caso o programa "ficou" na versão anterior, não "voltou". Escolhi uma frase só para não inventar texto novo (§11.7).
9. **A assinatura é calculada pelo nosso código.** O código das contas foi copiado da norma oficial da assinatura Ed25519 (RFC 8032), porque o `.venv` não tem biblioteca de assinatura, e confere com os exemplos oficiais dela. Se a gerente autorizar a biblioteca `cryptography`, dá para trocar sem mudar o formato.
10. **Os avisos na tela foram testados sem abrir janela** (regra do Samuel). Ver como ficam fica para o verificador.
11. **O GitHub não instala o `velopack`** (`.github/requisitos-windows.txt`). Os testes não precisam dele, mas a gerente pode acrescentar a linha quando o GitHub voltar.
12. **Sobra minha fora do projeto, não apagada (§10.9):** `C:\Users\fotog\AppData\Local\Temp\x_never\` tem um arquivo do Velopack que baixei por engano.

## 9. Bugs para a Lista de bugs

Nenhum no programa que já existia. Os dois achados do ensaio eram desta etapa e já foram consertados (seção 2).

## 10. Perguntas para o Samuel

**O instalador antigo sai do programa agora, ou fica de reserva até o teste no seu PC?**

O programa tinha um jeito antigo de montar o instalador, o que fez o instalador que o Kaique tem, de 28/10. Você
escolheu trocá-lo pelo Velopack (16/11). O novo já está no programa e o ensaio da atualização deu certo numa pasta de
teste. O antigo continua lá, sem mudar, e nove conferências automáticas dele continuam passando.

O que você escolhe:
- **Deixar o antigo de reserva até o teste da instalação no seu PC (sugestão).** Nada muda agora. Se o novo der
  problema na instalação de verdade, ainda dá para fazer um instalador do jeito antigo.
- **Tirar já.** Saem o arquivo do instalador antigo e as nove conferências que só olham para ele. As mesmas peças
  continuam conferidas no instalador novo.
- **Só comentário.**

Para o Kaique, nada muda nas duas opções: ele recebe o instalador novo. (As nove conferências estão listadas no
`ONDE-PAREI.md`.)
