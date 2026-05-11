"""Core rule-engine.

Each rule is a small object with:
  * a *matcher* that inspects a position in a token stream and returns a
    match descriptor (or None);
  * an *applier* that produces a list of replacement tokens given the
    descriptor;
  * a *confidence* in [0,1] – the engine accumulates a global score so the
    output quality can be estimated.

The driver applies rules repeatedly until a pass produces no change, then
moves to the next priority bucket.  This is the "self-organising" loop
mentioned in the design: high-priority structural rules fire first and
re-shape the token stream so lower-priority rules can match cleaner input.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .tokenizer import Tok


# A match descriptor is opaque to the engine – it is just whatever the
# matcher chose to return alongside the consumed span.
@dataclass
class Match:
    start: int
    end: int
    data: dict = field(default_factory=dict)


MatcherFn = Callable[[List[Tok], int, "Context"], Optional[Match]]
ApplierFn = Callable[[List[Tok], Match, "Context"], List[Tok]]


@dataclass
class Rule:
    name: str
    matcher: MatcherFn
    applier: ApplierFn
    priority: int = 100        # higher fires earlier
    confidence: float = 1.0    # contribution per successful match


@dataclass
class Context:
    """Global state shared across rule firings."""
    # type bindings learned by inference: name -> CJ type
    var_types: dict = field(default_factory=dict)
    # extra Cangjie imports needed (e.g. "std.collection.*")
    imports: set = field(default_factory=set)
    # accumulated quality score
    total_conf: float = 0.0
    total_fires: int = 0
    # ad-hoc helpers we need to inject (e.g. abs/max/min wrappers)
    helpers: set = field(default_factory=set)
    # diagnostic messages
    notes: List[str] = field(default_factory=list)
    # whether the source file already had a main() (TS top-level code)
    has_main: bool = False
    # collected top-level executable statements when wrapping in main()
    pending_top: List[Tok] = field(default_factory=list)


def skip_trivia(tokens: List[Tok], i: int, *, stop_at_nl: bool = False) -> int:
    while i < len(tokens) and tokens[i].kind in ("ws", "cmt") or (
        not stop_at_nl and i < len(tokens) and tokens[i].kind == "nl"
    ):
        i += 1
    return i


def next_significant(tokens: List[Tok], i: int) -> int:
    while i < len(tokens) and tokens[i].kind in ("ws", "nl", "cmt"):
        i += 1
    return i


def prev_significant(tokens: List[Tok], i: int) -> int:
    j = i - 1
    while j >= 0 and tokens[j].kind in ("ws", "nl", "cmt"):
        j -= 1
    return j


def is_punct(t: Tok, v: str) -> bool:
    return t.kind == "punct" and t.value == v


def is_op(t: Tok, v: str) -> bool:
    return t.kind == "op" and t.value == v


def is_kw(t: Tok, v: str) -> bool:
    return t.kind == "kw" and t.value == v


def find_matching(tokens: List[Tok], i: int, open_ch: str, close_ch: str) -> int:
    """Return index of matching close bracket. tokens[i] must be `open_ch`."""
    assert tokens[i].kind == "punct" and tokens[i].value == open_ch
    depth = 1
    j = i + 1
    while j < len(tokens):
        t = tokens[j]
        if t.kind == "punct" and t.value == open_ch:
            depth += 1
        elif t.kind == "punct" and t.value == close_ch:
            depth -= 1
            if depth == 0:
                return j
        # skip nested brackets of other kinds — they will balance themselves
        j += 1
    return -1


def run_rules(tokens: List[Tok], rules: List[Rule], ctx: Context,
              max_passes: int = 8) -> List[Tok]:
    """Run a list of rules to a fixed point (bounded passes)."""
    rules = sorted(rules, key=lambda r: -r.priority)
    for _ in range(max_passes):
        changed = False
        i = 0
        new_tokens: List[Tok] = []
        # We walk left-to-right; on each position we try each rule in
        # priority order. The first to match wins.
        while i < len(tokens):
            fired = False
            for rule in rules:
                m = rule.matcher(tokens, i, ctx)
                if m is None:
                    continue
                replacement = rule.applier(tokens, m, ctx)
                new_tokens.extend(replacement)
                ctx.total_conf += rule.confidence
                ctx.total_fires += 1
                i = m.end
                fired = True
                changed = True
                break
            if not fired:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens
        if not changed:
            break
    return tokens
