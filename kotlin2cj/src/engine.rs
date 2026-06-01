//! 自组织翻译引擎：对翻译图做异步 worklist 松弛，直至收敛。
//!
//! 每个节点仅依据 *自身 + 子节点（邻居）已确定的目标片段* 来计算自己的目标，
//! 这正是 idea.md 中的「表达式传播」局部规则。一旦某节点的目标发生变化，
//! 就把它的父节点与依赖者重新入队——形成沿语法/依赖边的「崩塌级联」。
//! 当 worklist 清空时，整张图到达稳定（临界）态。

use crate::node::*;
use std::collections::VecDeque;

pub struct Engine {
    pub g: Graph,
    /// 最近一次驱动引发的雪崩规模（状态变更次数）。
    pub last_avalanche: usize,
    /// 历次雪崩规模，用于观察幂律分布。
    pub avalanche_sizes: Vec<usize>,
    pub total_updates: u64,
}

const IND: &str = "    ";

impl Engine {
    pub fn new(mut g: Graph) -> Self {
        // 建立依赖边：标识符引用 → 声明。
        let n = g.nodes.len();
        for id in 0..n {
            if let Kind::NameRef { decl: Some(d), .. } = g.nodes[id].kind {
                g.nodes[id].dep = Some(d);
                g.nodes[d].dependents.push(id);
            }
        }
        g.link_children();
        Engine { g, last_avalanche: 0, avalanche_sizes: Vec::new(), total_updates: 0 }
    }

    /// 把整张图松弛到收敛（初始翻译）。
    pub fn relax(&mut self) {
        let n = self.g.nodes.len();
        let mut queue: VecDeque<NodeId> = (0..n).collect();
        let mut avalanche = 0;
        while let Some(id) = queue.pop_front() {
            if self.step(id, &mut queue) {
                avalanche += 1;
            }
        }
        self.last_avalanche = avalanche;
        self.avalanche_sizes.push(avalanche);
    }

    /// 对单个节点应用局部规则；若目标发生变化则把邻居重新入队。
    fn step(&mut self, id: NodeId, queue: &mut VecDeque<NodeId>) -> bool {
        let rendered = self.render(id);
        let new_target = match rendered {
            Some(t) => t,
            None => return false, // 子节点尚未就绪，等待被重新唤醒
        };
        self.g.nodes[id].state.temperature += 1;
        let changed = self.g.nodes[id].state.target.as_deref() != Some(new_target.as_str());
        if changed {
            self.g.nodes[id].state.target = Some(new_target);
            self.g.nodes[id].state.version += 1;
            self.g.nodes[id].state.confidence = 1.0;
            self.total_updates += 1;
            // 崩塌级联：唤醒父节点与依赖者。
            if let Some(p) = self.g.nodes[id].parent {
                queue.push_back(p);
            }
            for d in self.g.nodes[id].dependents.clone() {
                queue.push_back(d);
            }
        }
        changed
    }

    /// 扰动：强制重命名一个声明，观察引用雪崩（演示 SOC 自动修复）。
    pub fn perturb_rename(&mut self, name_node: NodeId, new_name: &str) {
        if let Kind::Name { original } = &mut self.g.nodes[name_node].kind {
            *original = new_name.to_string();
        }
        self.g.nodes[name_node].state.target = None;
        let mut queue: VecDeque<NodeId> = VecDeque::new();
        queue.push_back(name_node);
        let mut avalanche = 0;
        while let Some(id) = queue.pop_front() {
            if self.step(id, &mut queue) {
                avalanche += 1;
            }
        }
        self.last_avalanche = avalanche;
        self.avalanche_sizes.push(avalanche);
    }

    pub fn output(&self) -> String {
        self.g.target(self.g.root).unwrap_or("").to_string()
    }

    // ============ 局部渲染规则 ============
    fn t(&self, id: NodeId) -> Option<String> {
        self.g.target(id).map(|s| s.to_string())
    }

    /// 若操作数本身是二元/区间表达式，加括号以保持优先级。
    fn atom(&self, id: NodeId) -> Option<String> {
        let s = self.t(id)?;
        let need = matches!(self.g.kind(id), Kind::Binary { .. } | Kind::Range { .. });
        if need {
            Some(format!("({})", s))
        } else {
            Some(s)
        }
    }

