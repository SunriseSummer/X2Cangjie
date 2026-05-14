# go2cj_v3 测试日志

本文件由 `tests/run_tests.py` 自动生成。

## 汇总

- 用例总数：**60**
- 模式覆盖率（confident / chunks）：**100.00%** (109 / 109)
- Go 源编译（`go vet`）：**60 / 60** (100.00%)
- Cangjie 编译通过：**43 / 60** (71.67%)
- 运行输出匹配：**33 / 60** (55.00%)
- 综合质量分（0.4×覆盖率 + 0.4×编译 + 0.2×运行）：**79.67%**

## 评分公式

对每个用例：`score = 0.4 * pattern_coverage + 0.4 * cj_compiles + 0.2 * runs_and_matches_expected`。

* `pattern_coverage`：转换器对该用例顶层 chunk 的识别比例 （self-organizing pattern retrieval 成功率，不含 `package` / `import` 头）。
* `cj_compiles`：生成的仓颉源代码能否通过 `cjc` 编译。
* `runs_and_matches_expected`：仓颉二进制运行成功；如果存在 `<case>.expected`，输出必须逐字节匹配。

## 用例结果

| 用例 | chunks | confident | fallback | 覆盖率 | Go vet | CJ 编译 | 运行 | 评分 |
|---|---:|---:|---:|---:|:---:|:---:|:---:|---:|
| `01_hello` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `02_arithmetic` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `03_vars` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `04_if_else` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `05_for_classic` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `06_while_for` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `07_functions` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `08_recursion` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `09_fibonacci` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `10_multi_return` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `11_slice` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `12_slice_append` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `13_nested_for` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `14_if_elif` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `15_string_concat` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `16_boolean_logic` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `17_fizzbuzz` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `18_sum_array` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `19_switch` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `20_struct_basic` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `21_struct_methods` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `22_interface` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `23_break_continue` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `24_printf_format` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `25_const_block` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `26_float_math` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `27_typed_func` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `28_count_chars` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `29_nested_func_calls` | 3 | 3 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `30_mixed_program` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `31_map_basic` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `32_string_basics` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `33_max_min` | 3 | 3 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `34_polymorphism` | 6 | 6 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `35_max_in_slice` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `36_gcd` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `37_primes` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `38_reverse_slice` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `39_counter` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `40_matrix_sum` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `41_range_index` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `42_swap_tuple` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `43_clamp` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `44_pair_struct` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `45_even_odd` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `46_bubble_sort` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `47_sum_digits` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `48_power` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `49_lcm` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `50_sum_range` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `51_squares` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `52_point_method` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `53_count_multiples` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `54_counter_pointer` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `55_average` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `56_factorial_table` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `57_max_and` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `58_abs` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `59_map_square` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `60_rect_area` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |

## 失败 / 待改进用例诊断

### `02_arithmetic`

- cjc 诊断：`error: unclosed delimiter: '('`

### `13_nested_for`

- cjc 诊断：`error: the type Int64 of expression in for-in expression does not implement Iterator`

### `17_fizzbuzz`

- cjc 诊断：`error: expected ';' or '<NL>', found ''`

### `19_switch`

- cjc 诊断：`error: expected expression or declaration, found keyword 'case'`

### `21_struct_methods`

- cjc 诊断：`error: expected type name after ':', found literal '42'`

### `22_interface`

- cjc 诊断：`error: mismatched types`

### `23_break_continue`

- 运行差异：
  ```
  want:
  '1\n3\n'
   got:
  ''
  ```

### `24_printf_format`

- 运行差异：
  ```
  want:
  'name=Cangjie year=2024\n'
   got:
  'name=Cangie year=2024\n'
  ```

### `26_float_math`

- 运行差异：
  ```
  want:
  '12.56\n'
   got:
  ''
  ```

### `30_mixed_program`

- cjc 诊断：`error: expected type name after ':', found literal '4'`

### `34_polymorphism`

- cjc 诊断：`error: expected type name after ':', found ''`

### `37_primes`

- cjc 诊断：`error: expected declaration, found keyword 'return'`

### `39_counter`

- cjc 诊断：`error: expected type name after ':', found literal '0'`

### `40_matrix_sum`

- cjc 诊断：`error: unclosed delimiter: '('`

### `41_range_index`

- cjc 诊断：`error: undeclared identifier 'v'`

### `45_even_odd`

- 运行差异：
  ```
  want:
  '1 odd\n2 even\n3 odd\n4 even\n5 odd\n6 even\n'
   got:
  '1\n2 even\n3\n4 even\n5\n6 even\n'
  ```

### `46_bubble_sort`

- 运行差异：
  ```
  want:
  '1\n2\n3\n4\n5\n'
   got:
  ''
  ```

### `47_sum_digits`

- cjc 诊断：`error: cannot assign to immutable value`

### `48_power`

- cjc 诊断：`error: expected declaration, found keyword 'return'`

### `49_lcm`

- 运行差异：
  ```
  want:
  '12\n35\n'
   got:
  "Command '['/home/runner/work/X2Cangjie/X2Cangjie/go2cj-v3/tests/generated/49_lcm.bin']' timed out after 10 seconds"
  ```

### `50_sum_range`

- 运行差异：
  ```
  want:
  '55\n5050\n'
   got:
  '55\n5049\n'
  ```

### `52_point_method`

- cjc 诊断：`error: 'this' cannot be used outside class or struct or interface`

### `53_count_multiples`

- 运行差异：
  ```
  want:
  '6\n'
   got:
  ''
  ```

### `54_counter_pointer`

- cjc 诊断：`error: 'this' cannot be used outside class or struct or interface`

### `55_average`

- 运行差异：
  ```
  want:
  '150\n30\n'
   got:
  '150\n'
  ```

### `59_map_square`

- 运行差异：
  ```
  want:
  '1\n4\n9\n16\n25\n'
   got:
  ''
  ```

### `60_rect_area`

- cjc 诊断：`error: 'this' cannot be used outside class or struct or interface`


## 质量分析

* 转换器采用 **自组织映射 (SOM) + Hopfield 关联记忆 + 模板槽位绑定** 的非线性管线，从语料库自动学习 Go↔Cangjie 映射，无需手工编写规则解释器。
* 单用例转换耗时 < 100 ms（CPU only）；端到端（转换 + 编译 + 运行）一般在数秒级。
* 已观察到的常见误差及后续 AI 修正方向：
  - `int` 统一映射到 `Int64`；浮点 / 短整数场景需在后续 AI 流程按字面量精化。
  - Go 接口隐式实现：当前以 `interface` 声明 + 方法显式 `<:` 实现，由 AI 补全类型断言。
  - Goroutine / channel / `defer`：作为占位注释保留，需要在后续 AI 流程改写为 `spawn` + 同步原语。
  - 复合字面量内的 map literal：当前生成空 `HashMap` 并把键值对作为注释保留，后续 AI 可一次性补齐 `.add(k, v)` 调用。

