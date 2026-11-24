# Quem tenta quebrar, volta 1: o atualizador novo

24/11/2026. Agente que tenta quebrar (D-775), novo, que não escreveu este código. Ramo `atualizador-novo-2026-11-23`,
último commit conferido `cd4b8414` (diferença conferida: `7d1f633a..cd4b8414`). Nada do programa nem dos testes foi
mudado. Nenhuma janela foi aberta na tela, nenhuma pergunta do Windows, nada mudado em `C:\Program Files`, nenhuma
tarefa do Windows mexida. As provas rodaram em pastas de prova minhas no D:. Tudo o que está em `provas/` é meu.

## Em uma frase

**NÃO ESTÁ PRONTO para a prova à vista.** Há um defeito grave: se o Kaique clicar no atalho enquanto a versão nova
está sendo trocada (o mesmo clique que o Samuel fez na prova de 22/11), o programa anota uma falha que não aconteceu e
depois mostra "A atualização não deu certo. O programa voltou para a versão anterior...", com o programa já na
versão nova. Há também 5 médios (o "Reiniciar agora" que fecha o programa e não reabre; a volta que olha o motor
errado; 9 proteções que nenhum teste acusa quando desligadas; o estado que não grava e ninguém confere; e uma
pergunta de desenho sobre as outras contas do computador) e 12 leves.

O que está certo é bastante: a regra pura, a peça do Velopack, a troca por um lugar só, o "Não" do Windows que nunca
vira "deu certo", os textos da D-835 e da D-778 palavra por palavra, a ordem da primeira abertura (D-834). Ver
"Conferido e certo" no fim.

## Máquina ou olho

Tudo aqui é **máquina** (leitura do código, testes e provas rodadas) e **leitura do código do Velopack 1.2.161**
(clone limpo da etiqueta, commit `92d6a1c9`, numa pasta nova minha, nada rodado de dentro dele). Nada foi visto na
tela: o que só a prova à vista mostra está em "Não deu para conferir".

## Os testes do ramo, um arquivo por vez (no PC, pasta temporária no D:)

| Arquivo | Resultado |
|---|---|
| `test_fases_da_atualizacao.py` | 807 passaram |
| `test_atualizador_novo.py` | 35 passaram |
| `test_windows_preparo_do_computador.py` | 19 passaram, 1 pulado (o de verdade, só no GitHub) |
| `test_velopack_de_verdade.py` | 3 passaram |
| `test_porteiro_licenca_que_acrescenta.py` | 14 passaram |
| `test_trava_windows.py` | 42 passaram, 3 pulados |
| `test_decisoes_atualizacao.py` | 35 passaram |
| `test_decisoes_ajudante_da_atualizacao.py` | 22 passaram |
| `test_decisoes_preparo_d749.py` | 3 passaram |
| `test_decisoes_brasao.py` | 20 passaram |
| `test_decisoes_desinstalar.py` | 45 passaram |
| `test_decisoes_testes_a_distancia.py` | 13 passaram |
| `test_windows_peca.py` | 68 passaram, 3 pulados |
| `test_conferencias_pacote.py` | 26 passaram |

As 20 mutações do implementador (`relatorios/atualizador-novo/mutacoes.py`), rodadas por mim numa cópia do ramo:
**20 de 20 acusadas**, como ele disse. As minhas 17 mutações, com todos os arquivos de teste do atualizador (não só o
teste escolhido): **9 sobreviveram** (achado médio 3). A rodada inteira no GitHub não foi disparada por mim (é da
gerente).

---

## Achados graves

### G1. Abrir o programa pelo atalho no meio da troca anota uma falha que não houve, e a tela depois diz que a atualização falhou

