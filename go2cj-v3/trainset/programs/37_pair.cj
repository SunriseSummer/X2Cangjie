open class Pair {
    public var A: Int64
    public var B: Int64
    public init(A: Int64, B: Int64) {
        this.A = A
        this.B = B
    }
}

main() {
    var p = Pair(7, 8)
    println(p.A)
    println(p.B)
    println(p.A + p.B)
    return 0
}
