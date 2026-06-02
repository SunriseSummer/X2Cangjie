fun Int.isEven(): Boolean = this % 2 == 0
fun Int.isOdd(): Boolean = this % 2 != 0
fun Int.factorial(): Int {
    var result = 1
    var i = 1
    while (i <= this) {
        result *= i
        i++
    }
    return result
}

fun String.repeat(n: Int): String {
    val sb = StringBuilder()
    var i = 0
    while (i < n) {
        sb.append(this)
        i++
    }
    return sb.toString()
}

fun String.countChar(target: String): Int {
    var count = 0
    var i = 0
    while (i < this.length) {
        if (this.substring(i, i + 1) == target) {
            count++
        }
        i++
    }
    return count
}

fun ArrayList<Int>.computeAvg(): Int {
    if (this.size == 0) return 0
    var sum = 0
    for (n in this) {
        sum += n
    }
    return sum / this.size
}
