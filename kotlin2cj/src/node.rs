//! 翻译图：自组织临界（SOC）翻译引擎的核心数据结构。
//!
//! 每个语法单元（声明、语句、表达式）都是图中的一个 *节点*，携带一个
//! SOC 状态 `(目标片段, 置信度, 冲突标志, 版本号, 温度)`。节点之间通过
//! 两类边相连：
//!   * **语法邻接**：父子关系（`children` / `parent`）。
//!   * **依赖**：标识符引用 → 其声明节点（`dep` / `dependents`）。
//!
//! 引擎对图做异步松弛（worklist 迭代），每个节点仅依据 *自身 + 邻居* 的
//! 状态更新自己的翻译，状态变更像沙堆崩塌一样沿边级联传播，直至收敛。


pub type NodeId = usize;

/// 节点的语法类别及其携带的局部信息。
#[derive(Debug, Clone)]
pub enum Kind {
    Program { items: Vec<NodeId> },

    // ---- 声明 ----
    Func {
        name: String,
        params: Vec<NodeId>, // Param 节点
        ret: Option<String>, // 已映射的仓颉返回类型
        body: NodeId,
        is_main: bool,
        /// 抽象方法（接口/抽象类中无函数体的声明）。
        is_abstract: bool,
        /// `override` 修饰：实现接口/抽象方法，仓颉需 `public func`。
        is_override: bool,
    },
    Param {
        name_node: NodeId,
        ty: String, // 已映射类型
        /// 默认值（Kotlin 默认参数）；存在时渲染为仓颉具名参数 `p!: T = default`。
        default: Option<NodeId>,
    },
    Class {
        name: String,
        ctor_params: Vec<CtorParam>,
        members: Vec<NodeId>,
        /// 父类名（已映射），用于 `class C <: Super`。
        superclass: Option<String>,
        /// 是否可被继承（`open`/`abstract`/`sealed`）。
        is_open: bool,
        /// 是否为 `data class`（生成 ToString 以对齐 Kotlin 自动 toString）。
        is_data: bool,
        /// 是否为 `interface`。
        is_interface: bool,
        /// 是否为 `abstract class`（抽象方法须 `public func`）。
        is_abstract: bool,
        /// 额外实现的接口（继承列表中不带构造实参的超类型）。
        interfaces: Vec<String>,
        /// 调用父类构造器的实参（继承列表中带 `(...)` 的超类型）。
        super_args: Vec<NodeId>,
    },
    /// 枚举类（仅简单具名常量项）。
    Enum {
        name: String,
        entries: Vec<String>,
    },
    /// 局部变量 / 顶层变量 / 属性声明。
    VarDecl {
        mutable: bool,
        name_node: NodeId, // Name 节点（用于命名冲突崩塌）
        ty: Option<String>,
        init: Option<NodeId>,
    },
    /// 引入一个名字的节点，可被关键字转义“崩塌”改写，触发引用雪崩。
    Name {
        original: String,
    },

    // ---- 语句 ----
    Block { stmts: Vec<NodeId> },
    ExprStmt { expr: NodeId },
    Assign { target: NodeId, op: String, value: NodeId },
    Return { value: Option<NodeId> },
    /// `throw expr`
    Throw { value: NodeId },
    If { cond: NodeId, then_b: NodeId, else_b: Option<NodeId> },
    While { cond: NodeId, body: NodeId },
    DoWhile { body: NodeId, cond: NodeId },
    ForRange { var: NodeId, range: NodeId, body: NodeId },
    ForEach { var: NodeId, iter: NodeId, body: NodeId },
    /// `try { } catch (e: T) { } ... finally { }`
    Try { body: NodeId, catches: Vec<CatchClause>, finally: Option<NodeId> },
    /// `repeat(n) { ... }` → `for (_ in 0..n) { ... }`
    Repeat { count: NodeId, body: NodeId },
    /// 解构循环变量 `(k, v)`，其名字节点用于在作用域内建立引用依赖。
    Destructure { names: Vec<NodeId> },
    /// 解构声明 `val (a, b) = expr` → 仓颉 `let (a, b) = expr`。
    DestructureDecl { mutable: bool, names: Vec<NodeId>, init: NodeId },
    When { subject: Option<NodeId>, arms: Vec<WhenArm> },

