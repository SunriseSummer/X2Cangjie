# kotlin2cj 现状评估与下一步规划

> 本文给出 kotlin2cj（Kotlin → 仓颉源到源翻译器）截至当前迭代的能力评估、
> 测试现状、已知边界与后续路线图。配套基线见 [`tests/log.md`](./tests/log.md)，
> 支持的语言子集见 [`Readme.md`](./Readme.md)。

## 1. 一句话现状

kotlin2cj 已从「基础语法演示」推进到「**可翻译并端到端跑通中小规模实用 Kotlin
程序**」的阶段：覆盖控制流、函数（含嵌套/递归）、类、枚举、集合、异常、位运算、
区间成员检查、常见空安全惯用法等特性，**57 个端到端用例全部翻译 → `cjc` 编译 →
运行输出逐字节匹配（57/57/57）**。

## 2. 测试现状

| 指标 | 数值 |
|------|------|
| 端到端用例总数 | 57 |
| 翻译成功 | 57/57 |
| 仓颉 `cjc` 编译通过 | 57/57 |
| 运行输出匹配 | 57/57 |
| 验证工具链 | Cangjie SDK 1.0.5（cjnative，x86_64-linux） |

用例覆盖维度：

- **基础与控制流**：变量、运算符、`if/when/while/do-while/repeat/for`、`break/continue`、嵌套循环。
- **区间与成员**：`..`/`until`/`downTo`/`step`、`in`/`!in`（区间转比较、集合转 `contains`）。
- **函数**：块体/表达式体、递归、嵌套局部函数、顶层全局 `val`。
- **集合**：List/Map/Set 字面量与泛型、下标读写、嵌套集合、`forEach`、`map[k] ?: d`。
- **类型抽象**：类（主构造器/方法/多类协作）、`data class`、`enum class`（+`@Derive[Equatable]`）。
- **异常**：`try/catch/finally`、`throw`。
- **位运算**：`and/or/xor/shl/shr`。
- **规模**：筛法（50 以内素数）、Collatz 最长链、3×3 网格与分组映射、库存/状态机等综合程序。

运行方式：

```bash
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh
cd kotlin2cj && python3 tests/run_tests.py   # 结果写入 tests/log.md
```

## 3. 本轮新增能力

相对上一基线（34/34，仅基础子集），本轮新增：

1. **位运算中缀函数** `and/or/xor/shl/shr/ushr` → 仓颉 `& | ^ << >>`（解析为正确优先级层）。
2. **成员检查** `in` / `!in`：右操作数为区间时展开为 `lo <= x && x <= hi` 等比较；
   为集合时转 `coll.contains(x)`；`!in` 取反。
3. **异常处理** `try/catch/finally` 与 `throw`（catch 形参进入作用域）。
4. **`forEach`**：`xs.forEach { it -> ... }` / `xs.forEach { ... }`（隐式 `it`）→ `for (it in xs) { ... }`，
   规避了仓颉链式高阶函数对元素类型/`collect*` 的强依赖。
5. **隐式 lambda 参数 `it`**：无显式形参且引用 `it` 的 lambda 自动补 `it =>` 形参头。
6. **`enum class`**：具名常量枚举 → 仓颉 `enum` + `@Derive[Equatable]`（自动注入 `import std.deriving.*`），
   支持 `==` 比较与 `when`/`match` 匹配（`Type.X` 限定与裸构造器名均可）。
7. **顶层全局 `val`**：置于 `main` 之前作为全局声明，供各函数引用。
8. **嵌套局部函数**：函数体内 `fun` 直接落到仓颉嵌套函数。
9. **空安全惯用法** `map[k] ?: default` → `map.get(k) ?? default`（下标读取在仓颉抛异常、
   `get` 返回 `Option` 才能 coalesce）。
10. **集合/字符串方法映射补充**：`removeAt(i)`→`remove(at: i)`、`startsWith/endsWith/contains/isEmpty` 直通。

