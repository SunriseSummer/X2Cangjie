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
                Some(format!("{} {} {}", tt, op, v))
            }
            Kind::Return { value } => match value {
                Some(v) => Some(format!("return {}", self.t(v)?)),
                None => Some("return".to_string()),
            },
            Kind::Throw { value } => Some(format!("throw {}", self.t(value)?)),
            Kind::VarDecl { mutable, name_node, ty, init } => {
                let name = self.t(name_node)?;
                if init.is_none() && ty.is_none() {
                    return Some(name);
                }
                let kw = if mutable { "var" } else { "let" };
                let tys = ty.map(|t| format!(": {}", t)).unwrap_or_default();
                match init {
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
            Kind::Func { name, params, ret, body, is_main, is_abstract, is_override } => {
                self.render_func(&name, &params, ret, body, is_main, is_abstract, is_override)
            }
            Kind::Class { name, ctor_params, members, superclass, is_open, is_data, is_interface, is_abstract, interfaces, super_args, generics, init_block } => {
                self.render_class(&name, &ctor_params, &members, superclass, is_open, is_data, is_interface, is_abstract, &interfaces, &super_args, &generics, init_block)
            }
            Kind::Enum { name, entries } => self.render_enum(&name, &entries),
            Kind::Program { items } => self.render_program(&items),
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
        if matches!(op, "+" | "-" | "*" | "/" | "%") {
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
        let (b, dot) = if safe {
            let bs = if let Kind::Index { base: ib, index } = self.g.kind(base) {
                format!("{}.get({})", self.atom(*ib)?, self.t(*index)?)
            } else {
                self.atom(base)?
            };
            (bs, "?.")
        } else {
            // Auto-unwrap nullable types: if base has type ?T, use .getOrThrow() before member access
            let raw = self.atom(base)?;
            let b = if self.is_nullable_expr(base) {
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
            "first" if !safe && self.looks_tuple(base) => return Some(format!("{}[0]", b)),
            "second" if !safe && self.looks_tuple(base) => return Some(format!("{}[1]", b)),
            "third" if !safe && self.looks_tuple(base) => return Some(format!("{}[2]", b)),
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

    fn render_func(&self, name: &str, params: &[NodeId], ret: Option<String>, body: NodeId, is_main: bool, is_abstract: bool, is_override: bool) -> Option<String> {
        let ps: Vec<String> = params.iter().map(|p| self.t(*p)).collect::<Option<_>>()?;
        if is_main {
            let b = self.render_block(body)?;
            return Some(format!("main() {}", b));
        }
        let r = match ret {
            Some(r) => format!(": {}", r),
            None if self.refers_name(body, name) => ": Unit".to_string(),
            None if is_abstract => ": Unit".to_string(),
            None => String::new(),
        };
        let sig = format!("{}({}){}", name, ps.join(", "), r);
        if is_abstract {
            return Some(format!("public func {}", sig));
        }
        let b = self.render_block(body)?;
        let vis = if is_override { "public " } else { "" };
        Some(format!("{}func {} {}", vis, sig, b))
    }

    // ============ 类渲染 ============

    #[allow(clippy::too_many_arguments)]
    fn render_class(&self, name: &str, ctor_params: &[CtorParam], members: &[NodeId], superclass: Option<String>, is_open: bool, is_data: bool, is_interface: bool, is_abstract: bool, interfaces: &[String], super_args: &[NodeId], generics: &[String], init_block: Option<NodeId>) -> Option<String> {
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
                    let r = ret.clone().map(|r| format!(": {}", r)).unwrap_or_default();
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
                .map(|p| format!("{}: {}", p.name, p.ty))
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
            body.push_str(&indent(&mt, 1));
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

    fn render_enum(&self, name: &str, entries: &[String]) -> Option<String> {
        if entries.is_empty() {
            Some(format!("enum {} {{ | {} }}", name, name))
        } else {
            let body = entries.join(" | ");
            let mut arms = String::new();
            for e in entries {
                arms.push_str(&format!("{}{}{}case {} => \"{}\"\n", IND, IND, IND, e, e));
            }
            Some(format!(
                "@Derive[Equatable]\nenum {} <: ToString {{\n{}| {}\n{}public func toString(): String {{\n{}return match (this) {{\n{}{}}}\n{}}}\n}}",
                name, IND, body, IND, IND, IND, arms, IND
            ))
        }
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
                    let is_enum = arms.iter().any(|a| {
                        a.patterns.as_ref().map_or(false, |ps| {
                            ps.iter().any(|p| {
                                if let Some(s) = self.t(*p) {
                                    s.contains('.')
                                } else {
                                    false
                                }
                            })
                        })
                    });
                    if !is_enum {
                        body.push_str("case _ => ()\n");
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
                        format!("\n{}\n", indent(&inner, 1))
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
            "removeAt" if args.len() == 1 => {
                Some(format!("{}.remove(at: {})", b, self.t(args[0])?))
            }
            "addAll" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!("{}.add(all: {})", b, self.t(args[0])?))
            }
            "containsKey" if args.len() == 1 => {
                Some(format!("{}.contains({})", b, self.t(args[0])?))
            }
            "getOrDefault" if args.len() == 2 => {
                Some(format!("({}.get({}) ?? {})", b, self.t(args[0])?, self.t(args[1])?))
            }
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
            "withIndex" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!("{}.iterator().enumerate()", b))
            }
            "average" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!(
                    "(Float64({}.fold<Int64>(0, {{acc, x => acc + x}})) / Float64({}.count()))",
                    self.as_iter(base)?, self.as_iter(base)?
                ))
            }
            "substring" if args.len() == 2 => {
                Some(format!("{}[{}..{}]", b, self.t(args[0])?, self.t(args[1])?))
            }
            "substring" if args.len() == 1 => {
                Some(format!("{}[{}..]", b, self.t(args[0])?))
            }
            "isNotEmpty" if args.is_empty() => {
                Some(format!("!({}.isEmpty())", b))
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
            "joinToString" if !self.provably_non_collection(base) => {
                self.render_join_to_string(base, &b, args)
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
            "reversed" if args.is_empty() && self.looks_string(base) => {
                Some(format!(
                    "({{ => let _r = {}.toRuneArray(); String(Array<Rune>(_r.size, {{j => _r[_r.size - 1 - j]}})) }})()",
                    b
                ))
            }
            "reversed" if args.is_empty() && !self.provably_non_collection(base) => {
                Some(format!(
                    "({{ => let _s = collectArrayList({}); _s.reverse(); _s }})()",
                    self.as_iter(base)?
                ))
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
            "map" | "filter" if args.len() == 1 && !self.provably_non_collection(base) => {
                Some(format!(
                    "collectArrayList({}.{}({}))",
                    self.as_iter(base)?, name, self.t(args[0])?
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

    /// 查找名为 `fname` 的用户函数，返回其参数（安全名, 是否有默认值）列表。
    pub(crate) fn fn_named_params(&self, fname: &str) -> Option<Vec<(String, bool)>> {
        let target = crate::parser::safe_name(fname);
        for node in &self.g.nodes {
            if let Kind::Func { name, params, .. } = &node.kind {
                if *name != target {
                    continue;
                }
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
