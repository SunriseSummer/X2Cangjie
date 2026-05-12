// Small #1: bit manipulation & bitwise operators
let a = 0b1100
let b = 0b1010
print(a & b)
print(a | b)
print(a ^ b)
print(a << 2)
print(b >> 1)
print(~a & 0xFF)

func popcount(_ x: Int) -> Int {
    var n = x
    var c = 0
    while n != 0 {
        c += n & 1
        n = n >> 1
    }
    return c
}
print(popcount(255))
print(popcount(0b101010))
