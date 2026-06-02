import std.collection.*

extend Int64 {
    func isPositive(): Bool {
        return this > 0
    }
}

extend Int64 {
    func square(): Int64 {
        return this * this
    }
}

extend String {
    func addBrackets(): String {
        return "[${this}]"
    }
}

main() {
    println("5.isPositive: ${5.isPositive()}")
    let neg = -3
    println("-3.isPositive: ${neg.isPositive()}")
    println("4.square: ${4.square()}")
    println("Hello.addBrackets: ${"Hello".addBrackets()}")
    let list = ArrayList([10, 20, 30])
    println("list size: ${list.size}")
}
