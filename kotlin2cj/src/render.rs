//! 局部渲染规则：每个节点仅依据 *自身 + 子节点（邻居）已确定的目标片段*
//! 来计算自己的目标语言译文。这些规则是 SOC 框架中「局部崩塌/转换函数」
//! 的实现——节点状态变更触发邻居重新入队，形成沿语法/依赖边的级联传播。

use crate::engine::Engine;
use crate::node::*;

pub(crate) const IND: &str = "    ";

impl Engine {
    // ============ 基础工具 ============

    pub(crate) fn t(&self, id: NodeId) -> Option<String> {
        self.g.target(id).map(|s| s.to_string())
    }

    /// 若操作数本身是二元/区间表达式，加括号以保持优先级。
    pub(crate) fn atom(&self, id: NodeId) -> Option<String> {
        let s = self.t(id)?;
        let need = matches!(self.g.kind(id), Kind::Binary { .. } | Kind::Range { .. });
        if need {
            Some(format!("({})", s))
        } else {
            Some(s)
        }
    }

    // ============ 核心渲染 ============

    pub(crate) fn render(&self, id: NodeId) -> Option<String> {
        match self.g.kind(id).clone() {
            Kind::IntLit(s) => Some(s),
            Kind::FloatLit(s) => {
                if s.contains('.') || s.contains('e') || s.contains('E') {
                    Some(s)
                } else {
                    Some(format!("{}.0", s))
                }
            }
            Kind::BoolLit(b) => Some(if b { "true".into() } else { "false".into() }),
            Kind::CharLit(s) => Some(format!("r'{}'", s)),
            Kind::Raw(s) => Some(s),
            Kind::Name { original } => Some(crate::parser::safe_name(&original)),
            Kind::NameRef { original, decl } => match decl {
                Some(d) => self.t(d).or_else(|| Some(crate::parser::safe_name(&original))),
                None => Some(crate::parser::safe_name(&original)),
            },
            Kind::Unary { op, expr } => {
                let e = self.atom(expr)?;
                Some(format!("{}{}", op, e))
            }
            Kind::Binary { op, lhs, rhs } => self.render_binary(&op, lhs, rhs),
            Kind::Range { lo, hi, inclusive, down, step } => {
                let l = self.atom(lo)?;
                let h = self.atom(hi)?;
                let dots = if inclusive { "..=" } else { ".." };
                let stp = match step {
                    Some(s) => {
                        let sv = self.atom(s)?;
                        if down { format!(" : -{}", sv) } else { format!(" : {}", sv) }
                    }
                    None => {
                        if down { " : -1".to_string() } else { String::new() }
                    }
                };
                Some(format!("{}{}{}{}", l, dots, h, stp))
            }
            Kind::Index { base, index } => {
                let b = self.atom(base)?;
                let i = self.t(index)?;
                if self.looks_string(base) {
                    return Some(format!("{}.toRuneArray()[{}]", b, i));
                }
                Some(format!("{}[{}]", b, i))
            }
            Kind::Member { base, name, safe } => self.render_member(base, &name, safe),
            Kind::Call { callee, args } => self.render_call(callee, &args),
            Kind::CollLit { ctor, elem, args } => {
                if args.is_empty() {
                    match elem {
                        Some(e) => Some(format!("{}<{}>()", ctor, e)),
                        None => Some(format!("{}()", ctor)),
                    }
                } else {
                    let a: Vec<String> = args.iter().map(|x| self.t(*x)).collect::<Option<_>>()?;
                    match elem {
                        Some(e) => Some(format!("{}<{}>([{}])", ctor, e, a.join(", "))),
                        None => Some(format!("{}([{}])", ctor, a.join(", "))),
                    }
                }
            }
            Kind::Lambda { params, body } => {
                let inner = self.render_block_inner(body, 0)?;
                let head = if params.is_empty() {
                    if self.uses_it(body) {
                        "it =>".to_string()
                    } else {
                        "=>".to_string()
                    }
                } else {
                    let ps: Vec<String> = params
                        .iter()
                        .map(|p| match p.split_once(':') {
                            Some((n, t)) => format!("{}: {}", crate::parser::safe_name(n.trim()), t.trim()),
                            None => crate::parser::safe_name(p),
                        })
                        .collect();
                    format!("{} =>", ps.join(", "))
                };
                if inner.trim().is_empty() {
                    Some(format!("{{ {} }}", head))
                } else if inner.lines().count() <= 1 {
                    Some(format!("{{ {} {} }}", head, inner.trim()))
                } else {
                    Some(format!("{{ {}\n{}\n}}", head, indent(&inner, 1)))
                }
            }
            Kind::SafeLet { recv, var, body } => {
                let r = if let Kind::Index { base, index } = self.g.kind(recv) {
                    format!("{}.get({})", self.atom(*base)?, self.t(*index)?)
                } else {
                    self.atom(recv)?
                };
                let blk = self.render_block(body)?;
                Some(format!("if (let Some({}) <- {}) {}", crate::parser::safe_name(&var), r, blk))
            }
            Kind::StrTemplate { parts } => {
                let mut s = String::from("\"");
                for p in &parts {
                    match p {
                        TemplatePart::Lit(l) => s.push_str(l),
                        TemplatePart::Expr(e) => {
                            let et = self.t(*e)?;
                            s.push_str(&format!("${{{}}}", et));
                        }
                    }
                }
                s.push('"');
                Some(s)
            }

            // ---- 语句 ----
            Kind::ExprStmt { expr } => self.t(expr),
            Kind::Assign { target, op, value } => {
                let tt = self.t(target)?;
                let v = self.t(value)?;
                // String += Rune/non-string: convert RHS to string
                if op == "+=" && self.looks_string(target) && !self.looks_string(value) {
                    return Some(format!("{} += {}.toString()", tt, v));
                }
                // Float64 += / -= / *= / /= Int64: promote RHS to Float64
                if matches!(op.as_str(), "+=" | "-=" | "*=" | "/=")
                    && self.looks_float(target) && !self.looks_float(value)
                    && self.looks_numeric(value)
                {
                    return Some(format!("{} {} Float64({})", tt, op, v));
                }
                Some(format!("{} {} {}", tt, op, v))
            }
            Kind::Return { value } => match value {
                Some(v) => Some(format!("return {}", self.t(v)?)),
                None => Some("return".to_string()),
            },
            Kind::Throw { value } => Some(format!("throw {}", self.t(value)?)),
            Kind::VarDecl { mutable, name_node, ty, init, is_lazy } => {
                let name = self.t(name_node)?;
                if init.is_none() && ty.is_none() {
                    return Some(name);
                }
                let kw = if mutable { "var" } else { "let" };
                let tys = ty.map(|t| format!(": {}", t)).unwrap_or_default();
                match init {
                    Some(i) if is_lazy => {
                        // `by lazy { expr }` → Cangjie: `let x = { expr }()`
                        // (仓颉暂无 lazy 内置，用立即调用的 lambda 近似)
                        Some(format!("{} {}{} = {}", kw, name, tys, self.t(i)?))
                    }
                    Some(i) => Some(format!("{} {}{} = {}", kw, name, tys, self.t(i)?)),
                    None => Some(format!("{} {}{}", kw, name, tys)),
                }
            }
            Kind::If { cond, then_b, else_b } => self.render_if(cond, then_b, else_b),
            Kind::While { cond, body } => {
                Some(format!("while ({}) {}", self.t(cond)?, self.render_block(body)?))
            }
            Kind::DoWhile { body, cond } => {
                Some(format!("do {} while ({})", self.render_block(body)?, self.t(cond)?))
            }
            Kind::Repeat { count, body } => {
                let var = if self.uses_it(body) { "it" } else { "_" };
                Some(format!("for ({} in 0..{}) {}", var, self.atom(count)?, self.render_block(body)?))
            }
            Kind::Destructure { names } => {
                let ns: Vec<String> = names.iter().map(|n| self.t(*n)).collect::<Option<_>>()?;
                Some(format!("({})", ns.join(", ")))
            }
            Kind::DestructureDecl { mutable, names, init } => {
                let ns: Vec<String> = names.iter().map(|n| self.t(*n)).collect::<Option<_>>()?;
                let kw = if mutable { "var" } else { "let" };
                Some(format!("{} ({}) = {}", kw, ns.join(", "), self.t(init)?))
            }
            Kind::ForRange { var, range, body } => {
                let vn = self.loop_var_name(var)?;
                Some(format!("for ({} in {}) {}", vn, self.t(range)?, self.render_block(body)?))
            }
            Kind::ForEach { var, iter, body } => {
                let vn = self.loop_var_name(var)?;
                let it = if self.looks_string(iter) {
                    format!("{}.runes()", self.atom(iter)?)
                } else {
                    self.t(iter)?
                };
                // HashMap 解构遍历: for ((k, v) in map) → for ((k, v) in map)
                // 仓颉的 HashMap 遍历直接解构为 (key, value) 元组
                Some(format!("for ({} in {}) {}", vn, it, self.render_block(body)?))
            }
            Kind::Try { body, catches, finally } => {
                let mut s = format!("try {}", self.render_block(body)?);
                for c in &catches {
                    s.push_str(&format!(
                        " catch ({}: {}) {}",
                        c.name,
                        c.ty,
                        self.render_block(c.body)?
                    ));
                }
                if let Some(f) = finally {
                    s.push_str(&format!(" finally {}", self.render_block(f)?));
                }
                Some(s)
            }
            Kind::When { subject, arms } => self.render_when(subject, &arms),
            Kind::Block { .. } => self.render_block(id),
            Kind::IsCheck { expr, ty, negate } => {
                let e = self.atom(expr)?;
                if negate {
                    Some(format!("!({} is {})", e, ty))
                } else {
                    Some(format!("({} is {})", e, ty))
                }
            }
            Kind::TypePat { ty } => Some(format!("_: {}", ty)),

            // ---- 声明 ----
            Kind::Param { name_node, ty, default } => match default {
                Some(d) => Some(format!("{}!: {} = {}", self.t(name_node)?, ty, self.t(d)?)),
                None => Some(format!("{}: {}", self.t(name_node)?, ty)),
            },
            Kind::Func { name, params, ret, body, is_main, is_abstract, is_override, receiver_type, generic_params } => {
                self.render_func(id, &name, &params, ret, body, is_main, is_abstract, is_override, receiver_type.as_deref(), &generic_params)
            }
            Kind::Class { name, ctor_params, members, superclass, is_open, is_data, is_interface, is_abstract, interfaces, super_args, generics, init_block, companion_members, is_singleton } => {
                self.render_class(&name, &ctor_params, &members, superclass, is_open, is_data, is_interface, is_abstract, &interfaces, &super_args, &generics, init_block, &companion_members, is_singleton)
            }
            Kind::Enum { name, entries, params } => self.render_enum(&name, &entries, &params),
            Kind::TypeAlias { name, target_type } => {
                // Alias is expanded at parse time (parse_type); keep original as documentation comment
                Some(format!("// typealias {} = {}", name, target_type))
            }
            Kind::TypeCast { expr, ty, safe } => {
                let e = self.atom(expr)?;
                if safe {
                    // `as?` → try cast, return Option
                    Some(format!("(if ({} is {}) {{ {} as {} }} else {{ None }})", e, ty, e, ty))
                } else {
                    // `as` → direct cast
                    Some(format!("({} as {})", e, ty))
                }
            }
            Kind::Program { items } => self.render_program(&items),
            Kind::ForceUnwrap { expr } => {
                let e = self.t(expr)?;
                // Only emit .getOrThrow() for expressions that are genuinely Optional in Cangjie
                // HashMap/collection indexing already returns non-optional in Cangjie
                let is_map_index = matches!(self.g.kind(expr), Kind::Index { .. });
                if is_map_index {
                    return Some(e);
                }
                // Call expressions with !! always need unwrapping (user code knows the return is nullable)
                if matches!(self.g.kind(expr), Kind::Call { .. }) {
                    return Some(format!("{}.getOrThrow()", e));
                }
                // Member access on nullable fields
                if let Kind::Member { base, name, .. } = self.g.kind(expr) {
                    // Check if this member field is nullable in the class declaration
                    let field_nullable = self.is_nullable_member_field(*base, name);
                    if field_nullable {
                        return Some(format!("{}.getOrThrow()", e));
                    }
                    return Some(e);
                }
                // NameRef: check if the variable itself is nullable
                if self.is_nullable_expr(expr) {
                    Some(format!("{}.getOrThrow()", e))
                } else {
                    Some(e)
                }
            }
            Kind::InPat { .. } => None,
        }
    }

