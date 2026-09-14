#!/usr/bin/env bash
set -euo pipefail

BASE=${PROJECT_ROOT}/results/formal_chm13
ROOT=$BASE/innovation/pedsv_ml/pilot_v1
DATA=/opt/tools/HG002_trio_CHM13
ASM=$ROOT/hg002_trio_nocutesv_v1/assembly
HIFIASM=/opt/tools/conda-envs/hifiasm/bin/hifiasm
SAMTOOLS=/usr/bin/samtools
PIGZ=/usr/bin/pigz
LOG=$ROOT/logs/hg002_trio_hifiasm_v1.log
STATUS=$ROOT/status/HG002_TRIO_HIFIASM_V1

mkdir -p "$ASM" "$ROOT/logs" "$ROOT/status"
exec >> "$LOG" 2>&1
printf 'RUNNING\n' > "$STATUS"

bam_of(){
  case "$1" in
    HG002) echo "$DATA/HG002_PacBio-HiFi-Revio_20231031_48x_CHM13v2.0.bam" ;;
    HG003) echo "$DATA/HG003_PacBio-HiFi-Revio_20231031_46x_CHM13v2.0.bam" ;;
    HG004) echo "$DATA/HG004_PacBio-HiFi-Revio_20231031_36x_CHM13v2.0.bam" ;;
    *) return 1 ;;
  esac
}

assemble_one(){
  local sample=$1 bam fq out gfa1 gfa2 fa1 fa2
  bam=$(bam_of "$sample")
  out="$ASM/$sample"
  fq="$out/$sample.hifi.fastq.gz"
  mkdir -p "$out"
  [[ -s "$bam" && -s "$bam.bai" ]]

  if [[ ! -s "$fq" ]]; then
    echo "[$(date -Is)] $sample BAM -> FASTQ"
    "$SAMTOOLS" fastq -@ 32 -F 0x900 "$bam" | "$PIGZ" -p 32 > "$fq.tmp"
    mv "$fq.tmp" "$fq"
  else
    echo "[$(date -Is)] $sample FASTQ exists; skip conversion"
  fi

  gfa1="$out/$sample.bp.hap1.p_ctg.gfa"
  gfa2="$out/$sample.bp.hap2.p_ctg.gfa"
  if [[ ! -s "$gfa1" || ! -s "$gfa2" ]]; then
    echo "[$(date -Is)] $sample hifiasm"
    "$HIFIASM" -t 96 -o "$out/$sample" "$fq" > "$out/hifiasm.log" 2>&1
  else
    echo "[$(date -Is)] $sample hifiasm GFA exists; skip assembly"
  fi

  fa1="$out/hap1.p_ctg.fa"
  fa2="$out/hap2.p_ctg.fa"
  if [[ ! -s "$fa1" ]]; then
    awk -F '\t' '$1=="S" && $3!="*" {print ">"$2"\n"$3}' "$gfa1" > "$fa1"
  fi
  if [[ ! -s "$fa2" ]]; then
    awk -F '\t' '$1=="S" && $3!="*" {print ">"$2"\n"$3}' "$gfa2" > "$fa2"
  fi
  "$SAMTOOLS" faidx "$fa1"
  "$SAMTOOLS" faidx "$fa2"
  # samtools quickcheck validates BAM/CRAM, not FASTA.  FASTA integrity is
  # checked by faidx plus non-empty sequence/header checks below.
  [[ -s "$fa1" && -s "$fa2" ]]
  grep -q '^>' "$fa1"
  grep -q '^>' "$fa2"
  echo "[$(date -Is)] $sample complete"
}

# Sequential execution limits peak memory and I/O pressure.  Parent assemblies
# are produced first because Minisv needs HG003/HG004 before HG002 evaluation.
for sample in HG003 HG004 HG002; do
  assemble_one "$sample"
done

printf 'COMPLETE\n' > "$STATUS"
