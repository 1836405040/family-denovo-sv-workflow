# Two-family analysis flow

```mermaid
flowchart TD
  A[Input manifests and checksums] --> B{Pedigree branch}
  B --> C[HG002 trio assembly and QC]
  B --> D[Five-child parent provenance/QC and child assembly]
  C --> E[Assembly-derived SV calls]
  D --> F[Assembly-derived SV calls]
  E --> G[Sniffles2 / LongcallD / TRGT-denovo]
  G --> H[Child-only normalization]
  H --> I[Caller union and deduplication]
  I --> J[Per-caller and joint Minisv C2/C3]
  E --> K[HG002 method comparison]
  F --> L[Five-child caller/Minisv comparison]
  L --> M[Gap, MAPQ, repeat, contig-end, double-haplotype and parent-match audit]
  J --> N[Results tables and manifests]
  K --> N
  M --> N
```

The endpoint is a reproducible results package and an explanation audit for the five-child discrepancy. This workflow does not define a new truth set and does not include the legacy 17-truth rescue experiments.
