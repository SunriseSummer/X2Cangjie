# go2cj-new — 变更历史

## v0.3.11 — 循环迭代扩张 130→140 例 + 回退稳健性修复 (2026-05-17)

### 指标（cjc 1.0.5）

| 指标 | v0.3.10 (130 例) | **v0.3.11 (140 例)** |
|---|---|---|
| cjc 编译 | 130/130 (100%) | **140/140 (100%)** |
| 运行匹配 | 129/130 (99.23%) | **139/140 (99.29%)** |
| 唯一遗留 | `26_float_math` `%.2f` 输出格式 | 同左（与本轮无关） |

本轮新增 `131_*`~`140_*` 共 10 个大小混合算法用例。首轮回归暴露
tuple 短变量、索引自增、`len(arr[i])`、索引 append 与若干 CHIME
误路由问题；补齐最小确定性回退后，新增 10 例达到 **10/10 编译通过 +
10/10 运行匹配**。

### 转换器净增量（`converter.py`）

* `len(...)` 回退规则支持索引表达式（`len(xs[i])` → `xs[i].size`）。
* 新增 `arr[idx] = append(arr[idx], v)` → `arr[idx].add(v)`。
* 新增索引自增/自减回退：`arr[i]++` / `arr[i]--`。
* tuple 短变量归一化改为双分支：
  - 标量二元：`a, b := x, y` → `var a = x; var b = y`；
  - 其余形态：保持 `var (a, b) = ...`。
* `_FRAGILE_IDIOM_PROBES` 新增三类探针：
  - 索引自增/自减；
  - `return arr[i]` 索引返回；
  - `len(arr[i])` 索引长度。

---

## v0.3.10 — 循环迭代扩张 120→130 例 + 三类确定性修复 (2026-05-17)

### 指标（cjc 1.0.5）

| 指标 | v0.3.9 (120 例) | **v0.3.10 (130 例)** |
|---|---|---|
| cjc 编译 | 120/120 (100%) | **130/130 (100%)** |
| 运行匹配 | 119/120 (99.17%) | **129/130 (99.23%)** |
| 唯一遗留 | `26_float_math` `%.2f` 输出格式 | 同左（与本轮无关） |

本轮新增 `121_*`~`130_*` 共 10 个大小混合算法用例（prefix sums、
two-sum、row sums、histogram、matvec、subset sum、sliding window、
range diff、grid paths with blocks）。首次回归出现 4 个编译失败与 1
个运行偏差；针对新暴露形状做最小确定性修复后，新增 10 例达到
**10/10 编译通过 + 10/10 运行匹配**。

### 转换器净增量（`converter.py`）

* `make([]T, SIZE)` / `make([][]T, SIZE)` 的 `SIZE` 匹配放宽到可包含
  `len(xs)` 一类括号表达式，避免误生成 `len ( xs, {_ => ...})`。
* 新增 tuple return 归一化：`return a, b` → `return(a, b)`，修复
  二元返回函数在 Cangjie 侧的语法错误。
* `_FRAGILE_IDIOM_PROBES` 新增两类探针（强制走确定性回退）：
  - 双索引算术表达式（`xs[i] + xs[j]`）；
  - Go while 形态循环（`for cond { ... }`），避免 CHIME 误路由为 `if`。

---

## v0.3.9 — 循环迭代扩张 50→120 例 + 14 类新 fragile 探针 (2026-05-16)

### 指标（cjc 1.0.5）

| 指标 | v0.3.8 (50 例) | **v0.3.9 (120 例)** |
|---|---|---|
| cjc 编译 | 50/50 (100%) | **120/120 (100%)** |
| 运行匹配 | 49/50 (98.00%) | **119/120 (99.17%)** |
| 唯一遗留 | `26_float_math` `%.2f` 输出格式 | 同左（与本轮无关） |

按"循环迭代优化"方法连续追加 7 轮新用例（每轮 10 例，小/中/大
混合），共 70 例。前 5 轮在新用例暴露 CHIME 错配时持续打磨
转换器；最后 2 轮（`101_*`~`120_*`）**完全不改转换器**，仍
20/20 全部通过——证明确定性 spine 已具备真正的泛化能力。

### 每轮规模与发现的 CHIME 模式失效

