import std.collection.*

main() {
    let greeting = { => ("Hello" + " ") + "World" }()
    println(greeting)
    let computed = { =>
        let x = 10
        let y = 20
        x + y
    }()
    println(computed)
    let items = { => ArrayList([1, 2, 3]) }()
    println(items.size)
}
