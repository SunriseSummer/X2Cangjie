import std.collection.*

func classify(score: Int64): String {
    if ((score < 0) || (score > 100)) {
        return "Invalid"
    }
    if (score >= 90) {
        return "A"
    }
    if (score >= 80) {
        return "B"
    }
    if (score >= 70) {
        return "C"
    }
    if (score >= 60) {
        return "D"
    }
    return "F"
}

func findFirst(arr: ArrayList<Int64>, predicate: (Int64) -> Bool): Int64 {
    for (i in 0..=(arr.size - 1)) {
        if (predicate(arr[i])) {
            return i
        }
    }
    return -1
}

func sumUntil(limit: Int64): Int64 {
    var sum = 0
    var i = 1
    while (sum < limit) {
        sum += i
        i += 1
    }
    return sum
}

main() {
    println(classify(95))
    println(classify(82))
    println(classify(71))
    println(classify(55))
    println(classify(-5))
    let nums = ArrayList([3, 7, 2, 9, 4, 6])
    println(findFirst(nums, { it => it > 5 }))
    println(findFirst(nums, { it => it > 10 }))
    println(sumUntil(10))
    println(sumUntil(50))
}