| 轮次 | 新增范围 | 主要新形状 | 修复的 CHIME 模式失效 |
|---|---|---|---|
| R1 | 51-60 | factorial / sum_range / bubble_sort / prime_sieve | 多维 slice 返回类型、形参重赋值 |
| R2 | 61-70 | abs / collatz / point_dist / matmul | `return -x`、`Println(call(LIT))`、`Point{X:0,Y:0}` |
| R3 | 71-80 | gcd_rec / insertion_sort / levenshtein | `j := i-1`、`cost = 0` |
| R4 | 81-90 | clamp / merge_sorted / coin_change | 3 字段 struct、`append(xs,v)`、`a,b := f()`、`dp[i-c]`、`if c<=i` 误为 while |
| R5 | 91-100 | quicksort / lis / pair_slice | `best = dp[i]` 角色反转、`[]Pair{{…}}` |
| R6 | 101-110 | filter_positive / pascal / knapsack | （无新修复）10/10 直接通过 |
| R7 | 111-120 | sum_product / ackermann / floyd | （无新修复）10/10 直接通过 |

### 转换器净增量（`converter.py`）

* `_FUNC_SIG_RE`：放宽对 `[][]T` 等多维 slice 返回类型的接纳。
* `_shadow_mutated_params`：新增 post-assembly 段，扫描每个
  函数体内对形参的 `=` / `OP=` 赋值，自动重命名形参并注入
  `var p = p_param` 影子（Cangjie 形参默认 immutable）。
* `_FRAGILE_IDIOMS` 增加 **14** 类形状探针（强制走确定性回退）：
  自更新 `x = x op …`、`x := y[i]` 索引短变量、`return …
  (cmp) …` 布尔比较、C-style for 步长 `j = j + i`、`return EXPR
  含 +-*/%`、`Println(call())`、struct keyed literal、`x := y
  op …`、`x = INT`、`type T struct {…}` 3+ 字段、`append(…)`、
  tuple `a, b := f()`、`arr[i±j]` 算术下标、`arr[i] cmp X`、
  `if ID cmp ID`、`x = arr[i]` 普通赋值、`[]T{{…}}`。
* `_rewrite_go_idioms` 新增确定性改写：
  - `type T struct { F1 T1; F2 T2; F3 T3 }` → 多字段 `open class T`
    （结合现有 `synthesize_class_inits` 自动合成 init）
  - `Type{F1: v1, F2: v2}` → `Type(v1, v2)` 位置参数构造
  - `append(xs, v)` / `xs = append(xs, v)` → `xs.add(v)`
  - `a, b := f(x)` → `var (a, b) = f(x)` 元组解构
  - `[]T{{F:v,…}, {F:v,…}}` → `ArrayList<T>([T(v,…), T(v,…), …])`

### 收敛判据

R6 + R7 连续两轮"零修改"通过率 = **100%**（20/20 新用例 cjc 编译
成功且运行输出与 Go 一致），满足"高泛化"标准。总用例规模
从 50 扩至 120，cjc 编译率始终保持 100%，运行匹配率从 98.00%
升至 99.17%。

---

## v0.3.8 — 确定性 Go 习语改写器 + 易脆形状兜底 (2026-05-16)

### 指标（cjc 1.0.5，测试用例扩到 50 例）

| 指标 | v0.3.7 (45 例) | **v0.3.8 (50 例)** |
|---|---|---|
| 模式覆盖 | 100% | 67.93% |
| cjc 编译 | 45/45 (100%) | **50/50 (100%)** |
| 运行匹配 | 44/45 (97.78%) | **49/50 (98.00%)** |
| 综合质量分 | 99.56% | 86.83% |

`tests/cases/` 在本轮迭代中加入 5 个真实算法用例（`46_knapsack`
0/1 背包、`47_binary_search` 二分查找、`48_lcs` 最长公共子序列、
`49_quicksort` 快排、`50_knapsack_full` 多函数混合背包），
首次跑出来时只有 44/50 能编译、约 40/50 能运行匹配。这些用例
集中暴露了 CHIME 关联记忆的一类系统性弱点：**当训练集里没有
"该形状的确切配对"时，CHIME 会按结构相似度检索一条来自完全
不同程序的模板，让占位符按位置对齐而把变量绑定搞错**（典型例：
`dp[w] = max(dp[w], dp[w-weights[i]]+values[i])` 被映射成
`i[dp] = max(i[dp], i[dp-w[weights]]+values[weights])`）。

### 改动 — `converter.py`

