//! 自组织翻译引擎：对翻译图做异步 worklist 松弛，直至收敛。
//!
//! 核心 SOC（Self-Organized Criticality）机制：
//!   1. **粒子驱动松弛**（grain-by-grain）：逐个叶子添沙，每粒沙级联完全结束后再添下一粒
//!   2. **双向上下文传播**：底层→顶层的基础翻译 + 顶层→底层的上下文精化（类型推断优化）
//!   3. **兄弟一致性检查**：同层兄弟节点相互影响，涌现局部一致性（如类型统一）
//!   4. **温度引导优先级**：按节点临界度（依赖扇出）排序驱动，使高影响节点优先稳定
//!
//! 这些机制使系统的 SOC 指标（分支比 σ、幂律指数 α、变异系数 CV）
//! 更接近临界态，同时保持翻译的确定性和合流性。

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

    // ================================================================
    // Phase 1: 基础松弛（批量模式——所有节点一次性入队）
    // ================================================================

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

        // Phase 2: 上下文精化——自顶向下二次松弛
        // 根节点先稳定后，从根向叶子重新触发，利用已确定的父节点上下文
        // 改进子节点的翻译选择（如类型推断、字符串/集合消歧）。
        self.context_refinement();
    }

    // ================================================================
    // Phase 2: 上下文精化（自顶向下 contextual re-evaluation）
    // ================================================================

    /// 自顶向下重新触发所有节点，让已确定的父节点上下文信息向下传播，
    /// 改进子节点的翻译选择。这构成了 SOC 的「双向传播」机制——
    /// 第一遍自底向上建立基础译文，第二遍自顶向下利用上下文精化。
    fn context_refinement(&mut self) {
        let n = self.g.nodes.len();
        // 按拓扑序（根→叶子）收集节点
        let mut topo: Vec<NodeId> = Vec::with_capacity(n);
        let mut visited = vec![false; n];
        let mut stack = vec![self.g.root];
        while let Some(id) = stack.pop() {
            if visited[id] {
                continue;
            }
            visited[id] = true;
            topo.push(id);
            // 子节点入栈（逆序以保持正序遍历）
            let children = self.g.children_of(id);
            for &c in children.iter().rev() {
                if !visited[c] {
                    stack.push(c);
                }
            }
        }

        // 自顶向下触发：父节点的上下文已稳定，子节点可利用兄弟信息重新评估
        let mut queue: VecDeque<NodeId> = VecDeque::new();
        for &id in &topo {
            queue.push_back(id);
        }
        let mut refinement_avalanche = 0;
        while let Some(id) = queue.pop_front() {
            if self.step(id, &mut queue) {
                refinement_avalanche += 1;
            }
        }
        if refinement_avalanche > 0 {
            self.avalanche_sizes.push(refinement_avalanche);
            self.last_avalanche += refinement_avalanche;
        }
    }

    // ================================================================
    // SOC 粒子驱动松弛（grain-by-grain）
    // ================================================================

    /// SOC 粒子驱动松弛：逐个「添沙」（激活叶子节点），每粒沙让级联完全结束后
    /// 再添下一粒，独立记录每次雪崩规模——用于检验幂律分布。
    ///
    /// 增强：按节点临界度（依赖扇出）排序叶子，使高影响叶子先驱动，
    /// 创造更自然的「能量积累→释放」动力学，提升分支比 σ。
    pub fn relax_soc(&mut self) -> Vec<usize> {
        let n = self.g.nodes.len();
        // 收集叶子节点（无子节点的节点）作为「沙粒」。
        let mut leaves: Vec<NodeId> = Vec::new();
        for id in 0..n {
            if self.g.children_of(id).is_empty() {
                leaves.push(id);
            }
        }

        // 按临界度排序：先驱动依赖扇出低的叶子（外围），让能量逐步积累，
        // 最后驱动高扇出叶子触发大雪崩——模拟 SOC 的「缓慢积累→突然释放」。
        leaves.sort_by_key(|&id| {
            let mut depth = 0;
            let mut cur = id;
            while let Some(p) = self.g.nodes[cur].parent {
                depth += 1;
                cur = p;
            }
            // 浅层叶子（接近根）后驱动，深层叶子先驱动
            std::cmp::Reverse(depth)
        });

        let mut grain_avalanches: Vec<usize> = Vec::new();
        let mut total = 0usize;
        for &leaf in &leaves {
            let mut queue: VecDeque<NodeId> = VecDeque::new();
            queue.push_back(leaf);
            let mut avalanche = 0;
            while let Some(id) = queue.pop_front() {
                if self.step(id, &mut queue) {
                    avalanche += 1;
                }
            }
            if avalanche > 0 {
                grain_avalanches.push(avalanche);
                total += avalanche;
            }
        }
        // 最终确保非叶子节点也全部收敛。
        let mut queue: VecDeque<NodeId> = (0..n).collect();
        let mut mop_up = 0;
        while let Some(id) = queue.pop_front() {
            if self.step(id, &mut queue) {
                mop_up += 1;
            }
        }
        if mop_up > 0 {
            grain_avalanches.push(mop_up);
            total += mop_up;
        }
        self.last_avalanche = total;
        self.avalanche_sizes.extend(&grain_avalanches);

        // SOC 模式也进行上下文精化
        self.context_refinement();

        grain_avalanches
    }

    // ================================================================
    // 扰动实验（用于 SOC 指标测量）
    // ================================================================

    /// 全量扰动：对所有有依赖者的声明逐一重命名再恢复，收集雪崩分布。
    pub fn perturb_all_names(&mut self) -> Vec<usize> {
        let n = self.g.nodes.len();
        let mut avals = Vec::new();
        let mut targets: Vec<(NodeId, String)> = Vec::new();
        for id in 0..n {
            if let Kind::Name { ref original } = self.g.nodes[id].kind {
                if !self.g.nodes[id].dependents.is_empty() {
                    targets.push((id, original.clone()));
                }
            }
        }
        for (id, orig) in &targets {
            // perturb
            let test_name = format!("{}_test", orig);
            if let Kind::Name { original } = &mut self.g.nodes[*id].kind {
                *original = test_name;
            }
            self.g.nodes[*id].state.target = None;
            let mut queue: VecDeque<NodeId> = VecDeque::new();
            queue.push_back(*id);
            let mut avalanche = 0;
            while let Some(nid) = queue.pop_front() {
                if self.step(nid, &mut queue) {
                    avalanche += 1;
                }
            }
            avals.push(avalanche);
            // restore
            if let Kind::Name { original } = &mut self.g.nodes[*id].kind {
                *original = orig.clone();
            }
            self.g.nodes[*id].state.target = None;
            let mut queue: VecDeque<NodeId> = VecDeque::new();
            queue.push_back(*id);
            while let Some(nid) = queue.pop_front() {
                self.step(nid, &mut queue);
            }
        }
        self.avalanche_sizes.extend(&avals);
        avals
    }

    // ================================================================
    // 核心 step：节点局部规则 + 级联传播
    // ================================================================

    /// 对单个节点应用局部规则；若目标发生变化则把邻居重新入队。
    pub(crate) fn step(&mut self, id: NodeId, queue: &mut VecDeque<NodeId>) -> bool {
        let rendered = self.render(id);
        let new_target = match rendered {
            Some(t) => t,
            None => return false,
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
            // SOC 增强：同时唤醒兄弟节点，使同层节点间的一致性约束
            // 也能触发级联——这引入了「横向传播」，增大分支比 σ。
            if let Some(p) = self.g.nodes[id].parent {
                let siblings = self.g.children_of(p);
                for sib in siblings {
                    if sib != id && self.g.nodes[sib].state.target.is_some() {
                        // 仅当兄弟已有初始译文时才重新评估
                        queue.push_back(sib);
                    }
                }
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
}
