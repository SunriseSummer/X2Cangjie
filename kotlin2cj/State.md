# kotlin2cj 现状评估与下一步规划

> 本文给出 kotlin2cj（Kotlin → 仓颉源到源翻译器）截至当前迭代的能力评估、
> 测试现状、已知边界与后续路线图。配套基线见 [`tests/log.md`](./tests/log.md)，
> 支持的语言子集见 [`Readme.md`](./Readme.md)。

## 1. 一句话现状

kotlin2cj 已从「基础语法演示」推进到「**可翻译并端到端跑通中小规模实用 Kotlin
程序**」的阶段：覆盖控制流、函数（含嵌套/递归）、类（含继承/`sealed`）、枚举、集合、
异常、位运算、区间成员检查、`is` 类型判定、解构声明、`?.` 安全调用、`maxOf/minOf`
及常见空安全惯用法等特性，**69 个端到端用例全部翻译 → `cjc` 编译 →
运行输出逐字节匹配（69/69/69）**。State.md 路线图中的 **P0 与 P1 已基本完成**。

## 2. 测试现状

| 指标 | 数值 |
|------|------|
| 端到端用例总数 | 69 |
| 翻译成功 | 69/69 |
| 仓颉 `cjc` 编译通过 | 69/69 |
| 运行输出匹配 | 69/69 |
| 泛化抽样（未训练的新程序） | 5/6 通过（详见 §3.2） |
| 验证工具链 | Cangjie SDK 1.0.5（cjnative，x86_64-linux）；用例期望值由 `kotlinc` 实编译运行产出 |

用例覆盖维度：

- **基础与控制流**：变量、运算符、`if/when/while/do-while/repeat/for`、`break/continue`、嵌套循环。
- **区间与成员**：`..`/`until`/`downTo`/`step`、`in`/`!in`（区间转比较、集合转 `contains`）。
- **函数**：块体/表达式体、递归、嵌套局部函数、顶层全局 `val`、`maxOf/minOf`。
- **集合**：List/Map/Set 字面量与泛型、`ArrayList/HashMap/HashSet` 构造器、下标读写、嵌套集合、`forEach`、`map[k] ?: d`、`?.` 安全调用链。
- **类型抽象**：类（主构造器/方法/多类协作/继承）、`sealed class` + `when (x) { is T -> }`、`data class`、`enum class`（+`@Derive[Equatable]`）、解构声明 `val (a, b) = p`。
- **异常**：`try/catch/finally`、`throw`。
- **位运算与字面量**：`and/or/xor/shl/shr`、`0x`/`0b`/下划线数字字面量。
- **规模**：筛法（50 以内素数）、Collatz 最长链、3×3 网格与分组映射、库存/状态机、RPN 求值、词频统计、泛型栈、成绩分级等综合程序。

运行方式：

```bash
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh
cd kotlin2cj && python3 tests/run_tests.py   # 结果写入 tests/log.md
```

## 3. 本轮新增能力

### 3.1 新增语言特性（完成 P0 + P1）

相对上一基线（57/57），本轮在原有位运算/区间成员/异常/`forEach`/枚举/全局 `val`/嵌套函数
基础上，进一步补齐 P0 与 P1：

1. **数字字面量增强**（P0）：词法识别 `0x`/`0b`/下划线分隔，剥离 `L/u/U` 后缀后直接归一为仓颉字面量。
2. **`is` 类型判定与智能转换**（P0）：`when (x) { is T -> ... }` → `case x: T =>`（复用主体名实现智能转换），
   并捕获类继承（`sealed/open` → `open class`，子类 `<: Super`）。
3. **字符串/集合方法映射补充**（P0）：`substring`→区间下标 `s[a..b]`、`isNotEmpty`→`!isEmpty()`、
   `first/last`、`joinToString`→`String.join(arr.toArray())`、`map.keys/values`→方法调用、
   `toInt/toLong/toDouble/toFloat`（数值字面量直转 vs 字符串 `.parse` 启发式）。
4. **解构声明**（P1）：`val (a, b) = expr` → 仓颉元组解构；`Pair`/`Triple` → 元组字面量与元组类型。
5. **空安全细化**（P1）：`?.let { it -> ... }` → `if (let Some(it) <- recv) { ... }`；
   `?.` 安全成员调用 → 下标读取改用 `.get(k)` 得 `Option` 并保留 `?.`，可与 `?: d`（→ `?? d`）级联。
6. **`maxOf` / `minOf`** → 内联条件表达式 `(if (a > b) { a } else { b })`，不依赖标准库符号，稳健可靠。
7. **泛型容器构造器**：`ArrayList<T>()`/`HashMap<K,V>()`/`HashSet<T>()`/`LinkedHashMap` → 对应仓颉构造。

