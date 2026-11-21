# O PC travou na noite de 20/11/2026

Investigação feita só lendo os registros do Windows, em 20/11/2026 às 22h20, sem mudar nada no computador.

## O que aconteceu, em duas frases

Às 21:57:44, no meio de uma partida de Teamfight Tactics, a placa de vídeo NVIDIA parou de funcionar de repente: o jogo anotou "a placa de vídeo foi removida", a tela congelou (a tela verde) e o PC foi religado 30 segundos depois.

Na volta, às 21:58, o Windows não conseguiu ligar a outra parte de vídeo, a AMD (a que cuida da tela e do brilho), e usou o "vídeo de emergência" dele: por isso os ícones ficaram grandes e o brilho não mexia; no reinício seguinte, às 22:04, a AMD voltou ao normal, mas a NVIDIA continua **desativada**.

## Os nossos trabalhos causaram isso?

**Na noite de 20/11: não há nenhuma prova de que sim, e há provas de que não.**

O que é certo:

- **Nenhum comando nosso mexeu em vídeo, driver, brilho ou resolução.** Procurei em todas as conversas e em todos os agentes do dia. As únicas vezes em que aparecem as palavras de desligar aparelho (como "Disable-PnpDevice" ou "pnputil") são da gerente **procurando** por elas, às 22:01, depois do travamento.
- **Na hora do defeito, o agente não estava rodando nada.** O último comando dele terminou às 21:56:58. O seguinte começou às 21:57:46, dois segundos depois de a placa cair, e era só uma busca de palavras num arquivo de texto. Ele nunca devolveu resultado, porque o PC já tinha travado.
- **Os trabalhos pesados tinham acabado bem antes.** A montagem do programa (PyInstaller e vpk) terminou por volta das 19h17. O último teste pesado no PC terminou às 21h02. Nos 55 minutos antes do travamento, só rodaram coisas leves: consultar o GitHub, o git e ler arquivos.
- **O Windows não deu alarme de falta de memória em 20/11.** Ele dá esse alarme quando a memória acaba, e deu em 19/11 (veja abaixo). Em 20/11, nenhum.

O que é suspeita (não dá para provar com o que se lê sem administrador):

- **A parte da Acer que controla ventoinha, energia e placa de vídeo começou a falhar às 21:34**, 23 minutos antes do travamento. O serviço da Predator pergunta ao notebook, a cada um ou dois segundos, como estão as coisas. A partir das 21:34:31 ele recebeu erro em quase todas as perguntas: foram mais de mil até 21:57:45. Antes disso, desde o começo de 19/11, não houve nenhum. Isso sugere que o problema veio do próprio notebook (calor, energia, ou o controle da Acer), e não de um programa.
- **Alguém marcou a NVIDIA como "desativada" às 21:57:42**, dois segundos antes de o jogo perder a placa. O Windows guarda a hora em que cada aparelho foi mexido, e a da NVIDIA é essa. Não dá para saber quem foi sem administrador. Não fomos nós (veja acima), e você estava no meio da partida. Pode ter sido o próprio Windows, o programa da NVIDIA ou o da Acer reagindo à placa que falhava.

**Em 19/11, às 18h03, os nossos trabalhos ajudaram, sim.** É certo:

- Naquele minuto, o Windows anotou que a memória tinha acabado. Os três que mais gastavam: o jogo (4,5 GB), um Python nosso (4,4 GB, era a bateria completa de testes que a gerente rodava no PC) e o programa de sobreposição da NVIDIA (2,3 GB).
- No mesmo segundo caíram, por falta de memória, o programa do Windows que desenha a tela (por isso ela piscou preta e verde), o serviço da Predator, o Chrome e o programa da NVIDIA.
- Na manhã de 19/11, entre 8h41 e 8h46, um Python nosso chegou a gastar 13 GB, também com o jogo aberto.
- Em 17/11, às 18h16, o programa que desenha a tela também caiu por falta de memória, durante os nossos testes do instalador. Nesse dia o Windows não deu o alarme, então aqui é só suspeita.

**Mais um travamento em 20/11, às 13h13.** Você reiniciou o PC às 13:12. Ele ligou às 13:13 e não gravou mais nada por 15 minutos, até ser religado às 13:28. Nenhum agente nosso estava rodando (o último comando foi às 13:11). A causa não se sabe.

## Como consertar a tela e o brilho

