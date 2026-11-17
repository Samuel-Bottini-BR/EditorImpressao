# D-731 construção (itens 5 e 6 do plano) — ONDE-PAREI

Agente implementador. Cópia `.claude/worktrees/desinstalar-b`, ramo `desinstalar-b-2026-11-17`, começado em 17/11/2026
a partir de `997a3085`. Nada foi feito no Windows de verdade (só leitura).

## Decisões que esta tarefa precisa cumprir

- **D-731** (16/11): "ok" a "se um dia o programa for desinstalado do notebook do Kaique, o comando de longe e a conta
  de testes saem junto? Assim o notebook fica como era antes de instalar." Saem o OpenSSH (se foi o programa que
  instalou), a regra do firewall, a conta de testes e o perfil dela. Os projetos do Kaique ficam.
- **D-733** (17/11): "1- sim" (alternativa B do `plano-d732.md`): um ajudante do Windows que roda como o sistema. Para
  a D-731: o `ligar` cria uma tarefa "desfazer" que a conta comum pode mandar rodar; o gancho de desinstalar só manda.
- **D-705, D-711, D-717**: o que o `ligar` monta (OpenSSH só pelo Tailscale, liga com o Windows, senha, conta sem
  administrador e escondida). O desfazer tira isso e nada além. D-717: "um teste não [...] consegue mudar o Windows"
  (por isso a conta de testes não pode mandar rodar o desfazer).
- **D-712, D-721, D-728**: não mudam (instalador sem pergunta; janela da senha só no instalado).
- **D-722**: a etapa 5 desfaz tudo no PC do Samuel com o mesmo desfazer.
- **D-736**: não é desta tarefa (é do outro agente).
- CLAUDE.md §7 e §10.9 (nada que não é nosso se apaga), §11.7, §11.8, §11.12.

## O que já está escolhido e testado aqui (não pode mudar)

- `tests/test_decisoes_testes_a_distancia.py` (13 provas da etapa 4): os pedaços de texto que elas procuram nos
  comandos continuam lá; `ligar` não pode conter "Administ" nem "PubkeyAuthentication".
- `tests/test_decisoes_atualizacao.py`: `test_d714_criar_e_apagar_a_tarefa_pelo_schtasks`,
  `test_d723_o_portatil_nunca_cria_nem_apaga_a_tarefa`.
- `tests/test_promessas.py` P-215 (botão "Pôr a senha dos testes").
- A assinatura `ligar(senha)` e o jeito de pedir a licença (`Executor.aplicar`): o outro agente usa. Não mudam.

## Como fica para quem usa e no livro

- Kaique, usando o programa: nada muda. Janela da senha, Configurações, filtros e PDF iguais.
- Kaique, ao pôr a senha: a mesma pergunta do Windows de hoje. Por trás, o programa anota o que já havia no
  computador e deixa pronta a tarefa "desfazer".
- Kaique, ao desinstalar: nenhuma pergunta a mais. O gancho manda a tarefa rodar e volta. Em poucos minutos, por
  trás, o notebook fica como era. Os livros e projetos dele ficam.
- PDF: nada muda.

## Regra num lugar só (caminho → função)

| Caminho | Função |
|---|---|
| Desinstalar (gancho do Velopack) | `atualizacao.ao_desinstalar` → `testes_a_distancia.mandar_desfazer` → `Executor.rodar_a_tarefa` |
| Etapa 5, desfazer no PC do Samuel | a mesma tarefa (`mandar_desfazer`, como administrador) ou `plano_de_desfazer` → `Executor.aplicar` |
| O script que a tarefa roda | `montar_script(plano_de_desfazer(), ...)`, gravado pelo `ligar` |
| Ligar (janela da senha, caixinha, botão) | `testes_a_distancia.ligar` → `plano_de_ligar` |
| Tirar as linhas do `sshd_config` (ligar de novo, desligar do OpenSSH do dono, desfazer) | `_comando_tirar_o_bloco` |
| "O OpenSSH foi nosso?" / "A conta foi nossa?" | `_so_se_o_openssh_foi_nosso` / `_so_se_a_conta_foi_nossa` |

## Andamento

- [x] Leitura (agente, CLAUDE.md, INDICE, decisões, planos, etapa 4).
- [x] Provas novas (`tests/test_decisoes_desinstalar.py`), commit `47d96ffb`. No código de antes: 28 falham, 7
  passam (`prova-no-codigo-de-antes.txt`).
- [x] Código, commit `65303058`.
- [x] Um arquivo por vez: etapa 4 13/13, atualização 38/38, novo 35/35, P-215 1/1. Nenhum teste antigo mudou.
- [x] Relatório nos três formatos (`relatorio.md/.html/.pdf`).
- [ ] Rodada do GitHub: não disparada (pedido "sem push"); fica com a gerente.

PRONTO PARA CONFERIR. Parei aqui.

## Como cumpri cada decisão

- D-731: `ao_desinstalar` manda a tarefa "desfazer"; o desfazer tira OpenSSH (se nosso), regra, conta, perfil;
  nunca cita a pasta do Kaique (provas `test_d731_*`).
- D-733: tarefa como o sistema, licença para a conta comum, gancho sem esperar (`test_d731_desinstalar_*`,
  `test_d731_a_conta_comum_*`).
- D-717: a conta de testes é negada na licença da tarefa; conta nova continua só no grupo Usuários.
- D-722: o mesmo `plano_de_desfazer` (prova `..._com_o_mesmo_plano`); a lista vai para `o-que-foi-desfeito.txt`.
- D-705/D-711/D-712/D-721/D-728: as 13 provas da etapa 4 passam sem mudança.

## Perguntas para o Samuel

Nenhuma nova para ele. As perguntas abertas (para a gerente decidir ou levar) estão no relatório, seção "Perguntas
abertas".
