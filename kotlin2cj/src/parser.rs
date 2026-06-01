//! Kotlin 子集递归下降解析器：把 Token 流构造为翻译图（[`Graph`]）。
//!
//! 解析过程中同时完成：
//!   * Kotlin 类型 → 仓颉类型映射；
//!   * 词法作用域内的标识符引用解析（建立依赖边，支撑重命名雪崩）。

use crate::lexer::{StrPart, Tok, Token};
use crate::node::*;
use std::collections::HashMap;

pub struct Parser {
    toks: Vec<Token>,
    pos: usize,
    pub g: Graph,
    scopes: Vec<HashMap<String, NodeId>>, // name -> Name 节点
}

type PResult<T> = Result<T, String>;

impl Parser {
    pub fn new(toks: Vec<Token>) -> Self {
        Parser { toks, pos: 0, g: Graph::new(), scopes: vec![HashMap::new()] }
    }

    // ---- Token 游标 ----
    fn peek(&self) -> &Tok {
        &self.toks[self.pos].tok
    }
    fn line(&self) -> usize {
        self.toks[self.pos].line
    }
    fn at_eof(&self) -> bool {
        matches!(self.peek(), Tok::Eof)
    }
    fn bump(&mut self) -> Tok {
        let t = self.toks[self.pos].tok.clone();
        if self.pos + 1 < self.toks.len() {
            self.pos += 1;
        }
        t
    }
    fn is_sym(&self, s: &str) -> bool {
        matches!(self.peek(), Tok::Sym(x) if x == s)
    }
    fn is_kw(&self, s: &str) -> bool {
        matches!(self.peek(), Tok::Ident(x) if x == s)
    }
    fn eat_sym(&mut self, s: &str) -> bool {
        if self.is_sym(s) {
            self.bump();
            true
        } else {
            false
        }
    }
    fn expect_sym(&mut self, s: &str) -> PResult<()> {
        if self.eat_sym(s) {
            Ok(())
        } else {
            Err(format!("line {}: 期望 '{}'，但得到 {:?}", self.line(), s, self.peek()))
        }
    }
    fn eat_kw(&mut self, s: &str) -> bool {
        if self.is_kw(s) {
            self.bump();
            true
        } else {
            false
        }
    }
    fn skip_newlines(&mut self) {
        while matches!(self.peek(), Tok::Newline) {
            self.bump();
        }
    }
    fn skip_seps(&mut self) {
        while matches!(self.peek(), Tok::Newline) || self.is_sym(";") {
            self.bump();
        }
    }

    // ---- 作用域 ----
    fn push_scope(&mut self) {
        self.scopes.push(HashMap::new());
    }
    fn pop_scope(&mut self) {
        self.scopes.pop();
    }
    fn declare(&mut self, name: &str, node: NodeId) {
        self.scopes.last_mut().unwrap().insert(name.to_string(), node);
    }
    fn resolve(&self, name: &str) -> Option<NodeId> {
        for s in self.scopes.iter().rev() {
            if let Some(id) = s.get(name) {
                return Some(*id);
            }
        }
        None
    }

    // ================= 顶层 =================
    pub fn parse_program(&mut self) -> PResult<NodeId> {
        let mut items = Vec::new();
        self.skip_seps();
        while !self.at_eof() {
            // 跳过 Kotlin 的 package / import 行（仓颉侧自管导入）。
            if matches!(self.peek(), Tok::Ident(x) if x == "import" || x == "package") {
                while !matches!(self.peek(), Tok::Newline | Tok::Eof) {
                    self.bump();
                }
                self.skip_seps();
                continue;
            }
            let item = self.parse_top_level()?;
            items.push(item);
            self.skip_seps();
        }
        let root = self.g.add(Kind::Program { items });
        self.g.root = root;
        Ok(root)
    }

    fn parse_top_level(&mut self) -> PResult<NodeId> {
        // 跳过可见性 / 修饰符
        let mods = self.skip_modifiers();
        if self.is_kw("fun") {
            self.parse_fun()
        } else if self.is_kw("enum") {
            self.parse_enum()
        } else if self.is_kw("class") || self.is_kw("data") || self.is_kw("object") {
            self.parse_class(&mods)
        } else {
            // 顶层语句（少见）——并入隐式块
            self.parse_statement()
        }
    }

    fn skip_modifiers(&mut self) -> Vec<String> {
        const MODS: &[&str] = &[
            "public", "private", "internal", "protected", "open", "final", "abstract",
            "override", "inline", "data", "sealed", "const", "lateinit", "companion",
        ];
        let mut seen = Vec::new();
        loop {
            let mut matched = false;
            if let Tok::Ident(x) = self.peek() {
                if MODS.contains(&x.as_str()) && x != "data" && x != "const" {
                    seen.push(x.clone());
                    self.bump();
                    matched = true;
                }
            }
            if !matched {
                break;
            }
        }
        seen
    }

    // ---- 函数 ----
    fn parse_fun(&mut self) -> PResult<NodeId> {
        self.eat_kw("fun");
        let name = self.expect_ident()?;
        self.push_scope();
        let mut params = Vec::new();
        self.expect_sym("(")?;
        self.skip_newlines();
        while !self.is_sym(")") {
            let pname = self.expect_ident()?;
            self.expect_sym(":")?;
            let ty = self.parse_type()?;
            let nn = self.g.add(Kind::Name { original: pname.clone() });
            let pid = self.g.add(Kind::Param { name_node: nn, ty });
            self.declare(&pname, nn);
            params.push(pid);
            self.skip_newlines();
            if !self.eat_sym(",") {
                break;
            }
            self.skip_newlines();
        }
        self.expect_sym(")")?;
        let mut ret = None;
        if self.eat_sym(":") {
            ret = Some(self.parse_type()?);
        }
        // 函数体：块 或 `= expr`
        let body;
        if self.eat_sym("=") {
            self.skip_newlines();
            let e = self.parse_expr()?;
            let r = self.g.add(Kind::Return { value: Some(e) });
            body = self.g.add(Kind::Block { stmts: vec![r] });
        } else {
            body = self.parse_block()?;
        }
        self.pop_scope();
        let is_main = name == "main";
        let ret = if is_main { None } else { ret };
        Ok(self.g.add(Kind::Func { name: safe_name(&name), params, ret, body, is_main }))
    }

