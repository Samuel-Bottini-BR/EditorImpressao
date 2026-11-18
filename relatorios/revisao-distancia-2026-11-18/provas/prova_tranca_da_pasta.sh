#!/usr/bin/env bash
# Prova (18/11/2026, revisao-distancia): o mesmo comando de "trancar a pasta" que
# core/testes_a_distancia._comando_proteger_a_pasta usa, SEM o /setowner (que pede
# administrador), numa pasta de rascunho da conta comum. Nada do programa roda.
#
# Resultado de 18/11/2026 12:00 no PC do Samuel (sem administrador, sem janela):
#   com /T  -> a pasta fica certa, mas o ARQUIVO que ja estava dentro fica com a
#              lista de licencas VAZIA (ninguem le nem grava), e o icacls devolve 0;
#   sem /T  -> o arquivo herda da pasta: Sistema e Administradores tudo, Usuarios so le;
#              a conta comum le e nao grava (o que se queria).
# Uso: bash prova_tranca_da_pasta.sh <pasta de rascunho>
set -u
R="${1:?pasta de rascunho}"
export MSYS2_ARG_CONV_EXCL='*'
mkdir -p "$R/com-T" "$R/sem-T"
echo teste > "$R/com-T/antes.json"; echo teste > "$R/sem-T/antes.json"
LIC=('*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX')
icacls "$R/com-T" /inheritance:r /grant:r "${LIC[@]}" /T /C; echo "codigo com /T: $?"
icacls "$R/com-T/antes.json"; cat "$R/com-T/antes.json" || echo "NAO LEU (com /T)"
icacls "$R/sem-T" /inheritance:r /grant:r "${LIC[@]}" /C; echo "codigo sem /T: $?"
icacls "$R/sem-T/antes.json"; cat "$R/sem-T/antes.json" && echo "LEU (sem /T)"
echo x > "$R/sem-T/novo.txt" 2>/dev/null && echo "GRAVOU (nao devia)" || echo "NAO GRAVOU (certo)"
# devolve as licencas de antes, para a pasta de rascunho poder ser apagada
icacls "$R/com-T" /reset /T /C /Q >/dev/null; icacls "$R/sem-T" /reset /T /C /Q >/dev/null
