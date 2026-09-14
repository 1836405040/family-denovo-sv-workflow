#!/usr/bin/env bash
set -euo pipefail
BASE=${PROJECT_ROOT}/results/formal_chm13
ROOT=$BASE/innovation/pedsv_ml/pilot_v1
DATA=/opt/tools/HG002_trio_CHM13
REF=${PROJECT_ROOT}/refs/CHM13/chm13v2.0.fa
SNIFF=/opt/tools/conda-envs/sniffles2/bin/sniffles
LONG=$ROOT/software/longcallD_v0.0.11/longcallD
OUT=$ROOT/hg002_trio_nocutesv_v1/callers_raw
LOG=$ROOT/logs/hg002_trio_callers_v1.log
STATUS=$ROOT/status/HG002_TRIO_CALLERS_V1
mkdir -p "$OUT/sniffles2" "$OUT/longcallD" "$ROOT/logs" "$ROOT/status"
exec > >(tee -a "$LOG") 2>&1
printf 'RUNNING\n' > "$STATUS"

bam_of(){
  case "$1" in
    HG002) echo "$DATA/HG002_PacBio-HiFi-Revio_20231031_48x_CHM13v2.0.bam";;
    HG003) echo "$DATA/HG003_PacBio-HiFi-Revio_20231031_46x_CHM13v2.0.bam";;
    HG004) echo "$DATA/HG004_PacBio-HiFi-Revio_20231031_36x_CHM13v2.0.bam";;
  esac
}

run_sniffles(){
  local s=$1 b=$(bam_of "$1") o=$OUT/sniffles2/$1
  [[ -s "$o.vcf" && -s "$o.snf" ]] && { echo "SKIP sniffles2 $s"; return; }
  "$SNIFF" --input "$b" --vcf "$o.vcf" --snf "$o.snf" --reference "$REF" --threads 32 --minsvlen 50 --output-rnames
  grep -q '^#CHROM' "$o.vcf"
}

run_longcallD(){
  local s=$1 b=$(bam_of "$1") o=$OUT/longcallD/$1
  [[ -s "$o/$s.longcallD.raw.vcf" && -s "$o/$s.longcallD.refined.bam" ]] && { echo "SKIP longcallD $s"; return; }
  mkdir -p "$o"
  "$LONG" call --hifi --autosome-XY --min-sv-len 30 --refine-aln --out-sv-rnames --threads 32 --sample-name "$s" --out-vcf "$o/$s.longcallD.raw.vcf" -b "$o/$s.longcallD.refined.raw.bam" "$REF" "$b"
  samtools sort -@ 16 -o "$o/$s.longcallD.refined.bam" "$o/$s.longcallD.refined.raw.bam"
  samtools index -@ 8 "$o/$s.longcallD.refined.bam"
  samtools quickcheck "$o/$s.longcallD.refined.bam"
  grep -q '^#CHROM' "$o/$s.longcallD.raw.vcf"
}

for s in HG002 HG003 HG004; do
  run_sniffles "$s" &
  while (( $(jobs -rp | wc -l) >= 2 )); do wait -n; done
done
wait
for s in HG002 HG003 HG004; do
  run_longcallD "$s" &
  while (( $(jobs -rp | wc -l) >= 2 )); do wait -n; done
done
wait
printf 'COMPLETE\n' > "$STATUS"