    // ---- 枚举 ----
    fn parse_enum(&mut self) -> PResult<NodeId> {
        self.eat_kw("enum");
        // `enum class Name { A, B, C }`
        self.eat_kw("class");
        let name = self.expect_ident()?;
        self.skip_newlines();
        self.expect_sym("{")?;
        self.skip_seps();
        let mut entries = Vec::new();
        // 解析具名枚举项，直到 `}` 或成员分隔 `;`
        while !self.is_sym("}") && !self.is_sym(";") && !self.at_eof() {
            let entry = self.expect_ident()?;
            entries.push(entry);
            // 忽略枚举项可能携带的构造实参，如 RED(0xFF)
            if self.is_sym("(") {
                self.skip_balanced_parens();
            }
            self.skip_newlines();
            if !self.eat_sym(",") {
                break;
            }
            self.skip_seps();
        }
        // 跳过枚举体其余部分（成员函数等暂不支持）
        let mut depth = 1;
        while depth > 0 && !self.at_eof() {
            if self.is_sym("{") {
                depth += 1;
            } else if self.is_sym("}") {
                depth -= 1;
                if depth == 0 {
                    break;
                }
            }
            self.bump();
        }
        self.expect_sym("}")?;
        Ok(self.g.add(Kind::Enum { name: safe_name(&name), entries }))
    }

    fn skip_balanced_parens(&mut self) {
        if !self.eat_sym("(") {
            return;
        }
        let mut depth = 1;
        while depth > 0 && !self.at_eof() {
            if self.is_sym("(") {
                depth += 1;
            } else if self.is_sym(")") {
                depth -= 1;
            }
            self.bump();
        }
    }

    // ---- 类 ----
    fn parse_class(&mut self, mods: &[String]) -> PResult<NodeId> {
        let is_data = self.eat_kw("data");
        let _ = is_data;
        let is_object = self.is_kw("object");
        self.bump(); // class / object
        let name = self.expect_ident()?;
        // 跳过泛型形参 `<T>`
        if self.is_sym("<") {
            let mut depth = 0;
            loop {
                if self.is_sym("<") {
                    depth += 1;
                } else if self.is_sym(">") {
                    depth -= 1;
                    if depth == 0 {
                        self.bump();
                        break;
                    }
                } else if self.at_eof() {
                    break;
                }
                self.bump();
            }
        }
        let mut ctor_params = Vec::new();
        if self.eat_sym("(") {
            self.skip_newlines();
            while !self.is_sym(")") {
                self.skip_modifiers();
                let kind = if self.eat_kw("val") {
                    CtorParamKind::Val
                } else if self.eat_kw("var") {
                    CtorParamKind::Var
                } else {
                    CtorParamKind::Plain
                };
                let pname = self.expect_ident()?;
                self.expect_sym(":")?;
                let ty = self.parse_type()?;
                // 跳过默认值
                if self.eat_sym("=") {
                    self.parse_expr()?;
                }
                ctor_params.push(CtorParam { kind, name: safe_name(&pname), ty });
                self.skip_newlines();
                if !self.eat_sym(",") {
                    break;
                }
                self.skip_newlines();
            }
            self.expect_sym(")")?;
        }
        // 继承列表：捕获首个父类名（忽略接口/构造实参）。
        let mut superclass = None;
        if self.eat_sym(":") {
            if let Tok::Ident(sup) = self.peek().clone() {
                self.bump();
                superclass = Some(safe_name(&sup));
            }
            while !self.is_sym("{") && !matches!(self.peek(), Tok::Newline | Tok::Eof) {
                self.bump();
            }
        }
        let mut members = Vec::new();
        self.skip_newlines();
        if self.eat_sym("{") {
            self.push_scope();
            // 让构造参数在成员体内可见
            self.skip_seps();
            while !self.is_sym("}") && !self.at_eof() {
                self.skip_modifiers();
                if self.is_kw("fun") {
                    members.push(self.parse_fun()?);
                } else if self.is_kw("val") || self.is_kw("var") {
                    members.push(self.parse_var_decl()?);
                } else if self.is_kw("init") {
                    // init 块：跳过（构造参数已声明成员）
                    self.bump();
                    self.parse_block()?;
                } else if self.is_kw("companion") || self.is_kw("class") || self.is_kw("object") {
                    self.bump();
                    if self.is_sym("{") {
                        self.parse_block()?;
                    }
                } else {
                    self.bump();
                }
                self.skip_seps();
            }
            self.expect_sym("}")?;
            self.pop_scope();
        }
        let _ = is_object;
        let is_open = mods.iter().any(|m| m == "open" || m == "abstract" || m == "sealed");
        Ok(self.g.add(Kind::Class { name: safe_name(&name), ctor_params, members, superclass, is_open }))
    }

