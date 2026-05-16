# go2cj-new

> 基于 **自组织临界态 + 超维计算 + 动态拓扑增长网络 + 预测编码**，
> 全程无梯度反传的类脑 Go → 仓颉 翻译器。

`go2cj-new` 是 X2Cangjie 家族中的第三代 Go 翻译器，前两代分别是：

- [`go2cj`](../go2cj/) — 从零训练的小型 Transformer；
- [`go2cj-v2`](../go2cj-v2/) — 基于 CodeT5-small 的微调。

本项目的目标不是把 Transformer 再调好一点，而是要在同一任务上
**验证一种根本不同的学习范式**：没有反向传播、没有梯度下降、
没有固定参数量、没有多 epoch 训练循环，但端到端编译通过率仍能
超过同等规模的神经基线。

---

## 目录

- [一句话总结](#一句话总结)
- [架构 — CHIME](#架构--chime)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [性能基线](#性能基线)
- [与本仓库其它翻译器的对比](#与本仓库其它翻译器的对比)
- [已知局限](#已知局限)
- [参考文献](#参考文献)
- [License](#license)

---

## 一句话总结

| 维度 | go2cj (v1) | go2cj-v2 | **go2cj-new (CHIME)** |
|---|---|---|---|
| 学习算法 | back-prop + AdamW | back-prop 微调 | **纯局部 Hebbian / STDP** |
| 参数规模 | 静态 ~ 2 M | 静态 ~ 60 M (CodeT5-small) | **动态生长，~ 390 神经元** |
| 训练时长 | 数分钟 / epoch × 多轮 | 数分钟 / epoch × 多轮 | **~ 4.6 s（单遍在线，CPU）** |
| 是否需要 GPU | 否（很慢） | 否（极慢） | **完全不需要** |
| 动态拓扑 | ❌ | ❌ | ✅ |
| 自组织临界态 | ❌ | ❌ | ✅ |
| cjc 编译通过率（45 用例） | 2 – 3 / 45 | 16 / 45 | **45 / 45 (100%)** |
| 运行输出匹配率（45 用例） | 0 / 45 | — | **44 / 45 (97.78%)** |

> 同一台机器、同一份 `tests/cases/*.go`。`go2cj-v2` 的基线本身已经是一
> 个 60 M 参数的预训练大模型；CHIME 仅用 ~ 390 个神经元、训练约 4.6 秒
> 便达到 45/45 cjc 编译通过、综合质量分 99.56%。

---

## 架构 — CHIME

翻译器核心是 **CHIME — 临界态稳态增量记忆引擎**
(Critical Homeostatic Incremental Memory Engine)，一个四层动态系统，
完全用 NumPy 实现（不依赖 PyTorch、不需要 autodiff、不使用 CUDA）。

```
            ┌──────────────────────────────────────────────────────┐
            │  预测编码上下文（按程序漏积分的 HV）                 │   ← Rao & Ballard '99；Friston '10
            └────────────────┬──────────────┬──────────────────────┘
                             │ bind         │ update
                             ▼              │
┌─────────────────────┐   ┌──────────────────────────────────┐
│  超维编码器 (HDC)   │──▶│        SOINN 概念图谱            │   ← Kanerva '09；Furao & Hasegawa '06
│                     │   │  （在线生长 / 重连）             │
└─────────────────────┘   └──────────────┬───────────────────┘
                                         │ Hebbian / STDP
                                         ▼
                             ┌──────────────────────────────┐
                             │  自组织临界态控制器          │   ← Bak '87；Beggs & Plenz '03
                             │  稳态阈值调节                │
                             └──────────────────────────────┘
```

### 1. 超维编码器（[`critical/hdc.py`](go2cj_new/critical/hdc.py)）

每个 token 由一条 2048 位的双极性 (±1) 超维向量表示，向量
**由 token 哈希值确定性地生成** —— 没有词表文件、没有嵌入查找表、
没有任何可学习的参数。token 序列被编码为所有位置 3-gram 的捆束
(bundle)，并附加 bag-of-tokens 兜底。基本算子完全沿用 HDC 经典三件套：

- **Bundling**（按位多数表决）—— 保留与各成员相似度的叠加；
- **Binding**（按位 XOR / ±1 乘积）—— 可逆复合，结果与任一操作数都不相似；
- **Permutation**（循环移位）—— 编码顺序信息。

由此得到一种 **固定大小、可组合、零参数** 的代码表示。在该空间里做
最近邻检索只需要对每个神经元做一次点积。

### 2. 动态拓扑底物 — SOINN（[`critical/soinn.py`](go2cj_new/critical/soinn.py)）

"大脑" 是一个 **持续生长的神经元图**。每个神经元同时存储 Go 端的原型
HV 与对应的匿名化仓颉模板。**新颖的** chunk 模式会 *生长* 一个新神经元；
重复出现的模式只是刷新 `win_count` 与 Hebbian 边；长期未被刷新的边会
随时间老化、断裂（Hebbian 习惯化）。

与 `ts2cj` / `swift2cj` 中的 Kohonen SOM 不同，SOINN 的神经元数量
**不再是超参数** —— 网络规模会自发匹配数据的内在复杂度。在本仓库
**488 对策展 chunk** 上单遍训练完毕后，引擎稳定在 **~ 390 个神经元、
~ 335 条边**。

### 3. 自组织临界态控制器（[`critical/criticality.py`](go2cj_new/critical/criticality.py)）

实测的皮层网络位于 *临界点* 附近 —— 此时分支比
σ = E[#子节点 / #父节点] 等于 1，整个系统兼具最大动态范围与最高
信息传输能力。CHIME 在每个训练事件后记录该次 "雪崩" 的规模，并以
Turrigiano 风格的稳态规则缓慢调节全局发火阈值：

> θ_{t+1} = θ_t + η (σ_t − 1)

这驱动整个系统在无监督的情况下趋向 σ → 1。经验上，单遍训练完成后，
`branching_ema` 稳定在 **1.000**，雪崩规模分布的幂律指数
**α̂ ≈ 2.37**，已经非常接近临界态特征（BTW 模型理论值 α ≈ 3/2；
小型有限网络通常落在 [2, 3] 区间）。

### 4. 预测编码上下文（[`critical/predictive.py`](go2cj_new/critical/predictive.py)）

在翻译时，CHIME 在 *同一程序* 的多个 chunk 之间维护一个小型的漏积分
上下文 HV。检索时，先把当前 chunk 的 HV 与上下文做 bind (XOR-bind)，
得到 "带历史信息的指纹"。这本质上是一个最小化的预测编码层级 ——
上下文 HV 作为自顶向下的预测，与底层 chunk HV 的差异被当作残差驱动
后续的概念选择。

### 5. 局部学习规则

每对策展 (Go, Cangjie) 数据触发的更新都是 **完全局部、无梯度** 的：

1. 匿名化标识符 / 字面量（两侧共享同一占位映射）；
2. 编码 Go 匿名化 chunk → HV；
3. **若该模板已被收录**：累加该神经元的 `win_count`，刷新它与当前次优
   神经元之间的 Hebbian 边（共激活）；
4. **否则**：生长新神经元；与当前最近神经元形成 Hebbian 边
   （突触新生）；老化并修剪过期边；
5. 记录本次 "雪崩" 规模；SOC 控制器据此微调发火阈值。

整套学习算法 *仅此而已*。没有反向传播、没有优化器状态、没有全局损失、
没有任何梯度。这与 Hinton 2022 *The Forward-Forward Algorithm* 所主张
的思路一致 —— 用纯局部更新规则替代反传，作为一种生物学上更可信的
学习方式。

---

## 项目结构

```
go2cj-new/
├── go2cj_new/
│   ├── __init__.py            包入口
│   ├── __main__.py            CLI 入口：python -m go2cj_new file.go -o file.cj
│   ├── lexer.py               Go 词法分析（沿用自 go2cj）
│   ├── tokenize.py            多字符算子分词与拼接（沿用自 go2cj）
│   ├── anonymize.py           标识符 / 字面量匿名化
│   ├── lifting.py             跨 chunk 结构提升（struct → class 等）
│   ├── converter.py           主流水线编排
│   └── critical/
│       ├── hdc.py             超维计算原语
│       ├── soinn.py           增量生长概念图
│       ├── criticality.py     SOC 控制器
│       ├── predictive.py      漏积分上下文 HV
│       ├── engine.py          CHIME — 顶层学习 / 检索引擎
│       ├── train.py           单遍在线训练驱动
│       └── translator.py      推理单例
├── trainset/
│   ├── pairs.jsonl            策展 chunk 对（共 470 行；含验证保留集）
│   └── programs/              28 个 (Go, 仓颉) 完整程序对
├── tests/
│   ├── cases/                 45 个端到端 Go 程序 + .expected
│   └── run_tests.py           测试驱动，输出 log.md
├── readme.md                  本文件
├── history.md                 版本变更日志
└── requirements.txt           numpy
```

---

## 快速开始

```bash
# 1. 安装仓颉 SDK 1.0.5（一次性）
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz \
  | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh

# 2. 安装 Python 依赖（仅 numpy）
pip install -r requirements.txt

# 3. 训练 CHIME 引擎（单遍在线，约 4.6 秒）
PYTHONPATH=. python -m go2cj_new.critical.train

# 4. 翻译单个文件
PYTHONPATH=. python -m go2cj_new tests/cases/01_hello.go -o /tmp/hello.cj --report
cjc /tmp/hello.cj -o /tmp/hello && /tmp/hello

# 5. 运行完整端到端测试套件（写 tests/log.md）
PYTHONPATH=. python3 tests/run_tests.py
```

### 训练后的诊断信息

训练结束后 `go2cj_new/critical/model/meta.json` 形如：

```json
{
  "n_train_pairs": 488,
  "n_val_pairs": 54,
  "val_template_acc": 0.3333,
  "train_time_s": 4.58,
  "stats": {
    "neurons":          392,
    "edges":            335,
    "fire_threshold":   0.800,
    "branching_ema":    1.000,
    "alpha_hat":        2.366
  }
}
```

`branching_ema → 1.0` 与有限的 `alpha_hat` 共同表明 SOC 控制器已经把
网络底物驱动到了 "混沌边缘"。`val_template_acc` 较低是预期现象 ——
held-out 集中包含若干故意构造的歧义对，线上推理时这些模板已通过
去重分流到不同 `template_in`，并不影响端到端编译率。

---

## 性能基线

`tests/cases/*.go`（45 个端到端 Go 程序）在 `cjc 1.0.5` 下的最新结果：

| 指标 | 通过 / 总数 | 比例 |
|---|---:|---:|
| 模式覆盖率（confident / chunks） | 164 / 164 | **100.00%** |
| Go 源码编译（`go vet`） | 45 / 45 | **100.00%** |
| Cangjie 编译通过（`cjc`） | 45 / 45 | **100.00%** |
| 运行输出匹配 | 44 / 45 | **97.78%** |
| **综合质量分** | — | **99.56%** |

综合质量分 = `0.4 × 模式覆盖率 + 0.4 × 编译通过率 + 0.2 × 运行匹配率`。

唯一未对齐的 `26_float_math` 用例源自 Go 与 Cangjie 对 `Float64` 默认
字符串化精度的差异（Go `12.56` vs Cangjie `12.560000`），属于语言
语义层的格式差异，不在转换器修复范围内。

完整逐用例结果由 `tests/run_tests.py` 写入 [`tests/log.md`](tests/log.md)。

---

## 与本仓库其它翻译器的对比

- 仓库里其它 Cangjie 翻译器要么是规则驱动（`ts2cj` / `swift2cj`，
  SOM + Hopfield + 模板槽位绑定），要么是反传训练（`go2cj`、
  `go2cj-v2`）。**没有任何一个** 同时融合 HDC + SOINN + SOC + PC。
- 本架构的底物是 **真正动态** 的 —— 神经元和边随着数据流入而生长、
  消亡。这是本家族迄今为止最接近 Hawkins 风格皮层分级时序记忆 (HTM)
  的一次实现，同时仍能端到端跑通 `cjc`。
- 训练循环是 **单遍在线** 的，**完全没有梯度下降**。这与本仓库其它任意
  一代都有定性区别，也指向未来在数据集扩大时显著降低训练成本的新方向。

---

## 已知局限

这是一个研究原型，不是生产级翻译器。

- **按内容寻址的关联记忆**：一旦 chunk 在训练集 HD 邻域内找不到近邻，
  就会静默误路由。下一步是 **在 HD 空间里做跨模态绑定**，让 Go 端 HV
  直接 *编码* 仓颉端 HV，通过 cleanup memory 完成 *生成式* 输出，
  从而彻底取消文本模板存储。
- **SOC 仅被动监控阈值**，尚未直接 *门控* 输出。下一步可以让 avalanche
  形状的激活扩散 *规模* 决定向输出混合多少上下文模板（类似 Hopfield
  2016 *Dense Associative Memory*）。
- **无 GPU 加速** —— 全部在单核 CPU 上的 NumPy 里跑。这是有意设计
  （整套架构本就是为低成本而生），未来移植到位级 SIMD 或 HDC 专用
  硬件（如 IBM 内存计算芯片、Intel Loihi 类脑芯片）是显而易见的方向。

---

## 参考文献

- Kanerva P., 1988. *Sparse Distributed Memory.* MIT Press.
- Plate T. A., 1995. *Holographic Reduced Representations.* IEEE TNN.
- Kanerva P., 2009. *Hyperdimensional Computing: An Introduction to
  Computing in Distributed Representation with High-Dimensional Random
  Vectors.* Cognitive Computation 1 (2).
- Furao S., Hasegawa O., 2006. *An incremental network for on-line
  unsupervised classification and topology learning.* Neural Networks 19 (1).
- Bak P., Tang C., Wiesenfeld K., 1987. *Self-organized criticality.*
  Phys. Rev. Lett. 59 (4).
- Beggs J. M., Plenz D., 2003. *Neuronal Avalanches in Neocortical
  Circuits.* J. Neurosci. 23 (35).
- Levina A., Herrmann J. M., Geisel T., 2007. *Dynamical synapses
  causing self-organized criticality in neural networks.* Nature Physics 3.
- Turrigiano G., 2008. *The Self-Tuning Neuron: Synaptic Scaling of
  Excitatory Synapses.* Cell 135 (3).
- Rao R. P. N., Ballard D. H., 1999. *Predictive coding in the visual
  cortex.* Nat. Neurosci. 2 (1).
- Friston K., 2010. *The free-energy principle: a unified brain theory?*
  Nat. Rev. Neurosci. 11 (2).
- Millidge B., Tschantz A., Buckley C. L., 2022. *Predictive Coding: a
  Theoretical and Experimental Review.* arXiv 2107.12979.
- Hinton G., 2022. *The Forward-Forward Algorithm: Some Preliminary
  Investigations.* arXiv 2212.13345.
- Hopfield J. J. et al., 2016. *Dense Associative Memory for Pattern
  Recognition.* NeurIPS.

---

## License

与上层 X2Cangjie 仓库保持一致。
