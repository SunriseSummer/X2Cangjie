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
    # ---- imports / type aliases ------------------------------------------ #
    Pattern(
        "type_alias",
        "type $NAME = $TY ;",
        "type $NAME = $TY",
        ("NAME", "TY"),
    ),

    # ---- variable declarations -------------------------------------------- #
    Pattern(
        "const_number",
        "const $NAME : number = $EXPR ;",
        "let $NAME: Int64 = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_float",
        "const $NAME : Float64 = $EXPR ;",
        "let $NAME: Float64 = $EXPR",
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
        "let_float",
        "let $NAME : Float64 = $EXPR ;",
        "var $NAME: Float64 = $EXPR",
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
        "let_boolean",
        "let $NAME : boolean = $EXPR ;",
        "var $NAME: Bool = $EXPR",
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
        "let_array_number",
        "let $NAME : number [ ] = $EXPR ;",
        "var $NAME: ArrayList<Int64> = ArrayList<Int64>($EXPR)",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "let_array_string",
        "let $NAME : string [ ] = $EXPR ;",
        "var $NAME: ArrayList<String> = ArrayList<String>($EXPR)",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "const_typed",
        "const $NAME : $TY = $EXPR ;",
        "let $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "let_typed",
        "let $NAME : $TY = $EXPR ;",
        "var $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
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
    Pattern(
        "console_warn",
        "console . warn ( $EXPR ) ;",
        "println($EXPR)",
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
        "do_while_block",
        "do { $BODY } while ( $COND ) ;",
        "do {\n$BODY\n} while ($COND)",
        ("BODY", "COND"),
    ),
    Pattern(
        "for_classic",
        "for ( let $I = $START ; $I < $END ; $I ++ ) { $BODY }",
        "for ($I in $START..$END) {\n$BODY\n}",
        ("I", "START", "END", "BODY"),
    ),
    Pattern(
        "for_classic_le",
        "for ( let $I = $START ; $I <= $END ; $I ++ ) { $BODY }",
        "for ($I in $START..=$END) {\n$BODY\n}",
        ("I", "START", "END", "BODY"),
    ),
    Pattern(
        "for_classic_var",
        "for ( var $I = $START ; $I < $END ; $I ++ ) { $BODY }",
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
        "for_of_let",
        "for ( let $I of $XS ) { $BODY }",
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

    # ---- exceptions ------------------------------------------------------- #
    Pattern(
        "throw_stmt",
        "throw $EXPR ;",
        "throw $EXPR",
        ("EXPR",),
    ),
    Pattern(
        "try_catch_finally",
        "try { $BODY } catch ( $E ) { $CBODY } finally { $FBODY }",
        "try {\n$BODY\n} catch (e: Exception) {\n$CBODY\n} finally {\n$FBODY\n}",
        ("BODY", "E", "CBODY", "FBODY"),
    ),
    Pattern(
        "try_catch",
        "try { $BODY } catch ( $E ) { $CBODY }",
        "try {\n$BODY\n} catch (e: Exception) {\n$CBODY\n}",
        ("BODY", "E", "CBODY"),
    ),
    Pattern(
        "try_finally",
        "try { $BODY } finally { $FBODY }",
        "try {\n$BODY\n} finally {\n$FBODY\n}",
        ("BODY", "FBODY"),
    ),

    # ---- switch / match --------------------------------------------------- #
    # NOTE: switch bodies have a non-balanced structure (case labels) that the
    # token-level slot binder cannot decompose cleanly.  We therefore catch
    # the whole switch as a single $BODY slot and re-process the body with a
    # dedicated helper in :mod:`converter`.
    Pattern(
        "switch_block",
        "switch ( $EXPR ) { $BODY }",
        "match ($EXPR) {\n$SWBODY\n}",
        ("EXPR", "BODY"),
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
    # Generic function (single type parameter, common shape).
    Pattern(
        "function_generic_typed",
        "function $NAME < $TPARAMS > ( $PARAMS ) : $RET { $BODY }",
        "func $NAME<$TPARAMS>($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "TPARAMS", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "function_generic_void",
        "function $NAME < $TPARAMS > ( $PARAMS ) : void { $BODY }",
        "func $NAME<$TPARAMS>($PARAMS): Unit {\n$BODY\n}",
        ("NAME", "TPARAMS", "PARAMS", "BODY"),
    ),

    # Arrow-function assignment.  Cangjie lambdas use `{ params => expr }`.
    Pattern(
        "arrow_assign_expr",
        "const $NAME = ( $PARAMS ) => $EXPR ;",
        "let $NAME = { $LAMBDA_PARAMS => $EXPR }",
        ("NAME", "PARAMS", "EXPR"),
    ),
    Pattern(
        "arrow_assign_block",
        "const $NAME = ( $PARAMS ) => { $BODY } ;",
        "let $NAME = { $LAMBDA_PARAMS =>\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "arrow_assign_typed_block",
        "const $NAME = ( $PARAMS ) : $RET => { $BODY } ;",
        "let $NAME = { $LAMBDA_PARAMS =>\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "arrow_assign_let_expr",
        "let $NAME = ( $PARAMS ) => $EXPR ;",
        "var $NAME = { $LAMBDA_PARAMS => $EXPR }",
        ("NAME", "PARAMS", "EXPR"),
    ),

    # ---- enum ------------------------------------------------------------- #
    # TS enum maps to Cangjie enum.  Bodies handled by helper.
    Pattern(
        "enum_decl",
        "enum $NAME { $BODY }",
        "enum $NAME {\n$ENUMBODY\n}",
        ("NAME", "ENUMBODY"),
    ),

    # ---- struct / class / interface -------------------------------------- #
    Pattern(
        "struct_decl",
        "struct $NAME { $BODY }",
        "struct $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
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
        "class_generic_decl",
        "class $NAME < $TPARAMS > { $BODY }",
        "open class $NAME<$TPARAMS> {\n$BODY\n}",
        ("NAME", "TPARAMS", "BODY"),
    ),
    Pattern(
        "class_generic_decl_extends",
        "class $NAME < $TPARAMS > extends $BASE { $BODY }",
        "open class $NAME<$TPARAMS> <: $BASE {\n$BODY\n}",
        ("NAME", "TPARAMS", "BASE", "BODY"),
    ),
    Pattern(
        "abstract_class_decl",
        "abstract class $NAME { $BODY }",
        "abstract class $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "interface_decl",
        "interface $NAME { $BODY }",
        "interface $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "interface_generic_decl",
        "interface $NAME < $TPARAMS > { $BODY }",
        "interface $NAME<$TPARAMS> {\n$BODY\n}",
        ("NAME", "TPARAMS", "BODY"),
    ),
    Pattern(
        "interface_decl_extends",
        "interface $NAME extends $BASE { $BODY }",
        "interface $NAME <: $BASE {\n$BODY\n}",
        ("NAME", "BASE", "BODY"),
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
    # Default method body in interface — same surface form as a class method.
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
        "field_typed_no_init",
        "$NAME : $TY ;",
        "var $NAME: $TY",
        ("NAME", "TY"),
    ),
    Pattern(
        "field_readonly_typed_with_init",
        "readonly $NAME : $TY = $EXPR ;",
        "let $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "private_field_typed_with_init",
        "private $NAME : $TY = $EXPR ;",
        "private var $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "static_field_typed_with_init",
        "static $NAME : $TY = $EXPR ;",
        "public static let $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "constructor",
        "constructor ( $PARAMS ) { $BODY }",
        "public init($PARAMS) {\n$BODY\n}",
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
    Pattern(
        "method_generic_typed",
        "$NAME < $TPARAMS > ( $PARAMS ) : $RET { $BODY }",
        "public open func $NAME<$TPARAMS>($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "TPARAMS", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "static_method_typed",
        "static $NAME ( $PARAMS ) : $RET { $BODY }",
        "public static func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "static_method_void",
        "static $NAME ( $PARAMS ) : void { $BODY }",
        "public static func $NAME($PARAMS): Unit {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "private_method_typed",
        "private $NAME ( $PARAMS ) : $RET { $BODY }",
        "private func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "private_method_void",
        "private $NAME ( $PARAMS ) : void { $BODY }",
        "private func $NAME($PARAMS): Unit {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    # Abstract methods inside an `abstract class` (TS: `abstract foo(): T;`).
    Pattern(
        "abstract_method_typed",
        "abstract $NAME ( $PARAMS ) : $RET ;",
        "public func $NAME($PARAMS): $RET",
        ("NAME", "PARAMS", "RET"),
    ),
    Pattern(
        "abstract_method_void",
        "abstract $NAME ( $PARAMS ) : void ;",
        "public func $NAME($PARAMS): Unit",
        ("NAME", "PARAMS"),
    ),
    # TS getter/setter — we deliberately do NOT match these.  Converting
    # ``get foo(): T { ... }`` to a Cangjie ``prop`` requires also merging
    # any corresponding setter (a cross-chunk operation) so we leave it
    # to the downstream AI pass.  ``get`` and ``set`` used as plain method
    # names fall through to the regular ``method_typed`` patterns.

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
    ("Math.E", "2.718281828459045"),
    ("JSON.stringify", "/* JSON.stringify */"),
    # collection constructors
    ("Map", "HashMap"),
    ("Set", "HashSet"),
    # error / runtime
    ("Error", "Exception"),
    # member-name rewrites
    (".length", ".size"),
    (".push", ".add"),
    (".toUpperCase", ".toAsciiUpper"),
    (".toLowerCase", ".toAsciiLower"),
    (".toString", ".toString"),
    (".indexOf", ".indexOf"),
    (".includes", ".contains"),
    (".trim", ".trimAscii"),
    (".split", ".split"),
    (".join", ".join"),
]
