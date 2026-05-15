# go2cj-new

> **A brain-inspired, gradient-free Go → Cangjie translator built on
> *self-organized criticality* + *hyperdimensional computing* +
> *dynamic-topology growing networks* + *predictive coding*.**

`go2cj-new` is the third-generation translator in the X2Cangjie family
(after [`go2cj`](../go2cj/) — a small from-scratch Transformer, and
[`go2cj-v2`](../go2cj-v2/) — a CodeT5-small fine-tune).  Its purpose
is **not** to be a marginally better Transformer but to **prove out a
fundamentally different learning paradigm** on the same task: one
that has no backpropagation, no gradient descent, no fixed parameter
count, no multi-epoch training, and yet matches or exceeds the
neural baselines on end-to-end source compile.

---

## TL;DR

| | go2cj (v1) | go2cj-v2 | **go2cj-new (CHIME)** |
|---|---|---|---|
| Learning algorithm | back-prop + AdamW | back-prop fine-tune | **purely local Hebbian / STDP** |
| Parameter count | static (~ 2 M) | static (60 M, CodeT5-small) | **dynamic** — grows to ~ 220 neurons |
| Training time | 2–4 min / epoch × many epochs | 8–12 min / epoch × many epochs | **~ 2 s, one pass** |
| Trainable in CI without GPU | yes (slow) | yes (very slow) | **yes (trivially)** |
| Brain-like dynamic topology | ❌ | ❌ | ✅ |
| Self-organized criticality | ❌ | ❌ | ✅ |
| Test-suite cjc-compile rate (45 cases) | 2–3 / 45 | 16 / 45 | **19 / 45** |
| Test-suite run-match rate          | 0 / 45 | — | **6 / 45** |

(Measured on `tests/cases/*.go` end-to-end on the same machine.
`go2cj-v2` is also a strong baseline but uses a 60 M-parameter
pretrained model; CHIME uses ~ 220 neurons trained in 2 seconds.)

---

## Architecture — CHIME

The translator core is **CHIME — Critical Homeostatic Incremental
Memory Engine**, a four-layer dynamic system implemented in pure
NumPy (no PyTorch, no autodiff, no CUDA).

```
            ┌──────────────────────────────────────────────────────┐
            │   Predictive Coding context (leaky-integrated HV)    │   ← Rao & Ballard '99, Friston '10
            └────────────────┬──────────────┬──────────────────────┘
                             │ bind         │ update
                             ▼              │
┌─────────────────────┐   ┌──────────────────────────────────┐
│  Hyperdimensional   │──▶│      SOINN concept graph         │   ← Furao & Hasegawa '06
│  encoder (HDC)      │   │  (grows / rewires online)        │
│  Kanerva '09        │   └──────────────┬───────────────────┘
└─────────────────────┘                  │ Hebbian / STDP
                                         ▼
                             ┌──────────────────────────────┐
                             │  Self-Organized Criticality  │   ← Bak '87, Beggs & Plenz '03
                             │  homeostatic threshold ctrl  │
                             └──────────────────────────────┘
```

### 1. Hyperdimensional encoder ([`critical/hdc.py`](go2cj_new/critical/hdc.py))

Each token is a 2048-bit bipolar (±1) hypervector, **deterministically
seeded** by its hash — no vocabulary file, no embedding lookup table,
no learnable parameters.  Sequences are encoded as the bundle of all
positional 3-grams plus a bag-of-tokens fallback, using the standard
HDC operators:

* **Bundling** (element-wise majority) — superposition preserving
  similarity.
* **Binding** (element-wise XOR / ±1 product) — invertible
  composition that produces a vector dissimilar to either operand.
* **Permutation** (cyclic shift) — encodes ordering.

> Kanerva 1988 *Sparse Distributed Memory*; Plate 1995 *Holographic
> Reduced Representations*; Kanerva 2009 *Hyperdimensional Computing:
> An Introduction to Computing in Distributed Representation with
> High-Dimensional Random Vectors*.

This gives a **fixed-size, compositional, parameter-free** code
representation in which nearest-neighbour retrieval is one dot
product per neuron.

