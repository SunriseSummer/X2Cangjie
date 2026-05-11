func double(x: Int64): Int64 {
    return x * 2
}

open class Box {
    var value: Int64 = 0
    init(v: Int64) {
        this.value = v
    }
    public open func show(): Unit {
        println("box=${this.value}")
    }
}

let b = Box(double(7))

main() {
    b.show()
    return 0
}
