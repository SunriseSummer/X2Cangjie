# kotlin2cj 现状评估与下一步规划

> 本文给出 kotlin2cj（Kotlin → 仓颉源到源翻译器）截至当前迭代的能力评估、
> 测试现状、已知边界与后续路线图。配套基线见 [`tests/log.md`](./tests/log.md)，
> 支持的语言子集见 [`Readme.md`](./Readme.md)。

## 1. 一句话现状

kotlin2cj 已从「基础语法演示」推进到「**可翻译并端到端跑通中大规模实用 Kotlin
程序（千行级单文件）**」的阶段：覆盖控制流、函数（含嵌套/递归/**默认参数**）、类（含继承/`sealed`/
**接口/抽象类/用户泛型类**/`data class` 自动 `toString`）、枚举、集合、异常、位运算、区间成员检查、`is` 类型判定、解构声明、
`?.` 安全调用、`maxOf/minOf`、**返回集合的链式高阶（`map/filter/sorted/fold/reduce` 等）**、
**`when (x) { in 区间 -> }` 区间分支**、**字符串与非字符串 `+` 拼接**、**字符级访问与字符算术**、可空 `if (x != null)` 智能转换
及常见空安全惯用法等特性，**85 个端到端用例全部翻译 → `cjc` 编译 → 运行输出逐字节匹配（85/85/85）**，
其中含 1 个 **1068 行**与 3 个 200–310 行的大规模综合程序（综合工具箱、电商订单、成绩册、银行模拟）。
State.md 路线图中的 **P0 与 P1 已完成**。

## 2. 测试现状

| 指标 | 数值 |
|------|------|
| 端到端用例总数 | 85 |
| 翻译成功 | 85/85 |
| 仓颉 `cjc` 编译通过 | 85/85 |
| 运行输出匹配 | 85/85 |
| 大规模用例 | 用例 85 为 **1068 行**综合工具箱；82–84 为 213/222/310 行综合程序（订单/成绩册/银行） |
| 泛化抽样（未训练的新程序） | 累计 17/19 通过（详见 §3.2） |
| 验证工具链 | Cangjie SDK 1.0.5（cjnative，x86_64-linux）；用例期望值由 `kotlinc` 实编译运行产出 |

用例覆盖维度：

- **基础与控制流**：变量、运算符、`if/when/while/do-while/repeat/for`、`break/continue`、嵌套循环。
- **区间与成员**：`..`/`until`/`downTo`/`step`、`in`/`!in`（区间转比较、集合转 `contains`）。
- **函数**：块体/表达式体、递归、嵌套局部函数、顶层全局 `val`、`maxOf/minOf`、**默认参数**（→ 仓颉具名可选形参 + 调用端补名）、**函数类型 `(A,B)->R` 与高阶函数值**。
- **集合**：List/Map/Set 字面量与泛型、`ArrayList/HashMap/HashSet` 构造器、下标读写、嵌套集合、`forEach`、`map[k] ?: d`、`?.` 安全调用链、**函数式链式高阶 `map/filter/sorted/sortedBy/reversed/fold/reduce/sum/count/any/all/joinToString`**。
- **类型抽象**：类（主构造器/方法/多类协作/继承）、**接口 `interface`**、**抽象类 `abstract class` + `super(...)`**、**用户泛型容器类 `class Stack<T>`**、`sealed class` + `when (x) { is T -> }`、`data class`（**自动 `toString`**）、`enum class`（+`@Derive[Equatable]` 与自定义 `toString`）、解构声明 `val (a, b) = p`。
- **区间/关系分支**：`when (x) { in 90..100 -> ...; !in 0..100 -> ... }` → if-else 链。
- **规模**：用例 85 为 **1068 行**综合工具箱（数论/字符串/排序/矩阵/接口与抽象类多态/泛型栈与队列/枚举状态机/数据类/函数式链/RPN）；82–84 为 213/222/310 行综合程序（电商订单、成绩册、银行+库存+文本处理），覆盖多类协作、嵌套可空智能转换、默认参数、`when in`、数据类 `toString`、函数式链、质数/斐波那契/GCD 等。
- **异常**：`try/catch/finally`、`throw`。
- **位运算与字面量**：`and/or/xor/shl/shr`、`0x`/`0b`/下划线数字字面量。
- **字符串**：`for (c in s)` 逐字符遍历（改写为 `.runes()` 得 Rune）、`length/uppercase/contains/substring` 等方法映射。
- **规模**：筛法（50 以内素数）、Collatz 最长链、3×3 网格与分组映射、库存/状态机、RPN 求值、词频统计、泛型栈、成绩分级、扑克牌综合（枚举+数据类+多类+函数式链）等综合程序。

