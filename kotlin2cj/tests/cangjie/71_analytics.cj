import std.collection.*

main() {
    let data = ArrayList([12, 7, 23, 4, 18, 9, 31, 6, 15, 28])
    let evens = collectArrayList(data.iterator().filter({ it => (it % 2) == 0 }))
    let odds = collectArrayList(data.iterator().filter({ it => (it % 2) != 0 }))
    print("evens: ")
    for (e in evens) {
        print("${e} ")
    }
    println()
    print("odds: ")
    for (o in odds) {
        print("${o} ")
    }
    println()
    println("sum=${data.iterator().fold<Int64>(0, {acc, x => acc + x})} count=${data.size} evenCount=${data.iterator().filter({ it => (it % 2) == 0 }).count()}")
    println("max=${data.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0} min=${data.iterator().reduce({a, b => if (a < b) { a } else { b }}) ?? 0}")
    let squaresOver100 = collectArrayList(collectArrayList(data.iterator().map({ it => it * it })).iterator().filter({ it => it > 100 }))
    print("bigSquares: ")
    for (s in squaresOver100) {
        print("${s} ")
    }
    println()
    let avg = data.iterator().fold<Int64>(0, {acc, x => acc + x}) / data.size
    println("avg=${avg} over=${data.iterator().filter({ it => it > avg }).count()}")
}
