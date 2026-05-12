struct Vec2 {
    var x: Int64 = 0
    var y: Int64 = 0
    public func dot(o: Vec2): Int64 {
        return this.x * o.x + this.y * o.y
    }
    public init(x!: Int64, y!: Int64) {
        this.x = x
        this.y = y
    }
}

let a = Vec2(x: 1, y: 2)

let b = Vec2(x: 3, y: 4)

main() {
    println("dot=${a.dot(b)}")
    return 0
}