Do mais simples ao mais trabalhoso. Pare no passo em que tudo ficar bom.

**Passo 1: conferir se a tela já está certa.** Às 22:20 os registros mostram a tela já de volta ao normal: 1920 × 1080, escala de 125%, reconhecida como "Monitor integrado" pela AMD.

- Clique com o botão direito num lugar vazio da área de trabalho e escolha "Configurações de exibição".
- Em "Escala", deve estar **125% (Recomendado)**. Em "Resolução da tela", **1920 × 1080 (Recomendado)**.
- Se algum não estiver assim, escolha o que tem "(Recomendado)".
- Se só os ícones da área de trabalho estiverem grandes: botão direito na área de trabalho, "Exibir", "Ícones médios".
- Às 22:02 a escala foi mudada, mas essa mudança ficou guardada só para o "vídeo de emergência". Com a AMD funcionando, ela não vale.

**Passo 2: o brilho.** Agora o Windows já consegue controlar o brilho de novo. Mas ele está guardado em **0%, o mínimo**.

- Aperte **Fn + seta para a direita** algumas vezes (nos notebooks Acer, é a tecla de aumentar o brilho).
- Ou aperte **Windows + A** e arraste a barra do sol para a direita.
- O que deve ver: a tela clareando. Se a barra do sol não aparecer, reinicie o PC (Iniciar, Energia, Reiniciar) e tente de novo.

**Passo 3: ligar a placa NVIDIA de novo.** Enquanto ela estiver desativada, o jogo e tudo o que usa a placa NVIDIA ficam mais lentos. O jogo já está rodando na AMD desde as 22:07.

- Clique com o botão direito no botão Iniciar e escolha **"Gerenciador de Dispositivos"**.
- Abra **"Adaptadores de vídeo"**. A "NVIDIA GeForce GTX 1650" aparece com uma setinha para baixo no desenho: é o sinal de desativada.
- Clique nela com o botão direito e escolha **"Habilitar dispositivo"**. O Windows pode perguntar se você permite: essa pergunta é dele, e quem decide é você.
- O que deve ver: a setinha some, e a tela pode piscar uma vez.
- Reinicie o PC (Iniciar, Energia, Reiniciar).
- Se, ao jogar de novo, a tela travar outra vez, é sinal de defeito na placa NVIDIA ou no programa dela (o "driver", que faz a placa conversar com o Windows). Aí vá para o passo 5.

**Passo 4: se a tela congelar de novo e o PC ainda responder.** Aperte ao mesmo tempo **Windows + Ctrl + Shift + B**. Isso reinicia só o vídeo: a tela fica preta um segundo, dá um bipe e volta. Muitas vezes evita desligar à força.

**Passo 5 (o mais trabalhoso): atualizar os programas do vídeo.**

- O programa da AMD é de agosto de 2024. O da NVIDIA é de abril de 2026.
- Baixe os dois na página de suporte da Acer, pelo modelo do notebook (o código fica na etiqueta embaixo dele). O da NVIDIA também pode vir pelo aplicativo da NVIDIA.
- Instale primeiro o da AMD, reinicie, depois o da NVIDIA, e reinicie de novo.
- Se a NVIDIA continuar caindo mesmo assim, vale levar a uma assistência técnica: pode ser calor ou defeito da placa.

## Como evitar que aconteça de novo

- **Não jogar enquanto os nossos trabalhos pesados rodam no PC.** São eles: montar o programa, empacotar, a bateria completa de testes. Em 19/11, jogo e testes juntos acabaram com a memória duas vezes. Sugestão para a gerente: antes de um trabalho pesado, conferir a memória livre e pedir para fechar o jogo, ou mandar a bateria completa para o GitHub.
- **Deixar a ventilação livre.** Use o notebook numa mesa dura, nunca em cama ou almofada. No PredatorSense, deixe a ventoinha no modo automático ou no mais forte enquanto joga.
- **Olhar a temperatura da placa no PredatorSense** quando for jogar depois de religar a NVIDIA. Se ela passar de uns 85 °C, ou se a placa cair de novo, o problema é do notebook, não de programa.
- **Atualizar o programa do vídeo da AMD** (passo 5), porque ele está dois anos atrás do da NVIDIA.

## A tela verde: o que é