    // ================= 语句 =================
    fn parse_block(&mut self) -> PResult<NodeId> {
        self.expect_sym("{")?;
        self.push_scope();
        let mut stmts = Vec::new();
        self.skip_seps();
        while !self.is_sym("}") && !self.at_eof() {
            let s = self.parse_statement()?;
            stmts.push(s);
            self.skip_seps();
        }
        self.expect_sym("}")?;
        self.pop_scope();
        Ok(self.g.add(Kind::Block { stmts }))
    }

    fn parse_statement(&mut self) -> PResult<NodeId> {
        self.skip_modifiers();
        if self.is_kw("val") || self.is_kw("var") {
            return self.parse_var_decl();
        }
        if self.is_kw("return") {
            self.bump();
            if matches!(self.peek(), Tok::Newline | Tok::Eof) || self.is_sym("}") || self.is_sym(";") {
                return Ok(self.g.add(Kind::Return { value: None }));
            }
            let e = self.parse_expr()?;
            return Ok(self.g.add(Kind::Return { value: Some(e) }));
        }
        if self.is_kw("throw") {
            self.bump();
            let e = self.parse_expr()?;
            return Ok(self.g.add(Kind::Throw { value: e }));
        }
        if self.is_kw("while") {
            return self.parse_while();
        }
        if self.is_kw("do") {
            return self.parse_do_while();
        }
        if self.is_kw("try") {
            return self.parse_try();
        }
        if self.is_kw("for") {
            return self.parse_for();
        }
        if self.is_kw("break") {
            self.bump();
            return Ok(self.g.add(Kind::Raw("break".into())));
        }
        if self.is_kw("continue") {
            self.bump();
            return Ok(self.g.add(Kind::Raw("continue".into())));
        }
        if self.is_kw("fun") {
            return self.parse_fun();
        }
        // 表达式语句 / 赋值
        let e = self.parse_expr()?;
        if self.is_sym("++") || self.is_sym("--") {
            let op = if self.is_sym("++") { "+=" } else { "-=" };
            self.bump();
            let one = self.g.add(Kind::IntLit("1".into()));
            return Ok(self.g.add(Kind::Assign { target: e, op: op.into(), value: one }));
        }
        if let Tok::Sym(op) = self.peek().clone() {
            if matches!(op.as_str(), "=" | "+=" | "-=" | "*=" | "/=" | "%=") {
                self.bump();
                self.skip_newlines();
                let val = self.parse_expr()?;
                return Ok(self.g.add(Kind::Assign { target: e, op, value: val }));
            }
        }
        Ok(self.g.add(Kind::ExprStmt { expr: e }))
    }

    fn parse_var_decl(&mut self) -> PResult<NodeId> {
        let mutable = if self.eat_kw("var") {
            true
        } else {
            self.eat_kw("val");
            false
        };
        // 解构声明 `val (a, b) = expr`
        if self.is_sym("(") {
            self.bump();
            let mut name_nodes = Vec::new();
            loop {
                let nm = self.expect_ident()?;
                // 跳过可选类型标注 `a: T`
                if self.eat_sym(":") {
                    self.parse_type()?;
                }
                let nn = self.g.add(Kind::Name { original: nm.clone() });
                name_nodes.push((nm, nn));
                if !self.eat_sym(",") {
                    break;
                }
                self.skip_newlines();
            }
            self.expect_sym(")")?;
            self.expect_sym("=")?;
            self.skip_newlines();
            let init = self.parse_expr()?;
            for (nm, nn) in &name_nodes {
                self.declare(nm, *nn);
            }
            let names: Vec<NodeId> = name_nodes.into_iter().map(|(_, nn)| nn).collect();
            return Ok(self.g.add(Kind::DestructureDecl { mutable, names, init }));
        }
        let name = self.expect_ident()?;
        let mut ty = None;
        if self.eat_sym(":") {
            ty = Some(self.parse_type()?);
        }
        let mut init = None;
        if self.eat_sym("=") {
            self.skip_newlines();
            init = Some(self.parse_expr()?);
        }
        let name_node = self.g.add(Kind::Name { original: name.clone() });
        self.declare(&name, name_node);
        Ok(self.g.add(Kind::VarDecl { mutable, name_node, ty, init }))
    }

    fn parse_while(&mut self) -> PResult<NodeId> {
        self.eat_kw("while");
        self.expect_sym("(")?;
        let cond = self.parse_expr()?;
        self.expect_sym(")")?;
        self.skip_newlines();
        let body = self.parse_block_or_stmt()?;
        Ok(self.g.add(Kind::While { cond, body }))
    }

    fn parse_do_while(&mut self) -> PResult<NodeId> {
        self.eat_kw("do");
        self.skip_newlines();
        let body = self.parse_block_or_stmt()?;
        self.skip_newlines();
        if !self.eat_kw("while") {
            return Err(format!("line {}: do 之后期望 while", self.line()));
        }
        self.expect_sym("(")?;
        let cond = self.parse_expr()?;
        self.expect_sym(")")?;
        Ok(self.g.add(Kind::DoWhile { body, cond }))
    }

    fn parse_try(&mut self) -> PResult<NodeId> {
        self.eat_kw("try");
        self.skip_newlines();
        let body = self.parse_block()?;
        let mut catches = Vec::new();
        let mut finally = None;
        loop {
            self.skip_newlines_for_kw("catch");
            self.skip_newlines_for_kw("finally");
            if self.eat_kw("catch") {
                self.expect_sym("(")?;
                let name = self.expect_ident()?;
                self.expect_sym(":")?;
                let ty = self.parse_type()?;
                self.expect_sym(")")?;
                self.skip_newlines();
                self.push_scope();
                let nn = self.g.add(Kind::Name { original: name.clone() });
                self.declare(&name, nn);
                let cbody = self.parse_block()?;
                self.pop_scope();
                catches.push(CatchClause { name: safe_name(&name), ty, body: cbody });
            } else if self.eat_kw("finally") {
                self.skip_newlines();
                finally = Some(self.parse_block()?);
                break;
            } else {
                break;
            }
        }
        Ok(self.g.add(Kind::Try { body, catches, finally }))
    }

