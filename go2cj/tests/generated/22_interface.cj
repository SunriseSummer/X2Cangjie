interface Greeter {
    func Greet(): String
}

open class English <: Greeter {
    public init() {}
    public override func Greet(): String {
    return "Hello"
    }
}

main() {
    var g: Greeter = English()
    println(g.Greet())
    return 0
}