    // ============ 二元运算 ============

    fn render_binary(&self, op: &str, lhs: NodeId, rhs: NodeId) -> Option<String> {
        if op == "to" {
            let l = self.t(lhs)?;
            let r = self.t(rhs)?;
            return Some(format!("({}, {})", l, r));
        }
        if op == "?:" {
            let ra = self.atom(rhs)?;
            if let Kind::Index { base, index } = self.g.kind(lhs).clone() {
                let b = self.atom(base)?;
                let i = self.t(index)?;
                return Some(format!("{}.get({}) ?? {}", b, i, ra));
            }
            let la = self.atom(lhs)?;
            return Some(format!("{} ?? {}", la, ra));
        }
        if op == "in" || op == "!in" {
            let inner = self.render_in(lhs, rhs)?;
            return Some(if op == "!in" { format!("!({})", inner) } else { inner });
        }
        if op == "==" || op == "!=" {
            let lhs_null = matches!(self.g.kind(lhs), Kind::Raw(s) if s == "None");
            let rhs_null = matches!(self.g.kind(rhs), Kind::Raw(s) if s == "None");
            if lhs_null ^ rhs_null {
                let other = if lhs_null { rhs } else { lhs };
                let oa = self.atom(other)?;
                let m = if op == "==" { "isNone" } else { "isSome" };
                return Some(format!("{}.{}()", oa, m));
            }
        }
        let la = self.atom(lhs)?;
        let ra = self.atom(rhs)?;
        if (op == "+" || op == "+=") && (self.looks_string(lhs) || self.looks_string(rhs)) {
            let lc = if self.looks_string(lhs) { la.clone() } else { format!("{}.toString()", la) };
            let rc = if self.looks_string(rhs) { ra.clone() } else { format!("{}.toString()", ra) };
            return Some(format!("{} {} {}", lc, op, rc));
        }
        if matches!(op, "-" | "+")
            && self.looks_char(lhs)
            && self.looks_char(rhs)
        {
            return Some(format!(
                "(Int64(UInt32({})) {} Int64(UInt32({})))",
                la, op, ra
            ));
        }
        if matches!(op, "+" | "-")
            && self.looks_char(lhs)
            && !self.looks_char(rhs)
            && !self.looks_string(rhs)
        {
            return Some(format!(
                "Rune(UInt32(Int64(UInt32({})) {} {}))",
                la, op, ra
            ));
        }
        if matches!(op, "+" | "-" | "*" | "/" | "%" | ">" | "<" | ">=" | "<=" | "==" | "!=") {
            let lf = self.looks_float(lhs);
            let rf = self.looks_float(rhs);
            if lf && !rf && self.looks_numeric(rhs) {
                return Some(format!("{} {} Float64({})", la, op, ra));
            }
            if rf && !lf && self.looks_numeric(lhs) {
                return Some(format!("Float64({}) {} {}", la, op, ra));
            }
        }
        Some(format!("{} {} {}", la, op, ra))
    }

