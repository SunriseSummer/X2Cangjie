"""End-to-end Swift → Cangjie conversion pipeline.

Architecture closely mirrors :mod:`ts2cj.converter` but with Swift-specific
lexing, patterns, and post-processing.  The pipeline is fully deterministic
(the SOM is seeded) and requires no training data — pattern retrieval relies
on a Kohonen self-organizing map trained on the built-in pattern corpus at
import time, while symbol-level rewrites use a Hopfield-style associative
memory.

Pipeline stages:

1. Token-level pre-rewrite (string interpolation, ``.count`` → ``.size``,
   range operators inside string contexts, ``nil`` → ``None`` etc.).
2. Tokenization (:func:`.lexer.tokenize`).
3. Unbraced control-flow bodies are normalised; chunk segmentation finds
   top-level statements via brace / semicolon-equivalent balance.
4. For each chunk: SOM retrieves a candidate-pattern prior, full corpus is
   re-scored by anchor + cosine, slot binding emits Cangjie source.
5. Post-processing: ``import std.collection.*`` injection, ``main()`` wrap,
   ``override`` analysis, generic-bracket whitespace tightening.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from .embedding import embed_sequence, embed_token, cosine
from .hopfield import HopfieldMemory
from .lexer import Token, tokenize
from .patterns import CHUNK_PATTERNS, Pattern, TOKEN_MAPPINGS
from .som import SOM


# --------------------------------------------------------------------------- #
#  Result type                                                                #
# --------------------------------------------------------------------------- #


@dataclass
class ConversionResult:
    """Output of :func:`convert_source`."""

    source: str
    chunks: int = 0
    confident_chunks: int = 0
    fallback_chunks: int = 0
    patterns_used: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        if self.chunks == 0:
            return 0.0
        return self.confident_chunks / self.chunks


# --------------------------------------------------------------------------- #
#  Shared models (built once)                                                 #
# --------------------------------------------------------------------------- #


def _pattern_tokens(template: str) -> List[Tuple[str, str]]:
    """Split a pattern template string into ``(kind, value)`` pairs."""

    pieces = template.split()
    out: List[Tuple[str, str]] = []
    for p in pieces:
        if p.startswith("$"):
            out.append(("SLOT", p[1:]))
        else:
            out.append(("LIT", p))
    return out


class _Engine:
    """Lazy-loaded singleton holding the trained SOM + Hopfield memory."""

    _instance: Optional["_Engine"] = None

    def __init__(self) -> None:
        self.patterns = CHUNK_PATTERNS
        self.pattern_token_lists = [_pattern_tokens(p.swift_template) for p in self.patterns]
        self.pattern_embeddings = np.stack(
            [embed_sequence(pt) for pt in self.pattern_token_lists]
        )
        self.som = SOM(dim=self.pattern_embeddings.shape[1])
        self.som.train(self.pattern_embeddings)
        self.memory = HopfieldMemory()
        for k, v in TOKEN_MAPPINGS:
            self.memory.remember(k, v)

    @classmethod
    def get(cls) -> "_Engine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# --------------------------------------------------------------------------- #
#  Token-level rewriting (pre-pass)                                           #
# --------------------------------------------------------------------------- #


def _outside_strings_replace(src: str, pairs: List[Tuple[str, str]]) -> str:
    """Apply literal ``str.replace`` rewrites only outside string/comment regions."""

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            # Handle triple-quoted multi-line literal.
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(src[i:end])
                i = end
                continue
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            out.append(src[i:end])
            i = end
            continue
        out.append(ch)
        i += 1
    text = "".join(out)
    for k, v in pairs:
        text = text.replace(k, v)
    return text


def _outside_strings_word_replace(src: str, pairs: List[Tuple[str, str]]) -> str:
    """Apply ``\\bkey\\b`` regex replacements only outside string/comment regions."""

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(src[i:end])
                i = end
                continue
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            out.append(src[i:end])
            i = end
            continue
        out.append(ch)
        i += 1
    text = "".join(out)
    for k, v in pairs:
        text = re.sub(r"\b" + re.escape(k) + r"\b", v, text)
    return text


def _convert_string_interpolations(src: str) -> str:
    """Rewrite Swift ``\\(expr)`` interpolation to Cangjie ``${expr}``.

    We walk the source character-by-character so that nested parens inside
    an interpolation (e.g. ``"\\(f(x))"``) are matched correctly.  Only
    runs *inside* a string literal — strings start at ``"`` and end at the
    matching unescaped ``"``.  Triple-quoted multi-line strings are left
    alone (rare in idiomatic Swift; downstream AI handles them).
    """

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            # Skip triple-quoted strings verbatim.
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(src[i:end])
                i = end
                continue
            # Single-line string — scan & rewrite interpolations.
            out.append('"')
            i += 1
            while i < n:
                if src[i] == "\\" and i + 1 < n:
                    if src[i + 1] == "(":
                        # interpolation — collect balanced parens
                        depth = 1
                        j = i + 2
                        while j < n and depth > 0:
                            if src[j] == "(":
                                depth += 1
                            elif src[j] == ")":
                                depth -= 1
                                if depth == 0:
                                    break
                            j += 1
                        expr = src[i + 2:j]
                        out.append("${" + expr + "}")
                        i = j + 1
                        continue
                    # other escape — keep verbatim
                    out.append(src[i:i + 2])
                    i += 2
                    continue
                if src[i] == '"':
                    out.append('"')
                    i += 1
                    break
                if src[i] == "\n":
                    # Unterminated string — bail out preserving content.
                    out.append("\n")
                    i += 1
                    break
                out.append(src[i])
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _rewrite_source(src: str) -> Tuple[str, List[str]]:
    """Apply safe textual rewrites on the raw Swift source.

    Done before tokenization so that:

    * String interpolation ``\\(expr)`` → ``${expr}``
    * Common member-name swaps (``.count`` → ``.size``, ``.append`` → ``.add``)
    * ``nil`` → ``None`` (word-boundary)

    The bulk of type-name translation happens later, at slot-render time,
    so that primitive type names like ``Int``/``String`` remain available as
    pattern anchors.
    """

    notes: List[str] = []
    # 1. String interpolation first — operates inside string literals.
    src = _convert_string_interpolations(src)
    # 1a-pre-0.  Normalize higher-level Swift library/control-flow idioms into
    # forms the existing token/template pipeline can translate semantically.
    src = _rewrite_named_tuple_accesses(src)
    src = _rewrite_array_repeating_calls(src)
    src = _rewrite_reversed_calls(src)
    src = _rewrite_min_max_calls(src)
    src = _rewrite_stride_for_loops(src)
    src = _rewrite_guard_condition_commas(src)
    src = _rewrite_empty_arrays_in_named_tuple_returns(src)
    # 1a-pre.  Swift iterates ``String`` as Character values.  Cangjie 1.x
    #         string iteration yields bytes for ASCII text, so comparisons like
    #         ``for ch in title { if ch == \"#\" ... }`` need byte literals.
    src = _rewrite_string_iteration_char_comparisons(src)
    # 1a.  Scan for Optional-typed bindings/parameters so subsequent
    #      transforms can promote ``name!`` to ``name.getOrThrow()`` and
    #      ``name == nil`` / ``!= nil`` to ``isNone()`` / ``isSome()``.
    optional_names = _scan_optional_names(src)
    if optional_names:
        # Rewrite force-unwrap *only* for known-optional names.
        for nm in optional_names:
            # ``name!`` (force-unwrap) → ``name.getOrThrow()``.
            src = _outside_strings_regex(
                src, rf"\b{re.escape(nm)}\!(?!=)", f"{nm}.getOrThrow()"
            )
        # Same inside ``${…}`` interpolations.
        def _opt_in_interp(inner: str, _names=tuple(optional_names)) -> str:
            for nm in _names:
                inner = re.sub(
                    rf"\b{re.escape(nm)}\!(?!=)", f"{nm}.getOrThrow()", inner
                )
            return inner
        src = _rewrite_inside_interpolations(src, _opt_in_interp)
        # Equality with nil / None.
        opt_alt = "|".join(re.escape(n) for n in optional_names)
        src = _outside_strings_regex(
            src, rf"\b({opt_alt})\s*==\s*(?:nil|None)\b", r"\1.isNone()"
        )
        src = _outside_strings_regex(
            src, rf"\b({opt_alt})\s*!=\s*(?:nil|None)\b", r"\1.isSome()"
        )
    # 2. Literal text replacements (member-name calls etc.).  These are
    #    distinctive enough that they cannot collide with Swift keywords.
    src = _outside_strings_replace(
        src,
        [
            (".append(", ".add("),
            (".uppercased()", ".toAsciiUpper()"),
            (".lowercased()", ".toAsciiLower()"),
            (".hasPrefix(", ".startsWith("),
            (".hasSuffix(", ".endsWith("),
            # Swift super-constructor call ``super.init(...)`` → ``super(...)``.
            ("super.init(", "super("),
            # ``as!`` / ``as?`` Swift casts — keep ``as`` (Cangjie also has
            # ``as``) and drop the optional/forced markers.
            (" as!", " as"),
            (" as?", " as"),
        ],
    )
    # Swift ``Array.insert(elem, at: i)`` → Cangjie ``ArrayList.add(elem, at: i)``.
    # Use a small balanced scanner instead of a regex so nested call arguments
    # like ``xs.insert(make(a, b), at: i)`` are handled without backtracking.
    src = _rewrite_array_insert_calls(src)
    # ``.count`` is a *property* in Swift (no parens), and Cangjie's
    # collections expose ``.size`` for the same role.  We must NOT rewrite
    # ``.count()`` here — that is almost certainly a user-defined method.
    src = _outside_strings_regex(src, r"\.count(?!\w|\()", ".size")
    # Swift's ``Array(<stringExpr>)`` converts a String to ``[Character]``.
    # In Cangjie the corresponding shape is ``<stringExpr>.toRuneArray()``
    # which returns an ``Array<Rune>``.  Apply when the call has a single
    # identifier / dotted-path argument (the common case in test code).
    src = _outside_strings_regex(
        src,
        r"\bArray\(\s*([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\)",
        r"\1.toRuneArray()",
    )
    # ``.isEmpty`` likewise: in Swift it's a property; Cangjie exposes
    # ``isEmpty()`` as a method.  Add ``()`` only when not already followed
    # by ``(`` (e.g. ``.isEmpty()`` user-method call).
    src = _outside_strings_regex(src, r"\.isEmpty(?!\w|\()", ".isEmpty()")
    # Same two rewrites, but applied to expressions embedded inside
    # ``${…}`` interpolation blocks of string literals.
    def _prop_rewrite(inner: str) -> str:
        inner = re.sub(r"\.count(?!\w|\()", ".size", inner)
        inner = re.sub(r"\.isEmpty(?!\w|\()", ".isEmpty()", inner)
        # Force-unwrap inside interpolations: ``cur!.value`` → ``cur.value``.
        inner = re.sub(r"([A-Za-z_0-9\)\]])\!(?!=)", r"\1", inner)
        return inner
    src = _rewrite_inside_interpolations(src, _prop_rewrite)
    # If any user class declares its own ``count`` member, the rewrite above
    # over-fires on instances of that class.  Identify those instances by
    # name and revert ``.size`` → ``.count`` on the affected receivers
    # (applied AFTER the interpolation pass so both contexts are covered).
    src = _restore_user_count_members(src)
    # 3. Word-boundary identifier swaps.
    src = _outside_strings_word_replace(
        src,
        [
            ("nil", "None"),
            # Swift's ``self`` is ``this`` in Cangjie.
            ("self", "this"),
            # ``try`` at a call site is a Swift-only marker; Cangjie call
            # expressions don't need it.  Drop the surface keyword (the
            # downstream patterns still treat ``try`` blocks via do/catch).
            ("try", ""),
        ],
    )
    # 4. Swift's leading-dot enum shorthand (``.circle``) has no Cangjie
    #    analogue — strip the dot when the preceding character isn't part
    #    of an expression on the left (i.e. it's not a member access).
    src = _strip_leading_enum_dot(src)
    # 4b. Empty array literals at enum-case call sites need explicit container
    #     construction: ``JV.arr([])`` → ``JV.arr(ArrayList<JV>())``.  Case
    #     names are looked up via embedding-cosine for modest robustness.
    _ec_payloads = _scan_enum_case_payloads(src)
    src = _wrap_enum_case_empty_literals(src, _ec_payloads)
    # 5. Tuple element access: Swift uses ``t.0`` / ``t.1``; Cangjie uses
    #    ``t[0]`` / ``t[1]``.  The left side must be a letter/underscore/
    #    ``)``/``]`` — never a digit (so that ``3.14`` is preserved).
    src = _outside_strings_regex(src, r"\b([A-Za-z_]\w*)\.(\d+)\b", r"\1[\2]")
    src = _outside_strings_regex(src, r"(?<=[\)\]])\.(\d+)\b", r"[\1]")
    # 5b. Also apply tuple-element rewrite **inside** ``${...}`` interpolation
    #     blocks, which `_outside_strings_regex` deliberately skips.
    def _tup_rewrite(inner: str) -> str:
        inner = re.sub(r"\b([A-Za-z_]\w*)\.(\d+)\b", r"\1[\2]", inner)
        inner = re.sub(r"(?<=[\)\]])\.(\d+)\b", r"[\1]", inner)
        return inner
    src = _rewrite_inside_interpolations(src, _tup_rewrite)
    # 6. Swift force-unwrap of Optional (``x!``).  Cangjie returns concrete
    #    values from indexable lookups in our test domain, so we simply drop
    #    the trailing ``!`` when it isn't part of ``!=`` or a unary
    #    boolean-not operator.
    src = _outside_strings_regex(
        src, r"([A-Za-z_0-9\)\]])\!(?!=)", r"\1",
    )
    # 6a-pre.  Swift bitwise-NOT operator ``~`` has no direct Cangjie spelling;
    #     Cangjie uses unary ``!`` for *both* logical and bitwise negation on
    #     integers.  Rewrite the operator outside of strings.
    src = _outside_strings_regex(src, r"~", "!")
    # 6a. Drop Swift declaration modifiers that have no Cangjie analogue.
    #     ``mutating`` / ``nonmutating`` / ``lazy`` / ``@discardableResult`` / etc.
    src = _outside_strings_word_replace(
        src,
        [
            ("mutating", ""),
            ("nonmutating", ""),
            ("lazy", ""),
            ("weak", ""),
            ("unowned", ""),
            ("required", ""),
            ("indirect", ""),
            ("fileprivate", "private"),
            ("internal", "public"),
        ],
    )
    # 6b. ``@discardableResult``, ``@objc``, ``@inlinable`` etc. — drop the
    #     whole attribute (line-prefix).
    src = _outside_strings_regex(src, r"@[A-Za-z_]\w*(?:\s*\([^)]*\))?", "")
    # 6b-ii.  Swift's ``inout`` argument marker ``&name`` at call sites.
    #     Cangjie passes reference-types (classes, ArrayList, HashMap…) by
    #     reference already, so the sigil is dropped: ``f(&xs)`` → ``f(xs)``.
    src = _outside_strings_regex(src, r"(?<=[\(,]\s)&(?=[A-Za-z_])", "")
    src = _outside_strings_regex(src, r"(?<=[\(,])&(?=[A-Za-z_])", "")
    # 6b-iii.  Strip ``inout`` keyword in parameter type positions globally.
    #     Whether the param-list parser sees it or not, Cangjie has no
    #     ``inout`` and reference types pass by reference anyway.
    src = _outside_strings_regex(src, r"\binout\b\s*", "")
    # 6b-iii-c.  Some Swift identifiers collide with Cangjie keywords
    #     (``match``, ``where``, ``open`` …).  When the user has declared
    #     a method/field with such a name we rename every usage in the
    #     file with a trailing ``_`` to dodge the collision.
    src = _rename_keyword_collisions(src)
    # 6b-iv-b.  Swift's ``default: break`` (or ``case X: break``) inside a
    #     ``switch`` is a no-op early-exit; Cangjie's ``match`` arms must be
    #     expressions and ``break`` outside a loop is illegal.  Replace bare
    #     ``break`` in those spots with the unit value ``()``.
    src = _outside_strings_regex(
        src, r"(\bdefault\s*:\s*)break\b", r"\1()"
    )
    # 6b-iii-b.  Swift dictionary subscript returns ``T?``; in Cangjie the
    #     HashMap subscript returns ``T`` (and throws on miss).  The
    #     Optional-aware ``dict[k] ?? default`` idiom must be rewritten to
    #     ``dict.get(k) ?? default``.
    src = _outside_strings_regex(
        src,
        r"\b([A-Za-z_]\w*)\[([^\[\]]+)\]\s*\?\?",
        r"\1.get(\2) ??",
    )
    # 6b-iv.  Collection reassignment ``xs = []`` → ``xs.clear()``.
    #     In Swift this re-binds to an empty Array; in Cangjie ArrayList is
    #     a reference type so the equivalent is to clear it in place.  Only
    #     fires when *not* preceded by ``let`` / ``var`` (which would make
    #     it a *declaration* instead — those are typed elsewhere).
    src = _outside_strings_regex(
        src,
        r"(?<!\blet )(?<!\bvar )\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*=\s*\[\]",
        r"\1.clear()",
    )
    # 6b-iv-c.  ``dict[key] = []`` cannot stay as an empty Array literal in
    #     Cangjie — the type is undetermined.  Look up the dict's declared
    #     value type and instantiate an empty container.
    src = _replace_empty_array_dict_assign(src)
    # 6b-iv-d. HashMap subscript returns ``V`` in Cangjie, not ``Option<V>``.
    #     Swift dictionary lookup returns an Optional and commonly appears as
    #     ``dict[key] ?? default`` or ``let maybe = dict[key]`` before
    #     ``if let``.  Rewrite those read contexts to ``dict.get(key)`` for
    #     known dictionary receivers (including parameters and fields).
    src = _rewrite_known_dict_subscript_reads(src)
    # 6b-v.  Array literal used as a function argument / return value.
    #     Swift infers element type from context; Cangjie does not implicitly
    #     coerce ``Array<T>`` to ``ArrayList<T>``.  Detect a non-empty,
    #     homogeneous, non-type, non-dict literal at call-site positions and
    #     wrap it as ``ArrayList<T>([…])``.
    src = _wrap_call_site_array_literals(src)
    # 6b-vi.  Same wrap, but applied inside ``${…}`` interpolation blocks so
    #     call-site array literals embedded in printed expressions also get
    #     a concrete ``ArrayList<T>([…])`` constructor.
    src = _rewrite_inside_interpolations(
        src, lambda inner: _wrap_call_site_array_literals("(" + inner + ")")[1:-1]
    )
    # 6c. Multi-argument ``print(a, b, c)`` — Swift joins args with a single
    #     space; rewrite to ``print("${a} ${b} ${c}")`` so the single-arg
    #     ``println`` we lower to can render the same output.
    src = _rewrite_multi_arg_print(src)
    # 6d. Swift's ``print`` always writes a trailing newline; Cangjie's
    #     ``print`` does not but ``println`` does.  Map every ``print(``
    #     call site uniformly so behaviour matches.
    src = _outside_strings_regex(src, r"\bprint\s*\(", "println(")
    # 7. Closures: ``{ x in body }``  →  ``{ x => body }``.
    #    Tight pattern: parameter list is identifiers (optionally typed) followed
    #    by ``in``; this never collides with ``for x in xs { ... }`` because the
    #    ``in`` there sits *outside* a ``{...}`` body.  When the closure is
    #    bound by ``=`` we additionally annotate bare params as ``Int64`` so
    #    Cangjie can compile (``let f = { x => ... }`` has no surrounding
    #    context for inference); in call-arg positions we leave the params
    #    bare so the callee's higher-order parameter type can drive inference.
    _closure_re = re.compile(
        r"(?P<bind>=\s*)?\{[ \t]*"
        r"(?P<params>\(?[A-Za-z_][\w]*(?:[ \t]*,[ \t]*[A-Za-z_][\w]*)*\)?"
        r"(?:[ \t]*:[ \t]*[A-Za-z_][\w<>\[\]\?,\. ]*)?)"
        r"[ \t]+in\b"
    )

    def _closure_repl(m: re.Match) -> str:
        bind = m.group("bind") or ""
        params = m.group("params")
        # Cangjie multi-arg closure params must NOT be parenthesised:
        # ``{ a, b => … }``, not ``{ (a, b) => … }``.
        params = params.strip()
        if params.startswith("(") and params.endswith(")"):
            params = params[1:-1].strip()
        if bind:
            params = _annotate_closure_params(params)
        return f"{bind}{{ {params} =>"

    src = _outside_strings_regex(src, _closure_re.pattern, _closure_repl)
    # 7b. No-arg closures: ``return { body }``, ``= { body }``, etc. don't
    #     contain an ``in`` so the rule above leaves them as-is.  Cangjie
    #     requires explicit ``=>`` between params and body — for the
    #     zero-arg case insert it directly after the opening brace.  We
    #     only fire when there's no ``=>`` later on the same brace, no
    #     ``in`` (already rewritten), and the preceding context is a
    #     known expression position (``return`` / ``=`` / ``(`` / ``,``).
    src = _outside_strings_regex(
        src,
        r"(\breturn|=|\(|,)(\s*)\{(?![^}\n]*=>)(\s*\n)",
        r"\1\2{ =>\3",
    )
    # 8. ``guard cond else { B }`` is one Swift-only form; the rest of the
    #    function continues after the guard.  We rewrite it to an equivalent
    #    ``if (!(cond)) { B }`` early so the regular ``if`` pattern handles it.
    #
    #    Special form: ``guard let NAME = EXPR else { B }`` binds NAME from an
    #    Optional.  Cangjie has no inverted Optional-binding, but a value-style
    #    ``match`` works: ``let NAME = match (EXPR) { case Some(v) => v;
    #    case None => B }``.  We handle this BEFORE the general ``guard``
    #    rewrite so the literal ``let`` survives the binding form.
    src = _rewrite_guard_let(src)
    src = _outside_strings_regex(
        src,
        r"\bguard[ \t]+(.+?)[ \t]+else[ \t]*\{",
        r"if (!(\1)) {",
    )
    # 9. ``if let NAME = EXPR`` → ``if (let Some(NAME) <- EXPR)``.  The
    #    standard Cangjie idiom for optional binding.  Done at text level so
    #    the existing if-chain machinery picks it up verbatim.
    src = _outside_strings_regex(
        src,
        r"\bif[ \t]+let[ \t]+([A-Za-z_]\w*)[ \t]*=[ \t]*",
        r"if (let Some(\1) <- ",
    )
    # The previous rewrite produces a dangling ``(`` that doesn't match the
    # closing brace; we patch this up below.  Concretely turn
    #   ``if (let Some(NAME) <- EXPR {``
    # into
    #   ``if (let Some(NAME) <- EXPR) {``
    src = _outside_strings_regex(
        src,
        r"(if \(let Some\([A-Za-z_]\w*\) <- [^\n{]+?)[ \t]*\{",
        r"\1) {",
    )
    # ``if (let Some(x) <- m[k])`` where ``m`` is a known HashMap does not
    # work in Cangjie — subscript returns ``V``, not ``Option<V>``.  Rewrite
    # the inner subscript to ``.get(k)`` for any *declared* HashMap receiver
    # so the Optional binding lines up with the value type.
    src = _rewrite_optional_binding_dict_subscript(src)
    # 10. Ternary ``cond ? a : b`` → ``(if (cond) { a } else { b })``.
    #     Very conservative: we only match a ternary that lives on a single
    #     expression-line, doesn't touch dictionary literals (``[k:v]``), and
    #     whose ``a`` / ``b`` are simple parenthesisable expressions.
    src = _rewrite_ternary(src)
    return src, notes


def _rewrite_guard_let(src: str) -> str:
    """Rewrite ``guard let X = EXPR else { BODY }`` to a value-style match:

        let X = match (EXPR) { case Some(v) => v; case None => BODY }

    The Swift ``BODY`` typically diverges (return / throw / break), so the
    ``None`` arm types fine.  We match the *whole* statement including its
    closing brace, walking braces to keep nested ``{…}`` inside the else
    body intact.
    """

    out: List[str] = []
    pat = re.compile(
        r"\bguard[ \t]+let[ \t]+([A-Za-z_]\w*)[ \t]*=[ \t]*(.+?)[ \t]+else[ \t]*\{"
    )
    i, n = 0, len(src)
    while i < n:
        m = pat.search(src, i)
        if not m:
            out.append(src[i:])
            break
        name = m.group(1)
        expr = m.group(2).strip()
        out.append(src[i:m.start()])
        # Walk to find the matching closing brace of the else block.
        depth = 1
        j = m.end()
        while j < n and depth > 0:
            c = src[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = src[m.end():j].strip()
        out.append(
            f"let {name} = match ({expr}) {{ case Some(v) => v; "
            f"case None => ({body}) }}"
        )
        i = j + 1
    return "".join(out)


def _rewrite_optional_binding_dict_subscript(src: str) -> str:
    """In ``if (let Some(x) <- RECV[KEY])`` rewrite ``RECV[KEY]`` →
    ``RECV.get(KEY)`` when ``RECV`` (or its dotted field tail) refers to a
    HashMap.  Cangjie's subscript on HashMap returns ``V`` (panics on miss),
    not ``Option<V>``, so the Optional pattern would otherwise be unsound.

    The receiver set is gathered from textual ``[K: V]`` declarations and
    field initialisers of the form ``var X: [K: V] = [:]`` /
    ``var X = HashMap...`` — best effort, name-keyed.
    """

    # Collect dict-typed receiver names.
    dict_names: set = set()
    decl_re = re.compile(
        r"\b(?:var|let)\s+([A-Za-z_]\w*)\s*:\s*\[[^\[\]]+?:\s*"
    )
    for m in decl_re.finditer(src):
        dict_names.add(m.group(1))
    # Cangjie-shape declarations (after type conversion happened upstream).
    decl_re2 = re.compile(
        r"\b(?:var|let)\s+([A-Za-z_]\w*)\s*:\s*HashMap\s*<"
    )
    for m in decl_re2.finditer(src):
        dict_names.add(m.group(1))
    if not dict_names:
        return src
    alt = "|".join(sorted(re.escape(n) for n in dict_names))
    # Match the receiver as ``(.<field>)*<name>`` — i.e. last segment is dict-typed.
    pat = re.compile(
        rf"(if \(let Some\([A-Za-z_]\w*\) <- )"
        rf"((?:[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\.)?(?:{alt}))"
        rf"\[([^\[\]]+)\]"
    )
    return _outside_strings_regex(src, pat.pattern, r"\1\2.get(\3)")


def _split_top_level_str_aware(s: str, sep: str) -> List[str]:
    """Like :func:`_split_top_level` but skips over ``"..."`` string
    literals, including ones that contain commas or brackets.
    """

    out: List[str] = []
    depth = 0
    buf: List[str] = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if ch == '"':
            if s[i:i + 3] == '"""':
                end = s.find('"""', i + 3)
                end = n if end == -1 else end + 3
                buf.append(s[i:end])
                i = end
                continue
            j = i + 1
            while j < n and s[j] != '"':
                if s[j] == "\\" and j + 1 < n:
                    buf.append(s[i:j + 2])
                    i = j + 2
                    j = i
                    continue
                j += 1
            buf.append(s[i:j + 1])
            i = j + 1
            continue
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth = max(depth - 1, 0)
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    if buf:
        out.append("".join(buf))
    return out