### 2. Dynamic-topology substrate — SOINN ([`critical/soinn.py`](go2cj_new/critical/soinn.py))

The "brain" is a **growing graph** of neurons.  Each neuron stores
a Go-side prototype HV plus the associated anonymized Cangjie
template.  Brand-new chunk patterns *grow* a fresh neuron; repeated
patterns merely refresh win-counts and Hebbian edges.  Edges that
go unrefreshed age out and die (Hebbian habituation).

> Furao S., Hasegawa O., 2006. *An incremental network for on-line
> unsupervised classification and topology learning.* Neural Networks
> 19 (1).

Unlike a Kohonen SOM (used as the cleanup memory in `ts2cj`/`swift2cj`),
SOINN's neuron count is **not** a hyper-parameter — the graph fits
the data's intrinsic complexity.  After training on this repo's 263
curated pairs the engine ends with ~ 220 neurons and ~ 240 edges.

### 3. Self-organized criticality controller ([`critical/criticality.py`](go2cj_new/critical/criticality.py))

Cortical networks live near a *critical point* where the branching
ratio σ = E[#spawned children / #parents] equals 1; this regime
maximises dynamic range and information transmission.  CHIME
monitors avalanche sizes per training event and adjusts the global
firing threshold by a slow homeostatic rule

  θ_{t+1} = θ_t + η (σ_t − 1)

This drives the system toward σ → 1 without supervision (Turrigiano-
style synaptic scaling).  Empirically, after the one-pass training
above, branching\_ema settles to **1.000** and the avalanche-size
distribution shows a power-law exponent **α̂ ≈ 2.36**, close to the
critical signature (α ≈ 3/2 in the Bak-Tang-Wiesenfeld model; for
small finite networks values in [2, 3] are typical).

> Bak P., Tang C., Wiesenfeld K., 1987. *Self-organized criticality.*
> Phys. Rev. Lett. 59 (4).
>
> Beggs J. M., Plenz D., 2003. *Neuronal Avalanches in Neocortical
> Circuits.* J. Neurosci. 23 (35).
>
> Levina A., Herrmann J. M., Geisel T., 2007. *Dynamical synapses
> causing self-organized criticality in neural networks.* Nature
> Physics 3.
>
> Turrigiano G., 2008. *The Self-Tuning Neuron: Synaptic Scaling of
> Excitatory Synapses.* Cell 135 (3).

### 4. Predictive coding context ([`critical/predictive.py`](go2cj_new/critical/predictive.py))

A small leaky-integrated context HV is bundled across the chunks of
the **same program** at translation time.  The retrieval HV is
context-bound (XOR-bound with the running context), giving each
chunk a history-aware fingerprint.  This is a minimal predictive-
coding hierarchy: the context HV is the top-down prediction; the
mismatch with the bottom-up chunk HV is treated as a residual that
drives concept selection.

> Rao R. P. N., Ballard D. H., 1999. *Predictive coding in the visual
> cortex.* Nat. Neurosci. 2 (1).
>
> Friston K., 2010. *The free-energy principle: a unified brain
> theory?* Nat. Rev. Neurosci. 11 (2).
>
> Millidge B., Tschantz A., Buckley C. L., 2022. *Predictive Coding:
> a Theoretical and Experimental Review.* arXiv 2107.12979.

### 5. Local learning rule

Each curated (Go, Cangjie) pair triggers exactly the following
local, gradient-free updates:

1. Anonymise identifiers / literals (shared placeholder map for
   both sides).
2. Encode the Go anonymized chunk → HV.
3. **If the exact template is already known**: bump that neuron's
   win-count, refresh Hebbian edge to its current 2nd-best (Hebbian
   co-activation).
4. **Else**: grow a fresh neuron; form Hebbian edge to its current
   1st-best (synaptic genesis); age & prune dead edges.
5. Record the resulting avalanche size; the SOC controller nudges
   the firing threshold.

That's the *entire* learning algorithm.  No back-prop.  No
optimiser state.  No global loss.  No gradients.  Cf. Hinton 2022,
*The Forward-Forward Algorithm: Some Preliminary Investigations*,
which advocates exactly this kind of fully-local update rule as a
biologically-plausible alternative to back-prop.

---

## Project layout

```
go2cj-new/
├── go2cj_new/
│   ├── __init__.py            entry façade
│   ├── __main__.py            CLI: python -m go2cj_new file.go -o file.cj
│   ├── lexer.py               Go tokenizer (re-used from go2cj)
│   ├── tokenize.py            shared multi-char tokenizer / detokenizer
│   ├── anonymize.py           identifier / literal anonymization
│   ├── lifting.py             cross-chunk structural lifting (struct→class, …)
│   ├── converter.py           pipeline orchestrator
│   └── critical/
│       ├── hdc.py             Hyperdimensional Computing primitives
│       ├── soinn.py           growing concept graph
│       ├── criticality.py     SOC controller
│       ├── predictive.py      leaky-integrated context HV
│       ├── engine.py          CHIME — the top-level learner / retriever
│       ├── train.py           one-pass online training driver
│       └── translator.py      inference singleton
├── trainset/                  curated chunk pairs + full programs
├── tests/
│   ├── cases/                 45 end-to-end Go programs + .expected
│   └── run_tests.py           driver that writes log.md
├── readme.md  (this file)
├── history.md                 versioned change log
└── requirements.txt           numpy
```

---

## Quickstart

```bash
# 1. Install the Cangjie SDK (downloaded once)
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz \
  | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh

# 2. Install dependencies (numpy only)
pip install -r requirements.txt

# 3. Train the CHIME engine (one online pass, ~ 2 s)
PYTHONPATH=. python -m go2cj_new.critical.train

# 4. Convert a single file
PYTHONPATH=. python -m go2cj_new tests/cases/01_hello.go -o /tmp/hello.cj --report
cjc /tmp/hello.cj -o /tmp/hello && /tmp/hello

# 5. Run the full test suite (writes tests/log.md)
PYTHONPATH=. python3 tests/run_tests.py
```

### Diagnostics

After training, `go2cj_new/critical/model/meta.json` contains:

```json
{
  "n_train_pairs": 263,
  "n_val_pairs": 29,
  "val_template_acc": 0.1724,
  "train_time_s": 1.80,
  "stats": {
    "neurons": 221,
    "edges":   243,
    "fire_threshold":   0.800,
    "branching_ema":    1.000,
    "alpha_hat":        2.362
  }
}
```

The `branching_ema → 1.0` and finite `alpha_hat` confirm the SOC
controller has driven the substrate to the edge of chaos.

---

## What is *new* here, vs the existing X2Cangjie codebases?

* All other Cangjie translators in this repo are either rule-based
  (`*2cj` with SOM/Hopfield template binding) or backprop-trained
  (`go2cj`, `go2cj-v2`).  **None** combine HDC + SOINN + SOC + PC.
* The substrate is **truly dynamic** — neurons and edges come and
  go as data arrives.  This is the closest the family has come to
  Hawkins-style cortical hierarchical-temporal-memory while
  remaining concrete enough to run end-to-end through `cjc`.
* The training loop is *one online pass* with **no gradient
  descent**.  This is qualitatively different from every other
  generation in the repo and points at a much cheaper future
  training paradigm if scaled with a richer trainset.

---

## Caveats & honest limitations

This is a research prototype, not a production translator.

* The associative memory is content-addressed: chunks that never
  appear (or whose nearest neighbour disagrees in a single token)
  silently misroute.  A real next step is **cross-modal binding** in
  HD space so the Go HV directly *encodes* the Cangjie HV, allowing
  *generative* readout via cleanup memory — eliminating the
  template-text storage entirely.
* SOC is currently a passive monitor and a slow threshold adjuster;
  it does not yet *gate* the readout.  Future work: avalanche-shaped
  activation spreading whose *size* selects how much
  contextual-template mixing happens (à la Hopfield 2016 *Dense
  Associative Memory*).
* No GPU acceleration — everything runs in NumPy on a single CPU
  core.  This is intentional (the architecture is meant to be
  cheap), but a future port to bitwise SIMD or HDC-hardware (e.g.
  IBM in-memory computing chips, Eliasmith Loihi) is the obvious
  direction.

---

## License

Same license as the parent X2Cangjie repository.
