# swift2cj — Swift → Cangjie 神经/自组织代码转换器

`swift2cj` 把单个 Swift 源文件转换成等价的仓颉（Cangjie）源文件。它的核心目标
不是 100% 精确的传统编译式翻译，而是**对任意 Swift 输入都能高效产出"最优近似"
的仓颉表达**，作为后续 AI 修正流程的稳定输入。

转换器的设计思路与同仓库的 [`ts2cj`](../ts2cj/readme.md) 一致：用
**自组织映射（SOM）+ Hopfield 关联记忆 + 模板槽位绑定** 的非线性管线代替传统的
词法 / 语法分析器；语料是一组 Swift↔Cangjie 模式对，所有"学习"都发生在装载
模型时（无外部训练数据、无 GPU、无网络依赖）。

```
swift2cj/
├── swift2cj/
│   ├── __init__.py        # 包入口：convert_source / ConversionResult
│   ├── __main__.py        # CLI：python -m swift2cj
│   ├── lexer.py           # 轻量级 Swift 词法器（不解析语法）
│   ├── embedding.py       # 把 Token / Token 序列嵌入到固定维向量
│   ├── som.py             # Kohonen 自组织映射
│   ├── hopfield.py        # 离散 Hopfield 关联记忆（模式记忆 + 召回）
│   ├── patterns.py        # Swift↔Cangjie 模式库（约 90 条）
│   └── converter.py       # 顶层管线：chunk → 模式选择 → 槽位绑定 → 渲染
└── tests/
    ├── cases/             # 72 个 Swift 测试用例 + 期望输出（含 100 行 / 200 行 / 300+ 行规模）
    ├── run_tests.py       # 一键 swiftc + cjc + diff + 写 log.md
    ├── generated/         # 测试时生成的 .cj / 二进制（被 .gitignore 排除）
    └── log.md             # 由 run_tests.py 自动生成的覆盖率 / 评分报告
```

## 1. 快速开始

```bash
# 1) 准备 Cangjie 工具链（cjc）
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz \
  | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh

# 2) Python 依赖
pip install numpy

# 3) 转换单个文件
cd swift2cj
python -m swift2cj path/to/foo.swift -o foo.cj --report

# 4) 跑全部测试，生成 tests/log.md
python tests/run_tests.py
```

`--report` 会在 stderr 上打印形如
`[swift2cj] chunks=4 confident=4 fallback=0 confidence=100.00%` 的覆盖率信息。

## 2. 技术架构

### 2.1 管线总览

```
   Swift 源
     │
     ▼
[1] 文本预改写  ──  字符串插值 \(x) → ${x}、try → ""、nil → None、
                   .count→.size、.append→.add、super.init→super、
                   leading-dot 枚举去前缀、tuple .N → [N]、
                   force-unwrap "!" 去除……（_rewrite_source）
     │
     ▼
[2] 词法分析    ──  swift2cj/lexer.py  产出 Token 流
     │           (KEYWORD / IDENT / NUMBER / STRING / OP / PUNCT)
     ▼
[3] 顶层切片    ──  按"语句边界 + 平衡括号"切成 chunk；
                   if/else、do/catch、repeat/while 等结构粘合在一个 chunk
     ▼
[4] 嵌入        ──  swift2cj/embedding.py：token → 32 维稠密向量、
                   chunk → 序列均值向量（轻量、确定性、可逆）
     ▼
[5] SOM 召回    ──  Kohonen 自组织映射对 chunk 向量做 k-近邻召回，
                   产出"候选模式索引集合"作为打分加权
     ▼
[6] 槽位绑定    ──  对每个候选模式，用 _bind_slots 做"锚字面量对齐 +
                   平衡括号收集"的子线性槽位绑定；不需要 PEG / GLR
     ▼
[7] 综合打分    ──  锚字面量数 + Hopfield/SOM 相似度 + 类型上下文加分；
                   选最高分的模式
     ▼
[8] 渲染        ──  把绑定的槽位替换进 Cangjie 模板；
                   $EXPR/$BODY 等子结构递归回 [3]，保证嵌套块也走同管线
     ▼
[9] 后处理      ──  自动 `import std.collection.*`、合成 struct/class 
                   memberwise init、override→open override、
                   ArrayList/HashMap 字面量包装、main() 合并、收紧泛型空格
     ▼
   Cangjie 源
```