def _rewrite_multi_arg_print(src: str) -> str:
    """Rewrite ``print(a, b, c)`` → ``print("${a} ${b} ${c}")`` so the
    standard Cangjie single-argument ``println`` produces the same surface
    output that Swift's variadic ``print`` does (space-separated).
    """

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        # Find a literal ``print(`` token preceded by a word-boundary char.
        if (
            i + 6 <= n and src[i:i + 6] == "print("
            and (i == 0 or not (src[i - 1].isalnum() or src[i - 1] == "_" or src[i - 1] == "."))
        ):
            # Match balanced parens.
            depth = 1
            j = i + 6
            while j < n and depth > 0:
                c = src[j]
                if c == '"':
                    # Skip string literal.
                    if src[j:j + 3] == '"""':
                        end = src.find('"""', j + 3)
                        j = n if end == -1 else end + 3
                        continue
                    k = j + 1
                    while k < n and src[k] != '"':
                        if src[k] == "\\" and k + 1 < n:
                            k += 2
                            continue
                        k += 1
                    j = k + 1
                    continue
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth == 0:
                inner = src[i + 6:j]
                # Top-level comma split — string-aware.
                parts = _split_top_level_str_aware(inner, ",")
                if len(parts) >= 2:
                    parts = [p.strip() for p in parts if p.strip()]
                    # Build a single interpolated string.  String-literal args
                    # are inlined verbatim (their content placed directly
                    # inside the new string) so we don't generate nested
                    # interpolations like ``${"x"}`` which the lexer rejects.
                    pieces: List[str] = []
                    for p in parts:
                        if (
                            len(p) >= 2 and p.startswith('"') and p.endswith('"')
                            and p.count('"') == 2
                        ):
                            pieces.append(p[1:-1])
                        else:
                            pieces.append("${" + p + "}")
                    body = " ".join(pieces)
                    out.append('print("' + body + '")')
                    i = j + 1
                    continue
        out.append(src[i])
        i += 1
    return "".join(out)


_PROBE_DONE = True


def _rewrite_inside_interpolations(src: str, fn) -> str:
    """Walk *src* and apply ``fn`` to the *contents* of every ``${...}``
    interpolation block that lies inside a (single- or triple-quoted)
    string literal.  Useful for rewrites that must visit the expressions
    embedded in Cangjie string interpolations but otherwise treat string
    literals as opaque.
    """

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            # Detect triple-quoted string.
            triple = src[i:i + 3] == '"""'
            close = '"""' if triple else '"'
            j = i + len(close)
            buf = [close]
            while j < n:
                if not triple and src[j] == "\\" and j + 1 < n:
                    buf.append(src[j:j + 2])
                    j += 2
                    continue
                if src[j:j + 3] == '"""' and triple:
                    buf.append('"""')
                    j += 3
                    break
                if src[j] == '"' and not triple:
                    buf.append('"')
                    j += 1
                    break
                if src[j] == "$" and j + 1 < n and src[j + 1] == "{":
                    depth = 1
                    k = j + 2
                    while k < n and depth > 0:
                        c = src[k]
                        if c == "{":
                            depth += 1
                        elif c == "}":
                            depth -= 1
                            if depth == 0:
                                break
                        elif c == '"':
                            # Skip a nested string literal in the expression.
                            k += 1
                            while k < n and src[k] != '"':
                                if src[k] == "\\" and k + 1 < n:
                                    k += 2
                                    continue
                                k += 1
                        k += 1
                    inner = src[j + 2:k]
                    buf.append("${" + fn(inner) + "}")
                    j = k + 1
                    continue
                buf.append(src[j])
                j += 1
            out.append("".join(buf))
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)



def _rewrite_interpolations_for_ternary(s: str) -> str:
    """Recursively rewrite ternaries that live inside ``${...}`` interpolation
    expressions of a Cangjie string literal.  Cangjie has no native ``?:``
    operator, so any such ternary must be lowered to an ``if`` expression
    before lexing.
    """

    out: List[str] = []
    i, n = 0, len(s)
    while i < n:
        if i + 1 < n and s[i] == "$" and s[i + 1] == "{":
            depth = 1
            j = i + 2
            while j < n and depth > 0:
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner = s[i + 2:j]
            inner_rewritten = _rewrite_ternary_in_expr(inner)
            # Also rewrite tuple-element access inside the interpolation:
            # ``${s1.0}`` → ``${s1[0]}``.  Cangjie has no ``.0`` syntax.
            inner_rewritten = re.sub(
                r"(?<=[A-Za-z_\)\]])\.(\d+)", r"[\1]", inner_rewritten
            )
            out.append("${" + inner_rewritten + "}")
            i = j + 1
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def _rewrite_ternary_in_expr(expr: str) -> str:
    """Rewrite a bare ``a ? b : c`` (no nested ``?:``, no strings, no
    brackets crossing) inside a Cangjie expression.

    Matches a single top-level ternary; we look for ``?`` followed by ``:``
    where neither side contains another ``?``.
    """

    # Find top-level ``?`` (paren/bracket depth 0).
    depth = 0
    qpos = -1
    for k, ch in enumerate(expr):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(depth - 1, 0)
        elif ch == "?" and depth == 0:
            qpos = k
            break
    if qpos < 0:
        return expr
    # Find the matching ``:`` at the same depth.
    depth = 0
    cpos = -1
    for k in range(qpos + 1, len(expr)):
        ch = expr[k]
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(depth - 1, 0)
        elif ch == ":" and depth == 0:
            cpos = k
            break
    if cpos < 0:
        return expr
    cond = expr[:qpos].strip()
    then = expr[qpos + 1:cpos].strip()
    else_ = expr[cpos + 1:].strip()
    return f"if ({cond}) {{ {then} }} else {{ {else_} }}"


def _rewrite_ternary(src: str) -> str:
    """Translate Swift ternary ``a ? b : c`` into a Cangjie ``if`` expression.

    We avoid known false-positives:
    * dictionary literal ``[k: v, ...]`` (the ``?`` doesn't appear before ``:``);
    * type ascription ``name : Type`` (no preceding ``?``);
    * optional type ``T?`` (no following ``:``).
    """

    def repl(m: re.Match) -> str:
        head, a, b = m.group(1), m.group(2).strip(), m.group(3).strip()
        return f"{head} (if ({head}) {{ {a} }} else {{ {b} }})"  # placeholder

    # The naive ``head`` form above ignores that ``head`` is just the trailing
    # character of the condition expression — re-implement properly by walking.
    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        # Skip strings & comments verbatim — but DO process ``${...}``
        # interpolation expressions inside them, since those are evaluated
        # as Cangjie code at runtime and can contain ternaries.
        if src[i] == '"':
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(_rewrite_interpolations_for_ternary(src[i:end]))
                i = end
                continue
            else:
                # Walk over the string, recognising ``${...}`` blocks as
                # code that may contain its own quotes / braces.
                j = i + 1
                while j < n and src[j] != '"':
                    if src[j] == "\\" and j + 1 < n:
                        j += 2
                        continue
                    if src[j] == "$" and j + 1 < n and src[j + 1] == "{":
                        depth = 1
                        k = j + 2
                        while k < n and depth > 0:
                            ch = src[k]
                            if ch == "{":
                                depth += 1
                            elif ch == "}":
                                depth -= 1
                                if depth == 0:
                                    break
                            elif ch == '"':
                                # Skip nested string literal.
                                k += 1
                                while k < n and src[k] != '"':
                                    if src[k] == "\\" and k + 1 < n:
                                        k += 2
                                        continue
                                    k += 1
                            k += 1
                        j = k + 1 if k < n else n
                        continue
                    j += 1
                end = j + 1
            out.append(_rewrite_interpolations_for_ternary(src[i:end]))
            i = end
            continue
        if src[i] == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            out.append(src[i:end])
            i = end
            continue
        if src[i] == "?":
            # Optional type marker (``T?``): if the ``?`` is followed by a
            # type-position delimiter (``,`` ``)`` ``]`` ``}`` ``=`` ``>``
            # ``;`` newline, optionally after whitespace), it cannot be a
            # ternary — skip.
            jcheck = i + 1
            while jcheck < n and src[jcheck] in " \t":
                jcheck += 1
            if jcheck < n and src[jcheck] in ",)]}=>;\n":
                out.append(src[i])
                i += 1
                continue
            # Try to match a ternary starting near here.  Find a ``:`` later
            # on the same line at the same paren/bracket level; ``?`` and ``:``
            # paired only when neither side touches a dict literal.
            depth_p = depth_s = depth_b = 0
            j = i + 1
            colon_pos = -1
            line_end = src.find("\n", i)
            if line_end == -1:
                line_end = n
            while j < line_end:
                c = src[j]
                if c == "(":
                    depth_p += 1
                elif c == ")":
                    if depth_p == 0:
                        break
                    depth_p -= 1
                elif c == "[":
                    depth_s += 1
                elif c == "]":
                    if depth_s == 0:
                        break
                    depth_s -= 1
                elif c == "{":
                    depth_b += 1
                elif c == "}":
                    if depth_b == 0:
                        break
                    depth_b -= 1
                elif c == ":" and depth_p == 0 and depth_s == 0 and depth_b == 0:
                    colon_pos = j
                    break
                elif c == "?" and depth_p == 0 and depth_s == 0 and depth_b == 0:
                    # Nested ternary — bail out.
                    break
                elif c == ";":
                    break
                j += 1
            if colon_pos != -1:
                # Find start of ``cond`` walking backwards from i-1.
                k = i - 1
                while k >= 0 and src[k] in " \t":
                    k -= 1
                cond_end = k + 1
                cond_start = cond_end
                depth_p = depth_s = 0
                while cond_start > 0:
                    c = src[cond_start - 1]
                    if c == ")":
                        depth_p += 1
                    elif c == "(":
                        if depth_p == 0:
                            break
                        depth_p -= 1
                    elif c == "]":
                        depth_s += 1
                    elif c == "[":
                        if depth_s == 0:
                            break
                        depth_s -= 1
                    elif c in "\n;,{":
                        break
                    elif c == ":" and depth_p == 0 and depth_s == 0:
                        # ``:`` at depth 0 is always a statement boundary —
                        # type annotation, case label, dict key — and never
                        # part of our ternary's condition (the matching ``:``
                        # of THIS ``?`` lives forward of ``i``).
                        break
                    elif c in "=" and depth_p == 0 and depth_s == 0:
                        # left-hand side of ``=`` ends the condition.  We must
                        # NOT terminate when ``=`` is part of a comparison /
                        # compound-assign operator: ``==`` ``!=`` ``<=`` ``>=``.
                        # The Cangjie case-arm arrow ``=>`` IS a terminator —
                        # stop unconditionally for that one.
                        prev_c = src[cond_start - 2] if cond_start - 2 >= 0 else ""
                        next_c = src[cond_start] if cond_start < n else ""
                        if next_c == ">":
                            break
                        if prev_c in "=!<>" or next_c == "=":
                            cond_start -= 1
                            continue
                        break
                    cond_start -= 1
                # If the cond starts with a Swift statement-keyword
                # (``return`` / ``throw`` / ``yield``), nudge the start past it
                # so we don't pull the keyword into the ternary's condition.
                cond_text = src[cond_start:cond_end].lstrip()
                for kw in ("return", "throw", "yield"):
                    if cond_text.startswith(kw + " ") or cond_text.startswith(kw + "\t"):
                        nudge = src[cond_start:cond_end].find(kw) + len(kw)
                        cond_start += nudge
                        break
                cond_text = src[cond_start:cond_end].strip()
                then_text = src[i + 1:colon_pos].strip()
                # The else branch runs from ``colon_pos+1`` to end of line or a
                # statement terminator at the outer level.
                end_pos = colon_pos + 1
                depth_p = depth_s = depth_b = 0
                while end_pos < n:
                    c = src[end_pos]
                    if c == "(":
                        depth_p += 1
                    elif c == ")":
                        if depth_p == 0:
                            break
                        depth_p -= 1
                    elif c == "[":
                        depth_s += 1
                    elif c == "]":
                        if depth_s == 0:
                            break
                        depth_s -= 1
                    elif c == "{":
                        depth_b += 1
                    elif c == "}":
                        if depth_b == 0:
                            break
                        depth_b -= 1
                    elif c in "\n;," and depth_p == 0 and depth_s == 0 and depth_b == 0:
                        break
                    end_pos += 1
                else_text = src[colon_pos + 1:end_pos].strip()
                # Quick sanity: cond/then/else must all be non-empty and the
                # condition mustn't end with an "expression-incomplete" op.
                if cond_text and then_text and else_text and not cond_text.endswith(("=", "+", "-", "*", "/", "%", "<", ">", "!")):
                    # Recurse into the branches so nested ternaries are also
                    # lowered.  ``_rewrite_ternary`` itself walks all depths
                    # via its own paren/bracket tracking, so we re-invoke it
                    # rather than the shallower ``_in_expr`` helper.
                    then_text = _rewrite_ternary(then_text)
                    else_text = _rewrite_ternary(else_text)
                    cond_text = _rewrite_ternary(cond_text)
                    replacement = f"(if ({cond_text}) {{ {then_text} }} else {{ {else_text} }})"
                    # Splice: replace src[cond_start:end_pos] with replacement.
                    # ``out`` so far contains src[:i]; we need to rewind ``out``
                    # by (i - cond_start) characters and then emit replacement.
                    rewind = i - cond_start
                    if rewind > 0:
                        joined = "".join(out)
                        joined = joined[:len(joined) - rewind]
                        out = [joined]
                    out.append(replacement)
                    i = end_pos
                    continue
        out.append(src[i])
        i += 1
    return "".join(out)


