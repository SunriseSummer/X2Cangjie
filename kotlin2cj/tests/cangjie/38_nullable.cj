func describe(name: ?String): String {
    return name ?? "unknown"
}

main() {
    let a: ?String = None
    let b: ?String = "Kotlin"
    println(describe(a))
    println(describe(b))
    println(a ?? "none")
}