### 2.2 非线性核心组件

| 组件 | 文件 | 作用 |
|---|---|---|
| **Token 嵌入** | `embedding.py` | 把离散符号映射到 32 维向量，让"句法形态"可在向量空间度量相似度 |
| **SOM** | `som.py` | 在装载期把所有模式向量训练成 6×6 的拓扑图；推理时用 BMU + k-邻居召回，把候选集从 N 降到 ~8 |
| **Hopfield 关联记忆** | `hopfield.py` | 存储 chunk-级"完形"模式，用于在槽位绑定失败时给出最接近的回退建议 |
| **模板槽位绑定** | `converter.py::_bind_slots` | 把锚字面量当"晶格"，未知槽（如 `$EXPR`、`$BODY`）以平衡括号 / 大括号自然吸附；和神经召回联合打分 |

整条管线**没有真正的 AST**，因此对 Swift 文法的微小变体和不规范输入仍能稳定产
出；模式库可随时追加而不破坏既有路径——这是相对传统语言翻译工具最大的鲁棒性
来源。

### 2.3 模式库

`patterns.py` 中约 90 条模式覆盖了：

* 变量声明（`let` / `var`，带类型 / 不带类型 / 带初始化）
* 控制流（`if` / `else if` / `else`、`while`、`repeat ... while`、
  `for-in` 的半开区间 `..<` 与闭区间 `...`、`break` / `continue`）
* 函数（普通 / 抛出 / 泛型；带返回 / 不带返回；外部参数标签）
* 类、结构体、枚举、协议（含继承 / `<:`、`override` / `open override`）
* 集合（`[T]` → `ArrayList<T>`、`[K:V]` → `HashMap<K,V>`、字面量包装）
* `switch` / `case`（标签合并、`default` → `case _`、leading-dot 去前缀）
* `do { } catch { }` → `try { } catch (e: Exception) { }`
* 类型别名 `typealias`
* 任意 chunk 的兜底 `expr_stmt` 模式

任何当前没有匹配的 Swift 形态会保留为表达式语句并由 token 级渲染产出，不会
让管线崩溃。

### 2.4 关键文本前置改写

`converter.py::_rewrite_source` 在词法之前做一组"非语义敏感"的文本替换，
它们都尊重字符串字面量边界（`_outside_strings_*`），并能感知 `${...}` 插值
块为代码段递归处理：

* `\(expr)` → `${expr}`（支持嵌套括号、转义、三引号串保留）
* `nil` → `None`、`self` → `this`、`try`（前缀）→ 空
* `super.init(` → `super(`
* `.count` → `.size`（仅当不是方法调用）、`.isEmpty` → `.isEmpty()`、
  `.append(` → `.add(`、`.uppercased()` → `.toAsciiUpper()` 等
* 枚举 leading-dot：`(?<![A-Za-z0-9_)\]])\.(?=[A-Za-z_])` → 去掉点
* 元组成员：`(?<=[A-Za-z_\)\]])\.(\d+)` → `[\1]`
* 强解包：`x!` → `x`（不影响 `!=` 与一元 `!`）
* **闭包**：`{ x in body }` → `{ x => body }`；在 `let f = {...}` 处自动给
  bare 参数追加 `: Int64`，调用参位置则不加（让 callee 类型驱动推断）
* **guard**：`guard cond else { B }` → `if (!(cond)) { B }`，含 `guard let`
* **三元**：`a ? b : c` → `(if (a) { b } else { c })`，并能感知 `${...}` 插值
* **switch 解构**：`case .v(let a, let b):` → `case v(a, b) =>`（深度感知 +
  剥离 `let`）
* **枚举原始值**：`enum X: Int { case a = 1 }` → `enum X { | a | ... }`
* **运算符重载**：`static func +(a: T, b: T) -> R { ... }` → 
  `public operator func +(b: T): R { ... }`，并把首参替换为 `this`