    // ============ 成员访问 ============

    fn render_member(&self, base: NodeId, name: &str, safe: bool) -> Option<String> {
        // super.method() → super.method() (no backtick escaping for super keyword)
        if let Kind::NameRef { original, .. } = self.g.kind(base) {
            if original == "`super`" || original == "super" {
                let mapped = match name {
                    "length" => "size",
                    other => other,
                };
                return Some(format!("super.{}", crate::parser::safe_name(mapped)));
            }
        }
        // Singleton object member access: `ObjectName.member` → `ObjectName.INSTANCE.member`
        if let Kind::NameRef { original, .. } = self.g.kind(base) {
            if self.is_singleton_object(original) {
                let mapped = match name {
                    "length" => "size",
                    other => other,
                };
                return Some(format!("{}.INSTANCE.{}", original, crate::parser::safe_name(mapped)));
            }
        }
        let (b, dot) = if safe {
            let bs = if let Kind::Index { base: ib, index } = self.g.kind(base) {
                format!("{}.get({})", self.atom(*ib)?, self.t(*index)?)
            } else {
                self.atom(base)?
            };
            (bs, "?.")
        } else {
            // Auto-unwrap nullable types: if base has type ?T, use .getOrThrow() before member access
            // Skip unwrap for variables that are rebound inside if-let null-check blocks
            let raw = self.atom(base)?;
            let b = if self.is_nullable_expr(base) && !self.is_null_check_rebound(base) {
                format!("{}.getOrThrow()", raw)
            } else {
                raw
            };
            (b, ".")
        };
        let mapped = match name {
            "length" => "size",
            "indices" if !safe => return Some(format!("(0..{}.size)", b)),
            "lastIndex" if !safe => return Some(format!("({}.size - 1)", b)),
            "code" if !safe && self.looks_char(base) => {
                return Some(format!("Int64(UInt32({}))", b));
            }
            "first" if !safe && (self.looks_tuple(base) || !self.provably_non_collection(base)) => return Some(format!("{}[0]", b)),
            "second" if !safe && (self.looks_tuple(base) || !self.provably_non_collection(base)) => return Some(format!("{}[1]", b)),
            "third" if !safe && (self.looks_tuple(base) || !self.provably_non_collection(base)) => return Some(format!("{}[2]", b)),
            "toUpperCase" | "uppercase" => "toAsciiUpper",
            "toLowerCase" | "lowercase" => "toAsciiLower",
            "trim" => "trimAscii",
            "trimStart" => "trimAsciiStart",
            "trimEnd" => "trimAsciiEnd",
            "keys" => return Some(format!("{}{}keys()", b, dot)),
            "values" => return Some(format!("{}{}values()", b, dot)),
            other => other,
        };
        Some(format!("{}{}{}", b, dot, crate::parser::safe_name(mapped)))
    }

