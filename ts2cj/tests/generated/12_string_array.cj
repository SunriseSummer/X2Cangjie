import std.collection.*

let words: ArrayList<String> = ArrayList<String>(["alpha", "beta", "gamma"])

main() {
    for (w in words) {
        println(w)
    }
    return 0
}
