func sumOdd(_ n: Int) -> Int {
    var s: Int = 0
    for i in 1...n {
        if i % 2 != 0 {
            s = s + i
        }
    }
    return s
}
print(sumOdd(10))
print(sumOdd(20))
