//! 项目级转换：将 Kotlin 项目目录转换为仓颉 cjpm 项目。
//!
//! 职责：
//! - 扫描目录中的 .kt 文件
//! - 提取 package/import 信息
//! - 合并翻译（保持完整类型上下文）
//! - 按原始文件结构拆分输出为多个 .cj 文件
//! - 生成 cjpm.toml 和目录结构
//! - 输出映射后的 import 语句

use std::collections::{HashMap, HashSet};
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

/// 从 Kotlin 源码中提取顶层声明名称（class/enum/interface/object/fun）。
/// 只提取缩进为 0 的行（真正的顶层声明）。
fn extract_top_level_names(src: &str) -> Vec<String> {
    let mut names = Vec::new();
    for line in src.lines() {
        // 只处理无缩进的行（顶层声明）
        if line.starts_with(' ') || line.starts_with('\t') {
            continue;
        }
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        // 跳过 import / package
        if trimmed.starts_with("import ") || trimmed.starts_with("package ") {
            continue;
        }
        // 跳过修饰符前缀，找到 class/enum/interface/object/fun 关键字
        let tokens: Vec<&str> = trimmed.split_whitespace().collect();
        let mut idx = 0;
        const MODS: &[&str] = &[
            "public", "private", "internal", "protected", "open", "final", "abstract",
            "override", "inline", "data", "sealed", "const", "lateinit", "tailrec",
            "annotation",
        ];
        while idx < tokens.len() && MODS.contains(&tokens[idx]) {
            idx += 1;
        }
        if idx >= tokens.len() {
            continue;
        }
        let kw = tokens[idx];
        match kw {
            "class" | "interface" | "object" | "enum" => {
                // "enum" 后面可能跟 "class"
                let name_idx = if kw == "enum" && idx + 1 < tokens.len() && tokens[idx + 1] == "class" {
                    idx + 2
                } else {
                    idx + 1
                };
                if name_idx < tokens.len() {
                    // 用 split 而非 trim_end 来处理 "Account(val" → "Account"
                    let raw = tokens[name_idx];
                    let name = raw.split('(').next().unwrap_or(raw);
                    let name = name.split('{').next().unwrap_or(name);
                    let name = name.split(':').next().unwrap_or(name);
                    let name = name.split('<').next().unwrap_or(name);
                    if !name.is_empty() {
                        names.push(name.to_string());
                    }
                }
            }
            "fun" => {
                // 提取函数名（跳过泛型参数 <T>）
                let name_idx = idx + 1;
                if name_idx < tokens.len() {
                    let raw = tokens[name_idx];
                    let name = raw.split('(').next().unwrap_or(raw)
                        .split('<').next().unwrap_or(raw);
                    if !name.is_empty() && name != "main" {
                        names.push(name.to_string());
                    }
                }
            }
            _ => {}
        }
    }
    names
}

/// 翻译后的顶层代码块。
struct TopLevelBlock {
    /// 块的声明名称（class/enum/extend 的名称，func 名称，或 "main"）。
    name: String,
    /// 块的完整文本。
    text: String,
}

/// 将翻译后的代码体拆分为顶层声明块。
///
/// 识别在第 0 列开始的声明：class, enum, extend, func, main, let, var。
/// 通过大括号匹配确定块的范围。
fn split_into_blocks(code: &str) -> Vec<TopLevelBlock> {
    let mut blocks = Vec::new();
    let lines: Vec<&str> = code.lines().collect();
    let mut i = 0;
    while i < lines.len() {
        let line = lines[i];
        // 跳过空行
        if line.trim().is_empty() {
            i += 1;
            continue;
        }
        // 顶层声明必须从第 0 列开始（无前导空格）
        if line.starts_with(' ') || line.starts_with('\t') {
            // 孤立的非声明行（如全局变量），归入特殊块
            let text = String::from(line);
            i += 1;
            blocks.push(TopLevelBlock {
                name: String::new(),
                text,
            });
            continue;
        }
        // 解析声明名称
        let name = extract_block_name(line);
        // 收集整个块（包括大括号匹配的范围）
        let mut text = String::from(line);
        let mut brace_depth: i32 = count_braces(line);
        i += 1;
        // 如果打开了大括号但未关闭，继续收集行直到关闭
        while i < lines.len() && brace_depth > 0 {
            text.push('\n');
            text.push_str(lines[i]);
            brace_depth += count_braces(lines[i]);
            i += 1;
        }
        blocks.push(TopLevelBlock { name, text });
    }
    blocks
}

