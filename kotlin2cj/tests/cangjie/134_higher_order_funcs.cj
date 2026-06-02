import std.collection.*

func applyTwice(x: Int64, f: (Int64) -> Int64): Int64 {
    return f(f(x))
}

func compose(f: (Int64) -> Int64, g: (Int64) -> Int64): (Int64) -> Int64 {
    return { x: Int64 => f(g(x)) }
}

func applyToList(list: ArrayList<Int64>, transform: (Int64) -> Int64): ArrayList<Int64> {
    let result = ArrayList<Int64>()
    for (item in list) {
        result.add(transform(item))
    }
    return result
}

func filterList(list: ArrayList<Int64>, predicate: (Int64) -> Bool): ArrayList<Int64> {
    let result = ArrayList<Int64>()
    for (item in list) {
        if (predicate(item)) {
            result.add(item)
        }
    }
    return result
}

func reduceList(list: ArrayList<Int64>, initial: Int64, operation: (Int64, Int64) -> Int64): Int64 {
    var acc = initial
    for (item in list) {
        acc = operation(acc, item)
    }
    return acc
}

main() {
    println(applyTwice(3, { it => it * 2 }))
    println(applyTwice(1, { it => it + 10 }))
    let double = { x: Int64 => x * 2 }
    let addOne = { x: Int64 => x + 1 }
    let doubleThenAdd = compose(addOne, double)
    println(doubleThenAdd(5))
    let nums = ArrayList([1, 2, 3, 4, 5])
    let squared = applyToList(nums, { it => it * it })
    println(String.join(collectArray<String>(squared.iterator().map({e => e.toString()})), delimiter: " "))
    let evens = filterList(nums, { it => (it % 2) == 0 })
    println(String.join(collectArray<String>(evens.iterator().map({e => e.toString()})), delimiter: " "))
    let sum = reduceList(nums, 0, { a, b => a + b })
    println("Sum: ${sum}")
    let product = reduceList(nums, 1, { a, b => a * b })
    println("Product: ${product}")
}
