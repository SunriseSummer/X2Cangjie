// Complex when expressions: ranges, multiple conditions, nested when
fun classifyAge(age: Int): String {
    return when {
        age < 0 -> "invalid"
        age < 13 -> "child"
        age < 18 -> "teen"
        age < 65 -> "adult"
        else -> "senior"
    }
}

fun fizzBuzz(n: Int): String {
    return when {
        n % 15 == 0 -> "FizzBuzz"
        n % 3 == 0 -> "Fizz"
        n % 5 == 0 -> "Buzz"
        else -> n.toString()
    }
}

fun describeNumber(n: Int): String {
    return when {
        n < 0 -> "negative"
        n == 0 -> "zero"
        n in 1..10 -> "small"
        n in 11..100 -> "medium"
        else -> "large"
    }
}

fun dayType(day: String): String {
    return when (day) {
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday" -> "weekday"
        "Saturday", "Sunday" -> "weekend"
        else -> "unknown"
    }
}

fun main() {
    // Age classification
    println(classifyAge(-1))
    println(classifyAge(5))
    println(classifyAge(15))
    println(classifyAge(30))
    println(classifyAge(70))

    // FizzBuzz
    val fb = ArrayList<String>()
    for (i in 1..15) {
        fb.add(fizzBuzz(i))
    }
    println(fb.joinToString(" "))

    // Number description
    println(describeNumber(-5))
    println(describeNumber(0))
    println(describeNumber(7))
    println(describeNumber(50))
    println(describeNumber(200))

    // Day type
    println(dayType("Monday"))
    println(dayType("Saturday"))
    println(dayType("Holiday"))
}