    // ============ if 渲染 ============

    fn render_if(&self, cond: NodeId, then_b: NodeId, else_b: Option<NodeId>) -> Option<String> {
        if let Some((bind, recv, negated)) = self.null_check(cond) {
            let reassigned = self.block_assigns(then_b, &bind)
                || else_b.map_or(false, |e| self.block_assigns(e, &bind));
            if !reassigned {
                let tb = self.render_block(then_b)?;
                let head = format!("if (let Some({}) <- {})", bind, recv);
                if negated {
                    match else_b {
                        Some(e) => {
                            let eb = self.render_block(e)?;
                            return Some(format!("{} {} else {}", head, eb, tb));
                        }
                        None => {}
                    }
                } else {
                    match else_b {
                        Some(e) => {
                            let eb = self.render_block(e)?;
                            return Some(format!("{} {} else {}", head, tb, eb));
                        }
                        None => return Some(format!("{} {}", head, tb)),
                    }
                }
            }
        }
        let c = self.t(cond)?;
        let tb = self.render_block(then_b)?;
        match else_b {
            Some(e) => {
                let eb = if let Kind::Block { stmts } = self.g.kind(e) {
                    if stmts.len() == 1 && matches!(self.g.kind(stmts[0]), Kind::If { .. }) {
                        self.t(stmts[0])?
                    } else {
                        self.render_block(e)?
                    }
                } else {
                    self.render_block(e)?
                };
                Some(format!("if ({}) {} else {}", c, tb, eb))
            }
            None => Some(format!("if ({}) {}", c, tb)),
        }
    }

    // ============ 函数渲染 ============

    fn render_func(&self, id: NodeId, name: &str, params: &[NodeId], ret: Option<String>, body: NodeId, is_main: bool, is_abstract: bool, is_override: bool, receiver_type: Option<&str>, generic_params: &[String]) -> Option<String> {
        let ps: Vec<String> = params.iter().map(|p| self.t(*p)).collect::<Option<_>>()?;
        let gen_suffix = if generic_params.is_empty() {
            String::new()
        } else {
            format!("<{}>", generic_params.join(", "))
        };
        if is_main {
            let b = self.render_block(body)?;
            return Some(format!("main() {}", b));
        }
        // 扩展函数渲染为 extend ReceiverType { func name(...) { ... } }
        if let Some(recv_ty) = receiver_type {
            let r = match &ret {
                Some(r) => format!(": {}", r),
                None => String::new(),
            };
            let sig = format!("{}{}({}){}", name, gen_suffix, ps.join(", "), r);
            let b = self.render_block(body)?;
            let func_str = format!("func {} {}", sig, b);
            return Some(format!("extend {} {{\n{}\n}}", recv_ty, indent(&func_str, 1)));
        }
        let r = match &ret {
            Some(r) => format!(": {}", r),
            None if self.refers_name(body, name) => ": Unit".to_string(),
            None if is_abstract => ": Unit".to_string(),
            None if self.has_while_true_return(body) => ": Unit".to_string(),
            None => String::new(),
        };
        let sig = format!("{}{}({}){}", name, gen_suffix, ps.join(", "), r);
        if is_abstract {
            return Some(format!("public func {}", sig));
        }
        let mut b = self.render_block(body)?;
        // while(true) 返回修复：在 while(true) 后添加不可达默认返回以满足仓颉类型检查
        if self.has_while_true_return(body) && ret.is_some() {
            let ret_str = ret.as_ref().unwrap();
            let default_val = match ret_str.as_str() {
                "Int64" => "0",
                "Float64" => "0.0",
                "Bool" => "false",
                "String" => "\"\"",
                _ => "throw Exception(\"unreachable\")",
            };
            // Insert before the closing brace
            if b.ends_with('}') {
                b = format!("{}\n{}{}",
                    &b[..b.len()-1],
                    crate::render::IND,
                    format!("{}\n}}", default_val));
            }
        }
        // Determine visibility/open modifiers based on parent class context
        let in_open_class = self.func_in_open_class(id);
        let vis = if is_override && in_open_class {
            "public open override "
        } else if is_override {
            "public override "
        } else if in_open_class {
            "public open "
        } else {
            ""
        };
        Some(format!("{}func {} {}", vis, sig, b))
    }

    // ============ 类渲染 ============

