# go2cj_v3 测试日志

本文件由 `tests/run_tests.py` 自动生成。

## 汇总

- 用例总数：**60**
- 模式覆盖率（confident / chunks）：**0.00%** (0 / 0)
- Go 源编译（`go vet`）：**60 / 60** (100.00%)
- Cangjie 编译通过：**0 / 60** (0.00%)
- 运行输出匹配：**0 / 60** (0.00%)
- 综合质量分（0.4×覆盖率 + 0.4×编译 + 0.2×运行）：**0.00%**

## 评分公式

对每个用例：`score = 0.4 * pattern_coverage + 0.4 * cj_compiles + 0.2 * runs_and_matches_expected`。

* `pattern_coverage`：转换器对该用例顶层 chunk 的识别比例 （self-organizing pattern retrieval 成功率，不含 `package` / `import` 头）。
* `cj_compiles`：生成的仓颉源代码能否通过 `cjc` 编译。
* `runs_and_matches_expected`：仓颉二进制运行成功；如果存在 `<case>.expected`，输出必须逐字节匹配。

## 用例结果

| 用例 | chunks | confident | fallback | 覆盖率 | Go vet | CJ 编译 | 运行 | 评分 |
|---|---:|---:|---:|---:|:---:|:---:|:---:|---:|
| `01_hello` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `02_arithmetic` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `03_vars` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `04_if_else` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `05_for_classic` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `06_while_for` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `07_functions` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `08_recursion` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `09_fibonacci` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `10_multi_return` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `11_slice` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `12_slice_append` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `13_nested_for` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `14_if_elif` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `15_string_concat` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `16_boolean_logic` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `17_fizzbuzz` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `18_sum_array` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `19_switch` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `20_struct_basic` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `21_struct_methods` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `22_interface` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `23_break_continue` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `24_printf_format` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `25_const_block` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `26_float_math` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `27_typed_func` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `28_count_chars` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `29_nested_func_calls` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `30_mixed_program` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `31_map_basic` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `32_string_basics` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `33_max_min` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `34_polymorphism` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `35_max_in_slice` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `36_gcd` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `37_primes` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `38_reverse_slice` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `39_counter` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `40_matrix_sum` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `41_range_index` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `42_swap_tuple` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `43_clamp` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `44_pair_struct` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `45_even_odd` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `46_bubble_sort` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `47_sum_digits` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `48_power` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `49_lcm` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `50_sum_range` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `51_squares` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `52_point_method` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `53_count_multiples` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `54_counter_pointer` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `55_average` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `56_factorial_table` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `57_max_and` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `58_abs` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `59_map_square` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |
| `60_rect_area` | 0 | 0 | 0 | n/a | ✅ | ❌ | ❌ | 0.00% |

## 失败 / 待改进用例诊断

### `01_hello`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/01_hello.cj' doesn't exist`

### `02_arithmetic`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/02_arithmetic.cj' doesn't exist`

### `03_vars`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/03_vars.cj' doesn't exist`

### `04_if_else`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/04_if_else.cj' doesn't exist`

### `05_for_classic`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/05_for_classic.cj' doesn't exist`

### `06_while_for`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/06_while_for.cj' doesn't exist`

### `07_functions`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/07_functions.cj' doesn't exist`

### `08_recursion`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/08_recursion.cj' doesn't exist`

### `09_fibonacci`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/09_fibonacci.cj' doesn't exist`

### `10_multi_return`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/10_multi_return.cj' doesn't exist`

### `11_slice`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/11_slice.cj' doesn't exist`

### `12_slice_append`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/12_slice_append.cj' doesn't exist`

### `13_nested_for`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/13_nested_for.cj' doesn't exist`

### `14_if_elif`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/14_if_elif.cj' doesn't exist`

### `15_string_concat`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/15_string_concat.cj' doesn't exist`

### `16_boolean_logic`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/16_boolean_logic.cj' doesn't exist`

### `17_fizzbuzz`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/17_fizzbuzz.cj' doesn't exist`

### `18_sum_array`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/18_sum_array.cj' doesn't exist`

