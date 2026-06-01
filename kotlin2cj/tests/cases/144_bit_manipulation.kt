// Bit manipulation tricks: counting bits, power of two, XOR tricks
fun countBits(n: Int): Int {
    var count = 0
    var x = n
    while (x > 0) {
        count += x and 1
        x = x shr 1
    }
    return count
}

fun isPowerOfTwo(n: Int): Boolean {
    return n > 0 && (n and (n - 1)) == 0
}

fun nextPowerOfTwo(n: Int): Int {
    var p = 1
    while (p < n) {
        p = p shl 1
    }
    return p
}

fun xorSwap(a: Int, b: Int): String {
    var x = a
    var y = b
    x = x xor y
    y = x xor y
    x = x xor y
    return "($x, $y)"
}

fun reverseBits(n: Int, bits: Int): Int {
    var result = 0
    var x = n
    for (i in 0 until bits) {
        result = (result shl 1) or (x and 1)
        x = x shr 1
    }
    return result
}

fun main() {
    // Count bits
    for (n in arrayListOf(0, 1, 7, 15, 16, 255)) {
        println("bits($n) = ${countBits(n)}")
    }

    // Power of two check
    for (n in arrayListOf(1, 2, 3, 4, 8, 10, 16, 64)) {
        println("isPow2($n) = ${isPowerOfTwo(n)}")
    }

    // Next power of two
    for (n in arrayListOf(1, 3, 5, 9, 17)) {
        println("nextPow2($n) = ${nextPowerOfTwo(n)}")
    }

    // XOR swap
    println("swap(3,7) = ${xorSwap(3, 7)}")
    println("swap(10,20) = ${xorSwap(10, 20)}")

    // Reverse bits (8-bit)
    println("reverse(1, 8) = ${reverseBits(1, 8)}")
    println("reverse(128, 8) = ${reverseBits(128, 8)}")
    println("reverse(170, 8) = ${reverseBits(170, 8)}")
}
