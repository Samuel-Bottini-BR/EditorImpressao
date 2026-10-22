#!/bin/bash
# Verificador 22/10: rodadas pelo caminho inteiro, uma por processo, em sequência.
# 2.4 (antes = código 9804b98, depois = novo com margens iguais), somas "desligado = igual",
# 2.10 (uma x duas camadas) e 2.17 (luz). Saída em trabalho/<item>/.
export PYTHONIOENCODING=utf-8
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
W=/d/programas/EditorImpressao/.claude/worktrees
V=$W/vfr22-novo/relatorios/conferir/ferramentas-2026-10-22
S=$V/scripts/caminho.py
T=$V/trabalho
log() { echo "$(date +%H:%M:%S) $*" >> $T/rodada1.log; }

declare -A LIVROS=(
 [graduale]="graduale_p221 graduale_p222 graduale_p223"
 [horas]="horas_p011 horas_p013 horas_p014 horas_p047"
 [palatino]="palatino_p005 palatino_p007 palatino_p009 palatino_p010 palatino_p057 palatino_p066 palatino_p067"
 [opusmajus]="opusmajus_p003 opusmajus_p011 opusmajus_p020 opusmajus_p165 opusmajus_p256"
)
for nome in graduale horas palatino opusmajus; do
  log "2.4 $nome antes"
  $PY $S --raiz $W/vfr22-antes livro --saida $T/2.4/$nome-antes.pdf ${LIVROS[$nome]} >> $T/rodada1.log 2>&1
  log "2.4 $nome depois"
  $PY $S --raiz $W/vfr22-novo livro --saida $T/2.4/$nome-depois.pdf --campos '{"margens_iguais": true}' ${LIVROS[$nome]} >> $T/rodada1.log 2>&1
done

# somas: desligado de fabrica sai igual ao antigo (alternado)
for f in preto_e_branco melhorar; do
  for lado in antes novo; do
    log "somas $f $lado"
    $PY $S --raiz $W/vfr22-$lado somas --saida $T/somas/$lado-$f.json --filtro $f graduale_p222 horas_p014 palatino_p057 escola_p007 horas_p011 marial_p007 >> $T/rodada1.log 2>&1
  done
done

# 2.10: um livro de 6 paginas, Preto e branco e Melhorar, uma x duas camadas
C210="horas_p011 horas_p013 escola_p007 palatino_p005 graduale_p221 opusmajus_p020"
for f in preto_e_branco melhorar magico_pro; do
  log "2.10 $f uma"
  $PY $S --raiz $W/vfr22-novo livro --saida $T/2.10/$f-uma.pdf --campos "{\"filtro_padrao\": \"$f\"}" $C210 >> $T/rodada1.log 2>&1
  log "2.10 $f duas"
  $PY $S --raiz $W/vfr22-novo livro --saida $T/2.10/$f-duas.pdf --campos "{\"filtro_padrao\": \"$f\", \"pdf_em_duas_camadas\": true}" $C210 >> $T/rodada1.log 2>&1
done

# 2.17: um livro de 6 paginas
C217="marial_p007 graduale_p221 horas_p047 boecio_p007 escola_p035 palatino_p010"
run217() { log "2.17 $1"; $PY $S --raiz $W/vfr22-novo livro --saida $T/2.17/$1.pdf --campos "{\"filtro_padrao\": \"$2\"}" --pagina "$3" $C217 >> $T/rodada1.log 2>&1; }
run217 pb-hoje preto_e_branco '{}'
run217 pb-igualar preto_e_branco '{"luz_igualar": true}'
run217 pb-suavizar preto_e_branco '{"luz_suavizar": true}'
run217 pb-chuvisco20 preto_e_branco '{"luz_chuvisco": 20}'
run217 mel-hoje melhorar '{}'
run217 mel-igualar melhorar '{"luz_igualar": true}'
run217 mel-chuvisco20 melhorar '{"luz_chuvisco": 20}'
run217 mel-chuvisco50 melhorar '{"luz_chuvisco": 50}'
run217 orig-igualar original '{"luz_igualar": true}'
run217 orig-hoje original '{}'
log "FIM"
