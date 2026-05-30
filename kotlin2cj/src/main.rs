//! kotlin2cj —— 基于自组织临界性（SOC）局部规则的 Kotlin→仓颉翻译器。
//!
//! 用法：
//!   kotlin2cj <input.kt> [-o out.cj]   翻译单个文件
//!   kotlin2cj <input.kt> --stats       额外打印自组织/雪崩统计
//!   kotlin2cj --demo-avalanche <in.kt> 演示重命名引发的引用雪崩

mod engine;
mod lexer;
mod node;
mod parser;

use std::process::ExitCode;

fn translate(src: &str) -> Result<engine::Engine, String> {
    let toks = lexer::Lexer::new(src).tokenize()?;
    let mut p = parser::Parser::new(toks);
    p.parse_program()?;
    let mut eng = engine::Engine::new(p.g);
    eng.relax();
    Ok(eng)
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("用法: kotlin2cj <input.kt> [-o out.cj] [--stats] [--demo-avalanche]");
        return ExitCode::from(2);
    }

    let mut input: Option<String> = None;
    let mut output: Option<String> = None;
    let mut stats = false;
    let mut demo = false;
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-o" | "--output" => {
                i += 1;
                output = args.get(i).cloned();
            }
            "--stats" => stats = true,
            "--demo-avalanche" => demo = true,
            other => input = Some(other.to_string()),
        }
        i += 1;
    }

    let input = match input {
        Some(p) => p,
        None => {
            eprintln!("错误: 未指定输入文件");
            return ExitCode::from(2);
        }
    };

    let src = match std::fs::read_to_string(&input) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("无法读取 {}: {}", input, e);
            return ExitCode::from(2);
        }
    };

    let mut eng = match translate(&src) {
        Ok(e) => e,
        Err(e) => {
            eprintln!("翻译失败: {}", e);
            return ExitCode::FAILURE;
        }
    };

    let out = eng.output();

    match &output {
        Some(path) => {
            if let Err(e) = std::fs::write(path, &out) {
                eprintln!("无法写入 {}: {}", path, e);
                return ExitCode::FAILURE;
            }
        }
        None => print!("{}", out),
    }

    if stats {
        eprintln!("--- 自组织统计 ---");
        eprintln!("节点数        : {}", eng.g.nodes.len());
        eprintln!("初始雪崩规模  : {}", eng.last_avalanche);
        eprintln!("状态更新总数  : {}", eng.total_updates);
        let temp: u32 = eng.g.nodes.iter().map(|n| n.state.temperature).sum();
        eprintln!("累计触发次数  : {}", temp);
    }

    if demo {
        run_demo(&mut eng);
    }

    ExitCode::SUCCESS
}

/// 演示：重命名一个被引用的局部声明，观察依赖引用的雪崩级联与自动修复。
fn run_demo(eng: &mut engine::Engine) {
    use node::Kind;
    let target = eng
        .g
        .nodes
        .iter()
        .find(|n| matches!(n.kind, Kind::Name { .. }) && !n.dependents.is_empty())
        .map(|n| (n.id, n.dependents.len()));
    match target {
        Some((id, deps)) => {
            let old = if let Kind::Name { original } = &eng.g.nodes[id].kind {
                original.clone()
            } else {
                String::new()
            };
            eprintln!("--- 雪崩演示 ---");
            eprintln!("重命名声明 '{}' (直接引用 {} 处) -> '{}_renamed'", old, deps, old);
            eng.perturb_rename(id, &format!("{}_renamed", old));
            eprintln!("级联状态更新（雪崩规模）: {}", eng.last_avalanche);
            eprintln!("（系统已局部自动修复所有受影响引用，无需全局重译）");
        }
        None => eprintln!("--- 雪崩演示 --- 无可重命名的被引用声明"),
    }
}
