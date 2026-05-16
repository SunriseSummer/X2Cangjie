# go2cj-new 工作原理说明

本文面向想读懂 `go2cj-new` 源码的人，按 **运行入口 → 转换流水线 → CHIME 核心算法 → 训练 / 推理 / 测试** 的顺序解释整套代码如何工作，并补充每个核心算法背后的理论动机。

---

## 1. 项目定位：不是神经翻译器，而是关联记忆翻译器

`go2cj-new` 的任务是把 Go 源码转换为可编译、可运行的仓颉源码。它沿用了早期 `go2cj` 的词法拆分、chunk 化和部分结构提升思路，但把“每个 Go chunk → Cangjie chunk”的核心映射，从 Transformer / CodeT5 这类反向传播模型，替换为 **CHIME**：

> Critical Homeostatic Incremental Memory Engine，临界态稳态增量记忆引擎。

CHIME 的核心不是“生成下一个 token”，而是：

1. 把一个 Go chunk 匿名化成结构模板；
2. 把模板编码成 2048 维超维向量；
3. 在一个动态生长的 SOINN 图中检索最相近的已记忆模板；
4. 取出对应的匿名化仓颉模板；
5. 再把用户原始标识符、字面量填回去。

因此它更像一个 **符号槽位 + 超维近邻检索 + 动态拓扑记忆** 系统，而不是传统神经网络翻译器。

---

## 2. 两条主路径

### 2.1 训练路径

入口：[`go2cj_new/critical/train.py`](go2cj_new/critical/train.py)

训练命令：

```bash
PYTHONPATH=. python -m go2cj_new.critical.train
```

训练流程：

```text
trainset/pairs.jsonl
      │
      ├── 读取人工策展的 chunk 对
      │
trainset/programs/*.go + *.cj
      │
      ├── 拆成顶层 chunk；main() 体额外展开为语句级 chunk
      │
      ▼
anonymize_pair(go, cj)
      │
      ├── 两侧共享 ID0 / NUM0 / STR0 / CHR0 占位符映射
      │
      ▼
CHIME.learn(anon_go, anon_cj)
      │
      ├── HDC 编码 Go 模板
      ├── SOINN 新增或命中神经元
      ├── Hebbian 边刷新 / 老化
      └── SOC 控制器记录 avalanche 并调整阈值
      │
      ▼
go2cj_new/critical/model/
      ├── soinn.npz / soinn.json
      ├── criticality.json
      └── meta.json
```

训练不是多 epoch 反传。当前实现先对 90% 训练集做一次在线吸收，再轻量 replay 两轮以刷新 Hebbian 边、稳定临界态；测完 held-out `val_template_acc` 后，会把验证集也回灌进部署模型。这样做的理由是：CHIME 的底物是关联记忆，不是靠梯度压缩分布参数的模型；部署时让记忆见到全部策展规则通常只会提升召回。

### 2.2 推理 / 转换路径

入口：[`go2cj_new/__main__.py`](go2cj_new/__main__.py)、[`go2cj_new/converter.py`](go2cj_new/converter.py)

转换命令：

```bash
PYTHONPATH=. python -m go2cj_new tests/cases/01_hello.go -o /tmp/hello.cj --report
```

推理流程：

```text
Go 源码
  │
  ├── _convert_raw_strings：Go raw string → Cangjie 可接受的双引号字符串
  ├── lexer.tokenize：正则词法分析，保留 NEWLINE
  ├── _inject_semis：模拟 Go 自动分号插入
  ├── _segment_chunks：按括号 / 大括号 / 换行 / 分号切 chunk
  ├── _unfold_main：把 func main(){...} 展开成语句级 chunk
  │
  ▼
逐 chunk 调用 NeuralTranslator（实际是 CHIME 单例）
  │
  ├── anonymize_text：用户符号 → ID0 / NUM0 / STR0 / CHR0
  ├── CHIME.translate：HDC + SOINN + PredictiveContext 检索模板
  ├── deanonymize_tokens：占位符 → 用户原始符号
  └── detokenize：模板 token → 仓颉文本
  │
  ▼
后处理
  │
  ├── fallback_rewrite：无置信检索时做最小 Go→Cangjie 文本兜底
  ├── synthesize_class_inits：为 class 补构造器
  ├── promote_methods：Go receiver method 移入 class
  ├── attach_interface_impls：结构化接口满足 → 显式 <: / override
  ├── 按需注入 import std.collection.*
  └── 合成 main() { ... return 0 }
  │
  ▼
Cangjie 源码
```

---

## 3. 代码模块职责

