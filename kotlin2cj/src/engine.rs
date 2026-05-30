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
                    let la = self.atom(lhs)?;
                    let ra = self.atom(rhs)?;
                    return Some(format!("{} ?? {}", la, ra));
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
            Kind::Member { base, name } => {
                let b = self.atom(base)?;
                let mapped = match name.as_str() {
                    "length" => "size",
                    "toUpperCase" | "uppercase" => "toAsciiUpper",
                    "toLowerCase" | "lowercase" => "toAsciiLower",
                    "trim" => "trimAscii",
                    "trimStart" => "trimAsciiStart",
                    "trimEnd" => "trimAsciiEnd",
                    other => other,
                };
                Some(format!("{}.{}", b, mapped))
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
                    "=>".to_string()
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
            Kind::ForRange { var, range, body } => {
                let vn = self.loop_var_name(var)?;
                Some(format!("for ({} in {}) {}", vn, self.t(range)?, self.render_block(body)?))
            }
            Kind::ForEach { var, iter, body } => {
                let vn = self.loop_var_name(var)?;
                Some(format!("for ({} in {}) {}", vn, self.t(iter)?, self.render_block(body)?))
            }
            Kind::When { subject, arms } => self.render_when(subject, &arms),
            Kind::Block { .. } => self.render_block(id),

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
            Kind::Class { name, ctor_params, members } => {
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
                if body.is_empty() {
                    Some(format!("class {} {{}}", name))
                } else {
                    Some(format!("class {} {{\n{}}}", name, body))
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
                let mut body = String::new();
                for a in arms {
                    let arm_body = self.render_arm_body(a.body)?;
                    match &a.patterns {
                        Some(ps) => {
                            let pts: Vec<String> = ps.iter().map(|p| self.t(*p)).collect::<Option<_>>()?;
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
        let c = self.atom(callee)?;
        let a: Vec<String> = args.iter().map(|x| self.t(*x)).collect::<Option<_>>()?;
        Some(format!("{}({})", c, a.join(", ")))
    }

    fn render_program(&self, items: &[NodeId]) -> Option<String> {
        let mut decls = Vec::new();
        let mut loose = Vec::new();
        let mut has_main = false;
        for it in items {
            match self.g.kind(*it) {
                Kind::Func { is_main, .. } => {
                    if *is_main {
                        has_main = true;
                    }
                    decls.push(self.t(*it)?);
                }
                Kind::Class { .. } => decls.push(self.t(*it)?),
                _ => loose.push(self.t(*it)?),
            }
        }
        let mut body = decls.join("\n\n");
        if !loose.is_empty() && !has_main {
            let main_body = loose.join("\n");
            body.push_str(&format!("\n\nmain() {{\n{}\n}}", indent(&main_body, 1)));
        } else if !loose.is_empty() {
            body.push_str("\n\n");
            body.push_str(&loose.join("\n"));
        }
        // 按需注入集合导入
        let mut header = String::new();
        if body.contains("ArrayList") || body.contains("HashMap") || body.contains("HashSet") {
            header.push_str("import std.collection.*\n\n");
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
