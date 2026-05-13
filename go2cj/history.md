# go2cj 神经网络转换器 — 探索历程与经验

本文件按时间顺序记录 go2cj 转换器的关键决策、尝试过的方案、效果与经验教训，供后续开发者参考，避免重复试错。**只保留效果最好的版本**到主线代码 / 权重；本文档保存被替换 / 被否决方案的简要总结。

---

## v0.1 — 规则脚本（已淘汰）

* 实现：`embedding.py` + `hopfield.py` + `som.py` + `patterns.py` + `converter.py (~2100 行)`，基于 SOM 聚类 + Hopfield 联想 + 手写模板槽位绑定。
* 测试：30 个用例 100% 模式匹配，但代码可读性差，添加新模式需要修改五处文件。
* **结论**：表达能力受模板枚举限制；与用户"基于训练得到的模型做翻译"目标不符，整体替换为神经网络管线（v0.2）。

---

## v0.2 — 首个 Transformer seq2seq（已被 v0.3 取代）

* 架构：`nn.Transformer`，`d_model=128, 3 enc / 3 dec, nhead=4`，~1.75 M params。
* 训练：12 000 条合成语料，10 epochs，全词级 tokenizer，**未启用匿名化**。
* 结果：`val_tok_acc=0.676, val_seq_acc=0.264`；30 个测试用例端到端可跑但 cjc 编译率 ≈ 0。
* 关键问题：
  1. 词表必须记忆用户标识符 / 字面量，长尾严重，OOV 频繁；
  2. 模型一次性"全量训练"，每次实验都从零跑十几分钟。
* **结论**：保留 Transformer 骨架，但引入匿名化 + 增量训练（v0.3）。

---

## v0.3 — 匿名化 + 增量可恢复训练（**当前主线**）

* **匿名化**：识别符 / NUM / STR / CHR 替换为 `ID0/NUM0/STR0/CHR0`，模型只学规范模板，运行时反替换。OOV 实际占比 < 1%。
* **架构调优**：缩小为 `d_model=96, 2 enc / 2 dec, nhead=6`（~0.6 M params）。匿名化后真实学习目标变小，过大的网络反而过拟合且更慢；6 头 96 维做 token-空间复合编码足够。
* **增量训练**：
  - 默认 `python -m go2cj.neural.train` 每次从 `model.pt` 继续 1 个 epoch；
  - 每 epoch 原子写盘 `model.pt` (含 optimizer state) + `vocab.json` + `model_meta.json`；
  - 词表首轮构建后冻结（新 token 走 `<unk>`）。
* **数据来源**：249 条 curated `trainset/pairs.jsonl` + 5 个 `programs/*` 完整程序对，按 60–80× 占位符 index 置换增广 ≈ 20 k 条；外加 4 000 条 `corpus.py` 合成对。
* **首版 checkpoint**：8 epochs，`val_tok_acc=0.856, val_seq_acc=0.557`。

---

## v0.4 — 训练数据可执行验证 + 更多 program pairs + best-checkpoint 保留

* 用户要求："go 和 cangjie 代码都要编译运行验证，且各自都是最优编码实现"。
* 新工具：`trainset/verify_programs.py` 调用 `go run` 与 `cjc + 二进制`，要求两侧 stdout 完全一致；CI / 训练前必跑。
* 修复发现：
  1. 早期 `programs/*.cj` 用 `main(): Unit { ... return 0 }` 编译失败 → 改为 `main() { ... return 0 }`（仓颉 `main` 返回 Int64）。
  2. `Point(X: 3, Y: 4)` named-arg 构造不被 cjc 接受（参数未声明为 `!`）→ 改为位置参数 `Point(3, 4)`，同步更新 `pairs.jsonl`。
  3. `Float64.toString` 输出 `9.000000` 不同于 Go 的 `9`；在比对场景用 `Int64(f)` 强转后再打印。