| 模块 | 职责 |
|---|---|
| `__main__.py` | 命令行入口，读取 Go 文件、调用 `convert_source`、写出仓颉文件，并在 `--report` 下输出 chunk 覆盖统计。 |
| `lexer.py` | 正则 Go lexer。它不是完整 parser，只产生 token / NEWLINE / comment 等词法单元，供 chunker 使用。 |
| `converter.py` | 主编排器：预处理、分 chunk、main 展开、调用翻译器、fallback、结构提升、最终组装。 |
| `tokenize.py` | 模板级 tokenizer / detokenizer。保证多字符运算符、字符串字面量、插值字符串等在模板中稳定往返。 |
| `anonymize.py` | 标识符和字面量匿名化 / 反匿名化。它把开放词表问题压缩成有限模板匹配问题。 |
| `lifting.py` | 跨 chunk 结构提升：struct→class 构造器、receiver method 入类、Go 隐式接口满足转为仓颉显式实现。 |
| `critical/hdc.py` | 超维计算编码器，把 token 序列映射成固定 2048 维双极向量。 |
| `critical/soinn.py` | 动态生长的概念图，每个神经元记忆一个 Go 模板原型和对应仓颉模板。 |
| `critical/criticality.py` | 自组织临界态控制器，记录 avalanche，调节全局发火阈值。 |
| `critical/predictive.py` | 预测编码上下文，用漏积分的程序历史 HV 调制当前 chunk 检索。 |
| `critical/engine.py` | CHIME 总控：连接 HDC、SOINN、SOC、PredictiveContext，提供 `learn` / `translate`。 |
| `critical/translator.py` | 推理单例，保持与旧 `NeuralTranslator` 接口兼容，但内部调用 CHIME。 |
| `critical/train.py` | 从 `trainset/` 加载数据、匿名化、训练 CHIME、保存模型和诊断指标。 |
| `tests/run_tests.py` | 端到端测试驱动：转换 45 个 Go 用例，执行 `go vet`、`cjc` 编译和输出匹配。 |

---

## 4. 为什么先匿名化：把“生成问题”降维成“模板检索问题”

源码中的用户标识符和字面量是开放集合：`userCount`、`myMap`、`3.14159`、`"hello"` 都可能无限变化。如果直接让模型学习这些具体 token，小数据下很容易出现：

- 标识符丢失或幻觉；
- 字符串 / 数字复制错误；
- 相似结构因变量名不同而不能共享经验。

[`anonymize.py`](go2cj_new/anonymize.py) 的策略是把开放集合收缩成槽位：

```text
fmt.Println(total + price)
        │
        ▼
fmt . Println ( ID0 + ID1 )
```

对应的仓颉模板也使用同一套槽位：

```text
println ( ID0 + ID1 )
```

推理时只要找到这个模板，再把 `ID0=total`、`ID1=price` 填回去即可。这相当于把“任意用户代码的翻译”拆成两件事：

1. **结构识别**：当前 chunk 属于哪个匿名化模板；
2. **槽位复制**：用户原符号原样填回。

这也是 CHIME 能在小训练集上有效工作的关键：它不需要记住所有变量名，只需要记住有限的结构模式。

### 4.1 为什么要做占位符子集校验

[`critical/engine.py`](go2cj_new/critical/engine.py) 在检索后强制检查：候选仓颉模板中出现的所有占位符，必须是输入 chunk 已经定义过的占位符子集。

例如输入只有 `ID0`，候选却要输出 `ID1`，那就一定会产生无法反匿名化的悬空占位符，最终大概率无法编译。因此 CHIME 宁可放弃这个高相似候选、走 fallback，也不输出带幻觉槽位的模板。

---

## 5. HDC：为什么 2048 维随机向量能表示代码结构

[`critical/hdc.py`](go2cj_new/critical/hdc.py) 实现 Hyperdimensional Computing，也叫 Vector Symbolic Architectures。

核心理论假设是：在足够高的维度中，随机向量几乎两两正交。对于 2048 维 ±1 双极向量，两个无关 token 的归一化点积通常接近 0；而由相同结构组合出来的向量会保持可检测的相似度。

HDC 使用三种基本代数操作：

| 操作 | 代码实现 | 直观含义 | 用途 |
|---|---|---|---|
| Bundling | `bundle()` | 多个向量按位多数表决，结果仍与每个成员相似 | 表示集合 / 多重集合 |
| Binding | `bind()` | ±1 乘积，结果与任一操作数都不相似，但可逆 | 表示“角色-填充值”绑定或组合关系 |
| Permutation | `permute()` | 循环移位，产生同源但不同位置的向量 | 编码顺序 |

`encode_sequence()` 对 token 序列做两层编码：

1. 对每个 3-gram 用 permutation + binding 编码顺序结构；
2. 再额外 bundle 所有单 token，给短 chunk 和局部词袋信息兜底。

