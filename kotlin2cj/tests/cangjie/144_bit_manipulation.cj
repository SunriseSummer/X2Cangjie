import std.collection.*

func countBits(n: Int64): Int64 {
    var count = 0
    var x = n
    while (x > 0) {
        count += x & 1
        x = x >> 1
    }
    return count
}

func isPowerOfTwo(n: Int64): Bool {
    return (n > 0) && ((n & (n - 1)) == 0)
}

func nextPowerOfTwo(n: Int64): Int64 {
    var p = 1
    while (p < n) {
        p = p << 1
    }
    return p
}

func xorSwap(a: Int64, b: Int64): String {
    var x = a
    var y = b
    x = x ^ y
    y = x ^ y
    x = x ^ y
    return "(${x}, ${y})"
}

func reverseBits(n: Int64, bits: Int64): Int64 {
    var result = 0
    var x = n
    for (i in 0..bits) {
        result = (result << 1) | (x & 1)
        x = x >> 1
    }
    return result
}

main() {
    for (n in ArrayList([0, 1, 7, 15, 16, 255])) {
        println("bits(${n}) = ${countBits(n)}")
    }
    for (n in ArrayList([1, 2, 3, 4, 8, 10, 16, 64])) {
        println("isPow2(${n}) = ${isPowerOfTwo(n)}")
    }
    for (n in ArrayList([1, 3, 5, 9, 17])) {
        println("nextPow2(${n}) = ${nextPowerOfTwo(n)}")
    }
    println("swap(3,7) = ${xorSwap(3, 7)}")
    println("swap(10,20) = ${xorSwap(10, 20)}")
    println("reverse(1, 8) = ${reverseBits(1, 8)}")
    println("reverse(128, 8) = ${reverseBits(128, 8)}")
    println("reverse(170, 8) = ${reverseBits(170, 8)}")
}