* **`_rewrite_go_idioms` 全新一轮确定性改写器**：对一组高频、
  形状稳定、CHIME 又抓不住的 Go 习语做"模板无关"的转写，
  正确性来自语法形状本身而非模式匹配。覆盖：

  | Go 习语 | Cangjie 输出 |
  |---|---|
  | `make([]T, n)` | `ArrayList<T>(n, {_ => 0})` |
  | `make([][]T, n)` | `ArrayList<ArrayList<T>>(n, {_ => ArrayList<T>()})` |
  | `[]T{a,b,c}` | `ArrayList<T>([a, b, c])` |
  | `[][]T{{…},{…}}` | `ArrayList<ArrayList<T>>([ArrayList<T>([…]),…])` |
  | `for _, v := range xs {` | `for (v in xs) {` |
  | `for i := range xs {` | `for (i in 0..(xs).size) {` |
  | `for i, v := range xs {` | `for (i in 0..(xs).size) { let v = (xs)[i]; …` |
  | `for i := 0; i < n; i++ {` | `for (i in 0..n) {` |
  | `for i := 0; i*i <= n; i++ {` | `var i = 0; while (i*i <= n) { … i++ }` |
  | `a, b = b, a` | `let __tmp_swap = a; a = b; b = __tmp_swap` |
  | `var x: Float64 = 10` | `var x: Float64 = 10.0` |
  | `fmt.Println(a, b)` | `println("${a} ${b}")` |
  | `fmt.Printf("…%s…%d\n", a, b)` | `println("…${a}…${b}")` |
  | `len(x)` | `x.size` |
  | `func F() {…}` | `func F(): Unit {…}` |

  其中 `fmt.Println` / `fmt.Printf` 多参数走括号平衡解析
  （`_balanced_call_rewrite`），保证 `fmt.Println(foo(x, y), z)`
  也能正确切分。`for init;cond;step` 的非范围形式通过
  `__cstyle_step__:` 标记把 step 嵌到 while 循环体末尾，
  由 `_resolve_cstyle_steps` 在装配后扫描配对的 `}` 注入。

* **`_has_fragile_idiom` — 易脆形状兜底**：CHIME 命中（confident）
  也不一定代表正确。对于经验上**容易模板错位**的形状（双下标
  `dp[i][j]`、单下标 `arr[idx] = val`、`}else{`、3+ 参数函数调用、
  `a, b = b, a`、`fmt.Println(a, b)`、`fmt.Printf(...)`、`make`、
  范围 `for ... range`、C-style for、`var x = INT_LIT` 无类型注解）
  强制走确定性 fallback，绕开 CHIME 检索。这一改动是把 cjc 编译率
  从 44/50 推到 50/50 的关键。

* **`_dedup_var_in_block`**：相邻两段 C-style `for i :=` 展开为
  `var i = …; while (…) { … i++ }` 后会出现同作用域 `var i`
  二次声明 → Cangjie `redefinition`。新增装配后处理：按花括号深度
  跟踪同名声明，二次起追加 `_2/_3` 数字后缀，同时把同一作用域
  内之后的引用同步重命名。

* **`_rewrite_func_signature` 默认 `: Unit`**：原本无返回类型的
  Go 函数（如 `func quicksort(...)`）转译时省略 Cangjie 返回类型，
  导致**递归函数推断失败**（cjc 报 "unable to infer return type"）。
  现在统一显式注入 `: Unit`，对非递归 void 函数也无副作用。

* **`make([][]T, n)` 元素类型与 `make([]T, n)` 对齐**：两者都用
  `ArrayList`，保证 `dp[i] = make([]T, m+1)` 这种二维 DP 的行
  赋值不会因为 `Array` vs `ArrayList` 元素类型不匹配而拒绝。

* **`x := expr` 在非行首位置也改写**：之前的 `^\s*IDENT\s*:=`
  只识别 chunk 开头；CHIME 把 `for (row in matrix) { sum := 0 …`
  这类合并在一行的语句聚成一个 chunk 后，内部的 `sum := 0` 无法
  改写。改成 `(^|[;{\s])IDENT\s*:=` 后，行内短变量也能转成
  `var sum = 0`。

### 唯一未对齐用例

`26_float_math`：Go `fmt.Println(area)` 输出 `12.56`，Cangjie
`println(area)` 输出 `12.560000`。属于两种语言对 `Float64` 默认
字符串化的精度差异，非转换器可修复——除非在 `fmt.Println(float)`
位置额外注入一个剥尾零的辅助函数，但这与"最小确定性改写"原则
冲突且会牵涉到精度选择的语义假设，故保留现状。

---

## v0.3.7 — 字符串插值感知 + 占位符常量保持 + 编辑距离归一化 (2026-05-16)

### 指标（cjc 1.0.5）

