import std.collection.*

open class Rectangle {
    public var W: Int64
    public var H: Int64
    public init(W: Int64, H: Int64) {
        this.W = W
        this.H = H
    }
    public func Area(): Int64 {
    return this.W * this.H
    }
}

main() {
    var r = Rectangle(4, 5)
    println(r.Area())
    var xs = ArrayList<Int64>([1, 2, 3])
    var total = 0
    for (v in xs) {
        total += v
    }
    println(total)
    return 0
}
