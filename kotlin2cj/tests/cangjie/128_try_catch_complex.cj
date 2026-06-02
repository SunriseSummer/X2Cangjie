func safeDivide(a: Int64, b: Int64): String {
    return try {
        let result = a / b
        "Result: ${result}"
    } catch (e: Exception) {
        "Error: division by zero"
    }
}

func parseNumber(s: String): Int64 {
    return try {
        var result = 0
        for (c in s.runes()) {
            if ((c < r'0') || (c > r'9')) {
                throw Exception("Invalid character: ${c}")
            }
            result = (result * 10) + ((Int64(UInt32(c)) - Int64(UInt32(r'0'))))
        }
        result
    } catch (e: Exception) {
        -1
    }
}

func riskyOperation(level: Int64): String {
    let sb = StringBuilder()
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

main() {
    println(safeDivide(10, 3))
    println(safeDivide(10, 0))
    println(parseNumber("12345"))
    println(parseNumber("12a45"))
    println(riskyOperation(1))
    println(riskyOperation(5))
    let result = try {
        let inner = try {
            42
        } catch (e: Exception) {
            0
        }
        inner * 2
    } catch (e: Exception) {
        -1
    }
    println("Nested: ${result}")
}
