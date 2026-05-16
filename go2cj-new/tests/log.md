# go2cj_new 测试日志

本文件由 `tests/run_tests.py` 自动生成。

## 汇总

- 用例总数：**50**
- 模式覆盖率（confident / chunks）：**88.32%** (325 / 368)
- Go 源编译（`go vet`）：**50 / 50** (100.00%)
- Cangjie 编译通过：**44 / 50** (88.00%)
- 运行输出匹配：**40 / 50** (80.00%)
- 综合质量分（0.4×覆盖率 + 0.4×编译 + 0.2×运行）：**88.30%**

## 评分公式

对每个用例：`score = 0.4 * pattern_coverage + 0.4 * cj_compiles + 0.2 * runs_and_matches_expected`。

* `pattern_coverage`：转换器对该用例顶层 chunk 的识别比例 （self-organizing pattern retrieval 成功率，不含 `package` / `import` 头）。
* `cj_compiles`：生成的仓颉源代码能否通过 `cjc` 编译。
* `runs_and_matches_expected`：仓颉二进制运行成功；如果存在 `<case>.expected`，输出必须逐字节匹配。

## 用例结果

| 用例 | chunks | confident | fallback | 覆盖率 | Go vet | CJ 编译 | 运行 | 评分 |
|---|---:|---:|---:|---:|:---:|:---:|:---:|---:|
| `01_hello` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `02_arithmetic` | 7 | 7 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `03_vars` | 8 | 8 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `04_if_else` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `05_for_classic` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `06_while_for` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `07_functions` | 4 | 3 | 1 | 75% | ✅ | ✅ | ✅ | 90.00% |
| `08_recursion` | 7 | 6 | 1 | 86% | ✅ | ✅ | ✅ | 94.29% |
| `09_fibonacci` | 7 | 6 | 1 | 86% | ✅ | ✅ | ✅ | 94.29% |
| `10_multi_return` | 6 | 5 | 1 | 83% | ✅ | ✅ | ✅ | 93.33% |
| `11_slice` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `12_slice_append` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `13_nested_for` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `14_if_elif` | 7 | 6 | 1 | 86% | ✅ | ✅ | ✅ | 94.29% |
| `15_string_concat` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `16_boolean_logic` | 5 | 5 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `17_fizzbuzz` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `18_sum_array` | 9 | 7 | 2 | 78% | ✅ | ❌ | ❌ | 31.11% |
| `19_switch` | 12 | 11 | 1 | 92% | ✅ | ✅ | ✅ | 96.67% |
| `20_struct_basic` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `21_struct_methods` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `22_interface` | 5 | 5 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `23_break_continue` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `24_printf_format` | 3 | 3 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `25_const_block` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `26_float_math` | 4 | 4 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `27_typed_func` | 8 | 7 | 1 | 88% | ✅ | ✅ | ✅ | 95.00% |
| `28_count_chars` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `29_nested_func_calls` | 7 | 5 | 2 | 71% | ✅ | ✅ | ✅ | 88.57% |
| `30_mixed_program` | 8 | 8 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `31_map_basic` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `32_string_basics` | 3 | 3 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `33_max_min` | 14 | 12 | 2 | 86% | ✅ | ✅ | ✅ | 94.29% |
| `34_polymorphism` | 10 | 10 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `35_max_in_slice` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `36_gcd` | 8 | 6 | 2 | 75% | ✅ | ✅ | ✅ | 90.00% |
| `37_primes` | 12 | 10 | 2 | 83% | ✅ | ✅ | ❌ | 73.33% |
| `38_reverse_slice` | 11 | 10 | 1 | 91% | ✅ | ✅ | ❌ | 76.36% |
| `39_counter` | 8 | 8 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `40_matrix_sum` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `41_range_index` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `42_swap_tuple` | 6 | 5 | 1 | 83% | ✅ | ✅ | ✅ | 93.33% |
| `43_clamp` | 12 | 11 | 1 | 92% | ✅ | ✅ | ✅ | 96.67% |
| `44_pair_struct` | 5 | 5 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `45_even_odd` | 4 | 3 | 1 | 75% | ✅ | ✅ | ✅ | 90.00% |
| `46_knapsack` | 21 | 17 | 4 | 81% | ✅ | ❌ | ❌ | 32.38% |
| `47_binary_search` | 15 | 13 | 2 | 87% | ✅ | ✅ | ❌ | 74.67% |
| `48_lcs` | 15 | 13 | 2 | 87% | ✅ | ❌ | ❌ | 34.67% |
| `49_quicksort` | 17 | 12 | 5 | 71% | ✅ | ❌ | ❌ | 28.24% |
| `50_knapsack_full` | 54 | 45 | 9 | 83% | ✅ | ❌ | ❌ | 33.33% |

## 失败 / 待改进用例诊断

### `03_vars`

- cjc 诊断：`error: cannot convert an integer literal to type 'Float64'`

### `18_sum_array`

- cjc 诊断：`error: expected '(', found '_'`

### `26_float_math`

- 运行差异：
  ```
  want:
  '12.56\n'
   got:
  '12.560000\n'
  ```

### `37_primes`

- 运行差异：
  ```
  want:
  '2\n3\n5\n7\n11\n13\n17\n19\n'
   got:
  ''
  ```

### `38_reverse_slice`

- 运行差异：
  ```
  want:
  '5\n4\n3\n2\n1\n'
   got:
  '0\n0\n0\n0\n0\n5\n4\n3\n2\n1\n'
  ```

### `46_knapsack`

- cjc 诊断：`error: expected ';' or '<NL>', found 'dp'`

### `47_binary_search`


### `48_lcs`

- cjc 诊断：`error: invalid subscript operator [] on type 'Int64' with index type 'Int64'`

### `49_quicksort`

- cjc 诊断：`error: expected ';' or '<NL>', found ','`

### `50_knapsack_full`

- cjc 诊断：`error: expected ';' or '<NL>', found 'dp'`


## 质量分析

* 转换器采用 **自组织映射 (SOM) + Hopfield 关联记忆 + 模板槽位绑定** 的非线性管线，从语料库自动学习 Go↔Cangjie 映射，无需手工编写规则解释器。
* 单用例转换耗时 < 100 ms（CPU only）；端到端（转换 + 编译 + 运行）一般在数秒级。
* 已观察到的常见误差及后续 AI 修正方向：
  - `int` 统一映射到 `Int64`；浮点 / 短整数场景需在后续 AI 流程按字面量精化。
  - Go 接口隐式实现：当前以 `interface` 声明 + 方法显式 `<:` 实现，由 AI 补全类型断言。
  - Goroutine / channel / `defer`：作为占位注释保留，需要在后续 AI 流程改写为 `spawn` + 同步原语。
  - 复合字面量内的 map literal：当前生成空 `HashMap` 并把键值对作为注释保留，后续 AI 可一次性补齐 `.add(k, v)` 调用。

