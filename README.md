# Family de novo SV analysis: reproducible workflow

This repository contains the analysis workflow used to compare caller/Minisv results with assembly-derived structural variants in two pedigree datasets.

The repository is intended for code review and reproducibility. Sequencing data, assemblies, PAF/VCF outputs, server paths, SSH keys, and credentials are not included.

## Scope

The workflow starts with validated input manifests and currently ends with a reproducible results table and method/parameter manifests. 

It contains two branches:

- **HG002 trio**: HG002 child with HG003/HG004 parents. This branch runs haplotype assembly, assembly-derived SV extraction, Sniffles2, LongcallD, TRGT-denovo, child-only normalization, caller union/deduplication, and Minisv C2/C3.
- **Five-child pedigree**: NA12877/NA12878 parents with NA12879, NA12881, NA12882, NA12885, and NA12886 children. This release includes the existing child assembly, assembly-derived results, and existing caller/Minisv results for reproducibility.


## Start and end

Start:

1. CHM13 reference FASTA and index are registered.
2. BAM/BAI and assembly inputs are registered for each family.
3. Software versions, parameters, file paths, and checksums are recorded.
4. Input integrity and pedigree relationships pass validation.

End:

1. Per-caller and joint Minisv C2/C3 counts are reproducible.
2. Assembly-derived event classes and the currently available method-level comparisons are reproducible.
3. Existing two-family result tables, command manifests, and input checksum tables are documented.

## Workflow

```text
input manifest and validation
  -> phased assembly (HG002 trio and five children)
  -> minimap2 asm5 --cs + paftools.js assembly-derived calls
  -> Sniffles2 / LongcallD / TRGT-denovo calls
  -> child-only normalization
  -> caller union and duplicate removal
  -> per-caller and joint Minisv C2/C3
  -> assembly-derived family classification
  -> cross-method overlap and existing result summaries
  -> final tables and manifests
  -> future five-child anomaly audit (not yet performed)
```

See [`workflow/CODE_MAP.md`](workflow/CODE_MAP.md), [`workflow/stage_boundaries.tsv`](workflow/stage_boundaries.tsv), and [`workflow/flowchart.md`](workflow/flowchart.md).

## Configuration

Copy `config/config.example.env` to a private local file and fill in paths. Do not commit the local file. Copy `config/samples.example.tsv` and replace sample paths with paths available on the execution system.

The current server implementation uses `minimap2 -x asm5 --cs` and `paftools.js call` for assembly-derived calls, with an initial absolute SV length threshold of 50 bp, breakpoint tolerance of 100 bp, and absolute length tolerance of 50 bp.

## Repository layout

```text
config/                 public templates; local paths are ignored
scripts/                script inventory and publication notes
workflow/               stage map and data-product contracts
results/                ignored; only small, de-identified summaries belong here
```