运行方式：

```bash
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh
cd kotlin2cj && python3 tests/run_tests.py   # 结果写入 tests/log.md
```

## 3. 本轮新增能力

### 3.1 新增语言特性（完成 P0 + P1）

相对上一基线（69/69），本轮在原有位运算/区间成员/异常/`forEach`/枚举/全局 `val`/嵌套函数/
数字字面量/`is` 判定/解构/`?.` 安全调用基础上，**收尾 P1**，重点补齐「返回集合的链式高阶」：

1. **函数式集合链**（P1 收尾，核心难点）：`xs.map{}/filter{}` → `collectArrayList(xs.iterator()....)`（即时求值，
   元素类型由仓颉 `collectArrayList` 推断，无需显式 `<T>`）；`sum/sumOf/fold/reduce/count/any/all/none/max/min/
   maxOrNull/minOrNull` → 对应 `iterator()` 聚合（`fold<T>` 注入字面量类型、`reduce` 取 `getOrThrow()/?? d`）；
   `joinToString { it -> ... }` 带 transform → `String.join`。**保守守卫**：仅当接收者「不可证明为非集合」时改写，
   用户类的同名方法（如 `Library.count()`）、标量、字符串均被排除，循环变量与 `map.values` 视图等未知类型放行。
2. **排序与转换链**：`sorted/sortedDescending/sortedBy/sortedByDescending/reversed/toList/toMutableList`
   → 借助 `std.sort` 的就地 `sort` 以 IIFE 拷贝-排序-返回的方式实现（不改原集合，匹配 Kotlin 语义）。
3. **枚举 `toString`**：`enum class` 渲染 `<: ToString` 并生成 `match` 分支，使 `println(e)` 输出裸名
   （`ADD` 而非 `Op.ADD`），与 Kotlin 一致；与 `@Derive[Equatable]` 共存。
4. **字符串逐字符遍历**：`for (c in s)` 改写为遍历 `s.runes()`，得到 `Rune`（而非仓颉默认逐字节产出的 `UInt8`），
   使 `c == 'a'` 等字符比较成立。

实现仍遵循原有 SOC（自组织临界）管线：词法 → 递归下降建图 → worklist 松弛渲染，
新特性以局部渲染规则 + 轻量类型解析辅助（`expr_type_name`/`provably_non_collection`/`looks_string` 等启发式）的方式接入，
未改动核心引擎。

### 3.3 本轮（大规模单文件打磨）新增能力

本轮聚焦「**500–2000 行级单文件**」的翻译鲁棒性与产物质量，全部为**通用规则**（非用例硬编码），
新增能力均以局部渲染规则 + 轻量类型启发式接入，未改 SOC 核心引擎：

1. **默认参数**：Kotlin `fun f(a: Int, b: Int = 1)` → 仓颉具名可选形参 `b!: Int64 = 1`，
   并在**调用端按声明自动补名**（`f(5, 3)` → `f(5, b: 3)`，省略实参 `f(5)` 沿用默认值）。
2. **`data class` 自动 `toString`**：渲染 `<: ToString` 并生成 `Name(f1=${this.f1}, ...)`，
   对齐 Kotlin 自动 `toString`（`println(p)`、集合内逐元素打印一致）；已有用户 `toString` 则不重复生成。
3. **主语 `when` 的区间/关系分支**：`when (x) { in 90..100 -> ...; !in 0..100 -> ...; else -> }`
   → 对主语取条件的 if-else 链（仓颉 `match` 无法表达区间/关系分支），逗号多模式以 `||` 合并。
4. **字符串拼接补全**：`"a" + 1 + x` 等 String 与非 String 混合 `+` 自动对非字符串侧补 `.toString()`，
   并对拼接结果递归识别为字符串（支持多级级联）。
5. **可空 `if (x != null)` 智能转换**：`if (x != null) { ...x... }` → `if (let Some(x) <- x) { ... }`，
   支持嵌套；**保守守卫**：若分支体内对该变量再赋值则回退普通条件，避免 if-let 不可变绑定破坏语义。
6. **高阶函数值与函数类型**：解析 `(A, B) -> R` 函数类型与带类型的 lambda 形参 `{ n: Int -> ... }`，
   支持把函数作为参数传入（`fun transform(xs, f: (Int) -> Int)`）。
