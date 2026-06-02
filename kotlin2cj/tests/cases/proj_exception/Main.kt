fun main() {
    val v = Validator()

    println(v.validateAge(25))
    try {
        println(v.validateAge(-5))
    } catch (e: IllegalArgumentException) {
        println("Caught: ${e.message}")
    }
    try {
        println(v.validateAge(200))
    } catch (e: IllegalArgumentException) {
        println("Caught: ${e.message}")
    }

    println(v.validateName("Alice"))
    try {
        println(v.validateName(""))
    } catch (e: IllegalArgumentException) {
        println("Caught: ${e.message}")
    }

    println(v.safeDivide(10, 3))
    println(v.safeDivide(10, 0))

    println("Parsed '123': ${v.parseNumber("123")}")
    println("Parsed '-42': ${v.parseNumber("-42")}")
    try {
        println("Parsed 'abc': ${v.parseNumber("abc")}")
    } catch (e: IllegalArgumentException) {
        println("Caught: ${e.message}")
    }
}
