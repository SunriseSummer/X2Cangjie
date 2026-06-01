# kotlin2cj

**基于自组织临界性（SOC）局部规则的 Kotlin → 仓颉（Cangjie）源到源翻译工具**，
用 Rust 实现。它不依赖任何集中式神经网络或全局规划器，而是把代码翻译建模为
「信息沙堆」：每个语法单元只依据自身与邻居的状态局部更新译文，变更像雪崩一样
级联传播，直至整张「翻译图」自组织收敛到稳定态。

> 设计理念与架构详见 [`Design.md`](./Design.md)；灵感来源见 [`idea.md`](./idea.md)。

---

## 1. 环境要求

- **Rust** 工具链（`cargo`，edition 2024 / Rust 1.85+）。
- **仓颉编译器 `cjc`**（用于编译/运行翻译结果与跑测试；仅做翻译可不安装）。
  - 本仓库其余子项目约定的获取方式：
    ```bash
    curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz \
      | tar -xz -C /tmp
    source /tmp/cangjie/envsetup.sh
    ```
- **Python 3**（仅运行测试驱动 `tests/run_tests.py` 需要）。

---

## 2. 构建

```bash
cd kotlin2cj
cargo build --release
# 产物：target/release/kotlin2cj
```

---

## 3. 使用

### 3.1 翻译单个文件
```bash
# 输出到标准输出
./target/release/kotlin2cj input.kt

# 输出到文件
./target/release/kotlin2cj input.kt -o output.cj
```

### 3.2 翻译整个 Kotlin 项目（→ cjpm 项目）
```bash
# 输入目录路径，输出到指定目录
./target/release/kotlin2cj my_project/ -o my_project_cj/

# 不指定输出目录时，默认输出到 my_project_cj/
./target/release/kotlin2cj my_project/
```

项目级转换会：
- 扫描目录中的所有 `.kt` 文件（递归）
- 将所有源码合并为单一翻译单元（保证跨文件类型推断的正确性）
- 自动生成 `cjpm.toml`、`src/main.cj`
- 自动映射 Kotlin import → 仓颉 import

### 3.3 编译并运行翻译结果
```bash
source /tmp/cangjie/envsetup.sh

# 单文件模式
./target/release/kotlin2cj input.kt -o output.cj
cjc output.cj -o output
./output

# 项目模式
./target/release/kotlin2cj my_project/ -o my_project_cj/
cd my_project_cj && cjpm build && cjpm run
```

### 3.4 查看自组织统计
```bash
./target/release/kotlin2cj input.kt --stats
# 节点数 / 初始雪崩规模 / 状态更新总数 / 累计触发次数
```

### 3.5 演示「重命名雪崩」与自动修复
```bash
./target/release/kotlin2cj input.kt --demo-avalanche
# 选取一个被引用的局部声明改名，沿依赖边级联更新所有引用，
# 打印本次雪崩规模（只重算受影响子图，无需全局重译）。
```

命令行选项：

| 选项 | 说明 |
|------|------|
| `<input.kt>` | 输入的 Kotlin 文件（单文件模式） |
| `<project_dir>` | 输入的 Kotlin 项目目录（项目模式） |
| `-o, --output <file\|dir>` | 输出文件/目录，缺省单文件模式打印到 stdout，项目模式默认 `<name>_cj/` |
| `--stats` | 打印自组织 / 雪崩统计（写入 stderr） |
| `--demo-avalanche` | 演示重命名引发的引用雪崩 |

---

## 4. 翻译示例

输入 `Point.kt`：
```kotlin
class Point(val x: Int, val y: Int) {
    fun sumSquares(): Int {
        return x * x + y * y
    }
}
fun main() {
    val p = Point(3, 4)
    println("x=${p.x} y=${p.y} r2=${p.sumSquares()}")
}
```

输出（仓颉）：
```cangjie
class Point {
    let x: Int64
    let y: Int64
    init(x: Int64, y: Int64) {
        this.x = x
        this.y = y
    }
    func sumSquares(): Int64 {
        return (x * x) + (y * y)
    }
}

main() {
    let p = Point(3, 4)
    println("x=${p.x} y=${p.y} r2=${p.sumSquares()}")
}
```

运行：`x=3 y=4 r2=25`

---

## 5. 支持的 Kotlin 子集

- 变量 `val/var`、显式与推断类型、算术/比较/逻辑运算、`++ -- += -= *= /= %=`。
- 位运算中缀函数 `and / or / xor / shl / shr / ushr` → 仓颉 `& | ^ << >>`。
- 字符串模板 `"$x"` / `"${expr}"`（含嵌套表达式）、字符与浮点字面量。
- `if/else`（语句与表达式）、`when`（主语式 → `match`，支持 `Int`/`String`/枚举/逗号多值；
  含 `in 区间` / `!in 区间` / 关系分支时 → if-else 链；条件式 → `if/else` 链）。