    fn render(&self, id: NodeId) -> Option<String> {
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
            Kind::Binary { op, lhs, rhs } => {
                let l = self.t(lhs)?;
                let r = self.t(rhs)?;
                if op == "to" {
                    return Some(format!("({}, {})", l, r));
                }
                if op == "?:" {
                    let ra = self.atom(rhs)?;
                    // Kotlin `map[key] ?: default` → 仓颉 `map.get(key) ?? default`
                    // （下标读取在仓颉返回 V 且越界抛异常，.get 返回 Option 才能 coalesce）
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
                let la = self.atom(lhs)?;
                let ra = self.atom(rhs)?;
                // 仓颉无 Int64→Float64 隐式提升：算术运算中若一侧为 Float、另一侧为
                // 整型数值，则把整型侧显式包裹 Float64(...)，对齐 Kotlin 的自动提升语义。
                if matches!(op.as_str(), "+" | "-" | "*" | "/" | "%") {
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
                Some(format!("{}[{}]", b, i))
            }
            Kind::Member { base, name, safe } => {
                // 安全调用 `?.`：下标读取改用 .get 得到 Option，并保留 `?.`。
                let (b, dot) = if safe {
                    let bs = if let Kind::Index { base: ib, index } = self.g.kind(base) {
                        format!("{}.get({})", self.atom(*ib)?, self.t(*index)?)
                    } else {
                        self.atom(base)?
                    };
                    (bs, "?.")
                } else {
                    (self.atom(base)?, ".")
                };
                let mapped = match name.as_str() {
                    "length" => "size",
                    // 集合索引视图：indices → 0..size，lastIndex → size-1。
                    "indices" if !safe => return Some(format!("(0..{}.size)", b)),
                    "lastIndex" if !safe => return Some(format!("({}.size - 1)", b)),
                    // Pair/Triple 的 first/second/third → 元组下标（仅当接收者可证明为元组）。
                    "first" if !safe && self.looks_tuple(base) => return Some(format!("{}[0]", b)),
                    "second" if !safe && self.looks_tuple(base) => return Some(format!("{}[1]", b)),
                    "third" if !safe && self.looks_tuple(base) => return Some(format!("{}[2]", b)),
                    "toUpperCase" | "uppercase" => "toAsciiUpper",
                    "toLowerCase" | "lowercase" => "toAsciiLower",
                    "trim" => "trimAscii",
                    "trimStart" => "trimAsciiStart",
                    "trimEnd" => "trimAsciiEnd",
                    // Kotlin 的 `map.keys` / `map.values` 属性 → 仓颉方法。
                    "keys" => return Some(format!("{}{}keys()", b, dot)),
                    "values" => return Some(format!("{}{}values()", b, dot)),
                    other => other,
                };
                Some(format!("{}{}{}", b, dot, mapped))
            }
            Kind::Call { callee, args } => self.render_call(callee, &args),
            Kind::CollLit { ctor, elem, args } => {
                if args.is_empty() {
                    match elem {
                        Some(e) => Some(format!("{}<{}>()", ctor, e)),
                        None => Some(format!("{}()", ctor)),
                    }
                } else {
                    let a: Vec<String> = args.iter().map(|x| self.t(*x)).collect::<Option<_>>()?;
                    Some(format!("{}([{}])", ctor, a.join(", ")))
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
                // recv 为下标读取时改用 .get(index) 以得到 Option。
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
                    // 用作循环变量等场景，仅名字
                    return Some(name);
                }
                let kw = if mutable { "var" } else { "let" };
                let tys = ty.map(|t| format!(": {}", t)).unwrap_or_default();
                match init {
                    Some(i) => Some(format!("{} {}{} = {}", kw, name, tys, self.t(i)?)),
                    None => Some(format!("{} {}{}", kw, name, tys)),
                }
            }
            Kind::If { cond, then_b, else_b } => {
                let c = self.t(cond)?;
                let tb = self.render_block(then_b)?;
                match else_b {
                    Some(e) => {
                        // else if 链
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
            Kind::While { cond, body } => {
                Some(format!("while ({}) {}", self.t(cond)?, self.render_block(body)?))
            }
            Kind::DoWhile { body, cond } => {
                Some(format!("do {} while ({})", self.render_block(body)?, self.t(cond)?))
            }
            Kind::Repeat { count, body } => {
                Some(format!("for (_ in 0..{}) {}", self.atom(count)?, self.render_block(body)?))
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
                // 遍历字符串时改用 `.runes()` 以得到 Rune（与 Kotlin 的 Char 一致），
                // 否则仓颉直接迭代字符串会逐字节产出 UInt8。
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
            Kind::Param { name_node, ty } => Some(format!("{}: {}", self.t(name_node)?, ty)),
            Kind::Func { name, params, ret, body, is_main } => {
                let ps: Vec<String> = params.iter().map(|p| self.t(*p)).collect::<Option<_>>()?;
                let b = self.render_block(body)?;
                if is_main {
                    Some(format!("main() {}", b))
                } else {
                    let r = ret.map(|r| format!(": {}", r)).unwrap_or_default();
                    Some(format!("func {}({}){} {}", name, ps.join(", "), r, b))
                }
            }
            Kind::Class { name, ctor_params, members, superclass, is_open } => {
                let mut body = String::new();
                // 成员变量（来自主构造参数中带 val/var 的部分）
                for p in &ctor_params {
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
                // 构造函数
                if !ctor_params.is_empty() {
                    let ps: Vec<String> = ctor_params
                        .iter()
                        .map(|p| format!("{}: {}", p.name, p.ty))
                        .collect();
                    body.push_str(&format!("{}init({}) {{\n", IND, ps.join(", ")));
                    for p in &ctor_params {
                        if p.kind != CtorParamKind::Plain {
                            body.push_str(&format!("{}{}this.{} = {}\n", IND, IND, p.name, p.name));
                        }
                    }
                    body.push_str(&format!("{}}}\n", IND));
                }
                // 其它成员
                for m in &members {
                    let mt = self.t(*m)?;
                    body.push_str(&indent(&mt, 1));
                    body.push('\n');
                }
                let kw = if is_open { "open class" } else { "class" };
                let sup = match &superclass {
                    Some(s) => format!(" <: {}", s),
                    None => String::new(),
                };
                if body.is_empty() {
                    Some(format!("{} {}{} {{}}", kw, name, sup))
                } else {
                    Some(format!("{} {}{} {{\n{}}}", kw, name, sup, body))
                }
            }
            Kind::Enum { name, entries } => {
                if entries.is_empty() {
                    Some(format!("enum {} {{ | {} }}", name, name))
                } else {
                    let body = entries.join(" | ");
                    // 派生 Equatable 支持 `==`/`match`；自定义 toString 使枚举项在字符串
                    // 插值中打印裸名字（与 Kotlin 一致），而非 `Enum.Item` 限定名。
                    let mut arms = String::new();
                    for e in &entries {
                        arms.push_str(&format!("{}{}{}case {} => \"{}\"\n", IND, IND, IND, e, e));
                    }
                    Some(format!(
                        "@Derive[Equatable]\nenum {} <: ToString {{\n{}| {}\n{}public func toString(): String {{\n{}return match (this) {{\n{}{}}}\n{}}}\n}}",
                        name, IND, body, IND, IND, IND, arms, IND
                    ))
                }
            }
            Kind::Program { items } => self.render_program(&items),
        }
    }

    fn loop_var_name(&self, var: NodeId) -> Option<String> {
        if let Kind::VarDecl { name_node, .. } = self.g.kind(var) {
            self.t(*name_node)
        } else {
            self.t(var)
        }
    }

    fn render_block(&self, id: NodeId) -> Option<String> {
        let inner = self.render_block_inner(id, 0)?;
        if inner.trim().is_empty() {
            Some("{}".to_string())
        } else {
            Some(format!("{{\n{}\n}}", indent(&inner, 1)))
        }
    }

    /// 渲染块内部的语句序列（不含外层大括号，无缩进）。
    fn render_block_inner(&self, id: NodeId, _d: usize) -> Option<String> {
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

    fn render_when(&self, subject: Option<NodeId>, arms: &[WhenArm]) -> Option<String> {
        match subject {
            Some(subj) => {
                let s = self.t(subj)?;
                // 主语为简单标识符时，类型分支可复用该名字绑定，获得「智能转换」语义。
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
                            // 单一类型分支 `is T` → `case bind: T =>`（智能转换）。
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
                Some(format!("match ({}) {{\n{}}}", s, indent(&body, 1)))
            }
            None => {
                // 无主语的 when → if/else 链
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

    /// match 分支体：单表达式直接内联，多语句各占一行。
    fn render_arm_body(&self, id: NodeId) -> Option<String> {
        let inner = self.render_block_inner(id, 0)?;
        if inner.lines().count() <= 1 {
            Some(inner.trim().to_string())
        } else {
            Some(format!("\n{}", indent(&inner, 1)))
        }
    }

    fn render_call(&self, callee: NodeId, args: &[NodeId]) -> Option<String> {
        // Pair(a, b) / Triple(a, b, c) → 仓颉元组字面量 (a, b)。
        if let Kind::NameRef { original, .. } = self.g.kind(callee) {
            if (original == "Pair" || original == "Triple") && args.len() >= 2 {
                let a: Vec<String> = args.iter().map(|x| self.t(*x)).collect::<Option<_>>()?;
                return Some(format!("({})", a.join(", ")));
            }
            // maxOf(a, b) / minOf(a, b) / kotlin.math 的 max/min → 内联条件表达式（不依赖标准库符号）。
            if (original == "maxOf" || original == "minOf"
                || ((original == "max" || original == "min") && !self.is_user_func(original)))
                && args.len() == 2
            {
                let a = self.t(args[0])?;
                let b = self.t(args[1])?;
                let cmp = if original == "maxOf" || original == "max" { ">" } else { "<" };
                return Some(format!("(if ({} {} {}) {{ {} }} else {{ {} }})", a, cmp, b, a, b));
            }
            // kotlin.math 的 abs(x) → 内联条件（避免标准库重载与整/浮点歧义）。
            if original == "abs" && args.len() == 1 && !self.is_user_func(original) {
                let a = self.atom(args[0])?;
                return Some(format!("(if ({} < 0) {{ -({}) }} else {{ {} }})", a, a, a));
            }
        }
        // 成员方法的特殊映射。
        if let Kind::Member { base, name, .. } = self.g.kind(callee) {
            let b = self.atom(*base)?;
            match name.as_str() {
                // recv.removeAt(i) → recv.remove(at: i)
                "removeAt" if args.len() == 1 => {
                    return Some(format!("{}.remove(at: {})", b, self.t(args[0])?));
                }
                // Map 成员检查：Kotlin 的 containsKey/containsValue → 仓颉 HashMap.contains。
                "containsKey" if args.len() == 1 => {
                    return Some(format!("{}.contains({})", b, self.t(args[0])?));
                }
                // map.getOrDefault(k, d) → (map.get(k) ?? d)（下标读取会抛异常，get 返回 Option）。
                "getOrDefault" if args.len() == 2 => {
                    return Some(format!("({}.get({}) ?? {})", b, self.t(args[0])?, self.t(args[1])?));
                }
                // 就地排序：Kotlin 的 sort/sortDescending/sortBy/sortByDescending 改原集合，
                // 映射到仓颉 std.sort 的全局 sort（成员版已弃用），保持就地语义。
                "sort" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!("sort({})", b));
                }
                "sortDescending" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!("sort({}, descending: true)", b));
                }
                "sortBy" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!("sort({}, key: {})", b, self.t(args[0])?));
                }
                "sortByDescending" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!("sort({}, key: {}, descending: true)", b, self.t(args[0])?));
                }
                // xs.withIndex() → xs.iterator().enumerate()（产出 (index, value) 元组）。
                "withIndex" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!("{}.iterator().enumerate()", b));
                }
                // xs.average() → Float64(总和) / Float64(个数)（仓颉无内建 average）。
                "average" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!(
                        "(Float64({}.fold<Int64>(0, {{acc, x => acc + x}})) / Float64({}.count()))",
                        self.as_iter(*base)?, self.as_iter(*base)?
                    ));
                }
                // s.substring(a, b) → s[a..b]；s.substring(a) → s[a..]
                "substring" if args.len() == 2 => {
                    return Some(format!("{}[{}..{}]", b, self.t(args[0])?, self.t(args[1])?));
                }
                "substring" if args.len() == 1 => {
                    return Some(format!("{}[{}..]", b, self.t(args[0])?));
                }
                // xs.isNotEmpty() → !(xs.isEmpty())
                "isNotEmpty" if args.is_empty() => {
                    return Some(format!("!({}.isEmpty())", b));
                }
                // xs.first() → xs[0]；xs.last() → xs[xs.size - 1]
                "first" if args.is_empty() => {
                    return Some(format!("{}[0]", b));
                }
                "last" if args.is_empty() => {
                    return Some(format!("{}[{}.size - 1]", b, b));
                }
                // firstOrNull()/lastOrNull() → .get(i)（返回 Option，便于 `?:` 级联）。
                "firstOrNull" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!("{}.get(0)", b));
                }
                "lastOrNull" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!("{}.get({}.size - 1)", b, b));
                }
                // List<String>.joinToString(sep?) { transform? }
                //   → String.join(xs.toArray(), delimiter: sep)
                //   带 transform 时先 map 成字符串再收集为数组。
                "joinToString" if !self.provably_non_collection(*base) => {
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
                            self.as_iter(*base)?,
                            lam,
                            sep
                        ));
                    }
                    return Some(format!(
                        "String.join(collectArray<String>({}.map({{e => e.toString()}})), delimiter: {})",
                        self.as_iter(*base)?, sep
                    ));
                }
                // 排序：Kotlin 的 sorted*/reversed 返回新列表（不改原集合），
                // 用立即调用闭包先拷贝再就地排序，整体作为表达式产出新 ArrayList。
                "sorted" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!(
                        "({{ => let _s = collectArrayList({}); sort(_s); _s }})()",
                        self.as_iter(*base)?
                    ));
                }
                "sortedDescending" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!(
                        "({{ => let _s = collectArrayList({}); sort(_s, descending: true); _s }})()",
                        self.as_iter(*base)?
                    ));
                }
                "sortedBy" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!(
                        "({{ => let _s = collectArrayList({}); sort(_s, key: {}); _s }})()",
                        self.as_iter(*base)?, self.t(args[0])?
                    ));
                }
                "sortedByDescending" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!(
                        "({{ => let _s = collectArrayList({}); sort(_s, key: {}, descending: true); _s }})()",
                        self.as_iter(*base)?, self.t(args[0])?
                    ));
                }
                "reversed" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!(
                        "({{ => let _s = collectArrayList({}); _s.reverse(); _s }})()",
                        self.as_iter(*base)?
                    ));
                }
                // xs.toList()/toMutableList() / (a..b).toList() → 收集为 ArrayList。
                "toList" | "toMutableList" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!("collectArrayList({})", self.atom(*base)?));
                }
                // 返回集合的链式高阶：map/filter 急切收集为 ArrayList，
                // 既可继续链接、在 for 中遍历，也可存入变量后多次复用 / 取 size / 索引。
                "map" | "filter" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!(
                        "collectArrayList({}.{}({}))",
                        self.as_iter(*base)?, name, self.t(args[0])?
                    ));
                }
                // 布尔终结操作。
                "any" | "all" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!("{}.{}({})", self.as_iter(*base)?, name, self.t(args[0])?));
                }
                "none" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!("!{}.any({})", self.as_iter(*base)?, self.t(args[0])?));
                }
                // 计数：带谓词时先 filter，再 count；无参时即 size。
                "count" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!("{}.filter({}).count()", self.as_iter(*base)?, self.t(args[0])?));
                }
                "count" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!("{}.size", b));
                }
                // 求和：sum() 直接折叠；sumOf { } 先 map 再折叠（按 Int64 处理）。
                "sum" if args.is_empty() && !self.provably_non_collection(*base) => {
                    return Some(format!("{}.fold<Int64>(0, {{acc, x => acc + x}})", self.as_iter(*base)?));
                }
                "sumOf" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!(
                        "{}.map({}).fold<Int64>(0, {{acc, x => acc + x}})",
                        self.as_iter(*base)?,
                        self.t(args[0])?
                    ));
                }
                // fold(init) { acc, x -> } → iterator().fold<T>(init, lambda)，T 由 init 字面量推断。
                "fold" if args.len() == 2 && !self.provably_non_collection(*base) => {
                    let ty = self.lit_type(args[0]);
                    return Some(format!(
                        "{}.fold<{}>({}, {})",
                        self.as_iter(*base)?,
                        ty,
                        self.t(args[0])?,
                        self.t(args[1])?
                    ));
                }
                // reduce { a, b -> } → iterator().reduce(...).getOrThrow()（Kotlin reduce 返回非空 T）。
                "reduce" if args.len() == 1 && !self.provably_non_collection(*base) => {
                    return Some(format!("{}.reduce({}).getOrThrow()", self.as_iter(*base)?, self.t(args[0])?));
                }
                // max()/min()：折叠取极值并解包；maxOrNull()/minOrNull() 保留 Option 以便 `?:` 级联。
                "max" | "min" if args.is_empty() && !self.provably_non_collection(*base) => {
                    let cmp = if name == "max" { ">" } else { "<" };
                    return Some(format!(
                        "{}.reduce({{a, b => if (a {} b) {{ a }} else {{ b }}}}).getOrThrow()",
                        self.as_iter(*base)?, cmp
                    ));
                }
                "maxOrNull" | "minOrNull" if args.is_empty() && !self.provably_non_collection(*base) => {
                    let cmp = if name == "maxOrNull" { ">" } else { "<" };
                    return Some(format!(
                        "{}.reduce({{a, b => if (a {} b) {{ a }} else {{ b }}}})",
                        self.as_iter(*base)?, cmp
                    ));
                }
                // 数值/字符串转换：数值接收者用类型构造转换，字符串用 parse。
                "toInt" | "toLong" if args.is_empty() => {
                    if self.looks_numeric(*base) {
                        return Some(format!("Int64({})", b));
                    }
                    return Some(format!("Int64.parse({})", b));
                }
                "toDouble" | "toFloat" if args.is_empty() => {
                    if self.looks_numeric(*base) {
                        return Some(format!("Float64({})", b));
                    }
                    return Some(format!("Float64.parse({})", b));
                }
                _ => {}
            }
        }
        let c = self.atom(callee)?;
        let a: Vec<String> = args.iter().map(|x| self.t(*x)).collect::<Option<_>>()?;
        Some(format!("{}({})", c, a.join(", ")))
    }

    /// 把接收者渲染为「产生迭代器」的表达式（`recv.iterator()`）。map/filter 已急切收集为
    /// ArrayList，因此一律追加 `.iterator()` 即可继续链式调用。
    fn as_iter(&self, base: NodeId) -> Option<String> {
        Some(format!("{}.iterator()", self.atom(base)?))
    }

    /// 由字面量初值粗略推断 `fold` 的累加器类型实参。
    fn lit_type(&self, id: NodeId) -> String {
        match self.g.kind(id) {
            Kind::FloatLit(_) => "Float64".to_string(),
            Kind::BoolLit(_) => "Bool".to_string(),
            Kind::StrTemplate { .. } => "String".to_string(),
            _ => "Int64".to_string(),
        }
    }

    /// 映射后的类型字符串是否为集合类型（用于判断能否套用集合高阶/聚合操作）。
    fn is_coll_type(t: &str) -> bool {
        let t = t.trim_start_matches('?');
        t.starts_with("ArrayList")
            || t.starts_with("HashSet")
            || t.starts_with("HashMap")
            || t.starts_with("Array<")
            || t == "Array"
    }

    /// 名为 `name` 的成员函数（自由函数或类方法）的返回类型是否为集合。
    fn func_ret_is_coll(&self, name: &str) -> bool {
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
    fn expr_type_name(&self, id: NodeId) -> Option<String> {
        if let Kind::NameRef { decl: Some(d), .. } = self.g.kind(id) {
            for node in &self.g.nodes {
                match &node.kind {
                    Kind::VarDecl { name_node, ty, init, .. } if name_node == d => {
                        if let Some(t) = ty {
                            return Some(t.clone());
                        }
                        // `let v = ClassName(...)` → 由构造器调用回填类名。
                        if let Some(i) = init {
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
                    Kind::Param { name_node, ty } if name_node == d => {
                        return Some(ty.clone());
                    }
                    _ => {}
                }
            }
        }
        None
    }

    /// 图中是否存在名为 `name` 的类声明。
    fn is_class_name(&self, name: &str) -> bool {
        self.g.nodes.iter().any(|n| matches!(&n.kind, Kind::Class { name: cn, .. } if cn == name))
    }

    /// 图中是否存在名为 `name` 的用户函数声明（用于避免覆盖同名自定义函数）。
    fn is_user_func(&self, name: &str) -> bool {
        self.g.nodes.iter().any(|n| matches!(&n.kind, Kind::Func { name: fname, .. } if fname == name))
    }

    /// 成员字段 `base.field` 是否为集合类型（解析 base 的类与字段声明）。
    fn member_is_collection(&self, base: NodeId, field: &str) -> bool {
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

    /// 启发式判断表达式是否求值为集合（列表/数组/区间），用于安全地套用
    /// 集合专属的高阶与聚合方法，避免误改用户自定义同名方法（如 `count()`）。
    fn looks_collection(&self, id: NodeId) -> bool {
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
                        Kind::Param { name_node, ty } if name_node == d => {
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

    /// 解析成员字段 `base.field` 是否为集合：Some(true)=集合、Some(false)=非集合、None=无法判定。
    fn member_field_collection(&self, base: NodeId, field: &str) -> Option<bool> {
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
    /// 用于保守地放行集合高阶方法——未知类型一律允许改写（覆盖循环变量、map 视图等），
    /// 仅在接收者确为用户类/标量/字符串时阻止，避免误改同名自定义方法（如 `count()`）。
    fn provably_non_collection(&self, id: NodeId) -> bool {
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
                // 构造器调用 `ClassName(...)` → 用户对象，确为非集合（非集合容器构造器）。
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
                            return false; // 循环变量等：类型未知，放行
                        }
                        Kind::Param { name_node, ty } if *name_node == d => {
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

    /// 启发式判断表达式是否为字符串（用于把 `for (c in s)` 改写为遍历 `s.runes()`）。
    fn looks_string(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::StrTemplate { .. } => true,
            Kind::NameRef { decl: Some(d), .. } => {
                let d = *d;
                for node in &self.g.nodes {
                    match &node.kind {
                        Kind::VarDecl { name_node, ty, init, .. } if *name_node == d => {
                            if let Some(t) = ty {
                                return t == "String";
                            }
                            if let Some(i) = init {
                                return matches!(self.g.kind(*i), Kind::StrTemplate { .. });
                            }
                            return false;
                        }
                        Kind::Param { name_node, ty } if *name_node == d => {
                            return ty == "String";
                        }
                        _ => {}
                    }
                }
                false
            }
            _ => false,
        }
    }

    /// 成员检查 `x in rhs`：区间转比较，集合转 contains。
    fn render_in(&self, lhs: NodeId, rhs: NodeId) -> Option<String> {
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

    /// 粗略判断表达式是否为数值类型（用于 `toInt`/`toDouble` 转换分流）。
    fn looks_numeric(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::IntLit(_) | Kind::FloatLit(_) => true,
            Kind::Unary { expr, .. } => self.looks_numeric(*expr),
            Kind::Binary { op, .. } => matches!(op.as_str(), "+" | "-" | "*" | "/" | "%"),
            // 数值结果的成员访问/调用（.size/.length、聚合与数值转换）。
            Kind::Member { name, .. } => matches!(name.as_str(), "size" | "length"),
            Kind::Call { callee, .. } => {
                if let Kind::Member { name, .. } = self.g.kind(*callee) {
                    matches!(
                        name.as_str(),
                        "sum" | "sumOf" | "count" | "size" | "length"
                            | "max" | "min" | "toInt" | "toLong" | "toDouble" | "toFloat"
                    )
                } else if let Kind::NameRef { original, .. } = self.g.kind(*callee) {
                    matches!(original.as_str(), "maxOf" | "minOf")
                } else {
                    false
                }
            }
            Kind::NameRef { decl: Some(d), .. } => {
                if let Kind::Name { .. } = self.g.kind(*d) {
                    // 找到声明它的 VarDecl/Param，检查映射后的类型。
                    self.decl_is_numeric(*d)
                } else {
                    false
                }
            }
            _ => false,
        }
    }

    /// 启发式判断表达式是否求值为元组（Kotlin 的 Pair/Triple / `a to b`）。
    fn looks_tuple(&self, id: NodeId) -> bool {
        match self.g.kind(id) {
            Kind::Binary { op, .. } => op == "to",
            Kind::Call { callee, .. } => {
                matches!(self.g.kind(*callee), Kind::NameRef { original, .. } if original == "Pair" || original == "Triple")
            }
            Kind::NameRef { decl: Some(d), .. } => {
                for node in &self.g.nodes {
                    match &node.kind {
                        Kind::VarDecl { name_node, ty, init, .. } if name_node == d => {
                            if let Some(t) = ty {
                                return t.trim_start_matches('?').starts_with('(');
                            }
                            if let Some(i) = init {
                                return self.looks_tuple(*i);
                            }
                            return false;
                        }
                        Kind::Param { name_node, ty } if name_node == d => {
                            return ty.trim_start_matches('?').starts_with('(');
                        }
                        _ => {}
                    }
                }
                false
            }
            _ => false,
        }
    }

    /// 启发式判断表达式是否求值为浮点数（用于补显式 Int64→Float64 提升）。
    fn looks_float(&self, id: NodeId) -> bool {        match self.g.kind(id) {
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

    /// 检查某 Name 节点所属声明是否为浮点类型（按显式类型或初值推断）。
    fn decl_is_float(&self, name_node: NodeId) -> bool {
        for node in &self.g.nodes {
            match &node.kind {
                Kind::VarDecl { name_node: nn, ty: Some(t), .. } if *nn == name_node => {
                    return t == "Float64" || t == "Float32";
                }
                Kind::VarDecl { name_node: nn, ty: None, init: Some(i), .. } if *nn == name_node => {
                    return self.looks_float(*i);
                }
                Kind::Param { name_node: nn, ty } if *nn == name_node => {
                    return ty == "Float64" || ty == "Float32";
                }
                _ => {}
            }
        }
        false
    }

    /// 检查某 Name 节点所属声明的类型是否为数值类型。
    fn decl_is_numeric(&self, name_node: NodeId) -> bool {
        for node in &self.g.nodes {
            match &node.kind {
                Kind::VarDecl { name_node: nn, ty: Some(t), .. } if *nn == name_node => {
                    return t == "Int64" || t == "Float64";
                }
                // 无显式类型时由初值表达式推断（如 `val total = xs.sum()`）。
                Kind::VarDecl { name_node: nn, ty: None, init: Some(i), .. } if *nn == name_node => {
                    return self.looks_numeric(*i);
                }
                Kind::Param { name_node: nn, ty } if *nn == name_node => {
                    return ty == "Int64" || ty == "Float64";
                }
                _ => {}
            }
        }
        false
    }

    /// 判断子树中是否使用了隐式 lambda 参数 `it`。
    fn uses_it(&self, id: NodeId) -> bool {
        if let Kind::NameRef { original, .. } = self.g.kind(id) {
            if original == "it" {
                return true;
            }
        }
        // Lambda 内部若有自己的 it 绑定，这里仍可能误判，但 kotlin 中嵌套 it 罕见。
        for c in self.g.children_of(id) {
            if self.uses_it(c) {
                return true;
            }
        }
        false
    }

    fn render_program(&self, items: &[NodeId]) -> Option<String> {
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
                // 顶层变量声明 → 全局常量/变量，置于 main 之前以便函数引用。
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
        // 按需注入导入
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
fn indent(s: &str, n: usize) -> String {
    let pad = IND.repeat(n);
    s.lines()
        .map(|l| if l.is_empty() { String::new() } else { format!("{}{}", pad, l) })
        .collect::<Vec<_>>()
        .join("\n")
}
