import std.collection.*

open class Stack {
    public var items: ArrayList<Int64>
    public init() {
        this.items = ArrayList<Int64>()
    }
    public func Push(v: Int64): Unit {
        this.items.add(v)
    }
    public func Pop(): Int64 {
        let n = this.items.size
        let v = this.items[n - 1]
        this.items.remove(at: n - 1)
        return v
    }
    public func Size(): Int64 {
        return this.items.size
    }
}

main() {
    let s = Stack()
    s.Push(10)
    s.Push(20)
    s.Push(30)
    println(s.Size())
    println(s.Pop())
    println(s.Pop())
    println(s.Size())
    return 0
}