    fn skip_newlines_for_kw(&mut self, kw: &str) {
        let save = self.pos;
        self.skip_newlines();
        if !self.is_kw(kw) {
            self.pos = save;
        }
    }

    fn parse_for(&mut self) -> PResult<NodeId> {
        self.eat_kw("for");
        self.expect_sym("(")?;
        self.push_scope();
        // 解构循环变量：for ((k, v) in m)
        if self.is_sym("(") {
            self.bump();
            let mut name_nodes = Vec::new();
            loop {
                let nm = self.expect_ident()?;
                let nn = self.g.add(Kind::Name { original: nm.clone() });
                self.declare(&nm, nn);
                name_nodes.push(nn);
                if !self.eat_sym(",") {
                    break;
                }
                self.skip_newlines();
            }
            self.expect_sym(")")?;
            self.eat_kw("in");
            let var = self.g.add(Kind::Destructure { names: name_nodes });
            let iter_expr = self.parse_expr()?;
            self.expect_sym(")")?;
            self.skip_newlines();
            let body = self.parse_block_or_stmt()?;
            self.pop_scope();
            return Ok(self.g.add(Kind::ForEach { var, iter: iter_expr, body }));
        }
        let var_name = self.expect_ident()?;
        self.eat_kw("in");
        let var_node = self.g.add(Kind::Name { original: var_name.clone() });
        self.declare(&var_name, var_node);
        let var = self.g.add(Kind::VarDecl {
            mutable: false,
            name_node: var_node,
            ty: None,
            init: None,
        });
        // 区间 or 可迭代对象
        let iter_expr = self.parse_expr()?;
        self.expect_sym(")")?;
        self.skip_newlines();
        let body = self.parse_block_or_stmt()?;
        self.pop_scope();
        if matches!(self.g.kind(iter_expr), Kind::Range { .. }) {
            Ok(self.g.add(Kind::ForRange { var, range: iter_expr, body }))
        } else {
            Ok(self.g.add(Kind::ForEach { var, iter: iter_expr, body }))
        }
    }

    fn parse_block_or_stmt(&mut self) -> PResult<NodeId> {
        if self.is_sym("{") {
            self.parse_block()
        } else {
            let s = self.parse_statement()?;
            Ok(self.g.add(Kind::Block { stmts: vec![s] }))
        }
    }

    // ================= 表达式 =================
    fn parse_expr(&mut self) -> PResult<NodeId> {
        self.parse_or()
    }

    fn parse_binary_level(
        &mut self,
        ops: &[&str],
        next: fn(&mut Self) -> PResult<NodeId>,
    ) -> PResult<NodeId> {
        let mut lhs = next(self)?;
        loop {
            let mut matched = None;
            if let Tok::Sym(s) = self.peek() {
                if ops.contains(&s.as_str()) {
                    matched = Some(s.clone());
                }
            }
            match matched {
                Some(op) => {
                    self.bump();
                    self.skip_newlines();
                    let rhs = next(self)?;
                    lhs = self.g.add(Kind::Binary { op, lhs, rhs });
                }
                None => break,
            }
        }
        Ok(lhs)
    }

    fn parse_or(&mut self) -> PResult<NodeId> {
        self.parse_binary_level(&["||"], Self::parse_and)
    }
    fn parse_and(&mut self) -> PResult<NodeId> {
        self.parse_binary_level(&["&&"], Self::parse_equality)
    }
    fn parse_equality(&mut self) -> PResult<NodeId> {
        self.parse_binary_level(&["==", "!="], Self::parse_comparison)
    }
    fn parse_comparison(&mut self) -> PResult<NodeId> {
        self.parse_binary_level(&["<", "<=", ">", ">="], Self::parse_named_checks)
    }
    /// Kotlin 的 `in` / `!in` 成员检查与 `is` / `!is` 类型判定
    /// （优先级介于比较与 elvis 之间）。
    fn parse_named_checks(&mut self) -> PResult<NodeId> {
        let mut lhs = self.parse_elvis()?;
        loop {
            // `is T` / `!is T` 类型判定
            if self.is_kw("is") {
                self.bump();
                let ty = self.parse_type()?;
                lhs = self.g.add(Kind::IsCheck { expr: lhs, ty, negate: false });
                continue;
            }
            if self.is_sym("!") && self.peek_next_is_kw("is") {
                self.bump(); // !
                self.bump(); // is
                let ty = self.parse_type()?;
                lhs = self.g.add(Kind::IsCheck { expr: lhs, ty, negate: true });
                continue;
            }
            let negate = if self.is_sym("!") && self.peek_next_is_kw("in") {
                self.bump(); // !
                true
            } else {
                false
            };
            if self.is_kw("in") {
                self.bump();
                self.skip_newlines();
                let rhs = self.parse_elvis()?;
                let op = if negate { "!in" } else { "in" };
                lhs = self.g.add(Kind::Binary { op: op.into(), lhs, rhs });
            } else {
                if negate {
                    // 回退：把消费掉的 `!` 当作错误，理论上不会到这里
                }
                break;
            }
        }
        Ok(lhs)
    }
    fn parse_elvis(&mut self) -> PResult<NodeId> {
        self.parse_binary_level(&["?:"], Self::parse_to)
    }