实现仍遵循原有 SOC（自组织临界）管线：词法 → 递归下降建图 → worklist 松弛渲染，
新特性以新增节点种类（`IsCheck`/`TypePat`/`SafeLet`/`DestructureDecl`、`Member.safe` 标记等）与
局部渲染规则的方式接入，未改动核心引擎。

### 3.2 泛化能力评估（未训练新程序）

为避免「只对已有用例过拟合」，本轮额外撰写 6 个**不在测试集**的新程序，用 `kotlinc` 实编译运行得到
基准输出，再经 kotlin2cj 翻译 → `cjc` 编译 → 运行比对：

| 程序 | 主题 | 结果 |
|------|------|------|
| g1 | 可空链表递归求和（`Node?` + 早返空判定） | ❌ 受限（见下） |
| g2 | 枚举运算与遍历 | ✅ |
| g3 | 回文判定（字符串/区间） | ✅ |
| g4 | 数据类分组 + `?.size ?: 0` | ✅ |
| g5 | `sealed` 树深度 + `maxOf` | ✅ |
| g6 | 位运算综合 | ✅ |

**5/6 通过**。唯一失败 g1 暴露的是「可空接收者的流敏感智能转换」：Kotlin `if (n == null) return 0`
之后把 `n` 智能转换为非空，而仓颉对 `if` 不做流敏感 narrowing（仅 `match`/`if let` 解构可），
属于需要数据流分析的硬限制，已纳入 §4 与 §5 路线。

## 4. 已知边界与风险

| 类别 | 现状 | 影响 |
|------|------|------|
| 可空接收者的流敏感智能转换 | 未支持 | `if (n == null) return` 后对 `n` 的非空访问无法直接翻译（仓颉 `if` 不做 narrowing），需改写为 `match`/`if let` |
| 返回集合的链式高阶 `map/filter/reduce/sorted` | 未支持 | 仓颉需 `iterator()...collect*<T>(...)` 且依赖显式元素类型，难以零类型信息可靠生成 |
| 默认参数 / 命名参数调用 | 默认值被丢弃、命名实参标签被跳过 | 省略实参的调用会编译失败 |
| 带参/枚举成员函数 | 未支持（带参项的实参被忽略） | 复杂枚举语义丢失（`sealed class` 子类已可） |
| 数值隐式提升 | 仓颉无 `Int64→Float64` 隐式转换 | 混合数值运算需源端显式统一类型 |
| 浮点打印格式 | 仓颉默认 6 位小数 `3.140000` | 期望输出需按此格式书写 |
| 字符串字符级下标 | 仓颉 `s[i]` 取字节 | 避免对字符串做字符级 `s[i]` |
| 协程 / 泛型函数声明 / 扩展函数 / 委托属性 | 未支持 | 超出当前子集 |

> 注：原表中的「`is` 类型判定」「二进制/十六进制/下划线字面量」已在本轮实现并移出风险表。

## 5. 下一步规划

P0 与 P1 已基本完成（见 §3）。后续按「实用价值 ÷ 实现成本」排序：

**P1 收尾（剩余项）**

1. **返回集合的高阶链**：`xs.map{}/filter{}` → `collectArrayList<T>(xs.iterator()...)`，
   需引入轻量类型推断（从声明/字面量回填元素类型）。当前以 `forEach`→`for` 规避。
2. **可空流敏感转换**：把 `if (n == null) return x` 之后的非空使用改写为 `match (n) { case Some(v) => ... }`，
   或在早返点后对接收者插入 `getOrThrow()`（需基本数据流分析）。

**P2（远期，工程化与规模）**

3. **默认/命名参数**：把 Kotlin 默认值映射为仓颉具名可选形参 `p!: T = v`，并在调用端按需补名。
4. **带参枚举与枚举方法**：`enum class E(val v: Int)` → 仓颉带参构造器 + 成员函数。
5. **多文件 / 包**：识别 `package`/`import`，输出对应仓颉包结构。
6. **诊断与回退**：对不支持构造给出带行号的清晰报错或「原样注释 + TODO」降级策略，避免整文件失败。
7. **规模化语料与基准**：把用例扩到 100+，纳入真实开源 Kotlin 片段做回归，统计「编译通过率/运行匹配率」趋势；
   持续扩充 §3.2 式的「未训练泛化抽样」以量化通用能力。
8. **格式化对齐**：可选接入 `cjfmt`，使产物风格与仓颉社区一致。

## 6. 维护提示

- 构建：`cd kotlin2cj && cargo build --release`（Rust edition 2024 / 1.85+）。
- 测试：`source /tmp/cangjie/envsetup.sh && python3 tests/run_tests.py`（写 `tests/log.md`）。
- 新增特性的标准做法：在 `node.rs` 增节点种类并补 `children_of`；在 `parser.rs` 加解析；
  在 `engine.rs` 的 `render` 加局部渲染规则；再加 `tests/cases/NN_xxx.{kt,expected}` 用例闭环验证。
