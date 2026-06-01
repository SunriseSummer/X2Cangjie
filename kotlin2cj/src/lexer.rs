//! 词法分析器：把 Kotlin 源码切分为 Token 流。
//!
//! 字符串模板（`"...$x...${expr}..."`）在这里被拆解为若干 *片段*，
//! 这样每一个插值表达式都能够作为独立的子图进入自组织翻译引擎。

#[derive(Debug, Clone, PartialEq)]
pub enum Tok {
    Ident(String),
    Int(String),
    Float(String),
    /// 字符串模板，已拆分为字面量片段与插值表达式片段。
    Str(Vec<StrPart>),
    Char(String),
    /// 运算符 / 标点
    Sym(String),
    Newline,
    Eof,
}

/// 字符串模板的一个片段。
#[derive(Debug, Clone, PartialEq)]
pub enum StrPart {
    /// 普通文本（已是目标语言可直接使用的形式）。
    Lit(String),
    /// 插值表达式的原始 Kotlin 文本，稍后会被独立解析与翻译。
    Expr(String),
}

#[derive(Debug, Clone)]
pub struct Token {
    pub tok: Tok,
    pub line: usize,
}

pub struct Lexer<'a> {
    src: &'a [u8],
    pos: usize,
    line: usize,
}

const KEYWORD_SYMS: &[&str] = &[];

impl<'a> Lexer<'a> {
    pub fn new(src: &'a str) -> Self {
        Lexer { src: src.as_bytes(), pos: 0, line: 1 }
    }

    fn peek(&self) -> u8 {
        if self.pos < self.src.len() { self.src[self.pos] } else { 0 }
    }
    fn peek2(&self) -> u8 {
        if self.pos + 1 < self.src.len() { self.src[self.pos + 1] } else { 0 }
    }
    fn bump(&mut self) -> u8 {
        let c = self.peek();
        self.pos += 1;
        if c == b'\n' {
            self.line += 1;
        }
        c
    }

    pub fn tokenize(mut self) -> Result<Vec<Token>, String> {
        let mut out = Vec::new();
        loop {
            self.skip_ws_and_comments();
            if self.pos >= self.src.len() {
                out.push(Token { tok: Tok::Eof, line: self.line });
                break;
            }
            let line = self.line;
            let c = self.peek();
            let tok = if c == b'\n' {
                self.bump();
                Tok::Newline
            } else if c == b'"' {
                self.lex_string()?
            } else if c == b'\'' {
                self.lex_char()?
            } else if c.is_ascii_digit() {
                self.lex_number()
            } else if is_ident_start(c) {
                self.lex_ident()
            } else {
                self.lex_symbol()?
            };
            // 折叠连续换行为单个换行标记。
            if let Tok::Newline = tok {
                if let Some(Token { tok: Tok::Newline, .. }) = out.last() {
                    continue;
                }
            }
            out.push(Token { tok, line });
        }
        Ok(out)
    }

    fn skip_ws_and_comments(&mut self) {
        loop {
            let c = self.peek();
            if c == b' ' || c == b'\t' || c == b'\r' {
                self.bump();
            } else if c == b'/' && self.peek2() == b'/' {
                while self.peek() != b'\n' && self.pos < self.src.len() {
                    self.bump();
                }
            } else if c == b'/' && self.peek2() == b'*' {
                self.bump();
                self.bump();
                while self.pos < self.src.len() && !(self.peek() == b'*' && self.peek2() == b'/') {
                    self.bump();
                }
                self.bump();
                self.bump();
            } else {
                break;
            }
        }
    }

    fn lex_ident(&mut self) -> Tok {
        let start = self.pos;
        while is_ident_continue(self.peek()) {
            self.bump();
        }
        let s = std::str::from_utf8(&self.src[start..self.pos]).unwrap().to_string();
        Tok::Ident(s)
    }

    fn lex_number(&mut self) -> Tok {
        let start = self.pos;
        // 十六进制 / 二进制字面量：`0x..` / `0b..`（仓颉同样支持，原样保留，仅去后缀）。
        if self.peek() == b'0' && matches!(self.peek2(), b'x' | b'X' | b'b' | b'B') {
            self.bump(); // 0
            self.bump(); // x / b
            while self.peek().is_ascii_alphanumeric() || self.peek() == b'_' {
                self.bump();
            }
            // 去掉整型后缀 L/u/U
            while matches!(self.peek(), b'L' | b'u' | b'U') {
                self.bump();
            }
            let raw = std::str::from_utf8(&self.src[start..self.pos]).unwrap();
            let s: String = raw
                .chars()
                .filter(|c| !matches!(c, 'L' | 'u' | 'U'))
                .collect();
            return Tok::Int(s);
        }
        let mut is_float = false;
        while self.peek().is_ascii_digit() || self.peek() == b'_' {
            self.bump();
        }
        if self.peek() == b'.' && self.peek2().is_ascii_digit() {
            is_float = true;
            self.bump();
            while self.peek().is_ascii_digit() {
                self.bump();
            }
        }
        if self.peek() == b'e' || self.peek() == b'E' {
            is_float = true;
            self.bump();
            if self.peek() == b'+' || self.peek() == b'-' {
                self.bump();
            }
            while self.peek().is_ascii_digit() {
                self.bump();
            }
        }
        // 数值后缀（L / f / F / u 等）—— 去掉，靠类型推断。
        let mut suffix_float = false;
        while matches!(self.peek(), b'L' | b'f' | b'F' | b'u' | b'U') {
            if matches!(self.peek(), b'f' | b'F') {
                suffix_float = true;
            }
            self.bump();
        }
        let s = std::str::from_utf8(&self.src[start..self.pos]).unwrap();
        // 去掉后缀，保留下划线分隔符（仓颉支持 `1_000`）。
        let s: String = s.chars().filter(|c| c.is_ascii_digit() || *c == '.' || *c == 'e' || *c == 'E' || *c == '+' || *c == '-' || *c == '_').collect();
        if is_float || suffix_float {
            Tok::Float(s)
        } else {
            Tok::Int(s)
        }
    }

