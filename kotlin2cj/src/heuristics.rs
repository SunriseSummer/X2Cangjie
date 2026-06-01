//! 类型启发式：粗略推断表达式的类型特征（字符串/字符/数值/集合/元组等），
//! 用于引导翻译引擎在语义歧义处做出正确选择。
//!
//! 这些启发式是 SOC 框架中「邻域信息聚合」的体现——每个节点不仅依据自身
//! 字面信息，还通过局部邻居（声明、初值、形参类型）的状态来推断自身语义，
//! 从而在翻译过程中实现「上下文感知」的涌现效果。

use crate::engine::Engine;
use crate::node::*;

impl Engine {
    // ============ 集合类型判定 ============

    /// 映射后的类型字符串是否为集合类型（用于判断能否套用集合高阶/聚合操作）。
    pub(crate) fn is_coll_type(t: &str) -> bool {
        let t = t.trim_start_matches('?');
        t.starts_with("ArrayList")
            || t.starts_with("HashSet")
            || t.starts_with("HashMap")
            || t.starts_with("Array<")
            || t == "Array"
    }

    /// 名为 `name` 的成员函数（自由函数或类方法）的返回类型是否为集合。
    pub(crate) fn func_ret_is_coll(&self, name: &str) -> bool {
        for node in &self.g.nodes {
            if let Kind::Func { name: fname, ret: Some(r), .. } = &node.kind {
                if fname == name {
                    return Self::is_coll_type(r);
                }
            }
        }
        false
    }

    /// 解析表达式的静态类名（对带声明类型的标识符，或由构造器初始化的变量有效）。
    pub(crate) fn expr_type_name(&self, id: NodeId) -> Option<String> {
        self.expr_type_name_depth(id, 0)
    }

    fn expr_type_name_depth(&self, id: NodeId, depth: usize) -> Option<String> {
        if depth > 10 { return None; } // Prevent deep recursion on long assignment chains
        if let Kind::NameRef { decl: Some(d), .. } = self.g.kind(id) {
            for node in &self.g.nodes {
                match &node.kind {
                    Kind::VarDecl { name_node, ty, init, .. } if name_node == d => {
                        if let Some(t) = ty {
                            return Some(t.clone());
                        }
                        if let Some(i) = init {
                            // Recurse: if init is a NameRef, propagate its type
                            if let Kind::NameRef { .. } = self.g.kind(*i) {
                                return self.expr_type_name_depth(*i, depth + 1);
                            }
                            if let Kind::Call { callee, .. } = self.g.kind(*i) {
                                if let Kind::NameRef { original, .. } = self.g.kind(*callee) {
                                    if self.is_class_name(original) {
                                        return Some(original.clone());
                                    }
                                }
                            }
                        }
                        return None;
                    }
                    Kind::Param { name_node, ty, .. } if name_node == d => {
                        return Some(ty.clone());
                    }
                    _ => {}
                }
            }
        }
        if let Kind::NameRef { original, .. } = self.g.kind(id) {
            if let Some(t) = self.field_type_by_name(original) {
                return Some(t);
            }
        }
        None
    }

    /// 表达式是否为可空类型（类型以 `?` 开头）。
    pub(crate) fn is_nullable_expr(&self, id: NodeId) -> bool {
        if let Some(ty) = self.expr_type_name(id) {
            return ty.starts_with('?');
        }
        false
    }

    /// 图中是否存在名为 `name` 的类声明。
    pub(crate) fn is_class_name(&self, name: &str) -> bool {
        self.g.nodes.iter().any(|n| matches!(&n.kind, Kind::Class { name: cn, .. } if cn == name))
    }

    /// 查找名为 `name` 的枚举声明，返回其所有枚举项名。
    pub(crate) fn enum_entries(&self, name: &str) -> Option<Vec<String>> {
        self.g.nodes.iter().find_map(|n| match &n.kind {
            Kind::Enum { name: en, entries } if en == name && !entries.is_empty() => {
                Some(entries.clone())
            }
            _ => None,
        })
    }

    /// 按字段名在所有类的主构造器参数中查找其（已映射的）类型。
    pub(crate) fn field_type_by_name(&self, name: &str) -> Option<String> {
        for node in &self.g.nodes {
            if let Kind::Class { ctor_params, .. } = &node.kind {
                for cp in ctor_params {
                    if cp.name == name && cp.kind != crate::node::CtorParamKind::Plain {
                        return Some(cp.ty.clone());
                    }
                }
            }
        }
        None
    }

