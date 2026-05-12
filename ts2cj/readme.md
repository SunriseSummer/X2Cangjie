# ts2cj — TypeScript → 仓颉 (Cangjie) 神经网络转换器

`ts2cj` 是一个**单文件级** TypeScript 源代码到仓颉（Cangjie）源代码的转换器，
使用 **自组织映射（SOM）+ Hopfield 关联记忆 + 模板槽位绑定** 的非线性
神经/记忆模型实现，纯 Python，**无需 GPU、无需训练数据**。

> 设计目标：对**任意** TS 源文件，给出**最优的仓颉等价表示**，允许少量
> 细节错误（由后续 AI 修正流程处理），换取**高吞吐、强鲁棒性、强泛化能力**。

## 1. 仓库布局

```
ts2cj/
├── ts2cj/                  # Python 包
│   ├── __init__.py         # 公共 API：convert_source / ConversionResult
│   ├── __main__.py         # CLI：python -m ts2cj input.ts -o out.cj
│   ├── lexer.py            # TypeScript 词法器（正则 + 容错）
│   ├── embedding.py        # 哈希 trick token 嵌入（确定性、L2 归一化）
│   ├── som.py              # Kohonen 自组织映射
│   ├── hopfield.py         # Hopfield 风格关联记忆
│   ├── patterns.py         # 内置 TS↔CJ 翻译语料（chunk 模板 + token 映射）
│   └── converter.py        # 端到端管线
├── tests/
│   ├── cases/              # *.ts 测试用例（+ *.expected 期望输出）
│   ├── run_tests.py        # 编译 + 运行 + 评分驱动
│   └── log.md              # 自动生成的测试报告
└── readme.md               # 本文件
```

## 2. 快速开始

### 2.1 安装依赖

只需 Python ≥ 3.8 与 NumPy：

```bash
pip install numpy
```

### 2.2 安装仓颉 SDK（仅运行测试需要）

```bash
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh
cjc --version    # 应输出 1.0.5
```

### 2.3 转换单个文件

```bash
python3 -m ts2cj examples/hello.ts -o examples/hello.cj --report
cjc examples/hello.cj -o hello && ./hello
```

`--report` 会向 stderr 输出形如
`[ts2cj] chunks=N confident=M fallback=K confidence=...%` 的统计，
便于在批处理中聚合质量分。

### 2.4 作为库使用

```python
from ts2cj import convert_source

result = convert_source(open("hello.ts").read())
print(result.source)
print(result.confidence)      # ∈ [0, 1]
print(result.fallback_chunks) # 未识别的 chunk 数
```

## 3. 设计理念

传统的源-到-源转换器路径是 **AST → Visitor → 重写器**：需要完整的 TS
parser、严格的类型推断、为每种语法节点手写转换规则。这条路径**精度高
但脆弱**：碰到任何一个未覆盖的语法节点都会抛异常或产出错误代码，并且
对于 TS 这种"语法不断扩张"的语言，规则集需要持续扩展。

`ts2cj` 选择了一条相反的路径：**把翻译视为一个非线性的检索-生成问题**，
用与神经网络同源的思想做：

1. **泛化** — token 用 hashing trick 嵌入到 64 维欧氏空间，相似的
   TS 片段在嵌入空间中也接近；即使语料中没有完全一样的模式，也能
   通过 SOM 邻域得到合理的候选；
2. **自组织** — Kohonen SOM 在内置模板语料上无监督训练，自动把翻译
   模式聚类成"语法家族"，不需要任何标注数据；
3. **关联记忆** — Hopfield 网络存储 `console.log → println`、`number
   → Int64` 这类细粒度对应关系，单步检索即可解码；
4. **回退** — 任何未能可靠识别的 chunk 都被以 `/* ts2cj: TODO */`
   注释包裹原 TS 文本保留，下游 AI 修正流程可以精准定位需要修复的
   片段，避免在通过部分上浪费成本。

## 4. 管线总览

