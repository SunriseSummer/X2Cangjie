//! 标准库接口映射：Kotlin 标准库 → 仓颉标准库的数据驱动映射表。
//!
//! 将 API 映射与语言特性转换（render_calls.rs / render.rs）解耦：
//! - 本模块定义声明式映射表（类型、成员属性、成员方法、全局函数、import 等）
//! - render_calls.rs 对复杂/高频 API 保留特殊处理逻辑
//! - 新增映射只需修改本文件的表数据即可

/// Kotlin 类型 → 仓颉类型映射。
pub struct TypeMapping {
    pub kotlin: &'static str,
    pub cangjie: &'static str,
}

/// 成员属性映射：`base.kotlin_name` → `base.cangjie_name`。
pub struct PropMapping {
    pub kotlin: &'static str,
    pub cangjie: &'static str,
}

/// 简单成员方法映射（名称直通或简单重命名，签名兼容）。
pub struct MethodMapping {
    pub kotlin: &'static str,
    pub cangjie: &'static str,
    /// 适用的接收者类型提示（"string"/"collection"/"any"）。
    pub receiver: &'static str,
}

/// Kotlin import → 仓颉 import 映射。
pub struct ImportMapping {
    pub kotlin_prefix: &'static str,
    pub cangjie_import: &'static str,
}

/// 全局函数映射。
pub struct GlobalFuncMapping {
    pub kotlin: &'static str,
    pub cangjie: &'static str,
}

// ============ 类型映射表 ============

pub static TYPE_MAP: &[TypeMapping] = &[
    TypeMapping { kotlin: "Int", cangjie: "Int64" },
    TypeMapping { kotlin: "Long", cangjie: "Int64" },
    TypeMapping { kotlin: "Short", cangjie: "Int64" },
    TypeMapping { kotlin: "Byte", cangjie: "Int64" },
    TypeMapping { kotlin: "Double", cangjie: "Float64" },
    TypeMapping { kotlin: "Float", cangjie: "Float64" },
    TypeMapping { kotlin: "Boolean", cangjie: "Bool" },
    TypeMapping { kotlin: "Char", cangjie: "Rune" },
    TypeMapping { kotlin: "String", cangjie: "String" },
    TypeMapping { kotlin: "Unit", cangjie: "Unit" },
    TypeMapping { kotlin: "Any", cangjie: "Any" },
    TypeMapping { kotlin: "Nothing", cangjie: "Nothing" },
    TypeMapping { kotlin: "IntArray", cangjie: "Array<Int64>" },
    TypeMapping { kotlin: "BooleanArray", cangjie: "Array<Bool>" },
    TypeMapping { kotlin: "DoubleArray", cangjie: "Array<Float64>" },
    TypeMapping { kotlin: "LongArray", cangjie: "Array<Int64>" },
    TypeMapping { kotlin: "CharArray", cangjie: "Array<Rune>" },
    TypeMapping { kotlin: "StringBuilder", cangjie: "StringBuilder" },
    TypeMapping { kotlin: "Exception", cangjie: "Exception" },
    TypeMapping { kotlin: "RuntimeException", cangjie: "Exception" },
    TypeMapping { kotlin: "IllegalArgumentException", cangjie: "IllegalArgumentException" },
    TypeMapping { kotlin: "IllegalStateException", cangjie: "Exception" },
    TypeMapping { kotlin: "IndexOutOfBoundsException", cangjie: "Exception" },
    TypeMapping { kotlin: "UnsupportedOperationException", cangjie: "Exception" },
    TypeMapping { kotlin: "Comparable", cangjie: "Comparable" },
];

// ============ 泛型容器类型映射 ============

/// 泛型容器前缀映射（解析器中 `map_type` 需要特殊处理泛型参数）。
pub static GENERIC_CONTAINER_MAP: &[TypeMapping] = &[
    TypeMapping { kotlin: "List", cangjie: "ArrayList" },
    TypeMapping { kotlin: "MutableList", cangjie: "ArrayList" },
    TypeMapping { kotlin: "ArrayList", cangjie: "ArrayList" },
    TypeMapping { kotlin: "Map", cangjie: "HashMap" },
    TypeMapping { kotlin: "MutableMap", cangjie: "HashMap" },
    TypeMapping { kotlin: "HashMap", cangjie: "HashMap" },
    TypeMapping { kotlin: "LinkedHashMap", cangjie: "HashMap" },
    TypeMapping { kotlin: "Set", cangjie: "HashSet" },
    TypeMapping { kotlin: "MutableSet", cangjie: "HashSet" },
    TypeMapping { kotlin: "HashSet", cangjie: "HashSet" },
    TypeMapping { kotlin: "LinkedHashSet", cangjie: "HashSet" },
    TypeMapping { kotlin: "ArrayDeque", cangjie: "ArrayList" },
    TypeMapping { kotlin: "Queue", cangjie: "ArrayList" },
    TypeMapping { kotlin: "Deque", cangjie: "ArrayList" },
    TypeMapping { kotlin: "Stack", cangjie: "ArrayList" },
];