    #[allow(clippy::too_many_arguments)]
    fn render_class(&self, name: &str, ctor_params: &[CtorParam], members: &[NodeId], superclass: Option<String>, is_open: bool, is_data: bool, is_interface: bool, is_abstract: bool, interfaces: &[String], super_args: &[NodeId], generics: &[String], init_block: Option<NodeId>, companion_members: &[NodeId], is_singleton: bool) -> Option<String> {
        let gen_suffix = if generics.is_empty() {
            String::new()
        } else {
            format!("<{}>", generics.join(", "))
        };
        let name_gen = format!("{}{}", name, gen_suffix);
        if is_interface {
            let mut ibody = String::new();
            for m in members {
                if let Kind::Func { name: fname, params, ret, .. } = self.g.kind(*m) {
                    let ps: Vec<String> =
                        params.iter().map(|p| self.t(*p)).collect::<Option<_>>()?;
                    let r = ret.clone().map(|r| format!(": {}", r)).unwrap_or_else(|| ": Unit".to_string());
                    ibody.push_str(&format!(
                        "{}func {}({}){}\n",
                        IND,
                        fname,
                        ps.join(", "),
                        r
                    ));
                }
            }
            let sup = if interfaces.is_empty() {
                String::new()
            } else {
                format!(" <: {}", interfaces.join(" & "))
            };
            if ibody.is_empty() {
                return Some(format!("interface {}{} {{}}", name_gen, sup));
            }
            return Some(format!("interface {}{} {{\n{}}}", name_gen, sup, ibody));
        }
        // object 单例 → class with private init + static instance
        if is_singleton {
            let mut sbody = String::new();
            sbody.push_str(&format!("{}private init() {{}}\n", IND));
            sbody.push_str(&format!("{}public static let INSTANCE = {}()\n", IND, name));
            for m in members {
                let mt = self.t(*m)?;
                sbody.push_str(&indent(&mt, 1));
                sbody.push('\n');
            }
            let mut ifaces: Vec<String> = Vec::new();
            if let Some(s) = &superclass {
                ifaces.push(s.clone());
            }
            ifaces.extend(interfaces.iter().cloned());
            // Auto-add ToString interface if object has a toString() method
            if !ifaces.contains(&"ToString".to_string()) {
                let has_to_string = members.iter().any(|&m| {
                    if let Kind::Func { name: fn_name, is_override, .. } = self.g.kind(m) {
                        fn_name == "toString" && *is_override
                    } else {
                        false
                    }
                });
                if has_to_string {
                    ifaces.push("ToString".to_string());
                }
            }
            let sup = if ifaces.is_empty() {
                String::new()
            } else {
                format!(" <: {}", ifaces.join(" & "))
            };
            return Some(format!("class {}{} {{\n{}}}", name_gen, sup, sbody));
        }
        let mut body = String::new();
        for p in ctor_params {
            match p.kind {
                CtorParamKind::Val => {
                    body.push_str(&format!("{}let {}: {}\n", IND, p.name, p.ty));
                }
                CtorParamKind::Var => {
                    body.push_str(&format!("{}var {}: {}\n", IND, p.name, p.ty));
                }
                CtorParamKind::Plain => {}
            }
        }
        let super_call: Option<String> = if super_args.is_empty() {
            None
        } else {
            let a: Vec<String> =
                super_args.iter().map(|x| self.t(*x)).collect::<Option<_>>()?;
            Some(format!("super({})", a.join(", ")))
        };
        if !ctor_params.is_empty() || super_call.is_some() || init_block.is_some() {
            let ps: Vec<String> = ctor_params
                .iter()
                .map(|p| {
                    if let Some(def_id) = p.default {
                        let def_val = self.t(def_id).unwrap_or_else(|| "None".to_string());
                        format!("{}!: {} = {}", p.name, p.ty, def_val)
                    } else {
                        format!("{}: {}", p.name, p.ty)
                    }
                })
                .collect();
            body.push_str(&format!("{}init({}) {{\n", IND, ps.join(", ")));
            if let Some(sc) = &super_call {
                body.push_str(&format!("{}{}{}\n", IND, IND, sc));
            }
            for p in ctor_params {
                if p.kind != CtorParamKind::Plain {
                    body.push_str(&format!("{}{}this.{} = {}\n", IND, IND, p.name, p.name));
                }
            }
            if let Some(ib) = init_block {
                if let Kind::Block { stmts } = self.g.kind(ib) {
                    for s in stmts {
                        let st = self.t(*s)?;
                        body.push_str(&indent(&st, 2));
                        body.push('\n');
                    }
                }
            }
            body.push_str(&format!("{}}}\n", IND));
        }
        for m in members {
            let mt = self.t(*m)?;
            // companion object 成员渲染为 static
            let is_companion = companion_members.contains(m);
            if is_companion {
                // 在函数声明前添加 static 修饰符
                // 注意：static 和 open 冲突，需去掉行首修饰符 open
                let mt_no_open = strip_modifier(&mt, "open");
                let static_mt = if mt_no_open.starts_with("func ") {
                    format!("static {}", mt_no_open)
                } else if mt_no_open.starts_with("public ") {
                    // 如果已有修饰符，在 func 前插入 static
                    mt_no_open.replacen("func ", "static func ", 1)
                } else {
                    format!("static {}", mt_no_open)
                };
                body.push_str(&indent(&static_mt, 1));
            } else {
                body.push_str(&indent(&mt, 1));
            }
            body.push('\n');
        }
        let has_user_tostring = members.iter().any(|m| {
            matches!(self.g.kind(*m), Kind::Func { name, .. } if name == "toString")
        });
        if is_data && !ctor_params.is_empty() && !has_user_tostring {
            let fields: Vec<String> = ctor_params
                .iter()
                .filter(|p| p.kind != CtorParamKind::Plain)
                .map(|p| format!("{}=${{this.{}}}", p.name, p.name))
                .collect();
            body.push_str(&format!(
                "{}public func toString(): String {{\n{}{}return \"{}({})\"\n{}}}\n",
                IND, IND, IND, name, fields.join(", "), IND
            ));
        }
        let kw = if is_abstract {
            "abstract class"
        } else if is_open {
            "open class"
        } else {
            "class"
        };
        let mut ifaces: Vec<String> = Vec::new();
        if let Some(s) = &superclass {
            ifaces.push(s.clone());
        }
        ifaces.extend(interfaces.iter().cloned());
        if is_data {
            ifaces.push("ToString".to_string());
        }
        // Auto-add ToString interface if class has a toString() method
        if !is_data && !ifaces.contains(&"ToString".to_string()) {
            let has_to_string = members.iter().any(|&m| {
                if let Kind::Func { name: fn_name, is_override, .. } = self.g.kind(m) {
                    fn_name == "toString" && *is_override
                } else {
                    false
                }
            });
            if has_to_string {
                ifaces.push("ToString".to_string());
            }
        }
        let sup = if ifaces.is_empty() {
            String::new()
        } else {
            format!(" <: {}", ifaces.join(" & "))
        };
        if body.is_empty() {
            Some(format!("{} {}{} {{}}", kw, name_gen, sup))
        } else {
            Some(format!("{} {}{} {{\n{}}}", kw, name_gen, sup, body))
        }
    }