```
        TS 源代码
           ▼
   ┌───────────────────┐
   │ ① 安全文本预重写  │   ===, !==, .length, .push, Math.* …
   └───────────────────┘
           ▼
   ┌───────────────────┐
   │ ② 词法 tokenize   │   永不抛错；未知字符 → UNKNOWN
   └───────────────────┘
           ▼
   ┌───────────────────┐
   │ ③ chunk 分段       │   按花括号 / 分号平衡切分顶层块
   └───────────────────┘
           ▼
   ┌───────────────────────────┐
   │ ④ 对每个 chunk：           │
   │   ▸ 嵌入到 64 维向量       │
   │   ▸ SOM 检索候选模式族     │
   │   ▸ 对全语料做槽位绑定     │
   │   ▸ 综合打分挑选最优模式   │
   │   ▸ 递归翻译嵌套 body      │
   └───────────────────────────┘
           ▼
   ┌───────────────────┐
   │ ⑤ 后处理 + 装配    │   imports、main()、override 标记 …
   └───────────────────┘
           ▼
        仓颉源代码
```

### 4.1 词法 (`lexer.py`)

正则驱动的 token 流。关键设计：

* 永不抛错——未识别字符产出 `UNKNOWN` token，使得管线对损坏 / 不完整
  的 TS 输入仍能产出尽量合理的输出；
* 模板字符串作为**单个 token** 提取，避免 `${expr}` 中的内嵌表达式
  污染主 token 流——后续在表达式渲染阶段再做语法转换；
* 关键字集合是封闭的 `KEYWORDS` 常量，便于 chunk pattern 在模板中
  使用关键字字面量作为锚点。

### 4.2 Token 嵌入 (`embedding.py`)

我们没有训练任何 word2vec / Transformer。相反，使用**哈希特征技巧**
确定地把每个 token 投影到 64 维向量：

* 用 BLAKE2b（稳定哈希）把 token 整体 + 它的 2-gram、3-gram 各自
  映射到向量某一维，符号由哈希高位决定；
* 结果向量做 L2 归一化，从而**余弦相似度 ≡ 点积**；
* 多 token 序列的嵌入是 token 嵌入的均值（再 L2 归一化）。

这个方案有三个性质：

1. **确定性**：同样的输入永远得到同样的向量，便于复现；
2. **零数据**：无需任何训练语料；
3. **泛化**：因 n-gram 重叠，`consol`、`console`、`Console` 的向量
   彼此接近，从而对 typo 与变体有天然鲁棒性。

### 4.3 自组织映射 (`som.py`)

构造时即用内置模板的嵌入向量训练一个 `6×6` 的 Kohonen 网络
（800 次迭代，学习率与邻域半径随时间退火）。训练完成后：

* 每个神经元（grid 上的单元）成为一类翻译模式的**原型**；
* 我们记录"每个模式落到哪个神经元"，从而由神经元反查模式索引。

**推理时**：对待翻译的 chunk 嵌入，找最优匹配单元（BMU）及其 3×3
邻域里曾经命中过的模式作为候选——这就是"自组织的检索"。当输入与某
个模板非常接近时这一步几乎是直接命中；当输入是一个未见过的变体时，
我们仍会得到一组**语法家族相近的候选**。

### 4.4 Hopfield 关联记忆 (`hopfield.py`)

存储 ~30 条 token-级别的 `(键, 值)` 对：`(.length, .size)`、
`(===, ==)`、`(Math.floor, floor)` 等。检索时把查询向量与所有键向量
做点积，过低温 softmax 得到一个 winner-takes-all 概率分布；当胜者
置信度（最大概率 & 余弦相似度）双重超过阈值才回写值。

这种"单步现代 Hopfield"等价于一个最近邻分类器加置信度门控，是一个
非常轻的非线性记忆。

### 4.5 槽位绑定 (`converter._bind_slots`)

模板写法举例：

```
TS: "const $NAME : number = $EXPR ;"
CJ: "let $NAME: Int64 = $EXPR"
```