// ============ 成员属性映射 ============

pub static PROP_MAP: &[PropMapping] = &[
    PropMapping { kotlin: "length", cangjie: "size" },
    PropMapping { kotlin: "lastIndex", cangjie: "(size - 1)" },
];

// ============ 简单方法映射 ============

pub static METHOD_MAP: &[MethodMapping] = &[
    // String 方法
    MethodMapping { kotlin: "toUpperCase", cangjie: "toAsciiUpper", receiver: "string" },
    MethodMapping { kotlin: "uppercase", cangjie: "toAsciiUpper", receiver: "string" },
    MethodMapping { kotlin: "toLowerCase", cangjie: "toAsciiLower", receiver: "string" },
    MethodMapping { kotlin: "lowercase", cangjie: "toAsciiLower", receiver: "string" },
    MethodMapping { kotlin: "trim", cangjie: "trimAscii", receiver: "string" },
    MethodMapping { kotlin: "trimStart", cangjie: "trimAsciiStart", receiver: "string" },
    MethodMapping { kotlin: "trimEnd", cangjie: "trimAsciiEnd", receiver: "string" },
    MethodMapping { kotlin: "startsWith", cangjie: "startsWith", receiver: "string" },
    MethodMapping { kotlin: "endsWith", cangjie: "endsWith", receiver: "string" },
    MethodMapping { kotlin: "contains", cangjie: "contains", receiver: "string" },
    MethodMapping { kotlin: "isEmpty", cangjie: "isEmpty", receiver: "string" },

    // Char 方法
    MethodMapping { kotlin: "isDigit", cangjie: "isAsciiNumber", receiver: "char" },
    MethodMapping { kotlin: "isLetter", cangjie: "isAsciiLetter", receiver: "char" },
    MethodMapping { kotlin: "isWhitespace", cangjie: "isAsciiWhiteSpace", receiver: "char" },
    MethodMapping { kotlin: "isUpperCase", cangjie: "isAsciiUpperCase", receiver: "char" },
    MethodMapping { kotlin: "isLowerCase", cangjie: "isAsciiLowerCase", receiver: "char" },

    // 集合通用方法
    MethodMapping { kotlin: "add", cangjie: "add", receiver: "collection" },
    MethodMapping { kotlin: "contains", cangjie: "contains", receiver: "collection" },
    MethodMapping { kotlin: "isEmpty", cangjie: "isEmpty", receiver: "collection" },
    MethodMapping { kotlin: "remove", cangjie: "remove", receiver: "collection" },

    // 类型转换
    MethodMapping { kotlin: "toString", cangjie: "toString", receiver: "any" },
];

// ============ 全局函数映射 ============

pub static GLOBAL_FUNC_MAP: &[GlobalFuncMapping] = &[
    GlobalFuncMapping { kotlin: "println", cangjie: "println" },
    GlobalFuncMapping { kotlin: "print", cangjie: "print" },
    GlobalFuncMapping { kotlin: "readLine", cangjie: "Console.stdIn.readln" },
    GlobalFuncMapping { kotlin: "readlnOrNull", cangjie: "Console.stdIn.readln" },
    GlobalFuncMapping { kotlin: "readln", cangjie: "Console.stdIn.readln" },
    GlobalFuncMapping { kotlin: "require", cangjie: "assert" },
    GlobalFuncMapping { kotlin: "check", cangjie: "assert" },
    GlobalFuncMapping { kotlin: "error", cangjie: "throw Exception" },
    GlobalFuncMapping { kotlin: "TODO", cangjie: "throw Exception" },
];

// ============ Import 映射 ============

