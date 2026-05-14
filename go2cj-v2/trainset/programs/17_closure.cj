func makeAdder(x: Int64): (Int64) -> Int64 {
    return {y: Int64 => x + y}
}

main() {
    let add5 = makeAdder(5)
    let add10 = makeAdder(10)
    println(add5(3))
    println(add10(3))
    println(add5(add10(1)))
    return 0
}
