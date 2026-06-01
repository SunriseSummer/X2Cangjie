class Counter {
    var count = 0
    fun inc() { count += 1 }
    fun add(n: Int) { count += n }
}
fun main() {
    val c = Counter()
    repeat(5) { c.inc() }
    c.add(10)
    println("count=${c.count}")
    val nums = (1..10).toList()
    val evens = nums.filter { it % 2 == 0 }
    println("evens=${evens.joinToString(",")}")
    println("product=${nums.fold(1) { acc, n -> acc * n }}")
}