| 指标 | v0.3.6 | **v0.3.7** |
|---|---|---|
| 模式覆盖 | 100% | **100%** |
| cjc 编译 | 45/45 | **45/45 (100%)** |
| 运行匹配 | 27/45 | **44/45 (97.78%)** |
| 综合质量分 | 92.00% | **99.56%** |

唯一未对齐的 `26_float_math` 是 Go 与 Cangjie 对 `Float64`
缺省字符串化精度差异（Go `12.56` / Cangjie `12.560000`），
属于语言语义级别的格式差异，不在转换器修复范围内。

### 改动 — `anonymize.py`

* **字符串字面量分级**：原本所有 `"..."` 都归 `STR` 占位，导致
  Cangjie 端 `"${id} ${val}"` 形式的插值模板无法绑定外部
  `ID*`；现在 `_classify` 分三类：
  - 含 `${…}` 的插值字符串 → `keep`，由 `_rewrite_interp`
    把内部标识符同样化为 `ID*`，反向阶段再替换回来；
  - 极短的常量"粘合"字符串（`" "`/`""`/`"\\n"`/`": "`/`", "` 等）
    → `keep`，避免 `println("${x}" + " " + STR0)` 模板里的
    `" "` 也被吞为 `STR1` 然后被占位符子集校验拒掉；
  - Go printf 格式串（含 `%`）→ `keep`，避免不同 `Printf` 调用
    全部碰撞到同一个 `STR0` 桶造成模板互相覆盖。
* **微小整数常量保持**：`0` / `1` / `-1` 不再 `NUM` 占位 —— 因为
  它们多数情况下是 `i += 1` / `count = 0` 形态的常量胶水；
  曾经导致 `n++` → `n += NUM1` 因子集校验把 `NUM1=1` 拒在
  query 之外而无法触发的现象消失。
* **`_normalize_chunk_tokens`**：剥离 chunker 在 `_inject_semis`
  阶段塞进 `}` 前的尾分号 (`; }` → `}`)，保证 chunk 与原始训练
  对的锚点一致 —— 之前 `for ID0 < NUM0 {…; ID0 ++ ; }` 因末尾
  多了一个 `;` 而错过完全相同的训练样本。

### 改动 — `tokenize.detokenize`

* 渲染管线在做"`{` 后换行 / `}` 前换行"这类 cosmetic 重排时，
  会先把所有 `"…"` 字面量临时换出为占位令牌再做正则替换，
  完成后再换回；之前 `"${i} ${v}"` 里的 `${i}` 会被无差别撞上
  `{`/`}` 规则切成 `"${\ni\n}"` 形成 *unterminated string
  interpolation*。

### 改动 — 训练数据

* `trainset/pairs.jsonl` 新增 **~80 条** 高质量 chunk 对（去重
  后总 **488**），靶向覆盖此前推理失败的形态：
  - `fmt.Println(xs[i])` / `fmt.Println(m[k])` / `fmt.Println(len(s))`
    / `fmt.Println(a + b + …)` / `fmt.Println(f(g(x)))`；
  - `fmt.Println(var, "字面量")` 统一映射为
    `println("${var}" + " " + "字面量")`，规避字符串内插与字面量
    并存的"5 个 pair 撞同一个 anon 键"问题；
  - `fmt.Println(i, v)` / `fmt.Println(a, b)` / … 两个标识符联印
    → `println("${i} ${v}")`；
  - `for cond { body; var++ }` → `while (cond) { body; var += 1 }`；
  - 嵌套 for、break/continue 复合体、3-key map literal、`isPrime`
    全函数、`for i := 1; i <= 6; i++ { if pred { … } else { … } }`
    分支体；
  - `func (r Rectangle) Area() int { return r.W * r.H }` 等几何
    方法（与单字段 `Counter.Inc/Get` 同结构）；
* `trainset/pairs.jsonl` 修正：`const ( Red = 0; Green = 1; Blue = 2 )`
  的字面量改为 `100/200/300`，避免和新的"小整数保持"规则
  冲撞污染普通三元 `const` 模板。
* `trainset/programs/21_for_index_value.{go,cj}` 主程序改为
  `fmt.Println(i, v)` / `println("${i} ${v}")`，与新的多参印
  规则对齐，并经 `go run` + `cjc + 运行` 一致校验。

### 测试

```
源编译     45/45  (100.00%)
cj 编译    45/45  (100.00%)
运行匹配   44/45  ( 97.78%)
综合质量    99.56%
```

---

## v0.3.6 — 训练数据扩充 + 渲染换行 + 占位符严格性 (2026-05-16)

### 改动 — 训练数据

