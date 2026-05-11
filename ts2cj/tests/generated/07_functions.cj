func add(a: Int64, b: Int64): Int64 {
    return a + b
}

func mul(a: Int64, b: Int64): Int64 {
    return a * b
}

let x: Int64 = add(3, 4)

let y: Int64 = mul(x, 2)

main() {
    println("x=${x} y=${y}")
    return 0
}
