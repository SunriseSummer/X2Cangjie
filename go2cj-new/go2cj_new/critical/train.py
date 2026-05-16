"""Online, one-pass training of the CHIME engine on the curated trainset.

Unlike go2cj v1 (multi-epoch transformer training) or go2cj-v2 (multi-
epoch CodeT5 fine-tuning), CHIME requires *no* backpropagation, *no*
gradient descent, and **converges in a single pass** over the
trainset.  Empirically all 300+ curated pairs plus 15 full-program
chunks are absorbed in a few seconds on a single CPU.

Training pipeline:

1. Load every curated pair from ``trainset/pairs.jsonl``.
2. Load every full-program chunk pair from ``trainset/programs/*.go``
   & ``*.cj`` (using the same chunk segmenter as the converter).
3. Anonymize each pair with the *shared* placeholder map
   (:func:`go2cj_new.anonymize.anonymize_pair`) so identifiers /
   literals are aligned across the two sides.
4. Feed each anonymized pair to :meth:`CHIME.learn` in order — the
   SOINN substrate grows, Hebbian edges form, the criticality
   controller adapts.
5. Save the engine to ``go2cj_new/critical/model/``.

Validation: hold out 10 % of curated pairs, measure exact-template
recall after the single pass.  The metric we report is
``val_template_acc`` — fraction of held-out anonymized Go chunks for
which the engine emits the exact ground-truth anonymized Cj.

Usage::

    python -m go2cj_new.critical.train             # one-pass train
    python -m go2cj_new.critical.train --report    # + diagnostics
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

# Make ``import go2cj_new`` work when run as ``python -m
# go2cj_new.critical.train`` from anywhere.
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG.parent))

from go2cj_new.anonymize import anonymize_pair  # noqa: E402
from go2cj_new.lexer import tokenize  # noqa: E402
from go2cj_new.critical.engine import CHIME  # noqa: E402


TRAINSET = PKG.parent / "trainset"
MODEL_DIR = HERE / "model"


# --------------------------------------------------------------------------- #
#  Trainset loading                                                           #
# --------------------------------------------------------------------------- #


def _load_pairs() -> List[Tuple[str, str]]:
    """Return the ``[(go, cj), ...]`` list from ``pairs.jsonl``,
    with any whole-function pairs recursively unfolded into header,
    per-statement body chunks, and footer.

    This mirrors ``_load_programs`` so the same Recursive Block
    Unfolding invariants hold for ad-hoc curated pairs as well — a
    whole-function entry like ``func fib(n int) int { if n < 2 {…};
    return fib(n-1)+fib(n-2) }`` becomes a header neuron, two body
    neurons, and a footer neuron.  Without the unfold the body
    statements of any test program would HD-match the whole-function
    template at retrieval and the converter would inject a duplicated
    function into the body of its own function — exactly the failure
    we observed for ``09_fibonacci`` before this change.
    """
    p = TRAINSET / "pairs.jsonl"
    pairs: List[Tuple[str, str]] = []
    if not p.exists():
        return pairs
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        d = json.loads(line)
        if "go" not in d or "cj" not in d:
            continue
        go_text, cj_text = d["go"], d["cj"]
        # Try to unfold as a user function first.  Falls through to
        # the verbatim pair when the shape doesn't match (most pairs
        # are already statement-level).
        unfolded = _unfold_user_func(go_text, cj_text)
        if unfolded:
            pairs.extend(unfolded)
        else:
            pairs.append((go_text, cj_text))
    return pairs


def _split_top_level(src: str, semi: str = ";") -> List[str]:
    """Return top-level chunks of a source file by brace balance.

    Same logic as the converter's chunk segmenter, but operates on raw
    *text* so we can apply it to both Go and Cj curated programs.
    Comments / blank lines are removed first.  This is purely a
    splitter — no translation.
    """
    # Strip line + block comments to make brace balancing reliable.
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    chunks: List[str] = []
    cur: List[str] = []
    db = dp = ds = 0
    # Track whether we're inside a Go ``for init; cond; step`` header
    # so the ``;`` separators inside it do not split the chunk.  We
    # enter on a top-level ``for`` keyword and exit on the matching
    # ``{`` that opens the loop body.
    in_for_header = False
    i, n = 0, len(src)
    in_str = False
    str_ch = ""
    while i < n:
        c = src[i]
        cur.append(c)
        if in_str:
            if c == "\\" and i + 1 < n:
                cur.append(src[i + 1])
                i += 2
                continue
            if c == str_ch:
                in_str = False
            i += 1
            continue
        if c in '"\'`':
            in_str = True
            str_ch = c
            i += 1
            continue
        # ``for`` keyword detection — only at depth 0 and as a
        # whole word.  We need this so the ``;`` separators in a Go
        # ``for init; cond; step`` header do not split the chunk.
        if (c == "f" and db == 0 and dp == 0 and ds == 0
                and src[i:i + 3] == "for"
                and (i + 3 >= n or not (src[i + 3].isalnum()
                                        or src[i + 3] == "_"))
                and (i == 0 or not (src[i - 1].isalnum()
                                    or src[i - 1] == "_"))):
            in_for_header = True
        if c == "{":
            db += 1
            if in_for_header and db == 1:
                in_for_header = False
        elif c == "}":
            db = max(db - 1, 0)
            if db == 0 and dp == 0 and ds == 0:
                # End of block-level chunk.
                chunks.append("".join(cur).strip())
                cur = []
        elif c == "(":
            dp += 1
        elif c == ")":
            dp = max(dp - 1, 0)
        elif c == "[":
            ds += 1
        elif c == "]":
            ds = max(ds - 1, 0)
        elif (c == semi and db == 0 and dp == 0 and ds == 0
              and not in_for_header):
            chunks.append("".join(cur[:-1]).strip())
            cur = []
        elif c == "\n" and db == 0 and dp == 0 and ds == 0:
            cur_str = "".join(cur).strip()
            # Split on every top-level newline.  Previously we tried to
            # be clever and refuse to split when the trailing token
            # looked like an "operator" — but ``import std.collection.*``
            # ends with ``*`` and that gentleness collapsed entire
            # Cangjie files into one chunk.  Brace balance alone is a
            # sufficient guard against splitting mid-statement.
            if cur_str:
                chunks.append(cur_str)
                cur = []
        i += 1
    tail = "".join(cur).strip()
    if tail:
        chunks.append(tail)
    return [c for c in chunks if c]


def _block_split_text(stmt: str) -> Optional[Tuple[str, str]]:
    """Text-based mirror of :func:`go2cj_new.converter._block_split`.

    Returns ``(header_through_open_brace, body_between_braces)`` when
    ``stmt`` is a single-block statement like ``for X { body ; body }``,
    where the opening ``{`` matches the trailing ``}`` and the body
    contains at least one top-level ``;``.  Returns ``None`` for
    composite literals (``[]int{1, 2, 3}``), if-else (``if … {…} else
    {…}``), and non-block statements.
    """
    text = stmt.strip()
    if not text or text[-1] != "}":
        return None
    n = len(text)
    paren = bracket = 0
    open_idx = -1
    i = 0
    in_str = False
    str_ch = ""
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\" and i + 1 < n:
                i += 2
                continue
            if c == str_ch:
                in_str = False
            i += 1
            continue
        if c in '"\'`':
            in_str = True
            str_ch = c
            i += 1
            continue
        if c == "(":
            paren += 1
        elif c == ")":
            paren = max(paren - 1, 0)
        elif c == "[":
            bracket += 1
        elif c == "]":
            bracket = max(bracket - 1, 0)
        elif c == "{" and paren == 0 and bracket == 0:
            open_idx = i
            break
        i += 1
    if open_idx <= 0:
        return None
    # Walk to matching ``}``.  Must be exactly the final char.
    depth = 1
    j = open_idx + 1
    in_str = False
    str_ch = ""
    while j < n and depth > 0:
        c = text[j]
        if in_str:
            if c == "\\" and j + 1 < n:
                j += 2
                continue
            if c == str_ch:
                in_str = False
            j += 1
            continue
        if c in '"\'`':
            in_str = True
            str_ch = c
            j += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    if j != n - 1:
        return None
    header = text[:open_idx + 1]
    body = text[open_idx + 1:j]
    # Body must contain at least one top-level statement separator
    # (``;`` *or* ``\n``) to count as a real statement block — this
    # rules out composite literals like ``[]int{1, 2, 3}`` while
    # admitting both ``if cond { return 1 }`` (newline-separated) and
    # ``if cond { return 1; }`` (semicolon-separated) forms.
    body_depth = 0
    has_sep = False
    in_body_str = False
    body_str_ch = ""
    bi = 0
    bn = len(body)
    while bi < bn:
        bc = body[bi]
        if in_body_str:
            if bc == "\\" and bi + 1 < bn:
                bi += 2
                continue
            if bc == body_str_ch:
                in_body_str = False
            bi += 1
            continue
        if bc in '"\'`':
            in_body_str = True
            body_str_ch = bc
            bi += 1
            continue
        if bc in "{([":
            body_depth += 1
        elif bc in "})]":
            body_depth = max(body_depth - 1, 0)
        elif body_depth == 0 and bc in (";", "\n"):
            has_sep = True
            break
        bi += 1
    if not has_sep:
        return None
    return text[:open_idx + 1], body


def _expand_block_pairs(go_stmt: str, cj_stmt: str) -> List[Tuple[str, str]]:
    """Unfold a paired Go / Cj statement that has block shape
    ``<header> { body }`` on both sides into header / body-stmt /
    footer pairs.  *Non-recursive* — see the rationale in
    :func:`_unfold_main_body`.

    Currently unused (we keep the helper for future experiments, e.g.
    when the trainset gains identifier-bounded loops that can match
    test programs' literal-bounded loops); calling sites use the
    flat statement zip instead.
    """
    gs = _block_split_text(go_stmt)
    cs = _block_split_text(cj_stmt)
    if gs is None or cs is None:
        return []
    go_header, go_body = gs
    cj_header, cj_body = cs
    go_stmts = _split_top_level(go_body.strip())
    cj_stmts = _split_top_level(cj_body.strip())
    if len(go_stmts) != len(cj_stmts):
        return []
    pairs: List[Tuple[str, str]] = [(go_header, cj_header)]
    pairs.extend(zip(go_stmts, cj_stmts))
    pairs.append(("}", "}"))
    return pairs


_GO_MAIN_RE = re.compile(r"^func\s+main\s*\(\s*\)\s*\{(.*)\}\s*$", re.S)
_CJ_MAIN_RE = re.compile(r"^main\s*\(\s*\)\s*\{(.*)\}\s*$", re.S)
_GO_FUNC_RE = re.compile(
    r"^func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\([^)]*\)[^{]*\{",
    re.S,
)
_CJ_FUNC_RE = re.compile(
    r"^(?:public\s+)?(?:override\s+)?func\s+([A-Za-z_]\w*)\s*\([^)]*\)[^{]*\{",
    re.S,
)


def _split_func(chunk: str, header_re: re.Pattern) -> Optional[Tuple[str, str]]:
    """Return ``(header_through_open_brace, body_before_close_brace)``
    if ``chunk`` looks like ``func NAME(...) … { body }``, else None.

    Walks the chunk character-by-character to locate the matching
    closing brace; this is more robust than a single ``re.match`` once
    the body itself contains nested ``{`` / ``}``.
    """
    text = chunk.strip()
    match = header_re.match(text)
    if not match:
        return None
    open_brace = match.end() - 1
    # Find the matching ``}`` at depth 1.
    depth = 1
    i = open_brace + 1
    while i < len(text) and depth > 0:
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        return None
    header = text[:open_brace + 1]
    body = text[open_brace + 1:i]
    return header, body


def _unfold_main_body(go_chunk: str, cj_chunk: str) -> List[Tuple[str, str]]:
    """If ``go_chunk`` is ``func main(){…}`` and ``cj_chunk`` is the
    matching ``main(){…}``, return per-statement pairs from their
    bodies.

    Cangjie ``main`` bodies are wrapped in an outer ``return 0`` that
    Go's ``main`` does not have; we strip the trailing ``return 0`` (or
    ``return``) before splitting so the statement counts line up.

    Returned pairs are *only* yielded when both bodies split into the
    same number of top-level statements (otherwise alignment is
    ambiguous and we drop the program).
    """
    gm = _GO_MAIN_RE.match(go_chunk.strip())
    cm = _CJ_MAIN_RE.match(cj_chunk.strip())
    if not (gm and cm):
        return []
    go_body = gm.group(1).strip()
    cj_body = cm.group(1).strip()
    # Strip Cangjie's trailing ``return 0`` (synthesised by the
    # converter, not present in Go).
    cj_body = re.sub(r"\breturn\s+0\s*$", "", cj_body).strip()
    cj_body = re.sub(r"\breturn\s*$", "", cj_body).strip()
    go_stmts = _split_top_level(go_body)
    cj_stmts = _split_top_level(cj_body)
    if len(go_stmts) != len(cj_stmts):
        return []
    # Main-body statements are *not* recursively block-expanded: the
    # existing v0.3.7 trainset already has rich one-block templates
    # (``for i := 0; i < n; i++ { count++ }``) that retrieve cleanly
    # at the whole-block level, and recursive unfold on main would
    # require the trainset to *also* contain bare ``for i := 0; i <
    # NUM; i++ {`` headers (it does not — main bodies typically use
    # literal loop bounds, whereas inside a user function the bound
    # is a parameter identifier).  Recursive expand is therefore
    # reserved for user-function bodies, where chunks are long enough
    # to be worth the OOD risk.
    return list(zip(go_stmts, cj_stmts))


def _unfold_user_func(go_chunk: str, cj_chunk: str) -> List[Tuple[str, str]]:
    """Mirror of :func:`go2cj_new.converter._unfold_functions` for user
    functions, on the **training** side.

    Given a paired Go / Cj user function declaration
    (``func F(...) ret { body }`` vs ``func F(...): Ret { body }``),
    emit three kinds of (Go, Cj) chunk pairs that exactly match what
    the converter's RBU produces at inference time:

    1. A *header* pair — Go ``func F(...) ret {`` ↔ Cj
       ``func F(...): Ret {``.  Stored as its own neuron so the
       inference-time header chunk has a clean exact-template hit.
    2. *Per-statement body* pairs from the function body, aligned by
       top-level statement count.  Identical aim as
       ``_unfold_main_body`` — short, statement-shaped chunks retrieve
       far more accurately than 200-token function chunks.
    3. A *footer* pair — ``}`` ↔ ``}``.

    Returns ``[]`` when the body statement counts disagree
    (alignment is ambiguous; rare on well-curated trainsets).
    """
    gs = _split_func(go_chunk, _GO_FUNC_RE)
    cs = _split_func(cj_chunk, _CJ_FUNC_RE)
    if gs is None or cs is None:
        return []
    go_header, go_body = gs
    cj_header, cj_body = cs
    go_stmts = _split_top_level(go_body.strip())
    cj_stmts = _split_top_level(cj_body.strip())
    if len(go_stmts) != len(cj_stmts):
        return []
    pairs: List[Tuple[str, str]] = [(go_header, cj_header)]
    for g, c in zip(go_stmts, cj_stmts):
        sub = _expand_block_pairs(g, c)
        if sub:
            pairs.extend(sub)
        else:
            pairs.append((g, c))
    pairs.append(("}", "}"))
    return pairs


def _load_programs() -> List[Tuple[str, str]]:
    """Pair-align top-level chunks from ``programs/*.go`` and ``*.cj``.

    For each ``foo.go`` / ``foo.cj`` we segment both, drop
    ``package`` / ``import`` decls, and zip the remaining chunks
    pairwise.  In addition, **for every paired user-function chunk
    (including ``main``) we recursively unfold the body into
    per-statement chunk pairs** — this exactly mirrors the
    inference-time Recursive Block Unfolding in
    ``converter._unfold_functions`` so the neurons CHIME grows from
    training have the same shape as the chunks fed to it at inference.

    Mismatched chunk counts are skipped (they're noisy).
    """
    pdir = TRAINSET / "programs"
    if not pdir.is_dir():
        return []
    pairs: List[Tuple[str, str]] = []
    for go in sorted(pdir.glob("*.go")):
        cj = go.with_suffix(".cj")
        if not cj.exists():
            continue
        go_chunks = [c for c in _split_top_level(go.read_text(encoding="utf-8"))
                     if not c.startswith(("package", "import"))]
        cj_chunks = [c for c in _split_top_level(cj.read_text(encoding="utf-8"))
                     if not c.startswith(("package", "import"))]
        if len(go_chunks) != len(cj_chunks):
            continue
        for g, c in zip(go_chunks, cj_chunks):
            # Main bodies still get the "no header / footer / no
            # ``return 0``" treatment so the synthesised ``main()``
            # wrapper logic on the converter side keeps working.
            unfolded_main = _unfold_main_body(g, c)
            if unfolded_main:
                pairs.extend(unfolded_main)
                continue
            # Generic user functions get the recursive header / body /
            # footer unfolding.  Falls through to the original whole-
            # chunk pair when the function shape doesn't match (e.g.
            # ``type`` / ``var`` decls).
            unfolded_func = _unfold_user_func(g, c)
            if unfolded_func:
                pairs.extend(unfolded_func)
            else:
                pairs.append((g, c))
    return pairs


# --------------------------------------------------------------------------- #
#  Training                                                                   #
# --------------------------------------------------------------------------- #


def train(seed: int = 0, val_frac: float = 0.10, verbose: bool = True) -> CHIME:
    """Run one online pass over the entire trainset.  Returns the
    trained engine."""

    rnd = random.Random(seed)
    pairs = _load_pairs() + _load_programs()
    rnd.shuffle(pairs)

    if not pairs:
        raise RuntimeError("No training pairs found under trainset/.")

    n_val = max(1, int(len(pairs) * val_frac))
    val = pairs[:n_val]
    train_set = pairs[n_val:]

    engine = CHIME()

    t0 = time.time()
    for go_text, cj_text in train_set:
        anon_go, anon_cj = anonymize_pair(go_text, cj_text)
        engine.learn(anon_go, anon_cj)

    # Light replay: cycle through the trainset twice more to refresh
    # Hebbian edges and let the criticality controller settle.  Cost
    # is negligible (no gradients).  Skip if dataset is tiny.
    if len(train_set) > 30:
        for _ in range(2):
            rnd.shuffle(train_set)
            for go_text, cj_text in train_set:
                anon_go, anon_cj = anonymize_pair(go_text, cj_text)
                engine.learn(anon_go, anon_cj)

    train_time = time.time() - t0

    # Validation: exact-template match on held-out anonymized chunks.
    correct = 0
    for go_text, cj_text in val:
        anon_go, anon_cj = anonymize_pair(go_text, cj_text)
        pred, _ = engine.translate(anon_go)
        if pred.strip() == anon_cj.strip():
            correct += 1
    val_acc = correct / max(1, len(val))

    # After measuring validation accuracy, fold the held-out pairs
    # back into the engine so the *deployed* model has seen every
    # curated chunk.  CHIME has no backprop / overfitting failure
    # mode — the substrate is just associative memory, so withholding
    # supervision from the deployed model would only hurt downstream
    # retrieval.  We do this *after* val measurement so val_acc still
    # reflects true held-out generalisation.
    for go_text, cj_text in val:
        anon_go, anon_cj = anonymize_pair(go_text, cj_text)
        engine.learn(anon_go, anon_cj)

    if verbose:
        s = engine.stats()
        print(f"[CHIME] trained on {len(train_set)} pairs in {train_time:.2f}s")
        print(f"[CHIME] val_template_acc = {val_acc:.2%} ({correct}/{len(val)})")
        print(f"[CHIME] neurons={s['neurons']} edges={s['edges']} "
              f"fire_thr={s['fire_threshold']:.3f} "
              f"branching_ema={s['branching_ema']:.3f} "
              f"alpha_hat={s['alpha_hat']:.3f}")

    engine.save(MODEL_DIR)
    # Persist the validation metric for downstream tooling.
    (MODEL_DIR / "meta.json").write_text(json.dumps({
        "n_train_pairs": len(train_set),
        "n_val_pairs": len(val),
        "val_template_acc": val_acc,
        "train_time_s": round(train_time, 3),
        "stats": engine.stats(),
    }, indent=2), encoding="utf-8")
    return engine


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="go2cj_new.critical.train",
                                 description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--val-frac", type=float, default=0.10,
                    help="Held-out fraction (default 0.10).")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    train(seed=args.seed, val_frac=args.val_frac, verbose=not args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