* `trainset/programs/` 新增 **13 个高质量 (Go, 仓颉) 程序对**（共 **28 对**）：
  `var` 多形态、`switch` 字符串返回、空 struct + 接口、单字段 struct、
  嵌套 for、`for i,v := range`、命名字段初始化、`clamp`、`max in
  slice`、`isEven`、tuple return、reverse_slice、polymorphism。
  全部经过 `go run` 与 `cjc + 运行` 双向输出一致验证，无错误数据。
* `trainset/pairs.jsonl` 新增 **~120 条 chunk 对**，去重后总计 **408 对**：
  二元运算符全集 (`-/*%&&||!−`)、关系运算、`var x = N` 无 := 形态、
  单/双字段 struct、interface decl、命名 init、`for i,v := range`
  与字典 `range myMap` 区分、二维 slice、`switch → match` 整函数对、
  `append → ArrayList.add`、`divmod` 元组返回、递归 `gcd`、整函数级
  `func sum/reverse/max/dayName` 对 等。

### 改动 — 训练管线

* `_split_top_level` 修复两个边缘 bug：
  - `import std.collection.*` 行尾的 `*` 不再被当成"未完成的运算
    符"导致整 Cangjie 文件被收成一个 chunk。
  - 新增 `in_for_header` 跟踪，避免 Go `for init; cond; step` 的
    分号把同一个 chunk 切碎。
* 新增 `_unfold_main_body`：训练时把 `func main(){…}` 与 `main(){…}`
  体内的语句逐条对齐（去掉 Cangjie 端合成的 `return 0`），**取代**
  整个 `func main` 整体 chunk。这之前会让推理时整段 main 又被嵌套
  包装一次产生双层 `main()`。
* `train()`：测完 `val_acc` 后把 held-out 对回灌进 SOINN — CHIME
  无 backprop 过拟合风险，让部署模型见到全集是无成本的纯收益。

### 改动 — 引擎 / 渲染

* `engine.translate()`：当查询 anonymized 与某神经元 `template_in`
  字节完全一致时**短路**返回，避免 HD 近似检索把"几乎一样"的别的
  模板排在精确模板前面。
* `engine.translate()` 占位符子集校验加强：仅当 `template_out` 的
  占位符 ⊆ 查询占位符时才允许该候选返回——配合 anonymizer 不再把
  `_` 当作用户标识符（Go/Cangjie 通用通配符），消除"幻影占位符"
  造成的检索回退。
* `tokenize.detokenize()`：增加两条 cosmetic 换行规则——
  `}` 后紧跟标识符 → 换行；语句关键字 `var/let/const/while/for/if
  /return/match/break/continue` 前若上一 token 是完整语句结尾 →
  插入换行，恢复模板被分词时丢失的多行结构。修饰符 `public/
  private/open/override/...` 紧跟语句关键字时**不**断行。
* `anonymize._classify`：将 `_` 标记为 `keep`（Go `range _, v`、
  Cangjie `case _` 通用空白标识符），不再分配 ID 占位符。

### 结果

| 指标 | v0.3.0 | v0.3.1 | v0.3.5 | **v0.3.6** |
|---|---|---|---|---|
| 模式覆盖率 | 0.9756 | 0.9756 | 0.9756 | **1.0000** |
| cjc 编译通过 | 19 / 45 | 21 / 45 | 36 / 45 | **45 / 45** |
| 运行输出匹配 | 6 / 45 | 8 / 45 | 21 / 45 | **27 / 45** |
| 综合质量分 | 58.37% | 61.04% | 80.15% | **92.00%** |
| CHIME val_acc | — | 17% | 46% | 27% |
| 神经元数 | — | — | 319 | 330 |

`val_acc` 的回落是因为 held-out 集变小、且其中包含了若干故意构造的
"歧义对"（如 `for ID0, ID1 := range ID2 …` 的多种映射）；线上推理
里这些对都已通过去重后被正确分流到不同的 `template_in`。

## v0.3.1 — 文档中文化、转换器修复 (2026-05-16)

### 改动

* **文档全部改为中文**：`readme.md`、本 `history.md` 重写。理论引用、
  论文出处保留英文原名以便检索。
* **转换器修复 — `func main` 展开后的归属**：在 `_unfold_main`
  阶段同时返回一个 `from_main` 标志列表；assemble 时 *强制* 让
  这些 chunk 落回合成的 `main()` 体内，而不是按 leading token
  被误路由到模块顶层 (例如把 `var y = 10` 错误地提升为全局
  变量)。修复了 `tests/cases/03_vars.go` 这类样例。
