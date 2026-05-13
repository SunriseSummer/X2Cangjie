# go2cj 测试日志

本文件由 `tests/run_tests.py` 自动生成。

## 汇总

- 用例总数：**40**
- 模式覆盖率（confident / chunks）：**100.00%** (72 / 72)
- Go 源编译（`go vet`）：**40 / 40** (100.00%)
- Cangjie 编译通过：**5 / 40** (12.50%)
- 运行输出匹配：**0 / 40** (0.00%)
- 综合质量分（0.4×覆盖率 + 0.4×编译 + 0.2×运行）：**45.00%**

## 评分公式

对每个用例：`score = 0.4 * pattern_coverage + 0.4 * cj_compiles + 0.2 * runs_and_matches_expected`。

* `pattern_coverage`：转换器对该用例顶层 chunk 的识别比例 （self-organizing pattern retrieval 成功率，不含 `package` / `import` 头）。
* `cj_compiles`：生成的仓颉源代码能否通过 `cjc` 编译。
* `runs_and_matches_expected`：仓颉二进制运行成功；如果存在 `<case>.expected`，输出必须逐字节匹配。

## 用例结果

| 用例 | chunks | confident | fallback | 覆盖率 | Go vet | CJ 编译 | 运行 | 评分 |
|---|---:|---:|---:|---:|:---:|:---:|:---:|---:|
| `01_hello` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `02_arithmetic` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `03_vars` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `04_if_else` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `05_for_classic` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `06_while_for` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `07_functions` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `08_recursion` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `09_fibonacci` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `10_multi_return` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `11_slice` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `12_slice_append` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `13_nested_for` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `14_if_elif` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `15_string_concat` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `16_boolean_logic` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `17_fizzbuzz` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `18_sum_array` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `19_switch` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `20_struct_basic` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `21_struct_methods` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `22_interface` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `23_break_continue` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `24_printf_format` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `25_const_block` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `26_float_math` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `27_typed_func` | 2 | 2 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `28_count_chars` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `29_nested_func_calls` | 3 | 3 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `30_mixed_program` | 3 | 3 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `31_map_basic` | 1 | 1 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `32_string_basics` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `33_max_min` | 3 | 3 | 0 | 100% | ✅ | ✅ | ❌ | 80.00% |
| `34_polymorphism` | 6 | 6 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `35_max_in_slice` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `36_gcd` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `37_primes` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `38_reverse_slice` | 2 | 2 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `39_counter` | 4 | 4 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |
| `40_matrix_sum` | 1 | 1 | 0 | 100% | ✅ | ❌ | ❌ | 40.00% |

## 失败 / 待改进用例诊断

### `01_hello`

- cjc 诊断：`error: undeclared identifier 'NUM1'`

### `02_arithmetic`

- cjc 诊断：`error: undeclared identifier 'a'`

### `03_vars`

- cjc 诊断：`error: unclosed delimiter: '('`

### `04_if_else`

- cjc 诊断：`error: expected declaration, found 'println'`

### `05_for_classic`

- cjc 诊断：`error: expected '{', found '}'`

### `06_while_for`

- cjc 诊断：`error: expected '{', found '}'`

### `07_functions`

- 运行差异：
  ```
  want:
  '5\n'
   got:
  '2\n'
  ```

### `08_recursion`

- cjc 诊断：`error: unmatched delimiter: ')'`

### `09_fibonacci`

- cjc 诊断：`error: unmatched delimiter: ')'`

### `10_multi_return`

- cjc 诊断：`error: unclosed delimiter: '('`

### `11_slice`

- cjc 诊断：`error: undeclared identifier 'xs'`

### `12_slice_append`

- cjc 诊断：`error: undeclared identifier 'v'`

### `13_nested_for`

- cjc 诊断：`error: unclosed delimiter: '('`

### `14_if_elif`

- cjc 诊断：`error: expected declaration, found keyword 'return'`

### `15_string_concat`

- cjc 诊断：`error: cannot have assignment expression in initializer`

### `16_boolean_logic`

- cjc 诊断：`error: expected expression after '!', found ')'`

### `17_fizzbuzz`

- cjc 诊断：`error: expected ';' or '<NL>', found keyword 'else'`

### `18_sum_array`

- cjc 诊断：`error: undeclared identifier 'v'`

### `19_switch`

- cjc 诊断：`error: expected expression or declaration, found keyword 'case'`

### `20_struct_basic`

- cjc 诊断：`error: assignment operators cannot be chained`

### `21_struct_methods`

- cjc 诊断：`error: expected a func name after keyword 'func', found '('`

### `22_interface`

- cjc 诊断：`error: unclosed delimiter: '('`

### `23_break_continue`

- cjc 诊断：`error: expected '{', found '}'`

### `24_printf_format`

- cjc 诊断：`error: cannot have assignment expression in initializer`

### `25_const_block`

- cjc 诊断：`error: undeclared identifier 'B'`

### `26_float_math`

- cjc 诊断：`error: cannot have assignment expression in initializer`

### `27_typed_func`

- 运行差异：
  ```
  want:
  '7\n10\n'
   got:
  '10\n10\n10\n'
  ```

### `28_count_chars`

- cjc 诊断：`error: undeclared identifier 'NUM1'`

### `29_nested_func_calls`

- 运行差异：
  ```
  want:
  '12\n'
   got:
  '5\n'
  ```

### `30_mixed_program`

- cjc 诊断：`error: assignment operators cannot be chained`

### `31_map_basic`

- 运行差异：
  ```
  want:
  '1\n2\n3\n'
   got:
  'b\n'
  ```

### `32_string_basics`

- cjc 诊断：`error: unmatched delimiter: ')'`

### `33_max_min`

- 运行差异：
  ```
  want:
  '7\n3\n'
   got:
  '3\n7\n'
  ```

### `34_polymorphism`

- cjc 诊断：`error: assignment operators cannot be chained`

### `35_max_in_slice`

- cjc 诊断：`error: unclosed delimiter: '('`

### `36_gcd`

- cjc 诊断：`error: expected declaration, found keyword 'return'`

### `37_primes`

- cjc 诊断：`error: unclosed delimiter: '('`

### `38_reverse_slice`

- cjc 诊断：`error: unclosed delimiter: '('`

### `39_counter`

- cjc 诊断：`error: expected a func name after keyword 'func', found '('`

### `40_matrix_sum`

- cjc 诊断：`error: expected 'in' in for-in expression, found '}'`


## 质量分析

* 转换器采用 **自组织映射 (SOM) + Hopfield 关联记忆 + 模板槽位绑定** 的非线性管线，从语料库自动学习 Go↔Cangjie 映射，无需手工编写规则解释器。
* 单用例转换耗时 < 100 ms（CPU only）；端到端（转换 + 编译 + 运行）一般在数秒级。
* 已观察到的常见误差及后续 AI 修正方向：
  - `int` 统一映射到 `Int64`；浮点 / 短整数场景需在后续 AI 流程按字面量精化。
  - Go 接口隐式实现：当前以 `interface` 声明 + 方法显式 `<:` 实现，由 AI 补全类型断言。
  - Goroutine / channel / `defer`：作为占位注释保留，需要在后续 AI 流程改写为 `spawn` + 同步原语。
  - 复合字面量内的 map literal：当前生成空 `HashMap` 并把键值对作为注释保留，后续 AI 可一次性补齐 `.add(k, v)` 调用。