    /// 图中是否存在名为 `name` 的用户函数声明。
    pub(crate) fn is_user_func(&self, name: &str) -> bool {
        self.g.nodes.iter().any(|n| matches!(&n.kind, Kind::Func { name: fname, .. } if fname == name))
    }

    /// 子树 `id` 中是否出现对标识符 `name` 的引用（用于识别递归函数）。
    pub(crate) fn refers_name(&self, id: NodeId, name: &str) -> bool {
        if let Kind::NameRef { original, .. } = self.g.kind(id) {
            if original == name {
                return true;
            }
        }
        self.g.children_of(id).iter().any(|c| self.refers_name(*c, name))
    }

    /// 块（递归）内是否存在对名为 `bind` 的变量的赋值。
    pub(crate) fn block_assigns(&self, id: NodeId, bind: &str) -> bool {
        if let Kind::Assign { target, .. } = self.g.kind(id) {
            if let Kind::NameRef { original, .. } = self.g.kind(*target) {
                if crate::parser::safe_name(original) == bind {
                    return true;
                }
            }
        }
        self.g.children_of(id).iter().any(|c| self.block_assigns(*c, bind))
    }

    /// 识别 `name != null` / `name == null` 形式的空值判定。
    pub(crate) fn null_check(&self, cond: NodeId) -> Option<(String, String, bool)> {
        if let Kind::Binary { op, lhs, rhs } = self.g.kind(cond) {
            if op != "==" && op != "!=" {
                return None;
            }
            let is_null = |id: NodeId| matches!(self.g.kind(id), Kind::Raw(s) if s == "None");
            let name_side = if is_null(*rhs) {
                Some(*lhs)
            } else if is_null(*lhs) {
                Some(*rhs)
            } else {
                None
            }?;
            if let Kind::NameRef { original, .. } = self.g.kind(name_side) {
                let bind = crate::parser::safe_name(original);
                let recv = self.atom(name_side)?;
                return Some((bind, recv, op == "=="));
            }
        }
        None
    }

    // ============ 集合分析 ============

    /// 成员字段 `base.field` 是否为集合类型。
    pub(crate) fn member_is_collection(&self, base: NodeId, field: &str) -> bool {
        let cn = match self.expr_type_name(base) {
            Some(t) => t.trim_start_matches('?').to_string(),
            None => return false,
        };
        for node in &self.g.nodes {
            if let Kind::Class { name, ctor_params, members, .. } = &node.kind {
                if *name != cn {
                    continue;
                }
                for p in ctor_params {
                    if p.name == field {
                        return Self::is_coll_type(&p.ty);
                    }
                }
                for m in members {
                    if let Kind::VarDecl { name_node, ty, init, .. } = self.g.kind(*m) {
                        if let Kind::Name { original } = self.g.kind(*name_node) {
                            if original == field {
                                if let Some(t) = ty {
                                    return Self::is_coll_type(t);
                                }
                                if let Some(i) = init {
                                    return self.looks_collection(*i);
                                }
                            }
                        }
                    }
                }
            }
        }
        false
    }

