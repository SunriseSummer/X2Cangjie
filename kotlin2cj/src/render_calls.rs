//! 调用渲染：成员方法调用的特殊映射与 API 翻译规则。
//!
//! 从 render.rs 中拆分出来，集中管理 Kotlin→仓颉 API 映射规则，
//! 提升代码可维护性。新增 API 映射规则只需修改本文件。

use crate::engine::Engine;
use crate::node::*;

impl Engine {
    // ============ 调用渲染 ============

    pub(crate) fn render_call(&self, callee: NodeId, args: &[NodeId]) -> Option<String> {
        if let Kind::NameRef { original, .. } = self.g.kind(callee) {
            if (original == "Pair" || original == "Triple") && args.len() >= 2 {
                let a: Vec<String> = args.iter().map(|x| self.t(*x)).collect::<Option<_>>()?;
                return Some(format!("({})", a.join(", ")));
            }
            if (original == "maxOf" || original == "minOf"
                || ((original == "max" || original == "min") && !self.is_user_func(original)))
                && args.len() == 2
            {
                let a = self.t(args[0])?;
                let b = self.t(args[1])?;
                let cmp = if original == "maxOf" || original == "max" { ">" } else { "<" };
                return Some(format!("(if ({} {} {}) {{ {} }} else {{ {} }})", a, cmp, b, a, b));
            }
            if original == "abs" && args.len() == 1 && !self.is_user_func(original) {
                let a = self.atom(args[0])?;
                return Some(format!("(if ({} < 0) {{ -({}) }} else {{ {} }})", a, a, a));
            }
            if (original == "Array" || original == "IntArray" || original == "BooleanArray"
                || original == "DoubleArray" || original == "LongArray")
                && args.len() == 2
            {
                if let Kind::Lambda { params, body } = self.g.kind(args[1]) {
                    let n = self.t(args[0])?;
                    let inner = self.render_block_inner(*body, 0)?;
                    let pname = if let Some(p) = params.first() {
                        crate::parser::safe_name(p.split(':').next().unwrap_or(p).trim())
                    } else if self.uses_it(*body) {
                        "it".to_string()
                    } else {
                        "_idx".to_string()
                    };
                    let body_str = if inner.lines().count() <= 1 {
                        inner.trim().to_string()
                    } else {
                        format!("\n{}\n", crate::render::indent(&inner, 1))
                    };
                    return Some(format!("Array({}, {{ {} => {} }})", n, pname, body_str));
                }
            }
        }
        if let Kind::Member { base, name, .. } = self.g.kind(callee) {
            if let Some(result) = self.render_member_call(*base, name, args) {
                return Some(result);
            }
        }
        let c = self.atom(callee)?;
        if let Kind::NameRef { original, .. } = self.g.kind(callee) {
            if let Some(named) = self.fn_named_params(original) {
                let mut a = Vec::with_capacity(args.len());
                for (i, x) in args.iter().enumerate() {
                    let s = self.t(*x)?;
                    match named.get(i) {
                        Some((pname, true)) => a.push(format!("{}: {}", pname, s)),
                        _ => a.push(s),
                    }
                }
                return Some(format!("{}({})", c, a.join(", ")));
            }
        }
        let a: Vec<String> = args.iter().map(|x| self.t(*x)).collect::<Option<_>>()?;
        Some(format!("{}({})", c, a.join(", ")))
    }

