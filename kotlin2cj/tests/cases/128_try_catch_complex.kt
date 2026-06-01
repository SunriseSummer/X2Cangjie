// Complex try-catch-finally chains
fun safeDivide(a: Int, b: Int): String {
    return try {
        val result = a / b
        "Result: $result"
    } catch (e: Exception) {
        "Error: division by zero"
    }
}

fun parseNumber(s: String): Int {
    return try {
        var result = 0
        for (c in s) {
            if (c < '0' || c > '9') {
                throw Exception("Invalid character: $c")
            }
            result = result * 10 + (c - '0')
        }
        result
    } catch (e: Exception) {
        -1
    }
}

fun riskyOperation(level: Int): String {
    val sb = StringBuilder()
    try {
        sb.append("start")
        if (level > 2) {
            throw Exception("too deep")
        }
        sb.append("-ok")
    } catch (e: Exception) {
        sb.append("-caught")
    } finally {
        sb.append("-done")
    }
    return sb.toString()
}

fun main() {
    println(safeDivide(10, 3))
    println(safeDivide(10, 0))

    println(parseNumber("12345"))
    println(parseNumber("12a45"))

    println(riskyOperation(1))
    println(riskyOperation(5))

    // Nested try-catch
    val result = try {
        val inner = try {
            42
        } catch (e: Exception) {
            0
        }
        inner * 2
    } catch (e: Exception) {
        -1
    }
    println("Nested: $result")
}