    // ---- 表达式 ----
    IntLit(String),
    FloatLit(String),
    BoolLit(bool),
    CharLit(String),
    StrTemplate { parts: Vec<TemplatePart> },
    /// 标识符引用，`decl` 指向其声明的 Name 节点（若可解析）。
    NameRef { original: String, decl: Option<NodeId> },
    Unary { op: String, expr: NodeId },
    Binary { op: String, lhs: NodeId, rhs: NodeId },
    Range { lo: NodeId, hi: NodeId, inclusive: bool, down: bool, step: Option<NodeId> },
    Call { callee: NodeId, args: Vec<NodeId> },
    /// 集合字面量构造（listOf / mapOf / setOf 等），记录显式元素类型以支持空集合。
    CollLit { ctor: String, elem: Option<String>, args: Vec<NodeId> },
    Index { base: NodeId, index: NodeId },
    Member { base: NodeId, name: String, safe: bool },
    Lambda { params: Vec<String>, body: NodeId },
    /// `recv?.let { it -> ... }` → `if (let Some(it) <- recv) { ... }`。
    SafeLet { recv: NodeId, var: String, body: NodeId },
    /// `expr is T` / `expr !is T` 类型判定。
    IsCheck { expr: NodeId, ty: String, negate: bool },
    /// `when` 的类型分支模式 `is T`（仅出现在 when 臂的 patterns 中）。
    TypePat { ty: String },
    /// `when` 的成员检查分支模式 `in rhs` / `!in rhs`（仅出现在 when 臂的 patterns 中）。
    InPat { negated: bool, rhs: NodeId },
    /// 已经渲染好的原子片段（如简单标识符）。
    Raw(String),
}

#[derive(Debug, Clone)]
pub struct CtorParam {
    pub kind: CtorParamKind,
    pub name: String,
    pub ty: String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum CtorParamKind {
    Val,
    Var,
    Plain,
}

#[derive(Debug, Clone)]
pub struct WhenArm {
    /// None 表示 else 分支。
    pub patterns: Option<Vec<NodeId>>,
    pub body: NodeId,
}

/// try 的一个 catch 子句。
#[derive(Debug, Clone)]
pub struct CatchClause {
    pub name: String,
    pub ty: String,
    pub body: NodeId,
}

#[derive(Debug, Clone)]
pub enum TemplatePart {
    Lit(String),
    Expr(NodeId),
}

/// 自组织状态向量。
#[derive(Debug, Clone, Default)]
pub struct State {
    pub target: Option<String>,
    pub confidence: f32,
    #[allow(dead_code)]
    pub conflict: bool,
    pub version: u64,
    pub temperature: u32,
}

#[derive(Debug, Clone)]
pub struct Node {
    pub id: NodeId,
    pub kind: Kind,
    pub parent: Option<NodeId>,
    /// 依赖边：本节点 → 其依赖（如引用 → 声明）。
    pub dep: Option<NodeId>,
    /// 反向依赖边：依赖本节点的引用集合。
    pub dependents: Vec<NodeId>,
    pub state: State,
}

pub struct Graph {
    pub nodes: Vec<Node>,
    pub root: NodeId,
}

impl Graph {
    pub fn new() -> Self {
        Graph { nodes: Vec::new(), root: 0 }
    }

    pub fn add(&mut self, kind: Kind) -> NodeId {
        let id = self.nodes.len();
        self.nodes.push(Node {
            id,
            kind,
            parent: None,
            dep: None,
            dependents: Vec::new(),
            state: State::default(),
        });
        id
    }

    pub fn kind(&self, id: NodeId) -> &Kind {
        &self.nodes[id].kind
    }

    pub fn target(&self, id: NodeId) -> Option<&str> {
        self.nodes[id].state.target.as_deref()
    }

    /// 为本节点的所有句法子节点建立 parent 边。
    pub fn link_children(&mut self) {
        let n = self.nodes.len();
        for id in 0..n {
            let children = self.children_of(id);
            for c in children {
                self.nodes[c].parent = Some(id);
            }
        }
    }

