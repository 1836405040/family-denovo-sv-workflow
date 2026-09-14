#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1
OUT=$ROOT/hg5_assembly/five_children_hifiasm_v1/NA12886
BAM=${PROJECT_ROOT}/results/formal_chm13/input/chm13_bam/NA12886.CHM13.primary.bam
SAMTOOLS=/usr/bin/samtools
PIGZ=/usr/bin/pigz
HIFIASM=/opt/tools/conda-envs/hifiasm/bin/hifiasm
mkdir -p "$OUT"
echo "START $(date -Is) NA12886" > "$OUT/run.log"
test -s "$BAM" && test -s "$BAM.bai"
FQ=$OUT/NA12886.hifi.fastq.gz
if [[ ! -s "$FQ" ]]; then
  echo "BAM_TO_FASTQ $BAM" | tee -a "$OUT/run.log"
  "$SAMTOOLS" fastq -@ 16 -F 0x900 "$BAM" | "$PIGZ" -p 16 > "$FQ.tmp"
  mv "$FQ.tmp" "$FQ"
fi
if [[ ! -s "$OUT/NA12886.bp.hap1.p_ctg.gfa" || ! -s "$OUT/NA12886.bp.hap2.p_ctg.gfa" ]]; then
  echo "HIFIASM_THREADS 48" | tee -a "$OUT/run.log"
  "$HIFIASM" -t 48 -o "$OUT/NA12886" "$FQ" > "$OUT/hifiasm.log" 2>&1
fi
for h in 1 2; do
  GFA=$OUT/NA12886.bp.hap${h}.p_ctg.gfa
  FA=$OUT/hap${h}.p_ctg.fa
  if [[ ! -s "$FA" ]]; then
    awk -F '\t' '$1=="S" && $3!="*" {print ">"$2"\n"$3}' "$GFA" > "$FA"
  fi
  "$SAMTOOLS" faidx "$FA"
  test -s "$FA" && grep -q '^>' "$FA"
done
echo "COMPLETE $(date -Is)" | tee -a "$OUT/run.log"
