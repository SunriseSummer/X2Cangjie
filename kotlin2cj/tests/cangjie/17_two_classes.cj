class Rect {
    let w: Int64
    let h: Int64
    init(w: Int64, h: Int64) {
        this.w = w
        this.h = h
    }
    func area(): Int64 {
        return w * h
    }
}

class Box {
    let name: String
    let rect: Rect
    init(name: String, rect: Rect) {
        this.name = name
        this.rect = rect
    }
    func describe(): String {
        return "${name} area=${rect.area()}"
    }
}

main() {
    let r = Rect(3, 5)
    let b = Box("panel", r)
    println(b.describe())
}
