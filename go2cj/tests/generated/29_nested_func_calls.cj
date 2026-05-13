func double(x: Int64): Int64 {
    return x * 2
}

func inc(x: Int64): Int64 {
    return x + 1
}

main() {
    println(double(inc(5)))
    return 0
}
