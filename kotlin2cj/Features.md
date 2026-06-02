# kotlin2cj 语言特性支持清单

> 完整列出 kotlin2cj 翻译器对 Kotlin 语言特性的支持情况。
> ✅ 已支持 · ⚠️ 部分支持 · ❌ 未支持
>
> **翻译器版本**：187+33 用例基线（187/187 单文件 + 33/33 项目级全通过）
> **更新日期**：2026-06-02

---

## 目录

1. [基础类型与字面量](#1-基础类型与字面量)
2. [变量与类型推断](#2-变量与类型推断)
3. [运算符](#3-运算符)
4. [控制流](#4-控制流)
5. [函数](#5-函数)
6. [类与对象](#6-类与对象)
7. [继承与接口](#7-继承与接口)
8. [泛型](#8-泛型)
9. [枚举](#9-枚举)
10. [空安全](#10-空安全)
11. [集合与集合操作](#11-集合与集合操作)
12. [字符串](#12-字符串)
13. [异常处理](#13-异常处理)
14. [类型检查与转换](#14-类型检查与转换)
15. [解构声明](#15-解构声明)
16. [区间与步进](#16-区间与步进)
17. [作用域函数](#17-作用域函数)
18. [协程与异步](#18-协程与异步)
19. [委托](#19-委托)
20. [注解与反射](#20-注解与反射)
21. [其他高级特性](#21-其他高级特性)
22. [类型映射表](#22-类型映射表)
23. [未支持特性优先级排序](#23-未支持特性优先级排序)

---

## 1. 基础类型与字面量

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 整数 Int | ✅ | `Int` | `Int64` | 统一为 64 位整数 |
| 长整数 Long | ✅ | `Long` | `Int64` | 与 Int 统一 |
| Short / Byte | ✅ | `Short` / `Byte` | `Int64` | 无专用短/字节类型 |
| 浮点 Float | ✅ | `Float` | `Float64` | 统一为 64 位浮点 |
| 双精度 Double | ✅ | `Double` | `Float64` | 与 Float 统一 |
| 布尔 Boolean | ✅ | `Boolean` | `Bool` | |
| 字符 Char | ✅ | `Char` | `Rune` | Unicode 字符 |
| 字符串 String | ✅ | `String` | `String` | 直接映射 |
| Unit（无返回值） | ✅ | `Unit` | `Unit` | |
| Any（顶级类型） | ✅ | `Any` | `Object` | |
| 十进制字面量 | ✅ | `123` | `123` | |
| 十六进制字面量 | ✅ | `0x1F` | `0x1F` | |
| 二进制字面量 | ✅ | `0b1010` | `0b1010` | |
| 下划线分隔符 | ✅ | `1_000_000` | `1_000_000` | |
| Long 后缀 | ✅ | `1L` | 自动为 `Int64` | |
| Float 后缀 | ✅ | `1.5f` | 自动为 `Float64` | |
| 科学计数法 | ✅ | `1e10` | `1e10` | |

---

## 2. 变量与类型推断

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 不可变变量 | ✅ | `val x = 1` | `let x = 1` | |
| 可变变量 | ✅ | `var x = 1` | `var x = 1` | |
| 显式类型注解 | ✅ | `val x: Int = 1` | `let x: Int64 = 1` | 类型自动映射 |
| 类型推断 | ✅ | `val x = listOf(1)` | `let x = ArrayList(...)` | |
| 全局顶层 val | ✅ | `val PI = 3.14` | 顶层 `let` | |
| `lateinit var` | ❌ | `lateinit var x: T` | — | 无对应机制 |
| `const val` | ⚠️ | `const val X = 1` | `let X = 1` | `const` 关键字被跳过 |
| `by lazy { }` | ✅ | `val x by lazy { ... }` | `let x = ({ => ... })()` | 编译期即时求值（IIFE 模式） |

---

## 3. 运算符

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 算术 `+ - * / %` | ✅ | | | |
| 自增自减 `++ --` | ✅ | | | |
| 复合赋值 `+= -= *= /= %=` | ✅ | | | |
| 比较 `== != < <= > >=` | ✅ | | | |
| 逻辑 `&& \|\| !` | ✅ | | | |
| 位运算 `and or xor` | ✅ | `a and b` | `a & b` | 中缀转运算符 |
| 移位 `shl shr ushr` | ✅ | `a shl 2` | `a << 2` | |
| 字符串拼接 `+` | ✅ | `"a" + 1` | 非字符串侧自动 `.toString()` | |
| 混合数值运算 | ✅ | `5 + 2.5` | 自动 `Float64(...)` 提升 | Int + Float 场景 |
| 操作符重载 `operator` | ❌ | `operator fun plus(...)` | — | 关键字识别但不特殊处理 |
| 中缀函数 `infix` | ❌ | `infix fun Int.times(x: Int)` | — | 关键字识别但不特殊处理 |

---

## 4. 控制流

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| `if / else` | ✅ | | | |
| `if` 作为表达式 | ✅ | `val x = if (c) a else b` | | |
| `when` 语句 | ✅ | `when (x) { 1 -> ... }` | `match (x) { case 1 => ... }` | |
| `when` 无主语 | ✅ | `when { c1 -> ... }` | `if-else` 链 | |
| `when` + `in` 区间 | ✅ | `in 90..100 ->` | if-else 链（仓颉 match 不支持区间） | |
| `when` + `is` 类型 | ✅ | `is Type ->` | `case v: Type =>` | |
| `when` + 逗号多模式 | ✅ | `1, 2 ->` | `case 1 \| 2 =>` | |
| `for` 循环 | ✅ | `for (i in 0..n)` | `for (i in 0..n)` | |
| `for` + `until` | ✅ | `for (i in 0 until n)` | `for (i in 0..n)` (排他) | |
| `for` + `downTo` | ✅ | `for (i in n downTo 0)` | 降序区间 | |
| `for` + `step` | ✅ | `for (i in 0..n step 2)` | | |
| `for` + `withIndex` | ✅ | `for ((i, v) in xs.withIndex())` | 索引+值遍历 | |
| `for` + 解构 | ✅ | `for ((k, v) in map)` | | |
| `while` / `do-while` | ✅ | | | |
| `while(true)` 返回推断 | ✅ | 内含 `return` 时 | 自动添加 `: Unit` + 不可达默认返回 | |
| `break` / `continue` | ✅ | | | |
| 标签跳转 `break@label` | ✅ | `break@outerLoop` | | |
| `repeat(n) { }` | ✅ | `repeat(5) { it -> }` | `for` 循环 | |

---

## 5. 函数

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 顶层函数 | ✅ | `fun f() { }` | `func f() { }` | |
| 成员方法 | ✅ | `fun f() { }` | `func f() { }` | |
| 表达式体函数 | ✅ | `fun f() = expr` | `func f() { return expr }` | |
| 递归函数 | ✅ | | 递归 `Unit` 函数自动标注返回类型 | |
| 嵌套局部函数 | ✅ | `fun outer() { fun inner() { } }` | 嵌套 `func` | |
| 默认参数 | ✅ | `fun f(x: Int = 1)` | `func f(x!: Int64 = 1)` | 仓颉具名可选形参 |
| 调用端命名参数 | ✅ | `f(x = 5)` | `f(x: 5)` | 自动在调用端补名 |
| 函数类型 | ✅ | `(Int, Int) -> Int` | `(Int64, Int64) -> Int64` | |
| 高阶函数 | ✅ | `fun f(g: (Int) -> Int)` | | |
| Lambda 表达式 | ✅ | `{ x -> x * 2 }` | `{ x => x * 2 }` | |
| 隐式 `it` 参数 | ✅ | `{ it * 2 }` | `{ it => it * 2 }` | 显式化 |
| 扩展函数 | ✅ | `fun Int.square() = this * this` | `extend Int64 { func square() }` | P2 已实现 |
| 扩展属性 | ❌ | `val String.lastChar get() = ...` | — | |
| 可变参数 `vararg` | ✅ | `fun sum(vararg nums: Int)` | `func sum(nums: Array<Int64>)` | 翻译为数组参数 |
| `tailrec` 尾递归优化 | ⚠️ | `tailrec fun f(...)` | 作为普通递归函数 | 关键字被跳过 |
| `inline` 函数 | ⚠️ | `inline fun f(...)` | 作为普通函数 | 关键字被跳过 |
| `crossinline` / `noinline` | ⚠️ | | 关键字被跳过 | 修饰符识别 |

---

## 6. 类与对象

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 类定义 | ✅ | `class A { }` | `class A { }` | |
| 主构造器 | ✅ | `class A(val x: Int)` | 显式 `init(x: Int64) { this.x = x }` | 仓颉无主构造器语法 |
| 次构造器 | ⚠️ | `constructor(...)` | 部分支持 | |
| `init { }` 初始化块 | ✅ | `init { ... }` | 并入构造器体 | |
| `data class` | ✅ | `data class P(val x: Int)` | 自动生成 `toString()` | `<: ToString` |
| `open class` | ✅ | `open class A { }` | `open class A { }` | |
| `abstract class` | ✅ | `abstract class A { }` | `abstract class A { }` | |
| `sealed class` | ✅ | `sealed class S { }` | `sealed class` + `match` 穷尽分支 | |
| 嵌套类 | ⚠️ | `class Outer { class Inner { } }` | 部分支持 | |
| 内部类 `inner class` | ❌ | `inner class Inner` | — | `inner` 关键字不处理 |
| 对象声明 `object` | ✅ | `object Singleton { }` | `class + private init + static INSTANCE` | 单例模式 |
| 对象表达式（匿名对象） | ❌ | `object : Interface { }` | — | |
| `companion object` | ✅ | `companion object { ... }` | `static func` / `static let` | P2 已实现 |
| 属性 getter/setter | ❌ | `var x: Int; get() = ...; set(v) { }` | — | 仓颉无自定义属性访问器 |
| 可见性修饰符 | ⚠️ | `public/private/protected/internal` | 识别但映射可能不精确 | `internal` 无仓颉等价物 |
| `data object` | ❌ | `data object X` | — | Kotlin 1.9+ |

---

## 7. 继承与接口

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 类继承 | ✅ | `class B : A()` | `class B <: A` + `super()` | |
| 接口定义 | ✅ | `interface I { fun f() }` | `interface I { func f() }` | |
| 接口实现 | ✅ | `class C : I { override fun f() }` | `class C <: I` | |
| 多接口实现 | ✅ | `class C : I1, I2` | `class C <: I1 & I2` | |
| 方法覆盖 `override` | ✅ | `override fun f()` | `public override func f()` | |
| `open` 方法 | ✅ | `open fun f()` | 自动为 open class 方法添加 `open` | |
| `super` 调用 | ✅ | `super.f()` / `super(args)` | | |
| 抽象方法 | ✅ | `abstract fun f()` | `public func f()` (签名) | |
| 多层继承链 | ✅ | 4+ 层深度继承 | | 用例 163 验证 |
| 接口默认方法 | ⚠️ | `interface I { fun f() = ... }` | 部分支持 | |

---

## 8. 泛型

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 泛型类 | ✅ | `class Stack<T>` | `class Stack<T>` | |
| 嵌套泛型 | ✅ | `Stack<Pair<Int, Int>>` | `Stack<(Int64, Int64)>` | 用例 127 验证 |
| 泛型函数 | ✅ | `fun <T> first(list: List<T>): T` | `func first<T>(list: ArrayList<T>): T` | 保留类型参数 |
| 类型上界 `<T : Bound>` | ❌ | `<T : Comparable<T>>` | — | |
| 型变 `in/out` | ❌ | `List<out T>` / `MutableList<in T>` | — | 仓颉泛型模型不同 |
| 星投影 `<*>` | ❌ | `List<*>` | — | |
| 具体化类型参数 `reified` | ❌ | `inline fun <reified T>` | — | 需 inline + 运行时类型信息 |
| `where` 多约束 | ❌ | `<T> where T : A, T : B` | — | |

---

## 9. 枚举

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 基础枚举 | ✅ | `enum class Color { RED, GREEN }` | `enum Color { ... }` | `@Derive[Equatable]` |
| 枚举自定义 `toString` | ✅ | | `<: ToString` + `match` 分支 | |
| 枚举 `when` 穷尽匹配 | ✅ | `when (e) { A -> ...; B -> ... }` | `match (e) { ... }` | |
| 枚举构造器参数 | ✅ | `enum class E(val v: Int) { A(1) }` | `class` + `static let` + `_ordinal` | P1 已实现 |
| `.values()` | ✅ | `Color.values()` | 枚举全项数组字面量 | |
| `.name` / `.ordinal` | ⚠️ | `e.name` / `e.ordinal` | 部分支持 | 带参枚举通过 `_ordinal` 字段 |
| 枚举抽象方法 | ❌ | `enum class E { A { override fun f() } }` | — | 每个枚举项作为匿名子类 |
| `entries` 属性（Kotlin 1.9+） | ❌ | `Color.entries` | — | |

---

## 10. 空安全

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 可空类型 `?` | ✅ | `val x: Int?` | `var x: ?Int64` | 前缀 `?` 语法 |
| 安全调用 `?.` | ✅ | `x?.length` | `if let` 模式 | |
| Elvis 操作符 `?:` | ✅ | `x ?: default` | `x ?? default` | |
| 非空断言 `!!` | ✅ | `x!!` | `.getOrThrow()` | 上下文感知 |
| `?.let { }` | ✅ | `x?.let { it.f() }` | `if (let Some(x) <- x) { ... }` | |
| 块式 `if (x != null)` 智能转换 | ✅ | `if (x != null) { x.f() }` | `if (let Some(x) <- x) { ... }` | 含嵌套 |
| 早返式 `if (x == null) return` 智能转换 | ❌ | `if (x == null) return; x.f()` | — | 仓颉不允许同名遮蔽重绑定 |
| `== null` / `!= null` 表达式 | ✅ | `x == null` | `x.isNone()` | 值位置自动转换 |
| `?.` 链式安全调用 | ✅ | `a?.b?.c` | 嵌套 `if let` | |
| 可空成员字段检测 | ✅ | `node.prev?.value` | 精确判断字段可空性 | |
| 空安全集合 `filterNotNull` | ✅ | `list.filterNotNull()` | 完整支持 | P3 新增 |

---

## 11. 集合与集合操作

### 11.1 集合类型

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| `listOf(...)` | ✅ | `listOf(1, 2, 3)` | `ArrayList([1, 2, 3])` | |
| `mutableListOf(...)` | ✅ | `mutableListOf(1, 2)` | `ArrayList([1, 2])` | |
| `arrayListOf(...)` | ✅ | `arrayListOf(1, 2)` | `ArrayList([1, 2])` | |
| `mapOf(...)` | ✅ | `mapOf(1 to "a")` | `HashMap([(1, "a")])` | |
| `mutableMapOf(...)` | ✅ | | `HashMap(...)` | |
| `hashMapOf(...)` | ✅ | | `HashMap(...)` | |
| `setOf(...)` | ✅ | `setOf(1, 2)` | `HashSet([1, 2])` | |
| `mutableSetOf(...)` | ✅ | | `HashSet(...)` | |
| `emptyList/Map/Set` | ✅ | `emptyList<Int>()` | `ArrayList<Int64>()` | |
| `Array(n) { }` | ✅ | `Array(n) { i -> ... }` | `Array(n, { i => ... })` | |
| `intArrayOf(...)` | ⚠️ | `intArrayOf(1, 2)` | — | 建议用 `ArrayList` |
| `Pair` / `Triple` | ✅ | `Pair(1, "a")` | `(1, "a")` 元组 | |

### 11.2 集合基本操作

| 特性 | 状态 | Kotlin | Cangjie |
|:---|:---:|:---|:---|
| `add` / `append` | ✅ | `.add(x)` | `.append(x)` |
| `addAll` | ✅ | `.addAll(xs)` | `.add(all: xs)` |
| `get` / `set` (下标) | ✅ | `xs[i]` / `xs[i] = v` | |
| `size` | ✅ | `.size` | `.size` |
| `isEmpty` / `isNotEmpty` | ✅ | `.isEmpty()` | `.isEmpty()` |
| `contains` | ✅ | `.contains(x)` | `.contains(x)` |
| `containsKey` | ✅ | `map.containsKey(k)` | `.contains(k)` |
| `remove` | ✅ | `.remove(x)` | `.remove(x)` |
| `removeAt` | ✅ | `.removeAt(i)` | | |
| `clear` | ✅ | `.clear()` | `.clear()` |
| `indexOf` | ✅ | `.indexOf(x)` | `.indexOf(x)` |
| `getOrDefault` | ✅ | `map.getOrDefault(k, d)` | `map.getOrDefault(k, d)` |
| `.indices` | ✅ | `xs.indices` | `0..xs.size` |
| `.lastIndex` | ✅ | `xs.lastIndex` | `xs.size - 1` |
| `.first` / `.last` | ✅ | | |
| `subList` | ✅ | `.subList(from, to)` | |

### 11.3 函数式集合操作

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| `map { }` | ✅ | `.map { it * 2 }` | `collectArrayList(xs.iterator().map {...})` | 即时求值 |
| `filter { }` | ✅ | `.filter { it > 0 }` | `collectArrayList(xs.iterator().filter {...})` | |
| `flatMap { }` | ✅ | `.flatMap { ... }` | | P2 新增 |
| `forEach { }` | ✅ | `.forEach { ... }` | | |
| `forEachIndexed { }` | ✅ | `.forEachIndexed { i, v -> }` | | |
| `fold` / `reduce` | ✅ | `.fold(0) { acc, x -> }` | | |
| `sum` / `sumOf` | ✅ | `.sum()` / `.sumOf { }` | | |
| `count` / `count { }` | ✅ | `.count()` / `.count { }` | | |
| `any { }` / `all { }` | ✅ | `.any { it > 0 }` | | |
| `none { }` | ✅ | `.none { }` | | |
| `max` / `min` | ✅ | `.max()` / `.min()` | | |
| `maxOrNull` / `minOrNull` | ✅ | `.maxOrNull()` | 返回 `Option`（打印显示 `Some(x)`） | |
| `firstOrNull` / `lastOrNull` | ✅ | `.firstOrNull { }` | | |
| `sorted` | ✅ | `.sorted()` | IIFE 拷贝-排序-返回 | 稳定排序 |
| `sortedBy { }` | ✅ | `.sortedBy { it.x }` | | |
| `sortedDescending` | ✅ | | | |
| `sortedByDescending { }` | ✅ | | | |
| `reversed` | ✅ | `.reversed()` | | |
| `joinToString` | ✅ | `.joinToString(", ")` | `String.join(...)` | 支持 prefix/postfix/transform |
| `take` / `drop` | ✅ | `.take(n)` / `.drop(n)` | 迭代器 `.take(n)` / `.skip(n)` | |
| `distinct` | ✅ | `.distinct()` | | P2 新增 |
| `groupBy { }` | ✅ | `.groupBy { it.key }` | | P2 新增 |
| `associate { }` | ✅ | `.associate { it to v }` | | P2 新增 |
| `associateBy { }` | ✅ | `.associateBy { it.key }` | | P3 新增 |
| `associateWith { }` | ✅ | `.associateWith { f(it) }` | | P3 新增 |
| `mapIndexed { }` | ✅ | `.mapIndexed { i, v -> }` | | P3 新增 |
| `filterNot { }` | ✅ | `.filterNot { cond }` | | P3 新增 |
| `filterNotNull` | ✅ | `.filterNotNull()` | | P3 新增 |
| `flatten` | ✅ | `.flatten()` | | P3 新增 |
| `mapValues { }` | ✅ | `.mapValues { }` | | P3 新增 |
| `mapKeys { }` | ✅ | `.mapKeys { }` | | P3 新增 |
| `indexOfFirst { }` | ✅ | `.indexOfFirst { }` | | P3 新增 |
| `indexOfLast { }` | ✅ | `.indexOfLast { }` | | P3 新增 |
| `find { }` | ✅ | `.find { }` | | P3 新增 |
| `findLast { }` | ✅ | `.findLast { }` | | P3 新增 |
| `forEach { }` | ✅ | `.forEach { }` | for 循环 | P3 新增 |
| `forEachIndexed { }` | ✅ | `.forEachIndexed { i, v -> }` | | P3 新增 |
| `toList` / `toMutableList` | ✅ | | | |
| `average` | ✅ | `.average()` | | |
| `asSequence()` | ❌ | `.asSequence()` | — | 所有操作均为即时求值 |
| `zip { }` | ✅ | `.zip(other) { }` | 迭代器 `.zip()` | |
| `chunked` / `windowed` | ✅ | `.chunked(n)` | IIFE + 手动分块 | `chunked` 已支持 |
| `partition { }` | ✅ | `.partition { }` | IIFE + 条件分组 | |
| `unzip` | ❌ | `.unzip()` | — | |

### 11.4 就地排序

| 特性 | 状态 |
|:---|:---:|
| `sort()` / `sortDescending()` | ✅ |
| `sortBy { }` / `sortByDescending { }` | ✅ |

---

## 12. 字符串

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| 字符串模板 `${}` | ✅ | `"Hello, $name"` | `"Hello, ${name}"` | |
| 多行字符串 `"""` | ⚠️ | `"""..."""` | | 部分场景 |
| `length` | ✅ | `.length` | `.size` | |
| `substring` | ✅ | `.substring(a, b)` | | |
| `split` | ✅ | `.split(",")` | | P2 新增 |
| `replace` | ✅ | `.replace("a", "b")` | | P2 新增 |
| `trim` / `trimStart` / `trimEnd` | ✅ | | | |
| `uppercase` / `lowercase` | ✅ | `.uppercase()` | | |
| `startsWith` / `endsWith` | ✅ | | | P2 新增 |
| `contains` (字符串) | ✅ | `.contains("sub")` | | P2 新增 |
| `toInt` / `toLong` / `toDouble` | ✅ | `.toInt()` | 上下文感知（字符串→parse / 数值→Int64(...)） | |
| `reversed` (字符串) | ✅ | `.reversed()` | Rune 数组逆序重建 | |
| `repeat` | ✅ | `"ab".repeat(3)` | `"ab" * 3` | |
| `padStart` / `padEnd` | ✅ | `.padStart(5, '0')` | 仓颉 `padding:` 具名参数 | |
| `toCharArray` | ✅ | `.toCharArray()` | `.toRuneArray()` | |
| `for (c in s)` 遍历 | ✅ | `for (c in str)` | `for (c in str.runes())` | 得 Rune 而非字节 |
| `s[i]` 字符索引 | ✅ | `str[0]` | `str.toRuneArray()[0]` | 接收者证明为字符串时 |
| 字符判定方法 | ✅ | `isDigit/isLetter/isWhitespace/...` | Rune 的 `isAscii*` 方法 | |
| 字符算术 `c - '0'` | ✅ | `c - '0'` / `'0' + n` | `Int64(UInt32(c))` 码点运算 | |
| `Char.code` | ✅ | `c.code` | 码点转换 | |
| `Int.toChar()` | ✅ | `n.toChar()` | `Rune(UInt32(n))` | |

### StringBuilder

| 特性 | 状态 | Kotlin | Cangjie |
|:---|:---:|:---|:---|
| `StringBuilder()` | ✅ | | |
| `append` | ✅ | `.append(x)` | `.append(x)` |
| `toString` | ✅ | `.toString()` | `.toString()` |
| `clear` | ✅ | `.clear()` | `.reset()` |
| `insert` | ✅ | `.insert(i, x)` | |
| `deleteCharAt` | ✅ | `.deleteCharAt(i)` | |
| `isEmpty` / `isNotEmpty` | ✅ | `.isEmpty()` | `.toString().size == 0` |
| `length` | ✅ | `.length` | `.size` |

---

## 13. 异常处理

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| `try / catch` | ✅ | | | |
| `try / catch / finally` | ✅ | | | |
| `throw` | ✅ | `throw Exception("msg")` | | |
| `try` 作为表达式 | ✅ | `return try { x } catch { y }` | | |
| 多 `catch` 分支 | ✅ | `catch (e: IOException)` | | |
| 自定义异常类 | ✅ | `class MyException : Exception()` | | |
| `runCatching` / `Result` | ❌ | `runCatching { }` | — | |

---

## 14. 类型检查与转换

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| `is` 类型检查 | ✅ | `if (x is String)` | `if (x is String)` | 语法一致 |
| `!is` 否定检查 | ✅ | `if (x !is Int)` | | |
| 智能转型（`is` 后） | ✅ | `if (x is String) x.length` | | |
| `as` 类型转换 | ✅ | `x as String` | `(x as String)` | |
| `as?` 安全转换 | ✅ | `x as? String` | `if (x is T) { x as T } else { None }` | |

---

## 15. 解构声明

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| Pair 解构 | ✅ | `val (a, b) = pair` | | |
| Triple 解构 | ✅ | `val (a, b, c) = triple` | | |
| data class 解构 | ✅ | `val (x, y) = point` | | P2 增强 |
| Map.Entry 解构 | ✅ | `for ((k, v) in map)` | | |
| 嵌套解构 | ✅ | 多层解构 | | P2 增强 |

---

## 16. 区间与步进

| 特性 | 状态 | Kotlin | Cangjie |
|:---|:---:|:---|:---|
| `..` 闭区间 | ✅ | `1..10` | `1..=10` |
| `until` 半开区间 | ✅ | `0 until n` | `0..n` |
| `downTo` 降序 | ✅ | `10 downTo 1` | |
| `step` 步长 | ✅ | `1..10 step 2` | |
| `in` / `!in` 成员检查 | ✅ | `if (x in 1..10)` | 转为 `>=` 和 `<=` 比较 |
| 集合 `in` / `!in` | ✅ | `if (x in list)` | `.contains(x)` |

---

## 17. 作用域函数

| 特性 | 状态 | Kotlin | Cangjie | 备注 |
|:---|:---:|:---|:---|:---|
| `?.let { }` | ✅ | `x?.let { it.f() }` | `if (let Some(x) <- x) { ... }` | |
| `let { }` (非空) | ✅ | `x.let { ... }` | SafeLet 语法 | |
| `run { }` | ✅ | `obj.run { ... }` | IIFE 去糖 `({ => body })()` | |
| `with(obj) { }` | ❌ | `with(obj) { x = 1 }` | — | 隐式 `this` 不支持 |
| `apply { }` | ✅ | `obj.apply { x = 1 }` | IIFE + 返回 receiver | 同 `also` 模式 |
| `also { }` | ✅ | `obj.also { it.f() }` | IIFE + 返回 receiver | |
| `takeIf { }` / `takeUnless { }` | ❌ | `x.takeIf { it > 0 }` | — | |

---

## 18. 协程与异步

| 特性 | 状态 | 备注 |
|:---|:---:|:---|
| `suspend` 函数 | ❌ | Kotlin 与仓颉的异步模型根本不同 |
| `launch { }` / `async { }` | ❌ | 无协程作用域对应 |
| `Deferred` / `await()` | ❌ | |
| `Flow` | ❌ | |
| `Channel` | ❌ | |
| `withContext` | ❌ | |
| `coroutineScope` | ❌ | |

> **难以支持的原因**：Kotlin 协程基于 continuation-passing style (CPS) 变换，
> 编译器将 `suspend` 函数转换为状态机。仓颉使用不同的并发原语（如 Actor 模型），
> 两者在执行模型、调度方式、取消机制上存在根本性差异，无法通过简单的语法映射实现翻译。
> 建议：将源码中的异步逻辑手动重构为同步代码，或使用仓颉原生并发机制重写。

---

## 19. 委托

| 特性 | 状态 | 备注 |
|:---|:---:|:---|
| `by lazy { }` | ✅ | IIFE 模式 `({ => expr })()` |
| `by Delegates.observable()` | ❌ | |
| `by Delegates.vetoable()` | ❌ | |
| `by map` (Map 委托) | ❌ | |
| 接口委托 `class A : I by impl` | ❌ | |
| 自定义属性委托 `ReadWriteProperty` | ❌ | |

> **难以支持的原因**：Kotlin 的委托属性通过编译器生成的 `getValue`/`setValue` 包装器实现。
> 仓颉没有等价的属性拦截机制，无法透明地代理属性的读写操作。
> `by lazy` 可通过手动翻译为初始化标志 + 缓存字段来模拟，但通用委托机制难以自动化翻译。

---

## 20. 注解与反射

| 特性 | 状态 | 备注 |
|:---|:---:|:---|
| 标准注解 `@JvmStatic` 等 | ⚠️ | 注解被跳过（不影响翻译逻辑） |
| 自定义注解 | ❌ | |
| `::class` 类引用 | ❌ | 无反射 API 映射 |
| `::function` 函数引用 | ❌ | |
| `::property` 属性引用 | ❌ | |
| `KClass` / `KFunction` | ❌ | |

> **难以支持的原因**：反射需要运行时类型信息（RTTI）支持。
> 仓颉的反射 API 与 Kotlin 的 `kotlin-reflect` 完全不同，无法直接映射。
> 函数/属性引用（`::f`）是 Kotlin 编译器特性，依赖具体化的函数对象类型。

---

## 21. 其他高级特性

| 特性 | 状态 | 备注 |
|:---|:---:|:---|
| `typealias` 类型别名 | ✅ | 解析时展开为目标类型 |
| `value class` / `inline class` | ❌ | Kotlin 1.5+/1.3+ 特性 |
| 操作符重载 | ❌ | 关键字识别但不特殊渲染 |
| 中缀函数 `infix` | ❌ | 关键字识别但不特殊渲染 |
| DSL 构建器 | ❌ | 需要 lambda receiver 类型推断 |
| 上下文接收者 `context(...)` | ❌ | Kotlin 1.6.20+ 实验特性 |
| 多文件项目 | ✅ | 目录输入 → 合并翻译 → cjpm 项目（32/32 用例通过） |
| `package` / `import` | ✅ | 识别并映射为仓颉 `package`/`import std.*` |
| 解构赋值 `componentN` | ⚠️ | data class / Pair / Triple 的解构已支持 |
| 尾随 lambda 语法 | ✅ | `f(x) { ... }` → 正常解析 |
| 标签返回 `return@label` | ⚠️ | 部分场景 |
| SAM 转换 | ❌ | 单抽象方法接口自动转 lambda |
| 密封接口 `sealed interface` | ❌ | Kotlin 1.5+ |
| Kotlin Multiplatform `expect/actual` | ❌ | |

---

## 22. 类型映射表

| Kotlin 类型 | Cangjie 类型 | 备注 |
|:---|:---|:---|
| `Int` | `Int64` | |
| `Short` / `Byte` | `Int64` | 统一整数 |
| `Long` | `Int64` | |
| `Float` | `Float64` | |
| `Double` | `Float64` | |
| `Boolean` | `Bool` | |
| `Char` | `Rune` | |
| `String` | `String` | |
| `Unit` | `Unit` | |
| `Any` | `Object` | |
| `T?` | `?T` | 可空类型前缀 |
| `List<T>` | `ArrayList<T>` | |
| `MutableList<T>` | `ArrayList<T>` | |
| `Map<K,V>` | `HashMap<K,V>` | |
| `MutableMap<K,V>` | `HashMap<K,V>` | |
| `Set<T>` | `HashSet<T>` | |
| `MutableSet<T>` | `HashSet<T>` | |
| `Pair<A,B>` | `(A, B)` | 元组 |
| `Triple<A,B,C>` | `(A, B, C)` | 元组 |
| `Array<T>` | `Array<T>` | |
| `(A, B) -> R` | `(A, B) -> R` | 函数类型语法一致 |
| `Exception` | `Exception` | |

> **注意**：仓颉 `Float64` 默认打印 6 位小数（如 `5.000000`），与 Kotlin 的 `5.0` 不同。
> 这是仓颉平台特性，非翻译器缺陷。

---

## 23. 未支持特性优先级排序

按「实用价值 ÷ 实现成本」排序：

### 已完成的 P1/P2 特性

| # | 特性 | 状态 | 说明 |
|:---|:---|:---:|:---|
| 1 | **`by lazy { }`** | ✅ | IIFE 即时求值模式 |
| 2 | **`vararg` 可变参数** | ✅ | 翻译为 `Array<T>` 参数 |
| 3 | **泛型函数完整支持** | ✅ | 保留函数级类型参数 `<T>` |
| 4 | **`object` 单例声明** | ✅ | class + 私有构造器 + 静态 INSTANCE |
| 5 | **`typealias`** | ✅ | 解析时展开为目标类型 |
| 6 | **`as` / `as?` 完整支持** | ✅ | Cangjie cast 语法 |
| 7 | **作用域函数 `run/apply/also`** | ✅ | IIFE 去糖 |
| 8 | **更多集合操作 `zip/chunked/partition`** | ✅ | 迭代器映射规则 |

### P1（高优先级）— 常用且实现成本可控

| # | 特性 | 使用频率 | 实现复杂度 | 说明 |
|:---|:---|:---:|:---:|:---|
| 1 | **早返式空安全智能转换** | 高 | 中 | `if (x == null) return; x.f()` → 需数据流分析 + 后续引用自动 unwrap |
| 2 | **属性 getter/setter** | 中 | 高 | 仓颉无自定义属性访问器；需翻译为显式 getter/setter 方法 + 调用端替换 |

### P2（中优先级）— 有价值但实现有一定复杂度

| # | 特性 | 使用频率 | 实现复杂度 | 说明 |
|:---|:---|:---:|:---:|:---|
| 3 | **操作符重载** | 低-中 | 中 | 需将操作符调用展开为方法调用（`a + b` → `a.plus(b)`） |
| 4 | **扩展属性** | 低 | 中 | `extend` 块内添加计算属性 |
| 5 | **`with(obj) { }` 完整支持** | 低-中 | 中 | 需隐式 `this` → 显式变量引用 |

### P3（低优先级）— 使用频率低或实现成本极高

| # | 特性 | 使用频率 | 实现复杂度 | 说明 |
|:---|:---|:---:|:---:|:---|
| 13 | **多文件项目翻译** | 高(工程) | 极高 | 需跨文件符号解析、包结构生成、依赖拓扑 |
| 14 | **泛型型变 `in/out`** | 低 | 高 | 仓颉泛型模型与 Kotlin 不同（无声明点型变） |
| 15 | **`inner class`** | 低 | 中 | 需要持有外部类引用 |
| 16 | **`value class` / `inline class`** | 低 | 中 | 可展开为普通类 |
| 17 | **密封接口 `sealed interface`** | 低 | 中 | 扩展现有 `sealed class` 支持 |
| 18 | **SAM 转换** | 低 | 高 | 需类型推断识别单抽象方法接口 |
| 19 | **接口委托 `by`** | 低 | 高 | 需自动生成转发方法 |
| 20 | **注解处理** | 低 | 高 | 仓颉注解模型完全不同 |

### 不建议支持

| 特性 | 原因 |
|:---|:---|
| **协程 / `suspend` / `Flow`** | Kotlin 与仓颉异步模型根本不同（CPS 状态机 vs Actor 模型），无法语法映射，需完全重写异步逻辑 |
| **反射 `::class` / `KClass`** | 依赖运行时类型信息，两语言反射 API 完全不兼容 |
| **Kotlin Multiplatform `expect/actual`** | 平台特定编译机制，与翻译器目标不相关 |
| **上下文接收者 `context(...)`** | Kotlin 实验特性，尚未稳定 |
| **DSL 构建器** | 依赖 lambda receiver + 类型推断的深度组合，通用翻译几乎不可行 |

---

## 统计总览

| 类别 | 特性数 | ✅ 已支持 | ⚠️ 部分 | ❌ 未支持 |
|:---|:---:|:---:|:---:|:---:|
| 基础类型与字面量 | 17 | 17 | 0 | 0 |
| 变量与类型推断 | 8 | 6 | 1 | 1 |
| 运算符 | 11 | 9 | 0 | 2 |
| 控制流 | 17 | 17 | 0 | 0 |
| 函数 | 16 | 14 | 1 | 1 |
| 类与对象 | 14 | 9 | 2 | 3 |
| 继承与接口 | 10 | 9 | 1 | 0 |
| 泛型 | 8 | 3 | 0 | 5 |
| 枚举 | 8 | 5 | 1 | 2 |
| 空安全 | 11 | 9 | 1 | 1 |
| 集合与集合操作 | 50+ | 45 | 2 | 3+ |
| 字符串与 StringBuilder | 26 | 26 | 0 | 0 |
| 异常处理 | 7 | 6 | 0 | 1 |
| 类型检查与转换 | 5 | 5 | 0 | 0 |
| 解构声明 | 5 | 5 | 0 | 0 |
| 区间与步进 | 6 | 6 | 0 | 0 |
| 作用域函数 | 7 | 4 | 0 | 3 |
| 协程与异步 | 7 | 0 | 0 | 7 |
| 委托 | 6 | 1 | 0 | 5 |
| 注解与反射 | 6 | 0 | 1 | 5 |
| 其他高级特性 | 14 | 2 | 3 | 9 |
| **合计** | **~260** | **~197 (76%)** | **~13 (5%)** | **~50 (19%)** |

> 核心特性（基础类型、控制流、函数、类、集合、字符串、异常、区间）覆盖率接近 **100%**。
> P1/P2 特性已大幅完善：`by lazy`、`vararg`、`object` 单例、泛型函数、`typealias`、作用域函数、类型转换、更多集合操作均已支持。
> 未支持的特性多集中在高级元编程（反射/注解）、异步（协程）和语言语法糖（委托/DSL）领域。
