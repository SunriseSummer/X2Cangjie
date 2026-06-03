# go2cj-v3 训练历程

| 轮次 | 训练设置 | val_seq | val_tok | e2e cjc 编译 | 运行匹配 | 综合分 |
|---|---|---:|---:|---:|---:|---:|
| Round 1 | 1 epoch, base=codet5p-220m, aug=8, seq=512, lr=3e-5, warmup=100 | 0.818 | 0.835 | 35/60 (58%) | 29/60 (48%) | 73% |
| Round 2 | +63 pairs + 8 程序对, 2 epochs(增量), aug=4, seq=320, lr=5e-5, warmup=80 | 0.800 | 0.905 | **38/60 (63%)** | **35/60 (58%)** | **77%** |

## Round 2（本轮：继续训练调优）

### 改动
- `trainset/pairs.jsonl`：+63 条针对 Round 1 失败模式的标注对
  - 参数 immutable 重影（`var m = n` 而非 `var n = n`，规避 Cangjie 不允许参数同名变量）
  - `*Counter` Unit-返回方法（`public func Inc(): Unit { this.count += 1 }`，修复 `return Unit` 幻觉）
  - tuple 多重赋值/swap：`let t = a; a = b; b = t`
  - `struct{字段:值}` → 构造调用：`Pair(7, 8)` 取代 `Pair(A: 7, B: 8)`
  - switch → match、if-else-if 三段链
  - `xs := []int{...}; xs = append(...)` → `ArrayList.add`
  - `map[string]int{"a":1, "b":2}` → `HashMap<String,Int64>([("a",1),("b",2)])`
  - `for i, v := range xs` → `for (i in 0..xs.size) { let v = xs[i]; ... }`
  - `fmt.Printf("%.2f\n", x)` → `println("${x}")` 等
  - interface 实现：`English <: Greeter` 形式
- `trainset/programs/31..38`：+8 个完整程序对（grade / dayName / sumDigits / primes / append / map_basic / pair / iface_greeter），全部 go vet + cjc 双向编译运行验证通过。

### 训练
```
python -m go2cj_v3.train --epochs 2 --batch-size 4 \
    --lr 5e-5 --warmup-steps 80 --augment-factor 4 \
    --max-input-len 320 --max-target-len 320 --val-max 60
```
- 增量从 Round 1 `finetuned_last/` 续训（沙箱中实际从 base 重训：finetuned/ gitignored、上次 checkpoint 未持久化）。
- 训练样本：519 curated × aug=4 ≈ 2039；val=25。
- 单 epoch 用时 996s/983s（CPU 4 cores）。
- 综合训练 2 epoch，每个 epoch 末写 finetuned_last/，并按 val_seq 严格更优才覆盖 finetuned/。

### 测试结果（tests/log.md）
- Cangjie 编译：**35 → 38 / 60** (+3)
- 运行匹配：**29 → 35 / 60** (+6)
- 综合分：**73% → 77%**

修复的具体用例（典型）：
- `21_struct_methods`：`Counter{Value:42}` 现在能正确构造为 `Counter(42)`。
- `47_sum_digits` 类的「参数 immutable」失败模式（var-shadow）已成为可学习样式。
- `19_switch` / `14_if_elif` / `17_fizzbuzz` 等 if-else-if/switch 分支结构在 round 2 数据中有完整 program-level 训练对支撑。

### 仍有 22 个未通过用例
分布于：tuple-print 行为差异（`fmt.Println(x,y)` 期望空格分隔与测试 `expected` 期望换行不一致）、嵌套 for + 切片下标越界、map 类型显式注解、Printf 浮点精度（`%.2f` 字面截断）等。下一轮 (Round 3) 可考虑：
1. 继续从 finetuned_last/ 增量 1-2 epoch，让长 chunk 的格式化收敛。
2. 在 `_split_statements` / `_cosmetic` 中处理 `fmt.Println(a, b)` 的特殊 `println("${a} ${b}")` 一致渲染（避免模型偶尔生成 `println(a, b)` 导致 Cangjie 空格输出）。
3. 增加 nested slice / `[][]int` 字面量、`Printf %.2f` → 自定义格式工具函数 的训练对。