- `while`、`do/while`、`repeat(n)`、`for` + 区间（`..` / `until` / `downTo` / `step`）、
  `for` + 集合遍历（含 `(k, v)` 解构）、`break` / `continue`、嵌套循环。
- 成员检查 `in` / `!in`：区间转比较，集合转 `.contains`。
- `is` 类型判定与智能转换：`when (x) { is T -> ... }` → `case x: T =>`（复用主体名做 narrowing）；
  类继承（`sealed`/`open` → `open class`，子类 `<: Super`）。
- 异常：`try / catch / finally`、`throw`。
- 函数（块体 / 表达式体 `=` / 递归 / 嵌套局部函数 / `main`）；顶层全局 `val`；`maxOf` / `minOf`；
  **默认参数** `fun f(a, b: Int = 1)` → 仓颉具名可选形参 `b!: Int64 = 1` 并在调用端自动补名；
  **函数类型** `(A,B)->R` 与高阶函数值（函数作实参）。
- 高阶：`xs.forEach { ... }`（含隐式 `it`）→ `for` 循环；**返回集合的链式高阶**
  `map` / `filter` / `sorted` / `sortedBy` / `sortedDescending` / `reversed` / `toList`
  → `collectArrayList(xs.iterator()....)`；聚合 `sum` / `sumOf` / `fold` / `reduce` /
  `count` / `any` / `all` / `none` / `max` / `min` / `maxOrNull` / `minOrNull`、
  `joinToString { it -> ... }`（带 transform）。
- 空安全：可空类型 `T?` → `?T`、Elvis `?:` → `??`、`!!` 剥离、
  `map[k] ?: d` → `map.get(k) ?? d`、`?.let { }` → `if (let Some(it) <- ...)`、
  `?.` 安全成员调用（下标 `m[k]?.x` → `m.get(k)?.x`，可级联 `?? d`）。
- 解构：`val (a, b) = expr`、`Pair` / `Triple` → 元组。
- 数字字面量：十进制、`0x` 十六进制、`0b` 二进制、下划线分隔（`1_000`）。
- 集合 `List/Map/Set`：字面量、显式泛型、`ArrayList/HashMap/HashSet` 构造器、下标读写、`.size`、`.add`、
  `.contains`、`.removeAt(i)` → `.remove(at: i)`、`.addAll` → `.add(all:)`、就地 `sort/sortDescending/sortBy`
  → `std.sort` 全局 `sort(...)`（稳定排序 `stable: true`）、`withIndex`、`average`、`containsKey`/`getOrDefault`、嵌套集合。
- 类：主构造器（`val/var/普通`参数）、成员变量与方法、对象创建、多类协作、继承、`init {}` 初始化块（并入构造器）、
  把类实例放入集合；`data class`（**自动生成 `toString` → `Name(f1=v1, ...)`**，对齐 Kotlin）；
  **接口 `interface`**、**抽象类 `abstract class` + `super(...)`**、**用户泛型容器类 `class Stack<T> { ... }`**。
- 算术：混合 `Int`/`Float` 运算单侧自动 `Float64(...)` 提升；String 与非 String 的 `+` 拼接自动补 `.toString()`；
  `Char ± Int` 码点运算。
- 可空智能转换：`if (x != null) { ...x... }`（含嵌套）→ `if (let Some(x) <- x) { ... }`（分支内再赋值则回退）；
  `x == null`/`x != null` 作为值表达式 → `x.isNone()`/`x.isSome()`。
- 枚举：`enum class`（具名常量项）→ 仓颉 `enum` + `@Derive[Equatable]` + 自定义 `toString`，
  支持 `==` 比较、`when` 匹配、`println(e)` 输出裸名与 `Enum.values()` 遍历。
- 字符串方法映射：`length`→`size`、`toUpperCase/toLowerCase`→`toAsciiUpper/Lower`、
  `trim`→`trimAscii`、`substring`→区间下标、`isNotEmpty`→`!isEmpty()`、`first/last`、
  `joinToString`→`String.join`、`startsWith/endsWith/contains/isEmpty` 等直通；
  `for (c in s)` 逐字符遍历改写为 `s.runes()`（产出 `Rune` 而非字节）；
  字符串 `s[i]`（可证明为字符串）→ `s.toRuneArray()[i]` 取 `Rune`、`take/drop/repeat`、`padStart/padEnd`、
  `joinToString(sep, prefix, postfix)`；字符 `c - '0'`/`Char.code`/`Int.toChar()` 码点转换、
  `isDigit/isLetter/...` → Rune `isAscii*`；列表 `take/drop`；`repeat(n){ it }` 索引绑定。