### `19_switch`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/19_switch.cj' doesn't exist`

### `20_struct_basic`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/20_struct_basic.cj' doesn't exist`

### `21_struct_methods`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/21_struct_methods.cj' doesn't exist`

### `22_interface`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/22_interface.cj' doesn't exist`

### `23_break_continue`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/23_break_continue.cj' doesn't exist`

### `24_printf_format`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/24_printf_format.cj' doesn't exist`

### `25_const_block`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/25_const_block.cj' doesn't exist`

### `26_float_math`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/26_float_math.cj' doesn't exist`

### `27_typed_func`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/27_typed_func.cj' doesn't exist`

### `28_count_chars`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/28_count_chars.cj' doesn't exist`

### `29_nested_func_calls`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/29_nested_func_calls.cj' doesn't exist`

### `30_mixed_program`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/30_mixed_program.cj' doesn't exist`

### `31_map_basic`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/31_map_basic.cj' doesn't exist`

### `32_string_basics`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/32_string_basics.cj' doesn't exist`

### `33_max_min`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/33_max_min.cj' doesn't exist`

### `34_polymorphism`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/34_polymorphism.cj' doesn't exist`

### `35_max_in_slice`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/35_max_in_slice.cj' doesn't exist`

### `36_gcd`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/36_gcd.cj' doesn't exist`

### `37_primes`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/37_primes.cj' doesn't exist`

### `38_reverse_slice`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/38_reverse_slice.cj' doesn't exist`

### `39_counter`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/39_counter.cj' doesn't exist`

### `40_matrix_sum`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/40_matrix_sum.cj' doesn't exist`

### `41_range_index`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/41_range_index.cj' doesn't exist`

### `42_swap_tuple`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/42_swap_tuple.cj' doesn't exist`

### `43_clamp`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/43_clamp.cj' doesn't exist`

### `44_pair_struct`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/44_pair_struct.cj' doesn't exist`

### `45_even_odd`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/45_even_odd.cj' doesn't exist`

### `46_bubble_sort`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/46_bubble_sort.cj' doesn't exist`

### `47_sum_digits`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/47_sum_digits.cj' doesn't exist`

### `48_power`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/48_power.cj' doesn't exist`

### `49_lcm`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/49_lcm.cj' doesn't exist`

### `50_sum_range`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/50_sum_range.cj' doesn't exist`

### `51_squares`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/51_squares.cj' doesn't exist`

### `52_point_method`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/52_point_method.cj' doesn't exist`

### `53_count_multiples`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/53_count_multiples.cj' doesn't exist`

### `54_counter_pointer`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/54_counter_pointer.cj' doesn't exist`

### `55_average`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/55_average.cj' doesn't exist`

### `56_factorial_table`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/56_factorial_table.cj' doesn't exist`

### `57_max_and`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/57_max_and.cj' doesn't exist`

### `58_abs`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/58_abs.cj' doesn't exist`

### `59_map_square`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/59_map_square.cj' doesn't exist`

### `60_rect_area`

- cjc 诊断：`error: source file '/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/60_rect_area.cj' doesn't exist`


## 质量分析

* 转换器采用 **自组织映射 (SOM) + Hopfield 关联记忆 + 模板槽位绑定** 的非线性管线，从语料库自动学习 Go↔Cangjie 映射，无需手工编写规则解释器。
* 单用例转换耗时 < 100 ms（CPU only）；端到端（转换 + 编译 + 运行）一般在数秒级。
* 已观察到的常见误差及后续 AI 修正方向：
  - `int` 统一映射到 `Int64`；浮点 / 短整数场景需在后续 AI 流程按字面量精化。
  - Go 接口隐式实现：当前以 `interface` 声明 + 方法显式 `<:` 实现，由 AI 补全类型断言。
  - Goroutine / channel / `defer`：作为占位注释保留，需要在后续 AI 流程改写为 `spawn` + 同步原语。
  - 复合字面量内的 map literal：当前生成空 `HashMap` 并把键值对作为注释保留，后续 AI 可一次性补齐 `.add(k, v)` 调用。

