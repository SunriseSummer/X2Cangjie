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
                    let ps: Vec<String> = params.iter().map(|p| crate::parser::safe_name(p)).collect();
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
                Some(format!("for ({} in {}) {}", vn, self.t(iter)?, self.render_block(body)?))
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
                    Some(format!("@Derive[Equatable]\nenum {} {{\n{}| {}\n}}", name, IND, body))
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
            // maxOf(a, b) / minOf(a, b) → 内联条件表达式（不依赖标准库符号）。
            if (original == "maxOf" || original == "minOf") && args.len() == 2 {
                let a = self.t(args[0])?;
                let b = self.t(args[1])?;
                let cmp = if original == "maxOf" { ">" } else { "<" };
                return Some(format!("(if ({} {} {}) {{ {} }} else {{ {} }})", a, cmp, b, a, b));
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
                // List<String>.joinToString(sep?) { transform? }
                //   → String.join(xs.toArray(), delimiter: sep)
                //   带 transform 时先 map 成字符串再收集为数组。
                "joinToString" => {
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
                    return Some(format!("String.join({}.toArray(), delimiter: {})", b, sep));
                }
                // 返回集合的链式高阶：map/filter 急切收集为 ArrayList，
                // 既可继续链接、在 for 中遍历，也可存入变量后多次复用 / 取 size / 索引。
                "map" | "filter" if args.len() == 1 => {
                    return Some(format!(
                        "collectArrayList({}.{}({}))",
                        self.as_iter(*base)?, name, self.t(args[0])?
                    ));
                }
                // 布尔终结操作。
                "any" | "all" if args.len() == 1 => {
                    return Some(format!("{}.{}({})", self.as_iter(*base)?, name, self.t(args[0])?));
                }
                "none" if args.len() == 1 => {
                    return Some(format!("!{}.any({})", self.as_iter(*base)?, self.t(args[0])?));
                }
                // 计数：带谓词时先 filter，再 count；无参时即 size。
                "count" if args.len() == 1 => {
                    return Some(format!("{}.filter({}).count()", self.as_iter(*base)?, self.t(args[0])?));
                }
                "count" if args.is_empty() => {
                    return Some(format!("{}.size", b));
                }
                // 求和：sum() 直接折叠；sumOf { } 先 map 再折叠（按 Int64 处理）。
                "sum" if args.is_empty() => {
                    return Some(format!("{}.fold<Int64>(0, {{acc, x => acc + x}})", self.as_iter(*base)?));
                }
                "sumOf" if args.len() == 1 => {
                    return Some(format!(
                        "{}.map({}).fold<Int64>(0, {{acc, x => acc + x}})",
                        self.as_iter(*base)?,
                        self.t(args[0])?
                    ));
                }
                // fold(init) { acc, x -> } → iterator().fold<T>(init, lambda)，T 由 init 字面量推断。
                "fold" if args.len() == 2 => {
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
                "reduce" if args.len() == 1 => {
                    return Some(format!("{}.reduce({}).getOrThrow()", self.as_iter(*base)?, self.t(args[0])?));
                }
                // max()/min()：折叠取极值并解包；maxOrNull()/minOrNull() 保留 Option 以便 `?:` 级联。
                "max" | "min" if args.is_empty() => {
                    let cmp = if name == "max" { ">" } else { "<" };
                    return Some(format!(
                        "{}.reduce({{a, b => if (a {} b) {{ a }} else {{ b }}}}).getOrThrow()",
                        self.as_iter(*base)?, cmp
                    ));
                }
                "maxOrNull" | "minOrNull" if args.is_empty() => {
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

    /// 检查某 Name 节点所属声明的类型是否为数值类型。
    fn decl_is_numeric(&self, name_node: NodeId) -> bool {
        for node in &self.g.nodes {
            match &node.kind {
                Kind::VarDecl { name_node: nn, ty: Some(t), .. } if *nn == name_node => {
                    return t == "Int64" || t == "Float64";
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