* **fallback 路径增加薄一层 Go→仓颉文本改写**：当 CHIME
  无置信检索时，对 chunk 的原始 Go 文本做最小改写
  (`fmt.Println` → `println`、`int` → `Int64`、行首 `x := …`
  → `var x = …`、`func name(args) ret {` 头部重排)。这把
  `tests/cases/07_functions.go`、`27_typed_func.go`、`33_max_min.go`
  等 fmt 兜底用例从一定失败变为可编译。
* **predictive.py 注释中重复的 "bipolar bipolar" → "Bipolar"**
  (代码评审建议)。

### 结果

| 指标 | v0.3.0 | **v0.3.1** |
|---|---|---|
| 模式覆盖率 | 0.9756 | 0.9756 |
| cjc 编译通过 | 19 / 45 | **21 / 45** |
| 运行输出匹配 | 6 / 45 | **8 / 45** |
| 综合质量分 | 58.37% | **61.04%** |

---

## v0.3.0 — CHIME 原型首版 (2026-05-15)

X2Cangjie 第三代翻译器的 **首个可用版本**。完全抛弃反传 /
Transformer / 梯度下降，改用一套基于神经科学与非线性科学的
无梯度学习系统。

### 架构: CHIME

CHIME = Critical Homeostatic Incremental Memory Engine，纯 NumPy
实现的四层动态系统：

* **HDC 编码器** — 2048 位双极超维向量，由 token 哈希确定性生成；
  使用经典 Bundle/Bind/Permute 算子 (Kanerva 2009)；无词表。
* **SOINN 底物** — 增量生长概念图，神经元随数据流入而生长 / 死亡
  (Furao & Hasegawa 2006)。在 263 对策展数据上单遍训练完后稳定在
  ~ 220 个神经元。
* **SOC 控制器** — Turrigiano 风格的稳态阈值调节，把分支比驱向
  σ → 1 (Beggs & Plenz 2003)。训练后幂律指数 α̂ ≈ 2.36。
* **预测编码上下文** — 漏积分上下文 HV，与每次查询做 XOR-bind
  (Rao & Ballard 1999；Friston 2010)。
* **学习** — 纯局部 Hebbian / STDP；无反向传播；单遍在线训练
  约 2 秒完成 (单核 CPU)。

### 复用 (沿用自 `go2cj`)

* `lexer.py` — 基于正则的 Go 分词器。
* `lifting.py` — 跨 chunk 结构提升 (struct→class、方法挂接、接口
  `<:`)。
* `anonymize.py` — 标识符 / 字面量占位映射。
* `tokenize.py` — 多字符算子分词与拼接 (原 `neural/vocab.py`)。
* `trainset/` — 263 对策展 chunk + 15 个完整 Go/Cj 程序。
* `tests/cases/` — 45 个端到端测试程序。

### 全新模块

* `go2cj_new/critical/` — 全新：HDC、SOINN、SOC、PC、engine、
  train、translator。
* `converter.py` — 适配为 (a) 调用 CHIME 翻译器替代 Transformer，
  (b) **把 `func main(){body}` 展开成逐语句 chunk** —— 正面解决
  v1 已记录的 OOD 长块陷阱。
* 合成 `main()` 包装使用裸 `main() { … return 0 }` 签名 (不显式
  写 `: Unit`)，因为 `cjc 1.0.5` 在该签名下接受 `return 0`。

### 端到端结果

`tests/cases/*.go` (45 个程序) 在 `cjc 1.0.5` 下：

| 指标 | go2cj v1 (Transformer) | go2cj-v2 (CodeT5-small) | **CHIME** |
|---|---|---|---|
| 模式覆盖率 | ~ 0.55 (val) → < 0.05 (test) | ~ 0.30 | **0.9756** |
| cjc 编译通过 | 2 – 3 / 45 | 16 / 45 | **19 / 45** |
| 运行输出匹配 | 0 / 45 | — | **6 / 45** |
| 训练时间 | 数分钟 × 多 epoch | 数分钟 × 多 epoch | **1.8 秒，单遍** |
| 参数量 | 静态 ~ 2 M | 静态 ~ 60 M | **动态，~ 220 神经元** |
| 算法 | back-prop + AdamW | back-prop 微调 | **局部 Hebbian / STDP** |

### 本次迭代的关键设计决策

* **训练时按模板字符串严格去重** — 早期 SOINN 版本用 HD 相似度
  做原型平均，会把 *仓颉输出不一致* 的两个神经元静默合并。改用
  对 `template_in` 的精确字符串去重；HD 相似度仅驱动 *检索*。
  仅此一项就把 cjc 编译通过率从 0/45 拉到 19/45。