    /// 收集一个节点的全部句法子节点（用于 worklist 传播）。
    pub fn children_of(&self, id: NodeId) -> Vec<NodeId> {
        let mut v = Vec::new();
        match &self.nodes[id].kind {
            Kind::Program { items } => v.extend(items),
            Kind::Func { params, body, .. } => {
                v.extend(params);
                v.push(*body);
            }
            Kind::Param { name_node, default, .. } => {
                v.push(*name_node);
                if let Some(d) = default {
                    v.push(*d);
                }
            }
            Kind::Class { members, super_args, .. } => {
                v.extend(members);
                v.extend(super_args);
            }
            Kind::Enum { .. } => {}
            Kind::VarDecl { name_node, init, .. } => {
                v.push(*name_node);
                if let Some(i) = init {
                    v.push(*i);
                }
            }
            Kind::Name { .. } => {}
            Kind::Block { stmts } => v.extend(stmts),
            Kind::ExprStmt { expr } => v.push(*expr),
            Kind::Assign { target, value, .. } => {
                v.push(*target);
                v.push(*value);
            }
            Kind::Return { value } => {
                if let Some(val) = value {
                    v.push(*val);
                }
            }
            Kind::Throw { value } => v.push(*value),
            Kind::If { cond, then_b, else_b } => {
                v.push(*cond);
                v.push(*then_b);
                if let Some(e) = else_b {
                    v.push(*e);
                }
            }
            Kind::While { cond, body } => {
                v.push(*cond);
                v.push(*body);
            }
            Kind::DoWhile { body, cond } => {
                v.push(*body);
                v.push(*cond);
            }
            Kind::ForRange { var, range, body } => {
                v.push(*var);
                v.push(*range);
                v.push(*body);
            }
            Kind::ForEach { var, iter, body } => {
                v.push(*var);
                v.push(*iter);
                v.push(*body);
            }
            Kind::Try { body, catches, finally } => {
                v.push(*body);
                for c in catches {
                    v.push(c.body);
                }
                if let Some(f) = finally {
                    v.push(*f);
                }
            }
            Kind::Repeat { count, body } => {
                v.push(*count);
                v.push(*body);
            }
            Kind::Destructure { names } => v.extend(names),
            Kind::DestructureDecl { names, init, .. } => {
                v.extend(names);
                v.push(*init);
            }
            Kind::When { subject, arms } => {
                if let Some(s) = subject {
                    v.push(*s);
                }
                for a in arms {
                    if let Some(ps) = &a.patterns {
                        v.extend(ps);
                    }
                    v.push(a.body);
                }
            }
            Kind::Unary { expr, .. } => v.push(*expr),
            Kind::Binary { lhs, rhs, .. } => {
                v.push(*lhs);
                v.push(*rhs);
            }
            Kind::Range { lo, hi, step, .. } => {
                v.push(*lo);
                v.push(*hi);
                if let Some(s) = step {
                    v.push(*s);
                }
            }
            Kind::Call { callee, args } => {
                v.push(*callee);
                v.extend(args);
            }
            Kind::CollLit { args, .. } => v.extend(args),
            Kind::Index { base, index } => {
                v.push(*base);
                v.push(*index);
            }
            Kind::Member { base, .. } => v.push(*base),
            Kind::Lambda { body, .. } => v.push(*body),
            Kind::SafeLet { recv, body, .. } => {
                v.push(*recv);
                v.push(*body);
            }
            Kind::IsCheck { expr, .. } => v.push(*expr),
            Kind::TypePat { .. } => {}
            Kind::InPat { rhs, .. } => v.push(*rhs),
            Kind::StrTemplate { parts } => {
                for p in parts {
                    if let TemplatePart::Expr(e) = p {
                        v.push(*e);
                    }
                }
            }
            Kind::NameRef { .. } | Kind::IntLit(_) | Kind::FloatLit(_) | Kind::BoolLit(_)
            | Kind::CharLit(_) | Kind::Raw(_) => {}
        }
        v
    }
}