/// 从仓颉顶层声明行提取名称。
fn extract_block_name(line: &str) -> String {
    let tokens: Vec<&str> = line.split_whitespace().collect();
    if tokens.is_empty() {
        return String::new();
    }
    match tokens[0] {
        "class" | "interface" | "enum" | "extend" | "sealed" => {
            if tokens.len() > 1 {
                tokens[1]
                    .trim_end_matches('{')
                    .trim_end_matches('<')
                    .trim_end_matches(':')
                    .trim_start_matches('@')
                    .to_string()
            } else {
                String::new()
            }
        }
        "open" | "abstract" => {
            // open class Foo / abstract class Foo
            if tokens.len() > 2 && (tokens[1] == "class" || tokens[1] == "interface") {
                tokens[2]
                    .trim_end_matches('{')
                    .trim_end_matches('<')
                    .trim_end_matches(':')
                    .to_string()
            } else {
                String::new()
            }
        }
        "func" => {
            if tokens.len() > 1 {
                tokens[1].split('(').next().unwrap_or("").to_string()
            } else {
                String::new()
            }
        }
        "main()" | "main" => "main".to_string(),
        "let" | "var" => {
            if tokens.len() > 1 {
                tokens[1].trim_end_matches(':').trim_end_matches('=').to_string()
            } else {
                String::new()
            }
        }
        _ => {
            // main() { 形式
            if tokens[0].starts_with("main(") {
                "main".to_string()
            } else {
                String::new()
            }
        }
    }
}

/// 统计一行中的大括号差值（'{' 个数 - '}' 个数），跳过字符串内的大括号。
fn count_braces(line: &str) -> i32 {
    let mut depth: i32 = 0;
    let mut in_string = false;
    let mut in_template = 0i32;
    let bytes = line.as_bytes();
    let mut j = 0;
    while j < bytes.len() {
        let c = bytes[j];
        if in_string {
            if c == b'\\' {
                j += 1; // skip escaped char
            } else if c == b'"' {
                in_string = false;
            } else if c == b'$' && j + 1 < bytes.len() && bytes[j + 1] == b'{' {
                in_template += 1;
                in_string = false; // 进入模板表达式，由 in_template 分支处理
                j += 1;
                depth += 1;
            }
        } else if in_template > 0 {
            if c == b'{' {
                depth += 1;
            } else if c == b'}' {
                depth -= 1;
                // 检查是否退出模板
                in_template -= 1;
                if in_template == 0 {
                    // 回到字符串内部
                    in_string = true;
                }
            } else if c == b'"' {
                in_string = true;
            }
        } else {
            if c == b'"' {
                in_string = true;
            } else if c == b'{' {
                depth += 1;
            } else if c == b'}' {
                depth -= 1;
            }
        }
        j += 1;
    }
    depth
}

/// 生成文件头（package + imports）。
fn make_file_header(cangjie_pkg: &str, cangjie_imports: &[String]) -> String {
    let mut header = format!("package {}\n", cangjie_pkg);
    if !cangjie_imports.is_empty() {
        header.push('\n');
        for imp in cangjie_imports {
            header.push_str(imp);
            header.push('\n');
        }
    }
    header.push('\n');
    header
}

/// 将 .kt 文件路径转换为对应的 .cj 文件名。
fn kt_to_cj_filename(kt_path: &Path) -> String {
    let stem = kt_path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("file");
    // 保持原名小写，只改扩展名
    format!("{}.cj", stem.to_lowercase())
}

