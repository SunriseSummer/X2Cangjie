//! 项目级转换：将 Kotlin 项目目录转换为仓颉 cjpm 项目。
//!
//! 职责：
//! - 扫描目录中的 .kt 文件
//! - 提取 package/import 信息
//! - 逐文件翻译
//! - 生成 cjpm.toml 和目录结构
//! - 输出映射后的 import 语句

use std::collections::HashSet;
use std::path::{Path, PathBuf};

use crate::stdlib_map;

/// 项目转换的结果。
pub struct ProjectResult {
    pub output_dir: PathBuf,
    pub files_translated: usize,
    pub files_failed: Vec<(PathBuf, String)>,
}

/// 从 Kotlin 源码中提取 import 声明列表。
fn extract_imports(src: &str) -> Vec<String> {
    let mut imports = Vec::new();
    for line in src.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("import ") {
            imports.push(trimmed["import ".len()..].trim().trim_end_matches(';').to_string());
        }
    }
    imports
}

/// 将 Kotlin import 映射为仓颉 import。
fn map_imports(kotlin_imports: &[String], uses_collection: bool) -> Vec<String> {
    let mut cangjie_imports: HashSet<String> = HashSet::new();
    // 如果用到了集合类型，导入 std.collection
    if uses_collection {
        cangjie_imports.insert("import std.collection.*".to_string());
    }

    for ki in kotlin_imports {
        if let Some(ci) = stdlib_map::lookup_import(ki) {
            if !ci.is_empty() {
                cangjie_imports.insert(ci.to_string());
            }
        }
    }
    let mut sorted: Vec<String> = cangjie_imports.into_iter().collect();
    sorted.sort();
    sorted
}

/// 将 Kotlin 包名转换为仓颉包名。
fn map_package_name(kotlin_pkg: &str) -> String {
    // Kotlin: com.example.myapp → 仓颉: myapp
    // 取最后一段作为包名
    kotlin_pkg
        .rsplit('.')
        .next()
        .unwrap_or(kotlin_pkg)
        .to_string()
}

/// 生成 cjpm.toml 内容。
fn generate_cjpm_toml(project_name: &str) -> String {
    format!(
        r#"[package]
  cjc-version = "1.0.5"
  name = "{name}"
  version = "1.0.0"
  output-type = "executable"
"#,
        name = project_name
    )
}

/// 判断文件是否包含 main 函数。
fn has_main_func(src: &str) -> bool {
    for line in src.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("fun main(") || trimmed == "fun main() {" || trimmed.starts_with("fun main()") {
            return true;
        }
    }
    false
}

/// 从翻译输出中剥离自动生成的 import 头（项目模式下由项目级控制 import）。
fn strip_auto_imports(code: &str) -> String {
    let mut lines: Vec<&str> = Vec::new();
    let mut skipping_header = true;
    for line in code.lines() {
        if skipping_header {
            if line.starts_with("import ") || line.is_empty() {
                continue;
            }
            skipping_header = false;
        }
        lines.push(line);
    }
    lines.join("\n")
}

/// 翻译源码，返回 (完整输出含 import, 剥离 import 后的代码体)。
fn translate_file(src: &str) -> Result<(String, String), String> {
    let toks = crate::lexer::Lexer::new(src).tokenize()?;
    let mut p = crate::parser::Parser::new(toks);
    p.parse_program()?;
    let mut eng = crate::engine::Engine::new(p.g);
    eng.relax();
    let full = eng.output();
    let stripped = strip_auto_imports(&full);
    Ok((full, stripped))
}