    // ============ 枚举渲染 ============

    fn render_enum(&self, name: &str, entries: &[EnumEntry], params: &[CtorParam]) -> Option<String> {
        if entries.is_empty() {
            return Some(format!("enum {} {{ | {} }}", name, name));
        }

        // 无构造器参数的简单枚举
        if params.is_empty() {
            let body = entries.iter().map(|e| e.name.as_str()).collect::<Vec<_>>().join(" | ");
            let mut arms = String::new();
            for e in entries {
                arms.push_str(&format!("{}{}{}case {} => \"{}\"\n", IND, IND, IND, e.name, e.name));
            }
            return Some(format!(
                "@Derive[Equatable]\nenum {} <: ToString {{\n{}| {}\n{}public func toString(): String {{\n{}return match (this) {{\n{}{}}}\n{}}}\n}}",
                name, IND, body, IND, IND, IND, arms, IND
            ));
        }

        // 有构造器参数的枚举 → 仓颉: class + static let 模式
        // 使用 _ordinal 字段区分枚举项（即使构造参数值相同也能正确比较）
        let mut out = String::new();
        // 类声明
        out.push_str(&format!("class {} <: ToString & Equatable<{}> {{\n", name, name));
        // _ordinal 字段用于区分不同枚举项
        out.push_str(&format!("{}let _ordinal: Int64\n", IND));
        // 字段
        for p in params {
            let kw = if p.kind == CtorParamKind::Var { "var" } else { "let" };
            out.push_str(&format!("{}public {} {}: {}\n", IND, kw, p.name, p.ty));
        }
        // 构造器（增加 _ordinal 参数作为首个无名参数）
        let mut ps: Vec<String> = vec!["_ordinal: Int64".to_string()];
        ps.extend(params.iter().map(|p| format!("{}: {}", p.name, p.ty)));
        out.push_str(&format!("{}init({}) {{\n", IND, ps.join(", ")));
        out.push_str(&format!("{}{}this._ordinal = _ordinal\n", IND, IND));
        for p in params {
            out.push_str(&format!("{}{}this.{} = {}\n", IND, IND, p.name, p.name));
        }
        out.push_str(&format!("{}}}\n", IND));
        // 静态枚举常量（传入序号）
        for (i, e) in entries.iter().enumerate() {
            let args: Vec<String> = e.args.iter().map(|a| self.t(*a)).collect::<Option<_>>()?;
            out.push_str(&format!("{}public static let {} = {}({}, {})\n",
                IND, e.name, name, i, args.join(", ")));
        }
        // toString
        let mut arms = String::new();
        for e in entries {
            arms.push_str(&format!(
                "{}{}{}if (this == {}.{}) {{ return \"{}\" }}\n",
                IND, IND, IND, name, e.name, e.name
            ));
        }
        out.push_str(&format!(
            "{}public func toString(): String {{\n{}return \"{}(?)\"\n{}}}\n",
            IND, arms, name, IND
        ));
        // == operator（仅比较 _ordinal）
        out.push_str(&format!(
            "{}public operator func ==(rhs: {}): Bool {{\n",
            IND, name
        ));
        out.push_str(&format!("{}{}return this._ordinal == rhs._ordinal\n", IND, IND));
        out.push_str(&format!("{}}}\n", IND));
        // != operator
        out.push_str(&format!(
            "{}public operator func !=(rhs: {}): Bool {{\n",
            IND, name
        ));
        out.push_str(&format!("{}{}return !(this == rhs)\n", IND, IND));
        out.push_str(&format!("{}}}\n", IND));
        out.push_str("}");
        Some(out)
    }

    // ============ 块渲染 ============

    pub(crate) fn loop_var_name(&self, var: NodeId) -> Option<String> {
        if let Kind::VarDecl { name_node, .. } = self.g.kind(var) {
            self.t(*name_node)
        } else {
            self.t(var)
        }
    }

    pub(crate) fn render_block(&self, id: NodeId) -> Option<String> {
        let inner = self.render_block_inner(id, 0)?;
        if inner.trim().is_empty() {
            Some("{}".to_string())
        } else {
            Some(format!("{{\n{}\n}}", indent(&inner, 1)))
        }
    }

