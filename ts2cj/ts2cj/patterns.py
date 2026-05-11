"""Built-in TS→Cangjie translation patterns.

Each pattern is a pair (TS template, CJ template) plus optional metadata.
Patterns use ``$NAME`` placeholders for *slots*; downstream code performs
non-linear slot binding by token-similarity matching.

There are two kinds of patterns:

* **Chunk patterns** — match whole top-level chunks (a statement, a
  declaration, a class).  These drive the main self-organizing
  retrieval.
* **Token mappings** — single token / short-phrase rewrites stored in
  the Hopfield memory (e.g. ``console.log`` → ``println``).

Patterns are written with TypeScript-flavoured pseudo-source so that
their embeddings naturally cluster near real TS inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Pattern:
    name: str
    ts_template: str
    cj_template: str
    # Slot type hints help slot binding pick the right token spans.
    slots: tuple = ()


# --------------------------------------------------------------------------- #
#  Chunk patterns                                                             #
# --------------------------------------------------------------------------- #
CHUNK_PATTERNS: List[Pattern] = [
    # ---- variable declarations -------------------------------------------- #
    Pattern(
        "const_number",
        "const $NAME : number = $EXPR ;",
        "let $NAME: Int64 = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_int",
        "const $NAME = $INT ;",
        "let $NAME = $INT",
        ("NAME", "INT"),
    ),
    Pattern(
        "let_number",
        "let $NAME : number = $EXPR ;",
        "var $NAME: Int64 = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_string",
        "const $NAME : string = $EXPR ;",
        "let $NAME: String = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "let_string",
        "let $NAME : string = $EXPR ;",
        "var $NAME: String = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_boolean",
        "const $NAME : boolean = $EXPR ;",
        "let $NAME: Bool = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_array_number",
        "const $NAME : number [ ] = $EXPR ;",
        "let $NAME: ArrayList<Int64> = ArrayList<Int64>($EXPR)",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_array_string",
        "const $NAME : string [ ] = $EXPR ;",
        "let $NAME: ArrayList<String> = ArrayList<String>($EXPR)",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_inferred",
        "const $NAME = $EXPR ;",
        "let $NAME = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "let_inferred",
        "let $NAME = $EXPR ;",
        "var $NAME = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "var_inferred",
        "var $NAME = $EXPR ;",
        "var $NAME = $EXPR",
        ("NAME", "EXPR"),
    ),

    # ---- IO / printing ---------------------------------------------------- #
    Pattern(
        "console_log",
        "console . log ( $EXPR ) ;",
        "println($EXPR)",
        ("EXPR",),
    ),
    Pattern(
        "console_error",
        "console . error ( $EXPR ) ;",
        "eprintln($EXPR)",
        ("EXPR",),
    ),

    # ---- control flow ----------------------------------------------------- #
    Pattern(
        "if_block",
        "if ( $COND ) { $BODY }",
        "if ($COND) {\n$BODY\n}",
        ("COND", "BODY"),
    ),
    Pattern(
        "if_eif_else_block",
        "if ( $C1 ) { $B1 } else if ( $C2 ) { $B2 } else { $B3 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n} else {\n$B3\n}",
        ("C1", "B1", "C2", "B2", "B3"),
    ),
    Pattern(
        "if_eif_eif_else_block",
        "if ( $C1 ) { $B1 } else if ( $C2 ) { $B2 } else if ( $C3 ) { $B3 } else { $B4 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n} else if ($C3) {\n$B3\n} else {\n$B4\n}",
        ("C1", "B1", "C2", "B2", "C3", "B3", "B4"),
    ),
    Pattern(
        "if_eif_eif_eif_else_block",
        "if ( $C1 ) { $B1 } else if ( $C2 ) { $B2 } else if ( $C3 ) { $B3 } else if ( $C4 ) { $B4 } else { $B5 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n} else if ($C3) {\n$B3\n} else if ($C4) {\n$B4\n} else {\n$B5\n}",
        ("C1", "B1", "C2", "B2", "C3", "B3", "C4", "B4", "B5"),
    ),
    Pattern(
        "if_eif_block",
        "if ( $C1 ) { $B1 } else if ( $C2 ) { $B2 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n}",
        ("C1", "B1", "C2", "B2"),
    ),
    Pattern(
        "if_else_block",
        "if ( $COND ) { $A } else { $B }",
        "if ($COND) {\n$A\n} else {\n$B\n}",
        ("COND", "A", "B"),
    ),
    Pattern(
        "while_block",
        "while ( $COND ) { $BODY }",
        "while ($COND) {\n$BODY\n}",
        ("COND", "BODY"),
    ),
    Pattern(
        "for_classic",
        "for ( let $I = $START ; $I < $END ; $I ++ ) { $BODY }",
        "for ($I in $START..$END) {\n$BODY\n}",
        ("I", "START", "END", "BODY"),
    ),
    Pattern(
        "for_of",
        "for ( const $I of $XS ) { $BODY }",
        "for ($I in $XS) {\n$BODY\n}",
        ("I", "XS", "BODY"),
    ),
    Pattern(
        "for_in_obj",
        "for ( const $K in $XS ) { $BODY }",
        "for ($K in $XS.keys()) {\n$BODY\n}",
        ("K", "XS", "BODY"),
    ),
    Pattern(
        "return_value",
        "return $EXPR ;",
        "return $EXPR",
        ("EXPR",),
    ),
    Pattern(
        "return_void",
        "return ;",
        "return",
        (),
    ),
    Pattern(
        "break_stmt", "break ;", "break", (),
    ),
    Pattern(
        "continue_stmt", "continue ;", "continue", (),
    ),

    # ---- functions -------------------------------------------------------- #
    Pattern(
        "function_decl_typed",
        "function $NAME ( $PARAMS ) : $RET { $BODY }",
        "func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "function_decl_void",
        "function $NAME ( $PARAMS ) : void { $BODY }",
        "func $NAME($PARAMS): Unit {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "function_decl_no_ret",
        "function $NAME ( $PARAMS ) { $BODY }",
        "func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "arrow_assign_typed",
        "const $NAME = ( $PARAMS ) : $RET => { $BODY } ;",
        "let $NAME = {$PARAMS => \n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "arrow_assign",
        "const $NAME = ( $PARAMS ) => { $BODY } ;",
        "let $NAME = {$PARAMS => \n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),

    # ---- classes / interfaces -------------------------------------------- #
    Pattern(
        "class_decl",
        "class $NAME { $BODY }",
        "open class $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "class_decl_extends",
        "class $NAME extends $BASE { $BODY }",
        "open class $NAME <: $BASE {\n$BODY\n}",
        ("NAME", "BASE", "BODY"),
    ),
    Pattern(
        "class_decl_impl",
        "class $NAME implements $BASE { $BODY }",
        "open class $NAME <: $BASE {\n$BODY\n}",
        ("NAME", "BASE", "BODY"),
    ),
    Pattern(
        "interface_decl",
        "interface $NAME { $BODY }",
        "interface $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),

    # Abstract method declaration in an interface (no body).
    Pattern(
        "iface_method_typed",
        "$NAME ( $PARAMS ) : $RET ;",
        "func $NAME($PARAMS): $RET",
        ("NAME", "PARAMS", "RET"),
    ),
    Pattern(
        "iface_method_void",
        "$NAME ( $PARAMS ) : void ;",
        "func $NAME($PARAMS): Unit",
        ("NAME", "PARAMS"),
    ),
    # ---- class body items ------------------------------------------------ #
    Pattern(
        "field_number",
        "$NAME : number ;",
        "var $NAME: Int64 = 0",
        ("NAME",),
    ),
    Pattern(
        "field_string",
        "$NAME : string ;",
        "var $NAME: String = \"\"",
        ("NAME",),
    ),
    Pattern(
        "field_boolean",
        "$NAME : boolean ;",
        "var $NAME: Bool = false",
        ("NAME",),
    ),
    Pattern(
        "field_typed_with_init",
        "$NAME : $TY = $EXPR ;",
        "var $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "constructor",
        "constructor ( $PARAMS ) { $BODY }",
        "init($PARAMS) {\n$BODY\n}",
        ("PARAMS", "BODY"),
    ),
    Pattern(
        "method_typed",
        "$NAME ( $PARAMS ) : $RET { $BODY }",
        "public open func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "method_void",
        "$NAME ( $PARAMS ) : void { $BODY }",
        "public open func $NAME($PARAMS): Unit {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "method_no_ret",
        "$NAME ( $PARAMS ) { $BODY }",
        "public open func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),

    # ---- expression statement (very generic, low priority) ---------------- #
    Pattern(
        "expr_stmt",
        "$EXPR ;",
        "$EXPR",
        ("EXPR",),
    ),
]


# --------------------------------------------------------------------------- #
#  Token-level mappings (Hopfield memory contents)                            #
# --------------------------------------------------------------------------- #
#
# These are the workhorse of identifier-level translation.  Order is
# unimportant — duplicate keys overwrite earlier values.
TOKEN_MAPPINGS = [
    # primitives / pseudo-types
    ("number", "Int64"),
    ("string", "String"),
    ("boolean", "Bool"),
    ("void", "Unit"),
    ("any", "Any"),
    ("unknown", "Any"),
    ("undefined", "None"),
    ("null", "None"),
    ("true", "true"),
    ("false", "false"),
    # operators that differ
    ("===", "=="),
    ("!==", "!="),
    # popular library methods (used by call-site rewriting)
    ("console.log", "println"),
    ("console.error", "eprintln"),
    ("console.warn", "println"),
    ("Math.floor", "floor"),
    ("Math.ceil", "ceil"),
    ("Math.abs", "abs"),
    ("Math.max", "max"),
    ("Math.min", "min"),
    ("Math.sqrt", "sqrt"),
    ("Math.PI", "3.141592653589793"),
    ("JSON.stringify", "/* JSON.stringify */"),
    # member-name rewrites
    (".length", ".size"),
    (".push", ".append"),
    (".pop", ".popLast"),
    (".toUpperCase", ".toAsciiUpper"),
    (".toLowerCase", ".toAsciiLower"),
    (".toString", ".toString"),
    (".indexOf", ".indexOf"),
    (".includes", ".contains"),
    (".trim", ".trimAscii"),
    (".split", ".split"),
    (".join", ".join"),
]
