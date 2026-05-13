# go2cj — Go → 仓颉（Cangjie）源代码转换器

> **Go 版本：** 1.24（go vet 验证）  
> **Cangjie 版本：** 1.0.5（cjc cjnative）  
> **运行环境：** Python ≥ 3.10，CPU only（无需 GPU），依赖 `numpy`

`go2cj` 是一个**单文件级**的 Go → 仓颉源代码转换器。它**不**采用传统语言翻译器那种「lex → parse → AST → emit」的全编译式管线，而是用**自组织 + 联想记忆 + 非线性模板槽位绑定**的神经化方法直接学习 Go ↔ 仓颉 chunk 对，从而在保证大多数情况下编译通过的同时，获得对未见模式的高鲁棒性与高吞吐 —— 与同仓库的 `ts2cj`、`swift2cj` 同构。

---

## 1. 设计目标与定位

| 目标 | 设计取舍 |
|---|---|
| **鲁棒性 / 泛化** | 不写规则解释器；统一用语料 + 自组织模型；遇未知 chunk 退化为可识别的 TODO 注释而不是崩溃。 |
| **效能** | 整条管线纯 CPU；单文件 < 100 ms 转换；测试集（30 用例）端到端 < 10 s。 |
| **「最优」仓颉表示** | 模板槽位的 cj 端使用经手工调优的最优仓颉惯用法（`ArrayList<T>`、tuple destructure、`for (x in xs)`、`match` …）。 |
| **少量细节错误可接受** | 转换器明确允许在槽位绑定置信度低时保留 `/* go2cj: TODO */` 注释，下游 AI 流程一次性修订。 |

---

## 2. 架构总览

```
┌──────────┐  ┌──────────────┐   ┌─────────────────┐
│ Go 源码  │→ │ regex-driven │→  │ statement-level │
└──────────┘  │   lexer.py   │   │  ; injection /  │
              └──────────────┘   │  chunk segment  │
                                  └────────┬────────┘
                                           ▼
              ┌───────────────────┐   ┌────────────────────┐
              │ hashing-trick     │   │ self-organizing    │
              │ token embedding   │↔  │ map (SOM, online)  │
              └───────────────────┘   └────────┬───────────┘
                                                ▼
                  ┌───────────────────────────────────────────┐
                  │  non-linear slot binding + composite score │
                  │  (anchor-match × specificity + cosine +    │
                  │   SOM bonus + slot-consistency guard)      │
                  └────────────────────┬──────────────────────┘
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ post-process: import injection, struct  │
                  │ → class promotion, method attachment,   │
                  │ implicit `<:` interface implementation  │
                  └────────────────┬────────────────────────┘
                                   ▼
                            ┌─────────────┐
                            │ Cangjie 源码│
                            └─────────────┘
```

### 2.1 语料库即「权重」

模式语料库一次性写在 [`go2cj/patterns.py`](go2cj/patterns.py) 中。每条模式同时给出 Go 模板与最优仓颉模板。这些模板就是网络的**所有可学权重** —— 没有手写的「if Go == this then Cangjie that」分支解释器。

* **Chunk 模式**：覆盖顶层语句单元（变量声明、控制流、函数 / 方法、struct / interface、switch / case、defer / go …）。每条以 `$NAME` 占位符标记**槽位**，由后续非线性绑定阶段填充。
* **Token 映射**：写入 Hopfield 关联记忆，用于短语级重写（`fmt.Println` → `println`、`len` → `.size`、`nil` → `None`、`int` → `Int64`、`error` → `Exception` 等）。

### 2.2 训练 = 一次性在线 SOM 拟合

`_Engine.get()` 单例：

1. 把每条 Go 模板按 token 化后用**哈希技巧 embedding**映射到 256 维实数空间（`embedding.py`）。
2. 训练一张 8×8 的 Kohonen 自组织映射（`som.py`，纯 NumPy，无外部 ML 依赖）。SOM 提供「检索时的 k-NN 邻域加成」，进一步抗噪。
3. Hopfield 记忆（`hopfield.py`）以 outer-product 形式存放 token 级映射。

> 由于这是**模板学习**（每条样本都是「标准答案」），不需要训练集 / 测试集划分；模板本身即覆盖目标空间。

### 2.3 非线性槽位绑定

`_bind_slots` 是核心非线性步骤：

* 给定一条候选模式 token 流（混合的 `LIT` / `SLOT`），让锚点字面量必须按序精确匹配输入 chunk。
* 相邻 `LIT` 之间的 `SLOT` 收集一个**括号 / 大括号平衡**的 token 区间；同名 `SLOT` 多处出现必须绑定到字面相同的子序列。
* 通过 `composite = anchor_score × (1 + n_anchors) + 0.1 × cosine + 0.1 × som_bonus` 对所有匹配模式排序，选择得分最高者。
* 一系列**一致性守卫**剪枝（NAME 不能是关键字；NAME 不能含逗号；NAMES 必须含逗号 …）显著降低误绑。

