func mymin(_ a: Int, _ b: Int) -> Int {
    if a < b {
        return a
    }
    return b
}
func mymax(_ a: Int, _ b: Int) -> Int {
    if a > b {
        return a
    }
    return b
}
print(mymin(3, 7))
print(mymax(3, 7))
print(mymin(-1, -5))
print(mymax(-1, -5))
