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

/// 计算 .kt 文件相对于项目根目录的子目录路径（用于子包映射）。
/// 根目录下的文件返回 None，子目录下的文件返回 Some("model") 或 Some("model/entity") 等。
fn compute_relative_subdir(kt_path: &Path, input_dir: &Path) -> Option<String> {
    let parent = kt_path.parent()?;
    let rel = parent.strip_prefix(input_dir).ok()?;
    let s = rel.to_str()?;
    if s.is_empty() {
        None
    } else {
        Some(s.replace('\\', "/"))
    }
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
///
/// 使用栈跟踪 `${}` 模板表达式的嵌套：模板内的 `{...}` 对（如 lambda）
/// 需要独立计数，不能与模板的闭合 `}` 混淆。
fn count_braces(line: &str) -> i32 {
    let mut depth: i32 = 0;
    let mut in_string = false;
    // 栈：每个元素表示一层 ${} 模板内的非模板大括号嵌套深度
    let mut template_stack: Vec<i32> = Vec::new();
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
                // 进入模板表达式 ${ ... }
                template_stack.push(0);
                in_string = false;
                j += 1;
                depth += 1;
            }
        } else if !template_stack.is_empty() {
            // 在模板表达式内部
            if c == b'{' {
                // 模板内的嵌套大括号（如 lambda）
                if let Some(top) = template_stack.last_mut() {
                    *top += 1;
                }
                depth += 1;
            } else if c == b'}' {
                depth -= 1;
                let inner = template_stack.last().copied().unwrap_or(0);
                if inner > 0 {
                    // 关闭模板内的嵌套大括号
                    if let Some(top) = template_stack.last_mut() {
                        *top -= 1;
                    }
                } else {
                    // 关闭模板表达式本身
                    template_stack.pop();
                    if template_stack.is_empty() {
                        // 回到字符串内部
                        in_string = true;
                    }
                    // 如果栈非空，说明还在外层模板中
                }
            } else if c == b'"' {
                in_string = true;
            } else if c == b'$' && j + 1 < bytes.len() && bytes[j + 1] == b'{' {
                // 模板内嵌套的模板表达式
                template_stack.push(0);
                j += 1;
                depth += 1;
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

/// 生成文件头（package + imports + 子包间 imports）。
///
/// - `full_pkg`: 该文件的完整包路径（如 "proj.model"）
/// - `cangjie_imports`: 标准库 import 列表
/// - `cross_pkg_imports`: 跨子包 import 列表（如 "import proj.model.*"）
fn make_file_header(full_pkg: &str, cangjie_imports: &[String], cross_pkg_imports: &[String]) -> String {
    let mut header = format!("package {}\n", full_pkg);
    let has_std = !cangjie_imports.is_empty();
    let has_cross = !cross_pkg_imports.is_empty();
    if has_std || has_cross {
        header.push('\n');
        for imp in cangjie_imports {
            header.push_str(imp);
            header.push('\n');
        }
        for imp in cross_pkg_imports {
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

/// 为子包中的代码添加 public 可见性修饰符。
///
/// 仓颉中跨包访问需要 public 修饰。对子包文件中的声明添加 public：
/// - 顶层 class/enum/interface/sealed 声明
/// - 类内成员（let/var/func/init/operator/prop/static）
/// - 不修改已有 public/private/protected/internal 的行
/// - 不修改 main() 函数块中的行
fn add_public_visibility(code: &str) -> String {
    let mut result = Vec::new();
    let mut in_class = false;
    let mut in_main = false;
    let mut class_depth: i32 = 0;
    let mut main_depth: i32 = 0;
    let vis_keywords = ["public ", "private ", "protected ", "internal "];

    for line in code.lines() {
        let trimmed = line.trim();

        // 跳过空行和注释
        if trimmed.is_empty() || trimmed.starts_with("//") || trimmed.starts_with("/*") {
            result.push(line.to_string());
            continue;
        }

        let bc = count_braces(line);

        // 跟踪 main() 块（不修改其内部）
        if in_main {
            main_depth += bc;
            result.push(line.to_string());
            if main_depth <= 0 {
                in_main = false;
                main_depth = 0;
            }
            continue;
        }

        // 已有可见性修饰符，不修改
        if vis_keywords.iter().any(|k| trimmed.starts_with(k)) {
            result.push(line.to_string());
            if in_class {
                class_depth += bc;
                if class_depth <= 0 {
                    in_class = false;
                    class_depth = 0;
                }
            }
            continue;
        }

        if !in_class && !line.starts_with(' ') && !line.starts_with('\t') {
            // 检测 main() 块
            if trimmed.starts_with("main(") || trimmed == "main" {
                in_main = true;
                main_depth = bc;
                result.push(line.to_string());
                continue;
            }
            // 顶层声明
            let top_kws = ["class ", "enum ", "open ", "abstract ", "sealed ", "interface "];
            if top_kws.iter().any(|k| trimmed.starts_with(k)) {
                result.push(format!("public {}", line));
                if bc > 0 {
                    in_class = true;
                    class_depth = bc;
                }
                continue;
            }
        } else if in_class {
            class_depth += bc;
            if class_depth <= 0 {
                in_class = false;
                class_depth = 0;
                result.push(line.to_string());
                continue;
            }
            // 类内成员：添加 public
            let member_kws = ["let ", "var ", "func ", "init(", "init (", "operator ",
                              "prop ", "static ", "mut "];
            if member_kws.iter().any(|k| trimmed.starts_with(k)) {
                let indent: String = line.chars().take_while(|c| c.is_whitespace()).collect();
                result.push(format!("{}public {}", indent, trimmed));
                continue;
            }
            result.push(line.to_string());
            continue;
        }

        result.push(line.to_string());
    }
    result.join("\n")
}

/// 计算某个文件需要的跨子包 import 列表。
///
/// 通过检查代码中引用的类型名来确定实际需要的子包导入，避免循环依赖。
///
/// - 根包文件（subdir=None）：导入所有被引用的子包
/// - 子包文件：导入被引用的其他子包（不导入根包，因为根包是 executable 类型）
fn compute_cross_imports(
    root_pkg: &str,
    my_subdir: &Option<String>,
    _all_subdirs: &HashSet<String>,
    code: &str,
    name_to_subdir: &HashMap<String, String>,
) -> Vec<String> {
    // 找出代码中引用了哪些子包的类型（使用单词边界匹配避免子串误匹配）
    let mut needed_subdirs: HashSet<String> = HashSet::new();
    for (type_name, subdir) in name_to_subdir {
        // 跳过自身子包中的类型
        if let Some(my_sd) = my_subdir {
            if subdir == my_sd {
                continue;
            }
        }
        // 使用单词边界检查：类型名前后不能是字母/数字/下划线
        if contains_word(code, type_name) {
            needed_subdirs.insert(subdir.clone());
        }
    }

    let my_sd_str = my_subdir.as_deref().unwrap_or("");
    let mut imports = Vec::new();
    let mut sorted: Vec<&String> = needed_subdirs.iter()
        .filter(|sd| sd.as_str() != my_sd_str)
        .collect();
    sorted.sort();
    for sd in sorted {
        // 跳过根包的导入（子包不能导入 executable 根包）
        if my_subdir.is_some() && sd.is_empty() {
            continue;
        }
        let sub_pkg = sd.replace('/', ".");
        imports.push(format!("import {}.{}.*", root_pkg, sub_pkg));
    }
    imports
}

/// 检查 code 中是否以"单词"形式包含 word（前后不是字母/数字/下划线）。
fn contains_word(code: &str, word: &str) -> bool {
    let word_bytes = word.as_bytes();
    let code_bytes = code.as_bytes();
    if word_bytes.len() > code_bytes.len() {
        return false;
    }
    let mut start = 0;
    while let Some(pos) = find_substr(code_bytes, word_bytes, start) {
        let before_ok = pos == 0 || !is_word_char(code_bytes[pos - 1]);
        let after_pos = pos + word_bytes.len();
        let after_ok = after_pos >= code_bytes.len() || !is_word_char(code_bytes[after_pos]);
        if before_ok && after_ok {
            return true;
        }
        start = pos + 1;
    }
    false
}

fn is_word_char(c: u8) -> bool {
    c.is_ascii_alphanumeric() || c == b'_'
}

fn find_substr(haystack: &[u8], needle: &[u8], start: usize) -> Option<usize> {
    if needle.is_empty() || start + needle.len() > haystack.len() {
        return None;
    }
    for i in start..=(haystack.len() - needle.len()) {
        if &haystack[i..i + needle.len()] == needle {
            return Some(i);
        }
    }
    None
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

    // 7. 计算每个源文件的子包路径
    let mut file_subdir: HashMap<PathBuf, Option<String>> = HashMap::new();
    let mut all_subdirs: HashSet<String> = HashSet::new();
    for (path, _, _) in &file_sources {
        let subdir = compute_relative_subdir(path, input_dir);
        if let Some(ref sd) = subdir {
            all_subdirs.insert(sd.clone());
        }
        file_subdir.insert(path.clone(), subdir);
    }
    let has_subpackages = !all_subdirs.is_empty();

    // 构建声明名称 → 子包路径的映射（用于精确计算跨包 import）
    let mut name_to_subdir: HashMap<String, String> = HashMap::new();
    if has_subpackages {
        for (name, path) in &name_to_file {
            if let Some(Some(sd)) = file_subdir.get(path) {
                name_to_subdir.insert(name.clone(), sd.clone());
            }
        }
    }

    // 8. 将翻译结果拆分为多个文件
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

        // 为子包项目预先创建子目录
        if has_subpackages {
            for sd in &all_subdirs {
                let sub_dir = src_dir.join(sd);
                std::fs::create_dir_all(&sub_dir)
                    .map_err(|e| format!("创建子包目录失败: {}", e))?;
            }
        }

        // 写出各文件（根据子包路径生成正确的 package 声明和跨包 import）
        for (path, blocks) in &file_blocks {
            if blocks.is_empty() {
                continue;
            }
            let filename = kt_to_cj_filename(path);
            let subdir = file_subdir.get(path).cloned().flatten();

            // 计算该文件的完整包路径
            let full_pkg = match &subdir {
                Some(sd) => format!("{}.{}", cangjie_pkg, sd.replace('/', ".")),
                None => cangjie_pkg.clone(),
            };

            // 计算跨子包 import（基于代码中实际引用的类型）
            let code_text = blocks.join("\n");
            let cross_imports = if has_subpackages {
                compute_cross_imports(&cangjie_pkg, &subdir, &all_subdirs, &code_text, &name_to_subdir)
            } else {
                Vec::new()
            };

            let header = make_file_header(&full_pkg, &cangjie_imports, &cross_imports);
            let mut code_body = blocks.join("\n\n");
            // 子包文件需要添加 public 可见性修饰符以支持跨包访问
            if subdir.is_some() {
                code_body = add_public_visibility(&code_body);
            }
            let mut content = header;
            content.push_str(&code_body);
            content.push('\n');

            // 输出路径：有子包时放入对应子目录
            let out_path = match &subdir {
                Some(sd) => src_dir.join(sd).join(&filename),
                None => src_dir.join(&filename),
            };
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