/// 执行项目级转换。
///
/// 策略：将所有 .kt 文件合并为单一翻译单元，利用完整的类型上下文进行翻译，
/// 然后将翻译结果拆分回各文件。
pub fn convert_project(input_dir: &Path, output_dir: &Path) -> Result<ProjectResult, String> {
    // 1. 扫描 .kt 文件
    let kt_files = scan_kt_files(input_dir)?;
    if kt_files.is_empty() {
        return Err(format!("目录 {} 中没有找到 .kt 文件", input_dir.display()));
    }

    // 2. 确定项目名称
    let project_name = input_dir
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("project")
        .to_string();

    let cangjie_pkg = map_package_name(&project_name);

    // 3. 创建输出目录结构
    let src_dir = output_dir.join("src");
    std::fs::create_dir_all(&src_dir)
        .map_err(|e| format!("创建目录失败: {}", e))?;

    // 4. 读取所有文件，提取 import 信息，构建合并源码
    let mut all_imports: HashSet<String> = HashSet::new();
    let mut file_sources: Vec<(PathBuf, String, bool)> = Vec::new();
    let mut merged_source = String::new();

    for kt in &kt_files {
        let src = std::fs::read_to_string(kt)
            .map_err(|e| format!("读取 {} 失败: {}", kt.display(), e))?;
        let imports = extract_imports(&src);
        for imp in &imports {
            all_imports.insert(imp.clone());
        }
        let is_main = has_main_func(&src);
        file_sources.push((kt.clone(), src, is_main));
    }

    // 按顺序合并源码：非 main 文件在前，main 文件在后
    let mut non_main_sources: Vec<(&PathBuf, &str)> = Vec::new();
    let mut main_sources: Vec<(&PathBuf, &str)> = Vec::new();
    for (path, src, is_main) in &file_sources {
        if *is_main {
            main_sources.push((path, src));
        } else {
            non_main_sources.push((path, src));
        }
    }
    // 在非 main 文件之间插入分隔符（每个文件的 package/import 已被 parser 跳过）
    for (_, src) in &non_main_sources {
        merged_source.push_str(src);
        merged_source.push('\n');
    }
    for (_, src) in &main_sources {
        merged_source.push_str(src);
        merged_source.push('\n');
    }

    // 5. 统一翻译合并后的源码（一次翻译，同时获取完整输出和剥离 import 的代码体）
    let (full_raw, raw_output) = translate_file(&merged_source)
        .map_err(|e| format!("翻译失败: {}", e))?;

    // 6. 检测需要哪些 import
    let all_imports_vec: Vec<String> = all_imports.into_iter().collect();
    let needs_collection = full_raw.contains("import std.collection.*");
    let needs_deriving = full_raw.contains("import std.deriving.*");
    let needs_convert = full_raw.contains("import std.convert.*");
    let needs_sort = full_raw.contains("import std.sort.*");

    let mut cangjie_imports: Vec<String> = map_imports(&all_imports_vec, needs_collection);
    if needs_deriving && !cangjie_imports.contains(&"import std.deriving.*".to_string()) {
        cangjie_imports.push("import std.deriving.*".to_string());
    }
    if needs_convert && !cangjie_imports.contains(&"import std.convert.*".to_string()) {
        cangjie_imports.push("import std.convert.*".to_string());
    }
    if needs_sort && !cangjie_imports.contains(&"import std.sort.*".to_string()) {
        cangjie_imports.push("import std.sort.*".to_string());
    }
    cangjie_imports.sort();

    // 7. 写出单个合并文件 main.cj（项目所有代码合入一个文件是最安全的策略）
    let mut output = String::new();
    output.push_str(&format!("package {}\n\n", cangjie_pkg));
    for imp in &cangjie_imports {
        output.push_str(imp);
        output.push('\n');
    }
    if !cangjie_imports.is_empty() {
        output.push('\n');
    }
    output.push_str(&raw_output);

    let out_path = src_dir.join("main.cj");
    std::fs::write(&out_path, &output)
        .map_err(|e| format!("写入 {} 失败: {}", out_path.display(), e))?;

    // 8. 生成 cjpm.toml
    let toml_content = generate_cjpm_toml(&cangjie_pkg);
    std::fs::write(output_dir.join("cjpm.toml"), &toml_content)
        .map_err(|e| format!("写入 cjpm.toml 失败: {}", e))?;

    let files_translated = file_sources.len();
    Ok(ProjectResult {
        output_dir: output_dir.to_path_buf(),
        files_translated,
        files_failed: Vec::new(),
    })
}

/// 递归扫描目录中的 .kt 文件。
fn scan_kt_files(dir: &Path) -> Result<Vec<PathBuf>, String> {
    let mut files = Vec::new();
    scan_kt_recursive(dir, &mut files)?;
    files.sort();
    Ok(files)
}

fn scan_kt_recursive(dir: &Path, files: &mut Vec<PathBuf>) -> Result<(), String> {
    let entries = std::fs::read_dir(dir)
        .map_err(|e| format!("无法读取目录 {}: {}", dir.display(), e))?;
    for entry in entries {
        let entry = entry.map_err(|e| format!("读取目录项失败: {}", e))?;
        let path = entry.path();
        if path.is_dir() {
            // 跳过常见非源码目录
            let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
            if name.starts_with('.') || name == "build" || name == "target"
                || name == "node_modules" || name == ".gradle"
            {
                continue;
            }
            scan_kt_recursive(&path, files)?;
        } else if path.extension().and_then(|e| e.to_str()) == Some("kt") {
            files.push(path);
        }
    }
    Ok(())
}
