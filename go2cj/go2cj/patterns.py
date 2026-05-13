"""Built-in Go → Cangjie translation patterns.

Each pattern is a pair ``(go_template, cj_template)`` plus optional slot
metadata.  Patterns use ``$NAME`` placeholders for *slots*; downstream
code performs non-linear slot binding by token-similarity matching.

Two pattern kinds:

* **Chunk patterns** — match whole top-level Go chunks (a statement, a
  declaration, a function/struct/interface).  These drive the main
  self-organizing retrieval.
* **Token mappings** — single token / short-phrase rewrites stored in
  the Hopfield memory (``fmt.Println`` → ``println``, ``len`` → size-like
  context, etc.).

Templates are written with Go-flavoured pseudo-source so that their
embeddings naturally cluster near real Go inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Pattern:
    name: str
    go_template: str
    cj_template: str
    # Slot type hints help slot binding pick the right token spans.
    slots: tuple = ()


# --------------------------------------------------------------------------- #
#  Chunk patterns                                                             #
# --------------------------------------------------------------------------- #
CHUNK_PATTERNS: List[Pattern] = [
    # ---- top-level package / import housekeeping ------------------------- #
    # These get dropped at top-level assembly.  They still need to bind so
    # we don't fall back to TODO.
    Pattern("pkg_decl", "package $NAME", "/* go2cj: package $NAME */", ("NAME",)),
    Pattern("import_single", "import $S", "/* go2cj: import $S */", ("S",)),
    Pattern("import_group", "import ( $BODY )", "/* go2cj: import group */", ("BODY",)),

    # ---- type declarations ----------------------------------------------- #
    Pattern(
        "type_alias",
        "type $NAME = $TY",
        "type $NAME = $TY",
        ("NAME", "TY"),
    ),
    Pattern(
        "type_def",
        "type $NAME $TY",
        "type $NAME = $TY",
        ("NAME", "TY"),
    ),
    Pattern(
        "struct_decl",
        "type $NAME struct { $BODY }",
        "class $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "interface_decl",
        "type $NAME interface { $BODY }",
        "interface $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),

    # ---- variable declarations ------------------------------------------- #
    Pattern(
        "var_typed_init",
        "var $NAME : $TY = $EXPR",
        "var $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "var_typed",
        "var $NAME : $TY",
        "var $NAME: $TY = $DEFAULT",
        ("NAME", "TY"),
    ),
    Pattern(
        "var_inferred",
        "var $NAME = $EXPR",
        "var $NAME = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_typed_init",
        "const $NAME : $TY = $EXPR",
        "let $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "const_inferred",
        "const $NAME = $EXPR",
        "let $NAME = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_group",
        "const ( $BODY )",
        "$BODY",  # body is expanded as multiple let decls
        ("BODY",),
    ),
    Pattern(
        "var_group",
        "var ( $BODY )",
        "$BODY",  # body is expanded as multiple var decls
        ("BODY",),
    ),
    Pattern(
        "short_decl_single",
        "$NAME := $EXPR",
        "var $NAME = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "short_decl_multi",
        "$NAMES := $EXPR",
        "let ($NAMES) = ($EXPR)",
        ("NAMES", "EXPR"),
    ),

    # ---- assignments ----------------------------------------------------- #
    Pattern(
        "assign_simple",
        "$LHS = $RHS",
        "$LHS = $RHS",
        ("LHS", "RHS"),
    ),
    Pattern(
        "assign_plus",
        "$LHS += $RHS",
        "$LHS += $RHS",
        ("LHS", "RHS"),
    ),
    Pattern(
        "assign_minus",
        "$LHS -= $RHS",
        "$LHS -= $RHS",
        ("LHS", "RHS"),
    ),
    Pattern(
        "assign_mul",
        "$LHS *= $RHS",
        "$LHS *= $RHS",
        ("LHS", "RHS"),
    ),
    Pattern(
        "assign_div",
        "$LHS /= $RHS",
        "$LHS /= $RHS",
        ("LHS", "RHS"),
    ),
    Pattern(
        "incr_stmt",
        "$LHS ++",
        "$LHS += 1",
        ("LHS",),
    ),
    Pattern(
        "decr_stmt",
        "$LHS --",
        "$LHS -= 1",
        ("LHS",),
    ),

    # ---- IO / printing --------------------------------------------------- #
    Pattern(
        "fmt_println",
        "fmt . Println ( $EXPR )",
        "println($EXPR)",
        ("EXPR",),
    ),
    Pattern(
        "fmt_println_noargs",
        "fmt . Println ( )",
        "println(\"\")",
        (),
    ),
    Pattern(
        "fmt_print",
        "fmt . Print ( $EXPR )",
        "print($EXPR)",
        ("EXPR",),
    ),
    Pattern(
        "fmt_printf",
        "fmt . Printf ( $EXPR )",
        "print($EXPR)",  # downstream printf-string rewrite handles the format
        ("EXPR",),
    ),
    Pattern(
        "fmt_sprintf_assign",
        "$NAME := fmt . Sprintf ( $EXPR )",
        "let $NAME = $EXPR",  # rewritten as interpolated string
        ("NAME", "EXPR"),
    ),

    # ---- control flow ---------------------------------------------------- #
    Pattern(
        "if_block",
        "if $COND { $BODY }",
        "if ($COND) {\n$BODY\n}",
        ("COND", "BODY"),
    ),
    Pattern(
        "if_else_block",
        "if $COND { $A } else { $B }",
        "if ($COND) {\n$A\n} else {\n$B\n}",
        ("COND", "A", "B"),
    ),
    Pattern(
        "if_eif_block",
        "if $C1 { $B1 } else if $C2 { $B2 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n}",
        ("C1", "B1", "C2", "B2"),
    ),
    Pattern(
        "if_eif_else_block",
        "if $C1 { $B1 } else if $C2 { $B2 } else { $B3 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n} else {\n$B3\n}",
        ("C1", "B1", "C2", "B2", "B3"),
    ),
    Pattern(
        "if_eif_eif_else_block",
        "if $C1 { $B1 } else if $C2 { $B2 } else if $C3 { $B3 } else { $B4 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n} else if ($C3) {\n$B3\n} else {\n$B4\n}",
        ("C1", "B1", "C2", "B2", "C3", "B3", "B4"),
    ),

    # ---- for loops ------------------------------------------------------- #
    # ``for i := 0; i < N; i++``  →  ``for (i in 0..N)``
    Pattern(
        "for_classic",
        "for $I := $START ; $I < $END ; $I ++ { $BODY }",
        "for ($I in $START..$END) {\n$BODY\n}",
        ("I", "START", "END", "BODY"),
    ),
    Pattern(
        "for_classic_le",
        "for $I := $START ; $I <= $END ; $I ++ { $BODY }",
        "for ($I in $START..=$END) {\n$BODY\n}",
        ("I", "START", "END", "BODY"),
    ),
    # ``for ; cond ; { ... }`` and bare ``for cond { ... }`` → while.
    Pattern(
        "for_cond_only",
        "for $COND { $BODY }",
        "while ($COND) {\n$BODY\n}",
        ("COND", "BODY"),
    ),
    # ``for { ... }`` (infinite) → ``while (true) { ... }``.
    Pattern(
        "for_infinite",
        "for { $BODY }",
        "while (true) {\n$BODY\n}",
        ("BODY",),
    ),
    # ``for i, v := range xs { ... }``
    Pattern(
        "for_range_idx_val",
        "for $I , $V := range $XS { $BODY }",
        "for (($I, $V) in $XS.iterator().enumerate()) {\n$BODY\n}",
        ("I", "V", "XS", "BODY"),
    ),
    # ``for _, v := range xs { ... }``
    Pattern(
        "for_range_under_val",
        "for _ , $V := range $XS { $BODY }",
        "for ($V in $XS) {\n$BODY\n}",
        ("V", "XS", "BODY"),
    ),
    # ``for k := range m { ... }``  (range over map keys; also over slice idx)
    Pattern(
        "for_range_key_only",
        "for $K := range $XS { $BODY }",
        "for ($K in $XS.keys()) {\n$BODY\n}",
        ("K", "XS", "BODY"),
    ),
    # ``for k, v := range m { ... }``
    Pattern(
        "for_range_kv",
        "for $K , $V := range $XS { $BODY }",
        "for ((__k, $V) in $XS) {\nlet $K = __k\n$BODY\n}",
        ("K", "V", "XS", "BODY"),
    ),

    # ---- branching ------------------------------------------------------- #
    Pattern(
        "switch_block",
        "switch $EXPR { $BODY }",
        "match ($EXPR) {\n$SWBODY\n}",
        ("EXPR", "BODY"),
    ),
    Pattern(
        "switch_no_expr",
        "switch { $BODY }",
        "$IFBODY",  # rewritten by switch-body handler as if/else-if chain
        ("BODY",),
    ),

    # ---- jumps ----------------------------------------------------------- #
    Pattern("return_expr", "return $EXPR", "return $EXPR", ("EXPR",)),
    Pattern("return_void", "return", "return", ()),
    Pattern("break_stmt", "break", "break", ()),
    Pattern("continue_stmt", "continue", "continue", ()),

    # ---- functions ------------------------------------------------------- #
    # Plain ``func name(params) ret { body }``.
    Pattern(
        "func_decl_ret",
        "func $NAME ( $PARAMS ) $RET { $BODY }",
        "func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "func_decl_noret",
        "func $NAME ( $PARAMS ) { $BODY }",
        "func $NAME($PARAMS): Unit {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    # Multi-return: ``func name(params) (T, U) { body }``.
    Pattern(
        "func_decl_multi_ret",
        "func $NAME ( $PARAMS ) ( $RETS ) { $BODY }",
        "func $NAME($PARAMS): ($RETS) {\n$BODY\n}",
        ("NAME", "PARAMS", "RETS", "BODY"),
    ),
    # Method declaration: ``func (r T) Name(params) ret { body }``.
    # We render these as standalone funcs for simplicity (Cangjie doesn't
    # have Go's free-receiver methods); downstream AI pass can promote to
    # class methods if desired.
    Pattern(
        "method_decl_ret",
        "func ( $RECV ) $NAME ( $PARAMS ) $RET { $BODY }",
        "func $NAME($RECV, $PARAMS): $RET {\n$BODY\n}",
        ("RECV", "NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "method_decl_noret",
        "func ( $RECV ) $NAME ( $PARAMS ) { $BODY }",
        "func $NAME($RECV, $PARAMS): Unit {\n$BODY\n}",
        ("RECV", "NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "method_decl_multi_ret",
        "func ( $RECV ) $NAME ( $PARAMS ) ( $RETS ) { $BODY }",
        "func $NAME($RECV, $PARAMS): ($RETS) {\n$BODY\n}",
        ("RECV", "NAME", "PARAMS", "RETS", "BODY"),
    ),

    # ---- defer / go (best-effort) --------------------------------------- #
    Pattern(
        "defer_stmt",
        "defer $EXPR",
        "// go2cj: defer (manual cleanup needed)\n$EXPR",
        ("EXPR",),
    ),
    Pattern(
        "go_stmt",
        "go $EXPR",
        "// go2cj: go (use spawn or thread, manual)\n$EXPR",
        ("EXPR",),
    ),

    # ---- fall-through catch-all for plain expression statements ---------- #
    Pattern(
        "expr_stmt",
        "$EXPR",
        "$EXPR",
        ("EXPR",),
    ),
]


# --------------------------------------------------------------------------- #
#  Token / phrase level mappings (Hopfield-stored)                            #
# --------------------------------------------------------------------------- #
TOKEN_MAPPINGS: List[tuple] = [
    # IO short-hands (also covered as chunk patterns; here for any inline
    # references we miss).
    ("fmt.Println", "println"),
    ("fmt.Print",   "print"),
    ("fmt.Printf",  "print"),
    ("fmt.Sprintf", "sprintf"),
    # Length / size.
    ("len", "size"),
    ("cap", "size"),
    # Slice helpers.
    ("append", "add"),
    # Nil-likes.
    ("nil",       "None"),
    # Errors.
    ("error",     "Exception"),
    # Common conversions.
    ("string",    "String"),
    ("int",       "Int64"),
    ("int8",      "Int8"),
    ("int16",     "Int16"),
    ("int32",     "Int32"),
    ("int64",     "Int64"),
    ("uint",      "UInt64"),
    ("uint8",     "UInt8"),
    ("uint16",    "UInt16"),
    ("uint32",    "UInt32"),
    ("uint64",    "UInt64"),
    ("byte",      "UInt8"),
    ("rune",      "Rune"),
    ("float32",   "Float32"),
    ("float64",   "Float64"),
    ("bool",      "Bool"),
]
