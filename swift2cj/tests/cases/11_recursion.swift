func fact(_ n: Int) -> Int {
    if n <= 1 {
        return 1
    }
    return n * fact(n - 1)
}
print(fact(5))
print(fact(7))