类型映射速览：

| Kotlin | 仓颉 |
|--------|------|
| `Int` / `Long` / `Short` / `Byte` | `Int64` |
| `Double` / `Float` | `Float64` |
| `Boolean` | `Bool` |
| `Char` | `Rune` |
| `String` | `String` |
| `MutableList<T>` / `List<T>` | `ArrayList<T>` |
| `MutableMap<K,V>` / `Map<K,V>` | `HashMap<K,V>` |
| `MutableSet<T>` / `Set<T>` | `HashSet<T>` |

### 已知边界
- 仓颉**不自动**把 `Int64` 隐式转 `Float64`，混合数值运算需在源端显式统一类型。
- 仓颉浮点默认打印为 `3.140000` 这类格式。
- 仓颉 `HashMap`/`HashSet` 的遍历顺序与 Kotlin 不一致；若输出依赖该序，需源端先 `sortedBy` 再遍历。
- 仓颉字符串下标 `s[i]` 取字节而非字符；接收者可证明为字符串时已自动改 `s.toRuneArray()[i]` 取 `Rune`。
- 暂未覆盖：泛型**函数**（泛型**类**已支持）、协程、惰性序列 `asSequence` 与 `groupBy`、
  可空接收者的**早返式**流敏感智能转换（`if (x == null) return` 后再用 `x`）。
  已支持：**扩展函数**（→ `extend` 语法）、**带参枚举**（→ class + static let 模式）、**companion object**（→ static 成员）。
  详见 [`State.md`](./State.md) 的现状评估与下一步规划。

---

## 6. 数据集与测试

- **学习语料** [`corpus/`](./corpus/)：Kotlin↔仓颉平行片段与规则归纳表
  （`pairs.md`），是局部规则的来源。
- **单文件测试** [`tests/cases/*.kt`](./tests/cases/)：186 个端到端用例（含经典算法、多类协作、
  高挑战性边界用例等），每个含 `.kt` 输入与 `.expected` 期望标准输出。
- **项目级测试** [`tests/cases/proj_*`](./tests/cases/)：7 个多文件 Kotlin 项目用例
  （calculator, shapes, todolist, bank, inventory, linkedlist, statistics），
  每个目录含多个 `.kt` 文件和 `expected_output`，验证项目级转换的完整流程。

运行全部单文件测试：
```bash
source /tmp/cangjie/envsetup.sh
cd kotlin2cj
python3 tests/run_tests.py
# 结果汇总写入 tests/log.md
```

运行项目级测试：
```bash
source /tmp/cangjie/envsetup.sh
cd kotlin2cj
python3 tests/run_project_tests.py
# 结果汇总写入 tests/project_log.md
```

当前基线：**186/186 单文件测试通过，7/7 项目级测试通过**。

---

## 7. 目录结构

```
kotlin2cj/
├── Cargo.toml
├── src/
│   ├── lexer.rs        # 词法分析（含字符串模板拆分）
│   ├── node.rs         # 翻译图：节点种类 / SOC 状态 / 边
│   ├── parser.rs       # 递归下降解析 + 类型映射 + 作用域解析
│   ├── engine.rs       # 自组织 worklist 引擎 + 局部渲染规则 + 装配
│   ├── render.rs       # 核心渲染规则
│   ├── render_calls.rs # 调用渲染：成员方法映射与 API 翻译
│   ├── heuristics.rs   # 类型启发式推断
│   ├── stdlib_map.rs   # 标准库接口映射表（解耦于语言特性转换）
│   ├── project.rs      # 项目级转换：目录→cjpm 项目
│   └── main.rs         # CLI（支持文件和目录输入）
├── corpus/             # 学习语料（平行片段 + 规则表）
├── tests/
│   ├── cases/          # 186 个单文件 .kt/.expected 用例
│   ├── cases/proj_*/   # 7 个多文件项目用例
│   ├── cangjie/        # 项目级测试生成的 cjpm 项目
│   ├── run_tests.py    # 单文件端到端测试驱动
│   └── run_project_tests.py  # 项目级端到端测试驱动
├── Design.md           # 技术方案
├── Readme.md           # 本文档
└── idea.md             # 灵感来源
```

---

## 8. 工作原理（一句话）

把每个语法单元当作沙堆里的一格，局部规则回答「我的子节点都翻好后我该长成什么样」；
worklist 反复唤醒被影响的节点、就地应用规则、再唤醒邻居——全局正确的译文是这些
局部回答级联、自组织收敛后的**涌现结果**。详见 [`Design.md`](./Design.md)。
