open class Rect {
    public var W: Int64
    public var H: Int64
    public init(W: Int64, H: Int64) {
        this.W = W
        this.H = H
    }
    public func Area(): Int64 { return this.W * this.H }
    public func Perimeter(): Int64 { return 2 * (this.W + this.H) }
}

open class Circle {
    public var R: Int64
    public init(R: Int64) {
        this.R = R
    }
    public func Area(): Int64 { return 3 * this.R * this.R }
    public func Perimeter(): Int64 { return 6 * this.R }
}

main() {
    let r = Rect(3, 4)
    let c = Circle(5)
    println(r.Area())
    println(r.Perimeter())
    println(c.Area())
    println(c.Perimeter())
    return 0
}
