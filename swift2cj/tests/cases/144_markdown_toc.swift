// Large #2 (iter11): markdown heading extraction and table of contents
class Heading {
    let level: Int
    let title: String
    init(_ level: Int, _ title: String) {
        self.level = level
        self.title = title
    }
    func anchor() -> String {
        var s = ""
        for ch in title {
            if ch == " " { s = s + "-" } else { s = s + "\(ch)" }
        }
        return s
    }
    func line() -> String {
        var indent = ""
        var i = 1
        while i < level { indent = indent + "  "; i += 1 }
        return indent + "- " + title + " (#" + anchor() + ")"
    }
}

func parseHeadings(_ lines: [String]) -> [Heading] {
    var out: [Heading] = []
    for line in lines {
        var level = 0
        for ch in line {
            if ch == "#" { level += 1 } else { break }
        }
        if level > 0 && level < line.count {
            var title = ""
            var idx = 0
            for ch in line {
                if idx > level { title = title + "\(ch)" }
                idx += 1
            }
            out.append(Heading(level, title))
        }
    }
    return out
}

let doc = [
    "# Intro",
    "text",
    "## Setup",
    "### Install SDK",
    "## Usage",
    "# Appendix"
]
for h in parseHeadings(doc) { print(h.line()) }
