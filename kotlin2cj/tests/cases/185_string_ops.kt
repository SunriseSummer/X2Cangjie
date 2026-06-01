fun main() {
    val x = "hello"
    println(x.startsWith("he"))
    println(x.endsWith("lo"))
    println(x.contains("ell"))
    println(x.replace("l", "r"))

    val nums = listOf(1, 2, 3, 4, 5)
    val big = nums.filter { it > 3 }
    println(big.joinToString(", "))
}
