# go2cj trainset — curated Go ↔ Cangjie parallel pairs

This directory holds **hand-curated**, high-quality Go ↔ Cangjie chunk
pairs used to train the neural translator that powers `go2cj`.

Every pair is one **canonical, idiomatic** translation written by hand
to capture not just *correctness* but also *code taste* — the Cangjie
side uses preferred standard-library APIs, the right type names
(`Int64`, `Float64`, `String`, `Bool`, `ArrayList<T>`, `HashMap<K, V>`,
`Option<T>`, …), `match` over chained `if`, range-based `for`, tuple
destructuring, named-arg constructors, etc.

## Layout

```
trainset/
├── readme.md                   ← this file
├── pairs.jsonl                 ← chunk-level Go↔CJ pairs (one JSON per line)
└── programs/                   ← whole-program demonstrations (for documentation
                                  and for the corpus loader to slice into chunks)
    ├── 01_variables.go
    ├── 01_variables.cj
    ├── …                       ← matched .go / .cj pairs
```

## `pairs.jsonl`

Each line is a JSON object with two string fields:

```json
{"go": "x := 1", "cj": "var x = 1"}
{"go": "fmt.Println(x)", "cj": "println(x)"}
```

Whitespace inside the strings is preserved verbatim.  Tokens are
encoded the same way the neural model sees them (word-level), so
multi-line bodies are usually flattened to a single line with `;` as
the statement separator — that is the form produced by go2cj's chunk
segmenter and so the form the translator must learn.

## `programs/`

Each `<name>.go` / `<name>.cj` pair is a fully-working program that
demonstrates a feature in idiomatic style.  The corpus loader
(`go2cj.neural.corpus_curated`) lexes the Go side, segments it into
chunks, lines them up with the chunk segmentation of the Cangjie side,
and adds them to the training set.

Each program **must compile**:

* `go vet <name>.go` succeeds.
* `cjc <name>.cj -o /tmp/x` succeeds.
* Running both produces the same stdout.

The test runner (`tests/run_tests.py`) does **not** validate these —
they live outside the test suite by design — but the same invariants
hold.

## Adding a new pair

1. Write the Go snippet in idiomatic Go.
2. Hand-translate to Cangjie using the **preferred** Cangjie idiom
   (not a literal token-by-token mapping).  Match Cangjie style:
   `var` vs `let`, `Int64`/`Float64` types, `ArrayList<T>` instead of
   arrays where mutation is wanted, `match` instead of long `if`
   chains, `println` instead of `print` for line-terminated output,
   etc.
3. Add one JSONL line, or a `.go`/`.cj` program pair under `programs/`.
4. Re-train: `python -m go2cj.neural.train`.

## Training-data philosophy

* **Quality over quantity**: each curated pair represents the
  *correct* Cangjie translation for that Go pattern.  We rely on
  identifier/literal anonymization (`go2cj.neural.anonymize`) to
  generalize each pair into thousands of variants at training time.
* **Coverage breadth**: every major Go construct should have at
  least one pair (vars, control flow, functions, multiple-return,
  slices, maps, strings, structs, methods, interfaces, switch,
  defer/recover analogs, closures, range over collections, basic IO).
* **Idiomatic Cangjie**: when in doubt, prefer the Cangjie standard
  library form over the most literal mapping.
