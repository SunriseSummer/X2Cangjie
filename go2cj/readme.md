# go2cj — Go → 仓颉（Cangjie）神经网络源代码转换器

> **Go 版本：** 1.24（go vet 验证）  
> **Cangjie 版本：** 1.0.5（cjc cjnative）  
> **运行环境：** Python ≥ 3.10，CPU only（无需 GPU），依赖 `numpy`、`torch`（CPU）

`go2cj` 用**训练得到的 Transformer 编码器-解码器**做 Go → 仓颉的 chunk 级翻译。规则脚本已彻底替换，per-chunk 转换由 `go2cj/model.pt` 中的网络权重产出；用户标识符 / 字面量通过**匿名化层** (`anonymize.py`) 实现零损失保持。

---

## 1. 端到端管线

```
┌──────────┐  ┌────────────┐  ┌──────────────────┐
│ Go 源码  │→ │ regex lexer│→ │ ; injection +    │
└──────────┘  └────────────┘  │ chunk segmenter  │
                              └────────┬─────────┘
                                       ▼ (每个 chunk 是 Go 文本)
                       ┌────────────────────────────┐
                       │ anonymize identifiers /    │
                       │ NUM / STR / CHR literals   │
                       └────────────┬───────────────┘
                                    ▼
                       ┌────────────────────────────┐
                       │ Trained Transformer        │
                       │ seq2seq (d_model=96,       │
                       │ 2 enc/2 dec, 6 heads,      │
                       │ ~0.6M params)              │
                       └────────────┬───────────────┘
                                    ▼
                       ┌────────────────────────────┐
                       │ de-anonymize (substitute   │
                       │ original IDs / literals    │
                       │ back into output stream)   │
                       └────────────┬───────────────┘
                                    ▼
              ┌─────────────────────────────────────────┐
              │ cross-chunk structural lifting          │
              │  • struct → class + 合成 init           │
              │  • free `func (r T) M(...)` 挂入 class  │
              │  • 隐式接口实现 → 显式 `<:` + override  │
              └────────────────┬────────────────────────┘
                               ▼
              ┌─────────────────────────────────────────┐
              │ assemble: drop package/import,          │
              │   inject `import std.collection.*`,     │
              │   wrap free statements in `main()`      │
              └────────────────┬────────────────────────┘
                               ▼
                        ┌─────────────┐
                        │ Cangjie 源码 │
                        └─────────────┘
```

只剩三类**非 NN** 步骤：词法（Go 正则 lexer + `;` 注入）、chunk 切分、结构提升（跨 chunk 装配）。模型 + 词表 + trainset 是**唯一**的翻译知识载体。

---

## 2. 训练数据：`go2cj/trainset/`

```
trainset/
├── readme.md          ← 数据组织 & 添加新对的规范
├── pairs.jsonl        ← chunk 级 Go↔仓颉对（每行一个 JSON）
└── programs/          ← 完整程序对：<name>.go / <name>.cj
    ├── 01_addition.go    01_addition.cj
    ├── 02_sumto.go       02_sumto.cj
    └── …
```

* **`pairs.jsonl`**：人工撰写的、风格一致、最优编码实践的 Go ↔ 仓颉 chunk 对。覆盖变量声明、控制流、函数（含多返回 / 闭包）、方法、struct / interface / 隐式实现、slice / map / 字符串 API、`fmt.*`、`strings.*`、`math.*`、`strconv.*`、错误处理、`switch / match`、goroutine / channel 等场景。
* **`programs/`**：完整可编译运行的 Go / 仓颉对应程序，用于补充更长的多语句 chunk 形态。
* 训练时每条 curated 对通过**匿名化 + 占位符 index 置换**扩展为 ~60 个变体（`load_curated_corpus(augment_factor)`），单条优质对相当于上千条数据。
* 合成生成器（`corpus.py`）继续提供基础语法的随机覆盖。

### 添加训练数据

1. 在 `pairs.jsonl` 追加一行 `{"go": "...", "cj": "..."}`，仓颉端使用**最佳实践**（`var/let`、`Int64`、`ArrayList<T>`、`HashMap<K,V>`、`match`、`for x in xs`、tuple 解构、`String.fromUtf8` 等）。
2. 或在 `programs/` 加 `<name>.go` 与 `<name>.cj` 对（顶层 chunks 顺序对齐）。
3. `python -m go2cj.neural.train --epochs 1` 增量训练，权重自动从已有 `model.pt` 继续。

---

## 3. 增量、可恢复的训练

训练**永远不从零开始**（除非显式 `--restart`）。每个 epoch 结束**原子写盘** `model.pt`（含 optimizer 状态）/ `vocab.json` / `model_meta.json`，单次会话 SIGKILL 最多丢失 1 个 epoch。