    /// 成员方法调用的特殊映射，返回 None 表示无特殊处理。
    fn render_member_call(&self, base: NodeId, name: &str, args: &[NodeId]) -> Option<String> {
        // 枚举 values()
        if name == "values" && args.is_empty() {
            if let Kind::NameRef { original, .. } = self.g.kind(base) {
                if let Some(entries) = self.enum_entries(original) {
                    let items: Vec<String> = entries
                        .iter()
                        .map(|e| format!("{}.{}", original, e))
                        .collect();
                    return Some(format!("[{}]", items.join(", ")));
                }
            }
        }
        let b = self.atom(base)?;
        match name {
            // ---- Char 方法 ----
            "isDigit" | "isLetter" | "isWhitespace" | "isUpperCase" | "isLowerCase"
                if args.is_empty() && self.looks_char(base) =>
            {
                let m = match name {
                    "isDigit" => "isAsciiNumber",
                    "isLetter" => "isAsciiLetter",
                    "isWhitespace" => "isAsciiWhiteSpace",
                    "isUpperCase" => "isAsciiUpperCase",
                    _ => "isAsciiLowerCase",
                };
                Some(format!("{}.{}()", b, m))
            }
            "isLetterOrDigit" if args.is_empty() && self.looks_char(base) => {
                Some(format!(
                    "({}.isAsciiLetter() || {}.isAsciiNumber())",
                    b, b
                ))
            }
            "toChar" if args.is_empty() => {
                Some(format!("Rune(UInt32({}))", b))
            }

            // ---- String 方法 ----
            "padStart" | "padEnd" if self.looks_string(base) && (args.len() == 1 || args.len() == 2) => {
                let width = self.t(args[0])?;
                let pad = if args.len() == 2 {
                    if let Kind::CharLit(c) = self.g.kind(args[1]) {
                        format!("\"{}\"", c)
                    } else {
                        format!("({}).toString()", self.t(args[1])?)
                    }
                } else {
                    "\" \"".to_string()
                };
                Some(format!("{}.{}({}, padding: {})", b, name, width, pad))
            }
            "indexOf" if args.len() == 1 && self.looks_string(base) => {
                let needle = if let Kind::CharLit(c) = self.g.kind(args[0]) {
                    format!("\"{}\"", c)
                } else {
                    self.t(args[0])?
                };
                Some(format!("({}.indexOf({}) ?? -1)", b, needle))
            }
            "startsWith" if args.len() == 1 && self.looks_string(base) => {
                let needle = if let Kind::CharLit(c) = self.g.kind(args[0]) {
                    format!("\"{}\"", c)
                } else {
                    self.t(args[0])?
                };
                Some(format!("{}.startsWith({})", b, needle))
            }
            "endsWith" if args.len() == 1 && self.looks_string(base) => {
                let needle = if let Kind::CharLit(c) = self.g.kind(args[0]) {
                    format!("\"{}\"", c)
                } else {
                    self.t(args[0])?
                };
                Some(format!("{}.endsWith({})", b, needle))
            }
            "contains" if args.len() == 1 && self.looks_string(base) => {
                let needle = if let Kind::CharLit(c) = self.g.kind(args[0]) {
                    format!("\"{}\"", c)
                } else {
                    self.t(args[0])?
                };
                Some(format!("{}.contains({})", b, needle))
            }
            "replace" if args.len() == 2 && self.looks_string(base) => {
                let old_str = if let Kind::CharLit(c) = self.g.kind(args[0]) {
                    format!("\"{}\"", c)
                } else {
                    self.t(args[0])?
                };
                let new_str = if let Kind::CharLit(c) = self.g.kind(args[1]) {
                    format!("\"{}\"", c)
                } else {
                    self.t(args[1])?
                };
                Some(format!("{}.replace({}, {})", b, old_str, new_str))
            }
            "split" if args.len() == 1 && self.looks_string(base) => {
                let delim = if let Kind::CharLit(c) = self.g.kind(args[0]) {
                    format!("\"{}\"", c)
                } else {
                    self.t(args[0])?
                };
                Some(format!("collectArrayList({}.split({}).iterator())", b, delim))
            }
            "substring" if args.len() == 2 => {
                Some(format!("{}[{}..{}]", b, self.t(args[0])?, self.t(args[1])?))
            }
            "substring" if args.len() == 1 => {
                Some(format!("{}[{}..]", b, self.t(args[0])?))
            }
            "repeat" if args.len() == 1 && self.looks_string(base) => {
                Some(format!("({} * {})", b, self.atom(args[0])?))
            }
            "take" if args.len() == 1 && self.looks_string(base) => {
                Some(format!("{}[0..{}]", b, self.t(args[0])?))
            }
            "drop" if args.len() == 1 && self.looks_string(base) => {
                Some(format!("{}[{}..{}.size]", b, self.t(args[0])?, b))
            }
            "reversed" if args.is_empty() && self.looks_string(base) => {
                Some(format!(
                    "({{ => let _r = {}.toRuneArray(); String(Array<Rune>(_r.size, {{j => _r[_r.size - 1 - j]}})) }})()",
                    b
                ))
            }

            // ---- 集合通用方法 ----
            "isEmpty" if args.is_empty() && self.looks_string_builder(base) => {
                Some(format!("({}.toString().size == 0)", b))
            }
            "isNotEmpty" if args.is_empty() && self.looks_string_builder(base) => {
                Some(format!("({}.toString().size > 0)", b))
            }
            "removeAt" if args.len() == 1 => {
                Some(format!("{}.remove(at: {})", b, self.t(args[0])?))
            }
            "addAll" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!("{}.add(all: {})", b, self.t(args[0])?))
            }
            "containsKey" if args.len() == 1 => {
                Some(format!("{}.contains({})", b, self.t(args[0])?))
            }
            "clear" if args.is_empty() => {
                Some(format!("{}.reset()", b))
            }
            "getOrDefault" if args.len() == 2 => {
                Some(format!("({}.get({}) ?? {})", b, self.t(args[0])?, self.t(args[1])?))
            }
            "getOrPut" if args.len() == 2 => {
                let key = self.t(args[0])?;
                let default_lam = self.t(args[1])?;
                Some(format!(
                    "({{ => if ({b}.contains({key})) {{ {b}[{key}] }} else {{ let _v = ({default_lam})(); {b}[{key}] = _v; _v }} }})()",
                    b = b, key = key, default_lam = default_lam
                ))
            }
            "isNotEmpty" if args.is_empty() => {
                if self.looks_string_builder(base) {
                    Some(format!("({}.toString().size > 0)", b))
                } else {
                    Some(format!("!({}.isEmpty())", b))
                }
            }
            "first" if args.is_empty() => {
                Some(format!("{}[0]", b))
            }
            "last" if args.is_empty() => {
                Some(format!("{}[{}.size - 1]", b, b))
            }
            "firstOrNull" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("{}.get(0)", b))
            }
            "lastOrNull" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("{}.get({}.size - 1)", b, b))
            }

            // ---- 排序 ----
            "sort" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("sort({}, stable: true)", b))
            }
            "sortDescending" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("sort({}, stable: true, descending: true)", b))
            }
            "sortBy" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!("sort({}, key: {}, stable: true)", b, self.t(args[0])?))
            }
            "sortByDescending" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!("sort({}, key: {}, stable: true, descending: true)", b, self.t(args[0])?))
            }
            "sorted" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!(
                    "({{ => let _s = collectArrayList({}); sort(_s, stable: true); _s }})()",
                    self.as_iter(base)?
                ))
            }
            "sortedDescending" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!(
                    "({{ => let _s = collectArrayList({}); sort(_s, stable: true, descending: true); _s }})()",
                    self.as_iter(base)?
                ))
            }
            "sortedBy" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!(
                    "({{ => let _s = collectArrayList({}); sort(_s, key: {}, stable: true); _s }})()",
                    self.as_iter(base)?, self.t(args[0])?
                ))
            }
            "sortedByDescending" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!(
                    "({{ => let _s = collectArrayList({}); sort(_s, key: {}, stable: true, descending: true); _s }})()",
                    self.as_iter(base)?, self.t(args[0])?
                ))
            }

            // ---- 函数式集合操作 ----
            "withIndex" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("{}.iterator().enumerate()", b))
            }
            "map" | "filter" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!(
                    "collectArrayList({}.{}({}))",
                    self.as_iter(base)?, name, self.t(args[0])?
                ))
            }
            "flatMap" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!(
                    "collectArrayList({}.flatMap({{ _e => ({})(_e).iterator() }}))",
                    self.as_iter(base)?, self.t(args[0])?
                ))
            }
            "any" | "all" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!("{}.{}({})", self.as_iter(base)?, name, self.t(args[0])?))
            }
            "none" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!("!{}.any({})", self.as_iter(base)?, self.t(args[0])?))
            }
            "count" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!("{}.filter({}).count()", self.as_iter(base)?, self.t(args[0])?))
            }
            "count" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("{}.size", b))
            }
            "sum" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("{}.fold<Int64>(0, {{acc, x => acc + x}})", self.as_iter(base)?))
            }
            "sumOf" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!(
                    "{}.map({}).fold<Int64>(0, {{acc, x => acc + x}})",
                    self.as_iter(base)?,
                    self.t(args[0])?
                ))
            }
            "fold" if args.len() == 2 && !self.provably_non_collection(base) => {
                let ty = self.lit_type(args[0]);
                Some(format!(
                    "{}.fold<{}>({}, {})",
                    self.as_iter(base)?,
                    ty,
                    self.t(args[0])?,
                    self.t(args[1])?
                ))
            }
            "reduce" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!("{}.reduce({}).getOrThrow()", self.as_iter(base)?, self.t(args[0])?))
            }
            "max" | "min" if args.is_empty() && !self.provably_non_collection(base) => {
                let cmp = if name == "max" { ">" } else { "<" };
                Some(format!(
                    "{}.reduce({{a, b => if (a {} b) {{ a }} else {{ b }}}}).getOrThrow()",
                    self.as_iter(base)?, cmp
                ))
            }
            "maxOrNull" | "minOrNull" if args.is_empty() && !self.provably_non_collection(base) => {
                let cmp = if name == "maxOrNull" { ">" } else { "<" };
                Some(format!(
                    "{}.reduce({{a, b => if (a {} b) {{ a }} else {{ b }}}})",
                    self.as_iter(base)?, cmp
                ))
            }
            "average" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!(
                    "(Float64({}.fold<Int64>(0, {{acc, x => acc + x}})) / Float64({}.count()))",
                    self.as_iter(base)?, self.as_iter(base)?
                ))
            }
            "reversed" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!(
                    "({{ => let _s = collectArrayList({}); _s.reverse(); _s }})()",
                    self.as_iter(base)?
                ))
            }
            "take" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!(
                    "collectArrayList({}.take({}))",
                    self.as_iter(base)?, self.t(args[0])?
                ))
            }
            "drop" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!(
                    "collectArrayList({}.skip({}))",
                    self.as_iter(base)?, self.t(args[0])?
                ))
            }
            "toList" | "toMutableList" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("collectArrayList({})", self.atom(base)?))
            }
            "distinct" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!(
                    "({{ => let _hs = HashSet<Int64>(); let _r = ArrayList<Int64>(); for (_e in {}) {{ if (!_hs.contains(_e)) {{ _hs.put(_e); _r.append(_e) }} }}; _r }})()",
                    self.atom(base)?
                ))
            }
            "joinToString" if !self.provably_non_collection(base) => {
                self.render_join_to_string(base, &b, args)
            }

            // ---- HashMap 特有操作 ----
            "groupBy" if args.len() == 1 && !self.provably_non_collection(base) => {
                let key_fn = self.t(args[0])?;
                Some(format!(
                    "({{ => let _m = HashMap<Int64, ArrayList<Int64>>(); for (_e in {}) {{ let _k = ({})(_e); if (!_m.contains(_k)) {{ _m[_k] = ArrayList<Int64>() }}; _m[_k].append(_e) }}; _m }})()",
                    self.atom(base)?, key_fn
                ))
            }
            "associate" if args.len() == 1 && !self.provably_non_collection(base) => {
                let pair_fn = self.t(args[0])?;
                Some(format!(
                    "({{ => let _m = HashMap<Int64, Int64>(); for (_e in {}) {{ let _p = ({})(_e); _m[_p[0]] = _p[1] }}; _m }})()",
                    self.atom(base)?, pair_fn
                ))
            }

            // ---- 类型转换 ----
            "toInt" | "toLong" if args.is_empty() => {
                if self.looks_numeric(base) {
                    Some(format!("Int64({})", b))
                } else {
                    Some(format!("Int64.parse({})", b))
                }
            }
            "toDouble" | "toFloat" if args.is_empty() => {
                if self.looks_numeric(base) {
                    Some(format!("Float64({})", b))
                } else {
                    Some(format!("Float64.parse({})", b))
                }
            }
            "toString" if args.is_empty() => {
                Some(format!("{}.toString()", b))
            }

            _ => None,
        }
    }

    fn render_join_to_string(&self, base: NodeId, _b: &str, args: &[NodeId]) -> Option<String> {
        let has_lambda = args
            .last()
            .map(|a| matches!(self.g.kind(*a), Kind::Lambda { .. }))
            .unwrap_or(false);
        let sep = match args.first() {
            Some(a) if !(args.len() == 1 && has_lambda) => self.t(*a)?,
            _ => "\", \"".to_string(),
        };
        if has_lambda {
            let lam = self.t(*args.last().unwrap())?;
            return Some(format!(
                "String.join(collectArray<String>({}.map({})), delimiter: {})",
                self.as_iter(base)?,
                lam,
                sep
            ));
        }
        let joined = format!(
            "String.join(collectArray<String>({}.map({{e => e.toString()}})), delimiter: {})",
            self.as_iter(base)?, sep
        );
        if args.len() >= 2 {
            let prefix = self.t(args[1])?;
            let postfix = if args.len() >= 3 { self.t(args[2])? } else { "\"\"".to_string() };
            return Some(format!("({} + {} + {})", prefix, joined, postfix));
        }
        Some(joined)
    }
}
