func add(a: Int64, b: Int64): Int64 {
    return a + b
}

func square(n: Int64): Int64 {
    return n * n
}

func greet(name: String): String {
    return "Hi, ${name}"
}

main() {
    println(add(3, 4))
    println(square(5))
    println(greet("Cangjie"))
}
