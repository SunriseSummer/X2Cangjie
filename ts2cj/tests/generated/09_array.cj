import std.collection.*

let xs: ArrayList<Int64> = ArrayList<Int64>([10, 20, 30, 40])

main() {
    println("length = ${xs.size}")
    for (x in xs) {
        println("x = ${x}")
    }
    return 0
}
