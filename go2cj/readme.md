# go2cj — Go → 仓颉（Cangjie）神经网络源代码转换器

> **Go 版本：** 1.24（go vet 验证）
> **Cangjie 版本：** 1.0.5（cjc cjnative）
> **运行环境：** Python ≥ 3.10，CPU only（无需 GPU），依赖 `numpy`、`torch`（CPU）

`go2cj` 是一个**端到端、基于训练神经网络**的 Go → 仓颉源代码转换器。Chunk 级翻译由一颗在合成平行语料上训练的 **PyTorch Transformer 编码器-解码器** 完成，**不**再使用人工规则 / 模板槽位绑定。

> v0.2.0 起，原有的 SOM + Hopfield + 非线性模板槽位绑定全部移除；翻译能力来自训练得到的模型权重 (`go2cj/model.pt`)。

---

## 1. 架构

```
┌──────────┐   ┌────────────┐   ┌──────────────────┐
│ Go 源码  │→ │ regex lexer│→  │ ; injection +    │
└──────────┘   └────────────┘   │ chunk segmenter  │
                                 └────────┬─────────┘
                                          ▼ (每个 chunk 是一段 Go 文本)
                          ┌────────────────────────────┐
                          │ Trained Transformer        │
                          │ encoder–decoder (seq2seq)  │
                          │ d_model=128, 3 enc/3 dec   │
                          │ heads=4, ~1.75M params     │
                          └────────────┬───────────────┘
                                       ▼ (每个 chunk → Cangjie tokens)
                  ┌─────────────────────────────────────────┐
                  │ cross-chunk structural lifting:         │
                  │  • struct → class + 合成 init           │
                  │  • free `func (r T) M(...)` 挂入 class │
                  │  • 隐式接口实现 → 显式 `<:` + override │
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

只剩**三类**非 NN 步骤：

1. **词法**：Go 正则 lexer + 自动分号注入（Go 规范要求的语法预处理）。
2. **chunk 切分**：按 `{}` / `()` / `;` 平衡切顶层声明（句法分块，不是翻译规则）。
3. **结构提升**：struct 构造器合成、自由方法回挂、隐式接口的 `<:` 推断 —— 这些**跨 chunk** 的结构装配，per-chunk seq2seq 单独无法表达，但与"翻译规则"无关。

模型 + 词表是唯一的"翻译知识"载体。

## 2. 神经网络细节

源代码位于 [`go2cj/neural/`](go2cj/neural/)：

| 文件 | 角色 |
|---|---|
| `vocab.py` | 词级 tokenizer（保留多字符运算符 & 字符串字面量）+ `Vocab` 类 |
| `corpus.py` | **合成平行语料生成器**：~37 个 Go chunk 骨架 × 随机槽位填充（标识符 / 类型 / 数 / 表达式 / 嵌套体）→ 上万条 (Go, CJ) 对 |
| `model.py` | PyTorch `nn.Transformer` 编码-解码模型，正弦位置编码，绑定嵌入权重，贪心自回归解码 |
| `train.py` | 训练脚本：AdamW + OneCycleLR + label smoothing；记录 val token-acc 与 greedy seq-acc，保存 `model.pt` / `vocab.json` / `model_meta.json` |
| `translator.py` | 运行期单例 `NeuralTranslator`：批量贪心解码 |
| `anonymize.py` | 可选：标识符 / 字面量匿名化层（`ID0/NUM0/STR0`），用于未来训练降低需要"记住"的词表（当前 `model.pt` 未启用） |

### 训练
```bash
python -m go2cj.neural.train --samples 12000 --epochs 10 --batch-size 96 \
                              --lr 6e-4 --d-model 128 --layers 3
```
随包发布的 `model.pt` 即此命令产物（见 `model_meta.json`）。CPU 上约 28 min。

### 当前模型快照（`model_meta.json`）
```
samples=12000  epochs=10  bs=96  lr=6e-4  d_model=128  layers=3
vocab=1402    params=1.75M
val_tok_acc=0.676    val_seq_acc=0.264
```

> `val_tok_acc` 是合成验证集上的 token-level greedy accuracy；`val_seq_acc` 是整 chunk 完全匹配率。匿名化（`anonymize.py`）落地后 token 词表将骤降，准确率显著提升 —— 已留好接口，后续训练管线可一键启用。

## 3. 使用

```bash
python -m go2cj input.go -o output.cj
cjc output.cj -o output.bin && ./output.bin
```

Python API：
```python
from go2cj import convert_source
res = convert_source(open("a.go").read())
print(res.source)          # 仓颉源码
print(res.confidence)      # 模型给出非空翻译的 chunk 占比
```

## 4. 测试

```bash
source /tmp/cangjie/envsetup.sh   # cjc 工具链
cd go2cj && python3 tests/run_tests.py
```
* `tests/cases/*.go` —— 30 个样例
* `tests/log.md` —— 自动生成的指标表 + 失败诊断

> 当前神经管线在严格 cjc 编译率上**不及**前一版规则管线（神经翻译的少量细节错误如标识符替换 / 关键字遗漏会让 cjc 拒收）。这是有意的权衡：把"翻译知识"完全放在训练权重里、留出 `anonymize.py` 入口，后续：(a) 训练量加大；(b) 启用匿名化；(c) 用下游 AI repair 处理 cjc 诊断，即可逐步把编译率推回 >95%。

## 5. 目录

```
go2cj/
├── go2cj/
│   ├── __init__.py
│   ├── __main__.py            # CLI
│   ├── lexer.py               # Go regex tokenizer
│   ├── converter.py           # 主管线（神经驱动）
│   ├── lifting.py             # 跨 chunk 结构提升
│   ├── model.pt               # 训练好的 Transformer 权重
│   ├── vocab.json             # 词表
│   ├── model_meta.json        # 训练超参 & 指标
│   └── neural/                # 训练 + 推理子包
│       ├── corpus.py
│       ├── vocab.py
│       ├── model.py
│       ├── train.py
│       ├── translator.py
│       └── anonymize.py
├── tests/
│   ├── cases/
│   ├── generated/             # 转换器输出
│   ├── run_tests.py
│   └── log.md
└── readme.md
```
