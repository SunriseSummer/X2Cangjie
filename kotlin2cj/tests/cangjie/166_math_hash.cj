import std.collection.*

func simpleHash(s: String): Int64 {
    var hash = 0
    for (c in s.runes()) {
        hash = (hash * 31) + Int64(UInt32(c))
    }
    return hash & 0x7FFFFFFF
}

func modPow(base: Int64, exp: Int64, mod: Int64): Int64 {
    var result = 1
    var b = base % mod
    var e = exp
    while (e > 0) {
        if ((e % 2) == 1) {
            result = (result * b) % mod
        }
        e = e / 2
        b = (b * b) % mod
    }
    return result
}

func crc8(data: ArrayList<Int64>): Int64 {
    var crc = 0
    for (byte in data) {
        crc = crc ^ byte
        for (i in 0..=7) {
            crc = if ((crc & 1) != 0) {
                (crc >> 1) ^ 0xB2
            } else {
                crc >> 1
            }
        }
    }
    return crc & 0xFF
}

main() {
    println(simpleHash("hello"))
    println(simpleHash("world"))
    println(simpleHash(""))
    println(modPow(2, 10, 1000))
    println(modPow(3, 20, 1000000007))
    let data = ArrayList([0x01, 0x02, 0x03, 0x04])
    println(crc8(data))
    var n = 255
    var bits = 0
    while (n > 0) {
        bits += n & 1
        n = n >> 1
    }
    println("bits in 255: ${bits}")
}