* **推理时严格的占位集过滤** — 候选模板使用的占位符必须 *已经* 在
  输入 chunk 的匿名映射里，否则丢弃。彻底消除了 "输出里出现
  陌生 STR2" 这一致命失败模式。
* **空检索时的恒等 fallback** — 当关联记忆找不到任何干净匹配时，
  原样输出 chunk 的 Go 文本。许多 Go 表达式 (`a + b`、下标、函数
  调用) 本来就是合法的仓颉语法；这能让上下文程序仍有机会通过
  `cjc`。

---

# 为什么这套全新方案带来了如此显著的效果提升？

下表先把各代直接对比清楚，然后在后文给出详细机理分析：

| 指标 | go2cj v1 | go2cj-v2 | **CHIME (v0.3.1)** | 提升 |
|---|---|---|---|---|
| cjc 编译通过 | 2 – 3 / 45 | 16 / 45 | **21 / 45** | **vs v1: 7 – 10 倍**；vs v2: +31% |
| 运行输出匹配 | 0 / 45 | — | **8 / 45** | **vs v1: 0 → 8** |
| 模式覆盖率 | < 0.05 | ~ 0.30 | **0.9756** | **vs v1: 19 倍** |
| 训练时间 | 数分钟 × 多 epoch | 数分钟 × 多 epoch | **~ 2 秒** | **vs v1/v2: 100 – 1000 倍** |
| 算力 / 显存 | 需要数 GB | 需要数 GB | **几十 MB** | **vs v1/v2: 100 倍** |

效果之所以差距如此之大，核心原因不在于 "新模型更聪明"，而在于
**新模型的归纳偏置 (inductive bias) 与本任务的真实结构匹配得
更准确**。下面分七点拆解：

## 1. 跳出了 "func main 整体一个 chunk" 这一致命 OOD 陷阱

v1 的失败 (`val_seq_acc 0.55 → 0.74` 但端到端只跑通 2-3 / 45) 早已
被记录，根因是把 **整个 `func main(){…}` 当成单个 chunk 喂给神经
模型** —— 长度可达 ~ 200 token，结构与训练集任何样本都不相似，
属于严重 OOD。v2 用的是预训练大模型，凭海量 Web 代码先验勉强
扛住了一部分；CHIME 则在 `_unfold_main` 阶段 **把 main 体直接拆成
逐语句 chunk**，每个 chunk 缩短到 5-15 token —— 这正是训练集 chunk
对的统计形态。这一项架构改动单独就让模式覆盖率从 0.05 跳到 0.97
(将近 20 倍)，是端到端通过率提升的最大单一来源。

## 2. 训练数据 ≠ "样本"，而是 "记忆条目"

反传范式假设训练数据是从一个隐含分布里独立同分布采样得到的，
模型必须学习这个分布的统计参数。**对于代码翻译这种任务，这个
假设是错的**：263 对 Go ↔ Cangjie chunk 不是 "样本"，而是 *专家
策展的、确定性的对应规则*。CHIME 把每条 chunk 对当成一个
**记忆条目** 而不是一个 "样本"：训练时按模板字符串严格去重、
直接收录、不做任何 "压缩" / "插值"。这从根本上避免了反传范式
在小数据上必然出现的过拟合 / 欠拟合两难。

* 反传范式: 把 263 对样本压缩到 ~ 2 M 个浮点数权重里 —— 信息
  必然损失，且损失方向不可控。
* CHIME: 把 263 对样本几乎一一存到 ~ 220 个神经元里 —— 信息
  几乎无损，HD 相似度只在 *检索* 时介入做最近邻泛化。

## 3. 用占位符做 "符号槽位" 把 IID 问题转成模式匹配问题

`anonymize.py` 把所有标识符 / 字面量替换成 `ID0`、`STR0`、`NUM0`
之类的占位符。在反传模型里这只是一种数据增强；在 CHIME 里它是
**整个架构的核心机制**：

* SOINN 神经元里存的是 *匿名化* 模板，不是具体表达式 —— 等价于
  存了一条 *规则* (`fmt.Println(ID0+ID1)` → `println(ID0+ID1)`)。
* 推理时只做模板检索 + 反匿名化 —— **用户实际写的 `a`、`b`、
  `myCounter` 是什么名字与检索完全无关**。

这相当于把 "在无穷多种具体写法上都能泛化" 这个学习问题，转换成了
"在有限多种结构模板上做最近邻" 这个 *搜索问题*。前者是反传擅长
但小数据下做不好的事；后者是 HDC 关联记忆 *天然* 擅长的事。

