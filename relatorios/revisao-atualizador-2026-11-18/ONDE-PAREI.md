# ONDE PAREI — revisão da estrutura do atualizador (18/11/2026)

Cópia `.claude/worktrees/revisao-atualizador`, ramo `revisao-atualizador-2026-11-18`, a partir de `obra-2026-10-26`
(`b74a94e2`, Livro com a D-767). Tarefa **só de leitura e relatório**: nenhuma linha do programa nem dos testes mudou.
Nenhuma janela aberta na tela do Samuel, nenhuma pergunta do Windows, nada instalado, nada apagado.

## Decisões que esta tarefa precisa cumprir (do pedido da gerente e do Livro)

- **D-767** (18/11, a regra desta tarefa): "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos
  quero que funcione" · "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora
  de montar a estrutura do atualizador e testes a distancias". O que mexe no Windows só conta como pronto rodando de
  verdade, à vista; cada peça provada sozinha antes de montar a versão.
- **D-706** "a atualização via internet tem que ser como funciona com apps" · **D-714** publicada de propósito ·
  **D-732** "não, faz quando o programa é aberto" · **D-733** "1- sim" (uma pergunta do Windows na primeira abertura,
  depois nenhuma) · **D-734** "quando ele abrir o programa de novo" · **D-735**, **D-741**, **D-749** (a pergunta volta
  até o "Sim" com a preparação feita) · **D-742**/**D-748** (a janelinha "Atualizando o programa, espere um pouco...").
- **D-715**/**D-720** ("Reiniciar agora" e "Depois") · **D-718** "Sim, e tem que avisar a gente de alguma maneira" ·
  **D-719** "1" (aviso na tela e registro lido de longe; a frase combinada).
- **D-723** "velopack" · **D-724** "gratis, mas o que é essa assinatura e é segura?" (versão sem a assinatura certa não é
  instalada) · **D-727** tudo dentro do instalador · **D-713** projeto público.
- **D-731** "ok" (desinstalar deixa o computador como era; projetos ficam) · **D-763**/**D-764** (nome do pacote fora da
  pasta dos projetos; sobra `%LOCALAPPDATA%\EditorImpressaoPrograma`).
- **D-736** (de longe: o programa não procura sozinho; o Samuel manda atualizar) · **D-717** (a conta de testes não
  consegue mudar o Windows).
- **D-765** (nenhum conserto até a entrega) · **D-766** (depois, cada conserto vira versão).
- CLAUDE.md §3 (interface nunca congela; nenhuma exceção fecha a janela), §6 (trocar biblioteca precisa perguntar),
  §11.8 (nunca mudar teste antigo sem o ok), §11.12 (sem gambiarra), §11.13 (como perguntar).

## Como cumpri cada uma

- **D-767:** o relatório separa o que foi provado no Windows de verdade (etapa 5 e leituras feitas hoje, só lendo) do
  que é leitura de código; a seção 4 é o plano de provar cada peça à vista, uma por uma.
- **D-765:** nada foi consertado. Só relatório e ONDE-PAREI.
- **D-724, D-731, D-734, D-742, D-719:** cada uma tem, no relatório, o que hoje a contraria e o desenho que a cumpre.
- **§11.8:** o teste antigo que trava o defeito (`test_d733_o_script_escondido_vai_codificado_e_solto`) não foi
  tocado; vira pergunta.
- **§11.13:** as perguntas da seção 5 do relatório seguem o formato.

## O que já está escolhido e testado aqui (D-605)

Testes do atualizador que existem: `tests/test_decisoes_atualizacao.py` (38), `test_decisoes_ajudante_da_atualizacao.py`
(37), `test_decisoes_desinstalar.py` (37), `test_decisoes_desinstalar_pasta.py` (4), `test_decisoes_preparo_d749.py` (5),
`test_nome_do_pacote.py` (5), `test_assinatura.py` (9). Quase todos trocam a peça do Windows por uma de mentira
(gerente do Velopack falso, `rodar=` falso, executor de mentira, `Popen` trocado). Nada foi rodado nem mudado.

## Como fica para quem usa e no livro

Nada muda nesta tarefa. O relatório descreve, para cada proposta, o que o Kaique veria.

## A regra de cada coisa e os caminhos (§11.12), resumo

- "Lançar um processo solto": dois jeitos hoje (`_lancar_escondido`, `_aplicar_pacote_quando_sair`), os dois com
  `DETACHED_PROCESS`. Proposta: um só.
- "Pedir licença de administrador": um só (`_rodar_elevado`, do outro agente), mas lê o erro errado.
- "O computador está preparado": hoje é uma marca lembrada nas Configurações do Kaique; proposta: conferida no Windows.
- "Em que pé está a troca": `situacao()` lê um arquivo que o ajudante, a janela e o PowerShell da troca leem e escrevem
  em horas diferentes; a fase "aplicando" é lida como "falhou" durante a troca de verdade.
- "Falha": `registrar_falha()` é um lugar só (bom), mas não separa falha passageira de falha de verdade.

## Feito

- [x] Lidos inteiros: `implementador.md`, `CLAUDE.md`, `memoria/INDICE.md`, `memoria/itens/6.8.md`, D-705 a D-767 do
  Livro, as linhas de 18/11 da Lista de bugs, o ONDE-PAREI e o relatório da etapa 5, o relatório do estudo de publicar
  mais rápido.
- [x] Lidos inteiros: `atualizacao.py`, `publicar_versao_kaique.py`, `versao.py`, `ui/aviso_de_atualizacao.py`,
  `main.py`, `core/_testes_a_distancia_windows.py`; as partes do Velopack em `empacotar.py`; as partes de
  `core/testes_a_distancia.py` que o desinstalar usa.
- [x] Código do Velopack 1.2.161 (cópia do estudo, `saida_teste/publicar-rapido/fonte-velopack/repo`, só lido):
  `apply_windows_impl.rs`, `util_windows.rs` (mata os processos), `locator.rs` (`.portable`), commits `afa30e56`,
  `b40a2781`, `f31022e6` (conferido: nenhum dos três está na 1.2.161).
- [x] Leituras no Windows de verdade, só lendo (nenhuma pergunta): licenças de `C:\ProgramData\EditorImpressao` e
  subpastas (`icacls`); as duas tarefas do Agendador que sobraram depois do desinstalar da etapa 5 (última execução e
  resultado); o fim do `atualizacao.log`; `%LOCALAPPDATA%\EditorImpressaoPrograma` e `%LOCALAPPDATA%\velopack`; o
  Controle Inteligente de Aplicativos deste PC (desligado) e a página de código OEM (850).
- [x] Relatório em três formatos e este ONDE-PAREI.
- [x] Recado da gerente (12:05, achado N11 do revisor dos testes à distância): lido o relatório dele
  (`revisao-distancia-2026-11-18`); seção 3b nova (dono e licença de cada pasta segundo o código; o "lugar seguro de
  fábrica" serve para o atualizador; uma peça só para os dois). Às 12:11 a pasta do ProgramData, as tarefas e a pasta de
  reserva já não existiam (limpeza da fase 12 da etapa 5): as leituras de ~12:00 ficam anotadas com essa hora.

## Perguntas para o Samuel

Estão na seção 5 do relatório (`relatorio.md`), no formato do CLAUDE.md §11.13. São 8.

## Sobras

Nenhuma. Só criei esta pasta de relatório e a cópia `revisao-atualizador`.
