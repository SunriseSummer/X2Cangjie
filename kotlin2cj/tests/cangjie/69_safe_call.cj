import std.collection.*

main() {
    let groups = HashMap<String, ArrayList<Int64>>()
    groups["even"] = ArrayList<Int64>()
    for (x in ArrayList([1, 2, 3, 4, 5, 6])) {
        if ((x % 2) == 0) {
            groups.get("even")?.add(x)
        }
    }
    let evenCount = groups.get("even")?.size ?? 0
    let oddCount = groups.get("odd")?.size ?? 0
    println("even=" + evenCount.toString())
    println("odd=" + oddCount.toString())
}
