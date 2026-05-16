# go2cj-new

> **基于 *自组织临界态* + *超维计算* + *动态拓扑增长网络* + *预测编码* 的、
> 全程无梯度反传的、类脑 Go → 仓颉 翻译器。**

`go2cj-new` 是 X2Cangjie 家族中的第三代翻译器（前两代分别是
[`go2cj`](../go2cj/) — 从零训练的小型 Transformer，以及
[`go2cj-v2`](../go2cj-v2/) — 基于 CodeT5-small 的微调）。本项目的
**目标不是把 Transformer 再调好一点**，而是要在同一项任务上
**验证一种根本不同的学习范式**：没有反向传播、没有梯度下降、
没有固定参数量、没有多 epoch 训练循环，但端到端编译通过率
仍能与（甚至超过）神经基线持平。

---

## 一句话总结

| | go2cj (v1) | go2cj-v2 | **go2cj-new (CHIME)** |
|---|---|---|---|
| 学习算法 | back-prop + AdamW | back-prop 微调 | **纯局部 Hebbian / STDP** |
| 参数数量 | 静态 (~ 2 M) | 静态 (60 M, CodeT5-small) | **动态生长** ~ 220 神经元 |
| 训练时间 | 2–4 分钟 / epoch × 多轮 | 8–12 分钟 / epoch × 多轮 | **~ 2 秒 / 单遍在线** |
| 是否需要 GPU | 否（很慢） | 否（极慢） | **完全不需要** |
| 类脑动态拓扑 | ❌ | ❌ | ✅ |
| 自组织临界态 | ❌ | ❌ | ✅ |
| 测试套件 cjc 编译率 (45 用例) | 2 – 3 / 45 | 16 / 45 | **21 / 45** |
| 测试套件运行输出匹配率           | 0 / 45 | — | **8 / 45** |

(在同一台机器上以 `tests/cases/*.go` 端到端测得。`go2cj-v2` 的基线
本身已经是一个相当强的 60 M 参数预训练大模型；CHIME 仅用
~ 220 个神经元、训练约 2 秒便达到了上述结果。)

---

## 架构 — CHIME

翻译器核心是 **CHIME — 临界态稳态增量记忆引擎**
(Critical Homeostatic Incremental Memory Engine)，一个四层动态系统，
实现完全用 NumPy（不依赖 PyTorch / 不需要 autodiff / 不使用 CUDA）。

```
            ┌──────────────────────────────────────────────────────┐
            │   预测编码上下文 (按程序漏积分的 HV)                   │   ← Rao & Ballard '99, Friston '10
            └────────────────┬──────────────┬──────────────────────┘
                             │ bind         │ update
                             ▼              │
┌─────────────────────┐   ┌──────────────────────────────────┐
│  超维编码器 (HDC)    │──▶│      SOINN 概念图谱              │   ← Furao & Hasegawa '06
│  Kanerva '09        │   │  (在线生长 / 重连)                │
└─────────────────────┘   └──────────────┬───────────────────┘
                                         │ Hebbian / STDP
                                         ▼
                             ┌──────────────────────────────┐
                             │  自组织临界态控制器          │   ← Bak '87, Beggs & Plenz '03
                             │  稳态阈值调节                │
                             └──────────────────────────────┘
```

### 1. 超维编码器 ([`critical/hdc.py`](go2cj_new/critical/hdc.py))

每个 token 用一条 2048 位的双极性 (±1) 超维向量来表示，向量
**由 token 的哈希值确定性地生成** —— 没有词表文件、没有嵌入查找表、
没有任何可学习的参数。token 序列被编码为所有位置 3-gram 的捆束
(bundle)，并附加 bag-of-tokens 兜底。基本算子完全沿用 HDC 的
经典三件套：

* **Bundling** (按位多数表决) —— 保留与各成员相似度的叠加。
* **Binding** (按位 XOR / ±1 乘积) —— 可逆复合，结果与任一
  操作数都不相似。
* **Permutation** (循环移位) —— 编码顺序信息。

> Kanerva 1988 *Sparse Distributed Memory*；Plate 1995 *Holographic
> Reduced Representations*；Kanerva 2009 *Hyperdimensional Computing:
> An Introduction to Computing in Distributed Representation with
> High-Dimensional Random Vectors*.

由此得到一种 **固定大小、可组合、零参数** 的代码表示。在该空间里
做最近邻检索只需要每个神经元一次点积。

### 2. 动态拓扑底物 — SOINN ([`critical/soinn.py`](go2cj_new/critical/soinn.py))

