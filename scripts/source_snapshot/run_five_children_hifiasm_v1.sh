#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1
DATA=${PROJECT_ROOT}/data/hifi/public_g2_g3/source_bam
OUTROOT=$ROOT/hg5_assembly/five_children_hifiasm_v1
HIFIASM=/opt/tools/conda-envs/hifiasm/bin/hifiasm
SAMTOOLS=/usr/bin/samtools
PIGZ=/usr/bin/pigz
STATUS=$ROOT/status/HG5_CHILDREN_HIFIASM_V1
LOGROOT=$ROOT/logs/hg5_children_hifiasm_v1
mkdir -p "$OUTROOT" "$LOGROOT" "$ROOT/status"
printf 'RUNNING\n' > "$STATUS"

bam_for() {
  case "$1" in
    NA12879|NA12881|NA12882|NA12885) echo "$DATA/$1.CHM13.haplotagged.bam" ;;
    NA12886) echo "$ROOT/../../../input/chm13_bam/NA12886.CHM13.primary.bam" ;;
    *) return 1 ;;
  esac
}

assemble_one() {
  local s=$1 bam out fq gfa1 gfa2 fa1 fa2
  bam=$(bam_for "$s")
  out="$OUTROOT/$s"
  fq="$out/$s.hifi.fastq.gz"
  mkdir -p "$out"
  printf 'START %s %s\n' "$(date -Is)" "$s" > "$out/run.log"
  [[ -s "$bam" && -s "$bam.bai" ]]
  if [[ ! -s "$fq" ]]; then
    echo "BAM_TO_FASTQ $bam" | tee -a "$out/run.log"
    "$SAMTOOLS" fastq -@ 16 -F 0x900 "$bam" | "$PIGZ" -p 16 > "$fq.tmp"
    mv "$fq.tmp" "$fq"
  fi
  gfa1="$out/$s.bp.hap1.p_ctg.gfa"
  gfa2="$out/$s.bp.hap2.p_ctg.gfa"
  if [[ ! -s "$gfa1" || ! -s "$gfa2" ]]; then
    echo "HIFIASM_THREADS 48" | tee -a "$out/run.log"
    "$HIFIASM" -t 48 -o "$out/$s" "$fq" > "$out/hifiasm.log" 2>&1
  fi
  for h in 1 2; do
    local gfa="$out/$s.bp.hap${h}.p_ctg.gfa"
    local fa="$out/hap${h}.p_ctg.fa"
    if [[ ! -s "$fa" ]]; then
      awk -F '\t' '$1=="S" && $3!="*" {print ">"$2"\n"$3}' "$gfa" > "$fa"
    fi
    "$SAMTOOLS" faidx "$fa"
    [[ -s "$fa" ]] && grep -q '^>' "$fa"
  done
  printf 'READS %s\n' "$(zcat "$fq" | awk 'END{print NR/4}')" >> "$out/run.log"
  printf 'COMPLETE %s\n' "$(date -Is)" >> "$out/run.log"
}

export -f assemble_one bam_for
export ROOT DATA OUTROOT HIFIASM SAMTOOLS LOGROOT

running=0
for s in NA12879 NA12881 NA12882 NA12885 NA12886; do
  while (( running >= 3 )); do
    wait -n
    running=$((running-1))
  done
  assemble_one "$s" > "$LOGROOT/$s.launch.log" 2>&1 &
  running=$((running+1))
done
while (( running > 0 )); do
  wait -n
  running=$((running-1))
done

for s in NA12879 NA12881 NA12882 NA12885 NA12886; do
  [[ -s "$OUTROOT/$s/hap1.p_ctg.fa" && -s "$OUTROOT/$s/hap2.p_ctg.fa" ]]
done
printf 'COMPLETE\n' > "$STATUS"
echo "ALL_COMPLETE $(date -Is)"