pub static IMPORT_MAP: &[ImportMapping] = &[
    ImportMapping { kotlin_prefix: "kotlin.collections", cangjie_import: "import std.collection.*" },
    ImportMapping { kotlin_prefix: "kotlin.math", cangjie_import: "import std.math.*" },
    ImportMapping { kotlin_prefix: "kotlin.io", cangjie_import: "import std.io.*" },
    ImportMapping { kotlin_prefix: "kotlin.text", cangjie_import: "import std.convert.*" },
    ImportMapping { kotlin_prefix: "java.util", cangjie_import: "import std.collection.*" },
    ImportMapping { kotlin_prefix: "java.io", cangjie_import: "import std.io.*" },
    ImportMapping { kotlin_prefix: "java.lang", cangjie_import: "" },
];

// ============ 集合构造器映射 ============

pub struct CollCtorMapping {
    pub kotlin: &'static str,
    pub cangjie: &'static str,
    /// 是否需要显式泛型元素类型。
    pub needs_elem: bool,
}

pub static COLL_CTOR_MAP: &[CollCtorMapping] = &[
    CollCtorMapping { kotlin: "listOf", cangjie: "ArrayList", needs_elem: true },
    CollCtorMapping { kotlin: "mutableListOf", cangjie: "ArrayList", needs_elem: true },
    CollCtorMapping { kotlin: "arrayListOf", cangjie: "ArrayList", needs_elem: true },
    CollCtorMapping { kotlin: "setOf", cangjie: "HashSet", needs_elem: true },
    CollCtorMapping { kotlin: "mutableSetOf", cangjie: "HashSet", needs_elem: true },
    CollCtorMapping { kotlin: "hashSetOf", cangjie: "HashSet", needs_elem: true },
    CollCtorMapping { kotlin: "mapOf", cangjie: "HashMap", needs_elem: false },
    CollCtorMapping { kotlin: "mutableMapOf", cangjie: "HashMap", needs_elem: false },
    CollCtorMapping { kotlin: "hashMapOf", cangjie: "HashMap", needs_elem: false },
    CollCtorMapping { kotlin: "arrayOf", cangjie: "Array", needs_elem: true },
    CollCtorMapping { kotlin: "intArrayOf", cangjie: "Array<Int64>", needs_elem: false },
    CollCtorMapping { kotlin: "doubleArrayOf", cangjie: "Array<Float64>", needs_elem: false },
    CollCtorMapping { kotlin: "booleanArrayOf", cangjie: "Array<Bool>", needs_elem: false },
    CollCtorMapping { kotlin: "emptyList", cangjie: "ArrayList", needs_elem: true },
    CollCtorMapping { kotlin: "emptySet", cangjie: "HashSet", needs_elem: true },
    CollCtorMapping { kotlin: "emptyMap", cangjie: "HashMap", needs_elem: false },
];

// ============ 查询辅助函数 ============

/// 查找 Kotlin 类型对应的仓颉类型。
pub fn lookup_type(kotlin: &str) -> Option<&'static str> {
    TYPE_MAP.iter().find(|m| m.kotlin == kotlin).map(|m| m.cangjie)
}

/// 查找泛型容器类型。
pub fn lookup_generic_container(kotlin: &str) -> Option<&'static str> {
    GENERIC_CONTAINER_MAP.iter().find(|m| m.kotlin == kotlin).map(|m| m.cangjie)
}

/// 查找属性映射。
pub fn lookup_prop(kotlin: &str) -> Option<&'static str> {
    PROP_MAP.iter().find(|m| m.kotlin == kotlin).map(|m| m.cangjie)
}

/// 查找方法映射（指定接收者类型提示）。
pub fn lookup_method(kotlin: &str, receiver: &str) -> Option<&'static str> {
    METHOD_MAP
        .iter()
        .find(|m| m.kotlin == kotlin && (m.receiver == receiver || m.receiver == "any"))
        .map(|m| m.cangjie)
}

/// 查找全局函数映射。
pub fn lookup_global_func(kotlin: &str) -> Option<&'static str> {
    GLOBAL_FUNC_MAP.iter().find(|m| m.kotlin == kotlin).map(|m| m.cangjie)
}

/// 查找 import 映射。
pub fn lookup_import(kotlin_import: &str) -> Option<&'static str> {
    IMPORT_MAP
        .iter()
        .find(|m| kotlin_import.starts_with(m.kotlin_prefix))
        .map(|m| m.cangjie_import)
}

/// 查找集合构造器映射。
pub fn lookup_coll_ctor(kotlin: &str) -> Option<&'static CollCtorMapping> {
    COLL_CTOR_MAP.iter().find(|m| m.kotlin == kotlin)
}
