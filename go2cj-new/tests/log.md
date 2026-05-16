# go2cj_new 测试日志

本文件由 `tests/run_tests.py` 自动生成。

## 汇总

- 用例总数：**45**
- 模式覆盖率（confident / chunks）：**97.56%** (160 / 164)
- Go 源编译（`go vet`）：**45 / 45** (100.00%)
- Cangjie 编译通过：**31 / 45** (68.89%)
- 运行输出匹配：**18 / 45** (40.00%)
- 综合质量分（0.4×覆盖率 + 0.4×编译 + 0.2×运行）：**74.37%**

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
| `03_vars` | 8 | 8 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `04_if_else` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `05_for_classic` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `06_while_for` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `07_functions` | 2 | 1 | 1 | 50% | ✅ | ✅ | ✅ | 80.00% |
| `08_recursion` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `09_fibonacci` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `10_multi_return` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `11_slice` | 4 | 4 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `12_slice_append` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `13_nested_for` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `14_if_elif` | 5 | 5 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `15_string_concat` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `16_boolean_logic` | 5 | 5 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `17_fizzbuzz` | 1 | 1 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `18_sum_array` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `19_switch` | 5 | 5 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `20_struct_basic` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `21_struct_methods` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `22_interface` | 5 | 5 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `23_break_continue` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `24_printf_format` | 3 | 3 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `25_const_block` | 2 | 2 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `26_float_math` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `27_typed_func` | 3 | 2 | 1 | 67% | ✅ | ❌ | ❌ | 26.67% |
| `28_count_chars` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `29_nested_func_calls` | 3 | 3 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `30_mixed_program` | 8 | 8 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `31_map_basic` | 4 | 4 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `32_string_basics` | 3 | 3 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `33_max_min` | 4 | 2 | 2 | 50% | ✅ | ✅ | ✅ | 80.00% |
| `34_polymorphism` | 10 | 10 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `35_max_in_slice` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `36_gcd` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `37_primes` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `38_reverse_slice` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `39_counter` | 8 | 8 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `40_matrix_sum` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `41_range_index` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `42_swap_tuple` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `43_clamp` | 4 | 4 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `44_pair_struct` | 5 | 5 | 0 | 100% | ✅ | ✅ | ✅ | 100.00% |
| `45_even_odd` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |

## 失败 / 待改进用例诊断

### `06_while_for`

- 运行差异：
  ```
  want:
  '0\n1\n2\n'
   got:
  ''
  ```

### `11_slice`

- 运行差异：
  ```
  want:
  '1\n2\n3\n'
   got:
  '[1, 2, 3]\n[1, 2, 3]\n[1, 2, 3]\n'
  ```

### `12_slice_append`

- cjc 诊断：`error: no matching function for operator '()' function call`

### `13_nested_for`

- 运行差异：
  ```
  want:
  '0\n1\n2\n10\n11\n12\n20\n21\n22\n'
   got:
  '0\n1\n2\n'
  ```

### `14_if_elif`

- 运行差异：
  ```
  want:
  'A\nB\nC\nF\n'
   got:
  '8550\n90\n90\n90\n'
  ```

### `15_string_concat`

- cjc 诊断：`error: undeclared identifier 'c'`

### `18_sum_array`

- cjc 诊断：`error: mismatched types`

### `19_switch`

- cjc 诊断：`error: expected declaration, found keyword 'match'`

### `21_struct_methods`

- cjc 诊断：`error: 'this' cannot be used outside class or struct or interface`

### `22_interface`

- cjc 诊断：`error: expected declaration, found 'English'`

### `23_break_continue`

- 运行差异：
  ```
  want:
  '1\n3\n'
   got:
  '0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n'
  ```

### `24_printf_format`

- 运行差异：
  ```
  want:
  'name=Cangjie year=2024\n'
   got:
  'name=%s year=%d\n\n'
  ```

### `26_float_math`

- cjc 诊断：`error: undeclared identifier 'area'`

### `27_typed_func`

- cjc 诊断：`error: undeclared identifier 'Process'`

### `28_count_chars`

- 运行差异：
  ```
  want:
  '12\n'
   got:
  'hello, world\n'
  ```

### `29_nested_func_calls`

- 运行差异：
  ```
  want:
  '12\n'
   got:
  '25\n'
  ```

### `30_mixed_program`

- 运行差异：
  ```
  want:
  '20\n6\n'
   got:
  '9\n6\n'
  ```

### `31_map_basic`

- 运行差异：
  ```
  want:
  '1\n2\n3\n'
   got:
  '[(a, 1), (b, 2)]\n[(a, 1), (b, 2)]\n[(a, 1), (b, 2)]\n'
  ```

### `32_string_basics`

- 运行差异：
  ```
  want:
  '5\nhello world\n'
   got:
  'hello\nhello\n'
  ```

### `34_polymorphism`

- cjc 诊断：`error: no matching function for operator '()' function call`

### `36_gcd`

- cjc 诊断：`error: unable to infer generic argument of this function`

### `37_primes`

- cjc 诊断：`error: expected ';' or '<NL>', found keyword 'var'`

### `38_reverse_slice`

- cjc 诊断：`error: expected ';' or '<NL>', found keyword 'var'`

### `39_counter`

- cjc 诊断：`error: 'this' cannot be used outside class or struct or interface`

### `40_matrix_sum`

- cjc 诊断：`error: expected ';' or '<NL>', found keyword 'for'`

### `41_range_index`

- 运行差异：
  ```
  want:
  '0 1\n1 2\n2 3\n3 4\n4 5\n'
   got:
  '1\n2\n3\n4\n5\n'
  ```

### `45_even_odd`

- 运行差异：
  ```
  want:
  '1 odd\n2 even\n3 odd\n4 even\n5 odd\n6 even\n'
   got:
  'false\ntrue\nfalse\ntrue\nfalse\ntrue\n'
  ```


## 质量分析

* 转换器采用 **自组织映射 (SOM) + Hopfield 关联记忆 + 模板槽位绑定** 的非线性管线，从语料库自动学习 Go↔Cangjie 映射，无需手工编写规则解释器。
* 单用例转换耗时 < 100 ms（CPU only）；端到端（转换 + 编译 + 运行）一般在数秒级。
* 已观察到的常见误差及后续 AI 修正方向：
  - `int` 统一映射到 `Int64`；浮点 / 短整数场景需在后续 AI 流程按字面量精化。
  - Go 接口隐式实现：当前以 `interface` 声明 + 方法显式 `<:` 实现，由 AI 补全类型断言。
  - Goroutine / channel / `defer`：作为占位注释保留，需要在后续 AI 流程改写为 `spawn` + 同步原语。
  - 复合字面量内的 map literal：当前生成空 `HashMap` 并把键值对作为注释保留，后续 AI 可一次性补齐 `.add(k, v)` 调用。

