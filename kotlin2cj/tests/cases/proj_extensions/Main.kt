fun main() {
    println("4 is even: ${4.isEven()}")
    println("7 is even: ${7.isEven()}")
    println("3 is odd: ${3.isOdd()}")
    println("8 is odd: ${8.isOdd()}")

    println("5! = ${5.factorial()}")
    println("0! = ${0.factorial()}")
    println("6! = ${6.factorial()}")

    println("'ab' * 3 = ${"ab".repeat(3)}")

    println("Count 'l' in 'hello world': ${"hello world".countChar("l")}")
    println("Count 'z' in 'hello': ${"hello".countChar("z")}")

    val nums = arrayListOf(10, 20, 30, 40, 50)
    println("Average of [10,20,30,40,50]: ${nums.computeAvg()}")

    val empty = arrayListOf<Int>()
    println("Average of []: ${empty.computeAvg()}")
}
