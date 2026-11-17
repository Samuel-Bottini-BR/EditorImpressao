# ONDE PAREI — prova da pasta de reserva do Velopack (verificador, 17/11/2026)

Cópia `.claude/worktrees/velopack-pasta`, ramo `velopack-pasta-2026-11-17`, a partir de `a9d81030` (obra-2026-10-26).
Tarefa de **investigação**: nenhuma linha do programa muda, nada é consertado.

## Decisões que esta tarefa precisa cumprir (do pedido da gerente e do Livro da versão de teste)
- **D-723** "velopack": a atualização usa o Velopack; instala em Arquivos de Programas, pede administrador.
- **D-724** "gratis, mas o que é essa assinatura e é segura?": só entra versão com a assinatura do Samuel. Nesta prova
  a chave dele **não é usada**: a versão de mentira é assinada com uma chave de mentira, criada só para a prova.
- **D-731** "ok": desinstalar tira o que os testes à distância puseram; "Os projetos do Kaique
  (`%LOCALAPPDATA%\EditorImpressao`) continuam lá, como sempre (CLAUDE.md §7)".
- **D-733** "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?": programa em Arquivos de Programas; o ajudante
  (tarefa como SYSTEM) troca a versão; a janela do Kaique roda sem administrador.
- **D-741** "Sim" e **D-749** "Sim": a pergunta do Windows volta até dar certo (não tocadas por esta prova).
- CLAUDE.md §7: desinstalar **não apaga** `%LOCALAPPDATA%\EditorImpressao`, de propósito.
- Regras do pedido: nunca o id `EditorImpressao`; nunca gravar/ler para mudar/apagar em `%LOCALAPPDATA%\EditorImpressao`;
  nenhuma pergunta do Windows (UAC); nenhuma janela na tela do Samuel; não abrir agentes; devolver a permissão das
  pastas trancadas; não apagar fora do projeto o que não foi criado aqui.

## O que já está escolhido e testado aqui
Nada é mudado: nem código, nem testes. Os testes da atualização (`tests/test_atualizacao*.py`) não são tocados.

## Como fica para quem usa e no livro
Esta tarefa não muda nada para o Kaique nem no PDF. Ela só descobre se, no notebook dele, a peça de atualização grava
arquivos dentro da pasta dos projetos, e se desinstalar pode apagar alguma coisa ali.

## Plano da prova (escrito antes de rodar)
1. **Ler** o código do Velopack (ramo develop) e o que está dentro do Velopack 1.2.161 instalado aqui, para saber o
   que procurar. Feito: `locator.rs` (regra da pasta de reserva), `app.rs` (o `App().run()` também monta o localizador),
   `uninstall.rs`, e o ajudante do `.msi` (`wix-dll/lib.rs`). Guardado em `D:\agente_temp_testes\velopack-pasta\fonte-velopack\`.
2. **Programa de mentira** `ProvaPasta.exe` (PyInstaller, sem janela e sem console), id `EditorImpressaoProvaPasta`,
   que leva os arquivos de verdade `atualizacao.py`, `assinatura.py`, `versao.py` e `core/testes_a_distancia.py` e
   chama as **mesmas funções** que o programa chama ao abrir (`atender_linha_de_comando`, `procurar_ao_abrir`,
   `versao_que_roda`) e o que o ajudante chama ao atualizar (`rodar_ao_ligar` → `procurar_e_preparar` →
   `download_updates`). Por segurança, dentro dele: `PROGRAMDATA` e `LOCALAPPDATA` (variáveis) vão para pastas de
   mentira no D:; o nome das tarefas do Windows vira `EditorImpressaoProvaPasta\...` (não existem: o `schtasks` só
   falha); a peça que fala com o Windows nos testes à distância é trocada por uma que só anota; a chave pública é a
   de mentira; "programa aberto" fica sempre "sim" (assim nunca se pede ao Velopack para trocar a pasta, o que poderia
   pedir administrador).
3. Empacotar com o `vpk` 1.2.161 duas versões (1.0.0 e 1.0.1), sem atalhos.
4. **Caso A (pasta trancada, como Arquivos de Programas para o Kaique):** instalar a 1.0.0 em
   `D:\agente_temp_testes\velopack-pasta\instalado-trancado\` (pelo `.msi` por usuário, `msiexec /qn`, sem janela;
   se pedir administrador, falha calado e eu paro; plano B: o pacote portátil). Depois tirar da minha conta o direito
   de **criar** arquivo/pasta na raiz (`icacls /deny <eu>:(WD,AD)`, sem herança). Rodar, uma chamada por vez, e depois
   de cada uma fotografar `%LOCALAPPDATA%\EditorImpressaoProvaPasta` (o de verdade) e a pasta instalada:
   abrir (App().run), versão (`versao_que_roda`), procurar ao abrir, procurar+baixar (o que o ajudante faz).
   Ler o log do Velopack (`%LOCALAPPDATA%\velopack\velopack_EditorImpressaoProvaPasta.log`).
5. **Caso B (pasta que aceita gravação):** o mesmo, numa segunda instalação ou devolvendo a permissão.
6. **Desinstalar (se der sem administrador):** pôr um "projeto de mentira" em
   `%LOCALAPPDATA%\EditorImpressaoProvaPasta\projetos\` antes, desinstalar pelo `msiexec /x /qn` e ver o que sobra.
7. Devolver as permissões (`icacls /remove:d`), listar tudo o que foi criado fora do projeto.

## Feito
- [x] Worktree e ramo (renomeado de 18 para 17, a pedido da gerente).
- [x] Leitura do código do Velopack (passo 1).

## Próximo passo
- Montar o `ProvaPasta.exe` (passo 2).

## Perguntas para o Samuel
Nenhuma por enquanto.