7. **更多集合/Map/数值惯用法**：`containsKey`/`getOrDefault`、就地 `sort/sortDescending/sortBy(...)`
   → `std.sort` 全局 `sort(...)`、`addAll` → `add(all:)`、`withIndex`、`average`、`firstOrNull/lastOrNull`、
   `.indices`/`.lastIndex`、Pair `.first/.second/.third` → 元组下标、`for ((k,v) in map)`、`forEachIndexed`、
   算术中 `Int↔Float` 单侧自动 `Float64(...)` 提升、顶层 `package`/`import` 跳过。

### 3.4 本轮（1000 行级单文件强化）新增能力

本轮在 §3.3 基础上继续打磨「**1000 行以上单文件**」翻译，新增能力同样为**通用规则**（非用例硬编码），
均以局部渲染规则 + 轻量类型启发式接入，未改 SOC 核心引擎：

1. **接口与抽象类**：`interface Name { fun f(): T }` → 仓颉 `interface`（成员默认 public）；
   `abstract class A(...) { abstract fun g(): T; fun h() = ... }` → 仓颉 `abstract class`（抽象方法 `public func` 签名）；
   实现/继承方法的 `override` → `public func`，`A(name) : Animal(name)` 生成 `super(name)` 构造调用。
2. **用户泛型容器类**：`class Stack<T> { ... }`、`class Queue<T> { ... }` → 仓颉 `class Stack<T>`；
   泛型构造调用 `Stack<Int>()` 经平衡尖括号前瞻识别，避免与 `a < b` 比较歧义。
3. **字符与字符串字符级访问**：字符串 `s[i]`（接收者可证明为字符串时）→ `s.toRuneArray()[i]` 得 `Rune`；
   字符算术 `c - '0'`/`c + n` → `Int64(UInt32(c))` 码点运算；`Char.code` → 码点、`Int.toChar()` → `Rune(UInt32(n))`；
   字符判定 `isDigit/isLetter/isWhitespace/isUpperCase/isLowerCase/isLetterOrDigit` → Rune 的 `isAscii*` 方法。
4. **更多集合/字符串惯用法**：列表 `take/drop` → 迭代器 `take(n)`/`skip(n)`；字符串 `take/drop/repeat` → 切片与 `*`；
   `padStart/padEnd(len, char)` → 仓颉 `padding:` 具名（字符转字符串）；`joinToString(sep, prefix, postfix)` 支持前后缀；
   `repeat(n) { it }` 的索引 `it` 正确绑定；遍历「元组列表」时循环变量识别为元组（`p.first/.second` → 下标）。
5. **数值转换分流增强**：`x.toInt()/toLong()` 当接收者为返回数值的用户函数调用时走类型构造转换 `Int64(...)`
   （而非字符串 `parse`），覆盖 `power(...).toInt()` 等链式场景。

### 3.2 泛化能力评估（未训练新程序）

为避免「只对已有用例过拟合」，分两批撰写**不在测试集**的新程序，用 `kotlinc` 实编译运行得到
基准输出，再经 kotlin2cj 翻译 → `cjc` 编译 → 运行比对：

- **批次一（6 个，前轮）**：枚举运算、回文、数据类分组、`sealed` 树深度、位运算等 → **6/6 通过**
  （前轮失败的可空链表 g1 仍受流敏感限制制约，未计入）。
- **批次二（8 个，本轮）**：矩阵 trace+逐行 `joinToString`、map `values.sum()`、字符串元音统计、
  函数式管线、分析聚合等 → **7/8 通过**；唯一失败为「`maxOrNull/minOrNull` 直接打印」时 Option 显示
  `Some(1)`（Kotlin 显示 `1`/`null`）——为支持高频的 `?: default` 级联，刻意保留 Option 包装，属取舍而非缺陷。
- 其中矩阵（p2）、map 视图（p5）、字符串扫描（p7）三个程序及一个约 60 行的扑克牌综合程序（枚举+数据类+
  多类+函数式链+分组+字符频次）经验证后已**固化为正式用例 78–81**。
- **批次三（4 个，本轮，大规模）**：电商订单域（~213 行）、成绩册（~222 行，含默认参数/`when in`/数据类
  `toString`/HOF）、银行+库存+文本处理模拟（~310 行，含嵌套可空智能转换/字符串拼接/质数/斐波那契）等 →
  **4/4 通过**，并已固化为正式用例 82–84；另以多组小程序定向验证默认参数、`for ((k,v) in map)`、
  `uppercase/lowercase`、`StringBuilder`、`filter/map/sortedBy/count/any` 链等惯用法。

合计 **17/19 通过**，两类失败（可空流敏感、Option 直接打印）均为已文档化的设计边界（见 §4）。