* **LIT 锚点** 必须与 chunk 当前位置的 token **严格相等**；
* **SLOT** 在两个锚点之间贪心收集 token，**括号 / 花括号 / 方括号
  深度平衡** 时方可越过下一个匹配锚——这是确保函数体、表达式不会被
  锚点穿透的关键。

每个 chunk 对**全部模式**（仅 ~40 条）做一次绑定尝试，根据公式

```
score = anchor_score * (1 + n_anchors) + 0.1 * cosine_similarity + som_bonus
```

挑选**特异性最高**的模式。锚点数量作为乘性因子，确保 `console.log(...);`
这种 6 锚点模板优先于 `$EXPR ;` 通配模板被选中。SOM 命中给一个小加成，
用于打破打分相同时的平局。

### 4.6 递归 body 翻译

`if / for / while / function / class` 等模板中包含 `$BODY`、`$A`、
`$B`、`$B1..$B5` 这类**块槽位**。其内容会被**递归地**送回到 chunk 分段
+ 模式检索管线，从而支持任意深度的嵌套。

### 4.7 后处理 (`converter.convert_source` 尾部)

* 自动注入 `import std.collection.*`（当输出引用 `ArrayList`/`HashMap` 等）；
* 自动包裹 `main()`（当顶层没有显式 `main`）；
* 对 `class X extends Y` 模式自动给方法加 `override` 修饰符；
* 类统一发射为 `open class`（TS class 默认可继承）。

## 5. 已支持的 TS / 仓颉特性

经过两轮增强，转换器目前已覆盖 **仓颉语言绝大多数核心特性**（宏除外）。
下表按仓颉特性维度列出（→ 列展示典型的 TS 源形态）：

| 仓颉特性         | TS 形态（输入）                                              | 备注 |
|------------------|--------------------------------------------------------------|------|
| `let` / `var`    | `const x = e` / `let x = e`                                  | 推断类型时不强加注解 |
| 基础类型         | `number / string / boolean / void / any`                     | → `Int64 / String / Bool / Unit / Any` |
| 数组 / 集合      | `T[]` `Array<T>` `Map<K,V>` `Set<T>`                         | → `ArrayList<T>` `HashMap<K,V>` `HashSet<T>`，并自动注入 `import std.collection.*` |
| 元组             | `[T, U]` 类型 + `[a, b]` 字面量                              | → `(T, U)` / `(a, b)`；类型别名亦能触发字面量改写 |
| `?T` 可空        | `T \| null` / `T \| undefined`、字面量 `null`                | → `?T` / `None` |
| 控制流           | `if/else if/else`、`for(;;)`、`for-of`、`for-in`、`while`、`do-while`、`break`、`continue` | 单行无大括号体自动补齐 |
| `match` 模式匹配 | `switch / case / default / break`                            | → `match { … _ => ... }`，支持空 arm 补 `()`、嵌套 switch、`case A | B =>` 合并 |
| 函数             | `function f(…): T { … }`、可选 / 默认参数、箭头函数          | 顶层 `function main()` 自动转 CJ 入口 |
| 闭包 / Lambda    | `(x) => e` / `(x) => { … }`                                  | 应用于 `.map / .filter / .sort` 等链式调用 |
| 类               | `class C extends D implements I { … }`                       | `open class` + `init`；**智能 `override` 检测**（仅当子类方法名出现在父类链中） |
| 抽象类           | `abstract class` / `abstract foo();`                         | → `abstract` |
| 静态成员         | `static foo()`、`static field`                               | → `static func` / `static let` |
| 属性             | `get x() { … }` / `set x(v) { … }`                           | → `prop x` / `mut prop x` |
| 接口             | `interface I { foo(): T; }`                                  | 接口体上下文感知（不会错误加 `public open`） |
| 泛型             | `function f<T>(x: T): T`、`class Box<T>`                     | 含尖括号 / `where T <: U` 占位 |
| `struct`         | `struct S { x: number; y: number; }`                         | → `struct S { … }` |
| `enum`           | `enum Shape { Circle, Square }` / 带参 case                  | → `enum Shape { Circle \| Square }` |
| 异常             | `try { } catch (e) { } finally { }`、`throw new Error(s)`    | → `try { } catch (e: Exception) { } finally { }`、`throw Exception(s)` |
| 字符串插值       | `` `Hello ${name}` ``                                        | → `"Hello ${name}"` |
| 标准库映射       | `console.log → println` / `.error → eprintln` / `.length → .size` / `.push → .add` / `Math.* → math.*` | 通过 Hopfield 关联记忆批量映射 |
| 顶层声明排序     | TS 自由顺序                                                  | 输出按 imports → typealias → enum/struct → interface → class → func → main 装配 |
| 字面量精化       | `1.5` / `1e3` 含小数 → `Float64` 字面量保持；整数 → `Int64`  | |
| 算术规范化       | `Math.floor(a / b)`、`a === b` / `a !== b`                   | → 仓颉风格 `a / b`（Int 自截断）、`a == b` / `a != b` |