    fn parse_to(&mut self) -> PResult<NodeId> {
        let mut lhs = self.parse_range()?;
        loop {
            if self.is_kw("to") {
                self.bump();
                self.skip_newlines();
                let rhs = self.parse_range()?;
                lhs = self.g.add(Kind::Binary { op: "to".into(), lhs, rhs });
                continue;
            }
            // 命名中缀位运算：and / or / xor / shl / shr / ushr
            let mapped = match self.peek() {
                Tok::Ident(x) => match x.as_str() {
                    "and" => Some("&"),
                    "or" => Some("|"),
                    "xor" => Some("^"),
                    "shl" => Some("<<"),
                    "shr" | "ushr" => Some(">>"),
                    _ => None,
                },
                _ => None,
            };
            if let Some(op) = mapped {
                self.bump();
                self.skip_newlines();
                let rhs = self.parse_range()?;
                lhs = self.g.add(Kind::Binary { op: op.into(), lhs, rhs });
                continue;
            }
            break;
        }
        Ok(lhs)
    }

    fn parse_range(&mut self) -> PResult<NodeId> {
        let lo = self.parse_additive()?;
        // a..b / a until b / a downTo b (可带 step)
        let (inclusive, down, is_range) = if self.is_sym("..") {
            self.bump();
            (true, false, true)
        } else if self.is_kw("until") {
            self.bump();
            (false, false, true)
        } else if self.is_kw("downTo") {
            self.bump();
            (true, true, true)
        } else {
            (false, false, false)
        };
        if !is_range {
            return Ok(lo);
        }
        self.skip_newlines();
        let hi = self.parse_additive()?;
        let mut step = None;
        if self.eat_kw("step") {
            step = Some(self.parse_additive()?);
        }
        Ok(self.g.add(Kind::Range { lo, hi, inclusive, down, step }))
    }

    fn parse_additive(&mut self) -> PResult<NodeId> {
        self.parse_binary_level(&["+", "-"], Self::parse_multiplicative)
    }
    fn parse_multiplicative(&mut self) -> PResult<NodeId> {
        self.parse_binary_level(&["*", "/", "%"], Self::parse_unary)
    }

    fn parse_unary(&mut self) -> PResult<NodeId> {
        if self.is_sym("!") || self.is_sym("-") || self.is_sym("+") {
            let op = if let Tok::Sym(s) = self.bump() { s } else { unreachable!() };
            self.skip_newlines();
            let e = self.parse_unary()?;
            if op == "+" {
                return Ok(e);
            }
            return Ok(self.g.add(Kind::Unary { op, expr: e }));
        }
        self.parse_postfix()
    }

    fn parse_postfix(&mut self) -> PResult<NodeId> {
        let mut e = self.parse_primary()?;
        loop {
            // 允许换行后接 . 链式调用
            if matches!(self.peek(), Tok::Newline) {
                let save = self.pos;
                self.skip_newlines();
                if !(self.is_sym(".") || self.is_sym("?.")) {
                    self.pos = save;
                    break;
                }
            }
            if self.is_sym(".") || self.is_sym("?.") {
                let safe = self.is_sym("?.");
                self.bump();
                let name = self.expect_ident()?;
                if self.is_sym("(") {
                    let args = self.parse_args()?;
                    let m = self.g.add(Kind::Member { base: e, name, safe });
                    e = self.g.add(Kind::Call { callee: m, args });
                } else if self.is_sym("{") {
                    // 无括号尾随 lambda：recv.method { ... }
                    let lam = self.parse_lambda()?;
                    if name == "forEach" {
                        e = self.build_for_each(e, lam);
                    } else if name == "forEachIndexed" {
                        e = self.build_for_each_indexed(e, lam);
                    } else if name == "let" {
                        // recv?.let { it -> ... } / recv.let { ... }
                        e = self.build_safe_let(e, lam);
                    } else {
                        let m = self.g.add(Kind::Member { base: e, name, safe });
                        e = self.g.add(Kind::Call { callee: m, args: vec![lam] });
                    }
                } else {
                    e = self.g.add(Kind::Member { base: e, name, safe });
                }
            } else if self.is_sym("(") {
                let args = self.parse_args()?;
                e = self.g.add(Kind::Call { callee: e, args });
            } else if self.is_sym("[") {
                self.bump();
                let idx = self.parse_expr()?;
                self.expect_sym("]")?;
                e = self.g.add(Kind::Index { base: e, index: idx });
            } else if self.is_sym("!") && self.peek_next_is_bang() {
                // !! 非空断言：剥离
                self.bump();
                self.bump();
            } else {
                break;
            }
        }
        Ok(e)
    }

    fn build_for_each(&mut self, recv: NodeId, lam: NodeId) -> NodeId {        let (params, body) = if let Kind::Lambda { params, body } = self.g.kind(lam) {
            (params.clone(), *body)
        } else {
            (Vec::new(), lam)
        };
        let var_name = params.first().cloned().unwrap_or_else(|| "it".to_string());
        let nn = self.g.add(Kind::Name { original: var_name });
        let var = self.g.add(Kind::VarDecl {
            mutable: false,
            name_node: nn,
            ty: None,
            init: None,
        });
        self.g.add(Kind::ForEach { var, iter: recv, body })
    }

