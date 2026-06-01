// Combined test: by lazy + vararg + object + also

object Logger {
    var messages = mutableListOf<String>()

    fun log(msg: String) {
        messages.add(msg)
    }

    fun dump(): String {
        return messages.joinToString("; ")
    }
}

fun sum(vararg nums: Int): Int {
    var total = 0
    for (n in nums) {
        total += n
    }
    return total
}

fun main() {
    val greeting by lazy { "Hello from lazy!" }
    println(greeting)

    Logger.log("start")
    Logger.log("process")
    Logger.log("end")
    println(Logger.dump())

    println(sum(1, 2, 3, 4, 5))

    val nums = mutableListOf(10, 20, 30)
    val doubled = nums.map { it * 2 }
    println(doubled.joinToString(", "))
}