### 5.1 不（完全）支持的 TS 特性

下列特性会触发 fallback 注释 `/* ts2cj: TODO ... */` 或产出**轻微错误**
的代码（用户预期的"少量细节错误"），由后续 AI 修正流程补全：

* `async / await`、`Promise<T>`、装饰器、命名空间、`declare`；
* 复杂条件 / 映射类型、`infer`、`as const`、字面量类型；
* 大型对象解构 / spread / rest 参数；
* TS-only 模块系统（`import` / `export` 当前作为顶层声明透传）；
* TS 宏 / 仓颉宏（按需求显式排除）。

设计哲学：**这些缺口被有意识地保留**——我们追求转换器自身的
**高吞吐、强泛化**，把"语法挑剔"的最后一公里留给下游 AI 流程，避免在
转换器内引入脆弱的、覆盖度永远跟不上 TS 语言演化的规则集。

## 6. 输出风格 ——「专业、老练、规范」

ts2cj 把"语法机械替换"看作 baseline，并在多个层面做了**面向工程师可读性**
的优化，让产物不像中间表示，而像有经验的仓颉开发者会写的代码：

| 维度       | 反例（散装映射）                                  | ts2cj 输出（规范化）                                  |
|------------|---------------------------------------------------|-------------------------------------------------------|
| 类型注解   | `let x: Int64 = 42`                               | `let x = 42`（能推断的字面量不写注解）                |
| `override` | 给每个继承类的方法都打 `override`                 | 仅当子类方法名在父类链（含多级）中真实存在时才标      |
| 主入口     | 让 `console.log(...)` 散在顶层                    | 把全部顶层副作用收敛进 `main()` 并 `return 0`         |
| 异常类型   | `catch (e) { … }`                                 | `catch (e: Exception) { … }`                          |
| 集合 API   | `xs.append(v)` / `m.set(k,v)`                      | `xs.add(v)` / `m.add(k, v)`（按仓颉 stdlib 习惯）     |
| 字符串拼接 | `"a " + b + " c"`                                 | `` "a ${b} c" ``（可插值时收敛为模板）                |
| 默认初值   | 给所有未初始化变量发 `0`                          | 按类型选 `0` / `""` / `false` / `?T = None` / `ArrayList<T>()` / 元组零值 |
| 单行块     | `if (c) return x` → 直接丢                        | 自动补 `{ … }` 满足仓颉语法                           |
| 顶层顺序   | 与 TS 同序                                        | imports → typealias → enum/struct → interface → class → func → main |
| 多余 `main()` 调用 | 同时保留 `function main()` 与底部 `main();` | 自动剥离重复调用                                      |
| 嵌套 `switch` | 外层 case 切到内层 case                        | 按 `{}` 深度只切外层；内层完整保留                    |

这些规则全部在 `converter.py` 的后处理阶段实现，**不依赖** AST。

