func sign(_ x: Int) -> Int {
    if x > 0 {
        if x > 100 {
            return 2
        } else {
            return 1
        }
    } else if x < 0 {
        return -1
    } else {
        return 0
    }
}
print(sign(50))
print(sign(150))
print(sign(-3))
print(sign(0))
