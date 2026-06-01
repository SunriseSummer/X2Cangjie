main() {
    let mask = 0xFF
    let flag = 0b1010
    let big = 1_000_000
    let rgb = 0x00FF00
    println(mask)
    println(flag)
    println(big)
    println(mask & flag)
    println(mask | flag)
    println(rgb >> 8)
    println(flag << 2)
}
