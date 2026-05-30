# 学习语料（Kotlin ↔ 仓颉平行片段）

本目录是 kotlin2cj 的**学习数据集**。idea.md 提出「局部规则可以从平行语料中
通过图模式挖掘 / 小样本归纳得到」。我们把每一条局部翻译规则都对应到一组
**最小平行片段对**（Kotlin 片段 → 仓颉片段），规则引擎中的规则即是对这些片段对
所体现的「局部模式」的归纳固化。

> 测试数据集见 `../tests/cases/`（端到端可编译可运行用例）。

每一行：`规则名 | Kotlin 片段 | 仓颉片段`。

## 1. 原子类型映射（atom-type）
| 规则 | Kotlin | 仓颉 |
|------|--------|------|
| type.int | `Int` / `Long` / `Short` / `Byte` | `Int64` |
| type.float | `Double` / `Float` | `Float64` |
| type.bool | `Boolean` | `Bool` |
| type.char | `Char` | `Rune` |
| type.string | `String` | `String` |
| type.list | `MutableList<Int>` | `ArrayList<Int64>` |
| type.map | `MutableMap<String, Int>` | `HashMap<String, Int64>` |
| type.set | `MutableSet<Int>` | `HashSet<Int64>` |

## 2. 变量与字面量（decl / literal）
| 规则 | Kotlin | 仓颉 |
|------|--------|------|
| decl.val | `val x = 1` | `let x = 1` |
| decl.var | `var x = 1` | `var x = 1` |
| decl.typed | `val x: Int = 1` | `let x: Int64 = 1` |
| lit.char | `'A'` | `r'A'` |
| lit.float | `3` (Double 上下文) | `3.0` |

## 3. 表达式传播（expr-propagation）
| 规则 | Kotlin | 仓颉 |
|------|--------|------|
| expr.binary | `a + b` | `a + b` |
| expr.paren | `(a + b) * c` | `(a + b) * c` |
| expr.incr | `i++` | `i += 1` |
| str.template.simple | `"x=$x"` | `"x=${x}"` |
| str.template.expr | `"${a + b}"` | `"${a + b}"` |

## 4. 控制流（control）
| 规则 | Kotlin | 仓颉 |
|------|--------|------|
| range.until | `0 until n` | `0..n` |
| range.closed | `0..n` | `0..=n` |
| range.step | `0..n step 2` | `0..=n : 2` |
| range.down | `n downTo 0` | `n..=0 : -1` |
| ctrl.when | `when (x) { 1 -> a; 2,3 -> b; else -> c }` | `match (x) { case 1 => a; case 2 \| 3 => b; case _ => c }` |
| ctrl.when.cond | `when { c1 -> a; else -> b }` | `if (c1) { a } else { b }` |
| ctrl.foreach | `for (x in xs)` | `for (x in xs)` |

## 5. 集合（collection）
| 规则 | Kotlin | 仓颉 |
|------|--------|------|
| coll.list | `mutableListOf(1, 2, 3)` | `ArrayList([1, 2, 3])` |
| coll.list.empty | `mutableListOf<Int>()` | `ArrayList<Int64>()` |
| coll.map | `mutableMapOf("a" to 1)` | `HashMap([("a", 1)])` |
| coll.set | `setOf(1, 2)` | `HashSet([1, 2])` |
| coll.size | `xs.size` | `xs.size` |
| str.size | `s.length` | `s.size` |
| str.upper | `s.uppercase()` | `s.toAsciiUpper()` |

## 6. 函数与类（decl-fn / decl-class）
| 规则 | Kotlin | 仓颉 |
|------|--------|------|
| fn.def | `fun add(a: Int, b: Int): Int { ... }` | `func add(a: Int64, b: Int64): Int64 { ... }` |
| fn.expr | `fun sq(n: Int) = n * n` | `func sq(n: Int64) { return n * n }` |
| fn.main | `fun main() { ... }` | `main() { ... }` |
| class.ctor | `class P(val x: Int, var y: Int)` | `class P { let x: Int64; var y: Int64; init(x: Int64, y: Int64) { this.x = x; this.y = y } }` |
| class.new | `P(3, 4)` | `P(3, 4)` |

## 7. 关键字转义（keyword-escape）— 命名冲突崩塌
| 规则 | Kotlin | 仓颉 |
|------|--------|------|
| name.escape | `val match = 1` | `` let `match` = 1 `` |

> 该规则即 idea.md 中「类型/命名一致性崩塌」：声明节点选定转义名后，
> 其全部引用节点沿依赖边级联更新（见 `--demo-avalanche`）。