- **Este Windows não é de teste.** É o Windows 11 Home normal, versão 25H2, com a atualização de novembro de 2026 (26200.9974). Ele não está inscrito no programa de testes da Microsoft (Insider).
- **A tela verde de erro do Windows só existe nas versões de teste.** Nas versões normais, a tela de erro era azul, e desde 2025 é preta.
- **E não houve tela de erro do Windows nesta noite.** Quando ela acontece, o Windows guarda o código do erro e um arquivo do travamento. Desta vez o código ficou zerado e nenhum arquivo novo foi gravado (o último é de 20/10).
- **O mais provável:** a imagem parada da placa de vídeo que travou. Quando a placa trava com a memória de imagem vazia, a tela costuma ficar verde. Isso é explicação provável, não certeza.

## Para consulta: a linha do tempo, com as provas

Horas do relógio do PC.

| Hora | O que aconteceu | Onde está escrito |
|---|---|---|
| 20/11 13:12 | Você reinicia pelo menu Iniciar | registro do Sistema, aviso 1074 |
| 13:13 a 13:28 | O PC liga e não grava mais nada por 15 minutos; religado à força | Sistema, avisos 41 e 6008 |
| 17:57 a 19:17 | Montagem e envio do programa (PyInstaller, vpk), pesados | conversa da gerente |
| 20:06 | Jogo aberto, usando a placa NVIDIA | registro do jogo (TFT) |
| 21:02 | Último teste pesado nosso no PC | conversa da gerente |
| 21:34:31 | Começam os erros do controle da Acer (mais de mil até 21:57:45) | registro do WMI, aviso 5858, "AcerGamingFunction" |
| 21:56:58 | Termina o último comando do agente antes do travamento | conversa do agente |
| 21:57:42 | A ficha da NVIDIA no Windows é mexida (ela ficou "desativada") | hora gravada na ficha do aparelho |
| 21:57:44 | O jogo anota: "placa de vídeo removida" | registro do jogo: "GPU crash detected", "DXGI_ERROR_DEVICE_REMOVED" |
| 21:57:45 | Última pergunta do serviço da Predator registrada | registro do WMI |
| 21:57:46 | O agente começa uma busca de palavras, que nunca termina | arquivo de saída vazio do agente |
| 21:57:48 | O jogo tenta gravar o relatório de falha (fica vazio) | pasta de falhas do jogo |
| 21:58:18 | O PC liga de novo | Sistema, aviso 12 |
| 21:58:35 | A tela entra como "Monitor genérico", ligada pelo vídeo de emergência | registro dos aparelhos, aviso 442 |
| 22:02:55 | Mudança da escala, guardada só para o vídeo de emergência | registro de escala da tela |
| 22:04:03 | Você reinicia pelo menu Iniciar | Sistema, aviso 1074 |
| 22:04:29 | Liga: AMD funcionando, tela "Monitor integrado"; NVIDIA desativada | estado dos aparelhos agora |
| 22:07 | Jogo aberto de novo, agora na AMD | registro do jogo |

**Por que o Windows diz que o PC desligou às 21:28:18, se o agente rodou até 21:57?** Essa hora não é a do travamento. O Windows grava uma marca de "ainda estou ligado" uma vez por hora, contando da hora em que o PC ligou. O PC tinha ligado às 13:28:18, e a última marca saiu às 21:28:18, oito horas depois, no mesmo segundo. O travamento veio depois da marca. O registro do Sistema ficou quieto de 21:20 a 21:58 porque não aconteceu nada que ele anote. Outros registros do Windows (o do WMI e o do PowerShell) têm anotações até 21:57:45.

**Como estão as peças agora (22:20):**

- AMD Radeon: funcionando. Programa de agosto de 2024.
- NVIDIA GeForce GTX 1650: desativada (código 22, a marca de desativada está gravada). Programa de abril de 2026, instalado em 15/05/2026.
- Nenhum programa de vídeo foi trocado pelo Windows Update nos últimos dias. A última atualização do Windows foi a de segurança de 11/11.
- Serviços da NVIDIA ("NVIDIA Display Container") e da Acer ("Predator Service" e "PSAgent"): rodando.
- Tela: 1920 × 1080, escala 125%, brilho guardado em 0%.

**O que não deu para ler sem administrador** (não pedi licença):

- as pastas de relatórios de travamento do Windows (`C:\Windows\LiveKernelReports` e `C:\Windows\Minidump`). Dá só para ver a data delas: 02/11 e 20/10, nenhuma de 20/11;
- a temperatura;
- quem marcou a NVIDIA como desativada.