    pub(crate) fn render_block_inner(&self, id: NodeId, _d: usize) -> Option<String> {
        if let Kind::Block { stmts } = self.g.kind(id) {
            let mut lines = Vec::new();
            for s in stmts {
                lines.push(self.t(*s)?);
            }
            Some(lines.join("\n"))
        } else {
            self.t(id)
        }
    }

    // ============ when 渲染 ============

    fn render_when(&self, subject: Option<NodeId>, arms: &[WhenArm]) -> Option<String> {
        match subject {
            Some(subj) => {
                let needs_cond = arms.iter().any(|a| {
                    a.patterns.as_ref().map_or(false, |ps| {
                        ps.iter().any(|p| matches!(self.g.kind(*p), Kind::InPat { .. }))
                    })
                });
                if needs_cond {
                    return self.render_when_as_if(subj, arms);
                }
                let s = self.t(subj)?;
                let bind = if let Kind::NameRef { original, .. } = self.g.kind(subj) {
                    crate::parser::safe_name(original)
                } else {
                    "_".to_string()
                };
                let mut body = String::new();
                for a in arms {
                    let arm_body = self.render_arm_body(a.body)?;
                    match &a.patterns {
                        Some(ps) => {
                            if ps.len() == 1 {
                                if let Kind::TypePat { ty } = self.g.kind(ps[0]) {
                                    body.push_str(&format!("case {}: {} => {}\n", bind, ty, arm_body));
                                    continue;
                                }
                            }
                            let pts: Vec<String> = ps
                                .iter()
                                .map(|p| match self.g.kind(*p) {
                                    Kind::TypePat { ty } => Some(format!("_: {}", ty)),
                                    _ => self.t(*p),
                                })
                                .collect::<Option<_>>()?;
                            body.push_str(&format!("case {} => {}\n", pts.join(" | "), arm_body));
                        }
                        None => {
                            body.push_str(&format!("case _ => {}\n", arm_body));
                        }
                    }
                }
                // 非枚举类型的 match 需要 catch-all 以确保穷举
                let has_catch_all = arms.iter().any(|a| a.patterns.is_none());
                if !has_catch_all {
                    // Check if subject is an enum type (already exhaustive)
                    // Use enum_entries() for robust detection instead of fragile '.' heuristic
                    let is_enum = if let Kind::NameRef { original: _, .. } = self.g.kind(subj) {
                        // Check if the subject variable's type or declared enum matches
                        self.expr_type_name(subj)
                            .map_or(false, |ty| self.enum_entries(&ty).is_some())
                        || arms.iter().any(|a| {
                            a.patterns.as_ref().map_or(false, |ps| {
                                ps.iter().any(|p| {
                                    if let Some(s) = self.t(*p) {
                                        // Pattern like EnumName.ENTRY
                                        if let Some(prefix) = s.split('.').next() {
                                            self.enum_entries(prefix).is_some()
                                        } else {
                                            false
                                        }
                                    } else {
                                        false
                                    }
                                })
                            })
                        })
                    } else {
                        false
                    };
                    if !is_enum {
                        // Check if all arms are type patterns (sealed class style)
                        let all_type_pats = arms.iter().all(|a| {
                            a.patterns.as_ref().map_or(false, |ps| {
                                ps.iter().all(|p| matches!(self.g.kind(*p), Kind::TypePat { .. }))
                            })
                        });
                        if all_type_pats {
                            body.push_str("case _ => throw Exception(\"\")\n");
                        } else {
                            body.push_str("case _ => ()\n");
                        }
                    }
                }
                Some(format!("match ({}) {{\n{}}}", s, indent(&body, 1)))
            }
            None => {
                let mut out = String::new();
                for (i, a) in arms.iter().enumerate() {
                    let arm_body = self.render_block(a.body)?;
                    match &a.patterns {
                        Some(ps) => {
                            let cond = self.t(ps[0])?;
                            if i == 0 {
                                out.push_str(&format!("if ({}) {}", cond, arm_body));
                            } else {
                                out.push_str(&format!(" else if ({}) {}", cond, arm_body));
                            }
                        }
                        None => out.push_str(&format!(" else {}", arm_body)),
                    }
                }
                Some(out)
            }
        }
    }

    fn render_when_as_if(&self, subj: NodeId, arms: &[WhenArm]) -> Option<String> {
        let mut out = String::new();
        let mut first = true;
        for a in arms {
            let arm_body = self.render_block(a.body)?;
            match &a.patterns {
                Some(ps) => {
                    let mut conds = Vec::new();
                    for p in ps {
                        let c = match self.g.kind(*p) {
                            Kind::InPat { negated, rhs } => {
                                let inner = self.render_in(subj, *rhs)?;
                                if *negated { format!("!({})", inner) } else { inner }
                            }
                            Kind::TypePat { ty } => format!("{} is {}", self.atom(subj)?, ty),
                            _ => format!("{} == {}", self.atom(subj)?, self.t(*p)?),
                        };
                        conds.push(c);
                    }
                    let cond = conds.join(" || ");
                    if first {
                        out.push_str(&format!("if ({}) {}", cond, arm_body));
                        first = false;
                    } else {
                        out.push_str(&format!(" else if ({}) {}", cond, arm_body));
                    }
                }
                None => out.push_str(&format!(" else {}", arm_body)),
            }
        }
        Some(out)
    }

    fn render_arm_body(&self, id: NodeId) -> Option<String> {
        let inner = self.render_block_inner(id, 0)?;
        if inner.trim().is_empty() {
            Some("()".to_string())
        } else if inner.lines().count() <= 1 {
            Some(inner.trim().to_string())
        } else {
            Some(format!("\n{}", indent(&inner, 1)))
        }
    }

    // ============ 调用渲染 ============
    // 已迁移至 render_calls.rs

    // ============ 辅助 ============

