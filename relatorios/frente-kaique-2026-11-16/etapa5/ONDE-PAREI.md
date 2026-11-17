# ONDE PAREI — preparo da etapa 5 (verificador, 17/11/2026)

Cópia `.claude/worktrees/etapa5-preparo`, ramo `etapa5-preparo-2026-11-17`. Só preparo: nada foi instalado,
desinstalado nem criado no Windows. Nenhum código do programa nem teste foi mudado.

## Decisões que esta tarefa precisa cumprir
D-705, D-711 a D-724, D-727 a D-736 e os achados B1 a B4 (palavras do Samuel no `docs/plano/DECISOES.md`).
Em especial: D-722 ("Sim" a testar no PC dele e desfazer tudo, com a lista do que foi desfeito), D-729 ("pode" tirar
o Editor antigo de 01/09, projetos intactos), D-730 ("k": o instalador antigo fica de reserva).

## Feito
- [x] `lista.md`: a lista item por item, a ordem segura, os prints, os riscos, o tempo.
- [x] `comandos.md`: os comandos por fase, marcados [SÓ LÊ] / [SÓ NO D:] / [MUDA O WINDOWS]. Nenhum rodado.
- [x] `fotografo.py` (só lê) e `comparar.py` (português simples). Testados: duas fotos seguidas dão "igual";
      uma foto mexida de propósito (no scratchpad) dá os "sobrou/sumiu" certos e marca o Editor antigo como esperado.
- [x] Foto de 17/11, sem administrador: `foto-antes-preparo-17-11.json` (nesta pasta e em
      `D:\programas\EditorImpressao\saida_teste\etapa5\fotos\`), **fora do git** (`.gitignore` desta pasta), porque
      tem nomes de contas, programas e regras do PC e o projeto é público.

## O que a foto mostrou (17/11, 09:11)
- OpenSSH servidor: não instalado (sem `sshd`, sem `sshd.exe`); o cliente `ssh.exe` existe; `ssh-agent` desligado.
- `C:\ProgramData\ssh`: existe, vazia. `C:\ProgramData\EditorImpressao`: não existe.
- Conta de testes: não existe; sem `UserList`. Contas: `fotog` (administrador) e `WsiAccount` (comum, já existia).
- Editor antigo de 01/09: instalado (`C:\Program Files\Editor de Impressao`, 434 arquivos, 1.0.0, AppId do Inno), com
  atalho no Menu Iniciar e na Área de trabalho pública.
- Tailscale: serviço rodando, mas o cliente "parado"; placa "Tailscale" sem endereço 100.x.
- Pergunta do Windows na área segura (`PromptOnSecureDesktop = 1`). Antivírus: Windows Defender.
- Pasta dos projetos: 44 arquivos, 13 MB. C: 45,6 GB livres; D: 410 GB.
- Achado: `D:\` dá controle total a "Todos" (só lido com `icacls`).
- Sobra de outro agente (não apaguei): `%LOCALAPPDATA%\velopack\velopack_EditorImpressaoEnsaio.log` (ensaio da etapa 3).

## Falta (para a etapa 5)
- Os nomes que só os construtores sabem (lista, A2), principalmente como o programa instalado procura numa pasta
  de teste.
- As respostas do Samuel (as perguntas estão na entrega à gerente).
