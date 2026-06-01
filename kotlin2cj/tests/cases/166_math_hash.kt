// Test: Bitwise + math-heavy computation (CRC-like, hashing, modular arithmetic)
fun simpleHash(s: String): Int {
    var hash = 0
    for (c in s) {
        hash = hash * 31 + c.code
    }
    return hash and 0x7FFFFFFF
}

fun modPow(base: Long, exp: Long, mod: Long): Long {
    var result = 1L
    var b = base % mod
    var e = exp
    while (e > 0L) {
        if (e % 2L == 1L) {
            result = result * b % mod
        }
        e = e / 2L
        b = b * b % mod
    }
    return result
}

fun crc8(data: ArrayList<Int>): Int {
    var crc = 0
    for (byte in data) {
        crc = crc xor byte
        for (i in 0..7) {
            crc = if (crc and 1 != 0) {
                (crc shr 1) xor 0xB2
            } else {
                crc shr 1
            }
        }
    }
    return crc and 0xFF
}

fun main() {
    println(simpleHash("hello"))
    println(simpleHash("world"))
    println(simpleHash(""))

    println(modPow(2, 10, 1000))
    println(modPow(3, 20, 1000000007))

    val data = arrayListOf(0x01, 0x02, 0x03, 0x04)
    println(crc8(data))

    // Bit counting
    var n = 255
    var bits = 0
    while (n > 0) {
        bits += n and 1
        n = n shr 1
    }
    println("bits in 255: $bits")
}