* **多协议继承**：`: A, B` → `<: A & B`
* **命名参数**：用户写的 `init(x: T)` / `func f(x: T)` 默认翻成 `x!: T`，
  `_ x: T` 仍是位置参 —— 这样 Swift 调用站点的标签形 `Foo(x: 1)` 在 Cangjie 端
  也能 work
* **super 提升**：`init` 体内的 `super(...)` 自动提到首行（Cangjie 要求）
* **多参 print**：`print(a, b, c)` → `println("${a} ${b} ${c}")`（字符串字面
  量直接内联避免嵌套插值），并把所有 `print(...)` 统一映射为 `println(...)`
* **mutating / lazy / weak / unowned / required / @discardableResult / @objc**
  等 Swift-only 修饰符自动剥离
* 空数组字面量 `ArrayList<T>([])` 收紧为 `ArrayList<T>()`
* 一元减号去多余空格 `- 1` → `-1`
* `final class` / `public class` 模式；final 类移除多余 `open` 修饰符；
  `extend` 块剥离 `open`/`override` 修饰符

### 2.5 上下文敏感的模式门控

`_convert_chunk` 接受 `ctx∈{None, "class", "struct", "iface"}`，并按上下文
筛选候选模式：

* 顶层不允许 `method_*` / `init_*` / `proto_method_*` 命中
* 类 / 结构体内部不允许 `function_*` 命中
* 协议内部进一步偏向 `proto_method_*`

这避免了同形签名（如 `func f(x: Int) -> Int { ... }`）在不同位置被错误绑定。

### 2.6 自动合成 memberwise init

`_ensure_memberwise_init` 对每个 `class` / `struct` 主体做深度敏感扫描
（只看顶层字段、绝不把方法体里的 `let i: Int = ...` 当字段）：

* 如用户已写 `init(...)` —— 跳过；
* 否则收集所有**没有声明期默认值**的字段 `name: TY`，生成
  `public init(name!: TY, ...) { this.name = name; ... }`；
* 如**所有**字段都已有默认值，则不合成，依赖 Cangjie 的隐式零参构造器。

这一规则与 Swift "如果你没写 init，结构体获得 memberwise init，类获得 no-arg init
（当所有属性有默认值时）"语义对齐。

### 2.7 集合字面量回收

`var xs: [Int] = [1,2,3]` 经模式产出 `var xs: ArrayList<Int64> = [1,2,3]`，
但 Cangjie 不会把 `Array` 字面量隐式转换为 `ArrayList`。`_emit` 在
typed-init / 字段-init 类模式下检测到 RHS 是 `[...]` 字面量，会自动包装为
`ArrayList<Int64>([1,2,3])`；字典字面量 `[k1: v1, k2: v2]` 还会先重写成
`[(k1, v1), (k2, v2)]` 以适配 `HashMap` 构造器。

### 2.8 多级继承时的 override

Cangjie 的 `override` 不会自动让方法再次开放，因此**子类的 override 必须额外加
`open`**，否则孙类无法继续覆盖。`patterns.py` 中 `override_method_*` 直接
渲染为 `public open override func ...`；在子类内部扫描时，转换器还会探测父类
方法集，对同名方法再次注入 `open override`。

## 3. CLI 参考

```text
usage: python -m swift2cj [-h] [-o OUTPUT] [--report] input

positional arguments:
  input          path to a Swift source file (- for stdin)

optional arguments:
  -h, --help     show this help message and exit
  -o OUTPUT      write Cangjie output here (default: stdout)
  --report       print "chunks/confident/fallback/confidence" to stderr
```

退出码非零仅当输入读取失败或写入失败；语义层"无法识别"通过 `--report` 的
`fallback` 计数与（必要时）`/* swift2cj: TODO */` 注释体现，绝不抛异常。

## 4. 测试 & 评分

`tests/run_tests.py` 是一个零依赖（仅 `numpy`）的端到端驱动：