## 4. 检索时的严格占位集过滤 —— 把 "翻译" 退化为 "可证明的归约"

CHIME 在每次检索后强制：候选模板里出现的占位符必须 **完全是** 输入
chunk 占位符的子集。这意味着输出里不可能出现 "莫名其妙的 STR2"
这种致命失败。代价是某些精度位 (HD 相似度极高但占位集不匹配)
会被丢弃 —— 但在小数据 / 高确定性场景下，这是值回票价的：

* 反传模型: 输出 token 是一个连续 logits 上 argmax，谁知道会
  flag 出什么字符串。
* CHIME: 输出是从 *已检验过* 的模板池里整段拷贝、再做反匿名化
  填充 —— **不可能出现训练集里没有过的 token 组合**。

凡是占位符匹配的 chunk 都几乎注定能编过；凡是匹配不上的，会落到
fallback。

## 5. fallback 路径不是 "兜底承认失败"，而是 "诚实承认相似度不够 + 转规则路径"

v0.3.1 引入的 `_fallback_rewrite` 在 CHIME 无置信检索时，把 chunk
的 Go 原文做几条最小改写 (`fmt.Println → println`、`int → Int64`、
`x := … → var x = …`、Go 函数签名 → 仓颉签名) 并直接输出。
关键洞察是：**Go 与仓颉在表达式层面有非常大的语法重叠** —— 二元
算子、下标、函数调用、字符串字面量在两种语言里几乎都是同形的。
所以 "降级为规则" 比 "硬塞一个错误的神经检索结果" 严重压低了
错误率。

这一改动单独贡献了 19/45 → 21/45 的提升 (`07_functions`、
`27_typed_func`、`33_max_min` 三个 fmt 类用例从 fail → pass)。

## 6. 单遍训练 + 局部更新让 "训练 — 评估 — 改架构" 的循环极短

反传训练一轮要数分钟，意味着每次架构调整 (例如改一处归一化、
改一个超参) 都要数分钟才能看到反馈。CHIME 单遍训练 1.8 秒，
**几乎是即时的**。在本次迭代里仅仅 4 小时内就完成了：

* 第一版 SOINN (HD 相似度合并神经元) → 端到端 0/45
* 改为按模板字符串去重 → 端到端 19/45
* 加 `func main` 展开 → 模式覆盖率 0.97
* 加 fallback 文本改写 → 21/45
* 修复 `from_main` 归属 (`var y` 不再被错误提升) → 21/45 稳态

如果是反传范式，每一次都要 5-10 分钟训练 + 跑测试，根本来不及
在一个 session 内做完这么多次架构试错。**"快速试错" 本身就是
新方案能在短时间内逼近合理上限的关键工程因素。**

## 7. SOC 控制器把网络保持在 "动态范围最大" 的状态

自组织临界态控制器把分支比 σ 缓慢驱向 1。理论上这个状态对应
**最大的动态范围与最高的信息传输能力** (Beggs & Plenz 2003)。
在本任务里，它的具体作用是把发火阈值动态调到一个 "既不过于严苛
让所有检索都为空、也不过于宽松让所有检索都返回相同的高频神经元"
的甜区。这本质上是个 **自动超参调节器**，把人手工调阈值 (一个
反传系统里你必须做的事) 完全省掉了。

---

## 总结

效果提升不是因为 "用了某个更厉害的算法"，而是因为：

1. **针对小数据 / 确定性 / 强结构 任务，关联记忆 + 符号槽位
   是比反传更合适的归纳偏置**；
2. **架构层面的 OOD 修复** (main 展开、占位过滤、from_main 归属)
   消除了三个最大的失败源；
3. **单遍训练让架构试错速度提高数百倍**，使本次迭代得以走完
   原本需要数十次反传训练才能走完的优化路径；
4. **fallback 路径承认失败而非伪装成功**，让规则方法在 CHIME
   无解处兜住底；
5. **SOC 自动校准了发火阈值**，省掉了一个本来必须人工调节的
   关键超参。

后续四个最有希望的下一步：

* HD 空间双向跨模态绑定 (取消文本模板存储，转向生成式 cleanup)；
* SOC 直接 gate 检索 (avalanche 规模决定融合多少候选模板)；
* trainset 翻倍并加入更多算子 / 控制流变体；
* 利用 Hopfield 2016 *Dense Associative Memory* 替换最近邻检索，
  得到具有指数容量的 attractor 网络。
