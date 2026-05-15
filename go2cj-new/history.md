# go2cj-new — change history

## v0.3.0 — Initial CHIME prototype (2026-05-15)

**First working release** of the third-generation X2Cangjie translator.
A clean-slate research prototype that abandons backprop / Transformer /
gradient descent in favour of a biologically-inspired, gradient-free
learning system.

### Architecture: CHIME

CHIME = Critical Homeostatic Incremental Memory Engine, a four-layer
dynamic system implemented in pure NumPy:

* **HDC encoder** — 2048-bit bipolar hypervectors, deterministic
  hash-seeded, with the standard Bundle/Bind/Permute algebra
  (Kanerva 2009).  No vocabulary table.
* **SOINN substrate** — a growing concept graph that adds / removes
  neurons online (Furao & Hasegawa 2006).  ~ 220 neurons after a
  single pass over the 263-pair curated trainset.
* **SOC controller** — Turrigiano-style homeostatic threshold
  adaptation that drives the branching ratio toward σ → 1 (Beggs &
  Plenz 2003).  Power-law exponent α̂ ≈ 2.36 after training.
* **Predictive-coding context** — a leaky-integrated context HV that
  XOR-binds with each query (Rao & Ballard 1999; Friston 2010).
* **Learning** — purely local Hebbian / STDP updates; no
  back-propagation; one-pass online training in ≈ 2 s on a single
  CPU core.

### Reused machinery (verbatim from `go2cj`)

* `lexer.py`  — regex-based Go tokenizer.
* `lifting.py` — cross-chunk struct→class / method-attach /
  interface-`<:` lifting.
* `anonymize.py` — identifier / literal placeholder map.
* `tokenize.py` — multi-char operator tokenizer / detokenizer
  (formerly `neural/vocab.py`).
* `trainset/` — 263 curated chunk pairs + 15 full Go/Cj programs.
* `tests/cases/` — 45 end-to-end test programs.

### New machinery

* `go2cj_new/critical/` — entirely new: HDC, SOINN, SOC, PC, engine,
  train, translator.
* `converter.py` — adapted to (a) call the CHIME translator instead
  of the Transformer, (b) **unfold `func main(){body}` into per-stmt
  chunks** (an architectural fix to the well-documented v1 OOD
  pitfall where the entire main body was a single chunk).
* Synthetic `main()` wrap uses the bare `main() { … return 0 }`
  signature (no explicit `: Unit` annotation) so that the synthesised
  `return 0` is accepted by `cjc 1.0.5`.

### Results

End-to-end on `tests/cases/*.go` (45 programs) with `cjc 1.0.5`:

| Metric | go2cj v1 (Transformer) | go2cj-v2 (CodeT5-small) | **CHIME** |
|---|---|---|---|
| Pattern coverage | ~ 0.55 (val) → < 0.05 (test) | ~ 0.30 | **0.9756** |
| cjc-compile pass | 2–3 / 45 | 16 / 45 | **19 / 45** |
| Runtime match    | 0 / 45 | — | **6 / 45** |
| Training time | minutes × many epochs | minutes × many epochs | **1.8 s, single pass** |
| Parameters | static ~ 2 M | static ~ 60 M | **dynamic, ~ 220 neurons** |
| Algorithm | back-prop + AdamW | back-prop fine-tune | **local Hebbian / STDP** |

### Key design decisions during this iteration

* **Discrete-template dedup at training time** — early SOINN
  versions used HD-similarity-based prototype averaging, which
  silently merged neurons whose Cangjie outputs *disagreed*.
  Replaced with exact-string deduplication on `template_in`; HD
  similarity still drives **retrieval**.  This alone lifted the
  cjc-compile rate from 0 / 45 to 19 / 45.
* **Strict placeholder-set filter at inference** — a candidate
  template is rejected unless every placeholder it emits already
  exists in the input chunk's anonymisation map.  Eliminates the
  "stray `STR2` in output" failure mode entirely.
* **Identity fallback on empty retrieval** — when associative
  memory has no clean match for a chunk, we emit the chunk's Go
  text verbatim.  Many Go expressions (`a + b`, indexing, function
  calls) are already valid Cangjie; this maximises the chance of
  the surrounding program still compiling.

### Known limitations (see readme.md for full discussion)

* Misroutes when input chunk is dissimilar from every training
  chunk in HD space (e.g. `fmt.Println(a*b)` retrieves
  `println(a)` because no `*` variant is in the trainset).
* SOC is currently passive bookkeeping — does not yet gate readout
  via avalanche spreading.
* No bidirectional HDC cross-modal binding yet; templates are stored
  textually rather than as Cangjie-side HVs.