因此下面两个模板的 HV 会相近但不完全相同：

```text
fmt . Println ( ID0 )
fmt . Println ( ID1 )
```

而与下面这种结构距离更远：

```text
for ID0 := 0 ; ID0 < NUM0 ; ID0 ++ { ... }
```

HDC 的工程收益是：没有 embedding 表、没有梯度、没有 OOV；每个 token 的 HV 由哈希确定性生成，新 token 第一次出现也能立即进入同一向量空间。

---

## 6. SOINN：动态生长的概念图

[`critical/soinn.py`](go2cj_new/critical/soinn.py) 实现 Self-Organizing Incremental Neural Network。

传统 SOM 的神经元数是预先固定的；SOINN 则从空图开始，随着输入流在线生长。`go2cj-new` 中每个神经元保存：

- `hv_in`：匿名化 Go chunk 的 HDC 原型；
- `template_in`：匿名化 Go 模板文本；
- `template_out`：匿名化仓颉模板文本；
- `win_count`：该神经元作为 BMU（最佳匹配单元）的次数；
- Hebbian 边：与相近或共激活神经元之间的连接。

当前实现对代码翻译做了一个重要特化：**训练时按 `template_in` 精确去重**。如果同一个匿名化 Go 模板已经存在，就只更新命中次数和边；如果是新模板，就新增神经元。

这样做比“相似就合并原型”更安全，因为代码翻译不是普通聚类：两个 Go chunk 在 HDC 空间很近，不代表它们的仓颉输出可以平均或合并。模板输出必须保持离散和可读出。

推理时则允许 HDC 相似度发挥作用：没有精确命中时，从 SOINN 中取 top-k 近邻，经过占位符子集校验后输出最佳模板。

---

## 7. Hebbian / STDP：边为什么会形成和老化

CHIME 没有反向传播，但不是完全静态查表。SOINN 图中的边体现了局部学习思想：

> neurons that fire together wire together。

训练时，新输入会激活 BMU；BMU 与次优神经元之间形成或刷新一条 Hebbian 边。边有年龄，长期不被刷新就老化并被移除。

这类似 STDP（Spike-Timing-Dependent Plasticity）的离散工程化版本：经常相邻或共激活的模式更容易连接，长时间没有共同活动的连接会衰减。这样网络拓扑能反映训练集中的局部结构，而不是只保存一堆孤立模板。

在当前转换器中，边主要服务于两件事：

1. 给临界态控制器估计 avalanche 传播范围；
2. 为后续更复杂的邻域混合 / 多候选融合留下拓扑基础。

---

## 8. SOC：为什么要把网络推向“临界态”

[`critical/criticality.py`](go2cj_new/critical/criticality.py) 实现 Self-Organized Criticality 控制器。

理论背景来自沙堆模型和神经 avalanche：很多复杂系统会自发接近一个临界点。在这个点上，分支比 σ 接近 1：平均每个激活节点再激活一个后继节点。

- σ < 1：亚临界，激活很快熄灭，信息传播太短；
- σ > 1：超临界，激活爆炸扩散，模式区分度下降；
- σ ≈ 1：临界，动态范围和信息传输能力最大。

CHIME 在每次学习后计算一个简化 avalanche：从刚命中的神经元出发，查看 Hebbian 邻居中有多少与它足够相似、能被当前阈值点燃。然后用稳态规则调整全局阈值：

```text
theta_next = theta + eta * (sigma - 1)
```

如果网络偏超临界，阈值升高；如果偏亚临界，阈值降低。这个机制不是直接写翻译规则，而是在调节“激活能扩散多远”，让关联记忆保持在既不过冷、也不过热的状态。

---

## 9. PredictiveContext：程序上下文如何参与检索

[`critical/predictive.py`](go2cj_new/critical/predictive.py) 提供一个轻量预测编码层。

同一个 Go 片段放在不同上下文中，可能应当偏向不同模板。CHIME 因此在处理一个程序的多个 chunk 时维护一个漏积分上下文 HV：

```text
state_next = decay * state_prev + (1 - decay) * chunk_hv
```

推理时，CHIME 同时尝试：

1. 用当前 chunk 的原始 HV 检索；
2. 用 `bind(chunk_hv, context_hv)` 后的上下文调制 HV 检索。

这对应预测编码思想中的“自顶向下预测”：历史 chunk 提供上下文坐标系，当前 chunk 不再是孤立刺激，而是带有程序历史的模式。当前实现仍然保守：上下文候选会打 0.95 折扣，并且最终仍需通过占位符子集校验。

---

## 10. main 展开：端到端提升的关键工程点

