fun main() {
    val data = listOf(12, 7, 23, 4, 18, 9, 31, 6, 15, 28)
    val evens = data.filter { it % 2 == 0 }
    val odds = data.filter { it % 2 != 0 }
    print("evens: ")
    for (e in evens) print("$e ")
    println()
    print("odds: ")
    for (o in odds) print("$o ")
    println()
    println("sum=${data.sum()} count=${data.count()} evenCount=${data.count { it % 2 == 0 }}")
    println("max=${data.maxOrNull() ?: 0} min=${data.minOrNull() ?: 0}")
    val squaresOver100 = data.map { it * it }.filter { it > 100 }
    print("bigSquares: ")
    for (s in squaresOver100) print("$s ")
    println()
    val avg = data.sum() / data.count()
    println("avg=$avg over=${data.count { it > avg }}")
}