    /// xs.forEachIndexed { i, v -> ... } → for ((i, v) in xs.withIndex()) { ... }
    fn build_for_each_indexed(&mut self, recv: NodeId, lam: NodeId) -> NodeId {
        let (params, body) = if let Kind::Lambda { params, body } = self.g.kind(lam) {
            (params.clone(), *body)
        } else {
            (Vec::new(), lam)
        };
        let strip = |p: &String| -> String {
            p.split_once(':').map(|(n, _)| n.trim().to_string()).unwrap_or_else(|| p.clone())
        };
        let iname = params.first().map(&strip).unwrap_or_else(|| "index".to_string());
        let vname = params.get(1).map(&strip).unwrap_or_else(|| "it".to_string());
        let in_node = self.g.add(Kind::Name { original: iname });
        let vn_node = self.g.add(Kind::Name { original: vname });
        let var = self.g.add(Kind::Destructure { names: vec![in_node, vn_node] });
        let wi = self.g.add(Kind::Member { base: recv, name: "withIndex".to_string(), safe: false });
        let iter = self.g.add(Kind::Call { callee: wi, args: vec![] });
        self.g.add(Kind::ForEach { var, iter, body })
    }

    fn build_safe_let(&mut self, recv: NodeId, lam: NodeId) -> NodeId {
        let (params, body) = if let Kind::Lambda { params, body } = self.g.kind(lam) {
            (params.clone(), *body)
        } else {
            (Vec::new(), lam)
        };
        let var = params.first().cloned().unwrap_or_else(|| "it".to_string());
        self.g.add(Kind::SafeLet { recv, var, body })
    }

    fn peek_next_is_bang(&self) -> bool {
        self.pos + 1 < self.toks.len() && matches!(&self.toks[self.pos + 1].tok, Tok::Sym(s) if s == "!")
    }

    fn peek_next_is_kw(&self, kw: &str) -> bool {
        self.pos + 1 < self.toks.len()
            && matches!(&self.toks[self.pos + 1].tok, Tok::Ident(s) if s == kw)
    }

    /// builder 名后紧跟 `(` 或 `<`（泛型实参）。
    fn peek_after_ident_is_call_or_generic(&self) -> bool {
        if self.pos + 1 < self.toks.len() {
            matches!(&self.toks[self.pos + 1].tok, Tok::Sym(s) if s == "(" || s == "<")
        } else {
            false
        }
    }

    fn parse_args(&mut self) -> PResult<Vec<NodeId>> {
        self.expect_sym("(")?;
        self.skip_newlines();
        let mut args = Vec::new();
        while !self.is_sym(")") {
            // 跳过命名实参标签 `name =`
            if let Tok::Ident(_) = self.peek() {
                if self.pos + 1 < self.toks.len() {
                    if let Tok::Sym(s) = &self.toks[self.pos + 1].tok {
                        if s == "=" {
                            self.bump();
                            self.bump();
                            self.skip_newlines();
                        }
                    }
                }
            }
            let a = self.parse_expr()?;
            args.push(a);
            self.skip_newlines();
            if !self.eat_sym(",") {
                break;
            }
            self.skip_newlines();
        }
        self.expect_sym(")")?;
        // 尾随 lambda
        if self.is_sym("{") {
            let lam = self.parse_lambda()?;
            args.push(lam);
        }
        Ok(args)
    }

    fn parse_lambda(&mut self) -> PResult<NodeId> {
        self.expect_sym("{")?;
        self.push_scope();
        let mut params = Vec::new();
        // 检测 `params ->`，参数可带类型注解 `n: Int`。
        let save = self.pos;
        let mut has_arrow = false;
        let mut tmp: Vec<String> = Vec::new();
        loop {
            match self.peek().clone() {
                Tok::Ident(n) => {
                    self.bump();
                    let mut p = n;
                    if self.eat_sym(":") {
                        let ty = self.parse_type()?;
                        p = format!("{}: {}", p, ty);
                    }
                    tmp.push(p);
                    self.eat_sym(",");
                }
                Tok::Sym(s) if s == "->" => {
                    self.bump();
                    has_arrow = true;
                    break;
                }
                _ => break,
            }
        }
        if has_arrow {
            params = tmp;
        } else {
            self.pos = save;
        }
        self.skip_seps();
        let mut stmts = Vec::new();
        while !self.is_sym("}") && !self.at_eof() {
            stmts.push(self.parse_statement()?);
            self.skip_seps();
        }
        self.expect_sym("}")?;
        self.pop_scope();
        let body = self.g.add(Kind::Block { stmts });
        Ok(self.g.add(Kind::Lambda { params, body }))
    }

    fn parse_primary(&mut self) -> PResult<NodeId> {
        let line = self.line();
        match self.peek().clone() {
            Tok::Int(s) => {
                self.bump();
                Ok(self.g.add(Kind::IntLit(s)))
            }
            Tok::Float(s) => {
                self.bump();
                Ok(self.g.add(Kind::FloatLit(s)))
            }
            Tok::Char(s) => {
                self.bump();
                Ok(self.g.add(Kind::CharLit(s)))
            }
            Tok::Str(parts) => {
                self.bump();
                self.build_template(parts)
            }
            Tok::Ident(name) => {
                if name == "true" || name == "false" {
                    self.bump();
                    return Ok(self.g.add(Kind::BoolLit(name == "true")));
                }
                if name == "if" {
                    return self.parse_if();
                }
                if name == "when" {
                    return self.parse_when();
                }
                if name == "null" {
                    self.bump();
                    return Ok(self.g.add(Kind::Raw("None".into())));
                }
                // repeat(n) { ... } → for (_ in 0..n) { ... }
                if name == "repeat" && self.peek_after_ident_is_call_or_generic() {
                    self.bump(); // repeat
                    self.expect_sym("(")?;
                    self.skip_newlines();
                    let count = self.parse_expr()?;
                    self.skip_newlines();
                    self.expect_sym(")")?;
                    self.skip_newlines();
                    let body = if self.is_sym("{") {
                        let lam = self.parse_lambda()?;
                        if let Kind::Lambda { body, .. } = self.g.kind(lam) {
                            *body
                        } else {
                            lam
                        }
                    } else {
                        self.g.add(Kind::Block { stmts: vec![] })
                    };
                    return Ok(self.g.add(Kind::Repeat { count, body }));
                }
                // 集合字面量构造器（可带显式泛型实参）
                if let Some(ctor) = collection_ctor(&name) {
                    if self.peek_after_ident_is_call_or_generic() {
                        self.bump(); // 消费 builder 名
                        let mut elem = None;
                        if self.eat_sym("<") {
                            let mut tys = Vec::new();
                            loop {
                                tys.push(self.parse_type_raw()?);
                                if !self.eat_sym(",") {
                                    break;
                                }
                            }
                            self.expect_sym(">")?;
                            elem = Some(
                                tys.iter().map(|t| map_type(t)).collect::<Vec<_>>().join(", "),
                            );
                        }
                        let args = self.parse_args()?;
                        return Ok(self.g.add(Kind::CollLit { ctor: ctor.to_string(), elem, args }));
                    }
                }
                self.bump();
                let decl = self.resolve(&name);
                Ok(self.g.add(Kind::NameRef { original: name, decl }))
            }
            Tok::Sym(s) if s == "(" => {
                self.bump();
                self.skip_newlines();
                let e = self.parse_expr()?;
                self.skip_newlines();
                self.expect_sym(")")?;
                Ok(e)
            }
            Tok::Sym(s) if s == "{" => self.parse_lambda(),
            other => Err(format!("line {}: 非预期的记号 {:?}", line, other)),
        }
    }

