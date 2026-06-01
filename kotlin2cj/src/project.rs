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

/// 从 Kotlin 源码中提取 package 声明。
fn extract_package(src: &str) -> Option<String> {
    for line in src.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("package ") {
            return Some(trimmed["package ".len()..].trim().trim_end_matches(';').to_string());
        }
        // 跳过空行和注释
        if trimmed.is_empty() || trimmed.starts_with("//") || trimmed.starts_with("/*") {
            continue;
        }
        // 遇到 import 或其他内容则停止
        if trimmed.starts_with("import ") || trimmed.starts_with("fun ")
            || trimmed.starts_with("class ") || trimmed.starts_with("val ")
            || trimmed.starts_with("var ") || trimmed.starts_with("object ")
        {
            break;
        }
    }
    None
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

/// 翻译单个文件并返回仓颉代码（剥离 import 头）。
fn translate_file(src: &str) -> Result<String, String> {
    let toks = crate::lexer::Lexer::new(src).tokenize()?;
    let mut p = crate::parser::Parser::new(toks);
    p.parse_program()?;
    let mut eng = crate::engine::Engine::new(p.g);
    eng.relax();
    let raw = eng.output();
    Ok(strip_auto_imports(&raw))
}

/// 执行项目级转换。
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

    // 4. 分析所有文件的 package/import 信息
    let mut all_imports: HashSet<String> = HashSet::new();
    let mut file_contents: Vec<(PathBuf, String, bool)> = Vec::new(); // (path, source, has_main)

    for kt in &kt_files {
        let src = std::fs::read_to_string(kt)
            .map_err(|e| format!("读取 {} 失败: {}", kt.display(), e))?;
        let imports = extract_imports(&src);
        for imp in &imports {
            all_imports.insert(imp.clone());
        }
        let is_main = has_main_func(&src);
        file_contents.push((kt.clone(), src, is_main));
    }

    // 5. 映射 import（检测是否用到集合类型）
    let all_imports_vec: Vec<String> = all_imports.into_iter().collect();

    // 6. 翻译每个文件
    let mut files_translated = 0;
    let mut files_failed = Vec::new();
    let mut translated_files: Vec<(String, String, bool)> = Vec::new(); // (filename, code, has_main)
    let mut all_raw_code = String::new();

    for (kt_path, src, is_main) in &file_contents {
        let raw_toks = crate::lexer::Lexer::new(src).tokenize();
        let raw_code = match raw_toks {
            Ok(toks) => {
                let mut p = crate::parser::Parser::new(toks);
                match p.parse_program() {
                    Ok(_) => {
                        let mut eng = crate::engine::Engine::new(p.g);
                        eng.relax();
                        eng.output()
                    }
                    Err(e) => {
                        files_failed.push((kt_path.clone(), e));
                        continue;
                    }
                }
            }
            Err(e) => {
                files_failed.push((kt_path.clone(), e));
                continue;
            }
        };

        all_raw_code.push_str(&raw_code);

        let code = strip_auto_imports(&raw_code);
        let filename = kt_path
            .file_stem()
            .and_then(|n| n.to_str())
            .unwrap_or("unknown");
        let cj_filename = if *is_main {
            "main.cj".to_string()
        } else {
            format!("{}.cj", filename)
        };
        translated_files.push((cj_filename, code, *is_main));
        files_translated += 1;
    }

    // 检测翻译后的代码需要哪些 import
    let needs_collection = all_raw_code.contains("import std.collection.*");
    let needs_deriving = all_raw_code.contains("import std.deriving.*");
    let needs_convert = all_raw_code.contains("import std.convert.*");
    let needs_sort = all_raw_code.contains("import std.sort.*");

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

    // 7. 写出文件（附加 package 和 import 声明）
    for (filename, code, _is_main) in &translated_files {
        let mut output = String::new();

        // package 声明
        output.push_str(&format!("package {}\n\n", cangjie_pkg));

        // import 声明（只有项目中确实用到的）
        for imp in &cangjie_imports {
            output.push_str(imp);
            output.push('\n');
        }
        if !cangjie_imports.is_empty() {
            output.push('\n');
        }

        // 翻译后的代码
        output.push_str(code);

        let out_path = src_dir.join(filename);
        std::fs::write(&out_path, &output)
            .map_err(|e| format!("写入 {} 失败: {}", out_path.display(), e))?;
    }

    // 8. 生成 cjpm.toml
    let toml_content = generate_cjpm_toml(&cangjie_pkg);
    std::fs::write(output_dir.join("cjpm.toml"), &toml_content)
        .map_err(|e| format!("写入 cjpm.toml 失败: {}", e))?;

    Ok(ProjectResult {
        output_dir: output_dir.to_path_buf(),
        files_translated,
        files_failed,
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
