interface Greeter {
    func hello(): String
}

open class English <: Greeter {
    public open func hello(): String {
        return "hi"
    }
}

open class Chinese <: Greeter {
    public open func hello(): String {
        return "ni hao"
    }
}

let g1: Greeter = English()

let g2: Greeter = Chinese()

main() {
    println(g1.hello())
    println(g2.hello())
    return 0
}