    fn build_template(&mut self, parts: Vec<StrPart>) -> PResult<NodeId> {
        let mut out = Vec::new();
        for p in parts {
            match p {
                StrPart::Lit(s) => out.push(TemplatePart::Lit(s)),
                StrPart::Expr(raw) => {
                    let node = self.parse_subexpr(&raw)?;
                    out.push(TemplatePart::Expr(node));
                }
            }
        }
        Ok(self.g.add(Kind::StrTemplate { parts: out }))
    }

    /// 在当前作用域下解析一段子表达式文本（用于字符串插值）。
    fn parse_subexpr(&mut self, src: &str) -> PResult<NodeId> {
        let toks = crate::lexer::Lexer::new(src).tokenize()?;
        // 借用当前作用域解析
        let saved_toks = std::mem::replace(&mut self.toks, toks);
        let saved_pos = self.pos;
        self.pos = 0;
        self.skip_newlines();
        let res = self.parse_expr();
        self.toks = saved_toks;
        self.pos = saved_pos;
        res
    }

    fn parse_if(&mut self) -> PResult<NodeId> {
        self.eat_kw("if");
        self.expect_sym("(")?;
        let cond = self.parse_expr()?;
        self.expect_sym(")")?;
        self.skip_newlines();
        let then_b = self.parse_block_or_stmt()?;
        self.skip_newlines_for_else();
        let mut else_b = None;
        if self.eat_kw("else") {
            self.skip_newlines();
            if self.is_kw("if") {
                let e = self.parse_if()?;
                else_b = Some(self.g.add(Kind::Block { stmts: vec![e] }));
            } else {
                else_b = Some(self.parse_block_or_stmt()?);
            }
        }
        Ok(self.g.add(Kind::If { cond, then_b, else_b }))
    }

    fn skip_newlines_for_else(&mut self) {
        let save = self.pos;
        self.skip_newlines();
        if !self.is_kw("else") {
            self.pos = save;
        }
    }

    fn parse_when(&mut self) -> PResult<NodeId> {
        self.eat_kw("when");
        let mut subject = None;
        if self.eat_sym("(") {
            subject = Some(self.parse_expr()?);
            self.expect_sym(")")?;
        }
        self.skip_newlines();
        self.expect_sym("{")?;
        self.skip_seps();
        let mut arms = Vec::new();
        while !self.is_sym("}") && !self.at_eof() {
            if self.eat_kw("else") {
                self.expect_sym("->")?;
                self.skip_newlines();
                let body = self.parse_block_or_stmt()?;
                arms.push(WhenArm { patterns: None, body });
            } else {
                let mut pats = Vec::new();
                loop {
                    // `is T` 类型分支模式
                    if self.is_kw("is") {
                        self.bump();
                        let ty = self.parse_type()?;
                        pats.push(self.g.add(Kind::TypePat { ty }));
                    } else if self.is_kw("in") || (self.is_sym("!") && self.peek_next_is_kw("in")) {
                        // `in rhs` / `!in rhs` 成员检查分支模式
                        let negated = self.eat_sym("!");
                        self.eat_kw("in");
                        let rhs = self.parse_expr()?;
                        pats.push(self.g.add(Kind::InPat { negated, rhs }));
                    } else {
                        let p = self.parse_expr()?;
                        pats.push(p);
                    }
                    if !self.eat_sym(",") {
                        break;
                    }
                    self.skip_newlines();
                }
                self.expect_sym("->")?;
                self.skip_newlines();
                let body = self.parse_block_or_stmt()?;
                arms.push(WhenArm { patterns: Some(pats), body });
            }
            self.skip_seps();
        }
        self.expect_sym("}")?;
        Ok(self.g.add(Kind::When { subject, arms }))
    }

    // ---- 辅助 ----
    fn expect_ident(&mut self) -> PResult<String> {
        if let Tok::Ident(s) = self.peek().clone() {
            self.bump();
            Ok(s)
        } else {
            Err(format!("line {}: 期望标识符，得到 {:?}", self.line(), self.peek()))
        }
    }

    /// 解析一个类型，并映射为仓颉类型字符串。
    fn parse_type(&mut self) -> PResult<String> {
        let raw = self.parse_type_raw()?;
        Ok(map_type(&raw))
    }