* 新增 program pairs（每对都 `go run` & `cjc` 双向编译运行通过、stdout 完全一致）：factorial / fib_iter / fizzbuzz / reverse / counter / gcd / primes / stats / polymorphism / matrix。
* 新增 verify 工具：`tests/verify_go_cases.py` — 对 `tests/cases/*.go` 做 `go run` 并比对 `.expected`；发现并修复 `26_float_math.expected`（Go 的 `Println(12.56)` 输出 `12.56\n`，原 expected 是错的 `12.560000\n`）。
* **best-checkpoint 协议**：`model.pt` ← 最优，`model_last.pt` ← 最新可续训（gitignored）。每 epoch 末若 `val_seq_acc` 严格更优才覆盖 `model.pt`，否则保留历史最佳。`model_meta.json` 同时记 `epoch`/`best_epoch`/`best_val_*`。

---

## v0.5 — 增量训练继续推进

每次会话续训 2-4 个 epoch，单次沙箱时间 ≤ 30 min，best-checkpoint 保证劣化版本不污染线上。

| Session | epochs | LR | val_tok_acc | val_seq_acc | 备注 |
|---|---|---|---|---|---|
| v0.3 baseline | 1–8 | 3e-4 OneCycle | 0.856 | 0.557 | restart, anonymize 启用 |
| v0.4 round 1 | 9–11 | 2e-4 | 0.852 | 0.587 | +10 program pairs 后续训 |
| v0.5 round 1 | 12 | 1e-4 | 0.872 | 0.558 | **回退**，model.pt 保持 ep11 |
| v0.5 round 1 | 13–15 | 1e-4 | 0.904 | 0.647 | PROMOTED, ep15 |
| v0.5 round 2 | 16 | 8e-5 | 0.897 | 0.637 | **回退**，model.pt 保持 ep15 |
| v0.5 round 2 | 17 | 8e-5 | 0.910 | 0.676 | PROMOTED |
| **v0.5 round 2** | **18** | 8e-5 | **0.913** | **0.684** | **当前最佳，已发布** |

**经验**：
- 每次新会话第一个 epoch 经常回退（OneCycleLR 重新 warm-up 扰乱权重）→ best-checkpoint 协议是必须的。
- `lr=8e-5 ~ 1e-4` 是 v0.3 数据规模下 ep10+ 的甜区；继续降到 5e-5 以下进步会停滞。
- 短 anonymized chunk 上 seq_acc 已接近 0.85；长多语句 chunk 仍是主要扣分项 (`curated_factor=80` 增广只能 partial 覆盖)，下一步应在 `programs/` 加更多 5+ chunk 的程序对。

---

## 训练 / 推理优化经验

1. **匿名化 > 扩词表 / 复制机制**。Code 翻译的"标识符长尾"是真正的难题；匿名化让模型只看 < 500 token 的固定词表，参数量可以小一个数量级。
2. **小模型 + 多 epoch 增量** > 大模型一次性。0.6 M 参数在 CPU 上每 epoch ~2 min，错了可以快速重训；当 `val_tok_acc` 增长 ≤ 0.01 / epoch 时再考虑加层 / 加维度。
3. **OneCycleLR 在 resume 时 warm-restart**：每次新会话重建调度器，按当次 epochs 设置 `total_steps`，相当于多个 mini-restart，对小数据集表现良好（避免学习率永久收敛到 0）。
4. **Label smoothing 0.1** 对短序列有效，能避免模型过度自信地输出错误 token。
5. **Float-aware tokenizer**：`3.14` 不能被切成 `3 . 14`，否则匿名化和反替换会丢精度。
6. **Curated × 占位符增广 ≫ 纯合成**：249 条精选 chunk 对 60-80× 增广后，比 12 k 条合成对在测试集 cjc 编译率上更优 — 人工保证 idiomatic 仓颉。
7. **验证脚本是数据集的一部分**：`verify_programs.py` 与 `verify_go_cases.py` 让每次添加新对都自动 lint，杜绝训练在错误数据上。

---

## 仍待探索 / 下一步

* **Beam search** 替代贪心解码：长 chunk 上预计 +5-10% seq acc。
* **Sub-word tokenizer**（BPE）：对未匿名化的标识符更鲁棒；但需要重训词表，资源开销大。
* **Copy mechanism** (pointer-generator)：把 anonymize 做到模型内而非数据层，可省去预/后处理。
* **更大 curated 集**：当前 249 条覆盖基础语法 + 常见库；下一波重点放在错误处理（`error` / `Result<T,E>` / try-catch）、闭包、泛型、channel / 协程。
* **CI 集成**：在沙箱外的 CI 上跑 `tests/run_tests.py` + 上传 log.md。
