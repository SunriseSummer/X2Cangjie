func pow(_ base: Int, _ exp: Int) -> Int {
    var r: Int = 1
    var i: Int = 0
    while i < exp {
        r = r * base
        i = i + 1
    }
    return r
}
print(pow(2, 10))
print(pow(3, 4))
print(pow(5, 0))
