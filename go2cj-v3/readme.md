# go2cj-v3 — Go → 仓颉（Cangjie）转换器（基于 CodeT5p-220m 预训练底座的二次训练方案）

> **Go 版本：** 1.24 （`go vet` 验证）
> **Cangjie 版本：** 1.0.5（`cjc cjnative`）
> **运行环境：** Python ≥ 3.10，CPU only（无需 GPU），依赖 `torch`、`transformers`、`sentencepiece`
> **底座模型：** [Salesforce/codet5p-220m](https://huggingface.co/Salesforce/codet5p-220m)（222.9 M 参数，T5+ enc-dec，d_model=768、12+12 层、12 头、byte-BPE vocab=32100，预训练含 Go 等多语言代码语料）

go2cj-v3 是对 [go2cj-v2](../go2cj-v2) 的"再换底座"——把 v2 的 60.5 M `codet5-small` 升级为 222.9 M `codet5p-220m`。**训练数据与测试用例完全复用 v2**（`trainset/` + `tests/cases/` 一比一复制），周边管线（词法 / chunk 切分 / chunk 渲染 / 跨 chunk 结构提升 / 后处理）也完全沿用 v2 的成熟实现，**唯一变量是底座模型**。

---

## 1. 为什么再换底座？

go2cj-v2 把"从零训 0.6 M 参数 Transformer"换成"在 6 种代码语言上预训练的 60.5 M `codet5-small`"后，**端到端 cjc 编译率从 4.4 %（2/45）跃升到 36.7 %（22/60）、运行匹配率从 2.2 %（1/45）跃升到 30 %（18/60）**，强力验证了"预训练先验 + 二次微调"的方向。

但 v2 在长 chunk（`func main` 整块、含多语句）上仍有可见缺陷（详见 `../go2cj-v2/tests/log.md`）：
1. **容量不足**：60.5 M 参数 / d_model=512 在 384 token 长程依赖上学不饱满，多语句缺换行、`} return` 黏连频出（虽然已被 `_split_statements` 后处理兜住，但模型本身不知道）；
2. **预训练语料偏窄**：codet5-small 在 CodeSearchNet（约 4.5 M 函数）上预训，对仓颉风格关键字（`var`、`func`、`Unit`、`ArrayList<Int64>`）很难再泛化；
3. **重复 / 死循环式输出**：v2 偶有 `ArrayList<Int64>([1,2,3])` 重复 7 次的现象——典型的小模型 beam-search 自相关问题。

`codet5p-220m`（即 CodeT5+ 第二代）相比 `codet5-small`：

| 维度 | codet5-small (v2) | codet5p-220m (v3) | 收益 |
|---|---|---|---|
| 参数量 | 60.5 M | **222.9 M（≈ 3.7×）** | 容量更大，长 chunk 拟合更稳 |
| 架构 | T5 enc/dec 各 6 层、8 头、d_model=512 | T5+ enc/dec 各 12 层、12 头、d_model=768 | 深度 / 宽度均翻倍 |
| 预训练语料 | CodeSearchNet (~6 lang) | CodeSearchNet + BigQuery + GitHub 大规模代码（~26 M 函数，9 种语言，含 Span Denoising / NextTokenPrediction / Contrastive 多任务） | Go 表面形式覆盖更广，跨函数 / 跨文件结构感更强 |
| 上下文 | 512 BPE | 512 BPE（v2 实际用 384，因为模型小放不下长程） | 同 |
| Tokenizer | RobertaTokenizer (byte-BPE, vocab=32100) | RobertaTokenizerFast (byte-BPE, vocab=32100) | 完全兼容，可直接复用 v2 的数据预处理逻辑 |

**期望：** 同一份训练数据下，仅"换底座 + 同样的二次微调协议"，应当在端到端 cjc 编译率 / 运行匹配率上比 v2 再上一个台阶；并因模型本身代码先验更强，转出的仓颉代码更接近"仓颉最优表达"（自然换行、合理使用 `ArrayList`/`HashMap`/`println`、不机械翻译 Go 习语）。

---

## 2. 端到端管线

```
┌──────────┐   ┌────────────┐   ┌──────────────────┐
│ Go 源码  │ → │ regex lexer│ → │ ; injection +    │
└──────────┘   └────────────┘   │ chunk segmenter  │
                                └────────┬─────────┘
                                         ▼ (每个 chunk 渲染回自然 Go 源码)
                        ┌──────────────────────────────┐
                        │  Fine-tuned CodeT5p-220m     │
                        │  (222.9 M params, T5+ enc-dec│
                        │   d_model=768, 12/12 layers, │
                        │   12 heads, byte-BPE vocab)  │
                        │  prompt: "translate Go to    │
                        │           Cangjie: <chunk>"  │
                        │  beam=4, repetition_penalty  │
                        │  =1.15, no_repeat_ngram=6    │
                        └────────────┬─────────────────┘
                                     ▼
                        ┌──────────────────────────────┐
                        │ cross-chunk structural       │
                        │ lifting (复用 v2 的 lifting) │
                        │ • struct → class + init      │
                        │ • free `func (r T) M(...)`   │
                        │   挂回 class                 │
                        │ • implicit interface → `<:`  │
                        └────────────┬─────────────────┘
                                     ▼
                        ┌──────────────────────────────┐
                        │ assemble: drop pkg/import,   │
                        │ inject `import std.collec.*`,│
                        │ wrap free stmts in main(),   │
                        │ _split_statements / _indent  │
                        └────────────┬─────────────────┘
                                     ▼
                              ┌─────────────┐
                              │ Cangjie 源码 │
                              └─────────────┘
```

非 NN 步骤与 v2 完全相同；**唯一区别**是 chunk 级翻译由 `NeuralTranslator`（codet5p-220m 的 `generate`，beam=4 + repetition_penalty=1.15 + no_repeat_ngram_size=6 抑制重复幻觉）完成。

---

## 3. 训练数据：`trainset/`

直接复用 go2cj-v2 的 `trainset/`，按要求"适当调整后使用"——本次"调整"是**完全不动**（CodeT5p 与 CodeT5-small 共用 byte-BPE 分词、共用 T5ForConditionalGeneration 接口，不需要重新匿名化或重写增广）。

```
trainset/
├── readme.md
├── pairs.jsonl              ← chunk 级 Go↔仓颉对（354 行）
├── programs/                ← 完整程序对 30 套（60 个文件），每套 go run 与 cjc 双向编译运行通过
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
bash scripts/download_base.sh   # 把 codet5p-220m.zip (≈420 MB) 解压到 base_model/
```

模型存放：

| 目录 | 角色 | 何时更新 |
|---|---|---|
| `base_model/` | 预训练 CodeT5p-220m（不进 git，由 download 脚本拉取，~427 MB） | 仅 `download_base.sh` |
| `go2cj_v3/finetuned/` | **最优** fine-tuned，供推理（~850 MB） | 仅当本 epoch `val_seq_acc` 严格优于历史最佳时覆盖 |
| `go2cj_v3/finetuned_last/` | 最新 fine-tuned，供续训（~850 MB） | 每个 epoch 末写 |
| `go2cj_v3/train_meta.json` | 当前 epoch / 最佳 epoch / 最佳 val 指标 | 每个 epoch 末写 |

所有 fine-tuned 权重 / base model 都在 `.gitignore` 中，不进仓库。复现完整训练只需 `download_base.sh` + `python -m go2cj_v3.train`。

### 增量训练命令

```bash
# 默认：1 个 epoch 增量微调
python -m go2cj_v3.train

# 多 epoch
python -m go2cj_v3.train --epochs 3

# 从底座重启（清空 finetuned/）
python -m go2cj_v3.train --restart --epochs 3

# 调超参（CPU 资源紧张时把 seq 收紧到 128 可大幅加速）
python -m go2cj_v3.train --epochs 3 --batch-size 2 --lr 3e-5 \
    --augment-factor 4 --max-input-len 192 --max-target-len 192 \
    --warmup-steps 80
```

### 已选定的训练超参

| 项 | 取值 / 说明 |
|---|---|
| 底座 | `Salesforce/codet5p-220m`（222.9 M params, T5+, d_model=768, 12 enc / 12 dec, 12 heads, byte-BPE vocab=32100） |
| 输入格式 | `"translate Go to Cangjie: " + <chunk>` —— 与 v2 一致的 T5 任务前缀 |
| 损失 | T5 自带 cross-entropy（label_pad=-100） |
| 优化器 | AdamW (wd=1e-4)，lr=3e-5，**linear warmup 80 steps** —— 比 v2 (5e-5) 略小，因 220M 参数对 lr 更敏感 |
| 数据 | 395 curated pairs × **identifier-rename 增广因子 4-8** ≈ 1.5K-3K 训练样本 |
| 序列长度 | 输入 / 输出各 192 BPE token（curated 集 p99=90，留 2× 余量） |
| 解码 | beam=4, **repetition_penalty=1.15**, **no_repeat_ngram_size=6**（针对 v2 观察到的重复幻觉问题） |
| Checkpoint 选优 | val_seq_acc 严格更优才覆盖 `finetuned/`，劣化版本不污染推理 |
| 校验集 | 5% canonical pairs 留出（典型 ~20 条），从增广集中剔除避免泄漏 |

> **断点续训范式**：与 v2 一致。沙箱中推荐 1-3 epochs / 会话，每次从 `finetuned_last/` 续训。
> **CPU 训练耗时（实测）**：seq=192、batch=2、aug_factor=4 → 单 epoch ≈ 40-50 min。

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

如果尚未训练，`NeuralTranslator` 会回退到 `base_model/` —— 此时输出基本不可用（未微调到 Cangjie 输出空间），但 import / generate API 可以走通便于调试。

---

## 6. 测试

测试套件直接复用 `go2cj-v2/tests/cases/`（60 个用例 + `.expected` 文件），调用方式：

```bash
source /tmp/cangjie/envsetup.sh
cd go2cj-v3
python3 tests/verify_go_cases.py   # 先验证 .go + .expected 自洽（60/60 PASS）
python3 tests/run_tests.py         # 端到端转换 + cjc 编译 + 运行
```

`tests/log.md` 自动生成，含覆盖率 / cjc 编译率 / 运行匹配率 / 综合评分。

最新结果汇总记录在 `history.md`。

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
│   ├── converter.py             # 主管线（lex → segment → T5+ → lift → assemble）
│   ├── dataset.py               # curated pair 加载 + 标识符重命名增广
│   ├── translator.py            # 推理单例 NeuralTranslator（codet5p-220m generate）
│   ├── train.py                 # 增量、可恢复 fine-tune（best-checkpoint + warmup）
│   ├── finetuned/               # ★ best fine-tuned 权重（gitignored）
│   ├── finetuned_last/          # ★ 最新 fine-tuned，供续训（gitignored）
│   └── train_meta.json          # epoch / 最佳指标
├── base_model/                  # ★ 底座（gitignored，download_base.sh 装入）
├── trainset/                    # 训练语料（与 go2cj v1/v2 同步）
│   ├── pairs.jsonl              # 354 chunk 级对
│   ├── programs/                # 30 套完整程序对
│   └── verify_programs.py
└── tests/
    ├── cases/                   # 60 个用例（.go + .expected）
    ├── verify_go_cases.py
    ├── run_tests.py             # 转换 + cjc + 运行
    └── log.md                   # 自动生成
```