    /// 把接收者渲染为「产生迭代器」的表达式。
    pub(crate) fn as_iter(&self, base: NodeId) -> Option<String> {
        Some(format!("{}.iterator()", self.atom(base)?))
    }

    /// 由字面量初值粗略推断 `fold` 的累加器类型实参。
    pub(crate) fn lit_type(&self, id: NodeId) -> String {
        match self.g.kind(id) {
            Kind::FloatLit(_) => "Float64".to_string(),
            Kind::BoolLit(_) => "Bool".to_string(),
            Kind::StrTemplate { .. } => "String".to_string(),
            _ => "Int64".to_string(),
        }
    }

    /// 查找名为 `fname` 的用户函数或类构造器，返回其参数（安全名, 是否有默认值）列表。
    pub(crate) fn fn_named_params(&self, fname: &str) -> Option<Vec<(String, bool)>> {
        let target = crate::parser::safe_name(fname);
        for node in &self.g.nodes {
            match &node.kind {
                Kind::Func { name, params, .. } if *name == target => {
                    let mut out = Vec::new();
                    let mut any_default = false;
                    for p in params {
                        if let Kind::Param { name_node, default, .. } = self.g.kind(*p) {
                            let pn = if let Kind::Name { original } = self.g.kind(*name_node) {
                                crate::parser::safe_name(original)
                            } else {
                                "_".to_string()
                            };
                            let has = default.is_some();
                            any_default = any_default || has;
                            out.push((pn, has));
                        }
                    }
                    if any_default {
                        return Some(out);
                    }
                    return None;
                }
                Kind::Class { name, ctor_params, .. }
                    if *name == target =>
                {
                    let mut out = Vec::new();
                    let mut any_default = false;
                    for p in ctor_params {
                        let has = p.default.is_some();
                        any_default = any_default || has;
                        out.push((p.name.clone(), has));
                    }
                    if any_default {
                        return Some(out);
                    }
                    return None;
                }
                _ => {}
            }
        }
        None
    }

    /// 成员检查 `x in rhs`：区间转比较，集合转 contains。
    pub(crate) fn render_in(&self, lhs: NodeId, rhs: NodeId) -> Option<String> {
        let l = self.atom(lhs)?;
        if let Kind::Range { lo, hi, inclusive, down, .. } = self.g.kind(rhs).clone() {
            let lo_s = self.atom(lo)?;
            let hi_s = self.atom(hi)?;
            if down {
                return Some(format!("{} <= {} && {} >= {}", l, lo_s, l, hi_s));
            }
            let upper = if inclusive { "<=" } else { "<" };
            return Some(format!("{} >= {} && {} {} {}", l, lo_s, l, upper, hi_s));
        }
        let r = self.atom(rhs)?;
        Some(format!("{}.contains({})", r, l))
    }

    // ============ 程序渲染 ============

    pub(crate) fn render_program(&self, items: &[NodeId]) -> Option<String> {
        let mut globals = Vec::new();
        let mut decls = Vec::new();
        let mut loose = Vec::new();
        let mut has_main = false;
        let mut has_enum = false;
        for it in items {
            match self.g.kind(*it) {
                Kind::Func { is_main, .. } => {
                    if *is_main {
                        has_main = true;
                    }
                    decls.push(self.t(*it)?);
                }
                Kind::Class { .. } => decls.push(self.t(*it)?),
                Kind::Enum { .. } => {
                    has_enum = true;
                    decls.push(self.t(*it)?);
                }
                Kind::VarDecl { .. } => globals.push(self.t(*it)?),
                _ => loose.push(self.t(*it)?),
            }
        }
        let mut sections: Vec<String> = Vec::new();
        if !globals.is_empty() {
            sections.push(globals.join("\n"));
        }
        if !decls.is_empty() {
            sections.push(decls.join("\n\n"));
        }
        let mut body = sections.join("\n\n");
        if !loose.is_empty() && !has_main {
            let main_body = loose.join("\n");
            body.push_str(&format!("\n\nmain() {{\n{}\n}}", indent(&main_body, 1)));
        } else if !loose.is_empty() {
            body.push_str("\n\n");
            body.push_str(&loose.join("\n"));
        }
        let mut header = String::new();
        if body.contains("ArrayList") || body.contains("HashMap") || body.contains("HashSet")
            || body.contains(".iterator()") || body.contains("collectArray")
        {
            header.push_str("import std.collection.*\n");
        }
        if has_enum {
            header.push_str("import std.deriving.*\n");
        }
        if body.contains("Int64.parse") || body.contains("Float64.parse") {
            header.push_str("import std.convert.*\n");
        }
        if body.contains("sort(_s") || body.contains("sort(") {
            header.push_str("import std.sort.*\n");
        }
        if !header.is_empty() {
            header.push('\n');
        }
        Some(format!("{}{}\n", header, body))
    }
}

/// 给多行文本整体增加 n 级缩进。
pub(crate) fn indent(s: &str, n: usize) -> String {
    let pad = IND.repeat(n);
    s.lines()
        .map(|l| if l.is_empty() { String::new() } else { format!("{}{}", pad, l) })
        .collect::<Vec<_>>()
        .join("\n")
}

/// 从声明字符串中精确剥离修饰符关键字（仅匹配行首的修饰符序列，避免误伤标识符）。
fn strip_modifier(s: &str, modifier: &str) -> String {
    let prefix = format!("{} ", modifier);
    // 仅处理第一行（声明签名行），保护函数体内容
    if let Some(first_nl) = s.find('\n') {
        let (head, tail) = s.split_at(first_nl);
        let cleaned = head.replacen(&prefix, "", 1);
        format!("{}{}", cleaned, tail)
    } else {
        s.replacen(&prefix, "", 1)
    }
}
