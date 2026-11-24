# metaLncRNA

[![CI](https://github.com/LaBiOmicS/metaLncRNA/actions/workflows/ci.yml/badge.svg)](https://github.com/LaBiOmicS/metaLncRNA/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/LaBiOmicS/metaLncRNA)](https://github.com/LaBiOmicS/metaLncRNA/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Website](https://img.shields.io/badge/website-labiomics.github.io%2FmetaLncRNA-6b3fa0)](https://labiomics.github.io/metaLncRNA/)

**Consensus identification of long non-coding RNAs from seven unmodified coding-potential
predictors.**

Coding-potential predictors often disagree, and several of the best known ones are Python 2
programs that are hard to install today. metaLncRNA runs seven of them **exactly as their authors
released them**, each in its own container pinned by digest, reads the label each tool itself
gives, and calls every transcript by **majority vote**. Nothing is retrained, re-weighted or
re-implemented, so a result can be reported as "CNCI commit `745e2d1`, unmodified".

Website: <https://labiomics.github.io/metaLncRNA/>

```console
$ metalncrna predict -i transcripts.fa -o results/ --species human
```

| Transcript | Length | CNCI | CPPred | LGC | CPAT | CPC2 | PLEK | RNAsamba | Consensus |
|---|---:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|
| SHH mRNA (NM_001310462.1) | 733 | C | C | C | C | C | N | C | **coding** 6/7 |
| BGLAP mRNA (NM_199173.5) | 760 | N | C | N | C | N | C | C | **coding** 4/7 |
| NUDT15 mRNA (NM_001304745.1) | 934 | N | C | N | C | C | C | C | **coding** 5/7 |
| *A. thaliana* lncRNA (NR_143190.1) | 414 | N | N | N | N | N | N | N | **noncoding** 7/7 |
| *A. thaliana* lncRNA (NR_143145.1) | 419 | N | N | N | N | N | N | C | **noncoding** 6/7 |
| U6 snRNA pseudogene (ENST00000516288.1) | 111 | N | N | N | N | N | – | N | **noncoding** 6/6 |
| lncRNA with an `N` base (NR_143042.1) | 419 | – | N | N | N | N | N | N | **noncoding** 6/6 |

<sub>C = coding, N = noncoding, – = the tool abstained (PLEK skips transcripts ≤ 200 nt; CNCI skips
sequences with ambiguous bases). From `tests/data/small.fa`, human models; these are the labels
the real containers produce in CI.</sub>

## Contents

- [The seven predictors](#the-seven-predictors)
- [How the consensus is built](#how-the-consensus-is-built)
- [Install](#install)
- [Run](#run)
- [Outputs](#outputs)
- [Validation](#validation)
- [Reproducibility and provenance](#reproducibility-and-provenance)
- [Development](#development)
- [Citing](#citing)
- [License](#license)

## The seven predictors

| Tool | Version run | Approach | Models used by `--species` | Reference |
|---|---|---|---|---|
| CNCI | v2, commit `745e2d1` | adjacent-nucleotide-triplet profile + SVM | `ve` (vertebrate), `pl` for `plant` | Sun *et al.* 2013, [NAR 41:e166](https://doi.org/10.1093/nar/gkt646) |
| CPPred | tarball of 2018-05-17 | SVM on ORF, hexamer and CTD features | `Human` for `human`, `Integrated` otherwise | Tong & Liu 2019, [NAR 47:e43](https://doi.org/10.1093/nar/gkz087) |
| LGC | 1.0 | relationship between ORF length and GC content | single model | Wang *et al.* 2019, [Bioinformatics 35:2949](https://doi.org/10.1093/bioinformatics/btz008) |
| CPAT | 3.0.5 | logistic regression on ORF size, coverage, Fickett and hexamer scores | human, mouse, fly, zebrafish (none for plant/other) | Wang *et al.* 2013, [NAR 41:e74](https://doi.org/10.1093/nar/gkt006) |
| CPC2 | 1.0.1 | SVM on Fickett score, ORF length and integrity, isoelectric point | single model | Kang *et al.* 2017, [NAR 45:W12](https://doi.org/10.1093/nar/gkx428) |
| PLEK | 1.2 | improved k-mer scheme + SVM | single model | Li *et al.* 2014, [BMC Bioinformatics 15:311](https://doi.org/10.1186/1471-2105-15-311) |
| RNAsamba | 0.2.5 | neural network on the whole sequence and its ORF | full-length weights | Camargo *et al.* 2020, [NAR Genom Bioinform 2:lqz024](https://doi.org/10.1093/nargab/lqz024) |

CNCI, CPPred and LGC are built from the authors' original archives (Python 2.7), kept in
`containers/<tool>/upstream/` and checked by SHA-256 at build time. CPAT, CPC2, PLEK and RNAsamba
start from the BioContainers image of the Bioconda package, pinned by digest, plus the authors'
published model files. No line of any tool is changed; a small `run-<tool>` launcher only sets the
working directory. Details in [`containers/README.md`](containers/README.md).

## How the consensus is built

1. **Each tool decides with its own rule.** Every tool runs with its default parameters and its own
   threshold. CPAT reports a probability and no label, so the cut-off its authors published for
   the species is applied (human 0.364, mouse 0.44, fly 0.39, zebrafish 0.38); a transcript in which
   CPAT finds no ORF counts as noncoding.
2. **Tools may abstain.** A tool that does not report on a transcript does not vote: PLEK skips
   transcripts ≤ 200 nt, CNCI skips sequences with ambiguous bases, CPAT has no plant model, and a
   tool may fail (with `--allow-failures`).
3. **Majority of the tools that voted.** More coding votes → `coding`; more noncoding votes →
   `noncoding`; a tie → `ambiguous`; no votes → `unclassified`.

There are no weights and no calibration: every tool counts once. `agreement` in `results.tsv` is
the fraction of voters that agree with the consensus, and `--min-agree N` lets you ask for
stronger support when selecting lncRNAs.

## Install

Requirements: Linux, Python ≥ 3.11 and either Docker or Apptainer/Singularity. The package
itself has no Python dependencies.

```sh
pip install git+https://github.com/LaBiOmicS/metaLncRNA@v1.0.0
metalncrna setup     # pulls the seven public images from ghcr.io/labiomics
metalncrna check     # reports each image, its digest and whether it was verified
```

> The `metalncrna` releases 1.1.1–2.0.6 on PyPI are the previous, unrelated code base. Install
> this version from GitHub as above, or with `pip install .` from a clone.

**Apptainer/Singularity.** `setup` converts each image into a SIF file in the cache
(`~/.cache/metalncrna`, or `$METALNCRNA_CACHE`). The larger images (CPAT, RNAsamba) need several GB
of temporary space while converting; if `/tmp` is a small tmpfs, point `APPTAINER_TMPDIR` to a
directory on disk.

**Building the images yourself.** `metalncrna setup --build-from containers` builds the seven
images from a clone instead of pulling them. `scripts/publish-images.sh --update-manifest` builds,
pushes and pins them in the manifest; to use another registry, copy
[`manifest.toml`](src/metalncrna/manifest.toml), change the `ref` values and pass `--manifest`
(or set `$METALNCRNA_MANIFEST`).

## Run

```sh
metalncrna predict -i transcripts.fa -o results/ --species human
```

| Option | Meaning |
|---|---|
| `-i/--input`, `-o/--outdir` | transcripts in FASTA format; output directory |
| `-s/--species` | `human` (default), `mouse`, `fly`, `zebrafish`, `plant`, `other`; selects the CNCI, CPPred and CPAT models |
| `--tools` | run a subset, e.g. `cpc2,cpat,rnasamba` |
| `-j/--jobs`, `-t/--threads` | tools run concurrently (default 3) / threads per tool (default 4) |
| `--min-length` | minimum length for `lncrna.fasta` (default 200 nt, the usual lncRNA threshold) |
| `--min-agree N` | also require at least N noncoding votes for `lncrna.fasta` |
| `--allow-failures` | build the consensus from the tools that succeeded (default: stop) |
| `--engine` | `docker`, `apptainer` or `singularity` (default: the first one available) |
| `--manifest` | alternative image manifest (TOML) |
| `--force` | ignore checkpoints and rerun every tool |

Transcripts are given internal IDs before the tools run, because the tools mangle names in
different ways (CPAT upper-cases them, for example), and are mapped back afterwards. Sequences are
never altered. A tool is not rerun when its input, image and parameters are unchanged.

## Outputs

| File | Content |
|---|---|
| `results.tsv` | one row per transcript: original ID, length, each tool's label and native score (`NA` = abstained), vote counts, consensus and agreement |
| `lncrna.fasta` | the `noncoding` transcripts that pass `--min-length` (and `--min-agree`), with their original headers |
| `provenance.json` | input SHA-256, image references, digests and OCI labels, exact commands, run times, per-tool status and citations |
| `logs/<tool>.log` | the complete output of each tool |

## Validation

`scripts/validate.py` runs the coding and ncRNA test sets shipped inside the CPPred package
(100 + 100 transcripts per species) through `metalncrna predict` with the public images. Accuracy
on the transcripts each tool labelled (v1.0.0; full table with sensitivity, specificity and
precision in [`docs/validation/metrics-1.0.0.tsv`](docs/validation/metrics-1.0.0.tsv)):

| Predictor | Human | Mouse | Zebrafish | Fruit fly |
|---|---:|---:|---:|---:|
| CNCI | 0.935 | 0.975 | 0.990 | 0.995 |
| CPPred | 0.990 | 0.995 | 0.970 | 0.995 |
| LGC | 0.945 | 0.965 | 0.960 | 0.960 |
| CPAT | 0.995 | **1.000** | **1.000** | **1.000** |
| CPC2 | 0.980 | 0.970 | 0.980 | 0.995 |
| PLEK¹ | 0.960 | 0.870 | 0.890 | 0.721 |
| RNAsamba | **1.000** | **1.000** | 0.990 | 0.965 |
| **Consensus** | 0.995 | **1.000** | 0.985 | **1.000** |

¹ PLEK abstains on transcripts ≤ 200 nt and labelled only 50–61% of each set; the consensus
labelled every transcript.

The consensus scored above the median tool in every species and matched the best one in mouse and
fly; the voting tools disagreed on 101 of the 800 transcripts.

**This is a consistency check, not a lncRNA benchmark.** The ncRNAs in these sets are mostly
short (median ≈ 110 nt; the human set is 95 snRNA + 5 rRNA; only 23 of 400 reach 200 nt), the
coding RNAs are 2–3 kb mRNAs, and the sets are CPPred's own held-out data, which other tools may
have partly seen in training. The numbers show that every container runs and is parsed
correctly; they do not measure performance on long non-coding RNAs.

```sh
python scripts/validate.py -o validation/            # human, mouse, zebrafish, fly
```

## Reproducibility and provenance

- Every image is referenced by digest in [`manifest.toml`](src/metalncrna/manifest.toml) and is
  self-contained: tool, dependencies and model files, the latter verified by SHA-256 at build time.
- The images carry OCI labels with the upstream source, the base image and
  `metalncrna.modified="false"`.
- `provenance.json` records what actually ran, so a run can be repeated or audited later.
- Docker and Apptainer give byte-identical outputs for CPPred and CNCI and identical labels for LGC.
- CI builds all seven images from `containers/` and runs them end to end on every push.

## Development

```sh
uv venv && uv pip install -e '.[test]'
pytest -m "not containers"   # unit tests, replaying recorded tool outputs
pytest                       # also runs the real containers on tests/data/small.fa
ruff check src tests scripts
```

Bug reports, questions and feature requests go to the
[issue tracker](https://github.com/LaBiOmicS/metaLncRNA/issues). Pull requests against `main` are
welcome; please run the tests first. Adding a predictor takes a `containers/<tool>/` directory
(Dockerfile and `run-<tool>` launcher, upstream code unmodified), an entry in `manifest.toml` and a
`Tool` subclass in [`src/metalncrna/tools/`](src/metalncrna/tools/__init__.py).

## Citing

If you use metaLncRNA, please cite the software (see [`CITATION.cff`](CITATION.cff), or GitHub's
"Cite this repository" button) **and the seven predictors** listed
[above](#the-seven-predictors); the references are also written to `provenance.json` for the tools
that ran.

## License

The metaLncRNA wrapper (`src/`, `scripts/`, `tests/`, the Dockerfiles and `run-<tool>` launchers)
is released under the [MIT License](LICENSE). The predictors keep their own licenses; metaLncRNA
only runs them as separate programs, each in its own container, and does not modify them.

| Tool | License |
|---|---|
| CNCI | GPL-2.0 (`LICENSE` in the authors' repository) |
| CPAT | GPL-2.0-or-later |
| CPC2 | GPL-3.0 |
| PLEK | GPL-2.0 |
| RNAsamba | GPL-3.0 |
| CPPred | none declared by the authors |
| LGC | none declared by the authors |
| LIBSVM (bundled with CNCI and CPPred) | BSD-3-Clause |

CPPred and LGC are distributed by their authors without a license statement. Their original
archives (`containers/cppred/upstream/`, `containers/lgc/upstream/`) and the corresponding images
are redistributed unmodified, solely so that results can be reproduced; all rights remain with
the authors. If you are an author of one of these tools and want this changed, please open an
issue or contact the maintainers and the files will be removed or replaced by a download at build
time.

---

Developed at [LaBiOmicS](https://github.com/LaBiOmicS), Laboratory of Bioinformatics and Omics
Sciences, Universidade de Mogi das Cruzes (UMC), Brazil.