实现仍遵循原有 SOC（自组织临界）管线：词法 → 递归下降建图 → worklist 松弛渲染，
新特性以新增节点种类（`Try`/`Throw`/`Enum`）与局部渲染规则的方式接入，未改动核心引擎。

## 4. 已知边界与风险

| 类别 | 现状 | 影响 |
|------|------|------|
| 返回集合的链式高阶 `map/filter/reduce/sorted` | 未支持 | 仓颉需 `iterator()...collect*<T>(...)` 且依赖显式元素类型，难以零类型信息可靠生成 |
| 默认参数 / 命名参数调用 | 默认值被丢弃、命名实参标签被跳过 | 省略实参的调用会编译失败 |
| `is` 类型判定 / 智能转换 | 未支持 | 含 `is` 的 `when`/`if` 无法翻译 |
| 带参/`sealed` 枚举、枚举成员函数 | 未支持（带参项的实参被忽略） | 复杂枚举语义丢失 |
| 二进制/十六进制/下划线数字字面量 | 词法仅识别十进制 | `0b1010`/`0xFF`/`1_000` 解析错误 |
| 数值隐式提升 | 仓颉无 `Int64→Float64` 隐式转换 | 混合数值运算需源端显式统一类型 |
| 浮点打印格式 | 仓颉默认 6 位小数 `3.140000` | 期望输出需按此格式书写 |
| 字符串字符级下标 | 仓颉 `s[i]` 取字节 | 避免对字符串做字符级 `s[i]` |
| 协程 / 泛型函数声明 / 扩展函数 / 委托属性 | 未支持 | 超出当前子集 |

## 5. 下一步规划

按「实用价值 ÷ 实现成本」排序：

**P0（近期，扩大可翻译程序面）**

1. **数字字面量增强**：词法支持 `0x`/`0b`/下划线分隔，去后缀后正确归一为仓颉字面量。
2. **`is` 类型判定**：`x is T` → 仓颉 `x is T`；`when` 中 `is T -> ...` → `case _: T =>` 或类型模式。
3. **默认参数**：把 Kotlin 默认值映射为仓颉具名可选形参 `p!: T = v`，并在调用端按需补名。
4. **更多字符串/集合方法**：`substring`→区间下标、`split/joinToString/indexOf`（注意 `indexOf` 返回 `Option`）、
   `first/last/isNotEmpty`、`MutableList.removeAt/clear`。

**P1（中期，提升地道度与覆盖）**

5. **返回集合的高阶链**：`xs.map{}/filter{}` → `collectArrayList<T>(xs.iterator()...)`，
   需引入轻量类型推断（从声明/字面量回填元素类型）。
6. **`data class` 增强**：自动派生 `toString`/`==`（`@Derive`），支持解构声明 `val (a, b) = p`。
7. **带参枚举与枚举方法**：`enum class E(val v: Int)` → 仓颉带参构造器 + 成员函数。
8. **空安全细化**：`?.` 安全调用、`?.let{}`、可空链路的 `Option` 语义对齐。

**P2（远期，工程化与规模）**

9. **多文件 / 包**：识别 `package`/`import`，输出对应仓颉包结构。
10. **诊断与回退**：对不支持构造给出带行号的清晰报错或「原样注释 + TODO」降级策略，避免整文件失败。
11. **规模化语料与基准**：把用例扩到 100+，纳入真实开源 Kotlin 片段做回归，统计「编译通过率/运行匹配率」趋势。
12. **格式化对齐**：可选接入 `cjfmt`，使产物风格与仓颉社区一致。

## 6. 维护提示

- 构建：`cd kotlin2cj && cargo build --release`（Rust edition 2024 / 1.85+）。
- 测试：`source /tmp/cangjie/envsetup.sh && python3 tests/run_tests.py`（写 `tests/log.md`）。
- 新增特性的标准做法：在 `node.rs` 增节点种类并补 `children_of`；在 `parser.rs` 加解析；
  在 `engine.rs` 的 `render` 加局部渲染规则；再加 `tests/cases/NN_xxx.{kt,expected}` 用例闭环验证。
