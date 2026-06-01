fun main() {
    val groups = HashMap<String, ArrayList<Int>>()
    groups["even"] = ArrayList<Int>()
    for (x in listOf(1, 2, 3, 4, 5, 6)) {
        if (x % 2 == 0) {
            groups["even"]?.add(x)
        }
    }
    val evenCount = groups["even"]?.size ?: 0
    val oddCount = groups["odd"]?.size ?: 0
    println("even=" + evenCount.toString())
    println("odd=" + oddCount.toString())
}
