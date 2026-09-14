#!/usr/bin/env bash
set -euo pipefail

ROOT=${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1
ASM=$ROOT/hg002_trio_nocutesv_v1/assembly
OUT=$ROOT/hg002_trio_nocutesv_v1/assembly_derived_v1
REF=${PROJECT_ROOT}/refs/CHM13/chm13v2.0.fa
MM2=/opt/tools/conda-envs/minisv312/bin/minimap2
PAFTOOLS=/opt/tools/conda-envs/minisv312/bin/paftools.js
mkdir -p "$OUT/paf" "$OUT/vcf" "$OUT/logs" "$ROOT/status"
STATUS=$ROOT/status/HG002_ASSEMBLY_DERIVED_V1
printf 'RUNNING\n' > "$STATUS"

run_one(){
  local s=$1 h=$2 fa=$ASM/$s/hap${h}.p_ctg.fa paf=$OUT/paf/${s}.hap${h}.asm5.paf vcf=$OUT/vcf/${s}.hap${h}.asm5.vcf
  if [[ ! -s "$paf" ]]; then
    echo "[$(date -Is)] minimap2 $s hap$h"
    "$MM2" -x asm5 -t 32 --cs "$REF" "$fa" > "$paf"
  fi
  if [[ ! -s "$vcf" ]]; then
    echo "[$(date -Is)] paftools $s hap$h"
    "$PAFTOOLS" call -f "$REF" "$paf" > "$vcf"
  fi
}

export -f run_one
for s in HG002 HG003 HG004; do
  for h in 1 2; do
    run_one "$s" "$h" > "$OUT/logs/${s}.hap${h}.log" 2>&1 &
  done
done
wait

echo "[$(date -Is)] build independent de novo table"
python3 "$ROOT/scripts/build_assembly_derived_dnm_v1.py" --root "$ROOT" --out "$OUT/assembly_derived_dnm.tsv"
printf 'COMPLETE\n' > "$STATUS"