[`converter.py`](go2cj_new/converter.py) 的 `_unfold_main()` 会把：

```go
func main() {
    a := 1
    fmt.Println(a)
}
```

展开成两个语句级 chunk：

```text
a := 1
fmt.Println(a)
```

最后再由组装阶段合成：

```cj
main() {
    var a = 1
    println(a)
    return 0
}
```

这样做的原因是：训练集里的模板多数是短 chunk；如果把整个 `func main(){...}` 当作一个 100～200 token 的长 chunk，检索会严重 OOD，近邻没有意义。把 main 体切到语句级后，推理样本的形状与训练样本一致，HDC + SOINN 才能可靠命中。

`from_main` 标志同样重要。展开后的 `var a = 1` 看起来像顶层声明，如果不记录它来自 main，组装时就可能被错误提升到模块顶层。`from_main` 强制这些 chunk 回到合成的 main 体内。

---

## 11. fallback：承认无解，而不是硬输出错误模板

当 `CHIME.translate()` 无法找到通过校验的模板时，`converter.py` 不会硬取一个相似但不安全的神经元，而是进入 `_fallback_rewrite()`。

fallback 很克制，只做少量高确定性文本改写：

- `fmt.Println(` → `println(`；
- Go 基础类型名 → 仓颉类型名；
- 行首 `x := expr` → `var x = expr`；
- 简单 Go 函数签名 → 仓颉函数签名。

很多表达式级语法（算术、下标、调用、字符串字面量）在 Go 与仓颉中本来就近似同形，因此“原样输出 + 少量桥接”往往比错误检索更安全。

---

## 12. lifting：为什么翻译后还要跨 chunk 修正

每个 chunk 独立翻译无法解决所有语言结构差异。Go 与仓颉在若干跨声明关系上不同：

1. Go `struct` 没有显式构造器；仓颉 `class` 通常需要 `init`；
2. Go receiver method 是顶层函数；仓颉方法应在 class 内；
3. Go 接口满足是隐式结构化的；仓颉需要显式 `<:` 和 `override`。

[`lifting.py`](go2cj_new/lifting.py) 因此在所有 chunk 翻译完成后做全局扫描：

- `synthesize_class_inits()`：为 `open class` 中的字段合成 `public init(...)`；
- `promote_methods()`：把 `func (r: T) M(...)` 移入 `class T`，并把 receiver 名改为 `this`；
- `attach_interface_impls()`：如果 class 方法签名覆盖了 interface 要求，就给 class 头补 `<: Interface`，并给方法补 `public override`。

这部分不是“学习”，而是语言结构差异的确定性后处理。

---

## 13. 测试如何评价质量

[`tests/run_tests.py`](tests/run_tests.py) 遍历 `tests/cases/*.go`，每个用例执行：

1. 调用 `python -m go2cj_new` 生成 `.cj`；
2. 用 `go vet` 对 Go 源做快速检查；
3. 用 `cjc` 编译生成的仓颉源码；
4. 运行仓颉二进制；
5. 如果存在 `.expected`，逐字节比较输出；
6. 把结果写入 `tests/log.md`。

综合质量分公式：

```text
score = 0.4 * pattern_coverage + 0.4 * cj_compiles + 0.2 * runs_and_matches_expected
```

这比只看 `val_template_acc` 更接近真实目标。`val_template_acc` 衡量 held-out 模板是否完全匹配；端到端测试衡量生成的仓颉文件是否能编译、运行、输出正确。

---

## 14. 一句话串起全系统

`go2cj-new` 的本质可以概括为：

> 用匿名化把开放代码压缩成有限模板，用 HDC 把模板变成可相似检索的高维指纹，用 SOINN 把模板对存成动态生长的概念图，用 Hebbian / SOC / PredictiveContext 维护图的局部连接、临界状态和程序上下文，最后用确定性 lifting 弥补 Go 与仓颉在跨 chunk 结构上的差异。

这套设计的优势不是“比大模型更通用”，而是在 **小数据、强结构、确定性翻译** 场景下，把问题改写成了更合适的形式：模板记忆与安全检索，而非端到端概率生成。

---

## 15. 当前局限与后续方向

- 关联记忆仍然依赖训练集覆盖；训练集中没有的结构可能误路由或 fallback。
- HDC 检索目前主要读出单个最佳模板，尚未充分利用 SOINN 邻域做多候选组合。
- SOC 当前主要调节和诊断网络状态，尚未深度参与输出门控。
- PredictiveContext 是轻量上下文层，还不是完整的层级生成模型。
- 输出仍基于文本模板；未来可以探索 Go HV ↔ Cangjie HV 的跨模态绑定和 cleanup memory，减少对文本模板库的依赖。