- **O que acontece.** O Kaique escolhe "Reiniciar agora" (ou "Sim" no "Atualizar agora?" ao fechar). O programa grava
  no `estado.json` "tentando de X para Y" e pede a troca ao Velopack (`atualizacao.py:845`, `trocar_para`). O
  Velopack espera o programa sair (até 60 s), mostra a janelinha dele e abre o pacote inteiro (uns 460 MB), e só
  depois fecha à força o que roda da pasta e renomeia `current`. Nesse tempo todo, `current` ainda é a versão X, e o
  atalho abre a X normalmente: o atalho do Velopack não espera a troca nem olha a tranca dele. Essa segunda abertura
  lê "tentando X para Y" do disco (`atualizacao.py:893-899`), vê que roda a X e conclui "a troca não aconteceu"
  (`core/fases_da_atualizacao.py:433-440`): anota a falha "troca", põe Y em "não tentar" e manda a frase (1) para a
  tela. O Velopack então a fecha à força (com o que o Kaique tiver feito nela desde a última gravação), troca e reabre
  a Y, que passa no teste rápido e apaga só o "tentando" (`anotar_ok`, `atualizacao.py:199-204`): **a falha falsa
  fica anotada**. Resultado: ou a frase "A atualização não deu certo. O programa voltou para a versão anterior e
  continua funcionando. Avise o Samuel." aparece na janela que vai ser fechada à força, ou, se ela não chegou a
  abrir, aparece na abertura seguinte, com o programa já na versão nova.
- **A causa.** A regra trata "a versão que roda é a de antes" como "a troca não aconteceu", sem separar "a troca ainda
  está acontecendo". O dado do disco é usado como prova de algo que ele não prova.
