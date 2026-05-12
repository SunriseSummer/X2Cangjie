"""Built-in Swift → Cangjie translation patterns.

Each :class:`Pattern` is a pair (Swift template, Cangjie template) plus an
optional ordered tuple of slot names.  ``$NAME`` markers denote *slots*;
literal tokens act as anchors during non-linear slot binding.

Swift's syntax differs from TypeScript in a number of ways that drive the
patterns below:

* ``if`` / ``while`` / ``for`` conditions are **un-parenthesised** in Swift —
  the templates here therefore *omit* parens around ``$COND`` and the Cangjie
  template **adds** them in the rendered output.
* Constructors use the ``init(...)`` keyword (vs ``constructor`` in TS).
* Class inheritance uses ``:`` (Cangjie's ``<:``).
* Range operators ``..<`` / ``...`` are lexed as single tokens.
* String interpolation uses ``\\(expr)`` — handled by a dedicated post-pass.

Patterns are written with Swift-flavoured pseudo-source so their hashing-trick
embeddings naturally cluster near real Swift inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Pattern:
    name: str
    swift_template: str
    cj_template: str
    slots: tuple = ()


# --------------------------------------------------------------------------- #
#  Chunk patterns                                                             #
# --------------------------------------------------------------------------- #
CHUNK_PATTERNS: List[Pattern] = [
    # ---- typealias -------------------------------------------------------- #
    Pattern(
        "typealias_decl",
        "typealias $NAME = $TY",
        "type $NAME = $TY",
        ("NAME", "TY"),
    ),

    # ---- import ----------------------------------------------------------- #
    Pattern(
        "import_decl",
        "import $NAME",
        "",  # Swift module imports have no Cangjie analogue — drop.
        ("NAME",),
    ),

    # ---- variable declarations -------------------------------------------- #
    Pattern(
        "let_typed_init",
        "let $NAME : $TY = $EXPR",
        "let $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "var_typed_init",
        "var $NAME : $TY = $EXPR",
        "var $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "let_inferred",
        "let $NAME = $EXPR",
        "let $NAME = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "var_inferred",
        "var $NAME = $EXPR",
        "var $NAME = $EXPR",
        ("NAME", "EXPR"),
    ),
    Pattern(
        "var_typed_no_init",
        "var $NAME : $TY",
        "var $NAME: $TY = $DEFAULT",
        ("NAME", "TY"),
    ),
    Pattern(
        "let_typed_no_init",
        "let $NAME : $TY",
        "let $NAME: $TY = $DEFAULT",
        ("NAME", "TY"),
    ),

    # ---- IO / printing ---------------------------------------------------- #
    Pattern(
        "print_call",
        "print ( $EXPR )",
        "println($EXPR)",
        ("EXPR",),
    ),

    # ---- control flow ----------------------------------------------------- #
    # NOTE: Swift conditions have NO parens; templates add them at emit time.
    Pattern(
        "if_eif_else_block",
        "if $C1 { $B1 } else if $C2 { $B2 } else { $B3 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n} else {\n$B3\n}",
        ("C1", "B1", "C2", "B2", "B3"),
    ),
    Pattern(
        "if_eif_block",
        "if $C1 { $B1 } else if $C2 { $B2 }",
        "if ($C1) {\n$B1\n} else if ($C2) {\n$B2\n}",
        ("C1", "B1", "C2", "B2"),
    ),
    Pattern(
        "if_else_block",
        "if $COND { $A } else { $B }",
        "if ($COND) {\n$A\n} else {\n$B\n}",
        ("COND", "A", "B"),
    ),
    Pattern(
        "if_block",
        "if $COND { $BODY }",
        "if ($COND) {\n$BODY\n}",
        ("COND", "BODY"),
    ),
    Pattern(
        "while_block",
        "while $COND { $BODY }",
        "while ($COND) {\n$BODY\n}",
        ("COND", "BODY"),
    ),
    Pattern(
        "repeat_while",
        "repeat { $BODY } while $COND",
        "do {\n$BODY\n} while ($COND)",
        ("BODY", "COND"),
    ),
    # Range-based for: ``for i in 0..<n { ... }``  (half-open).
    Pattern(
        "for_range_half",
        "for $I in $START ..< $END { $BODY }",
        "for ($I in $START..$END) {\n$BODY\n}",
        ("I", "START", "END", "BODY"),
    ),
    # Range-based for: ``for i in 0...n { ... }``  (closed).
    Pattern(
        "for_range_closed",
        "for $I in $START ... $END { $BODY }",
        "for ($I in $START..=$END) {\n$BODY\n}",
        ("I", "START", "END", "BODY"),
    ),
    # Collection iteration: ``for x in xs { ... }``.
    Pattern(
        "for_in",
        "for $I in $XS { $BODY }",
        "for ($I in $XS) {\n$BODY\n}",
        ("I", "XS", "BODY"),
    ),
    Pattern(
        "return_value",
        "return $EXPR",
        "return $EXPR",
        ("EXPR",),
    ),
    Pattern(
        "return_void", "return", "return", (),
    ),
    Pattern(
        "break_stmt", "break", "break", (),
    ),
    Pattern(
        "continue_stmt", "continue", "continue", (),
    ),

    # ---- exceptions ------------------------------------------------------- #
    Pattern(
        "throw_stmt",
        "throw $EXPR",
        "throw $EXPR",
        ("EXPR",),
    ),
    Pattern(
        "do_catch",
        "do { $BODY } catch { $CBODY }",
        "try {\n$BODY\n} catch (e: Exception) {\n$CBODY\n}",
        ("BODY", "CBODY"),
    ),
    Pattern(
        "do_catch_bind",
        "do { $BODY } catch $E { $CBODY }",
        "try {\n$BODY\n} catch (e: Exception) {\n$CBODY\n}",
        ("BODY", "E", "CBODY"),
    ),

    # ---- switch / match --------------------------------------------------- #
    # Swift ``switch`` body is irregular — caught here as a single slot
    # and re-processed by :func:`converter._convert_switch_body`.
    Pattern(
        "switch_block",
        "switch $EXPR { $BODY }",
        "match ($EXPR) {\n$SWBODY\n}",
        ("EXPR", "BODY"),
    ),

    # ---- functions -------------------------------------------------------- #
    Pattern(
        "function_typed",
        "func $NAME ( $PARAMS ) -> $RET { $BODY }",
        "func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "function_throws_typed",
        "func $NAME ( $PARAMS ) throws -> $RET { $BODY }",
        "func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "function_no_ret",
        "func $NAME ( $PARAMS ) { $BODY }",
        "func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "function_throws_no_ret",
        "func $NAME ( $PARAMS ) throws { $BODY }",
        "func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    # Generic function.
    Pattern(
        "function_generic_typed",
        "func $NAME < $TPARAMS > ( $PARAMS ) -> $RET { $BODY }",
        "func $NAME<$TPARAMS>($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "TPARAMS", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "function_generic_no_ret",
        "func $NAME < $TPARAMS > ( $PARAMS ) { $BODY }",
        "func $NAME<$TPARAMS>($PARAMS) {\n$BODY\n}",
        ("NAME", "TPARAMS", "PARAMS", "BODY"),
    ),

    # ---- enum ------------------------------------------------------------- #
    Pattern(
        "enum_decl",
        "enum $NAME { $BODY }",
        "enum $NAME {\n$ENUMBODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "enum_raw_decl",
        "enum $NAME : $BASE { $BODY }",
        "enum $NAME {\n$ENUMBODY\n}",
        ("NAME", "BASE", "BODY"),
    ),

    # ---- struct / class / protocol --------------------------------------- #
    Pattern(
        "struct_decl",
        "struct $NAME { $BODY }",
        "struct $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "struct_impl_decl",
        "struct $NAME : $BASE { $BODY }",
        "struct $NAME <: $BASE {\n$BODY\n}",
        ("NAME", "BASE", "BODY"),
    ),
    Pattern(
        "class_decl",
        "class $NAME { $BODY }",
        "open class $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "class_decl_inherit",
        "class $NAME : $BASE { $BODY }",
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
        "class_generic_decl_inherit",
        "class $NAME < $TPARAMS > : $BASE { $BODY }",
        "open class $NAME<$TPARAMS> <: $BASE {\n$BODY\n}",
        ("NAME", "TPARAMS", "BASE", "BODY"),
    ),
    Pattern(
        "protocol_decl",
        "protocol $NAME { $BODY }",
        "interface $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "protocol_decl_inherit",
        "protocol $NAME : $BASE { $BODY }",
        "interface $NAME <: $BASE {\n$BODY\n}",
        ("NAME", "BASE", "BODY"),
    ),

    # Extension is mapped to an ``extend`` block (Cangjie 1.x supports
    # ``extend Type { ... }``).  Body methods are converted using the
    # regular class-body machinery.
    Pattern(
        "extension_decl",
        "extension $NAME { $BODY }",
        "extend $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),

    # ---- class body items ------------------------------------------------ #
    # Field with explicit type + default.
    Pattern(
        "field_var_typed_with_init",
        "var $NAME : $TY = $EXPR",
        "var $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "field_let_typed_with_init",
        "let $NAME : $TY = $EXPR",
        "let $NAME: $TY = $EXPR",
        ("NAME", "TY", "EXPR"),
    ),
    Pattern(
        "field_var_typed",
        "var $NAME : $TY",
        "var $NAME: $TY = $DEFAULT",
        ("NAME", "TY"),
    ),
    Pattern(
        "field_let_typed",
        "let $NAME : $TY",
        "let $NAME: $TY = $DEFAULT",
        ("NAME", "TY"),
    ),

    # Initialiser (``init(...)``).
    Pattern(
        "init_decl",
        "init ( $PARAMS ) { $BODY }",
        "public init($PARAMS) {\n$BODY\n}",
        ("PARAMS", "BODY"),
    ),
    Pattern(
        "public_init_decl",
        "public init ( $PARAMS ) { $BODY }",
        "public init($PARAMS) {\n$BODY\n}",
        ("PARAMS", "BODY"),
    ),
    Pattern(
        "init_throws_decl",
        "init ( $PARAMS ) throws { $BODY }",
        "public init($PARAMS) {\n$BODY\n}",
        ("PARAMS", "BODY"),
    ),
    Pattern(
        "override_init_decl",
        "override init ( $PARAMS ) { $BODY }",
        "public init($PARAMS) {\n$BODY\n}",
        ("PARAMS", "BODY"),
    ),
    Pattern(
        "convenience_init_decl",
        "convenience init ( $PARAMS ) { $BODY }",
        "public init($PARAMS) {\n$BODY\n}",
        ("PARAMS", "BODY"),
    ),

    # ---- method declarations (within classes/structs/protocols) ---------- #
    Pattern(
        "method_typed",
        "func $NAME ( $PARAMS ) -> $RET { $BODY }",
        "public open func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "method_throws_typed",
        "func $NAME ( $PARAMS ) throws -> $RET { $BODY }",
        "public open func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "method_no_ret",
        "func $NAME ( $PARAMS ) { $BODY }",
        "public open func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "method_throws_no_ret",
        "func $NAME ( $PARAMS ) throws { $BODY }",
        "public open func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "method_generic_typed",
        "func $NAME < $TPARAMS > ( $PARAMS ) -> $RET { $BODY }",
        "public open func $NAME<$TPARAMS>($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "TPARAMS", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "static_method_typed",
        "static func $NAME ( $PARAMS ) -> $RET { $BODY }",
        "public static func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "static_method_no_ret",
        "static func $NAME ( $PARAMS ) { $BODY }",
        "public static func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "private_method_typed",
        "private func $NAME ( $PARAMS ) -> $RET { $BODY }",
        "private func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "private_method_no_ret",
        "private func $NAME ( $PARAMS ) { $BODY }",
        "private func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    Pattern(
        "override_method_typed",
        "override func $NAME ( $PARAMS ) -> $RET { $BODY }",
        "public open override func $NAME($PARAMS): $RET {\n$BODY\n}",
        ("NAME", "PARAMS", "RET", "BODY"),
    ),
    Pattern(
        "override_method_no_ret",
        "override func $NAME ( $PARAMS ) { $BODY }",
        "public open override func $NAME($PARAMS) {\n$BODY\n}",
        ("NAME", "PARAMS", "BODY"),
    ),
    # Protocol method declaration: ``func foo() -> T`` (no body).
    Pattern(
        "proto_method_typed",
        "func $NAME ( $PARAMS ) -> $RET",
        "func $NAME($PARAMS): $RET",
        ("NAME", "PARAMS", "RET"),
    ),
    Pattern(
        "proto_method_no_ret",
        "func $NAME ( $PARAMS )",
        "func $NAME($PARAMS): Unit",
        ("NAME", "PARAMS"),
    ),

    # ---- final / open class variants ------------------------------------- #
    Pattern(
        "final_class_decl",
        "final class $NAME { $BODY }",
        "class $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),
    Pattern(
        "final_class_decl_inherit",
        "final class $NAME : $BASE { $BODY }",
        "class $NAME <: $BASE {\n$BODY\n}",
        ("NAME", "BASE", "BODY"),
    ),
    Pattern(
        "public_class_decl",
        "public class $NAME { $BODY }",
        "public open class $NAME {\n$BODY\n}",
        ("NAME", "BODY"),
    ),

    # ---- expression statement (very generic, low priority) ---------------- #
    Pattern(
        "expr_stmt",
        "$EXPR",
        "$EXPR",
        ("EXPR",),
    ),
]


# --------------------------------------------------------------------------- #
#  Token-level mappings (Hopfield memory contents)                            #
# --------------------------------------------------------------------------- #
TOKEN_MAPPINGS = [
    # primitive type names — Swift → Cangjie
    ("Int", "Int64"),
    ("Int64", "Int64"),
    ("Int32", "Int32"),
    ("Int16", "Int16"),
    ("Int8", "Int8"),
    ("UInt", "UInt64"),
    ("UInt64", "UInt64"),
    ("UInt32", "UInt32"),
    ("Double", "Float64"),
    ("Float", "Float32"),
    ("Float64", "Float64"),
    ("Bool", "Bool"),
    ("String", "String"),
    ("Character", "Rune"),
    ("Void", "Unit"),
    ("Any", "Any"),
    # nil sentinel
    ("nil", "None"),
    ("true", "true"),
    ("false", "false"),
    # I/O / runtime helpers
    ("print", "println"),
    # exception
    ("Error", "Exception"),
    # collection methods
    (".count", ".size"),
    (".append", ".add"),
    (".isEmpty", ".isEmpty()"),
    (".uppercased", ".toAsciiUpper"),
    (".lowercased", ".toAsciiLower"),
    (".contains", ".contains"),
]
