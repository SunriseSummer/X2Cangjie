func square(x: Int64): Int64 {
    return x * x
}

func cube(x: Int64): Int64 {
    return x * square(x)
}

main() {
    println(square(4))
    println(cube(3))
    println(cube(square(2)))
    return 0
}