1. 遍历 `tests/cases/*.swift`；
2. 用 `swiftc -typecheck` 检查 Swift 源（若 `swiftc` 不在 PATH 则跳过；不计为失败）；
3. 调本包 CLI 转换；
4. 调 `cjc` 编译产物为二进制；
5. 运行二进制，与同名 `.expected` 文件做逐字节比对；
6. 把每个用例的 `chunks / confident / fallback / 覆盖率 / Swift / CJ / 运行` 写进
   `tests/log.md`，并按
   `score = 0.4 × pattern_coverage + 0.4 × cj_compiles + 0.2 × runs_and_matches`
   计算综合分。

当前结果（见 [`tests/log.md`](tests/log.md)）：

| 指标 | 数值 |
|---|---|
| 用例总数 | 72 |
| 模式覆盖率 | **100.00 %** |
| Swift 类型检查通过 | **72 / 72** |
| Cangjie 编译通过 | **72 / 72** |
| 运行输出匹配 | **72 / 72** |
| 综合质量分 | **100.00 %** |

测试覆盖范围：基础类型 / 算术 / 比较 / 布尔逻辑、`if-else-if-else` 任意深度链、
`while` / `repeat-while` / `for-in` 两种区间、函数（普通、递归、泛型、`throws`）、
类（含继承 / 多级继承 / `override` / `final` / 多协议 `&` 复合）、结构体（含
memberwise init）、枚举（含 `switch` 多标签 / `default` / 关联值 / 原始值 /
`case .v(let a, let b)` 解构）、协议、`[T]` / `[K:V]` 集合、元组、`typealias`、
方法链、堆栈与统计类、**闭包/Lambda**、**运算符重载**（`+ - * / == < >`）、
**guard 与三元**、**try/catch + 自定义 Exception 子类**、**`extend` 扩展**、
**`Bag<T>` / `Stack<T>` 等泛型容器**、以及百行 / 200 行 / 300+ 行级的综合
程序（`70_shapes_large.swift`、`71_inventory_large.swift`、`72_card_game.swift`）。

## 5. 已知简化与后续 AI 可修正方向

转换器主动选择"快、稳、保留语义骨架"而牺牲极端边角的精确度；下列项会被原样
（语法可编译）但语义可能略有偏差地翻译，由后续 AI 修复：

* **数值类型粒度**：`Int` 一律落到 `Int64`，`Double` 落到 `Float64`；用户若要更窄
  整数 / 浮点类型，需要 AI 看 literal 范围回写。
* **可选类型**：当前把 `T?` 仅做形态保留（`?T`），并把表达式中的 `x!`
  力解包整体抹去；若用户依赖 `if let` / `guard let` 等更复杂控制流，AI 需要补
  全 `match` 解构。
* **错误处理**：`throw MyError(...)` 当 `MyError` 不继承 `Exception` 时 Cangjie
  会拒收。测试集合中已用兼容的形态；现实代码需要 AI 把自定义 `Error` 改为继承
  `Exception`。
* **泛型约束**：`<T: P>` 当前丢弃为 `<T>`；多重 / where 约束需 AI 翻译为
  Cangjie `where` 子句。
* **闭包**：尾随闭包、捕获列表、`@escaping` 等语法当前以 token 级渲染保留，未
  做特殊 Cangjie lambda 重写。
* **属性观察器**（`willSet` / `didSet`）：保留为 token 级文本，需 AI 转写为
  Cangjie property accessor。
* **call-site 集合字面量**：构造器实参位置的 `[...]` 字面量目前不会自动包装为
  目标 `ArrayList<...>`，需要 AI 在调用点显式包一层。

这些简化都是显式的、可枚举的，因此后续 AI 修正阶段的搜索空间是有限的。

## 6. 与 ts2cj 的对比

* **同**：同样的 SOM + Hopfield + 模板槽位绑定管线；同样的"宁可弱表达也不崩溃"
  哲学；同样的 `import std.collection.*` 注入、`main()` 合并、override 检测等
  后处理流程。
* **异**：Swift 的字符串插值 `\(expr)`、leading-dot 枚举、强解包 `!`、元组
  `.N` 访问、`super.init`、memberwise init 等特性都是 swift2cj 独有的；同时
  Swift 没有 TS 的接口/类型字面量，所以模式库的形态更面向"类 + 协议"。
