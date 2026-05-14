# go2cj-v2 训练历程与试错经验

本文件按时间顺序记录 go2cj-v2 的关键决策与效果，供后续训练 / 调参参考。

---

## v2.0 — CodeT5-small 底座 + 二次微调（**当前主线**）

### 动机
go2cj v1（从零训 0.6 M 参数 Transformer + anonymization）chunk 级 `val_seq_acc ≈ 0.74` 但端到端 `cjc` 编译率长期停留在 2/45 (4.4%)、运行匹配 1/45 (2.2%)。诊断结论：
- 参数太少，无法泛化到长 chunk（func main 整块作为单 chunk 严重 OOD）；
- 零先验，模型连 Go 与 Cangjie 的基础语法都得从训练数据里学；
- 手工 curated 300 条对 × 60× 增广只够覆盖匿名化模板。

### 选型
调研了 codet5-small / codet5p-220m / plbart-base / t5-small，最终选 **Salesforce/codet5-small**：60.5 M 参数、T5 enc-dec、预训练含 Go 等 6 种代码语言、CPU 单 epoch 可控（~7.5 min）。

底座通过 `scripts/download_base.sh` 从 `https://github.com/SunriseSummer/CangjieSDK/releases/download/1.0.5/codet5-small.zip` 获取（HuggingFace 在沙箱不可达，故走 GitHub Release 镜像）。

### 关键调整 vs v1
- **舍弃 anonymization 层**：CodeT5 自带 byte-level BPE，标识符 / 字面量天然多 token 拷贝，不需要匿名化也能泛化；
- **数据增广改为标识符随机重命名**：每个 curated pair 用 `_POOL` 里的 100+ 候选名替换其用户标识符，factor=10 即可（vs v1 factor=60）；
- **chunk 渲染回自然 Go 源码**：不再"空格分隔 token 流"，而是按 `_NO_SPACE_BEFORE / _AFTER` 还原自然空白，让 BPE 输入接近预训练分布；
- **T5 标准任务前缀** `"translate Go to Cangjie: "`，inference 与 train 端一致；
- **best-checkpoint 协议**沿用 v1：`finetuned/` ← 严格最优、`finetuned_last/` ← 最新可续训。

### 首轮训练（3 epochs，CPU，lr=5e-5, batch=4, factor=10）

| epoch | avg loss | val_seq_acc | val_tok_acc | 耗时 |
|---|---|---|---|---|
| 1 | 0.44 | **0.867** | 0.860 | 7.6 min |
| 2 | 0.14 | 0.867 | 0.896 | 7.8 min |
| 3 | **0.028** | **1.000** | **1.000** | 7.5 min |

仅 1 个 epoch 就把 val_seq 从零拉到 0.867，验证了"预训练先验"假设。3 个 epoch 后在 15 条 holdout 上达到 100%。

### 首轮端到端测试

| 指标 | go2cj v1 | go2cj-v2 (3 ep) | 提升 |
|---|---|---|---|
| 模式覆盖率 | 100% | 100% | — |
| Go vet 通过 | 45/45 | 45/45 | — |
| **cjc 编译通过** | 2/45 (4.4%) | **16/45 (35.6%)** | **+8×** |
| **运行匹配 expected** | 1/45 (2.2%) | **14/45 (31.1%)** | **+14×** |
| 综合评分 | 42% | 60% | +18 pts |

### 已发现的失败模式 & 后续方向
1. **模型在长 chunk 上偶有重复 / 死循环式输出**（如 `ArrayList<Int64>([1,2,3])` 重复 7 次）。可通过 `repetition_penalty` 解码参数缓解，或继续增训。
2. **微小语义错位**：`var y: 10`（应为 `var y = 10`）、`p.Z`（应为 `p.Y`）等。属于训练样本覆盖度问题，加更多 `programs/*` 对针对结构体字段命名应有改善。
3. **多语句缺换行**：模型按训练样式（chunk 内空格分隔）输出，cjc 在 `} return ...` 等位置要求换行 / `;`。已在 `converter._cosmetic` 加 `_split_statements` + `_indent_block` 后处理。
4. **第 4 个 epoch 出现轻微回退**（val_seq 1.0 → 0.933）：典型小数据集过拟合 / 优化噪声。best-checkpoint 协议保证 `finetuned/` 仍是 epoch 3 权重，不污染线上。

### 经验
- 同一份训练数据下，仅通过"换底座 + 二次微调"，端到端 cjc 编译率从 4.4% → 35.6%（+8×），运行匹配率从 2.2% → 31.1%（+14×）。验证了用户原始判断："神经网络方案选型有问题，应该基于一个类似领域的预训练小模型做二次训练"。
- CodeT5-small 已经知道 Go 的语法 / `:=` / `for i := 0; i < n; i++` / `fmt.Println` 等，只需用监督对引导它输出 Cangjie 即可。
- 后续提升空间：
  - 多增量训练（每会话 1-3 epochs），但要监控 val 回退；
  - 适当扩充 `pairs.jsonl`（覆盖更多 struct field / interface / map literal 情况）；
  - 调 `generate(repetition_penalty=1.2, no_repeat_ngram_size=4)` 抑制重复幻觉；
  - 若仍不足，可升级到 codet5p-220m。
