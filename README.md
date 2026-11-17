# metaLncRNA

Consensus identification of long non-coding RNAs. metaLncRNA runs seven published
coding-potential predictors, each **exactly as released by its authors** and isolated in its own
container, and calls a transcript coding or noncoding by **majority vote of the tools' own verdicts**.

| Tool | Version | Built from |
|---|---|---|
| CNCI | v2 (`745e2d1`) | the authors' code (Python 2.7) |
| CPPred | 2018-05-17 tarball | the authors' code (Python 2.7) |
| LGC | 1.0 download | the authors' code (Python 2.7) |
| CPAT | 3.0.5 | BioContainers image + the authors' prebuilt models |
| CPC2 | 1.0.1 | BioContainers image |
| PLEK | 1.2 | BioContainers image |
| RNAsamba | 0.2.5 | BioContainers image + the authors' pretrained weights |

All seven images are built the same way from [`containers/`](containers/README.md): each is
self-contained (unmodified tool, dependencies, model files verified by SHA-256 at build time), has
a `run-<tool>` entry point and OCI provenance labels. Published images are referenced by digest in
[`src/metalncrna/manifest.toml`](src/metalncrna/manifest.toml).

## Consensus rule

1. Each tool gives its own label with its own default parameters. CPAT does not emit a label, so the
   authors' published species cut-off is applied (human 0.364, mouse 0.44, fly 0.39, zebrafish 0.38);
   transcripts in which CPAT finds no ORF are counted as noncoding.
2. A tool that does not report on a transcript **abstains** (PLEK skips transcripts ≤ 200 nt, CNCI
   skips transcripts with ambiguous bases, CPAT has no plant model, a tool may have failed...).
3. Among the tools that voted: more coding votes → `coding`, more noncoding votes → `noncoding`,
   a tie → `ambiguous`, no votes → `unclassified`.

`lncrna.fasta` contains the `noncoding` transcripts of at least `--min-length` nt (default 200, the
conventional lncRNA length threshold), optionally requiring at least `--min-agree N` noncoding votes.

## Install

Requirements: Python ≥ 3.11 and Docker or Apptainer/Singularity.

```sh
pip install .                                 # no Python dependencies
metalncrna setup                              # pull the 7 images (or --build-from containers)
metalncrna check
```

`scripts/publish-images.sh --update-manifest` builds and pushes the seven images and pins them in
the manifest (`$METALNCRNA_MANIFEST` or `--manifest` selects another one). With Apptainer, `setup` converts each image to a SIF file in the cache
(`~/.cache/metalncrna`, or `$METALNCRNA_CACHE`). Converting the larger images (CPAT, RNAsamba)
needs several GB of temporary space; if `/tmp` is a small tmpfs, set `APPTAINER_TMPDIR` to a
directory on disk. To use images from another registry, copy
`manifest.toml`, change the `ref` values and pass `--manifest`.

## Run

```sh
metalncrna predict -i transcripts.fa -o results/ --species human
```

| Option | Meaning |
|---|---|
| `-s/--species` | `human` (default), `mouse`, `fly`, `zebrafish`, `plant`, `other` — selects CPAT, CPPred and CNCI models |
| `--tools` | subset, e.g. `cpc2,cpat,rnasamba` |
| `-j/--jobs`, `-t/--threads` | tools run concurrently / threads per tool |
| `--min-agree N`, `--min-length` | filters for `lncrna.fasta` |
| `--allow-failures` | build the consensus from the tools that succeeded (default: abort) |
| `--engine` | `docker`, `apptainer` or `singularity` (default: first available) |
| `--force` | ignore checkpoints |

Outputs in `results/`:

* `results.tsv` — per transcript: original ID, length, each tool's label and native score
  (`NA` = abstained), vote counts, consensus and agreement (fraction of voters agreeing).
* `lncrna.fasta` — selected transcripts with their original headers.
* `provenance.json` — input SHA-256, image IDs/digests and labels, exact commands, run times,
  per-tool status and citations.
* `logs/<tool>.log` — the full output of each tool.

Transcripts are renamed to internal IDs before the tools run (tools mangle names differently, e.g.
CPAT upper-cases them) and mapped back afterwards; sequences are never altered. A tool is not rerun
if its input, image and parameters are unchanged (checkpoint).

## Development

```sh
uv venv && uv pip install -e '.[test]'
pytest -m "not containers"   # unit tests, replay recorded tool outputs
pytest                       # also runs the real containers on tests/data/small.fa
```

## Contributing and support

Bug reports, questions and feature requests: [GitHub issues](https://github.com/LaBiOmicS/metaLncRNA/issues).
Contributions are welcome as pull requests against `main`; please run `pytest` (and `ruff check src tests`)
first. Adding a predictor means a `containers/<tool>/` directory (Dockerfile + `run-<tool>` launcher, upstream
code unmodified), an entry in `manifest.toml` and a `Tool` subclass in `src/metalncrna/tools/`.

## Citing

Please cite the seven tools (their references are listed in `provenance.json`) alongside metaLncRNA.
