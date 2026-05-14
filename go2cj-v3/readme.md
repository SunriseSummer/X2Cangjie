# go2cj-v3 — Go → 仓颉（Cangjie）转换器（基于 CodeT5p-220m 预训练底座的二次训练方案）

> **Go 版本：** 1.24 （`go vet` 验证）
> **Cangjie 版本：** 1.0.5（`cjc cjnative`）
> **运行环境：** Python ≥ 3.10，CPU only（无需 GPU），依赖 `torch`、`transformers`、`sentencepiece`
> **底座模型：** [Salesforce/codet5p-220m](https://huggingface.co/Salesforce/codet5p-220m)（220 M 参数，T5 enc-dec，d\_model=768；CodeT5+ 家族，预训练含 Go 等多语言代码语料）

go2cj-v3 是对 [go2cj-v2](../go2cj-v2) 的"换底再训"：训练数据、测试集、词法 / chunk 切分 / 跨 chunk 结构提升 / 装配管线完全复用 v2，**唯一变化是把翻译核心由 60 M 参数的 codet5-small 换成 220 M 参数的 codet5p-220m**，期望在端到端 `cjc` 编译率与运行匹配率上相对 v2 进一步大幅提升。

---

## 1. 为什么再换底座？

go2cj-v2 用 codet5-small（60 M）作底座，3 epochs 微调后在 60 个测试用例上达到：

| 指标 | v1 (from-scratch 0.6 M) | v2 (codet5-small 60 M) |
|---|---|---|
| chunk-level val_seq_acc | 0.74 | **1.000** |
| 端到端 cjc 编译 | 2/45 (4.4%) | 22/60 (36.7%) |
| 运行匹配 | 1/45 (2.2%) | 18/60 (30.0%) |

继续推断 v2 失败用例，可以看到瓶颈不再是"模型不懂 Go"，而是**生成端的细粒度语法/类型选择**：

* `var y: 10`（漏掉 `=`）、`p.Z`（字段名错位）等小幅幻觉；
* `} return ...` 单行布局漏换行 / `;`；
* `int → Int64` 统一映射对 `float64` 不友好；
* `for i := 0; i < n; i++` 容易丢 `var`。

这些都属于"模型容量边界"问题——多分一倍的 attention 头 / 更宽 d\_model 通常就能拟合。v2 history 里也明确写过下一步可选 `codet5p-220m`。本版即落地该升级。

候选对比（同 v2 调研，结论已变）：

| 候选 | 参数量 | 架构 | 选择 |
|---|---|---|---|
| Salesforce/codet5-small | 60.5 M | T5 enc-dec (d\_model=512, 6/6) | v2 已用，瓶颈 |
| **Salesforce/codet5p-220m** | 220 M | T5 enc-dec (d\_model=768, 12/12) | ✅ v3 主线 |
| Salesforce/codet5-base | 220 M | T5 enc-dec (d\_model=768) | 备选，CodeT5+ 预训练任务更丰富，故选 v2p |
| Salesforce/codet5p-770m | 770 M | T5+ enc-dec | CPU 单 epoch >2 h，过重 |

codet5p-220m 的 tokenizer 与 codet5-small 同为 `RobertaTokenizer`（byte-level BPE，vocab=32100），模型类同为 `T5ForConditionalGeneration`，因此 v2 的训练 / 推理代码可以**直接复用**，无需改 tokenization 层。

---

## 2. 端到端管线

```
┌──────────┐   ┌────────────┐   ┌──────────────────┐
│ Go 源码  │ → │ regex lexer│ → │ ; injection +    │
└──────────┘   └────────────┘   │ chunk segmenter  │
                                └────────┬─────────┘
                                         ▼ (每个 chunk 是 Go 源文本)
                        ┌──────────────────────────────┐
                        │  Fine-tuned CodeT5p-220m     │
                        │  (220 M params, T5 enc-dec,  │
                        │   d_model=768, 12/12 layers, │
                        │   12 heads, byte-BPE vocab)  │
                        │  prompt: "translate Go to    │
                        │           Cangjie: <chunk>"  │
                        └────────────┬─────────────────┘
                                     ▼
                        ┌──────────────────────────────┐
                        │ cross-chunk structural       │
                        │ lifting (复用 v1/v2 lifting) │
                        │ • struct → class + init      │
                        │ • free `func (r T) M(...)`   │
                        │   挂回 class                 │
                        │ • implicit interface → `<:`  │
                        └────────────┬─────────────────┘
                                     ▼
                        ┌──────────────────────────────┐
                        │ assemble: drop pkg/import,   │
                        │ inject `import std.collec.*`,│
                        │ wrap free stmts in main()    │
                        └────────────┬─────────────────┘
                                     ▼
                              ┌─────────────┐
                              │ Cangjie 源码 │
                              └─────────────┘
```

非 NN 步骤（词法、chunk 切分、结构装配）与 v2 完全相同。

---

## 3. 训练数据：`trainset/`

数据组织与 v2 完全一致（直接从 v2 复制过来，按要求"复用 v2 训练和测试数据"）：

```
trainset/
├── readme.md
├── pairs.jsonl              ← chunk 级 Go↔仓颉对（354 条）
├── programs/                ← 完整程序对 30 套，每套 go run 与 cjc 双向编译运行通过
└── verify_programs.py
```

### 数据自验证

```bash
source /tmp/cangjie/envsetup.sh
cd go2cj-v3
python3 trainset/verify_programs.py     # programs/*.go vs *.cj
python3 tests/verify_go_cases.py        # tests/cases/*.go vs *.expected
```

### 添加训练数据

1. 在 `pairs.jsonl` 追加一行 `{"go": "...", "cj": "..."}`。
2. 或在 `programs/` 添加 `<name>.go` 与 `<name>.cj` 对（顶层 chunks 顺序对齐）。
3. `python -m go2cj_v3.train --epochs 1` 增量微调（权重自动从 `finetuned_last/` 续）。

---

## 4. 训练 & best-checkpoint 协议

### 一次性：下载底座模型

```bash
bash scripts/download_base.sh   # 把 codet5p-220m.zip 解压到 base_model/
```

模型存放（与 v2 协议一致）：

| 目录 | 角色 | 何时更新 |
|---|---|---|
| `base_model/` | 预训练 CodeT5p-220m（不进 git，由 download 脚本拉取） | 仅 `download_base.sh` |
| `go2cj_v3/finetuned/` | **最优** fine-tuned，供推理 | 仅当本 epoch `val_seq_acc` 严格优于历史最佳时覆盖 |
| `go2cj_v3/finetuned_last/` | 最新 fine-tuned，供续训 | 每个 epoch 末写 |
| `go2cj_v3/train_meta.json` | 当前 epoch / 最佳 epoch / 最佳 val 指标 | 每个 epoch 末写 |

所有 fine-tuned 权重 / base model 都在 `.gitignore` 中（每份 ~860 MB），不进仓库。复现完整训练只需 `download_base.sh` + `python -m go2cj_v3.train`。

### 增量训练命令

```bash
# 默认：1 个 epoch 增量微调（CPU 上 220 M ≈ 25-40 分钟）
python -m go2cj_v3.train

# 多 epoch
python -m go2cj_v3.train --epochs 3

# 从底座重启（清空 finetuned/）
python -m go2cj_v3.train --restart --epochs 3

# 调超参（220 M 默认 batch=2，把 augment 拉低以控总 step 数）
python -m go2cj_v3.train --epochs 3 --batch-size 2 --lr 3e-5 \
    --augment-factor 6 --max-input-len 384 --max-target-len 384
```

### 已选定的训练超参

| 项 | 取值 / 说明 |
|---|---|
| 底座 | `Salesforce/codet5p-220m`（220 M params, T5, d\_model=768, 12 enc / 12 dec, 12 heads, byte-BPE vocab=32100） |
| 输入格式 | `"translate Go to Cangjie: " + <chunk>` —— 标准 T5 任务前缀 |
| 损失 | T5 自带 cross-entropy（label\_pad=-100） |
| 优化器 | AdamW (wd=1e-4)，固定 lr=3e-5（CodeT5+ 微调推荐范围更小） |
| 数据 | 354 curated pairs × identifier-rename 增广因子 6 ≈ 2100 训练样本 |
| 序列长度 | 输入 / 输出各 384 BPE token |
| 解码 | beam=4, greedy（`generate`），CPU 单 chunk ~500 ms-1 s |
| Checkpoint 选优 | val\_seq\_acc 严格更优才覆盖 `finetuned/`，劣化版本不污染推理 |
| 校验集 | 5% canonical pairs 留出，从增广集中剔除避免泄漏 |

> **断点续训范式**：与 v1/v2 一致。沙箱中推荐每会话 1 epoch，每次从 `finetuned_last/` 续训；`finetuned/` 仅在更优时被覆盖。

---

## 5. 推理（`NeuralTranslator`）

```python
from go2cj_v3 import convert_source
res = convert_source(open("a.go").read())
print(res.source)
print(res.confidence)
```

CLI：

```bash
python -m go2cj_v3 input.go -o output.cj --report
```

仅 chunk 级翻译：

```python
from go2cj_v3.translator import NeuralTranslator
t = NeuralTranslator.get()
print(t.translate("x := 1"))                  # → "var x = 1"
print(t.translate("for i := 0; i < n; i++ {}"))
```

如果尚未训练，`NeuralTranslator` 会回退到 `base_model/` —— 此时输出基本不可用，但 import / generate API 可以走通便于调试。

---

## 6. 测试

测试套件直接复制自 `go2cj-v2/tests/cases/`（60 个用例 + `.expected` 文件），调用方式：

```bash
source /tmp/cangjie/envsetup.sh
cd go2cj-v3
python3 tests/verify_go_cases.py   # 先验证 .go + .expected 自洽
python3 tests/run_tests.py         # 端到端转换 + cjc 编译 + 运行
```

`tests/log.md` 自动生成，含覆盖率 / cjc 编译率 / 运行匹配率 / 综合评分。

---

## 7. 目录结构

```
go2cj-v3/
├── readme.md                    # 本文件
├── history.md                   # 训练历程与试错经验
├── requirements.txt             # torch + transformers + sentencepiece
├── .gitignore                   # 屏蔽 base_model/ + finetuned*/
├── scripts/
│   └── download_base.sh         # 从 GitHub release 下载 codet5p-220m
├── go2cj_v3/                    # Python 包
│   ├── __init__.py
│   ├── __main__.py              # CLI: python -m go2cj_v3
│   ├── lexer.py                 # 复用 go2cj 的 Go 正则 lexer
│   ├── lifting.py               # 复用 go2cj 的跨 chunk 结构提升
│   ├── converter.py             # 主管线（lex → segment → T5 → lift → assemble）
│   ├── dataset.py               # curated pair 加载 + 标识符重命名增广
│   ├── translator.py            # 推理单例 NeuralTranslator（T5 generate）
│   ├── train.py                 # 增量、可恢复 fine-tune（best-checkpoint）
│   ├── finetuned/               # ★ best fine-tuned 权重（gitignored）
│   ├── finetuned_last/          # ★ 最新 fine-tuned，供续训（gitignored）
│   └── train_meta.json          # epoch / 最佳指标
├── base_model/                  # ★ 底座（gitignored，download_base.sh 装入）
├── trainset/                    # 训练语料（与 v2 同步）
│   ├── pairs.jsonl              # chunk 级对
│   ├── programs/                # 完整程序对
│   └── verify_programs.py
└── tests/
    ├── cases/                   # 60 个用例（.go + .expected）
    ├── verify_go_cases.py
    ├── run_tests.py             # 转换 + cjc + 运行
    └── log.md                   # 自动生成
```