- **批次四（本轮，1000 行级与定向探针）**：撰写一个 **1068 行**综合工具箱程序（数论/字符串/排序/矩阵/
  接口与抽象类多态/泛型栈与队列/枚举状态机/数据类/函数式链/RPN 求值机，共 16 个子域、上百个函数与近 150 行输出），
  经 `kotlinc` 基准比对**逐字节通过**，已固化为正式用例 85；另以 8 组定向探针验证接口/抽象类、泛型容器、
  字符算术与 `Char.code`/`Int.toChar`、`padStart/padEnd`、`joinToString` 前后缀、`repeat{it}`、元组列表遍历、
  `power(...).toInt()` 数值转换等惯用法，均通过。

## 4. 已知边界与风险

| 类别 | 现状 | 影响 |
|------|------|------|
| 可空接收者的流敏感智能转换（早返式） | 部分支持 | `if (x != null) { ...x... }` 块式（含嵌套）已自动转 `if let`；但 `if (x == null) return` 之后再用 `x` 的**早返式**仍未支持（仓颉不允许同名遮蔽重绑定），需改写为嵌套 `if (x != null) { ... }` |
| `maxOrNull/minOrNull` 直接打印 | 保留 `Option` 包装 | `println(xs.maxOrNull())` 显示 `Some(1)` 而非 `1`/`null`；为支持高频 `?: d` 级联刻意保留，需打印裸值时改用 `max()` |
| 带参/枚举成员函数 | 未支持（带参项的实参被忽略） | 复杂枚举语义丢失（`sealed class` 子类已可） |
| 数值隐式提升 | 仓颉无 `Int64→Float64` 隐式转换 | 混合数值运算需源端显式统一类型 |
| 浮点打印格式 | 仓颉默认 6 位小数 `3.140000` | 期望输出需按此格式书写 |
| 字符串字符级下标 | 部分支持 | 接收者可证明为字符串时 `s[i]` 自动改 `s.toRuneArray()[i]` 取 `Rune`；类型不明处仍建议用 `for (c in s)`（自动 `.runes()`） |
| 协程 / 泛型**函数**声明 / 扩展函数 / 委托属性 | 未支持 | 泛型**类**已支持；泛型函数、扩展函数、协程超出当前子集 |

> 注：原表中的「`is` 类型判定」「二进制/十六进制/下划线字面量」「返回集合的链式高阶 `map/filter/reduce/sorted`」
> 「默认参数 / 命名参数调用」「块式可空智能转换」「接口/抽象类/用户泛型类」「字符串字符级访问与字符算术」
> 已在历轮实现并移出风险表。

## 5. 下一步规划

P0 与 P1 已完成（见 §3）。后续按「实用价值 ÷ 实现成本」排序：

**P1.5 收尾（少量遗留）**

1. **可空流敏感转换（早返式）**：把 `if (n == null) return x` 之后的非空使用改写为 `match (n) { case Some(v) => ... }`，
   或在早返点后对接收者插入 `getOrThrow()` 并重命名后续引用（需基本数据流分析 + 变量重命名）。
2. **惰性集合链与序列**：当前 `map/filter` 即时 `collectArrayList`，可补 `asSequence()` 惰性链与 `groupBy/associate*` 等。

**P2（远期，工程化与规模）**

3. **带参枚举与枚举方法**：`enum class E(val v: Int)` → 仓颉带参构造器 + 成员函数。
4. **多文件 / 包**：识别 `package`/`import`（当前已跳过顶层声明），输出对应仓颉包结构。
5. **诊断与回退**：对不支持构造给出带行号的清晰报错或「原样注释 + TODO」降级策略，避免整文件失败。
6. **规模化语料与基准**：把用例扩到 100+，纳入真实开源 Kotlin 片段做回归，统计「编译通过率/运行匹配率」趋势；
   持续扩充 §3.2 式的「未训练泛化抽样」以量化通用能力。
7. **格式化对齐**：可选接入 `cjfmt`，使产物风格与仓颉社区一致。

## 6. 维护提示

- 构建：`cd kotlin2cj && cargo build --release`（Rust edition 2024 / 1.85+）。
- 测试：`source /tmp/cangjie/envsetup.sh && python3 tests/run_tests.py`（写 `tests/log.md`）。
- 新增特性的标准做法：在 `node.rs` 增节点种类并补 `children_of`；在 `parser.rs` 加解析；
  在 `engine.rs` 的 `render` 加局部渲染规则；再加 `tests/cases/NN_xxx.{kt,expected}` 用例闭环验证。