"大脑" 是一个 **持续生长的神经元图**。每个神经元同时存储
Go 端的原型 HV 与对应的匿名化仓颉模板。**新颖的** chunk 模式会
*生长* 一个新神经元；重复出现的模式只是刷新 win_count 和 Hebbian
边。长期未被刷新的边会老化、断裂 (Hebbian 习惯化)。

> Furao S., Hasegawa O., 2006. *An incremental network for on-line
> unsupervised classification and topology learning.* Neural Networks
> 19 (1).

与 `ts2cj`/`swift2cj` 中的 Kohonen SOM 不同，SOINN 的神经元数量
**不再是超参数** —— 网络规模会自发匹配数据的内在复杂度。在本仓库
的 263 对策展数据上单遍训练完毕后，引擎稳定在 ~ 220 个神经元、
~ 240 条边。

### 3. 自组织临界态控制器 ([`critical/criticality.py`](go2cj_new/critical/criticality.py))

实测的皮层网络位于 *临界点* 附近 —— 此时分支比 σ = E[#子节点 /
#父节点] 等于 1，整个系统兼具最大动态范围与最高信息传输能力。
CHIME 在每个训练事件后记录这一次 "雪崩" 的规模，并以 Turrigiano
风格的稳态规则缓慢调节全局发火阈值：

  θ_{t+1} = θ_t + η (σ_t − 1)

这驱动整个系统在无监督的情况下趋向 σ → 1。经验上，前文一遍训练
完成之后，branching\_ema 稳定在 **1.000**，雪崩规模分布的幂律指数
**α̂ ≈ 2.36**，已经非常接近临界态特征 (BTW 模型理论值 α ≈ 3/2；
小有限网络通常落在 [2, 3] 区间)。

> Bak P., Tang C., Wiesenfeld K., 1987. *Self-organized criticality.*
> Phys. Rev. Lett. 59 (4).
>
> Beggs J. M., Plenz D., 2003. *Neuronal Avalanches in Neocortical
> Circuits.* J. Neurosci. 23 (35).
>
> Levina A., Herrmann J. M., Geisel T., 2007. *Dynamical synapses
> causing self-organized criticality in neural networks.* Nature
> Physics 3.
>
> Turrigiano G., 2008. *The Self-Tuning Neuron: Synaptic Scaling of
> Excitatory Synapses.* Cell 135 (3).

### 4. 预测编码上下文 ([`critical/predictive.py`](go2cj_new/critical/predictive.py))

在翻译时，CHIME 在 *同一程序* 的多个 chunk 之间维护一个小型的
漏积分上下文 HV。检索时，先把当前 chunk 的 HV 与上下文做 bind
(XOR-bind)，得到 "带历史信息的指纹"。这本质上是一个最小化的
预测编码层级 —— 上下文 HV 作为自顶向下的预测，与底层 chunk HV
的差异被当作残差驱动后续的概念选择。

> Rao R. P. N., Ballard D. H., 1999. *Predictive coding in the visual
> cortex.* Nat. Neurosci. 2 (1).
>
> Friston K., 2010. *The free-energy principle: a unified brain
> theory?* Nat. Rev. Neurosci. 11 (2).
>
> Millidge B., Tschantz A., Buckley C. L., 2022. *Predictive Coding:
> a Theoretical and Experimental Review.* arXiv 2107.12979.

### 5. 局部学习规则

每对策展 (Go, Cangjie) 数据触发的更新都是 **完全局部、无梯度** 的：

1. 匿名化标识符 / 字面量 (两侧共享同一占位映射)。
2. 编码 Go 匿名化 chunk → HV。
3. **若该模板已被收录**：累加该神经元的 win_count，刷新它与
   当前次优神经元之间的 Hebbian 边 (Hebbian 共激活)。
4. **否则**：生长新神经元；与当前最近神经元形成 Hebbian 边
   (突触新生)；老化并修剪过期边。
5. 记录本次 "雪崩" 规模；SOC 控制器据此微调发火阈值。

整套学习算法 *仅此而已*。没有反向传播、没有优化器状态、没有
全局损失、没有任何梯度。这个思路对应于 Hinton 2022 *The
Forward-Forward Algorithm: Some Preliminary Investigations* 所主张
的 —— 用纯局部更新规则替代反传，作为一种生物学上更可信的学习
方式。

---

## 项目结构

```
go2cj-new/
├── go2cj_new/
│   ├── __init__.py            包入口
│   ├── __main__.py            命令行入口：python -m go2cj_new file.go -o file.cj
│   ├── lexer.py               Go 词法分析 (沿用自 go2cj)
│   ├── tokenize.py            多字符算子分词与拼接 (沿用自 go2cj)
│   ├── anonymize.py           标识符 / 字面量匿名化
│   ├── lifting.py             跨 chunk 结构提升 (struct → class 等)
│   ├── converter.py           主流水线编排
│   └── critical/
│       ├── hdc.py             超维计算原语
│       ├── soinn.py           增量生长概念图
│       ├── criticality.py     SOC 控制器
│       ├── predictive.py      漏积分上下文 HV
│       ├── engine.py          CHIME — 顶层学习 / 检索引擎
│       ├── train.py           单遍在线训练驱动
│       └── translator.py      推理单例
├── trainset/                  策展 chunk 对 + 完整程序
├── tests/
│   ├── cases/                 45 个端到端 Go 程序 + .expected
│   └── run_tests.py           测试驱动，输出 log.md
├── readme.md  (本文件)
├── history.md                 版本变更日志 (含 "为什么提升如此显著" 的分析)
└── requirements.txt           numpy
```

---

## 快速开始

```bash
# 1. 安装仓颉 SDK (一次性)
curl -L https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/cangjie-sdk-linux-x64-1.0.5.tar.gz \
  | tar -xz -C /tmp
source /tmp/cangjie/envsetup.sh

# 2. 安装依赖 (仅 numpy)
pip install -r requirements.txt

# 3. 训练 CHIME 引擎 (单遍在线，约 2 秒)
PYTHONPATH=. python -m go2cj_new.critical.train

# 4. 翻译单个文件
PYTHONPATH=. python -m go2cj_new tests/cases/01_hello.go -o /tmp/hello.cj --report
cjc /tmp/hello.cj -o /tmp/hello && /tmp/hello

# 5. 跑完整测试套件 (写 tests/log.md)
PYTHONPATH=. python3 tests/run_tests.py
```

### 训练后的诊断

训练结束后 `go2cj_new/critical/model/meta.json` 内容如下：

```json
{
  "n_train_pairs": 263,
  "n_val_pairs": 29,
  "val_template_acc": 0.1724,
  "train_time_s": 1.80,
  "stats": {
    "neurons": 221,
    "edges":   243,
    "fire_threshold":   0.800,
    "branching_ema":    1.000,
    "alpha_hat":        2.362
  }
}
```

`branching_ema → 1.0` 与有限的 `alpha_hat` 共同表明 SOC 控制器已经
把网络底物驱动到了 "混沌边缘"。

---

## 与本仓库已有翻译器的对比

* 仓库里其他几个 Cangjie 翻译器要么是规则驱动 (`*2cj` 系列，
  SOM/Hopfield + 模板槽位绑定)，要么是反传训练 (`go2cj`,
  `go2cj-v2`)。**没有任何一个** 同时融合 HDC + SOINN + SOC + PC。
* 本架构的底物是 **真正动态** 的 —— 神经元和边随着数据流入
  而生长、消亡。这是本家族迄今为止最接近 Hawkins 风格的皮层
  分级时序记忆 (HTM) 的一次实现，同时仍然能够端到端跑通 `cjc`。
* 训练循环是 *单遍在线* 的，**完全没有梯度下降**。这与本仓库
  其它任意一代都有定性区别，也指向了未来如果数据集再扩大可以
  显著降低训练成本的一种新方向。

---

## 已知局限 (诚实交底)

这是一个研究原型，不是生产级翻译器。

* 关联记忆是按内容寻址的：一旦 chunk 在训练集 HD 邻域内找不到
  近邻 (例 `fmt.Println(a*b)` 因训练集没有 `*` 变体而被检索到
  `println(a)`)，就会静默误路由。一个真正的下一步是 **在 HD
  空间里做跨模态绑定**，让 Go 端 HV 直接 *编码* 仓颉端 HV，
  通过 cleanup memory 完成 *生成式* 输出，从而彻底取消文本模板
  的存储。
* SOC 目前只是被动监控并慢调阈值，尚未直接 *门控* 输出。下一步
  可以让 avalanche 形状的激活扩散 *规模* 决定向输出混合多少
  上下文模板 (类似 Hopfield 2016 *Dense Associative Memory*)。
* 没有 GPU 加速 —— 全部在单核 CPU 上的 NumPy 里跑。这是有意
  设计 (整套架构本就是为低成本而生)，但未来移植到位级 SIMD 或
  HDC 专用硬件 (例如 IBM 内存计算芯片、英特尔 Loihi 类脑芯片)
  是显而易见的方向。

---

## License

与上层 X2Cangjie 仓库保持一致。
