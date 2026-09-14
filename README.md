# Family de novo SV analysis: reproducible workflow

This repository contains the analysis workflow used to compare caller/Minisv results with assembly-derived structural variants in two pedigree datasets.

The repository is intended for code review and reproducibility. Sequencing data, assemblies, PAF/VCF outputs, server paths, SSH keys, and credentials are not included.

## Scope

The workflow starts with validated input manifests and ends with a reproducible results table plus an anomaly audit.

It contains two branches:

- **HG002 trio**: HG002 child with HG003/HG004 parents. This branch runs haplotype assembly, assembly-derived SV extraction, Sniffles2, LongcallD, TRGT-denovo, child-only normalization, caller union/deduplication, and Minisv C2/C3.
- **Five-child pedigree**: NA12877/NA12878 parents with NA12879, NA12881, NA12882, NA12885, and NA12886 children. This branch includes parent assembly provenance/QC, child assembly, assembly-derived calling, comparison with the existing caller/Minisv results, and diagnosis of the unexpectedly large `both child haps / no parent match` category.

The 17 legacy truth records, their rescue experiments, VISOR work, and any new truth-definition procedure are outside this release.

## Start and end

Start:

1. CHM13 reference FASTA and index are registered.
2. BAM/BAI and assembly inputs are registered for each family.
3. Software versions, parameters, file paths, and checksums are recorded.
4. Input integrity and pedigree relationships pass validation.

End:

1. Per-caller and joint Minisv C2/C3 counts are reproducible.
2. Assembly-derived event classes and event-level overlap are reproducible.
3. The five-child anomaly audit reports QC strata, parent-match evidence, double-haplotype consistency, and unresolved loci.
4. A result table, command manifest, and input checksum table are produced.

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
  -> cross-method overlap and five-child anomaly audit
  -> final tables and manifests
```

See [`workflow/CODE_MAP.md`](workflow/CODE_MAP.md), [`workflow/stage_boundaries.tsv`](workflow/stage_boundaries.tsv), and [`workflow/flowchart.md`](workflow/flowchart.md).

## Configuration

Copy `config/config.example.env` to a private local file and fill in paths. Do not commit the local file. Copy `config/samples.example.tsv` and replace sample paths with paths available on the execution system.

The current server implementation uses `minimap2 -x asm5 --cs` and `paftools.js call` for assembly-derived calls, with an initial absolute SV length threshold of 50 bp, breakpoint tolerance of 100 bp, and absolute length tolerance of 50 bp. The published pipeline must keep these values in the parameter file rather than hard-coding them.

The existing table's `defaultbase` Minisv runs and tuned/frozen runs are separate experiments. Their parameters must be recorded separately and must not be combined by directory name alone.

## Repository layout

```text
config/                 public templates; local paths are ignored
scripts/                script inventory and publication notes
workflow/               stage map and data-product contracts
results/                ignored; only small, de-identified summaries belong here
```

The exact server scripts used for the previous table are listed in `scripts/SCRIPT_INVENTORY.md`. Before the first public release, each script should be converted to use the configuration templates instead of server-specific absolute paths.

## Review rules

- Preserve raw caller records, source IDs, read names, deduplication decisions, and command parameters.
- Do not compare total counts unless the event definition and thresholds are identical.
- Treat `both child haps / no parent match` as a candidate class, not as confirmed de novo SV.
- Keep assembly-derived classification independent of Minisv pass/fail to avoid circular evaluation.
- Never commit BAM/FASTA/VCF data, SSH configuration, private keys, access tokens, or server credentials.
