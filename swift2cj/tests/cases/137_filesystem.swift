// Large #1 (iter10): in-memory filesystem tree size aggregation
class FileNode {
    let name: String
    let isDir: Bool
    var size: Int
    var children: [FileNode] = []
    init(_ name: String, _ isDir: Bool, _ size: Int) {
        self.name = name
        self.isDir = isDir
        self.size = size
    }
    func add(_ child: FileNode) { children.append(child) }
    func totalSize() -> Int {
        if !isDir { return size }
        var total = 0
        for c in children { total += c.totalSize() }
        return total
    }
    func list(_ prefix: String) {
        let path = prefix + "/" + name
        print(path + " size=\(totalSize())")
        for c in children { c.list(path) }
    }
}

let root = FileNode("root", true, 0)
let src = FileNode("src", true, 0)
src.add(FileNode("main.cj", false, 120))
src.add(FileNode("util.cj", false, 80))
let docs = FileNode("docs", true, 0)
docs.add(FileNode("readme.md", false, 30))
let assets = FileNode("assets", true, 0)
assets.add(FileNode("logo.png", false, 200))
docs.add(assets)
root.add(src)
root.add(docs)
root.list("")
