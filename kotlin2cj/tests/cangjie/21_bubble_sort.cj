import std.collection.*

main() {
    let a = ArrayList([5, 2, 8, 1, 9, 3, 7])
    let n = a.size
    for (i in 0..n) {
        for (j in 0..((n - 1) - i)) {
            if (a[j] > a[j + 1]) {
                let tmp = a[j]
                a[j] = a[j + 1]
                a[j + 1] = tmp
            }
        }
    }
    for (x in a) {
        print("${x} ")
    }
    println("")
}
