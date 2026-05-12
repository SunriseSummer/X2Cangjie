func square(_ x: Int) -> Int {
    return x * x
}
func cube(_ x: Int) -> Int {
    return x * square(x)
}
print(square(4))
print(cube(3))
print(cube(square(2)))