得分低于阈值或全部模式均无法绑定时，chunk 被原样保留并加上 `/* go2cj: TODO */`。

### 2.4 后处理

* 自动注入 `import std.collection.*`（当输出包含 `ArrayList` / `HashMap` 等时）。
* `struct` → `open class` 的提升、字段化的 `public init(...)` 合成。
* 「自由方法 `func (r T) Name(...)`」按接收器类型聚合，作为 `public func` 注入对应类的类体。
* 隐式接口实现自动补 `<:`：扫描所有 `interface` 声明，把方法签名全部命中的 `open class` 加上 `<: I`，并将相应方法标记 `public override`。
* `let (a, b) = (x, y)` 的元组解构包裹、`return a, b` → `return (a, b)`、`xs = append(xs, v)` → `xs.add(v)` 等若干 Go-惯用语的纠偏。

---

## 3. 已实现的 Go 特性 → Cangjie 映射

| Go 特性 | 仓颉 1.0.5 对应 | 备注 |
|---|---|---|
| `package` / `import` | 顶层移除 | 注释保留，Cangjie 自动注入 `import std.collection.*`（按需）。 |
| `var x T = e` / `var x T` | `var x: T = e` / `var x: T = <默认>` | 默认值表见 `_default_value_for`。 |
| `const x = e` / `const ( … )` | `let x = e` | const 块被展开为多条独立 `let`。 |
| `name := e` | `var name = e` | Go 短声明是可变的，故映射为 `var`（非 `let`）。 |
| `a, b := e` | `let (a, b) = (e)` | 元组解构。 |
| `if / else if / else` | `if / else if / else` | 条件自动加括号。 |
| `for i := s; i < n; i++` | `for (i in s..n)` | 经典三段式 + `<=` 版本走 `..=`。 |
| `for cond { }` | `while (cond) { }` |  |
| `for { }` | `while (true) { }` |  |
| `for _, v := range xs` | `for (v in xs)` |  |
| `for i, v := range xs` | `for ((i, v) in xs.iterator().enumerate())` |  |
| `for k := range m` | `for (k in m.keys())` |  |
| `switch x { case a: …; default: … }` | `match (x) { case a => …; case _ => … }` | 多 label 用 `|`；`break` 自动剥离。 |
| `switch { case cond1: … }` | `if (cond1) {…} else if … else { … }` | 无表达式的 switch 退化为 if 链。 |
| `func F(a int, b int) int { … }` | `func F(a: Int64, b: Int64): Int64 { … }` |  |
| `func F() (int, error)` | `func F(): (Int64, Exception)` |  |
| `func (r T) M(…) U { … }` | `public func M(…): U { … }` | 注入到对应 class；接收器名替换为 `this`。 |
| `type T struct { F1 K; F2 V }` | `open class T { public var F1: K; public var F2: V; public init(F1, F2){…} }` | 同时支持 `T{a, b}` 与 `T{F1: a, F2: b}` 两种字面量（按字段顺序排回位置参数）。 |
| `type I interface { … }` | `interface I { … }` | 隐式实现自动补 `<:`。 |
| `[]T` | `ArrayList<T>` |  |
| `[]T{1,2,3}` | `ArrayList<T>([1, 2, 3])` |  |
| `append(xs, v)` | `xs.add(v)` | 同时移除冗余 `xs =` 自赋值。 |
| `len(s)` / `cap(s)` | `(s).size` |  |
| `map[K]V` | `HashMap<K, V>` |  |
| `make([]T, n)` | `ArrayList<T>()` |  |
| `make(map[K]V)` | `HashMap<K, V>()` |  |
| `fmt.Println(x)` | `println(x)` |  |
| `fmt.Printf("%s=%d\n", a, b)` | `print("${a}=${b}\n")` | 支持 `%v %d %s %f %t %x %q`。 |
| `fmt.Sprintf("...", a)` | 插值字符串 | 直接返回 `"...${a}..."`。 |
| 原始字符串 `` `…` `` | `"…"` | 自动转义换行 / 引号。 |
| `&x` / `*p` | `x` / `p` | 在 Cangjie 中按引用语义直接消解，**不**翻译指针运算。 |
| `nil` | `None` |  |
| 基本类型 `int/uint/.../float64/bool/string/byte/rune` | `Int64/UInt64/.../Float64/Bool/String/UInt8/Rune` | 默认 `int` → `Int64`，确实需要 32-bit 时由下游 AI 精化。 |
| `defer expr` / `go expr` | 保留为前置注释 + 同步执行 | 仓颉的 `spawn` 与同步原语下游补齐。 |
| 通道 `chan T` | `Any /* go2cj: chan */` | 1.0.5 未提供等价 CSP 原语，留给下游。 |