```bash
# 默认：1 个 epoch 增量训练（沙箱中约 2 分钟）
python -m go2cj.neural.train

# 增量再训 5 个 epoch
python -m go2cj.neural.train --epochs 5

# 从头训练
python -m go2cj.neural.train --restart --epochs 8

# 也可调神经网络架构 / 超参
python -m go2cj.neural.train --restart --d-model 96 --layers 2 --nhead 6 \
    --samples 4000 --curated-factor 80 --batch-size 96 --lr 5e-4
```

### 已优化的关键算法点

| 项 | 取值 / 说明 |
|---|---|
| 输入 / 输出表示 | **匿名化** (`ID0/NUM0/STR0/CHR0`) — 标识符与字面量零损失保持，模型只学规范化模板 |
| 模型 | Transformer encoder-decoder（PyTorch `nn.Transformer`） |
| 规模 | `d_model=96, 2 enc / 2 dec, nhead=6` — 约 0.6 M 参数，CPU 上每 epoch ≈ 2 min |
| 词表 | 由首个训练 run 在 trainset+合成数据上构建后**冻结**；后续增加 trainset 通过 `<unk>` 兜底（实际比例 < 1%） |
| 损失 | Cross-entropy + label smoothing (0.1) |
| 优化器 | AdamW (wd=1e-4)；OneCycleLR，每次 resume warm-restart |
| 数据 | curated（249 对）× 增广因子 (默认 60) + 合成（默认 8000）+ 全部匿名化 |
| 解码 | 贪心自回归 |

如需更高质量，可加大 `--samples`、`--curated-factor`、`--d-model`、`--layers`，并多次增量训练（每次只跑 1-3 epochs 以避免超时）。

---

## 4. 推理（`NeuralTranslator`）

```python
from go2cj import convert_source
res = convert_source(open("a.go").read())
print(res.source)
print(res.confidence)
```

或仅做 chunk 级翻译：

```python
from go2cj.neural.translator import NeuralTranslator
t = NeuralTranslator.get()
print(t.translate("x := 1"))                  # → "var x = 1"
print(t.translate("for i := 0; i < n; i++ {}"))  # → "for (i in 0..n) {}"
```

`translate_batch` 在沙箱里批量 greedy decode（单 chunk < 100 ms）。

---

## 5. 测试

测试套件位于 `tests/cases/*.go`（+ `.expected` 标准输出）。当前规模：**40 个用例**，覆盖：算术、控制流、函数、递归、slice、append、嵌套循环、字符串、布尔逻辑、fizzbuzz、求和、switch / match、struct / 方法、interface 多态、`break/continue`、`fmt.Printf`、const block、float math、count chars、嵌套调用、混合程序，以及新增的 map、字符串基础、max/min、polymorphism、reverse slice、gcd、primes、matrix sum、counter 等。

```bash
source /tmp/cangjie/envsetup.sh
cd go2cj && python3 tests/run_tests.py
```

`tests/log.md` 自动生成，包含覆盖率 / cjc 编译率 / 运行匹配率 / 综合评分以及失败诊断。

> 神经管线的精度受训练量影响：增量训练 epochs 越多，匿名化 token 的复用越好，cjc 编译通过率越高。如果发现回归，最直接的解法是 `python -m go2cj.neural.train --epochs 5` 多次叠加，**而不是**改回规则。

---

## 6. 目录结构

```
go2cj/
├── go2cj/                       # Python 包
│   ├── __init__.py
│   ├── __main__.py
│   ├── lexer.py
│   ├── converter.py             # 主管线（神经驱动 + 结构装配）
│   ├── lifting.py               # 跨 chunk 结构提升
│   ├── model.pt                 # 训练得到的 Transformer 权重（增量更新）
│   ├── vocab.json               # 冻结的词表
│   ├── model_meta.json          # 训练超参 / 指标 / 当前 epoch
│   └── neural/
│       ├── corpus.py            # 合成语料生成器
│       ├── curated.py           # 加载 trainset/* 并增广
│       ├── vocab.py             # 词级 tokenizer + Vocab
│       ├── model.py             # Seq2SeqTransformer
│       ├── anonymize.py         # 标识符/字面量匿名化层
│       ├── translator.py        # 推理单例 NeuralTranslator
│       └── train.py             # 增量可恢复训练
├── trainset/                    # 训练语料（hand-curated）
│   ├── readme.md
│   ├── pairs.jsonl
│   └── programs/
└── tests/
    ├── cases/                   # 40 个用例
    ├── run_tests.py
    └── log.md
```