def _annotate_closure_params(params: str) -> str:
    """Add ``: Int64`` to each bare-identifier closure parameter.

    Examples
    --------
    ``x``        →  ``x: Int64``
    ``a, b``     →  ``a: Int64, b: Int64``
    ``x: Int64`` →  ``x: Int64`` (already typed; passthrough)
    """

    params = params.strip()
    if not params:
        return params
    if params.startswith("(") and params.endswith(")"):
        params = params[1:-1].strip()
    parts = [p.strip() for p in params.split(",") if p.strip()]
    out: List[str] = []
    for p in parts:
        if ":" in p:
            out.append(p)
        else:
            out.append(f"{p}: Int64")
    return ", ".join(out)


def _outside_strings_regex(src: str, pattern: str, repl) -> str:
    """Apply a regex substitution only outside string / comment regions.

    Builds a list of ``(text, is_code)`` segments, applies the substitution
    only to ``is_code=True`` chunks, and rejoins.
    """

    segs: List[Tuple[str, bool]] = []
    i, n = 0, len(src)
    buf: List[str] = []
    while i < n:
        ch = src[i]
        if ch == '"':
            if buf:
                segs.append(("".join(buf), True))
                buf = []
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                segs.append((src[i:end], False))
                i = end
                continue
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            segs.append((src[i:j + 1], False))
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if buf:
                segs.append(("".join(buf), True))
                buf = []
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            segs.append((src[i:end], False))
            i = end
            continue
        buf.append(ch)
        i += 1
    if buf:
        segs.append(("".join(buf), True))
    return "".join(
        re.sub(pattern, repl, text) if is_code else text
        for text, is_code in segs
    )


def _outside_strings_transform(src: str, fn) -> str:
    """Apply *fn* only to code regions outside string / comment spans."""

    segs: List[Tuple[str, bool]] = []
    i, n = 0, len(src)
    buf: List[str] = []
    while i < n:
        ch = src[i]
        if ch == '"':
            if buf:
                segs.append(("".join(buf), True))
                buf = []
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                segs.append((src[i:end], False))
                i = end
                continue
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            segs.append((src[i:j + 1], False))
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if buf:
                segs.append(("".join(buf), True))
                buf = []
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            segs.append((src[i:end], False))
            i = end
            continue
        buf.append(ch)
        i += 1
    if buf:
        segs.append(("".join(buf), True))
    return "".join(fn(text) if is_code else text for text, is_code in segs)


def _rewrite_array_insert_calls(src: str) -> str:
    """Rewrite ``.insert(value, at: index)`` calls to ``.add(value, at: index)``.

    The argument scanner tracks nested ``()``/``[]``/``{}`` pairs, so it is not
    limited to a single parenthesis level.
    """

    def _transform(text: str) -> str:
        out: List[str] = []
        i = 0
        needle = ".insert("
        while True:
            pos = text.find(needle, i)
            if pos < 0:
                out.append(text[i:])
                break
            arg_start = pos + len(needle)
            depth_p = depth_s = depth_b = 0
            split = -1
            j = arg_start
            while j < len(text):
                ch = text[j]
                if ch == "(":
                    depth_p += 1
                elif ch == ")":
                    if depth_p == 0:
                        break
                    depth_p -= 1
                elif ch == "[":
                    depth_s += 1
                elif ch == "]":
                    depth_s = max(depth_s - 1, 0)
                elif ch == "{":
                    depth_b += 1
                elif ch == "}":
                    depth_b = max(depth_b - 1, 0)
                elif (
                    ch == "," and depth_p == 0 and depth_s == 0 and depth_b == 0
                    and text[j + 1:].lstrip().startswith("at:")
                ):
                    split = j
                j += 1
            if j >= len(text) or split < 0:
                out.append(text[i:pos + len(needle)])
                i = pos + len(needle)
                continue
            out.append(text[i:pos])
            out.append(".add(")
            out.append(text[arg_start:split])
            out.append(text[split:j])
            out.append(")")
            i = j + 1
        return "".join(out)

    return _outside_strings_transform(src, _transform)