/// 执行项目级转换。
///
/// 策略：将所有 .kt 文件合并为单一翻译单元，利用完整的类型上下文进行翻译，
/// 然后将翻译结果按原始文件结构拆分回多个 .cj 文件。
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

    // 4. 读取所有文件，提取 import 信息和顶层声明名称
    let mut all_imports: HashSet<String> = HashSet::new();
    let mut file_sources: Vec<(PathBuf, String, bool)> = Vec::new();
    let mut merged_source = String::new();
    // 声明名称 → 源文件路径的映射
    let mut name_to_file: HashMap<String, PathBuf> = HashMap::new();
    // 含 main 的文件
    let mut main_file: Option<PathBuf> = None;

    for kt in &kt_files {
        let src = std::fs::read_to_string(kt)
            .map_err(|e| format!("读取 {} 失败: {}", kt.display(), e))?;
        let imports = extract_imports(&src);
        for imp in &imports {
            all_imports.insert(imp.clone());
        }
        let is_main = has_main_func(&src);
        if is_main {
            main_file = Some(kt.clone());
        }
        // 提取顶层声明名称并建立映射
        let names = extract_top_level_names(&src);
        for name in &names {
            name_to_file.insert(name.clone(), kt.clone());
        }
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
    for (_, src) in &non_main_sources {
        merged_source.push_str(src);
        merged_source.push('\n');
    }
    for (_, src) in &main_sources {
        merged_source.push_str(src);
        merged_source.push('\n');
    }

    // 5. 统一翻译合并后的源码
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

    // 7. 将翻译结果拆分为多个文件
    if kt_files.len() == 1 {
        // 单文件项目：直接写出 main.cj（与之前行为一致）
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
    } else {
        // 多文件项目：按声明名称映射回原始文件
        let blocks = split_into_blocks(&raw_output);

        // 将块分组到对应的源文件
        let mut file_blocks: HashMap<PathBuf, Vec<String>> = HashMap::new();
        // 初始化所有源文件的空块列表
        for (path, _, _) in &file_sources {
            file_blocks.insert(path.clone(), Vec::new());
        }

        // 未能映射的块收集到 main 文件
        let fallback_file = main_file.clone()
            .unwrap_or_else(|| kt_files[0].clone());

        for block in &blocks {
            if block.name == "main" {
                // main 块归属于含有 fun main 的文件
                let target = main_file.as_ref().unwrap_or(&fallback_file);
                file_blocks.entry(target.clone()).or_default().push(block.text.clone());
            } else if !block.name.is_empty() {
                if let Some(path) = name_to_file.get(&block.name) {
                    file_blocks.entry(path.clone()).or_default().push(block.text.clone());
                } else {
                    // 对于 extend 块，尝试提取目标类型名并映射到对应文件
                    let first_line = block.text.lines().next().unwrap_or("");
                    let extend_target = if first_line.trim_start().starts_with("extend ") {
                        let tokens: Vec<&str> = first_line.split_whitespace().collect();
                        tokens.get(1).map(|t| {
                            t.split('<').next().unwrap_or(t)
                                .split('{').next().unwrap_or(t)
                                .to_string()
                        })
                    } else {
                        None
                    };
                    if let Some(ref target_name) = extend_target {
                        if let Some(path) = name_to_file.get(target_name) {
                            file_blocks.entry(path.clone()).or_default().push(block.text.clone());
                        } else {
                            file_blocks.entry(fallback_file.clone()).or_default().push(block.text.clone());
                        }
                    } else {
                        file_blocks.entry(fallback_file.clone()).or_default().push(block.text.clone());
                    }
                }
            } else {
                // 无名块（全局变量等）归入 fallback 文件
                file_blocks.entry(fallback_file.clone()).or_default().push(block.text.clone());
            }
        }

        // 写出各文件
        let header = make_file_header(&cangjie_pkg, &cangjie_imports);
        for (path, blocks) in &file_blocks {
            if blocks.is_empty() {
                continue;
            }
            let filename = kt_to_cj_filename(path);
            let mut content = header.clone();
            content.push_str(&blocks.join("\n\n"));
            content.push('\n');

            let out_path = src_dir.join(&filename);
            std::fs::write(&out_path, &content)
                .map_err(|e| format!("写入 {} 失败: {}", out_path.display(), e))?;
        }
    }

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
