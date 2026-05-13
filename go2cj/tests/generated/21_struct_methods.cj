open class Counter {
    public var Value: Int64
    public init(Value: Int64) {
        this.Value = Value
    }
    public func Get(): Int64 {
    return this.Value
    }
}

main() {
    var c = Counter(42)
    println(c.Get())
    return 0
}
