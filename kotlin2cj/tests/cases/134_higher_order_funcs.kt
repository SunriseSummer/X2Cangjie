// Higher-order functions, function references, lambda composition
fun applyTwice(x: Int, f: (Int) -> Int): Int {
    return f(f(x))
}

fun compose(f: (Int) -> Int, g: (Int) -> Int): (Int) -> Int {
    return { x: Int -> f(g(x)) }
}

fun applyToList(list: ArrayList<Int>, transform: (Int) -> Int): ArrayList<Int> {
    val result = ArrayList<Int>()
    for (item in list) {
        result.add(transform(item))
    }
    return result
}

fun filterList(list: ArrayList<Int>, predicate: (Int) -> Boolean): ArrayList<Int> {
    val result = ArrayList<Int>()
    for (item in list) {
        if (predicate(item)) {
            result.add(item)
        }
    }
    return result
}

fun reduceList(list: ArrayList<Int>, initial: Int, operation: (Int, Int) -> Int): Int {
    var acc = initial
    for (item in list) {
        acc = operation(acc, item)
    }
    return acc
}

fun main() {
    // Apply twice
    println(applyTwice(3, { it * 2 }))    // 3*2=6, 6*2=12
    println(applyTwice(1, { it + 10 }))   // 1+10=11, 11+10=21

    // Compose
    val double = { x: Int -> x * 2 }
    val addOne = { x: Int -> x + 1 }
    val doubleThenAdd = compose(addOne, double)
    println(doubleThenAdd(5))  // 5*2=10, 10+1=11

    // Apply to list
    val nums = arrayListOf(1, 2, 3, 4, 5)
    val squared = applyToList(nums, { it * it })
    println(squared.joinToString(" "))

    // Filter
    val evens = filterList(nums, { it % 2 == 0 })
    println(evens.joinToString(" "))

    // Reduce
    val sum = reduceList(nums, 0, { a, b -> a + b })
    println("Sum: $sum")
    val product = reduceList(nums, 1, { a, b -> a * b })
    println("Product: $product")
}