- **A leitura do Velopack que mostra a janela de tempo:** `src/bins/src/stub.rs` 32-39 (o atalho só chama
  `Update.exe start`); `src/bins/src/commands/start_windows_impl.rs` 111-133 (`start` abre `current\` sem tranca nem
  espera); `src/bins/src/shared/util_common.rs` 14-26 (espera o programa até 60 s); `apply_windows_impl.rs` 134-147
  (a janelinha e a extração do pacote), 159 (só então fecha à força), 162 (renomeia).
- **Prova (rodada):** `provas/test_qtq_provas.py::test_A_...` e `::test_A2_...`, com a regra e o executor de verdade,
  o `estado.json` de verdade numa pasta de prova e as mesmas peças de mentira na borda que os testes do implementador
  usam. Passam (isto é: o defeito acontece). Saída em `provas/test_qtq_provas-resultado.txt`.
- **Fere:** D-828 (1), palavras dele: "abrir o programa pelo atalho no meio da troca não estraga a troca (o caso que
  ele fez na prova)"; D-770: "em vez de o programa ser fechado à força e acusar uma falha que não houve"; CLAUDE.md
  §11.12, ponto 2 (nada se dá como feito, nem como falho, sem conferir).
- **Defeito ou risco:** **defeito** na lógica (provado). O tamanho da janela de tempo no notebook é leitura do código
  do Velopack: a confirmar na prova à vista (passo 8 do plano: "Clicar no atalho durante a janelinha do Velopack").

---

## Achados médios

### M1. "Reiniciar agora" fecha o programa antes de conferir se pode trocar; se não puder, nada reabre e nada aparece

- **O que acontece.** "Reiniciar agora" → a janela fecha (`ui/aviso_de_atualizacao.py:67-70`; `fases:526-528`) → só
  então `trocar_para` confere o pacote, o motor e se há outra janela aberta (`atualizacao.py:823-842`). Se qualquer
  um disser não (outra janela do programa aberta, o motor fora do lugar, o Windows não deu a lista de processos, o
  Velopack não aceitou), a regra vai para "parado" com uma linha no registro (`fases:549-550`). O programa já fechou;
  ninguém o reabre; a tela não diz nada. Para o Kaique: clicou "Reiniciar agora" e o programa sumiu.
- **Prova (rodada):** `provas/test_qtq_provas.py::test_B_...` (o executor: depois do fechar, nenhum efeito de tela e
  nenhuma saída) e `::test_E_...` (a regra pura: só `Registrar`).
- **Fere:** D-715 ("reinicializar o programa") e D-720 ("Reiniciar agora"); §11.12, ponto 3 (nada pela metade sem a
  tela dizer o que ficou). A lista das falhas do ONDE-PAREI diz "não troca; o aviso volta na próxima abertura", mas
  não diz que o programa fica fechado.
- **Defeito.** (No "Sim" ao fechar o efeito é menor: o programa ia fechar mesmo; só a troca não acontece, calada.)

### M2. A volta para a versão anterior confere o motor da versão que falhou; e ninguém lê qual motor a versão nova pede

- **O que acontece.** `motor_esta_no_lugar` confere o motor que **o programa que roda** pede
  (`atualizacao.py:478-490` → `core/ocr_kraken.py:151-157`, com `VERSAO_DO_MOTOR` deste programa). A troca única usa
  essa conferência (`atualizacao.py:662`, `835-836`), e a volta também passa por ela (`atualizacao.py:880`). Se a
  versão nova falhou no teste rápido justamente porque o motor dela não está (uma versão que pede outro motor), a volta
  é recusada por "o motor do Kraken não está no lugar", a tela mostra a frase (3) ("não conseguiu voltar sozinho. Não
  desinstale nada.") e a versão quebrada fica, com o motor da anterior inteiro no lugar.
- **A causa, mais funda.** O pacote de cada atualização leva o `motor-exigido.json` (que motor esta versão pede,
  `empacotar.py:235` e `264`), mas nada no atualizador o lê. Então a versão nova é anunciada e trocada sem saber se o
  motor dela está no lugar; o "tudo ou nada" só vale quando o motor da nova é o mesmo da que roda.
- **Prova (rodada):** `provas/test_qtq_provas.py::test_C_...` (baixa a anterior assinada e não pede a troca de volta;
  falha "volta" com o motivo "motor").
- **Fere:** D-833 ("a versão nova só é anunciada com o motor dela no lugar"), D-790 ("A volta para a versão anterior
  acha o motor antigo na pasta dele"), D-718 (volta sozinha).
- **Defeito na lógica, risco ainda não vivido:** hoje todas as versões pedem o motor 1, então não acontece até o motor
  mudar. Era igual no conserto 4 da volta 1 (que a D-833 manda trazer); a volta recusada pelo motor errado é nova
  deste desenho.

### M3. Nove proteções que nenhum teste acusa quando desligadas (D-827)

Desliguei cada uma numa cópia do ramo, rodando **todos** os arquivos de teste do atualizador (924 casos), não só o
teste escolhido (`provas/mutacoes_qtq.py`, saída em `provas/mutacoes_qtq-resultado.txt`). Sobreviveram:

| Proteção desligada | Onde | O que ela protege |
|---|---|---|
| Q1 a conferência do espaço livre antes de abrir o motor | `atualizacao.py:543-547` | o disco nunca fica cheio por causa do motor |
| Q2 a conferência do motor aberto antes de dar o nome final | `atualizacao.py:550-552` | motor pela metade nunca passa por "está no lugar" (D-833) |
| Q3 "o motor já está" invertido: nunca põe e diz que pôs | `atualizacao.py:531-532` | D-788, D-833 |
| Q4 "o motor está no lugar" sempre sim | `atualizacao.py:490` | D-833 (antes de anunciar e de trocar) |
| Q5 o "preparado?" só olhando se a pasta existe | `atualizacao.py:341-355` | D-741, D-749 (é a regra única do "preparado?") |
| Q7 a leitura de volta do arquivo de dentro (`sq.version`) | `core/windows.py:2715` | D-837, §11.12 ponto 2 (a licença "pegou" lá dentro) |
| Q8 o Visual C++ só roda se só administradores podem trocá-lo | `core/windows.py:2606-2609` | segurança: o instalador roda com a licença de administrador |
| Q14 "o Windows não deu a lista de processos" vira "pode trocar" | `atualizacao.py:839-840` | outra janela fechada à força com o trabalho dentro |
| Q15 o processo cujo caminho não deu para ler conta como de dentro | `core/windows.py:1928` | a mesma (a janela de outra conta) |

- Q1 a Q4: `garantir_o_motor` e `motor_esta_no_lugar` **não têm teste nenhum neste ramo** (só peças de mentira que
  devolvem sim ou não). O plano, seção 5, dizia que vinham do ramo `atualizador-4` "e os testes do conserto 4 que
  cobram o motor"; lá eram uns 8 (`test_conserto4_*` e `test_volta2_medio1_*` em `tests/test_atualizador_4.py`). Não
  vieram, e a lista da D-836 não fala deles.
- **Fere:** D-827 ("proteção sem teste nunca é 'baixo'"), D-811 a D-813, D-833 ("O que foi feito no conserto 4 da
  volta 1 passa para o desenho novo").
- **Defeito** (falta de prova; as proteções em si existem no código).

### M4. O estado que não grava: a troca é pedida mesmo assim, e a falha some

- **O que acontece.** `trocar_para` não olha o que `anotar_tentativa` devolve (`atualizacao.py:845`), e `anotar_falha`,
  `anotar_ok` e `apagar_tentativa` não olham o que `gravar_estado` devolve (`atualizacao.py:195`, `203`, `218`). Se o
  `estado.json` não aceita gravação pela conta do Kaique, a troca é pedida sem a anotação e a falha não fica: a versão
  que acabou de falhar no teste rápido volta a ser procurada, baixada (uns 460 MB) e anunciada na abertura seguinte, e
  a frase da falha nunca aparece. Pode repetir a cada abertura.
- **Quando o estado não grava:** o arquivo nasce de um processo com licença e a conta comum não consegue substituí-lo
  (a pasta `C:\ProgramData\EditorImpressao\atualizacao` só dá às contas comuns "criar arquivo novo"). A prova nº 1 de
  22/11 mostrou que o `.msi` aberto por janela com licença abre o programa com licença no "Iniciar" do fim; esse
  programa grava o registro e pode gravar o estado. O mesmo vale para o registro (`atualizacao.log`): se nascer de um
  processo com licença (o próprio trabalho do preparo grava nele), as linhas da conta do Kaique vão para o `erros.log`
  dele e saem do registro que a gerente lê de longe (D-719).
- **Prova (rodada):** `provas/test_qtq_provas.py::test_F_...` (com o gravar do estado recusando).
- **Fere:** §11.12, ponto 2 (resultado não conferido); D-718/D-719 (o aviso e o registro).
- **Defeito** no "não conferir" (provado); **risco** no "quando acontece" (não provado no notebook).

### M5. Pergunta de desenho: "Usuários podem modificar" vale para todas as contas do computador, inclusive a dos testes à distância

- **O que é.** A licença da D-837 vai para o grupo Usuários, que tem todas as contas do computador. Com ela, qualquer
  conta pode trocar `current\EditorImpressao.exe` e o `Update.exe`. Esses arquivos rodam na conta do Kaique, e o
  `EditorImpressao.exe` roda com a licença de administrador quando o Kaique diz "Sim" à pergunta do Windows. A conta
  dos testes à distância (D-717: "sem poder de administrador") passa a ter, na prática, um caminho até o
  administrador. O desenho apagou o ajudante antigo antes da licença justamente por isso (o Fable elogiou), mas não
  olhou as outras contas.
- **Efeito no que já foi feito:** a proteção 3 (a soma do pacote conferida antes de trocar, "outra conta poderia
  trocar o arquivo") não protege dessa outra conta: ela troca `current\` direto, e entre a conferência e a troca do
  Velopack há segundos.
- **Fere:** não é defeito do código (o código faz o que a D-837 pede). É um ponto que a lista das falhas (§11.12 ponto
  3) e o parecer não trataram, e que bate na D-717. **Risco de desenho, não provado.** Pergunta para o Samuel antes da
  entrega dos testes à distância (é ali que a outra conta nasce).

---

## Achados leves (12)

1. **A falha "troca" usa a frase que diz "voltou".** Quando o Velopack não consegue trocar (arquivo preso), o programa
   nunca saiu da versão de antes, e a tela diz "O programa voltou para a versão anterior" (`atualizacao.py:112-113`).
   A D-778 tem três frases e nenhuma para esse caso; a escolha é do agente, sem pergunta (§11.7). Prova: `test_D`.
2. **A exceção da K03 do porteiro é mais larga que a D-837.** Na função da exceção passa um `/grant` para Todos com
   Controle total; fora dela passa tirar licença ou trocar o dono com o nome da ferramenta escrito em pedaços; e chamar
   a função com outra pasta (ex.: `C:\Windows`) não é acusado. A leitura de volta (`core/windows.py:2645`) também não
   recusa linha a mais. Prova: `provas/prova_porteiro_k03.py` (saída em `-resultado.txt`). O porteiro é rede de
   segurança por texto; o caso "tirar a herança em dois pedaços" dentro da função foi acusado.
3. **"Outra janela aberta" pelo número de quem abriu cada processo, sem a hora de criação** (`core/windows.py:1858`).
   O Windows reaproveita números: uma janela aberta por um processo que já morreu e cujo número passou para este
   programa conta como "da família" e fica de fora; o Velopack a fecharia à força. Risco não provado.
4. **"Nenhum PowerShell" não é verdade** (`atualizacao.py:8`): o passo 1 do preparo (`apagar_tarefa`) lê a tarefa
   pelo PowerShell duas vezes (`core/windows.py:2145`, `2242-2246`), com a licença. Num computador que bloqueia o
   PowerShell, o passo 1 falha sempre, a licença nunca é dada e a pergunta volta a cada abertura, sem nada na tela.
   No notebook do Kaique a tarefa nem existe. Risco não provado.
5. **O teste do "preparado?" não cobre a pasta que existe e não aceita gravação** (mutação Q5, médio 3): fica aqui
   como lembrete de que é a regra única de D-741/D-749.
6. **Afirmação do ONDE-PAREI que não confere neste PC:** o `atualizacao.log` velho em
   `C:\ProgramData\EditorImpressao\atualizacao\` é da conta do Samuel, com controle total para ela (lido só com a
   leitura de licenças da peça), não "do sistema". Sem efeito ruim.
7. **Comentários que dizem o que não é mais:** `core/testes_a_distancia.py:26`, `384`, `829` citam
   `atualizacao.preparar_como_administrador`, que saiu (§11.12: comentário "como X" se confere na hora).
8. **Corrida entre o aviso e o fechar:** se o download terminar no instante em que o Kaique fecha, o aviso "Reiniciar
   agora / Depois" (que vem por sinal de outro fio) pode aparecer junto ou depois do "Atualizar agora?". Risco não
   provado.
9. **Sem o "Sim", não há motor do Kraken:** no programa instalado o motor só é procurado em `<raiz>\motor-kraken\1`,
   e só é tirado do arquivo depois do preparo. Enquanto o Kaique disser "Não", o detector do Kraken não funciona. Era
   igual no `atualizador-4`.
10. **Falha que não passa nunca vira pergunta a cada abertura, sem aviso:** Visual C++ ou Inno que falham sempre, ou um
    bloqueio de gravação (ex.: proteção contra ransomware do Windows na pasta), fazem a pergunta voltar em toda
    abertura (é a D-749) e nada na tela diz por quê; só o registro.
11. **Aberto "como administrador" conta como preparado:** o teste de gravar dá sim com a licença, a pergunta não é
    feita e a procura e o download rodam com a licença (`atualizacao.py:903`). Na abertura comum seguinte a pergunta
    vem. Risco não provado.
12. **Segundos sem nada na tela depois da troca** (o teste rápido antes da janela, até 5 min de limite): um segundo
    clique abre outra abertura que também roda o teste rápido e depois abre outra janela. Risco não provado (ressalva
    3 do plano).

---

## A peça de fora (§11.12 ponto 6): a leitura do implementador, conferida

Li eu mesmo o Velopack 1.2.161 (clone limpo da etiqueta) e o pacote da `.venv` (`velopack-1.2.161`, `__init__.pyi`):

- **Confere:** `wait_exit_then_apply_updates` (`manager.rs` 602-680: exige o pacote em `packages\`, `--waitPid` deste
  processo, `--norestart` se não reabrir, os argumentos depois de `--`); a espera de 60 s (`util_common.rs` 14-26);
  na falha com reabrir, abre a de antes com os mesmos argumentos (`apply.rs` 57-61); "Unable to start the update" sem
  mexer (`apply_windows_impl.rs` 162-163) e "broken state" (175-176); "Failed to update uninstall entry" não para
  nada (210-212); `download_updates` não baixa nem confere se o arquivo já existe (`manager.rs` 414-416) e confere
  tamanho e SHA256 (537-561); a reserva no `%LOCALAPPDATA%` quando a raiz não grava (`locator.rs` 152-178); só os 10
  "Releases" mais novos (`github.rs` 80) e o arquivo achado pelo nome (129-138); o `App().run()` sem troca automática
  (`app.rs` 180-191); as assinaturas de `UpdateInfo`, `VelopackAsset` e `UpdateOptions` usadas em
  `core/conversa_com_o_velopack.py` batem com o `__init__.pyi`.
- **Conferido a mais por mim:** os ganchos rápidos saem do processo mesmo sem função nossa (`app.rs` 211-225), então o
  `--veloapp-obsolete` que o Velopack roda no meio da troca nunca chega ao nosso `abrir` (bom); a limpeza do `.msi`
  como o sistema usa `remove_dir_all` 1.0.0 (`Cargo.lock`), a versão que já não segue atalho de pasta.
- **O que faltou na leitura:** a ordem "janelinha → abrir o pacote → fechar à força → renomear", que o ONDE-PAREI
  cita, deixa a versão de antes abrível pelo atalho durante a espera e a extração; e o `start` não olha a tranca.
  Daí o grave 1.
- **icacls:** conferi de verdade, numa pasta minha no D:, que um arquivo aberto por outro processo sem compartilhar
  nada também recebe a licença (`provas/prova_licenca_arquivo_em_uso.py`; ressalva 2 do plano, nessa parte, resolvida).
  Não conferi em `C:\Program Files` (proibido aqui).

## Conferido e certo (curto)

- A regra é pura e exaustiva (807 pares); o executor chama o Windows só pela peça e o Velopack só pela peça dele; a
  trava pega também `importlib.import_module("velopack")` e `__import__("velopack")` (`provas/prova_trava_velopack.py`).
- A troca passa por um lugar só (`trocar_para`), pelos três caminhos; o `silent` nunca é ligado (D-832).
- O "Não" e a falha da pergunta do Windows nunca viram "deu certo"; o "preparado?" é o teste de gravar feito de novo
  depois do trabalho com licença, nunca o que ele anotou (D-741, D-749).
- A licença é o último passo; o ajudante antigo sai antes dela (D-838); os passos não aceitam dado no pedido e a raiz
  é conferida em Arquivos de Programas; a licença é só o `icacls ... /grant "*S-1-5-32-545:(OI)(CI)M" /T`, lido de
  volta (D-837). Nada do desenho antigo vivo no código novo: sem ajudante, sem marcas, sem a espera de 30 s, sem
  `estado.json` como canal (sobra só o nome da tarefa velha, para apagá-la).
- Textos palavra por palavra: D-835 (aviso: "Se escolher "Depois", você pode atualizar quando fechar o programa.";
  "Atualizar agora?" / "Quer atualizar o programa agora, ao fechar?" / "Sim" / "Não") e as três frases da D-778.
- A pergunta do Windows vem dentro de `atender_linha_de_comando`, antes do brasão e da janela; a janela da senha vem
  depois e não pergunta nada ao Windows (D-834, D-825). Procura só ao abrir (D-732). Conta de testes, código e
  portátil: nada (D-728, D-736).
- "Depois" sempre leva ao "Atualizar agora?" ao fechar; fechar sem versão pronta não pergunta nada (D-831, D-794).
- A catraca da trava desceu de 46 para 34 e bate com a lista.

## Não deu para conferir sem a prova à vista

- A pergunta do Windows no meio da tela, sem janela dona, logo no clique (D-806, ressalva 1 do plano).
- O `icacls` na pasta de verdade de Arquivos de Programas, com os arquivos do `.msi` e o programa rodando.
- Se a janelinha do Velopack aparece de fato quando a troca é pedida por `wait_exit_then_apply_updates` (ele abre o
  `Update.exe` com `CREATE_NO_WINDOW`, `process_win.rs` 388-392; a leitura diz que só some a janela preta).
- O tamanho real da janela de tempo do grave 1 no notebook.
- Desinstalar (a pasta inteira some com o motor), a conta padrão, o `.msi` aberto com ou sem licença no notebook.

## As provas (tudo meu, nesta pasta)

- `provas/test_qtq_provas.py` (7 provas; rodar com o PYTHONPATH na raiz do ramo) e `-resultado.txt`.
- `provas/mutacoes_qtq.py` (roda numa cópia do ramo, nunca no worktree) e `mutacoes_qtq-resultado.txt`.
- `provas/prova_porteiro_k03.py`, `provas/prova_trava_velopack.py`, `provas/prova_licenca_arquivo_em_uso.py` e as
  saídas.

Não proponho conserto: a causa de cada achado está escrita acima.
