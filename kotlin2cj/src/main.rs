//! kotlin2cj —— 基于自组织临界性（SOC）局部规则的 Kotlin→仓颉翻译器。
//!
//! 用法：
//!   kotlin2cj <input.kt> [-o out.cj]   翻译单个文件
//!   kotlin2cj <input.kt> --stats       额外打印自组织/雪崩统计
//!   kotlin2cj --demo-avalanche <in.kt> 演示重命名引发的引用雪崩

mod engine;
mod heuristics;
mod lexer;
mod node;
mod render;
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

fn translate_soc(src: &str) -> Result<(engine::Engine, Vec<usize>), String> {
    let toks = lexer::Lexer::new(src).tokenize()?;
    let mut p = parser::Parser::new(toks);
    p.parse_program()?;
    let mut eng = engine::Engine::new(p.g);
    let grain_avals = eng.relax_soc();
    Ok((eng, grain_avals))
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
    let mut soc_analysis = false;
    let mut soc_mode = false;
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-o" | "--output" => {
                i += 1;
                output = args.get(i).cloned();
            }
            "--stats" => stats = true,
            "--demo-avalanche" => demo = true,
            "--soc-analysis" => soc_analysis = true,
            "--soc-mode" => soc_mode = true,
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

    let mut eng = if soc_mode {
        match translate_soc(&src) {
            Ok((e, _avals)) => e,
            Err(e) => {
                eprintln!("翻译失败: {}", e);
                return ExitCode::FAILURE;
            }
        }
    } else {
        match translate(&src) {
            Ok(e) => e,
            Err(e) => {
                eprintln!("翻译失败: {}", e);
                return ExitCode::FAILURE;
            }
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

    if soc_analysis {
        run_soc_analysis(&src);
    }

    ExitCode::SUCCESS
}

/// SOC 分析：粒子驱动松弛 + 全量扰动，输出雪崩分布 JSON。
fn run_soc_analysis(src: &str) {
    // Phase 1: 粒子驱动松弛
    let toks = match lexer::Lexer::new(src).tokenize() {
        Ok(t) => t,
        Err(e) => { eprintln!("词法分析失败: {}", e); return; }
    };
    let mut p = parser::Parser::new(toks);
    if let Err(e) = p.parse_program() {
        eprintln!("语法分析失败: {}", e); return;
    }
    let mut eng = engine::Engine::new(p.g);
    let grain_avals = eng.relax_soc();
    eprintln!("SOC_GRAIN_AVALANCHES:{}", grain_avals.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","));

    // Phase 2: 全量扰动
    let perturb_avals = eng.perturb_all_names();
    eprintln!("SOC_PERTURB_AVALANCHES:{}", perturb_avals.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","));

    // Phase 3: 汇总统计
    eprintln!("SOC_NODES:{}", eng.g.nodes.len());
    eprintln!("SOC_TOTAL_UPDATES:{}", eng.total_updates);

    // Timing: 比较批量模式 vs SOC 模式（此处源码已通过 Phase 1 验证）
    let Ok(toks2) = lexer::Lexer::new(src).tokenize() else { return };
    let mut p2 = parser::Parser::new(toks2);
    if p2.parse_program().is_err() { return }
    let start = std::time::Instant::now();
    let mut eng2 = engine::Engine::new(p2.g);
    eng2.relax();
    let bulk_time = start.elapsed();
    let bulk_output = eng2.output();

    let Ok(toks3) = lexer::Lexer::new(src).tokenize() else { return };
    let mut p3 = parser::Parser::new(toks3);
    if p3.parse_program().is_err() { return }
    let start_soc = std::time::Instant::now();
    let mut eng3 = engine::Engine::new(p3.g);
    eng3.relax_soc();
    let soc_time = start_soc.elapsed();
    let soc_output = eng3.output();

    eprintln!("SOC_BULK_TIME_US:{}", bulk_time.as_micros());
    eprintln!("SOC_SOC_TIME_US:{}", soc_time.as_micros());
    eprintln!("SOC_OUTPUT_MATCH:{}", bulk_output == soc_output);
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
