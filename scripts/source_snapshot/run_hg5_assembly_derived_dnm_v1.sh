#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1
REF=${PROJECT_ROOT}/refs/CHM13/chm13v2.0.fa
OUT=$ROOT/hg5_assembly/assembly_derived_dnm_v1
V=$OUT/vcf
MM=/opt/tools/conda-envs/minisv312/bin/minimap2
PT=/opt/tools/conda-envs/minisv312/bin/paftools.js
PY=/opt/tools/conda-envs/minisv312/bin/python
export PATH=/opt/tools/conda-envs/minisv312/bin:$PATH
mkdir -p "$V" "$OUT/logs" "$ROOT/status"
printf 'RUNNING\n' > "$ROOT/status/HG5_ASSEMBLY_DERIVED_DNM_V1"

align_one() {
  local sample=$1 hap=$2 fa=$3
  local paf="$V/${sample}.hap${hap}.asm5.paf" vcf="$V/${sample}.hap${hap}.asm5.vcf"
  if [[ ! -s "$paf" ]]; then "$MM" -x asm5 -t 16 --cs "$REF" "$fa" > "$paf"; fi
  if [[ ! -s "$vcf" ]]; then "$PT" call -f "$REF" "$paf" > "$vcf"; fi
}
export -f align_one
export ROOT REF OUT V MM PT

for s in NA12877 NA12878; do
  for h in 1 2; do
    fa=${PROJECT_ROOT}/results/formal_chm13/assembly/parents/hap_fasta/${s}.hap${h}.p_ctg.fa
    align_one "$s" "$h" "$fa" > "$OUT/logs/${s}.hap${h}.log" 2>&1 &
  done
done
wait

run_child() {
  local s=$1
  local base=$ROOT/hg5_assembly/five_children_hifiasm_v1/$s
  if [[ ! -s "$base/hap1.p_ctg.fa" || ! -s "$base/hap2.p_ctg.fa" ]]; then
    echo "SKIP_MISSING_ASSEMBLY $s" >&2
    return 0
  fi
  for h in 1 2; do align_one "$s" "$h" "$base/hap${h}.p_ctg.fa" > "$OUT/logs/${s}.hap${h}.log" 2>&1; done
}
export -f run_child
running=0
for s in NA12879 NA12881 NA12882 NA12885 NA12886; do
  while (( running >= 3 )); do wait -n; running=$((running-1)); done
  run_child "$s" &
  running=$((running+1))
done
while (( running > 0 )); do wait -n; running=$((running-1)); done

"$PY" "$ROOT/scripts/build_hg5_assembly_derived_dnm_v1.py"
printf 'COMPLETE\n' > "$ROOT/status/HG5_ASSEMBLY_DERIVED_DNM_V1"
echo "ALL_COMPLETE $(date -Is)"
