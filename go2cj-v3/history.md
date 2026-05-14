# go2cj-v3 训练历程与试错经验

本文件按时间顺序记录 go2cj-v3 的关键决策与效果，供后续训练 / 调参参考。

---

## v3.0 — CodeT5p-220m 底座 + 二次微调（**当前主线**）

### 动机

go2cj-v2 用 codet5-small（60 M）作底座，在 60 个测试用例上端到端 cjc 编译率 22/60 (36.7%)、运行匹配 18/60 (30.0%)、综合 60.67%。继续诊断剩余失败 case：

* 模型已经会用 `for/while/if` 等 Cangjie 关键字，但**字段命名 / 单行布局换行 / 类型字面量精化**仍是难点；
* `} return ...`、`} var ...` 等需在 `}` 后插 NL 才能被 cjc 接受，v2 的 `_split_statements` 已经覆盖大部分，但仍有少量遗漏；
* 整数 `int → Int64` 在 `float64`、`UInt64` 等场景过粗。

这些都属于"模型表达力上限"问题——v2 已经能学到 chunk-level 1.0 val\_seq\_acc，但**生成空间太大的细节决策**（"这个变量该用 var 还是 let"、"这里要不要换行"）需要更多 attention 头 / 更宽 d\_model 才能稳定。v2 history 里也明确预留了 codet5p-220m 作为下一步备选。

### 选型

候选与决定（同 v2 调研，结论变更）：

| 候选 | 参数量 | 架构 | CPU 单 epoch 估时 | 选择 |
|---|---|---|---|---|
| Salesforce/codet5-small | 60.5 M | T5 (d\_model=512, 6/6) | ~8 min | v2 主线 |
| **Salesforce/codet5p-220m** | 220 M | T5 (d\_model=768, 12/12) | ~25-40 min | ✅ v3 主线 |
| Salesforce/codet5p-770m | 770 M | T5+ | >2 h | 过重 |

220 M 是"CPU 上仍可单机 1-3 epochs 训完、且参数量足够覆盖小语种 chunk 翻译"的甜蜜点。

底座通过 `scripts/download_base.sh` 从 `https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/codet5p-220m.zip` 获取。

### 关键调整 vs v2

* **模型加载代码完全复用**：codet5p-220m 与 codet5-small 都是 `T5ForConditionalGeneration` + `RobertaTokenizer`，`translator.py` / `train.py` 不改任何接口。
* **训练超参缩放**：
  * 默认 `--batch-size 2`（v2 是 4）：220 M 在 d\_model=768 / 12 层下，activations 体积接近 4×，CPU 单步耗时 ~2-3 倍；
  * 默认 `--lr 3e-5`（v2 是 5e-5）：更大模型更易过拟合，遵循 CodeT5+ 微调推荐范围；
  * 默认 `--augment-factor 6`（v2 是 12）：训练样本量 354 × 6 ≈ 2100，与 v2 的 ~3500 同量级，但单步更慢，需总 step 数对齐。
* **best-checkpoint 协议**沿用 v1/v2：`finetuned/` ← 严格最优、`finetuned_last/` ← 最新可续训。
* **训练 / 测试数据 100% 复用 v2**（用户要求）：`trainset/pairs.jsonl`、`trainset/programs/`、`tests/cases/` 直接拷贝。

### 训练记录

> 表格中训练数据由 `train_meta.json` + `tests/log.md` 自动生成；以下为本仓库实际跑出的曲线。

| epoch | avg loss | val\_seq\_acc | val\_tok\_acc | 备注 |
|---|---|---|---|---|
| 1 | _见 train\_meta.json_ | _见 train\_meta.json_ | _见 train\_meta.json_ | 首轮微调 |

（沙箱时间约束下，可能只跑 1-2 epochs；后续会话可以继续增量训练。）

### 端到端测试（与 v2 同一 60 case 套件）

| 指标 | go2cj-v2 (3 ep) | go2cj-v3 | 提升 |
|---|---|---|---|
| 用例总数 | 60 | 60 | — |
| 模式覆盖率 | 100% | 100% | — |
| Go vet 通过 | 60/60 | 60/60 | — |
| **cjc 编译通过** | 22/60 (36.7%) | _见 tests/log.md_ | _待填_ |
| **运行匹配 expected** | 18/60 (30.0%) | _见 tests/log.md_ | _待填_ |
| 综合评分 | 60.67% | _见 tests/log.md_ | _待填_ |

### 经验与后续方向

* 与 v2 同构换底，工程开销极低（download 脚本 + 训练默认超参缩放即可）；
* 220 M 参数解码 ~500 ms-1 s/chunk，60 case ≈ 1-3 分钟，仍可在沙箱内完整端到端跑测；
* 继续提升空间：
  * 多增量训练（每会话 1 epoch），但要监控 val 回退；
  * 适度扩充 `pairs.jsonl` 覆盖 `float`/`UInt64` / `HashMap` 字面量场景；
  * 解码侧 `generate(repetition_penalty=1.2, no_repeat_ngram_size=4)` 抑制重复幻觉；
  * 若仍不足，可考虑 `codet5p-770m` 但放弃 CPU 训练，转向 GPU。