    fn parse_type_raw(&mut self) -> PResult<String> {
        // 函数类型 `(A, B) -> R`（仓颉语法一致，可直接映射）。
        if self.is_sym("(") {
            self.bump();
            let mut params = Vec::new();
            if !self.is_sym(")") {
                loop {
                    params.push(self.parse_type_raw()?);
                    if !self.eat_sym(",") {
                        break;
                    }
                }
            }
            self.expect_sym(")")?;
            self.expect_sym("->")?;
            let ret = self.parse_type_raw()?;
            let mut s = format!("({}) -> {}", params.join(", "), ret);
            if self.eat_sym("?") {
                s = format!("{}?", s);
            }
            return Ok(s);
        }
        let mut s = self.expect_ident()?;
        if self.eat_sym("<") {
            let mut args = Vec::new();
            loop {
                args.push(self.parse_type_raw()?);
                if !self.eat_sym(",") {
                    break;
                }
            }
            self.expect_sym(">")?;
            s = format!("{}<{}>", s, args.join(","));
        }
        // 可空类型 `?` —— 保留为前缀标记，交由 map_type 处理
        if self.eat_sym("?") {
            s = format!("{}?", s);
        }
        Ok(s)
    }
}

/// 关键字转义：把与仓颉关键字冲突的标识符用反引号包裹。
pub fn safe_name(name: &str) -> String {
    const KW: &[&str] = &[
        "this", "super", "let", "var", "func", "class", "struct", "interface", "enum",
        "match", "case", "where", "open", "init", "main", "type", "as", "is", "in",
        "spawn", "macro", "quote", "extend", "prop", "mut", "unsafe", "foreign",
    ];
    if KW.contains(&name) {
        format!("`{}`", name)
    } else {
        name.to_string()
    }
}

/// 集合字面量构造器名 → 仓颉容器类型名。
pub fn collection_ctor(name: &str) -> Option<&'static str> {
    match name {
        "listOf" | "mutableListOf" | "arrayListOf" | "ArrayList" => Some("ArrayList"),
        "setOf" | "mutableSetOf" | "hashSetOf" | "HashSet" => Some("HashSet"),
        "mapOf" | "mutableMapOf" | "hashMapOf" | "HashMap" | "LinkedHashMap" => Some("HashMap"),
        _ => None,
    }
}

/// Kotlin 类型 → 仓颉类型。
pub fn map_type(raw: &str) -> String {
    let raw = raw.trim();
    // 函数类型 `(A, B) -> R` → 逐段映射参数与返回类型（仓颉语法一致）。
    if raw.starts_with('(') {
        if let Some(close) = matching_paren(raw) {
            let after = raw[close + 1..].trim_start();
            if let Some(rest) = after.strip_prefix("->") {
                let inner = &raw[1..close];
                let params: Vec<String> = if inner.trim().is_empty() {
                    Vec::new()
                } else {
                    split_top(inner).iter().map(|a| map_type(a)).collect()
                };
                let ret = map_type(rest.trim());
                return format!("({}) -> {}", params.join(", "), ret);
            }
        }
    }
    // 可空类型：Kotlin `T?` → 仓颉 `?T`
    if let Some(base) = raw.strip_suffix('?') {
        return format!("?{}", map_type(base));
    }
    // 解析泛型
    if let Some(lt) = raw.find('<') {
        let base = &raw[..lt];
        let inner = &raw[lt + 1..raw.rfind('>').unwrap_or(raw.len())];
        let args: Vec<String> = split_top(inner).iter().map(|a| map_type(a)).collect();
        // Kotlin `Pair<A, B>` / `Triple<A, B, C>` → 仓颉元组类型 `(A, B)`。
        if base == "Pair" || base == "Triple" {
            return format!("({})", args.join(", "));
        }
        let mapped_base = match base {
            "List" | "MutableList" | "ArrayList" | "Collection" | "Iterable" => "ArrayList",
            "Map" | "MutableMap" | "HashMap" | "LinkedHashMap" => "HashMap",
            "Set" | "MutableSet" | "HashSet" => "HashSet",
            "Array" => "Array",
            other => other,
        };
        return format!("{}<{}>", mapped_base, args.join(", "));
    }
    match raw {
        "Int" | "Short" | "Byte" | "Long" => "Int64".to_string(),
        "Double" | "Float" => "Float64".to_string(),
        "Boolean" => "Bool".to_string(),
        "Char" => "Rune".to_string(),
        "String" | "CharSequence" => "String".to_string(),
        "Unit" => "Unit".to_string(),
        "Any" => "Object".to_string(),
        other => other.to_string(),
    }
}

fn split_top(s: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut depth = 0;
    let mut cur = String::new();
    for c in s.chars() {
        match c {
            '<' | '(' => {
                depth += 1;
                cur.push(c);
            }
            '>' | ')' => {
                depth -= 1;
                cur.push(c);
            }
            ',' if depth == 0 => {
                out.push(cur.trim().to_string());
                cur.clear();
            }
            _ => cur.push(c),
        }
    }
    if !cur.trim().is_empty() {
        out.push(cur.trim().to_string());
    }
    out
}

/// 返回与位置 0 的 `(` 匹配的 `)` 的下标。
fn matching_paren(s: &str) -> Option<usize> {
    let bytes = s.as_bytes();
    if bytes.first() != Some(&b'(') {
        return None;
    }
    let mut depth = 0;
    for (i, &b) in bytes.iter().enumerate() {
        match b {
            b'(' => depth += 1,
            b')' => {
                depth -= 1;
                if depth == 0 {
                    return Some(i);
                }
            }
            _ => {}
        }
    }
    None
}
