# go2cj-v2 — Go → 仓颉（Cangjie）转换器（基于 CodeT5-small 预训练底座的二次训练方案）

> **Go 版本：** 1.24 （`go vet` 验证）
> **Cangjie 版本：** 1.0.5（`cjc cjnative`）
> **运行环境：** Python ≥ 3.10，CPU only（无需 GPU），依赖 `torch`、`transformers`、`sentencepiece`
> **底座模型：** [Salesforce/codet5-small](https://huggingface.co/Salesforce/codet5-small)（60.5 M 参数，T5 enc-dec，预训练含 Go 等 6 种代码语言）

go2cj-v2 是对 [go2cj](../go2cj) 神经网络方案的换底重做：把"从零训的 0.6 M 参数小 Transformer"换成"在代码语料预训练过的 60 M 参数 CodeT5-small 上做二次微调"。除翻译核心外，词法 / chunk 切分 / 跨 chunk 结构提升 / 装配等周边管线沿用 go2cj v1 的成熟实现。

---

## 1. 为什么换底座？

go2cj v1 在 chunk 级 `val_seq_acc` 已经达到 ~0.74，但 `tests/cases/*.go` 端到端 `cjc` 编译率长期停留在 2–3/45（≈4-7%）。诊断（详见 [go2cj/history.md](../go2cj/history.md)）：

* **参数太小**：0.6 M 参数 + 词级 tokenizer 无法泛化到稍长的 chunk。
* **零先验**：模型对 Go 与 Cangjie 都是从零学，长程依赖（`func main` 整块作为单 chunk 输入）严重 OOD。
* **数据规模有限**：手工 curated ~300 对 × 60× 增广只能覆盖匿名化模板。

二次训练方案的核心假设：**用一个已经在 Go 等代码语料上预训练过的小模型当起点，模型本来就知道 `:=`、`for i := 0; i < n; i++`、`fmt.Println` 是什么，再用少量 Go↔Cangjie 监督对引导它输出 Cangjie 即可。**

候选调研：

| 候选 | 参数量 | 架构 | 预训练语料 | 选择 |
|---|---|---|---|---|
| **Salesforce/codet5-small** | 60.5 M | T5 enc-dec | CodeSearchNet（Go/Python/Java/JS/PHP/Ruby）+ BigQuery，多任务（含 code-to-code） | ✅ |
| Salesforce/codet5p-220m | 220 M | T5+ enc-dec | 同上 + 更多语料 | 太重，CPU 单 epoch 30-60 min |
| uclanlp/plbart-base | 140 M | BART | 含 Java/Python，无 Go | 次选 |
| google/t5-small | 60 M | T5 | 纯文本 | 缺代码语料，先验弱 |

CodeT5-small 自带 RobertaTokenizer（byte-level BPE）可以处理任意标识符 / 字面量，因此**舍弃 v1 的 anonymization 层**，改成更轻量的"标识符随机重命名"做数据增广。

---

## 2. 端到端管线

```
┌──────────┐   ┌────────────┐   ┌──────────────────┐
│ Go 源码  │ → │ regex lexer│ → │ ; injection +    │
└──────────┘   └────────────┘   │ chunk segmenter  │
                                └────────┬─────────┘
                                         ▼ (每个 chunk 是 Go 源文本)
                        ┌──────────────────────────────┐
                        │  Fine-tuned CodeT5-small     │
                        │  (60.5 M params, T5 enc-dec, │
                        │   d_model=512, 6/6 layers,   │
                        │   8 heads, byte-BPE vocab)   │
                        │  prompt: "translate Go to    │
                        │           Cangjie: <chunk>"  │
                        └────────────┬─────────────────┘
                                     ▼
                        ┌──────────────────────────────┐
                        │ cross-chunk structural       │
                        │ lifting (复用 v1 的 lifting) │
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

非 NN 步骤（词法、chunk 切分、结构装配）与 v1 完全相同，**唯一区别**是 chunk 级翻译由 `NeuralTranslator`（T5 enc-dec 的 `generate`，beam=4 贪心）完成。

---

## 3. 训练数据：`trainset/`

数据组织与 go2cj v1 完全一致（直接复制过来，已按要求"适当调整后使用"——`anonymize_pair` 不再使用，取而代之是 byte-BPE + identifier-rename 增广）：

```
trainset/
├── readme.md
├── pairs.jsonl              ← chunk 级 Go↔仓颉对（303 条）
├── programs/                ← 完整程序对 15 套，每套 go run 与 cjc 双向编译运行通过
└── verify_programs.py
```

### 数据自验证

```bash
source /tmp/cangjie/envsetup.sh
cd go2cj-v2
python3 trainset/verify_programs.py     # programs/*.go vs *.cj
python3 tests/verify_go_cases.py        # tests/cases/*.go vs *.expected
```

### 添加训练数据

1. 在 `pairs.jsonl` 追加一行 `{"go": "...", "cj": "..."}`。
2. 或在 `programs/` 添加 `<name>.go` 与 `<name>.cj` 对（顶层 chunks 顺序对齐）。
3. `python -m go2cj_v2.train --epochs 1` 增量微调（权重自动从 `finetuned_last/` 续）。

---

## 4. 训练 & best-checkpoint 协议

### 一次性：下载底座模型

```bash
bash scripts/download_base.sh   # 把 codet5-small.zip 解压到 base_model/
```

模型存放：

| 目录 | 角色 | 何时更新 |
|---|---|---|
| `base_model/` | 预训练 CodeT5-small（不进 git，由 download 脚本拉取） | 仅 `download_base.sh` |
| `go2cj_v2/finetuned/` | **最优** fine-tuned，供推理 | 仅当本 epoch `val_seq_acc` 严格优于历史最佳时覆盖 |
| `go2cj_v2/finetuned_last/` | 最新 fine-tuned，供续训 | 每个 epoch 末写 |
| `go2cj_v2/train_meta.json` | 当前 epoch / 最佳 epoch / 最佳 val 指标 | 每个 epoch 末写 |

所有 fine-tuned 权重 / base model 都在 `.gitignore` 中（每份 ~230 MB），不进仓库。复现完整训练只需 `download_base.sh` + `python -m go2cj_v2.train`。

### 增量训练命令

```bash
# 默认：1 个 epoch 增量微调（CPU 上约 8-12 分钟）
python -m go2cj_v2.train

# 多 epoch
python -m go2cj_v2.train --epochs 3

# 从底座重启（清空 finetuned/）
python -m go2cj_v2.train --restart --epochs 3

# 调超参
python -m go2cj_v2.train --epochs 3 --batch-size 4 --lr 5e-5 \
    --augment-factor 10 --max-input-len 384 --max-target-len 384
```

### 已选定的训练超参

| 项 | 取值 / 说明 |
|---|---|
| 底座 | `Salesforce/codet5-small`（60.5 M params, T5, d_model=512, 6 enc / 6 dec, 8 heads, byte-BPE vocab=32100） |
| 输入格式 | `"translate Go to Cangjie: " + <chunk>` —— 标准 T5 任务前缀 |
| 损失 | T5 自带 cross-entropy（label_pad=-100） |
| 优化器 | AdamW (wd=1e-4)，固定 lr=5e-5（CodeT5 微调推荐范围） |
| 数据 | 303 curated pairs × **identifier-rename 增广因子 10** ≈ 3000 训练样本 |
| 序列长度 | 输入 / 输出各 384 BPE token（足够覆盖最长的 func main 单 chunk） |
| 解码 | beam=4, greedy（`generate`），CPU 单 chunk ~200-500 ms |
| Checkpoint 选优 | val_seq_acc 严格更优才覆盖 `finetuned/`，劣化版本不污染推理 |
| 校验集 | 5% canonical pairs 留出（典型 15 条），从增广集中剔除避免泄漏 |

> **断点续训范式**：与 v1 一致。沙箱中推荐 1-3 epochs / 会话，每次从 `finetuned_last/` 续训。

---

## 5. 推理（`NeuralTranslator`）

```python
from go2cj_v2 import convert_source
res = convert_source(open("a.go").read())
print(res.source)
print(res.confidence)
```

CLI：

```bash
python -m go2cj_v2 input.go -o output.cj --report
```

仅 chunk 级翻译：

```python
from go2cj_v2.translator import NeuralTranslator
t = NeuralTranslator.get()
print(t.translate("x := 1"))                  # → "var x = 1"
print(t.translate("for i := 0; i < n; i++ {}"))
```

如果尚未训练，`NeuralTranslator` 会回退到 `base_model/` —— 此时输出基本不可用，但 import / generate API 可以走通便于调试。

---

## 6. 测试

测试套件直接复制自 `go2cj/tests/cases/`（45 个用例 + `.expected` 文件），调用方式：

```bash
source /tmp/cangjie/envsetup.sh
cd go2cj-v2
python3 tests/verify_go_cases.py   # 先验证 .go + .expected 自洽（45/45 PASS）
python3 tests/run_tests.py         # 端到端转换 + cjc 编译 + 运行
```

`tests/log.md` 自动生成，含覆盖率 / cjc 编译率 / 运行匹配率 / 综合评分。

---

## 7. 目录结构

```
go2cj-v2/
├── readme.md                    # 本文件
├── history.md                   # 训练历程与试错经验
├── requirements.txt             # torch + transformers + sentencepiece
├── .gitignore                   # 屏蔽 base_model/ + finetuned*/
├── scripts/
│   └── download_base.sh         # 从 GitHub release 下载 codet5-small
├── go2cj_v2/                    # Python 包
│   ├── __init__.py
│   ├── __main__.py              # CLI: python -m go2cj_v2
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
├── trainset/                    # 训练语料（与 go2cj v1 同步）
│   ├── pairs.jsonl              # 303 chunk 级对
│   ├── programs/                # 15 套完整程序对
│   └── verify_programs.py
└── tests/
    ├── cases/                   # 45 个用例（.go + .expected）
    ├── verify_go_cases.py
    ├── run_tests.py             # 转换 + cjc + 运行
    └── log.md                   # 自动生成
```