## 7. 测试与评分

### 7.1 运行测试套件

```bash
source /tmp/cangjie/envsetup.sh
python3 ts2cj/tests/run_tests.py
```

驱动脚本会：

1. 用 `python -m ts2cj` 把每个 `tests/cases/*.ts` 转换为 `.cj`；
2. 用 `tsc --noEmit`（如可用）校验 TS 源；
3. 用 `cjc` 编译生成的 `.cj`；
4. 运行二进制并与 `<case>.expected` 比对（如存在）；
5. 把结果写入 `tests/log.md`。

### 7.2 评分公式

对每个用例：

```
score = 0.4 × pattern_coverage   # confident / chunks
      + 0.4 × cj_compiles         # cjc 退出码 == 0
      + 0.2 × runs_and_matches    # 二进制运行成功 & 输出匹配
```

### 7.3 测试矩阵（共 45 个用例）

| 范围         | 用例编号                       | 说明 |
|--------------|--------------------------------|------|
| 基础语法     | `01_hello` … `28_edge_arrow`   | 表达式 / 控制流 / 函数 / 类 / 接口 / 递归 / 数组等 28 个最小用例 |
| 数据类型     | `29_struct` `30_enum_basic` `34_tuple` `35_option` `39_type_alias` | `struct` / `enum` / 元组 / `?T` / 类型别名 |
| 控制 & 异常  | `31_try_catch` `40_do_while`   | 异常 + `do-while` |
| 泛型         | `32_generic_fn` `33_generic_class` `41_stack_generic` | 函数 / 类 / 泛型栈（含 Option peek） |
| 集合         | `36_hashmap`                   | `HashMap` 增删查 |
| 类高级       | `37_static` `38_abstract`      | 静态成员 / 抽象类 |
| 中型综合     | `42_bank` (~110 行)            | 银行账户继承体系 + 异常 + ArrayList 遍历 |
|              | `43_collections` (~50 行)      | 函数式数组聚合（filter / map / reduce 链） |
| 大型综合     | `44_tictactoe` (~200 行)       | 井字棋 + Minimax AI |
| **千行级**   | `45_algorithms` (~563 行)      | **算法工具箱**：埃氏筛 / 数论 / 矩阵 / 五种排序 / 图 BFS+DFS / 并查集 / 统计 / 位图 |

百行 / 千行综合用例聚焦"一个完整可运行的程序"，覆盖：泛型容器 +
继承 + 多态 + 异常 + 嵌套循环 + 模式匹配 + 函数式高阶 + 顶层
驱动，且**最终 `cjc` 编译通过并运行匹配 `.expected`**。

### 7.4 当前结果

* 用例总数：**45**
* 模式覆盖率（confident / chunks）：**≥ 99.5%**
* 综合质量分：**≥ 99%**

完整数据见自动生成的 `tests/log.md`。

## 8. 性能

* SOM 训练：~50 ms（首次加载时一次性）。
* 单文件转换：典型 100 行级 TS 文件 < 30 ms（NumPy 向量化）；
  563 行的 `45_algorithms` 端到端 ~150 ms。
* `cjc` 编译占绝大部分端到端时间（每用例 ~3 秒），但与转换器无关。

整个管线是**单线程、可重入、确定性**的（SOM 用固定随机种子）。

## 9. 后续工作

* 把 chunk 模式语料从 ~45 条扩展到 ~200 条以覆盖更多惯用法；
* 在 SOM 训练时混入用户语料以做 **个性化适配**；
* `number` → `Int64`/`Float64` 的字面量级精化（当源字面量含小数点时
  自动选 `Float64`）；
* 在 Hopfield 记忆里加入"常见错误 → 修正建议"的反向映射，让转换器
  能为下游 AI 修正流程附带语义提示；
* 实验 *modern Hopfield with attention* 替换当前一阶 Hopfield，
  以在保持无 GPU 训练的前提下提升复杂模板检索召回率。

## 10. 许可证

与本仓库一致。