def _restore_user_count_members(src: str) -> str:
    """If any user-defined class declares a stored member named ``count``,
    revert the global ``.count → .size`` rewrite for accesses targeting
    instances of that class.  Identification is heuristic: classes that
    declare ``var count`` or ``let count`` at the top of their body are
    captured, then variables initialised from those classes' constructors
    or annotated with their type are tracked, and ``.size`` is restored to
    ``.count`` *only* for those receivers.  Also applies inside ``${…}``
    interpolations.
    """

    # 1. Classes that declare ``count`` as a member.
    classes_with_count: set = set()
    cls_re = re.compile(r"\bclass\s+([A-Za-z_]\w*)(?:\s*[<:][^{]*)?\s*\{")
    for m in cls_re.finditer(src):
        cname = m.group(1)
        brace_start = m.end() - 1
        depth = 1
        j = brace_start + 1
        n = len(src)
        while j < n and depth > 0:
            c = src[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        body = src[brace_start + 1:j - 1]
        if re.search(r"\b(?:var|let)\s+count\b", body):
            classes_with_count.add(cname)
    if not classes_with_count:
        return src
    # Within classes that own a user member named ``count``, ``self.count`` has
    # already become ``self.size`` by the global collection-property rewrite.
    # Restore the receiver forms used before/after the ``self`` → ``this``
    # lowering.
    src = _outside_strings_regex(src, r"\b(self|this)\.size\b(?!\w|\()", r"\1.count")
    # 2. Variables of those classes (``let x = Foo(…)`` / ``var x: Foo``).
    cls_alt = "|".join(re.escape(c) for c in classes_with_count)
    inst_names: set = set()
    for m in re.finditer(
        rf"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*({cls_alt})\s*\(",
        src,
    ):
        inst_names.add(m.group(1))
    for m in re.finditer(
        rf"\b(?:let|var)\s+([A-Za-z_]\w*)\s*:\s*({cls_alt})\b",
        src,
    ):
        inst_names.add(m.group(1))
    # Also class member ``var X: Foo`` declarations.
    for m in re.finditer(
        rf"\b(?:var|let)\s+([A-Za-z_]\w*)\s*:\s*({cls_alt})\b",
        src,
    ):
        inst_names.add(m.group(1))
    # Propagate through ``let|var Y = X`` chains so locals like ``var node =
    # root`` inherit the receiver classification.  Fixed-point iteration
    # since chains can have arbitrary length.
    rhs_re = re.compile(
        r"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\b"
    )
    changed = True
    while changed:
        changed = False
        for m in rhs_re.finditer(src):
            if m.group(2) in inst_names and m.group(1) not in inst_names:
                inst_names.add(m.group(1))
                changed = True
    if not inst_names:
        return src
    # 3. Restore ``.size`` → ``.count`` on those receivers.
    alt = "|".join(re.escape(n) for n in inst_names)
    src = _outside_strings_regex(
        src, rf"\b({alt})\.size\b(?!\w|\()", r"\1.count",
    )
    # Inside ``${…}`` interpolations too.
    def _inner(inner: str, _alt=alt) -> str:
        return re.sub(
            rf"\b({_alt})\.size\b(?!\w|\()", r"\1.count", inner,
        )
    src = _rewrite_inside_interpolations(src, _inner)
    return src


_CJ_KEYWORDS_USER_COLLISION = ("match", "where", "init", "do", "try", "catch")


def _rename_keyword_collisions(src: str) -> str:
    """Swift permits identifiers (method names, fields, locals) that
    collide with Cangjie reserved words such as ``match`` / ``where``.
    When the source declares such an identifier, rename every textual
    occurrence to ``<name>_`` so the emitted Cangjie compiles.  Only the
    member-call form ``.<name>(`` / ``.<name>`` is touched along with
    the declaration site, so ordinary control-flow keywords elsewhere
    in the file are not disturbed.
    """

    for kw in _CJ_KEYWORDS_USER_COLLISION:
        # Method/init declaration: ``func match(...)`` / ``init(...)``.
        decl_re = re.compile(rf"\bfunc\s+{re.escape(kw)}\b")
        if not decl_re.search(src):
            continue
        # Declaration.
        src = _outside_strings_regex(src, rf"\bfunc\s+{re.escape(kw)}\b", f"func {kw}_")
        # Call sites: ``x.match(...)`` and bare ``match(...)``.
        src = _outside_strings_regex(
            src, rf"(?<=\.)\b{re.escape(kw)}\b(?=\s*\()", f"{kw}_"
        )
        src = _outside_strings_regex(
            src,
            rf"(?<![A-Za-z0-9_.])\b{re.escape(kw)}\b(?=\s*\()",
            f"{kw}_",
        )
    return src


def _replace_empty_array_dict_assign(src: str) -> str:
    """Find ``var/let X: [K: [V]] = …`` (or ``[K: V]`` where V is itself an
    array type) declarations and rewrite any subsequent ``X[k] = []``
    assignment so the empty literal is instantiated with the declared
    value type.  ``X[k] = ArrayList<V>()`` for array values; nothing for
    scalar values (the rewrite is no-op).
    """

    # Find dict declarations of the form ``[K: V]`` and remember X → V text.
    val_ty: dict = {}
    decl_re = re.compile(
        r"\b(?:var|let)\s+([A-Za-z_]\w*)\s*:\s*\[([^\[\]:]+):\s*((?:\[[^\]]*\]|[^\[\]])+)\]"
    )
    for m in decl_re.finditer(src):
        name = m.group(1).strip()
        v_raw = m.group(3).strip()
        v_translated = _convert_type_text(v_raw)
        val_ty[name] = v_translated
    if not val_ty:
        return src
    for name, vty in val_ty.items():
        # Only meaningful when value type is a concrete container/class.
        empty_init = f"{vty}()"
        src = _outside_strings_regex(
            src,
            rf"\b{re.escape(name)}\[([^\[\]]+)\]\s*=\s*\[\]",
            rf"{name}[\1] = {empty_init}",
        )
        # ``name.get(<key>) ?? []``  →  ``name.get(<key>) ?? V()`` so that the
        # nil-coalesce fallback has the same container type as the success arm.
        # Cangjie cannot promote an empty Array literal to ArrayList here.
        src = _outside_strings_regex(
            src,
            rf"\b{re.escape(name)}\.get\(([^()]*)\)\s*\?\?\s*\[\]",
            rf"{name}.get(\1) ?? {empty_init}",
        )
        # Same rewrite for the subscript form that may appear inside string
        # interpolation: ``${name[k] ?? []}`` → ``${name.get(k) ?? V()}``.
        def _inside(text: str, _n=name, _e=empty_init) -> str:
            return re.sub(
                rf"\b{re.escape(_n)}\[([^\[\]]+)\]\s*\?\?\s*\[\]",
                rf"{_n}.get(\1) ?? {_e}",
                text,
            )
        src = _rewrite_inside_interpolations(src, _inside)
    return src


def _scan_dict_names(src: str) -> set:
    """Return variable / parameter / field names declared as Swift dictionaries.

    This is intentionally name-based and lightweight; it powers several
    Swift-dictionary → Cangjie-HashMap rewrites before tokenisation.
    """

    names: set = set()
    decl_re = re.compile(
        r"\b(?:var|let)\s+([A-Za-z_]\w*)\s*:\s*\[([^\[\]:]+):\s*((?:\[[^\]]*\]|[^\[\]])+)\]"
    )
    for m in decl_re.finditer(src):
        names.add(m.group(1))
    param_re = re.compile(
        r"(?:[(,]\s*(?:_\s+)?)([A-Za-z_]\w*)\s*:\s*\[([^\[\]:]+):\s*((?:\[[^\]]*\]|[^\[\]])+)\]"
    )
    for m in param_re.finditer(src):
        names.add(m.group(1))
    dict_func_re = re.compile(
        r"\bfunc\s+([A-Za-z_]\w*)\s*\([^)]*\)\s*->\s*\[[^\[\]:]+:\s*((?:\[[^\]]*\]|[^\[\]])+)\]"
    )
    dict_funcs = set(m.group(1) for m in dict_func_re.finditer(src))
    if dict_funcs:
        func_alt = "|".join(sorted(re.escape(n) for n in dict_funcs))
        for m in re.finditer(
            rf"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:{func_alt})\s*\(",
            src,
        ):
            names.add(m.group(1))
    return names


def _find_matching(src: str, open_idx: int, open_ch: str, close_ch: str) -> int:
    """Find the matching closing delimiter for ``src[open_idx]``.

    Args:
        src: Source text to scan.
        open_idx: Index of the already-seen opening delimiter.
        open_ch: Opening delimiter character.
        close_ch: Closing delimiter character.

    Returns:
        The index of the matching closing delimiter, or ``-1`` if no balanced
        close is found.  Nested delimiter pairs and string literals are
        accounted for.
    """

    depth = 1
    i = open_idx + 1
    in_str = False
    esc = False
    while i < len(src):
        ch = src[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return -1


def _parse_labeled_call_args(arg_text: str) -> dict:
    """Parse Swift-style labeled call arguments into ``label -> value``.

    Args:
        arg_text: Text inside a call's parentheses, e.g. ``"from: a, by: -1"``.

    Returns:
        A dictionary mapping each top-level argument label to its value text.
    """

    out: dict = {}
    for part in _split_top_level(arg_text, ","):
        if ":" not in part:
            continue
        label, value = part.split(":", 1)
        out[label.strip()] = value.strip()
    return out


def _parse_array_repeating_call(expr: str) -> Optional[Tuple[str, str]]:
    """Parse ``Array(repeating: value, count: n)`` call text.

    Args:
        expr: Candidate expression text.

    Returns:
        ``(repeating_value, count)`` when the expression matches the Swift
        initializer form; otherwise ``None``.
    """

    expr = expr.strip()
    if not expr.startswith("Array"):
        return None
    m = re.match(r"Array\s*\(", expr)
    if not m:
        return None
    close = _find_matching(expr, m.end() - 1, "(", ")")
    if close != len(expr) - 1:
        return None
    args = _parse_labeled_call_args(expr[m.end():close])
    if "repeating" not in args or "count" not in args:
        return None
    return args["repeating"], args["count"]


def _rewrite_array_repeating_calls(src: str) -> str:
    """Swift ``Array(repeating:count:)`` -> helper-backed ArrayList creation.

    Args:
        src: Swift source text after interpolation normalization.

    Returns:
        Source text with repeating-array initializers rewritten to helper calls.

    The nested two-dimensional form gets its own helper so each row is a fresh
    ArrayList rather than repeated references to the same mutable row.
    """

    out: List[str] = []
    i = 0
    while i < len(src):
        m = re.search(r"\bArray\s*\(", src[i:])
        if not m:
            out.append(src[i:])
            break
        start = i + m.start()
        paren = i + m.end() - 1
        close = _find_matching(src, paren, "(", ")")
        if close < 0:
            out.append(src[i:])
            break
        call = src[start:close + 1]
        parsed = _parse_array_repeating_call(call)
        if not parsed:
            out.append(src[i:close + 1])
            i = close + 1
            continue
        value, count = parsed
        nested = _parse_array_repeating_call(value)
        out.append(src[i:start])
        if nested:
            inner_value, inner_count = nested
            out.append(f"_swiftArray2DRepeating({inner_value}, {count}, {inner_count})")
        else:
            out.append(f"_swiftArrayRepeating({value}, {count})")
        i = close + 1
    return "".join(out)


def _rewrite_reversed_calls(src: str) -> str:
    """Rewrite Swift ``xs.reversed()`` calls to a Cangjie helper call.

    Args:
        src: Swift source text.

    Returns:
        Source text where simple ``.reversed()`` calls use
        ``_swiftArrayReversed(xs)``.
    """

    return _outside_strings_regex(
        src,
        r"\b([A-Za-z_]\w*(?:\[[^\]]+\])?)\.reversed\(\)",
        r"_swiftArrayReversed(\1)",
    )


def _rewrite_min_max_calls(src: str) -> str:
    """Rewrite Swift stdlib ``min``/``max`` two-arg calls to Cangjie if-exprs.

    Args:
        src: Swift source text.

    Returns:
        Source text with free ``min(a, b)`` / ``max(a, b)`` calls rewritten to
        Cangjie ``if`` expressions.  Member calls and function declarations are
        left unchanged.
    """

    out: List[str] = []
    i = 0
    while i < len(src):
        m = re.search(r"(?<![\w.])(min|max)\s*\(", src[i:])
        if not m:
            out.append(src[i:])
            break
        name = m.group(1)
        start = i + m.start()
        paren = i + m.end() - 1
        if re.search(r"\bfunc\s+$", src[max(0, start - 12):start]):
            out.append(src[i:paren + 1])
            i = paren + 1
            continue
        close = _find_matching(src, paren, "(", ")")
        if close < 0:
            out.append(src[i:])
            break
        args = _split_top_level(src[paren + 1:close], ",")
        if len(args) != 2:
            out.append(src[i:close + 1])
            i = close + 1
            continue
        a = re.sub(r"//.*", "", args[0]).strip()
        b = re.sub(r"//.*", "", args[1]).strip()
        if not a or not b:
            out.append(src[i:close + 1])
            i = close + 1
            continue
        op = "<" if name == "min" else ">"
        out.append(src[i:start])
        out.append(f"(if ({a} {op} {b}) {{ {a} }} else {{ {b} }})")
        i = close + 1
    return "".join(out)


def _rewrite_stride_for_loops(src: str) -> str:
    """Lower ``for x in stride(from:..., through/to:..., by:...)`` to while.

    Args:
        src: Swift source text.

    Returns:
        Source text with stride-based ``for`` loops rewritten to equivalent
        ``var`` + ``while`` loops.
    """

    out: List[str] = []
    i = 0
    pat = re.compile(r"\bfor\s+([A-Za-z_]\w*)\s+in\s+stride\s*\(")
    while i < len(src):
        m = pat.search(src, i)
        if not m:
            out.append(src[i:])
            break
        var = m.group(1)
        paren = m.end() - 1
        close = _find_matching(src, paren, "(", ")")
        if close < 0:
            out.append(src[i:])
            break
        j = close + 1
        while j < len(src) and src[j].isspace():
            j += 1
        if j >= len(src) or src[j] != "{":
            out.append(src[i:close + 1])
            i = close + 1
            continue
        body_end = _find_matching(src, j, "{", "}")
        if body_end < 0:
            out.append(src[i:])
            break
        args = _parse_labeled_call_args(src[paren + 1:close])
        start_expr = args.get("from")
        end_expr = args.get("through") or args.get("to")
        step_expr = args.get("by")
        if not start_expr or not end_expr or not step_expr:
            out.append(src[i:body_end + 1])
            i = body_end + 1
            continue
        negative = step_expr.strip().startswith("-")
        inclusive = "through" in args
        if negative:
            cond_op = ">=" if inclusive else ">"
            step_stmt = f"{var} -= {step_expr.strip()[1:].strip()}"
        else:
            cond_op = "<=" if inclusive else "<"
            step_stmt = f"{var} += {step_expr.strip()}"
        body = src[j + 1:body_end].rstrip()
        out.append(src[i:m.start()])
        out.append(
            f"var {var} = {start_expr}\n"
            f"while {var} {cond_op} {end_expr} {{"
            f"{body}\n    {step_stmt}\n}}"
        )
        i = body_end + 1
    return "".join(out)


def _rewrite_guard_condition_commas(src: str) -> str:
    """Convert comma-separated Swift ``guard`` conditions to ``&&``.

    Args:
        src: Swift source text.

    Returns:
        Source text where top-level commas in guard conditions are logical AND
        operators that the Cangjie condition emitter can handle.
    """

    def repl(m: re.Match) -> str:
        cond = m.group(1)
        parts = _split_top_level(cond, ",")
        if len(parts) <= 1:
            return m.group(0)
        return "guard " + " && ".join(p.strip() for p in parts) + " else {"

    return _outside_strings_regex(src, r"\bguard\s+(.+?)\s+else\s*\{", repl)


def _scan_named_tuple_returns(src: str) -> dict:
    """Scan function declarations with named tuple return types.

    Args:
        src: Swift source text.

    Returns:
        A mapping of function name to ``[(label, swift_type), ...]`` entries
        for each named tuple element.
    """

    out: dict = {}
    func_re = re.compile(r"\bfunc\s+([A-Za-z_]\w*)\s*\([^{}]*\)\s*->\s*\(([^{}]+)\)\s*\{")
    for m in func_re.finditer(src):
        labels: List[Tuple[str, str]] = []
        for elem in _split_top_level(m.group(2), ","):
            if ":" not in elem:
                labels = []
                break
            label, ty = elem.split(":", 1)
            labels.append((label.strip(), ty.strip()))
        if labels:
            out[m.group(1)] = labels
    return out


def _rewrite_named_tuple_accesses(src: str) -> str:
    """Rewrite named tuple field accesses to Cangjie tuple indices.

    Args:
        src: Swift source text.

    Returns:
        Source text where bindings of functions returning named tuples can be
        accessed as ``result[0]`` instead of Swift's ``result.maxValue`` form.
    """

    tuple_returns = _scan_named_tuple_returns(src)
    for fn, labels in tuple_returns.items():
        binding_re = re.compile(rf"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*{re.escape(fn)}\s*\(")
        for bm in list(binding_re.finditer(src)):
            var = bm.group(1)
            for idx, (label, _ty) in enumerate(labels):
                src = _outside_strings_regex(
                    src,
                    rf"\b{re.escape(var)}\.{re.escape(label)}\b",
                    f"{var}[{idx}]",
                )
                src = _rewrite_inside_interpolations(
                    src,
                    lambda inner, _v=var, _l=label, _i=idx: re.sub(
                        rf"\b{re.escape(_v)}\.{re.escape(_l)}\b",
                        f"{_v}[{_i}]",
                        inner,
                    ),
                )
    return src


def _rewrite_empty_arrays_in_named_tuple_returns(src: str) -> str:
    """Type empty array literals in named tuple return statements.

    Args:
        src: Swift source text.

    Returns:
        Source text where tuple returns such as ``return (0, [])`` use explicit
        ``ArrayList<T>()`` constructors when the named tuple return annotation
        provides the array element type.
    """

    tuple_returns = _scan_named_tuple_returns(src)
    if not tuple_returns:
        return src
    out: List[str] = []
    pos = 0
    func_re = re.compile(r"\bfunc\s+([A-Za-z_]\w*)\s*\([^{}]*\)\s*->\s*\(([^{}]+)\)\s*\{")
    for m in func_re.finditer(src):
        fn = m.group(1)
        labels = tuple_returns.get(fn)
        if not labels:
            continue
        body_end = _find_matching(src, m.end() - 1, "{", "}")
        if body_end < 0:
            continue
        out.append(src[pos:m.start()])
        body = src[m.start():body_end + 1]
        converted_types = [_convert_type_text(ty) for _label, ty in labels]

        def ret_repl(rm: re.Match) -> str:
            elems = [p.strip() for p in _split_top_level(rm.group(1), ",")]
            if len(elems) != len(converted_types):
                return rm.group(0)
            for idx, elem in enumerate(elems):
                if elem == "[]" and converted_types[idx].startswith("ArrayList<"):
                    elems[idx] = f"{converted_types[idx]}()"
            return "return (" + ", ".join(elems) + ")"

        body = re.sub(r"return\s*\(([^()\n]*)\)", ret_repl, body)
        out.append(body)
        pos = body_end + 1
    out.append(src[pos:])
    return "".join(out)


def _rewrite_string_iteration_char_comparisons(src: str) -> str:
    """Rewrite ASCII Character comparisons from Swift string iteration.

    Swift ``for ch in someString`` binds ``ch`` as ``Character`` and permits
    ``ch == "#"``.  Cangjie string iteration yields ``UInt8`` for ASCII text,
    so the equivalent comparison is ``ch == UInt8(35)``.  We infer only loop
    variables proven to come from ``String`` or ``[String]`` flows.
    """

    string_names: set = set()
    string_arrays: set = set()
    for m in re.finditer(r"\b(?:let|var)\s+([A-Za-z_]\w*)\s*:\s*String\b", src):
        string_names.add(m.group(1))
    for m in re.finditer(r"(?:[(,]\s*(?:_\s+)?)([A-Za-z_]\w*)\s*:\s*String\b", src):
        string_names.add(m.group(1))
    for m in re.finditer(r"\b(?:let|var)\s+([A-Za-z_]\w*)\s*:\s*\[\s*String\s*\]", src):
        string_arrays.add(m.group(1))
    for m in re.finditer(r"(?:[(,]\s*(?:_\s+)?)([A-Za-z_]\w*)\s*:\s*\[\s*String\s*\]", src):
        string_arrays.add(m.group(1))
    for m in re.finditer(r"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*\[([^\]]*)\]", src):
        parts = [p.strip() for p in _split_top_level(m.group(2), ",") if p.strip()]
        if parts and all(re.match(r'^"(?:\\.|[^"\\])*"$', p) for p in parts):
            string_arrays.add(m.group(1))

    char_vars: set = set()
    loop_re = re.compile(r"\bfor\s+([A-Za-z_]\w*)\s+in\s+([^{\n]+)\{")
    changed = True
    while changed:
        changed = False
        for m in loop_re.finditer(src):
            var = m.group(1)
            expr = m.group(2).strip()
            base = expr.split(".", 1)[0].strip()
            if expr.startswith('"') or expr in string_names or base in string_names:
                if var not in char_vars:
                    char_vars.add(var)
                    changed = True
            elif expr in string_arrays or base in string_arrays:
                if var not in string_names:
                    string_names.add(var)
                    changed = True
    if not char_vars:
        return src

    alt = "|".join(sorted(re.escape(v) for v in char_vars))

    def _byte_for_literal(lit: str) -> str:
        raw = lit[1:-1]
        if raw.startswith("\\"):
            escapes = {
                "\\0": "\0",
                "\\t": "\t",
                "\\n": "\n",
                "\\r": "\r",
                "\\\"": "\"",
                "\\'": "'",
                "\\\\": "\\",
            }
            text = escapes.get(raw, raw)
        else:
            text = raw
        if len(text) != 1:
            return lit
        if ord(text) > 255:
            return lit
        return f"UInt8({ord(text)})"

    def _rhs(m: re.Match) -> str:
        return f"{m.group(1)} {m.group(2)} {_byte_for_literal(m.group(3))}"

    def _lhs(m: re.Match) -> str:
        return f"{_byte_for_literal(m.group(1))} {m.group(2)} {m.group(3)}"

    src = re.sub(rf"\b({alt})\s*(==|!=)\s*(\"(?:\\.|[^\"\\])\")", _rhs, src)
    src = re.sub(rf"(\"(?:\\.|[^\"\\])\")\s*(==|!=)\s*\b({alt})\b", _lhs, src)

    def _char_interp(inner: str, known_char_vars=char_vars) -> str:
        stripped = inner.strip()
        if stripped in known_char_vars:
            return f"Rune({stripped})"
        return inner

    src = _rewrite_inside_interpolations(src, _char_interp)
    return src


def _rewrite_known_dict_subscript_reads(src: str) -> str:
    """Rewrite read-context dictionary subscripts to ``.get``.

    Swift ``dict[key]`` is optional; Cangjie ``HashMap`` subscript is not.
    For known dictionary receivers we therefore rewrite:

    * ``dict[key] ?? fallback`` → ``dict.get(key) ?? fallback``
    * ``let tmp = dict[key]``   → ``let tmp = dict.get(key)``

    and apply the coalescing form inside string interpolations as well.
    """

    names = _scan_dict_names(src)
    if not names:
        return src
    alt = "|".join(sorted(re.escape(n) for n in names))
    # Optional tests on dictionary reads.
    src = _outside_strings_regex(
        src,
        rf"\b({alt})\[([^\[\]]+)\]\s*==\s*(?:nil|None)\b",
        r"\1.get(\2).isNone()",
    )
    src = _outside_strings_regex(
        src,
        rf"\b({alt})\[([^\[\]]+)\]\s*!=\s*(?:nil|None)\b",
        r"\1.get(\2).isSome()",
    )
    # Nil-coalescing reads, including ``${m[k] ?? d}`` through the
    # interpolation-aware pass below.
    coalesce_pat = rf"\b({alt})\[([^\[\]]+)\]\s*\?\?"
    src = _outside_strings_regex(src, coalesce_pat, r"\1.get(\2) ??")
    # Same shape when the key expression itself contains string literals, e.g.
    # ``walls["${r},${c}"] ?? false``.  The generic outside-string splitter
    # cannot match across the quoted key, so use a string-literal-aware key
    # pattern here.
    quoted_key_pat = re.compile(
        rf"\b({alt})\[((?:[^\[\]\"]|\"(?:\\.|[^\"\\])*\")*)\]\s*\?\?"
    )
    src = quoted_key_pat.sub(r"\1.get(\2) ??", src)

    def _inside(inner: str, _pat=coalesce_pat) -> str:
        return re.sub(_pat, r"\1.get(\2) ??", inner)

    src = _rewrite_inside_interpolations(src, _inside)
    # Optional-preserving temporary bindings, but only when immediately used by
    # Swift's optional-binding syntax.  Plain ``let a = dict[key]`` in Swift is
    # often used when the key is known to exist; rewriting every such binding to
    # Option would degrade downstream member access quality.
    src = _outside_strings_regex(
        src,
        rf"\b((?:let|var)\s+([A-Za-z_]\w*)\s*=\s*)({alt})\[([^\[\]]+)\](\s*\n\s*if\s+let\s+[A-Za-z_]\w*\s*=\s*\2\b)",
        r"\1\3.get(\4)\5",
    )
    return src


def _wrap_call_site_array_literals(src: str) -> str:
    """Find ``[…]`` array literals appearing in call-site / return-value
    positions (preceded by ``(``, ``,`` or ``return``) and wrap them as
    ``ArrayList<T>([…])`` when the element type can be inferred from
    homogeneous literal members.  Skips string interior, type-position
    literals (``: [Int]``), dictionary literals (``[k: v]``) and empty
    literals (``[]`` — there is no context-free type to choose).
    """

    out: List[str] = []
    i, n = 0, len(src)
    in_string = False
    string_kind = None
    while i < n:
        ch = src[i]
        if not in_string:
            if ch == '"':
                if src[i:i + 3] == '"""':
                    end = src.find('"""', i + 3)
                    end = n if end == -1 else end + 3
                    out.append(src[i:end])
                    i = end
                    continue
                # Single-line string — pass through.
                j = i + 1
                while j < n and src[j] != '"':
                    if src[j] == "\\" and j + 1 < n:
                        j += 2
                        continue
                    j += 1
                out.append(src[i:j + 1])
                i = j + 1
                continue
            if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
                if src[i + 1] == "/":
                    end = src.find("\n", i)
                    end = n if end == -1 else end
                else:
                    end = src.find("*/", i)
                    end = n if end == -1 else end + 2
                out.append(src[i:end])
                i = end
                continue
            if ch == "[":
                # Look at the previous non-space char.
                k = len(out) - 1
                prev = ""
                while k >= 0 and out[k] in (" ", "\t", "\n"):
                    k -= 1
                if k >= 0:
                    prev = out[k]
                # Already inside an explicit ``ArrayList<T>([...])``
                # constructor: keep its backing array literal unchanged.
                if re.search(r"\bArrayList\s*<[^<>]+>\s*\(\s*$", "".join(out)):
                    out.append(ch)
                    i += 1
                    continue
                # Subscript ``foo[x]`` — prev is identifier letter / ``)`` / ``]``.
                if prev and (prev.isalnum() or prev == "_" or prev in ")]"):
                    out.append(ch)
                    i += 1
                    continue
                # Type position: preceded by ``:`` (annotation) — skip.
                if prev == ":":
                    out.append(ch)
                    i += 1
                    continue
                # Balanced-bracket scan for the closing ``]``.
                depth = 1
                j = i + 1
                in_str2 = False
                while j < n and depth > 0:
                    c = src[j]
                    if in_str2:
                        if c == "\\" and j + 1 < n:
                            j += 2
                            continue
                        if c == '"':
                            in_str2 = False
                    else:
                        if c == '"':
                            in_str2 = True
                        elif c == "[":
                            depth += 1
                        elif c == "]":
                            depth -= 1
                            if depth == 0:
                                break
                    j += 1
                if depth != 0:
                    out.append(ch)
                    i += 1
                    continue
                inner = src[i + 1:j]
                stripped = inner.strip()
                if not stripped:
                    out.append(ch)
                    i += 1
                    continue
                if not _is_pair_free(inner):
                    # Dictionary literal.  Wrap at call-site / return positions
                    # as ``HashMap([(k, v), ...])`` so Cangjie can infer the
                    # element type from context.  Empty ``[:]`` and type-position
                    # literals are not affected.
                    if prev in ("(", ",") or _ends_with_word(out, "return"):
                        # Recurse into the inner text so nested dict/array
                        # literals are also wrapped before we form the pairs.
                        inner_rec = _wrap_call_site_array_literals(
                            "(" + inner + ")"
                        )[1:-1]
                        pairs = _convert_dict_literal_to_pairs(inner_rec)
                        if pairs is not None:
                            out.append(f"HashMap([{pairs}])")
                            i = j + 1
                            continue
                    out.append(ch)
                    i += 1
                    continue
                elem_ty = _guess_elem_type_extended(inner)
                if not elem_ty:
                    out.append(ch)
                    i += 1
                    continue
                # Only wrap at call-site / return / assignment-to-non-decl.
                # We require prev to be one of ``(``, ``,``, ``=`` (paren)
                # but skip ``= [` where ``let_inferred`` will already wrap.
                if prev in ("(", ",") or _ends_with_word(out, "return"):
                    # Recurse into the inner so that nested call-site
                    # literals (dicts inside arrays, arrays inside dicts) are
                    # wrapped too.  The "(" .. ")" padding keeps the prev-char
                    # context inside the recursive call coherent.
                    inner_rec = _wrap_call_site_array_literals(
                        "(" + inner + ")"
                    )[1:-1]
                    out.append(f"ArrayList<{elem_ty}>([{inner_rec}])")
                    i = j + 1
                    continue
                out.append(ch)
                i += 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def _ends_with_word(out: List[str], word: str) -> bool:
    """Return True iff the trailing tokens in *out* form ``…<word>\\s*``."""

    s = "".join(out[-(len(word) + 16):])
    s = s.rstrip()
    if not s.endswith(word):
        return False
    pre = s[:-len(word)]
    return pre == "" or not (pre[-1].isalnum() or pre[-1] == "_")


def _guess_elem_type_extended(inner: str) -> str:
    """Like :func:`_guess_elem_type` but also recognises homogeneous
    ``ClassName(...)`` constructor calls."""

    direct = _guess_elem_type(inner)
    if direct:
        return direct
    parts = _split_top_level(inner, ",")
    if not parts:
        return ""
    # Homogeneous nested array literals, e.g. ``[[1], [2, 3]]`` should infer
    # ``ArrayList<ArrayList<Int64>>`` after recursive wrapping.
    nested_elem = ""
    all_nested_arrays = True
    for p in parts:
        p = p.strip()
        if not (p.startswith("[") and p.endswith("]")):
            all_nested_arrays = False
            break
        nested_inner = p[1:-1].strip()
        if not nested_inner or not _is_pair_free(nested_inner):
            all_nested_arrays = False
            break
        sub_ty = _guess_elem_type_extended(nested_inner)
        if not sub_ty:
            all_nested_arrays = False
            break
        if nested_elem and nested_elem != sub_ty:
            return ""
        nested_elem = sub_ty
    if all_nested_arrays and nested_elem:
        return f"ArrayList<{nested_elem}>"
    ctor_name = ""
    for p in parts:
        p = p.strip()
        if not p:
            continue
        m_generic = re.match(r"^(ArrayList<[^<>]+>|HashSet<[^<>]+>|HashMap<[^<>]+>)\s*\(", p)
        if m_generic:
            nm = m_generic.group(1)
            if ctor_name and ctor_name != nm:
                return ""
            ctor_name = nm
            continue
        m = re.match(r"^([A-Z][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)?)\s*\(", p)
        if m:
            nm = m.group(1)
        else:
            # Allow bare ``Enum.case`` (no parens) as a valid member of the
            # same enum — useful for heterogeneous payloads (``.null`` etc).
            m2 = re.match(
                r"^([A-Z][A-Za-z_0-9]*)\.[A-Za-z_][A-Za-z_0-9]*\s*$", p
            )
            if not m2:
                return ""
            nm = m2.group(1)
        # For ``Enum.case(...)`` constructions, the *container* element type
        # is the enum itself, not the case label.
        if "." in nm:
            nm = nm.split(".", 1)[0]
        if ctor_name and ctor_name != nm:
            return ""
        ctor_name = nm
    return ctor_name


def _scan_enum_case_payloads(src: str) -> dict:
    """Like :func:`_scan_enum_cases` but additionally records each case's
    **translated** payload type list.

    Returns ``{ (EnumName, case_name): [payload_type_text, ...] }`` where each
    payload type has already been mapped through :func:`_convert_type_text`
    (so ``[Int]`` becomes ``ArrayList<Int64>`` etc).
    """

    out: dict = {}
    enum_re = re.compile(r"\benum\s+([A-Za-z_]\w*)(?:\s*:\s*[^{]+)?\s*\{")
    case_re = re.compile(r"\bcase\s+([A-Za-z_]\w*)(\s*\([^)]*\))?")
    pos = 0
    while True:
        m = enum_re.search(src, pos)
        if not m:
            break
        enum_name = m.group(1)
        brace_start = m.end() - 1
        depth = 1
        j = brace_start + 1
        n = len(src)
        while j < n and depth > 0:
            c = src[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        body = src[brace_start + 1:j - 1]
        for cm in case_re.finditer(body):
            cn = cm.group(1)
            params = cm.group(2) or ""
            inner = params.strip()
            payload_types: List[str] = []
            if inner.startswith("(") and inner.endswith(")"):
                inner_body = inner[1:-1].strip()
                if inner_body:
                    for p in _split_top_level(inner_body, ","):
                        p = p.strip()
                        # ``label: Type`` or just ``Type``.
                        if ":" in p:
                            p = p.split(":", 1)[1].strip()
                        payload_types.append(_convert_type_text(p))
            out[(enum_name, cn)] = payload_types
        pos = j
    return out


def _enum_case_similarity_match(
    case_payloads: dict, enum_name: str, case_text: str
) -> Optional[List[str]]:
    """Look up ``(enum_name, case_text)`` in *case_payloads*.

    On exact miss, fall back to an embedding-cosine nearest-match within the
    same enum: gives modest robustness to capitalisation drift / small
    misnamings, without resorting to brittle hand-coded aliases.  Returns the
    payload type list or ``None`` if no acceptable match exists.
    """

    if (enum_name, case_text) in case_payloads:
        return case_payloads[(enum_name, case_text)]
    candidates = [k for k in case_payloads if k[0] == enum_name]
    if not candidates:
        return None
    try:
        from .embedding import embed_token, cosine  # local import to keep cycle-free
        qv = embed_token(case_text)
        best, best_s = None, -1.0
        for k in candidates:
            s = cosine(qv, embed_token(k[1]))
            if s > best_s:
                best_s, best = s, k
        # Only accept very high similarity to avoid false collapses.
        if best is not None and best_s >= 0.95:
            return case_payloads[best]
    except Exception:
        return None
    return None


def _wrap_enum_case_empty_literals(src: str, case_payloads: dict) -> str:
    """For every recorded ``Enum.case(...)`` whose payload is a single
    container type (``ArrayList<…>`` or ``HashMap<…>``), rewrite the
    *empty* literal forms ``Enum.case([])`` and ``Enum.case([:])`` so the
    fallback constructs an explicitly-typed empty container.

    Cangjie has no context-free coercion from ``Array``/``[]`` to
    ``ArrayList``, so the call site must produce the concrete type itself.
    The lookup uses :func:`_enum_case_similarity_match` so out-of-vocabulary
    case spellings still resolve when they're embedding-close to a known one.
    """

    if not case_payloads:
        return src
    pat = re.compile(
        r"\b([A-Z][A-Za-z_0-9]*)\.([A-Za-z_]\w*)\s*\(\s*(\[\])\s*\)"
    )

    def _repl(m: "re.Match") -> str:
        enum_name = m.group(1)
        case_text = m.group(2)
        payloads = _enum_case_similarity_match(
            case_payloads, enum_name, case_text
        )
        if not payloads or len(payloads) != 1:
            return m.group(0)
        ty = payloads[0]
        if ty.startswith("ArrayList<") or ty.startswith("HashMap<") \
                or ty.startswith("HashSet<"):
            return f"{enum_name}.{case_text}({ty}())"
        return m.group(0)

    return _outside_strings_regex(src, pat.pattern, _repl)


def _scan_optional_names(src: str) -> set:
    """Return the set of identifier names declared with an Optional type
    (``Type?``) anywhere in *src*.  Includes ``let``/``var`` bindings,
    parameters and class/struct field declarations.

    Best-effort textual scan; the names are global (no scope tracking) but
    cross-name collisions are rare in practice and the downstream rewrite
    only kicks in for names actually present in the set.
    """

    names: set = set()
    # Variable / field declarations:  ``[let|var] NAME : TYPE?``
    decl_re = re.compile(
        r"\b(?:let|var)\s+([A-Za-z_]\w*)\s*:\s*[A-Za-z_][\w<>\[\], ]*\?"
    )
    for m in decl_re.finditer(src):
        names.add(m.group(1))
    # Function / init parameters:  ``NAME : TYPE?`` (catches both
    # external-label and positional forms thanks to permissive boundary).
    param_re = re.compile(
        r"(?:[(,]\s*(?:_\s+)?)([A-Za-z_]\w*)\s*:\s*[A-Za-z_][\w<>\[\], ]*\?"
    )
    for m in param_re.finditer(src):
        names.add(m.group(1))
    # Initialiser-with-nil:  ``var NAME = nil`` / ``let NAME = nil``.
    for m in re.finditer(
        r"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*nil\b", src
    ):
        names.add(m.group(1))
    # Propagate: ``var/let NAME = <already-optional-NAME>`` carries Optional
    # through.  Iterate to a fixed point to chain ``a = b; c = a`` etc.
    rhs_re = re.compile(
        r"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\b"
    )
    # Functions returning ``T?`` — their call sites yield Optional bindings.
    opt_func_re = re.compile(
        r"\bfunc\s+([A-Za-z_]\w*)\s*\([^)]*\)\s*->\s*[A-Za-z_][\w<>\[\], ]*\?"
    )
    opt_funcs: set = set(m.group(1) for m in opt_func_re.finditer(src))
    call_rhs_re = re.compile(
        r"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*\("
    )
    if opt_funcs:
        for m in call_rhs_re.finditer(src):
            if m.group(2) in opt_funcs:
                names.add(m.group(1))
    # Swift dictionary subscript reads produce Optional values.  Track
    # temporaries such as ``let j = jobs[name]`` (or after the rewrite above,
    # ``let j = jobs.get(name)``) so later ``if let jj = j`` compiles as an
    # Optional binding.
    dict_names = _scan_dict_names(src)
    if dict_names:
        dict_alt = "|".join(sorted(re.escape(n) for n in dict_names))
        for m in re.finditer(
            rf"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:{dict_alt})\[[^\[\]]+\]",
            src,
        ):
            names.add(m.group(1))
        for m in re.finditer(
            rf"\b(?:let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:{dict_alt})\.get\(",
            src,
        ):
            names.add(m.group(1))
    changed = True
    while changed:
        changed = False
        for m in rhs_re.finditer(src):
            if m.group(2) in names and m.group(1) not in names:
                names.add(m.group(1))
                changed = True
    return names


def _scan_enum_cases(src: str) -> dict:
    """Scan *src* for ``enum Name { case a; case b(...); … }`` declarations
    and return a mapping ``case_name → (enum_name, arity)`` for every case
    that appears in **exactly one** enum.  Ambiguous case names (defined by
    multiple enums) map to ``("", 0)`` so the caller can leave them alone.
    """

    cases: dict = {}
    ambig: set = set()

    enum_re = re.compile(r"\benum\s+([A-Za-z_]\w*)(?:\s*:\s*[^{]+)?\s*\{")
    case_re = re.compile(r"\bcase\s+([A-Za-z_]\w*)(\s*\([^)]*\))?")
    pos = 0
    while True:
        m = enum_re.search(src, pos)
        if not m:
            break
        enum_name = m.group(1)
        brace_start = m.end() - 1
        depth = 1
        j = brace_start + 1
        n = len(src)
        while j < n and depth > 0:
            c = src[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        body = src[brace_start + 1:j - 1]
        for cm in case_re.finditer(body):
            cn = cm.group(1)
            params = cm.group(2) or ""
            arity = 0
            inner = params.strip()
            if inner.startswith("(") and inner.endswith(")"):
                inner_body = inner[1:-1].strip()
                if inner_body:
                    arity = len(_split_top_level(inner_body, ","))
            existing = cases.get(cn)
            if existing and existing[0] != enum_name:
                ambig.add(cn)
            else:
                cases[cn] = (enum_name, arity)
        pos = j
    for a in ambig:
        cases[a] = ("", 0)
    return cases


def _scan_parent_class_names(src: str) -> set:
    """Return Swift class names that appear as a superclass.

    The converter templates historically emitted every class and method as
    ``open``.  A simple non-local scan lets leaf classes use Cangjie's default
    internal visibility while preserving ``open`` only for classes that need to
    support subclass overriding.
    """

    parents: set = set()
    class_re = re.compile(
        r"\bclass\s+[A-Za-z_]\w*(?:\s*<[^>{}]*>)?\s*:\s*([A-Za-z_]\w*)"
    )
    for m in class_re.finditer(src):
        parents.add(m.group(1))
    return parents


_LEADING_ENUM_DOT_RE = re.compile(r"(?<![A-Za-z0-9_)\]!\?.])\.([A-Za-z_]\w*)")


def _strip_leading_enum_dot(src: str) -> str:
    """Strip Swift leading-dot enum shorthand outside string/comment regions.

    When a global ``case_name → enum_name`` map is available (built upstream
    by :func:`_scan_enum_cases`) and the name is *unambiguous*, the leading
    dot is replaced with ``EnumName.`` so the resulting Cangjie reference is
    fully qualified (Cangjie has no leading-dot shorthand).
    """

    case_map = _scan_enum_cases(src)

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(src[i:end])
                i = end
                continue
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            out.append(src[i:end])
            i = end
            continue
        out.append(ch)
        i += 1
    text = "".join(out)

    def _repl(m: "re.Match") -> str:
        name = m.group(1)
        v = case_map.get(name, None)
        if v is None:
            return name
        enum_n, _ = v
        if enum_n:
            return f"{enum_n}.{name}"
        return name

    return _LEADING_ENUM_DOT_RE.sub(_repl, text)


_PRIMITIVE_MAP = {
    "Int": "Int64",
    "Int64": "Int64",
    "Int32": "Int32",
    "Int16": "Int16",
    "Int8": "Int8",
    "UInt": "UInt64",
    "UInt64": "UInt64",
    "UInt32": "UInt32",
    "Double": "Float64",
    "Float": "Float32",
    "Float64": "Float64",
    "Bool": "Bool",
    "String": "String",
    "Character": "Rune",
    "Void": "Unit",
    "Any": "Any",
}
_PRIMITIVE_TYPE_RE = re.compile(
    r"\b(Int8|Int16|Int32|Int64|Int|UInt32|UInt64|UInt|Float32|Float64|Float|Double|Bool|String|Character|Void)\b"
)


def _apply_primitive_types(text: str) -> str:
    """Translate Swift primitive type names → Cangjie."""

    return _PRIMITIVE_TYPE_RE.sub(lambda m: _PRIMITIVE_MAP[m.group(1)], text)


# --------------------------------------------------------------------------- #
#  Statement boundary synthesis                                               #
# --------------------------------------------------------------------------- #
#
# Swift uses *newlines* as primary statement terminators rather than ``;``.
# Our chunker expects semicolon-terminated chunks (like the ts2cj baseline),
# so we synthesise a top-level ``;`` token at every newline that lies
# **outside** any brace / paren / bracket group **and** which doesn't
# immediately precede a token that should continue the previous statement
# (``else``, ``catch``, ``while`` of a ``repeat-while``, ``{``, ``.``).
def _insert_semicolons(tokens: List[Token]) -> List[Token]:
    """Walk *tokens* and insert ``;`` tokens at top-level statement breaks."""

    out: List[Token] = []
    depth_b = depth_p = depth_s = 0
    n = len(tokens)
    i = 0
    last_meaningful: Optional[Token] = None

    # tokens that, when starting the *next* line, mean the previous line
    # continues (no ``;`` should be inserted).
    cont_starts = {".", ",", ")", "]", "}", "else", "catch", "where",
                   "?", ":", "&&", "||", "==", "!=", "<", ">", "<=", ">=",
                   "+", "-", "*", "/", "%", "=", "+=", "-=", "*=", "/=",
                   "->", "..<", "...", "??"}
    # tokens that should NEVER receive a synthesised ``;`` after them
    # because they themselves expect a continuation.
    no_semi_after = {"{", "(", "[", ",", ";", ".", "?", ":", "&&", "||",
                     "==", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/",
                     "%", "=", "+=", "-=", "*=", "/=", "->", "..<", "...",
                     "??", "else", "case", "default", "where", "throw",
                     "return", "in", "do", "try", "if", "while", "for",
                     "switch", "repeat", "guard"}

    for tok in tokens:
        if tok.kind == "NEWLINE":
            # Decide whether to flush a ``;`` at this newline.
            if (
                depth_p == 0 and depth_s == 0
                and last_meaningful is not None
                and last_meaningful.value not in no_semi_after
                and last_meaningful.kind not in ("COMMENT_BLOCK", "COMMENT_LINE")
            ):
                # peek ahead for the next meaningful token (skip newlines/comments).
                pass  # handled below by scanning the *out* stream
                out.append(Token("PUNCT", ";", tok.line, tok.col))
                last_meaningful = out[-1]
            continue
        if tok.kind in ("COMMENT_BLOCK", "COMMENT_LINE"):
            continue
        if tok.value == "{":
            depth_b += 1
        elif tok.value == "}":
            depth_b = max(depth_b - 1, 0)
        elif tok.value == "(":
            depth_p += 1
        elif tok.value == ")":
            depth_p = max(depth_p - 1, 0)
        elif tok.value == "[":
            depth_s += 1
        elif tok.value == "]":
            depth_s = max(depth_s - 1, 0)
        out.append(tok)
        last_meaningful = tok
        i += 1

    # Second pass: remove inserted ``;`` that ended up adjacent to a
    # continuation start token (e.g. ``...\n.foo()`` or ``...\nelse {``).
    cleaned: List[Token] = []
    j = 0
    m = len(out)
    while j < m:
        t = out[j]
        if t.kind == "PUNCT" and t.value == ";":
            # Look at next meaningful token.
            k = j + 1
            while k < m and out[k].kind in ("COMMENT_BLOCK", "COMMENT_LINE"):
                k += 1
            if k < m:
                nxt = out[k]
                if nxt.value in cont_starts:
                    j += 1
                    continue
            # collapse multiple ``;`` in a row
            if cleaned and cleaned[-1].kind == "PUNCT" and cleaned[-1].value == ";":
                j += 1
                continue
        cleaned.append(t)
        j += 1
    return cleaned


# --------------------------------------------------------------------------- #
#  Chunk segmentation                                                         #
# --------------------------------------------------------------------------- #
def _segment_chunks(tokens: List[Token]) -> List[List[Token]]:
    """Split a token stream into balanced top-level chunks.

    A chunk ends at a top-level ``;`` or at a top-level ``}`` that closes a
    previously opened ``{`` — **unless** the next meaningful token is one of
    ``else`` / ``catch`` / ``while`` (``repeat-while`` trailer), in which
    case the chunk continues.
    """

    toks = [t for t in tokens if t.kind not in ("NEWLINE", "COMMENT_BLOCK", "COMMENT_LINE")]
    chunks: List[List[Token]] = []
    cur: List[Token] = []
    depth_b = depth_p = depth_s = 0

    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        cur.append(t)
        if t.kind == "PUNCT":
            if t.value == "{":
                depth_b += 1
            elif t.value == "}":
                depth_b = max(depth_b - 1, 0)
                if depth_b == 0 and depth_p == 0 and depth_s == 0:
                    nxt = toks[i + 1] if i + 1 < n else None
                    if nxt is not None and nxt.kind == "KEYWORD" and nxt.value in (
                        "else", "catch", "while",
                    ):
                        i += 1
                        continue
                    chunks.append(cur)
                    cur = []
            elif t.value == "(":
                depth_p += 1
            elif t.value == ")":
                depth_p = max(depth_p - 1, 0)
            elif t.value == "[":
                depth_s += 1
            elif t.value == "]":
                depth_s = max(depth_s - 1, 0)
            elif t.value == ";" and depth_b == 0 and depth_p == 0 and depth_s == 0:
                # drop the ``;`` itself (we synthesised it as a separator).
                cur.pop()
                if cur:
                    chunks.append(cur)
                cur = []
        i += 1
    if cur:
        chunks.append(cur)
    return chunks


# --------------------------------------------------------------------------- #
#  Slot binding                                                               #
# --------------------------------------------------------------------------- #
def _bind_slots(
    chunk: List[Token],
    pat_tokens: List[Tuple[str, str]],
) -> Optional[Tuple[dict, float]]:
    """Try to bind *chunk* to a pattern template.

    Each ``LIT`` event must match ``chunk[i]`` exactly.  Each ``SLOT`` event
    collects a brace/paren/bracket-balanced token span up to the next ``LIT``
    anchor (or the end of the chunk).  A slot mentioned multiple times must
    bind to the same token sequence each time.
    """

    events = pat_tokens
    if not events:
        return None

    bindings: dict = {}
    i = 0
    total_anchors = sum(1 for k, _ in events if k == "LIT")
    matched_anchors = 0

    e = 0
    while e < len(events):
        kind, val = events[e]
        if kind == "LIT":
            if i >= len(chunk) or chunk[i].value != val:
                return None
            i += 1
            matched_anchors += 1
            e += 1
            continue
        nxt = None
        for k in range(e + 1, len(events)):
            if events[k][0] == "LIT":
                nxt = events[k][1]
                break
        slot_tokens: List[Token] = []
        if nxt is None:
            slot_tokens = chunk[i:]
            i = len(chunk)
        else:
            depth_b = depth_p = depth_s = 0
            j = i
            while j < len(chunk):
                tv = chunk[j].value
                if tv == nxt and depth_b == 0 and depth_p == 0 and depth_s == 0:
                    break
                if tv == "{":
                    depth_b += 1
                elif tv == "}":
                    depth_b -= 1
                elif tv == "(":
                    depth_p += 1
                elif tv == ")":
                    depth_p -= 1
                elif tv == "[":
                    depth_s += 1
                elif tv == "]":
                    depth_s -= 1
                slot_tokens.append(chunk[j])
                j += 1
            if j >= len(chunk):
                return None
            i = j
        if val in bindings:
            prev = bindings[val]
            if len(prev) != len(slot_tokens) or any(
                a.value != b.value for a, b in zip(prev, slot_tokens)
            ):
                return None
        else:
            bindings[val] = slot_tokens
        e += 1

    if i != len(chunk):
        return None

    score = (matched_anchors / total_anchors) if total_anchors else 1.0
    return bindings, score


# --------------------------------------------------------------------------- #
#  Rendering helpers                                                          #
# --------------------------------------------------------------------------- #
def _is_word(s: str) -> bool:
    return bool(s) and (s[0].isalnum() or s[0] == "_")


def _render_tokens(tokens: List[Token]) -> str:
    """Render a token list back to surface source with reasonable spacing."""

    binary_ops = {"+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                  "&&", "||", "??", "&", "|", "^", "<<", ">>", "**",
                  "+=", "-=", "*=", "/=", "%=", "=", "=>", "->"}
    # Tokens that, when they directly precede a ``-``/``+``/``!``, indicate
    # that the operator is **unary** (not binary).  In that case we render
    # without a leading space and without a separating space after.
    unary_prev_values = {
        "(", "[", "{", ",", ";", ":", "?",
        "=", "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
        "&&", "||", "??", "->", "=>", "+=", "-=", "*=", "/=", "%=",
        "return", "throw", "if", "while", "else", "case", "in",
    }
    out: List[str] = []
    for i, t in enumerate(tokens):
        if i > 0:
            prev = tokens[i - 1]
            # Detect unary ``-`` / ``+`` / ``!`` after a value/operator boundary.
            is_unary = (
                t.value in ("-", "+", "!")
                and (prev.value in unary_prev_values or prev.kind == "KEYWORD")
            )
            # Following token can be glued if the previous one was a unary op.
            prev_is_unary = (
                prev.value in ("-", "+", "!")
                and i >= 2
                and (
                    tokens[i - 2].value in unary_prev_values
                    or tokens[i - 2].kind == "KEYWORD"
                )
            )
            need_space = False
            if _is_word(prev.value) and _is_word(t.value):
                need_space = True
            elif prev.value == "," and t.value not in (")", "]", "}"):
                need_space = True
            elif t.value in binary_ops and not is_unary:
                need_space = True
            elif prev.value in binary_ops and not prev_is_unary:
                need_space = True
            elif prev.value == ":":
                need_space = True
            if is_unary or prev_is_unary:
                need_space = False
            if need_space:
                out.append(" ")
        out.append(t.value)
    return "".join(out)


def _strip_trailing_semicolon(tokens: List[Token]) -> List[Token]:
    if tokens and tokens[-1].kind == "PUNCT" and tokens[-1].value == ";":
        return tokens[:-1]
    return tokens


_PRIMITIVE_DEFAULTS = {
    "Int64": "0", "Int32": "0", "Int16": "0", "Int8": "0",
    "UInt64": "0", "UInt32": "0", "UInt16": "0", "UInt8": "0",
    "Float64": "0.0", "Float32": "0.0",
    "Bool": "false", "String": "\"\"", "Rune": "r' '",
}


def _scalar_default(ty: str) -> Optional[str]:
    ty = ty.strip()
    if ty.startswith("?"):
        return "None"
    return _PRIMITIVE_DEFAULTS.get(ty)


def _default_value_for(ty: str) -> str:
    """Pick a Cangjie default-value literal for ``ty``.

    For unknown / generic types returns the type name itself + ``()`` as a
    best-effort fallback; callers should generally prefer
    :func:`_scalar_default` and fall through to leaving the field
    uninitialised (which then forces the synthetic memberwise constructor
    to set it).
    """

    ty = ty.strip()
    s = _scalar_default(ty)
    if s is not None:
        return s
    if ty.startswith("ArrayList<") or ty.startswith("Array<"):
        return ty + "()"
    if ty.startswith("HashMap<") or ty.startswith("HashSet<"):
        return ty + "()"
    if ty.startswith("("):
        inner = ty[1:-1]
        parts = [_default_value_for(p.strip()) for p in _split_top_level(inner, ",")]
        return "(" + ", ".join(parts) + ")"
    return ty + "()"


def _split_top_level(s: str, sep: str) -> List[str]:
    out: List[str] = []
    depth = 0
    buf: List[str] = []
    for ch in s:
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth = max(depth - 1, 0)
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


# --------------------------------------------------------------------------- #
#  Body recursion                                                             #
# --------------------------------------------------------------------------- #
def _convert_body(tokens: List[Token], indent: int = 1, ctx: Optional[str] = None) -> str:
    inner_chunks = _segment_chunks(tokens)
    pieces: List[str] = []
    pad = "    " * indent
    for ch in inner_chunks:
        if not ch:
            continue
        line = _convert_chunk(ch, ctx=ctx)
        if line is None:
            line = "/* swift2cj: unrecognised */ // " + _render_tokens(ch)
        line = _adjust_for_context(line, ctx)
        for ln in line.split("\n"):
            pieces.append(pad + ln if ln else ln)
    return "\n".join(pieces)


def _adjust_for_context(line: str, ctx: Optional[str]) -> str:
    if ctx == "iface":
        line = line.replace("public open func ", "func ")
        line = line.replace("public static func ", "static func ")
    elif ctx == "struct":
        line = line.replace("public open func ", "public func ")
    return line


# --------------------------------------------------------------------------- #
#  Chunk → Cangjie                                                            #
# --------------------------------------------------------------------------- #
def _convert_if_chain(chunk: List[Token]) -> Optional[str]:
    """Convert a Swift ``if … else if … else …`` chain of any depth.

    Returns ``None`` if the chunk doesn't look like an if-chain, letting
    the caller fall back to pattern retrieval (e.g. for ``if let``
    guards which need different handling).
    """

    n = len(chunk)
    i = 0
    arms: List[Tuple[Optional[List[Token]], List[Token]]] = []
    # tuple (condition_tokens_or_None_for_else, body_tokens)

    def find_matching_brace(start: int) -> int:
        # ``chunk[start]`` must be ``{``.  Return index of matching ``}``.
        depth = 0
        j = start
        while j < n:
            v = chunk[j].value
            if v == "{":
                depth += 1
            elif v == "}":
                depth -= 1
                if depth == 0:
                    return j
            j += 1
        return -1

    while i < n:
        t = chunk[i]
        if t.kind == "KEYWORD" and t.value == "if":
            # Collect condition tokens up to next top-level ``{``.
            i += 1
            cond: List[Token] = []
            depth_p = depth_s = 0
            while i < n:
                v = chunk[i].value
                if v == "{" and depth_p == 0 and depth_s == 0:
                    break
                if v == "(":
                    depth_p += 1
                elif v == ")":
                    depth_p -= 1
                elif v == "[":
                    depth_s += 1
                elif v == "]":
                    depth_s -= 1
                cond.append(chunk[i])
                i += 1
            if i >= n or chunk[i].value != "{":
                return None
            brace_end = find_matching_brace(i)
            if brace_end == -1:
                return None
            body = chunk[i + 1:brace_end]
            arms.append((cond, body))
            i = brace_end + 1
            # Look for ``else`` or end.
            if i < n and chunk[i].value == "else":
                i += 1
                if i < n and chunk[i].value == "if":
                    continue  # next iteration handles ``if`` arm
                if i < n and chunk[i].value == "{":
                    brace_end = find_matching_brace(i)
                    if brace_end == -1:
                        return None
                    body = chunk[i + 1:brace_end]
                    arms.append((None, body))
                    i = brace_end + 1
                    continue
                return None
            continue
        # unexpected trailing tokens
        return None

    if not arms:
        return None

    # Emit Cangjie source.
    parts: List[str] = []
    for idx, (cond, body) in enumerate(arms):
        body_text = _convert_body(body, indent=1)
        if cond is None:  # else arm
            parts.append("else {\n" + body_text + "\n}")
        else:
            cond_text = _convert_expr(cond)
            kw = "if" if idx == 0 else "else if"
            parts.append(f"{kw} ({cond_text}) " + "{\n" + body_text + "\n}")
    return " ".join(parts)


def _convert_chunk(chunk: List[Token], ctx: Optional[str] = None) -> Optional[str]:
    if not chunk:
        return ""
    engine = _Engine.get()

    # ------- structural pre-pass: if / else-if / else chain ------- #
    # Handle arbitrary-depth ``if ... { ... } else if ... { ... } ... else
    # { ... }`` chains directly — built-in patterns only cover two and
    # three-arm forms.
    if chunk and chunk[0].kind == "KEYWORD" and chunk[0].value == "if":
        chain = _convert_if_chain(chunk)
        if chain is not None:
            return chain

    chunk_emb = embed_sequence(chunk)
    som_candidates = {i for i, _ in engine.som.query(chunk_emb, k=8)}

    # Context-driven pattern gating.  In an interface/protocol body we want
    # the ``proto_method_*`` patterns to win over ``expr_stmt``; inside a
    # class / struct body we want the ``method_*`` / ``init_*`` patterns
    # rather than the top-level ``function_*`` ones (and vice versa at the
    # top level).  Sets enumerated explicitly for clarity.
    method_pats = {
        "method_typed", "method_throws_typed", "method_no_ret",
        "method_throws_no_ret", "method_generic_typed",
        "static_method_typed", "static_method_no_ret",
        "private_method_typed", "private_method_no_ret",
        "override_method_typed", "override_method_no_ret",
        "init_decl", "init_throws_decl",
        "override_init_decl", "convenience_init_decl",
        "field_var_typed_with_init", "field_let_typed_with_init",
        "field_var_typed", "field_let_typed",
        "proto_method_typed", "proto_method_no_ret",
    }
    function_pats = {
        "function_typed", "function_throws_typed", "function_no_ret",
        "function_throws_no_ret",
        "function_generic_typed", "function_generic_no_ret",
    }
    proto_pats = {"proto_method_typed", "proto_method_no_ret"}

    best: Optional[Tuple[Pattern, dict, float]] = None
    for idx in range(len(engine.patterns)):
        pat = engine.patterns[idx]
        # Apply context filtering.
        if ctx in ("class", "struct"):
            if pat.name in function_pats:
                continue
        elif ctx == "iface":
            # In a protocol body, only signature-only proto patterns plus
            # a few generic catch-alls make sense; suppress full-body ones.
            if pat.name in function_pats:
                continue
            if pat.name in ("method_typed", "method_throws_typed",
                            "method_no_ret", "method_throws_no_ret"):
                # Allow as default-method, but proto_method_* should win on
                # signature-only chunks via the anchor count.
                pass
        else:  # top-level
            if pat.name in method_pats:
                continue
            # proto_method_* patterns are no-body and very catchy; suppress.
            if pat.name in proto_pats:
                continue

        pat_tokens = engine.pattern_token_lists[idx]
        result = _bind_slots(chunk, pat_tokens)
        if result is None:
            continue
        bindings, anchor_score = result
        if "NAME" in bindings:
            first = bindings["NAME"][0] if bindings["NAME"] else None
            if first is not None and first.kind == "KEYWORD" and first.value in (
                "for", "while", "if", "else", "do", "switch", "case", "default",
                "return", "throw", "try", "catch", "repeat", "guard", "break",
                "continue", "let", "var", "func", "class", "struct", "enum",
                "protocol", "extension", "init", "import", "typealias",
            ):
                continue
        n_anchors = sum(1 for k, _ in pat_tokens if k == "LIT")
        sim = cosine(chunk_emb, engine.pattern_embeddings[idx])
        som_bonus = 0.1 if idx in som_candidates else 0.0
        composite = anchor_score * (1.0 + n_anchors) + 0.1 * sim + som_bonus
        if best is None or composite > best[2]:
            best = (pat, bindings, composite)

    if best is None:
        return None
    pat, bindings, _score = best
    return _emit(pat, bindings, ctx=ctx)


def _is_body_slot(slot: str) -> bool:
    if slot in ("BODY", "A", "CBODY", "FBODY"):
        return True
    if slot == "B" or (slot.startswith("B") and slot[1:].isdigit()):
        return True
    if slot == "C" or (slot.startswith("C") and slot[1:].isdigit()):
        # C1/C2 are *conditions* — expressions, not bodies.
        return False
    return False


_TYPE_ALIASES: dict = {}
_CLASS_METHODS: dict = {}
_ENUM_CASE_INFO: dict = {}
_CLASS_PARENT: dict = {}
_PARENT_CLASS_NAMES: set = set()
_OVERLOADABLE_OPS = {
    "+", "-", "*", "/", "%", "**",
    "==", "!=", "<", ">", "<=", ">=",
    "&", "|", "^", "<<", ">>",
}


def _hoist_super_call(text: str) -> str:
    """Move the ``super(...)`` line in an ``init`` body to the top.

    Cangjie requires ``super(...)`` to be the first statement of an
    initialiser; Swift permits (and in fact requires for subclass-field
    initialisation) the reverse.  We locate the body block and lift any
    ``super(...)`` statement to immediately follow the opening ``{``.
    """

    head_m = re.search(r"public\s+init\s*\([^)]*\)\s*\{\n", text)
    if not head_m:
        return text
    body_start = head_m.end()
    # Walk forward to the matching ``}``.
    depth = 1
    i = body_start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        return text
    body = text[body_start:i]
    lines = body.split("\n")
    super_idx = -1
    for k, ln in enumerate(lines):
        if re.match(r"\s*super\s*\(", ln):
            super_idx = k
            break
    if super_idx <= 0:
        return text
    super_line = lines.pop(super_idx)
    lines.insert(0, super_line)
    new_body = "\n".join(lines)
    return text[:body_start] + new_body + text[i:]


def _rewrite_static_operator(text: str) -> str:
    """Rewrite a ``public static func OP(a: T, b: T): R { ... }`` block
    emitted by the ``static_method_*`` patterns into an idiomatic Cangjie
    operator overload ``public operator func OP(b: T): R { ... }`` where the
    first parameter's identifier is replaced by ``this`` throughout the body.

    Cangjie operator overloads use positional parameters (the operator is
    dispatched on the LHS receiver), so we also strip any ``!`` named-arg
    markers our default param renderer may have inserted.
    """

    m = re.match(
        r"^(\s*)public static func "
        r"(\S+?)\s*\(\s*([A-Za-z_]\w*)\s*!?\s*:\s*([^,)]+?)\s*,\s*"
        r"([A-Za-z_]\w*)\s*!?\s*:\s*([^,)]+?)\s*\)\s*(?::\s*([^\{]+?))?\{\s*\n",
        text,
        flags=re.DOTALL,
    )
    if not m:
        return text
    indent, op, a_name, _a_ty, b_name, b_ty, ret = m.groups()
    header_end = m.end()
    # Find matching ``}`` for the body.
    depth = 1
    i = header_end
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        return text
    body = text[header_end:i]
    body = re.sub(rf"\b{re.escape(a_name)}\b", "this", body)
    ret_clause = f": {ret.strip()} " if ret else ""
    new = (
        f"{indent}public operator func {op}({b_name}: {b_ty.strip()}){ret_clause}"
        + "{\n" + body + "}"
    )
    return text[:m.start()] + new + text[i + 1:]


def _emit(pat: Pattern, bindings: dict, ctx: Optional[str] = None) -> str:
    out = pat.cj_template

    if pat.name == "switch_block":
        expr = _convert_expr(bindings.get("EXPR", []))
        body = _convert_switch_body(bindings.get("BODY", []))
        return out.replace("$EXPR", expr).replace("$SWBODY", body)

    if pat.name in ("enum_decl", "enum_raw_decl"):
        name = _convert_expr(bindings.get("NAME", [])).strip()
        body = _convert_enum_body(bindings.get("BODY", []))
        # When every variant is a *bare* name (no payload tuple), Swift's
        # enum auto-synthesises ``==`` — Cangjie's does not.  Append a small
        # ``Equatable`` impl so callers can use ``e == .case`` directly,
        # mirroring Swift semantics.  The match exhausts the variants pairwise.
        variant_names: List[str] = []
        bare = True
        for ln in body.split("\n"):
            ln = ln.strip()
            if not ln.startswith("|"):
                continue
            v = ln[1:].strip()
            if "(" in v:
                bare = False
                break
            if v:
                variant_names.append(v)
        if bare and len(variant_names) >= 1:
            cmp_arms = "\n".join(
                f"            case ({v}, {v}) => true" for v in variant_names
            )
            eq_impl = (
                f"    public operator func ==(other: {name}): Bool {{\n"
                f"        match ((this, other)) {{\n"
                f"{cmp_arms}\n"
                f"            case _ => false\n"
                f"        }}\n"
                f"    }}\n"
                f"    public operator func !=(other: {name}): Bool {{ !(this == other) }}"
            )
            decl = f"enum {name} <: Equatable<{name}> {{\n{body}\n{eq_impl}\n}}"
            return decl
        return out.replace("$NAME", name).replace("$ENUMBODY", body)

    if pat.name == "import_decl":
        # Drop imports entirely (Cangjie has its own module system; we inject
        # std.collection later if needed).
        return ""

    if "$DEFAULT" in out and "TY" in bindings:
        # Field declarations of type ``var x: T`` (no user default) get no
        # declaration-site initialiser.  The synthesised memberwise
        # constructor — produced by :func:`_ensure_memberwise_init` — is
        # responsible for assigning every such field.  This matches Swift
        # semantics: a stored property with no default value must be set
        # before the instance is used, and Swift's implicit memberwise
        # ``init`` is what does so.
        out = out.replace(" = $DEFAULT", "")

    iface_like = pat.name in ("protocol_decl", "protocol_decl_inherit")
    struct_like = pat.name in ("struct_decl", "struct_impl_decl")
    class_like = pat.name in (
        "class_decl", "class_decl_inherit", "class_generic_decl",
        "class_generic_decl_inherit", "extension_decl",
        "final_class_decl", "final_class_decl_inherit", "public_class_decl",
    )
    if iface_like:
        sub_ctx = "iface"
    elif struct_like:
        sub_ctx = "struct"
    elif class_like:
        sub_ctx = "class"
    else:
        sub_ctx = None

    # In a protocol body, method-without-body chunks are emitted using the
    # ``proto_method_*`` patterns — but the slot binder needs help: those
    # patterns will be retried with ctx propagation below.
    for slot in pat.slots:
        if slot not in bindings:
            continue
        tokens = bindings[slot]
        if _is_body_slot(slot):
            body_text = _convert_body(tokens, indent=1, ctx=sub_ctx)
            out = out.replace(f"${slot}", body_text)
        elif slot == "PARAMS":
            out = out.replace(f"${slot}", _convert_params(tokens))
        elif slot == "RET" or slot == "TY":
            out = out.replace(f"${slot}", _convert_type(tokens))
        elif slot == "BASE":
            # Multi-protocol inheritance: ``: Named, Priced`` (Swift) becomes
            # ``<: Named & Priced`` in Cangjie.  We render every comma-
            # separated piece individually.
            text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
            parts = [_convert_type_text(p.strip()) for p in _split_top_level(text, ",")]
            out = out.replace(f"${slot}", " & ".join(parts))
        elif slot == "TPARAMS":
            out = out.replace(f"${slot}", _convert_type_params(tokens))
        else:
            out = out.replace(f"${slot}", _convert_expr(tokens))

    # Override / inheritance bookkeeping.
    if pat.name in ("class_decl_inherit", "class_generic_decl_inherit",
                    "final_class_decl_inherit"):
        name = _convert_expr(bindings.get("NAME", [])).strip()
        base_text = _convert_type(bindings.get("BASE", [])).strip() if "BASE" in bindings else ""
        base = re.sub(r"<.*$", "", base_text).strip()
        my_methods = _scan_method_names(bindings.get("BODY", []))
        _CLASS_METHODS[name] = my_methods
        _CLASS_PARENT[name] = base
        parent_methods: set = set()
        cur = base
        seen: set = set()
        while cur and cur not in seen:
            seen.add(cur)
            parent_methods |= _CLASS_METHODS.get(cur, set())
            cur = _CLASS_PARENT.get(cur, "")

        def _mark(m: re.Match) -> str:
            n = m.group(1)
            if n in parent_methods:
                # Re-mark as ``open override`` so further subclasses may
                # override this method as well — Cangjie's ``override``
                # alone does NOT keep the method open for additional
                # overrides.
                return f"public open override func {n}"
            return f"public open func {n}"

        out = re.sub(r"public open func (\w+)", _mark, out)
    elif pat.name in ("class_decl", "class_generic_decl"):
        name = _convert_expr(bindings.get("NAME", [])).strip()
        _CLASS_METHODS[name] = _scan_method_names(bindings.get("BODY", []))
        if name not in _PARENT_CLASS_NAMES:
            out = re.sub(r"\bopen class\b", "class", out, count=1)
            out = re.sub(r"\bpublic open func\b", "func", out)
            out = re.sub(r"\bpublic init\b", "init", out)

    # In a ``final`` class, member methods must NOT carry the ``open``
    # modifier (Cangjie warns and refuses subsequent overrides).  Strip
    # ``open`` while preserving ``override`` where present.
    if pat.name in ("final_class_decl", "final_class_decl_inherit"):
        out = re.sub(r"\bpublic open override func\b", "public override func", out)
        out = re.sub(r"\bpublic open func\b", "public func", out)

    # In an ``extend`` body Cangjie forbids the ``open`` / ``override``
    # modifiers — we have to drop them.
    if pat.name == "extension_decl":
        out = re.sub(r"\bpublic open (?:override )?func\b", "public func", out)
        out = re.sub(r"\bopen (?:override )?func\b", "func", out)

    if pat.name == "typealias_decl" and "NAME" in bindings and "TY" in bindings:
        name = _convert_expr(bindings["NAME"]).strip()
        ty = _convert_type(bindings["TY"]).strip()
        _TYPE_ALIASES[name] = ty

    # Auto-synthesize a memberwise initialiser for structs / classes that
    # declare fields but no explicit ``init``.  Swift gives structs an
    # implicit memberwise init; Cangjie does not.
    if pat.name in ("struct_decl", "struct_impl_decl", "class_decl",
                    "class_decl_inherit", "class_generic_decl",
                    "class_generic_decl_inherit", "final_class_decl",
                    "final_class_decl_inherit", "public_class_decl"):
        out = _ensure_memberwise_init(out)

    # Operator overload: Swift writes binary operators as ``static func +``
    # taking two operands, but Cangjie's operator overloads are *instance*
    # methods on the left operand.  Rewrite by dropping the first param and
    # renaming it to ``this`` throughout the body.
    if pat.name in ("static_method_typed", "static_method_no_ret"):
        name_toks = bindings.get("NAME", [])
        if (
            len(name_toks) == 1
            and name_toks[0].kind == "PUNCT"
            and name_toks[0].value in _OVERLOADABLE_OPS
        ):
            out = _rewrite_static_operator(out)

    # Cangjie requires ``super(...)`` to be the first statement in an
    # initialiser; Swift requires the opposite (subclass fields first).
    # When emitting an ``init`` body we lift any ``super(...)`` call to the
    # top so the result type-checks.
    if pat.name in ("init_decl", "init_no_params", "public_init_decl"):
        out = _hoist_super_call(out)


    # Post-substitution: wrap bare collection literals to match a typed
    # collection annotation:
    #   ``let xs: ArrayList<Int64> = [1,2,3]``  →
    #   ``let xs: ArrayList<Int64> = ArrayList<Int64>([1,2,3])``
    # Cangjie 1.x has no implicit conversion from ``Array`` literals.
    if pat.name in (
        "let_typed_init", "var_typed_init",
        "field_var_typed_with_init", "field_let_typed_with_init",
    ) and "TY" in bindings:
        ty_text = _convert_type(bindings["TY"]).strip()
        if ty_text.startswith(("ArrayList<", "HashSet<", "HashMap<")):
            m = re.search(r"=\s*\[(.*)\]\s*$", out, flags=re.DOTALL)
            if m:
                inner = m.group(1).strip()
                if not inner:
                    # Empty literal — use the zero-arg constructor directly.
                    out = out[:m.start()] + f"= {ty_text}()" + out[m.end():]
                elif ty_text.startswith("HashMap<"):
                    # Swift dict literal ``[k1: v1, k2: v2]`` → list of pairs.
                    pairs = []
                    for kv in _split_top_level(inner, ","):
                        kv = kv.strip()
                        if not kv:
                            continue
                        parts = _split_top_level(kv, ":")
                        if len(parts) == 2:
                            pairs.append(f"({parts[0].strip()}, {parts[1].strip()})")
                    body = ", ".join(pairs)
                    out = out[:m.start()] + f"= {ty_text}([{body}])" + out[m.end():]
                else:
                    out = out[:m.start()] + f"= {ty_text}([{inner}])" + out[m.end():]
    # Inferred bindings (``let xs = [1,2,3]``) — Swift infers ``Array<Int>``;
    # Cangjie inference would land on ``Array<Int64>`` which has no ``.add`` /
    # ``.remove``.  Promote homogeneous integer/float/string literals to the
    # corresponding ``ArrayList<…>`` so the value behaves like a Swift Array.
    if pat.name in ("let_inferred", "var_inferred"):
        eq_pos = out.find("=")
        rhs = out[eq_pos + 1:].strip() if eq_pos >= 0 else ""
        if rhs.startswith("[") and rhs.endswith("]") and len(rhs) >= 2:
            inner = rhs[1:-1].strip()
            # Skip dictionary literals (``k: v``) — let user type them.
            if ":" not in inner or _is_pair_free(inner):
                inner_rec = _wrap_call_site_array_literals(
                    "(" + inner + ")"
                )[1:-1]
                inner_rec = _tighten_generic_spacing(inner_rec)
                elem_ty = _guess_elem_type_extended(inner_rec)
                if elem_ty:
                    prefix = out[:eq_pos]
                    out = (
                        prefix
                        + f"= ArrayList<{elem_ty}>([{inner_rec}])"
                    )
    return out


def _is_pair_free(s: str) -> bool:
    """Return True iff *s* (an array literal's inner text) does **not** look
    like a dictionary literal (no top-level ``key: value`` separator)."""

    depth = 0
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(depth - 1, 0)
        elif ch == ":" and depth == 0:
            return False
    return True


def _convert_dict_literal_to_pairs(inner: str) -> Optional[str]:
    """Convert the inner text of a Swift dictionary literal ``"k1": v1, "k2": v2``
    into a comma-separated list of tuples ``("k1", v1), ("k2", v2)`` suitable
    for ``HashMap([...])``.  Returns ``None`` if the literal is empty (``[:]``),
    malformed, or looks like a *type* literal (``[Key: Value]`` with both
    halves bare type identifiers) rather than a value literal.  String literals
    and nested brackets are honoured."""

    # Split top-level commas (depth-0 only).
    pieces: List[str] = []
    cur: List[str] = []
    depth = 0
    in_str = False
    i = 0
    n = len(inner)
    while i < n:
        ch = inner[i]
        if in_str:
            cur.append(ch)
            if ch == "\\" and i + 1 < n:
                cur.append(inner[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            cur.append(ch)
            i += 1
            continue
        if ch in "([{":
            depth += 1
            cur.append(ch)
        elif ch in ")]}":
            depth = max(depth - 1, 0)
            cur.append(ch)
        elif ch == "," and depth == 0:
            pieces.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    last = "".join(cur).strip()
    if last:
        pieces.append(last)
    if not pieces:
        return None
    # Split each piece at the *first* top-level colon into key, value.
    out: List[str] = []
    for piece in pieces:
        depth = 0
        in_str = False
        split_at = -1
        for k, ch in enumerate(piece):
            if in_str:
                if ch == "\\" and k + 1 < len(piece):
                    continue
                if ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
                continue
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth = max(depth - 1, 0)
            elif ch == ":" and depth == 0:
                split_at = k
                break
        if split_at < 0:
            return None
        key = piece[:split_at].strip()
        val = piece[split_at + 1:].strip()
        if not key or not val:
            return None
        # Type-literal guard: ``[Key: Value]`` where both halves are bare
        # identifiers (no quotes, parens, dots or call syntax) is almost
        # certainly a *type* (enum payload, parameter annotation), not a
        # dictionary value.  Skip wrapping in that case.
        if (re.fullmatch(r"[A-Za-z_]\w*", key)
                and re.fullmatch(r"[A-Za-z_]\w*", val)):
            return None
        out.append(f"({key}, {val})")
    return ", ".join(out)


def _guess_elem_type(inner: str) -> str:
    """Inspect a homogeneous array-literal body and return the Cangjie element
    type, or ``""`` if it cannot be determined unambiguously."""

    parts = _split_top_level(inner, ",")
    if not parts:
        return ""
    saw_float = False
    saw_int = False
    saw_str = False
    saw_other = False
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if re.fullmatch(r"-?\d+", p):
            saw_int = True
        elif re.fullmatch(r"-?\d+\.\d+(?:[eE][+-]?\d+)?", p):
            saw_float = True
        elif p.startswith('"') and p.endswith('"'):
            saw_str = True
        else:
            saw_other = True
    if saw_other:
        return ""
    if saw_float and not saw_str:
        return "Float64"
    if saw_int and not saw_str and not saw_float:
        return "Int64"
    if saw_str and not saw_int and not saw_float:
        return "String"
    return ""


def _scan_method_names(tokens: List[Token]) -> set:
    names: set = set()
    i, n = 0, len(tokens)
    depth = 0
    while i < n:
        t = tokens[i]
        if t.value == "{":
            depth += 1
        elif t.value == "}":
            depth -= 1
        if depth != 0:
            i += 1
            continue
        # look for ``func NAME``
        if t.kind == "KEYWORD" and t.value == "func":
            if i + 1 < n and tokens[i + 1].kind == "IDENT":
                names.add(tokens[i + 1].value)
        i += 1
    return names


def _scan_class_fields(body: str) -> List[Tuple[str, str, str, Optional[str]]]:
    """Return ``(kw, name, ty, default_or_None)`` for every TOP-LEVEL field
    declaration in *body* (i.e. brace-depth == 0).

    A regex-only scan is unreliable because it picks up ``let i: Int = ...``
    declarations *inside* method bodies; here we walk character-by-character
    and only inspect lines at brace depth 0.
    """

    fields: List[Tuple[str, str, str, Optional[str]]] = []
    depth = 0
    i, n = 0, len(body)
    line_start = 0
    while i <= n:
        ch = body[i] if i < n else "\n"
        if ch == "{":
            depth += 1
            i += 1
            continue
        if ch == "}":
            depth -= 1
            i += 1
            continue
        if ch == "\n":
            if depth == 0:
                line = body[line_start:i]
                m = re.match(
                    r"^\s*(?:public\s+|private\s+|protected\s+|static\s+)*"
                    r"(var|let)\s+([A-Za-z_]\w*)\s*:\s*([^=\n]+?)"
                    r"(?:\s*=\s*(.+?))?\s*$",
                    line,
                )
                if m:
                    fields.append((m.group(1), m.group(2), m.group(3).strip(),
                                   m.group(4)))
            line_start = i + 1
        i += 1
    return fields


def _ensure_memberwise_init(class_text: str) -> str:
    """If a class/struct body has no ``init``, synthesize a memberwise one.

    Swift gives structs an implicit memberwise initialiser; Cangjie has no
    such mechanism so we emit one explicitly using the declared fields.
    Fields that already carry a default value at the declaration site are
    omitted from the init signature — Cangjie keeps the declaration-site
    initialiser in scope when a constructor doesn't reassign that field.

    If *every* field has a default, no synthesis is performed: Cangjie's
    implicit zero-arg constructor is sufficient.
    """

    if re.search(r"\b(public\s+)?init\s*\(", class_text):
        return class_text
    m = re.search(r"\{\n(.*)\n\}\s*$", class_text, flags=re.DOTALL)
    if not m:
        return class_text
    body = m.group(1)
    fields = _scan_class_fields(body)
    fields_no_default = [f for f in fields if f[3] is None]
    if not fields:
        return class_text
    if not fields_no_default:
        return class_text
    params = []
    assigns = []
    for _kw, name, ty, _default in fields_no_default:
        params.append(f"{name}!: {ty}")
        assigns.append(f"        this.{name} = {name}")
    init_text = (
        "    public init(" + ", ".join(params) + ") {\n"
        + "\n".join(assigns) + "\n    }"
    )
    new_body = body.rstrip() + "\n" + init_text
    return class_text[:m.start()] + "{\n" + new_body + "\n}" + class_text[m.end():]


# --------------------------------------------------------------------------- #
#  Expression rewriting                                                       #
# --------------------------------------------------------------------------- #
def _convert_expr(tokens: List[Token]) -> str:
    """Render an expression's token list to Cangjie surface syntax."""

    tokens = _strip_trailing_semicolon(tokens)
    rendered = _render_tokens(tokens)
    # Drop any stray ``try`` (Swift call-site marker — Cangjie has no analogue).
    rendered = re.sub(r"\btry\s*[!?]?\s*", "", rendered)
    # Swift array literal type-form ``[Int]()`` → ``ArrayList<Int64>()``.
    rendered = re.sub(r"\[\s*([^\[\]:,]+?)\s*\]\s*\(\s*\)",
                      lambda m: f"ArrayList<{_convert_type_text(m.group(1))}>()",
                      rendered)
    # Swift dictionary literal type-form ``[K: V]()`` → ``HashMap<K, V>()``.
    rendered = re.sub(
        r"\[\s*([^\[\]]+?)\s*:\s*([^\[\]]+?)\s*\]\s*\(\s*\)",
        lambda m: f"HashMap<{_convert_type_text(m.group(1))}, {_convert_type_text(m.group(2))}>()",
        rendered,
    )
    rendered = _apply_primitive_types(rendered)
    return rendered.strip()


def _convert_params(tokens: List[Token]) -> str:
    """Convert a Swift parameter list to Cangjie form.

    Swift allows external + internal labels (``func f(_ x: Int)`` /
    ``func f(label x: Int)``).  Cangjie uses a single parameter name; we
    drop the external label (the underscore ``_`` is a Swift "no external
    label" marker, and a distinct ``label`` external would conflict with
    Cangjie's call-site syntax — the downstream AI pass can recover named
    arguments where needed).
    """

    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    if not text:
        return ""
    parts = _split_top_level(text, ",")
    out_parts: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Swift forms:
        #   ``name: Type``
        #   ``ext name: Type``         (external + internal label)
        #   ``_ name: Type``           (no external label)
        #   ``name: Type = default``
        #   ``inout name: Type``
        p = re.sub(r"^inout\s+", "", p)
        # In Swift ``inout`` may also appear *after* the parameter label,
        # e.g. ``visited: inout [Bool]``.  Strip it from the type as well.
        p = re.sub(r":\s*inout\s+", ": ", p)
        m = re.match(
            r"^(?:(_|[A-Za-z_][\w]*)\s+)?([A-Za-z_][\w]*)\s*:\s*([^=]+?)\s*(?:=\s*(.+))?$",
            p,
        )
        if not m:
            out_parts.append(p)
            continue
        _ext, name, ty, default = m.group(1), m.group(2), m.group(3), m.group(4)
        ty_t = _convert_type_text(ty.strip())
        # Swift function calls use labels by default (``f(x: 5)``) for any
        # parameter that doesn't have a leading ``_`` to suppress the label.
        # Cangjie's positional parameters won't accept that call form, so we
        # emit a named (``!``) parameter unless the Swift form was
        # explicitly positional (``_ name: Type``).
        is_positional = _ext == "_"
        if default is not None:
            out_parts.append(f"{name}!: {ty_t} = {default.strip()}")
        elif is_positional:
            out_parts.append(f"{name}: {ty_t}")
        else:
            out_parts.append(f"{name}!: {ty_t}")
    return ", ".join(out_parts)


def _convert_type(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    return _convert_type_text(text)


def _convert_type_text(text: str) -> str:
    """Translate a Swift type expression to Cangjie.

    * ``Int`` / ``Double`` / etc.  → ``Int64`` / ``Float64`` / etc.
    * ``T?``                       → ``?T``
    * ``[T]``                      → ``ArrayList<T>``
    * ``[K: V]``                   → ``HashMap<K, V>``
    * ``(T, U)``                   → ``(T, U)`` (Cangjie tuple)
    """

    text = (text or "").strip()
    if not text:
        return "Any"

    # Optional ``T?`` (allow chained ``T??`` collapsed to ``?T``).
    if text.endswith("?"):
        return "?" + _convert_type_text(text[:-1].strip())

    # Dictionary ``[K: V]``.
    if text.startswith("[") and text.endswith("]") and ":" in text:
        inner = text[1:-1]
        parts = _split_top_level(inner, ":")
        if len(parts) == 2:
            k = _convert_type_text(parts[0].strip())
            v = _convert_type_text(parts[1].strip())
            return f"HashMap<{k}, {v}>"

    # Array ``[T]``.
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return f"ArrayList<{_convert_type_text(inner)}>"

    # Tuple ``(T, U)`` — Cangjie tuples share the same surface form.
    if text.startswith("(") and text.endswith(")") and "," in text:
        inner = text[1:-1]
        elems = []
        for elem in _split_top_level(inner, ","):
            elem = elem.strip()
            if ":" in elem:
                _label, elem = elem.split(":", 1)
                elem = elem.strip()
            elems.append(_convert_type_text(elem))
        return "(" + ", ".join(elems) + ")"

    text = _apply_primitive_types(text)
    return text


def _convert_type_params(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    out: List[str] = []
    for p in _split_top_level(text, ","):
        p = p.strip()
        if not p:
            continue
        # ``T: Foo`` (Swift conformance constraint) → drop constraint.
        m = re.match(r"^([A-Za-z_][\w]*)\s*(?::\s*(.+))?$", p)
        if m:
            out.append(m.group(1))
        else:
            out.append(p)
    return ", ".join(out)


# --------------------------------------------------------------------------- #
#  Enum / switch helpers                                                      #
# --------------------------------------------------------------------------- #
def _convert_enum_variant_payload(variant: str) -> str:
    """For ``name(T, U)`` variants, translate each payload type via
    :func:`_convert_type_text` so that array/dictionary surface forms
    (``[T]``, ``[K: V]``) are converted just like field type annotations.
    Variants without a payload are returned unchanged.
    """

    m = re.match(r"^([A-Za-z_]\w*)\s*\((.*)\)\s*$", variant, re.DOTALL)
    if not m:
        return variant
    name = m.group(1)
    payload = m.group(2)
    parts = []
    for p in _split_top_level(payload, ","):
        p = p.strip()
        if not p:
            continue
        parts.append(_convert_type_text(p))
    return f"{name}({', '.join(parts)})"


def _convert_enum_body(tokens: List[Token]) -> str:
    """Convert a Swift enum body into Cangjie ``| Var1 | Var2`` form.

    Swift enums look like::

        case a
        case b, c
        case d(Int)

    We split on each ``case`` keyword and collect comma-separated variant
    names; payload types in parentheses are preserved verbatim.
    """

    variants: List[str] = []
    i, n = 0, len(tokens)
    while i < n:
        t = tokens[i]
        if t.kind == "KEYWORD" and t.value == "case":
            i += 1
            # collect tokens until ``;`` (already inserted) or another ``case``
            # or end.
            buf: List[Token] = []
            while i < n:
                tt = tokens[i]
                if tt.kind == "PUNCT" and tt.value == ";":
                    i += 1
                    break
                if tt.kind == "KEYWORD" and tt.value == "case":
                    break
                buf.append(tt)
                i += 1
            # Split on top-level commas.
            text = _render_tokens(buf).strip()
            # Strip raw-value assignment ``= 0`` / ``= "red"`` per variant.
            text = re.sub(r"\s*=\s*[^,]+", "", text)
            # Translate primitive type names inside payload tuples
            # (``rect(Int, Int)`` → ``rect(Int64, Int64)``).
            text = _apply_primitive_types(text)
            for v in _split_top_level(text, ","):
                v = v.strip()
                if v:
                    variants.append(_convert_enum_variant_payload(v))
            continue
        i += 1
    if not variants:
        return "    /* swift2cj: empty enum */"
    return "    | " + "\n    | ".join(variants)


def _convert_switch_body(tokens: List[Token]) -> str:
    """Convert a Swift ``switch`` body into Cangjie ``match`` arms."""

    toks = [t for t in tokens if t.kind not in ("COMMENT_BLOCK", "COMMENT_LINE")]

    cases: List[Tuple[List[List[Token]], List[Token]]] = []
    cur_labels: List[List[Token]] = []
    cur_body: List[Token] = []
    brace_depth = 0

    def flush():
        if cur_labels or cur_body:
            cases.append((list(cur_labels), list(cur_body)))

    i, n = 0, len(toks)
    while i < n:
        t = toks[i]
        if t.kind == "PUNCT" and t.value == "{":
            brace_depth += 1
            cur_body.append(t)
            i += 1
            continue
        if t.kind == "PUNCT" and t.value == "}":
            brace_depth -= 1
            cur_body.append(t)
            i += 1
            continue
        if brace_depth == 0 and t.kind == "KEYWORD" and t.value == "case":
            if cur_body:
                flush()
                cur_labels.clear()
                cur_body.clear()
            i += 1
            # In Swift ``case Foo, Bar:`` the labels are comma-separated then ``:``.
            lab_tokens: List[Token] = []
            while i < n and not (toks[i].kind == "PUNCT" and toks[i].value == ":"):
                lab_tokens.append(toks[i])
                i += 1
            i += 1  # skip ``:``
            # Split labels by top-level commas (depth-aware so that
            # ``case .rect(let w, let h):`` stays a single label).
            buf: List[Token] = []
            depth_p = depth_s = depth_b = 0
            for tt in lab_tokens:
                v = tt.value
                if v == "(":
                    depth_p += 1
                elif v == ")":
                    depth_p = max(depth_p - 1, 0)
                elif v == "[":
                    depth_s += 1
                elif v == "]":
                    depth_s = max(depth_s - 1, 0)
                elif v == "{":
                    depth_b += 1
                elif v == "}":
                    depth_b = max(depth_b - 1, 0)
                if (
                    tt.kind == "PUNCT" and v == ","
                    and depth_p == 0 and depth_s == 0 and depth_b == 0
                ):
                    if buf:
                        cur_labels.append(buf)
                    buf = []
                else:
                    buf.append(tt)
            if buf:
                cur_labels.append(buf)
            continue
        if brace_depth == 0 and t.kind == "KEYWORD" and t.value == "default":
            if cur_body:
                flush()
                cur_labels.clear()
                cur_body.clear()
            i += 1
            if i < n and toks[i].kind == "PUNCT" and toks[i].value == ":":
                i += 1
            cur_labels.append([])
            continue
        # Drop any synthesised ``;`` at this level — match arms use newlines.
        if brace_depth == 0 and t.kind == "KEYWORD" and t.value == "break":
            j = i + 1
            if j < n and toks[j].kind == "PUNCT" and toks[j].value == ";":
                i = j + 1
                continue
        cur_body.append(t)
        i += 1
    flush()

    if not cases:
        return "    case _ => ()"

    out_lines: List[str] = []
    for labels, body in cases:
        is_default = any(len(l) == 0 for l in labels)
        body_text = _convert_body(body, indent=2)
        if is_default:
            label_str = "_"
        else:
            label_str = " | ".join(_convert_expr(l) for l in labels if l)
            # Strip Swift ``let `` binders inside enum-payload destructuring:
            # ``case rect(let w, let h)`` → ``case rect(w, h)``.
            label_str = re.sub(r"\blet\s+", "", label_str)
            # If the label is a bare enum case ``Enum.case`` whose declared
            # arity is > 0 (i.e. it has a payload) and no destructuring
            # parens were supplied, Swift's shorthand means "match any
            # payload".  Cangjie has no such shorthand — append ``(_, …, _)``.
            def _addw(m: "re.Match") -> str:
                full = m.group(0)
                cname = m.group(2)
                info = _ENUM_CASE_INFO.get(cname)
                if info and info[1] > 0:
                    placeholders = ", ".join("_" for _ in range(info[1]))
                    return f"{full}({placeholders})"
                return full
            label_str = re.sub(
                r"\b([A-Z][A-Za-z_0-9]*)\.([A-Za-z_]\w*)(?!\s*\()",
                _addw,
                label_str,
            )
        out_lines.append(f"    case {label_str} =>")
        body_lines = [ln for ln in body_text.split("\n") if ln.strip()]
        if not body_lines:
            out_lines.append("        ()")
        else:
            out_lines.extend(body_lines)
    return "\n".join(out_lines)


# --------------------------------------------------------------------------- #
#  Top-level driver                                                           #
# --------------------------------------------------------------------------- #
_NEEDS_COLLECTION = re.compile(r"\b(ArrayList|HashMap|HashSet)\b")
_GENERIC_NAMES = (
    "ArrayList", "HashMap", "HashSet", "Array", "Map", "Set",
    "Option", "Iterator", "List", "Queue", "Stack", "Box",
)
_ANGLE_BRACKET_TYPES = _GENERIC_NAMES + ("Equatable", "Hashable", "Comparable")


def _tighten_generic_spacing(text: str) -> str:
    name_alt = "|".join(_ANGLE_BRACKET_TYPES)
    pat_open = re.compile(rf"\b({name_alt})\s+<\s*")
    pat_close = re.compile(r"([\w\)>\]])\s+>")
    pat_call = re.compile(rf"\b({name_alt})(<[^<>\n]*(?:<[^<>\n]*>[^<>\n]*)*>)\s+\(")
    for _ in range(6):
        new = pat_open.sub(r"\1<", text)
        new = pat_close.sub(r"\1>", new)
        new = pat_call.sub(r"\1\2(", new)
        if new == text:
            break
        text = new
    return text


def _polish_cj_style(text: str) -> str:
    """Apply small Cangjie-style whitespace polish to generated code.

    This intentionally stays conservative and string-aware: it does not try to
    be a formatter, but fixes the most visible non-professional artefacts from
    token rendering (``a> b``, ``a&&!b``, ``if(cond)``) while preserving generic
    type arguments such as ``ArrayList<Int64>``.
    """

    protected: List[str] = []
    name_alt = "|".join(_ANGLE_BRACKET_TYPES)

    def _mask_generic(m: "re.Match") -> str:
        protected.append(m.group(0))
        return f"__SWIFT2CJ_GENERIC_{len(protected) - 1}__"

    masked = re.sub(
        rf"\b(?:{name_alt})<[^<>\n]*(?:<[^<>\n]*>[^<>\n]*)*>",
        _mask_generic,
        text,
    )
    masked = _outside_strings_regex(masked, r"\b(if|while|for|match)\(", r"\1 (")
    masked = _outside_strings_regex(masked, r"}\s*else\s*{", r"} else {")
    masked = _outside_strings_regex(masked, r"(?<=[\w\]\)])\s*(==|!=|<=|>=|&&|\|\|)\s*(?=[!\w\(\[])", r" \1 ")
    masked = _outside_strings_regex(masked, r"(?<=[\w\]\)])\s*([<>])\s*(?=[\w\(\[])", r" \1 ")
    masked = _outside_strings_regex(masked, r"&&\s*!", r"&& !")
    masked = _outside_strings_regex(masked, r"\)\s*\{", r") {")
    masked = _outside_strings_regex(masked, r"\}\s*else\b", r"} else")
    masked = _outside_strings_regex(masked, r"\boperator func (==|!=|<=|>=|<|>)\s+\(", r"operator func \1(")
    masked = _outside_strings_regex(masked, r"([=(,\[:])\s*-\s+(?=\d)", r"\1-")
    masked = _outside_strings_regex(masked, r"=\s*-(?=\d)", r"= -")
    masked = _outside_strings_regex(masked, r"\breturn\s+-\s+(?=\d)", r"return -")
    for i, original in enumerate(protected):
        masked = masked.replace(f"__SWIFT2CJ_GENERIC_{i}__", original)
    return masked


def convert_source(swift_source: str, wrap_main: bool = True) -> ConversionResult:
    """Convert a Swift source string into Cangjie source."""

    global _TYPE_ALIASES, _CLASS_METHODS, _CLASS_PARENT, _PARENT_CLASS_NAMES
    global _ENUM_CASE_INFO
    rewritten, notes = _rewrite_source(swift_source)
    tokens = tokenize(rewritten)
    # Synthesise statement-terminating ``;`` tokens at top-level newlines.
    tokens = _insert_semicolons(tokens)
    _TYPE_ALIASES.clear()
    _CLASS_METHODS.clear()
    _CLASS_PARENT.clear()
    _PARENT_CLASS_NAMES = _scan_parent_class_names(rewritten)
    _ENUM_CASE_INFO.clear()
    _ENUM_CASE_INFO.update(_scan_enum_cases(rewritten))

    chunks = _segment_chunks(tokens)
    result = ConversionResult(source="", notes=notes)
    result.chunks = sum(1 for c in chunks if c)

    rendered_chunks: List[str] = []
    top_level_decls: List[str] = []
    main_body: List[str] = []
    has_user_main = False

    for ch in chunks:
        if not ch:
            continue
        cj = _convert_chunk(ch)
        if cj is None:
            result.fallback_chunks += 1
            verbatim = _render_tokens(ch)
            cj = f"/* swift2cj: TODO unrecognised chunk */ // {verbatim}"
        elif cj == "":
            # Empty emission (e.g. ``import``) — count as confident but skip.
            result.confident_chunks += 1
            continue
        else:
            result.confident_chunks += 1
        rendered_chunks.append(cj)

        # Top-level classification.
        i0 = 0
        while i0 < len(ch) and ch[i0].value in (
            "public", "private", "internal", "fileprivate", "open", "final",
            "static", "indirect",
        ):
            i0 += 1
        first = ch[i0].value if i0 < len(ch) else ""
        if first in (
            "class", "struct", "enum", "protocol", "extension",
            "func", "typealias", "import",
        ):
            if first == "func" and i0 + 1 < len(ch) and ch[i0 + 1].value == "main":
                has_user_main = True
                cj = re.sub(
                    r"^func\s+main\s*\([^)]*\)\s*(?::\s*\w+\s*)?\{",
                    "main() {", cj, count=1,
                )
                if "\nreturn " not in cj and "\n    return " not in cj:
                    cj = cj[:-1] + "    return 0\n}"
                rendered_chunks[-1] = cj
            top_level_decls.append(cj)
        elif first in ("let", "var"):
            # Swift top-level scripts run sequentially; if any imperative
            # statement has *already* been emitted into ``main_body`` we
            # must keep this binding *inside* ``main`` to preserve order
            # (otherwise a top-level ``let t = m.transpose()`` would run
            # *before* the earlier ``m.fillSequential()`` call).
            if main_body:
                main_body.append(cj)
            else:
                top_level_decls.append(cj)
        else:
            main_body.append(cj)

    if has_user_main:
        wrap_main = False

    parts: List[str] = []
    if top_level_decls:
        parts.extend(top_level_decls)
    if wrap_main:
        if not any(re.search(r"^main\s*\(", d, re.MULTILINE) for d in top_level_decls):
            body = "\n".join("    " + ln for ln in "\n".join(main_body).split("\n") if ln)
            parts.append("main() {\n" + body + "\n    return 0\n}")
    else:
        parts.extend(main_body)

    body_text = "\n\n".join(p for p in parts if p)
    body_text = _tighten_generic_spacing(body_text)
    body_text = _polish_cj_style(body_text)
    helper_parts: List[str] = []
    if "_swiftArrayRepeating(" in body_text:
        helper_parts.append(
            "func _swiftArrayRepeating<T>(value: T, count: Int64): ArrayList<T> {\n"
            "    var out = ArrayList<T>()\n"
            "    var i = 0\n"
            "    while (i < count) {\n"
            "        out.add(value)\n"
            "        i += 1\n"
            "    }\n"
            "    return out\n"
            "}"
        )
    if "_swiftArray2DRepeating(" in body_text:
        helper_parts.append(
            "func _swiftArray2DRepeating<T>(value: T, rows: Int64, cols: Int64): ArrayList<ArrayList<T>> {\n"
            "    var out = ArrayList<ArrayList<T>>()\n"
            "    var i = 0\n"
            "    while (i < rows) {\n"
            "        var row = ArrayList<T>()\n"
            "        var j = 0\n"
            "        while (j < cols) {\n"
            "            row.add(value)\n"
            "            j += 1\n"
            "        }\n"
            "        out.add(row)\n"
            "        i += 1\n"
            "    }\n"
            "    return out\n"
            "}"
        )
    if "_swiftArrayReversed(" in body_text:
        helper_parts.append(
            "func _swiftArrayReversed<T>(items: ArrayList<T>): ArrayList<T> {\n"
            "    var out = ArrayList<T>()\n"
            "    var i = items.size - 1\n"
            "    while (i >= 0) {\n"
            "        out.add(items[i])\n"
            "        i -= 1\n"
            "    }\n"
            "    return out\n"
            "}"
        )
    if helper_parts:
        body_text = "\n\n".join(helper_parts + [body_text])

    headers: List[str] = []
    if _NEEDS_COLLECTION.search(body_text):
        headers.append("import std.collection.*")
    header = ("\n".join(headers) + "\n\n") if headers else ""
    result.source = header + body_text + ("\n" if body_text and not body_text.endswith("\n") else "")
    return result