    /// 启发式判断表达式是否求值为集合。
    pub(crate) fn looks_collection(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::CollLit { .. } | Kind::Range { .. } => true,
            Kind::Call { callee, .. } => {
                if let Kind::Member { base, name, .. } = self.g.kind(*callee) {
                    if matches!(
                        name.as_str(),
                        "map" | "filter" | "sorted" | "sortedBy" | "sortedDescending"
                            | "sortedByDescending" | "reversed" | "toList" | "toMutableList"
                            | "split" | "keys" | "values" | "toCharArray"
                    ) {
                        return true;
                    }
                    return self.func_ret_is_coll(name) || self.member_is_collection(*base, name);
                }
                if let Kind::NameRef { original, .. } = self.g.kind(*callee) {
                    return self.func_ret_is_coll(original);
                }
                false
            }
            Kind::NameRef { decl: Some(d), .. } => {
                for node in &self.g.nodes {
                    match &node.kind {
                        Kind::VarDecl { name_node, ty, init, .. } if name_node == d => {
                            if let Some(t) = ty {
                                return Self::is_coll_type(t);
                            }
                            if let Some(i) = init {
                                return self.looks_collection(*i);
                            }
                            return false;
                        }
                        Kind::Param { name_node, ty, .. } if name_node == d => {
                            return Self::is_coll_type(ty);
                        }
                        _ => {}
                    }
                }
                false
            }
            Kind::Member { base, name, .. } => self.member_is_collection(*base, name),
            _ => false,
        }
    }

    /// 成员字段的集合判定（三值）：Some(true)=集合、Some(false)=非集合、None=无法判定。
    pub(crate) fn member_field_collection(&self, base: NodeId, field: &str) -> Option<bool> {
        let cn = self.expr_type_name(base)?;
        let cn = cn.trim_start_matches('?').to_string();
        for node in &self.g.nodes {
            if let Kind::Class { name, ctor_params, members, .. } = &node.kind {
                if *name != cn {
                    continue;
                }
                for p in ctor_params {
                    if p.name == field {
                        return Some(Self::is_coll_type(&p.ty));
                    }
                }
                for m in members {
                    if let Kind::VarDecl { name_node, ty, init, .. } = self.g.kind(*m) {
                        if let Kind::Name { original } = self.g.kind(*name_node) {
                            if original == field {
                                if let Some(t) = ty {
                                    return Some(Self::is_coll_type(t));
                                }
                                if let Some(i) = init {
                                    return Some(self.looks_collection(*i));
                                }
                            }
                        }
                    }
                }
            }
        }
        None
    }

    /// 接收者是否「可证明为非集合」：仅当能解析出确定的非集合类型时为真。
    pub(crate) fn provably_non_collection(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::CollLit { .. } | Kind::Range { .. } => return false,
            Kind::IntLit(_) | Kind::FloatLit(_) | Kind::BoolLit(_)
            | Kind::CharLit(_) | Kind::StrTemplate { .. } => return true,
            Kind::Member { base, name, .. } => {
                match self.member_field_collection(*base, name) {
                    Some(is_coll) => return !is_coll,
                    None => return false,
                }
            }
            Kind::Call { callee, .. } => {
                if let Kind::NameRef { original, .. } = self.g.kind(*callee) {
                    if self.is_class_name(original) {
                        return true;
                    }
                    if self.func_ret_is_coll(original) {
                        return false;
                    }
                }
                return false;
            }
            Kind::NameRef { decl: Some(d), .. } => {
                let d = *d;
                for node in &self.g.nodes {
                    match &node.kind {
                        Kind::VarDecl { name_node, ty, init, .. } if *name_node == d => {
                            if let Some(t) = ty {
                                return !Self::is_coll_type(t);
                            }
                            if let Some(i) = init {
                                return self.provably_non_collection(*i);
                            }
                            return false;
                        }
                        Kind::Param { name_node, ty, .. } if *name_node == d => {
                            return !Self::is_coll_type(ty);
                        }
                        _ => {}
                    }
                }
                false
            }
            _ => false,
        }
    }

    // ============ 字符/字符串/数值 类型推断 ============

    /// 粗略判断表达式是否为字符（Rune）类型。
    pub(crate) fn looks_char(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::CharLit(_) => true,
            Kind::Index { base, .. } => self.looks_string(*base),
            Kind::NameRef { decl: Some(d), .. } => {
                let d = *d;
                for node in &self.g.nodes {
                    if let Kind::ForEach { var, iter, .. } = &node.kind {
                        if let Kind::VarDecl { name_node, .. } = self.g.kind(*var) {
                            if *name_node == d && self.looks_string(*iter) {
                                return true;
                            }
                        }
                    }
                    if let Kind::Param { name_node, ty, .. } = &node.kind {
                        if *name_node == d {
                            return ty == "Char" || ty == "Rune";
                        }
                    }
                    if let Kind::VarDecl { name_node, ty, init, .. } = &node.kind {
                        if *name_node == d {
                            if let Some(t) = ty {
                                return t == "Char" || t == "Rune";
                            }
                            if let Some(i) = init {
                                return matches!(self.g.kind(*i), Kind::CharLit(_))
                                    || matches!(self.g.kind(*i), Kind::Index { base, .. } if self.looks_string(*base));
                            }
                        }
                    }
                }
                false
            }
            Kind::NameRef { original, .. } => {
                matches!(self.field_type_by_name(original).as_deref(), Some("Char") | Some("Rune"))
            }
            _ => false,
        }
    }

    /// 启发式判断表达式是否为字符串。
    pub(crate) fn looks_string(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::StrTemplate { .. } => true,
            Kind::Binary { op, lhs, rhs } if op == "+" => {
                self.looks_string(*lhs) || self.looks_string(*rhs)
            }
            Kind::Call { callee, .. } => {
                if let Kind::Member { name, base, .. } = self.g.kind(*callee) {
                    matches!(
                        name.as_str(),
                        "toString" | "substring" | "joinToString" | "trim" | "trimStart"
                            | "trimEnd" | "uppercase" | "lowercase" | "toUpperCase"
                            | "toLowerCase" | "replace" | "padStart" | "padEnd" | "repeat"
                            | "reversed"
                    ) && (matches!(name.as_str(), "toString" | "joinToString")
                        || self.looks_string(*base))
                } else {
                    false
                }
            }
            Kind::NameRef { decl: Some(d), .. } => {
                let d = *d;
                for node in &self.g.nodes {
                    if let Kind::ForEach { var, iter, .. } = &node.kind {
                        if let Kind::VarDecl { name_node, .. } = self.g.kind(*var) {
                            if *name_node == d && self.iter_elem_is_string(*iter) {
                                return true;
                            }
                        }
                    }
                }
                for node in &self.g.nodes {
                    match &node.kind {
                        Kind::VarDecl { name_node, ty, init, .. } if *name_node == d => {
                            if let Some(t) = ty {
                                return t == "String";
                            }
                            if let Some(i) = init {
                                return self.looks_string(*i);
                            }
                            return false;
                        }
                        Kind::Param { name_node, ty, .. } if *name_node == d => {
                            return ty == "String";
                        }
                        _ => {}
                    }
                }
                false
            }
            Kind::NameRef { original, .. } => {
                self.field_type_by_name(original).as_deref() == Some("String")
            }
            _ => false,
        }
    }

    /// 迭代源 `iter` 的元素是否为字符串。
    pub(crate) fn iter_elem_is_string(&self, iter: NodeId) -> bool {
        match self.g.kind(iter) {
            Kind::CollLit { elem, args, .. } => {
                if let Some(e) = elem {
                    if e == "String" {
                        return true;
                    }
                }
                args.first().map_or(false, |a| self.looks_string(*a))
            }
            Kind::NameRef { decl: Some(d), .. } => {
                let d = *d;
                for node in &self.g.nodes {
                    if let Kind::VarDecl { name_node, init: Some(i), .. } = &node.kind {
                        if *name_node == d {
                            return self.iter_elem_is_string(*i);
                        }
                    }
                }
                false
            }
            _ => false,
        }
    }

    /// 粗略判断表达式是否为数值类型。
    pub(crate) fn looks_numeric(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::IntLit(_) | Kind::FloatLit(_) => true,
            Kind::Unary { expr, .. } => self.looks_numeric(*expr),
            Kind::Binary { op, .. } => matches!(op.as_str(), "+" | "-" | "*" | "/" | "%"),
            Kind::Member { name, .. } => matches!(name.as_str(), "size" | "length"),
            Kind::Call { callee, .. } => {
                if let Kind::Member { name, .. } = self.g.kind(*callee) {
                    matches!(
                        name.as_str(),
                        "sum" | "sumOf" | "count" | "size" | "length"
                            | "max" | "min" | "toInt" | "toLong" | "toDouble" | "toFloat"
                    )
                } else if let Kind::NameRef { original, .. } = self.g.kind(*callee) {
                    if matches!(original.as_str(), "maxOf" | "minOf") {
                        return true;
                    }
                    self.g.nodes.iter().any(|n| matches!(&n.kind,
                        Kind::Func { name: fname, ret: Some(r), .. }
                            if fname == original && (r == "Int64" || r == "Float64")))
                } else {
                    false
                }
            }
            Kind::NameRef { decl: Some(d), .. } => {
                if let Kind::Name { .. } = self.g.kind(*d) {
                    self.decl_is_numeric(*d)
                } else {
                    false
                }
            }
            _ => false,
        }
    }

    /// 启发式判断表达式是否为浮点数。
    pub(crate) fn looks_float(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::FloatLit(_) => true,
            Kind::Unary { expr, .. } => self.looks_float(*expr),
            Kind::Binary { op, lhs, rhs } => {
                matches!(op.as_str(), "+" | "-" | "*" | "/" | "%")
                    && (self.looks_float(*lhs) || self.looks_float(*rhs))
            }
            Kind::Call { callee, .. } => {
                if let Kind::Member { name, .. } = self.g.kind(*callee) {
                    matches!(name.as_str(), "toDouble" | "toFloat")
                } else if let Kind::NameRef { original, .. } = self.g.kind(*callee) {
                    original == "Float64" || original == "Float32"
                } else {
                    false
                }
            }
            Kind::NameRef { decl: Some(d), .. } => {
                if let Kind::Name { .. } = self.g.kind(*d) {
                    self.decl_is_float(*d)
                } else {
                    false
                }
            }
            _ => false,
        }
    }

    /// 启发式判断表达式是否为元组。
    pub(crate) fn looks_tuple(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::Binary { op, .. } => op == "to",
            Kind::Call { callee, .. } => {
                matches!(self.g.kind(*callee), Kind::NameRef { original, .. } if original == "Pair" || original == "Triple")
            }
            Kind::NameRef { decl: Some(d), .. } => {
                for node in &self.g.nodes {
                    match &node.kind {
                        Kind::VarDecl { name_node, ty, init, .. }
                            if name_node == d && (ty.is_some() || init.is_some()) =>
                        {
                            if let Some(t) = ty {
                                return t.trim_start_matches('?').starts_with('(');
                            }
                            if let Some(i) = init {
                                return self.looks_tuple(*i);
                            }
                            return false;
                        }
                        Kind::Param { name_node, ty, .. } if name_node == d => {
                            return ty.trim_start_matches('?').starts_with('(');
                        }
                        Kind::ForEach { var, iter, .. } => {
                            if let Kind::VarDecl { name_node, .. } = self.g.kind(*var) {
                                if name_node == d && self.elem_looks_tuple(*iter) {
                                    return true;
                                }
                            }
                        }
                        _ => {}
                    }
                }
                false
            }
            _ => false,
        }
    }

    /// 判断某可迭代表达式的元素是否为元组。
    pub(crate) fn elem_looks_tuple(&self, iter: NodeId) -> bool {
        match self.g.kind(iter) {
            Kind::CollLit { args, .. } => {
                args.first().map(|a| self.looks_tuple(*a)).unwrap_or(false)
            }
            Kind::Call { callee, args } => {
                if matches!(self.g.kind(*callee), Kind::NameRef { original, .. }
                    if original == "listOf" || original == "mutableListOf" || original == "arrayListOf")
                {
                    return args.first().map(|a| self.looks_tuple(*a)).unwrap_or(false);
                }
                false
            }
            Kind::NameRef { decl: Some(d), .. } => {
                for node in &self.g.nodes {
                    if let Kind::VarDecl { name_node, init: Some(i), .. } = &node.kind {
                        if name_node == d {
                            return self.elem_looks_tuple(*i);
                        }
                    }
                }
                false
            }
            _ => false,
        }
    }

    /// 检查某 Name 节点所属声明是否为浮点类型。
    pub(crate) fn decl_is_float(&self, name_node: NodeId) -> bool {
        for node in &self.g.nodes {
            match &node.kind {
                Kind::VarDecl { name_node: nn, ty: Some(t), .. } if *nn == name_node => {
                    return t == "Float64" || t == "Float32";
                }
                Kind::VarDecl { name_node: nn, ty: None, init: Some(i), .. } if *nn == name_node => {
                    return self.looks_float(*i);
                }
                Kind::Param { name_node: nn, ty, .. } if *nn == name_node => {
                    return ty == "Float64" || ty == "Float32";
                }
                _ => {}
            }
        }
        false
    }

    /// 检查某 Name 节点所属声明的类型是否为数值类型。
    pub(crate) fn decl_is_numeric(&self, name_node: NodeId) -> bool {
        for node in &self.g.nodes {
            match &node.kind {
                Kind::VarDecl { name_node: nn, ty: Some(t), .. } if *nn == name_node => {
                    return t == "Int64" || t == "Float64";
                }
                Kind::VarDecl { name_node: nn, ty: None, init: Some(i), .. } if *nn == name_node => {
                    return self.looks_numeric(*i);
                }
                Kind::Param { name_node: nn, ty, .. } if *nn == name_node => {
                    return ty == "Int64" || ty == "Float64";
                }
                _ => {}
            }
        }
        false
    }

    /// 判断子树中是否使用了隐式 lambda 参数 `it`。
    pub(crate) fn uses_it(&self, id: NodeId) -> bool {
        if let Kind::NameRef { original, .. } = self.g.kind(id) {
            if original == "it" {
                return true;
            }
        }
        for c in self.g.children_of(id) {
            if self.uses_it(c) {
                return true;
            }
        }
        false
    }
}
