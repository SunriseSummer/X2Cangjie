import std.collection.*

interface Greeter {
    func hello(): String
}

open class Eng <: Greeter {
    public open func hello(): String {
        return "hi"
    }
}

open class Fr <: Greeter {
    public open func hello(): String {
        return "bonjour"
    }
}

let xs: ArrayList<Greeter> = ArrayList<Greeter>([Eng(), Fr()])

main() {
    for (g in xs) {
        println(g.hello())
    }
    return 0
}