    fn lex_char(&mut self) -> Result<Tok, String> {
        self.bump(); // '
        let start = self.pos;
        while self.peek() != b'\'' && self.pos < self.src.len() {
            if self.peek() == b'\\' {
                self.bump();
            }
            self.bump();
        }
        let s = std::str::from_utf8(&self.src[start..self.pos]).unwrap().to_string();
        if self.peek() != b'\'' {
            return Err(format!("line {}: 未闭合的字符字面量", self.line));
        }
        self.bump(); // '
        Ok(Tok::Char(s))
    }

    /// 解析字符串模板，拆为字面量 / 插值表达式片段。
    fn lex_string(&mut self) -> Result<Tok, String> {
        self.bump(); // "
        // 三引号原始字符串
        if self.peek() == b'"' && self.peek2() == b'"' {
            return self.lex_raw_string();
        }
        let mut parts: Vec<StrPart> = Vec::new();
        let mut buf = String::new();
        loop {
            if self.pos >= self.src.len() {
                return Err(format!("line {}: 未闭合的字符串", self.line));
            }
            let c = self.peek();
            if c == b'"' {
                self.bump();
                break;
            } else if c == b'\\' {
                // 保留转义序列原样（Kotlin 与仓颉转义基本一致）。
                buf.push('\\');
                self.bump();
                buf.push(self.bump() as char);
            } else if c == b'$' {
                if !buf.is_empty() {
                    parts.push(StrPart::Lit(std::mem::take(&mut buf)));
                }
                self.bump(); // $
                if self.peek() == b'{' {
                    self.bump(); // {
                    let mut depth = 1;
                    let start = self.pos;
                    while depth > 0 && self.pos < self.src.len() {
                        match self.peek() {
                            b'{' => depth += 1,
                            b'}' => {
                                depth -= 1;
                                if depth == 0 {
                                    break;
                                }
                            }
                            _ => {}
                        }
                        self.bump();
                    }
                    let expr = std::str::from_utf8(&self.src[start..self.pos]).unwrap().to_string();
                    self.bump(); // }
                    parts.push(StrPart::Expr(expr));
                } else {
                    // 简单 $ident 形式（可带 .member 链）
                    let start = self.pos;
                    while is_ident_continue(self.peek()) {
                        self.bump();
                    }
                    let expr = std::str::from_utf8(&self.src[start..self.pos]).unwrap().to_string();
                    parts.push(StrPart::Expr(expr));
                }
            } else {
                let ch_start = self.pos;
                // 处理多字节 UTF-8
                self.bump();
                while self.peek() >= 0x80 && self.peek() < 0xC0 {
                    self.bump();
                }
                buf.push_str(std::str::from_utf8(&self.src[ch_start..self.pos]).unwrap());
            }
        }
        if !buf.is_empty() {
            parts.push(StrPart::Lit(buf));
        }
        Ok(Tok::Str(parts))
    }

    fn lex_raw_string(&mut self) -> Result<Tok, String> {
        self.bump(); // 2nd "
        self.bump(); // 3rd "
        let mut buf = String::new();
        loop {
            if self.pos >= self.src.len() {
                return Err(format!("line {}: 未闭合的三引号字符串", self.line));
            }
            if self.peek() == b'"' && self.peek2() == b'"'
                && self.pos + 2 < self.src.len() && self.src[self.pos + 2] == b'"'
            {
                self.bump();
                self.bump();
                self.bump();
                break;
            }
            let c = self.bump();
            if c == b'\n' {
                buf.push_str("\\n");
            } else if c == b'\\' {
                buf.push_str("\\\\");
            } else if c == b'"' {
                buf.push_str("\\\"");
            } else {
                buf.push(c as char);
            }
        }
        Ok(Tok::Str(vec![StrPart::Lit(buf)]))
    }

    fn lex_symbol(&mut self) -> Result<Tok, String> {
        // 多字符运算符
        let three: Vec<&str> = vec!["===", "!=="]; // 退化为 == / !=
        let two: Vec<&str> = vec![
            "==", "!=", "<=", ">=", "&&", "||", "++", "--", "+=", "-=", "*=", "/=", "%=",
            "->", "?.", "?:", "::", "..",
        ];
        let rest = std::str::from_utf8(&self.src[self.pos..]).unwrap_or("");
        for s in &three {
            if rest.starts_with(s) {
                for _ in 0..s.len() {
                    self.bump();
                }
                let mapped = if *s == "===" { "==" } else { "!=" };
                return Ok(Tok::Sym(mapped.to_string()));
            }
        }
        for s in &two {
            if rest.starts_with(s) {
                for _ in 0..2 {
                    self.bump();
                }
                return Ok(Tok::Sym(s.to_string()));
            }
        }
        let c = self.bump() as char;
        let _ = KEYWORD_SYMS;
        Ok(Tok::Sym(c.to_string()))
    }
}

fn is_ident_start(c: u8) -> bool {
    c == b'_' || c.is_ascii_alphabetic() || c >= 0x80
}
fn is_ident_continue(c: u8) -> bool {
    c == b'_' || c.is_ascii_alphanumeric() || c >= 0x80
}