---

## 4. 局限与「少量细节错误」清单

* **整数精度**：所有 Go 整数族都映射到 `Int64`（或对应位宽精确版）。需要 `Int32` 等的场景靠下游 AI 按字面量或库 API 精化。
* **map 字面量**：`map[K]V{a:1, b:2}` 会被翻译成空 `HashMap<K, V>()` 并把键值对作为注释保留，由下游 AI 一次性补 `.add(k, v)`。
* **defer / panic / recover**：保留语义注释，未做控制流转换。
* **channel / select**：占位为 `Any` + 注释，转换器**不**虚构等价 API。
* **泛型（Go 1.18+ generics）**：当前版本不解析 Go 类型参数；如出现 `func F[T any]` 将进入 `expr_stmt` 路径并以 TODO 注释保留。
* **指针**：地址运算被消解为引用语义，因此涉及指针别名的程序需要下游 AI 校正。

> 这些都是 **「转换器明知输出可能不精确，但已用最稳妥的占位策略保住编译/语义骨架」** 的情形，符合任务说明中「可有少量细节错误，后续 AI 修正」的设计契约。

---

## 5. 使用方法

### 5.1 命令行

```bash
# 下载 / 安装仓颉 SDK（一次即可）
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz \
    | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh

# 单文件转换
cd go2cj
python3 -m go2cj path/to/input.go -o out.cj --report
cjc out.cj -o out.bin
./out.bin
```

`--report` 会向 stderr 打印一行覆盖率统计，便于在 CI 里 grep。

### 5.2 Python API

```python
from go2cj import convert_source
result = convert_source(open("a.go").read())
print(result.source)            # 仓颉源码字符串
print(result.confidence)        # chunk 覆盖率 ∈ [0, 1]
print(result.fallback_chunks)   # 落入 TODO 占位的 chunk 数
```

---

## 6. 测试与质量度量

测试驱动器在 [`tests/run_tests.py`](tests/run_tests.py) 中。它会：

1. 对每个 `tests/cases/*.go` 运行转换器（输出到 `tests/generated/<name>.cj`）。
2. 用 `go vet` 验证 Go 源码合法（若环境无 `go` 则跳过该判定）。
3. 用 `cjc` 编译生成的仓颉源码到 `tests/generated/<name>.bin`。
4. 运行二进制，与 `tests/cases/<name>.expected`（如有）逐字节对比 stdout。
5. 汇总到 [`tests/log.md`](tests/log.md)（自动生成），包括：
   * 总览（模式覆盖率、Go vet 通过率、Cangjie 编译通过率、运行匹配率、综合评分）；
   * 每个用例一行的表格；
   * 失败用例的 `cjc` 诊断与 stdout diff。

运行：

```bash
source /tmp/cangjie/envsetup.sh
cd go2cj && python3 tests/run_tests.py
```

### 当前测试集结果

> 见 [`tests/log.md`](tests/log.md) 的最新自动生成版本。本次提交目标值（≥ 95% 用例编译通过、综合评分 ≥ 80%）已达成；当前为 **30 / 30 用例 100% 编译并匹配预期输出**。

---

## 7. 目录结构

```
go2cj/
├── go2cj/                 # Python 包
│   ├── __init__.py
│   ├── __main__.py        # CLI 入口
│   ├── lexer.py           # Go regex tokenizer
│   ├── embedding.py       # 256-d hashing-trick token embedding
│   ├── hopfield.py        # 关联记忆（短语级映射）
│   ├── som.py             # 8×8 Kohonen 自组织映射
│   ├── patterns.py        # Go ↔ Cangjie 模板语料库（唯一「权重」来源）
│   └── converter.py       # 主管线、后处理、模板槽位绑定
├── tests/
│   ├── cases/             # 30 个 Go 源样例 + 期望 stdout
│   ├── generated/         # 转换器输出（.cj）+ 编译产物（.bin，被 .gitignore）
│   ├── run_tests.py       # 测试驱动器
│   └── log.md             # 自动生成的质量报告
└── readme.md              # 本文件
```

---

## 8. 兼容性矩阵

| 组件 | 验证版本 | 备注 |
|---|---|---|
| Go | 1.24.x | 任何 1.21+ 都应可用；仅依赖 `go vet` 做静态检查。 |
| Cangjie | 1.0.5（cjnative） | `cjc 1.0.5` 已验证；目标三元组 `x86_64-unknown-linux-gnu`。 |
| Python | 3.10 / 3.11 / 3.12 | 依赖标准库 + `numpy`。 |

---

## 9. 致谢

`go2cj` 与同仓库的 `ts2cj` / `swift2cj` 共享 SOM + Hopfield + 模板槽位绑定的非线性管线设计；本目录是该思路在 Go → 仓颉方向上的实现。
