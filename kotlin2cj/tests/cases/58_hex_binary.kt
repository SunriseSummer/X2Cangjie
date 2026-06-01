fun main() {
    val mask = 0xFF
    val flag = 0b1010
    val big = 1_000_000
    val rgb = 0x00FF00
    println(mask)
    println(flag)
    println(big)
    println(mask and flag)
    println(mask or flag)
    println(rgb shr 8)
    println(flag shl 2)
}
